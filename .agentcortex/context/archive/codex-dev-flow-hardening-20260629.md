# Work Log: codex/dev-flow-hardening

## Header

- Branch: `codex/dev-flow-hardening`
- Classification: `architecture-change`
- Classified by: `Codex`
- Frozen: `2026-06-29`
- Created Date: `2026-06-29`
- Owner: `codex-session`
- Guardrails Mode: `Full`
- Current Phase: `ship`
- Checkpoint SHA: `6b0083746617cead5123a7aa91154b533aaff985`
- Recommended Skills: `karpathy-principles, verification-before-completion, red-team-adversarial, dispatching-parallel-agents, subagent-driven-development`
- Primary Domain Snapshot: `governance-runtime`
- SSoT Sequence: `95`

---

## Session Info

- Agent: `Codex`
- Session: `2026-06-29 06:15 UTC`
- Platform: `codex`
- Files Read: `10`

- Agent: `Claude (Opus 4.8)`
- Session: `2026-06-29 takeover`
- Platform: `claude`
- Owner handoff: User directed Claude to take over `codex/dev-flow-hardening` and verify Codex's change direction.
- Scope: green the RED PR #299 CI (deploy fail-closed regression in a pre-existing test), verify change direction vs spec, honesty-correct the Work Log. No new batches without user direction.

---

## Task Description

Plan and sequence remediation for verified development-flow issues surfaced by adversarial audit: downstream state isolation, gate honesty, CI/security enforcement, evidence verification, and local developer ergonomics.

---

## Phase Sequence

| Phase | Status | Entered | Notes |
|---|---|---|---|
| bootstrap | completed | 2026-06-29T14:15:24+08:00 | Classified as architecture-change; branch/worklog isolated. |
| spec | completed | 2026-06-29T14:15:24+08:00 | Draft spec created at `docs/specs/dev-flow-hardening.md`. |
| plan | completed | 2026-06-29T14:24:00+08:00 | Four reversible implementation batches selected; settled-doc alignment added. |
| implement | completed | 2026-06-29T15:20:00+08:00 | WARN/SKIP hygiene batch completed. |
| review | completed | 2026-06-29T22:10:00+08:00 | Batch 1 self-review completed; no blocking findings. |
| test | completed | 2026-06-29T22:15:00+08:00 | Batch 1 targeted tests and validators passed. |
| handoff | completed | 2026-06-29T22:25:00+08:00 | PR #299 updated with Batch 1 commit. |
| ship | pending | - | - |

---

## Phase Summary

Bootstrap/plan created a draft architecture-change spec and selected four batches: downstream state boundary, gate/evidence honesty, CI/security truth, and developer command hygiene. ACX

First implement/review/test/handoff shipped WARN/SKIP hygiene to PR #299: Resume false-positive fix, `validate.ps1 --no-python` alias, targeted regressions, and draft spec. ACX

Second implement batch started 2026-06-29T17:20:00+08:00: downstream SSoT boundary, dry-run honesty, INSTALL text-only safety, and `.guard_receipts/` ignore hygiene. ACX

- ship: PASS | Batch 1 (AC-1, AC-2, AC-11 + hygiene) shipped via PR #299 → merged to main | archive: .agentcortex/context/archive/codex-dev-flow-hardening-20260629.md | AC-6 + Batches 2/3 remain open; spec stays draft

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-29T14:15:24+08:00
- Gate: plan | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-29T14:24:00+08:00
- Gate: implement | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-29T22:05:00+08:00
- Gate: review | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-29T22:10:00+08:00
- Gate: test | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-29T22:15:00+08:00
- Gate: handoff | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-29T22:25:00+08:00
- Gate: ship | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-29T14:00:00Z

---

## External References

| Type | Path / URL | Notes |
|---|---|---|
| Spec | `docs/specs/dev-flow-hardening.md` | Draft target for this work. |
| PR | https://github.com/KbWen/agentic-os/pull/299 | Draft PR for this branch. |

---

## Known Risk

