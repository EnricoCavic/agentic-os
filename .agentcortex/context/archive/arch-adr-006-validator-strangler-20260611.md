# Work Log: arch-adr-006-validator-strangler

## Header

- Branch: `arch/adr-006-validator-strangler`
- Classification: `architecture-change`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Full`
- Current Phase: `ship`
- Checkpoint SHA: `c87d50a`
- Recommended Skills: `verification-before-completion (auto), red-team-adversarial (auto — arch→Full+Beast), karpathy-principles (auto), test-driven-development (auto)`
- Primary Domain Snapshot: `governance`
- SSoT Sequence: `50`

---

## Session Info

- Agent: Claude (Fable 5)
- Session: 2026-06-10
- Platform: Claude Code (Windows)
- Guardrails loaded: cached core + §5/§12
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- Direct SSoT write: ADR Index row for ADR-006 added directly (per AGENTS.md non-ship SSoT exception for `/adr`; guard has no section targeting) — this entry is the required Drift Log record.
- /brainstorm satisfied by TWO expert passes: E1 deep analysis + attribution review (which materially CORRECTED E1: perf rationale was analyst inference, not history; ratchet needs justification escape hatch + growable no-python core).

---

## Task Description

- E1 of the strict self-assessment queue: dual-validator maintenance debt (validate.sh 2465 + validate.ps1 2291 lines, hand-kept parity; 6+ shipped parity defects in ~10 weeks, 52/45 commits churn). Verdict REAL-FIX-NOW for the POLICY piece via expert analysis, then PROCEED-MODIFIED via attribution review.
- Decision (ADR-006, single decision per [adr-discipline]): all NEW validator checks = Python tools behind the existing run_python_check/Invoke-PythonCheck twin wrappers; native additions only via justified baseline bump (Zero-Python doctrine honored); bidirectional ratchet test enforces; opportunistic backfill on touch; no runtime behavior change at adoption.
- Attribution corrections recorded IN the ADR: ps1 exists for Windows-native operation since first release (c1ced66), NOT performance; Zero-Python downstream is doctrine (aec35d6, README, --no-python flag, CI job) with run_python_check as the sanctioned boundary.

## Plan

- Artifacts: ADR-006 (accepted, applies_to validate.sh/ps1/tools — delivery mechanism = existing bootstrap ADR-coverage check, ZERO new always-loaded lines); spec validator-strangler-policy.md (signal_tier: 1 — ratchet test IS the T1 enforcement); tests/ci/validator_native_baseline.json (floor 187/188 frozen 2026-06-10) + test_validator_native_check_ratchet.py (grow→FAIL, shrink→FAIL stale-floor, justification assertion, counting-heuristic fixture).
- Deletion-First compliance: zero additions to always-loaded surfaces (rule delivered via ADR coverage, by construction).
- Rollback: revert PR — validators byte-identical at adoption. Confidence: 90%.

## Review Feedback

- R1 (red-team Full+Beast): **PASS** — 6/6 ACs PROVEN with independent evidence (live count re-grep 187/188 exact; coverage tool live-run confirms ADR-006 surfaces for validate.sh/ps1/tools paths; validators byte-identical in diff). 1 MEDIUM accepted-and-pinned: line-leading counter is blind to mid-line emission styles (4 pre-existing live sites; empirically confirmed evasion) — documented-scope limitation backstopped by reviewer judgment; pinned post-review via test_midline_emission_styles_are_known_uncounted + baseline _doc note. 1 LOW noted (fnmatch * spans /; permissive but works).

## Security Findings

- none (policy + test; no runtime surface).

## Phase Sequence

- bootstrap (expert E1 + attribution review = research/brainstorm basis)
- adr
- spec
- plan
- implement
- review

## External References

- E1 expert analysis + attribution review (2026-06-10); ADR-001..005 precedent (5/5 classification: architecture-change); parity-defect evidence: 55ed8ea, 2354c5f, 47102d2, fcd30b6, 78d96bc, 6f0d2d2

## Known Risk

- Baseline ceremony risk (rare-by-design edits only). Evasion path: new logic routed through an existing call site — reviewable in the same diff, out of machine reach; stated in spec Enforcement Boundary. Rollback plan: revert PR.

## Conflict Resolution

none

## Skill Notes

none

## Test Gate Results

- `pytest tests/ci/test_validator_native_check_ratchet.py` → 4 passed.
- Mutation: +1 native line → growth detected; −1 line → shrink detected (both directions verified pre-review).

## Phase Summary

- bootstrap/adr/spec/plan: ADR-006 authored with attribution corrections; spec frozen (signal_tier: 1 self-applied); zero always-loaded growth by construction. ⚡ ACX
- implement: baseline JSON (187/188) + ratchet test + ADR Index direct write (logged). ⚡ ACX
- review: R1 PASS (6/6 ACs); MEDIUM blind-spot pinned as intent (5th test) + baseline _doc note. ⚡ ACX
- test: ratchet 5/5; fast loop 431 passed 3:37; slow set unaffected (validators byte-identical) — full suite delegated to PR CI both platforms. ⚡ ACX
- handoff: closure = PR on green CI; migration ADR is policy-only, rollback = revert. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-11T00:40:00+08:00
- Gate: plan | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-11T00:50:00+08:00
- Gate: implement | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-11T01:10:00+08:00
- Gate: review | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-11T01:50:00+08:00
- Gate: test | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-11T02:05:00+08:00
- Gate: handoff | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-11T02:10:00+08:00

## Evidence

- Baseline counts measured: `grep -cE '^[[:space:]]*record_result ' validate.sh` = 187; `^[[:space:]]*Add-Result ` ps1 = 188.
- Ratchet 5/5 post-pin; mutation checks both directions (growth +1 / shrink −1 detected); reviewer independently re-greped counts (exact) + live-ran coverage tool (ADR-006 surfaces for all 3 target path classes).

## Resume

- State: TESTED → HANDEDOFF → ship in flight
- Next: SSoT Spec Index + Ship History (Seq 51), spec→shipped, archive log, PR, CI both platforms, merge.

### Read Map

- docs/adr/ADR-006-validator-python-core-strangler.md — the decision + attribution corrections
- tests/ci/test_validator_native_check_ratchet.py — enforcement incl. pinned blind spot

### Skip List

- validate.sh/ps1 (byte-identical at adoption)

### Context Snapshot

- Branch @ c87d50a + review-pin commit pending; future validator-touching tasks get ADR-006 surfaced by bootstrap coverage check automatically.

### Backlog Status

- No backlog row (assessment-queue item); E1 queue closed by this ship.

## Observability

- Enforcement surfaces via pytest in CI on every PR; no runtime sink applicable (policy + test).
- ADR delivery mechanism verified earlier this session: check_adr_coverage.py surfaces covering ADRs by applies_to glob at bootstrap (used live for #17/#45/#65).
