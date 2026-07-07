#!/usr/bin/env python3
"""Blob-size guard for the fixture-heavy test corpus (GitHub 100 MiB hard limit).

This plan multiplies fixtures (types x distributions x N=65537 x 4 versions) plus
per-fixture ``.cells/`` parquet and ``.segments.json``, so it will re-hit the GitHub
100 MiB push limit unless every oversized ``.bak`` is committed as ``*.bak.zst``
(see the fixture-size policy / ``compress_oversized_bak_fixtures`` convention).

``core.hooksPath`` is redirected to a global (Databricks) hooks dir in this
environment, so a repo-local ``.git/hooks/pre-push`` would never run. Instead this
is a plain checker invoked two ways:

- **CLI** — ``python -m tools.check_fixture_size`` (optionally ``--staged`` for a
  pre-push/CI gate) exits non-zero on any tracked/added blob >= the hard limit.
- **pytest** — ``tests/test_fixture_size_guard.py`` runs it over tracked files so
  the guard is enforced by the normal test suite / CI, not a git hook.

Only git-tracked and staged-added files are checked; gitignored raw ``*.bak`` files
(the local decompress cache) are correctly ignored.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIB = 1024 * 1024
HARD_LIMIT_MB = 100  # GitHub rejects blobs >= 100 MiB
WARN_LIMIT_MB = 50   # SHOULD compress at/above this


@dataclass(frozen=True)
class SizeViolation:
    path: str
    size_mb: float
    level: str  # "error" (>= hard) or "warn" (>= warn, < hard)
    hint: str


def _git(args: list[str], repo_root: Path) -> list[str]:
    """Run a git command returning NUL-separated names as a list (empty on error)."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [p for p in out.split("\0") if p]


def candidate_files(repo_root: Path = REPO_ROOT, *, staged_only: bool = False) -> list[Path]:
    """Files git would push: staged adds/mods, plus all tracked files unless staged_only."""
    names = set(_git(["diff", "--cached", "--name-only", "-z", "--diff-filter=AM"], repo_root))
    if not staged_only:
        names.update(_git(["ls-files", "-z"], repo_root))
    paths = []
    for name in names:
        p = repo_root / name
        if p.is_file() and not p.is_symlink():
            paths.append(p)
    return sorted(paths)


def _hint_for(path: Path) -> str:
    name = path.name
    if name.endswith(".bak"):
        return "commit as *.bak.zst (zstd-19) — conftest decompresses it at test time"
    if any(part.endswith(".cells") for part in path.parts):
        return "bound the .cells/ sidecar via sample+digest mode"
    if name.endswith(".parquet"):
        return "bound via sample+digest, or store the source compressed"
    return "compress or remove from version control"


def check_files(
    paths: list[Path],
    *,
    hard_mb: int = HARD_LIMIT_MB,
    warn_mb: int = WARN_LIMIT_MB,
    repo_root: Path = REPO_ROOT,
) -> list[SizeViolation]:
    """Return size violations (errors and warnings) sorted largest-first."""
    violations: list[SizeViolation] = []
    for p in paths:
        try:
            size = p.stat().st_size
        except OSError:
            continue
        size_mb = size / MIB
        if size >= hard_mb * MIB:
            level = "error"
        elif size >= warn_mb * MIB:
            level = "warn"
        else:
            continue
        rel = str(p.relative_to(repo_root)) if p.is_relative_to(repo_root) else str(p)
        violations.append(SizeViolation(rel, round(size_mb, 2), level, _hint_for(p)))
    return sorted(violations, key=lambda v: v.size_mb, reverse=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard against oversized committed blobs.")
    parser.add_argument("--staged", action="store_true", help="only check staged (added/modified) files")
    parser.add_argument("--hard-mb", type=int, default=HARD_LIMIT_MB, help="hard limit in MiB (default 100)")
    parser.add_argument("--warn-mb", type=int, default=WARN_LIMIT_MB, help="warn threshold in MiB (default 50)")
    args = parser.parse_args(argv)

    paths = candidate_files(staged_only=args.staged)
    violations = check_files(paths, hard_mb=args.hard_mb, warn_mb=args.warn_mb)

    errors = [v for v in violations if v.level == "error"]
    warns = [v for v in violations if v.level == "warn"]

    for v in warns:
        print(f"WARN  {v.size_mb:8.2f} MiB  {v.path}\n      -> {v.hint}", file=sys.stderr)
    for v in errors:
        print(f"ERROR {v.size_mb:8.2f} MiB  {v.path}\n      -> {v.hint}", file=sys.stderr)

    if errors:
        print(
            f"\n{len(errors)} blob(s) >= {args.hard_mb} MiB would be rejected by GitHub. "
            "Compress or remove them before pushing.",
            file=sys.stderr,
        )
        return 1
    if warns:
        print(f"\n{len(warns)} blob(s) >= {args.warn_mb} MiB (should compress); none over the hard limit.", file=sys.stderr)
    else:
        print("fixture-size guard: OK (no tracked/staged blob over thresholds).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
