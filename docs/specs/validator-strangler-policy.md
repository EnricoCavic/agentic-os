---
status: shipped
title: Validator Python-Core Strangler Policy (ADR-006)
source: self-assessment queue E1 + attribution review 2026-06-10
created: 2026-06-10
primary_domain: governance
secondary_domains: [tooling, ci]
signal_tier: 1
signal_tier_note: The ratchet test IS the machine enforcement (T1) for the new authoring rule; ADR-006 is surfaced to future validator-touching tasks via the existing bootstrap ADR-coverage check (applies_to globs) — zero new always-loaded lines.
---

# Validator Python-Core Strangler Policy (ADR-006)

## Goal

Stop the dual-validator parity tax from growing: new validator checks are single-implementation Python tools behind the existing twin wrappers; the native check surface becomes monotonically non-increasing except through a justified, diff-visible escape hatch that honors the Zero-Python-downstream doctrine.

## Acceptance Criteria

- AC-1: `docs/adr/ADR-006-validator-python-core-strangler.md` exists (accepted; single decision; `applies_to` covers validate.sh/ps1 + tools) and records the attribution-review corrections (ps1 exists for Windows-native operation since `c1ced66`, NOT performance; Zero-Python downstream is doctrine with `run_python_check` as the sanctioned boundary).
- AC-2: `tests/ci/validator_native_baseline.json` commits the 2026-06-10 floor: native result-emission call-site counts for both shells (ALL non-comment line-leading `record_result ` in validate.sh / `Add-Result ` in validate.ps1 — helper-internal calls are a constant offset absorbed by the baseline, so no exclusion logic is needed; adding a check via the python wrappers adds zero such lines) + an empty `justifications` list + the counting rule documented in the file.
- AC-3: `tests/ci/test_validator_native_check_ratchet.py`: (a) count > baseline → FAIL naming the delta and pointing at ADR-006 + the justification mechanism; (b) count < baseline → FAIL with "stale baseline — ratchet it down" so migrations shrink the floor; (c) count == baseline → PASS; (d) any baseline above the recorded original floor requires a non-empty justification entry (asserted).
- AC-4: The counting heuristic is itself regression-guarded: a fixture-based unit test proves the counter (i) counts a representative call-site line regardless of indentation, (ii) does NOT count commented-out lines, (iii) does NOT count occurrences embedded mid-line (e.g. inside a string or echo).
- AC-5: ADR Index in `current_state.md` gains the ADR-006 row (direct write per AGENTS.md non-ship SSoT exception for `/adr`, logged in Work Log Drift Log) — and the ship updates Spec Index/backlog normally.
- AC-6: Full test suite green; both validators byte-identical in behavior at adoption (no validate.sh/ps1 edits in this change).

## Non-goals

- No migration of any existing native check in this change (opportunistic backfill is future work, per-touch).
- No new always-loaded governance text (no AGENTS.md/guardrails edits — ADR coverage check is the delivery mechanism to future authors).
- No change to `--no-python` semantics or the deploy-no-python CI job.
- No codegen/DSL (rejected as over-engineering in expert analysis).

## Constraints

- Counting rule must be stable under formatting noise (indentation) and must not be foolable by string content inside other lines (line-leading anchored regex).
- The ratchet must fail in BOTH directions (growth = policy violation; shrink-without-baseline-update = stale floor) so the committed number is always the truth.

## Enforcement Boundary (honest)

The ratchet counts result-emission sites — a proxy, not semantics: it cannot tell a good native check from a bad one, only that the native surface grew. Whether a justification is *valid* is reviewer-judged (the diff makes it visible). An agent could in principle route new logic through an existing call site; that evasion is reviewable in the same diff and out of machine reach — stated, not hidden.

## Domain Decisions

- [DECISION] The rule lives in ADR-006, not in guardrails: bootstrap's existing ADR-coverage check (`applies_to` globs) surfaces it exactly when a task touches validator files — zero new always-loaded instruction load (Deletion-First compliant by construction).
- [DECISION] Bidirectional ratchet: a one-way ceiling would let the baseline silently overstate the floor after migrations; failing on shrink forces the baseline down and keeps the number honest.
- [DECISION] Escape hatch is a justification entry in the baseline JSON (diff-visible, reviewer-judged) — mirroring §13's net-add-justification pattern rather than inventing a new mechanism.
- [CONSTRAINT] Attribution-review discipline applied: the perf rationale from the first analysis was an inference, not history — corrected in the ADR so future readers aren't misled about why the twin exists.
