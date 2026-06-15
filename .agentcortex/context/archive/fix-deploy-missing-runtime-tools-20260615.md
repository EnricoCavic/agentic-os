# Work Log: fix/deploy-missing-runtime-tools

## Header

- Branch: `fix/deploy-missing-runtime-tools`
- Classification: `quick-win`
- Classified by: `claude-opus-4-8`
- Frozen: `2026-06-08`
- Created Date: `2026-06-08`
- Owner: `claude-opus-4-8 (luvseldom)`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `b704b23`
- Recommended Skills: `none`
- Primary Domain Snapshot: `deploy/runtime-tools`
- SSoT Sequence: `40`

---

## Session Info

- Agent: `claude-opus-4-8`
- Session: `2026-06-08 09:00 UTC`
- Platform: `claude-code`
- Files Read: `15`

---

## Task Description

Downstream simulation found a real regression: `deploy.sh`'s hardcoded runtime-tools whitelist omits two tools that deployed governance docs instruct downstream agents to run — `recover_worklog_lock.py` (bootstrap.md:284) and `lint_spec_drift.py` (review.md:21). Downstream non-tiny-fix bootstrap and spec-backed review hit `No such file`. Fix: add both tools to both whitelists in deploy.sh, and add a regression test codifying the invariant "every `.agentcortex/tools/*.py` referenced by deployed governance docs is deployed."

---

## Phase Sequence

| Phase | Status | Entered | Notes |
|---|---|---|---|
| bootstrap | done | 2026-06-08 | quick-win; verified+reproduced via downstream sim |
| plan | done | 2026-06-08 | deploy.sh 2 whitelists + 1 regression test |
| implement | done | 2026-06-08 | deploy.sh 2 whitelists + regression test |
| ship | done | 2026-06-08 | committed; PR; SSoT |

---

## Phase Summary

- **bootstrap**: Found via multi-angle downstream simulation (fresh sh + ps1 deploys into temp projects). Reproduced `python .agentcortex/tools/recover_worklog_lock.py ... → No such file or directory` in the deployed tree. Cross-checked deployed-governance-referenced tools vs deployed whitelist: exactly 2 missing (`recover_worklog_lock.py`, `lint_spec_drift.py`); the other 12 source-only tools are unreferenced framework/CI-internal, correctly excluded. Deps verified: `recover_worklog_lock` imports only the already-deployed `guard_context_write`; `lint_spec_drift` is stdlib-only.
- **plan**: Two edit points in `deploy.sh` — `_runtime_tools` string (update/migrate path, ~L444) and `runtime_tools=()` array (fresh-deploy path, ~L625). Both must list the 2 tools. Regression test added to `tests/ci/test_deploy_tiering.py`: deploy to temp, scan deployed governance docs for `.agentcortex/tools/*.py` refs, assert each exists in the deployed tree (catches any future drift, not just these 2).
- **implement**: Added `recover_worklog_lock.py` + `lint_spec_drift.py` to both whitelists; added `test_deployed_governance_referenced_tools_are_deployed`. Verified by re-simulation (fresh deploy → 12 tools, the previously-failing bootstrap command now returns `{"status":"created","exit_code":0}`, referenced-vs-deployed drift empty). `pytest tests/ci/test_deploy_tiering.py` → 13 passed. `validate.sh` → fail=0.

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T09:00:00Z
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T09:05:00Z
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T09:20:00Z
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T09:30:00Z

---

## External References

| Type | Path / URL | Notes |
|---|---|---|
| Spec | — | — |
| ADR | docs/adr/ADR-005-downstream-file-preservation-tiering.md | deploy tiering domain |
| Issue | — | — |
| PR | — | — |

---

## Known Risk

- Adding tools to the whitelist increases the deployed surface; both are referenced by deployed governance, so this is closing drift, not expanding scope. Low risk.

---

## Conflict Resolution

none

---

## Skill Notes

none

---

## Drift Log

- Ship SSoT write applied directly via Edit (Ship History entry + Update Sequence 40→41 + Last Updated), not via `guard_context_write.py` — guard section-targeting doesn't cover combined Ship-History-append + header-field update. Logged per AGENTS.md guard-fallback discipline.

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

## Evidence

- Repro (deployed tree): `python .agentcortex/tools/recover_worklog_lock.py ensure ... → C:\Python314\python.exe: can't open file '...recover_worklog_lock.py': [Errno 2] No such file or directory`.
- Referenced-vs-deployed diff: `comm -23 referenced deployed` → exactly `lint_spec_drift.py`, `recover_worklog_lock.py`.
- Source tools=22, deployed tools=10; 12 source-only, only these 2 referenced by deployed governance.
- Post-fix re-sim (fresh deploy): tools dir 10→12; `recover_worklog_lock.py ensure ...` → `{"status":"created","exit_code":0}` (was: No such file); `comm -23 referenced deployed` → empty.
- `python -m pytest tests/ci/test_deploy_tiering.py -q` → `13 passed in 440.75s` (12 prior + new regression test).
- `bash .agentcortex/bin/validate.sh` → `Summary: pass=101 warn=7 fail=0 skip=2`.

⚡ ACX
