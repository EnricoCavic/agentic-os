---
status: accepted
date: 2026-06-14
classification: architecture-change
primary_domain: downstream-adaptability
deciders: "@kbwen (human steer + flexibility directive) + Claude Opus 4.8 (1M) + 5-expert panel (architect / downstream-integrator / extensibility / skeptic / agent-safety), each grounded against real files (acx-reviewer.md:9, bootstrap §3.6a, deploy.sh, recover_worklog_lock.py)"
applies_to:
  - ".agent/workflows/bootstrap.md"
  - ".agent/config.yaml"
  - ".agentcortex/tools/recover_worklog_lock.py"
  - ".agent/workflows/routing.md"
lifecycle:
  owner: "/adr"
  review_cadence: on-event
  review_trigger: "When a downstream needs a capability kind the schema cannot express, OR a platform changes its harness/subagent model"
  supersedes: none
  superseded_by: none
---

# ADR-007: Downstream Capability Declaration Seam

## Context

Downstream is now using the framework in **heterogeneous** ways: projects bring
many of their own skills, drive work through **harness/subagent fan-out**, and
already run their own work-management flows. The framework is strong at
**preservation** — ADR-004 (override layer), ADR-005 (`custom-*` namespace +
deploy tiering), capability-by-presence — but weak at **integration**:
downstream skills/agents/trackers *coexist* but cannot plug into core machinery.

### Evidence (Verified)

- **Custom skills are second-class**: `custom-*` skills are deploy-preserved
  (ADR-005, sim-verified `custom-* silent`) but cannot auto-activate — the
  `bootstrap.md §3.6` rule table is framework-owned and source-regenerated, and
  pinning a custom skill hits `bootstrap.md §3.6a` step 3 *"validate IDs against
  the rule table / compact-index; warn on unknown IDs; **ignore them**"*. A
  `custom-*` ID is always "unknown".
- **Subagent fan-out has no declared policy**: the single-writer Work Log lock
  (`worklog_lock.mode: blocking`, default) makes every phase-entry call
  `recover_worklog_lock.py ensure`; parallel `acx-*` shims on one branch each
  call it → first wins, the rest get exit 2 → **Gate FAIL**. The
  `subagent-driven-development` / `dispatching-parallel-agents` skills are
  advisory prose, not a declared contract.
- **No seam for an external tracker**: the framework owns the work-mgmt spine
  (SSoT, Work Logs, gates); there is no declared place to say "Linear/Jira is our
  tracker", so the answer defaults to a dismissive "go write your own skill".

A 5-expert panel **split**: architect/extensibility/integrator proposed a
present-only declaration seam; the skeptic argued *decline-all* (no verified
in-repo consumer; `OPTIMIZATION_ROADMAP.md:22-31` already retracted ~20
conceptual-port tickets). **The maintainer's directive resolves the split**:
prioritize downstream **flexibility/adaptability**, and **keep the skeptic's
anti-bloat constraints as design guardrails** rather than as reasons to decline.
This mirrors ADR-004's logic — *the arrival of real downstream heterogeneity is
the new evidence that flips the calculus* — while refusing to let "flexible"
become "bloated".

## Decision

**Add one present-only, opt-in, gate-capped declaration file that lets downstream
contribute capabilities the framework reads but never lets relax a gate.**

1. **File**: `.agentcortex/context/private/downstream-capabilities.yaml` —
   gitignored runtime state, **never shipped by deploy** (so it is conflict-free
   on `git pull` and auto-preserved exactly like `custom-*`). Path registered in
   `.agent/config.yaml §downstream_capabilities`, mirroring `§user_preferences`.
2. **Loader**: a new `bootstrap.md §1b "Load Downstream Capabilities"` step,
   present-only and lazy — a structural twin of `§1a` (override) and `§3.6a`
   (user-preferences). **Present → parse + merge; absent → zero reads, zero
   tokens.** Malformed → warn-once, never block. Read-Once: loaded once at
   session start, recorded in Work Log `## Session Info`; later phases trust it.
