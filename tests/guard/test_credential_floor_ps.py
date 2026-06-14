"""No-python credential FLOOR PowerShell parity (credential_floor.ps1) - ADR-008 AC-S6.

Parity with credential_floor.sh: same AKIA / PEM / ghp_ shapes, same _BENIGN no-FP
corpus, same REDACTED output, binds `-Staged` (not `--staged`). Fakes built by concat
so no full literal sits in the repo.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FLOOR = ROOT / ".agentcortex" / "tools" / "credential_floor.ps1"
PS = shutil.which("pwsh") or shutil.which("powershell")

pytestmark = pytest.mark.skipif(PS is None, reason="PowerShell required for the .ps1 floor")


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                   encoding="utf-8", errors="replace", check=True)


def _repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    return tmp_path


def _run(cwd):
    return subprocess.run(
        [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(FLOOR), "-Staged"],
        cwd=str(cwd), capture_output=True, encoding="utf-8", errors="replace",
    )


_FAKES = {
    "aws-access-key-id": "AKIA" + "IOSFODNN7" + "EXAMPLE",
    "pem-private-key": "-----BEGIN " + "RSA PRIVATE KEY" + "-----",
    "github-token": "ghp_" + "A" * 36,
}
_BENIGN = [
    "the AKIA prefix marks an AWS access key id",
    "ghp_short and github_pat_short are not real",
    "use sk-123 as a short placeholder",
    "class sk-loading-spinner-component {}",
    "https://github.com/KbWen/agentic-os",
]


def test_ps_floor_catches_subset_redacted(tmp_path):
    repo = _repo(tmp_path)
    for name, fake in _FAKES.items():
        (repo / "f.txt").write_text("x = " + fake + "\n", encoding="utf-8")
        _git(repo, "add", "f.txt")
        r = _run(repo)
        assert r.returncode == 1, f"{name} not blocked (rc={r.returncode}, err={r.stderr!r})"
        assert name in r.stderr, f"{name} pattern-name missing"
        out = r.stdout + r.stderr
        assert not any(fake[i:i + 8] in out for i in range(len(fake) - 7)), f"{name} leaked value"
        _git(repo, "reset", "-q")


def test_ps_floor_no_false_positive(tmp_path):
    repo = _repo(tmp_path)
    for i, benign in enumerate(_BENIGN):
        (repo / f"b{i}.txt").write_text(benign + "\n", encoding="utf-8")
    _git(repo, "add", ".")
    r = _run(repo)
    assert r.returncode == 0, f"false positive: {r.stderr!r}"


def test_ps_floor_allowlist_pragma(tmp_path):
    repo = _repo(tmp_path)
    fake = "AKIA" + "IOSFODNN7" + "EXAMPLE"
    (repo / "doc.md").write_text(f"example: {fake}  # pragma: allowlist secret\n", encoding="utf-8")
    _git(repo, "add", ".")
    assert _run(repo).returncode == 0, "allowlist pragma must suppress the hit"


def test_ps_floor_git_failure_exits_3(tmp_path):
    """Not a git repo -> fail-CLOSED exit 3."""
    r = subprocess.run(
        [PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(FLOOR), "-Staged"],
        cwd=str(tmp_path), capture_output=True, encoding="utf-8", errors="replace",
    )
    assert r.returncode == 3
