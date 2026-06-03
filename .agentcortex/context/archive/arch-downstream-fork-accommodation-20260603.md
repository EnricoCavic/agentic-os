# Work Log — arch-downstream-fork-accommodation

| Field | Value |
|---|---|
| Branch | arch/downstream-fork-accommodation |
| Classification | architecture-change |
| Classified by | Claude Opus 4.8 |
| Frozen | true |
| Created Date | 2026-06-03 |
| Owner | KbWen |
| Guardrails Mode | Full |
| Current Phase | ship |
| Checkpoint SHA | (ship commit on arch/downstream-fork-accommodation) |
| Recommended Skills | verification-before-completion (completion claims), karpathy-principles (design baseline), red-team-adversarial (review/test — arch Full+Beast), test-driven-development (deploy sidecar logic is testable), production-readiness (deploy robustness/error paths) |
| Primary Domain Snapshot | none |

## Session Info
- Agent: Claude Opus 4.8 (1M context)
- Session: 2026-06-03
- Platform: Claude Code
- Guardrails loaded: §1, §2, §4, §7, §8.1, §10 (core), §11 (multi-session)
- Context Read Receipt: current_state.md (Last Updated 2026-06-02, Seq 30) · Work Log (created) · Spec Scope (none — new ADR+spec to be authored)

## Drift Log
- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- ADR Index update: ADR-004 + ADR-005 added (direct write, /adr-phase SSoT write exception per AGENTS.md).
- B-scope DEVIATION (recorded): user directed "sidecar all core"; ADR-005 narrows to "skills→sidecar, framework-authoritative core→force-update" on governance-drift safety grounds (expert-unanimous). ADR proposed (reversible pre-/implement). Surfaced to user → user CONFIRMED narrowing.
- Spec Index update: downstream-fork-accommodation added (Draft→Frozen→Shipped). Direct write per /adr+/ship single-session exception.
- Ship SSoT direct writes (Spec Index status, Ship History entry, Update Sequence 30→31, Last Updated/Verified): direct edit (single-session, no concurrent owner); guard_context_write append would mis-order Ship History (newest-first). Logged per AGENTS.md non-ship-exception discipline.

## Task Description
- Strengthen downstream (fork + clone/deploy) compatibility via four work items, decided with the user after a 2-round multi-expert analysis (16 agents, 48-scenario catalog, external prior-art on Copier/Cookiecutter/git-subtree/Nix/Kustomize):
  - **A** Activate the already-shipped-but-unwired `AGENTS.override.md` personal/per-fork governance layer (lazy-load at session start, present-only). Files: `.agent/workflows/bootstrap.md`, `.agentcortex/docs/guides/doc-governance.md:35-51` (status soft-launch → active), `AGENTS.md:97`.
  - **B** Deploy core-tier sidecar guard — user-modified core files write `.acx-incoming` instead of silent `cp` (fixes R1 silent overwrite). Files: `.agentcortex/bin/deploy.sh:149-153`, `deploy.ps1` (parity). **OPEN RISK**: user chose "extend to all core tier", but rules/workflows are framework-authoritative and must stay force-updatable — extending sidecar to them risks freezing governance/security fixes (governance-drift, worse than R1). Scope MUST be vetted in /adr (likely scope = skills + safe subset; rules/workflows stay force-update).
  - **C** README fork conditional-support stance (additive-fork friendly; never edit framework files in place). Files: `README.md`, `docs/README_zh-TW.md` (parity).
  - **D** Publish framework-owned skill-name set + reserve `custom/*` skill namespace (pure docs). Files: skill registry / `routing.md §3`.
- Full chain (architecture-change): /brainstorm (skip — design already explored via 2 expert workflows, log here) → /adr → /spec → /plan → /implement → /review → /test → /handoff → /ship.

## Phase Sequence
- bootstrap

## External References
- ADR-001 covers AGENTS.md (applies_to match). deploy.sh / doc-governance.md / README.md / bootstrap.md are NOT covered → new ADR required (check_adr_coverage Exit 1 no_covering_adr, 2026-06-03).
- Prior decisions reference: existing `AGENTS.override.md` spec at `.agentcortex/docs/guides/doc-governance.md` §"Override Layer — soft-launch" (precedence chain + "MUST NOT relax gates" carve-out; mirrors Codex AGENTS.override.md convention).
- Existing working extension-seam precedent: `.agentcortex/context/private/user-preferences.yaml` (bootstrap §3.6a, lazy/present-only) — the activation pattern A must mirror (lazy, NOT eager @import).

