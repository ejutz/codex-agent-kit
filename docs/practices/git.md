---
scope: target-specific version-control workflow and policy references
load_when: version-control actions or repository workflow conventions are relevant
depends_on: []
---
# Git

Authorization for Git and externally visible actions follows [classification and authorization](../../AGENTS.md#classification-and-authorization). The [authority and mandatory-control rules](../../AGENTS.md#authority-and-mandatory-controls) govern branch protection, prohibitions, and actual global or project workflow requirements. This document records repository-specific additions and references; it does not grant authorization or introduce a competing approval policy.

**Target adaptation: UNKNOWN.** Inspect available version-control state and applicable workflow sources using [evidence and adaptation](../implementation/workflow.md#evidence-and-adaptation). Record confirmed absence of version control separately from inaccessible or unknown state.

| Subject | Target-specific record |
|---|---|
| Branch strategy and names | UNKNOWN — reference actual policy or established practice. No branch-per-task default is imposed. |
| Commit format and grouping | UNKNOWN — reference adopted convention; no Conventional Commit or commit-per-step requirement is imposed by this template. |
| Review and integration | UNKNOWN — reference required reviewers, checks, and merge procedure where established. |
| Protected operations | UNKNOWN — locate applicable protection rules, authorization requirements, and technical boundaries. |

Preserve established workflows and unrelated working-tree changes through the workflow's integration method. An observed convention is evidence, not authority to override an applicable instruction. Absence of an observed convention does not adopt a template rule; routine choices within authorized work follow the router.

When an authorized review or change description is needed, use the workflow's [reporting requirements](../implementation/workflow.md#verification-and-reporting) and any applicable repository template. Link an existing plan when useful; no extra plan or commit is required merely to populate a description.
