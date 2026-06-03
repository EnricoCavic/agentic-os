---
status: shipped
source: internal
classification: architecture-change
primary_domain: document-governance
secondary_domains: [deploy, skills]
adr: [ADR-004, ADR-005]
created: 2026-06-03
---

# Spec: Downstream Fork/Clone Accommodation

Strengthen downstream compatibility for both distribution paths (fork + `git pull
upstream`, and clone + `deploy_brain.sh`) so that downstream users can keep their
own skills and governance customizations across framework upgrades **without
editing framework-owned files in place**. Implements ADR-004 (override layer
activation) and ADR-005 (downstream file-preservation tiering), plus the README
fork stance (C) and `custom/*` namespace publication (D).

## 1. Goal

A downstream user (forker or clone-deployer) has a documented, runtime-wired,
token-safe place to put governance overrides and custom skills that survives
both `git pull upstream` (fork) and `deploy_brain.sh` (clone) — with framework
governance/security files always staying current.

## 2. Acceptance Criteria

- **AC-1 (A, override load)**: When `AGENTS.override.md` exists at project root and/or `~/.agentcortex/AGENTS.override.md`, `bootstrap.md` loads them at session start (after SSoT read, before Work Log setup) in precedence order, and records the loaded filename(s) + source in the Work Log `## Session Info`.
- **AC-2 (A, present-only)**: When no override file exists, bootstrap performs zero extra reads, zero writes, no error; `## Session Info` records `Override: none`. (Capability-by-presence, mirroring `§3.6a`.)
- **AC-3 (A, carve-out warn)**: An override directive citing `> Overrides: AGENTS.md §Delivery Gates` (or `§Core Directives`/No-Bypass Rule) causes bootstrap to emit a WARN, record `rejected` in `## Drift Log`, and NOT apply that directive; other (narrowing) directives in the same file still apply. Bootstrap does not hard-block.
- **AC-4 (A, doc status)**: `doc-governance.md` §49 reads "**MUST** read … when present" (was "SHOULD"); §51 `Status` reads `active` (was `soft-launch`) with an Implementation Contract subsection pointing at the bootstrap load step; the §47 carve-out text is unchanged.
- **AC-5 (B, force-update)**: After a local edit to any framework-authoritative file (`.agent/rules/*`, `.agent/workflows/*`, `.agent/config.yaml`, `.agentcortex/bin/validate.*`, `.agentcortex/bin/deploy.*`, `.antigravity/rules.md`, `codex/rules/*`, `.agentcortex/tools/**`, `.agentcortex/metadata/**`), a re-deploy overwrites it and produces **no** `.acx-incoming`.
- **AC-6 (B+D, skill sidecar)**: After a local edit to any framework-shipped skill under `.agent/skills/**` or `.agents/skills/**`, a re-deploy produces a `.acx-incoming`, leaves the original file unchanged, increments `COUNT_SKIPPED`, and the SKIP message offers manual/AI merge. Net-new `custom-*` skills are never touched by deploy.
- **AC-7 (parity)**: `deploy.ps1` exhibits AC-5 + AC-6 behavior identically to `deploy.sh` (verified by running the relevant entry point, per Global Lesson `[cross-platform-cli]` — not by reading). `validate.sh` and `validate.ps1` both gain the same new structural check(s) if any are added.
- **AC-8 (A enforcement, structural)**: `validate.sh` and `validate.ps1` each assert that `bootstrap.md` contains the override-load step (structural presence check — the framework ships the instruction). No fake per-agent MUST is added.
- **AC-9 (C, README)**: `README.md` gains an "Additive Fork" section (override layer + skill sidecar + `custom-*` namespace + "never edit framework files in place; copy-then-customize"); `docs/README_zh-TW.md` mirrors it with equivalent 繁體中文 content.
- **AC-10 (D, namespace)**: `routing.md` (or the skill registry) publishes the framework-owned skill-name set and documents the reserved `custom-*` prefix (framework never ships a `custom-*` skill).

