---
title: AI Contributor Interaction Guide
created: 2026-06-04
status: living
---

# AI Contributor Interaction Guide

Use this guide to invite AI coding agents into the project without duplicating governance rules across tools. The shared contract lives in `AGENTS.md`; tool-specific files should stay short and point back to it.

## Shared Instructions

- `AGENTS.md`: shared behavior, delivery gates, and review guidelines for all agents.
- `CLAUDE.md`: Claude-specific entry point; imports `AGENTS.md`.
- `GEMINI.md`: Gemini-specific entry point; imports `AGENTS.md`.
- `.github/copilot-instructions.md`: short Copilot entry point for GitHub/VS Code contexts.
- `.github/instructions/*.instructions.md`: focused Copilot/VS Code file-based instructions.

## GitHub PR Interaction

| Tool | Trigger | Best Use |
|---|---|---|
| Codex | `@codex review` | Ask for a GitHub code review on a PR. |
| Codex | `@codex fix ...` | Ask Codex to address review feedback or CI failures in PR context. |
| Claude | `@claude ...` | Trigger Claude Code GitHub Actions when the repo has the workflow/app configured. |
| Copilot | `@copilot ...` in PR review comments | Ask Copilot cloud agent to make changes on an existing PR. |
| Copilot | assign an issue to Copilot | Delegate an issue so Copilot can open a PR. |

## Local Interaction

| Tool | Entry File | Notes |
|---|---|---|
| Codex | `AGENTS.md` | Reads shared repo guidance and nested instructions where available. |
| Claude Code | `CLAUDE.md` | Keep Claude-specific dispatch here; avoid duplicating `AGENTS.md`. |
| Gemini CLI | `GEMINI.md` | Use `/memory show` to inspect loaded context and `/memory refresh` after edits. |
| Copilot / VS Code | `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` | Keep repository-wide Copilot instructions short; use file-based instructions for focused guidance. |

## Review Expectations

All AI contributors should follow `AGENTS.md ## Review guidelines`. In short: focus on correctness, security, missing tests, governance evidence, and scope discipline before style.

## Maintenance Rules

- Keep shared rules in `AGENTS.md`.
- Keep adapters short and tool-specific.
- Put long workflow detail in `.agent/workflows/` or `.agent/rules/`.
- Add or update guard tests when adapter structure or size matters.
