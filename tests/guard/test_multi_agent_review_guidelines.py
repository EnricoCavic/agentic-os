"""Guard tests for multi-agent review guideline adapters.

Spec: docs/specs/multi-agent-review-guidelines.md (AC-1..AC-6)
Run: python -m unittest tests.guard.test_multi_agent_review_guidelines -v
"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class TestMultiAgentReviewGuidelines(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_agents_md_exposes_codex_review_guidelines(self) -> None:
        text = self.read("AGENTS.md")

        self.assertIn("## Review guidelines", text)
        self.assertIn("governance-bypass", text)
        self.assertIn("Work Log evidence", text)
        self.assertIn("tool-specific adapters", text)

    def test_gemini_adapter_imports_agents_without_duplication(self) -> None:
        text = self.read("GEMINI.md")

        self.assertTrue(text.startswith("@AGENTS.md"))
        self.assertIn("Gemini Integration Entry", text)
        self.assertIn("/memory show", text)
        self.assertIn("do not duplicate rules here", text)

    def test_copilot_repository_instruction_is_short_and_shared(self) -> None:
        text = self.read(".github/copilot-instructions.md")

        self.assertLess(len(text), 4000)
        self.assertIn("AGENTS.md", text)
        self.assertIn("Review guidelines", text)
        self.assertIn("tests/guard/", text)

    def test_copilot_governance_review_instruction_exists(self) -> None:
        text = self.read(".github/instructions/governance-review.instructions.md")

        self.assertIn("applyTo:", text)
        self.assertIn("Governance Review Instructions", text)
        self.assertIn("canonical source", text)
        self.assertIn("validator, guard test, or explicit evidence", text)

    def test_human_contributor_guide_lists_supported_tools(self) -> None:
        text = self.read("docs/ai-contributors.md")

        for expected in ("@codex review", "@claude", "@copilot", "GEMINI.md"):
            self.assertIn(expected, text)
        self.assertIn("AGENTS.md ## Review guidelines", text)


if __name__ == "__main__":
    unittest.main()