## 3. Non-goals

- NOT building fork merge tooling, `--merge-strategy`, rollback, or sidecar-merge automation (no verified consumer; DELETE-bias).
- NOT enabling overrides to disable/relax Delivery Gates or change classification thresholds (ADR-004 carve-out forbids it; those belong to reclassification or a separate ADR).
- NOT solving shared-SSoT/Work-Log partitioning for submodule/monorepo adoption.
- NOT adding manifest schema-versioning or tier-history.
- NOT adding a skill-name validator (deferred; no verified consumer of a bad skill name yet).

## 4. Constraints

- Cross-platform parity is mandatory: `deploy.sh`↔`deploy.ps1`, `README.md`↔`docs/README_zh-TW.md`, `validate.sh`↔`validate.ps1`; override semantics align across Claude/Codex/Gemini/Antigravity (override convention is Codex-originated; `.antigravity/rules.md` is orthogonal platform hardening, not a conflict).
- Every new MUST must have a validator/test/hook or be honestly labeled advisory (Global Lesson `[enforcement][HIGH]`).
- Tier reclassification must reuse the existing scaffold sidecar machinery — no new deploy code path (DELETE-bias).
- Override load must be lazy/present-only — no eager `@import` (token governance: `§Context Pruning`/`§Read-Once`/`§Response Brevity`).
- Windows EOL discipline for any validator content-compare or shell append (Global Lesson `[cross-platform-eol]`).

## 5. File Relationship

INDEPENDENT — new spec. No existing `docs/specs/*.md` covers downstream fork/clone accommodation, override activation, or deploy tiering.

## Domain Decisions

- [DECISION] Activate the **already-shipped-but-inert** `AGENTS.override.md` layer (lazy, present-only) rather than invent a new `AGENTS.local.md` eager-`@import` twin — avoids one-topic-two-files and warm-cache prefix bloat. (ADR-004)
- [DECISION] Reclassify skills (`.agent/skills/**`, `.agents/skills/**`) to the sidecar class while keeping rules/workflows/validate/deploy/platform/tools/metadata as force-update — skills are advisory (non-gate), so a frozen skill is a visible, low-cost loss; a frozen workflow/rule is invisible governance drift. (ADR-005)
- [TRADEOFF] Narrowed the user's literal "sidecar all core" to "skills only" — accepts that editing a framework skill freezes it (visible via sidecar) in exchange for guaranteeing governance/security files always update. Worse-than-R1 invisible drift is the avoided failure. (ADR-005, flagged for user confirmation)
- [DECISION] Override carve-out (no gate relaxation) and citation requirement are **warn-only advisory**, not hard-block — a pure-text override cannot be machine-proven to "relax vs legitimately narrow" a gate; only the machine-verifiable deploy behaviors become hard-tested MUSTs. (ADR-004, Lesson [enforcement])
- [CONSTRAINT] The framework MUST NEVER ship a skill under the `custom-*` prefix — it is a reserved downstream namespace contract. (ADR-005)
- [CONSTRAINT] Downstream users MUST NOT edit framework-authoritative files in place; customize via `AGENTS.override.md` (governance) or `custom-*` skills (capabilities). Framework skill edits are tolerated (sidecar-protected) but discouraged. (ADR-004/005, README)

## 7. Test Plan (seeds)

- `tests/deploy/test_core_authoritative_no_sidecar.*` — AC-5.
- `tests/deploy/test_skill_sidecar.*` — AC-6 (framework skill sidecar + `custom-*` untouched).
- `tests/bootstrap/test_override_load.*` — AC-1/AC-2/AC-3 (present→recorded; absent→none; gate-relax→warn+rejected).
- `validate.sh`/`validate.ps1` structural check — AC-8.
- Parity: run each `deploy.ps1` path for AC-5/AC-6 (AC-7), not read-only inspection.
