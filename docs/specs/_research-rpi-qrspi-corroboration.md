---
status: research
topic: rpi-qrspi-corroboration
date: 2026-06-03
---

# Research: RPI → QRSPI (Horthy) vs. Agentic OS — Full-Flow Reference Study

External trigger: Dexter Horthy (HumanLayer) keynote *"Everything We Got Wrong About
Research-Plan-Implement"* (Coding Agents Conf, 2026-03) + the QRSPI write-ups + the
original *Advanced Context Engineering for Coding Agents* (ace-fca) doc. Deep re-read of
all sources 2026-06-03.

> **Scope discipline (do NOT prematurely converge).** Every detail below is a potential
> direction. "We already have a mechanism for X" is NOT proof the deeper failure mode X
> points at is solved — a skill/rule that *names* a concern ≠ the concern handled.
> Convergence to a concrete scope happens only when the work is actually picked up —
> re-research then, fresh. (Memory: `feedback-dont-narrow-research-scope`.)

> **Reframe of the core question.** It is NOT "we only have RPI." We have RPI **plus**
> Review, Worktree, handoff/ship governance — on the *execution/governance* side we are
> arguably thicker than base RPI. QRSPI's reference value is on the **alignment side**:
> the stages that happen *before* Plan (Questions, Design Discussion, Structure) which we
> likely **collapse into a single `/plan` step** — the exact mega-prompt that QRSPI split
> apart. That collapse is the thing worth studying, not "add stages."

## The QRSPI full pipeline (reconciled across sources)

The acronym "QRSPI" compresses an **8-stage** flow (most detailed: alexlavaee; betterquestions
collapses D→S and Worktree/PR→Implement into 5). Canonical expanded form:

**ALIGNMENT (before any code)**
1. **Questions (Q)** — *human writes questions that force the model to touch all relevant code*; agent surfaces knowledge gaps + explicit options (A/B/C). Output: list of technical inquiries / decision log. Fixes: instruction-budget overflow (alignment via targeted questions, not a mega-prompt).
2. **Research (R)** — agent gathers **objective facts only**; **the feature ticket is deliberately hidden** so output is a factual *technical map*, not a persuasive narrative. Output: findings doc, no opinions. Fixes: plan-reading illusion. (Parallel sub-agents as context firewalls; coordinate via filesystem artifacts, not shared context.)
3. **Design Discussion (D)** — agent "brain dumps" understanding into a **~200-line markdown** (current state / desired end state / design decisions); human does "**brain surgery**" redirecting to correct architecture. Fixes: magic-words trap (an explicit alignment conversation **by default**, no incantation).
4. **Structure Outline (S)** — agent defines **signatures, new types, high-level phases** — "like a **C header file**." **Mandatory** (RPI made it optional → frequently dropped). Enforces **vertical slices** (mock API → front end → DB, **checkpoint after each slice**).
5. **Plan (P)** — tactical implementation doc, now *pre-validated* by Q/R/D/S, so the plan-reading illusion "has no room to operate." Human spot-checks (reduced deep review).

**EXECUTION**
6. **Work Tree** — tasks organized into a hierarchy mapping to the vertical slices; each branch = a testable unit.
7. **Implement (I)** — code; reported as "20 min instead of 4 hrs" *because* alignment was front-loaded.
8. **Pull Request** — human reads/owns; review is fast because Design+Structure already agreed.

Human approval gates explicitly land **after D, after S, after P** (3 gates before execution).

## Stage-by-stage map — QRSPI ↔ Agentic OS (open, no closing verdict)

| QRSPI stage | Our nearest mechanism | Deeper question still open |
|---|---|---|
| Q — forced questioning | `brainstorm` (optional, un-gated) + bootstrap classify | Is optional questioning de-facto skipped? Should it be *structured/multi-agent* and *make the model touch the code*, vs freeform chat? |
| R — research, **ticket hidden** | `/research` workflow exists | Does ours produce a *factual map* or a solution-biased narrative? Is the ticket-hidden trick worth adopting? Are firewall subagents actually used by default? |
| **D — Design Discussion artifact** | partial: `/decide` records decisions; design lives *inside* `/plan` | **Likely our biggest gap as a distinct step.** Do we ever force a ~200-line current/desired/decisions brain-dump + explicit human brain-surgery gate *before* planning? |
| **S — Structure / header + vertical slices** | partial: vertical-slice *mentioned* in implement/review; not a distinct artifact | Does the plan-reading illusion survive because structure is never a separate checkable output with per-slice checkpoints? |
| P — Plan | `/plan` (files/steps/risks/rollback + spec) — **strong** | Are we conflating D+S+P into one mega-step (the failure QRSPI split)? |
| Work Tree | `using-git-worktrees` / `worktree-first` | mostly covered; is slice→branch mapping explicit? |
| Implement | `/implement` | covered |
| (Review) | `/review` (we have a full phase) | **We are AHEAD of base QRSPI here** — base folds review into PR; Tyler Burleigh's variant adds per-phase review, which we already do. |
| PR / handoff | `/handoff` + `/ship` (evidence, SSoT) | covered + richer governance |

