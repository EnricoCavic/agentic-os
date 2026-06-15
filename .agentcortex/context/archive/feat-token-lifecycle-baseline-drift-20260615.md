# Work Log — feat/token-lifecycle-baseline-drift

- Branch: feat/token-lifecycle-baseline-drift
- Classification: quick-win
- Owner: KbWen
- Current Phase: REVIEW PASS → SHIP
- Checkpoint SHA: f0be123
- Worklog Key: feat-token-lifecycle-baseline-drift
- Created: 2026-06-13
- GH Issue: #157 (backlog #51)

## Session Info
- Session 1 (2026-06-13): bootstrap → plan → implement. Single owner, single session.
- Scope: token lifecycle baseline + drift detector wrapped around the EXISTING
  `analyze_token_lifecycle.py`. Additive tooling + tests + advisory validator wiring.

## Recommended Skills
- none auto-attached (quick-win). /review + /test to run before ship.

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13

## Drift Log
- Local-only artifact: `validate.sh`/`validate.ps1` report fail=1 "active work log
  count 13 > 12". Work logs are gitignored (only `.gitkeep.md` tracked; verified via
  `git ls-files` + `git check-ignore`), so a CI checkout has 0 active logs -> CI sees
  fail=0. Not a committed regression; pre-existing local cruft from prior sessions.
- Scope cut (logged): issue #157 proposed a `cc_memory_files_tokens` baseline field;
  dropped — no deterministic repo-local source (CC memory is user/env-specific). The
  baseline records only analyzer-emitted, repo-local signals. A test pins the omission.
- Ship SSoT/backlog written directly via Edit tool (not guard_context_write.py):
  current_state.md Ship History + Update Sequence 61->62 + dates; _product-backlog.md
  #51 Pending->Shipped + last_updated. lint_governed_writes scans code write-paths, not
  content edits, so no FAIL; guard receipt left advisory per ship.md §194.

## Evidence
- Tool end-to-end: `--init` seeds 6 scenarios + aggregate (exit 0); `--dry-run` all
  rows "ok" within ±10% slack (exit 0); `--init` again refuses (exit 2); `--apply`
  rewrites (exit 0).
- Tests: `tests/ci/test_lifecycle_baseline_drift.py` 6 passed; ratchet
  `test_validator_native_check_ratchet.py` 5 passed (sh 192 / ps1 193 == bumped
  baseline; above-floor justification present).
- Validators: `validate.sh` and `validate.ps1` both `pass=101 warn=9 fail=1 skip=2`,
  identical — the single FAIL is the local gitignored work-log count (see Drift Log);
  new `[PASS] token lifecycle drift: within slack` fires on both platforms.

## Review
4-expert adversarial panel (distinct lenses — value/direction, correctness,
cross-platform/CI, governance — to mitigate same-vendor blind-spot per Lesson
4faa557a; every material claim re-verified against code per Lesson ad985879):
- Value/direction: HELPS, correct shape. No existing test catches slow per-PR token
  creep (static ceilings in `test_lifecycle_token_consumption.py` bound only the gross
  case); reuses the analyzer; advisory-WARN + pytest-teeth = ADR-006 precedent.
- Correctness: no CI/behavior bug. Tests proven REAL mutation guards (panel
  monkeypatched each → fails on its mutation). base==0, slack boundary, CLI exit
  codes, `set -e` idiom, ps1 mirror all correct.
- Cross-platform/CI: green both platforms; worklog FAIL vanishes in CI (gitignored);
  baseline portable.
- Governance: COMPLIANT — ADR-006 escape hatch legitimate (wrappers cannot emit a
  present-Python WARN, confirmed at source); enforcement honest (real pytest teeth);
  scope cut documented + test-pinned; quick-win receipts pass.
- ADJUDICATION (verified, not relayed): REJECTED the value-expert's "CRLF inflates
  baseline ~462 tokens" — `read_text()` strips all 473 CRLF in trigger-registry.yaml
  (char len 19352 == LF-normalized 19352, CR residue 0); baseline is already
  LF-normalized and CI-identical. No regeneration needed.
- APPLIED two fixes, both re-verified green (native count unchanged 192/193):
  (a) reworded validator WARN so a detector error is not mislabeled "drift beyond
  slack" (correctness LOW); (b) ASCII-ized tool `print()` strings (em-dash → ASCII) —
  cp950 redirected-stderr UnicodeEncodeError risk caught in regression output.
- Verdict: PASS.

## Test Gate Results
- Full `tests/ci/` suite: 105 passed (13.5 min).
- Focused after fixes: `test_lifecycle_baseline_drift.py` 6 + ratchet 5 = 11 passed.
- Both validators: `pass=101 warn=9 fail=1 skip=2` identical; CI-equivalent fail=0
  (sole FAIL = gitignored local work-log count, absent in a CI checkout).
- New behavior covered: seed/refuse/apply/dry-run exit codes (0/2/0/0|1), growth-drift
  teeth, shrink-advisory, missing-scenario drift, schema + scope-cut pin.

## Phase Summary
- Bootstrap: classified quick-win; analyzer + scenarios + ADR-006 ratchet + advisory
  WARN precedent pre-exist; #157 is additive.
- Plan: 6 files. Decisions: drop cc_memory_files_tokens; growth=teeth/shrink=advisory;
  WARN via native block + ADR-006 justified bump.
- Implement: tool reuses `analyze_token_lifecycle.analyze()`; baseline LF-pinned; 6
  drift tests + native bump (192/193) + justification; both validators wired.
- Review: 4-expert panel + self-verification → PASS; rejected 1 false alarm with
  evidence; applied 2 small fixes (WARN reword + ASCII print).
- Test: 105 + 11 passed; both validators CI-equivalent fail=0.

⚡ ACX
