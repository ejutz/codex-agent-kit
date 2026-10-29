---
scope: project check commands, regression coverage, verification outcomes, and unsatisfied required checks
load_when: selecting or interpreting verification, changing tests or behavior, assessing completion
depends_on: [../../AGENTS.md, ../implementation/workflow.md]
---
# Testing Strategy

This document owns regression coverage, failure interpretation, verification outcomes, test integrity, and unsatisfied required checks within the scope delegated by [AGENTS.md](../../AGENTS.md#authority-and-mandatory-controls). These rules apply whether or not a persistent plan exists. General check selection, step and integrated verification, evidence reuse, documentation checks, and reporting belong to the [workflow](../implementation/workflow.md#verification-and-reporting). Command suitability and evidence follow [evidence and adaptation](../implementation/workflow.md#evidence-and-adaptation).

## Project check commands

**Target adaptation: UNKNOWN.** No target repository commands or testing architecture have been established. The entries below are information to resolve, not executable commands or a requirement that every target provide every listed check.

| Check or preparation | Current command evidence | Evidence needed before use |
|---|---|---|
| Test prerequisites | UNKNOWN | Actual repository prerequisites, setup procedure, effects, and authorization. |
| Relevant tests or full suite | UNKNOWN | Repository script/configuration, intended selection, environment, and required coverage. |
| Focused regression | UNKNOWN | Relevant test location, supported selection method, and observed defect. |
| Lint, formatting, or type checks | UNKNOWN | Applicable repository configuration and supported commands. |
| Build or generated artifacts | UNKNOWN | Applicable project procedure, prerequisites, and relevance to the affected behavior or artifacts. |
| Documentation checks | UNKNOWN | Relevant repository procedure or a justified direct inspection of the affected artifacts. |

When adapting these entries, identify each command or procedure's source, intended use, relevant checkout/configuration/environment, and prerequisites. Command identity and intended use use the workflow's evidence vocabulary; execution uses the outcomes below. A configured command is not evidence of a successful run. Keep unresolved entries visible; never execute a placeholder or substitute a guessed command. A proposed new procedure remains a proposal until adopted where adoption is required.

## Regression and test integrity

- For a bugfix, SHOULD first reproduce the defect with a failing regression test when practical. Practicality depends on whether the failure is observable, sufficiently reproducible, and testable with proportionate effort using suitable infrastructure. Where practical, SHOULD show the defect before the fix and the corrected behavior afterward.
- When a failing regression test is impractical, MUST explain why and identify the alternative reproduction or verification used. If no adequate alternative exists, MUST retain that limitation. Behavior changes SHOULD add or update tests according to repository conventions and MUST satisfy applicable testing requirements. No particular testing architecture is imposed here.
- MUST distinguish a failure observed before the change, an introduced regression, and unknown origin where evidence supports the distinction. A pre-change run is useful but not mandatory for every task; other relevant evidence may establish origin. MUST NOT attribute or dismiss a failure without sufficient evidence. A pre-change failure does not prove that the final state has no additional regressions.
- MUST retain successful and unsuccessful observations for intermittent results. A later pass does not erase an earlier failure. An unclear cause or successful retry alone does not establish flakiness.
- MUST NOT disable, bypass, or weaken tests or security controls to obtain a passing result. An incorrect or obsolete test MAY be corrected within authorized scope when evidence establishes the intended behavior; MUST preserve verification of applicable requirements and explain why the previous expectation was invalid.
- Removing or skipping a test, or relaxing an assertion, requires substantive justification and compliance with applicable approval rules. Authorization alone does not justify losing required coverage. Changing a check MUST NOT be presented as proof that the original failure was fixed unless the affected behavior was independently established.

## Verification outcomes

Reported checks MUST use an outcome that accurately describes the evidence:

| Outcome | Meaning |
|---|---|
| `passed` | The relevant check completed successfully in the observed environment and scope. |
| `failed` | The check produced a failure; its origin is reported where established. |
| `incomplete` | Execution started but did not establish a complete result, such as an interrupted, timed-out, or partial run. |
| `not run â€” unavailable` | The check is identified, but a required capability, prerequisite, or permission is unavailable. |
| `not run â€” unknown` | No suitable command or procedure has been established. |
| `not run â€” deferred` | The check is identified but has not been executed; state the reason. |
| `not applicable` | The check is irrelevant to the work, justified under its governing applicability criteria. |

If failures coexist with an interrupted or partial run, MUST retain both the observed failures and incomplete verification. A single overall label must not erase either fact.

A successful process exit alone MUST NOT establish that intended tests ran or required coverage was achieved. MUST disclose skipped tests, empty selections, and partial scope when they limit confidence. An empty or entirely skipped intended selection does not satisfy a required check merely through a successful exit. A `not applicable` outcome MUST be justified under the governing applicability criteria.

Results MUST remain associated with the version, environment, and scope actually checked. Subsequent changes MUST trigger reassessment of applicability; reuse and rerun selection follow the workflow.

A valid requirement revision or permitted alternative MUST NOT retrospectively change an observed result. Preserve the original failed, incomplete, unavailable, or other outcome; record the replacement or alternative check's own result. MAY explain why the original check is no longer required or how an alternative satisfies the current requirement, without reporting the original check as passed.

## Required checks and incomplete work

A required check is one mandated by an applicable instruction, adopted acceptance criterion, or governing workflow. A recommendation is not automatically mandatory; authority follows [AGENTS.md](../../AGENTS.md#authority-and-mandatory-controls).

If a required check is unsatisfied, including failure, incomplete execution, or not being run for any reason, MUST report the affected completion criterion, observed result or limitation, and evidence, capability, or action needed to resolve it.

That obligation prevents verified completion until the required verification is satisfied or resolved through the router's valid revision, alternative, or exception rules, accounting for every independently applicable source. Criteria or scope changes follow [classification and authorization](../../AGENTS.md#classification-and-authorization), with evidence recorded through the workflow and the existing plan where one exists. Unresolved authority does not authorize an exception. Approval MUST NOT be represented as successful verification.

Partial results MAY be presented within authorized scope with explicit verification status and unfinished work. Presenting partial results does not authorize publication, deployment, or closure as `done`; closure follows [plan lifecycle and resumption](../implementation/workflow.md#plan-lifecycle-and-resumption).

The workflow's final report MUST retain material failures, incomplete coverage, skipped or empty intended selections, established or unknown failure origin, and unsatisfied criteria with prerequisites needed to continue. Concise prose is sufficient, but MUST distinguish implementation progress, verification status, and overall completion without hiding material limitations.

## Kit preparation-control checks

For this kit's Python adapter, use an existing Python 3.11+ interpreter and run
`<verified-python> -B -m unittest discover -s tests -v` from the kit root.
On Windows invoke an absolute executable with the PowerShell call operator (&).
The bundled Python 3.12 interpreter used by the installed hook is verified;
`py -3` is an optional launcher only where executable access is available.
The tests invoke the hook process with temporary files and no live application
services. They verify missing/incomplete/stale/out-of-scope preparation denies
covered mutations and valid preparation permits disposable writes. Installation
tests verify backups, idempotent hook merging and preservation of other settings.
These checks are required for changes to this adapter; they do not impose Python
or this command on unrelated target repositories.

Also check the actual installed Codex hook path with disposable canaries and
verify enabled/trusted registration. Keep Python fixture outcomes, real host
execution, configuration and unverified enforcement limits distinct. Review
documentation links/metadata, source diffs and Windows CRLF without rewriting
unrelated pre-existing changes. The installation guide owns its recovery steps.
