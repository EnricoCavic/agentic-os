---
status: research
topic: rpi-qrspi-corroboration
date: 2026-06-03
---

# Research: RPI → QRSPI (Horthy) vs. Agentic OS — External Corroboration & Delta

External trigger: Dexter Horthy (HumanLayer) keynote *"Everything We Got Wrong About
Research-Plan-Implement"* (Coding Agents Conf, 2026-03) + the QRSPI write-ups. Goal:
decide whether any QRSPI lesson is a real, un-covered gap in THIS repo — or whether we
have already converged. DELETE-bias; "they have it" ≠ evidence.

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

## Genuinely-new deltas (honest triage — most already covered)
| QRSPI idea | Status in our repo | Verdict |
|---|---|---|
| Reduce per-phase instruction count | partially (−43% done; still ~90 dirs) | **REAL, highest value** — continue trimming, not adding |
| Questioning phase before research | `brainstorm` exists but is *optional/un-gated* | candidate: make brainstorm the default-on entry for feature, not a separate new gate |
| Structure outline (vertical slice) separate from Plan | mentioned in implement/review, not its own step | LOW — fold a 1-line "vertical-slice + checkpoint" requirement into existing `/plan`, do NOT add a phase |
| Research with ticket hidden (objective map) | not explicit | candidate: 1-line note in `research.md` |
| Subagent context-firewall | covered (2 skills) | **no-op** |
| After-action reports | covered (`/retro`) | **no-op** |

## Suggested Scope (recommendation)
Primary, evidence-backed action is **subtractive, not additive**:
1. **Instruction-budget audit** of the ~90 phase-entry directives → identify honor-system MUSTs with no validator (per Lesson #70) and DELETE/merge them. This is the QRSPI lesson that actually applies and the one our own lessons already mandate. Target: drop phase-entry directive count below the ~85 threshold with enforcement-backed survivors only.
2. Only IF (1) frees budget: fold two ≤1-line refinements into existing workflows (default-on brainstorm for feature; vertical-slice + ticket-hidden research notes). No new phases, no new MUSTs.

## Next Actions
- **Decision needed (`/decide` or ADR-006)**: subtractive instruction-budget pass vs. status-quo. This is an architecture-level tradeoff (governance surface vs. cross-platform parity) → ADR is the right home.
- If approved → `/spec-intake` can consume this file for the budget-audit spec; the two micro-refinements ride as small `quick-win` doc edits, not a feature.
- Do NOT add Questioning/Structure as new gated phases — fails the measured-budget constraint and Lesson #70.

## Official References
- [Horthy keynote](https://www.youtube.com/watch?v=YwZR6tc7qYg) · [QRSPI breakdown](https://alexlavaee.me/blog/from-rpi-to-qrspi/) · [2026 evolution](https://betterquestions.ai/the-necessary-evolution-of-research-plan-implement-as-an-agentic-practice-in-2026/)
- [obra/superpowers](https://github.com/obra/superpowers) · [bostonaholic/rpikit](https://github.com/bostonaholic/rpikit) · [spec-kit](https://github.com/github/spec-kit) · [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- [Advanced Context Engineering (prior talk)](https://www.youtube.com/watch?v=VvkhYWFWaKI) · [Ralph loop](https://linearb.io/blog/dex-horthy-humanlayer-rpi-methodology-ralph-loop)