## Known Risk
- B "all-core" scope can freeze framework-authoritative rules/workflows from receiving updates → governance/security drift. Must be scoped in /adr.
- A must be lazy-load (present-only) per token-governance (§Context Pruning / Read-Once / Brevity); an eager @import would pin a near-empty governance file into every downstream turn's warm-cache prefix. Mirror user-preferences.yaml lazy pattern.
- Cross-platform parity: B touches deploy.sh AND deploy.ps1; C touches README AND zh-TW; A semantics must align across Claude/Codex/Gemini/Antigravity (override convention is Codex-originated).
- Honor-system caution (Global Lesson [enforcement][HIGH]): activating override = a new governance-loading behavior with no validator. Decide enforcement (validator/test) or keep explicitly advisory; do NOT add an unenforceable MUST.
- **Rollback**: revert the ship commit / PR (`git revert <sha>` or close PR). Changes are isolated to the arch branch; ADRs/spec are additive; deploy tier change is a single get_tier reclassification. No data migration, no runtime state. Downstream impact only on next `deploy` (skills sidecar) — reverting restores prior force-update behavior.

## Conflict Resolution
none

## Skill Notes
- red-team-adversarial caution (Global Lesson [audit-method][HIGH] 4faa557a + [audit-verification][HIGH]): same-vendor sub-agent roundtables share blind spots; 2 expert workflows already used — findings (esp. the override-already-exists discovery, R1) were spot-verified against actual files (doc-governance.md:35-51, deploy.sh:149-153). Continue verifying each subagent claim against the real code path before acting.

