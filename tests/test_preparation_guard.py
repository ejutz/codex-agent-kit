"""Exercise the actual hook process and verify denial precedes file writes."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/preparation_guard.py"
spec = importlib.util.spec_from_file_location("preparation_guard", SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class PreparationGuardTest(unittest.TestCase):
    """Use only disposable files, no services, credentials or application DB."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.kit = self.root / "kit"
        self.home = self.root / "home"
        self.workspace = self.root / "project"
        for path in [self.home / "AGENTS.md", self.kit / "AGENTS.md",
                     self.kit / "docs/implementation/workflow.md",
                     self.kit / "docs/implementation/preparation-control.md",
                     self.kit / "docs/testing/strategy.md", self.kit / "scripts/preparation_guard.py",
                     self.workspace / "AGENTS.md"]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture instructions\n", encoding="utf-8")
        self.config = {"kit_root": str(self.kit), "codex_home": str(self.home), "state_root": str(self.home / "preparation-control/state")}
        self.config_path = self.home / "guard-config.json"
        guard.write_json(self.config_path, self.config)
        self.event = {"session_id": "test-session", "cwd": str(self.workspace), "hook_event_name": "PreToolUse", "tool_name": "apply_patch"}
        self.context, self.record_path = guard.new_context(self.config, self.event)
        self.target = self.workspace / "canary.txt"
        self.command = "*** Begin Patch\n*** Add File: " + str(self.target) + "\n+allowed\n*** End Patch"
        self.event["tool_input"] = {"command": self.command}

    def ready(self):
        record = guard.read_json(self.record_path)
        record.update(status="ready", task="Disposable blocking test", type="tests", complexity="bounded",
                      complexity_reason="Two local paths and isolated assertions", risk="low",
                      risk_reason="Disposable files only", objective="Verify denial before writing",
                      scope="The canary file", steps=["Run the hook and check the canary"],
                      verification=["Assert denied writes have no side effects"], risks=["No live data touched"],
                      recovery="TemporaryDirectory removes only these test fixtures",
                      authorization={"basis": "User requested isolated blocking validation", "pending": []},
                      write_paths=[str(self.target)])
        check = {"source": str(self.kit / "AGENTS.md"), "requirement": "Preparation exists before mutation",
                 "status": "passed", "evidence": "Fixture plan covers these local tests"}
        record["requirements"] = [check]
        record["pre_execution_checks"] = [copy.deepcopy(check)]
        guard.write_json(self.record_path, record)
        return record

    def process(self, event=None):
        result = subprocess.run([sys.executable, str(SCRIPT), "--config", str(self.config_path)],
                                input=json.dumps(event or self.event), text=True, capture_output=True, check=True)
        return json.loads(result.stdout)

    def denied(self, result):
        return result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

    def execute_after_hook(self, event, operation):
        result = self.process(event)
        if not self.denied(result):
            operation()
        return result

    def test_missing_preparation_blocks_before_canary_creation(self):
        result = self.execute_after_hook(self.event, lambda: self.target.write_text("must not exist"))
        self.assertTrue(self.denied(result))
        self.assertFalse(self.target.exists())

    def test_each_required_field_is_checked(self):
        baseline = self.ready()
        for field in ["status", "objective", "scope", "steps", "verification", "risks", "recovery",
                      "authorization", "sources", "requirements", "pre_execution_checks", "complexity_reason", "risk_reason"]:
            with self.subTest(field=field):
                record = copy.deepcopy(baseline)
                del record[field]
                guard.write_json(self.record_path, record)
                self.assertTrue(self.denied(self.process()))

    def test_pending_requirement_and_pending_approval_are_denied(self):
        record = self.ready()
        record["requirements"][0]["status"] = "pending"
        guard.write_json(self.record_path, record)
        self.assertTrue(self.denied(self.process()))
        record = self.ready()
        record["authorization"]["pending"] = ["deployment approval"]
        guard.write_json(self.record_path, record)
        self.assertTrue(self.denied(self.process()))

    def test_valid_preparation_permits_real_disposable_write(self):
        self.ready()
        result = self.execute_after_hook(self.event, lambda: self.target.write_text("allowed", encoding="utf-8"))
        self.assertFalse(self.denied(result))
        self.assertEqual("allowed", self.target.read_text(encoding="utf-8"))

    def test_changed_instruction_is_denied(self):
        self.ready()
        (self.kit / "AGENTS.md").write_text("changed rules", encoding="utf-8")
        self.assertTrue(self.denied(self.process()))

    def test_omitted_instruction_is_denied(self):
        record = self.ready()
        record["sources"] = record["sources"][1:]
        guard.write_json(self.record_path, record)
        self.assertTrue(self.denied(self.process()))

    def test_newly_added_override_invalidates_preparation(self):
        self.ready()
        (self.workspace / "AGENTS.override.md").write_text("new instructions", encoding="utf-8")
        self.assertTrue(self.denied(self.process()))

    def test_wrong_session_generation_or_workspace_is_denied(self):
        baseline = self.ready()
        for field in ["session_id", "generation", "workspace"]:
            with self.subTest(field=field):
                record = copy.deepcopy(baseline)
                record[field] = "another"
                guard.write_json(self.record_path, record)
                self.assertTrue(self.denied(self.process()))

    def test_expired_preparation_is_denied(self):
        record = self.ready()
        with self.assertRaises(guard.PreparationError):
            guard.validate(self.config, self.context, record, now=self.context["created_at"] + guard.MAX_AGE_SECONDS + 1)

    def test_new_prompt_invalidates_old_record(self):
        record = self.ready()
        event = dict(self.event, hook_event_name="UserPromptSubmit", turn_id="next-turn")
        self.process(event)
        self.assertTrue(self.denied(self.process()))
        guard.write_json(self.record_path, record)
        self.assertTrue(self.denied(self.process()))

    def test_state_files_cannot_be_used_as_a_patch_bootstrap(self):
        event = copy.deepcopy(self.event)
        event["tool_input"]["command"] = "*** Begin Patch\n*** Update File: " + str(self.record_path) + "\n@@\n-old\n+new\n*** End Patch"
        self.assertTrue(self.denied(self.process(event)))
        event["tool_input"]["command"] = event["tool_input"]["command"].replace("*** End Patch", "*** Add File: " + str(self.target) + "\n+bad\n*** End Patch")
        self.assertTrue(self.denied(self.process(event)))

    def test_metadata_submission_registers_ready_preparation_without_agent_file_write(self):
        record = self.ready()
        guard.write_json(self.record_path, dict(record, status="draft"))
        event = dict(self.event, tool_name="update_plan", tool_input={"explanation": guard.SUBMISSION_PREFIX + json.dumps(record), "plan": [{"step": "Verify fixture", "status": "in_progress"}]})
        result = self.process(event)
        self.assertFalse(self.denied(result))
        self.assertEqual("ready", guard.read_json(self.record_path)["status"])
        self.assertEqual("Preparation verified by the global hook.", result["hookSpecificOutput"]["updatedInput"]["explanation"])
        self.assertFalse(self.denied(self.process()))

    def test_literal_shell_submission_is_rewritten_before_execution(self):
        record = self.ready()
        record["task"] = "User's disposable fixture"
        command = "Write-Output '" + (guard.SUBMISSION_PREFIX + json.dumps(record)).replace("'", "''") + "'"
        event = dict(self.event, tool_name="Bash", tool_input={"command": command})
        result = self.process(event)
        self.assertFalse(self.denied(result))
        self.assertEqual("Write-Output 'Preparation verified by the global hook.'", result["hookSpecificOutput"]["updatedInput"]["command"])
        event["tool_input"]["command"] += "; Set-Content escape.txt bad"
        self.assertTrue(self.denied(self.process(event)))

    def test_invalid_submission_revokes_previous_ready_state(self):
        record = self.ready()
        record["objective"] = ""
        event = dict(self.event, tool_name="update_plan", tool_input={"explanation": guard.SUBMISSION_PREFIX + json.dumps(record), "plan": []})
        self.assertTrue(self.denied(self.process(event)))
        self.assertEqual("draft", guard.read_json(self.record_path)["status"])
        self.assertTrue(self.denied(self.process()))

    def test_out_of_scope_traversal_and_move_are_denied(self):
        self.ready()
        for destination in [str(self.root / "escape.txt"), "../escape.txt", str(self.workspace / "canary.txt.extra")]:
            with self.subTest(destination=destination):
                event = copy.deepcopy(self.event)
                event["tool_input"]["command"] = self.command.replace(str(self.target), destination)
                self.assertTrue(self.denied(self.process(event)))
        event = copy.deepcopy(self.event)
        event["tool_input"]["command"] = self.command.replace("*** Add File:", "*** Update File:").replace("+allowed", "*** Move to: " + str(self.root / "escape.txt") + "\n+allowed")
        self.assertTrue(self.denied(self.process(event)))

    def test_hook_owned_context_cannot_be_patched(self):
        record = self.ready()
        context_path, _ = guard.state_paths(self.config, self.event["session_id"])
        record["write_paths"] = [str(context_path)]
        guard.write_json(self.record_path, record)
        event = copy.deepcopy(self.event)
        event["tool_input"]["command"] = self.command.replace(str(self.target), str(context_path))
        self.assertTrue(self.denied(self.process(event)))

    def test_read_only_shell_and_unknown_shell(self):
        for command in ["Get-Content AGENTS.md", "git status --short", "rg -n MUST AGENTS.md"]:
            event = dict(self.event, tool_name="Bash", tool_input={"command": command})
            self.assertFalse(self.denied(self.process(event)))
        for command in ["Set-Content canary.txt bad", "python -c 'open(\"canary.txt\",\"w\")'", "Get-Content a | Set-Content b", "rg --pre malicious.py a", "git diff --output=canary.txt", "$x = 1"]:
            event = dict(self.event, tool_name="Bash", tool_input={"command": command})
            self.assertTrue(self.denied(self.process(event)))

    def test_exact_prepared_shell_command_and_cwd_are_required(self):
        record = self.ready()
        command = "Set-Content -LiteralPath canary.txt -Value allowed"
        record["commands"] = [{"command": command, "cwd": str(self.workspace), "purpose": "Write only the test canary"}]
        guard.write_json(self.record_path, record)
        event = dict(self.event, tool_name="Bash", tool_input={"command": command})
        self.assertFalse(self.denied(self.process(event)))
        event["tool_input"]["command"] += "bad"
        self.assertTrue(self.denied(self.process(event)))
        event["tool_input"] = {"command": command, "workdir": str(self.root)}
        self.assertTrue(self.denied(self.process(event)))

    def test_unknown_mcp_requires_exact_prepared_arguments(self):
        record = self.ready()
        args = {"path": str(self.target), "content": "allowed"}
        event = dict(self.event, tool_name="mcp__filesystem__write_file", tool_input=args)
        self.assertTrue(self.denied(self.process(event)))
        record["tool_calls"] = [{"tool": event["tool_name"], "input_sha256": guard.input_hash(args), "purpose": "Write only the test canary"}]
        guard.write_json(self.record_path, record)
        self.assertFalse(self.denied(self.process(event)))
        event["tool_input"] = dict(args, content="different")
        self.assertTrue(self.denied(self.process(event)))

    def test_malformed_record_is_denied(self):
        self.record_path.write_text("not json", encoding="utf-8")
        self.assertTrue(self.denied(self.process()))

    def test_missing_config_and_malformed_event_return_explicit_deny(self):
        for raw, config in [("{", self.config_path), (json.dumps(self.event), self.root / "missing.json")]:
            result = subprocess.run([sys.executable, str(SCRIPT), "--config", str(config)], input=raw, text=True, capture_output=True, check=True)
            self.assertTrue(self.denied(json.loads(result.stdout)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