3. **Four opt-in capability kinds** (each absent by default):
   - **`skills:`** — register `custom-*` skills into auto-activation. Their IDs
     are *unioned* into the `§3.6a` step-3 validation set, so a pinned/declared
     `custom-*` skill resolves instead of "unknown → ignore". **Capped**:
     `trigger_priority` ≤ `contextual`, clamped to a declared `phase_scope`,
     conflict-matrix-checked, `custom-*` names only. (Problem #1)
   - **`subagent_policy:`** — `read-only` (default) or `governed` (opt-in).
     `read-only` = subagents fan out / return evidence; the **primary is the sole
     Work Log writer, gate owner, and sentinel emitter** (no lock contention).
     `governed` = downstream explicitly opts into delegating mutation, but Work
     Log writes stay primary-only. **The `recover_worklog_lock.py` same-owner
     short-circuit is DEFERRED, NOT shipped here** (see Alternatives): it has no
     verified parallel-shim consumer and would weaken the single-writer
     guarantee. `read-only` makes contention moot *without touching the lock* —
     subagents never acquire it. (Problem #3 — the declaration ships now; the
     lock-code change waits for a consumer + a write-side ownership check.)
   - **sentinel clarification** (doc, not config): the `⚡ ACX` sentinel is
     **primary-emitted**; a subagent's output returns to the primary (internal),
     not as a user-facing chat turn, so subagents neither emit nor need it.
     (Problem #4)
   - **`trackers:`** — **advisory declaration only**. The framework emits a
     phase-entry note ("sync `<tracker>` via `<custom-skill>`"); it builds **no
     sync machinery**, and a tracker declaration can **never** gate a phase.
     (Problem #5)
4. **Hard design guardrails — gate-relaxation is UNREPRESENTABLE by schema**: a
   contribution can never raise `trigger_priority` above `contextual`, declare a
   gate, add a ship edge, authorize concurrent Work Log writers, or make a
   tracker blocking. The validator **rejects** any file that violates these.

**Honest enforcement boundary** (per `[enforcement][HIGH]`): the
*machine-enforceable* part is **structural T1** — `validate.sh`/`validate.ps1`
assert (i) `bootstrap.md` still ships the `§1b` load step (mirror the ADR-004
line-528 override-step check) and (ii) if the file is present, every
`skills[].id` is `custom-*` and no field exceeds the caps (schema gate-safety).
"Did the agent honor the declaration" is honor-system advisory, like the override
read and the Sentinel — **no fake MUST**.

## Alternatives Considered

- **Decline all three (skeptic's verdict)** — no verified in-repo consumer;
  pinning + `acx-*` shims + `custom-*` skills "already cover it";
  `OPTIMIZATION_ROADMAP.md:22-31` retracted ~20 conceptual ports. **Rejected**:
  the maintainer's explicit flexibility directive is the new evidence (mirrors
  ADR-004's "downstream arrival flips it"), and decline leaves real rigidity
  (custom-* second-class; lock FAILs same-owner fan-out). The skeptic's valid
  concerns — attack surface, bloat — are neutralized **by the gate-cap
  guardrails** (opt-in, present-only, unrepresentable gate-relaxation), not by
  declining. Flexibility is delivered *with* the guardrails, not instead of them.
- **Let downstream edit `trigger-registry.yaml` directly** — **Rejected**: it is
  force-update/source-regenerated core (ADR-005); downstream edits are silently
  overwritten on deploy, reintroducing the exact silent-loss footgun ADR-005
  closed. Registration must live in never-shipped `context/private/`.
- **A new eager `@import` capabilities file** — **Rejected** (same as ADR-004
  round-1): pins a near-empty file into every turn's warm-cache prefix; violates
  `§Read-Once`/`§Context Pruning`. Use the lazy present-only pattern.
- **Same-owner lock short-circuit (loosen `recover_worklog_lock.py` from
  same-session to same-owner)** — **DEFERRED, not shipped**: the lock never
  guarded *writes* (`worklog-lock-blocking` Non-goal), so "subagents are
  read-only" is assumed, not enforced; an owner-only short-circuit + a `governed`
  policy could let two same-owner sessions concurrently write one Work Log,
  reopening the lost-update `blocking` prevents. No verified parallel-shim
  consumer. Ship the `read-only` declaration now (no lock change); revisit the
  lock code only when a real consumer needs governed parallel mutation **and** a
  write-side ownership check lands.
- **Flip the lock to `advisory`** — **Rejected**: re-opens concurrent Work-Log
  corruption (`worklog-lock-blocking` spec).

## Consequences

**Positive**: downstream gets ONE flexible, opt-in, token-safe place to extend
the framework (skills / subagent-policy / tracker) without editing framework
files → additive forks stay `git pull`-clean (both `custom-*` and
`context/private/` are never-shipped); `custom-*` skills become
auto-activatable; the `read-only` subagent policy avoids lock contention by
design (the same-owner lock-code fix is deferred to a verified consumer); the framework
moves from "owns everything" toward "**owns the kernel, downstream contributes
(capped) capabilities**". **Generalizes to unknown future flows**: a new
capability kind = a schema stanza + one validator line + one loader clause —
never an AGENTS.md gate edit.

**Negative / accepted**: per-agent honoring is honor-system (the validator proves
the schema is gate-safe + the step ships, not that the agent merged the
declaration) — same boundary as ADR-004. A malformed file warns-and-skips. The
same-owner short-circuit assumes the harness propagates a **stable shared
`owner`** to its subagents; a harness that gives each subagent a distinct owner
still contends (documented; "subagents inherit the primary's `owner`" is itself
advisory).

**Out of scope (honest boundaries)**: custom-skill **auto-discovery** without an
explicit declaration entry (auto-activating unvetted skill descriptions is an
untrusted-activation surface — the skeptic's valid point; we require opt-in);
external-tracker **sync** machinery (advisory note only; real sync is a
downstream `custom-*` skill); the general **validator-content-tolerance**
principle (problem #6 — its own ADR/spec, sequenced next); **multi-writer Work
Log** / concurrent governed mutation (`subagent_policy: governed` authorizes
evidence-producing fan-out, NOT concurrent Work Log writes).
