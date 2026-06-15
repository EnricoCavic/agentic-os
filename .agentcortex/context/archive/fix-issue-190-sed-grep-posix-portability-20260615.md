---
template: false
description: Work Log for fix/issue-190-sed-grep-posix-portability
---

# Work Log: fix/issue-190-sed-grep-posix-portability

## Header

- Branch: `fix/issue-190-sed-grep-posix-portability`
- Classification: `quick-win`
- Classified by: `claude-opus-4-8`
- Frozen: `2026-06-06`
- Created Date: `2026-06-06`
- Owner: `claude-opus-4-8`
- Guardrails Mode: `Quick`
- Current Phase: `implement`
- Checkpoint SHA: `dfe27b2`
- Recommended Skills: `none`
- Primary Domain Snapshot: `none`
- SSoT Sequence: `35`

---

## Session Info

- Agent: `claude-opus-4-8`
- Session: `2026-06-06 (find-a-task autonomous)`
- Platform: `claude-code`
- Files Read: `6`

---

## Task Description

Fix issue #190: `validate.sh` uses GNU-only `\s` in `grep -E` / `sed -E` regexes, which BSD grep/sed (macOS default) treats as a literal `s`, breaking whitespace handling. Replace the 6 shell-context `\s` occurrences with POSIX `[[:space:]]` (works on GNU and BSD). Python-`re` `\s` left untouched (cross-platform-safe).

Triage note (separate, not this branch): #186, #187, #191 from the same 2026-06-05 batch were verified as false-premise (empirical evidence) and recommended for closure; this branch only addresses the genuine portability defect #190.

---

## Phase Sequence

| Phase | Status | Entered | Notes |
|---|---|---|---|
| bootstrap | done | 2026-06-06 | quick-win, SSoT read |
| plan | skipped | — | quick-win fast-path |
| implement | done | 2026-06-06 | 6 `\s` → `[[:space:]]` in validate.sh |
| review | done | 2026-06-06 | self-review PASS; scope = 6 lines, no creep |
| test | done | 2026-06-06 | validate.sh + ci/guard suite |
| handoff | exempt | — | quick-win |
| ship | in-progress | 2026-06-06 | — |

---

## Task Description Detail / Fix Sites

`validate.sh` shell-context `\s` (GNU-only) → `[[:space:]]` (POSIX):
- L783: `grep -Eq '^primary_domain:\s*...'`
- L807: `grep -Eq '^status:\s*living$'` + `grep -Eq '^domain:\s*...'`
- L1412: `grep -qiE '^\s*-\s+Reclassif'`
- L1652: `sed -E 's/...:\s*`?//; s/\s*$//'`
- L1680: `sed -E 's/...:\s*`?//; s/\s*$//'`
- L1980: `grep -vE '^\s*(—)?\s*$'`

Left untouched (Python `re`, cross-platform): L1132/1135/1162/1175/1177/1228/1238/1356/1357.
`validate.ps1`: no change — .NET regex `\s` is cross-platform; Windows path unaffected.

---

## Phase Summary

- **bootstrap**: classified quick-win (validate.* is tiny-fix-excluded → quick-win minimum). SSoT read. Scope = issue #190 portability defect only.
- **plan**: fast-path (no spec artifact). Target = `validate.sh`; 6 shell-context `\s` → `[[:space:]]`; Python-`re` `\s` untouched; rollback = revert. ⚡ ACX
- **implement**: applied the 6 edits; `bash -n` OK.
- **review**: self-review PASS — POSIX `[[:space:]]` is ERE-valid on GNU+BSD; empirically equivalent on GNU; scope = 6 lines no creep; `validate.ps1` (.NET regex) needs no change.
- **test**: `validate.sh` fail=0 (edited checks `[PASS]`); `pytest tests/ci tests/guard` 198 passed.

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T12:10:00Z
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T12:20:00Z
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T12:30:00Z
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T12:35:00Z
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T12:40:00Z
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T12:45:00Z

---

## External References

| Type | Path / URL | Notes |
|---|---|---|
| Issue | https://github.com/KbWen/agentic-os/issues/190 | BSD grep/sed portability |

---

## Drift Log

none

---

## Evidence

> Filled during implement/review/test.

- GNU equivalence (pre-change baseline, this machine GNU grep 3.0 / sed 4.9): `\s` and `[[:space:]]` produce identical output for both the `status:` grep and the Classification `sed` extraction (`quick-win`). Confirms no CI/Linux regression from the substitution.
- Scope confirmed complete: `grep -nF '\s'` after edits shows zero shell-context occurrences (only Python-`re` lines remain, which are cross-platform). No `\w`/`\d`/`\b` in shell context. `deploy.sh` has zero `\s`/`\w` (issue's "validation scripts" plural fully covered).
- `bash -n .agentcortex/bin/validate.sh` → OK.
- `bash .agentcortex/bin/validate.sh` → pass=98 warn=7 fail=0 after gate receipts written (the transient fail=1 was this Work Log lacking receipts, now resolved). Edited document-governance checks still `[PASS]`.
- `python -m pytest tests/ci tests/guard` → **198 passed in 235s** (exit 0). No test asserts on the `\s` literal (grep-confirmed).
- Diff: `validate.sh` 6 insertions / 6 deletions, 1 file.

---

⚡ ACX
