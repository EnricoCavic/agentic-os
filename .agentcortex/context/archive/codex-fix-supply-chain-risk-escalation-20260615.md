# Work Log: codex-fix-supply-chain-risk-escalation

## Header

- Branch: `codex/fix-supply-chain-risk-escalation`
- Classification: `hotfix`
- Classified by: `Codex`
- Frozen: `2026-06-12`
- Created Date: `2026-06-12`
- Owner: `codex`
- Guardrails Mode: `Full`
- Current Phase: `test`
- Checkpoint SHA: `94d9056`
- Recommended Skills: `red-team-adversarial`, `systematic-debugging`, `verification-before-completion`
- Primary Domain Snapshot: `governance`
- SSoT Sequence: `61`

---

## Session Info

- Agent: `Codex`
- Session: `2026-06-12T12:00:00+08:00`
- Platform: `Codex App`
- Guardrails loaded: `AGENTS.md supplied by user; current_state.md; shared-contracts.md`
- Override: `none`

---

## Task Description

Fix the governance classification gap that lets downstream installer/updater/source-provenance trust-boundary changes remain quick-win and legally skip review/test/adversarial coverage.

---

## Phase Sequence

| Phase | Status | Entered | Notes |
|---|---|---|---|
| bootstrap | completed | 2026-06-12 | Classified as hotfix because the issue affects downstream trust-boundary governance. |
| plan | completed | 2026-06-12 | Narrow rule + enforcement tests; preserve normal quick-win fast path. |
| implement | completed | 2026-06-12 | Fixed review finding on bootstrap first-match ordering. |
| review | completed | 2026-06-12 | PASS after first-match ordering fix. |
| test | completed | 2026-06-12 | Guard suite and validators pass. |
| handoff | skipped | - | Hotfix exempt. |
| ship | pending | - | - |

---

## Phase Summary

- bootstrap: hotfix — same-vendor expert panel found a real process gap, but agreed the fix should be narrow and not enable red-team for all quick-wins.
- plan: target `engineering_guardrails.md` and `state_machine.md` classification text, plus guard/eval tests; avoid changing quick-win global phase order or red-team matrix.
- implement: added a narrow `Supply-Chain / Provenance Escalation` rule to guardrails, bootstrap, state machine, and eval/tests.
- review: NOT READY — independent reviewer found bootstrap first-match table could classify mixed governance+provenance changes as quick-win before reaching the hotfix row.
- implement: moved the hotfix pre-classification row above all quick-win rows and added ordering coverage.
- review: PASS — prior HIGH bypass is closed by first-match ordering test.
- test: PASS — guard suite 53 passed; bash and PowerShell validators fail=0.
- review: PASS after second-angle review — fixed docs-only carve-out drift and strengthened tests for row order, state-machine hotfix semantics, and eval downgrade phrases.
- test: PASS — broader governance/deploy suites, no-python validator, deploy tiering, and eval positive/negative transcripts passed.

---

## Gate Evidence

- Gate: plan | Verdict: PASS | Classification: hotfix | Timestamp: 2026-06-12T12:00:00+08:00
- Gate: implement | Verdict: PASS | Classification: hotfix | Timestamp: 2026-06-12T15:10:00+08:00
- Gate: review | Verdict: NOT READY | Classification: hotfix | Timestamp: 2026-06-12T15:16:33+08:00
- Gate: implement | Verdict: PASS | Classification: hotfix | Timestamp: 2026-06-12T15:24:00+08:00
- Gate: review | Verdict: PASS | Classification: hotfix | Timestamp: 2026-06-12T15:25:00+08:00
- Gate: test | Verdict: PASS | Classification: hotfix | Timestamp: 2026-06-12T15:25:00+08:00

---

## External References

| Type | Path / URL | Notes |
|---|---|---|
| Spec | - | Hotfix; no new spec planned. |
| ADR | `docs/adr/ADR-001-governance-friction-tuning.md` | Preserves quick-win friction-tuning intent. |

---

## Known Risk

- Root Cause: quick-win classification was optimized for token/phase cost, but lacked a narrow hazard trigger for downstream source provenance and installer trust-boundary changes.
- Rollback: revert this branch; existing quick-win behavior returns unchanged.

---

## Conflict Resolution

- Preserve quick-win low-friction design.
- Do not run Full Red Team for all quick-wins.
- Add a narrow escalation trigger for installer/updater/source/cache/provenance trust-boundary changes.

---

## Skill Notes

### red-team-adversarial
- Checklist: confirm attacker path through source selection, cache origin, manifest provenance, remote fetch/update, or downstream installer execution.
- Checklist: require concrete file/path trigger, not broad "deploy" keyword matching.
- Constraint: avoid full red-team for ordinary quick-wins; the fix is classification escalation.

