"""Check preparation before supported Codex tools run; standard library only.

This is a workflow guardrail, not a security boundary or proof of comprehension.
Do not log prompts, command bodies, credentials, or entire tool inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import sys
import time
import tomllib

VERSION = 1
MAX_BYTES = 262144
MAX_AGE_SECONDS = 24 * 60 * 60
READ_TOOLS = {"view_image", "update_plan", "list_mcp_resources", "list_mcp_resource_templates", "read_mcp_resource"}
SHELL_TOOLS = {"Bash", "exec_command", "shell", "shell_command"}
PATCH_TOOLS = {"apply_patch", "Edit", "Write"}
PLACEHOLDERS = {"", "unknown", "todo", "tbd", "...", "<fill>", "pending"}
SUBMISSION_PREFIX = "CODEX_PREPARATION_V1:"


class PreparationError(ValueError):
    """An unmet preparation condition that must deny the dependent operation."""


def text(value):
    """Require useful, non-placeholder text without treating it as authorization."""
    return isinstance(value, str) and value.strip().lower() not in PLACEHOLDERS


def require(condition, message):
    """Raise an actionable policy failure instead of silently accepting bad state."""
    if not condition:
        raise PreparationError(message)


def absolute(value):
    """Resolve paths, including existing symlinks/junctions, before containment."""
    require(isinstance(value, str) and Path(value).is_absolute(), "An absolute path is required.")
    return Path(value).resolve()


def digest(path):
    """Fingerprint exact instruction bytes; this does not prove they were read."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    """Read a bounded UTF-8 JSON object, accepting a Windows UTF-8 BOM."""
    require(path.stat().st_size <= MAX_BYTES, "Preparation state exceeds the size limit.")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(data, dict), "Preparation state must be a JSON object.")
    return data


def write_json(path, data):
    """Atomically publish hook-owned context using Windows-compatible text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + secrets.token_hex(6) + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\r\n") as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    for attempt in range(5):
        try:
            os.replace(temporary, path)
            break
        except PermissionError as error:
            # Windows may briefly deny replacement while another handle closes.
            # Retry the same atomic publication; persistent failures still deny.
            if os.name != "nt" or getattr(error, "winerror", None) not in {5, 32, 33} or attempt == 4:
                raise
            time.sleep(0.025 * (attempt + 1))


def under(path, directory):
    """Use path containment, never a string-prefix comparison."""
    return path == directory or directory in path.parents


def read_toml(path):
    """Read local discovery settings without executing repository configuration."""
    if not path.is_file():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8-sig"))


def filenames(value, label):
    """Discovery names must not escape the directory being inspected."""
    require(isinstance(value, list) and all(
        isinstance(name, str) and name.strip() and name not in {".", ".."} and
        not any(char in name for char in ("/", "\\", ":")) for name in value),
        label + " must contain plain filenames.")
    return value


def project_directories(cwd, markers):
    """Use the nearest root marker (including a worktree .git file), or cwd."""
    chain = [cwd, *cwd.parents]
    for index, directory in enumerate(chain):
        if any((directory / marker).exists() for marker in markers):
            return list(reversed(chain[:index + 1]))
    return [cwd]


def discovery(config, cwd):
    """Resolve supported user/trusted-project settings and explicit host mapping.

    Hook events do not expose the full effective host config. Installations using
    profile, managed or CLI overrides must map these two options in discovery.
    """
    home = absolute(config["codex_home"])
    user = read_toml(home / "config.toml")
    overrides = config.get("discovery", {})
    require(isinstance(overrides, dict) and set(overrides) <= {
        "project_root_markers", "project_doc_fallback_filenames"}, "Invalid discovery mapping.")
    markers = filenames(overrides.get("project_root_markers", user.get("project_root_markers", [".git"])), "project_root_markers")
    directories = project_directories(cwd, markers)
    fallback = user.get("project_doc_fallback_filenames", [])
    projects = user.get("projects", {})
    require(isinstance(projects, dict), "Invalid project trust configuration.")
    trust = {}
    for path, settings in projects.items():
        if Path(path).is_absolute() and isinstance(settings, dict):
            trust[Path(path).resolve()] = settings.get("trust_level")
    trusted = next((trust[path] == "trusted" for path in reversed(directories) if path in trust), False)
    if trusted:
        for directory in directories:
            layer = read_toml(directory / ".codex/config.toml")
            require("project_root_markers" not in layer or layer["project_root_markers"] == markers or
                    "project_root_markers" in overrides,
                    "Map project-local root-marker overrides explicitly in guard discovery settings.")
            fallback = layer.get("project_doc_fallback_filenames", fallback)
    fallback = filenames(overrides.get("project_doc_fallback_filenames", fallback), "project_doc_fallback_filenames")
    return directories, list(dict.fromkeys(["AGENTS.override.md", "AGENTS.md", *fallback]))


