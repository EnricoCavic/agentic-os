# Work Log: fix-deploy-eol-hash-stale-skills

## Header

- Branch: `fix/deploy-eol-hash-stale-skills`
- Classification: `feature`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Full`
- Current Phase: `ship`
- Checkpoint SHA: `18e84d5`
- Recommended Skills: `verification-before-completion (auto), red-team-adversarial (auto), test-driven-development (auto)`
- Primary Domain Snapshot: `document-governance` (rides ADR-005 deploy-tiering domain)
- SSoT Sequence: `49`

---

## Session Info

- Agent: Claude (Fable 5) — implementation delegated to acx-implementer in isolated worktree; review by acx-reviewer; orchestration + verification by session owner
- Session: 2026-06-10
- Platform: Claude Code (Windows)
- Guardrails loaded: cached core + §5/§12 (implement-entry)
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- Process note: an in-flight agent worktree gitlink was accidentally swept into PR #214's first commit by `git add -A`; removed same-PR and `.claude/worktrees/` is now gitignored (prevention, not just cleanup).

---

## Task Description

- E4 of the strict self-assessment queue (user-directed: verify real → fix in order; fork flexibility is first-class). Two defects EVIDENCED in the live downstream (agent-virtual-office @ v1.2.0, read-only reference):
  1. HIGH — raw-byte sha256 in deploy.sh misclassifies CRLF-checked-out-but-unmodified files as "locally modified" (downstream AGENTS.md byte-identical to upstream 1.2.0 under --strip-trailing-cr, yet hash-mismatched). Consequence: spurious .acx-incoming sidecars → framework updates silently don't land — the exact failure class ADR-005 exists to prevent. Root cause: .gitattributes pinned eol=lf only for *.py/*.json; *.md is bare `text`.
  2. MEDIUM — skills retired upstream before a downstream's manifest era (5 skills deleted in f3d97fc) are invisible to the removed-files detector forever; stale SKILL.md contradicts inlined workflows.
- E4 NOT-REAL verdicts also actioned: issue #164 (local_guardrails.md) closed as redundant — override layer (ADR-004) already provides the surface; zero demand signal downstream.

## Plan

- deploy.sh: compute_sha256_normalized (tr -d '\r'); double-compare migration for old raw-hash manifests; normalized hashes in new manifests; stale-skill scan (live source-derived set, warn-only, custom-* exempt). deploy.ps1 verified pure bash-wrapper → no parallel change.
- .gitattributes: *.md/*.yaml/*.yml eol=lf (index already all-LF → zero renormalization churn, reviewer-verified).
- tests/ci/test_deploy_tiering.py: +4 behavioral tests + direct manifest-hash mutation guards.
- Rollback: revert PR. Confidence: 90%.

## Review Feedback

- R1 (red-team): NOT READY — production code PROVEN at all 4 design items; HIGH = the 2 EOL tests passed with the fix "reverted" (mutation). Fix 18e84d5: direct LF-normalized manifest-hash assertions. Post-fix mutation check: call-site revert → 2 FAILED ("revert to compute_sha256 (raw) = regression"); restored → 2 passed. Methodology note: R1's own sed mutation was flawed (renamed the function DEFINITION → bash override kept normalization active), so the original "test blindness" was partly an artifact — the new direct assertions are strictly stronger regardless and kill the CORRECT call-site mutation.
- R1 LOW (accepted, documented): binary files would hash-corrupt under tr -d '\r' — not exploitable (deploy set verified text-only via git ls-tree); latent guard noted in code comment. Unquoted word-split in stale-skill loop — warn-only surface, accepted.

## Security Findings

- none. Warn-only detection, no destructive ops, no injection surface (reviewer-verified basename/glob handling).

## Phase Sequence

- bootstrap (E4 expert analysis = research+plan basis)
- plan
- implement (delegated, worktree)
- review (NOT READY → fix → mutation-verified)
- test
- handoff
- ship

## External References

- E4 expert analysis 2026-06-10; ADR-005 (covering domain); downstream evidence: agent-virtual-office v1.2.0 manifest-vs-disk hash divergence on byte-identical AGENTS.md
- Issue #164 closed as redundant (override layer); backlog row #58 → Cancelled this ship

## Known Risk

- Deliberate downstream CRLF→LF-only edits are now treated as unmodified (update lands in place) — consistent with ADR-005 (content preserved; EOL is framework-canonical), reviewer-judged acceptable.
- Rollback plan: revert PR; old manifests keep working either way (double-compare reads both hash forms).

## Conflict Resolution

none

## Skill Notes

none

## Test Gate Results

- `python -m pytest tests/ci/test_deploy_tiering.py -q` → **18 passed** (14 existing + 4 new) in 991s (implementer, worktree) + spot re-verify in main tree: stale/custom subset 4 passed.
- Mutation gate: call-site raw-hash revert → 2 failed (expected); restored → passed.
- `bash validate.sh` (worktree) pass=103 fail=0; `--no-python` pass=95 fail=0 (reviewer).

## Resume

- State: TESTED → HANDEDOFF → ship in flight
- Next: push branch, PR (closes nothing — assessment-queue item), CI green incl. Windows, merge; ship metadata (Ship History + backlog row #58 Cancelled + archive log) lands on the same branch pre-PR.

### Read Map

- .agentcortex/bin/deploy.sh — compute_sha256_normalized + stale-skill block
- tests/ci/test_deploy_tiering.py — manifest-hash mutation guards

### Skip List

- deploy.ps1 (pure wrapper, verified twice)

### Context Snapshot

- Branch @ 18e84d5 (2 commits); downstream upgrade 1.2.0→1.4.x will now land .md updates correctly and name its 5 orphaned retired skills.

### Backlog Status

- Row #58 → Cancelled (issue #164 redundant-closed) in this ship; no other rows touched.

## Phase Summary

- bootstrap/plan: E4 expert analysis verified against live downstream evidence; design bound. ⚡ ACX
- implement: 668cf70 (delegated, isolated worktree; ps1 confirmed wrapper; .gitattributes risk-assessed). ⚡ ACX
- review: R1 NOT READY (HIGH test-mutation gap) → 18e84d5 direct manifest-hash guards, mutation-verified both directions → PASS. ⚡ ACX
- test: 18/18 module + mutation gate + no-python validate. ⚡ ACX
- handoff: Resume written; closure = PR on green CI. ⚡ ACX
- ship: Ship History + row #58 Cancelled + archive; release-notes line for downstream upgrade. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T20:10:00+08:00
- Gate: plan | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T20:15:00+08:00
- Gate: implement | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T21:00:00+08:00
- Gate: review | Verdict: NOT READY | Classification: feature | Timestamp: 2026-06-10T21:30:00+08:00 | Transition: REVIEWED→IMPLEMENTING
- Gate: implement | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T22:10:00+08:00
- Gate: review | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T22:20:00+08:00
- Gate: test | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T22:30:00+08:00
- Gate: handoff | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T22:35:00+08:00

## Evidence

- Downstream repro (read-only): agent-virtual-office AGENTS.md `diff --strip-trailing-cr` vs upstream 1.2.0 = empty, raw hashes differ → misclassification proven before any code written.
- Mutation evidence: with call-site raw hashing, both EOL tests fail with explicit "revert = regression" message; with fix, 18 passed.
- Reviewer live checks: LF≡CRLF normalized hash equality; `git ls-files --eol` 0 i/crlf .md (no renormalization churn); no-python validate pass=95 fail=0.
- Commits: 668cf70 → 18e84d5.

## Observability

- deploy.sh prints [STALE SKILL] warnings + locally-modified decisions to stdout per run — operator-facing CLI; no production sink applicable.
