# Work Log — feat/credential-ci-hardening

- Branch: feat/credential-ci-hardening
- Classification: quick-win
- Classified by: Claude Opus 4.8
- Frozen: true
- Created Date: 2026-06-13
- Owner: KbWen
- Guardrails Mode: Quick
- Current Phase: ship
- Checkpoint SHA: 977ca41
- Recommended Skills: verification-before-completion (implement/test/ship), karpathy-principles (plan/implement/review), auth-security (implement/review/test — credential handling)
- Primary Domain Snapshot: none
- SSoT Sequence: 64
- GH Issue: backlog #73, #74, #75 (all #225 review/dev-flow follow-ups)

## Session Info
- Agent: Claude Opus 4.8 (1M context)
- Session: 2026-06-13T15:48:11+08:00
- Platform: Claude Code (Antigravity workspace)
- Guardrails loaded: skipped (quick-win) — §13 heading-scoped already in context from #225
- Override: none

## Drift Log
- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- Dismissed task chip task_c1dd10f8 (#75) — handling inline in this batch instead of a separate session.

## Task Description
- Batch the 3 follow-ups from #225 (cohesive: pre-commit / CI credential / validator UX). One quick-win, one PR. Same rigor as #157/#225 (DELETE-bias, multi-expert review, dev-flow sim).
- **#73** CI PR-diff credential scan: add `scan_credentials.py --range <base>..<head>` + a pull_request CI step → cross-contributor pre-merge protection (hook is opt-in).
- **#74** CI ShellCheck lints only `**/*.sh`; `.githooks/*.sample` unlinted → fix the glob (+ fix the pre-existing SC2034 it will surface).
- **#75** opt-in #192 hook gates EVERY commit on the FULL validator → a CI-invisible local FAIL (gitignored worklog-count 14>12) blocks ALL commits. Fix in /plan.
- Phase chain: /plan → /implement → /review → /test → /ship.

## Phase Sequence
- bootstrap

## External References
- #225 review (4-expert panel) + dev-flow simulation findings. TruffleHog CI: `security.yml:99-101` uses `trufflehog@v3.95.5` with `--only-verified`.

## Known Risk
- DELETE-bias (#73): VERIFIED non-redundant — TruffleHog runs `--only-verified` (`security.yml:101`), so it flags only LIVE-verifiable secrets; a revoked/unverifiable but real-shaped credential passes it. #73's pattern scan on the PR diff catches the shape regardless of liveness → genuine complementary value.
- DELETE-bias (#75 FAIL→WARN): relaxing a gate — justified IF the check is CI-invisible (gitignored-driven). Confirm the worklog-count FAIL provides no CI enforcement before downgrading; keep it a visible WARN (honest tiering, not removal). This is "讓治理更完善" (a local hygiene signal shouldn't be a hard gate), not "破壞治理".
- #73 CI scan must scan only the PR DIFF (not whole-repo) to avoid false positives; the precise-only patterns (post-#225) keep FP low.

## Conflict Resolution
- none — verification × karpathy = compatible; auth-security has no conflict-matrix entries (per #225 pass).

## Skill Notes
- none

## Review Feedback
3-expert panel (fresh, diff-only) + my verification → **NOT READY**. #75 governance VALIDATED by the panel (honest FAIL→WARN re-tiering: work logs gitignored + count CI-invisible, exit driven by FAIL count only, co-located compaction FAIL left intact, No-Bypass untouched, endorsed by [enforcement]/[rule-placement] lessons). Blocking findings on #73:
- [MED][false-positive] VERIFIED by me: the CI credential-scan BLOCKS a legit PR on full-length EXAMPLE tokens that share the real shape — `AKIAIOSFODNN7EXAMPLE` (AWS's OWN canonical doc example) → flagged (exit 1). Also ghp_/AIza/sk-+40/PEM-header in docs/fixtures. No escape hatch. FIX: add an inline `# pragma: allowlist secret` allowlist (detect-secrets convention) to scan_text.
- [MED][range] two-dot `base..head` over-scans vs the repo's own three-dot `base...head` (security.yml `changes` job L48): on a diverged base it can attribute a credential already on main to the PR → false block. FIX: use `...` in the credential-scan job + the scanner docstring.
- [MED][CI fail-safe] the job treats exit 3 (scan-couldn't-run: zero-sha / git error) the SAME as exit 1 (found) → false block; sibling jobs guard zero-sha, and the scanner docstring says exit 3 = WARN-not-fail. FIX: zero-sha guard + map exit 3 → `::warning::` + exit 0 (rely on TruffleHog).
- PASS: --staged identical post-refactor; --range correct; argparse no shadow; exit-3 fail-closed both modes; self-skip honored in --range; #73 genuinely non-redundant vs TruffleHog `--only-verified` (revoked / unverifiable-PEM / offline-CI cases); validate.yml .sample lint sound; #75 honest.
- Durable-record note (expert 2, optional): record the FAIL-vs-WARN tiering principle ("FAIL reserved for CI-visible/correctness state; gitignored/local-only hygiene = WARN") as a retro lesson so it isn't misapplied later.

## Phase Summary
- bootstrap: classified quick-win (touches validate.* + .github/workflows + scanner + tests; no spec/handoff). 3 cohesive #225 follow-ups. #73 DELETE-bias confirmed non-redundant (TruffleHog --only-verified gap). SSoT seq 64.
- plan: 7 files. #73 scanner --range (refactor _staged_added_lines → shared _diff_added_lines) + security.yml pull_request `credential-scan` job (reuse base/head SHA infra at L35-37); #74 validate.yml ShellCheck also lints `.githooks/*.sample` + remove the hook's dead `warn` accumulator (the SC2034 it surfaces); #75 worklog-count FAIL→WARN at validate.sh:999 + validate.ps1:967 (still line-leading record_result → ADR-006 baseline 192/193 unchanged, no bump). Mode Normal | Confidence: 88% — #73 CI base/head ref handling is the main risk (mirror trufflehog's existing range pattern); #75 = 2-line severity change.
- implement: 7 files. --range scanner mode + CI job + ShellCheck .sample + hook dead-warn removed + worklog FAIL→WARN. 15 tests pass (incl. --range); ratchet 192/193 unchanged; **LOCAL validate now fail=0** (#75 fixed the perennial worklog FAIL AND the dev-flow hook-blocks-all-commits issue at the root). | Confidence: 92% — high.
- review: NOT READY — 3-expert panel + my verification: 3 MED on #73 (AWS-EXAMPLE-token false-positive [verified], two-dot→three-dot range, exit-3-treated-as-found). #75 governance validated as honest. Routed back to /implement.
- implement(fix): allowlist pragma (scan_text skips `# pragma: allowlist secret`) + three-dot `base...head` range + zero-sha/exit-3 fail-safe in the CI job. AWS-example FP resolved (with-pragma→clean, without→caught); 17 tests; ratchet 192/193. Commit 977ca41.
- re-review: PASS — all 3 MED fixed & verified (allowlist escape works, YAML parses, exit-3/zero-sha logic traced correct, three-dot matches the repo convention). #75 governance was panel-validated as honest tiering. | Confidence: 92% — high.
- test: PASS — 17 unit tests + dev-flow simulation. #75 confirmed (validate.sh+ps1 both fail=0, worklog→WARN under 5.1 and 7); hook correctly blocks real validate FAILs; the sim's temp-file `text integrity` FAILs were my own printf-EOL harness artifact ([cross-platform-eol] footgun), not a product issue.
- ship: SSoT Ship History + backlog #73/#74/#75 → Shipped (pending).

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
- #73: `scan_credentials.py --range A..B` verified in an isolated temp git repo (HEAD~1..HEAD with a runtime ghp_ → exit 1, `b.txt:1: github-token` redacted; HEAD..HEAD → exit 0). `security.yml` `credential-scan` pull_request job added (scans base..head; complements TruffleHog `--only-verified`).
- #74: `validate.yml` ShellCheck now also lints `.githooks/*.sample`; the hook's dead `warn`/`warn=1` accumulator removed (the SC2034 it surfaces).
- #75: `validate.sh:999` + `validate.ps1:967` FAIL→WARN. **Local validate now `pass=101 warn=10 fail=0`** — the perennial worklog-count FAIL is gone; a dev with the #192 hook installed can now commit benign code (the validator no longer hard-FAILs on gitignored, CI-invisible cruft). Real validate FAILs still block the hook.
- Tests: 15 passed (incl. new `test_range_mode`); ADR-006 ratchet GREEN — native count unchanged 192/193 (FAIL→WARN kept the line-leading `record_result`, no baseline bump).

⚡ ACX
