#!/usr/bin/env python3
"""Capture verifier sidecars for ARCHIVE columnstore fixtures (A1 step).

For each target .bak file, restores the database (if needed) and queries
``sys.column_store_segments`` + ``sys.column_store_row_groups`` to produce a
``.segments.json`` file alongside the .bak.  This sidecar is the ground-truth
reference for:

  - encoding_type per column per segment (confirms enc=1 vs enc=5 per bug)
  - null_count per column per segment (confirms where our decoder diverges)
  - on_disk_size per segment (cross-checks the blob bytes we extract from .bak)

The sidecar supports the A1 tier of the top-down/bottom-up verification
strategy described in docs/260616-2-fixture-dbcc-page-verifier.md §13.3.

Usage (recommended — credentials loaded via forgedb)::

    python -m tools.fixture_run capture-verifier-sidecar

Or for all four SQL Server versions::

    python -m tools.fixture_run all-versions --suite capture-verifier-sidecar

Or directly (env vars must be set)::

    FIXTURE_DBA_PASSWORD=... FIXTURE_CONTAINER=... \\
        python -m tools.capture_verifier_sidecar

Output files written alongside each input .bak::

    tests/fixtures_2022/archive_columnstore_partition_full.bak.segments.json
    tests/fixtures_2022/archive_columnstore_types_full.bak.segments.json
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import (  # noqa: E402
    fixture_credentials,
    skip_if_exists,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))

# Target .bak files to capture.  Relative to FIXTURE_DIR.
_TARGET_BAKS = [
    "archive_columnstore_partition_full.bak",
    "archive_columnstore_types_full.bak",
]

# Temporary path inside the container for SQL scripts.
_CONTAINER_SQL = "/tmp/_capture_verifier_q.sql"

_SQLCMD_CANDIDATES = [
    "/opt/mssql-tools18/bin/sqlcmd",
    "/opt/mssql-tools/bin/sqlcmd",
]


# ---------------------------------------------------------------------------
# sqlcmd helpers (local copies — avoids circular imports with fixture_utils)
# ---------------------------------------------------------------------------

def _discover_sqlcmd(container: str) -> str:
    for candidate in _SQLCMD_CANDIDATES:
        r = subprocess.run(
            ["podman", "exec", container, "test", "-f", candidate],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            return candidate
    raise RuntimeError(
        f"sqlcmd not found in container {container!r}; tried: {_SQLCMD_CANDIDATES}"
    )


def _run(cmd: list[str], **kw: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, **kw)


def _run_sql(container: str, password: str, sql: str, *, sep: str = "|") -> str:
    """Execute *sql* inside *container*; return stdout."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
        f.write(sql)
        local = f.name
    try:
        _run(["podman", "cp", local, f"{container}:{_CONTAINER_SQL}"])
        cmd = [
            "podman", "exec", container,
            _discover_sqlcmd(container),
            "-S", "localhost", "-U", "sa", "-P", password,
            "-C",           # trust self-signed cert
            "-W",           # remove trailing whitespace
            "-h", "-1",     # no column headers
            "-s", sep,
            "-i", _CONTAINER_SQL,
        ]
        r = _run(cmd)
        return r.stdout
    finally:
        try:
            os.unlink(local)
        except OSError:
            pass
        _run(["podman", "exec", container, "rm", "-f", _CONTAINER_SQL])


# ---------------------------------------------------------------------------
# Restore helper
# ---------------------------------------------------------------------------

def _db_exists(container: str, password: str, db_name: str) -> bool:
    sql = f"SELECT name FROM sys.databases WHERE name = N'{db_name}';"
    out = _run_sql(container, password, sql)
    return db_name in out


