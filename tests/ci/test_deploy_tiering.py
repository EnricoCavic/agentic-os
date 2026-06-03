"""Downstream file-preservation tiering tests (ADR-005) + override activation
structural tests (ADR-004).

Spec: docs/specs/downstream-fork-accommodation.md (AC-1..AC-10).

Behavioral tests shell out to the real deploy.sh into a temp target and assert:
  - AC-6: a user-modified framework SKILL is preserved via .acx-incoming sidecar
    (skills are scaffold-tier), and a net-new custom-* skill is never touched.
  - AC-5: a user-modified framework-authoritative core file (a rule) is
    force-updated with NO sidecar (governance must not drift).
Structural tests guard the wiring/parity against silent deletion.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEPLOY_SH = ROOT / ".agentcortex" / "bin" / "deploy.sh"
BOOTSTRAP = ROOT / ".agent" / "workflows" / "bootstrap.md"
DOC_GOV = ROOT / ".agentcortex" / "docs" / "guides" / "doc-governance.md"
ROUTING = ROOT / ".agent" / "workflows" / "routing.md"
VALIDATE_SH = ROOT / ".agentcortex" / "bin" / "validate.sh"
VALIDATE_PS1 = ROOT / ".agentcortex" / "bin" / "validate.ps1"
README = ROOT / "README.md"
README_ZH = ROOT / "docs" / "README_zh-TW.md"

bash = shutil.which("bash")
requires_bash = pytest.mark.skipif(bash is None, reason="bash not available")


def _deploy(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [bash, str(DEPLOY_SH), str(target)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )


# ---------------------------------------------------------------------------
# Behavioral (AC-5 / AC-6) — the core of ADR-005
# ---------------------------------------------------------------------------

@requires_bash
def test_skill_edit_sidecars_and_core_rule_force_updates() -> None:
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()

        first = _deploy(target)
        assert first.returncode == 0, f"first deploy failed:\n{first.stderr}"
        assert (target / ".agentcortex-manifest").exists(), "manifest not created"

        skill = target / ".agents" / "skills" / "api-design" / "SKILL.md"
        rule = target / ".agent" / "rules" / "engineering_guardrails.md"
        assert skill.exists(), "framework skill not deployed"
        assert rule.exists(), "framework rule not deployed"

        # User customizes a framework skill (the R1 scenario) and a core rule.
        skill.write_text(skill.read_text(encoding="utf-8") + "\n<!-- downstream edit -->\n", encoding="utf-8")
        rule.write_text(rule.read_text(encoding="utf-8") + "\n<!-- downstream edit -->\n", encoding="utf-8")

        # A net-new custom-* skill (reserved namespace, never in framework source).
        custom = target / ".agents" / "skills" / "custom-acme" / "SKILL.md"
        custom.parent.mkdir(parents=True, exist_ok=True)
        custom.write_text("# custom-acme\nproject-only skill\n", encoding="utf-8")

        second = _deploy(target)
        assert second.returncode == 0, f"update deploy failed:\n{second.stderr}"

        # AC-6: edited framework skill is PRESERVED via sidecar (not silently lost).
        assert skill.with_name("SKILL.md.acx-incoming").exists(), \
            "edited framework skill should produce a .acx-incoming sidecar"
        assert "<!-- downstream edit -->" in skill.read_text(encoding="utf-8"), \
            "user's skill edit must be preserved, not overwritten"

        # AC-6: net-new custom-* skill is never touched.
        assert custom.exists() and "project-only skill" in custom.read_text(encoding="utf-8"), \
            "custom-* skill must be preserved untouched"

        # AC-5: edited framework-authoritative core rule is FORCE-UPDATED, no sidecar.
        assert not rule.with_name("engineering_guardrails.md.acx-incoming").exists(), \
            "core rule must NOT produce a sidecar (governance must force-update)"
        assert "<!-- downstream edit -->" not in rule.read_text(encoding="utf-8"), \
            "core rule edit must be overwritten by the framework version"


# ---------------------------------------------------------------------------
# Structural — guard the wiring + cross-platform parity against silent drift
# ---------------------------------------------------------------------------

def test_deploy_classifies_skills_as_scaffold() -> None:
    s = DEPLOY_SH.read_text(encoding="utf-8")
    assert ".agent/skills/*|.agents/skills/*) echo \"scaffold\"" in s, \
        "deploy.sh must classify skills as scaffold (ADR-005)"


def test_bootstrap_ships_override_load_step() -> None:
    assert "Load Override Layer" in BOOTSTRAP.read_text(encoding="utf-8")


def test_doc_governance_override_is_active() -> None:
    txt = DOC_GOV.read_text(encoding="utf-8")
    assert "soft-launch" not in txt.split("## Override Layer", 1)[-1].split("##", 1)[0], \
        "override section must no longer be labeled soft-launch"
    assert "MUST read override files at session start" in txt


def test_routing_reserves_custom_namespace() -> None:
    txt = ROUTING.read_text(encoding="utf-8")
    assert "ship a skill whose name begins with" in txt and "custom-" in txt


def test_validators_check_override_step_parity() -> None:
    assert "Load Override Layer" in VALIDATE_SH.read_text(encoding="utf-8")
    assert "Load Override Layer" in VALIDATE_PS1.read_text(encoding="utf-8")


def test_readme_fork_guidance_parity() -> None:
    assert "Customizing Without Conflicts" in README.read_text(encoding="utf-8")
    assert "客製化而不衝突" in README_ZH.read_text(encoding="utf-8")


def test_framework_ships_no_custom_namespace_skill() -> None:
    """ADR-005 contract: the framework MUST NEVER ship a skill under the reserved
    custom-* downstream namespace. Regression guard (G-005) so a future framework
    PR adding such a skill fails CI instead of silently breaking the guarantee."""
    for base in (ROOT / ".agents" / "skills", ROOT / ".agent" / "skills"):
        if not base.exists():
            continue
        offenders = [p.name for p in base.iterdir() if p.name.startswith("custom-")]
        assert not offenders, f"framework must not ship custom-* skills (ADR-005): {offenders}"
