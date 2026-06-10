# Governance (meta) — Layer 2 Decision Log

> Append-only chronological entries. Never delete or modify existing entries.
> Each entry records a [DECISION] / [TRADEOFF] / [CONSTRAINT] from a shipped spec.
> Domain scope: meta-governance — rule authoring, enforcement tiers, behavioral evals,
> session/lock discipline. (Document lifecycle decisions live in document-governance.log.md.)

---

### [governance][2026-06-10][feat/deletion-first-add-gate]
source_spec: docs/specs/deletion-first-add-gate.md
source_sha: ccb0294

[DECISION] 3 tiers, not 4: "external standard" as a standalone tier fails the [enforcement] lesson's test (citation ≠ enforcement); demoted to supporting metadata. Tiers map 1:1 to the lesson's taxonomy (validator/test/hook · eval case · named observer), ordered strongest-first so authoring is "pick strongest feasible", not a 4-way judgment.

[DECISION] Deletion-First scope = the three always-loaded surfaces only (AGENTS.md, .agent/rules/*, shared-contracts.md). Workflow files are heading-scope-read and mostly receive operational fixes — taxing each tweak with a deletion citation is the heaviness this feature is forbidden to add. The ADD-gate still covers workflows for NEW gates.

[DECISION] T2 is constrained to rules inside the eval harness's governance files — the seed-schema test requires `protects` anchors to resolve against that inventory; expanding the inventory for workflow gates would be scope creep (workflow gates use T1: validate.* already does workflow-literal checking).

[CONSTRAINT] `signal_tier: none` escape exists so tooling-only governance specs don't WARN forever — a nagging false positive trains people to ignore the validator.
