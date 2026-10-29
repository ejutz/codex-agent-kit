---
scope: routing index for the development-agent package and adapted target documentation
load_when: at task startup with applicable instruction files, and when selecting additional documentation
depends_on: []
---
# Documentation Index

Paths are relative to this index. Entries select context; authority and dependency resolution belong to the [router](../AGENTS.md#context-and-dependencies). Read relevant documents and required prerequisites only. An adequate unchanged index may be reused. Register target-specific entries and verified path mappings here during authorized integration.

## Instruction integration
- `implementation/instruction-loading.md` · stable global reference, origin-independent target instructions, preservation, and update verification · **configuring loading or migrating project instructions**
- `implementation/migrate-project-instructions-prompt.md` · reusable user request for another project's migration · **the user requests the same migration in another project; task artifact only**

## Workflow
- `implementation/preparation-control.md` · machine-readable preparation record, synchronous Codex hooks, installation, trust, rollback and limitations · **before modifications when the global control is installed, or installing/testing it**
- `implementation/workflow.md` · evidence and adaptation, proportional phases and verification, lifecycle and resumption · **preparing, performing, resuming, or reporting a task**

## Planning
- `planning/done/preparation-control.md` · authorized implementation, validation evidence and global-installation checkpoint · **resuming or auditing this control implementation**
- `planning/_template-plan.md` · optional format for scope, progress, gates, evidence, and continuity · **creating a persistent plan when selected or required by applicable instructions**
- `planning/active/` · open plans and checkpoints · **find the relevant plan for ongoing or resumed work; inspect selected records only**
- `planning/done/` · closed-plan archive; records retain their actual terminal state · **when relevant prior work explains affected decisions or behavior, including without an explicit history request**

## Design
- `design/architecture.md` · evidence-backed target structure, boundaries, data flows, and visible unknowns · **when architecture affects analysis, feature, refactor, infrastructure, or adaptation work**
- `design/decisions/` · adopted, proposed, or superseded decisions with provenance · **when an affected decision or its rationale matters; select relevant records only**
- `design/_template-adr.md` · decision-record format · **recording a significant design decision when the target uses this format**

## Practices and preferences
- `practices/coding.md` · project coding additions and references to governing policy · **writing or reviewing code**
- `practices/git.md` · project Git conventions and authorization references · **Git operations or proposed changes to established Git workflow**
- `practices/security.md` · policy coverage assessment and project security additions · **security, privacy, secrets, permissions, external input, data impact, required policy assessment, or high-risk execution**
- `preferences/developer.md` · adopted project preferences within governing requirements · **writing code or when a relevant communication or implementation preference applies**

## Verification
- `testing/strategy.md` · verified checks, regression evidence, outcomes, test integrity, and incomplete required checks · **selecting or interpreting checks, assessing failures, or determining verified completion**
