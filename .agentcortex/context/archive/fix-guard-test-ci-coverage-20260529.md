| Field | Value |
|---|---|
| Branch | fix/guard-test-ci-coverage |
| Classification | quick-win |
| Classified by | Claude Opus 4.8 (1M) |
| Frozen | true |
| Created Date | 2026-05-29 |
| Owner | luvseldom (session 2026-05-29) |
| Guardrails Mode | Quick |
| Current Phase | ship |
| Checkpoint SHA | 0b44bf1504af85432e7606444f2d73b6b7aa1ff2 |
| Recommended Skills | verification-before-completion (completion claims), karpathy-principles (coding baseline), systematic-debugging (if test errors arise) |
| Primary Domain Snapshot | none |

## Session Info
- Agent: Claude Opus 4.8 (1M context)
- Session: 2026-05-29
- Platform: Antigravity
- Guardrails loaded: skipped (quick-win) — AGENTS.md §Core Directives only
- Context Read Receipt: current_state.md (Update Seq 21, Last Verified 2026-05-26) · Work Log (created) · Spec Scope (none — both indexed specs are [Shipped], not design authority)

## Drift Log
- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- SSoT write procedure deviation: ship.md §State Update step 2 prescribes guard `append` mode (entry at file bottom). Used guard `replace` mode (CAS, expected-sha) to INSERT the Ship History entry at the TOP of the section instead — the existing ## Ship History is strictly newest-first, so append-to-bottom would have placed the newest entry in the oldest position. Same guard tool, same atomicity; ordering correctness preserved. new_sha 945bff8c.
- Bad commit message (first attempt): used PowerShell here-string `@'...'@` in bash shell → literal `@` leaked into subject; also the failed `git add` of already-staged deletions aborted staging of validate.yml + work log. Fixed via `git commit --amend -F <msgfile>` after re-staging. Lesson candidate (process): match here-string syntax to the actual shell (Bash tool ≠ PowerShell).

## Task Description
- Fix framework self-test integrity (audit item A+B, 2026-05-29). Two faults found and verified:
  - **A**: `tests/guard/test_sentinel_hook.py` and `tests/guard/test_precompact_hook.py` `exec_module()` the deleted hook sources `.claude/hooks/check-sentinel.py` / `check-precompact.py` (removed intentionally in commit `aec35d6`, zero-python-downstream design per `.claude/settings.json` `_governance_ref`). They raise `FileNotFoundError` at pytest **collection** time → aborts the ENTIRE `tests/guard/` collection → all 82 valid tests for shipped governance tools never run.
  - **B**: CI (`.github/workflows/validate.yml:161`) runs only `pytest tests/ci/`, never `tests/guard/`. The 82 tests covering `guard_context_write`, audit-chain, lint, lifecycle, ADR-coverage are ungated.
- Fix: delete the 2 orphaned test files (feature intentionally removed; matches documented zero-dep decision) + add a `tests/guard/` pytest step to CI.
- Verified pre-fix: `pytest tests/guard/ --ignore=<2 orphans>` → 82 passed; `pytest tests/guard/` → 2 collection errors, Interrupted.
- Phase chain: /plan → /implement → /review → /test → /ship (quick-win; handoff exempt)

## Phase Sequence
- bootstrap

## External References
none

## Known Risk
- Deleting test files could be seen as reducing coverage. Mitigation: the deleted tests target a feature (Python Stop/PreCompact hooks) that was deliberately removed for zero-runtime-dep downstream; settings.json documents the decision. Net coverage INCREASES (82 previously-unreachable tests become CI-gated).
- Wiring tests/guard into CI may surface latent tool bugs (audit found C1/C2/C3 candidates not covered by the 82 tests). Confirmed current 82 pass, so CI stays green; deeper bugs are separate work items.

## Conflict Resolution
none

## Skill Notes
none

## Risks
- R1 (coverage perception): deleting 2 test files looks like coverage loss. Mitigation: they target the deliberately-removed Python hook feature (zero-dep design, documented in `.claude/settings.json`); net coverage rises (82 tests become CI-gated).
- R2 (latent tool bugs surfaced in CI): wiring tests/guard may expose tool bugs. Mitigation: confirmed 82 pass now → CI stays green; deeper audit findings (C1/C2/C3) are separate items.
- R3 (CI job runtime): adds ~2s pytest. Negligible.
- Rollback: `git revert` the single commit; CI returns to prior tests/ci-only scope, test files restored from history.

## Phase Summary
- bootstrap: classified as quick-win; skills matched (verification-before-completion, karpathy-principles); SSoT + Work Log loaded; spec scope none.
- plan: 3 target files (2 deletes + 1 CI edit); extend test-ci-structural job to `pytest tests/ci/ tests/guard/`; Mode Normal | Confidence: 95% — high (pre-verified 82 pass)
- implement: deleted 2 orphaned test files (355 lines) + stale .pyc; CI step → `pytest tests/ci/ tests/guard/ -v`; scope matched plan exactly (3 files, 0 divergence); `pytest tests/ci/ tests/guard/` → 114 passed, 0 collection errors. Confidence: 95% — high
- ship: PASS; commit 8001ef5; SSoT Ship History + Update Seq 22 (guard replace CAS, new_sha 945bff8c); backlog #41 Shipped + #42-#44 queued; archived to archive/fix-guard-test-ci-coverage-20260529.md

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-05-29
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-05-29
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-05-29
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-05-29

## Evidence
- Pre-fix (reproduction): `pytest tests/guard/` → 2 errors during collection (FileNotFoundError on .claude/hooks/check-sentinel.py & check-precompact.py), Interrupted → 0 tests run.
- Pre-fix (isolated): `pytest tests/guard/ --ignore=<2 orphans>` → 82 passed.
- Post-fix: `pytest tests/ci/ tests/guard/ -q` → 114 passed in 1.00s, 0 collection errors (= exact CI command).
- Scope: `git diff --stat` → 3 files (test_precompact_hook.py -157, test_sentinel_hook.py -198, validate.yml +2/-2). Matches plan Target Files.
- Files deleted match documented zero-dep decision in `.claude/settings.json` `_governance_ref`.
