---
status: accepted
date: 2026-06-14
classification: architecture-change
primary_domain: safety-governance
deciders: "@kbwen (human steer; flagged the no-python tradeoff) + Claude Opus 4.8 (1M) + 5-expert panel (agent-safety lens led), grounded against AGENTS.md §Core Directives, deploy.sh L725/L910-927, .githooks/pre-commit.guard-ssot.sample:23-41, and the 2026-06-11 data-loss incident archive"
applies_to:
  - "AGENTS.md"
  - ".agentcortex/bin/deploy.sh"
  - ".agentcortex/bin/deploy.ps1"
  - ".githooks/pre-commit.guard-ssot.sample"
  - ".agentcortex/tools/scan_credentials.py"
lifecycle:
  owner: "/adr"
  review_cadence: on-event
  review_trigger: "When a new always-loaded safety invariant is added/removed, OR a platform changes how subagents inherit context"
  supersedes: none
  superseded_by: none
---

# ADR-008: Portable Safety Floor

## Context

The three safety invariants — **Destructive Command Gate**, **Secrets
Prohibition**, **Untrusted Tool Output** — correctly live on the always-loaded
`AGENTS.md §Core Directives` surface (per Global Lesson `[rule-placement][HIGH]`:
hazard reachable from any tool call, irreversible/exfiltrating → always-loaded).
Two real gaps surface once downstream drives work through **harness/subagent
fan-out**:

### Evidence (Verified)

- **The floor evaporates for non-shim harnesses.** On Claude, `acx-*` shims
  (`.claude/agents/acx-reviewer.md:9` *"Execute review.md verbatim"*) re-inject
  governance by re-running the gated workflow. But that is **Claude-only**:
  Codex / Gemini / a custom orchestrator have **no** such mechanism — they must
  re-inject `AGENTS.md`, yet the safety floor is welded into the ~114-line
  monolith, so there is **no cheap ~15-line nucleus** to inject into every
  ephemeral subagent. A subagent that loaded neither gets no floor.
- **The secrets T1 is dead downstream.** The pre-commit credential pre-screen
  (`.githooks/pre-commit.guard-ssot.sample:23`) references
  `.agentcortex/tools/scan_credentials.py`, but that scanner is **absent from
  both `deploy.sh` whitelist spots** (L725 string + L910-927 array; `deploy.ps1`
  is a pure bash delegator that inherits the change) **and** the hook **skips when Python is absent** (`:38-40`). So the
  advertised *"block secrets before object history"* control **silently no-ops**
  on a no-python downstream — violating the framework's own no-python doctrine
  (ADR-006 family).
- **Real failure mode**: the 2026-06-11 data-loss incident (an autonomous agent
  ran `rm -rf` without asking; partial Windows failure → git fell through to the
  parent repo) is exactly the autonomous-subagent-without-floor case.

## Decision

**Factor the always-loaded safety floor into a portable, environment-independent
nucleus, and make the secrets control real without Python.**

1. **Fence** the 3 invariants in `AGENTS.md` with
   `<!-- ACX:SAFETY-FLOOR:BEGIN -->` / `<!-- ACX:SAFETY-FLOOR:END -->`. The
   invariant **text is byte-unchanged** (so `governance.yaml` eval cases + every
   adapter canary still pass); the fence is an HTML comment (invisible to
   humans/LLMs, greppable by tooling). **The floor STAYS on the always-loaded
   surface — the fence does NOT move it off** (per `[rule-placement]`).
2. **Generate + freshness-check (committed), NOT slice-at-deploy**:
   `.agentcortex/AGENTS.safety.md` is a **committed generated file** (~15 lines =
   the fenced span), guarded by a `validate.sh`/`validate.ps1` **freshness check**
   that asserts its content equals the current fenced span (the
   `generate_compact_index.py --check` pattern: FAIL on stale, SKIP when the
   generator is absent). A deploy-time text slice is **rejected**: AGENTS.md is
   scaffold-tier, so a downstream-edited AGENTS.md would be sidecar'd and silently
   disagree with a freshly-sliced nucleus, and the slice would bypass the
   manifest/EOL machinery. Committed + freshness makes "nucleus == fenced
   invariants" a **T1** guarantee. `deploy.sh` ships it like any core file;
   `deploy.ps1` is a pure bash delegator (no separate slicer). Any non-shim
   harness injects this ~15-line nucleus into every dispatched subagent.
3. **Primary-delegation contract** (T0 advisory): add ONE sentence inside the
   fence — *when delegating to a subagent, the primary confirms the floor is in
   the subagent's context AND treats any shell-mutation a subagent proposes as
   subject to the same Destructive Command Gate (the subagent's own confirmation
   does not satisfy it; the primary re-confirms).* Marked **advisory — not
   machine-enforced**; only an operator-owned harness wrapper can intercept a
   runtime `rm`.
