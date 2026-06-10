# Work Log: fix-eval-coverage-accuracy

## Header

- Branch: `fix/eval-coverage-accuracy`
- Classification: `quick-win`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `967cf2e`
- Recommended Skills: `verification-before-completion (auto)`
- Primary Domain Snapshot: `none`
- SSoT Sequence: `49`

---

## Session Info

- Agent: Claude (Fable 5)
- Session: 2026-06-10
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win)
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO

---

## Task Description

- E3 expert-analysis follow-up (strict self-assessment queue, user-directed verify-then-fix). The "44/51 MUST sections zero-coverage" number overstated the real gap ~3x. Root causes verified: (1) `_extract_rule_inventory` counted a parent `##` section whenever a MUST appeared anywhere in its body INCLUDING `###` children, then counted the children again (~9 phantom anchors); (2) the WARN wording implied all 44 were uncovered behavioral gaps, but the set mixes T1 machine-enforced and T3 principle-tier rules.
- Expert option analysis adopted (c): pure-logic counter fix + honest wording. Rejected (a) heuristic T1 auto-detection (would count doc-presence literals as enforcement — vacuous-wiring failure mode) and (b) t1_backed allowlist (registry whose drift is invisible; freshness grep can't verify semantic claims).
- Plus Deliverable C: 8 new high-value adversarial cases for genuinely-unbacked behavioral rules (Confidence Gate, 2-Strike, auth quick-win escalation, Design-First, Anti-Rationalization, unresolved-HIGH ship pressure, vague-input clarification, skill-as-phase-bypass).

## Plan

- run_governance_eval.py: inventory = own-text MUST only (heading line to next heading of ANY level).
- governance.yaml: remap 2 cases whose parent anchor lost own-text MUST (worklog-lock-ssot-integrity → AGENTS §vNext State Model [Write Isolation is the violated rule]; lock-takeover → AGENTS §Core Directives/No Bypass Rule [unapproved takeover = gate bypass]); +8 new cases.
- validate.sh/ps1: WARN wording → "without eval cases (tier-blind: includes machine-enforced and principle-tier rules; see guardrails s13)".
- Rollback: revert PR. Confidence: 92%.

## Phase Sequence

- bootstrap
- plan
- implement
- ship

## External References

- E3 expert analysis (session subagent, 2026-06-10); option (b) rejection rationale = verify_agent_evidence vacuous-wiring precedent
- Deferred (recorded, NOT shipped): E3's delete-bias nominees (§6 Explainability, Loaded-Sections Receipt, §12.5, §1.2 fromRecord bullet, §References MUST) — need measured run_delete_bias_diff.sh evidence first

## Known Risk

- none material; tool logic change is test-covered; eval cases are data. Rollback = revert PR.

## Conflict Resolution

none

## Skill Notes

none

## Phase Summary

- bootstrap: E3 verdicts verified against code (double-count reproduced; 9 phantom anchors confirmed via before/after inventory diff 53→44... measured 51→44 hmm see Evidence). ⚡ ACX
- implement: counter fix + 2 remaps + 8 cases + honest wording; live-scored samples both directions (caught and fixed a full-width-？ vs ASCII-? expect bug in the vague-input case). ⚡ ACX
- ship: 31 schema tests green; validators fail=0; coverage now honest 29/44. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T19:10:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T19:12:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T19:40:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-10T19:50:00+08:00

## Evidence

- Inventory: 51 → 44 sections (7 phantom parent anchors removed by own-text rule; E3 estimated ~9 incl. 2 keyword false-positives that legitimately remain — §References and SEC §Scope have MUST in own text).
- Cases 15 → 23; zero-coverage 44 → 29 (honest count). `pytest tests/guard/test_governance_eval.py` → 31 passed.
- Live-scoring: vague-input PASS on zh clarification / FAIL on action-taken; confidence-gate PASS on stop-and-ask. Full-width-？ expect bug caught by live-scoring and fixed.
- `bash validate.sh` → pass=101 warn=9 fail=0 (new wording live); ps1 parity run pre-PR.
