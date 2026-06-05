# Work Log — fix/tiny-fix-exclusion-adapter-parity

- **Branch**: fix/tiny-fix-exclusion-adapter-parity
- **Classification**: quick-win (governance-file edit; semantic)
- **Owner**: KbWen (Claude Opus 4.8 session)
- **Current Phase**: SHIPPED
- **Checkpoint SHA**: 160566b (implementation commit)
- **Recommended Skills**: none

## Session Info
- 2026-06-05 — Add platform adapter entry files (CLAUDE.md, GEMINI.md) to the tiny-fix exclusion list across all 4 mirrored sites + test token array, closing the parity gap that let PR #195 ship a semantic governance edit via the silent tiny-fix path.

## Problem / Root Cause
PR #195 (`fc54c34`) edited `CLAUDE.md` + `GEMINI.md` startup lines — a semantic governance change — but took the silent tiny-fix path with no Work Log / gate evidence. **Root Cause**: the tiny-fix exclusion list named `AGENTS.md` and other governance files but NOT the platform adapter entry files `CLAUDE.md` / `GEMINI.md`, which `@import AGENTS.md` and carry governance dispatch. The tiny-fix path therefore looked legitimately available for adapter edits.

## Scope Decision (Plan-consulted)
Add exactly `CLAUDE.md` + `GEMINI.md`. Rejected an `*.override.md` glob as speculative: no per-adapter override files exist, the override loader (bootstrap §1a) only reads `AGENTS.override.md`, and ADR-004 overrides "MUST NOT relax gates" — so an override cannot reopen the tiny-fix path. No `CODEX.md` adapter exists (AGENTS.md is the Codex/shared file, already listed). Adapter-entry class today = closed set of {CLAUDE.md, GEMINI.md}.

## Changes (5 files, list/wording only — no logic)
1. `.agent/rules/engineering_guardrails.md` §10.3 — new exclusion bullet for CLAUDE.md/GEMINI.md.
2. `AGENTS.md` Runtime v1 rule 2 — appended `CLAUDE.md`, `GEMINI.md` to ADDITIONAL TINY-FIX EXCLUSIONS clause (before the §10.3 ref so the drift-guard regex captures them).
3. `.agent/workflows/routing.md` §4 rule 3 — appended adapter entry files to escalation enumeration.
4. `.agent/workflows/bootstrap.md` §0 — extended the existing `AGENTS.md` row to include CLAUDE.md/GEMINI.md.
5. `tests/guard/test_classification_escalation.py` — (a) added `CLAUDE.md`, `GEMINI.md` tokens to `GOVERNANCE_EXCLUSION_TOKENS` (makes sites 1+2 self-enforcing); (b) added two new drift guards `test_routing_escalation_rule_matches_guardrails` + `test_bootstrap_fastcheck_table_matches_guardrails` so ALL 4 mirror sites are now test-backed (closes the gap noted in Known Risk).
   - Index regen: `.agentcortex/metadata/trigger-compact-index.json` (AGENTS.md is a registry `detail_ref`).

## Drift Log
- none

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-05T13:00:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-05T13:05:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-05T13:15:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-05T13:18:00+08:00

## Evidence
- Contract test: `python -m pytest tests/guard/test_classification_escalation.py -q` → 10 passed (8 original + 2 new site-3/site-4 guards). All 4 mirror sites now require the full `GOVERNANCE_EXCLUSION_TOKENS` set incl. `CLAUDE.md`/`GEMINI.md`.
- Full guard suite: `python -m pytest tests/guard/ -q` → 132 passed.
- New-guard scoping verified: bootstrap-table regex captures exactly the 9-line `| IF the task` table (stops at section boundary); negative control confirms an absent token (`FAKE.md`) is NOT matched → guard is non-vacuous.
- Side-effect caught + fixed: editing `AGENTS.md` (a registry `detail_ref`, trigger-registry.yaml:36) staled `.agentcortex/metadata/trigger-compact-index.json`. Regenerated via `generate_compact_index.py`; `--check` → fresh. Diff = 1 line (AGENTS.md content_hash 1da5e965→a0433316).
- Validator (PowerShell): `pass=98 warn=9 fail=0 skip=2` (baseline was identical; 0 new fails).
- Validator (bash) parity: `pass=98 warn=9 fail=0 skip=2` — cross-platform consistent.
- Baseline comparison: clean `main` = `fail=0`; mid-change = `fail=2` (both index-staleness); post-regen = `fail=0`.

## Known Risk
- RESOLVED (same branch, per user request): sites 3 (routing.md) + 4 (bootstrap.md) now have test backstops. All 4 mirror sites are drift-guarded against the same token set. No remaining known risk for this change.

## Phase Summary
- **bootstrap/plan**: classified quick-win (governance-file edit is semantic → not tiny-fix, which is precisely the gap being fixed). Mapped the exclusion list to 4 mirrored doc sites + 1 test contract via an Explore agent; consulted a Plan agent on scope, which confirmed adapters-only (no speculative `*.override.md` glob).
- **implement**: added `CLAUDE.md`/`GEMINI.md` to all 4 mirror sites and the test token array; extended the drift guard with two new tests so routing.md + bootstrap.md are also backed. Caught a real side-effect — editing `AGENTS.md` (a registry `detail_ref`) staled the trigger compact index — and regenerated it.
- **test**: escalation test 10/10, full guard suite 132/132; both PowerShell + bash validators `fail=0` at parity; negative-control proved the new guards are non-vacuous.
- **ship**: implementation commit `160566b`; Ship History + SSoT heartbeat (seq 34→35) written via `guard_context_write.py`; Work Log archived; INDEX.jsonl chained. Rollback = revert PR.

⚡ ACX
