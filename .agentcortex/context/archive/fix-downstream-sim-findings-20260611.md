# Work Log: fix-downstream-sim-findings

## Header

- Branch: `fix/downstream-sim-findings`
- Classification: `quick-win`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-11`
- Owner: `claude`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `4e58ae9`
- Recommended Skills: `verification-before-completion (auto)`
- Primary Domain Snapshot: `none`
- SSoT Sequence: `53`

---

## Session Info

- Agent: Claude (Fable 5) — findings from a 6-way parallel Sonnet downstream-simulation fleet, fixes + attribution by session owner
- Session: 2026-06-11
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win) + §13 heading read (governance-path edits: deploy.sh/validate.sh/tool)
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO

---

## Task Description

- Post-v1.5.0 multi-angle downstream simulation (user-requested; multi-angle-before-fixed discipline). 6 parallel Sonnet sims (A1 fresh-install matrix, A2 no-python, A3 legacy-upgrade gauntlet, A4 runtime tooling, A5 user-content preservation, A6 validator/lock edge). 36 of ~40 checks PASS; the v1.5.0 promises (EOL in-place update, manifest-proven stale-skill split, lock lifecycle, guarded writes, no-python) all held. Findings triaged with attribution (real issue vs by-design vs sim artifact):
  - **GEMINI.md never wired into deploy.sh (HIGH, real)**: present in source root + a first-class agent entry point (multi-agent-review AC-2: "GEMINI.md imports AGENTS.md") but absent from every deploy site — downstream Gemini/Antigravity users got no entry point. Pure omission (CLAUDE.md is wired, GEMINI.md was missed). → wired into all 7 sites (tier maps ×2, dry-run list, deploy_file, manifest managed-set, summary echo, git-add hint), scaffold tier like AGENTS/CLAUDE.
  - **Lifecycle FAIL on user-authored ADRs (HIGH, real tolerance gap)**: `check_lifecycle_frontmatter.py` FAILs any post-cutoff `docs/adr/*.md` lacking the framework's lifecycle frontmatter — including a downstream user's OWN ADR, blocking their `validate.sh`. Framework imposes its doc contract on content it never wrote. → downstream user content (manifest present + path under `docs/`) degrades to WARN; framework source repo (no manifest) stays FAIL-gated. Back-compat: `root` is optional (legacy callers keep FAIL behavior).
  - **Migration banner on every routine deploy (LOW noise)**: a bare `.agentcortex-manifest` is the normal installed state, yet "Migrating from legacy paths…/Migration complete." printed on every re-deploy. → banner gated on actual legacy ARTIFACTS (agentcortex/, docs/context/, tools/validate.*); migration steps still run as silent no-ops.
  - **Validator gate-grep case-sensitivity (LOW, sh/ps1 parity drift)**: validate.sh `grep -q 'Gate: implement'`/`'Gate: plan'` are case-sensitive; ps1 mirror is case-insensitive → 2-count parity drift on lowercase `gate:` receipts. → both `grep -qi`.
  - **Aggregated local-skill note double-lists flat+dir variants (LOW cosmetic)**: a skill present in both `.agent/skills/` and `.agents/skills/` listed twice. → dedupe via sort -u.
- BY-DESIGN (not fixed, confirmed via attribution): governance.yaml not deployed (capability-by-presence); ADRs/specs not deployed to downstream docs/ (project-owned); generate_compact_index.py source-only (rarely regenerated downstream); stale-signal weakening on 2nd upgrade run (warn-only no-delete; the strong signal already fired once); `status: active` enum WARN (real user enum, advisory only — left as WARN).

## Plan

- deploy.sh (GEMINI ×7 + migration gate + dedupe), check_lifecycle_frontmatter.py (downstream WARN, back-compat optional root), validate.sh (grep -qi ×2), + tests (3 deploy, 3 lifecycle). Rollback: revert PR. Confidence: 92%.

## Phase Sequence

- bootstrap (6-sim fleet = research)
- plan
- implement
- ship

## External References

- 6 sim reports (A1-A6, 2026-06-11); multi-agent-review-guidelines.md AC-2 (GEMINI.md entry-point contract)

## Known Risk

- Lifecycle downstream-WARN keys on manifest presence; a fork that deletes its manifest would see FAILs return — acceptable (manifest is the install marker). Rollback = revert PR.

## Conflict Resolution

none

## Skill Notes

none

## Phase Summary

- bootstrap/plan: 6-way sim fleet run; 5 real findings triaged from by-design via attribution (governance.yaml/ADR non-deploy etc. confirmed intentional, NOT fixed). ⚡ ACX
- implement: GEMINI.md wired (7 sites); lifecycle downstream-WARN (back-compat); migration banner gated; gate-grep case-insensitive; note dedupe. +6 regression tests. ⚡ ACX
- ship: deploy+lifecycle suites 40 passed; validate fail=0; compact index fresh. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T09:00:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T09:05:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T10:00:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T10:15:00+08:00

## Evidence

- GEMINI.md: fresh deploy → present at downstream root + in manifest (test_gemini_md_is_deployed).
- Lifecycle: unit-verified upstream FAIL / downstream WARN (manifest gate); 19 lifecycle tests pass incl. 3 new degradation tests + back-compat root=None.
- Migration banner: 0 occurrences on fresh AND update deploy (test_no_migration_banner_on_clean_update; was printing on every re-deploy pre-fix).
- `pytest tests/ci/test_deploy_tiering.py tests/guard/test_d2_3_lifecycle.py` → 40 passed.
- `bash validate.sh` → pass=101 warn=9 fail=0; compact index fresh.
- Sims confirmed v1.5.0 promises hold: EOL CRLF→in-place (0 spurious sidecars over 161 CRLF files), manifest-proven stale-skill split (executing-plans loud / my-team-conventions gentle / custom-* silent), lock lifecycle (created→active(2)→takeover→release), guarded SSoT write + receipt, no-python deploy + validate fail=0.
