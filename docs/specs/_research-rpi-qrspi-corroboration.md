---
status: research
topic: rpi-qrspi-corroboration
date: 2026-06-03
---

# Research: RPI → QRSPI (Horthy) vs. Agentic OS — External Corroboration & Delta

External trigger: Dexter Horthy (HumanLayer) keynote *"Everything We Got Wrong About
Research-Plan-Implement"* (Coding Agents Conf, 2026-03) + the QRSPI write-ups. Goal:
map how each QRSPI lesson lands against THIS repo. DELETE-bias; "they have it" ≠ evidence.

> **Scope discipline (do NOT prematurely converge).** Every detail below is a potential
> direction. "We already have a mechanism for X" is NOT proof the deeper failure mode X
> points at is solved — a skill/rule that *names* a concern ≠ the concern handled. Items
> are framed `signal → our current mechanism → deeper question still open`, with **no
> closing verdict**. Convergence to a concrete scope happens only when the work is
> actually picked up — re-research then, fresh. (Memory: `feedback-dont-narrow-research-scope`.)

## Key Facts

### Our current instruction budget (measured 2026-06-03)
- Always loaded / turn: `AGENTS.md` ~2,194 tok (22 MUST/NEVER-class directives) + `CLAUDE.md` ~241 tok.
- Added at every non-tiny-fix phase entry: `engineering_guardrails.md` ~5,453 tok (**65 hard directives**) + `shared-contracts.md` ~793 tok + `security_guardrails.md` ~745 tok.
- → **~90 MUST/NEVER-class directives and ~9,400 governance tokens live at a phase entry**, before SSoT/Work Log/code. Bootstrap adds `bootstrap.md` ~7,718 tok.
- Horthy's failure threshold ("model silently skips deepest-buried steps") is cited at **~85+ instructions**. We sit at/just above it — even after the PR #112 cut (`AGENTS.md` 191→98 lines, −43%, backlog #38).

### What we have ALREADY converged on (independent of Horthy)
- **Magic-words / honor-system critique** = our Global Lesson #70 `[enforcement][HIGH]`: every MUST relying on self-attestation (incl. the `⚡ ACX` sentinel) is "theatre"; every MUST needs a hook/validator/test or should be **DELETED**. Identical conclusion to QRSPI's "if a tool needs magic words, the tool is broken."
- **Context-firewall subagents** = skills `dispatching-parallel-agents` + `subagent-driven-development`.
- **Questioning-before-build** = `brainstorm.md` workflow + `spec-intake` decomposition + `/decide`.
- **40–60% compaction / fresh context** = `token-governance.md` + `context-budget.md` + handoff-trigger-occupancy (Shipped 2026-05-31).
- **After-action / lessons at phase boundary** = `/retro` + Work Log Drift/Evidence + Global Lessons registry.
- **Worktree isolation for implement** = `using-git-worktrees` skill.
- **Plan-reading illusion** guard = `engineering_guardrails §4.5` Anti-Rationalization write-before-verdict tripwire.

### Similar-project landscape (verified)
| Project | Closest-to-us trait | Their distinctive move |
|---|---|---|
| Horthy QRSPI | R-P-I core | adds Questioning + Structure stages; "fewer directives per phase" |
| obra/superpowers | mandatory approval gates + 2-stage review | auto-triggering skills; enforced TDD RED-GREEN |
| bostonaholic/rpikit | phase approval gates | parallel research subagents + worktree default |
| teambrilliant/claude-RPI | persistent sessions (≈ our Work Log) | **archived → migrated to plugin-skill system** |
| BMAD-METHOD (46k★) | SDLC gates | 12+ role agents |
| GitHub spec-kit (93k★) | "constitution" ≈ our guardrails | 30+ agent targets |

