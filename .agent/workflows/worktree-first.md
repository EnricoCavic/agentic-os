---
name: worktree-first
description: Git worktree-first branching and workspace governance.
tasks:
  - using-git-worktrees
  - plan
  - implement
  - review
  - ship
---

# Worktree-first Workflow

1. Apply `skills/using-git-worktrees` to establish an isolated workspace FIRST.
2. `/plan`: Define scope exclusively within the new worktree.
3. `/implement`: Complete all modifications and commits inside the worktree.
4. `/review` + `/test`: Confirm zero side-effects.
5. Finalize via `/handoff` + `/ship` — choose closure option explicitly: Merge now / Open PR / Keep branch / Archive-Close (decision tree inlined in `ship.md`).