## Phase Summary
- bootstrap: classified as architecture-change; ADR coverage Exit 1 (no covering ADR for deploy/doc/readme) → /adr required next; 5 skills matched; SSoT (Seq 30) + Work Log loaded.
- adr: ADR-004 (override activation) + ADR-005 (deploy skill-sidecar tiering, B narrowed from user's "all core" w/ user confirmation) written, indexed. /brainstorm skipped — design explored via 3 expert workflows (20+ agents), logged.
- spec: docs/specs/downstream-fork-accommodation.md frozen; 10 AC covering A–D; INDEPENDENT.
- plan: 9 steps, 10 target files; deploy.ps1 delegates to .sh (auto-parity); skills→scaffold reuses sidecar machinery (minimal). | Confidence: 88% — residual is A honor-system enforcement, scoped to structural check.
- implement: A–D done across 10 files + tests/ci/test_deploy_tiering.py (8 tests). Full ci+guard suite 151 passed pre-review.
- review: adversarial workflow (20 agents, 18 findings) — 15 false-alarms killed by claim-verification (same-vendor blind-spot pattern, [audit-verification]). 3 REAL/PARTIAL all LOW, all fixed: (FINDING-004) validate.ps1 message §1a parity; (G-005) added custom-* namespace regression test; (G-006) README EN heading "1a." for zh parity. Verdict PASS — no CRITICAL/HIGH/MEDIUM.
- test: see ## Evidence. validate.sh (CI-aligned) pass=100 fail=2 (pre-existing Windows CRLF: metadata-deep + compact-index; CI green). validate.ps1 witness parity follow-up investigated: CRLF hypothesis DISPROVEN (lines byte-identical in PS5.1 + pwsh7); real cause is environmental/stateful (validate.ps1 mutating `git fetch` + local-ahead-of-remote), NOT a code bug → no patch applied (evidence-before-adding); spawned task left open for separate read-only-witness hardening.
- handoff: doc path docs/specs/downstream-fork-accommodation.md (+ ADR-004/005) · code path 10 files + tests/ci/test_deploy_tiering.py · worklog .agentcortex/context/work/arch-downstream-fork-accommodation.md. HANDEDOFF.
- ship: Verdict PASS; ADRs accepted, spec shipped; SSoT Ship History + Update Sequence bumped; Domain L2 consolidated; PR opened (see chat). Codex final double-check pending per user.

⚡ ACX

## Handoff
- Doc: docs/specs/downstream-fork-accommodation.md · docs/adr/ADR-004-override-layer-activation.md · docs/adr/ADR-005-downstream-file-preservation-tiering.md
- Code: .agentcortex/bin/deploy.sh · .agent/workflows/bootstrap.md · .agentcortex/docs/guides/doc-governance.md · AGENTS.md · .agent/workflows/routing.md · README.md · docs/README_zh-TW.md · .agentcortex/bin/validate.sh · .agentcortex/bin/validate.ps1 · tests/ci/test_deploy_tiering.py
- Work Log: .agentcortex/context/work/arch-downstream-fork-accommodation.md
- Resumable state: complete through ship; awaiting Codex review on PR.

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-03
- Gate: plan | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-03
- Gate: implement | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-03
- Gate: review | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-03
- Gate: test | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-03
- Gate: handoff | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-03
- Gate: ship | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-03

## Risks
- Wrong B scope (sidecar leaking to rules/workflows) → invisible governance drift. Mitigation: skills-only sidecar; validate test AC-5 asserts framework-authoritative core gets NO sidecar.
- A override-load is an agent instruction (honor-system). Mitigation: structural validate check (AC-8) that bootstrap.md ships the step; carve-out is warn-only (honest per [enforcement][HIGH]).
- Cross-platform parity: deploy.ps1 delegates to deploy.sh (auto-parity, verify delegation); README↔zh-TW + validate.sh↔ps1 must mirror.
- Windows EOL ([cross-platform-eol]): use Edit tool / LF-safe for any validate content-compare or tracked-file append.

## Evidence
- Implemented A–D across 10 files (deploy.sh get_tier skills→scaffold; bootstrap.md §1a override-load + Session Info Override field; doc-governance.md soft-launch→active + Implementation Contract; AGENTS.md override pointer; routing.md §3a framework skill set + custom-* reservation; README + zh-TW "Customizing Without Conflicts"; validate.sh + validate.ps1 structural override-step check).
- New tests: tests/ci/test_deploy_tiering.py — **7 tests**. Behavioral `test_skill_edit_sidecars_and_core_rule_force_updates` PASSED (AC-5: core rule force-updates, NO sidecar; AC-6: edited framework skill → .acx-incoming preserved + custom-* untouched). 6 structural tests PASSED (skills→scaffold, override step in bootstrap+both validators, doc-gov active, custom-* namespace, README↔zh-TW parity).
- validate.sh: pass=100 warn=8 fail=2. The 2 FAILs (`metadata deep validation`, `compact index freshness`) are the documented Windows-local CRLF artifact (compact-index content_hash over CRLF checkout ≠ committed LF hash) — CI=green; my diff touches NO SKILL.md / trigger-compact-index.json / trigger-registry.yaml (git status verified). `document-governance spec contract` FAIL was mine (numbered `## 6. Domain Decisions` heading) → fixed to literal `## Domain Decisions` → now PASS.
- Parity: deploy.ps1 delegates to deploy.sh (B auto-parity); validate.sh↔ps1 both gained the override-step check; README↔zh-TW mirrored.
- FINAL: full ci+guard suite **152 passed** (0 fail) incl. behavioral deploy test + custom-* namespace regression guard. Review PASS (3 LOW fixed).
- POST-SHIP CI FIX (commit edef328): PR #175 CI initially RED on `metadata deep validation` + `compact index freshness`. Root cause: AGENTS.md is a `detail_ref` in trigger-registry → the override-pointer edit shifted its CR-normalized content_hash → committed `trigger-compact-index.json` genuinely stale on CI. This was MASKED locally by the Windows CRLF-on-disk artifact (so my earlier "fail=2 = pre-existing CRLF, CI green" claim was WRONG — corrected). Regenerated the index → `validate.sh` pass=101 **fail=0**; **all PR #175 CI checks green** (Framework Validation Linux+Windows+Py3.9, SAST, secrets, shellcheck, smoke). Lesson: a `detail_ref` content edit (esp. AGENTS.md) requires regenerating the compact index; the local CRLF artifact can mask real staleness — trust CI (LF), not local Windows verdicts.
