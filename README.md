---
status: accepted
owner: user
baseline: v1.0
---
# Development Agent Package — v1.0

## Purpose and status

This package expresses the accepted development-agent requirements as a reusable project router and supporting Markdown documents. It is intended for a Codex host that supplies instruction discovery, repository inspection, and authorized execution capabilities. Specific tools, runtimes, repository commands, and permissions must be verified in the target environment.

**v1.0 is the approved first reference version containing the accepted specification and aligned package, closed on 2026-10-17.** Requirement adoption, version approval, target adoption, installation, and behavior evaluation are distinct outcomes.

> **Verification limitation:** Documentary verification completed; target installation and agent behavior evaluation pending.

The package is not operationally self-contained: required global policy, target-specific evidence, and host permissions remain external prerequisites. Markdown does not configure or enforce technical permissions. Acceptance scenarios describe intended behavior and are not executed agent evaluations. Successful installation checks alone do not validate agent behavior or resolve unavailable required policy.

## Authoring boundaries

Within this authoring workspace, the root design router governs design sessions and these files are artifacts under review. Start design sessions from the workspace root. A session inside this package may discover the nested `AGENTS.md`; proposal metadata does not disable discovery.

The following links are optional authoring references, excluded from the runtime payload and unnecessary for installed operation: [design router](../../AGENTS.md), [package separation decision](../../docs/decisions/DEC-0001-development-agent-package.md), and [requirement adoption and v1.0 preparation decision](../../docs/decisions/DEC-0005-adopt-requirements-and-prepare-v1.md). No installed document depends on that design framework or its session history.

## Payload and required prerequisites

The runtime payload is this directory's `AGENTS.md` and associated `docs/` tree. This README is an installation/authoring guide outside that payload. The router defines global-policy prerequisite behavior and delegates operational subjects inside the payload; no essential runtime rule exists only in this README.

Read the [package index](docs/INDEX.md) to select supporting files. Required links and dependency paths must resolve within the mapped payload, a verified target document, or an explicitly identified external prerequisite. Optional authoring references do not belong in runtime dependency metadata.

The required external policy subjects, discovery method, unmet-prerequisite behavior, and readiness boundary are defined by [Required global policy](AGENTS.md#required-global-policy), with the action-scoped assessment in [Security practices](docs/practices/security.md#policy-coverage-assessment). Actual global approval thresholds, safeguards, confidentiality rules, and technical boundaries come from their governing sources. Inspection, editing, execution, verification, and optional memory depend on available host capabilities; no particular memory service or tool name is assumed.

## Installation mapping

The sources below exist in this package. No target repository has been selected or inspected for this candidate, so target destinations are prospective and their existence is unknown.

| Verified package source | Prospective target destination | Adaptation before application |
|---|---|---|
| `AGENTS.md` | Applicable target `AGENTS.md` | Inspect existing instructions and scope; integrate router and delegated owners under the actual hierarchy. |
| `docs/INDEX.md` | Existing target index or authorized equivalent | Merge routes and rewrite references for the actual layout. |
| `docs/implementation/workflow.md` | Existing workflow owner or authorized mapped destination | Preserve adopted phases, planning storage, required checks, and authorization requirements. |
| `docs/planning/_template-plan.md`, `docs/planning/active/`, `docs/planning/done/` | Existing plan format and storage or authorized mapped destinations | Reuse a compatible format; map lifecycle, per-step progress, and per-gate authorization without forcing a second system. |
| `docs/testing/strategy.md` | Existing verification owner or authorized mapped destination | Populate commands from verified evidence; preserve required checks and their sources. |
| `docs/design/architecture.md`, `docs/design/_template-adr.md`, `docs/design/decisions/` | Existing architecture and decision records or authorized mapped destinations | Record observed architecture, retain unknowns, and reuse target ADR conventions and history. |
| `docs/practices/coding.md`, `docs/practices/git.md`, `docs/practices/security.md`, `docs/preferences/developer.md` | Existing corresponding owners or authorized mapped destinations | Retain established conventions, integrate scoped adopted additions, and reference canonical policy instead of copying it. |

The nominal root mapping is `AGENTS.md` to target `AGENTS.md` and `docs/` to target `docs/`. Preserve existing target structure unless changes are authorized; the concrete mapping distinguishes verified destinations from proposed creation. Adapt payload links to the actual mapping; `depends_on` resolves from the declaring document's directory.

## Integration procedure

Use the payload's [evidence and adaptation method](docs/implementation/workflow.md#evidence-and-adaptation) for installation or later adaptation. Before edits, inspect target structure, instructions, content, applicable policy, and available version-control state; prepare the concrete integration mapping and assess authorization under the router. Existing instruction replacements require explicit authorization identifying files. Preserve unrelated content and local changes; reuse compatible owners rather than creating competing guides.

Resolve placeholders, commands, architecture, workflows, and capabilities from actual target evidence. Unknowns remain visible and cannot become guessed commands or fabricated results. Installing or staging a proposal does not adopt it. Track target policy adoption separately from installation verification and account for instruction discovery when selecting a staging location.

Before reporting installation success, verify mapped references and prerequisites, unresolved placeholders, target preservation, and applicable required checks. Report actual scope, results, and limitations through the [workflow](docs/implementation/workflow.md#verification-and-reporting) and [verification outcomes](docs/testing/strategy.md#verification-outcomes). Required policy or capability gaps can restrict operation even when local document checks pass.

## Candidate scope and continuity — 2026-10-16

- **Accepted:** REQ-001–008 and their integrated corrections; earlier package-separation and scoped policy decisions remain applicable. The user authorized preparing specification plus aligned package with the visible limitation note.
- **Prepared here:** the existing package documents express the adopted requirements in their assigned operational owners. No target repository or installation is selected by this preparation.
- **Pending:** final documentary verification, approval of the concrete first version, target-specific adoption and installation, and agent behavior evaluation.
- **Baseline:** none until the user approves the concrete candidate. A version label is not evidence of operational validation.

## Candidate verification — 2026-10-17

Documentary review and local checks are complete: accepted requirement coverage, policy ownership, links and anchors, index entries, dependency resolution, status consistency, and payload isolation. The earlier preparation checkpoint above is historical. Final candidate approval, target-specific adoption and installation, and behavior evaluation remain pending; no target command or operational behavior was validated.

## Version closure — 2026-10-17

The user approved the presented first version by requesting its verification, commit, and `v1.0` tag. The authoring-only [approval record](../../docs/releases/v1.0/approval.md) identifies the unchanged reviewed snapshot and documentary verification scope. It is outside the runtime payload. This section supersedes the pending version-approval statements in the historical checkpoints above; target-specific adoption and installation, and behavior evaluation, remain pending.
