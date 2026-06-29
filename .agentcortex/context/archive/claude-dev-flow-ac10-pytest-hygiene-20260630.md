# Work Log: claude/dev-flow-ac10-pytest-hygiene

## Header

- Branch: `claude/dev-flow-ac10-pytest-hygiene`
- Classification: `quick-win`
- Classified by: `Claude (Opus 4.8)`
- Frozen: `2026-06-30`
- Created Date: `2026-06-30`
- Owner: `claude-session`
- Guardrails Mode: `Full`
- Current Phase: `ship`
- Diff Base SHA: `b1beaa2`
- Checkpoint SHA: `bf71296`
- Recommended Skills: `verification-before-completion`
- Primary Domain Snapshot: `developer-experience`
- SSoT Sequence: `99`

---

## Session Info

- Agent: `Claude (Opus 4.8)`
- Session: `2026-06-30 ac10`
- Platform: `claude`
- Continuation of: dev-flow-hardening (Batch 1 #299, Batch 2 #300, AC-13 #301, CI/security #302 shipped). This branch = AC-10, the LAST remaining acceptance criterion (Batch 4 dev-command hygiene; AC-11 already shipped in Batch 1).

---

## Task Description

Implement AC-10 of `docs/specs/dev-flow-hardening.md` — the default/documented pytest command must be safe: a naive `pytest` from repo root must not break on collecting ignored/demo/secret-requiring files. Classified quick-win (small, mechanical, no gate-semantics change).

---

## Plan (per Plan-expert design)

Root cause (confirmed live earlier): a bare `pytest --collect-only` from repo root **errors** because the tracked `cache_test.py` (a prompt-caching DEMO script) matches pytest's `*_test.py` collection pattern and does `anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])` at import → `KeyError` → "Interrupted: 1 error during collection" → whole run dies before any test executes. `pytest.ini` has no `testpaths`/`norecursedirs`/`collect_ignore` (deliberate — CI uses explicit paths).

1. **Rename `cache_test.py` → `cache_demo.py`** (it is a demo, not a test — the honest fix; removes the `*_test.py` collection match). GREP for all references first (`grep -rn "cache_test"`) and update any.
2. **`pytest.ini`: add `norecursedirs`** to prune non-test recursion: `temp_downstream* scratch demo codex installers __pycache__ .pytest_cache .git .acx-local`. Recursion-pruning only — do NOT add `testpaths`/`addopts` that would narrow what CI collects (the `pytest.ini` no-testpaths stance is a load-bearing, attribution-reviewed decision — preserve it).
3. **Document the canonical command** in `README.md` (or CONTRIBUTING if present): the intended local invocation is `pytest tests/ci/ tests/guard/ .agentcortex/tests/ -m "not slow"` (mirrors the CI Structural command). Keep it terse.
4. **Lock test** (optional, low-cost) in `tests/ci/test_ci_hardening.py`: assert `pytest.ini` contains `norecursedirs` with the temp/scratch entries AND that no tracked root-level `*_test.py` demo collides (i.e. `cache_test.py` is gone) — so the breakage cannot regress.

**Verification**: `python -m pytest --collect-only -q` from root MUST exit 0 with NO collection error (the demonstration this AC exists for). Full CI-equivalent not-slow set still green. `pytest tests/ci/ tests/guard/ .agentcortex/tests/ -m "not slow"` exercises the intended surface. Token aggregate ≤ 355,000 (expect ~0 delta — pytest.ini/README/demo not AI-loaded scenario docs). `generate_compact_index.py --check` fresh.

**Quick-win gate note**: quick-win Work Log still needs bootstrap+plan+implement+ship receipts + a real `## Phase Summary`, else validate FAILs. Skips TESTED→HANDEDOFF (quick-win path: TESTED→SHIPPED).

Constraints: only /ship writes SSoT; rename via `git mv` (preserve history); English; small/reversible. Test discipline: run WHOLE affected files, not -k slices.

---

## Drift Log

- Continuation; off main b1beaa2 (post CI/security #302 merge, which already bumped pytest→9.0.3). ADR Coverage: no new ADR; dev-command ergonomics.

---

## Evidence

- BEFORE: `python -m pytest --collect-only -q` → "Interrupted: 1 error during collection" (KeyError: ANTHROPIC_API_KEY from cache_test.py line 9)
- AFTER: `python -m pytest --collect-only -q` → 628 tests collected, exit 0, no errors
- cache_test.py renamed to cache_demo.py (untracked/gitignored); .gitignore updated
- pytest.ini: norecursedirs added (temp_downstream*, scratch, demo, codex, installers, __pycache__, .pytest_cache, .git, .acx-local)
- README.md: "Running the tests" section added with canonical command
- tests/ci/test_ci_hardening.py: 2 AC-10 lock tests added (11 passed total)

## Test Gate Results

- `python -m pytest tests/ci/test_ci_hardening.py -v`: 11/11 PASSED
- `python -m pytest tests/ci/ tests/guard/ .agentcortex/tests/ -m "not slow" -q`: 564 passed, 64 deselected, 0 failed
- Token aggregate: test_aggregate_current_total_stays_under_350k PASSED
- compact index: `generate_compact_index.py --check` → "compact index is fresh"
- Commits: 199fcd7 / 3e3dc0d / bf71296

## Phase Summary

quick-win AC-10: renamed cache_test.py → cache_demo.py, added pytest.ini norecursedirs, documented canonical test command in README, added regression lock tests. Bare `pytest --collect-only` now exits 0 (was broken with KeyError). All 564 not-slow tests green.
- ship: PASS | PR #303 merged d8fa426 | archive: .agentcortex/context/archive/claude-dev-flow-ac10-pytest-hygiene-20260630.md

---

## Resume

State: AC-10 branch off b1beaa2; plan locked; implement dispatched.
Next: rename cache_test.py→cache_demo.py (grep refs first); pytest.ini norecursedirs; README canonical command; lock test; verify bare `pytest --collect-only` exits 0; ship.
Context: This is the LAST AC. After ship, dev-flow-hardening spec can move toward settled (all 13 ACs done) — but spec status change is a separate decision; leave draft unless instructed.

### Read Map
- `docs/specs/dev-flow-hardening.md`, `pytest.ini`, `cache_test.py`, `README.md`, `tests/ci/test_ci_hardening.py`

### Skip List
- `.agentcortex/context/.guard_receipt.json`, `.guard_receipts/*`, archive/*, `.acx-local/*`, `temp_downstream*/*`

### Context Snapshot
Resume from main b1beaa2. cache_test.py is the collection-breaker (tracked demo needing ANTHROPIC_API_KEY at import).

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-30T00:00:00Z
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-30T00:00:00Z
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-30T00:00:00Z
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-30T00:00:00Z
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-30T20:00:00Z

---

## Design Reference

none
