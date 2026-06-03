"""Contract-regression test: SSoT Update-Sequence heartbeat (ship-time).

Locks the AC-25 heartbeat contract in `.agent/workflows/ship.md` and the
`Update Sequence` field in the SSoT, so a careless ship.md edit cannot drop the
heartbeat step or contradict the "Work Log SSoT Sequence is a bootstrap snapshot,
not ship-incremented" invariant. Part of #16 (test coverage for critical
governance paths). CI-gated (tests/guard/), unlike the legacy
`.agentcortex/tests/test_ssot_completeness.py` which CI does not run.

Verifies contract text presence/consistency, not running-agent behavior.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHIP = ROOT / ".agent" / "workflows" / "ship.md"
SSOT = ROOT / ".agentcortex" / "context" / "current_state.md"


class SsotHeartbeatContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ship = SHIP.read_text(encoding="utf-8")
        cls.ssot = SSOT.read_text(encoding="utf-8")

    def test_ship_defines_heartbeat_increment_step(self) -> None:
        """ship.md MUST keep the AC-25 step that increments Update Sequence."""
        self.assertIn("SSoT Heartbeat", self.ship, "ship.md lost the SSoT Heartbeat step")
        self.assertIn("AC-25", self.ship)
        self.assertIn("Update Sequence", self.ship)
        self.assertRegex(self.ship, r"increment.*Update Sequence")

    def test_ship_marks_heartbeat_as_final_step(self) -> None:
        """The increment MUST be ordered after the other ship writes (it reflects a
        completed ship)."""
        self.assertRegex(self.ship, r"(final step|runs after all other ship writes)")

    def test_ship_preserves_worklog_sequence_snapshot_invariant(self) -> None:
        """The Work Log `SSoT Sequence` header is a bootstrap snapshot and MUST NOT
        be incremented at ship — only current_state.md's Update Sequence is."""
        self.assertRegex(self.ship, r"SSoT Sequence.*(NOT incremented|bootstrap-time snapshot)")

    def test_ssot_has_update_sequence_field(self) -> None:
        """current_state.md MUST expose the Update Sequence field the heartbeat bumps."""
        self.assertRegex(self.ssot, r"\*\*Update Sequence\*\*:\s*\d+")


if __name__ == "__main__":
    unittest.main()
