"""ADR-006 ratchet: the native validator check surface may not grow silently.

New validator checks are Python tools behind run_python_check / Invoke-PythonCheck
(single implementation, no parity tax). A native check may still be added when it
must protect the no-python path — via a baseline bump WITH a justification entry
(diff-visible, reviewer-judged). Migrations must ratchet the baseline DOWN so the
committed number is always the truth.

Spec: docs/specs/validator-strangler-policy.md (AC-3, AC-4)
ADR:  docs/adr/ADR-006-validator-python-core-strangler.md
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "tests" / "ci" / "validator_native_baseline.json"
VALIDATE_SH = ROOT / ".agentcortex" / "bin" / "validate.sh"
VALIDATE_PS1 = ROOT / ".agentcortex" / "bin" / "validate.ps1"

_SH_RE = re.compile(r"^\s*record_result ")
_PS1_RE = re.compile(r"^\s*Add-Result ")


def count_native_sites(text: str, pattern: re.Pattern[str]) -> int:
    """Count non-comment, line-leading result-emission call sites."""
    count = 0
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if pattern.match(line):
            count += 1
    return count


def _load() -> dict:
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def test_native_check_counts_match_baseline_exactly() -> None:
    data = _load()
    actual_sh = count_native_sites(VALIDATE_SH.read_text(encoding="utf-8", errors="replace"), _SH_RE)
    actual_ps1 = count_native_sites(VALIDATE_PS1.read_text(encoding="utf-8", errors="replace"), _PS1_RE)
    base_sh = data["baseline"]["validate_sh"]
    base_ps1 = data["baseline"]["validate_ps1"]

    grow_msg = (
        "native validator check surface GREW ({which}: {actual} > {base}). "
        "Per ADR-006, new checks MUST be Python tools behind run_python_check / "
        "Invoke-PythonCheck. If this check genuinely must run without Python, bump "
        "tests/ci/validator_native_baseline.json AND add a one-line entry to its "
        "'justifications' list."
    )
    shrink_msg = (
        "stale ratchet baseline ({which}: {actual} < {base}) — a native check was "
        "removed/migrated. Ratchet the baseline DOWN in "
        "tests/ci/validator_native_baseline.json in the same change so the committed "
        "floor stays honest (ADR-006)."
    )
    for which, actual, base in (("validate_sh", actual_sh, base_sh), ("validate_ps1", actual_ps1, base_ps1)):
        assert actual <= base, grow_msg.format(which=which, actual=actual, base=base)
        assert actual >= base, shrink_msg.format(which=which, actual=actual, base=base)


def test_baseline_above_original_floor_requires_justification() -> None:
    data = _load()
    floor = data["original_floor"]
    over = [
        which for which in ("validate_sh", "validate_ps1")
        if data["baseline"][which] > floor[which]
    ]
    if over:
        justs = [j for j in data.get("justifications", []) if isinstance(j, str) and j.strip()]
        assert justs, (
            f"baseline raised above the {floor['frozen']} floor for {over} with no "
            "justification entry — ADR-006 requires a one-line justification naming "
            "the check and why it must run without Python."
        )


def test_counting_heuristic_fixture() -> None:
    """AC-4: the counter counts call sites, not noise."""
    fixture = "\n".join([
        "record_result PASS \"top-level\"",            # counted (no indent)
        "  record_result WARN \"indented\"",            # counted
        "    record_result FAIL \"deep indent\"",       # counted
        "# record_result PASS \"commented out\"",       # not counted
        "  # record_result WARN \"indented comment\"",  # not counted
        "echo \"call record_result yourself\"",         # not counted (mid-line)
        "some_var=\"record_result \"",                  # not counted (mid-line)
    ])
    assert count_native_sites(fixture, _SH_RE) == 3

    ps1_fixture = "\n".join([
        "Add-Result -Level 'PASS' -Message 'x'",
        "    Add-Result -Level 'WARN' -Message 'y'",
        "# Add-Result -Level 'PASS' -Message 'no'",
        "Write-Output 'use Add-Result here'",
    ])
    assert count_native_sites(ps1_fixture, _PS1_RE) == 2


def test_midline_emission_styles_are_known_uncounted() -> None:
    """Documented scope limitation (review 2026-06-10, MEDIUM, accepted):
    mid-line emission styles are NOT counted by the line-leading rule — a new
    native check authored as `cmd && record_result ...` evades the machine
    ratchet and is caught by reviewer judgment over the diff instead (spec
    §Enforcement Boundary). This test pins the blind spot as INTENT so a future
    heuristic change that silently alters scope is visible.
    """
    midline = "\n".join([
        '[[ -f x ]] && record_result PASS "midline-and"',
        'grep -q y file || { record_result WARN "midline-or-group"; }',
    ])
    assert count_native_sites(midline, _SH_RE) == 0

    ps1_midline = "if ($ok) { Add-Result -Level 'PASS' -Message 'inline-if' }"
    assert count_native_sites(ps1_midline, _PS1_RE) == 0


def test_baseline_schema() -> None:
    data = _load()
    for key in ("original_floor", "baseline", "justifications"):
        assert key in data, f"baseline json missing {key!r}"
    for which in ("validate_sh", "validate_ps1"):
        assert isinstance(data["baseline"][which], int)
        assert isinstance(data["original_floor"][which], int)