def instruction_sources(config, cwd):
    """Locate mandatory kit owners plus global and repository instruction files."""
    kit = absolute(config["kit_root"])
    home = absolute(config["codex_home"])
    sources = [kit / "AGENTS.md", kit / "docs/implementation/workflow.md",
               kit / "docs/implementation/preparation-control.md", kit / "docs/testing/strategy.md",
               kit / "scripts/preparation_guard.py"]
    directories, project_names = discovery(config, cwd)
    for directory, names in [(home, ["AGENTS.override.md", "AGENTS.md"]),
                             *((directory, project_names) for directory in directories)]:
        for name in names:
            candidate = directory / name
            if candidate.is_file() and candidate.stat().st_size:
                sources.append(candidate.resolve())
                break
    require(any(path.parent == home for path in sources), "The global instruction loader is missing.")
    if (cwd / "docs/INDEX.md").is_file():
        sources.append(cwd / "docs/INDEX.md")
    sources = list(dict.fromkeys(path.resolve() for path in sources))
    for path in sources:
        require(path.is_file(), "A required instruction source is unavailable: " + str(path))
    return sources


def state_paths(config, session):
    """Keep untrusted session identifiers out of filesystem paths."""
    require(text(session), "The hook session identifier is missing.")
    key = hashlib.sha256(session.encode("utf-8")).hexdigest()
    directory = absolute(config["state_root"]) / key
    return directory / "context.json", directory / "preparation.json"


def invalidation_path(config_path, session):
    """Locate a lifecycle marker without depending on readable guard settings."""
    require(text(session), "The hook session identifier is missing.")
    key = hashlib.sha256(session.encode("utf-8")).hexdigest()
    return config_path.parent / (config_path.name + ".invalidations") / (key + ".json")


def new_context(config, event):
    """Start a new task generation; old records cannot authorize this one."""
    cwd = absolute(event.get("cwd"))
    session = event.get("session_id")
    context_path, record_path = state_paths(config, session)
    context = {"version": VERSION, "session_id": session, "workspace": str(cwd),
               "generation": secrets.token_hex(16), "created_at": time.time(),
               "turn_id": event.get("turn_id")}
    record = {"version": VERSION, "status": "draft", "session_id": session,
              "workspace": str(cwd), "generation": context["generation"],
              "task": "", "type": "", "complexity": "", "complexity_reason": "",
              "risk": "", "risk_reason": "", "objective": "", "scope": "",
              "steps": [], "verification": [], "risks": [], "recovery": "",
              "authorization": {"basis": "", "pending": []},
              "requirements": [], "pre_execution_checks": [],
              "sources": [], "prerequisite_errors": [],
              "write_paths": [], "commands": [], "tool_calls": []}
    # Invalidate the old generation before discovering potentially missing files.
    write_json(context_path, context)
    write_json(record_path, record)
    try:
        record["sources"] = [{"path": str(path), "sha256": digest(path), "purpose": "Applicable instruction source"}
                             for path in instruction_sources(config, cwd)]
    except (PreparationError, OSError, ValueError, KeyError, TypeError) as error:
        record["prerequisite_errors"] = [str(error) if isinstance(error, PreparationError) else type(error).__name__]
    write_json(record_path, record)
    return context, record_path


def context_for(config, event):
    """Recover only the current task; a changed workspace forces a new draft."""
    context_path, record_path = state_paths(config, event.get("session_id"))
    if not context_path.is_file():
        return new_context(config, event)
    context = read_json(context_path)
    if (absolute(event.get("cwd")) != absolute(context["workspace"]) or
            event.get("turn_id") is not None and context.get("turn_id") is not None and
            event["turn_id"] != context["turn_id"]):
        return new_context(config, event)
    return context, record_path


