"""Regressions for routing, safe diagnostics and actual preparation transport."""

import json
import contextlib
import io
import os
import shutil
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import test_preparation_guard as fixtures

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import model_routing as routing


def task(**changes):
    return {
        "kind": "analysis", "complexity": "trivial", "scope": "local",
        "risk": "low", "uncertainty": "low", "reasoning": "routine",
        "dependencies": "known", "delegation_value": "worthwhile",
        "objective": "Inspect README.md.", "acceptance": ["Report the heading."],
        "assessment_basis": ["One known file."], **changes,
    }


def result(status="completed", **changes):
    return {"status": status, "summary": "Read the README.",
            "evidence": [{"criterion_id": "AC-1", "observation": "# Pilot"}],
            "signal": None, **changes}


def execution(payload, returncode=0):
    events = [{"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(payload)}},
              {"type": "turn.completed"}]
    return SimpleNamespace(returncode=returncode, stdout="\n".join(map(json.dumps, events)))


class RoutingTests(unittest.TestCase):
    def test_clean_runtime_subset_runs_and_detects_missing_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = Path(folder).resolve() / "runtime"
            (runtime / "scripts").mkdir(parents=True)
            shutil.copy2(ROOT / "AGENTS.md", runtime / "AGENTS.md")
            shutil.copytree(ROOT / "docs", runtime / "docs")
            for name in ("model_routing.py", "model_routing_result.schema.json", "preparation_guard.py"):
                shutil.copy2(ROOT / "scripts" / name, runtime / "scripts" / name)
            script = runtime / "scripts/model_routing.py"
            process = routing.subprocess.run([sys.executable, "-B", str(script), "--assessment", "-"],
                input=json.dumps(task()), capture_output=True, text=True, check=False, cwd=runtime)
            self.assertEqual(0, process.returncode, "Clean runtime selection failed.")
            self.assertEqual("gpt-6-luna", json.loads(process.stdout)["model"])
            (runtime / "scripts/preparation_guard.py").unlink()
            missing = routing.subprocess.run([sys.executable, "-B", str(script), "--preparation", "PRIVATE_RECORD_MARKER",
                "--guard-config", "PRIVATE_CONFIG_MARKER", "--workspace", str(runtime)],
                capture_output=True, text=True, check=False, cwd=runtime)
            self.assertEqual(2, missing.returncode)
            self.assertEqual("", missing.stdout)
            self.assertIn("preparation guard is unavailable", missing.stderr)
            self.assertNotIn("PRIVATE_", missing.stderr)

    def test_actual_malformed_context_is_reported_without_traceback(self):
        fixture, _ = self.real_preparation()
        context_path, _ = fixtures.guard.state_paths(fixture.config, fixture.event["session_id"])
        context = fixtures.guard.read_json(context_path)
        del context["created_at"]
        fixtures.guard.write_json(context_path, context)
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = routing.main(["--preparation", str(fixture.record_path), "--guard-config",
                                 str(fixture.config_path), "--workspace", str(fixture.workspace)])
        self.assertEqual(2, code)
        self.assertEqual("", output.getvalue())
        self.assertIn("Preparation", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())
        self.assertNotIn(str(fixture.root), errors.getvalue())

    def real_preparation(self):
        fixture = fixtures.PreparationGuardTest()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        record = fixture.ready()
        record.update(type="analysis", objective=task()["objective"], complexity="trivial",
                      write_paths=[], routing=task(), verification=["Coordinator must compare source hashes."])
        fixtures.guard.write_json(fixture.record_path, dict(record, status="draft"))
        event = dict(fixture.event, tool_name="update_plan", tool_input={
            "explanation": fixtures.guard.SUBMISSION_PREFIX + json.dumps(record),
            "plan": [{"step": "Verify isolated read-only routing", "status": "in_progress"}],
        })
        response = fixture.process(event)
        self.assertFalse(fixture.denied(response))
        return fixture, fixtures.guard.read_json(fixture.record_path)

    def test_actual_guard_transport_preserves_routing_and_required_checks(self):
        fixture, record = self.real_preparation()
        before = fixture.record_path.read_bytes()
        decision = routing.prepared_route(fixture.record_path, fixture.config_path, fixture.workspace)
        self.assertEqual("gpt-6-luna", decision["model"])
        self.assertEqual(record["generation"], decision["preparation"]["generation"])
        self.assertEqual(before, fixture.record_path.read_bytes())
        self.assertEqual(["Coordinator must compare source hashes."], record["verification"])

    def test_actual_guard_rejects_stale_sources(self):
        fixture, _ = self.real_preparation()
        (fixture.workspace / "AGENTS.md").write_text("Changed source.", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Preparation validation rejected"):
            routing.prepared_route(fixture.record_path, fixture.config_path, fixture.workspace)

    def test_actual_guard_rejects_pending_authorization(self):
        fixture, record = self.real_preparation()
        record["authorization"]["pending"] = ["Unresolved fixture gate"]
        fixtures.guard.write_json(fixture.record_path, record)
        with self.assertRaisesRegex(ValueError, "Preparation validation rejected"):
            routing.prepared_route(fixture.record_path, fixture.config_path, fixture.workspace)

    def test_actual_guard_rejects_expired_context(self):
        fixture, _ = self.real_preparation()
        context_path, _ = fixtures.guard.state_paths(fixture.config, fixture.event["session_id"])
        context = fixtures.guard.read_json(context_path)
        context["created_at"] -= fixtures.guard.MAX_AGE_SECONDS + 1
        fixtures.guard.write_json(context_path, context)
        with self.assertRaisesRegex(ValueError, "Preparation validation rejected"):
            routing.prepared_route(fixture.record_path, fixture.config_path, fixture.workspace)

    def test_actual_guard_rejects_lifecycle_invalidation(self):
        fixture, record = self.real_preparation()
        marker = fixtures.guard.invalidation_path(fixture.config_path, record["session_id"])
        fixtures.guard.write_json(marker, {"reason": "New fixture generation"})
        with self.assertRaisesRegex(ValueError, "invalidation"):
            routing.prepared_route(fixture.record_path, fixture.config_path, fixture.workspace)

    def test_actual_guard_rejects_routing_mismatch_and_write_scope(self):
        fixture, record = self.real_preparation()
        for mutation, message in (({"write_paths": [str(fixture.target)]}, "empty write"),
                                  ({"routing": task(objective="Different objective.")}, "must match")):
            with self.subTest(mutation=mutation):
                fixtures.guard.write_json(fixture.record_path, {**record, **mutation})
                with self.assertRaisesRegex(ValueError, message):
                    routing.prepared_route(fixture.record_path, fixture.config_path, fixture.workspace)

    def test_dispatch_failure_diagnostics_do_not_copy_subprocess_data(self):
        decision = {**routing.route(task()), "preparation": {"generation": "test"}}
        for error, expected in (
            (routing.subprocess.TimeoutExpired("PRIVATE_COMMAND_MARKER", 300, output="PRIVATE_STREAM_MARKER"), "timed out"),
            (UnicodeDecodeError("utf-8", b"\xff", 0, 1, "PRIVATE_ENCODING_MARKER"), "encoding"),
        ):
            with self.subTest(error=type(error).__name__), patch.object(routing, "profile_preflight", return_value=(Path("codex"), Path("profile"), Path("repo"))):
                with patch.object(routing.subprocess, "run", side_effect=error):
                    outcome = routing.launch_read_only(decision, None, None, None)
                self.assertEqual("blocked", outcome["status"])
                self.assertIn(expected, outcome["reason"])
                self.assertNotIn("PRIVATE_", outcome["reason"])

    def test_invocation_error_is_safe_and_not_a_completed_result(self):
        decision = {**routing.route(task()), "preparation": {"generation": "test"}}
        with patch.object(routing, "profile_preflight", return_value=(Path("codex"), Path("profile"), Path("repo"))):
            with patch.object(routing.subprocess, "run", side_effect=OSError("PRIVATE_INVOCATION_MARKER")):
                with self.assertRaises(ValueError) as stopped:
                    routing.launch_read_only(decision, None, None, None)
        self.assertIn("invocation", str(stopped.exception))
        self.assertNotIn("PRIVATE_", str(stopped.exception))

    def test_every_selection_factor_is_independently_effective(self):
        for key, value in {
            "complexity": "complex", "scope": "cross_component", "risk": "medium",
            "uncertainty": "material", "reasoning": "advanced",
            "dependencies": "unknown", "delegation_value": "low",
        }.items():
            with self.subTest(factor=key):
                decision = routing.route(task(**{key: value}))
                self.assertEqual("gpt-6.1-sol", decision["model"])
                self.assertIn(f"{key}={value}", decision["reasons"])

    def test_missing_assessment_diagnostic_does_not_echo_path(self):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = routing.main(["--assessment", str(ROOT / "PRIVATE_PATH_MARKER.json")])
        self.assertEqual(2, code)
        self.assertEqual("", output.getvalue())
        self.assertNotIn("PRIVATE_PATH_MARKER", errors.getvalue())
        self.assertIn("Assessment", errors.getvalue())

    def test_argument_error_does_not_echo_unknown_values(self):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            with self.assertRaises(SystemExit) as stopped:
                routing.main(["--assessment", "-", "--unknown=PRIVATE_ARGUMENT_MARKER"])
        self.assertEqual(2, stopped.exception.code)
        self.assertEqual("", output.getvalue())
        self.assertNotIn("PRIVATE_ARGUMENT_MARKER", errors.getvalue())

    def test_malformed_preparation_does_not_escape_as_traceback(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(routing, "prepared_route", side_effect=KeyError("PRIVATE_STATE_MARKER")):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                code = routing.main(["--preparation", "record.json", "--guard-config", "guard.json", "--workspace", "."])
        self.assertEqual(2, code)
        self.assertNotIn("PRIVATE_STATE_MARKER", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())
        self.assertEqual("", output.getvalue())
        self.assertIn("Preparation", errors.getvalue())

    def test_process_failure_retains_code_without_guessing_cause(self):
        process = SimpleNamespace(returncode=-9, stdout="PRIVATE_STREAM_MARKER", stderr="PRIVATE_STREAM_MARKER")
        outcome = routing.outcome_from_execution(routing.route(task()), process)
        self.assertEqual("blocked", outcome["status"])
        self.assertIn("-9", outcome["reason"])
        self.assertIn("unclassified", outcome["reason"])
        self.assertNotIn("PRIVATE_STREAM_MARKER", json.dumps(outcome))

    def test_unexpected_validator_text_is_not_a_diagnostic(self):
        with patch.object(routing, "validate_outcome", side_effect=ValueError("PRIVATE_EXCEPTION_MARKER")):
            outcome = routing.outcome_from_execution(routing.route(task()), execution(result()))
        self.assertEqual("blocked", outcome["status"])
        self.assertNotIn("PRIVATE_EXCEPTION_MARKER", outcome["reason"])

    def test_missing_runtime_schema_prevents_dispatch(self):
        decision = {**routing.route(task()), "preparation": {"generation": "test"}}
        with patch.object(routing, "profile_preflight", return_value=(Path("codex"), Path("profile"), Path("repo"))):
            with patch.object(Path, "read_text", side_effect=FileNotFoundError("PRIVATE_SCHEMA_MARKER")):
                with patch.object(routing.subprocess, "run") as run:
                    with self.assertRaisesRegex(ValueError, "schema"):
                        routing.launch_read_only(decision, None, None, None)
                    run.assert_not_called()

    def test_selection_keeps_risk_separate(self):
        self.assertEqual("gpt-6-luna", routing.route(task())["model"])
        self.assertEqual("gpt-6.1-sol", routing.route(task(complexity="complex"))["model"])
        decision = routing.route(task(risk="high"))
        self.assertEqual(("gpt-6.1-sol", "coordinator"), (decision["model"], decision["dispatch"]))

    def test_completion_remains_subject_to_review(self):
        decision = routing.route(task())
        self.assertEqual("needs_review", routing.outcome_from_execution(decision, execution(result()))["status"])
        for process in (execution(result(evidence=[])), execution(result(), 4),
                        SimpleNamespace(returncode=0, stdout="")):
            with self.subTest(process=process):
                self.assertEqual("blocked", routing.outcome_from_execution(decision, process)["status"])

    def test_long_criterion_is_preserved_and_evidence_uses_only_its_id(self):
        text = "Return the exact first Markdown heading from README.md as the complete observation."
        decision = routing.route(task(acceptance=[text]))
        self.assertEqual([{"id": "AC-1", "text": text}], decision["criteria"])
        outcome = routing.outcome_from_execution(decision, execution(result()))
        self.assertEqual("needs_review", outcome["status"])
        self.assertEqual(text, outcome["decision"]["criteria"][0]["text"])

    def test_missing_duplicate_and_unknown_ids_report_specific_failures(self):
        decision = routing.route(task(acceptance=["First criterion.", "Second criterion."]))
        one = {"criterion_id": "AC-1", "observation": "First result"}
        for evidence, expected in [
            ([one], "every acceptance criterion ID"),
            ([one, one], "repeats an acceptance criterion ID"),
            ([one, {"criterion_id": "AC-99", "observation": "Wrong ID"}], "unknown acceptance criterion ID"),
        ]:
            with self.subTest(evidence=evidence):
                outcome = routing.outcome_from_execution(decision, execution(result(evidence=evidence)))
                self.assertEqual("blocked", outcome["status"])
                self.assertIn(expected, outcome["reason"])
        valid = result(evidence=[{"criterion_id": "AC-2", "observation": "Second result"}, one])
        self.assertEqual("needs_review", routing.outcome_from_execution(decision, execution(valid))["status"])

    def test_malformed_native_result_is_distinguished_from_missing_evidence(self):
        decision = routing.route(task())
        process = execution(result())
        events = [json.loads(line) for line in process.stdout.splitlines()]
        events[0]["item"]["text"] = "This is not JSON."
        process.stdout = "\n".join(map(json.dumps, events))
        outcome = routing.outcome_from_execution(decision, process)
        self.assertEqual("blocked", outcome["status"])
        self.assertIn("not valid JSON", outcome["reason"])

    def test_escalation_preserves_original_acceptance_and_evidence(self):
        decision = routing.route(task())
        outcome = routing.outcome_from_execution(
            decision, execution(result("escalated", signal="scope_growth"))
        )
        self.assertEqual("escalated", outcome["status"])
        self.assertEqual(task(), outcome["decision"]["assessment"])
        self.assertEqual("# Pilot", outcome["reported"]["evidence"][0]["observation"])

    def test_unprepared_assessment_never_launches(self):
        with patch.object(routing.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "prepare"):
                routing.launch_read_only(routing.route(task()), None, None, None)
            run.assert_not_called()

    def test_launch_uses_read_only_schema_and_passes_verification(self):
        command = "Get-Content -LiteralPath README.md -TotalCount 1"
        decision = {**routing.route(task(inspection_command=command)), "preparation": {"generation": "test"}}
        with patch.object(routing, "profile_preflight", return_value=(Path("codex"), Path("profile"), Path("repo"))):
            with patch.object(routing.subprocess, "run", return_value=execution(result())) as run:
                self.assertEqual("needs_review", routing.launch_read_only(decision, None, None, None)["status"])
                args = run.call_args.args[0]
                self.assertEqual("read-only", args[args.index("--sandbox") + 1])
                self.assertEqual("gpt-6-luna", args[args.index("--model") + 1])
                self.assertTrue(Path(args[args.index("--output-schema") + 1]).is_file())
                prompt = run.call_args.kwargs["input"]
                self.assertIn("Do not submit resolve or ready records", prompt)
                self.assertIn(decision["verification"][0], prompt)
                request = json.loads(prompt.split("\n", 1)[1])
                self.assertEqual(decision["criteria"], request["acceptance"])
                self.assertEqual(command, request["inspection_command"])
                schema = json.loads(Path(args[args.index("--output-schema") + 1]).read_text(encoding="utf-8"))
                self.assertEqual({None, *routing.ESCALATION_SIGNALS}, set(schema["properties"]["signal"]["enum"]))

    def test_prepared_route_reuses_guard_and_rejects_scope_or_mismatches(self):
        work = ROOT.resolve()
        record_path, config_path = work / "preparation.json", work / "guard.json"
        record = {"routing": task(), "session_id": "session", "generation": "gen",
                  "workspace": str(work), "write_paths": [], "objective": task()["objective"],
                  "risk": "low", "complexity": "trivial"}
        validator = unittest.mock.Mock()
        guard = SimpleNamespace(
            read_json=lambda p: record if p == record_path else {},
            state_paths=lambda *_: (work / "context.json", record_path),
            invalidation_path=lambda *_: work / "missing-invalidation.json",
            validate=validator,
            shell_read_only=lambda command: command == "Get-Content -LiteralPath README.md -TotalCount 1",
            PreparationError=ValueError,
        )
        original_resolve = Path.resolve
        def resolve(path, **kwargs):
            return original_resolve(path)
        with patch.dict(sys.modules, {"preparation_guard": guard}), patch.object(Path, "resolve", resolve):
            self.assertEqual("gen", routing.prepared_route(record_path, config_path, work)["preparation"]["generation"])
            validator.assert_called_once()
            record["write_paths"] = ["an allowed write in another workflow"]
            with self.assertRaisesRegex(ValueError, "empty write"):
                routing.prepared_route(record_path, config_path, work)
            record.update(write_paths=[], risk="medium")
            with self.assertRaisesRegex(ValueError, "must match"):
                routing.prepared_route(record_path, config_path, work)
            record.update(risk="low", routing=task(inspection_command="Set-Content README.md changed"))
            with self.assertRaisesRegex(ValueError, "literal read"):
                routing.prepared_route(record_path, config_path, work)

    def test_profile_rejects_empty_hooks_and_active_custom_home(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = Path(folder).resolve()
            codex, profile, work = root / "codex.exe", root / "profile", root / "repo"
            codex.touch()
            profile.mkdir()
            work.mkdir()
            path = profile / "hooks.json"
            trusted = []
            events = {}
            for name, key in (("SessionStart", "session_start"), ("UserPromptSubmit", "user_prompt_submit"),
                              ("PreToolUse", "pre_tool_use")):
                events[name] = [{"hooks": [{"type": "command", "command": "verified pilot guard"}]}]
                trusted.append(f'{json.dumps(str(path) + ":" + key + ":0:0")} = {{trusted_hash = "sha256:{"a" * 64}"}}')
            (profile / "config.toml").write_text("[hooks.state]\n" + "\n".join(trusted), encoding="utf-8")
            path.write_text(json.dumps({"hooks": events}), encoding="utf-8")
            self.assertEqual(profile, routing.profile_preflight(codex, profile, work)[1])
            with patch.dict(os.environ, {"CODEX_HOME": str(profile)}):
                with self.assertRaisesRegex(ValueError, "active Codex"):
                    routing.profile_preflight(codex, profile, work)
            events["PreToolUse"] = [{}]
            path.write_text(json.dumps({"hooks": events}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "PreToolUse"):
                routing.profile_preflight(codex, profile, work)


if __name__ == "__main__":
    unittest.main()
