---
scope: canonical route registry and automatic required-context validation
load_when: preparing context with the adapter, changing routing or diagnosing context failures
depends_on: [../../AGENTS.md]
---
# Required Context Resolution

The router delegates the package's route mapping to [context-routing.json](context-routing.json). It is the single source of package selectors for the agent and the preparation adapter. Repository-specific context remains selected from applicable target instructions, indexes and evidence. Selection does not grant authority or resource access.

## Route registry

The registry is a version-1 JSON object with exactly `version`, `concerns` and `routes`. `concerns` maps stable identifiers to assessment prompts. Each route contains a unique `id`, a nonempty `paths` list and a nonempty `any` list of selector objects. Unsupported versions, keys, identifiers or values fail validation.

Within a selector, all entries must match; between selectors, any match selects the route. An empty selector always matches. Supported keys are `type`, `risk` and `concern`; values use the preparation task/risk vocabulary or a defined concern identifier. A concern matches when its recorded `applies` is true. Route paths resolve from the registry's directory, not the workspace. Changes to the registry are policy-routing changes subject to the router's authorization rules, not task-local exclusions.

The registry selects package guidance; it does not discover all relevant target source code, historical decisions or semantic concerns. The agent must still select that evidence. Keep new target documents in `sources` so their own dependencies are resolved as well. Do not interpret arbitrary prose in `load_when` as executable logic or use it to cancel a dependency.

## Preparation fields and resolution request

Every ready preparation includes `concerns`: one entry for each current registry identifier, with exactly boolean `applies` and a non-placeholder `reason`. The agent must justify both inclusion and exclusion from task evidence. A valid boolean/reason does not prove a correct assessment. Unconditional type/risk routes remain required regardless of a negative concern assessment.

For automatic discovery, read the current draft, classify `type` and `risk`, fill the concern assessments and retain the current session/workspace/generation. Add any already selected sources, intended command directories and known write paths, then submit the record with `status: "resolve"` through the existing data-only [preparation transport](preparation-control.md#operation).

The callback resolves context and stores a **draft**, with current paths/hashes and reported cycles. It clears requirement and pre-execution assertions. It does not read content into the model or enable task writes. Read the resulting record and required documents, assess their obligations and authorization, resolve any reported cycles, then submit the completed preparation with `status: "ready"`.

The resolve request itself must match the current task identity. Missing files or malformed metadata leave readiness revoked; independent permitted diagnostics remain available. Existing ready records from an earlier adapter must be refreshed after upgrade: missing concern assessments cannot silently count as completed preparation.

## Dependency traversal

Resolution starts with the kit router, route registry and guard identity, always-selected package routes, applicable global/project instructions, available root/current target indexes, task-selected routes and explicit source roots. For actual supported operations it also resolves instructions along the affected directories. It does not scan unrelated folders.

The adapter interprets `depends_on` only in Markdown front matter beginning on the first line with `---` (a UTF-8 BOM is accepted), ending with another `---`. The supported literal subset is:

- One unindented `depends_on` field, with an inline list such as `[workflow.md, "../design/architecture.md"]`, or a block list of literal file paths.
- Unquoted simple paths, single-quoted literal paths with doubled apostrophes, or double-quoted JSON strings. Use quotes for spaces or punctuation and `/` for portable separators.
- `depends_on: []` for no prerequisites. Full-line comments in block lists are permitted. Aliases, tags, mappings, folded values, inline comments and other unsupported dependency syntax must be rewritten to this subset; it is not silently interpreted as an empty list.

Absent metadata adds no declared dependencies and waives no applicable instruction. Non-Markdown sources remain identity-checked without interpreting their contents as metadata. Dependency paths resolve from the declaring file; absolute references must identify an actually applicable, authorized prerequisite. Environment variables, globs, fragments and commands are not expanded or evaluated.

Traversal is iterative and uses resolved platform path identities. Each document is visited once per graph resolution; shared prerequisites and equivalent references do not create cycles. Missing/unreadable files and unsupported metadata block the dependent operation. The adapter's existing 262144-byte processing limit applies per Markdown document and JSON record/registry; exceeding it is reported, never silently truncated. No new document-count or dependency-depth limit is imposed.

## Cycles and freshness

The computed graph reports cycles as closed path lists. A cycle does not automatically invalidate its documents. Before readiness, `context_cycles` must match the current cycles, each entry containing `paths` and a concrete `resolution` describing how the complete guidance is usable and any remaining dependent blocker. If guidance remains unresolved, keep preparation unready. The callback checks the cycle identity and presence of a resolution; interpretation remains an agent assessment.

Every required source must be present in `sources` with its current hash, including transitive prerequisites. Declared `not_applicable` check results do not remove graph obligations. Recompute at ready submission and before dependent operations: a new override, route, dependency or source change cannot be covered merely by an older ready record. Review previously acknowledged cycles again when their identity changes; preserve material interpretation changes under the normal reassessment rules.

## Evidence boundary

These checks establish the computed context set and current source identities. They do not establish that content reached the model, that it was understood, that every natural-language concern was identified, that all requirements were enumerated or that authorization is authentic. The normal tool-path, editable-configuration and target-installation limitations of the adapter remain in force. A successful resolution is not an approval, a passed test or certification of full policy compliance.
