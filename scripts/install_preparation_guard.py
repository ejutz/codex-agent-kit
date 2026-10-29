"""Install user-global Codex preparation hooks without replacing other hooks.

Requires explicit authorization to modify the chosen Codex home. Trust review
is performed through Codex /hooks, never by manufacturing internal trust state.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import secrets
import shutil
import sys
import tomllib


def write_text(path, content):
    """Preserve a UTF-8 BOM when present and use CRLF on Windows installations."""
    bom = path.is_file() and path.read_bytes().startswith(b"\xef\xbb\xbf")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig" if bom else "utf-8", newline="\r\n") as stream:
        stream.write(content.replace("\r\n", "\n"))


def enabled_config(content):
    """Enable hooks while preserving all unrelated TOML text and comments."""
    parsed = tomllib.loads(content)
    # Inline hooks in the user config also merge with hooks.json. Do not alter them.
    lines = content.splitlines()
    start = next((index for index, line in enumerate(lines) if re.fullmatch(r"\s*\[features\]\s*(?:#.*)?", line)), None)
    if start is None:
        result = content.rstrip() + "\n\n[features]\nhooks = true\n"
    else:
        end = next((index for index in range(start + 1, len(lines)) if re.match(r"\s*\[", lines[index])), len(lines))
        index = next((index for index in range(start + 1, end) if re.match(r"\s*hooks\s*=", lines[index])), None)
        if index is None:
            lines.insert(start + 1, "hooks = true")
        else:
            comment = lines[index].split("#", 1)
            lines[index] = "hooks = true" + (" #" + comment[1] if len(comment) == 2 else "")
        result = "\n".join(lines) + "\n"
    actual = tomllib.loads(result)
    expected = dict(parsed)
    expected["features"] = dict(parsed.get("features", {}), hooks=True)
    if actual != expected:
        raise ValueError("Configuration edit would change unrelated TOML settings.")
    return result


def install(kit, home, python):
    """Back up exact global artifacts, then merge three synchronous hook events."""
    kit, home, python = (Path(path).resolve() for path in (kit, home, python))
    script = kit / "scripts/preparation_guard.py"
    if not script.is_file() or not python.is_file() or not (home / "AGENTS.md").is_file():
        raise ValueError("Verify the installed script, Python interpreter and existing global loader first.")
    config_path = home / "config.toml"
    previous_config = config_path.read_text(encoding="utf-8-sig") if config_path.is_file() else ""
    updated_config = enabled_config(previous_config)
    hooks_path = home / "hooks.json"
    hooks = json.loads(hooks_path.read_text(encoding="utf-8-sig")) if hooks_path.is_file() else {"hooks": {}}
    if not isinstance(hooks, dict) or not isinstance(hooks.get("hooks", {}), dict):
        raise ValueError("Existing hooks.json is not a supported object.")
    hooks.setdefault("hooks", {})
    control = home / "preparation-control"
    guard_config = control / "config.json"
    previous_guard = json.loads(guard_config.read_text(encoding="utf-8-sig")) if guard_config.is_file() else {}
    if not isinstance(previous_guard, dict):
        raise ValueError("Existing preparation configuration is not a supported object.")
    updated_guard = {"version": 1, "kit_root": str(kit), "codex_home": str(home), "state_root": str(control / "state")}
    if "discovery" in previous_guard:
        updated_guard["discovery"] = previous_guard["discovery"]
    # Both command paths are quoted. No shell-expanded user input is interpolated.
    command = '"' + str(python) + '" "' + str(script) + '" --config "' + str(guard_config) + '"'
    # Native Codex uses PowerShell on Windows: quoted executables need '&'.
    ps_quote = lambda value: "'" + str(value).replace("'", "''") + "'"
    command_windows = "& " + ps_quote(python) + " " + ps_quote(script) + " --config " + ps_quote(guard_config)
    for event in ("SessionStart", "UserPromptSubmit", "PreToolUse"):
        groups = hooks["hooks"].setdefault(event, [])
        for group in groups:
            group["hooks"] = [handler for handler in group.get("hooks", []) if
                              handler.get("statusMessage") != "Checking task preparation (agent kit)"]
        groups[:] = [group for group in groups if group.get("hooks")]
        groups.append({"hooks": [{"type": "command", "command": command, "commandWindows": command_windows,
                                   "timeout": 10, "statusMessage": "Checking task preparation (agent kit)",
                                   "additionalContextLimit": 1800}]})
    backup = control / "backups" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4))
    backup.mkdir(parents=True)
    manifest = {"kit_root": str(kit), "codex_home": str(home), "files": {}}
    for path in (config_path, hooks_path, guard_config):
        relative = str(path.relative_to(home))
        manifest["files"][relative] = path.is_file()
        if path.is_file():
            destination = backup / path.relative_to(home)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    write_text(backup / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    try:
        write_text(guard_config, json.dumps(updated_guard, indent=2) + "\n")
        write_text(hooks_path, json.dumps(hooks, indent=2) + "\n")
        write_text(config_path, updated_config)
    except Exception:
        # Restore only exact files this installation owned, not recursive trees.
        for relative, existed in manifest["files"].items():
            target = home / relative
            if existed:
                shutil.copy2(backup / relative, target)
            elif target.is_file():
                target.unlink()
        raise
    print(json.dumps({"installed": True, "hooks_file": str(hooks_path), "backup": str(backup),
                      "trust": "Review the exact hooks with /hooks in Codex before relying on them."}))
    return backup


def main():
    """Expose explicit installation paths; never infer a different user profile."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit-root", required=True)
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    install(args.kit_root, args.codex_home, args.python)


if __name__ == "__main__":
    main()
