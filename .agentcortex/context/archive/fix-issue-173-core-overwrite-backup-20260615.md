---
template: false
description: Work Log for fix/issue-173-core-overwrite-backup
---

# Work Log: fix/issue-173-core-overwrite-backup

## Header

- Branch: `fix/issue-173-core-overwrite-backup`
- Classification: `quick-win`
- Classified by: `claude-opus-4-8`
- Frozen: `2026-06-06`
- Created Date: `2026-06-06`
- Owner: `claude-opus-4-8`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `dfe27b2`
- Recommended Skills: `none`
- Primary Domain Snapshot: `none`
- SSoT Sequence: `35`

---

## Session Info

- Agent: `claude-opus-4-8`
- Session: `2026-06-06 (find-a-task autonomous)`
- Platform: `claude-code`
- Files Read: `12`

---

## Task Description

Fix issue #173: on the deploy UPDATE path, a downstream-locally-modified **core** file was silently overwritten (no warning, no backup, hidden inside "N updated"), unlike scaffold-tier files which sidecar via `.acx-incoming`. Reproduced empirically. Fix preserves the ADR-005 force-update invariant (the new framework version still lands) but backs up the user's prior version to `.acx-local` + surfaces the overwrite in deploy output, closing the silent-data-loss footgun.

Issue-claim correction: `deploy.ps1` is only a thin bash launcher (delegates to `deploy.sh`), so there is a single logic file — the fix is `deploy.sh` only, not "both".

---

## Phase Sequence

| Phase | Status | Entered | Notes |
|---|---|---|---|
| bootstrap | done | 2026-06-06 | quick-win; verified #173 real via code-read + repro |
| plan | done | 2026-06-06 | fast-path; deploy.sh core branch + counter + summary + warn |
| implement | done | 2026-06-06 | 4 edits in deploy.sh + 1 new test |
| review | done | 2026-06-06 | ADR-005 invariant preserved; no break to existing AC-5 test |
| test | done | 2026-06-06 | repro pass + deploy tiering suite |
| handoff | exempt | — | quick-win |
| ship | in-progress | 2026-06-06 | — |

---

## Phase Summary

- **bootstrap**: classified quick-win. Verified #173 is REAL — `deploy.sh:161` core branch force-overwrites with no hash check; empirically reproduced (core edit lost + silent + no sidecar; scaffold control preserved). ⚡ ACX
- **plan**: fast-path. Targets = `deploy.sh` (core branch backup+warn, new `COUNT_CORE_OVERWRITTEN`, summary annotation, warning block) + `tests/ci/test_deploy_tiering.py` (new behavioral test). Chose sidecar name `.acx-local` (user's OLD version) distinct from `.acx-incoming` (scaffold's NEW version) — also keeps the existing AC-5 test green.
- **implement**: 4 edits in deploy.sh; `bash -n` OK.
- **review**: force-update invariant preserved (new version lands); `.acx-local` ≠ `.acx-incoming` so existing AC-5 test still passes; no ADR-005 boundary changed. **Adversarial review (subagent + code-verified) caught a real HIGH defect**: the backup `cp ${CP_FLAG}` could be silently skipped under user-set `CP_FLAG=-n`/`-i` because `.acx-local` is never auto-cleaned (a stale one pre-exists) → reintroduced the very silent-data-loss #173 closes. Fixed with `rm -f "$dst.acx-local"` before the backup cp. Also adopted MEDIUM finding: added `*.acx-local` to the managed `.gitignore` block (heredoc + awk strip table) for parity with `*.acx-incoming`. LOW finding (single-slot "latest-wins" backup) accepted as intended + now asserted by test. Verified the openssl branch needs no `\`-strip (no filename escaping), per reviewer.
- **test**: post-fix repro — `[OVERWRITE]` line emitted, summary annotated, `.acx-local` holds the edit, live file force-updated, scaffold preserved, 180+ unmodified core files not false-flagged; deploy tiering suite run.

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T13:10:00Z
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T13:20:00Z
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T13:30:00Z
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T13:40:00Z
- Gate: test | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T13:50:00Z
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-06T14:00:00Z

---

## External References

| Type | Path / URL | Notes |
|---|---|---|
| Issue | https://github.com/KbWen/agentic-os/issues/173 | core silent-overwrite |
| ADR | docs/adr/ADR-005-downstream-file-preservation-tiering.md | force-update invariant (preserved) |

---

## Drift Log

- Scope expansion (same bug, root cause): the new idempotency test exposed a **pre-existing latent cross-platform defect** in `compute_sha256`. GNU `sha256sum` / BSD `shasum` escape filenames containing a backslash by prefixing the output line with a literal `\`. On Windows/Git Bash a backslash TARGET path (e.g. `C:\proj`, as `deploy.ps1`/subprocess pass) made every `dst` hash come back as `\<hash>`, while repo-side `src` (forward-slash `$REPO_ROOT`) hashed clean → every `dst`-vs-manifest comparison mismatched. This silently mis-flagged unmodified core (my new branch) AND scaffold-tier (existing `.acx-incoming` branch) files as "locally modified" on backslash-path deploys. Fixed by stripping a leading `\` in `compute_sha256`. In-scope because #173's fix is incorrect without it (and it hardens the existing scaffold path too). Found via stderr-debug: `dst=[\29e5c992…]` vs `src=[29e5c992…]`.

---

## Evidence

- Repro (pre-fix): core `engineering_guardrails.md` edit LOST, no sidecar, not mentioned in output, counted in "183 updated"; scaffold `current_state.md` preserved + `.acx-incoming` (control).
- Repro (post-fix): `[OVERWRITE] .agent/rules/engineering_guardrails.md (... backed up to ...acx-local)`; `Summary: 183 updated (1 locally-modified core force-updated) / 1 skipped`; `.acx-local` contains the user edit; live file force-updated (edit gone); scaffold still preserved; only the 1 modified core flagged (no false positives over 180+ core files).
- `bash -n deploy.sh` OK.
- New test `test_modified_core_rule_backs_up_to_acx_local_and_is_not_silent` (incl. idempotency: 2nd update does not re-flag).
- Existing `test_skill_edit_sidecars_and_core_rule_force_updates` (AC-5) still green (`.acx-local` ≠ `.acx-incoming`).
- Root-cause fix: `compute_sha256` strips a leading `\` (GNU sha256sum / BSD shasum backslash-path escaping). New idempotency test (2nd unmodified update) went 124 spurious overwrites → 0. Test `test_modified_core_rule_backs_up_to_acx_local_and_is_not_silent` PASS (95s).
- Review-fix evidence: new `test_core_backup_not_skipped_under_cp_flag_n` (two `CP_FLAG=-n` updates with successive edits A→B; asserts backup holds B not A — would fail without the `rm -f`) + `test_deploy_gitignores_acx_local_sidecar`. Targeted run (4 tests incl. AC-5): 4 passed.

---

⚡ ACX
