#!/usr/bin/env python3
"""Static pre-publication check for accidental local paths or credentials."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "results", "logs", "tmp", "__pycache__"}
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----"),
    "ssh_key_path": re.compile(r"(?:codex_minisv|\.ssh[/\\].*key)", re.I),
    "token_assignment": re.compile(r"(?:token|password|passwd|secret)\s*[=:]\s*[^#\s]+", re.I),
    "server_absolute_path": re.compile(r"(?:^|[\s=:\"'])/(?:home|data)/|[A-Za-z]:[/\\]Users[/\\]"),
}

def main() -> int:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix == ".pyc" or any(part in SKIP for part in path.parts):
            continue
        if path.name == "check_publication.py":
            continue
        if path.stat().st_size > 5_000_000:
            failures.append((path, "file larger than 5 MB"))
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            failures.append((path, f"cannot read: {exc}"))
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append((path, label))
    if failures:
        for path, reason in failures:
            print(f"FAIL\t{reason}\t{path.relative_to(ROOT)}")
        return 1
    print("PASS\tno credentials, server absolute paths, or oversized files detected")
    return 0

if __name__ == "__main__":
    sys.exit(main())
