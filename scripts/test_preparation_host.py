"""Probe real Codex tool hooks using a deterministic loopback Responses server.

No model/API service is contacted. Each ephemeral CLI run receives one canned
tool call, then a final message. Only disposable canaries and new probe records
are written. The actual global hook registration and trust are used unchanged.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time


def load_guard(kit):
    spec = importlib.util.spec_from_file_location("preparation_guard", kit / "scripts/preparation_guard.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_probe(guard, home, workspace, mode, command, register=False):
    """Supply fixture preparation only for this new disposable CLI workspace."""
    matches = []
    for path in (home / "preparation-control/state").glob("*/preparation.json"):
        record = guard.read_json(path)
        if Path(record["workspace"]).resolve() == workspace.resolve():
            matches.append((path.stat().st_mtime, path, record))
    if not matches:
        raise AssertionError("Actual lifecycle hook did not create the probe preparation record.")
    _, path, record = max(matches, key=lambda item: item[0])
    if mode == "missing":
        path.unlink()
        return
    record.update(status="ready", task="Native Codex hook canary test", type="tests", complexity="bounded",
                  complexity_reason="One deterministic tool call in a temporary workspace", risk="low",
                  risk_reason="Only a disposable canary is writable", objective="Verify real pre-tool denial",
                  scope="This disposable test workspace", steps=["Execute one canned tool call"],
                  verification=["Check the hook denial and canary existence"], risks=["No application data or external model service"],
                  recovery="Delete only the temporary probe workspace after verifying it",
                  authorization={"basis": "User requested validation that global preparation hooks block writes", "pending": []},
                  write_paths=[str(workspace / "canary.txt")], commands=[{"command": command, "cwd": str(workspace), "purpose": "Write only the disposable test canary"}])
    check = {"source": str(home / "AGENTS.md"), "requirement": "Resolve preparation before writing",
             "status": "passed", "evidence": "Deterministic isolated integration fixture"}
    record["requirements"] = [check]
    record["pre_execution_checks"] = [dict(check)]
    if mode == "incomplete":
        record["objective"] = ""
    if mode == "pending":
        record["authorization"]["pending"] = ["Unresolved fixture authorization"]
    if not register:
        guard.write_json(path, record)
    if mode == "stale":
        (workspace / "AGENTS.md").write_text("Changed fixture instructions after preparation", encoding="utf-8")
    return path, record


def run_probe(args, mode, kind):
    guard = load_guard(args.kit)
    with tempfile.TemporaryDirectory(prefix="codex-preparation-host-", dir=args.output) as directory:
        workspace = Path(directory).resolve()
        (workspace / "AGENTS.md").write_text("Disposable preparation-control integration fixture.\n", encoding="utf-8")
        canary = workspace / "canary.txt"
        target = workspace / "outside.txt" if mode == "scope" else canary
        command = "Set-Content -LiteralPath '" + str(canary) + "' -Value 'allowed'"
        patch = "*** Begin Patch\n*** Add File: " + str(target) + "\n+allowed\n*** End Patch"
        observed = {"requests": 0, "tools": [], "tool_feedback": "", "errors": [], "request_shapes": []}
        catalog_data = json.loads(subprocess.run([str(args.codex), "debug", "models", "--bundled"], capture_output=True, text=True, encoding="utf-8", check=True).stdout)
        catalog = json.dumps(catalog_data)

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *unused):
                pass

            def do_GET(self):
                body = catalog.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                try:
                    data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    observed["request_shapes"].append({"path": self.path, "keys": list(data), "tools": data.get("tools", [])[:1]})
                    observed["requests"] += 1
                    tools = data.get("tools", [])
                    if not observed["tools"]:
                        observed["tools"] = [tool.get("name", tool.get("type")) for tool in tools]
                    for item in data.get("input", []):
                        if item.get("type") in {"function_call_output", "custom_tool_call_output"}:
                            observed["tool_feedback"] = str(item.get("output", ""))
                    first = observed["requests"] == 1
                    if first:
                        prepared = prepare_probe(guard, args.home, workspace, mode, command, register=kind in {"plan", "submit"})
                        if kind == "plan":
                            observed["preparation_path"] = prepared[0]
                            parameters = {"explanation": guard.SUBMISSION_PREFIX + json.dumps(prepared[1]), "plan": [{"step": "Verify disposable preparation registration", "status": "in_progress"}]}
                            item = {"type": "function_call", "id": "fc_probe", "call_id": "call_probe", "name": "update_plan", "arguments": json.dumps(parameters)}
                        elif kind == "submit":
                            observed["preparation_path"] = prepared[0]
                            transport = "Write-Output '" + (guard.SUBMISSION_PREFIX + json.dumps(prepared[1])).replace("'", "''") + "'"
                            item = {"type": "function_call", "id": "fc_probe", "call_id": "call_probe", "name": "exec_command", "arguments": json.dumps({"cmd": transport, "workdir": str(workspace)})}
                        elif kind == "patch":
                            tool = next((tool for tool in tools if tool.get("name") == "apply_patch"), None)
                            if not tool:
                                tool = {"name": "apply_patch", "type": "custom"}
                            if tool["type"] == "custom":
                                item = {"type": "custom_tool_call", "id": "ctc_probe", "call_id": "call_probe", "name": "apply_patch", "input": patch}
                            else:
                                item = {"type": "function_call", "id": "fc_probe", "call_id": "call_probe", "name": "apply_patch", "arguments": json.dumps({"patch": patch})}
                        else:
                            name = next((name for name in observed["tools"] if name in {"exec_command", "shell_command", "shell"}), None)
                            if not name:
                                name = "exec_command"
                            parameters = {"cmd": command, "workdir": str(workspace)} if name == "exec_command" else {"command": command, "workdir": str(workspace)}
                            item = {"type": "function_call", "id": "fc_probe", "call_id": "call_probe", "name": name, "arguments": json.dumps(parameters)}
                    else:
                        item = {"type": "message", "id": "msg_probe", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": "Disposable hook probe finished.", "annotations": []}]}
                    response = {"id": "resp_probe_" + str(observed["requests"]), "object": "response", "created_at": int(time.time()), "status": "completed", "output": [item],
                                "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}}
                    events = [("response.created", {"response": dict(response, status="in_progress", output=[])}),
                              ("response.output_item.added", {"output_index": 0, "item": item}),
                              ("response.output_item.done", {"output_index": 0, "item": item}),
                              ("response.completed", {"response": response})]
                    body = "".join("event: " + name + "\ndata: " + json.dumps(dict(payload, type=name)) + "\n\n" for name, payload in events).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except Exception as error:
                    observed["errors"].append(str(error))
                    self.send_error(500, "Disposable fixture protocol failure")

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        endpoint = "http://127.0.0.1:" + str(server.server_port) + "/v1"
        cmd = [str(args.codex), "--no-daemon", "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--sandbox", "workspace-write", "-C", str(workspace),
               "-c", 'model_provider="preparation_probe"',
               "-c", 'model_providers.preparation_probe.name="Preparation loopback fixture"',
               "-c", 'model_providers.preparation_probe.base_url="' + endpoint + '"',
               "-c", 'model_providers.preparation_probe.wire_api="responses"',
               "-c", 'model_providers.preparation_probe.requires_openai_auth=false',
               "-c", "features.responses_websockets=false", "-c", "features.responses_websockets_v2=false",
               "Execute the deterministic disposable hook fixture, then stop. No other work is requested."]
        try:
            process = subprocess.run(cmd, cwd=workspace, env=dict(os.environ, CODEX_HOME=str(args.home)),
                                     capture_output=True, text=True, encoding="utf-8", timeout=90)
        finally:
            server.shutdown()
            server.server_close()
        wrote = target.exists()
        should_write = mode == "ready" and kind not in {"plan", "submit"}
        registered = kind in {"plan", "submit"} and "preparation_path" in observed and guard.read_json(observed["preparation_path"]).get("status") == "ready"
        denied = "prepar" in observed["tool_feedback"].lower() and any(word in observed["tool_feedback"].lower() for word in ("den", "reject", "not ready", "missing", "changed", "outside", "pending"))
        report = {"mode": mode, "tool": kind, "requests": observed["requests"], "returncode": process.returncode,
                  "canary_written": wrote, "expected_write": should_write, "denial_feedback": denied,
                  "fixture_errors": observed["errors"], "tool_names": observed["tools"],
                  "registered": registered,
                  "passed": process.returncode == 0 and observed["requests"] >= 2 and wrote == should_write and not observed["errors"] and (registered if kind in {"plan", "submit"} else should_write or denied)}
        if not report["passed"]:
            report["request_shapes"] = [{"path": shape["path"], "keys": shape["keys"], "tool_shapes": [{"keys": list(tool), "type": tool.get("type"), "name": tool.get("name")} for tool in shape["tools"]]} for shape in observed["request_shapes"]]
            report["feedback"] = observed["tool_feedback"][:1800]
            report["diagnostic"] = process.stderr[-2500:]
            report["events"] = process.stdout[-3500:]
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True)
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--codex", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["missing", "incomplete", "pending", "stale", "scope", "ready"], default="missing")
    parser.add_argument("--tool", choices=["patch", "shell", "plan", "submit"], default="patch")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = run_probe(args, args.mode, args.tool)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
