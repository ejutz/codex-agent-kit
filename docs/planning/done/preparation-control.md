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

## Operation-context implementation checkpoint — 2026-11-01

**Authorization:** the user explicitly requested implementation of the reviewed
recommendations from the audit supplied by another installation. Scope covers
the shared package, disposable tests and documentation. Global installation and
client trust were not changed. The approved authoring baseline remains v1.0.

### Embedded ADR: bind preparation to concrete operations

**Status:** accepted for this authorized implementation; target-client validation
remains pending. **Context:** normalized hook input may omit workdir, startup
instruction discovery does not cover nested patch destinations, and structural
record validation does not authenticate an agent's claims.

**Decision:** use the canonical adapter contract in
[Preparation control](../../implementation/preparation-control.md#command-directories-and-tool-guarantees).
Bind prepared shell execution to one explicit directory through updatedInput,
resolve instructions along affected paths, and retain distinct declaration,
artifact-identity and tool-response evidence. Preserve prior records as history
while every lifecycle transition still creates a fresh draft.

**Alternatives:** relying on session cwd cannot establish the effective directory;
waiting solely for a new client field leaves the observed gap unresolved. A full
shell parser adds a shell/runtime dependency, so diagnostic reads use a bounded
literal grammar and unsupported syntax retains preparation requirements. Loading
all nested instructions adds irrelevant context; affected-path chains are sufficient
for the supported operations. Automatically inheriting readiness is rejected.

**Consequences:** the installed shell must be identified explicitly. Native aliases
must arrive canonically. Unknown tool hashes still establish identity rather than
filesystem containment. New PostToolUse registration requires target trust review.
The callback cannot prove human authorization, comprehension or semantic success.

### Plan execution and evidence

| Step | Result |
| --- | --- |
| Preserve current work and reproduce gaps | Package snapshot and hashes retained in the ignored evaluation area. Seven initial regression methods failed before correction (eight failure assertions and one error). |
| Bind commands and resolve operation context | Implemented unique-directory selection, explicit shell binding, ambiguity rejection and instruction checks for patch/move and known filesystem-write paths. |
| Refine diagnostic reads and continuity | Literal quoting respects separators; unsupported expansions and smart quotes remain restricted. Prior records are archived without transferring readiness or action permissions. |
| Distinguish evidence | Optional declared/artifact entries; byte identity validated for artifacts. PostToolUse receipts contain metadata/hashes and make no success claim. |
| Verify package behavior | Final suite: 62 tests passed, no skips, using Python 3.14.7 on Windows. Includes two actual PowerShell subprocess cases: Python child executes in the prepared directory, and a directory removed after validation prevents the payload from writing. |
| Prepare installed-client check | Added --mode ready --tool cwd to the native probe. It submits preparation through the callback and distinguishes bound execution, explicit denial and unverified behavior. The new native probe path was reviewed and syntax-checked, not executed here. |

Command from the authoring root:
`python -B -m unittest discover -s templates/development-agent/tests -q`.
TMP/TEMP/TMPDIR pointed into the ignored evaluation area and Python bytecode writes
were disabled. Earlier 55- and 61-test runs passed before the final coverage additions.

Affected code: preparation_guard.py, install_preparation_guard.py and
test_preparation_host.py; existing guard/installer tests and the new
test_operation_preparation.py. Updated documents: preparation-control,
instruction-loading, workflow, testing strategy and this historical record.
No new normative requirement or baseline was adopted through this checkpoint.

### Completion and continuation

Package implementation and automated checks are complete. The current profile
has no preparation-control/config.json; installed-client normalization, rewritten
execution, registration/trust and observation delivery remain unverified here.
The foreign installation's audit is source evidence, not a certification of this
checkout. POSIX command grouping is provided but was not executed on this Windows
host. Existing local changes were preserved; no commit or publication was made.

Next action: update an authorized target installation with the verified shell,
review the four hook registrations, reload the client and run the documented
native probe. Require directory_binding_verified for positive binding evidence;
an explicit rejection establishes only that the mismatched call was blocked.

## Required-context validation checkpoint — 2026-11-01

**Authorization and scope:** the user requested continuation of the validator
to check required context automatically. This scoped implementation covers the
shared adapter, canonical routing, disposable regressions and documentation.
Global installation, trust and release approval remain separate. The earlier
design-only authoring default is overridden only for this explicitly requested
package implementation, consistent with the earlier adapter work.

### Decision and plan

Use one delegated JSON route registry for both the agent and the validator.
Replace the router's independent task-to-file table with that canonical reference;
retain the router's classification, authority and dependency rules. Resolve only
selected roots and affected paths, with iterative traversal, path-equivalent
identity and explicit cycle review. The supported metadata subset and actual
processing limits are documented; unsupported forms must not become empty lists.

The plan was to preserve existing changes, reproduce the audit omissions, add
routing/dependency validation and a data-only resolution request, then run the
complete suite and review package integration. No new dependency or service is
needed. Record freshness and graph completeness remain separate from the agent's
semantic judgments and from authentic authorization evidence.

### Execution and verification

- Eight initial regression methods reproduced the gaps before correction, with
  ten failing assertions including subtests.
- Implemented canonical selection by type/risk/assessed concern, transitive
  prerequisites, missing/stale source rejection, shared-node handling, cycle
  reconciliation and operation-specific dependency checks.
- Added status=resolve to the existing data-only transport. It computes a draft
  with source identities and clears check assertions; it cannot authorize writes.
- Updated the fixture and native probe preparation format without relaxing the
  previous blocking tests. Twenty new regression methods cover the resolver.
- The first expanded full run had 76 passes and one fixture-isolation failure:
  the real-payload test inherited the authoring Git root from its temporary path.
  An explicit target root marker corrected the fixture boundary; the resolver's
  discovery behavior was retained.
- Final full suite: **82 tests passed**, no skips, in 30.071 seconds on Windows,
  including the existing PowerShell execution regressions. Command from the
  authoring root: `python -B -m unittest discover -s templates/development-agent/tests -q`.
  Temporary files were directed to the ignored evaluation area and bytecode
  writes were disabled. This does not certify installed-client behavior.
- Artifact checks passed for 15 changed/new files: four Python files parsed,
  93 local links/fragments resolved, and 12 dependency documents had no unresolved
  cycle or missing source. The canonical registry passed schema validation.
  All 25 fingerprinted requirement/release files and the historical prefix of
  this record remained unchanged. Both repository diff checks passed, retaining
  the existing root-index line-ending conversion warning. Python was 3.14.7.

### Continuity and remaining limits

The computed context check is implemented in the working package, subsequent to
the approved v1.0 snapshot. The new route registry and resolver guide must travel
with the kit on update; old records require current concern/source assessment.
No global configuration or trust was changed. The updated native probe was not
executed against an installed client in this session.

Task classification, concern relevance, cycle interpretation and completeness of
natural-language requirements remain assessments; the adapter does not prove
source delivery, comprehension or human authorization. The next operational step
is an authorized target update, trust/reload review and actual client-path checks.
