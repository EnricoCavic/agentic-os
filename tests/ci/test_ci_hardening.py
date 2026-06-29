"""Structural regression tests for CI hardening (#163).

Locks the reproducibility/hygiene wiring so a careless edit can't silently
un-pin the CI deps, drop pip caching, lose the UTF-8 default, or revert to the
old ad-hoc `pip install pyyaml pytest`. Mirrors the structural style of
test_security_workflow.py. Pure-Python (CI-safe on Linux).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQS = ROOT / ".github" / "requirements-ci.txt"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"


def test_requirements_file_pins_test_deps() -> None:
    assert REQS.exists(), ".github/requirements-ci.txt must exist (#163)"
    lines = [ln.strip() for ln in REQS.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.strip().startswith("#")]
    pkgs = {re.split(r"[=<>!~]", ln, maxsplit=1)[0].lower(): ln for ln in lines}
    for required in ("pytest", "pyyaml"):
        assert required in pkgs, f"requirements-ci.txt must list {required}"
        assert "==" in pkgs[required], f"{required} must be pinned with '==' (got: {pkgs[required]})"


def test_workflow_installs_from_pinned_requirements() -> None:
    txt = WORKFLOW.read_text(encoding="utf-8")
    assert "pip install -r .github/requirements-ci.txt" in txt, \
        "CI must install from the pinned requirements file (#163)"
    assert "pip install pyyaml pytest" not in txt, \
        "CI must not reintroduce the ad-hoc unpinned install (#163)"


def test_workflow_enables_pip_cache() -> None:
    txt = WORKFLOW.read_text(encoding="utf-8")
    assert "cache: 'pip'" in txt, "CI must enable pip caching (#163)"
    assert "cache-dependency-path: .github/requirements-ci.txt" in txt, \
        "pip cache must key on the requirements file (#163)"


def test_workflow_forces_utf8() -> None:
    txt = WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"PYTHONUTF8:\s*[\"']?1", txt), \
        "CI must export PYTHONUTF8=1 for cross-platform encoding safety (#163)"


def test_workflow_gates_legacy_framework_tests_on_linux() -> None:
    txt = WORKFLOW.read_text(encoding="utf-8")
    linux_pytest = re.search(r"pytest tests/ci/ tests/guard/ \.agentcortex/tests/ -v", txt)
    assert linux_pytest, \
        ".agentcortex/tests/ must be CI-gated alongside tests/ci + tests/guard on Linux (#163)"


def test_workflow_runs_pytest_on_windows() -> None:
    txt = WORKFLOW.read_text(encoding="utf-8")
    assert "test-windows:" in txt and "runs-on: windows-latest" in txt, \
        "CI must have a Windows pytest job (#163)"
    win_block = txt.split("test-windows:", 1)[1]
    assert re.search(r"pytest tests/ci/ tests/guard/ \.agentcortex/tests/", win_block), \
        "Windows job must run the full pytest set, not only validate.ps1 (#163)"


def test_workflow_has_utf8_sweep_and_critical_file_precheck() -> None:
    txt = WORKFLOW.read_text(encoding="utf-8")
    assert "utf8-and-critical-files:" in txt, "CI must have the UTF-8 sweep job (#163)"
    block = txt.split("utf8-and-critical-files:", 1)[1]
    for needle in ('decode("utf-8")', "AGENTS.md", "validate.ps1", "git", "ls-files"):
        assert needle in block, f"UTF-8 sweep job must contain {needle!r} (#163)"


# AC-12: threat-aware classifier parity — .agentcortex/context/* must NOT be on
# the inert skip arm in EITHER workflow (both classifiers must stay in sync).
_CONTEXT_SKIP_PATTERN = re.compile(r"\.agentcortex/context/\*")


def _inert_arm_text(workflow_text: str) -> str:
    """Extract the case-arm block that handles inert/skip patterns (docs-only path)."""
    # Both classifiers use a case statement with a trailing `*) heavy=true` arm.
    # Capture everything between the opening `case "$f" in` and `*) heavy=true`.
    m = re.search(r"case \"\$f\" in(.*?)\*\)\s*heavy=true", workflow_text, re.DOTALL)
    return m.group(1) if m else ""


def test_ac12_context_not_on_inert_arm_validate_yml() -> None:
    txt = WORKFLOW.read_text(encoding="utf-8")
    inert = _inert_arm_text(txt)
    assert inert, "Could not locate the case-arm classifier in validate.yml"
    assert not _CONTEXT_SKIP_PATTERN.search(inert), (
        ".agentcortex/context/* must NOT be on the inert skip arm in validate.yml "
        "(SSoT/runtime state is security-relevant — AC-12)"
    )


def test_ac12_context_not_on_inert_arm_security_yml() -> None:
    txt = SECURITY_WORKFLOW.read_text(encoding="utf-8")
    inert = _inert_arm_text(txt)
    assert inert, "Could not locate the case-arm classifier in security.yml"
    assert not _CONTEXT_SKIP_PATTERN.search(inert), (
        ".agentcortex/context/* must NOT be on the inert skip arm in security.yml "
        "(SSoT/runtime state is security-relevant — AC-12)"
    )
