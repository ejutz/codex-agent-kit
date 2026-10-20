---
lifecycle_status: draft
primary_task: UNKNOWN
secondary_tasks: []
complexity: UNKNOWN
risk: UNKNOWN
---
# Plan: <title>

This is a recording template. Use it only when a persistent plan is appropriate under the [workflow](../implementation/workflow.md#planning-and-task-phases), or use an equivalent adopted format. Resolve UNKNOWN fields from evidence; they are not classifications. Verify the adopted active-plan location before creating a record. State definitions and transitions belong to [plan lifecycle and resumption](../implementation/workflow.md#plan-lifecycle-and-resumption).

## Objective and scope
- **Objective and expected result:** <what and why>
- **In scope:** <actions and affected resources>
- **Out of scope:** <relevant boundaries>
- **Complexity rationale:** <analysis, coordination, and decisions needed>
- **Risk rationale:** <consequences, exposure, and recovery limitations>
- **Context and constraints:** <existing behavior, invariants, applicable instructions, environment>

## Evidence and decisions
| Material claim or choice | Evidence status / decision status | Source and relevant checkout, configuration, or environment | Reasoning, uncertainty, or evidence needed |
|---|---|---|---|
| <claim or choice> | <VERIFIED / INFERRED / UNKNOWN for evidence; ACCEPTED / PROPOSED / OPEN for a decision> | <source and scope> | <basis or open issue> |

- **Relevant documents and dependencies loaded:** <paths; missing necessary context>
- **Approach and material alternatives:** <choice, justification, and adoption status>
- **Significant design decisions:** <existing ADRs or required decision record, if applicable>

## Acceptance criteria and verification strategy
| Criterion | Governing source or adoption evidence | Intended verification and scope | Required or additional, with basis |
|---|---|---|---|
| <observable result> | <source> | <identified check or UNKNOWN procedure> | <basis> |

- **Step and integrated checks:** <suitable coverage and completion points; shared evidence where relevant>
- **Verification prerequisites:** <capabilities, environment, access, and dependent actions>
- **Material verification limitations:** <unresolved procedure, unavailable prerequisite, or coverage gap>

Use established commands or procedures and record actual outcomes under the [testing strategy](../testing/strategy.md#verification-outcomes). A planned check is not evidence that it ran.

## Authorization
- **Authorization basis:** <user request and applicable authority, action, scope, and evidence; state when no explicit gate applies>

Include the following rows only for actual explicit gates. Identify user authorization and technical permission separately when both apply.

| Gate and governed action / scope | Requiring rule; authority or mechanism | authorization_status | Evidence and conditions |
|---|---|---|---|
| <actual gate> | <source and authority> | <pending / granted / denied / reassessment-required> | <grant, denial, or missing evidence> |

## Execution steps
| Step | Intended result and dependencies | execution_status | Suitable verification / evidence | Blocker, skipped or superseded reason |
|---|---|---|---|---|
| <step> | <individually verifiable result> | <pending / in-progress / completed / blocked; identify skipped or superseded explicitly> | <check and actual result reference> | <if applicable> |

## Risks and material assumptions
- **Risks and mitigations:** <consequences and preparation proportionate to risk>
- **Material assumptions:** <basis, uncertainty, and how to resolve>
- **High-risk preparation, if applicable:** <affected resources, expected consequences, verification, recovery or containment and limitations; link the required policy-coverage assessment>
- **Recovery limitations:** <irreversible effects or unavailable mechanisms, where material; do not promise unsupported rollback>
- **Open issues:** <issue, dependent action, and resolution needed>

## Results and deviations
| Observation / attempt | Version, environment, and scope | Actual result or evidence | Interpretation, deviation, and remaining work |
|---|---|---|---|
| <performed check or action> | <observed scope> | <outcome and evidence> | <limitations or next action> |

Retain unsuccessful attempts, incomplete effects, and later results separately. Identify material scope or criteria revisions with their authority and evidence; the existing results remain historical observations.

## Resumption checkpoint
- **Current lifecycle_status and reason:** <consistent with the plan field>
- **Last verified progress:** <evidence and scope>
- **Unfinished or uncertain effects:** <what must be reconciled before potentially repeating an effect>
- **Blocker or pause cause and condition to continue:** <if applicable>
- **Authorization and policy changes to reassess:** <affected gates or prerequisites>
- **Next permitted action:** <specific step, or condition that must be resolved first>

## Closure record
- **Acceptance and required verification:** <criteria satisfied, evidence, or outstanding obligations>
- **Remaining limitations or unfinished work:** <explicit scope and status>
- **Final lifecycle_status:** <actual state under the workflow; do not infer done from approval>
- **Successor:** <link if superseded; transferred progress, issues, and authorization scope>
- **Record location:** <verified adopted active or archive path, when applicable>
