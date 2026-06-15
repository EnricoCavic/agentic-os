# Work Log — feat/precommit-credential-scan

- Branch: feat/precommit-credential-scan
- Classification: quick-win
- Classified by: Claude Opus 4.8
- Frozen: true
- Created Date: 2026-06-13
- Owner: KbWen
- Guardrails Mode: Quick
- Current Phase: ship
- Checkpoint SHA: b460c2f
- Recommended Skills: verification-before-completion (implement/test/ship), karpathy-principles (plan/implement/review), auth-security (implement/review/test — task handles credential/token/secret patterns)
- Primary Domain Snapshot: none
- SSoT Sequence: 62
- GH Issue: #225 (backlog #71)

## Session Info
- Agent: Claude Opus 4.8 (1M context)
- Session: 2026-06-13T11:53:06+08:00
- Platform: Claude Code (Antigravity workspace)
- Guardrails loaded: skipped (quick-win) — §13 heading-scoped read deferred to /plan per §0 token-leak rule
- Override: none (no root/home AGENTS.override.md — checked this session)

## Drift Log
- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- Ship SSoT/backlog written directly via Edit (not guard_context_write.py): current_state.md Ship History + Update Sequence 62->63 + dates; backlog #71 In Progress->Shipped + registered review-finding rows #73/#74. lint_governed_writes scans code write-paths not content edits -> no FAIL; guard receipt advisory per ship.md §194.
- NOT READY receipt deviates from review.md §279 format by adding `Classification:` (the validator's gate-receipt schema requires Verdict+Classification, which the review.md format omits) — framework inconsistency, recorded.

## Task Description
- Issue #225 (backlog #71): T1 pre-commit credential-regex check = the **L2 machine layer** for the AGENTS.md Secrets Prohibition invariant (currently T2/eval-backed; CI TruffleHog is post-commit only — the secret is already in object history once committed; a push window is an exfiltration window, and rotation-not-deletion becomes the remedy).
- Strong evidence: designated follow-up from PR #224 safety-invariant promotion. Consumer = Secrets Prohibition (always-on) which today lacks a *pre-commit* machine layer.
- Scope (per issue): regex for AWS keys, PEM headers, connection strings, bearer/API tokens; wired into the existing pre-commit-local-validation mechanism (`.githooks/pre-commit.guard-ssot.sample`, #192); sh/ps1 parity; fixture tests both directions (catch + no-false-positive on docs). Declared tier when shipped: T1.
- Phase chain: /plan → /implement → /review → /test → /ship.

## Phase Sequence
- bootstrap

## External References
- Issue #225, backlog #71. PR #224 (safety-invariant promotion) registered this follow-up. Existing mechanism: `.githooks/pre-commit.guard-ssot.sample` (opt-in hook from #192). pre-commit-local-validation.md spec is [Shipped] — NOT opened (AC-28). docs/adr non-empty → quick-win no-ADR-prompt.
- Credential pattern formats (public, supporting metadata per §13 — NOT a code dependency; Python `re` stdlib only): AWS access-key-id `AKIA`+16 base32; PEM private-key headers (RFC 7468 `-----BEGIN ... PRIVATE KEY-----`); token prefixes GitHub `ghp_`/`github_pat_`, OpenAI `sk-`, Slack `xox[baprs]-`, Google `AIza`; connection strings `proto://user:pass@host`.

## Known Risk
- **Enforcement reach**: the pre-commit hook is OPT-IN (`.sample`, user installs) AND bypassable (`--no-verify`). A hook-only layer is not a true machine gate. /plan to decide whether to ALSO wire a credential scan into CI (validate.* via run_python_check per ADR-006, or a CI job) so the layer is actually enforced, not advisory-opt-in.
- **Mechanism choice** (/plan): Python tool (ADR-006, cross-platform, one impl, reusable in hook + validate.*) vs bash-grep-in-hook (dependency-light, literal T1). Lean Python-tool + hook caller + optional validate wiring; needs a Python-unavailable fallback for the hook.
- **False positives**: issue mandates no-false-positive on docs. Regex must be tight; fixture tests both directions.
- **Secret redaction**: scanner MUST NOT echo matched secret VALUES (auth-security discipline) — report file:line + pattern-name only.
- **Fixture self-poisoning**: test fixtures need credential-SHAPED strings that are verifiably FAKE (e.g. AKIA + zeros) AND the scanner + TruffleHog must allowlist the fixture path, else the scanner flags its own fixtures and TruffleHog/Secrets-Prohibition trips on the test data. RESOLVED in plan: tests build fakes by runtime string-concat so NO complete credential literal sits in the repo → no allowlist needed, no TruffleHog/self-scan trip.

## Design Decision (plan)
- Mechanism: Python tool `scan_credentials.py` (ADR-006: one impl, cross-platform — dissolves the sh/ps1 parity concern) called by the `.githooks` pre-commit hook on the STAGED diff. NOT wired into validate.* (whole-repo scan risks false positives on benign/example content; CI TruffleHog is the existing post-commit backstop). §13 ADD-Gate tier = **T1 machine-enforced** (tested scanner + hook in the same change). Honest enforcement model: hook = opt-in local pre-commit fast-catch; pytest = machine-verifies the scanner; TruffleHog = CI enforcement. The hook being opt-in/bypassable is acceptable because TruffleHog backstops at CI (issue's own framing).
- Rollback: revert PR — purely additive (new tool + new test + edit to an opt-in `.sample` hook); zero impact on anyone who has not installed the hook.

## Risks
- False positives blocking commits → mitigate: tight patterns + staged-diff-only scope + no-false-positive fixtures + hook is opt-in. Rollback: revert PR.
- Regex precision (the only real tuning risk) → the no-false-positive fixtures (near-miss benign strings) are the guard; tune in /implement.

## Conflict Resolution
- none — verification × karpathy = compatible; auth-security has no entries in skill_conflict_matrix.md (independent, no conflict).

## Skill Notes
- none

## Review Feedback
4-expert panel (fresh instances, diff-only per the Freshness Invariant) + my own code verification → **NOT READY**. Blocking findings (resume scope for /implement):
- [HIGH][false-positive] Patterns too loose — VERIFIED by running the scanner: 5 FPs on realistic benign content (`sk-`+32 data-id→openai-key; benign JWT→jwt; `postgres://user:password@`, `amqp://guest:guestpassword@`, `postgres://user:${DB_PASSWORD}@`→connection-string). A commit-blocking hook with these FPs gets disabled by devs. (experts 1+4, verified by me.)
- [HIGH][honesty] T1 label overclaims (`scan_credentials.py:1`). Machine-enforced = the regex *correctness* (pytest); NOT the invariant — no CI job scans the diff, hook is opt-in `.sample` (not installed even here), `--no-verify`-bypassable. Honest tier = dev-convenience, not "T1 machine-enforced invariant layer". Matches my own plan-time [enforcement] flag that I then declared T1 anyway. (expert 3.)
- [HIGH][test] `test_output_is_redacted` (test:78) weak — whole-string `fake not in ...` only; a body/partial leak (`value[4:]`) passes. Need structural assertion (no ≥8-char run of the value). (expert 4, verified.)
- [HIGH][doc-honesty] docstring implies "AWS" coverage but AWS *secret* keys (40-char) uncaught; cross-line/binary/env-indirection evasions undocumented. (expert 1.)
- [MED][hook] fail-OPEN when git exits non-zero (`subprocess.run` no `check`; non-zero→`[]`→exit 0→commit allowed, `scan_credentials.py:72-77`); `+++`-content-line drop (`:86`); trailing-TAB path corruption defeats `_is_self` on space-paths (`:82`). (expert 2, ShellChecked — added hook block itself is SC-clean.)
- [MED][coverage] `--staged` (the PRIMARY use case) has ZERO tests; `_BENIGN` too easy; conn-string `{6,64}` boundary untested. (expert 4.)
- PASS: redaction has no full-value leak; self-poisoning genuinely avoided; hook portable + the added block ShellCheck-clean. (experts 1,2,4.)

Recommended fix (precise-only redesign — keeps value, kills FPs, honest):
1. DROP `connection-string-password` + `jwt` from the blocking set — intrinsically ambiguous (benign vs secret share the shape; JWTs often non-secret); leave to TruffleHog. This removes 4 of 5 FPs.
2. FIX `openai-key` → real format `sk-(proj-|svcacct-)?...{40,}` (kills the last FP + the `sk-proj-` FN); tighten `slack-token` charclass.
3. Honest framing — drop the §13 "T1 machine-enforced" self-label; docstring = "high-confidence pre-commit catch; regex CI-tested; TruffleHog is the enforced control." Add an explicit "Does NOT catch" block (AWS secret keys, cross-line, binary, env-indirection).
4. Strengthen tests — structural redaction assertion; add the false-firing benign strings to `_BENIGN`; add a `--staged` test; conn-string boundary (if kept).
5. Fix hook — fail-closed/warn on git non-zero; fix `+++` drop + trailing-tab.

## Phase Summary
- bootstrap: classified quick-win (extends pre-commit/governance tooling; no spec/handoff). Context loaded from SSoT (seq 62) + `.githooks` sample. Strong evidence (PR #224 follow-up). Key design constraints flagged for /plan (enforcement reach, mechanism, redaction, fixture self-poisoning).
- plan: 3 target files (scan_credentials.py + .githooks hook edit + test); Python-tool+hook (NOT validate.*; TruffleHog = CI backstop), T1 per §13; runtime-assembled fixtures avoid self-poisoning. Mode Normal | Confidence: 88% — staged-diff-only + tight patterns + no-FP fixtures keep false positives acceptable.
- implement: 3 files (+247); 5/5 tests; `--staged` both directions verified on real git index (dirty→exit1 redacted, clean→exit0); validate CI-equiv fail=0 (local worklog-count artifact only); security quick-scan clean; shellcheck → CI. Commit 5445efc. | Confidence: 90% — high.
- review: NOT READY — 4-expert panel + my verification found 5 reproduced false-positives (commit-blocking), an overclaiming T1 label, a weak redaction test, hook fail-open, and untested --staged. Routed back to /implement (precise-only redesign + honest framing). The user-requested deep review caught what implement's 5/5 green missed.
- implement(fix): precise-only redesign — dropped connection-string+JWT (ambiguous→TruffleHog), fixed openai (sk-proj-/legacy-48) + slack (24-tail) patterns, honest framing (no T1 claim + Does-NOT-catch block), hook fail-closed-with-warn, ScanError exit 3. 5 FPs→0 verified, catch intact (6 real shapes), 10 tests. Commit a6f0f1c.
- re-review: PASS — fresh independent verifier confirmed F1-F4,F6 fixed AND caught an F5-residual false-negative (an added content line `++ /dev/null`→diff `+++ /dev/null` reset the file context and dropped the next secret; reproduced rc=0). Fixed with hunk-context parser + regression test; re-reproduced → now caught (rc=1). All 6 findings + the new issue resolved & verified. Commit b460c2f. | Confidence: 92% — high.
- test: 10 unit tests + end-to-end simulation (installed hook → staged fake AWS key → git commit BLOCKED, value redacted 0-leak, no commit created, config restored). | Confidence: 95% — high.

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: review | Verdict: NOT READY | Classification: quick-win | Transition: REVIEWED→IMPLEMENTING | Timestamp: 2026-06-13
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-13

## Evidence
- Unit: `tests/ci/test_scan_credentials.py` 10 passed (catch 7 patterns + 14 benign no-FP + structural redaction + parse-diff edge cases incl. the `++ /dev/null` regression + git-failure exit 3 + self-skip).
- FP elimination: the 5 review-reproduced false positives → all exit 0 (clean); 6 real key shapes (incl. legacy sk-48 / full slack / PEM OPENSSH) → all caught.
- Simulation (end-to-end): opt-in hook installed → staged fake AKIA → `git commit` BLOCKED with redacted message; AKIA value occurrences in hook output = 0; no commit created (HEAD stayed b460c2f); `core.hooksPath` restored to original.
- validate.sh CI-equiv fail=0 (sole local FAIL = the gitignored active-work-log count; my code adds no FAIL/WARN).
- Dev-flow simulation (real developer workflow, per user request — not just install): (A) credential layer on REALISTIC benign dev code (a module with a `${DB_PASS}` connection-string in a comment, a `sk-loading-spinner` CSS id, a `Bearer {token}` ref, a URL) → exit 0, NO false-positive (confirms the precise redesign on real code); (C) an accidental hardcoded AKIA in a staged file → credential BLOCK before the validator. (B) FINDING (pre-existing #192, surfaced): the installed hook gates EVERY commit on the FULL validator passing, so a local validate FAIL — here the gitignored worklog-count cruft (14>12, CI-invisible) — blocks ALL commits incl. benign ones. #225's credential layer is correct + dev-friendly; the validator-gating is #192's design → registered as a follow-up.

⚡ ACX
