---
status: frozen
title: Deletion-First Norm + ADD-Gate Signal Tiering
source: GitHub issue #166 / backlog #65
created: 2026-06-10
primary_domain: governance
secondary_domains: [workflow, tooling]
signal_tier: 2
signal_tier_note: ADD-gate self-backed by a guarding eval case (T2, #45 coverage-tracked); the signal_tier frontmatter field itself is T1 (validator WARN checks presence). External anchors (QRSPI/ace-fca instruction-load research) are supporting metadata, not the tier.
---

# Deletion-First Norm + ADD-Gate Signal Tiering

## Goal

Make the repo's DELETE-bias discipline structural at rule-authoring time — without making the AI dumber (zero growth of always-loaded context) or the process heavier (no new hard gates; advisory-only enforcement; zero cost for non-governance tasks). Two norms: governance-doc changes must cite a deletion or justify the net-add; new rules must declare how they are enforced (signal tier) or not be added.

## Acceptance Criteria

- AC-1: `engineering_guardrails.md` gains a **conditional** §13 "Governance Change Norms" (≤ 15 lines incl. tier definitions): **Deletion-First Norm** — a change to `AGENTS.md`, `.agent/rules/*.md`, or `.agent/workflows/shared-contracts.md` (the always-loaded instruction surfaces) MUST cite a deletion/trim in the same change OR record a 1-line net-add justification in the Work Log. **ADD-Gate** — a NEW rule (MUST/NEVER/gate) anywhere under `.agent/**` requires a declared signal tier, strongest feasible: **T1 machine-enforced** (validator/test/hook exists or added in same change) · **T2 eval-backed** (guarding case added to `.agentcortex/eval/governance.yaml`; available only for rules in the eval harness's three governance files) · **T3 named human observer** (+ 1-line recorded unmeasurable-rationale). External citations are supporting metadata on any tier, never a tier. No feasible tier → do not add; prefer deletion. Existing rules grandfathered.
- AC-2: §13 is registered in the Heading-Scoped Read conditional list with trigger: change modifies `AGENTS.md`, `.agent/rules/*`, `.agent/workflows/*`, `.agent/config.yaml`, or adds any MUST/NEVER/gate.
- AC-3: `bootstrap.md` quick-win reachability fix (~2 lines): governance-path edits are directed to read §13 before editing, with a narrow Token-Leak-Block exemption for a heading-scoped §13 read on quick-win governance edits. Without this, §13 is structurally unreadable on the most common governance-edit path (= theatre).
- AC-4: `review.md ## Minimum Checks` gains ONE advisory bullet: governance-doc diff → verify deletion-cited-or-justified + signal tier present for any new rule.
- AC-5: `.agentcortex/eval/governance.yaml` gains one adversarial case protecting §13 (pressure to add a MUST skipping the tier/deletion discipline → expected refusal); `protects` tag resolves against the live MUST-rule inventory (enforced by the existing seed-schema test).
- AC-6: `validate.sh` AND `validate.ps1` (parity) add an advisory WARN: a `docs/specs/*.md` whose `primary_domain` contains `governance`, with `created:` ≥ 2026-06-10, `status` not in {shipped, cancelled}, and no `signal_tier:` line → WARN naming the file. `signal_tier: none` (spec introduces no new rule) silences it. Missing `created:` = grandfathered. Never FAIL.
- AC-7: Dogfood deletions land in the same change and are cited as this PR's Deletion-First compliance: (a) §5.3's duplicate scope bullet ("Never silently expand or shrink scope…" — strict restatement of the Gate-FAIL bullet above it; no machine consumer, grep-verified); (b) the stale Token-budget-estimate block in the Reading Mode header (meta-commentary whose hardcoded counts this very change invalidates).
- AC-8: This spec self-applies: `signal_tier: 2` in its own frontmatter (first machine-visible instance for the AC-6 check).
- AC-9: Guard test covers the AC-6 validator behavior with fixtures: missing field → WARN; `signal_tier: 2` → no WARN; `signal_tier: none` → no WARN; `created:` < 2026-06-10 → no WARN. Existing eval schema tests stay green with the new case.

## Non-goals

- No `AGENTS.md` content additions — zero growth of every-turn context (the norm reaches AGENTS.md *changes* via §13's trigger, not via text in AGENTS.md).
- No change to `.agentcortex/templates/spec-app-feature.md` — that template deploys downstream into APP projects; pushing `signal_tier` there would export irrelevant instruction load.
- No directive-counter tool or numeric instruction-count gate — Strand D of `_research-rpi-qrspi-corroboration.md` explicitly rejects naive count thresholds; the "MUSTs lacking validators" axis is already measured by the shipped #45 coverage WARN.
- No retro-fitting tiers onto existing rules (grandfathered; retrofit opportunistically via the delete-bias workflow).
- No hard gates anywhere in this feature.

## Constraints

- §13 body ≤ 15 lines; conditional load only (never part of core Full-mode read).
- All machine checks WARN-only, cross-platform parity (sh/ps1).
- The norm must remain reachable in the quick-win governance-edit flow (AC-3) — reachability is a hard design requirement, not polish.

## Enforcement Boundary (honest)

The AC-6 validator checks **field presence**, not tier truth — tier claims are verified by the reviewer (AC-4) and, for T2, by the #45 coverage WARN that fires automatically when a MUST-bearing section has no guarding eval case. Deletion-First compliance is observer-enforced (reviewer + Work Log record); building a machine net-add checker would be the rejected counter tool by another door.

## Follow-up (recorded, not shipped here)

- First `run_delete_bias_diff.sh` candidate: the guardrails "Loaded-Sections Receipt" (self-attestation MUST with no validator backing — [enforcement] theatre class, but has a claimed audit consumer; needs the measured diff before deletion).

## Domain Decisions

- [DECISION] 3 tiers, not 4: "external standard" as a standalone tier fails the [enforcement] lesson's test (citation ≠ enforcement); demoted to supporting metadata. Tiers map 1:1 to the lesson's taxonomy (validator/test/hook · eval case · named observer), ordered strongest-first so authoring is "pick strongest feasible", not a 4-way judgment.
- [DECISION] Deletion-First scope = the three always-loaded surfaces only (AGENTS.md, .agent/rules/*, shared-contracts.md). Workflow files are heading-scope-read and mostly receive operational fixes — taxing each tweak with a deletion citation is the heaviness this feature is forbidden to add. The ADD-gate still covers workflows for NEW gates.
- [DECISION] T2 is constrained to rules inside the eval harness's `_GOVERNANCE_FILES` — the seed-schema test requires `protects` anchors to resolve against that inventory; expanding the inventory for workflow gates would be scope creep (workflow gates use T1: validate.* already does workflow-literal checking).
- [CONSTRAINT] `signal_tier: none` escape exists so tooling-only governance specs don't WARN forever — a nagging false positive trains people to ignore the validator.
