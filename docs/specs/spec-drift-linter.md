---
status: frozen
title: Spec Drift Linter
source: GitHub issue #156
created: 2026-06-04
primary_domain: governance-tooling
secondary_domains: [review-workflow]
---

# Spec Drift Linter

## Goal

Add an advisory linter that helps reviewers spot branch changes that are not covered by the active spec's Acceptance Criteria, and Acceptance Criteria that mention files not touched by the branch.

## Acceptance Criteria

- AC-1: `.agentcortex/tools/lint_spec_drift.py` can resolve a spec path from an explicit `--spec` argument or from a Work Log passed with `--worklog`.
- AC-2: `.agentcortex/tools/lint_spec_drift.py` compares `git diff --name-only` changed files against path-like references found in the spec `## Acceptance Criteria` section.
- AC-3: `.agentcortex/tools/lint_spec_drift.py` reports changed files with no AC coverage and AC-mentioned paths not touched by the branch, while exiting `0` so the signal remains advisory.
- AC-4: `tests/guard/test_spec_drift_linter.py` covers clean matches, uncovered changed files, untouched AC paths, Work Log spec detection, and advisory exit-code behavior.
- AC-5: `.agent/workflows/review.md` invokes or instructs reviewers to run the advisory linter at `/review` entry without making it a blocking gate.

## Non-goals

- Do not enforce spec drift as a hard CI failure.
- Do not parse natural-language requirements beyond path-like references in Acceptance Criteria.
- Do not modify `validate.sh`, `validate.ps1`, or GitHub Actions in this slice.
- Do not create a broad lifecycle or authority-map framework.

## Constraints

- The linter must be deterministic and stdlib-only.
- The linter must work on Windows and POSIX path separators.
- The linter must keep output concise enough to paste into review evidence.
- The implementation must stay limited to the issue #156 surface.

## API / Data Contract

CLI shape:

```text
python .agentcortex/tools/lint_spec_drift.py --root . --worklog .agentcortex/context/work/<key>.md
python .agentcortex/tools/lint_spec_drift.py --root . --spec docs/specs/<feature>.md --base <rev> --head <rev>
```

Output shape:

```text
Spec drift advisory: <N> warning(s)
UNCOVERED_CHANGED: <path>
UNTOUCHED_AC_PATH: <path>
```

Exit code is always `0` unless invocation itself is invalid, such as a missing spec path.

## File Relationship

INDEPENDENT from existing specs. It complements review burden-of-proof rules but does not replace them.

## Domain Decisions

- [DECISION] Keep the linter advisory so it can surface likely scope drift without creating a brittle hard gate around prose parsing.
- [DECISION] Extract only path-like references from Acceptance Criteria because that is deterministic and easy to test across platforms.
- [CONSTRAINT] `/review` integration must describe the linter as non-blocking and must not change review verdict rules.
