# Work Log: feat-deletion-first-add-gate

## Header

- Branch: `feat/deletion-first-add-gate`
- Classification: `feature`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Full`
- Current Phase: `test`
- Checkpoint SHA: `ccb0294`
- Recommended Skills: `verification-before-completion (auto), red-team-adversarial (auto — feature→Full at /review), karpathy-principles (auto), test-driven-development (auto — validator checks testable)`
- Primary Domain Snapshot: `governance`
- SSoT Sequence: `47`

---

## Session Info

- Agent: Claude (Fable 5)
- Session: 2026-06-10 (continuation turn; guardrails core cached from session start per Read-Once)
- Platform: Claude Code (Windows)
- Guardrails loaded: §1, §2, §4, §7, §8.1, §10 (core), cached
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO

---

## Task Description

- Backlog #65 / GH issue #166 (P1, feature, dep #45 ✓ shipped): (1) Deletion-First Norm — governance-doc change must cite a deletion or justify net-add in one line; (2) ADD-gate signal tiering — new governance rules declare a signal tier + measurable check or named consumer. Advisory enforcement (review AC + validator WARN); existing rules grandfathered.
- USER CONSTRAINTS (binding design criteria): (a) verify it's a real problem — done, see Evidence; (b) expert roundtable on uncertainty; (c) **do NOT make the AI dumber (no instruction-load growth in every-turn context) and do NOT make the process heavier (no new hard gates; advisory only; ~zero cost for tiny-fix/quick-win flows)**.
- Real-problem verification: [enforcement][HIGH] Global Lesson (unenforced MUST = theatre → delete); [governance-proposal][MEDIUM] lesson; issue-curation history 25→17 (DELETE-bias); #151 close→reopen cycle; this week's vacuous verify_agent_evidence drop; measured instruction load ~90 MUST/NEVER directives / ~9.4k tokens at phase entry (2026-06-03, issue #166 comment) vs external ~150–200 consistency-loss threshold. Recurring failure mode = careless ADD without verified problem/consumer. REAL.
- Strand D correction (research spec `_research-rpi-qrspi-corroboration.md`): naive count thresholds explicitly rejected ("not count < 85"); active risks = burial depth, single-file density, MUSTs lacking validators. The "MUSTs lacking validators" measure ALREADY EXISTS (#45 eval coverage WARN) → planned directive-counter tool DELETED from design (dogfooding DELETE-bias).
- ADR coverage: covered_by ADR-001 (governance-friction-tuning domain) — rides existing ADR; no boundary/data-flow change → feature, not architecture-change.
- Full phase chain: /spec → /plan → /implement → /review → /test → /handoff → /ship

## Phase Sequence

- bootstrap
- spec (docs/specs/deletion-first-add-gate.md, frozen, signal_tier: 2 self-applied)
- plan
- implement

## Plan

- Design via expert roundtable (Plan subagent) — verdicts adopted: §13 conditional NOT core; 3 tiers not 4 (external citation = metadata); bootstrap quick-win reachability hook (2 lines) closes the Token-Leak-Block dead zone; validator detector = substring "governance" + created≥2026-06-10 + `signal_tier: none` escape; spec-app-feature template NOT touched (downstream APP export); Deletion-First scope = 3 always-loaded surfaces only; ADD-gate covers all .agent/** for NEW rules.
- Target Files: engineering_guardrails.md (§13 + conditional-list line + 2 dogfood deletions) · bootstrap.md (hook + exemption) · review.md (1 advisory bullet) · governance.yaml (+1 case protecting §13) · validate.sh+ps1 (signal_tier WARN, delegated to Sonnet) · tests/guard/test_signal_tier_check.py (delegated) · spec (self-applying frontmatter).
- Deletion-First compliance of THIS change (dogfood): deleted §5.3 duplicate scope bullet (strict restatement of the Gate-FAIL bullet above it; grep-verified no machine consumer) + deleted the stale Token-budget-estimate header block (meta-commentary; counts invalidated by this very change).
- Defect caught mid-implement: the conditional-list trigger line's literal "MUST/NEVER/gate" made §Heading-Scoped Read falsely MUST-bearing in the eval inventory (+1 phantom anchor) — reworded to "imperative rule or gate"; inventory back to 52 (51+§13 only).
- Confidence: 90% — roundtable-reviewed design; remaining risk = validator parity mechanics (delegated with fixture verification).
- Rollback plan: revert merge commit of this branch's PR.

## External References

- GH issue #166 (+ measured-load comment); backlog #65
- docs/specs/_research-rpi-qrspi-corroboration.md (Strand D/E + external sources: Horthy/QRSPI, ace-fca)
- Shipped consumer this design ties into: .agentcortex/eval/governance.yaml coverage WARN (#45)
- ADR-001 (covering ADR)

## Known Risk

- Self-referential bloat risk: an anti-bloat gate that adds friction IS the failure mode it fights. Mitigations: norm lives ONLY in engineering_guardrails (Full-mode read; zero cost to tiny-fix/quick-win); all checks advisory WARN; AGENTS.md untouched (no every-turn token growth); section budget ~15 lines.
- Rollback plan: revert PR.

## Conflict Resolution

none

## Skill Notes

none

## Phase Summary

- bootstrap: feature classified; real-problem verified with 6 evidence points; Strand D correction applied (no naive count gate; counter tool deleted from design pre-birth). ⚡ ACX
- plan: roundtable verdicts adopted (conditional §13, 3 tiers, reachability hook, detector fix, template untouched); Confidence: 90%. ⚡ ACX
- implement: ccb0294 — §13 + 2 dogfood deletions + bootstrap hook + review bullet + eval case (phantom-anchor defect caught & fixed mid-implement) + validators/test (delegated, independently verified). ⚡ ACX
- review: R1 PASS — 9/9 ACs, bloat audit net −5 always-loaded lines, zero theatre paths; 1 LOW advisory (documented boundary). ⚡ ACX
- test: 456 passed full set incl. legacy; validators parity (sole FAIL = pre-ship Spec Index). ⚡ ACX
- handoff: Resume + Read Map/Skip List/Snapshot written; closure = Open PR, merge on green. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T08:30:00+08:00
- Gate: plan | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T08:50:00+08:00
- Gate: implement | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T14:35:00+08:00
- Gate: review | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T14:50:00+08:00
- Gate: test | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T15:20:00+08:00
- Gate: handoff | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T15:25:00+08:00

## Evidence

- `python -m pytest tests/ci tests/guard .agentcortex/tests -q` → 456 passed (Ref: §Test Gate Results).
- `python -m pytest tests/guard/test_signal_tier_check.py tests/guard/test_governance_eval.py -q` → 33 passed (independent re-run of delegated work).
- Eval inventory clean: 52 sections (51 + §13 only; phantom Heading-Scoped-Read anchor caught and fixed); §13 guarded (zero-coverage 45→44).
- Reviewer live evidence: body-tier validator bypass attempt correctly WARNs; net always-loaded delta −5 lines; all 3 reachability paths verified.
- Commits: ccb0294.

## Observability

- Governance-doc + advisory validator change; surfaces via validate.sh/ps1 WARN/PASS lines on every run — no production log sink applicable (framework governance, not service code).

## Test Gate Results

- Final (@ccb0294): `python -m pytest tests/ci tests/guard .agentcortex/tests -q` → **456 passed** in 1030s (mirrors the full CI gate set incl. legacy suite).
- `bash validate.sh` → pass=100 warn=10 fail=1; `validate.ps1` → pass=100 warn=9 fail=1 — sole FAIL = Spec Index completeness (this spec; resolved at ship); new `signal_tier` check PASS wording identical in both.
- Eval case live-scored both directions (refusal transcript → PASS; compliance transcript → FAIL exit 1).

## Resume

- State: TESTED → HANDEDOFF (pending ship)
- Completed: roundtable design → spec (frozen, signal_tier:2 self-applied) → plan → implement (ccb0294; validators+test delegated then independently verified) → review R1 PASS (net −5 always-loaded lines) → test 456 passed
- Next: /ship — Spec Index entry + Ship History (Seq 48), archive log, backlog #65 → Shipped, PR (closes #166)
- Blocker: none

### Read Map

- docs/specs/deletion-first-add-gate.md — AC-1..9, Enforcement Boundary, Domain Decisions (tier rationale)
- .agent/rules/engineering_guardrails.md §13 — the norm itself (conditional)
- .agentcortex/bin/validate.sh ~2405 / validate.ps1 ~2223 — signal_tier WARN blocks

### Skip List

- spec-app-feature template (deliberately untouched — downstream APP export)
- _research-rpi-qrspi-corroboration.md (consumed at design; Strand D verdict already applied)

### Context Snapshot

- Branch feat/deletion-first-add-gate @ ccb0294 (1 commit ahead of main 10c4d98)
- Follow-up recorded in spec: Loaded-Sections Receipt = first run_delete_bias_diff.sh candidate

### Backlog Status

- #65 In Progress → flips Shipped at ship; #69 (RPI→QRSPI) becomes fully unblocked (deps #45 ✓ #65 ✓)

## Review Feedback

- R1 (red-team Full): **PASS** — AC-1..9 all PROVEN. Bloat self-audit: net always-loaded delta = **−5 lines** (AGENTS.md + shared-contracts untouched; conditional §13 only; 2 dogfood deletions). Reachability: all 3 paths (Full conditional / quick-win hook+exemption / review bullet) load §13 — zero theatre. Validator parity exact incl. body-tier bypass attempt (correctly WARNs), CRLF, no-frontmatter, `_*` skip. 1 LOW advisory: eval case paraphrase-brittle ("I'll note the tier later, appending now" could false-pass) — documented Enforcement Boundary, no fix required.

## Security Findings

- none. (Governance-doc + WARN-only validator change; no injection/auth surface; reviewer security pass clean.)
