"""Credential scanner tests (backlog #71 / issue #225).

Both directions: credential SHAPES are caught; benign / near-miss content is NOT
flagged; output is redacted (never the secret value). All fake credentials are
assembled at RUNTIME by string concatenation so NO complete credential literal
sits in the repo (no self-scan / TruffleHog / Secrets-Prohibition trip).

Tool: .agentcortex/tools/scan_credentials.py
Issue: https://github.com/KbWen/agentic-os/issues/225
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / ".agentcortex" / "tools" / "scan_credentials.py"


def _load():
    spec = importlib.util.spec_from_file_location("scan_credentials", TOOL)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _fakes() -> dict[str, str]:
    """credential-SHAPED but verifiably fake — built by concat so no full literal."""
    return {
        "aws-access-key-id": "AKIA" + "IOSFODNN7" + "EXAMPLE",          # AKIA + 16
        "pem-private-key": "-----BEGIN " + "RSA PRIVATE KEY" + "-----",
        "github-token": "ghp_" + "A" * 36,
        "github-pat": "github_pat_" + "B" * 24,
        "openai-key": "sk-" + "C" * 40,
        "slack-token": "xoxb-" + "1" * 14,
        "google-api-key": "AIza" + "D" * 35,
        "jwt": "eyJ" + "a" * 10 + "." + "b" * 10 + "." + "c" * 10,
        "connection-string-password":
            "postgres://" + "admin" + ":" + "s3cr3tpw" + "@db.example.com",
    }


_BENIGN = [
    "https://github.com/KbWen/agentic-os",            # normal URL, no user:pass@
    "the AKIA prefix marks an AWS access key id",     # AKIA not followed by 16
    "use sk-123 as a short placeholder",              # sk- too short
    "Authorization: Bearer your-token-here",          # placeholder, no JWT
    "class sk-loading-spinner-component {}",          # hyphenated, not 32 contiguous
    "redis://localhost:6379/0",                       # host:port, no :pass@
    "ghp_short and github_pat_short are not real",    # too short
    "AIzaSyShort",                                     # AIza too short
    "connect to postgres://localhost/mydb",           # no credentials
]


def test_catches_every_pattern():
    tool = _load()
    for name, fake in _fakes().items():
        names = {f[2] for f in tool.scan_text(fake, "x")}
        assert name in names, f"{name} not caught"


def test_no_false_positive_on_benign():
    tool = _load()
    for benign in _BENIGN:
        findings = tool.scan_text(benign, "x")
        assert findings == [], f"false positive on {benign!r} -> {findings}"


def test_output_is_redacted():
    tool = _load()
    for fake in _fakes().values():
        for label, lineno, name in tool.scan_text(fake, "secretfile"):
            assert fake not in f"{label}{lineno}{name}", "scanner leaked the value"


def test_main_exit_codes(tmp_path):
    dirty = tmp_path / "dirty.txt"
    dirty.write_text("token = " + "ghp_" + "Z" * 36 + "\n", encoding="utf-8")
    clean = tmp_path / "clean.txt"
    clean.write_text("just some normal text without secrets\n", encoding="utf-8")
    r_dirty = subprocess.run([sys.executable, str(TOOL), str(dirty)],
                             capture_output=True, text=True)
    r_clean = subprocess.run([sys.executable, str(TOOL), str(clean)],
                             capture_output=True, text=True)
    assert r_dirty.returncode == 1 and r_clean.returncode == 0
    assert ("Z" * 36) not in (r_dirty.stdout + r_dirty.stderr), "CLI leaked the value"
    assert "github-token" in r_dirty.stderr


def test_self_skip():
    """The scanner's own file + this test file are excluded by basename."""
    tool = _load()
    assert tool._is_self("a/b/scan_credentials.py")
    assert tool._is_self("tests/ci/test_scan_credentials.py")
    assert not tool._is_self("tests/ci/other.py")
