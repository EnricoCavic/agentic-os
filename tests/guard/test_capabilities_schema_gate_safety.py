"""Schema gate-safety validator tests - ADR-007 AC-D6.

Gate-relaxation must be UNREPRESENTABLE: a malicious / over-cap
downstream-capabilities.yaml is REJECTED (exit 1, naming the offending field), NOT
silently clamped. A gate-safe file -> exit 0; absent / empty -> exit 0 (inert).
The reject-vs-clamp parametrization IS the mutation guard: if anyone weakens the
validator to lower a value instead of rejecting, these exit-1 assertions fail.
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / ".agentcortex" / "tools" / "validate_downstream_capabilities.py"


def _check(tmp_path, body):
    f = tmp_path / "downstream-capabilities.yaml"
    f.write_text(textwrap.dedent(body), encoding="utf-8")
    return subprocess.run([sys.executable, str(VALIDATOR), str(f)],
                          capture_output=True, encoding="utf-8", errors="replace")


_SAFE = """\
version: 1
skills:
  - id: custom-terraform-safety
    load_policy: on-match
    phase_scope: [implement, review]
subagent_policy: read-only
trackers:
  - id: custom-jira
    skill: custom-jira-sync
"""


def test_gate_safe_file_passes(tmp_path):
    r = _check(tmp_path, _SAFE)
    assert r.returncode == 0, f"gate-safe file must pass: {r.stderr!r}"


def test_absent_file_is_safe(tmp_path):
    r = subprocess.run([sys.executable, str(VALIDATOR), str(tmp_path / "nope.yaml")],
                       capture_output=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0


def test_empty_file_is_safe(tmp_path):
    assert _check(tmp_path, "").returncode == 0


@pytest.mark.parametrize("body,needle", [
    ("skills:\n  - id: red-team-adversarial\n    load_policy: on-match\n", "custom-"),
    ("skills:\n  - id: custom-x\n    load_policy: always\n", "ceiling"),
    ("skills:\n  - id: custom-x\n    block_if_missed: true\n", "block_if_missed"),
    ("skills:\n  - id: custom-x\n    gate: ship\n", "gate"),
    ("subagent_policy: anything-goes\n", "subagent_policy"),
    ("trackers:\n  - id: custom-j\n    blocking: true\n", "blocking"),
    ("trigger_priority: hard\n", "trigger_priority"),
    ("skip_confirmation: true\n", "unknown top-level"),
    ("ship_without_review: true\n", "unknown top-level"),
    ("skills:\n  - id: custom-x\n    autonomy: full\n", "unknown key"),
])
def test_unsafe_file_is_rejected_not_clamped(tmp_path, body, needle):
    r = _check(tmp_path, body)
    assert r.returncode == 1, f"must REJECT (not clamp) {body!r} -> rc={r.returncode}, err={r.stderr!r}"
    assert needle in r.stderr, f"reason must name {needle!r}: {r.stderr!r}"