## Constraints Found
- **Cross-platform parity is our moat** (Claude/Codex/Gemini/API). Every comparable project is Claude-centric. Any adopted idea MUST hold across platforms or be rejected — see memory `feedback_cross_platform_parity`.
- **No new honor-system MUST** (Lesson #70 + #72): a new phase/gate without a validator is anti-help. Adding stages *increases* the instruction budget we just measured as near-threshold — the opposite of QRSPI's actual fix.
- The thing QRSPI optimizes FOR (fewer directives/phase) is in tension with our reflex (add a gate). The measurement above is the binding constraint.

## Direction space (open — do NOT prematurely converge)
Each row is a live direction. "Our current mechanism" is what *exists*, not proof the
deeper question is closed. Re-interrogate every row when the work is picked up.

| QRSPI signal | Our current mechanism | Deeper question still open |
|---|---|---|
| Reduce per-phase instruction count | −43% done (PR #112); still ~90 dirs at entry | Which of the ~90 are honor-system w/o validator? Is the threshold even the right metric, or is *ordering / burial depth* the real failure? |
| Questioning **before** research | `brainstorm` workflow exists, but optional/un-gated | Do agents actually run it? Is "optional questioning" functionally skipped? Should questioning be structured/multi-agent rather than freeform? |
| Structure outline (vertical slice) separate from Plan | mentioned in implement/review/guardrails | Is "mentioned" enough, or does the *plan-reading illusion* survive because structure is never a distinct, checkable artifact? |
| Research with ticket **hidden** (objective map, no persuasion) | not explicit | Does our `/research` produce a factual map or a solution-biased narrative? Worth testing on a real task. |
| Subagent **context-firewall** | 2 skills (`dispatching-parallel-agents`, `subagent-driven-development`) | Skills *exist* — but is `/research` actually wired to use them by default, or do they sit unused? Coverage-in-form ≠ coverage-in-practice. |
| Per-phase **after-action** reports | `/retro` + Drift/Evidence + Lessons registry | `/retro` is coarse/session-level; QRSPI's is per-phase. Is the finer granularity a real gain we're missing? |
| Magic-words / honor-system critique | Lesson #70 `[enforcement]` (same conclusion) | We *named* it — but is it *applied*? How many live MUSTs still violate it (incl. `⚡ ACX`)? |

> None of the above is closed as "no-op." Where we have a mechanism, the open question is
> whether it addresses QRSPI's *deeper* failure mode or merely shares its vocabulary.

## Candidate strands (NOT a converged scope)
These are ways in, not a ranked plan. Backlog #69 currently parks ONE strand (the
instruction-budget audit) because it is the most measurable entry point — that choice is
a starting handle, **not** a decision that the other strands are out of scope.

- **Strand A — instruction-budget audit** (most measurable): enumerate the ~90 phase-entry directives; mark which have a hook/validator/test (Lesson #70). Subtractive where un-enforced. *Open even here:* is directive *count* the right metric, or is burial-depth/ordering the real driver of silent skips?
- **Strand B — questioning/research quality**: test whether `/research` produces a factual map vs. a persuasive narrative, and whether optional brainstorm is de-facto skipped. May reveal a deeper gap than "add a step."
- **Strand C — structure-as-artifact**: whether the plan-reading illusion survives because vertical-slice structure is never a distinct checkable output.
- **Strand D — mechanism-in-practice audit**: do the context-firewall subagent skills actually get used, or do they sit unused? (coverage-in-form vs in-practice).
- **Strand E — Lesson #70 application audit**: how many live MUSTs still violate our own enforcement rule.

## Next Actions
- **When picked up: re-research the full direction space first** (per `feedback-dont-narrow-research-scope`) — do not start from this file's framing as settled. Treat every row of the Direction-space table as a question to re-open with fresh eyes.
- A decision (`/decide` or **ADR-006**) is likely needed for any strand that touches `AGENTS.md` / `engineering_guardrails.md` (architecture-level: governance surface vs. cross-platform parity).
- Hard constraint that survives across strands: **no new honor-system MUST** (a new phase/gate without a validator both raises the measured budget and violates Lesson #70). Cross-platform parity required.
- `/spec-intake` can consume this file once a strand is chosen — but choosing a strand ≠ closing the others.

## Official References
- [Horthy keynote](https://www.youtube.com/watch?v=YwZR6tc7qYg) · [QRSPI breakdown](https://alexlavaee.me/blog/from-rpi-to-qrspi/) · [2026 evolution](https://betterquestions.ai/the-necessary-evolution-of-research-plan-implement-as-an-agentic-practice-in-2026/)
- [obra/superpowers](https://github.com/obra/superpowers) · [bostonaholic/rpikit](https://github.com/bostonaholic/rpikit) · [spec-kit](https://github.com/github/spec-kit) · [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- [Advanced Context Engineering (prior talk)](https://www.youtube.com/watch?v=VvkhYWFWaKI) · [Ralph loop](https://linearb.io/blog/dex-horthy-humanlayer-rpi-methodology-ralph-loop)
