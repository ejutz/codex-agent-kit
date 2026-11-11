---
status: proposed
candidate: 1.2.0-rc.4
scope: opt-in read-only model selection and coordinator outcome validation
load_when: evaluating or piloting model routing
depends_on: [workflow.md, preparation-control.md, ../testing/strategy.md]
---

# Model routing candidate

The [workflow](workflow.md#opt-in-model-routing-for-read-only-work) calls the
selector after normal task preparation when the user opts into the isolated
pilot. The existing [preparation guard](preparation-control.md) retains control
of exact commands and tool permissions.

## Selection and preparation

Use GPT-6 Luna for trivial or bounded tasks with local or related scope, low
risk and uncertainty, routine reasoning, known dependencies and worthwhile
delegation. A material trigger on any of those dimensions selects GPT-6.1 Sol.
High-risk tasks and escalations stay with the coordinator. Verification derives
from the work and its impact independently of the model.

The coordinator adds a `routing` object to the current ready preparation using
the regular hook transport. The record retains `write_paths: []`. The routing
objective, risk and complexity must match the prepared values. Include the
same acceptance criteria and evidence that the coordinator will use to review
the returned result. For example, this is the value of `routing` for a literal read.

```json
{
  "kind": "analysis",
  "complexity": "trivial",
  "scope": "local",
  "risk": "low",
  "uncertainty": "low",
  "reasoning": "routine",
  "dependencies": "none",
  "delegation_value": "worthwhile",
  "objective": "Read README.md and report its first heading.",
  "acceptance": ["Quote the heading exactly and identify the file."],
  "assessment_basis": ["One known file and a directly verifiable output."]
}
```

For an inspection with a known shell command, the coordinator may also supply
`inspection_command` in the same assessment. The guard's existing literal-read
classifier must accept it. The launcher passes the exact command separately
from the original objective and criteria. This creates no new tool permission.

Use Python 3.11 or later. The optional launch goes through a new Codex CLI
execution with an explicit model, read-only sandbox, hooks enabled and approval
set to never. Register the exact launch command in preparation as required by
the existing guard. For decision-only usage, omit `--run-read-only` and the
binary/profile options, or use `--assessment task.json`.

```powershell
python -B scripts/model_routing.py --preparation $pilotPreparation --guard-config $pilotGuardConfig --workspace $pilotRepository --run-read-only --codex $pilotCodexBinary --codex-home $pilotProfile
python -B -m unittest discover -s tests -p test_model_routing.py -v
```

Use a dedicated, authenticated pilot profile. The launcher checks profile
separation, required catch-all command registrations and well-formed declared
trust metadata. The managed visualization directory can contain a separate
pilot profile. This preflight does not verify current hook-definition trust or
identify a callback as the kit guard. Codex owns trust enforcement. Confirm
enabled/trusted operation through the supported host mechanism and verify the
actual guard with a disposable negative control before relying on enforcement.
Keep the production launcher in read-only mode.

## Outcome review

The preparation's primary `type`, requirements, checks and sources remain the
governing context. `routing.kind` supplies supplementary suggestions; justify a
material difference from primary type in the existing `assessment_basis`.
The coordinator retains the original verification obligations and identifies
which checks are delegated and which remain its responsibility. A generic
suggestion does not authorize writes or waive an original required check.

The coordinator receives `needs_review`, `blocked`, or `escalated`. A reported
completion needs one observation per acceptance criterion. The coordinator
assigns the criteria IDs `AC-1`, `AC-2`, and so on, in prepared order. The model
receives each ID with the original wording and returns it as `criterion_id`.
The coordinator retains the complete ID-to-text mapping in its decision and
rejects missing, duplicate or unknown IDs with distinct reasons. The launcher
also passes the suggested verification and rejects malformed or failed responses. A zero process exit establishes that a reviewable result
was returned. The coordinator still checks whether the evidence proves the
task result.

Escalation retains the original assessment, signal, finding and evidence for
the coordinator. Reassess scope and authorization before any further dispatch.
For a revised assessment, the optional `escalation` object contains `signal`,
`finding`, `work_done`, `changed_files`, `open_decisions` and `evidence`.

## Safe failure diagnostics

The wrapper uses kit-owned messages, known schema labels and actual numeric
exit codes. Unknown causes remain unclassified. Raw CLI streams, exception
bodies and tracebacks are not copied into generated diagnostics. Public flags,
child schema and exit codes remain unchanged: 0 for selection or a reviewable
result, 2 for unsuccessful work, 3 for escalation. Preflight/input/invocation
errors use safe stderr; handled execution failures retain `blocked` results.
Runtime schema availability is checked before launch. No retry or fallback
dispatch is automatic. Tests require the separate development assets.

## Historical RC.3 diagnostic

RC.2 compared the criterion in the model's evidence with the original sentence
verbatim. A local reproduction returned `blocked` with the correct README
heading and a paraphrased criterion, and returned `needs_review` when the
original sentence was supplied. The first real CLI rejection recorded only the
generic error. Its ephemeral response was unavailable for exact attribution.
RC.3 preserves the original criteria and validates references by ID.

A live repeat with the original text read the correct heading and used the
right ID, then escalated after an unnecessary preparation submission. The
launcher now makes the permitted read path explicit and constrains the
structured signal to the same codes accepted by the coordinator.

## Historical RC.3 CLI verification

The observations below belong to the supplied rc.3 input. They are not new
execution evidence for the corrected rc.4 working candidate.

On 2026-11-06, the installed v1.2.0-rc.3 launcher was tested with the real
Codex CLI against the PRIMADOCA Instance Control repository. The coordinator
prepared each task separately and supplied a literal read command accepted
by the existing guard.

| Prepared task | Model launched | Evidence checked against source |
| --- | --- | --- |
| Trivial, local, low-risk README inspection | GPT-6 Luna | The exact first heading was `# PRIMADOCA Instance Control` (`AC-1`). |
| Complex, cross-component, low-risk deployment review | GPT-6.1 Sol | The Jenkins stages were `Checkout → Validate → Deployment preflight → Deploy and verify` (`AC-1`). WinSW uses `NT AUTHORITY\LocalService` and the loopback address `127.0.0.1:3080` (`AC-2`). Jenkins execution, target service ACLs and reboot behavior remained unverified (`AC-3`). |

The CLI completed both turns using the selected models and the prepared
literal reads. Each model reported `completed`; the coordinator returned
`needs_review`, and the observations were independently checked against
the repository files. Both runs used the isolated profile, the `read-only`
sandbox and `write_paths: []`. Before and after hashes matched for the
global configuration, installed guard and task source files.

The Sol run was a static review of `Jenkinsfile`, the WinSW template and
`README.md`. No pipeline, application, service operation or deployment
test ran. The earlier Luna canary denial was a separate guard probe.

## Historical RC.3 probe narrative

The supplied rc.3 guide describes an earlier V1 Luna read and patch-scope denial,
and a V2 dispatch attempt gated by a changing encrypted input fingerprint. It
also describes a separate patch acceptance probe. That probe and a reproducible
result record are absent from the supplied package. These statements retain
input provenance; they are not reproduced rc.4 execution evidence or an available
runtime verification procedure.

## Pilot and adoption

Prepare explicit task-specific acceptance criteria before each pilot. Review
the returned observations and summary against independently observed source
output; merely containing an expected phrase cannot establish a correct result.
A literal-read experiment may specify a strict response format without changing
the general result schema. Distinguish format mismatch, incorrect source output
and missing execution evidence. `needs_review` retains coordinator ownership.

Keep each guard claim tied to the exercised operation and exact denial reason.
A local patch callback checks path-scope rejection. A native unprepared-command
control checks command preparation through the client and trusted hooks. The
latter does not establish native patch-path enforcement. Record the client,
guard/configuration identity, preparation scope, actual tool feedback and target
preservation; absent canaries and process success alone do not establish denial.

Compare equivalent tasks with the existing Sol workflow before default adoption.
Record acceptance, elapsed time, tokens, retries, escalations and verification
effort. The candidate adds no write-enabled launch mode.