def validate(config, context, record, now=None):
    """Validate mechanically observable preparation conditions, not semantics."""
    require(record.get("version") == VERSION and record.get("status") == "ready", "Preparation is not ready.")
    for key in ("session_id", "generation", "workspace"):
        require(record.get(key) == context.get(key), "Preparation belongs to another session, task or workspace.")
    age = (time.time() if now is None else now) - context["created_at"]
    require(0 <= age <= MAX_AGE_SECONDS, "Preparation has expired; start a new task generation.")
    for key in ("task", "complexity_reason", "risk_reason", "objective", "scope", "recovery"):
        require(text(record.get(key)), "Missing preparation field: " + key)
    require(record.get("type") in {"analysis", "feature", "bugfix", "refactor", "tests", "infrastructure", "documentation"}, "Invalid task type.")
    require(record.get("complexity") in {"trivial", "bounded", "complex"}, "Invalid complexity.")
    require(record.get("risk") in {"low", "medium", "high"}, "Invalid risk.")
    for key in ("steps", "verification", "risks"):
        values = record.get(key)
        require(isinstance(values, list) and bool(values) and all(text(item) for item in values), "Missing verifiable preparation: " + key)
    auth = record.get("authorization")
    require(isinstance(auth, dict) and text(auth.get("basis")) and auth.get("pending") == [], "Authorization is missing or has pending gates.")
    source_list = record.get("sources")
    require(isinstance(source_list, list) and bool(source_list), "Instruction sources are missing.")
    sources = {}
    for source in source_list:
        path = absolute(source["path"])
        require(path.is_file() and digest(path) == source.get("sha256"), "An instruction source changed; re-read and reassess: " + str(path))
        require(text(source.get("purpose")), "An instruction source needs its applicability reason.")
        sources[str(path)] = source
    for path in instruction_sources(config, absolute(context["workspace"])):
        require(str(path) in sources, "A mandatory instruction source was omitted: " + str(path))
    for key in ("requirements", "pre_execution_checks"):
        checks = record.get(key)
        require(isinstance(checks, list) and bool(checks), "Missing checks: " + key)
        for check in checks:
            require(check.get("status") in {"passed", "not_applicable"} and text(check.get("evidence")), "A preparation requirement is unresolved: " + key)
            require(text(check.get("requirement")), "Each preparation check needs a requirement.")
            require(str(absolute(check.get("source"))) in sources, "Each requirement must cite a loaded instruction source.")
    require(isinstance(record.get("write_paths"), list), "write_paths must be a list.")
    for path in record["write_paths"]:
        absolute(path)
    for key in ("commands", "tool_calls"):
        require(isinstance(record.get(key), list), key + " must be a list.")


def shell_read_only(command):
    """Recognize a deliberately small read-only subset; reject unknown syntax.

    No variables, substitutions, redirects, invocation operators or script blocks.
    Pipelines can only append numeric Select-Object slicing to an accepted read.
    """
    if not isinstance(command, str) or re.search(r"[$`&><(){}\n\r]", command):
        return False
    if "|" in command:
        stages = command.split("|")
        if ";" in command or not shell_read_only(stages[0]):
            return False
        for stage in stages[1:]:
            try:
                args = shlex.split(stage.strip(), posix=True)
            except ValueError:
                return False
            if not args or args[0].lower() != "select-object" or len(args) < 3 or len(args) % 2 != 1:
                return False
            if any(args[i].lower() not in {"-first", "-last", "-skip"} or
                   not re.fullmatch(r"[0-9]+", args[i + 1]) for i in range(1, len(args), 2)):
                return False
        return True
    parts = command.split(";")
    for part in parts:
        try:
            args = shlex.split(part.strip(), posix=True)
        except ValueError:
            return False
        if not args:
            return False
        name = args[0].lower()
        if name in {"get-content", "get-childitem", "get-location", "resolve-path", "test-path", "get-command", "select-string", "get-filehash"}:
            continue
        if name == "git":
            tail = args[1:]
            if len(tail) >= 2 and tail[0] == "-c" and tail[1].startswith("safe.directory="):
                tail = tail[2:]
            if tail and tail[0] in {"status", "diff", "show", "log", "ls-files", "rev-parse"}:
                if not any(arg in {"--output", "--ext-diff", "--textconv", "--exec"} or arg.startswith(("--output=", "--ext-diff=", "--exec=")) for arg in tail):
                    continue
        if name == "rg":
            # Reject external preprocessors, archive helpers and config injection.
            if not any(arg.startswith(("--pre", "--hostname-bin", "--search-zip")) or arg == "-z" for arg in args[1:]):
                continue
        return False
    return True