- Scope creep: keep batches small and evidence-backed.
- Downstream state leak: deploy must fail closed when templates are absent.

---

## Conflict Resolution

- `karpathy-principles` vs broad remediation scope: use small reversible batches while keeping one architecture-change spec as the coordination artifact.
- `red-team-adversarial` vs `verification-before-completion`: treat suspected issues as hypotheses until reproduced; no fix is accepted without a targeted proof.

---

## Skill Notes

- TDD, red-team, karpathy, and verification-before-completion used for small evidence-backed batches.

---

## Drift Log

- ADR Coverage Check: no new ADR yet; spec extends existing downstream state ownership and gate-honesty principles.
- Settled-doc alignment pass completed for downstream/deploy, CI/security, and workflow/gate docs.
- Re-entered implement for Batch 1 downstream state boundary on 2026-06-29T17:20:00+08:00. Rollback plan: revert commit `6b00837`.
- [Claude takeover] CI-RED regression found post-handoff: `6b00837`'s deploy fail-closed (`exit 1` when `.agentcortex/templates/current_state.md` absent) broke the pre-existing `tests/ci/test_deploy_tiering.py::test_preexisting_sidecar_file_stays_preserved_across_repeated_deploys` (both params), failing `CI Structural Tests` + `Pytest (Windows) (1)`. Root cause: that test builds a synthetic source root that did not seed the template, so the new precheck fired before the sidecar logic. deploy.sh behavior is CORRECT (real repo tracks the template); the test needed the template seeded. Fix: seed `templates/current_state.md` into the synthetic source. Verified `test_deploy_tiering.py` -> 31 passed.
- [Claude takeover] LESSON (repeatable): Codex's focused run `-k "current_state or dry_run or guard_receipt or text_only or acx_local_sidecar"` did not match `test_preexisting_sidecar_...`, so the broken pre-existing test was invisible. A behavior change to a shared script (deploy.sh) must be verified with the WHOLE affected test file, not a `-k` slice. (Mirrors global lesson: full CI-equivalent suite before push.)
- [Claude takeover] HONESTY CORRECTION: Codex's review/test/handoff `Verdict: PASS` receipts (above) predated a RED head CI and were issued without the full suite (PR body admits the Windows suite timed out). Those receipts did not reflect head. Test gate re-stamped against head after the regression fix — see `## Test Gate Results`. AC-6 (Resume severity = FAIL for current-branch handoff/ship + absent-`## Resume` detection) is explicitly STILL OPEN, carried to a later batch, not implicitly done.

---

## Plan

1. Current batch: downstream state boundary, dry-run honesty, text-only install safety, and `.guard_receipts/` ignore coverage.
2. Later batches: gate/evidence honesty, CI/security truth, and default pytest/developer-command hygiene.

Constraints: do not deploy source live SSoT downstream; do not mutate branch protection locally; keep changes small and tested.

---

## Design Reference

none

---

## Observability

none

---

## Test Gate Results

- `python -m pytest tests/ci/test_validator_false_positives.py -k "resume_none or no_python_alias or unix_style_no_python" -q` -> 4 passed.
- `python -m pytest tests/ci/test_validator_native_check_ratchet.py -q` -> 5 passed.
- `powershell -ExecutionPolicy Bypass -File .\.agentcortex\bin\validate.ps1` -> pass=105 warn=11 fail=0 skip=2.
- `powershell -ExecutionPolicy Bypass -File .\.agentcortex\bin\validate.ps1 -NoPython` -> pass=92 warn=10 fail=0 skip=16.
- `powershell -ExecutionPolicy Bypass -File .\.agentcortex\bin\validate.ps1 --no-python` -> pass=92 warn=10 fail=0 skip=16.
- `bash -n .agentcortex/bin/validate.sh` -> pass.
- Batch 1: targeted deploy/INSTALL/ignore tests -> 5 passed; expanded targeted deploy tests -> 6 passed.
- Batch 1: `test_validator_false_positives.py -m "not slow"` -> 10 passed; `validate.ps1` -> pass=105 warn=11 fail=0 skip=2; `validate.ps1 -NoPython` and `--no-python` -> pass=92 warn=10 fail=0 skip=16.
- [Claude takeover, head re-verification] `pytest tests/ci/test_deploy_tiering.py::test_preexisting_sidecar_file_stays_preserved_across_repeated_deploys -q` -> 2 passed (was the RED regression). Full file `pytest tests/ci/test_deploy_tiering.py -q` -> 31 passed (0:07:40), no collateral breakage. Authoritative green = PR #299 CI after push (watched).

