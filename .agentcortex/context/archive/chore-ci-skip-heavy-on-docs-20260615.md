# Work Log: chore-ci-skip-heavy-on-docs

| Field | Value |
|:---|:---|
| Branch | chore/ci-skip-heavy-on-docs |
| Classification | quick-win |
| Owner | KbWen (Claude Opus 4.8) |
| Current Phase | IMPLEMENT |
| Checkpoint SHA | b623744 |
| Created | 2026-06-12T03:40:00Z |

## Session Info
- 2026-06-12 — Claude Opus 4.8 — CI optimization. Trigger: owner observed PRs sit ~8–10 min. Root cause: every PR (incl. docs-only) runs `test-windows` (full pytest on windows-latest, ~8 min) though only 3 fast ubuntu checks are branch-protection-required. Fix: add a `changes` scope-detector job; skip the 4 expensive jobs (+ Semgrep) on docs-only changes.

## Drift Log
- 2026-06-12 — Direct SSoT write (current_state.md Ship History + Update Sequence 60→61) without guard_context_write.py; permitted ship-time write, logged per AGENTS.md fallback clause.

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-12T03:40:00Z
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-12T03:40:00Z
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-12T03:42:00Z
- Gate: review | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-12T03:55:00Z
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-12T03:58:00Z

## Evidence
- Diagnosis: required checks = only Framework Validation / ShellCheck / Check Markdown Links (all ubuntu, seconds). Long pole = Pytest (Windows) ~8 min. Recent run wall-clock 8–10 min (gh run list). deploy.sh ships only .github/ISSUE_TEMPLATE + PR template — NOT .github/workflows or tests/, so downstream does NOT inherit this CI.
- Scope-detector logic unit-tested locally: docs-only (README/llms.txt/docs/*/.agentcortex/context/*) → heavy=false; code/governance/CI/mixed → heavy=true.

## Phase Summary
- bootstrap: quick-win — CI config optimization, 2 workflow files, no app code. Path-gate heavy jobs on docs-only changes; required checks stay always-on (branch protection intact).
- implement: `changes` detector + 4 gated jobs in validate.yml, Semgrep gated in security.yml. YAML parse OK; validate.sh fail=0.
- review: heavy path validated on live runner (PR #231, changes job success → gated jobs ran + passed); gating structure verified by yaml introspection (3 required jobs ungated). Evidence-based PASS.
- ship: SSoT Ship History recorded; PR #231 open; required checks fast-green so merge is unblocked without waiting on the self-validating Windows run.
