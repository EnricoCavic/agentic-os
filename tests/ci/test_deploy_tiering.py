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

import os
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


git_path = shutil.which("git")
git_root = Path(git_path).parent.parent if git_path else None
bash_candidates = [
    str(git_root / "bin" / "bash.exe") if git_root else None,
    str(git_root / "usr" / "bin" / "bash.exe") if git_root else None,
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files\Git\usr\bin\bash.exe",
    r"C:\Program Files (x86)\Git\bin\bash.exe",
    shutil.which("bash"),
]
bash = next(
    (
        candidate for candidate in bash_candidates
        if candidate and "WindowsApps" not in candidate and Path(candidate).exists()
    ),
    None,
)
requires_bash = pytest.mark.skipif(bash is None, reason="bash not available")
powershell = shutil.which("powershell") or shutil.which("pwsh")
requires_powershell = pytest.mark.skipif(powershell is None, reason="PowerShell not available")


def _deploy(target: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    run_env = {**os.environ, **env} if env else None
    return subprocess.run(
        [bash, str(DEPLOY_SH), str(target)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=run_env,
    )


def _deploy_ps1(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            powershell,
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / ".agentcortex" / "bin" / "deploy.ps1"),
            str(target),
        ],
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


@requires_bash
def test_modified_core_rule_backs_up_to_acx_local_and_is_not_silent() -> None:
    """#173: a locally-modified core file is force-updated (ADR-005 invariant),
    but its previous version is backed up to a .acx-local sidecar and the
    overwrite is surfaced in deploy output — never silently lost."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()

        assert _deploy(target).returncode == 0
        rule = target / ".agent" / "rules" / "engineering_guardrails.md"
        assert rule.exists()

        marker = "<!-- downstream core tweak 173 -->"
        rule.write_text(rule.read_text(encoding="utf-8") + f"\n{marker}\n", encoding="utf-8")

        second = _deploy(target)
        assert second.returncode == 0, f"update failed:\n{second.stderr}"

        backup = rule.with_name("engineering_guardrails.md.acx-local")
        # The user's edit is recoverable from the .acx-local backup ...
        assert backup.exists(), "modified core file must back up to .acx-local"
        assert marker in backup.read_text(encoding="utf-8"), \
            "the .acx-local backup must contain the user's edit"
        # ... while the live file is force-updated (ADR-005 invariant preserved) ...
        assert marker not in rule.read_text(encoding="utf-8"), \
            "core rule must still be force-updated to the framework version"
        # ... using .acx-local, NOT .acx-incoming (parity with the AC-5 contract).
        assert not rule.with_name("engineering_guardrails.md.acx-incoming").exists()
        # ... and the overwrite is NOT silent.
        assert "acx-local" in second.stdout, \
            "deploy must surface the core overwrite (non-silent)"

        # Idempotency: a second update (file now matches framework) must NOT
        # re-flag or create another backup.
        backup.unlink()
        third = _deploy(target)
        assert third.returncode == 0
        assert not backup.exists(), \
            "unmodified core file must not be flagged as locally-modified"
        assert "acx-local" not in third.stdout


@requires_bash
def test_core_backup_not_skipped_under_cp_flag_n() -> None:
    """#173 regression: the .acx-local backup must ALWAYS land, even with
    CP_FLAG=-n. .acx-local is never auto-cleaned, so a stale one + `cp -n`
    would silently skip the backup and lose the newest local edits — exactly
    the data loss this fix closes."""
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()
        assert _deploy(target).returncode == 0
        rule = target / ".agent" / "rules" / "engineering_guardrails.md"
        backup = rule.with_name("engineering_guardrails.md.acx-local")
        base = rule.read_text(encoding="utf-8")

        # First local edit, then a no-clobber (CP_FLAG=-n) update creates .acx-local(A).
        rule.write_text(base + "\n<!-- edit A -->\n", encoding="utf-8")
        assert _deploy(target, env={"CP_FLAG": "-n"}).returncode == 0
        assert backup.exists() and "edit A" in backup.read_text(encoding="utf-8")

        # Second local edit, then another -n update. The stale backup must be
        # replaced with edit B — NOT skipped by `cp -n`.
        rule.write_text(base + "\n<!-- edit B -->\n", encoding="utf-8")
        assert _deploy(target, env={"CP_FLAG": "-n"}).returncode == 0
        bk = backup.read_text(encoding="utf-8")
        assert "edit B" in bk, "newest local edits must be backed up, not skipped under CP_FLAG=-n"
        assert "edit A" not in bk, "stale backup must be replaced, not retained"


def test_deploy_gitignores_acx_local_sidecar() -> None:
    """#173: the .acx-local backup is deploy-generated; it must be in the
    managed downstream .gitignore block (parity with *.acx-incoming) so it
    does not pollute the downstream working tree."""
    s = DEPLOY_SH.read_text(encoding="utf-8")
    assert "*.acx-local" in s, "deploy.sh must add *.acx-local to the managed .gitignore block"


@requires_powershell
def test_deploy_ps1_entrypoint_resolves_real_bash() -> None:
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()

        result = _deploy_ps1(target)
        assert result.returncode == 0, (
            f"deploy.ps1 failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert (target / ".agentcortex-manifest").exists(), "deploy.ps1 should create manifest"


@requires_bash
def test_deployed_governance_referenced_tools_are_deployed() -> None:
    """Regression: every `.agentcortex/tools/<name>.py` that a DEPLOYED governance
    doc instructs a downstream agent to run MUST itself be deployed. The runtime-
    tools whitelist in deploy.sh is hand-maintained, so a new feature that adds a
    workflow tool but forgets the whitelist ships a dangling `python ...` command
    that fails with 'No such file' in every downstream bootstrap/review.
    Found via downstream simulation (recover_worklog_lock.py + lint_spec_drift.py
    were referenced by bootstrap.md / review.md but absent from the deployed tree).
    """
    import re

    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()
        assert _deploy(target).returncode == 0, "deploy failed"

        gov_files: list[Path] = [target / "AGENTS.md", target / "CLAUDE.md"]
        for sub in (".agent/workflows", ".agent/rules"):
            d = target / sub
            if d.exists():
                gov_files.extend(sorted(d.glob("*.md")))

        pat = re.compile(r"\.agentcortex/tools/([A-Za-z0-9_]+\.py)")
        referenced: set[str] = set()
        for f in gov_files:
            if f.exists():
                referenced.update(pat.findall(f.read_text(encoding="utf-8")))

        tools_dir = target / ".agentcortex" / "tools"
        missing = sorted(name for name in referenced if not (tools_dir / name).exists())
        assert not missing, (
            "deployed governance docs reference tools that deploy.sh did not ship "
            f"(add them to the runtime_tools whitelist in deploy.sh): {missing}"
        )
        # Sanity: the two tools this regression was opened for are now shipped.
        assert (tools_dir / "recover_worklog_lock.py").exists()
        assert (tools_dir / "lint_spec_drift.py").exists()


@requires_bash
def test_deploy_does_not_scaffold_docs_architecture() -> None:
    """`docs/architecture/` is intentionally capability-by-presence, NOT a fixed
    anchor like docs/adr/ + docs/specs/. It is created on demand by /app-init;
    bootstrap.md keys the "skip all Domain Doc steps, zero extra reads"
    optimization on its ABSENCE. Scaffolding it empty on deploy would silently
    flip that optimization off for every downstream project. This guard locks in
    the no-scaffold design so a well-meaning "fix" cannot regress it.
    (engineering_guardrails.md §4.2 / bootstrap.md capability-by-presence.)
    """
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "proj"
        target.mkdir()
        assert _deploy(target).returncode == 0, "deploy failed"

        # The two fixed anchors ARE scaffolded ...
        assert (target / "docs" / "adr").is_dir(), "docs/adr/ is a fixed anchor"
        assert (target / "docs" / "specs").is_dir(), "docs/specs/ is a fixed anchor"
        # ... but docs/architecture/ must NOT be (capability-by-presence).
        assert not (target / "docs" / "architecture").exists(), (
            "deploy must NOT scaffold docs/architecture/ — it is created on demand "
            "by /app-init; its absence drives bootstrap's zero-read optimization"
        )


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
