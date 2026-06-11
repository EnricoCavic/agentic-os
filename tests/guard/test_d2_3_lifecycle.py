"""Unit tests for ADR-002 D2.3 — check_lifecycle_frontmatter.py.

Spec: docs/specs/lock-unification.md (AC-15..AC-20)
"""

from __future__ import annotations

import concurrent.futures
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agentcortex" / "tools"))

import check_lifecycle_frontmatter as lc  # noqa: E402


VALID_FM = """---
status: draft
date: 2026-04-30
lifecycle:
  owner: "/govern-docs"
  review_cadence: quarterly
  review_trigger: "When section X is touched"
  supersedes: none
  superseded_by: none
---

# Test
"""

MISSING_LIFECYCLE = """---
status: draft
date: 2026-04-30
---

# Test
"""

GRANDFATHERED = """---
status: draft
date: 2026-01-01
---

# Test
"""

INVALID_CADENCE = """---
status: draft
date: 2026-04-30
lifecycle:
  owner: "/govern-docs"
  review_cadence: weekly
  review_trigger: "X"
  supersedes: none
  superseded_by: none
---
"""


class TestTargetMatching(unittest.TestCase):
    def test_audit_path(self) -> None:
        self.assertTrue(lc._is_target("docs/audit/foo.md"))

    def test_governance_guide_path(self) -> None:
        self.assertTrue(lc._is_target("docs/guides/governance-x.md"))

    def test_adr_path(self) -> None:
        self.assertTrue(lc._is_target("docs/adr/ADR-001-foo.md"))

    def test_l1_architecture(self) -> None:
        self.assertTrue(lc._is_target("docs/architecture/foo.md"))

    def test_l2_excluded(self) -> None:
        self.assertFalse(lc._is_target("docs/architecture/foo.log.md"))

    def test_dotfiles_excluded(self) -> None:
        self.assertFalse(lc._is_target("docs/adr/.gitkeep.md"))

    def test_non_governance_excluded(self) -> None:
        self.assertFalse(lc._is_target("docs/specs/foo.md"))
        self.assertFalse(lc._is_target("docs/guides/non-governance.md"))


class TestFrontmatterParsing(unittest.TestCase):
    def test_valid_lifecycle_passes(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            f = Path(base_dir) / "doc.md"
            f.write_text(VALID_FM)
            finding = lc.check_file(f, "docs/audit/doc.md")
            self.assertEqual(finding.severity, "PASS")

    def test_parser_uses_unique_tempfile_not_source_sidecar(self) -> None:
        source = (ROOT / ".agentcortex" / "tools" / "check_lifecycle_frontmatter.py").read_text(encoding="utf-8")

        self.assertIn("mkstemp", source)
        self.assertNotIn(".__fm_probe__", source)

    def test_parallel_frontmatter_parse_does_not_race_on_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            f = Path(base_dir) / "doc.md"
            f.write_text(VALID_FM)

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                results = list(executor.map(lambda _i: lc.parse_frontmatter(f), range(24)))

            for raw, parsed in results:
                self.assertIsNotNone(raw)
                self.assertIsInstance(parsed, dict)
                self.assertIn("lifecycle", parsed)
            self.assertFalse(list(Path(base_dir).glob("*.__fm_probe__.yaml")))

    def test_missing_lifecycle_fails_when_recent(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            f = Path(base_dir) / "doc.md"
            f.write_text(MISSING_LIFECYCLE)
            finding = lc.check_file(f, "docs/audit/doc.md")
            self.assertEqual(finding.severity, "FAIL")
            self.assertIn("lifecycle: block missing", finding.detail)

    def test_grandfathered_warns_not_fails(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            f = Path(base_dir) / "doc.md"
            f.write_text(GRANDFATHERED)
            finding = lc.check_file(f, "docs/audit/doc.md")
            self.assertEqual(finding.severity, "WARN")
            self.assertIn("grandfathered", finding.detail)

    def test_invalid_cadence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as base_dir:
            f = Path(base_dir) / "doc.md"
            f.write_text(INVALID_CADENCE)
            finding = lc.check_file(f, "docs/audit/doc.md")
            self.assertEqual(finding.severity, "FAIL")
            self.assertIn("review_cadence", finding.detail)


class TestValidateLifecycle(unittest.TestCase):
    def test_all_fields_present(self) -> None:
        fm = {
            "lifecycle": {
                "owner": "/x",
                "review_cadence": "quarterly",
                "review_trigger": "Y",
                "supersedes": "none",
                "superseded_by": "none",
            }
        }
        self.assertEqual(lc.validate_lifecycle(fm), [])

    def test_missing_field(self) -> None:
        fm = {
            "lifecycle": {
                "owner": "/x",
                "review_cadence": "quarterly",
                "review_trigger": "Y",
                "supersedes": "none",
                # superseded_by missing
            }
        }
        issues = lc.validate_lifecycle(fm)
        self.assertEqual(len(issues), 1)
        self.assertIn("superseded_by", issues[0])

    def test_invalid_cadence(self) -> None:
        fm = {
            "lifecycle": {
                "owner": "/x",
                "review_cadence": "monthly",
                "review_trigger": "Y",
                "supersedes": "none",
                "superseded_by": "none",
            }
        }
        issues = lc.validate_lifecycle(fm)
        self.assertTrue(any("review_cadence" in i for i in issues))


if __name__ == "__main__":
    unittest.main()


class TestDownstreamUserContentDegradation(unittest.TestCase):
    """Sim finding 2026-06-11: a downstream install (.agentcortex-manifest present)
    owns its docs/ tree — the framework never deploys ADRs/specs there, so a
    user-authored ADR without lifecycle frontmatter must WARN (advisory), not FAIL
    (which blocked innocent downstream `validate.sh`). The framework source repo
    has no manifest, so its own governance docs stay FAIL-gated."""

    def _bare_adr(self, root: Path) -> Path:
        d = root / "docs" / "adr"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "ADR-001-user-stack.md"
        f.write_text("# User ADR\n\nWe use Postgres. No lifecycle frontmatter.\n", encoding="utf-8")
        return f

    def test_user_adr_fails_without_manifest_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            f = self._bare_adr(root)
            finding = lc.check_file(f, "docs/adr/ADR-001-user-stack.md", root)
            self.assertEqual(finding.severity, "FAIL")

    def test_user_adr_warns_with_manifest_downstream(self) -> None:
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            (root / ".agentcortex-manifest").write_text("version: 1.5.0\n", encoding="utf-8")
            f = self._bare_adr(root)
            finding = lc.check_file(f, "docs/adr/ADR-001-user-stack.md", root)
            self.assertEqual(finding.severity, "WARN")
            self.assertIn("downstream user content", finding.detail)

    def test_root_none_keeps_legacy_fail_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            f = self._bare_adr(root)
            finding = lc.check_file(f, "docs/adr/ADR-001-user-stack.md")  # no root arg
            self.assertEqual(finding.severity, "FAIL")
