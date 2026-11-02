---
scope: adopted methodology extension for proportionate engineering artifacts, reviews, and revision traceability
load_when: preparing, performing, resuming, or reviewing development changes under the adopted extension
depends_on: [workflow.md, ../testing/strategy.md]
status: accepted
owner: user
baseline: v1.1
adopted_on: 2026-11-01
---
# Engineering Method

Engineering Method is a compatible extension of the development workflow, adopted in the current working package through the router. It organizes engineering work and its evidence without replacing the core policy owners. This adoption is subsequent to the v1.0 baseline; it does not certify a target installation or automatic enforcement.

## Scope and ownership

The [router](../../AGENTS.md#delegated-document-owners) delegates methodology, artifact mapping, review preparation and document-revision traceability to this document. Classification, authorization, authority, context resolution and global-policy prerequisites remain with the router; plan states and general verification remain with the [workflow](workflow.md); verification outcomes and required-check handling remain with the [testing strategy](../testing/strategy.md).

Use Engineering Method when applicable instructions adopt this extension. Adoption of the core alone does not adopt it. Preserve an established compatible target method and map these outcomes to it. Names below describe artifact roles, not mandatory filenames, folders or separate files. Missing target structure calls for a verified mapping, not invented paths. If selected required guidance is unavailable, defer its dependent actions under the router; continue independent permitted work without silently dropping the obligation.

## Process depth and classification

The agent assesses the task from repository evidence under [classification and authorization](../../AGENTS.md#classification-and-authorization). It remains responsible for that assessment; a schema validator does not establish that its classification is correct. No separate Governance Engine or aggregate risk/permission score is assumed.

The following optional depth labels summarize the workflow's preparation levels. They select detail, never permission, mandatory approval gates, or a fixed sequence of phases.

| Depth | Usual fit | Proportionate record |
|---|---|---|
| Light | Trivial work under the actual preparation exemption | One-line action and verification; direct evidence. |
| Standard | Bounded investigation and changes | Brief objective, scope, verifiable steps, relevant checks and material risks; design notes only where needed. |
| Extended | Complex execution, significant decisions or difficult verification | Inspected scope, design decisions, dependencies, individually verifiable steps, tests, risks and material assumptions. |

Inspect uncertainty before increasing depth; explain any material adjustment. Complexity, risk and authorization retain their independent assessments. Security precautions and required checks still apply to a mechanically small change. Do not impose a Discovery/SPEC/TDD document bundle merely because work uses Standard depth.

For analysis-only work, use the workflow's [read-only route](workflow.md#analysis-and-read-only-work): define the question, scope, evaluation criteria and evidence proportionately. No implementation steps, approval gate or artifact edits arise from this extension. Reviewing a design does not authorize implementing it.

## Phases and artifact mapping

Select and revisit the phases that contribute to the requested outcome or satisfy applicable requirements. Existing evidence may satisfy a phase; record material gaps instead of regenerating documents. Conversation sections may hold the result unless an applicable rule requires persistent storage.

| Phase / artifact role | When useful | Minimum outcome and existing location |
|---|---|---|
| Discovery | The problem, scope or constraints are unclear | Objective, stakeholders where relevant, boundaries and open questions in the task conversation or existing plan. |
| Specification (SPEC) | Behavior or acceptance needs definition | Observable behavior, contracts, constraints and acceptance criteria in existing target requirements or the plan's objective/criteria sections. |
| Technical design document (TDD) | A significant technical choice or interface is affected | Alternatives, selected approach, contracts, data/control flows and consequences in target design documentation or `docs/design/` when mapped. TDD means technical design here. |
| Implementation plan | Execution needs written preparation | Use the [existing plan format](../planning/_template-plan.md) or an adopted equivalent; verified target planning location only. |
| Implementation | The requested changes are authorized and prepared | Changes scoped to the plan, with actual progress and deviations recorded under the workflow. |
| Test plan / test report | Selecting checks and recording outcomes | Intended checks in the plan; canonical command definitions in target testing guidance; actual results in the existing plan or report. |
| Review | Assessing the resulting change or a requested proposal | Findings, affected criteria, evidence and unresolved issues in the existing review record or conversation. |

Principles continue to live with the existing practice owners. Significant architectural decisions use the established ADR convention. Approval requirements stay with their governing sources; no new approval-policy file, parallel roadmap, `engineering/` tree or `.agent-config/` installation is required.

## Architecture and security reviews

Assess architecture when the task materially affects boundaries, contracts, dependencies, data flows or significant design decisions. Assess security when permissions, sensitive information, external input, trust boundaries or other applicable security concerns are affected. Record the applicability decision and its evidence proportionately; a trivial correction needs no standalone review record.

For an applicable review, identify the affected decisions or controls, evaluation criteria, evidence examined, findings and dependent actions. Address preparation findings before the affected implementation step and verification findings before claiming that step complete. These are review activities, not automatic human-approval gates. A required independent reviewer comes from an applicable rule, not the depth label; self-review is not independent review.

Security coverage and high-risk preparation use the canonical [policy coverage assessment](../practices/security.md#policy-coverage-assessment). This extension supplies no substitute global policy or new risk-based approval threshold. Required-check blockers, permitted alternatives and exceptions follow the testing strategy and the router's [mandatory-control rules](../../AGENTS.md#authority-and-mandatory-controls).

## Separate state dimensions

Do not place document review, authorization, execution and verification on one progress ladder. Reuse the adopted format with these distinct meanings:

| Dimension | Owner / recording rule |
|---|---|
| Document status | Drafting, review and adoption status of that artifact, using the target vocabulary; identify its revision and any remaining findings. An accepted document is not permission to execute it. |
| `lifecycle_status` | The plan's lifecycle under the [workflow](workflow.md#scoped-states), including blocked, paused, cancelled and superseded. |
| `execution_status` | Each step's progress under the workflow; preserve skipped or superseded reasons. |
| `authorization_status` | Each actual gate under [authorization records](workflow.md#authorization-records); omit gates that do not apply and retain the authorization basis. |
| Verification outcome | Each performed or unavailable check under [verification outcomes](../testing/strategy.md#verification-outcomes); do not replace results with a generic VERIFIED state. |

Do not invent an approval step to move a document out of draft. Document acceptance, where required, follows the actual responsible authority and adopted process.

## Approval and revision traceability

When an actual approval covers a document, identify its location and reviewed revision with an immutable reference, preserved snapshot or content digest. Link the authorizing user instruction or recognized mechanism, governed action/scope and relevant conditions in the existing authorization record. A digest identifies bytes; it neither authenticates the approver nor grants permission. Keep the approved revision identifiable after later edits.

For a changed approved artifact, compare the current revision with the covered revision and apply the router's [material-change rule](../../AGENTS.md#classification-and-authorization):

- An editorial correction changes presentation without changing the covered meaning, obligations, scope or consequences. Record the revision relationship and basis for retaining authorization; a typo alone does not require renewed approval.
- A material change challenges the covered action or approach. Record the affected scope and reassess the applicable gate; obtain new approval only when the existing authorization no longer covers the action or a governing rule requires it.
- An unavailable comparison or uncertain material effect remains unresolved. Defer dependent actions while reconciling evidence; do not silently carry authorization forward.

Keep the original grant and original check results. A fresh artifact hash may be required by a technical adapter even when human authorization remains valid; these are separate reassessments. The optional extension section in the plan records these references without requiring another approval file.

## Preparation and evidence integration

Before the first modification, apply the workflow's [preparation verification](workflow.md#before-the-first-modification). Include this method, selected task guidance and transitive prerequisites in the resolved context under the router's [dependency rules](../../AGENTS.md#context-and-dependencies). Record unresolved guidance and the actions it prevents.

Where the [preparation adapter](preparation-control.md) is installed, assess the concerns defined by the canonical route registry and use its [context resolver](context-resolution.md) to calculate required sources and dependencies. Read and assess the resulting draft before completing relevant obligations in `requirements` / `pre_execution_checks` and submitting ready. Registration supplements the task plan and does not create a second authorization system.

Distinguish evidence at each stage: a discovered path; identified current bytes; content supplied to the agent through host context or an observed read; the agent's applicability assessment; and actual check results. State which stages are established. A hash alone proves no read; a read proves no comprehension; a tool-response receipt proves no successful verification. An agent declaration must remain identified as such.

**Implemented context checks:** the adapter derives required package sources from canonical routes, follows supported `depends_on` metadata from selected roots and operation instructions, requires reviewed cycles and checks source identity/freshness. **Remaining limitation:** declared task/concern relevance and cycle interpretation are not semantic proof; the adapter does not authenticate human approval or establish that all relevant target evidence or natural-language obligations were identified. Installation, trust, reload and actual client-path verification remain separate from package checks.

## Follow-up implementation targets

The following are proposed adapter improvements, not implemented capabilities or automatic prerequisites introduced by this extension:

- Evaluate the correctness of declared concerns, target-specific context selection and exclusion reasoning; the implemented resolver checks structure and declared selectors, not natural-language relevance.
- Associate source-delivery and check evidence with the relevant revision, task and operation while distinguishing host-supplied context from explicit reads and declarations.
- Verify actual hook registration, blocking and supported tool paths in the target; protect controls through independently governed host permissions when stronger enforcement is required.

The agent remains subject to the adopted instructions while those improvements are pending. A successful record validation must not be reported as full context or semantic validation.
