"""Verify global installation preserves existing configuration and hooks."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/install_preparation_guard.py"
spec = importlib.util.spec_from_file_location("install_preparation_guard", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallPreparationGuardTest(unittest.TestCase):
    """Exercise repeat installation and backups in a disposable Codex home."""

    def test_preserves_unrelated_toml_and_hook_handlers_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home, kit = root / "home", root / "kit"
            home.mkdir()
            (kit / "scripts").mkdir(parents=True)
            (kit / "scripts/preparation_guard.py").write_text("# fixture", encoding="utf-8")
            (home / "AGENTS.md").write_text("Global loader", encoding="utf-8")
            original = '# preserve comment\nmodel = "existing"\n[features]\nhooks = false # preserve\nother = true\n[projects."example"]\ntrust_level = "trusted"\n'
            (home / "config.toml").write_text(original, encoding="utf-8")
            unrelated = {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "existing-script"}]}]}}
            (home / "hooks.json").write_text(json.dumps(unrelated), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                backup = installer.install(kit, home, sys.executable)
                guard_path = home / "preparation-control/config.json"
                guard_config = json.loads(guard_path.read_text(encoding="utf-8"))
                mapping = {"project_root_markers": [".git"], "project_doc_fallback_filenames": ["TEAM_GUIDE.md"]}
                guard_config["discovery"] = mapping
                guard_path.write_text(json.dumps(guard_config), encoding="utf-8")
                installer.install(kit, home, sys.executable)
            self.assertEqual(mapping, json.loads(guard_path.read_text(encoding="utf-8"))["discovery"])
            self.assertEqual(original, (backup / "config.toml").read_text(encoding="utf-8"))
            config = tomllib.loads((home / "config.toml").read_text(encoding="utf-8"))
            self.assertEqual("existing", config["model"])
            self.assertTrue(config["features"]["other"])
            self.assertTrue(config["features"]["hooks"])
            self.assertIn("# preserve comment", (home / "config.toml").read_text(encoding="utf-8"))
            hooks = json.loads((home / "hooks.json").read_text(encoding="utf-8"))
            self.assertEqual(unrelated["hooks"]["PreToolUse"][0], hooks["hooks"]["PreToolUse"][0])
            self.assertEqual(2, len(hooks["hooks"]["PreToolUse"]))
            self.assertEqual(1, len(hooks["hooks"]["SessionStart"]))
            self.assertEqual(1, len(hooks["hooks"]["UserPromptSubmit"]))
            windows = hooks["hooks"]["PreToolUse"][-1]["hooks"][0]["commandWindows"]
            self.assertTrue(windows.startswith("& '"))
            self.assertIn(str(Path(sys.executable).resolve()), windows)

    def test_unsupported_configuration_fails_before_writes(self):
        original = 'features = { hooks = false, other = true }\n'
        with self.assertRaises((ValueError, tomllib.TOMLDecodeError)):
            installer.enabled_config(original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
