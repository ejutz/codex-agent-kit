---
lifecycle_status: done
primary_task: infrastructure
complexity: complex
risk: high
---
# Global preparation control implementation

The original installation record below describes its named target environment.
The separate correction checkpoint at the end records later package changes;
it does not certify installation in the current authoring profile.

## Objective, scope and authorization
The user explicitly requested kit changes, global preparation control and
validation that missing requirements block writes on 2026-10-27. Scope covers
the kit adapter, canonical instructions, global hook configuration and isolated
tests. No application changes, commit, push or publication were authorized.
Host sandbox escalations were granted separately for the named kit/global paths.

Complexity is complex because lifecycle, schema, native host and Windows behavior
interact. Risk is high because a faulty global guard could interrupt every
project. The router, workflow, instruction-loading, security, testing, coding,
Git, preferences and actual host policies were read. Their applicable controls,
user authorization, host permissions and secrecy rules provide policy coverage
for this installation; no broader security/OS-enforcement claim is made.

## Accepted design
- The workflow owns preparation policy; preparation-control.md owns its adapter.
- Records bind to session, workspace, task generation and source byte hashes.
- New prompts/sessions and changed instruction sources invalidate readiness;
  24-hour expiry bounds stale unattended use.
- Data-only update_plan or exact literal PowerShell submission is validated and
  stored by the callback; task tools never need to patch protected state files.
- Paths are resolved before patch containment; unknown shell commands need exact
  prepared command/cwd entries. Other tools need an exact input digest.
- Normal authorization and host sandbox/approval rules remain independent.

## Execution and acceptance
| Step / criterion | execution_status | Evidence |
| --- | --- | --- |
| Inspect kit/config and preserve prior changes | completed | Existing modified/untracked files inventoried; byte-exact kit backup retained. |
| Implement validation and canonical instructions | completed | Adapter, installer, record contract and indexed guide installed. |
| Validate guard acceptance and denial | completed | 23 Python tests passed, including real disposable fixture writes and denial without side effects. |
| Install global hooks and verify trust | completed | SessionStart, UserPromptSubmit and PreToolUse enabled/trusted through official /hooks; hooks/list reports no hook errors/warnings in kit and PRIMADOCA. |
| Validate real native rejection before writes | completed | Six canary cases passed: absent preparation via patch and shell; incomplete preparation, pending authorization, stale instructions and out-of-scope patch. No canary created. |
| Validate callback-owned submission | completed | Native ready/submit probe registered ready state without agent file writes in .codex. |
| Review preservation, links, whitespace and CRLF | completed | 13 affected artifacts passed link/dependency, syntax, CRLF and preservation checks; git diff --check passed. |

The guard accepts valid readiness in fixture tests, and native positive calls
reached the actual file/command tools after passing it. That does not guarantee
the separate Windows sandbox can execute them.

## Retained unsuccessful observations and limitations
- Initial native lifecycle hooks failed because a quoted Python executable
  requires PowerShell's call operator. commandWindows was corrected and all
  three exact definitions were reviewed/trusted again.
- Initial fake provider probes had no emitted tool call because the model is
  code-mode-only. The deterministic harness now emits native tool calls directly.
  It uses no model inference and does not validate hosted code-mode execution.
- Native ready/patch and ready/shell did not complete file writes: Windows
  command sandbox setup reported failed_to_write_file / setup refresh errors.
  Moving the disposable target out of .codex and into Temp and D: did not resolve
  this independent host limitation. These observations remain failed native
  positive-write probes; they are not reported as passing file-write tests.
- update_plan is unavailable in this CLI/model tool registry. The documented
  exact PowerShell data transport was verified instead. Unit tests cover both.
- The py -3 launcher could not execute its Windows Store interpreter in this
  environment (access denied). The same 23 tests passed with the installed
  bundled Python 3.12 executable; the verification procedure documents that
  explicit-interpreter alternative without skipping tests.
- Global configuration gained hook-trust metadata and TUI onboarding state; an
  unrelated project entry was also added during the task. All pre-existing
  settings were preserved and concurrent additions were not reverted.
- Existing unrecognized shell_default_timeout_ms/tool_timeout_sec settings and
  plugin icon warnings were observed and preserved as unrelated configuration.
- User-global hooks can be disabled or fail at the host level; unsupported tool
  paths, later process input and semantic instruction compliance are not fully
  enforced. No managed ACL or operating-system security boundary was installed.
- The running desktop conversation was not restarted. Start/reload a local
  client before relying on newly installed hooks; desktop hosted code-mode
  execution was not independently exercised by this CLI fixture.

