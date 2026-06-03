"""Regression tests for validator framework-self false positives (#170/#171/#172).

Locks three WARNs that fired on the framework repo itself but should not, and
guards cross-platform (validate.sh ↔ validate.ps1) parity of each fix:

- #170: underscore-prefixed meta/index specs (`_product-backlog-archive.md`
  status:archive, `_research-*.md` status:research) are exempt from the
  spec-status enum, matching the `_*` skip convention already used elsewhere.
- #171: `ship-history-*.md` archives are not Work Logs (no `## Phase Summary`
  contract) and must be excluded from the archived-Work-Log Phase-Summary scan.
- #172: the app-init template / Project Name checks fire only for a genuine
  downstream app — detected by an `ADR-00N-project-architecture.md` (created by
  /app-init), NOT by any ADR. The framework's governance ADRs never match, and
  the signal is deploy-independent so it also covers fork/clone adopters that
  never ran deploy.sh (no `.agentcortex-manifest`).
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATE_SH = ROOT / ".agentcortex" / "bin" / "validate.sh"
VALIDATE_PS1 = ROOT / ".agentcortex" / "bin" / "validate.ps1"
DEPLOY_SH = ROOT / ".agentcortex" / "bin" / "deploy.sh"

# bash discovery (mirror test_deploy_tiering.py — avoid the WindowsApps stub).
git_path = shutil.which("git")
git_root = Path(git_path).parent.parent if git_path else None
bash_candidates = [
    str(git_root / "bin" / "bash.exe") if git_root else None,
    str(git_root / "usr" / "bin" / "bash.exe") if git_root else None,
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files\Git\usr\bin\bash.exe",
    shutil.which("bash"),
]
bash = next(
    (c for c in bash_candidates if c and "WindowsApps" not in c and Path(c).exists()),
    None,
)
requires_bash = pytest.mark.skipif(bash is None, reason="bash not available")

# The four WARN substrings this change eliminates on the framework repo.
STATUS_WARN = "unrecognized status value"          # #170
PHASE_SUMMARY_WARN = "with empty Phase Summary"     # #171 (WARN-specific; avoids
#   matching the PASS line "...have non-empty Phase Summary")
TEMPLATE_WARN = "project spec template missing"     # #172
PROJECT_NAME_WARN = "Project Name field absent"     # #172


def _run_validate(cwd: Path) -> str:
    proc = subprocess.run(
        [bash, str(cwd / ".agentcortex" / "bin" / "validate.sh")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd),
    )
    return proc.stdout + proc.stderr


@pytest.fixture(scope="module")
def framework_validate_output() -> str:
    if bash is None:
        pytest.skip("bash not available")
    return _run_validate(ROOT)


# ---------------------------------------------------------------------------
# Behavioral — the framework repo must validate without these false WARNs
# ---------------------------------------------------------------------------

@requires_bash
def test_170_underscore_meta_specs_no_status_warn(framework_validate_output: str) -> None:
    # The repo really contains _product-backlog-archive.md (status: archive);
    # _research-*.md (status: research) may also be present transiently.
    assert STATUS_WARN not in framework_validate_output, (
        "underscore-prefixed meta specs must be exempt from the spec-status enum (#170)"
    )


@requires_bash
def test_171_ship_history_no_phase_summary_warn(framework_validate_output: str) -> None:
    assert (ROOT / ".agentcortex" / "context" / "archive" / "ship-history-2026.md").exists(), \
        "fixture precondition: ship-history archive should exist in the framework repo"
    assert PHASE_SUMMARY_WARN not in framework_validate_output, (
        "ship-history-*.md is not a Work Log and must be excluded from the scan (#171)"
    )


@requires_bash
def test_172_no_app_init_warn_on_framework(framework_validate_output: str) -> None:
    assert TEMPLATE_WARN not in framework_validate_output, (
        "framework governance ADRs must not trigger the app-init template check (#172)"
    )
    assert PROJECT_NAME_WARN not in framework_validate_output, (
        "framework repo has no Project Name and must not trigger the check (#172)"
    )


@requires_bash
def test_172_app_init_checks_fire_for_fork_downstream() -> None:
    """A fork/clone adopter (no .agentcortex-manifest) that ran /app-init — i.e.
    has an ADR-00N-project-architecture.md — MUST still get the template /
    Project Name checks. This is the case the earlier manifest-based marker
    under-suppressed; the project-architecture-ADR signal is deploy-independent.
    """
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()
        first = subprocess.run(
            [bash, str(DEPLOY_SH), str(target)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT),
        )
        assert first.returncode == 0, f"deploy failed:\n{first.stderr}"

        # Simulate a fork adopter: remove the deploy manifest, then run /app-init's
        # observable effect (the project-architecture ADR) WITHOUT setting a
        # Project Name or creating a spec-app-feature template.
        (target / ".agentcortex-manifest").unlink(missing_ok=True)
        adr_dir = target / "docs" / "adr"
        adr_dir.mkdir(parents=True, exist_ok=True)
        (adr_dir / "ADR-001-project-architecture.md").write_text(
            "# ADR-001 Project Architecture\n", encoding="utf-8"
        )

        out = _run_validate(target)
        assert TEMPLATE_WARN in out, "template check must fire for an app-init'd fork downstream (#172)"
        assert PROJECT_NAME_WARN in out, "Project Name check must fire for an app-init'd fork downstream (#172)"


@requires_bash
def test_172_governance_only_adrs_do_not_fire() -> None:
    """A repo with ONLY governance-named ADRs (no *-project-architecture.md) must
    NOT trigger the app-init checks, even with a manifest present."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()
        first = subprocess.run(
            [bash, str(DEPLOY_SH), str(target)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT),
        )
        assert first.returncode == 0, f"deploy failed:\n{first.stderr}"
        adr_dir = target / "docs" / "adr"
        adr_dir.mkdir(parents=True, exist_ok=True)
        (adr_dir / "ADR-001-governance-friction-tuning.md").write_text("# gov\n", encoding="utf-8")

        out = _run_validate(target)
        assert TEMPLATE_WARN not in out and PROJECT_NAME_WARN not in out, (
            "governance-only ADRs must not be read as an /app-init signal (#172)"
        )


