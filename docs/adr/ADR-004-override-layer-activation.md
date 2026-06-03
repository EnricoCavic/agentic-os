---
status: accepted
date: 2026-06-03
classification: architecture-change
primary_domain: document-governance
deciders: "@kbwen + Claude Opus 4.8 + multi-expert workflow (3 rounds, 20+ agents; 48-scenario catalog; external prior-art on Copier/Cookiecutter/git-subtree/Nix/Kustomize/VSCode layering)"
applies_to:
  - "AGENTS.md"
  - ".agent/workflows/bootstrap.md"
  - ".agentcortex/docs/guides/doc-governance.md"
  - ".antigravity/rules.md"
  - "codex/rules/**"
lifecycle:
  owner: "/adr"
  review_cadence: on-event
  review_trigger: "When a downstream consumer needs override semantics the spec did not anticipate, OR when a platform changes its native override convention"
  supersedes: none
  superseded_by: none
---

# ADR-004: Override Layer Activation

## Context

Downstream users are now arriving (fork and clone+deploy). They bring their own
skills and, in some cases, their own governance preferences. The framework needs
a place where a downstream project (or an individual user) can **refine, narrow,
or disable** specific governance directives **without editing framework-owned
files in place** — because editing framework files in place causes merge
conflicts on `git pull upstream` (fork path) and silent loss on the next
`deploy` (clone path).

A multi-round expert analysis discovered that this layer **already exists in
spec but was never wired into the runtime**:

### Evidence (Verified)

- `.agentcortex/docs/guides/doc-governance.md` §"Override Layer (`AGENTS.override.md`) — soft-launch" (lines 35–51): a complete specification — precedence chain (`AGENTS.md` → project-root `AGENTS.override.md` → `~/.agentcortex/AGENTS.override.md`), a "MAY refine/narrow/disable, **MUST NOT** relax `## Delivery Gates` or the No-Bypass Rule" carve-out, the citation convention `> Overrides: AGENTS.md §<section> — <reason>`, and `Status: soft-launch. Documented but not yet runtime-enforced.`
- It explicitly mirrors the Codex `AGENTS.override.md` precedence convention (vendor-grounded, cross-platform).
- `AGENTS.md:97` is only a pointer HTML comment: `<!-- Override Layer (AGENTS.override.md) is soft-launch — see ... -->`.
- `.agent/workflows/bootstrap.md` has **no** override-load step — so the layer is inert.
- A working **lazy / present-only** extension-seam precedent exists at `.agentcortex/context/private/user-preferences.yaml`, loaded by `bootstrap.md §3.6a` (capability-by-presence: absent → zero cost).

The decision the team made when it first shipped the soft-launch (no consumer yet → don't wire) was correct **at that time**. The arrival of downstream users is the new evidence that flips the calculus.

## Decision

**Activate the override layer as a lazy, present-only governance read at bootstrap session start.**

1. `bootstrap.md` gains a step (after SSoT read, before Work Log setup): check for `AGENTS.override.md` at project root, then `~/.agentcortex/AGENTS.override.md`. **Present → read and apply per the precedence chain; absent → zero reads, zero tokens** (mirror the `§3.6a` capability-by-presence pattern). Record loaded override filename(s) + source, or `Override: none`, in the Work Log `## Session Info`.
2. The carve-out is **enforced as a warn-only advisory**: if an override directive cites `> Overrides: AGENTS.md §Delivery Gates` (or `§Core Directives`/No-Bypass Rule), bootstrap emits a WARN, records `rejected` in the Work Log `## Drift Log`, and does **not** apply that directive. It does **not** hard-block (a pure-text override cannot be machine-proven to "relax" vs "legitimately narrow" a gate; hard-blocking would false-kill legitimate narrowing).
3. `doc-governance.md` §51 status flips `soft-launch` → `active`; §49 "SHOULD read … when present" → "**MUST** read … when present"; an Implementation Contract subsection points at the bootstrap load step. The §47 carve-out text is unchanged.
4. **Read-Once compliant**: override files are read once at session start and recorded; later phases trust the recorded result and MUST NOT re-read.

**Honest enforcement boundary** (per Global Lesson `[enforcement][HIGH]`): "an agent reads the override when present" is, like the Sentinel, ultimately honor-system — no test can prove a given agent read a file. The *machine-enforceable* part is **structural**: a `validate.sh`/`validate.ps1` check that `bootstrap.md` still contains the override-load step (the framework ships the instruction). We do **not** add a fake MUST that pretends per-agent behavior is enforced.

**Compliance check**: given a project `AGENTS.override.md` containing a non-gate directive, a bootstrap run records that filename in the Work Log `## Session Info`; given a gate-relaxing directive, the run records a `rejected` WARN in `## Drift Log`.

## Alternatives Considered

- **Build a new `AGENTS.local.md` + unconditional `@import` layer** (the initial proposal). Rejected: it is a re-skin of the already-shipped `AGENTS.override.md`, violating one-topic-one-file; and an eager `@import` would pin a near-empty governance file into every downstream turn's warm-cache prefix, violating `§Context Pruning`/`§Read-Once`/`§Response Brevity`. The proven seam (`user-preferences.yaml`) is **lazy**, not eager — activate the existing lazy design instead of inventing an eager twin.
- **DELETE the soft-launch override spec** (the round-1 verdict, on DELETE-bias + "no consumer"). Rejected: the "no consumer" premise no longer holds now that downstream users are arriving; deleting the comfort layer exactly as users arrive is premature.
- **Keep it parked.** Rejected for the same reason — leaving a shipped-but-inert governance mechanism is the worst state (documented but non-functional → user confusion).

## Consequences

**Positive**: downstream forks/clones get an official, cross-platform-aligned (Codex-originated), token-safe place to customize governance without editing framework files → additive forks stay `git pull`-clean; the dual-purpose-repo "don't edit our files" guidance gains a concrete home. Resolves the shipped-but-inert state.

**Negative / accepted**: the override-read MUST is honor-system at the per-agent level (mitigated by structural validator, stated honestly). A stale `AGENTS.override.md` across skipped framework versions can reference a renamed/removed section (NEW risk; documented boundary — a future validator may detect orphaned citations). The carve-out is warn-only, so a determined agent could still apply a gate-relaxing override — but that is already covered by the No-Bypass Rule and `/review`/`/ship` gates.

**Out of scope (honest boundaries)**: disabling a gate or changing thresholds (the carve-out forbids relaxing gates — those belong to reclassification / a new ADR, not the override layer); shared-SSoT partitioning for submodule/monorepo adoption.