def _restore_bak(container: str, password: str, bak_path: Path, db_name: str) -> None:
    """Restore *bak_path* as *db_name* in *container* (MDF/LDF redirected to /tmp)."""
    container_bak = f"/tmp/{bak_path.name}"
    print(f"  copying {bak_path.name} into container …", file=sys.stderr)
    r = _run(["podman", "cp", str(bak_path), f"{container}:{container_bak}"])
    if r.returncode != 0:
        raise RuntimeError(f"podman cp failed: {r.stderr}")

    # Get the logical file names so we can redirect data/log to /tmp.
    filelist_sql = f"RESTORE FILELISTONLY FROM DISK = N'{container_bak}';"
    filelist_out = _run_sql(container, password, filelist_sql)

    moves = []
    for line in filelist_out.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        logical = parts[0]
        if not logical or logical.startswith("-"):
            continue
        ext = ".ldf" if parts[1].endswith(".ldf") else ".mdf"
        moves.append(f"MOVE N'{logical}' TO N'/tmp/{db_name}{ext}'")

    if not moves:
        raise RuntimeError(f"RESTORE FILELISTONLY returned no files for {bak_path.name}")

    move_clause = ",\n    ".join(moves)
    restore_sql = (
        f"RESTORE DATABASE [{db_name}]\n"
        f"FROM DISK = N'{container_bak}'\n"
        f"WITH {move_clause},\n"
        f"     REPLACE, RECOVERY, STATS = 10;\n"
    )
    print(f"  restoring as [{db_name}] …", file=sys.stderr)
    out = _run_sql(container, password, restore_sql)
    if "RESTORE DATABASE successfully" not in out and "successfully processed" not in out:
        # Check if it already exists and the restore just printed progress without
        # the final line (some versions omit it).
        if not _db_exists(container, password, db_name):
            raise RuntimeError(f"RESTORE failed for {bak_path.name}:\n{out}")
    # The restored DB no longer needs the .bak copy. Remove it immediately so a
    # bulk --all run does not fill the container's /tmp (the accumulated copies
    # otherwise cause later 'RESTORE FILELISTONLY returned no files' failures).
    _run(["podman", "exec", container, "rm", "-f", container_bak])
    print(f"  restored [{db_name}]", file=sys.stderr)


# ---------------------------------------------------------------------------
# Segment metadata queries
# ---------------------------------------------------------------------------

_SEGMENTS_SQL = """\
USE [{db}];
SET NOCOUNT ON;
SELECT
    OBJECT_SCHEMA_NAME(p.object_id)     AS schema_name,
    OBJECT_NAME(p.object_id)            AS table_name,
    c.name                              AS column_name,
    c.column_id                         AS column_id,
    p.partition_number                  AS partition_number,
    css.segment_id                      AS segment_id,
    css.version                         AS segment_version,
    css.encoding_type                   AS encoding_type,
    css.row_count                       AS row_count,
    CAST(css.has_nulls AS INT)          AS has_nulls,
    css.null_value                      AS null_value,
    CAST(css.min_data_id AS BIGINT)     AS min_data_id,
    CAST(css.max_data_id AS BIGINT)     AS max_data_id,
    css.on_disk_size                    AS on_disk_size,
    css.base_id                         AS base_id,
    css.magnitude                       AS magnitude
FROM sys.column_store_segments css
JOIN sys.partitions p
    ON css.hobt_id = p.hobt_id
JOIN sys.indexes i
    ON p.object_id = i.object_id AND p.index_id = i.index_id
JOIN sys.columns c
    ON p.object_id = c.object_id AND css.column_id = c.column_id
WHERE i.type IN (5, 6)
ORDER BY table_name, partition_number, segment_id, column_id;
"""

_ROW_GROUPS_SQL = """\
USE [{db}];
SET NOCOUNT ON;
SELECT
    OBJECT_SCHEMA_NAME(object_id)   AS schema_name,
    OBJECT_NAME(object_id)          AS table_name,
    partition_number                AS partition_number,
    row_group_id                    AS row_group_id,
    state                           AS state,
    state_description               AS state_description,
    total_rows                      AS total_rows,
    deleted_rows                    AS deleted_rows,
    size_in_bytes                   AS size_in_bytes
FROM sys.column_store_row_groups
ORDER BY table_name, partition_number, row_group_id;
"""

