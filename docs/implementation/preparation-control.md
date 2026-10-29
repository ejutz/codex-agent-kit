---
scope: Codex preparation record, hook adapter, installation and verification
load_when: before task modifications when the global preparation control is installed, or when installing or testing it
depends_on: [../../AGENTS.md, workflow.md, instruction-loading.md]
---
# Preparation control for local Codex

The [workflow](workflow.md#before-the-first-modification) owns the mandatory
preparation check. This document owns its machine-readable adapter, not a new
authorization policy. The user's 2026-10-27 instruction authorizes this adapter.

## Operation

The synchronous `SessionStart` and `UserPromptSubmit` hooks create a draft
record and a hook-owned context under the configured Codex home's
`preparation-control/state/<session-hash>/`. `PreToolUse` checks preparation
before supported mutations. New prompts and resumed/forked/compacted sessions
invalidate the old generation. A record also expires after 24 hours; this is
a bounded freshness safeguard, not a claim that a task needs daily approval.

Lifecycle invalidation is saved per session beside the fixed guard configuration
in `<config-filename>.invalidations/` before that configuration is read. Missing
or malformed settings therefore cannot revive an older ready record after repair.
Missing instruction sources remain listed in the draft's `prerequisite_errors`;
diagnostic inspection can continue while dependent operations remain blocked.
If durable invalidation itself cannot be saved, the lifecycle event stops.
Atomic state publication makes at most five attempts for Windows access/sharing
failures, with 250 ms total delay; persistent errors still propagate and block the
dependent operation. The previous file is never deleted to force replacement.

The hook tells the agent the exact preparation.json path. Publish the required
preparation in the conversation, read the applicable sources, and update that
JSON through a supported data submission, without agent writes to the protected
Codex home. Use `update_plan.explanation` containing `CODEX_PREPARATION_V1:`
followed by the complete JSON when that tool is available. Otherwise use the
exact literal PowerShell command `Write-Output 'CODEX_PREPARATION_V1:<JSON>'`,
doubling embedded apostrophes. No extra command or shell syntax is permitted.
The hook validates and stores the record, then replaces the metadata/command
with a fixed confirmation. It never evaluates the supplied JSON as code.
Invalid submission revokes readiness. Do not patch context.json or state files.
These two data transports are the sole preparation-registration exception; they grant no
approval for task writes or pending actions. The normal host permissions apply.

## Instruction discovery

The global loader is the first nonempty `AGENTS.override.md` or `AGENTS.md` in
the configured Codex home. Project discovery walks from the nearest root marker
to the current directory; `.git` files and directories both count. With no
matching marker, or `project_root_markers = []`, only the current directory is
searched. Unrelated ancestors above that root are excluded. Each directory
selects its first nonempty override, AGENTS.md, or configured fallback filename.

The adapter reads `project_root_markers` and `project_doc_fallback_filenames`
from the Codex home's config.toml. Explicitly trusted project configuration
layers supply fallback names in root-to-current-directory order; nearer layers
win. Untrusted project configuration is ignored. Discovery names must be plain
filenames, without path separators, traversal or drive prefixes. Mandatory kit
owners remain required independently of project discovery.

Hook input does not provide the complete effective host configuration. For
profile, managed or CLI overrides, explicitly map these two effective settings
in the optional `discovery` object of preparation-control/config.json. That
mapping takes precedence and survives reinstallation. Project-local root-marker
changes also require this mapping; unresolved changes block preparation. Do not
claim identical host discovery until the effective configuration is checked.
Source identities and byte hashes are revalidated before dependent operations.

## Record contract

Retain the draft's version, session_id, workspace and generation. Fill:

| Field | Required evidence |
| --- | --- |
| task, objective, scope | Concise task summary, expected outcome and boundaries; no transcript or sensitive payload. |
| type | analysis, feature, bugfix, refactor, tests, infrastructure or documentation. |
| complexity, complexity_reason | trivial, bounded or complex and a concrete reason. |
| risk, risk_reason | low, medium or high and concrete consequences. |
| steps, verification, risks | Nonempty arrays of individually verifiable steps, checks and material risks. Trivial work may use one concise entry each. |
| recovery | Relevant recovery/containment or a concrete limitation, including high-risk preparation. |
| authorization | basis describes existing user authorization; pending is empty only when no required gate remains pending. |
| sources | Absolute path, exact-byte sha256 and applicability purpose for each selected source. Mandatory sources are prefilled. Add selected dependencies and project owners. |
| requirements, pre_execution_checks | Nonempty arrays with source, requirement, status (passed/not_applicable) and evidence. Non-applicability needs a concrete reason. Pending/failed checks deny writes. |
| write_paths | Absolute files or directories covered by the task for patch operations. Paths are resolved before containment checks. |
| commands | Exact command, absolute cwd and purpose for every nontrivial shell invocation. Unknown shell syntax is treated as potentially mutating. |
| tool_calls | tool, input_sha256 and purpose for other calls. The hash is SHA-256 of UTF-8 JSON serialized with sorted keys, compact separators and ensure_ascii=False. |

Set status to ready only after resolving preparation and authorization. Hashes
prove freshness, not reading or comprehension. Requirement evidence is agent
self-attestation; a complete record cannot prove all natural-language policy
was interpreted correctly. This control never grants an approval or expands
host permissions. Reassess and update preparation for material scope changes.

The small read-only shell subset accepts direct Get-Content/Get-ChildItem,
Get-Location/Resolve-Path/Test-Path/Get-Command/Select-String/Get-FileHash,
selected git inspection commands and rg without preprocessors. Variables,
substitutions and unknown commands require an exact prepared entry. A pipeline
may append only Select-Object with numeric -First/-Last/-Skip arguments to an
accepted read; redirects, script expressions and write stages are rejected.
These reads remain available before preparation, even with missing guard settings.
The exact trusted filesystem adapter `mcp__filesystem__read_file` accepts only
an absolute `path` argument. Unknown MCP tools, additional execution arguments,
and arbitrary JavaScript/Python still require preparation. Ordinary metadata
updates and built-in resource/image reads remain available; preparation-bearing
update_plan calls always pass through validation and storage.
The adapter does not infer a script's side effects from its name. Prepared shell
commands remain subject to review: the hook does not sandbox their internal writes.

## Installation and trust

Use the existing Python 3.11+ standard-library runtime, with explicit paths:

```powershell
py -3 scripts/install_preparation_guard.py --kit-root <absolute-kit> --codex-home <absolute-codex-home> --python <absolute-python-executable>
```

The installer merges three events into user-global hooks.json, enables
features.hooks, preserves other handlers/settings and creates exact backups
under preparation-control/backups. The global AGENTS.md loader remains unchanged.
Scripts are referenced from the stable kit path; projects contain no kit paths.

Review and trust the exact definitions using Codex `/hooks`. Do not fabricate
trust records. Restart/reload clients and verify hooks/list reports enabled,
trusted hooks with no errors. Configured, trusted, and executed are separate
claims. Existing sessions are not assumed to hot-reload a new control.

## Validation, recovery and limitations

Run the unittest command from [Testing strategy](../testing/strategy.md#kit-preparation-control-checks)
with the verified interpreter in this kit. Fixtures use only
temporary files and no application services or credentials. Verify absent,
incomplete, stale, out-of-scope and pending-authorization cases leave canaries
unwritten; verify prepared commands/patches can write their disposable targets.
Test the actual installed Codex tool hook path separately from Python fixtures.

`scripts/test_preparation_host.py` provides an opt-in deterministic native CLI
probe. Supply explicit --kit, --home, --codex and --output absolute paths, then
--mode missing/incomplete/pending/stale/scope/ready and --tool patch/shell/submit.
It runs an ephemeral Codex process against a loopback canned Responses server;
no model or external API is used. Existing global hook trust is required.
Use a disposable directory under --output. Native local tools receive canned
calls; this does not evaluate model behavior or hosted code-mode integration.
The ready/submit case verifies callback-owned registration; ready/patch and
ready/shell additionally require a working Windows command sandbox.

Rollback uses the installation backup manifest: restore precisely the files
that existed before installation and remove only newly created hook/config
files named by that manifest. Preserve later unrelated changes and restart the
client. Do not recursively delete the Codex home or control directory.

Hooks are workflow guardrails. Unsupported tools, input sent later to an
already-running process, client callback errors/timeouts, an unavailable
interpreter and editable local settings are not a complete enforcement boundary.
Handled validation errors return an explicit deny, but host-level hook failure
may still allow a tool. An agent with permission to change the guard/config can
weaken it. Strong enforcement requires independently protected configuration,
scripts and filesystem permissions plus environment-specific validation.
No claim of managed OS-level enforcement is made by a user-global installation.

Official references: [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced),
[Codex hooks](https://learn.chatgpt.com/docs/hooks), and
[protecting safeguards](https://learn.chatgpt.com/docs/enterprise/security-cookbook#keep-codex-from-changing-its-own-safeguards).