def inspection_only(event):
    """Recognize explicit read adapters before touching preparation state.

    Filesystem MCP names here assume the installed, trusted filesystem server's
    read contract. Unknown servers, arbitrary JS/Python and extra inputs do not
    become read-only merely because their name or description claims it.
    """
    tool = event.get("tool_name")
    arguments = event.get("tool_input", {})
    if tool in READ_TOOLS:
        if tool == "update_plan" and isinstance(arguments, dict):
            explanation = arguments.get("explanation", "")
            if isinstance(explanation, str) and explanation.startswith(SUBMISSION_PREFIX):
                return False  # Submission must validate/store data, even on the inspection path.
        return True
    if tool == "mcp__filesystem__read_file":
        return (isinstance(arguments, dict) and set(arguments) == {"path"} and
                isinstance(arguments["path"], str) and Path(arguments["path"]).is_absolute())
    if tool in SHELL_TOOLS and isinstance(arguments, dict):
        # Do not admit alternate executable/script input fields via this exception.
        if set(arguments) - {"command", "cmd", "workdir", "description", "timeout",
                             "timeout_ms", "yield_time_ms", "max_output_tokens", "login",
                             "tty", "sandbox_permissions", "justification", "prefix_rule"}:
            return False
        if "command" in arguments and "cmd" in arguments:
            return False
        return shell_read_only(arguments.get("command", arguments.get("cmd")))
    return False


def patch_paths(command, cwd):
    """Extract every source/destination, rejecting unknown patch control lines."""
    require(isinstance(command, str) and command.startswith("*** Begin Patch\n"), "Unsupported patch format.")
    paths = []
    ended = False
    for line in command.splitlines()[1:]:
        match = re.fullmatch(r"\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)", line)
        if match:
            value = Path(match.group(1))
            paths.append((value if value.is_absolute() else cwd / value).resolve())
        elif line == "*** End Patch":
            ended = True
        elif line.startswith("*** ") and line != "*** End of File":
            raise PreparationError("Unsupported patch control line.")
    require(bool(paths) and ended, "A complete file patch is required.")
    return paths


