# Work Log: chore-pytest-slow-markers

## Header

- Branch: `chore/pytest-slow-markers`
- Classification: `quick-win`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `5f9871e`
- Recommended Skills: `verification-before-completion (auto)`
- Primary Domain Snapshot: `none`
- SSoT Sequence: `50`

---

## Session Info

- Agent: Claude (Fable 5)
- Session: 2026-06-10
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win)
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO

---

## Task Description

- E2 of the strict self-assessment queue. Attribution review (per new owner directive) ran BEFORE modification and verified: no prior decision against pytest config (no pytest.ini ever existed in git history); the latency is a DELIBERATE fidelity choice (subprocess tests exercise real deploy/validate scripts and have caught real cross-platform bugs) — so the fix is annotate-only, never default-deselect; markers conflict with no existing convention (path-based selection remains primary); a markers-only pytest.ini at repo root is collection-neutral (rootdir already resolves there; zero conftest.py; CI invokes explicit paths with no -m filter → CI keeps running the full set, byte-identical).

## Plan

- pytest.ini (markers registration ONLY, no addopts/testpaths) + `slow` marks: module-level on test_deploy_tiering.py (18), test_signal_tier_check.py (2), test_ssot_completeness.py (8 — found during verification: ~40s/test validate spawns, missed by the original E2 estimate); per-test on 6 validator-spawning tests in test_validator_false_positives.py. CONTRIBUTING §Running the Test Suite.
- Rollback: revert PR. Confidence: 95%.

## Phase Sequence

- bootstrap
- plan
- implement
- ship

## External References

- E2 expert analysis + attribution review (2026-06-10). CI workflows verified unchanged-by-design (validate.yml explicit-path invocations, no -m).

## Known Risk

- none material. The marker is opt-out only; CI selection unchanged (collect-only proof: full=460 with and without the ini).

## Conflict Resolution

none

## Skill Notes

none

## Phase Summary

- bootstrap/plan: attribution review PROCEED verdict (no past decision contradicted; fidelity intent preserved by annotate-only design). ⚡ ACX
- implement: 34 tests marked across 4 files; one placement defect (mark inserted between decorator and class) caught by collect-only and fixed; CONTRIBUTING numbers corrected after measurement (predicted ~26/~3min → measured 34 marked, 3:20). ⚡ ACX
- ship: full collection 460 unchanged; fast loop 426 passed in 3:20 (was 17 min); CI selection untouched. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T23:30:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T23:32:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T00:05:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T00:15:00+08:00

## Evidence

- `pytest --collect-only`: 460 collected with ini == 460 without (collection-neutral); `-m "not slow"` → 426/460 (34 deselected).
- Fast loop measured: **426 passed, 34 deselected in 200.60s (3:20)** — was ~17 min full.
- Slow-set discovery beyond original estimate: test_ssot_completeness.py top durations 47.2/44.8/38.7s per test (validate.sh spawn each) — found by measuring, not assuming.
- CI invariance: validate.yml runs explicit paths with no -m filter → full 460 on Linux + Windows unchanged.