### systematic-debugging
- Checklist: distinguish intended fast-path design from missing risk trigger.
- Checklist: verify with archive examples and tests, not inference alone.
- Constraint: no speculative broad refactor of phase model.

### verification-before-completion
- Checklist: scope, quality, evidence, risk, communication.
- Checklist: all new MUST language needs a guarding test/eval.
- Constraint: do not claim completion without passing focused tests and validators.

---

## Drift Log

- Phase entry: `/plan` hotfix; lock acquired for `codex-fix-supply-chain-risk-escalation`.
- Phase entry: `/implement`; lock refreshed.
- Phase entry: `/review`; lock refreshed.
- Phase entry: `/implement`; lock refreshed after review NOT READY.
- ADD-Gate: new MUST is T1 guarded by `tests/guard/test_classification_escalation.py` and T2 guarded by `.agentcortex/eval/governance.yaml`.
- Deletion-First: net-add justified because this closes a downstream trust-boundary classification gap; no lower-cost deletion preserves the same protection.
- Recovered stale Work Log lock on 2026-06-12T08:52:16.404300+00:00; prior_owner=codex; prior_session=2026-06-12T12:00:00+08:00; reason=stale-time; lock=codex-fix-supply-chain-risk-escalation.lock.json

---

## Design Reference

none

---

## Observability

none

---

## Resume

none

---

## Security Findings

none yet

---

## Evidence

- Expert synthesis: four same-vendor subagents agreed not to globally enable quick-win red-team; three recommended a narrow supply-chain/provenance escalation, one framed the original claim as overbroad but still supported the narrow classification/control fix.
- Plan: add a `Supply-Chain / Provenance Escalation` quick-win rule requiring at least `hotfix` for installer/updater/source resolver/cache origin/manifest provenance/remote fetch changes; guard it with `tests/guard/test_classification_escalation.py` and `.agentcortex/eval/governance.yaml`.
- Red test: `python -m pytest tests/guard/test_classification_escalation.py::ClassificationEscalationContractTests::test_supply_chain_provenance_escalation_rule_present -q` -> failed before rule text existed.
- Focused tests: `python -m pytest tests/guard/test_classification_escalation.py::ClassificationEscalationContractTests::test_supply_chain_provenance_escalation_rule_present -q` -> 1 passed.
- Guard/eval/state-machine suite: `python -m pytest tests/guard/test_classification_escalation.py tests/guard/test_state_machine_contract.py tests/guard/test_governance_eval.py -q` -> 53 passed.
- Validators after EOL normalization: `validate.sh` -> pass=100 warn=10 fail=0 skip=2; `validate.ps1` -> pass=100 warn=10 fail=0 skip=2.
- Review finding: HIGH bootstrap first-match bypass; moved the supply-chain/provenance hotfix row above quick-win rows and added row-order coverage.
- Review finding: MEDIUM eval polarity weakness; tightened the deploy-provenance eval with explicit anti-downgrade forbids and a stronger must/escalation regex.
- Validator finding: Work Log needed explicit implement PASS receipts around the NOT READY review edge; receipts added.
- Re-test after review fix: `python -m pytest tests/guard/test_classification_escalation.py::ClassificationEscalationContractTests::test_supply_chain_provenance_escalation_rule_present -q` -> 1 passed.
- Re-test guard/eval/state-machine suite: `python -m pytest tests/guard/test_classification_escalation.py tests/guard/test_state_machine_contract.py tests/guard/test_governance_eval.py -q` -> 53 passed.
- Re-test validators: `validate.sh` -> pass=100 warn=10 fail=0 skip=2; `validate.ps1` -> pass=100 warn=10 fail=0 skip=2.
- Second-angle tests: `python -m pytest tests/guard/test_classification_escalation.py tests/guard/test_state_machine_contract.py tests/guard/test_governance_eval.py tests/ci/test_deploy_brain_bootstrap.py -q` -> 57 passed.
- Downstream deploy tiering: `python -m pytest tests/ci/test_deploy_tiering.py -q` -> 21 passed.
- No-python validator: `validate.sh --no-python` -> pass=91 warn=7 fail=0 skip=14.
- Eval polarity smoke: positive deploy-provenance transcript PASS; negative `remain quick-win / review not needed / tests optional` transcript FAIL.
- Final validators after test strengthening: `validate.sh` -> pass=100 warn=11 fail=0 skip=2; `validate.ps1` -> pass=100 warn=11 fail=0 skip=2.
