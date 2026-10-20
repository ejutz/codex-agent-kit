---
scope: action-scoped safety-policy coverage assessment and target-specific security references
load_when: high-risk preparation, security or privacy impact, sensitive data, permissions, external input or disclosure, policy coverage assessment
depends_on: [../../AGENTS.md, ../implementation/workflow.md]
---
# Security

This document owns the safety-policy coverage assessment within the scope delegated by [AGENTS.md](../../AGENTS.md#authority-and-mandatory-controls). The router owns [required global-policy availability and unresolved-policy behavior](../../AGENTS.md#required-global-policy), [classification, preparation and authorization](../../AGENTS.md#classification-and-authorization), and authority. This assessment references actual safeguards rather than defining competing approval thresholds, dependency conventions, or confidentiality exceptions.

## Policy coverage assessment

Before dependent high-risk execution, MUST map intended actions, affected resources, and material effects to these four required subjects. Applicable general rules MAY establish coverage without naming every command or resource.

| Required subject | Canonical sources to identify and assess |
|---|---|
| Risk classification, affected resources, consequences, verification, and recovery limitations | The router's classification and authorization rules and the applicable governing instructions. |
| Authorization for each intended action | The router and the actual governing approval rules, resolved through its authority rules. |
| Mandatory safeguards, prohibitions, permitted exceptions, and technical boundaries | Every applicable governing policy source and the host's enforced boundaries. |
| Secrets, credentials, sensitive data, and disclosure restrictions | Applicable governing security and privacy policy. |

For each required subject, MUST identify the authoritative source, applicable scope, availability evidence, and material conflicts or coverage gaps. Use current evidence under the [workflow](../implementation/workflow.md#evidence-and-adaptation). Establish actual approval thresholds and mandatory controls from their governing definitions; do not invent values or duplicate those definitions here.

Coverage is sufficient for the assessed scope only when all of the following hold:

1. Required global-policy sources are available; their identity, authority, applicability, and material conflicts are resolved under the router using current evidence.
2. Each of the four subjects is traced to applicable canonical sources and relevant rules for the intended actions and resources, accounting for every independently applicable obligation under the router.
3. No material unresolved gap remains concerning authorization requirements, mandatory safeguards or prohibitions, enforced boundaries, or confidentiality and disclosure restrictions.
4. The router's action-specific high-risk preparation is identified. Recovery or containment limitations, including irreversible effects, are explicit. An unavailable recovery mechanism is not described as established; performing recovery or containment remains subject to the router's authorization rules.

A subject's limited relevance MAY be recorded with a reason supported by inspected policy and observed scope. This does not waive a required global-policy source, treat unavailable rules as inapplicable, or infer permission from silence.

Sufficient coverage establishes which rules govern the assessed work. It establishes neither granted authorization nor satisfied controls nor permission to act. A clear prohibition can provide sufficient coverage while preventing execution. Check satisfaction follows [required checks](../testing/strategy.md#required-checks-and-incomplete-work); authorization and permitted exceptions remain with the router.

The assessment applies only to the assessed actions, resources, environment, and evidence. It is neither general safety assurance nor an operational-readiness claim. Material changes require targeted reassessment through the router and workflow. A source's existence alone is insufficient. Missing policy or a material unresolved coverage gap follows the router's unresolved-policy behavior. This assessment creates neither a standalone fallback nor an approval gate based solely on a risk label.

## Sensitive material encountered

Sensitive material encountered during inspection or adaptation MUST be handled under governing confidentiality and privacy rules. Issue descriptions MUST avoid reproducing sensitive values. Discovery alone does not authorize deletion, rotation, or external notification; those actions follow the router's authorization rules.

## Target-specific additions and references

**Target adaptation: UNKNOWN.** Record relevant security and privacy policy sources and any explicitly delegated repository-specific additions after inspecting the target. Preserve established controls and reference their canonical definitions; this template supplies no policy replacement.

Relevant inspection subjects include trust boundaries, input validation and domain invariants, access controls and least privilege, secrets handling, diagnostic disclosure, dependencies, and data integrity. They are prompts for locating applicable controls, not independently adopted implementation prescriptions. Document relevant source, scope, evidence, and unresolved coverage through the assessment above. If a doubt affects an action, apply the router's unresolved-policy and authorization rules to that dependent action.
