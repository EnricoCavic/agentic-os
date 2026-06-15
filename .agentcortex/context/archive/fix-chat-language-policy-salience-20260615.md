# Work Log: fix/chat-language-policy-salience

## Header

- Branch: `fix/chat-language-policy-salience`
- Classification: `quick-win`
- Classified by: `claude-opus-4-8`
- Frozen: `2026-06-08`
- Created Date: `2026-06-08`
- Owner: `claude-code-session-2026-06-08`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `none`
- Recommended Skills: `none`
- Primary Domain Snapshot: `governance-docs`
- SSoT Sequence: `42`

---

## Session Info

- Agent: `claude-opus-4-8`
- Session: `2026-06-08 (Asia/Taipei)`
- Platform: `claude-code`
- Files Read: `8`

---

## Task Description

Fix chat-language drift: agents under this framework often reply in English to Traditional-Chinese input (worst on Claude) and occasionally emit Korean/Japanese. Root cause = output-layer enforcement asymmetry (English sentinel/gate templates reinforced every turn vs a single un-reinforced declarative language line) + ~99% English context dilution + an artifact-vs-chat carve-out gap + an Antigravity-only contradictory "default Traditional Chinese" rule. Apply the minimal cross-platform fix (owner-selected options 1+2+4).

---

## Phase Sequence

| Phase | Status | Entered | Notes |
|---|---|---|---|
| bootstrap | done | 2026-06-08 | quick-win, governance-file exclusion (tiny-fix barred) |
| plan | done | 2026-06-08 | plan-skip artifact; enforcement-lesson cross-check recorded |
| implement | done | 2026-06-08 | 3 edits + compact-index regen; validate fail=0 |
| review | done | 2026-06-08 | adversarial self-review; Verdict PASS |
| test | done | 2026-06-08 | doc-only; validate.sh = regression gate |
| ship | done | 2026-06-08 | SSoT seq 42→43; impl commit f99d711 |

---

## Phase Summary

**bootstrap**: Classified `quick-win`. Self-check (Lesson classification-flow 67): writing a spec? No. Running /handoff? No → quick-win confirmed. Touches governance files (`AGENTS.md`, `.antigravity/rules.md`) → tiny-fix fast path barred (AGENTS.md §Runtime v1 rule 2 / engineering_guardrails §10.3), quick-win minimum. Diagnosis grounded in 4 sub-agent expert passes + direct grep: only `AGENTS.md:7` and `.antigravity/rules.md:6` carry chat-language rules; `.agent/` phase/guardrail corpus has ZERO chat-language references (the rule is never reinforced at the layer where English templates ARE).

**plan**: 3 edits (AGENTS.md policy rewrite + sentinel co-location + .antigravity inherit-pointer) + compact-index regen. Enforcement cross-check recorded (Known Risk): no validator added; enforcement = user-as-observer + salience.

**implement**: (1) `AGENTS.md §Chat Language Policy` rewritten — universal-language + anti-CJK-drift + artifact-vs-chat carve-out + English fallback. (2) `AGENTS.md §Runtime v1 rule 11` sentinel clause appended (body before `⚡ ACX` in user's language). (3) `.antigravity/rules.md:6` hardcoded zh-TW default → inherit-pointer. (4) `trigger-compact-index.json` regenerated (1 hash line: AGENTS.md). `validate.sh` pass=101 warn=7 fail=0 (warn=7 all pre-existing on unrelated logs, matches v1.4.0 baseline).

**review**: adversarial self-review — root-cause coverage ①②③④ + fallback confirmed; scope clean (3 files only, no dragged refactor); no new contradiction (carve-out reconciles CONTRIBUTING/AGENT_PHILOSOPHY; pointer target exists); 4-platform parity restored; fake-MUST handled (rides existing honor-system sentinel, policy body imperative not gated). Verdict PASS, no CRITICAL/HIGH/MEDIUM; 1 LOW (fallback-to-prior-turn) deferred as not worth complexity.

**test**: doc/governance change, no runtime path → test-classify = no automated unit test; regression gate is `validate.sh` (structural + compact-index freshness) = fail=0.

⚡ ACX

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T00:00:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T00:00:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T00:00:00+08:00
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T00:00:00+08:00
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T00:00:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T00:00:00+08:00

---

## External References

| Type | Path / URL | Notes |
|---|---|---|
| Spec | — | quick-win, no spec |
| ADR | — | no behavior-boundary change (steering/salience only) |
| Issue | — | — |
| PR | — | pending |

---

## Known Risk

- **Fake-MUST theatre** (Lesson enforcement 74 / governance-proposal 76): the fix strengthens an unenforceable behavioral rule. Mitigation: chat language is the USER-VISIBLE output — the user is the immediate external observer (a valid enforcement class per Lesson 74). NO validator added (correctly impossible/inappropriate to gate chat language; adding one would be the scope-creep the experts flagged). Framed as a salience/steering fix, not a gated safety property.
- **Compact-index staleness**: `AGENTS.md` is `detail_ref` for `phase-entry-skill-loading` (no heading scope) → any edit shifts its content_hash. Mitigation: regenerate `trigger-compact-index.json` in the same change; verify `validate.sh` fail=0.

---

## Conflict Resolution

none

---

## Skill Notes

none

---

## Drift Log

- Re-read: none beyond session-init governance.
- SSoT write: `current_state.md` updated via Edit tool (direct), NOT `guard_context_write.py`. Reason: targeted multi-line Ship-History insert + seq/date field bumps are not expressible via the guard's single-line `append` mode, and `replace` mode (whole-file rewrite) is higher-risk than a scoped Edit. Optimistic-lock value is nil here (sole owner, fresh branch, immediate commit). Transparent deviation logged per AGENTS.md SSoT-write note.
- Post-ship pre-merge refinement (user-approved): generalized the anti-drift *verb* to "never collapse a non-English input into English" + added "English" to the CJK example list. Triggered by user Q on Latin-script coverage; a cold-read subagent test (EN/FR/DE/ES + mixed) confirmed routing was already correct but the imperative verb named only CJK. Same PR #206, no seq bump (same ship).
- Scope expansion (user-requested "CI要修" + "發個小版本"): PR CI went red on `tests/guard/test_worklog_lock_recovery.py::test_active_lock_preserved_by_api_and_cli`. Verified PRE-EXISTING (fails on pristine origin/main locally; unrelated to my files) — a TIME-BOMB: the test anchors a lock `updated_at` to a frozen `NOW` (2026-06-08T12:15Z) but the CLI subprocess has no clock injection and judges staleness against wall-clock, so it flips active(2)→recovered(0) ~60 min after that timestamp. main's green CI predated the window. Fixed by anchoring the lock to real current time. Also cut **v1.4.1** patch release (banner bumps + CHANGELOG). All three (lang fix + test fix + release) ride PR #206.

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

> Populated at implement/ship.

none
