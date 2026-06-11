# Work Log: fix/downstream-incident-findings

| Field | Value |
| --- | --- |
| Branch | fix/downstream-incident-findings |
| Classification | quick-win (w/ feature-grade review) |
| Classified by | Claude (Fable 5) |
| Frozen | true |
| Created Date | 2026-06-11 |
| Owner | claude-fable-5 |
| Guardrails Mode | Quick |
| Current Phase | ship |
| Checkpoint SHA | f20c7c4 (pre-change base: 0a75067) |
| Recommended Skills | verification-before-completion (auto: completion claims), systematic-debugging (auto: incident root-cause), karpathy-principles (auto: non-trivial baseline) |
| Primary Domain Snapshot | none |
| SSoT Sequence | 55 |

## Session Info
- Agent: Claude (Fable 5)
- Session: 2026-06-11T12:00:00+08:00
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win; §13 heading-scoped read planned before governance edits — sole exemption)
- Override: none

## Drift Log
- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- Re-read: engineering_guardrails.md §13 only — reason: governance-path edit, sole quick-win exemption per bootstrap §0
- Skipped: /decide (design fork: rule surface AGENTS.md vs engineering_guardrails.md) — always-loaded test makes AGENTS.md dominant; rationale in §Decisions D-3
- Environmental note (/test): one validate.sh run died exit-255 after check 71 (0 FAIL up to that point) — attribution: 3 concurrent validate.sh sessions on the machine + my own Force-kill of an orphaned bash tree (process-kill was my misattribution; per [process-batching] lesson, re-derived state before trusting). Clean retry → pass=100 fail=0. Not a code defect.
- Mid-Execution Guard note: diff = 220 ins/19 del > 200-line hard threshold. Attribution: 152 = new test file, 23 = compact-index regen, ~45 = semantic. Zero deviation from planned Target Files (creep = 0; the guard's trigger condition is "changes EXCEED classification scope"). Kept quick-win w/ feature-grade review per repo precedent (fix/downstream-sim-findings, fix/deploy-batch-hashing both larger). Surfaced to owner in ship summary for veto.

## Task Description
Downstream field report (agent-virtual-office @ v1.5.1, 2026-06-11) — real incident: agent ran
`rm -rf` on `.agentcortex-src/` cache without asking; partial failure on Windows left a `.git`-less
dir; subsequent git commands fell through to the PARENT repo and `remote set-url` + `fetch --force`
+ `checkout --force <foreign-tag>` clobbered the working tree. Recovered only via pre-task snapshot.

**Feature Inventory (multi-item input decomposition — user pre-selected ALL, item 1 priority):**
1. **[P0] Destructive-command rule drift** — README.md:99 (EN) + docs/README_zh-TW.md:133-138 (zh,
   stricter + longer list) advertise "Destructive Command Blocking" as part of the always-loaded
   constitution; VERIFIED absent from AGENTS.md, engineering_guardrails.md, security_guardrails.md.
   Only non-loaded mention: token-governance.md:153 (manual-only guide). Fix: one canonical rule on
   an always-loaded surface + demote both READMEs to pointers. Mind §13 Deletion-First/ADD-Gate +
   signal tier. Rollback plan must cover UNTRACKED/gitignored state (incident: git snapshot did not
   cover the cache dir).
2. **[P1] deploy_brain.* stale-cache remote mismatch** — VERIFIED installers/deploy_brain.sh:45-57:
   `if -d cache/.git → git pull` never compares `git -C cache remote get-url origin` vs resolved
   ACX_SOURCE/manifest `source_repo:`. Downstream pulled 457 commits of the WRONG repo. Fix in
   .sh/.ps1/.cmd + test.
3. **[P2] .gitattributes scaffold LF pin gap** — VERIFIED source .gitattributes has no rule for
   `.agentcortex-manifest` (extensionless → `* text=auto` → CRLF rewrite on Windows) nor
   `.githooks/**`. Deployed as scaffold tier via deploy.sh:816-817. Fix: pin `eol=lf` for both.

**Context Read Receipt**: SSoT (2026-06-11, seq 55) · Work Log created · Spec Scope: none mapped
(no existing spec covers READMEs/installers/.gitattributes) · Backlog read: 16 active, no overlap.

**Read Plan**: Quick guardrails mode. Reads done: bootstrap.md, SSoT, backlog inventory,
skill_conflict_matrix.md, validate.sh canary block (lines 915-970 — canary phrases NOT in target
sections; README edit safe). Planned conditional read: engineering_guardrails.md §13 only.
Skipped: full engineering_guardrails.md (Token Leak Block, quick-win), state_machine.md (flow known).

## Phase Sequence
- bootstrap
- plan
- implement
- review
- test
- ship

## External References
- Downstream field report (in-conversation, agent-virtual-office, 2026-06-11)
- ADR-005 (deploy tiering — adjacent domain; installers/deploy_brain.* not in its applies_to)
- Global Lesson [enforcement][HIGH]: MUST without enforcement = theatre → new rule needs signal tier
  (planned: T2 eval-backed via governance.yaml case + validator/test where feasible)

## Known Risk
- README zh/EN canary coupling: verified canary phrases ('governance-first layer...', '用工作流程、交付閘門與工程護欄') are OUTSIDE the sections being edited — no repoint needed.
- Always-loaded surface growth: §13 Deletion-First applies; the README demotion IS the cited deletion (net governance text shrinks at the doc layer).
- deploy_brain.cmd may lack git plumbing parity — verify before editing.

## Conflict Resolution
- karpathy-principles ↔ verification-before-completion: compatible per matrix (behavioral prompts vs procedural gates). No partial-conflicts in recommended set.

## Skill Notes
none

## Decisions
- D-1: Classification quick-win (not feature): no new spec planned (per classification-flow lesson — flow actually run = plan→implement→review→test→ship; no /handoff). Feature-grade review retained (governance + deploy surface).
- D-2: Label cluster advisory ('governance' label has 4+ pending items): declined — existing items (#67/#68/#69/#70) are unrelated topics; unifying spec would be artificial. Advisory noted per bootstrap §1.5.
- D-3: Rule surface = **AGENTS.md §Core Directives** (NOT engineering_guardrails.md as the report suggested). Incident test: the agent acted outside any phase / on a tiny-fix-class action — engineering_guardrails.md is structurally NOT loaded on quick-win/tiny-fix flows (Token Leak Block) nor out-of-phase; AGENTS.md is the only surface auto-injected every turn on all platforms (CLAUDE.md/GEMINI.md @import, Codex native). A rule in guardrails would have missed THIS incident again. security_guardrails.md rejected for the same reason (implement/review/ship-scoped).
- D-4: Canonical severity = merge of the three drifted texts: deny-by-default; before running, state blast radius + rollback plan **explicitly covering untracked/gitignored state** + user confirmation. Canonical command list lives ONLY in AGENTS.md; both READMEs demote to a 1-line summary + pointer (kills the EN/zh severity+list disagreement permanently).
- D-5: Signal tier **T2 eval-backed** (strongest feasible): AGENTS.md is inside the eval harness's governance files; a guarding case is added to `.agentcortex/eval/governance.yaml`. T1 infeasible — no validator/hook can intercept an agent's runtime shell commands framework-side.
- D-6: §13 Deletion-First net-add justification (1-line): real downstream data-loss incident; the rule was advertised in 2 READMEs but existed on no loaded surface; ~4 added lines guard a working-tree-destruction class. README zh §高風險指令 body trimmed in same change (net repo-wide governance text shrinks).
- D-7: Incident's second failure mode (partial rm → git fall-through to parent repo) gets BOTH a rule clause (stop + re-verify cwd/repo after a failed destructive step) AND a code guard in deploy_brain.sh (`remove_cache_or_die`: post-rm existence check → hard fail with manual-removal message, never proceed).

## Risks
- AGENTS.md is every platform's always-loaded prompt: a malformed edit degrades ALL sessions. Mitigation: ~4-line compact bullet, validate.sh+ps1 run, compact-index regen in same step.
- README canary coupling: canary phrases verified OUTSIDE edited sections (validate.sh:935-948); encoding checks must stay PASS after zh edit (UTF-8, no mojibake).
- deploy_brain.sh is the bootstrap entry for ALL downstream installs: origin-mismatch false-positive would force re-clones. Mitigation: URL normalization (trailing `/` + `.git`) + match-path test case; mismatch path is re-clone (safe, idempotent), never deploy-from-wrong-repo.
- .gitattributes new pins could renormalize tracked files. Mitigation: `git ls-files --eol .githooks/` pre-check; `.agentcortex-manifest` is untracked in source repo (forbidden-downstream list) → zero index impact.
- Rollback (all items): revert PR; no data migration, no manifest format change.

## External References
- Downstream field report (in-conversation, agent-virtual-office, 2026-06-11) | incident evidence + asks
- ADR-005 (deploy tiering) | adjacent domain; installers/* not in applies_to — no unfreeze needed
- engineering_guardrails.md §13 (heading-scoped read) | Deletion-First + ADD-Gate compliance for item 1
- `git remote get-url origin` / gitattributes `**` patterns | standard git, no external research needed

## Phase Summary
- bootstrap: classified quick-win (w/ feature-grade review); all 3 downstream claims independently verified against source; 3 skills matched, no conflicts; lock acquired; canary risk cleared.
- plan: 8 steps, 7 target files (AGENTS.md, governance.yaml, 2 READMEs, deploy_brain.sh, new test, .gitattributes) + compact-index regen; surface decision D-3 (AGENTS.md, not guardrails); T2 signal tier; Mode Normal | Confidence: 90% — assumption: governance.yaml case schema readable at implement (structure verified to exist, schema not yet read)
- implement: all 8 steps done, commit c2b2be3 (11 files: planned 8 + SSoT Last-Verified bump + 2 guard receipts — sanctioned bootstrap side-effects); pytest 3/3 new tests PASS; validate.sh + validate.ps1 pass=100 fail=0; eval coverage loads 24 cases incl. new one; .githooks re-smudged to LF; security quick-scan clean | Confidence: 95% — high
- review: PASS (fresh acx-reviewer, diff+AC only per Freshness Invariant) — 5/5 ACs PROVEN incl. mutation kill of origin check (gutted normalize → mismatch test FAILED with WRONG REPO deployed → restored clean); security clean; red team: no CRITICAL/HIGH, eval case weaponizes the incident's own rationalization; 1 MEDIUM ps1-`-Source`→origin-check disconnect VERIFIED real (per [audit-verification] lesson: re-read both files before fixing) and FIXED same-session (f20c7c4, --source peek + 4th test, 4/4 PASS); 1 LOW (double-slash normalize) accepted as informational; optional wording suggestion declined — §Context-Bound Confirmation already covers non-transferable approval (DELETE-bias)
- test: PASS — fast loop 263 passed (ci+guard, not-slow), new module 4/4, validators fail=0 both platforms; coverage delta deploy_brain bootstrap 0→4 tests; one environmental 255 retried clean (see Drift Log) | Confidence: 95% — high
- ship: PASS — PR #222 opened (closure: Open PR); commits c2b2be3 + f20c7c4; origin/main contained in branch (no sync conflict); archive .agentcortex/context/archive/fix-downstream-incident-findings-20260611.md; knowledge nudge: no docs/architecture/ L2 structure in this repo — skipped (capability-by-presence)

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T12:05:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T12:20:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T14:25:00+08:00
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T14:50:00+08:00
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T15:10:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T15:30:00+08:00

## Evidence
- Commit: c2b2be3 — 11 files changed, 220 insertions(+), 19 deletions(-)
- `python -m pytest tests/ci/test_deploy_brain_bootstrap.py` → **3 passed** in 3.42s (mismatch→re-clone w/ origin assert; match→pull path; trailing-slash normalization)
- `validate.sh` → `Summary: pass=100 warn=11 fail=0 skip=2` · `validate.ps1` → identical summary
- `run_governance_eval.py --coverage` → 24 cases evaluated (new destructive-command case loads; no schema error); `AGENTS.md §Core Directives` not in zero-coverage list
- `git ls-files --eol .githooks/` → `i/lf w/lf attr/text eol=lf` (no renormalization churn; manifest untracked in source repo → zero index impact)
- README canaries: encoding checks PASS in both validators post-edit
- **/test @ f20c7c4**: `pytest tests/ci tests/guard -m "not slow"` → **263 passed, 33 deselected** (36s) · new module `test_deploy_brain_bootstrap.py` → **4/4 passed** · `validate.sh` → pass=100 warn=10 fail=0 · `validate.ps1` → pass=100 warn=10 fail=0 · coverage delta: deploy_brain.sh bootstrap path 0 → 4 tests
