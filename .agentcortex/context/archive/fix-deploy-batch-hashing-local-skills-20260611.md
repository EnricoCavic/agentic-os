# Work Log: fix-deploy-batch-hashing-local-skills

## Header

- Branch: `fix/deploy-batch-hashing-local-skills`
- Classification: `quick-win`
- Classified by: `acx-implementer (sonnet), adopted by Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `88b82a0` (+ order-pairing fix pending commit)
- Recommended Skills: `verification-before-completion (auto), systematic-debugging (auto)`
- Primary Domain Snapshot: `none`
- SSoT Sequence: `51`

---

## Session Info

- Agent: Claude (Fable 5) — implement delegated to acx-implementer (worktree, 2 rounds), final root-cause redesign by session owner
- Session: 2026-06-10/11
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win)
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO

---

## Task Description

- Owner verdict: "tests take unreasonably long — fix it." Expert root cause (measured): each deploy spawns ~2,600 processes × ~28ms MSYS fork = 43-72s; one batch sha256 pass over 187 files = 0.10s. Attribution: slowness NOT deliberate (all code comments document correctness rationale, zero perf consideration). Plus Q4: the day-old [STALE SKILL] scan falsely accused downstream user-created skills ("retired upstream; delete it").
- Three implementation rounds (honest record):
  1. acx-implementer r1 (637c148): queue + batch hasher + stale-skill manifest split — measured only 14% faster; deviated from the pure-bash design (python hasher, /c/-only path translation).
  2. acx-implementer r2 (88b82a0): diagnosed 374/374 cache-key misses — python TEXT-MODE stdout emitted CRLF; bash keys kept a trailing \r (len 62 vs 61, xxd-confirmed) → every lookup missed → full per-file fallback (36.0s of 37.3s). Binary-stdout fix; claimed update ~6.5s (true in its worktree: /c/-style paths translate).
  3. Session-owner verification FAILED to reproduce (update 29.7s, 187 fallbacks): `/tmp`-form MSYS target paths are untranslatable by the /c/-only regex → silent full fallback again — same failure class via a different door. Root redesign: **order-paired hashing** — path strings never cross the bash↔python boundary (kills the key-corruption class entirely); `cygpath -m -f -` batch-translates any MSYS path form; MISS sentinels keep counts aligned; count mismatch → discard cache, degrade per-file (never wrong, only slower). Two more traps caught en route: heredoc-fed `python -` clobbered the stdin pipe (0 output lines → 0/187), and the translated temp file's own path needed cygpath too; nameref gate tightened to bash 4.3+.

## Plan

- deploy.sh only (+ r1 tests). Behavior identical — the 19-test module incl. EOL mutation guards is the lock. Rollback: revert PR. Confidence: 92% post owner-verified measurement.

## Review Feedback

- R1 (feature-grade scrutiny on quick-win): **PASS** — 11/11 behavioral criteria PROVEN incl. live E4-promise checks under the batch path (content edit → sidecar; CRLF-only → in-place), order-pairing attacks (cygpath 1:1 line count w/ nonexistent+spaced paths; count-mismatch guard fired in simulation), no-python deploy end-to-end OK. 3 LOW folded in pre-merge: flat-skill manifest lookup exact-match (prefix could false-accuse e.g. "red-team" vs "red-team-adversarial"); 3 stale design-era comments rewritten (load-bearing given this PR's boundary-misunderstanding history); queue/xlat temps added to EXIT trap (SIGINT leak window).

## Phase Sequence

- bootstrap (expert analysis + attribution)
- plan
- implement (3 rounds)
- review
- ship

## External References

- Q2 expert analysis (spawn census ~2,600/deploy; 100 per-file pipelines 11.1s vs one batch 0.10s); Q4 design (manifest-proven retired vs user-created); E4/PR #215 groundwork

## Known Risk

- Batch path requires newline-free paths (repo-controlled set; documented in code) + bash 4.3 namerefs (older → per-file path; macOS forks cheaply). Rollback = revert PR.

## Conflict Resolution

none

## Skill Notes

none

## Test Gate Results

- `python -m pytest tests/ci/test_deploy_tiering.py -q` → **19 passed in 231s** (module ~990s pre-fix — the fix proves itself in its own tests).
- Owner-measured (main checkout, /tmp target — the previously failing form): fresh **15.3s** / update **7.5s** (stock 43s/72s; ~10× on update), batch-mismatch fallbacks **0**.
- `ACX_FORCE_PERFILE=1` degradation smoke OK.
- `bash validate.sh` → fail=0.

## Phase Summary

- bootstrap/plan: root cause measured; slowness attributed non-deliberate; Q4 false-accusation gap designed away. ⚡ ACX
- implement: 3 rounds — two delegated rounds missed (14%; then environment-specific 6.5s that didn't reproduce); owner reproduction + order-pairing redesign landed the durable fix. Lesson ([audit-verification] family): sub-agent perf claims require owner-environment reproduction. ⚡ ACX
- ship: deploy update 72s→7.5s; test module 990s→231s; user-created skills no longer accused; custom-* silent. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T03:00:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T03:05:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T05:30:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T06:00:00+08:00

## Evidence

- Pre-fix spawn census (bash -x, update mode): 187 `compute_sha256_normalized` fallback calls → 0 post-fix; r2 section timers: second-pass 36.0s→0.43s on cache hit.
- r2 CRLF proof: xxd `0d 0a` line ends; key len 62 vs query 61; direct-key lookup hits, query-key misses.
- Stale-skill behavior: manifest-proven retired → loud [STALE SKILL]; user-created → ONE aggregated gentle note; custom-* silent (3 tests).
- Commits: 637c148 → 88b82a0 → order-pairing fix (this commit).
