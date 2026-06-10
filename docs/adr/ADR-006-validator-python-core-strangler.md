---
status: accepted
date: 2026-06-10
classification: architecture-change
applies_to:
  - ".agentcortex/bin/validate.sh"
  - ".agentcortex/bin/validate.ps1"
  - ".agentcortex/tools/*.py"
lifecycle:
  owner: framework
  review_cadence: on-event
  review_trigger: "next shipped validator parity defect, native-check count crossing the committed baseline, or a downstream no-python user reporting lost coverage"
---

# ADR-006: Validator Python-Core Strangler (new checks are Python tools)

## Status

Accepted (2026-06-10).

## Context

`validate.sh` (~2,465 lines) and `validate.ps1` (~2,291 lines) are hand-maintained twins. The parity tax is real and recurring: 6+ shipped parity defects in ~10 weeks (missing ps1 gate-receipt-schema check backfilled in #44/`55ed8ea`; column-index misalignment `2354c5f`; missing PASS branch `47102d2`; Measure-Object count bug `fcd30b6`; two rounds of parity-test platform-gating fixes `78d96bc`/`6f0d2d2`), with 52/45 commits of churn since 2026-03-01. Nearly every governance feature pays the cost twice.

**Attribution review corrections (2026-06-10, recorded so the rationale is honest):**
- `validate.ps1` exists for **Windows-native operation since the first public release** (`c1ced66`, pre-dating any performance measurement). An earlier analysis inferred a performance rationale (ps1 ~9.4s vs Git-Bash sh ~105s on Windows); the speed difference is real and worth keeping, but it is NOT why the twin exists and is not the basis of this decision.
- **Zero-Python-downstream is doctrine, not accident** (`aec35d6`; README "deploys and works without Python"; first-class `--no-python` flag; CI `deploy-no-python` job). Native shell checks are the guaranteed coverage floor on Python-less hosts; `run_python_check`/`Invoke-PythonCheck` are the deliberate, already-sanctioned exception boundary with graceful SKIP/WARN degradation (8-9 call sites today).

## Decision (one decision, per [adr-discipline])

**All NEW validator checks MUST be implemented as Python tools in `.agentcortex/tools/`, invoked through the existing `run_python_check` / `Invoke-PythonCheck` twin wrappers — unless the check must protect the no-python path, in which case a native check MAY be added with a recorded one-line justification and a baseline bump.**

Mechanics:
1. **Ratchet (machine enforcement, signal tier T1)**: `tests/ci/test_validator_native_check_ratchet.py` counts native result-emission call sites (line-leading `record_result` in validate.sh, `Add-Result` in validate.ps1, excluding the helper function bodies) against the committed baseline `tests/ci/validator_native_baseline.json`. Counts above baseline FAIL. Counts below baseline FAIL too ("stale baseline") so the baseline ratchets DOWN as checks migrate — the parity surface is monotonically non-increasing except through the justified path.
2. **Escape hatch (honors Zero-Python doctrine)**: bumping the baseline requires editing the JSON's `justifications` list with a one-line entry naming the check and why it must run without Python (mirrors §13 Deletion-First's net-add-justification pattern). The diff makes the exception visible to review; the ratchet test asserts every bump above the original 2026-06-10 floor has a justification entry.
3. **Opportunistic backfill**: when an existing native check is touched (bug, feature, parity defect), port it to a Python tool with fixture tests and delete it from BOTH shells. No big-bang rewrite — stable checks that never change pay no parity tax.
4. **No-python contract unchanged at adoption**: every check native today stays native until individually migrated; `--no-python` semantics and the `deploy-no-python` CI job are untouched by this ADR. Each migration decides explicitly whether the check may degrade to SKIP under `--no-python` (most may; checks protecting Python-less downstreams must not — they use the escape hatch to stay/become native).

## Consequences

- Adding a governance check becomes ~2 identical wrapper lines (one per shell) plus one Python tool with real unit tests — instead of two divergent shell implementations.
- Parity defects in NEW checks become structurally impossible at the logic level (one implementation); only the thin wrapper lines can diverge.
- Python-less downstream coverage is explicit and reviewable (baseline justifications) instead of implicit in 4,700 lines of twin shell.
- Risk: long-tail of never-migrated native checks — accepted; the tax is on churn, which the new-check policy eliminates. Risk: baseline file becomes ceremony — mitigated by it only changing when a native check is added/removed, which is rare by design.

## Rollback

Revert the PR (policy + ratchet test + baseline). No runtime behavior changes at adoption — validators are byte-identical the day this lands.
