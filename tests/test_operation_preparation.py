"""Regressions for operation context, literal reads and safe continuity."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import test_preparation_guard as existing


class OperationPreparationTest(unittest.TestCase):
    def setUp(self):
        self.f = existing.PreparationGuardTest()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        (self.f.workspace / ".git").mkdir()
        self.f.config["shell"] = "powershell"
        existing.guard.write_json(self.f.config_path, self.f.config)
        self.f.context, self.f.record_path = existing.guard.new_context(self.f.config, self.f.event)

    def include(self, record, directory):
        known = {source["path"] for source in record["sources"]}
        for path in existing.guard.instruction_sources(self.f.config, directory):
            if str(path) not in known:
                record["sources"].append({"path": str(path), "sha256": existing.guard.digest(path), "purpose": "Affected operation context"})

    def shell_event(self, command, **arguments):
        return dict(self.f.event, tool_name="Bash", tool_input=dict(command=command, **arguments))

    def test_missing_workdir_is_bound_to_the_unique_prepared_directory(self):
        f = self.f
        other = f.root / "other directory's"
        other.mkdir()
        command = "& '" + sys.executable.replace("'", "''") + "' -B -c 'import os; print(os.getcwd())'"
        record = f.ready()
        record["commands"] = [{"command": command, "cwd": str(other), "purpose": "Inspect actual directory"}]
        self.include(record, other)
        existing.guard.write_json(f.record_path, record)
        result = f.process(self.shell_event(command))
        self.assertFalse(f.denied(result), result)
        rewritten = result["hookSpecificOutput"]["updatedInput"]["command"]
        self.assertNotEqual(command, rewritten)
        shell = shutil.which("pwsh")
        if not shell:
            self.skipTest("Real PowerShell execution requires pwsh")
        process = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-Command", rewritten], cwd=f.workspace, capture_output=True, text=True, check=True)
        self.assertEqual(other, Path(process.stdout.strip()))

    def test_missing_workdir_with_multiple_prepared_directories_is_denied(self):
        f = self.f
        record = f.ready()
        command = "Write-Output 'probe'"
        record["commands"] = [{"command": command, "cwd": str(path), "purpose": "Ambiguous directory fixture"} for path in (f.workspace, f.root)]
        existing.guard.write_json(f.record_path, record)
        self.assertTrue(f.denied(f.process(self.shell_event(command))))

    def test_failed_directory_change_prevents_the_payload_from_running(self):
        shell = shutil.which("pwsh")
        if not shell:
            self.skipTest("Real PowerShell execution requires pwsh")
        f = self.f
        other = f.root / "vanishing-directory"
        other.mkdir()
        canary = f.root / "must-not-exist.txt"
        command = "trap { continue }; [IO.File]::WriteAllText('" + str(canary).replace("'", "''") + "', 'forbidden')"
        record = f.ready()
        record["commands"] = [{"command": command, "cwd": str(other), "purpose": "Directory-race regression"}]
        self.include(record, other)
        existing.guard.write_json(f.record_path, record)
        result = f.process(self.shell_event(command))
        self.assertFalse(f.denied(result), result)
        other.rmdir()  # This empty fixture directory disappears after validation.
        process = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-Command", result["hookSpecificOutput"]["updatedInput"]["command"]], cwd=f.workspace, capture_output=True, text=True)
        self.assertNotEqual(0, process.returncode)
        self.assertFalse(canary.exists())

    def test_nested_instruction_is_required_for_patch_and_rechecked(self):
        f = self.f
        directory = f.workspace / "src"
        directory.mkdir()
        policy = directory / "AGENTS.md"
        policy.write_text("Nested instructions", encoding="utf-8")
        target = directory / "example.txt"
        record = f.ready()
        record["write_paths"] = [str(target)]
        event = dict(f.event, tool_input={"command": f.command.replace(str(f.target), str(target))})
        existing.guard.write_json(f.record_path, record)
        self.assertTrue(f.denied(f.process(event)))
        self.include(record, directory)
        existing.guard.write_json(f.record_path, record)
        self.assertFalse(f.denied(f.process(event)))
        policy.write_text("Changed instructions", encoding="utf-8")
        self.assertTrue(f.denied(f.process(event)))

    def test_quoted_read_literals_are_distinct_from_shell_operators(self):
        for command in ("rg -n 'alpha|beta' AGENTS.md", "rg -n 'a$b;(c)' AGENTS.md", 'rg -n "alpha|beta" AGENTS.md'):
            with self.subTest(command=command):
                self.assertTrue(existing.guard.shell_read_only(command))
        for command in ("rg alpha AGENTS.md | Set-Content bad.txt", 'rg "$(Set-Content bad.txt x)" AGENTS.md', "rg --pre='evil' alpha", "rg alpha > bad.txt", "Get-Content 'a\u2019; Set-Content bad.txt x; # '"):
            with self.subTest(command=command):
                self.assertFalse(existing.guard.shell_read_only(command))

    def test_noncanonical_write_alias_cannot_bypass_path_checks(self):
        f = self.f
        record = f.ready()
        record["write_paths"] = []
        arguments = {"file_path": str(f.target), "content": "fixture"}
        record["tool_calls"] = [{"tool": "Write", "input_sha256": existing.guard.input_hash(arguments), "purpose": "Synthetic alias"}]
        existing.guard.write_json(f.record_path, record)
        self.assertTrue(f.denied(f.process(dict(f.event, tool_name="Write", tool_input=arguments))))

    def test_new_prompt_preserves_history_without_granting_readiness(self):
        f = self.f
        before = f.ready()
        f.process(dict(f.event, hook_event_name="UserPromptSubmit"))
        draft = existing.guard.read_json(f.record_path)
        self.assertEqual("draft", draft["status"])
        self.assertNotEqual(before["generation"], draft["generation"])
        self.assertEqual([], draft["commands"])
        previous = existing.guard.read_json(Path(draft["continuity"]["previous_record"]))
        self.assertEqual(before["steps"], previous["steps"])
        self.assertEqual(before["authorization"], previous["authorization"])
        self.assertTrue(f.denied(f.process()))

    def test_artifact_evidence_must_match_current_bytes(self):
        f = self.f
        artifact = f.workspace / "result.txt"
        artifact.write_text("Observed result", encoding="utf-8")
        record = f.ready()
        record["evidence"] = [{"kind": "artifact", "path": str(artifact), "sha256": existing.guard.digest(artifact), "claim": "Result exists"}]
        existing.guard.write_json(f.record_path, record)
        self.assertFalse(f.denied(f.process()))
        artifact.write_text("Changed result", encoding="utf-8")
        self.assertTrue(f.denied(f.process()))

    def test_workdir_disagreement_and_unconfigured_shell_are_denied(self):
        f = self.f
        record = f.ready()
        command = "Write-Output 'fixture'"
        record["commands"] = [{"command": command, "cwd": str(f.workspace), "purpose": "Bounded fixture"}]
        existing.guard.write_json(f.record_path, record)
        self.assertTrue(f.denied(f.process(self.shell_event(command, workdir=str(f.root)))))
        del f.config["shell"]
        existing.guard.write_json(f.config_path, f.config)
        self.assertTrue(f.denied(f.process(self.shell_event(command))))

    def test_mcp_write_requires_destination_scope_and_nested_policy(self):
        f = self.f
        directory = f.workspace / "src"
        directory.mkdir()
        (directory / "AGENTS.override.md").write_text("Nested override", encoding="utf-8")
        target = directory / "example.txt"
        arguments = {"path": str(target), "content": "fixture"}
        event = dict(f.event, tool_name="mcp__filesystem__write_file", tool_input=arguments)
        record = f.ready()
        record["tool_calls"] = [{"tool": event["tool_name"], "input_sha256": existing.guard.input_hash(arguments), "purpose": "Write fixture"}]
        existing.guard.write_json(f.record_path, record)
        self.assertTrue(f.denied(f.process(event)))
        record["write_paths"] = [str(target)]
        existing.guard.write_json(f.record_path, record)
        self.assertTrue(f.denied(f.process(event)))
        self.include(record, directory)
        existing.guard.write_json(f.record_path, record)
        self.assertFalse(f.denied(f.process(event)))

    def test_move_across_repositories_requires_both_instruction_chains(self):
        f = self.f
        other = f.root / "second-project"
        other.mkdir()
        (other / ".git").mkdir()
        (other / "AGENTS.md").write_text("Second project instructions", encoding="utf-8")
        target = other / "moved.txt"
        patch = f"*** Begin Patch\n*** Update File: {f.target}\n*** Move to: {target}\n@@\n-old\n+new\n*** End Patch"
        record = f.ready()
        record["write_paths"] = [str(f.target), str(target)]
        event = dict(f.event, tool_input={"command": patch})
        existing.guard.write_json(f.record_path, record)
        self.assertTrue(f.denied(f.process(event)))
        self.include(record, other)
        existing.guard.write_json(f.record_path, record)
        self.assertFalse(f.denied(f.process(event)))

    def test_new_nested_fallback_invalidates_operation_coverage(self):
        f = self.f
        (f.home / "config.toml").write_text('project_doc_fallback_filenames = ["TEAM.md"]', encoding="utf-8")
        folder = f.workspace / "src"
        folder.mkdir()
        target = folder / "file.txt"
        record = f.ready()
        record["write_paths"] = [str(target)]
        existing.guard.write_json(f.record_path, record)
        event = dict(f.event, tool_input={"command": f.command.replace(str(f.target), str(target))})
        self.assertFalse(f.denied(f.process(event)))
        (folder / "TEAM.md").write_text("New instructions", encoding="utf-8")
        self.assertTrue(f.denied(f.process(event)))

    def test_post_tool_receipt_contains_hashes_without_payload_or_success_claim(self):
        f = self.f
        before = existing.guard.read_json(f.record_path)
        event = dict(f.event, hook_event_name="PostToolUse", tool_use_id="fixture-call", turn_id="fixture-turn", tool_response={"output": "PRIVATE_FIXTURE_OUTPUT", "exit_code": 1})
        self.assertEqual({}, f.process(event))
        path = f.record_path.parent / "observations" / (existing.guard.input_hash("fixture-call") + ".json")
        receipt = existing.guard.read_json(path)
        self.assertEqual(existing.guard.input_hash(event["tool_response"]), receipt["response_sha256"])
        self.assertNotIn("PRIVATE_FIXTURE_OUTPUT", path.read_text(encoding="utf-8"))
        self.assertNotIn("passed", receipt)
        self.assertEqual(before, existing.guard.read_json(f.record_path))

    def test_post_tool_failure_reports_missing_evidence_without_claiming_denial(self):
        result = self.f.process(dict(self.f.event, hook_event_name="PostToolUse"))
        self.assertIn("systemMessage", result)
        self.assertNotIn("hookSpecificOutput", result)


if __name__ == "__main__":
    unittest.main()
