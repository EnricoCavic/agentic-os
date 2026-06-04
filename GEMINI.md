@AGENTS.md

# Gemini Integration Entry

`AGENTS.md` is the shared governance and review source of truth for this repository. This file only adapts Gemini CLI to that shared context; do not duplicate rules here.

## Startup

1. Load the shared instructions from `AGENTS.md`.
2. Use `/memory show` when you need to inspect the active Gemini context.
3. Use `/memory refresh` after this file or `AGENTS.md` changes during an active session.

## Review

Use `AGENTS.md ## Review guidelines` for review priorities. For phase/gate details, read the referenced `.agent/workflows/*.md` files instead of inferring process from this adapter.
