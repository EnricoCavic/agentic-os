---
status: shipped
title: Hard Work Log Lock (advisory → blocking)
source: GitHub issue #147 / backlog #17
created: 2026-06-10
primary_domain: governance
secondary_domains: [workflow, tooling]
---

# Hard Work Log Lock (advisory → blocking)

## Goal

Upgrade the Work Log lock (`.agentcortex/context/work/<worklog-key>.lock.json`) from advisory to blocking so concurrent sessions cannot silently interleave writes to one branch's Work Log: atomic cross-platform acquisition, explicit release/takeover verbs, mode-aware phase-entry gate semantics, and validator teeth — with the enforcement boundary stated honestly.

## Acceptance Criteria

- AC-1: Lock acquisition in `recover_worklog_lock.py` is atomic and never overwrites an active other-holder lock: creation uses `O_CREAT|O_EXCL`; the recoverable path (stale / dead-pid / corrupt) uses unlink (FileNotFoundError tolerated) followed by `O_CREAT|O_EXCL`, and on EEXIST re-classifies — exiting 2 if another holder is now active; only the same-owner+session update path uses tmp + `os.replace`.
- AC-2: The Drift Log recovery line is appended only after the recovering session has won the `O_EXCL` create — a session that loses the race writes nothing.
- AC-3: New `release` subcommand: deletes the lock iff `owner` + `session` match; missing lock → exit 0 with status `missing` (idempotent); other-holder lock → exit 2, no delete.
- AC-4: New `--takeover` flag on `ensure`: permits replacing an ACTIVE other-holder lock; requires `--worklog`; appends one Drift Log takeover line naming the prior owner and session. Without `--takeover`, active-other behavior is unchanged (exit 2).
- AC-5: Transient Windows unlink/replace failures (WinError 5/32) get a bounded retry (3 × 100 ms); final failure exits non-zero with a distinct `reason` instead of misreporting the lock state.
- AC-6: `.agent/config.yaml §worklog_lock` gains `mode: blocking` (default) / `advisory`; the comment block is corrected to describe only checks the validators actually perform. Tool behavior is mode-independent — `mode` governs how workflows consume exit 2.
- AC-7: `shared-contracts.md` gains a **Phase-Entry Lock** contract: every non-`tiny-fix` phase entry runs `ensure` with the current phase; exit 2 under `blocking` = Gate FAIL with explicit options (wait for staleness / user-approved `--takeover` / different branch); under `advisory` = warn + confirm. `tiny-fix` exempt. Python-unavailable hosts degrade to the documented manual advisory checklist (stated honestly — no fake MUST).
- AC-8: `bootstrap.md §2a` is rewritten mode-aware and §1 Step 2's "Concurrent session detected" prompt defers to the lock verdict (single authoritative concurrency check). Test-asserted literals (`.agentcortex/tools/recover_worklog_lock.py ensure`, `Drift Log`) are preserved.
- AC-9: `ship.md` and `handoff.md` gain a lock-release step at phase exit (MUST attempt `release`; failure → WARN, not gate-fail). `AGENTS.md §Multi-Person` wording updated from "Advisory lock" to mode-aware phrasing.
- AC-10: `validate.sh` AND `validate.ps1` (parity) add WARN checks for **non-stale** locks only: lock `owner` vs Work Log `Owner` mismatch; lock `phase` vs Work Log `Current Phase` mismatch. Existing stale-lock WARN unchanged; never FAIL.
- AC-11: New `tests/guard/test_worklog_lock_blocking.py` covers: deterministic create/recovery race injection (EEXIST handling), release happy path / wrong-owner / idempotent-missing, takeover Drift Log line, exit codes, same-session re-ensure. All existing tests in `test_worklog_lock_recovery.py` stay green.

## Non-goals

- No `guard_context_write.py` verification of lock ownership before Work Log writes — write-level enforcement is a separate backlog candidate. "Blocking" here means gate semantics with unambiguous tool verdicts; an agent that ignores exit 2 can still write. This boundary is stated, not hidden.
- No change to Domain Doc L2 locks (`domain_doc.lock_stale_timeout_minutes`).
- No third-party dependencies (stdlib-only stays).
- No `.gitignore` change — `*.lock.json` under `context/work/` is already ignored upstream and in the deploy-managed downstream block (verified precondition, not a work item).

## Constraints

- Cross-platform without `flock`: `O_CREAT|O_EXCL` + `os.replace` (atomic on NTFS and POSIX).
- Stale-timeout semantics (60 min default) unchanged; lock refresh is phase-granular, so a single >60-min phase still opens a mid-phase staleness window — documented next to the timeout config, not papered over.
- Downstream: `recover_worklog_lock.py` is force-update tier in `deploy.sh`; downstream `config.yaml` is user-owned, so absent `mode` keys inherit the `blocking` default — called out in release notes.
- Enforcement honesty (Global Lesson [enforcement][HIGH]): teeth = tool exit codes + validator WARNs + guard tests; workflow text only consumes those verdicts.

## File Relationship

Extends the auto-recovery feature (`worklog-lock-auto-recovery.md`, shipped 2026-06-08) and rides under ADR-002's guarded-governance-writes domain. Supersedes that spec's "keep locks advisory" decision by explicit design (this feature IS the advisory→blocking graduation the earlier non-goal deferred).

## Domain Decisions

- [DECISION] `mode` lives at the workflow-consumption layer, not in the tool: the tool already refuses to clobber active locks and exits 2 in both modes; branching tool behavior on mode doubles the test matrix for zero benefit.
- [DECISION] Default `mode: blocking`. Solo single-session flows never hit exit 2; the crash-resume-within-60-min case costs one `--takeover` confirmation — friction parity with today's advisory "Proceed?" prompt.
- [DECISION] Recovery uses unlink + `O_EXCL` (serializes racing recoverers), NOT `os.replace` (last-writer-wins would let two sessions both believe they recovered).
- [DECISION] Release at /ship AND /handoff: the post-handoff window is exactly when another session resumes within the staleness timeout; release failure is WARN because staleness self-heals.
- [CONSTRAINT] `--takeover` requires `--worklog` so the audit line cannot be silently skipped.
