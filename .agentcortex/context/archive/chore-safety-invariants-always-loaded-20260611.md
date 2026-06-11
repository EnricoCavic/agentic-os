# Work Log: chore/safety-invariants-always-loaded

| Field | Value |
| --- | --- |
| Branch | chore/safety-invariants-always-loaded |
| Classification | quick-win |
| Classified by | Claude (Fable 5) |
| Frozen | true |
| Created Date | 2026-06-11 |
| Owner | claude-fable-5 |
| Guardrails Mode | Quick |
| Current Phase | ship |
| Checkpoint SHA | afd1944 (base: #223 head — STACKED, depth 3: #222 → #223 → this) |
| Recommended Skills | verification-before-completion (auto), karpathy-principles (auto) |
| Primary Domain Snapshot | none |
| SSoT Sequence | 57 |

## Session Info
- Agent: Claude (Fable 5)
- Session: 2026-06-11T18:00:00+08:00
- Platform: Claude Code (Windows)
- Guardrails loaded: skipped (quick-win; §13 already read this session — Read-Once, no re-read)
- Override: none

## Drift Log
- Skip Attempt: NO
- Gate Fail Reason: N/A
- Token Leak: NO
- ADR-001 amendment written directly (quick-win, owner-approved; ADRs lack a guarded-write path) — logged here per non-ship write discipline.

## Task Description
Owner-approved synthesis of 3-expert panel (token-economics / safety-architecture / simplicity)
following the destructive-command incident audit. Promote the 2 remaining flow-independent safety
invariants to the always-loaded surface; fix the dangling eval protects-tags; minimal parity +
honesty fixes. Owner note: "AI 又發展了一陣子，細節可以優化" — wording may reflect current reality.

**AC:**
1. AGENTS.md §Core Directives gains a capped safety-invariant cluster: existing Destructive
   Command Gate + NEW Secrets Prohibition + NEW Untrusted Tool Output (one line each), with a
   1-line HTML-comment cap/placement-test note (max ~5; promote-one-demote-one; test = hazard
   reachable from any tool call AND irreversible/exfiltrating).
2. governance.yaml: `secret-credential-exposure` protects → AGENTS.md §Core Directives/Secrets
   Prohibition; `prompt-injection-in-tool-output` protects → AGENTS.md §Core Directives/Untrusted
   Tool Output (text lands in SAME commit — no dangling tags in either direction). Coverage runs clean.
3. codex/rules/default.rules gains a secrets prefix_rule (closes the Codex↔Antigravity asymmetry;
   Antigravity already has its secrets line).
4. README EN guardrails intro stops over-claiming ("loaded automatically, enforced at every
   phase" → tier-honest wording); Confidence Gate bullet scoped honestly. zh README mirrored if
   it has the equivalent claim.
5. ADR-001 D3 gains a short dated Amendment: safety invariants carved out of skip-policy
   jurisdiction (D3 governs cost/process rules only); notes the dollar-premise staleness.
6. Compact index regenerated; validators fail=0 both platforms; eval coverage + guard tests green.

**Out of scope (registered, not done here):** T1 pre-commit credential regex (L2 machine layer —
backlog row at ship); adapter copies of untrusted-output line (adapters import AGENTS.md;
skeptic anti-creep ruling); ADR-007-style meta-framework (explicitly rejected by panel).

**§13 compliance**: Deletion-First — net-add (~110 tokens always-loaded) justified: closes 2
incident-shaped gaps (secrets reachable from any tool call + irreversible-on-push; injection
per-tool-call hazard); README over-claim trimmed in same change. ADD-Gate — both new rules
T2 (eval-backed, cases retargeted same commit); secrets has CI TruffleHog as existing machine
backstop and a planned T1 pre-commit layer (backlog).

## Phase Sequence
- bootstrap
- plan
- implement
- ship

## External References
- Expert panel outputs (in-conversation, 3 parallel agents, 2026-06-11) — same-vendor caveat noted; owner is the external signal
- ADR-001 D3 (origin of the skip policy; amendment target)
- governance.yaml protects format precedent: "AGENTS.md §Core Directives/No Bypass Rule" (subsection-style resolves)

## Known Risk
- AGENTS.md is the all-platform prompt — wording errors propagate everywhere. Mitigation: one-line invariants, cluster placement next to existing gate, validators + eval coverage + guard tests before commit. Rollback = revert PR.
- Stack depth 3: merge order #222 → #223 → this; merge-commit strategy required (repo default); retarget + sync commit each level.

## Conflict Resolution
none

## Skill Notes
none

## Phase Summary
- bootstrap: quick-win; stacked on #223 (afd1944); panel synthesis is the plan input; §13 compliance pre-mapped.
- plan: 6 ACs, 6 files (AGENTS.md, governance.yaml, codex rules, README×1-2, ADR-001, compact index); verify = coverage + guard tests + validators | Confidence: 92% — assumption: zh README has an equivalent guardrails-claim section to mirror (verified at implement)
- implement: commit 08b1e77 (6 files, +24/−5); zh README confirmed claim-free (canary untouched); coverage 24 cases + both retargeted protects resolve; guard suite 31 passed; validators pass=100 fail=0 both; zero-coverage 29→30 (security_guardrails §3 now unguarded — accepted: the case better guards the always-loaded line; §3 is procedural duty) | Confidence: 95% — high
- ship: PASS — PR #224 (stacked #222→#223→this); issue #225 + backlog row #71 register the T1 pre-commit credential layer; archive .agentcortex/context/archive/chore-safety-invariants-always-loaded-20260611.md ⚡ ACX

## Gate Evidence
- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T18:02:00+08:00
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T18:04:00+08:00
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T18:20:00+08:00
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-11T18:30:00+08:00

## Evidence
- Commit: 08b1e77 — 6 files changed, 24 insertions(+), 5 deletions(-)
- `run_governance_eval.py --coverage` → 24 cases evaluated; both retargeted protects resolve (no schema/resolution error)
- `pytest tests/guard/test_governance_eval.py` → **31 passed** (protects-resolution suite)
- `validate.sh` → pass=100 warn=11 fail=0 · `validate.ps1` → pass=100 warn=11 fail=0
- zh README verified claim-free (only canary line 5 mentions 工程護欄 — untouched)
- Follow-up: issue #225 + backlog row #71 (T1 pre-commit credential regex)
