# Work Log: feat-governance-eval-harness

## Header

- Branch: `feat/governance-eval-harness`
- Classification: `feature`
- Classified by: `Claude (Fable 5)`
- Frozen: `true`
- Created Date: `2026-06-10`
- Owner: `claude`
- Guardrails Mode: `Full`
- Current Phase: `test`
- Checkpoint SHA: `c60c4f4` (+ NEW-1 fix commit pending in Test Gate run)
- Recommended Skills: `verification-before-completion (auto), systematic-debugging (auto), red-team-adversarial (auto — feature→Full at /review), karpathy-principles (auto), test-driven-development (auto), subagent-driven-development (auto — 5+ new files)`
- Primary Domain Snapshot: `governance`
- SSoT Sequence: `45`

---

## Session Info

- Agent: Claude (Fable 5)
- Session: 2026-06-10 (same session as #17 ship; guardrails already loaded — §1, §2, §4, §7, §8.1, §10 core + §5/§12 at implement)
- Platform: Claude Code (Windows)
- Guardrails loaded: §1, §2, §4, §7, §8.1, §10 (core) — cached from session start per Read-Once
- Override: none

## Drift Log

- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- /brainstorm replaced by design analysis inline (issue #151 already specifies files + schema; design forks resolved in spec Domain Decisions). Logged per bootstrap §3.7.

---

## Task Description

- Backlog #45 / GH issue #151 (P1, feature): language-neutral, data-only governance eval harness — YAML eval-spec of adversarial prompts tagged with the rule each protects + stdlib-only runner scoring transcripts or a live --agent-cmd, --coverage mode flagging zero-guarded rules, and a DELETE-bias diff workflow proving a rule is load-bearing before deletion.
- Issue history: closed once (DELETE-bias, no consumer), reopened after multi-pass verification confirmed a real gap with an existing consumer (validate advisory WARN as enforcement hook).
- Key constraint discovered at bootstrap: stdlib-only YAML → reuse `.agentcortex/tools/_yaml_loader.py` (PyYAML→subset-parser→json fallback); eval YAML must stay within the supported subset (mappings, sequences of mappings, flow sequences, `>` folded scalars).
- ADR coverage: covered_by ADR-002 + ADR-003 (validate.sh surface). Exit 0.
- Full phase chain: /spec → /plan → /implement → /review → /test → /handoff → /ship

## Phase Sequence

- bootstrap
- spec (docs/specs/governance-eval-harness.md, frozen)
- plan
- implement (delegated to acx-implementer subagent; verification + commit by session owner)

## Plan

- Target Files: `.agentcortex/eval/governance.yaml` (≥12 seed cases) · `.agentcortex/tools/run_governance_eval.py` · `.agentcortex/tools/run_delete_bias_diff.sh` · `validate.sh`+`validate.ps1` advisory coverage WARN (parity) · `docs/guides/delete-bias-workflow.md` · `tests/guard/test_governance_eval.py` · `deploy.sh` runtime-tools whitelist (validate references the new tool → test_deployed_governance_referenced_tools_are_deployed will enforce).
- Steps: implementer subagent builds all targets per spec AC-1..9 → I verify (tests + validators + spot re-trace) → commit → /review (red-team) → /test → /handoff → /ship.
- Risk + Rollback: new files + 2 validator hunks + deploy whitelist lines; revert PR = rollback.
- AC Coverage: AC-1..9 ↔ targets 1:1; deploy whitelist is AC-7 collateral (referenced-tool drift test).
- Mode: Full. Confidence: 90% — schema and consumer pinned by issue + spec; residual risk is YAML-subset friction (mitigated: loader-compat test is AC-1/AC-9 mandatory).
- Rollback plan: revert merge commit of this branch's PR.

## Test Gate Results

- Final (@d884cc6): `python -m pytest tests/ci tests/guard -q` → **272 passed** in 524s (241 post-#17 baseline + 31 new eval tests).
- `bash validate.sh` → pass=99 warn=10 fail=1; `validate.ps1` → pass=99 warn=9 fail=1 — both: sole FAIL = Spec Index completeness (resolves at ship); new `governance eval coverage: 44 ...` WARN wording identical in both.
- Live checks: `--coverage` (51 anchors / 14 cases / 44 zero), `--transcripts` empty dir → 14 skipped exit 0, wrapper multi-word `--agent-cmd` end-to-end pass, non-interactive baseline/mutated diff → vacuous verdict.

## Resume

- State: TESTED → HANDEDOFF (pending ship)
- Completed: spec (frozen) → plan → implement (add417a, delegated + independently verified) → review R1 NOT READY → fixes (c60c4f4) → R2 PASS → NEW-1 hardening (d884cc6) → test
- Next: /ship — Spec Index entry + Ship History (Seq 46), archive log, backlog #45 → Shipped, PR (closes #151)
- Blocker: none

### Read Map

- docs/specs/governance-eval-harness.md — AC-1..9 + Domain Decisions
- .agentcortex/tools/run_governance_eval.py — runner core (structural gate at main() load; injection-safe _run_agent)
- .agentcortex/eval/governance.yaml — 14 seed cases
- docs/guides/delete-bias-workflow.md — operator runbook

### Skip List

- validate.sh/ps1 full bodies (only the eval-coverage advisory blocks are new)
- _yaml_loader.py (reused, unmodified)

### Context Snapshot

- Branch feat/governance-eval-harness @ d884cc6 (4 commits ahead of main 991ec8c)
- Coverage honesty: 44/51 MUST-rule sections have zero guarding cases — the WARN is the standing consumer; growing the case set is follow-up work (#65 depends on this harness)

### Backlog Status

- #45 In Progress → flips Shipped at ship; #65/#69 unblocked by this feature

## Review Feedback

- R1 (red-team Full, AC-1..9 BoP: 7 PROVEN, AC-6/AC-9 PARTIAL): NOT READY — HIGH-1 run_delete_bias_diff.sh RUNNER_ARGS word-split broke documented multi-word `--agent-cmd` live mode (reproduced; swallowed by `|| true`); MED-1 validate.sh dead json block + double coverage subprocess (ps1 asymmetry); MED-2 malformed-YAML clear-error guarantee PyYAML-only (subset parser lenient, untested); MED-3 advisory: Spec Index FAIL expected pre-ship, must clear at ship. → fixes c60c4f4 (bash array; dead block removed; structural validation + yaml.py-blocker test).
- R2: PASS — all three blockers re-verified with reproduction evidence; 44 tests green ×2. NEW-1 (LOW, non-blocking): scoring-mode field shapes unvalidated (assertions non-dict → AttributeError; expect_substrings scalar → silent char-iteration). Fixed anyway same-day (cheap, same class as MED-2): extended structural gate + 1 sweep test (31 tests).

## Security Findings

- none unresolved. (R1 HIGH-1 was robustness, not security; --agent-cmd injection surface verified safe in R1: shlex-split-template-then-substitute, shell=False, 5 attack vectors held.)

## External References

- GH issue #151; backlog #45 (set In Progress 2026-06-10)
- `.agentcortex/tools/_yaml_loader.py` (reused loader)
- Global Lesson [enforcement][HIGH] (the lesson this harness operationalizes)
- AGENTS.md / .agent/rules/engineering_guardrails.md / .agent/rules/security_guardrails.md (rule inventory sources for --coverage)

## Known Risk

- Honest boundary: the harness measures behavior only when RUN (manual / dispatch); it is not always-on enforcement. The validate WARN covers coverage (zero-guarded rules), not behavioral pass rates. Spec states this; no fake MUST.
- Scoring is substring/regex-based on transcripts — brittle to paraphrase; mitigated by forbid/expect pairs and assertions; documented limitation.
- YAML subset: complex prompts with special chars must use quoted/folded forms the subset parser supports; test with the actual loader.
- Rollback plan: revert PR (new files + 2 validator hunks only).

## Conflict Resolution

none

## Skill Notes

none

## Phase Summary

- bootstrap: classified as feature (backlog tier), ADR coverage OK, _yaml_loader constraint identified, backlog row → In Progress. ⚡ ACX
- plan: 7 target groups (incl. deploy whitelist collateral), AC-1..9 1:1; Confidence: 90%; implementation delegated to acx-implementer. ⚡ ACX
- implement: commit add417a (14 seed cases, runner, diff workflow, validators, runbook, 29 tests, deploy whitelist) — independently re-verified (43 tests + live coverage + validate parity) before commit. Post-review fixes c60c4f4 + NEW-1 commit. ⚡ ACX
- review: R1 NOT READY (HIGH-1/MED-1/MED-2) → fixes → R2 PASS; LOW NEW-1 fixed beyond verdict (same class as MED-2). ⚡ ACX
- test: 272 passed full suite; validators parity (sole FAIL = pre-ship Spec Index, WARN wording identical); live runner/wrapper checks green. ⚡ ACX
- handoff: Resume + Read Map/Skip List/Snapshot written; closure = Open PR then merge on green CI; next /ship. ⚡ ACX

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T03:30:00+08:00
- Gate: plan | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T03:35:00+08:00
- Gate: implement | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T04:30:00+08:00
- Gate: review | Verdict: NOT READY | Classification: feature | Timestamp: 2026-06-10T04:50:00+08:00 | Transition: REVIEWED→IMPLEMENTING
- Gate: implement | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T05:10:00+08:00
- Gate: review | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T05:30:00+08:00
- Gate: test | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T05:50:00+08:00
- Gate: handoff | Verdict: PASS | Classification: feature | Timestamp: 2026-06-10T05:55:00+08:00

## Evidence

- `python -m pytest tests/ci tests/guard -q` → 272 passed (Ref: §Test Gate Results for breakdown).
- `python -m pytest tests/guard/test_governance_eval.py -q` → 31 passed; `tests/ci/test_deploy_tiering.py` → 14 passed (deploy whitelist holds).
- Reviewer live evidence: PyYAML-vs-subset field-identical parse; 5 injection vectors inert; two `--format json` runs byte-identical (`cmp`); HIGH-1 old-vs-new wrapper reproduction.
- Validators: sole FAIL = Spec Index completeness pre-ship (resolved by ship-time index entry); `governance eval coverage` WARN wording identical sh/ps1.
- Commits: add417a → c60c4f4 → d884cc6.

## Observability

- Tooling is operator-invoked CLI (stderr errors, distinct exit codes 0/1/2-class); validator advisory surfaces coverage drift on every validate run — no production log sink applicable (framework tooling, not service code).
