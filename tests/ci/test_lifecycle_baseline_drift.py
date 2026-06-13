"""Token lifecycle baseline drift detector tests (backlog #51 / issue #157).

The committed baseline must stay honest — cover every scenario and sit within
slack of the live analysis — and the detector must catch GROWTH drift while
treating shrink as advisory. Mirrors the ADR-006 native-ratchet discipline:
the guard ships in the SAME commit as the mechanism, and the committed baseline
is asserted to match reality (legitimate changes require an explicit --apply).

Tool: .agentcortex/tools/update_lifecycle_baseline.py
Issue: https://github.com/KbWen/agentic-os/issues/157
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".agentcortex" / "metadata" / "lifecycle-baseline.json"
TOOL = ROOT / ".agentcortex" / "tools" / "update_lifecycle_baseline.py"


def _load_tool():
    spec = importlib.util.spec_from_file_location("update_lifecycle_baseline", TOOL)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _load_baseline() -> dict:
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def test_baseline_present_and_schema() -> None:
    data = _load_baseline()
    for key in ("_doc", "version", "last_updated", "slack_default",
                "baselines", "aggregate"):
        assert key in data, f"baseline missing {key!r}"
    assert isinstance(data["baselines"], dict) and data["baselines"]
    for key in ("registry_tokens", "compact_index_tokens"):
        assert key in data["aggregate"]
    # The dropped field (issue scope cut) must not creep back in without a decision.
    assert "cc_memory_files_tokens" not in json.dumps(data), (
        "cc_memory_files_tokens was deliberately omitted (no deterministic "
        "repo-local source); reintroducing it needs a scope decision."
    )


def test_baseline_covers_all_scenarios() -> None:
    tool = _load_tool()
    snapshot = tool.current_snapshot(ROOT)
    data = _load_baseline()
    assert set(data["baselines"]) == set(snapshot["baselines"]), (
        "committed baseline scenarios drift from the live scenario set — run "
        "update_lifecycle_baseline.py --apply"
    )


def test_committed_baseline_within_slack() -> None:
    """The honesty gate: the committed numbers must match the live analysis.

    Legitimate governance changes that move a scenario beyond slack must be
    acknowledged by re-running --apply in the same change (ADR-006 ergonomic).
    """
    tool = _load_tool()
    data = _load_baseline()
    snapshot = tool.current_snapshot(ROOT)
    slack = float(data.get("slack_default", tool.DEFAULT_SLACK))
    rows, has_growth = tool.compare(data, snapshot, slack)
    drifted = [r for r in rows if r[4].startswith("DRIFT") or "NEW" in r[4]]
    assert not has_growth, (
        "committed baseline is stale (live token cost grew beyond slack). "
        f"Drifted rows: {drifted}. Re-baseline: "
        "update_lifecycle_baseline.py --apply"
    )


def test_detects_growth_drift() -> None:
    tool = _load_tool()
    data = _load_baseline()
    snapshot = tool.current_snapshot(ROOT)
    slack = float(data.get("slack_default", tool.DEFAULT_SLACK))
    # Tamper: halve every baseline so the live numbers look inflated -> drift.
    tampered = json.loads(json.dumps(data))
    for v in tampered["baselines"].values():
        v["current_total_tokens"] = max(1, v["current_total_tokens"] // 2)
    _rows, has_growth = tool.compare(tampered, snapshot, slack)
    assert has_growth, "halved baseline must register as GROWTH drift"


def test_shrink_is_advisory_not_drift() -> None:
    tool = _load_tool()
    data = _load_baseline()
    snapshot = tool.current_snapshot(ROOT)
    slack = float(data.get("slack_default", tool.DEFAULT_SLACK))
    # Tamper: double every baseline so the live numbers look shrunk.
    tampered = json.loads(json.dumps(data))
    for v in tampered["baselines"].values():
        v["current_total_tokens"] = v["current_total_tokens"] * 2
    rows, has_growth = tool.compare(tampered, snapshot, slack)
    assert not has_growth, "shrink must not have teeth (trimming is never punished)"
    assert any("shrink" in r[4] for r in rows), "shrink rows must be surfaced"


def test_missing_scenario_is_drift() -> None:
    tool = _load_tool()
    data = _load_baseline()
    snapshot = tool.current_snapshot(ROOT)
    slack = float(data.get("slack_default", tool.DEFAULT_SLACK))
    tampered = json.loads(json.dumps(data))
    victim = next(iter(tampered["baselines"]))
    del tampered["baselines"][victim]
    _rows, has_growth = tool.compare(tampered, snapshot, slack)
    assert has_growth, "a scenario missing from the baseline must register as drift"
