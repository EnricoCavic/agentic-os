#!/usr/bin/env python3
"""Credential pattern scanner — T1 pre-commit machine layer for the AGENTS.md
Secrets Prohibition invariant (backlog #71 / issue #225).

Reports content that matches common credential SHAPES WITHOUT echoing the secret
value (redacted: ``path:line: pattern-name`` only). CI TruffleHog remains the
post-commit backstop; this is the pre-commit fast-catch so a secret never enters
object history (where rotation, not deletion, becomes the remedy).

Modes:
  --staged              scan only newly-ADDED lines of the git staged diff
                        (``git diff --cached -U0``) — the pre-commit use case.
  <file> [<file> ...]   scan the given files.
  (stdin)               scan stdin when no files and not --staged.

Exit: 1 if any credential pattern matches, 0 if clean, 2 on usage error.

Self-exclusion: this scanner's own source and the test fixture file are skipped —
their pattern definitions / runtime-assembled fakes are not secrets.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# (name, compiled regex). Deliberately tight, distinctive-prefix shapes to keep the
# false-positive surface low; the no-false-positive fixtures guard precision.
_PATTERNS: list[tuple[str, "re.Pattern[str]"]] = [
    ("aws-access-key-id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("pem-private-key",
     re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}")),
    ("connection-string-password",
     re.compile(r"\b[a-z][a-z0-9+.\-]{1,15}://[^\s:@/]{1,64}:[^\s:@/]{6,64}@[a-zA-Z0-9._\-]+")),
]

# Files whose matches are definitions/fixtures, not real secrets.
_SELF_SKIP = ("scan_credentials.py", "test_scan_credentials.py")


def _is_self(path: str) -> bool:
    base = path.replace("\\", "/").rsplit("/", 1)[-1]
    return base in _SELF_SKIP


def scan_text(text: str, label: str) -> list[tuple[str, int, str]]:
    """Return ``(label, lineno, pattern_name)`` per match. NEVER returns the value."""
    findings: list[tuple[str, int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, rx in _PATTERNS:
            if rx.search(line):
                findings.append((label, lineno, name))
    return findings


def _staged_added_lines() -> list[tuple[str, str]]:
    """Return ``(path, added-content)`` per staged file from ``git diff --cached -U0``.

    Only ``+`` added lines are scanned (not context/removed) so the scan targets
    NEW content entering the commit.
    """
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "-U0", "--no-color"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    files: dict[str, list[str]] = {}
    cur: str | None = None
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
            files.setdefault(cur, [])
        elif line.startswith("+++ "):
            cur = None
        elif cur is not None and line.startswith("+") and not line.startswith("+++"):
            files[cur].append(line[1:])
    return [(p, "\n".join(v)) for p, v in files.items() if v]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan for credential patterns (redacted output)")
    ap.add_argument("--staged", action="store_true",
                    help="scan git staged-diff added lines")
    ap.add_argument("files", nargs="*", help="files to scan")
    args = ap.parse_args()

    findings: list[tuple[str, int, str]] = []
    if args.staged:
        for path, content in _staged_added_lines():
            if not _is_self(path):
                findings += scan_text(content, path)
    elif args.files:
        for f in args.files:
            if _is_self(f):
                continue
            try:
                findings += scan_text(
                    Path(f).read_text(encoding="utf-8", errors="replace"), f)
            except (OSError, ValueError):
                continue
    else:
        findings += scan_text(sys.stdin.read(), "<stdin>")

    if findings:
        print("CREDENTIAL PATTERN(S) DETECTED (values redacted):", file=sys.stderr)
        for label, lineno, name in findings:
            print(f"  {label}:{lineno}: {name}", file=sys.stderr)
        print("Rotate the exposed secret, remove it from the change, then retry.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
