"""Tests for the advisory spec drift linter (#156).

Spec: docs/specs/spec-drift-linter.md (AC-1..AC-4)
Run: python -m unittest tests.guard.test_spec_drift_linter -v
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agentcortex" / "tools"))

import lint_spec_drift as lint  # noqa: E402


SPEC_TEXT = """\
# Demo Spec

## Goal

Keep this section ignored: `.agent/workflows/ignored.md`.

## Acceptance Criteria

- AC-1: `.agentcortex/tools/lint_spec_drift.py` implements the advisory.
- AC-2: `tests/guard/test_spec_drift_linter.py` verifies it.

## Non-goals

- Do not inspect `.github/workflows/validate.yml`.
"""


class TestAcceptanceCriteriaPathExtraction(unittest.TestCase):
    def test_extracts_only_paths_from_acceptance_criteria(self) -> None:
        paths = lint.extract_ac_paths(SPEC_TEXT)

        self.assertEqual(
            paths,
            {
                ".agentcortex/tools/lint_spec_drift.py",
                "tests/guard/test_spec_drift_linter.py",
            },
        )


class TestDriftEvaluation(unittest.TestCase):
    def test_clean_match_has_no_warnings(self) -> None:
        result = lint.evaluate_drift(
            changed_files=[
                ".agentcortex/tools/lint_spec_drift.py",
                "tests/guard/test_spec_drift_linter.py",
            ],
            ac_paths={
                ".agentcortex/tools/lint_spec_drift.py",
                "tests/guard/test_spec_drift_linter.py",
            },
        )

        self.assertEqual(result.uncovered_changed, [])
        self.assertEqual(result.untouched_ac_paths, [])

    def test_reports_uncovered_changed_and_untouched_ac_paths(self) -> None:
        result = lint.evaluate_drift(
            changed_files=[
                ".agentcortex/tools/lint_spec_drift.py",
                ".agent/workflows/review.md",
            ],
            ac_paths={
                ".agentcortex/tools/lint_spec_drift.py",
                "tests/guard/test_spec_drift_linter.py",
            },
        )

        self.assertEqual(result.uncovered_changed, [".agent/workflows/review.md"])
        self.assertEqual(result.untouched_ac_paths, ["tests/guard/test_spec_drift_linter.py"])


class TestWorkLogSpecDetection(unittest.TestCase):
    def test_resolves_spec_path_from_worklog_table(self) -> None:
        worklog = textwrap.dedent(
            """\
            ## External References

            | Type | Path / URL | Notes |
            |---|---|---|
            | Issue | https://github.com/KbWen/agentic-os/issues/156 | Source |
            | Spec | docs/specs/spec-drift-linter.md | Frozen |
            """
        )

        self.assertEqual(
            lint.spec_from_worklog(worklog),
            "docs/specs/spec-drift-linter.md",
        )


class TestCliBehavior(unittest.TestCase):
    def test_cli_returns_zero_for_advisory_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            root = Path(base_dir)
            spec = root / "docs" / "specs" / "demo.md"
            spec.parent.mkdir(parents=True)
            spec.write_text(SPEC_TEXT, encoding="utf-8")

            original_changed_files = lint.changed_files
            lint.changed_files = lambda *_args, **_kwargs: [".agent/workflows/review.md"]
            stdout = io.StringIO()
            argv = ["lint_spec_drift.py", "--root", str(root), "--spec", "docs/specs/demo.md"]
            try:
                with contextlib.redirect_stdout(stdout):
                    rc = lint.main(argv)
            finally:
                lint.changed_files = original_changed_files

            self.assertEqual(rc, 0)
            self.assertIn("Spec drift advisory: 3 warning(s)", stdout.getvalue())
            self.assertIn("UNCOVERED_CHANGED: .agent/workflows/review.md", stdout.getvalue())
            self.assertIn("UNTOUCHED_AC_PATH: tests/guard/test_spec_drift_linter.py", stdout.getvalue())

    def test_cli_returns_nonzero_for_missing_spec(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            stderr = io.StringIO()
            argv = ["lint_spec_drift.py", "--root", base_dir, "--spec", "docs/specs/missing.md"]

            with contextlib.redirect_stderr(stderr):
                rc = lint.main(argv)

            self.assertEqual(rc, 2)
            self.assertIn("spec not found", stderr.getvalue())

    def test_cli_rejects_git_revision_options(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            root = Path(base_dir)
            spec = root / "docs" / "specs" / "demo.md"
            spec.parent.mkdir(parents=True)
            spec.write_text(SPEC_TEXT, encoding="utf-8")
            stderr = io.StringIO()
            argv = [
                "lint_spec_drift.py",
                "--root",
                str(root),
                "--spec",
                "docs/specs/demo.md",
                "--base=--output=owned",
            ]

            with contextlib.redirect_stderr(stderr):
                rc = lint.main(argv)

            self.assertEqual(rc, 2)
            self.assertIn("unsafe git revision", stderr.getvalue())


class TestReviewWorkflowIntegration(unittest.TestCase):
    def test_review_workflow_mentions_advisory_linter(self) -> None:
        review_text = (ROOT / ".agent" / "workflows" / "review.md").read_text(encoding="utf-8")

        self.assertIn("lint_spec_drift.py", review_text)
        self.assertIn("advisory", review_text.lower())
        self.assertIn("non-blocking", review_text.lower())


if __name__ == "__main__":
    unittest.main()