# Dictionaries feed the dict_scope qualifier: dictionary_id = 0 is the global
# (primary) dictionary for a column; > 0 are local/per-segment (secondary).
_DICTIONARIES_SQL = """\
USE [{db}];
SET NOCOUNT ON;
SELECT
    OBJECT_SCHEMA_NAME(p.object_id) AS schema_name,
    OBJECT_NAME(p.object_id)        AS table_name,
    c.name                          AS column_name,
    d.column_id                     AS column_id,
    d.dictionary_id                 AS dictionary_id,
    d.version                       AS version,
    d.type                          AS type,
    d.last_id                       AS last_id,
    d.entry_count                   AS entry_count,
    d.on_disk_size                  AS on_disk_size
FROM sys.column_store_dictionaries d
JOIN sys.partitions p
    ON d.hobt_id = p.hobt_id
JOIN sys.indexes i
    ON p.object_id = i.object_id AND p.index_id = i.index_id
JOIN sys.columns c
    ON p.object_id = c.object_id AND d.column_id = c.column_id
WHERE i.type IN (5, 6)
ORDER BY table_name, column_id, dictionary_id;
"""


def _parse_rows(raw: str, fields: list[str]) -> list[dict[str, Any]]:
    """Parse pipe-separated sqlcmd output into a list of dicts."""
    rows: list[dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("-") or line == "":
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != len(fields):
            continue
        row: dict[str, Any] = {}
        for field, val in zip(fields, parts):
            # Coerce to int where possible
            try:
                row[field] = int(val)
            except (ValueError, TypeError):
                row[field] = val if val != "NULL" else None
        rows.append(row)
    return rows


_SEG_FIELDS = [
    "schema_name", "table_name", "column_name", "column_id",
    "partition_number", "segment_id", "segment_version", "encoding_type",
    "row_count", "has_nulls", "null_value",
    "min_data_id", "max_data_id", "on_disk_size", "base_id", "magnitude",
]
# segment_version: -2147483647 = COLUMNSTORE_ARCHIVE, 1 = regular COLUMNSTORE
_ARCHIVE_VERSION = -2147483647

_RG_FIELDS = [
    "schema_name", "table_name", "partition_number", "row_group_id",
    "state", "state_description", "total_rows", "deleted_rows", "size_in_bytes",
]

_DICT_FIELDS = [
    "schema_name", "table_name", "column_name", "column_id",
    "dictionary_id", "version", "type", "last_id", "entry_count", "on_disk_size",
]

# sys.column_store_row_groups.state enum.
_RG_STATE_TOMBSTONE = 4


def _reconcile_row_groups(row_groups: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-table live-vs-total reconciliation — the offline tombstone-filter verifier.

    ``live_rows`` is what the decoder MUST emit for the table: the sum over every
    non-TOMBSTONE row group of ``total_rows - deleted_rows``. TOMBSTONE row groups
    are fully dead (their rows were already migrated to a new compressed group), so
    they contribute zero. A decoder that fails to drop tombstones / delete-bitmap
    rows will exceed ``live_rows``; one that over-drops will fall short.
    """
    recon: dict[str, Any] = {}
    for rg in row_groups:
        tbl = rg["table_name"]
        t = recon.setdefault(
            tbl,
            {
                "total_rows": 0,
                "deleted_rows": 0,
                "live_rows": 0,
                "n_row_groups": 0,
                "state_counts": {},
                "tombstone_row_group_ids": [],
            },
        )
        total = rg.get("total_rows") or 0
        deleted = rg.get("deleted_rows") or 0
        state_desc = rg.get("state_description") or str(rg.get("state"))
        t["n_row_groups"] += 1
        t["total_rows"] += total
        t["deleted_rows"] += deleted
        t["state_counts"][state_desc] = t["state_counts"].get(state_desc, 0) + 1
        if rg.get("state") == _RG_STATE_TOMBSTONE or state_desc.upper() == "TOMBSTONE":
            t["tombstone_row_group_ids"].append(rg.get("row_group_id"))
        else:
            t["live_rows"] += max(total - deleted, 0)
    for t in recon.values():
        t["has_tombstones"] = bool(t["tombstone_row_group_ids"])
        t["has_delete_bitmap"] = t["deleted_rows"] > 0
    return recon


def _capture_segments(container: str, password: str, db_name: str) -> dict[str, Any]:
    """Query segment + row-group + dictionary metadata; return a structured dict."""
    print(f"  querying sys.column_store_segments for [{db_name}] …", file=sys.stderr)
    seg_raw = _run_sql(container, password, _SEGMENTS_SQL.format(db=db_name))
    print(f"  querying sys.column_store_row_groups for [{db_name}] …", file=sys.stderr)
    rg_raw = _run_sql(container, password, _ROW_GROUPS_SQL.format(db=db_name))
    print(f"  querying sys.column_store_dictionaries for [{db_name}] …", file=sys.stderr)
    dict_raw = _run_sql(container, password, _DICTIONARIES_SQL.format(db=db_name))

    segments = _parse_rows(seg_raw, _SEG_FIELDS)
    row_groups = _parse_rows(rg_raw, _RG_FIELDS)
    dictionaries = _parse_rows(dict_raw, _DICT_FIELDS)

    # Group segments by table → partition → segment_id → list[col_entry]
    by_table: dict[str, Any] = {}
    for seg in segments:
        tbl = seg["table_name"]
        part = seg["partition_number"]
        sid = seg["segment_id"]
        by_table.setdefault(tbl, {}).setdefault(
            f"partition_{part}", {}
        ).setdefault(f"segment_{sid}", []).append({
            k: seg[k]
            for k in ("column_name", "column_id", "segment_version",
                      "encoding_type", "row_count", "has_nulls", "null_value",
                      "min_data_id", "max_data_id", "on_disk_size",
                      "base_id", "magnitude")
        })

    # Index ALL row groups by table (every state, not just COMPRESSED) so the
    # sidecar captures the OPEN/CLOSED/COMPRESSED/TOMBSTONE lifecycle.
    by_rg: dict[str, list[dict[str, Any]]] = {}
    for rg in row_groups:
        by_rg.setdefault(rg["table_name"], []).append({
            k: rg[k]
            for k in ("partition_number", "row_group_id", "state", "state_description",
                      "total_rows", "deleted_rows", "size_in_bytes")
        })

    # Dictionaries by table → column, tagged primary (dictionary_id 0) vs secondary.
    by_dict: dict[str, list[dict[str, Any]]] = {}
    for d in dictionaries:
        entry = {
            k: d[k]
            for k in ("column_name", "column_id", "dictionary_id", "version",
                      "type", "last_id", "entry_count", "on_disk_size")
        }
        entry["dict_scope"] = "primary" if d.get("dictionary_id") == 0 else "secondary"
        by_dict.setdefault(d["table_name"], []).append(entry)

    return {
        "segments": by_table,
        "row_groups": by_rg,
        "dictionaries": by_dict,
        "reconciliation": _reconcile_row_groups(row_groups),
        "raw_segment_count": len(segments),
        "raw_row_group_count": len(row_groups),
        "raw_dictionary_count": len(dictionaries),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _db_name_from_bak(bak_path: Path) -> str:
    """Derive a database name from the .bak stem (same convention as register_bak)."""
    stem = bak_path.stem  # e.g. "archive_columnstore_types_full"
    # Mirror register_bak.py: prefix with "RegisterBak_"
    return "RegisterBak_" + stem


def _drop_db(container: str, password: str, db_name: str) -> None:
    sql = (
        f"IF DB_ID(N'{db_name}') IS NOT NULL BEGIN "
        f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
        f"DROP DATABASE [{db_name}]; END;"
    )
    _run_sql(container, password, sql)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Capture sys.column_store_segments verifier sidecars"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing .segments.json files",
    )
    parser.add_argument(
        "--bak", action="append", default=[], metavar="PATH",
        help="capture this .bak (repeatable; absolute or relative to FIXTURE_DIR)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="capture every *.bak in FIXTURE_DIR (non-columnstore fixtures are skipped)",
    )
    parser.add_argument(
        "--keep", action="store_true",
        help="keep databases this run restores (default: drop them after capture)",
    )
    parser.add_argument(
        "--fresh", action="store_true",
        help="drop and re-restore even if the database already exists (fixes a "
             "broken DB left RESTORING by a prior failed run)",
    )
    args = parser.parse_args(argv)

    user, password, container = fixture_credentials()
    print(
        f"==> verifier sidecar capture: container={container}",
        file=sys.stderr,
    )

    # Target selection: explicit --bak / --all override the curated default list.
    if args.all:
        targets = [p.name for p in sorted(FIXTURE_DIR.glob("*.bak"))]
    elif args.bak:
        targets = list(args.bak)
    else:
        targets = list(_TARGET_BAKS)

    errors: list[str] = []
    for bak_name in targets:
        cand = Path(bak_name)
        bak_path = cand if cand.is_absolute() else (FIXTURE_DIR / bak_name)
        out_path = Path(str(bak_path) + ".segments.json")

        if not bak_path.exists():
            print(
                f"  skip (bak not found): {bak_path.name}",
                file=sys.stderr,
            )
            continue

        if skip_if_exists(out_path, force=args.force):
            continue

        db_name = _db_name_from_bak(bak_path)
        print(f"\n==> {bak_path.name}", file=sys.stderr)

        restored_here = False
        try:
            # --fresh: drop any pre-existing (possibly broken/RESTORING) DB first.
            if args.fresh and _db_exists(container, password, db_name):
                print(f"  --fresh: dropping existing [{db_name}] before restore", file=sys.stderr)
                _drop_db(container, password, db_name)
            # Restore the database if it isn't already present.
            if not _db_exists(container, password, db_name):
                _restore_bak(container, password, bak_path, db_name)
                restored_here = True
            else:
                print(f"  [{db_name}] already restored — skipping restore", file=sys.stderr)

            # Capture metadata.
            sidecar = _capture_segments(container, password, db_name)

            # A fixture with no columnstore segments is not a matrix target — don't
            # leave an empty/misleading sidecar (matters most under --all).
            if sidecar["raw_segment_count"] == 0:
                print(
                    f"  skip (no columnstore segments): {bak_path.name}",
                    file=sys.stderr,
                )
                continue

            sidecar["bak"] = bak_path.name
            sidecar["database"] = db_name
            sidecar["fixture_dir"] = str(FIXTURE_DIR)

            out_path.write_text(json.dumps(sidecar, indent=2))
            print(
                f"  wrote {out_path.name} "
                f"({sidecar['raw_segment_count']} segments)",
                file=sys.stderr,
            )

        except Exception as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
            errors.append(bak_name)
        finally:
            # Best-effort: remove any leftover /tmp .bak copy (covers the path where
            # the restore raised before _restore_bak's own cleanup ran).
            _run(["podman", "exec", container, "rm", "-f", f"/tmp/{bak_path.name}"])
            # Drop only databases this run restored (leave pre-existing ones), so a
            # bulk --all run doesn't accumulate hundreds of restored databases.
            if restored_here and not args.keep:
                print(f"  dropping [{db_name}] …", file=sys.stderr)
                try:
                    _drop_db(container, password, db_name)
                except Exception as exc:  # cleanup must not mask a capture error
                    print(f"  WARN: drop [{db_name}] failed: {exc}", file=sys.stderr)

    if errors:
        print(f"\nFailed: {', '.join(errors)}", file=sys.stderr)
        return 1

    print("\ndone.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