4. **No-python credential floor** (the secrets invariant's T1): redesign the
   pre-commit pre-screen so a **shell + PowerShell regex floor — a deliberately
   narrow, redaction-safe, FP-free SUBSET (unambiguous prefixes only: AWS `AKIA`,
   PEM header, `ghp_`; per-staged-file; value never printed) — is the canonical,
   Python-independent control** (the `validate.sh ↔ validate.ps1` parity pattern,
   preserving `scan_credentials.py`'s no-FP corpus). `scan_credentials.py` stays
   the **richer path when Python is present** and is added to **both** `deploy.sh`
   whitelist spots (L725 string + L910-927 array; `deploy.ps1` inherits via
   delegation). Narrow > recall: a blocking hook that false-positives gets
   disabled. (See Alternatives — the maintainer's flagged tradeoff.)

**Honest signal tiers** (per `[enforcement][HIGH]`):
- **Secrets** — **T1** at the git commit boundary: the shell/PS regex floor
  blocks before object history with **no Python dependency**; `.py` enriches when
  present. (Restores the currently-dead control.)
- **Destructive Command Gate** — **T1 only at the git boundary** (a `pre-push`
  hook can block `--force` to protected refs); **`rm -rf` at the filesystem
  layer = T0 advisory** — no framework-side hook intercepts a runtime `rm`; only
  a downstream harness wrapper can, shipped as an opt-in sample, never enforced
  remotely.
- **Untrusted Tool Output** — **T0** reasoning constraint with a **T2** eval
  backstop (the existing `governance.yaml` prompt-injection case).

**§13 ADD-Gate justification**: net new always-loaded `AGENTS.md` text ≈ 2 comment
lines + 1 delegation sentence; justified by a real data-loss incident + the
no-floor-for-non-shim-subagents gap. **Deletion-First**: the fence *enables* an
~85%-smaller subagent inject downstream (nucleus replaces monolith for injection).

## Alternatives Considered

- **Credential-floor fork — (A) shell+PS regex canonical + `.py` optional
  [CHOSEN] vs (B) `.py`-CI-only.** Chose **A**: it honors the no-python doctrine
  (every control has a no-python path), and the hook's whole purpose — block
  *before* object history — is something CI (post-commit) structurally cannot do;
  **B** leaves no-python downstream with zero pre-commit control (the status-quo
  defect). Cost of A: a curated regex set duplicated in shell + PS that must stay
  in parity with `scan_credentials.py` — mitigated by parity tests + a shared
  pattern source (same discipline as `validate.sh ↔ ps1`). *(The maintainer
  explicitly said "deploy not adding the `.py` is reasonable; downstream may lack
  Python, so there must be another way" → A.)*
- **A hand-maintained separate `AGENTS.safety.md`** (not generated). **Rejected**:
  two sources of truth for one MUST → drift; violates one-canonical-file.
  Generate-on-deploy from the fenced span.
- **Force every subagent through the full 5-gate governance.** **Rejected**:
  ephemeral subagents cannot carry the session state (Work Log / lock /
  classification); forcing it guarantees non-compliance and erodes the floor's
  credibility; contradicts the framework's own quick-win/tiny-fix fast-paths.
- **Mirror the floor into every platform adapter "for completeness".**
  **Rejected** (the `safety-invariants-always-loaded` panel already ruled):
  adapters `@import` AGENTS.md; more copies = more drift, zero added protection.
- **An ADR-style "meta-framework for safety inheritance".** **Rejected**: the
  fence is ~2 lines; a meta-framework is pure ceremony.

## Consequences

**Positive**: the safety floor becomes **portable** — any harness (Claude shim
OR Codex/Gemini/custom) can cheaply inherit the ~15-line nucleus; the secrets T1
works on no-python downstream (restores an advertised, currently-dead
protection); single-source/generated keeps eval cases + canaries valid; net
always-loaded cost ≈ 3 lines.

**Negative / accepted**: **`rm -rf` at the filesystem layer stays T0 advisory**
even after this — no framework-side interception is possible (honest boundary;
the incident's specific failure remains advisory unless a downstream harness
wrapper gates it). The shell/PS regex floor is a curated **subset** of
`scan_credentials.py`'s detection (a pre-commit floor, not full entropy
analysis) — accepted; TruffleHog CI remains the post-commit backstop. A harness
that injects **neither** AGENTS.md **nor** the nucleus is unreachable by any
instruction (only an operator-owned wrapper helps). The committed nucleus is downstream-MUTABLE: a
downstream may edit their own `AGENTS.md` / nucleus, and the freshness `--check` then WARNs
(not FAILs) downstream — the documented override-tolerance stance. An intentional-override-
vs-accidental-drift marker (a security-review suggestion) is DEFERRED to the general
validator-content-tolerance principle (#6), per evidence-before-adding: the WARN already
surfaces drift, and overriding one's own always-loaded floor is an allowed, documented choice.

**Out of scope (honest boundaries)**: enforcing per-subagent that the floor was
injected (honor-system at the harness boundary; the validator only proves the
deploy slice + the fence ship); runtime `rm -rf` filesystem interception
(operator-wrapper territory); changing any invariant's *text* (this ADR only
fences + slices + makes the secrets control Python-independent).