def input_hash(tool_input):
    """Bind non-shell tool preparation to the exact JSON arguments."""
    return hashlib.sha256(json.dumps(tool_input, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def submission(tool, tool_input, command):
    """Recognize only data-bearing metadata or an exact literal PowerShell call."""
    if tool == "update_plan" and isinstance(tool_input, dict):
        explanation = tool_input.get("explanation", "")
        if isinstance(explanation, str) and explanation.startswith(SUBMISSION_PREFIX):
            return explanation[len(SUBMISSION_PREFIX):], dict(tool_input, explanation="Preparation verified by the global hook.")
    if tool in SHELL_TOOLS and isinstance(command, str):
        match = re.fullmatch(r"Write-Output 'CODEX_PREPARATION_V1:((?:[^']|'')*)'", command)
        if match:
            updated = dict(tool_input)
            key = "command" if "command" in updated else "cmd"
            updated[key] = "Write-Output 'Preparation verified by the global hook.'"
            return match.group(1).replace("''", "'"), updated
    return None


def decision(config, event):
    """Return deny/reason, or allow without overriding normal host permissions."""
    if inspection_only(event):
        return None
    context, record_path = context_for(config, event)
    tool = event.get("tool_name")
    tool_input = event.get("tool_input", {})
    command = tool_input.get("command", tool_input.get("cmd")) if isinstance(tool_input, dict) else tool_input
    cwd = absolute(event["cwd"])
    tool_cwd = absolute(tool_input.get("workdir", str(cwd))) if isinstance(tool_input, dict) else cwd
    prepared = submission(tool, tool_input, command)
    if prepared:
        # Context and records are owned by the callback, outside the tool sandbox.
        # Never require an agent to write into the protected Codex home itself.
        previous = read_json(record_path) if record_path.is_file() else {}
        write_json(record_path, dict(previous, status="draft"))
        raw, updated = prepared
        require(len(raw.encode("utf-8")) <= MAX_BYTES, "Preparation submission exceeds the size limit.")
        record = json.loads(raw)
        validate(config, context, record)
        write_json(record_path, record)
        return {"permissionDecision": "allow", "updatedInput": updated}
    paths = patch_paths(command.replace("\r\n", "\n"), cwd) if tool == "apply_patch" and isinstance(command, str) else []
    try:
        record = read_json(record_path)
        validate(config, context, record)
        if tool == "apply_patch":
            approved = [absolute(path) for path in record["write_paths"]]
            control = absolute(config["state_root"])
            require(all(not under(path, control) for path in paths), "Hook-owned context cannot be modified through task writes.")
            require(paths and all(any(under(path, root) for root in approved) for path in paths), "Patch touches paths outside the prepared write scope.")
            return None
        if tool in SHELL_TOOLS:
            require(any(item.get("command") == command and absolute(item.get("cwd")) == tool_cwd and text(item.get("purpose")) for item in record["commands"]), "This exact command/cwd has not been included in preparation.")
            return None
        require(any(item.get("tool") == tool and item.get("input_sha256") == input_hash(tool_input) and text(item.get("purpose")) for item in record["tool_calls"]), "This tool call has not been included in preparation.")
        return None
    except (PreparationError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        return str(error) + " Prepare " + str(record_path) + "; see " + str(absolute(config["kit_root"]) / "docs/implementation/preparation-control.md")


def hook(config, event):
    """Handle lifecycle events, invalidation and synchronous tool checks."""
    name = event.get("hook_event_name")
    if name in {"SessionStart", "UserPromptSubmit"}:
        context, path = new_context(config, event)
        message = ("Before task writes, read the global instruction loader and applicable kit/project instructions. "
                   "Publish the required plan, then complete the draft preparation record at " + str(path) +
                   ". Read that draft, complete it as JSON with status=ready after resolving prerequisites and authorization. "
                   "Register it through update_plan.explanation='CODEX_PREPARATION_V1:' followed by the JSON, "
                   "or the exact PowerShell command Write-Output 'CODEX_PREPARATION_V1:<JSON>' (double embedded apostrophes). "
                   "The hook validates and stores the data; do not patch protected state files yourself. "
                   "Exact mutating/unknown shell commands and cwd must be listed in commands. "
                   "Instructions: " + str(absolute(config["kit_root"]) / "docs/implementation/preparation-control.md"))
        errors = read_json(path).get("prerequisite_errors", [])
        if errors:
            message = ("Preparation prerequisites are unresolved: " + "; ".join(errors) +
                       ". Diagnostic inspection may continue; dependent mutations remain blocked. " + message)
        return {"hookSpecificOutput": {"hookEventName": name, "additionalContext": message}}
    if name == "PreToolUse":
        reason = decision(config, event)
        if isinstance(reason, dict):
            return {"hookSpecificOutput": dict(reason, hookEventName=name)}
        if reason:
            return {"hookSpecificOutput": {"hookEventName": name, "permissionDecision": "deny", "permissionDecisionReason": reason}}
        return {}  # Never grant host approval or bypass another hook.
    return {}


def main():
    """Load fixed installation config and deny handled validation failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    event = {}
    lifecycle_invalidated = False
    try:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, "Hook event exceeds the size limit.")
        event = json.loads(raw.decode("utf-8-sig"))
        require(isinstance(event, dict), "Hook event must be an object.")
        if event.get("hook_event_name") == "PreToolUse" and inspection_only(event):
            result = {}  # Diagnostics remain available even if guard configuration is missing.
        else:
            config_path = absolute(args.config)
            pending = invalidation_path(Path(args.config), event.get("session_id"))
            lifecycle = event.get("hook_event_name") in {"SessionStart", "UserPromptSubmit"}
            if lifecycle:
                # Persist invalidation even when config cannot reveal the state directory.
                write_json(pending, {"invalidated": True})
                lifecycle_invalidated = True
            config = read_json(config_path)
            if not lifecycle and pending.is_file():
                new_context(config, event)
                pending.unlink()
            result = hook(config, event)
            if lifecycle:
                pending.unlink()
    except Exception as error:
        # Fail closed for handled errors; host timeouts/missing runtimes are a separate limitation.
        reason = "Preparation guard could not validate prerequisites: " + type(error).__name__
        if isinstance(error, PreparationError):
            reason += ": " + str(error)
        if isinstance(event, dict) and event.get("hook_event_name") in {"SessionStart", "UserPromptSubmit"}:
            if lifecycle_invalidated:
                result = {"hookSpecificOutput": {"hookEventName": event["hook_event_name"],
                          "additionalContext": reason + ". Diagnostic inspection may continue; dependent mutations remain blocked."}}
            else:
                result = {"continue": False, "stopReason": reason + ". Could not invalidate previous preparation safely."}
        else:
            result = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
