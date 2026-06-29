# Work Log: claude/dev-flow-batch3-demonstration

## Header

- Branch: `claude/dev-flow-batch3-demonstration`
- Classification: `architecture-change`
- Classified by: `Claude (Opus 4.8)`
- Frozen: `2026-06-30`
- Created Date: `2026-06-30`
- Owner: `claude-session`
- Guardrails Mode: `Full`
- Current Phase: `ship`
- Diff Base SHA: `3b91905`
- Checkpoint SHA: `bba1106`
- Recommended Skills: `verification-before-completion, red-team-adversarial, karpathy-principles`
- Primary Domain Snapshot: `governance-runtime`
- SSoT Sequence: `97`

---

## Session Info

- Agent: `Claude (Opus 4.8)`
- Session: `2026-06-30 ac13`
- Platform: `claude`
- Continuation of: dev-flow-hardening (Batch 1 #299, Batch 2 #300 shipped). This branch = AC-13 demonstration mechanism (the "Batch 3" the owner sequenced next).

---

## Task Description

Add AC-13 (demonstration over green gates — product-side twin of the gate-honesty ACs) to `docs/specs/dev-flow-hardening.md` and implement the converged 3-expert-panel design: a CI-enforced, anchored demonstration of user-facing surfaces, riding existing rails, with near-zero AI-context (token-ceiling) footprint.

---

## Owner Decisions (signed off)

- Adopt the principle as **AC-13** in dev-flow-hardening (converged panel design): minimal × anchored × no-new-phase.
- Mechanism: CI-enforced golden snapshot of the adopter-visible deploy output + lightweight demonstration receipt; do NOT build README screenshot/golden machinery (no consumer); honest-ceiling stated in spec.
- Timing: this PR comes after Batch 2 (done), before CI/security (AC-7/8/9/12) and AC-10.
- Weight constraint (owner-emphasized): governance must NOT get heavier. Token ceiling is 355,000 with only ~270 headroom. Put the mechanism in test/recipe/tool/CI (0 ceiling cost — validators/tools/tests are NOT lifecycle-scenario detail_refs); keep phase-doc (ship.md) additions to a terse minimum. If the ceiling is breached, STOP and flag for an owner minimal-bump decision (do NOT silently bump).
- AI-discoverability (owner-emphasized): the demonstration requirement must live where the AI actually loads it (ship.md at /ship) AND be machine-enforced (the CI deploy-manifest test), not spec-only.

---

## Plan (converged 3-panel design)

**The decisive principle**: "regenerate ≠ demonstrate" is only solved when the proof is anchored to an artifact CI itself produces by re-running the real path. Deploy is the only user-facing surface CI already executes (`test_deploy_tiering.py` shells real `deploy.sh`), so it is the verified consumer.

1. **Paved one-command demo recipe** — `.agentcortex/tools/demo_deploy.sh` (or documented invocation): deploy into a temp dir + print the adopter-visible view (deployed `current_state.md` head + dry-run inventory). Cost-asymmetry lever; 0 ceiling cost (tooling).
2. **Anchored deploy-manifest snapshot test** — extend `tests/ci/test_deploy_tiering.py`: assert the normalized install/dry-run inventory (tier + rel-path, line-oriented, low-churn — NOT free-text stdout) against a committed golden `tests/ci/fixtures/deploy_manifest_golden.txt`. CI re-runs real `deploy.sh`, so a hand-faked golden diverges and stays red. 0 ceiling cost (test). This IS the demonstration, captured + CI-enforced.
3. **Demonstration receipt (terse, in ship.md)** — ≤2 lines: for changes touching user-facing surfaces (deploy / validator output / README), record a `Demonstration:` line in Work Log `## Evidence` citing the recipe command + captured output; the deploy-manifest CI test is the anchored backstop. Scope-gated by intent (deploy/validator/README touched). Token-minimal.
4. **Spec**: add **AC-13** + an explicit **honest-ceiling** clause — for surfaces CI executes (deploy) the proof is anchored; for surfaces nothing executes (README render, holistic "reads right") it stays honestly ADVISORY (no fake "we enforce it"; no screenshot harness — no consumer).
5. **Do NOT**: build README/full-stdout golden snapshots; add a new phase; add a heavy receipt the AI can fabricate without a CI anchor.

**Token discipline**: after implement, run `analyze_token_lifecycle.py`; aggregate MUST stay ≤ 355,000. If over, STOP — flag for owner (do not bump).

**Test discipline**: run the WHOLE `tests/ci/test_deploy_tiering.py` (not a -k slice — the recurring footgun) + the full CI-equivalent not-slow set before push.

**Commit grouping**: (1) recipe + manifest golden + test; (2) ship.md terse receipt line; (3) spec AC-13 + honest-ceiling.

Constraints: only /ship writes SSoT; no branch-protection mutation; English artifacts; preserve all existing behavior; small/reversible.

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-30T00:00:00Z
- Gate: plan | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-30T00:00:00Z
- Gate: implement | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-30T00:00:00Z
- Gate: review | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-30T12:00:00Z | Source: independent fresh-context review (Ready to merge: yes; all AC-13 sub-claims PROVEN)
- Gate: test | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-30T12:00:00Z | Source: 554 not-slow CI-equivalent passed; test_deploy_tiering.py 32 passed; token 354,976/355,000; index fresh
- Gate: handoff | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-30T12:00:00Z | ship:[doc=docs/specs/dev-flow-hardening.md][code=tests/ci/test_deploy_tiering.py,tests/ci/fixtures/deploy_manifest_golden.txt,.agentcortex/tools/demo_deploy.sh][log=.agentcortex/context/work/claude-dev-flow-batch3-demonstration.md]
- Gate: ship | Verdict: PASS | Classification: architecture-change | Timestamp: 2026-06-30T12:00:00Z

## Phase Summary

- implement: 5 files created/modified (demo_deploy.sh, conftest.py, deploy_manifest_golden.txt, test_deploy_tiering.py+1test, ship.md+1line, spec+AC-13); 554 not-slow tests pass; token ceiling 354,976/355,000.
- ship: PASS; PR #301 merged 046c368; archive path claude-dev-flow-batch3-demonstration-20260630.md

## Drift Log

- Continuation of dev-flow-hardening; off main 3b91905 (post Batch-2 merge #300).
- ADR Coverage: no new ADR; AC-13 extends the gate-honesty principle to the product/demonstration dimension.
- Token tight: ship.md wording compressed after first attempt exceeded ceiling by 72 tokens (355,072 → 354,976).
- Domain Doc Gate (AC-15) skip justification: spec primary_domain=governance-runtime; governance-runtime.log.md does not exist. Domain Decisions span the full dev-flow-hardening spec (all batches 1-3+). Per-batch consolidation would produce partial/stale L2 entries. Deferred to final batch ship when spec reaches status:shipped.

---

## Evidence

- Demonstration: `bash .agentcortex/tools/demo_deploy.sh` → deploy OK, deployed current_state.md head = template placeholders, inventory printed (30 files shown). Full output captured in session.
- CI anchor: `test_deploy_manifest_snapshot` — 198-entry normalized golden committed at `tests/ci/fixtures/deploy_manifest_golden.txt`; asserts tier+rel-path only (no version/sha/timestamp drift).
- Token ceiling: `python .agentcortex/tools/analyze_token_lifecycle.py` → 354,976 total (ceiling 355,000, headroom 24).
- Test suite (not-slow): `python -m pytest tests/ci/ tests/guard/ .agentcortex/tests/ -m "not slow" -q` → 554 passed, 64 deselected.
- `test_deploy_tiering.py` full run: 32 passed (includes new test_deploy_manifest_snapshot).
- Compact index: `generate_compact_index.py --root . --check` → fresh.

---

## Test Gate Results

- `python -m pytest tests/ci/test_deploy_tiering.py -q` → 32 passed (includes new `test_deploy_manifest_snapshot`)
- `python -m pytest tests/ci/ tests/guard/ .agentcortex/tests/ -m "not slow" -q` → 554 passed, 64 deselected
- Anchor perturbation: `test_deploy_manifest_snapshot` FAIL-on-drift confirmed (golden diverges when golden is tampered → red)
- Token ceiling: `python .agentcortex/tools/analyze_token_lifecycle.py` → 354,976 / 355,000 (headroom 24)
- Compact index: `python .agentcortex/tools/generate_compact_index.py --root . --check` → fresh

---

## Known Risk

- Rollback: revert PR via `gh pr revert <PR#>` or `git revert <merge-sha>`. Untracked state unaffected (gitignored).
- Token headroom: only 24 tokens remaining before ceiling. Any future ship.md addition to this spec area must be weighed carefully.
- AC-7/8/9/10/12 remain open; spec stays `status: draft` until all ACs land.
- Observability: governance-runtime tooling; no production logging infrastructure — error paths surface via pytest/validate.sh CI output. Logged as Known Risk per §Observability Readiness.

## Observability

No production logging infrastructure (governance tooling only). Error sink: pytest/validate.sh CI output. Rollback detection: CI checks return to green after revert.

## Resume

State: AC-13 branch off 3b91905; converged design locked; implement dispatched.
Next: implement recipe + manifest golden test + terse ship.md receipt + spec AC-13/honest-ceiling; verify token ceiling ≤355k; review; test; ship.
Context: token headroom is only 270 — keep the mechanism in test/tool/CI, ship.md minimal.

### Read Map
- `docs/specs/dev-flow-hardening.md`
- `tests/ci/test_deploy_tiering.py`
- `.agentcortex/bin/deploy.sh`
- `.agent/workflows/ship.md`
- `.agentcortex/tools/analyze_token_lifecycle.py`

### Skip List
- `.agentcortex/context/.guard_receipt.json`, `.guard_receipts/*`, archive/*, `.acx-local/*`

### Context Snapshot
Resume from main 3b91905. Converged design + owner decisions above are authoritative.

---

## Design Reference

none
