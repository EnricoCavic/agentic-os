# Work Log: ci-issue-163-remainder

## Header

- Branch: `ci/issue-163-remainder`
- Classification: `quick-win`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Quick`
- Current Phase: `implement`
- Checkpoint SHA: `d51d288`
- Recommended Skills: `verification-before-completion (auto)`
- Primary Domain Snapshot: `none`
- SSoT Sequence: `46`

---

## Session Info

- Agent: Claude (Fable 5)
- Session: 2026-06-10
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win — bootstrap.md embedded rules)
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO

---

## Task Description

- Backlog #57 / issue #163 remainder (core slice shipped earlier as PR #177). Issue comment lists 3 deferred items; each premise was verified before acting (evidence-before-adding):
  1. CI-gate `.agentcortex/tests` on Linux + Windows — REAL: those 177 tests are not CI-gated at all; local Windows run = 177 passed in 304s (the "Windows behavior unproven" concern is disproven).
  2. `verify_agent_evidence.py` on PRs — **VACUOUS, dropped**: the tool only inspects `.agentcortex/context/review/` mirrors, a mechanism this repo deliberately removed 2026-05-22 (no producer). Probed on two real merge ranges (991ec8c..d51d288, c66b254..991ec8c): both → "No changed reviewable Work Logs found", exit 0. Wiring it = always-skip theatre (Lesson [enforcement]). Noted on the issue at close.
  3. UTF-8 file-validity sweep + critical-file presence pre-check — REAL: cp1252/encoding failures are a recurring class here (validator encoding canaries exist for this reason); cheap tracked-file decode sweep.

## Plan

- `.github/workflows/validate.yml`: (a) structural job pytest now includes `.agentcortex/tests/`; (b) new `test-windows` job (windows-latest, pinned reqs + pip cache, full pytest set); (c) new `utf8-and-critical-files` job (tracked .md/.sh/.yml/.yaml UTF-8 decode + 7 critical-file presence).
- `tests/ci/test_ci_hardening.py`: +3 regression guards locking the new wiring.
- Risk: Windows CI duration (~local 14 min worst case; GH runners faster). Rollback = revert PR.
- Confidence: 90% — premises verified by direct local runs.

## Phase Sequence

- bootstrap
- plan
- implement

## External References

- Issue #163 (core slice: PR #177); backlog #57
- Probe evidence for dropped item 2: verify_agent_evidence exit 0 + skip warning on both probed SHA ranges

## Known Risk

- Windows pytest job adds wall-clock to PR CI; accepted per owner's explicit issue ask ("real pytest run on Windows as well as Linux"). Rollback: revert PR.

## Conflict Resolution

none

## Skill Notes

none

## Phase Summary

- bootstrap: quick-win; 3 remainder premises verified — 2 real, 1 vacuous (dropped with evidence). ⚡ ACX
- implement: validate.yml +2 jobs +1 extension; +3 regression guards. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T06:40:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T06:45:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T07:00:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T07:10:00+08:00

## Evidence

- `python -m pytest tests/ci/test_ci_hardening.py -q` → 7 passed (3 new regression guards).
- Local UTF-8 sweep simulation: 225 tracked files clean, 7/7 critical files present, exit 0.
- Local Windows legacy-suite run: `python -m pytest .agentcortex/tests -q` → 177 passed in 304s (premise proof for CI gating).
- Vacuity probe for dropped item: `verify_agent_evidence.py --base-sha/--head-sha` on 991ec8c..d51d288 and c66b254..991ec8c → both "No changed reviewable Work Logs found", exit 0.
- Before/after: CI previously ran zero `.agentcortex/tests` and zero pytest on Windows; after this PR both gates exist + an encoding sweep. PR CI (incl. the new Windows job) = final verification.
- Implementation commit: 91e85b7.

## Phase Summary (ship)

- ship: SSoT Seq 47 + Ship History + backlog #57 Shipped→archive (18 active); worklog archived; PR merge on green CI closes #163. ⚡ ACX
