#!/usr/bin/env python3
"""Restore a real-world .bak on the current SQL Server and re-backup
to capture the native on-disk format of that SQL Server version.

Use-case
--------
Many real-world backups in ``tests/fixtures_realworld/`` originate from old
SQL Server versions (2008R2, 2012, 2014, 2016).  Restoring them on a modern
engine and re-backing up produces a new ``.bak`` whose *backup-file format*
belongs to the modern engine while its *data* (compatibility level, row
format, page types) matches the original source.  This isolates whether
format differences in the backup container itself cause parser regressions.

Output filename convention
--------------------------
``{source_stem}_{ss_year}.bak``  — e.g. ``NYCTaxi_Sample_2017.bak``

The source .bak is not modified; only a new file is created.

Scan mode (--scan-dir)
----------------------
Scans a directory for ``.bak`` files that do NOT already come from one of the
four standard fixture versions (2017 / 2019 / 2022 / 2025), and rebaks each
one.  Files whose stem already ends with a standard year (e.g.
``AdventureWorks2022.bak``) or with ``_{year}`` (e.g.
``NYCTaxi_Sample_2019.bak``) are skipped automatically.

Usage
-----
  # Single file against the current server
  python -m tools.fixture_run --server <blob> rebak-realworld \\
      --source tests/fixtures_realworld/NYCTaxi_Sample.bak

  # Scan the whole realworld dir (run once per server version)
  python -m tools.fixture_run --server <blob> rebak-realworld \\
      --scan-dir tests/fixtures_realworld/
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.register_bak import (  # noqa: E402
    _bak_header_info,
    _copy_bak,
    _drop_db,
    _restore_bak,
    _run,
    _run_sql,
    _server_db_version,
    _ss_year_for_db_version,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_STANDARD_YEARS: frozenset[str] = frozenset({"2017", "2019", "2022", "2025"})
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCAN_DIR = REPO_ROOT / "tests" / "fixtures_realworld"

# Temp DB name prefix used during restore+rebak.  Kept short to avoid SQL
# Server's 128-char identifier limit on very long source names.
_TEMP_DB_PREFIX = "rebak_"
_MAX_STEM_LEN = 80  # truncate after prefix


# ---------------------------------------------------------------------------
# Filename heuristics
# ---------------------------------------------------------------------------

def _is_standard_year_source(stem: str) -> bool:
    """Return True if *stem* looks like it already comes from a standard SS year.

    Matches stems that end with a 4-digit standard year, optionally preceded
    by a separator (``_`` or ``-``).  Examples:
      ``AdventureWorks2022``   → True   (bare year suffix)
      ``AdventureWorks_2019``  → True   (underscore-separated)
      ``NYCTaxi_Sample``       → False  (no year suffix)
      ``IndexInternals2008``   → False  (2008 not a standard year)
    """
    m = re.search(r"[_-]?(\d{4})$", stem)
    return m is not None and m.group(1) in _STANDARD_YEARS


def _is_rebaked_output(stem: str) -> bool:
    """Return True if *stem* looks like an already-rebaked output.

    Pattern: ``{original_stem}_{year}`` where year is a standard year.
    e.g. ``NYCTaxi_Sample_2017`` → True.
    """
    m = re.match(r"^(.+)_(\d{4})$", stem)
    return m is not None and m.group(2) in _STANDARD_YEARS


def _scan_candidates(scan_dir: Path) -> list[Path]:
    """Return .bak files in *scan_dir* that are candidates for rebaking.

    Excludes:
    - Files that look like they already originate from a standard SS year
      (filename heuristic — avoids copying large files to the container).
    - Files that look like previously rebaked outputs (``_{year}.bak``).
    """
    candidates: list[Path] = []
    for bak in sorted(scan_dir.glob("*.bak")):
        stem = bak.stem
        if _is_standard_year_source(stem):
            print(f"  scan: skip {bak.name} (standard-year source)", file=sys.stderr)
            continue
        if _is_rebaked_output(stem):
            print(f"  scan: skip {bak.name} (already a rebaked output)", file=sys.stderr)
            continue
        candidates.append(bak)
    return candidates


# ---------------------------------------------------------------------------
# Core rebak logic
# ---------------------------------------------------------------------------

def _rebak_one(
    container: str,
    password: str,
    source_bak: Path,
    out_dir: Path,
    *,
    force: bool = False,
    skip_standard: bool = True,
) -> int:
    """Restore *source_bak* and re-backup in the server's native format.

    Parameters
    ----------
    container:      Podman container name.
    password:       SA / dba password.
    source_bak:     Local path to the source ``.bak`` file.
    out_dir:        Directory for the output ``.bak``.
    force:          Overwrite an existing output; do not skip standard-year sources.
    skip_standard:  When True (default), skip sources that appear to come from a
                    standard year (confirmed via RESTORE HEADERONLY).

    Returns 0 on success, 1 on skip, 2 on error.
    """
    # Detect target server version first (cheap — one SQL round-trip).
    srv_db_ver = _server_db_version(container, password)
    if not srv_db_ver:
        print("error: could not detect server database version", file=sys.stderr)
        return 2
    ss_year = _ss_year_for_db_version(srv_db_ver)

    out_path = out_dir / f"{source_bak.stem}_{ss_year}.bak"
    if out_path.exists() and not force:
        print(f"skip (already exists): {out_path.name}", file=sys.stderr)
        return 1

    # Copy source into container once; reuse for HEADERONLY + RESTORE.
    print(f"==> copying {source_bak.name} into container …", file=sys.stderr)
    container_src = _copy_bak(container, source_bak)

    # Check source version (HEADERONLY; requires file already in container).
    _, src_db_ver = _bak_header_info(container, password, container_src)
    src_year = _ss_year_for_db_version(src_db_ver) if src_db_ver else "unknown"

    if skip_standard and not force and src_year in _STANDARD_YEARS:
        print(
            f"skip: {source_bak.name} is already from SQL Server {src_year} "
            f"(DatabaseVersion={src_db_ver}); pass --force to rebak anyway",
            file=sys.stderr,
        )
        return 1

    print(
        f"==> {source_bak.name}  src=SS{src_year}(ver={src_db_ver})"
        f"  →  {out_path.name}  tgt=SS{ss_year}",
        file=sys.stderr,
    )

    db_name = (_TEMP_DB_PREFIX + source_bak.stem)[:_MAX_STEM_LEN]
    container_out = f"/tmp/{out_path.name}"

    # Drop any leftover temp DB from a previous failed run.
    _drop_db(container, password, db_name)

    try:
        # Restore using the shared helper (handles full / diff / striped).
        # _restore_bak calls _copy_bak internally, but we already copied it;
        # the second copy is cheap for local Podman and keeps the API clean.
        _restore_bak(container, password, source_bak, db_name)

        # Re-backup in the server's native format.
        backup_sql = (
            f"USE [master];\nGO\n"
            f"BACKUP DATABASE [{db_name}] TO DISK=N'{container_out}'"
            f" WITH FORMAT, INIT;\nGO\n"
        )
        _run_sql(container, password, backup_sql)

        # Copy the new .bak out.
        cp = _run(["podman", "cp", f"{container}:{container_out}", str(out_path)])
        if cp.returncode:
            raise RuntimeError(f"podman cp out failed:\n{cp.stderr}")

        size = out_path.stat().st_size
        print(f"wrote {out_path} ({size:,} bytes)", file=sys.stderr)
    finally:
        _drop_db(container, password, db_name)
        # Remove temp backup from container (best effort).
        _run(["podman", "exec", container, "rm", "-f", container_out])

    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__, formatter_class=_ap.RawDescriptionHelpFormatter)

    src_group = p.add_mutually_exclusive_group(required=True)
    src_group.add_argument(
        "--source",
        metavar="BAK",
        help="path to a specific source .bak file to restore and re-backup",
    )
    src_group.add_argument(
        "--scan-dir",
        metavar="DIR",
        help=(
            "scan a directory for candidate .bak files and rebak each one "
            "(skips files that appear to originate from a standard SS year by "
            "filename heuristic, then confirms via RESTORE HEADERONLY)"
        ),
    )
    p.add_argument(
        "--out-dir",
        default=None,
        metavar="DIR",
        help="output directory for rebaked .bak files (default: same dir as source)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help=(
            "overwrite an existing output file; also rebak sources from standard "
            "years (2017/2019/2022/2025) that would normally be skipped"
        ),
    )
    args = p.parse_args()

    container = os.environ.get("FIXTURE_SERVER_NAME", "")
    if not container:
        print("error: FIXTURE_SERVER_NAME not set — run via fixture_run.py or set env vars",
              file=sys.stderr)
        return 2
    password = os.environ.get("FIXTURE_DBA_PASSWORD", "")
    if not password:
        print("error: FIXTURE_DBA_PASSWORD not set", file=sys.stderr)
        return 2

    if args.source:
        source = Path(args.source)
        if not source.is_file():
            print(f"error: {source} not found", file=sys.stderr)
            return 2
        out_dir = Path(args.out_dir) if args.out_dir else source.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        rc = _rebak_one(container, password, source, out_dir, force=args.force)
        return 0 if rc in (0, 1) else rc

    # --scan-dir mode
    scan_dir = Path(args.scan_dir)
    if not scan_dir.is_dir():
        print(f"error: {scan_dir} is not a directory", file=sys.stderr)
        return 2
    out_dir = Path(args.out_dir) if args.out_dir else scan_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = _scan_candidates(scan_dir)
    if not candidates:
        print("==> no rebak candidates found", file=sys.stderr)
        return 0

    print(f"==> {len(candidates)} candidate(s) to rebak …", file=sys.stderr)
    errors: list[tuple[Path, str]] = []
    for bak in candidates:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"==> {bak.name}", file=sys.stderr)
        try:
            rc = _rebak_one(
                container, password, bak, out_dir,
                force=args.force,
                skip_standard=True,
            )
            if rc == 2:
                errors.append((bak, "returned error code 2"))
        except Exception as exc:
            errors.append((bak, str(exc)))
            print(f"  ERROR: {exc}", file=sys.stderr)

    print(
        f"\n==> rebak complete: {len(candidates) - len(errors)} ok, {len(errors)} failed",
        file=sys.stderr,
    )
    for bak, msg in errors:
        print(f"  FAILED {bak.name}: {msg}", file=sys.stderr)
    return len(errors)


if __name__ == "__main__":
    sys.exit(main())
