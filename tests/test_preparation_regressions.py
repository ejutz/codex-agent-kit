"""Regressions for instruction discovery and preparation-time inspection."""

import json
import subprocess
import sys
import unittest
from unittest import mock

import test_preparation_guard as existing


class PreparationRegressionTest(unittest.TestCase):
    """Reuse disposable fixtures without inheriting or duplicating their tests."""

    def setUp(self):
        self.fixture = existing.PreparationGuardTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def sources(self, cwd=None):
        fixture = self.fixture
        return existing.guard.instruction_sources(fixture.config, cwd or fixture.workspace)

    def configure(self, content):
        (self.fixture.home / "config.toml").write_text(content, encoding="utf-8")

    def inspect(self, command, **extra):
        fixture = self.fixture
        event = dict(fixture.event, tool_name="Bash", tool_input={"command": command}, **extra)
        return fixture.process(event)

    def test_transient_windows_replace_failure_retries_the_same_atomic_publication(self):
        guard = existing.guard
        path = self.fixture.root / "atomic.json"
        path.write_text('{"old": true}', encoding="utf-8")
        error = PermissionError("Temporary sharing conflict")
        error.winerror = 32
        replace = guard.os.replace
        attempts = []

        def transient(source, target):
            attempts.append((source, target))
            if len(attempts) == 1:
                self.assertEqual({"old": True}, guard.read_json(path))
                raise error
            return replace(source, target)

        with mock.patch.object(guard.os, "name", "nt"), mock.patch.object(guard.os, "replace", side_effect=transient), mock.patch.object(guard.time, "sleep"):
            guard.write_json(path, {"new": True})
        self.assertEqual(attempts[0], attempts[1])
        self.assertEqual({"new": True}, guard.read_json(path))

    def test_persistent_windows_replace_failure_is_bounded_and_preserves_previous_file(self):
        guard = existing.guard
        path = self.fixture.root / "atomic.json"
        path.write_text('{"old": true}', encoding="utf-8")
        error = PermissionError("Persistent access denial")
        error.winerror = 5
        with mock.patch.object(guard.os, "name", "nt"), mock.patch.object(guard.os, "replace", side_effect=error) as replace, mock.patch.object(guard.time, "sleep"):
            with self.assertRaises(PermissionError):
                guard.write_json(path, {"new": True})
        self.assertEqual(5, replace.call_count)
        self.assertEqual({"old": True}, guard.read_json(path))

    def test_git_boundary_excludes_an_unrelated_ancestor(self):
        fixture = self.fixture
        (fixture.workspace / ".git").mkdir()
        outside = fixture.root / "AGENTS.md"
        outside.write_text("Unrelated parent policy", encoding="utf-8")
        child = fixture.workspace / "src"
        child.mkdir()
        local = child / "AGENTS.md"
        local.write_text("Source-specific policy", encoding="utf-8")
        sources = self.sources(child)
        self.assertNotIn(outside, sources)
        self.assertIn(fixture.workspace / "AGENTS.md", sources)
        self.assertIn(local, sources)
        self.assertLess(sources.index(fixture.workspace / "AGENTS.md"), sources.index(local))

    def test_worktree_git_file_is_a_project_boundary(self):
        fixture = self.fixture
        (fixture.workspace / ".git").write_text("gitdir: /fixture/metadata", encoding="utf-8")
        outside = fixture.root / "AGENTS.md"
        outside.write_text("Outside the worktree", encoding="utf-8")
        self.assertNotIn(outside, self.sources())
        self.assertIn(fixture.workspace / "AGENTS.md", self.sources())

    def test_nearest_nested_repository_boundary_wins(self):
        fixture = self.fixture
        (fixture.workspace / ".git").mkdir()
        child = fixture.workspace / "independent"
        child.mkdir()
        (child / ".git").mkdir()
        local = child / "AGENTS.md"
        local.write_text("Independent repository", encoding="utf-8")
        sources = self.sources(child)
        self.assertNotIn(fixture.workspace / "AGENTS.md", sources)
        self.assertIn(local, sources)

    def test_no_matching_project_marker_uses_only_the_current_directory(self):
        fixture = self.fixture
        # Temporary files may themselves be inside the authoring Git checkout.
        # A distinct absent marker makes the no-project case independent of that host.
        self.configure('project_root_markers = [".absent-fixture-root"]\n')
        ancestor = fixture.root / "AGENTS.md"
        ancestor.write_text("Not an applicable project", encoding="utf-8")
        self.assertNotIn(ancestor, self.sources())
        self.assertIn(fixture.workspace / "AGENTS.md", self.sources())

    def test_custom_marker_selects_the_project_root(self):
        fixture = self.fixture
        self.configure('project_root_markers = [".fixture-root"]\n')
        (fixture.workspace / ".fixture-root").write_text("", encoding="utf-8")
        child = fixture.workspace / "src"
        child.mkdir()
        (child / "AGENTS.md").write_text("Local rules", encoding="utf-8")
        outside = fixture.root / "AGENTS.md"
        outside.write_text("Unrelated", encoding="utf-8")
        sources = self.sources(child)
        self.assertIn(fixture.workspace / "AGENTS.md", sources)
        self.assertIn(child / "AGENTS.md", sources)
        self.assertNotIn(outside, sources)

    def test_empty_marker_configuration_disables_parent_discovery(self):
        fixture = self.fixture
        self.configure("project_root_markers = []\n")
        (fixture.workspace / ".git").mkdir()
        child = fixture.workspace / "src"
        child.mkdir()
        (child / "AGENTS.md").write_text("Only this directory", encoding="utf-8")
        self.assertNotIn(fixture.workspace / "AGENTS.md", self.sources(child))
        self.assertIn(child / "AGENTS.md", self.sources(child))

    def test_configured_fallback_is_used_and_obeys_priority(self):
        fixture = self.fixture
        self.configure('project_doc_fallback_filenames = ["TEAM_GUIDE.md", "LOCAL_GUIDE.md"]\n')
        first = fixture.workspace / "TEAM_GUIDE.md"
        second = fixture.workspace / "LOCAL_GUIDE.md"
        first.write_text("First fallback", encoding="utf-8")
        second.write_text("Second fallback", encoding="utf-8")
        primary = fixture.workspace / "AGENTS.md"
        override = fixture.workspace / "AGENTS.override.md"
        override.write_text("Override", encoding="utf-8")
        sources = self.sources()
        self.assertIn(override, sources)
        self.assertNotIn(primary, sources)
        self.assertNotIn(first, sources)
        override.unlink()
        sources = self.sources()
        self.assertIn(primary, sources)
        self.assertNotIn(first, sources)
        primary.unlink()
        sources = self.sources()
        self.assertIn(first, sources)
        self.assertNotIn(second, sources)

    def test_empty_standard_instruction_file_does_not_hide_fallback(self):
        fixture = self.fixture
        self.configure('project_doc_fallback_filenames = ["TEAM_GUIDE.md"]\n')
        (fixture.workspace / "AGENTS.md").write_text("", encoding="utf-8")
        (fixture.workspace / "AGENTS.override.md").write_text("", encoding="utf-8")
        fallback = fixture.workspace / "TEAM_GUIDE.md"
        fallback.write_text("Effective instructions", encoding="utf-8")
        sources = self.sources()
        self.assertIn(fallback, sources)
        self.assertNotIn(fixture.workspace / "AGENTS.md", sources)
        self.assertNotIn(fixture.workspace / "AGENTS.override.md", sources)

    def test_trusted_project_configuration_can_supply_the_fallback(self):
        fixture = self.fixture
        (fixture.workspace / ".git").mkdir()
        (fixture.workspace / "AGENTS.md").unlink()
        local_config = fixture.workspace / ".codex/config.toml"
        local_config.parent.mkdir()
        local_config.write_text('project_doc_fallback_filenames = ["PROJECT_GUIDE.md"]\n', encoding="utf-8")
        fallback = fixture.workspace / "PROJECT_GUIDE.md"
        fallback.write_text("Project instructions", encoding="utf-8")
        self.configure(f'[projects."{fixture.workspace.as_posix()}"]\ntrust_level = "trusted"\n')
        self.assertIn(fallback, self.sources())

    def test_untrusted_project_configuration_cannot_change_discovery(self):
        fixture = self.fixture
        (fixture.workspace / ".git").mkdir()
        (fixture.workspace / "AGENTS.md").unlink()
        local_config = fixture.workspace / ".codex/config.toml"
        local_config.parent.mkdir()
        local_config.write_text('project_doc_fallback_filenames = ["PROJECT_GUIDE.md"]\n', encoding="utf-8")
        fallback = fixture.workspace / "PROJECT_GUIDE.md"
        fallback.write_text("Untrusted project instructions", encoding="utf-8")
        for content in ("", f'[projects."{fixture.workspace.as_posix()}"]\ntrust_level = "untrusted"\n'):
            with self.subTest(configuration=content):
                self.configure(content)
                self.assertNotIn(fallback, self.sources())
        local_config.write_text("This is not valid TOML", encoding="utf-8")
        self.assertNotIn(fallback, self.sources(), "An ignored layer must not prevent independent discovery")

    def test_nearer_trusted_project_configuration_overrides_outer_fallback(self):
        fixture = self.fixture
        (fixture.workspace / ".git").mkdir()
        (fixture.workspace / "AGENTS.md").unlink()
        child = fixture.workspace / "src"
        child.mkdir()
        self.configure(f'[projects."{fixture.workspace.as_posix()}"]\ntrust_level = "trusted"\n')
        for directory, name in ((fixture.workspace, "OUTER_GUIDE.md"), (child, "NEAR_GUIDE.md")):
            config = directory / ".codex/config.toml"
            config.parent.mkdir()
            config.write_text(f'project_doc_fallback_filenames = ["{name}"]\n', encoding="utf-8")
            (child / name).write_text(name, encoding="utf-8")
        sources = self.sources(child)
        self.assertIn(child / "NEAR_GUIDE.md", sources)
        self.assertNotIn(child / "OUTER_GUIDE.md", sources)

    def test_explicit_host_discovery_mapping_overrides_global_and_project_settings(self):
        fixture = self.fixture
        (fixture.workspace / ".git").mkdir()
        (fixture.workspace / "AGENTS.md").unlink()
        self.configure('project_root_markers = [".unused-root"]\n'
                       'project_doc_fallback_filenames = ["GLOBAL_GUIDE.md"]\n'
                       f'[projects."{fixture.workspace.as_posix()}"]\ntrust_level = "trusted"\n')
        child = fixture.workspace / "src"
        child.mkdir()
        config = fixture.workspace / ".codex/config.toml"
        config.parent.mkdir()
        config.write_text('project_root_markers = [".project-root"]\n'
                          'project_doc_fallback_filenames = ["PROJECT_GUIDE.md"]\n', encoding="utf-8")
        for name in ("GLOBAL_GUIDE.md", "PROJECT_GUIDE.md", "HOST_GUIDE.md"):
            (fixture.workspace / name).write_text(name, encoding="utf-8")
            (child / name).write_text(name, encoding="utf-8")
        fixture.config["discovery"] = {"project_root_markers": [".git"],
                                       "project_doc_fallback_filenames": ["HOST_GUIDE.md"]}
        sources = self.sources(child)
        self.assertIn(fixture.workspace / "HOST_GUIDE.md", sources)
        self.assertIn(child / "HOST_GUIDE.md", sources)
        for name in ("GLOBAL_GUIDE.md", "PROJECT_GUIDE.md"):
            self.assertNotIn(fixture.workspace / name, sources)
            self.assertNotIn(child / name, sources)

    def test_invalid_discovery_names_deny_readiness_but_allow_diagnosis(self):
        fixture = self.fixture
        record = fixture.ready()
        for setting in (
            'project_doc_fallback_filenames = ["../outside.md"]\n',
            'project_root_markers = ["../.git"]\n',
            'project_doc_fallback_filenames = "GUIDE.md"\n',
            'project_root_markers = [42]\n',
        ):
            with self.subTest(setting=setting):
                self.configure(setting)
                with self.assertRaises(existing.guard.PreparationError):
                    existing.guard.validate(fixture.config, fixture.context, record)
                self.assertFalse(fixture.denied(self.inspect("Get-Content AGENTS.md")))
                self.assertTrue(fixture.denied(fixture.process()))

    def test_missing_guard_configuration_still_allows_concrete_read_but_denies_patch(self):
        fixture = self.fixture
        missing = fixture.root / "absent-guard-config.json"
        read_event = dict(fixture.event, tool_name="Bash", tool_input={"command": "Get-Content AGENTS.md"})
        for event, should_deny in ((read_event, False), (fixture.event, True)):
            with self.subTest(tool=event["tool_name"]):
                process = subprocess.run([sys.executable, "-B", str(existing.SCRIPT), "--config", str(missing)],
                                         input=json.dumps(event), text=True, capture_output=True, check=True)
                self.assertEqual(should_deny, fixture.denied(json.loads(process.stdout)))

    def test_missing_global_allows_diagnosis_but_not_task_mutations(self):
        fixture = self.fixture
        (fixture.home / "AGENTS.md").unlink()
        result = self.inspect("Get-Content AGENTS.md", session_id="diagnose-missing-global")
        self.assertFalse(fixture.denied(result), result)
        for tool, tool_input in (
            ("apply_patch", {"command": fixture.command}),
            ("Bash", {"command": "Set-Content canary.txt forbidden"}),
        ):
            with self.subTest(tool=tool):
                event = dict(fixture.event, session_id="diagnose-missing-global",
                             tool_name=tool, tool_input=tool_input)
                result = fixture.execute_after_hook(event, lambda: fixture.target.write_text("forbidden"))
                self.assertTrue(fixture.denied(result), result)
                self.assertFalse(fixture.target.exists())

    def test_missing_kit_source_does_not_block_lifecycle_or_diagnostic_read(self):
        fixture = self.fixture
        (fixture.kit / "docs/testing/strategy.md").unlink()
        for event_name in ("SessionStart", "UserPromptSubmit"):
            with self.subTest(event_name=event_name):
                session = "missing-kit-" + event_name
                event = dict(fixture.event, session_id=session, hook_event_name=event_name)
                result = fixture.process(event)
                self.assertIsNot(result.get("continue"), False, result)
                diagnostic = result.get("hookSpecificOutput", {}).get("additionalContext", "") or result.get("systemMessage", "")
                self.assertTrue(diagnostic, result)
                self.assertFalse(fixture.denied(self.inspect("Get-Content AGENTS.md", session_id=session)))
                mutation = dict(fixture.event, session_id=session)
                self.assertTrue(fixture.denied(fixture.process(mutation)))

    def test_failed_discovery_on_new_prompt_cannot_reuse_previous_ready_record(self):
        fixture = self.fixture
        fixture.ready()
        global_path = fixture.home / "AGENTS.md"
        original = global_path.read_bytes()
        global_path.unlink()
        result = fixture.process(dict(fixture.event, hook_event_name="UserPromptSubmit", turn_id="new-task"))
        self.assertIsNot(result.get("continue"), False, result)
        global_path.write_bytes(original)
        self.assertTrue(fixture.denied(fixture.process()), "A new task must still require its own preparation")

    def test_bounded_readonly_pipeline_is_available_before_preparation(self):
        result = self.inspect("Get-Content 'guide with spaces.md' | Select-Object -First 20")
        self.assertFalse(self.fixture.denied(result), result)

    def test_repaired_guard_config_cannot_revive_preparation_from_an_earlier_prompt(self):
        fixture = self.fixture
        original = fixture.config_path.read_bytes()
        for broken in (None, "{invalid json"):
            with self.subTest(configuration=broken):
                old_record = fixture.ready()
                if broken is None:
                    fixture.config_path.unlink()
                else:
                    fixture.config_path.write_text(broken, encoding="utf-8")
                result = fixture.process(dict(fixture.event, hook_event_name="UserPromptSubmit"))
                self.assertIsNot(result.get("continue"), False, result)
                self.assertFalse(fixture.denied(self.inspect("Get-Content AGENTS.md")))
                fixture.config_path.write_bytes(original)
                result = fixture.execute_after_hook(fixture.event, lambda: fixture.target.write_text("forbidden"))
                self.assertTrue(fixture.denied(result), result)
                self.assertFalse(fixture.target.exists())
                current = existing.guard.read_json(fixture.record_path)
                self.assertNotEqual(old_record["generation"], current["generation"])
                fixture.ready()
                self.assertFalse(fixture.denied(fixture.process()), "Fresh preparation must still be usable")

    def test_lifecycle_stops_when_durable_invalidation_cannot_be_saved(self):
        fixture = self.fixture
        fixture.ready()
        pending = existing.guard.invalidation_path(fixture.config_path, fixture.event["session_id"])
        pending.parent.write_text("A file prevents creating the marker directory", encoding="utf-8")
        result = fixture.process(dict(fixture.event, hook_event_name="UserPromptSubmit"))
        self.assertIs(result.get("continue"), False, result)
        self.assertIn("invalidate previous preparation", result["stopReason"])

    def test_readonly_pipeline_exception_does_not_allow_mutation_or_code(self):
        for command in (
            "Get-Content AGENTS.md | Set-Content canary.txt",
            "Get-Content AGENTS.md | Select-Object -First 20; Set-Content canary.txt bad",
            "Get-Content AGENTS.md | Select-Object -Property @{Name='X';Expression={Set-Content canary.txt bad}}",
            "Get-Content AGENTS.md | Select-Object -First 20 > canary.txt",
        ):
            with self.subTest(command=command):
                self.assertTrue(self.fixture.denied(self.inspect(command)))

    def test_explicit_filesystem_read_adapter_accepts_only_valid_read_arguments(self):
        fixture = self.fixture
        reader = dict(fixture.event, tool_name="mcp__filesystem__read_file",
                      tool_input={"path": str(fixture.workspace / "AGENTS.md")})
        self.assertFalse(fixture.denied(fixture.process(reader)))
        for arguments in (
            {"path": 42},
            {"path": str(fixture.target), "content": "forbidden"},
            {"path": str(fixture.target), "code": "writeSomething()"},
            [],
        ):
            with self.subTest(arguments=arguments):
                self.assertTrue(fixture.denied(fixture.process(dict(reader, tool_input=arguments))))

    def test_read_adapter_does_not_trust_other_tool_names_or_arbitrary_execution(self):
        fixture = self.fixture
        for tool, arguments in (
            ("mcp__filesystem__write_file", {"path": str(fixture.target), "content": "forbidden"}),
            ("mcp__unknown__read_file", {"path": str(fixture.target)}),
            ("mcp__node_repl__js", {"code": "await fs.writeFile('canary.txt', 'forbidden')"}),
            ("Bash", {"command": "python -c 'print(1)'"}),
        ):
            with self.subTest(tool=tool):
                event = dict(fixture.event, tool_name=tool, tool_input=arguments)
                self.assertTrue(fixture.denied(fixture.process(event)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