# ---------------------------------------------------------------------------
# Structural — cross-platform parity (sh ↔ ps1) of each fix
# ---------------------------------------------------------------------------

def test_precondition_framework_has_no_project_architecture_adr() -> None:
    """The #172 discriminator relies on the framework never shipping an
    *-project-architecture.md ADR (its ADRs are governance-named)."""
    for base in (ROOT / "docs" / "adr", ROOT / ".agentcortex" / "adr"):
        if base.exists():
            offenders = list(base.glob("*-project-architecture.md"))
            assert not offenders, f"framework must not ship a project-architecture ADR: {offenders}"


def test_fix_markers_present_in_both_validators() -> None:
    sh = VALIDATE_SH.read_text(encoding="utf-8")
    ps1 = VALIDATE_PS1.read_text(encoding="utf-8")
    for marker in ("(#170)", "(#171)", "(#172)"):
        assert marker in sh, f"validate.sh missing {marker} fix"
        assert marker in ps1, f"validate.ps1 missing {marker} fix (parity)"


def test_172_pattern_parity() -> None:
    assert "*-project-architecture.md" in VALIDATE_SH.read_text(encoding="utf-8")
    assert "*-project-architecture.md" in VALIDATE_PS1.read_text(encoding="utf-8")


def test_171_ship_history_exclusion_parity() -> None:
    assert "ship-history-*" in VALIDATE_SH.read_text(encoding="utf-8")
    assert "ship-history-*" in VALIDATE_PS1.read_text(encoding="utf-8")
