---
scope: shared entry-point loading, project-instruction separation, and update compatibility
load_when: configuring shared guidance, migrating project instruction files, or validating instruction loading
depends_on: [../../AGENTS.md, workflow.md, ../testing/strategy.md]
---
# Instruction Loading

Document type: Integration contract.
Status: Active; adopted by the user on 2026-10-26.
Scope: Shared development guidance loaded globally and origin-independent project instructions.

## Ownership and stable interface

| Owner | Content |
| --- | --- |
| Global instruction file | One stable entry-point reference and adoption scope for development tasks. |
| This package's entry point and delegated owners | Shared rules, routing, context selection, dependency resolution, security assessment, verification, and maintenance. |
| Target project instructions and guides | Project-specific architecture evidence, commands, platform constraints, contracts, and compatible conventions. |

The global loader references this package's root AGENTS.md. It does not enumerate internal documents, reproduce rules, or pin a commit/version. Keep that entry point stable across internal updates. A changed installation location or incompatible entry-point contract may require a loader migration; ordinary internal updates must not require editing the loader or target instruction files.

Project instructions must not contain this package's name, repository URL, checkout path, version/hash, loading procedure, or explicit adoption declaration. Their scope may state that they supplement the development instructions already applicable to the session. Loading and adoption occur globally; target files remain usable without knowledge of this package's identity.

The router owns authority and mandatory controls. This contract adds no alternative precedence order. Host instructions and technical permissions remain applicable; a global label does not mechanically prevent project overrides. Project-specific conventions supplement shared guidance within the actual governing hierarchy.

## Loading and target context

Load the shared entry point before dependent development work, then follow its selected context and delegated owners. Read the target's applicable instruction files and documentation entry point for project additions. Resolve package links from their declaring files and target paths from the actual task workspace.

A dependency already read in the same resolution pass need not be loaded twice. Reassess relevant content when it changes or a session resumes with potentially stale evidence; retain the router's completeness and prerequisite rules.

The global loader is a reference, not an independent body of safety policy. Required global policy still comes from actual governing host/configuration sources under the router's existing prerequisite. Do not resolve that requirement by circularly treating this package or its loader as a replacement policy.

Templates containing UNKNOWN are adaptation prompts rather than target facts or commands. Use target evidence and existing canonical documents without populating the shared checkout with each project's architecture or build commands.

If the entry point or selected prerequisite is unavailable, report the gap and defer dependent work under the router. Do not silently substitute project instructions for missing shared guidance.

## Migration and preservation

Inventory existing instructions and local changes before editing. Classify each affected rule as shared, project-specific, personal, historical, or unresolved. Remove a shared rule from the target only when its applicable canonical replacement is established; preserve unique project safeguards and do not broaden local preferences to all projects without authorization.

Keep historical records with their original scope, attribution, and verification. Mark superseded loading arrangements as historical, and remove them from active routing. Archive history must not become an operational prerequisite or substitute policy.

Update project entry points, specialist configurations, indexes, and active guides together. Active target instructions refer to target documents and project responsibilities; they do not reconstruct shared routing or package discovery. Preserve unrelated source, tests, configuration, and data.

Use the [migration prompt](migrate-project-instructions-prompt.md) for an authorized target migration. It is a reusable task artifact, not additional runtime policy.

## Verification and update lifecycle

- Check the global reference, actual override/configuration discovery, stable entry-point existence, selected dependencies, target links/fragments, index coverage, line endings, and whitespace.
- Compare project-specific safeguards and specialist contracts with the pre-migration snapshot; confirm unrelated changes remain intact.
- Verify active target instructions contain no package identity, path, hash, internal document routes, or copied shared-policy blocks.
- Use a fresh read-only session when available to identify loaded sources and explain the applicable analysis/feature workflow, project constraints, and missing-prerequisite handling. A documentary or resolver check alone is not a model-behavior evaluation.
- Test update independence in an isolated fixture: revise the referenced entry-point content while leaving global and target files byte-identical, then resolve/read it again. This proves reference independence, not universal model compliance.
- Distinguish passed artifact checks, unavailable fresh-session evaluation, and pending product runtime checks. Approval and verification remain separate under the testing strategy.

Update the installed checkout independently through its authorized version-control workflow. Do not fetch, pull, change branches, commit, or push automatically at task startup. Start a fresh session or explicitly revalidate changed guidance after an update; do not assume an existing session has refreshed its instructions.

## Global preparation hook integration

The global loader remains a single entry-point reference. The optional runtime
adapter is installed independently through [Preparation control](preparation-control.md).
The user's 2026-10-27 request activates it for this local installation. Keep kit
paths and hook configuration out of target-project instructions. Existing
sessions must not be assumed to reload new hooks or instruction bytes.

Validate loading, record validation, trusted hook registration and actual
pre-tool blocking as separate outcomes. A JSON/schema test alone is not an
executed Codex tool-hook test. Non-managed hooks need exact-definition trust
review through the supported client; never manufacture internal trust records.
Preserve other handlers and config layers. Report unsupported host paths,
callback failure behavior and pending client reloads explicitly.
