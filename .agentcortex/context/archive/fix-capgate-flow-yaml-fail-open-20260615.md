# Work Log — fix/capgate-flow-yaml-fail-open

| Field | Value |
|---|---|
| Branch | fix/capgate-flow-yaml-fail-open |
| Classification | quick-win |
| Classified by | Claude (Opus 4.8) |
| Frozen | true |
| Created Date | 2026-06-15 |
| Owner | KbWen |
| Guardrails Mode | Quick |
| Current Phase | ship |
| Checkpoint SHA | e561429 (shipped, PR #244) |
| Recommended Skills | verification-before-completion (ship evidence), systematic-debugging (defect fix) |
| Primary Domain Snapshot | none |

## Session Info
- Agent: Claude Opus 4.8 (1M context)
- Session: 2026-06-15
- Platform: Claude Code (Antigravity runtime)
- Guardrails loaded: skipped (quick-win) — but security-control weight → mandatory independent /review + full-suite /test
- Override: none
- Downstream-Capabilities: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- Recovered stale Work Log lock on 2026-06-15T05:31:16.270212+00:00; prior_owner=KbWen; prior_session=2026-06-15T03:00:00+08:00; reason=stale-time; lock=fix-capgate-flow-yaml-fail-open.lock.json

## Task Description
- **Bug (verified, self-reproduced):** the ADR-007 capability gate validator `validate_downstream_capabilities.py` **fails OPEN** on flow-style YAML when PyYAML is absent — the exact env of the branch-protection-required Framework Validation CI jobs (`validate.yml:78-108` run `setup-python` + `validate.sh` with NO `pip install`). The fallback parser `_yaml_loader._parse_yaml_subset` doesn't handle flow *mappings* `{k: v}` (only flow *sequences* `[a,b]`), so `trackers: [{id: custom-j, blocking: true}]` parses to a single mangled key `"{id"` → the `_forbidden` denylist never sees `blocking`/`gate`/`ship_edge`… → PASS. ADR-007 + the validator docstring claim this is "UNREPRESENTABLE… caught regardless of parser" — false in the enforcing env.
- **Repro proof:** PyYAML present → REJECT; PyYAML absent (fallback) → PASS for flow-style, REJECT for block-style. (`.acx-local/repro_capgate.py`, to be converted into a real test.)
- **Severity:** HIGH as a security control that claims enforcement but fails open (core [enforcement] theme); runtime impact bounded (ADR-007 trackers advisory, no shipped consumer yet) — defense-in-depth fail-open, not active exploit.
- **Fix (root, fail-closed):** make the fallback parser RAISE on flow-mapping/anchor/alias/merge syntax it cannot faithfully represent (so `load_data` → exception → validator `main()` already catches → exit 2 MALFORMED). Precise detection: an unquoted scalar value that is `{...}` (flow mapping), or starts with `&`/`*` (anchor/alias), or a `<<` merge key. MUST NOT reject flow *sequences* `[a,b]` (supported) or `{`/`:` inside quoted strings / descriptions.
- **Plus:** add a no-PyYAML + flow-style regression test to `tests/guard/test_capabilities_schema_gate_safety.py` (existing test only covers the PyYAML path + block-style — false confidence).

## Phase Sequence
- bootstrap
- plan
- implement → review(R1 NOT READY) → implement → review(R2 NOT READY) → implement → review(R3 NOT READY) → **design panel → Option-4 pivot** → implement → test → review(R4 PASS)
- ship

## Final Design (Option 4 — supersedes the original _yaml_loader approach)
- The fix evolved through 4 independent review rounds (each found a real residual fail-open) + a 3-expert design panel. **Final design: a dedicated STRICT allowlist mini-parser** (`parse_strict`) inside `validate_downstream_capabilities.py`, decoupled from the shared `_yaml_loader` (REVERTED — zero blast radius on its ~20 other consumers) and from PyYAML.
- Root cause (panel): `_yaml_loader` serves two opposite masters — trigger-registry.yaml (where `trigger_priority`/`block_if_missed` are legal data) vs capabilities (where they're forbidden). Hardening the shared parser is whack-a-mole; the capabilities file needs its OWN strict handling.
- `parse_strict` accepts ONLY the minimal block subset the schema needs (block maps/seqs, plain + simple-quoted scalars, `[a,b]` plain flow-seqs) and RAISES (→ exit 2) on EVERYTHING else (flow maps, anchors, aliases, tags, merge, explicit keys, escapes, block scalars, inline comments, tabs, multi-doc, dup keys, misaligned indentation). Allowlist, not denylist → fail-closed on any unforeseen syntax by construction.

## External References
none

## Known Risk
- **Blast radius — RESOLVED to zero:** the original approach edited the shared `_yaml_loader` (8 callers); the Option-4 pivot REVERTED it and put a capabilities-only strict parser in the validator. `git diff --name-only` = only `validate_downstream_capabilities.py` + the test. No shared-parser change → no caller can regress.
- **New hand-rolled parser risk (panel-flagged):** mitigated by R4's exhaustive differential fuzz (1.15M+ cases vs PyYAML, 0 leaks, 0 crashes) + an independent confirm that `parse_strict ≡ PyYAML` structure on accepted docs (validate runs on real data) + RecursionError caught → fail-closed.
- **Usability (non-blocking, fail-CLOSED):** unquoted special chars in a description / inline comments → rc 2 (author quotes the value). Safe direction; error messages name the line+reason. Optional follow-up: a one-line author note in ADR-007/downstream guide.
- Rollback: revert PR (single validator file + test; `_yaml_loader` already at main).

## Conflict Resolution
none

## Skill Notes
none

## Phase Summary
- bootstrap: classified quick-win; security-control weight → mandatory review+test; bug self-reproduced + CI env confirmed.
- plan: root-fix design + blast-radius survey (later superseded). | Confidence: high.
- implement (×4 rounds): flow-map → +quoted-key → +flow-seq-kv/mismatched-quote/raw-scan → **pivot to strict mini-parser (Option 4)**; _yaml_loader reverted. | Confidence: high.
- test: capability-gate 38 passed; full suite 503 passed, 0 regressions; R4 fuzz 1.15M+ cases 0 leaks. | Confidence: 96% — high.
- review: R1/R2/R3 NOT READY (each a real residual, fixed) → 3-expert design panel → Option-4 → R4 PASS (ship-ready). | Confidence: 96% — high.
- ship: PR (pending commit). | Confidence: 95% — high.

⚡ ACX

## Review Feedback
- R1: independent fresh-context adversarial reviewer. Verified flow-mapping/anchor/alias/merge fix correct + non-vacuous (mutation-confirmed) + no false-positive on registry/flow-sequences. **BUT found a real residual (NOT READY): quoted-key bypass.**
- **BLOCKER (R1, fixed):** the subset parser unquoted *values* (`_parse_scalar`) but took *keys* raw (`.strip()`), so `trackers:\n  - 'blocking': true` parsed the key as literal `"'blocking'"` → denylist missed it → gate-safe (exit 0) under no-PyYAML, where PyYAML rejects (exit 1). Same fail-open class, 4/6 placements (trackers items + skills.detect_by; top-level caught by allowlist).
- **Resolution:** added `_unquote_key()` applied symmetrically at all 3 key sites (`_parse_mapping`, sequence-item first key, sequence-item later key). Independently reproduced the bypass (exit 0) THEN confirmed closed (now REJECT naming the resolved key). +4 quoted-key tests (cover all 3 sites). Tightened flow tests to assert rc==2 (self-validating fallback, per R1 nit #1).
- R1 nit #3 (docstring "regardless of parser" was aspirational while residual stood) — now accurate after the quoted-key close. R1 confirmed no metadata uses quoted keys → unquoting is regression-free.
- **R2 (NOT READY):** found 2 more vectors — flow-seq `[blocking: true]` (mangled to a string) + mismatched/unterminated quote `'blocking: true`. Both reproduced. Fixed via parser guards + a raw-text forbidden-key scan (Option A, user-chosen at the time). 4 vectors closed.
- **R3 (NOT READY):** found a **5th vector** — double-quoted backslash-escape key `"\x62locking"` (PyYAML decodes → `blocking`; subset keeps literal). ALSO proved the raw scan (Option A) causes false-positives (`description: "first, gate: second"` wrongly rejected) AND adds no unique protection. All reproduced with a clean harness.
- **Design panel (3 fresh experts):** rejected Option 1 (Expert 1 found a **6th vector** — silent-drop misindentation; the parser drops lines it can't place while PyYAML errors). Root cause = one lenient parser, two opposite masters. Recommended a dedicated strict-allowlist mini-parser. User approved Option 4.
- **R4 (PASS):** reviewed the new strict parser with **1,143,072 differential fuzz cases vs PyYAML + 4,536 subprocess cases + ~150 hand vectors → 0 fail-open leaks, 0 crashes, 0 hangs.** All 6 historical vectors closed by construction. Independent confirm: `parse_strict ≡ PyYAML` structure on accepted docs. Only findings = 2 fail-CLOSED usability nits (non-blocking). **Verdict: ship-ready.**

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: review | Verdict: NOT READY | Classification: quick-win | Timestamp: 2026-06-15
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: review | Verdict: NOT READY | Classification: quick-win | Timestamp: 2026-06-15
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: review | Verdict: NOT READY | Classification: quick-win | Timestamp: 2026-06-15
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-15

## Evidence
- Repro: PyYAML-absent flow-style `{blocking: true}` → PASS (vuln); block-style → REJECT. CI Framework Validation jobs run without PyYAML (validate.yml:78-108).
- implement: root fix in `_yaml_loader.py` — 3 precise fail-closed guards (`_parse_scalar` value-start `{`/`&`/`*`; `_parse_sequence` item-start `{`/`&`/`*`; `_parse_mapping` `<<` key) + docstring. Spares flow-sequences `[a,b]`, quoted strings, folded scalars (verified by design + the no-false-positive test).
- Tests: +5 to `test_capabilities_schema_gate_safety.py` (no-PyYAML subprocess harness via PYTHONPATH-shadowed `yaml.py` raising ImportError): 3 flow-style trackers evasion cases (must be NOT gate-safe) + 1 safe flow-sequence file (no false-positive) + 1 block-style still-rejects. **21 passed**.
- **Mutation-verified both directions**: with the `_parse_sequence` guard disabled, the 3 flow-style tests FAIL with `rc=0 / "gate-safe"` — the exact fail-open reproduced; guard restored → pass. The test is a genuine guard, not vacuous.
- **FINAL (Option 4):** `git diff --name-only` = `validate_downstream_capabilities.py` (strict mini-parser + schema checks, _yaml_loader/PyYAML decoupled) + `tests/guard/test_capabilities_schema_gate_safety.py` (38 tests). `_yaml_loader.py` reverted to main.
- Capability-gate tests: **38 passed** (5 schema + 12 reject-not-clamp + rich-safe + 5 clean-forbidden→rc1 + 13 exotic-syntax→rc2 + 3 value-FP→rc0). Full fast suite: **503 passed, 45 deselected, 0 regressions.**
- R4 differential fuzz: 1.15M+ cases vs PyYAML → **0 fail-open leaks**. Independent confirm: `parse_strict(_RICH_SAFE) == yaml.safe_load(...)` (True) — validate runs on real data; 6 vectors rc 2/1; value-FP rc 0.
- Rollback: revert PR (1 validator file + 1 test).
