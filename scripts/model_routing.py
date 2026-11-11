"""Select a Codex model from a prepared task assessment and optionally run a read-only turn."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib


RC_VERSION = "1.2.0-rc.4"
CHOICES = {
    "kind": {"documentation", "configuration", "code", "analysis"},
    "complexity": {"trivial", "bounded", "complex"},
    "scope": {"local", "related", "cross_component", "cross_repository"},
    "risk": {"low", "medium", "high"},
    "uncertainty": {"low", "material"},
    "reasoning": {"routine", "advanced"},
    "dependencies": {"none", "known", "unknown"},
    "delegation_value": {"worthwhile", "low"},
}
ESCALATION_SIGNALS = {
    "scope_growth", "unexpected_dependency", "additional_component",
    "unexplained_test_failure", "regression", "architecture_decision",
    "increased_uncertainty", "risk_increase",
}


class RoutingError(ValueError):
    """A diagnostic assembled only from kit-owned text and known field labels."""


class RoutingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's original message can contain arbitrary argument values.
        super().error("Invalid command arguments; consult --help for supported options.")


def resolve_input(path, role):
    try:
        return path.resolve(strict=True)
    except (OSError, RuntimeError, ValueError, AttributeError) as error:
        raise RoutingError(f"{role} path is unavailable.") from error


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise RoutingError(f"{field} must be nonempty text")


def require_text_list(value, field, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise RoutingError(f"{field} must be {'a nonempty' if nonempty else 'a'} list of text")
    for item in value:
        require_text(item, field)


def assess(task):
    required = set(CHOICES) | {"objective", "acceptance", "assessment_basis"}
    if not isinstance(task, dict) or not required <= task.keys() or task.keys() - required - {"escalation", "inspection_command"}:
        raise RoutingError("Expected all task assessment fields and optional escalation or inspection command")
    for key, choices in CHOICES.items():
        value = task[key]
        if not isinstance(value, str) or value not in choices:
            raise RoutingError(f"{key} must be one of {', '.join(sorted(choices))}")
    require_text(task["objective"], "objective")
    require_text_list(task["acceptance"], "acceptance", nonempty=True)
    require_text_list(task["assessment_basis"], "assessment_basis", nonempty=True)
    if "inspection_command" in task:
        require_text(task["inspection_command"], "inspection_command")
    if "escalation" in task:
        handoff = task["escalation"]
        fields = {"signal", "finding", "work_done", "changed_files", "open_decisions", "evidence"}
        if not isinstance(handoff, dict) or handoff.keys() != fields:
            raise RoutingError("Escalation requires a signal, finding, work, paths, decisions and evidence")
        signal = handoff["signal"]
        if not isinstance(signal, str) or signal not in ESCALATION_SIGNALS:
            raise RoutingError("Unknown escalation signal")
        require_text(handoff["finding"], "escalation.finding")
        for field in ("work_done", "changed_files", "open_decisions", "evidence"):
            require_text_list(handoff[field], f"escalation.{field}", nonempty=field == "evidence")


def choose_verification(task):
    checks = {
        "documentation": ["Review the diff for scope, accuracy and references."],
        "configuration": ["Validate syntax and effective configuration in the affected environment."],
        "code": ["Review the diff and run the affected tests."],
        "analysis": ["Check findings against their sources and the acceptance criteria."],
    }[task["kind"]]
    if task["scope"] in {"related", "cross_component", "cross_repository"}:
        checks.append("Check regressions across the affected dependencies.")
    if (
        task["complexity"] == "complex" or task["risk"] != "low"
        or task["scope"] in {"cross_component", "cross_repository"} or "escalation" in task
    ):
        checks.append("Review impact, relevant regressions and acceptance with the coordinator.")
    return checks


def route(task):
    assess(task)
    sol_reasons = {
        "complexity": task["complexity"] == "complex",
        "scope": task["scope"] in {"cross_component", "cross_repository"},
        "risk": task["risk"] != "low",
        "uncertainty": task["uncertainty"] == "material",
        "reasoning": task["reasoning"] == "advanced",
        "dependencies": task["dependencies"] == "unknown",
        "delegation_value": task["delegation_value"] == "low",
    }
    reasons = [f"{factor}={task[factor]}" for factor, requires_sol in sol_reasons.items() if requires_sol]
    escalation = task.get("escalation")
    if escalation:
        reasons.append(f"escalation={escalation['signal']}")
    model = "gpt-6.1-sol" if reasons else "gpt-6-luna"
    return {
        "version": RC_VERSION,
        "model": model,
        "reasons": reasons or ["Low risk and uncertainty, bounded scope, routine reasoning, and useful delegation."],
        "assessment": task,
        "criteria": [
            {"id": f"AC-{index}", "text": text}
            for index, text in enumerate(task["acceptance"], start=1)
        ],
        "verification": choose_verification(task),
        "dispatch": "coordinator" if escalation or task["risk"] == "high" else "read_only_available",
    }


def profile_preflight(codex, profile, workspace):
    codex = resolve_input(codex, "Codex binary")
    profile = resolve_input(profile, "Pilot profile")
    workspace = resolve_input(workspace, "Workspace")
    default_home = (Path.home() / ".codex").resolve()
    active_home = Path(os.environ.get("CODEX_HOME") or default_home).resolve()
    artifacts = default_home / "visualizations"
    artifact_profile = profile != artifacts and profile.is_relative_to(artifacts)
    for home in {default_home, active_home}:
        if home.is_relative_to(profile) or (
            profile.is_relative_to(home) and not (home == default_home and artifact_profile)
        ):
            raise RoutingError("Use a dedicated profile outside the active Codex state")
    if workspace.is_relative_to(profile) or profile.is_relative_to(workspace):
        raise RoutingError("The Codex home and task workspace must be separate")
    if not codex.is_file() or not workspace.is_dir():
        raise RoutingError("Expected a Codex binary and a workspace directory")
    try:
        config = tomllib.loads((profile / "config.toml").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise RoutingError("Profile preflight: pilot configuration is unreadable or invalid.") from error
    hooks_path = profile / "hooks.json"
    try:
        hooks = json.loads(hooks_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise RoutingError("Profile preflight: hook registrations are unreadable or invalid.") from error
    try:
        state = config["hooks"]["state"]
        events = hooks["hooks"]
        for event in ("SessionStart", "UserPromptSubmit", "PreToolUse"):
            for group_index, group in enumerate(events[event]):
                if group.get("matcher") not in (None, "", ".*", "^.*$"):
                    continue
                for handler_index, handler in enumerate(group.get("hooks", [])):
                    command = handler.get("commandWindows" if os.name == "nt" else "command") or handler.get("command")
                    key = f"{hooks_path}:{ {'SessionStart': 'session_start', 'UserPromptSubmit': 'user_prompt_submit', 'PreToolUse': 'pre_tool_use'}[event]}:{group_index}:{handler_index}"
                    trusted_hash = state.get(key, {}).get("trusted_hash")
                    if (
                        handler.get("type") == "command" and isinstance(command, str)
                        and command.strip() and isinstance(trusted_hash, str)
                        and trusted_hash.startswith("sha256:") and len(trusted_hash) == 71
                        and all(c in "0123456789abcdef" for c in trusted_hash[7:])
                    ):
                        break
                else:
                    continue
                break
            else:
                raise RoutingError(f"Dedicated profile needs a catch-all {event} command hook and declared trust metadata")
    except (KeyError, TypeError, AttributeError) as error:
        raise RoutingError("Dedicated profile hook registration or trust metadata is incomplete") from error
    return codex, profile, workspace


def prepared_route(record_path, config_path, workspace):
    # Reuse the installed guard's schema, lifecycle and context validation.
    if not Path(__file__).with_name("preparation_guard.py").is_file():
        raise RoutingError("Runtime prerequisites: preparation guard is unavailable.")
    try:
        import preparation_guard as guard
    except ImportError as error:
        raise RoutingError("Runtime prerequisites: preparation guard is unavailable.") from error

    config_path = resolve_input(config_path, "Guard configuration")
    config = guard.read_json(config_path)
    record_path = resolve_input(record_path, "Preparation record")
    record = guard.read_json(record_path)
    context_path, expected_path = guard.state_paths(config, record.get("session_id"))
    if record_path != expected_path:
        raise RoutingError("Use the active preparation record in the configured guard state")
    if guard.invalidation_path(config_path, record["session_id"]).exists():
        raise RoutingError("Preparation has a pending lifecycle invalidation")
    context = guard.read_json(context_path)
    try:
        guard.validate(config, context, record)
    except guard.PreparationError as error:
        raise RoutingError("Preparation validation rejected the record.") from error
    if record["write_paths"] != [] or workspace.resolve(strict=True) != Path(record["workspace"]).resolve():
        raise RoutingError("Dispatch requires empty write paths and the same prepared workspace")
    task = record.get("routing")
    decision = route(task)
    if any(task[key] != record[key] for key in ("objective", "risk", "complexity")):
        raise RoutingError("The routing assessment must match the prepared objective, risk and complexity")
    if "inspection_command" in task and not guard.shell_read_only(task["inspection_command"]):
        raise RoutingError("The inspection command must satisfy the guard's literal read rules")
    decision["preparation"] = {
        key: record[key] for key in ("session_id", "generation", "workspace")
    }
    return decision


def validate_outcome(decision, payload):
    if not isinstance(payload, dict) or set(payload) != {"status", "summary", "evidence", "signal"}:
        raise RoutingError("Unexpected outcome fields")
    status = payload["status"]
    if status not in ("completed", "blocked", "escalated"):
        raise RoutingError("Unknown outcome status")
    require_text(payload["summary"], "summary")
    evidence = payload["evidence"]
    if not isinstance(evidence, list):
        raise RoutingError("Evidence must be a list")
    expected_ids = {criterion["id"] for criterion in decision["criteria"]}
    seen_ids = set()
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"criterion_id", "observation"}:
            raise RoutingError("Evidence entries need a criterion_id and observation")
        criterion_id = item["criterion_id"]
        require_text(criterion_id, "criterion_id")
        require_text(item["observation"], "observation")
        if criterion_id not in expected_ids:
            raise RoutingError("Evidence references an unknown acceptance criterion ID")
        if criterion_id in seen_ids:
            raise RoutingError("Evidence repeats an acceptance criterion ID")
        seen_ids.add(criterion_id)
    if status == "completed" and seen_ids != expected_ids:
        raise RoutingError("A completion report needs evidence for every acceptance criterion ID")
    signal = payload["signal"]
    if status == "escalated":
        if not isinstance(signal, str) or signal not in ESCALATION_SIGNALS or not evidence:
            raise RoutingError("Escalation requires a known signal and evidence")
    elif signal is not None:
        raise RoutingError("Only an escalation may include a signal")
    return {
        "decision": decision,
        "status": "needs_review" if status == "completed" else status,
        "reported": payload,
    }


def outcome_from_execution(decision, execution):
    def blocked(reason):
        return {"decision": decision, "status": "blocked", "reason": reason}

    if execution.returncode != 0:
        code = execution.returncode
        if type(code) is int:
            return blocked(f"CLI process failed with exit code {code}; cause unclassified.")
        return blocked("CLI process failed; exit code unavailable and cause unclassified.")
    try:
        events = [json.loads(line) for line in execution.stdout.splitlines() if line.strip()]
        if not events or events[-1].get("type") != "turn.completed":
            return blocked("No completed Codex turn")
        if any(event.get("type") in {"error", "turn.failed"} for event in events):
            return blocked("Codex reported an execution error")
        messages = [
            event["item"]["text"] for event in events
            if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message"
        ]
        if not messages:
            return blocked("No structured model result")
    except (ValueError, KeyError, AttributeError, TypeError):
        return blocked("Invalid Codex event stream")
    try:
        payload = json.loads(messages[-1])
    except (ValueError, TypeError):
        return blocked("Final model message is not valid JSON")
    try:
        return validate_outcome(decision, payload)
    except RoutingError as error:
        return blocked(f"Invalid structured model result: {error}")
    except Exception:
        return blocked("Result validation failed; cause unclassified.")


def launch_read_only(decision, codex, profile, workspace):
    if decision["dispatch"] != "read_only_available" or "preparation" not in decision:
        raise RoutingError("The coordinator must review and prepare the task before dispatch")
    codex, profile, workspace = profile_preflight(codex, profile, workspace)
    schema = Path(__file__).with_name("model_routing_result.schema.json")
    try:
        schema_document = json.loads(schema.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RoutingError("Runtime prerequisites: result schema is unavailable or invalid.") from error
    if not isinstance(schema_document, dict):
        raise RoutingError("Runtime prerequisites: result schema must be an object.")
    command = [
        str(codex), "--no-daemon", "--ask-for-approval", "never", "-c", "features.hooks=true",
        "exec", "--ephemeral", "--sandbox", "read-only", "--cd", str(workspace),
        "--model", decision["model"], "--json", "--output-schema", str(schema), "-",
    ]
    task = decision["assessment"]
    request = {
        "objective": task["objective"], "acceptance": decision["criteria"],
        "verification": decision["verification"],
    }
    if "inspection_command" in task:
        request["inspection_command"] = task["inspection_command"]
    prompt = (
        "Perform only this read-only task. Follow all applicable instructions and hooks. "
        "The coordinator already validated the preparation for this read-only dispatch. "
        "For a literal inspection that the guard permits, perform the read directly and evaluate the result. "
        "Do not submit resolve or ready records for a task that only requires a permitted read. "
        "If scope grows or work is blocked, stop and report a structured escalation or blocker. "
        "Use a supported signal code only for an escalation, and put the explanation in summary. "
        "Verification suggestions are supplementary; the coordinator retains the original required checks. "
        "Perform only checks permitted in this read-only scope and report any unperformed checks honestly. "
        "For completed or blocked results, set signal to null. "
        "When inspection_command is supplied, execute that exact single command in the workspace first. "
        "Do not wrap, extend or substitute the command. Use its successful output to assess acceptance. "
        "For each evidence entry copy the supplied acceptance id into criterion_id. "
        "Report one observation per id before claiming completion.\n"
        + json.dumps(request)
    )
    try:
        execution = subprocess.run(
            command, cwd=workspace, env={**os.environ, "CODEX_HOME": str(profile)},
            input=prompt, encoding="utf-8", capture_output=True, timeout=300, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"decision": decision, "status": "blocked", "reason": "CLI execution timed out after 300 seconds."}
    except UnicodeError:
        return {"decision": decision, "status": "blocked", "reason": "CLI transport: output encoding is invalid."}
    except OSError as error:
        raise RoutingError("CLI invocation: Codex could not be started.") from error
    return outcome_from_execution(decision, execution)


def main(argv=None):
    parser = RoutingArgumentParser(prog="model_routing.py", description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--assessment", help="Unprepared assessment JSON path or - for stdin")
    source.add_argument("--preparation", type=Path, help="Active ready preparation from the coordinator")
    parser.add_argument("--guard-config", type=Path)
    parser.add_argument("--run-read-only", action="store_true")
    parser.add_argument("--codex", type=Path)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--workspace", type=Path)
    args = parser.parse_args(argv)
    if args.preparation and not all((args.guard_config, args.workspace)):
        parser.error("--preparation requires --guard-config and --workspace")
    if args.run_read_only and not all((args.preparation, args.codex, args.codex_home)):
        parser.error("--run-read-only requires --preparation, --codex and --codex-home")
    phase = "Preparation" if args.preparation else "Assessment"
    try:
        if args.preparation:
            decision = prepared_route(args.preparation, args.guard_config, args.workspace)
        else:
            task = json.load(sys.stdin) if args.assessment == "-" else json.loads(
                Path(args.assessment).read_text(encoding="utf-8-sig")
            )
            decision = route(task)
        phase = "Read-only dispatch"
        result = launch_read_only(decision, args.codex, args.codex_home, args.workspace) if args.run_read_only else decision
        print(json.dumps(result, indent=2))
        return {"blocked": 2, "escalated": 3}.get(result.get("status"), 0)
    except RoutingError as error:
        print(f"Model routing ({phase}): {error}", file=sys.stderr)
        return 2
    except Exception:
        # Unknown exceptions can contain paths, argument values or partial data.
        print(f"Model routing ({phase}): operation failed; cause unclassified.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
