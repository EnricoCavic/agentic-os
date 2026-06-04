---
status: frozen
title: Multi-Agent Review Guidelines and Contributor Adapters
source: user-request-2026-06-04
created: 2026-06-04
primary_domain: document-governance
backlog: 56
---

# Multi-Agent Review Guidelines and Contributor Adapters

## Problem

Agentic OS currently has strong Codex/Claude governance entry points, but the contributor experience is uneven across Codex, Claude, Gemini, and GitHub Copilot. Review guidance should be discoverable by each tool without making `AGENTS.md` too long or duplicating the full governance system into every tool-specific file.

## Goals

- Give Codex GitHub review a concise `AGENTS.md ## Review guidelines` section.
- Add lightweight adapters for Gemini CLI and GitHub Copilot.
- Document human-facing interaction patterns for Codex, Claude, Copilot, and Gemini.
- Keep all shared instructions short and route detailed governance to existing canonical files.
- Add validation so the new adapter files do not silently drift or exceed known tool limits.

## Non-Goals

- Build a generator for all future adapter files.
- Install or configure third-party GitHub apps.
- Add API keys, secrets, or new CI credentials.
- Replace existing Agentic OS phase/gate workflows.

## External References

- OpenAI Codex GitHub integration: `https://developers.openai.com/codex/integrations/github.md`
- GitHub Copilot custom instructions: `https://docs.github.com/en/copilot/concepts/prompting/response-customization`
- VS Code custom instructions: `https://code.visualstudio.com/docs/agent-customization/custom-instructions`
- Anthropic Claude Code GitHub Actions: `https://docs.anthropic.com/en/docs/claude-code/github-actions`
- Gemini CLI context files: `https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md`

## Acceptance Criteria

- AC-1: `AGENTS.md` contains a concise `## Review guidelines` section suitable for Codex GitHub review.
- AC-2: `GEMINI.md` exists and imports `AGENTS.md` without duplicating governance rules.
- AC-3: `.github/copilot-instructions.md` exists, points to shared governance, and stays below 4,000 characters.
- AC-4: `.github/instructions/governance-review.instructions.md` exists for governance-specific Copilot review context.
- AC-5: `docs/ai-contributors.md` documents Codex, Claude, Copilot, and Gemini interaction entry points.
- AC-6: Guard tests verify AC-1 through AC-5 and protect the Copilot instruction length cap.

## Domain Decisions

- [DECISION] Keep `AGENTS.md` as the short cross-agent source of truth and keep tool-specific files as adapters rather than duplicated governance manuals.
- [DECISION] Use `.github/copilot-instructions.md` for Copilot's always-on short entry point because Copilot code review has a documented custom-instruction length boundary.
- [CONSTRAINT] Do not add new "MUST" governance claims unless a guard test or validator verifies the structural presence or size constraint.