## Borrowable mechanisms (independent of whether we adopt the stage structure)

- **Ticket-hidden research** → factual map, not advocacy.
- **Design-discussion artifact** (~200 lines: current state / desired end / decisions) as an explicit pre-plan gate ("brain dump → human brain surgery").
- **Structure-as-header** (signatures/types/phases) + **vertical slices with per-slice checkpoints** (vs horizontal layers that defer integration).
- **AI-reviews-its-own-work in a fresh session BEFORE the human** (Tyler Burleigh) — cuts human-review noise; reduces touchpoints ~12 → ~2.
- **Different model for review** (uncorrelated errors) — ⚠ tension with cross-platform parity; treat as cross-vendor adversarial, not Claude-only.
- **Fresh session between phases** + **intentional compaction** (distill logs → artifact; keep utilization 40–60%; ace-fca cites ~170k usable, "use as little as possible").
- **Per-phase after-action report** ("what went well / wrong / lessons forward") feeding **Agent Skills** refinement — finer-grained than our session-level `/retro`.
- **File-artifact coordination, not shared context** — we already do this (Work Log/SSoT); ace-fca confirms it as the right primitive.
- **Leverage inversion**: human review of a 200-line plan >> review of a 2000-line PR; "a bad line of research → thousands of bad lines of code."

## Corrections / constraints to carry forward
- **Instruction threshold is a RANGE, not 85.** ace-fca/alexlavaee cite frontier models losing consistency after **~150–200 instructions in a single prompt**. Our measured ~90 phase-entry directives sit *under* that — so raw count is NOT a smoking gun. The live questions are (a) `engineering_guardrails.md` packs **65 in one file**, and (b) **burial depth / ordering** may matter more than count (deepest-buried steps skipped first). Re-frame Strand A accordingly.
- RPI/QRSPI is explicitly a **brownfield** method; Horthy says it "falls flat for greenfield" (specs + loops win there). Our framework spans both → don't import wholesale.
- **Cross-platform parity** is our moat (every comparable project is Claude-centric). Any borrowed mechanism must hold across Claude/Codex/Gemini/API.
- **No new honor-system MUST** (Lesson #70): a new gate without a validator both raises load and is theatre.

## Candidate strands (NOT a converged scope — re-research each when picked up)
- **Strand A — alignment-side decomposition** (the headline): do we collapse Design+Structure into `/plan`? Prototype a distinct **Design-discussion** and **Structure** artifact/gate *before* `/plan` and test on a real brownfield task. Highest reference value.
- **Strand B — research quality**: test ticket-hidden factual-map research + default firewall subagents in `/research`.
- **Strand C — review leverage**: AI-self-review-in-fresh-session before human; cross-vendor reviewer (parity-safe form).
- **Strand D — instruction load**: not "count < 85" but burial-depth/ordering audit of the 65-in-one-file guardrails; which MUSTs lack a validator (Lesson #70).
- **Strand E — per-phase after-action → Skills** finer than `/retro`.

## Next Actions
- **When picked up: re-research the full direction space first** — treat every row above as a question to re-open, not settled.
- Likely needs `/decide` or **ADR-006** for any strand touching `AGENTS.md` / `engineering_guardrails.md` / the phase set (governance surface vs. parity).
- `/spec-intake` can consume this file once a strand is chosen — choosing one ≠ closing the others.

## Official References
- [Horthy keynote](https://www.youtube.com/watch?v=YwZR6tc7qYg) · [QRSPI breakdown](https://alexlavaee.me/blog/from-rpi-to-qrspi/) · [2026 evolution](https://betterquestions.ai/the-necessary-evolution-of-research-plan-implement-as-an-agentic-practice-in-2026/)
- [ace-fca original (HumanLayer)](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents) · [RPI anti-vibe workflow](https://htek.dev/articles/research-plan-implement-anti-vibe-coding-workflow/) · [Burleigh: R-P-I-Review](https://tylerburleigh.com/blog/2026/02/22/)
- [Dumb Zone / Ralph + RPI](https://linearb.io/blog/dex-horthy-humanlayer-rpi-methodology-ralph-loop) · [Advanced Context Engineering (talk)](https://www.youtube.com/watch?v=VvkhYWFWaKI) · [example prompts repo](https://github.com/marcaurelsecond/Advanced-Context-Engineering-for-AI-Agents)
