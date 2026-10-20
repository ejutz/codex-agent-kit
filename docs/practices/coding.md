---
scope: target-specific coding conventions and references to canonical practices
load_when: when writing or reviewing code
depends_on: []
---
# Coding Practices

Use this document for repository-specific additions and references to actual governing rules. Authority and explicit delegation follow [AGENTS.md](../../AGENTS.md#authority-and-mandatory-controls); inspection, integration, and preservation follow [evidence and adaptation](../implementation/workflow.md#evidence-and-adaptation).

**Target adaptation: UNKNOWN.** No stack, naming scheme, formatter, or architectural convention has been established for a target repository. Resolve relevant entries from applicable instructions, observed code, configuration, and adopted design decisions rather than introducing a generic standard.

| Subject to inspect | Record when relevant |
|---|---|
| Structure and naming | Existing module boundaries, language idioms, naming rules, and canonical sources. |
| Types and invariants | Established type/nullability conventions and where boundary validation and domain invariants are enforced. |
| Errors and diagnostics | Error contracts, propagation, useful context, and applicable confidentiality restrictions. |
| Comments and formatting | Repository formatting configuration and conventions for explanations and documentation. |
| Dependencies and shared utilities | Existing abstractions, dependency constraints, and relevant project policy. |

These inspection prompts do not independently adopt coding rules. Reference canonical definitions rather than duplicating them. Consult [security](security.md) for relevant safety-policy coverage and [testing](../testing/strategy.md) for regression and test-integrity requirements. Preserve unrelated content and identify material disagreements between documented and observed conventions through the workflow.