## Preservation and recovery
Kit snapshot: C:/Users/psesjue/.codex/preparation-control/backups/kit-20261027T151121Z-5b2e14fd.
First global snapshot: C:/Users/psesjue/.codex/preparation-control/backups/20261027T151141Z-cba28e97.
The later Windows-invocation correction has a separate snapshot. Restore only
the exact manifest-listed files, preserving subsequent unrelated edits. Global
AGENTS.md remains the original single stable entry-point loader.

## Closure
The requested preparation guard is installed and its native denial and data
registration paths verified. The independent positive-write sandbox limitation
and untested desktop/code-mode paths remain explicit. Next permitted action:
reload the local client and use the automatically supplied draft for the next
task; diagnose native Windows command sandbox setup separately if needed.
No commit or publication was performed.

## Correction checkpoint — 2026-10-29

**Status: completed within the authorized correction scope.** The user requested
correction of instruction discovery and preparation-time diagnostic access,
then explicitly requested continuation. This is a correction to the working
package; the approved v1.0 archive, requirements, commit and tag remain unchanged.
No installation, global profile changes, commit or publication was performed
as part of this correction. The installation assertions above remain historical.

### Scope and results

| Artifact (relative to the package root) | Result |
| --- | --- |
| `scripts/preparation_guard.py` | Repository boundaries, configured fallbacks and trusted project layers; explicit effective-setting mapping; diagnostic reads before preparation; durable invalidation when configuration or sources are missing; bounded Windows atomic-replacement retries. |
| `scripts/install_preparation_guard.py` | Reinstallation preserves the optional discovery mapping. Only disposable fixture installations were executed. |
| `tests/test_preparation_regressions.py` | 25 added regressions cover discovery, diagnostic access, rejected mutations, configuration repair and state-write failures. |
| `tests/test_install_preparation_guard.py` | Existing preservation test also verifies that effective discovery settings survive reinstallation. |
| `docs/implementation/preparation-control.md` | Updated canonical adapter behavior, configuration limits and recovery guarantees. |
| `docs/planning/done/preparation-control.md` | This checkpoint and retained verification history. |

The plan was extended within the same two behaviors after review reproduced
reuse of old readiness following guard-configuration repair, and repeated tests
exposed intermittent Windows replacement failures. Both were corrected without
relaxing preparation, authorization, source checks or persistent-error handling.
An independent review confirmed the old-readiness issue was addressed. Marker
identity uses the absolute configuration argument without resolving the file's
symlink; reading the configuration still resolves its target.

### Verification evidence and retained failures

- The original 15 regression methods reproduced the reviewed behaviors before
  correction: 13 methods failed. Later cases extend configuration-layer coverage.
- An intermediate 38-test run had two update_plan failures and one PermissionError.
  The submission bypass was fixed; the resumed 44-test run passed.
- Review then reproduced stale readiness after removing/restoring guard JSON.
  Missing and malformed JSON now force a fresh generation; inability to save the
  invalidation stops the lifecycle event. The focused test failed before the fix.
- The installer preservation assertion also failed before its correction.
- An intermediate 45-test run failed a shell-submission assertion; ten focused
  repeats passed, so that individual failure was not conclusively attributed.
  A later 46-test run passed, but its standard rerun exposed WinError 5 in
  os.replace. A separate rapid-replacement probe reproduced that filesystem error.
- After bounded retry handling, 200 successive atomic replacements passed.
  Deterministic tests verify a transient retry and persistent-error propagation
  while preserving the prior file. No check was removed or weakened.
- Final command from the authoring root:
  `python -B -m unittest discover -s templates/development-agent/tests -v`.
  **48 tests passed** using the available Python 3.14.7 on Windows. Temporary
  directories were restricted to the ignored evaluation-lab/.runs area, and
  PYTHONDONTWRITEBYTECODE was enabled.
- Final checks passed for the six edited files: Python syntax, CRLF, whitespace,
  local documentation links/dependencies and preservation of the historical
  installation record. git diff --check passed, with an existing root-index
  line-ending conversion warning.

### Session continuity and remaining limits

The two requested corrections are implemented and fixture-verified. Diagnostic
access does not establish authorization or policy coverage. Profile/CLI/managed
discovery overrides still require an explicit mapping because hook input lacks
the effective configuration. Local callbacks remain workflow guardrails.
Installation/trust/reload and actual host-path behavior for these corrections
remain unverified in the current profile; the earlier installation evidence is
not substituted for those checks. Other pre-existing package changes were kept.
The next recommended step is a separately scoped target installation check.
The authoritative approved baseline remains v1.0; this work does not approve a
new baseline or certify model behavior.
