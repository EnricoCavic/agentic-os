"""No-python credential FLOOR (credential_floor.sh) tests — ADR-008 AC-S4/S6.

The floor is a narrow FP-free SUBSET (AKIA / PEM / ghp_) for hosts WITHOUT Python:
it scans staged content and prints REDACTED `path:line: name`, exit 1 on hit / 0 clean
/ 3 on git failure. Fakes are built by concatenation so no full literal sits in the repo.
The floor is pure bash + grep — it never invokes Python (the no-python guarantee).
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FLOOR = ROOT / ".agentcortex" / "tools" / "credential_floor.sh"

# Resolve a REAL bash (Git Bash), excluding the WindowsApps WSL placeholder that
# emits a UTF-16 "install <Distro>" stub and never runs the script (per the
# [windows-install] lesson; mirrors tests/ci/test_deploy_tiering.py).
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
BASH = next(
    (c for c in bash_candidates if c and "WindowsApps" not in c and Path(c).exists()),
    None,
)
pytestmark = pytest.mark.skipif(BASH is None, reason="real bash (Git Bash) required for the shell floor")


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                   encoding="utf-8", errors="replace", check=True)


def _repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    return tmp_path


def _run(cwd):
    return subprocess.run([BASH, str(FLOOR)], cwd=str(cwd), capture_output=True, encoding="utf-8", errors="replace")


_FAKES = {
    "aws-access-key-id": "AKIA" + "IOSFODNN7" + "EXAMPLE",   # AKIA + 16
    "pem-private-key": "-----BEGIN " + "RSA PRIVATE KEY" + "-----",
    "github-token": "ghp_" + "A" * 36,
}

# benign content that MUST stay clean — the exact near-miss shapes for these 3 patterns
_BENIGN = [
    "the AKIA prefix marks an AWS access key id",
    "ghp_short and github_pat_short are not real",
    "use sk-123 as a short placeholder",
    "https://github.com/KbWen/agentic-os",
    "git_sha da39a3ee5e6b4b0d3255bfef95601890afd80709",
    "class sk-loading-spinner-component {}",
]


def test_floor_catches_subset_redacted(tmp_path):
    repo = _repo(tmp_path)
    for name, fake in _FAKES.items():
        (repo / "f.txt").write_text("x = " + fake + "\n", encoding="utf-8")
        _git(repo, "add", "f.txt")
        r = _run(repo)
        assert r.returncode == 1, f"{name} not blocked (rc={r.returncode}, err={r.stderr!r})"
        assert name in r.stderr, f"{name} pattern-name missing from output"
        out = r.stdout + r.stderr
        assert not any(fake[i:i + 8] in out for i in range(len(fake) - 7)), \
            f"{name}: floor leaked >=8 chars of the value"
        _git(repo, "reset", "-q")


def test_floor_no_false_positive(tmp_path):
    repo = _repo(tmp_path)
    for i, benign in enumerate(_BENIGN):
        (repo / f"b{i}.txt").write_text(benign + "\n", encoding="utf-8")
    _git(repo, "add", ".")
    r = _run(repo)
    assert r.returncode == 0, f"false positive: {r.stderr!r}"


def test_floor_clean_repo_exits_0(tmp_path):
    repo = _repo(tmp_path)
    (repo / "ok.txt").write_text("just some normal text without secrets\n", encoding="utf-8")
    _git(repo, "add", ".")
    assert _run(repo).returncode == 0


def test_floor_allowlist_pragma(tmp_path):
    repo = _repo(tmp_path)
    fake = "AKIA" + "IOSFODNN7" + "EXAMPLE"
    (repo / "doc.md").write_text(f"example: {fake}  # pragma: allowlist secret\n", encoding="utf-8")
    _git(repo, "add", ".")
    assert _run(repo).returncode == 0, "allowlist pragma must suppress the hit"


def test_floor_git_failure_exits_3(tmp_path):
    """Not a git repo → fail-CLOSED exit 3 (never 0 'clean')."""
    r = subprocess.run([BASH, str(FLOOR)], cwd=str(tmp_path), capture_output=True, encoding="utf-8", errors="replace")
    assert r.returncode == 3