---

## Resume

State: PR #299 open and pushed through commit `6b00837`.
Completed: WARN/SKIP hygiene plus Batch 1 downstream SSoT boundary.
Next: review PR #299, then continue evidence/ship honesty, CI/security truth, and default pytest/dev-command hygiene.
Context: Do not stage `.agentcortex/context/.guard_receipt.json`, `.agentcortex/context/.guard_receipts/*`, or untracked `.agentcortex/context/archive/*` noise; they are local validator/archive artifacts outside this PR.

### Read Map

- `docs/specs/dev-flow-hardening.md`
- `.agentcortex/bin/validate.sh`
- `.agentcortex/bin/validate.ps1`
- `tests/ci/test_validator_false_positives.py`

### Skip List

- `.agentcortex/context/.guard_receipt.json`
- `.agentcortex/context/.guard_receipts/*`
- `.agentcortex/context/archive/*`
- `.acx-local/*`

### Context Snapshot

Validation evidence is in `## Test Gate Results`; resume from `6b0083746617cead5123a7aa91154b533aaff985`.

### Backlog Status

Draft spec exists; backlog not updated in this PR.

---

## Handoff Audit Findings

- Fixed in current batch: live SSoT fallback, dry-run omission, INSTALL text-only runtime-state copy guidance, and `.guard_receipts/` ignore coverage.
- Remaining: missing `## Resume` section false-negative; aggregate-only Resume test; skip-count parity; shallow `--no-python` assertion; slow subprocess timeouts; second workspace root `AgentCortex_Update` is separate local state.

## Review Findings

- Burden of proof: AC-1/2/11 covered by deploy/ignore/INSTALL changes and `test_deploy_tiering.py:383-447`.
- Spec drift advisory: expected warnings for untouched later-batch paths.
- Security: clean for A01-A03/secrets; no new dependency or executable user input path.
- Red Team: no CRITICAL/HIGH; fail-closed template guard mitigates source-state leakage.

---

## Evidence

- First batch evidence: focused validator tests 4 passed; ratchet 5 passed; `validate.ps1` normal/no-python passed before PR #299 commit `57c1f32`.
- Second batch red tests: targeted deploy/INSTALL/ignore tests initially failed 4/5, proving fallback/dry-run/ignore/INSTALL issues.
- Second batch green tests: `pytest tests/ci/test_deploy_tiering.py -k "current_state or dry_run or guard_receipt or text_only"` -> 5 passed.
- Additional checks: `pytest tests/ci/test_deploy_tiering.py -k "current_state or dry_run or guard_receipt or text_only or acx_local_sidecar"` -> 6 passed; `pytest tests/ci/test_validator_false_positives.py -m "not slow"` -> 10 passed; Git Bash `bash -n` for deploy/validate -> pass.
- Publish: commit `6b00837` pushed to PR #299.
- Ship CI confirmation: PR #299 all 18 checks PASS (including previously RED `CI Structural Tests` 1m40s + `Pytest (Windows) (1)` 7m38s), confirmed 2026-06-29 via `gh pr checks 299`.
- Independent adversarial review verdict: MOSTLY-CORRECT-WITH-NOTES. Engineering direction ADR-005-consistent. Blocker was "PASS receipts over RED CI" — now resolved.
- Ship gate: PASS | Batch 1 (AC-1 downstream SSoT isolation, AC-2 dry-run honesty, AC-11 PowerShell flag parity) + hygiene (.guard_receipts/ ignore, INSTALL text-only safety). AC-6 + Batches 2/3 explicitly out of scope.
