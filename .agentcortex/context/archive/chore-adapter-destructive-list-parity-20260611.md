# Work Log: chore/adapter-destructive-list-parity

| Field | Value |
| --- | --- |
| Branch | chore/adapter-destructive-list-parity |
| Classification | quick-win |
| Classified by | Claude (Fable 5) |
| Frozen | true |
| Created Date | 2026-06-11 |
| Owner | claude-fable-5 |
| Guardrails Mode | Quick |
| Current Phase | ship |
| Checkpoint SHA | e509a06 (base: PR #222 head — STACKED on fix/downstream-incident-findings) |
| Recommended Skills | verification-before-completion (auto), karpathy-principles (auto) |
| Primary Domain Snapshot | none |
| SSoT Sequence | 56 |

## Session Info
- Agent: Claude (Fable 5)
- Session: 2026-06-11T16:30:00+08:00
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win)
- Override: none

## Drift Log
- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- Stacked-PR note: base PR #222 unmerged; repo merges via merge commits (safe per [pr-workflow] lesson). After #222 merges: retarget this PR to main + push a sync commit so CI fires.

## Task Description
Follow-up to PR #222 (Destructive Command Gate in AGENTS.md §Core Directives). The two platform
adapter surfaces carry day-one copies of the blacklist with divergent lists:
- `codex/rules/default.rules:4-5`: has `sudo curl | bash`; missing `git checkout/fetch --force`,
  force pushes; no canonical citation.
- `.antigravity/rules.md:10`: has blind `sudo`; missing `git checkout/fetch --force`, force
  pushes; no canonical citation.
Align: adapters keep self-contained inline lists (Codex `prefix_rule()` injects literal prompt
text; Antigravity workspace rules likewise load standalone) but cite AGENTS.md §Core Directives
(Destructive Command Gate) as canonical and add the missing canonical entries + untracked-state
rollback nuance. AGENTS.md NOT touched (adapters may keep platform-specific extras like sudo
entries; canonical absorbs nothing this change — scope discipline).

**Constraint (verified)**: validate.sh/.ps1 pin literals — `.antigravity/rules.md` must contain
`docker system prune -a`, `chown -R`, `rollback`; codex rules must contain `prefix_rule(`,
`docker system prune -a`, `chown -R`. All edits are ADD-only → canaries survive; no validator
edits needed. tests/ pin nothing on these files (grep zero).

## Phase Sequence
- bootstrap
- plan
- implement
- ship

## External References
- PR #222 (canonical gate) — base of this stack
- doc-governance: adapters point back to shared rules instead of duplicating

## Known Risk
- Adapter text is downstream-deployed (deploy.sh sites 826-827) — wording must stay platform-appropriate; ADD-only edits keep validator canaries intact. Rollback = revert PR.

## Conflict Resolution
none

## Skill Notes
none

## Phase Summary
- bootstrap: quick-win; both divergences re-verified against working tree; canary constraints mapped; stacked on #222 head e509a06.
- plan: 2 files, ADD-only (missing entries + canonical citation each); verify = grep canaries + validate.sh both platforms | Confidence: 95% — high
- implement: both adapters aligned (checkout/fetch --force + force pushes + untracked-state rollback + canonical citation); validate.sh pass=100 fail=0, all adapter canaries PASS.
- ship: PASS — PR #223 opened (closure: Open PR, stacked on #222); archive .agentcortex/context/archive/chore-adapter-destructive-list-parity-20260611.md ⚡ ACX

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T16:32:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T16:33:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T16:45:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T16:50:00+08:00

## Evidence
- Commit: 7d54ee9 — 2 files changed, 2 insertions(+), 2 deletions(-) (ADD-only line rewrites)
- `validate.sh` → pass=100 warn=11 fail=0 (all 6 adapter canary checks PASS) · `validate.ps1` → pass=101 warn=10 fail=0
- grep verified: tests/ pin nothing on the two adapter files
- PR #223 (stacked on #222; retarget to main + sync commit after base merges)
