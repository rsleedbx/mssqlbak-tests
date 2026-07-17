#!/usr/bin/env python3
"""Register a .bak fixture by restoring it to the forgedb SQL Server and collecting ground-truth statistics.

Usage
-----
Via fixture_run (recommended — credentials loaded automatically)::

    python -m tools.fixture_run register-bak tests/fixtures/tabletypecoverage_full.bak
    python -m tools.fixture_run register-bak tests/fixtures/tabletypecoverage_full.bak --version 2019

Or directly (env vars must be set)::

    FIXTURE_DBA_PASSWORD=... FIXTURE_CONTAINER=... python -m tools.register_bak <bak>

Output
------
``<bak>.stats.json`` written alongside the .bak file (and into ``tests/fixtures/``).
The file contains per-table row counts and per-column null counts — the minimum
ground truth needed to catch extraction bugs (skipped rows, mishandled NULLs).

Comparison
----------
``mssqlbak.tests.test_stats`` loads ``.stats.json`` files and compares the
mssqlbak extraction against each table's expected row_count and null counts.

Run ``python -m tools.fixture_run register-bak --help`` for options.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.cell_canon import clr_text_method  # noqa: E402
from tools.fixture_run import bootstrap_fixture_env  # noqa: E402
from tools.fixture_utils import discover_sqlcmd_path  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
MSSQL_IMAGE_MATCH = "mssql/server"

_UNREGISTERABLE_BAKS = frozenset({
    "corrupt_metadata_confidence_full.bak",
    "tde_full.bak",
})

# Platform/container notes for fixtures that require a specific SQL Server 2025
# image or host configuration:
#
# SQL Server 2025 + In-Memory OLTP (XTP/Hekaton) on macOS
#   Restoring any memory-optimized fixture into the older
#   mcr.microsoft.com/mssql/server:2025-CU5-ubuntu-22.04 image under Rosetta
#   (x86-64 emulation on Apple Silicon, lima + podman) causes the container
#   process to exit — the XTP engine does not survive the emulation layer.
#   The fix is to use the CU7 Ubuntu 24.04 image, which supports XTP on macOS:
#       image:     mcr.microsoft.com/mssql/server:2025-CU7-ubuntu-24.04
#       image_tag: "2025-CU7-ubuntu-24.04"
#   Affected fixtures (all memory-optimized / XTP):
#     - fixtures_2025/xtp_simple_full.bak
#     - fixtures_2025/xtp_probe_full.bak
#     - fixtures_2025/xtp_rich_full.bak
#     - fixtures_2025/xtp_checkpoint_straddle_full.bak
#     - fixtures_realworld/AdventureWorks2016_EXT.bak
#   Symptoms: the copy/restore step appears to start, but the container exits
#   before RESTORE DATABASE completes, leaving only a connection failure on the
#   next step with no SQL-level error message.


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    """Return the hex SHA-256 digest of *path* (streamed in 1 MiB chunks)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while data := f.read(chunk):
            h.update(data)
    return h.hexdigest()

def _discover_sqlcmd(container: str) -> str:
    """Return the sqlcmd binary path inside *container*.

    Delegates to ``tools.fixture_utils.discover_sqlcmd_path`` which uses a
    two-stage probe: container PATH first, then hardcoded candidate list.  It
    also correctly distinguishes a stopped container from a missing binary and
    raises a clear "container is not running" error in that case.
    """
    return discover_sqlcmd_path(container, "sqlcmd")


# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], *, check: bool = False, **kw: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check, **kw)


def _sqlcmd_base(container: str, password: str) -> list[str]:
    return [
        "podman", "exec", "-i", container,
        _discover_sqlcmd(container), "-S", "localhost", "-U", "sa", "-P", password,
        "-C",   # trust self-signed cert
        "-b",   # exit non-zero on SQL error
        "-W",   # remove trailing spaces
    ]


def _run_sql(container: str, password: str, sql: str) -> str:
    """Run a SQL batch inside the container; return stdout."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sql", prefix="register_bak_", delete=False
    ) as f:
        f.write(sql)
        local_sql = f.name
    try:
        # Copy the SQL file into the container then run it.
        container_sql = f"/tmp/register_{os.path.basename(local_sql)}"
        cp = _run(["podman", "cp", local_sql, f"{container}:{container_sql}"])
        if cp.returncode:
            raise RuntimeError(f"podman cp failed:\n{cp.stderr}")
        cmd = _sqlcmd_base(container, password) + ["-i", container_sql]
        result = _run(cmd)
        # Cleanup inside container (best effort).
        _run(["podman", "exec", container, "rm", "-f", container_sql])
        if result.returncode:
            raise RuntimeError(f"sqlcmd failed:\n{result.stderr or result.stdout}")
        return result.stdout
    finally:
        os.unlink(local_sql)


def _run_sql_query(container: str, password: str, sql: str, *, sep: str = "") -> str:
    """Run a SQL query batch; return stdout (no -b, tolerates informational messages).

    Pass sep="|" to use a pipe column separator — required when parsing tabular
    output whose columns may contain spaces (e.g. RESTORE FILELISTONLY / HEADERONLY).
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sql", prefix="register_bak_q_", delete=False
    ) as f:
        f.write(sql)
        local_sql = f.name
    try:
        container_sql = f"/tmp/register_q_{os.path.basename(local_sql)}"
        _run(["podman", "cp", local_sql, f"{container}:{container_sql}"])
        cmd = [
            "podman", "exec", "-i", container,
            _discover_sqlcmd(container), "-S", "localhost", "-U", "sa", "-P", password,
            "-C", "-W", "-h", "-1",   # no column headers
        ]
        if sep:
            cmd += ["-s", sep]
        cmd += ["-i", container_sql]
        result = _run(cmd)
        _run(["podman", "exec", container, "rm", "-f", container_sql])
        return result.stdout
    finally:
        os.unlink(local_sql)


# ---------------------------------------------------------------------------
# SQL Server internal database version → minimum SQL Server release year.
# DatabaseVersion comes from RESTORE HEADERONLY column 11 (1-indexed).
#
# These are lower-bound thresholds (each entry covers from its value up to
# the next threshold minus 1).  SQL Server CUs can increment the version
# within a release (e.g. SS2022 RTM shipped 957, later CUs use 958), so
# a range lookup is more robust than an exact dict.
# ---------------------------------------------------------------------------

_SS_YEAR_BREAKPOINTS: list[tuple[int, str]] = sorted(
    [
        (998, "2025"),
        (952, "2022"),   # SS2022 RTM = 957; later CUs may use 958
        (895, "2019"),   # SS2019 RTM = 904
        (845, "2016"),   # SS2016 RTM = 852
        (775, "2014"),   # SS2014 RTM = 782
        (700, "2012"),   # SS2012 RTM = 706
    ],
    reverse=True,  # high-to-low for first-match lookup
)


def _ss_year_for_db_version(version: int) -> str:
    """Return the SQL Server release year for a given internal DatabaseVersion."""
    for threshold, year in _SS_YEAR_BREAKPOINTS:
        if version >= threshold:
            return year
    return f"pre-2012 ({version})"


# ---------------------------------------------------------------------------
# BAK restoration helpers
# ---------------------------------------------------------------------------

def _bak_header_info(
    container: str, password: str, container_bak: str
) -> tuple[bool, int]:
    """Run RESTORE HEADERONLY and return ``(is_differential, db_version)``.

    HEADERONLY column layout (1-indexed, pipe-separated):
      col  3 – BackupType  (5 = Database Differential)
      col 11 – DatabaseVersion (e.g. 958 for SQL Server 2022, 998 for 2025)

    Both values are parsed in a single query.  HEADERONLY succeeds even when
    the backup's DatabaseVersion is higher than the server supports; only
    RESTORE DATABASE rejects mismatched versions.
    """
    sql = f"RESTORE HEADERONLY FROM DISK = N'{container_bak}';"
    out = _run_sql_query(container, password, sql, sep="|")
    is_diff = False
    db_version = 0
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) < 11:
            continue
        backup_type = parts[2].strip()
        if backup_type == "5":
            is_diff = True
        try:
            db_version = int(parts[10].strip())
        except ValueError:
            pass
        # Stop after the first data row (one row per backup set; we only
        # need the first set's values).
        if backup_type or db_version:
            break
    return is_diff, db_version


# RESTORE HEADERONLY column indices (0-indexed, pipe-separated output).
# Matches SQL Server documentation and empirical verification against SS2017–2025.
_HDR_COL_BACKUP_NAME = 0
_HDR_COL_BACKUP_TYPE = 2
_HDR_COL_DB_VERSION = 10
_HDR_COL_FIRST_LSN = 13
_HDR_COL_LAST_LSN = 14
_HDR_COL_CHECKPOINT_LSN = 15
_HDR_COL_DB_BACKUP_LSN = 16
_HDR_COL_BACKUP_START = 17
_HDR_COL_BACKUP_FINISH = 18

_BACKUP_TYPE_NAMES = {
    "1": "Database",
    "2": "TransactionLog",
    "4": "File",
    "5": "Differential",
    "6": "FileDifferential",
    "7": "Partial",
    "8": "PartialDifferential",
}


def _collect_headeronly_info(
    container: str, password: str, container_bak: str
) -> list[dict[str, Any]]:
    """Run ``RESTORE HEADERONLY`` and return one dict per backup set.

    Each dict contains:
    - ``BackupName``, ``BackupType`` (label), ``BackupTypeCode`` (int string)
    - ``FirstLSN``, ``LastLSN``, ``CheckpointLSN``, ``DatabaseBackupLSN``
      as ``numeric(25,0)`` decimal strings exactly as SQL Server reports them
    - ``BackupStartDate``, ``BackupFinishDate`` as ISO-8601 strings
    - ``DatabaseVersion`` as an integer

    Tolerates SQL Server versions that do not return all columns (e.g. pre-2012
    backups with fewer columns) — missing fields are omitted from the dict.
    """
    sql = f"RESTORE HEADERONLY FROM DISK = N'{container_bak}';"
    out = _run_sql_query(container, password, sql, sep="|")
    sets: list[dict[str, Any]] = []
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        backup_type_raw = parts[_HDR_COL_BACKUP_TYPE].strip() if len(parts) > _HDR_COL_BACKUP_TYPE else ""
        if not backup_type_raw or backup_type_raw.startswith("-"):
            continue
        try:
            int(backup_type_raw)
        except ValueError:
            continue  # header row or noise

        entry: dict[str, Any] = {
            "BackupName": parts[_HDR_COL_BACKUP_NAME].strip() if len(parts) > _HDR_COL_BACKUP_NAME else "",
            "BackupType": _BACKUP_TYPE_NAMES.get(backup_type_raw, backup_type_raw),
            "BackupTypeCode": backup_type_raw,
        }

        for key, col in [
            ("FirstLSN", _HDR_COL_FIRST_LSN),
            ("LastLSN", _HDR_COL_LAST_LSN),
            ("CheckpointLSN", _HDR_COL_CHECKPOINT_LSN),
            ("DatabaseBackupLSN", _HDR_COL_DB_BACKUP_LSN),
            ("BackupStartDate", _HDR_COL_BACKUP_START),
            ("BackupFinishDate", _HDR_COL_BACKUP_FINISH),
        ]:
            if col < len(parts):
                val = parts[col].strip()
                if val:
                    entry[key] = val

        if _HDR_COL_DB_VERSION < len(parts):
            db_ver = parts[_HDR_COL_DB_VERSION].strip()
            try:
                entry["DatabaseVersion"] = int(db_ver)
            except ValueError:
                pass

        sets.append(entry)
    return sets


def _collect_dbinfo_lsns(container: str, password: str, db_name: str) -> dict[str, Any] | None:
    """Run ``DBCC DBINFO`` on *db_name* and capture key LSN fields.

    Returns a dict with ``dbi_checkptLSN``, ``dbi_differentialBaseLSN``, and
    ``dbi_dbbackupLSN`` as decimal strings — the same format as HEADERONLY —
    or ``None`` on failure.  This is used as an independent cross-check against
    the HEADERONLY values.
    """
    sql = f"""
USE [master];
SET NOCOUNT ON;
DBCC DBINFO([{db_name}]) WITH TABLERESULTS, NO_INFOMSGS;
"""
    try:
        out = _run_sql_query(container, password, sql, sep="|")
    except Exception:
        return None

    result: dict[str, Any] = {}
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        field_name = parts[1].strip() if len(parts) > 1 else ""
        field_val = parts[2].strip() if len(parts) > 2 else ""
        if field_name in ("dbi_checkptLSN", "dbi_differentialBaseLSN", "dbi_dbbackupLSN"):
            result[field_name] = field_val

    return result if result else None


def _write_headeronly_sidecar(
    bak_path: Path,
    headeronly_sets: list[dict[str, Any]],
    dbinfo_lsns: dict[str, Any] | None,
    out_path: Path | None = None,
) -> Path:
    """Write ``<bak>.bak.headeronly.json`` and return the output path."""
    out = out_path or bak_path.with_suffix(bak_path.suffix + ".headeronly.json")
    payload: dict[str, Any] = {
        "bak": bak_path.name,
        "backup_sets": headeronly_sets,
    }
    if dbinfo_lsns:
        payload["dbinfo_lsns"] = dbinfo_lsns
    out.write_text(json.dumps(payload, indent=2))
    print(f"==> wrote {out}", file=sys.stderr)
    return out


def _server_db_version(container: str, password: str) -> int:
    """Return the SQL Server engine's native DatabaseVersion (e.g. 958 for 2022)."""
    sql = "SELECT DATABASEPROPERTYEX('master', 'Version');"
    out = _run_sql_query(container, password, sql)
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)
    return 0


def _find_full_for_diff(bak_path: Path) -> Path | None:
    """Find the full backup that a differential backup depends on.

    Naming convention:  *_diff*.bak → *_full.bak
    Examples:
      incrementalcoverage_diff_01.bak → incrementalcoverage_full.bak
      tabletypecoverage_diff.bak      → tabletypecoverage_full.bak
    """
    import re
    full_stem = re.sub(r"_diff(_.+)?$", "_full", bak_path.stem)
    full_path = bak_path.parent / f"{full_stem}.bak"
    return full_path if full_path.exists() else None


def _find_stripe_companions(bak_path: Path) -> list[Path] | None:
    """Return all stripe files for a striped backup (including bak_path), or None.

    Naming convention: prefix_1.bak, prefix_2.bak, … (single-digit stripe index).
    Two-digit suffixes like _01, _02 are differential sequences, not stripes.

    Raises RuntimeError when the filename matches the stripe pattern but companion
    files are missing — restoring a single stripe always fails with Msg 3132.
    """
    import re
    m = re.match(r"^(.+)_(\d)$", bak_path.stem)  # single digit only
    if not m:
        return None
    prefix = m.group(1)
    siblings = sorted(bak_path.parent.glob(f"{prefix}_?.bak"))  # single-digit glob
    if len(siblings) <= 1:
        raise RuntimeError(
            f"{bak_path.name} matches the striped-backup naming convention "
            f"(prefix_N.bak) but no companion stripe files were found in "
            f"{bak_path.parent} — all stripes must be present to restore."
        )
    return siblings


def _parse_logical_names(filelist_out: str) -> list[tuple[str, str]]:
    """Parse pipe-separated RESTORE FILELISTONLY output into (LogicalName, Type) pairs.

    FILELISTONLY columns (1-indexed):
      1. LogicalName  2. PhysicalName  3. Type ('D'=data, 'L'=log, 'S'=filestream/
         memory-optimised container, 'F'=full-text)  4. …

    The PhysicalName column (2) can contain spaces (Windows paths), so we use
    the pipe separator from _run_sql_query(sep="|") to avoid ambiguity.

    Types 'S' (filestream / memory-optimised container) and 'F' (full-text
    catalog) must also be included in the MOVE list; without an explicit MOVE
    SQL Server falls back to the original Windows path which is invalid on Linux.
    """
    logical_names: list[tuple[str, str]] = []
    for line in filelist_out.splitlines():
        parts = line.split("|")
        if len(parts) < 3:
            continue
        name = parts[0].strip()
        ftype = parts[2].strip()  # column 3: Type
        if ftype in ("D", "L", "S", "F") and name and not name.startswith("-"):
            logical_names.append((name, ftype))
    return logical_names


def _move_clauses(logical_names: list[tuple[str, str]], db_name: str) -> str:
    """Build MOVE … TO … clauses so all files land under the mssql data dir.

    Type mapping:
    - 'D' → .mdf / .ndf  (regular data files)
    - 'L' → .ldf          (log files)
    - 'S' → bare directory path (filestream / memory-optimised container)
    - 'F' → .fts directory (full-text catalog)
    """
    clauses: list[str] = []
    seen_data = seen_log = seen_stream = seen_fts = 0
    for lname, ftype in logical_names:
        if ftype == "D":
            ext = "_data.mdf" if seen_data == 0 else f"_data{seen_data}.ndf"
            seen_data += 1
            target = f"/var/opt/mssql/data/{db_name}{ext}"
        elif ftype == "L":
            ext = "_log.ldf" if seen_log == 0 else f"_log{seen_log}.ldf"
            seen_log += 1
            target = f"/var/opt/mssql/data/{db_name}{ext}"
        elif ftype == "S":
            # Filestream / memory-optimised container — target is a directory.
            sfx = "" if seen_stream == 0 else str(seen_stream)
            seen_stream += 1
            target = f"/var/opt/mssql/data/{db_name}_mem{sfx}"
        else:  # 'F' — full-text catalog directory
            sfx = "" if seen_fts == 0 else str(seen_fts)
            seen_fts += 1
            target = f"/var/opt/mssql/data/{db_name}_fts{sfx}"
        clauses.append(f"MOVE N'{lname}' TO N'{target}'")
    return ",\n    ".join(clauses)


def _drop_if_exists_sql(db_name: str) -> str:
    return (
        f"IF DB_ID(N'{db_name}') IS NOT NULL BEGIN\n"
        f"    ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;\n"
        f"    DROP DATABASE [{db_name}];\n"
        f"END;"
    )


def _copy_bak(container: str, bak_path: Path) -> str:
    """Copy bak_path into the container and return the container path."""
    container_bak = f"/tmp/{bak_path.name}"
    cp = _run(["podman", "cp", str(bak_path), f"{container}:{container_bak}"])
    if cp.returncode:
        raise RuntimeError(f"podman cp failed:\n{cp.stderr}")
    return container_bak


# ---------------------------------------------------------------------------
# BAK restoration (full / differential / striped)
# ---------------------------------------------------------------------------

def _restore_bak(container: str, password: str, bak_path: Path, db_name: str) -> None:
    """Copy bak_path into the container and restore it as db_name.

    Handles three cases automatically:
    - Full backup: straightforward RESTORE DATABASE … WITH RECOVERY.
    - Differential backup: first restore the matching full with NORECOVERY,
      then apply the diff with RECOVERY.
    - Striped backup: gather all stripe files and provide them as multiple
      DISK = N'…' clauses in a single RESTORE command.
    """
    print(f"==> copying {bak_path.name} into container …", file=sys.stderr)
    # Track every container-side /tmp copy so we can delete them afterwards.
    # Without this, a bulk backfill leaks .bak copies into the container /tmp
    # and eventually fills the disk (RESTORE FILELISTONLY → "no files").
    copied: list[str] = []
    container_bak = _copy_bak(container, bak_path)
    copied.append(container_bak)
    try:
        _restore_bak_body(
            container, password, bak_path, db_name, container_bak, copied,
        )
    finally:
        if copied:
            _run(["podman", "exec", container, "rm", "-f", *copied])


def _restore_bak_body(
    container: str,
    password: str,
    bak_path: Path,
    db_name: str,
    container_bak: str,
    copied: list[str],
) -> None:
    """Inner restore logic; container /tmp copies tracked in ``copied``."""
    # --- Detect backup type and check engine version compatibility ---
    diff_full_path: Path | None = None
    stripe_paths: list[Path] | None = _find_stripe_companions(bak_path)

    # HEADERONLY works even when DatabaseVersion > server's native version,
    # so we can read both backup type and db version before attempting the restore.
    is_diff, bak_db_ver = _bak_header_info(container, password, container_bak)
    if bak_db_ver:
        srv_db_ver = _server_db_version(container, password)
        if srv_db_ver and bak_db_ver > srv_db_ver:
            needed = _ss_year_for_db_version(bak_db_ver)
            have   = _ss_year_for_db_version(srv_db_ver)
            raise RuntimeError(
                f"backup requires SQL Server {needed} (DatabaseVersion={bak_db_ver}); "
                f"container supports up to version {srv_db_ver} (SQL Server {have}) — "
                f"provision a SQL Server {needed} container to register this fixture"
            )

    if stripe_paths is None:
        if is_diff:
            diff_full_path = _find_full_for_diff(bak_path)
            if diff_full_path is None:
                raise RuntimeError(
                    f"{bak_path.name} is a differential backup but no matching full "
                    f"backup was found (expected *_full.bak alongside it)."
                )

    # --- Gather all container paths and logical file names ---
    if stripe_paths is not None:
        # Copy companion stripes (skip the one already copied).
        for sp in stripe_paths:
            if sp != bak_path:
                print(f"==> copying stripe {sp.name} …", file=sys.stderr)
                copied.append(_copy_bak(container, sp))
        all_disks = [f"/tmp/{sp.name}" for sp in stripe_paths]
        disk_clause = ",\n    ".join(f"DISK = N'{d}'" for d in all_disks)
        filelist_sql = f"USE [master]; RESTORE FILELISTONLY FROM {disk_clause};"
    else:
        disk_clause = f"DISK = N'{container_bak}'"
        filelist_sql = f"USE [master]; RESTORE FILELISTONLY FROM {disk_clause};"

    filelist_out = _run_sql_query(container, password, filelist_sql, sep="|")
    logical_names = _parse_logical_names(filelist_out)
    moves = _move_clauses(logical_names, db_name)
    with_moves = (",\n    " + moves) if moves else ""

    # --- Build and run the restore SQL ---
    drop_sql = _drop_if_exists_sql(db_name)

    if diff_full_path is not None:
        # Two-step: full with NORECOVERY, then diff with RECOVERY.
        print(f"==> copying full backup {diff_full_path.name} …", file=sys.stderr)
        full_container_bak = _copy_bak(container, diff_full_path)
        copied.append(full_container_bak)

        # Logical names for the full backup (may differ from the diff).
        full_filelist_out = _run_sql_query(
            container, password,
            f"USE [master]; RESTORE FILELISTONLY FROM DISK = N'{full_container_bak}';",
            sep="|",
        )
        full_logical = _parse_logical_names(full_filelist_out)
        full_moves = _move_clauses(full_logical, db_name)
        full_with = "WITH REPLACE, NORECOVERY" + (",\n    " + full_moves if full_moves else "")

        restore_sql = f"""
USE [master];
GO
{drop_sql}
GO
RESTORE DATABASE [{db_name}]
FROM DISK = N'{full_container_bak}'
{full_with};
GO
RESTORE DATABASE [{db_name}]
FROM DISK = N'{container_bak}'
WITH RECOVERY{with_moves};
GO
"""
        print("==> restoring (full+diff) …", file=sys.stderr)
    else:
        restore_sql = f"""
USE [master];
GO
{drop_sql}
GO
RESTORE DATABASE [{db_name}]
FROM {disk_clause}
WITH REPLACE, RECOVERY{with_moves};
GO
"""
        print("==> restoring database …", file=sys.stderr)

    _run_sql(container, password, restore_sql)
    print(f"==> restored as [{db_name}]", file=sys.stderr)


# ---------------------------------------------------------------------------
# Statistics collection
# ---------------------------------------------------------------------------

# Sentinel written into the stats JSON to represent a SQL NULL min/max.
_NULL_SENTINEL = "__NULL__"

def _minmax_col_exprs(col_name: str, sql_type: str) -> tuple[str, str]:
    """Return (min_expr, max_expr) SQL fragments that evaluate to an NVARCHAR string.

    Types that support native MIN/MAX compute it in native type then cast;
    this preserves correct ordering (e.g. numeric, temporal).  Types that
    don't support MIN/MAX directly cast to a comparable intermediate first.

    Cast width policy:
    - NVARCHAR(4000) for string types (varchar/nvarchar/char/nchar/text/ntext/xml)
      so that columns wider than 200 characters do not get truncated in the
      ground-truth JSON (Gap-2 fix).
    - NVARCHAR(200) for all other types whose string representations are short
      (numbers, dates, binary hex, etc.).

    Known SQL Server restrictions handled here:
    - ``bit``: MIN/MAX not allowed on bit; cast to TINYINT first.
    - ``image``: explicit conversion to NVARCHAR not allowed; go via VARBINARY.
    - ``timestamp``/``rowversion``: same restriction; cast to BINARY(8) first.
    - ``text``/``ntext``: use CONVERT to NVARCHAR(MAX) (implicit cast disallowed).
    - ``xml``: cast via NVARCHAR(MAX) to avoid XML-to-NVARCHAR(n) restriction.
    - ``json``/``vector``: MIN/MAX unsupported; CAST to NVARCHAR(MAX) is valid.
      Both are in _MINMAX_SKIP_TYPES so the value is captured but never compared.
    - CLR spatial/hierarchyid: call .STAsText() / .ToString() then take MIN/MAX.
    - ``binary``/``varbinary``: convert with style 1 (hex) after native MIN/MAX.
    - Alias/user types: the caller uses a CASE expression that resolves genuine
      alias types (is_user_defined=1, is_assembly_type=0) via TYPE_NAME(system_type_id)
      so they dispatch to their base type branch (e.g. alias over bit → 'bit').
      Native and CLR types keep their declared name (vector, json, geometry …).
      The native VECTOR type specifically has system_type_id=165 (varbinary) /
      user_type_id=255; without the CASE it would resolve to 'varbinary' and
      the MIN() call would fail ("Argument data type vector is invalid").
    """
    q = f"[{col_name}]"
    typ = sql_type.lower()
    null_s = f"N'{_NULL_SENTINEL}'"

    clr_method = clr_text_method(typ)
    if clr_method is not None:
        # Binary collation so MIN/MAX ordering matches Python's code-point comparison.
        # NVARCHAR(4000) avoids the 200-char truncation for longer WKT / path strings.
        raw = f"CAST({q}.{clr_method} AS NVARCHAR(4000)) COLLATE Latin1_General_100_BIN2"
        return f"ISNULL(MIN({raw}), {null_s})", f"ISNULL(MAX({raw}), {null_s})"

    if typ == "bit":
        # MIN/MAX not supported on bit — promote to TINYINT.
        raw_min = f"CAST(MIN(CAST({q} AS TINYINT)) AS NVARCHAR(200))"
        raw_max = f"CAST(MAX(CAST({q} AS TINYINT)) AS NVARCHAR(200))"
        return f"ISNULL({raw_min}, {null_s})", f"ISNULL({raw_max}, {null_s})"

    if typ in ("char", "nchar"):
        # Fixed-width: RTRIM removes trailing space padding, then binary collation
        # (Latin1_General_100_BIN2) orders by Unicode code point, matching Python's
        # str comparison.  CI_AS collation would give case-insensitive ordering
        # that disagrees with Python (MIN('a','Z')='a' in CI_AS, 'Z' in Python).
        # NVARCHAR(4000) avoids truncation for char(n) where n > 200 (Gap-2 fix).
        raw_min = f"CAST(MIN(RTRIM({q}) COLLATE Latin1_General_100_BIN2) AS NVARCHAR(4000))"
        raw_max = f"CAST(MAX(RTRIM({q}) COLLATE Latin1_General_100_BIN2) AS NVARCHAR(4000))"
        return f"ISNULL({raw_min}, {null_s})", f"ISNULL({raw_max}, {null_s})"

    if typ in ("varchar", "nvarchar"):
        # Variable-width: apply binary collation so MIN/MAX uses code-point ordering
        # rather than the database's CI_AS default.  NVARCHAR(4000) matches the limit
        # used for text/ntext/xml — avoids truncating varchar(MAX) columns whose
        # min/max row holds a value longer than 200 characters (e.g. PostHistory.Text).
        raw_min = f"CAST(MIN({q} COLLATE Latin1_General_100_BIN2) AS NVARCHAR(4000))"
        raw_max = f"CAST(MAX({q} COLLATE Latin1_General_100_BIN2) AS NVARCHAR(4000))"
        return f"ISNULL({raw_min}, {null_s})", f"ISNULL({raw_max}, {null_s})"

    if typ in ("text", "ntext"):
        # text/ntext do not support MIN/MAX directly; convert to NVARCHAR(MAX) first.
        # Binary collation applied after conversion for code-point ordering.
        # NVARCHAR(4000) avoids the 200-char truncation that plagued the old GT while
        # keeping the result within a column width that sqlcmd can return reliably.
        raw = f"CONVERT(NVARCHAR(MAX), {q}) COLLATE Latin1_General_100_BIN2"
        return f"ISNULL(CAST(MIN({raw}) AS NVARCHAR(4000)), {null_s})", f"ISNULL(CAST(MAX({raw}) AS NVARCHAR(4000)), {null_s})"

    if typ in ("smalldatetime", "datetime"):
        # Style 120 = ODBC canonical: 'YYYY-MM-DD HH:MM:SS' — ISO-parseable by Python.
        # The default CAST gives 'Jan  1 1900 12:00AM' which has no strptime equivalent.
        raw_min = f"CONVERT(NVARCHAR(23), MIN({q}), 120)"
        raw_max = f"CONVERT(NVARCHAR(23), MAX({q}), 120)"
        return f"ISNULL({raw_min}, {null_s})", f"ISNULL({raw_max}, {null_s})"

    if typ == "xml":
        # CAST xml→NVARCHAR(MAX) first (direct cast to NVARCHAR(n) is not allowed),
        # then truncate to NVARCHAR(4000) with binary collation for consistent ordering.
        raw = f"CAST(CAST({q} AS NVARCHAR(MAX)) AS NVARCHAR(4000)) COLLATE Latin1_General_100_BIN2"
        return f"ISNULL(MIN({raw}), {null_s})", f"ISNULL(MAX({raw}), {null_s})"

    if typ in ("json", "vector"):
        # json/vector: MIN/MAX not supported by SQL Server; CAST to NVARCHAR(MAX) is.
        # Both types surface as JSON-array / document text over the wire.
        # This is a whole-column min/max of the stored document value — deliberately
        # NOT a per-property aggregate (MIN(CAST(JSON_VALUE(col,'$.x') AS ...)))
        # which would require a fixed schema we don't have for arbitrary GT columns.
        # The document-string ordering is not semantically meaningful and the native
        # binary form may re-serialize differently than the parser output, so both
        # types are listed in _MINMAX_SKIP_TYPES and the value is never compared.
        # The CAST exists only to keep the UNION-ALL query syntactically valid.
        raw = f"CAST(CAST({q} AS NVARCHAR(MAX)) AS NVARCHAR(4000)) COLLATE Latin1_General_100_BIN2"
        return f"ISNULL(MIN({raw}), {null_s})", f"ISNULL(MAX({raw}), {null_s})"

    if typ == "image":
        # image → NVARCHAR is not allowed; go image→VARBINARY(250)→hex NVARCHAR.
        # NVARCHAR(MAX) with style-1 binary→hex returns '' for empty input on some
        # SQL Server versions; fixed-size NVARCHAR(n) correctly returns '0x'.
        # 250 bytes → 500 hex chars + '0x' = 502 chars fits in NVARCHAR(502).
        raw = f"CONVERT(NVARCHAR(502), CONVERT(VARBINARY(250), {q}), 1)"
        return f"ISNULL(MIN({raw}), {null_s})", f"ISNULL(MAX({raw}), {null_s})"

    if typ == "timestamp":
        # timestamp/rowversion → NVARCHAR is not allowed; cast to BINARY(8) first.
        raw = f"CONVERT(NVARCHAR(20), CAST({q} AS BINARY(8)), 1)"
        return f"ISNULL(MIN({raw}), {null_s})", f"ISNULL(MAX({raw}), {null_s})"

    if typ in ("binary", "varbinary"):
        # Native MIN/MAX first (preserves byte ordering), then hex-encode the result.
        # NVARCHAR(500) handles up to 249-byte values without truncation.
        raw_min = f"CONVERT(NVARCHAR(500), MIN({q}), 1)"
        raw_max = f"CONVERT(NVARCHAR(500), MAX({q}), 1)"
        return f"ISNULL({raw_min}, {null_s})", f"ISNULL({raw_max}, {null_s})"

    if typ == "money":
        # CAST(money AS NVARCHAR) shows only 2 decimal places; go via DECIMAL(19,4)
        # to preserve all 4 stored decimal places in the ground-truth string.
        raw_min = f"CAST(CAST(MIN({q}) AS DECIMAL(19,4)) AS NVARCHAR(200))"
        raw_max = f"CAST(CAST(MAX({q}) AS DECIMAL(19,4)) AS NVARCHAR(200))"
        return f"ISNULL({raw_min}, {null_s})", f"ISNULL({raw_max}, {null_s})"

    if typ == "smallmoney":
        raw_min = f"CAST(CAST(MIN({q}) AS DECIMAL(10,4)) AS NVARCHAR(200))"
        raw_max = f"CAST(CAST(MAX({q}) AS DECIMAL(10,4)) AS NVARCHAR(200))"
        return f"ISNULL({raw_min}, {null_s})", f"ISNULL({raw_max}, {null_s})"

    # All other types: native MIN/MAX then cast result to NVARCHAR(200).
    return (
        f"ISNULL(CAST(MIN({q}) AS NVARCHAR(200)), {null_s})",
        f"ISNULL(CAST(MAX({q}) AS NVARCHAR(200)), {null_s})",
    )


def _collect_stats(cur: Any) -> list[dict[str, Any]]:
    """Return per-table row counts, per-column null counts, and per-column min/max.

    Accepts an mssql_python cursor already positioned on the target database.
    Returns typed values directly — no sqlcmd display-width truncation.
    """
    # Step 1: enumerate user tables.
    # Driver returns typed rows; no sqlcmd noise filtering needed.
    # Spaces in schema/table names are handled correctly (unlike the old
    # sqlcmd path which excluded names with spaces to filter out noise lines).
    tables_sql = """\
SELECT s.name + '.' + t.name
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE t.is_ms_shipped = 0
ORDER BY s.name, t.name"""
    table_fqns = [row[0] for row in _query(cur, tables_sql) if row[0]]

    if not table_fqns:
        print("  (no user tables found)", file=sys.stderr)
        return []

    tables_result: list[dict[str, Any]] = []

    for fqn in table_fqns:
        schema_name, table_name = fqn.split(".", 1)
        quoted = f"[{schema_name}].[{table_name}]"
        print(f"  collecting stats for {quoted} …", file=sys.stderr)

        # Row count — driver returns the bigint directly as int.
        rc_rows = _query(cur, f"SELECT COUNT_BIG(*) FROM {quoted}")
        row_count = int(rc_rows[0][0]) if rc_rows else 0

        # Column names and effective type names for dispatch in _minmax_col_exprs.
        # The CASE expression resolves alias/user-defined types (is_user_defined=1,
        # is_assembly_type=0) to their underlying system type via TYPE_NAME(system_type_id)
        # — e.g. an alias "IsActive" over bit returns 'bit' so the bit branch is used.
        # Native and CLR types (is_user_defined=0, or is_assembly_type=1) keep t.name,
        # which is their real type name (vector, json, geometry, geography, hierarchyid …).
        # This is necessary because the native VECTOR type has system_type_id=165
        # (varbinary) but user_type_id=255; resolving via system_type_id would yield
        # 'varbinary', causing the varbinary MIN() branch to run and fail with
        # "Argument data type vector is invalid for argument 1 of min function."
        # c.graph_type IS NULL excludes graph-internal columns (graph_id_*, from_id_*,
        # to_id_* etc.) that appear in sys.columns on SQL Server 2017+ but cannot
        # be selected in a query (error 13908, "Cannot access internal graph column").
        # c.encryption_type IS NULL excludes Always Encrypted (AE) columns.  Without
        # the Column Encryption Key (CEK) the mssql-python driver cannot decrypt the
        # ciphertext, so MIN/MAX and even IS NULL raise "Encryption scheme mismatch …
        # expects it to be PLAINTEXT" (AEAD_AES_256_CBC_HMAC_SHA_256).  mssqlbak
        # itself returns None for all AE column values (G53 gap), so skipping them
        # in GT collection is consistent — null_count and min/max are left absent
        # and test_stats.py skips those columns automatically.
        sn_esc = schema_name.replace("'", "''")
        tn_esc = table_name.replace("'", "''")
        cols_sql = f"""\
SELECT c.name,
  CASE
    WHEN t.is_user_defined = 1 AND t.is_assembly_type = 0
      THEN TYPE_NAME(c.system_type_id)
    ELSE t.name
  END
FROM sys.columns c
JOIN sys.types t ON t.user_type_id = c.user_type_id
JOIN sys.tables tbl ON tbl.object_id = c.object_id
JOIN sys.schemas s ON s.schema_id = tbl.schema_id
WHERE s.name = N'{sn_esc}' AND tbl.name = N'{tn_esc}'
  AND c.is_computed = 0
  AND c.graph_type IS NULL
  AND c.encryption_type IS NULL
ORDER BY c.column_id"""
        columns: list[dict[str, Any]] = []
        col_names: list[str] = []
        for row in _query(cur, cols_sql):
            col_names.append(row[0])
            columns.append({"name": row[0], "sql_type": row[1]})

        # Null counts via one query per table (dynamic SQL → single round trip).
        # Driver returns ints positionally in the single result row.
        if col_names and row_count > 0:
            null_parts = ",\n    ".join(
                f"SUM(CASE WHEN [{c}] IS NULL THEN 1 ELSE 0 END) AS [{c}]"
                for c in col_names
            )
            null_rows = _query(cur, f"SELECT {null_parts} FROM {quoted}")
            null_vals = list(null_rows[0]) if null_rows else []
            for i, col in enumerate(columns):
                v = null_vals[i] if i < len(null_vals) else None
                col["null_count"] = int(v) if v is not None else None
        else:
            for col in columns:
                col["null_count"] = 0

        # Min/max via UNION ALL — one row per column: (col_name, min_val, max_val).
        # _NULL_SENTINEL replaces SQL NULL so we can distinguish "no rows" from NULL.
        # Keep _minmax_col_exprs SQL expressions unchanged; the driver returns the
        # NVARCHAR results as Python str without any display-width truncation.
        if col_names and row_count > 0:
            union_terms: list[str] = []
            for col in columns:
                min_e, max_e = _minmax_col_exprs(col["name"], col["sql_type"])
                name_lit = col["name"].replace("'", "''")
                union_terms.append(
                    f"SELECT N'{name_lit}', {min_e}, {max_e} FROM {quoted}"
                )
            minmax_sql = "\nUNION ALL\n".join(union_terms)
            minmax_map: dict[str, tuple[str | None, str | None]] = {}
            for row in _query(cur, minmax_sql):
                cname = row[0]
                if not cname:
                    continue
                raw_min = row[1]
                raw_max = row[2]
                minmax_map[cname] = (
                    None if raw_min == _NULL_SENTINEL else raw_min,
                    None if raw_max == _NULL_SENTINEL else raw_max,
                )
            for col in columns:
                pair = minmax_map.get(col["name"])
                col["min_val"] = pair[0] if pair else None
                col["max_val"] = pair[1] if pair else None
        else:
            for col in columns:
                col["min_val"] = None
                col["max_val"] = None

        tables_result.append({
            "schema": schema_name,
            "name": table_name,
            "row_count": row_count,
            "columns": columns,
        })

    return tables_result


def _sql_version(container: str, password: str) -> str:
    out = _run_sql_query(container, password, "SELECT @@VERSION;")
    for line in out.splitlines():
        line = line.strip()
        if line and not line.startswith("-") and not line.startswith("("):
            return line
    return "unknown"


# ---------------------------------------------------------------------------
# Drop helper
# ---------------------------------------------------------------------------

def _drop_db(container: str, password: str, db_name: str) -> None:
    sql = f"""
USE [master];
GO
IF DB_ID(N'{db_name}') IS NOT NULL BEGIN
    ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{db_name}];
END;
GO
"""
    _run_sql(container, password, sql)


# ---------------------------------------------------------------------------
# Metadata ground-truth collectors (use mssql_python cursor — no sqlcmd truncation)
# ---------------------------------------------------------------------------
#
# Each collector accepts an mssql_python cursor already positioned on the
# target database (caller runs ``cur.execute(f"USE [{db_name}]")``) and
# returns JSON-serialisable Python objects.
#
# sqlcmd is NOT used here: its default -y 256 silently truncates any
# variable-length column at 256 chars (root cause of the "c_varbin" stats GT
# bug).  The mssql_python driver returns typed Python values with no
# display-width limit.
#
# _parse_pipe / _SQLCMD_NOISE are kept below for _collect_stats (data GT),
# which still runs through sqlcmd.

_SQLCMD_NOISE = frozenset({"Changed database context to", "NULL"})


def _parse_pipe(out: str, n_cols: int) -> list[list[str]]:
    """Parse pipe-separated sqlcmd output into rows, skipping noise lines."""
    rows = []
    for line in out.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < n_cols:
            continue
        # Skip header separators (all dashes) and blank leading values
        if parts[0].startswith("-") or not any(parts):
            continue
        # Skip sqlcmd informational messages (e.g. "Changed database context to '...'")
        if any(parts[0].startswith(noise) for noise in _SQLCMD_NOISE):
            continue
        rows.append(parts)
    return rows


def _query(cur: Any, sql: str) -> list[Any]:
    """Execute *sql* on *cur* and return all rows."""
    cur.execute(sql)
    return cur.fetchall()


def _collect_constraints(cur: Any) -> list[dict[str, Any]]:
    """Collect user constraints: PK, UQ, FK, CHECK, DEFAULT (name-resolved)."""
    sql_pkuq = """\
SELECT
    s.name + '.' + t.name,
    kc.name,
    CASE kc.type WHEN 'PK' THEN 'primary key' WHEN 'UQ' THEN 'unique constraint' END,
    CASE WHEN kc.is_system_named=1 THEN '1' ELSE '0' END,
    COALESCE(STUFF((SELECT ',' + c.name
           FROM sys.index_columns ic
           JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id
           WHERE ic.object_id=kc.parent_object_id AND ic.index_id=kc.unique_index_id
           ORDER BY ic.index_column_id
           FOR XML PATH('')),1,1,''), ''),
    '', '', ''
FROM sys.key_constraints kc
JOIN sys.tables t ON t.object_id=kc.parent_object_id
JOIN sys.schemas s ON s.schema_id=t.schema_id
WHERE t.is_ms_shipped=0
ORDER BY s.name, t.name, kc.name"""

    sql_fk = """\
SELECT
    s.name + '.' + t.name,
    fk.name,
    'foreign key',
    CASE WHEN fk.is_system_named=1 THEN '1' ELSE '0' END,
    COALESCE(STUFF((SELECT ',' + c.name
           FROM sys.foreign_key_columns fkc
           JOIN sys.columns c ON c.object_id=fkc.parent_object_id AND c.column_id=fkc.parent_column_id
           WHERE fkc.constraint_object_id=fk.object_id
           ORDER BY fkc.constraint_column_id
           FOR XML PATH('')),1,1,''), ''),
    rs.name + '.' + rt.name,
    COALESCE(STUFF((SELECT ',' + rc.name
           FROM sys.foreign_key_columns fkc
           JOIN sys.columns rc ON rc.object_id=fkc.referenced_object_id AND rc.column_id=fkc.referenced_column_id
           WHERE fkc.constraint_object_id=fk.object_id
           ORDER BY fkc.constraint_column_id
           FOR XML PATH('')),1,1,''), ''),
    ''
FROM sys.foreign_keys fk
JOIN sys.tables t ON t.object_id=fk.parent_object_id
JOIN sys.schemas s ON s.schema_id=t.schema_id
JOIN sys.tables rt ON rt.object_id=fk.referenced_object_id
JOIN sys.schemas rs ON rs.schema_id=rt.schema_id
WHERE t.is_ms_shipped=0
ORDER BY s.name, t.name, fk.name"""

    sql_check = """\
SELECT
    s.name + '.' + t.name,
    cc.name,
    'check',
    CASE WHEN cc.is_system_named=1 THEN '1' ELSE '0' END,
    COALESCE(c.name, ''),
    '', '',
    CAST(cc.definition AS nvarchar(max))
FROM sys.check_constraints cc
JOIN sys.tables t ON t.object_id=cc.parent_object_id
JOIN sys.schemas s ON s.schema_id=t.schema_id
LEFT JOIN sys.columns c ON c.object_id=cc.parent_object_id AND c.column_id=cc.parent_column_id
WHERE t.is_ms_shipped=0
ORDER BY s.name, t.name, cc.name"""

    sql_default = """\
SELECT
    s.name + '.' + t.name,
    dc.name,
    'default',
    CASE WHEN dc.is_system_named=1 THEN '1' ELSE '0' END,
    COALESCE(c.name, ''),
    '', '',
    CAST(dc.definition AS nvarchar(max))
FROM sys.default_constraints dc
JOIN sys.tables t ON t.object_id=dc.parent_object_id
JOIN sys.schemas s ON s.schema_id=t.schema_id
LEFT JOIN sys.columns c ON c.object_id=dc.parent_object_id AND c.column_id=dc.parent_column_id
WHERE t.is_ms_shipped=0
ORDER BY s.name, t.name, dc.name"""

    all_rows = (
        _query(cur, sql_pkuq)
        + _query(cur, sql_fk)
        + _query(cur, sql_check)
        + _query(cur, sql_default)
    )
    result = []
    for row in all_rows:
        table = row[0]
        name = row[1]
        kind = row[2]
        sys_named = row[3] or ""
        cols_str = row[4] or ""
        ref_table = row[5] or ""
        ref_cols_str = row[6] or ""
        definition = row[7] or ""
        if not name:
            continue
        entry: dict[str, Any] = {
            "table": table,
            "name": name,
            "kind": kind,
            "is_system_named": sys_named == "1",
        }
        if cols_str:
            entry["columns"] = cols_str.split(",")
        if ref_table:
            entry["ref_table"] = ref_table
        if ref_cols_str:
            entry["ref_columns"] = ref_cols_str.split(",")
        if kind in ("check", "default"):
            col = cols_str  # single column name for check/default
            if col:
                entry["column"] = col
            entry["definition"] = definition
        result.append(entry)
    return result


def _collect_indexes(cur: Any) -> list[dict[str, Any]]:
    """Collect non-heap indexes (name-resolved key column lists)."""
    sql = """\
SELECT
    s.name + '.' + t.name,
    i.name,
    i.type_desc,
    CASE WHEN i.is_unique=1 THEN '1' ELSE '0' END,
    CASE WHEN i.is_primary_key=1 THEN '1' ELSE '0' END,
    COALESCE(STUFF((SELECT ',' + c.name
           FROM sys.index_columns ic
           JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id
           WHERE ic.object_id=i.object_id AND ic.index_id=i.index_id AND ic.is_included_column=0
           ORDER BY ic.index_column_id
           FOR XML PATH('')),1,1,''), '')
FROM sys.indexes i
JOIN sys.tables t ON t.object_id=i.object_id
JOIN sys.schemas s ON s.schema_id=t.schema_id
WHERE t.is_ms_shipped=0 AND i.type > 0
ORDER BY s.name, t.name, i.name"""
    result = []
    for row in _query(cur, sql):
        name = row[1]
        if not name:
            continue
        key_cols_str = row[5] or ""
        result.append({
            "table": row[0],
            "name": name,
            "type": row[2].lower(),
            "is_unique": (row[3] or "") == "1",
            "is_primary_key": (row[4] or "") == "1",
            "key_columns": key_cols_str.split(",") if key_cols_str else [],
        })
    return result


def _collect_extended_properties(cur: Any) -> list[dict[str, Any]]:
    """Collect extended properties (MS_Description, etc.) name-resolved."""
    sql = """\
SELECT
    'table' + CASE WHEN ep.minor_id=0 THEN '' ELSE '/column' END,
    s.name + '.' + t.name,
    CASE WHEN ep.minor_id=0 THEN '' ELSE c.name END,
    ep.name,
    CAST(ep.value AS nvarchar(max))
FROM sys.extended_properties ep
JOIN sys.tables t ON t.object_id=ep.major_id
JOIN sys.schemas s ON s.schema_id=t.schema_id
LEFT JOIN sys.columns c ON c.object_id=ep.major_id AND c.column_id=ep.minor_id
WHERE ep.class=1 AND t.is_ms_shipped=0
  AND CAST(ep.value AS sql_variant) IS NOT NULL

UNION ALL

SELECT
    'schema',
    sc.name,
    '',
    ep.name,
    CAST(ep.value AS nvarchar(max))
FROM sys.extended_properties ep
JOIN sys.schemas sc ON sc.schema_id=ep.major_id
WHERE ep.class=3

ORDER BY 1,2,3,4"""
    result = []
    for row in _query(cur, sql):
        level = row[0]
        obj = row[1]
        col = row[2] or ""
        name = row[3]
        value = row[4] or ""
        if not name:
            continue
        entry: dict[str, Any] = {
            "level": level,
            "object": obj,
            "name": name,
            "value": value,
        }
        if col:
            entry["column"] = col
        result.append(entry)
    return result


def _collect_modules(cur: Any) -> list[dict[str, Any]]:
    """Collect module definitions (views, procs, functions, triggers)."""
    sql = """\
SELECT
    s.name + '.' + o.name,
    o.type_desc,
    CAST(sm.definition AS nvarchar(max))
FROM sys.sql_modules sm
JOIN sys.objects o ON o.object_id=sm.object_id
JOIN sys.schemas s ON s.schema_id=o.schema_id
WHERE o.type IN ('V','P','FN','TF','IF','TR')
  AND OBJECTPROPERTY(o.object_id,'IsMSShipped')=0
ORDER BY s.name, o.name"""
    result = []
    for row in _query(cur, sql):
        obj = row[0]
        if not obj:
            continue
        result.append({
            "object": obj,
            "type": row[1],
            "definition": row[2] or "",
        })
    return result


def _collect_schema_objects(cur: Any) -> dict[str, Any]:
    """Collect schemas, sequences, synonyms, and user table types."""
    sql_schemas = """\
SELECT name FROM sys.schemas WHERE schema_id < 16384 ORDER BY name"""
    sql_sequences = """\
SELECT s.name + '.' + seq.name FROM sys.sequences seq
JOIN sys.schemas s ON s.schema_id=seq.schema_id ORDER BY 1"""
    sql_synonyms = """\
SELECT s.name + '.' + syn.name, syn.base_object_name
FROM sys.synonyms syn
JOIN sys.schemas s ON s.schema_id=syn.schema_id ORDER BY 1"""
    sql_tts = """\
SELECT
    s.name + '.' + tt.name,
    c.name,
    tp.name,
    CASE WHEN c.is_nullable=1 THEN '1' ELSE '0' END
FROM sys.table_types tt
JOIN sys.schemas s ON s.schema_id=tt.schema_id
JOIN sys.columns c ON c.object_id=tt.type_table_object_id
JOIN sys.types tp ON tp.user_type_id=c.user_type_id
WHERE tt.is_user_defined=1
ORDER BY s.name, tt.name, c.column_id"""

    schemas = [row[0] for row in _query(cur, sql_schemas) if row[0]]
    sequences = [row[0] for row in _query(cur, sql_sequences) if row[0]]
    synonyms = [{"name": row[0], "target": row[1]} for row in _query(cur, sql_synonyms) if row[0]]

    tt_cols: dict[str, list[dict[str, Any]]] = {}
    for row in _query(cur, sql_tts):
        tt_name = row[0]
        if not tt_name:
            continue
        tt_cols.setdefault(tt_name, []).append({
            "name": row[1],
            "sql_type": row[2],
            "nullable": (row[3] or "") == "1",
        })
    table_types = [{"name": k, "columns": v} for k, v in sorted(tt_cols.items())]
    return {
        "schemas": [{"name": s} for s in schemas],
        "sequences": [{"name": s} for s in sequences],
        "synonyms": synonyms,
        "table_types": table_types,
    }


def _collect_security(cur: Any) -> dict[str, Any]:
    """Collect user/role principals and object permissions (name-resolved)."""
    sql_principals = """\
SELECT name, type_desc FROM sys.database_principals
WHERE type IN ('R','S','U','G','E','X') AND is_fixed_role=0
  AND name NOT IN ('guest','INFORMATION_SCHEMA','sys','public')
ORDER BY name"""
    sql_perms = """\
SELECT
    grantee.name,
    COALESCE(s.name + '.' + o.name, ''),
    dp.permission_name,
    dp.state_desc
FROM sys.database_permissions dp
JOIN sys.database_principals grantee ON grantee.principal_id=dp.grantee_principal_id
LEFT JOIN sys.objects o ON o.object_id=dp.major_id
LEFT JOIN sys.schemas s ON s.schema_id=o.schema_id
WHERE dp.class IN (0,1)
  AND grantee.name NOT IN ('guest','INFORMATION_SCHEMA','sys','public')
  AND grantee.is_fixed_role=0
ORDER BY grantee.name, s.name, o.name, dp.permission_name"""

    principals = []
    for row in _query(cur, sql_principals):
        if row[0]:
            principals.append({"name": row[0], "type": row[1]})
    permissions = []
    for row in _query(cur, sql_perms):
        grantee, obj, action, state = row[0], row[1] or "", row[2], row[3]
        if grantee and action:
            permissions.append({
                "grantee": grantee,
                "object": obj,
                "action": action,
                "state": state,
            })
    return {"principals": principals, "permissions": permissions}


def _collect_statistics(cur: Any) -> list[dict[str, Any]]:
    """Collect statistics objects (existence + key columns + flags)."""
    sql = """\
SELECT
    s2.name + '.' + t.name,
    st.name,
    CASE WHEN st.auto_created=1 THEN '1' ELSE '0' END,
    CASE WHEN st.no_recompute=1 THEN '1' ELSE '0' END,
    COALESCE(CAST(st.filter_definition AS nvarchar(max)), ''),
    COALESCE(STUFF((SELECT ',' + c.name
           FROM sys.stats_columns sc
           JOIN sys.columns c ON c.object_id=sc.object_id AND c.column_id=sc.column_id
           WHERE sc.object_id=st.object_id AND sc.stats_id=st.stats_id
           ORDER BY sc.stats_column_id
           FOR XML PATH('')),1,1,''), '')
FROM sys.stats st
JOIN sys.tables t ON t.object_id=st.object_id
JOIN sys.schemas s2 ON s2.schema_id=t.schema_id
WHERE t.is_ms_shipped=0
ORDER BY s2.name, t.name, st.name"""
    result = []
    for row in _query(cur, sql):
        name = row[1]
        if not name:
            continue
        key_cols_str = row[5] or ""
        result.append({
            "table": row[0],
            "name": name,
            "auto_created": (row[2] or "") == "1",
            "no_recompute": (row[3] or "") == "1",
            "filter": (row[4] or "") or None,
            "key_columns": key_cols_str.split(",") if key_cols_str else [],
        })
    return result


def _collect_plan_guides(cur: Any) -> list[dict[str, Any]]:
    """Collect plan guides (name, scope, query text, hints)."""
    sql = """\
SELECT
    name,
    scope_type_desc,
    CAST(query_text AS nvarchar(max)),
    COALESCE(CAST(parameters AS nvarchar(max)), ''),
    COALESCE(CAST(hints AS nvarchar(max)), '')
FROM sys.plan_guides
ORDER BY name"""
    result = []
    for row in _query(cur, sql):
        name = row[0]
        if not name:
            continue
        result.append({
            "name": name,
            "scope_type_desc": row[1],
            "query_text": row[2] or "",
            "parameters": (row[3] or "") or None,
            "hints": (row[4] or "") or None,
        })
    return result


def _collect_query_store(cur: Any) -> dict[str, Any]:
    """Collect Query Store enabled flag and query text list (presence only)."""
    sql_opts = "SELECT desired_state FROM sys.database_query_store_options"
    sql_texts = """\
SELECT CAST(query_sql_text AS nvarchar(max))
FROM sys.query_store_query_text
ORDER BY 1"""

    desired_state = 0
    try:
        rows = _query(cur, sql_opts)
        if rows:
            desired_state = int(rows[0][0] or 0)
    except Exception:
        pass

    query_texts: list[str] = []
    try:
        for row in _query(cur, sql_texts):
            text = row[0]
            if text:
                query_texts.append(text)
    except Exception:
        pass

    return {
        "enabled": desired_state > 0,
        "query_texts": query_texts,
    }


def _stable_write_metadata(out_path: Path, payload: dict[str, Any]) -> None:
    """Write metadata sidecar only when canonical content has changed.

    Volatile field ``captured_at`` is excluded from the change check.
    """
    canonical_keys = [k for k in payload if k != "captured_at"]
    canonical = {k: payload[k] for k in canonical_keys}
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
            existing_canonical = {k: existing[k] for k in canonical_keys if k in existing}
            if existing_canonical == canonical:
                print(
                    f"==> verified, no content change — {out_path} not rewritten",
                    file=sys.stderr,
                )
                return
        except (json.JSONDecodeError, OSError, KeyError):
            pass
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"==> wrote {out_path}", file=sys.stderr)


def _write_metadata_sidecar(
    bak_path: Path,
    bak_sha256: str,
    metadata: dict[str, Any],
    out_path: Path | None = None,
) -> Path:
    """Write ``<bak>.metadata.json`` and return the output path."""
    import datetime as _dt
    out = out_path or bak_path.with_suffix(bak_path.suffix + ".metadata.json")
    payload: dict[str, Any] = {
        "bak": bak_path.name,
        "bak_sha256": bak_sha256,
        "captured_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        **metadata,
    }
    _stable_write_metadata(out, payload)
    return out


def register_metadata_all(
    fixture_dir: Path,
    *,
    skip_existing: bool = True,
) -> int:
    """Capture ``<bak>.metadata.json`` sidecars for every .bak in fixture_dir.

    Requires the SQL Server container to be running (full restore per fixture).
    Skips fixtures that already have a ``.metadata.json`` sidecar when
    *skip_existing* is ``True`` (default).

    Returns the number of fixtures that failed (0 = all ok or nothing to do).
    """
    baks = sorted(fixture_dir.glob("*.bak"))
    todo = []
    for bak in baks:
        if bak.name in _UNREGISTERABLE_BAKS:
            print(f"  skip (unregisterable by design): {bak.name}", file=sys.stderr)
            continue
        sidecar = bak.with_suffix(bak.suffix + ".metadata.json")
        if skip_existing and sidecar.exists():
            print(f"  skip (metadata sidecar already exists): {bak.name}", file=sys.stderr)
            continue
        todo.append(bak)

    if not todo:
        print("==> all fixtures already have .metadata.json sidecars", file=sys.stderr)
        return 0

    print(f"==> capturing metadata for {len(todo)} fixture(s) …", file=sys.stderr)
    errors: list[tuple[Path, str]] = []
    for bak in todo:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"==> {bak.name}", file=sys.stderr)
        try:
            rc = main([str(bak), "--metadata-only"])
            if rc != 0:
                errors.append((bak, f"exited {rc}"))
        except Exception as exc:
            errors.append((bak, str(exc)))
            print(f"  ERROR: {exc}", file=sys.stderr)

    print(f"\n==> done: {len(todo) - len(errors)} ok, {len(errors)} failed", file=sys.stderr)
    for bak, msg in errors:
        print(f"  FAILED {bak.name}: {msg}", file=sys.stderr)
    return len(errors)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _stable_write_stats(out_path: Path, stats: dict[str, Any]) -> None:
    """Write stats to *out_path* only when the canonical content has changed.

    The volatile fields ``database``, ``registered_at``, and
    ``sqlserver_restore_s`` change on every run; we suppress the rewrite
    when only those fields differ so committed ``.stats.json`` files do not
    accumulate spurious git diffs.

    Canonical content = ``bak_sha256`` + ``tables`` (the fields that reflect
    real data changes).  If both match the existing file, the old file is left
    untouched and a "verified, no change" message is printed instead.
    """
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
            if (
                existing.get("bak_sha256") == stats.get("bak_sha256")
                and existing.get("tables") == stats.get("tables")
            ):
                print(
                    f"==> verified, no content change — {out_path} not rewritten",
                    file=sys.stderr,
                )
                return
        except (json.JSONDecodeError, OSError):
            pass  # unreadable or missing — fall through to write

    out_path.write_text(json.dumps(stats, indent=2))
    print(f"==> wrote {out_path}", file=sys.stderr)


def _verify_stats_match(
    out_path: Path,
    new_tables: list[dict[str, Any]],
    new_sha256: str,
) -> int:
    """Compare freshly-collected stats against an existing .stats.json.

    Returns 0 if the canonical content (``bak_sha256`` + ``tables``) matches,
    1 if they differ or no existing file is found.  Does NOT write anything.
    """
    if not out_path.exists():
        print(
            f"==> verify-only: no existing file at {out_path}",
            file=sys.stderr,
        )
        return 1
    try:
        existing = json.loads(out_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"==> verify-only: cannot read {out_path}: {exc}", file=sys.stderr)
        return 1

    sha_match = existing.get("bak_sha256") == new_sha256
    tables_match = existing.get("tables") == new_tables
    if sha_match and tables_match:
        print(f"==> verify-only: MATCH — {out_path}", file=sys.stderr)
        return 0

    if not sha_match:
        print(
            f"==> verify-only: MISMATCH — bak_sha256 differs "
            f"(existing={existing.get('bak_sha256', '?')!r})",
            file=sys.stderr,
        )
    if not tables_match:
        existing_tables = {
            f"{t['schema']}.{t['name']}": t
            for t in existing.get("tables", [])
        }
        new_tables_idx = {f"{t['schema']}.{t['name']}": t for t in new_tables}
        for fqn, new_t in sorted(new_tables_idx.items()):
            old_t = existing_tables.get(fqn)
            if old_t != new_t:
                print(
                    f"  table {fqn}: was {old_t!r}, now {new_t!r}",
                    file=sys.stderr,
                )
        for fqn in sorted(set(existing_tables) - set(new_tables_idx)):
            print(f"  table {fqn}: removed", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Restore a .bak to the forgedb SQL Server container and write "
            "<bak>.stats.json ground-truth statistics."
        )
    )
    parser.add_argument("bak", type=Path, help="path to the .bak fixture file")
    parser.add_argument(
        "--db-name", default="",
        help="database name to restore as (default: derived from .bak stem)",
    )
    parser.add_argument(
        "--keep", action="store_true",
        help="don't drop the restored database after collecting stats",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="output path for the .stats.json (default: <bak>.stats.json)",
    )
    parser.add_argument(
        "--no-cells", action="store_true",
        help="skip the per-cell ground-truth capture (<bak>.cells/ sidecar)",
    )
    parser.add_argument(
        "--cells-sample-n", type=int, default=200_000,
        help="rows stored in .cells/ parquet for tables above the sample threshold",
    )
    parser.add_argument(
        "--verify-only", action="store_true",
        help=(
            "restore and compare stats against the existing .stats.json without "
            "rewriting it; exit 0 if tables match, 1 if they differ or no "
            "existing file is found"
        ),
    )
    parser.add_argument(
        "--cells-only", action="store_true",
        help=(
            "capture only the <bak>.cells/ sidecar; do NOT collect or rewrite "
            "<bak>.stats.json (avoids churning its volatile registered_at/timing "
            "fields during a cells backfill)"
        ),
    )
    parser.add_argument(
        "--no-headeronly", action="store_true",
        help="skip writing the <bak>.bak.headeronly.json LSN sidecar",
    )
    parser.add_argument(
        "--headeronly-only", action="store_true",
        help=(
            "capture only the <bak>.bak.headeronly.json LSN sidecar without "
            "restoring the database or collecting stats (reads HEADERONLY without RESTORE)"
        ),
    )
    parser.add_argument(
        "--metadata-only", action="store_true",
        help=(
            "capture only the <bak>.metadata.json sidecar (non-data metadata: "
            "constraints, indexes, comments, modules, schemas, security, statistics, "
            "plan guides, Query Store); does NOT collect or rewrite <bak>.stats.json"
        ),
    )
    args = parser.parse_args(argv)

    if args.cells_only and (args.no_cells or args.verify_only):
        parser.error("--cells-only conflicts with --no-cells / --verify-only")

    bak_path: Path = args.bak.resolve()
    if not bak_path.is_file():
        print(f"error: {bak_path} not found", file=sys.stderr)
        return 1

    db_name: str = args.db_name or f"RegisterBak_{bak_path.stem}"
    out_path: Path = args.out or bak_path.with_suffix(bak_path.suffix + ".stats.json")

    # Load forgedb credentials (sets FIXTURE_* env vars).
    _server, container = bootstrap_fixture_env()
    password = os.environ["FIXTURE_DBA_PASSWORD"]

    print(f"==> bak:       {bak_path}", file=sys.stderr)
    print(f"==> container: {container}", file=sys.stderr)
    print(f"==> db_name:   {db_name}", file=sys.stderr)
    print(f"==> output:    {out_path}", file=sys.stderr)

    import datetime
    import time

    sql_ver = _sql_version(container, password)
    bak_stat = bak_path.stat()
    bak_size_bytes = bak_stat.st_size
    bak_size_mb = round(bak_size_bytes / 1_048_576, 3)

    headeronly_only: bool = getattr(args, "headeronly_only", False)
    no_headeronly: bool = getattr(args, "no_headeronly", False)
    metadata_only: bool = getattr(args, "metadata_only", False)

    if args.cells_only:
        bak_sha256 = ""
    else:
        print("==> hashing bak …", file=sys.stderr)
        bak_sha256 = _sha256(bak_path)

    # --headeronly-only: capture RESTORE HEADERONLY sidecar without restoring.
    # Copy the .bak into the container just long enough to run HEADERONLY.
    if headeronly_only:
        print("==> copying .bak for HEADERONLY (no restore) …", file=sys.stderr)
        container_bak = _copy_bak(container, bak_path)
        try:
            headeronly_sets = _collect_headeronly_info(container, password, container_bak)
        finally:
            _run(["podman", "exec", container, "rm", "-f", container_bak])
        _write_headeronly_sidecar(bak_path, headeronly_sets, dbinfo_lsns=None)
        return 0

    tables: list[dict[str, Any]] = []
    _restore_s: float = 0.0
    _headeronly_sets: list[dict[str, Any]] = []
    _dbinfo_lsns: dict[str, Any] | None = None
    _metadata: dict[str, Any] = {}
    try:
        t0 = time.perf_counter()
        _restore_bak(container, password, bak_path, db_name)
        _restore_s = round(time.perf_counter() - t0, 3)
        print(f"==> restore took {_restore_s:.1f}s", file=sys.stderr)

        # One driver connection serves both _collect_stats and _collect_metadata.
        # Opened whenever stats or metadata are needed; sqlcmd (podman exec) is
        # kept only for RESTORE/FILELISTONLY/HEADERONLY/BACKUP/DBCC above.
        if not args.cells_only:
            import tools.fixture_utils as _fu
            _conn = _fu.connect(container, "sa", password)
            try:
                _cur = _conn.cursor()
                _cur.execute(f"USE [{db_name}]")

                print("==> collecting statistics …", file=sys.stderr)
                tables = _collect_stats(_cur)

                # Metadata ground truth — collected unless verify-only.
                if not args.verify_only:
                    print("==> collecting metadata ground truth …", file=sys.stderr)
                    schema_objects = _collect_schema_objects(_cur)
                    security = _collect_security(_cur)
                    _metadata = {
                        "constraints": _collect_constraints(_cur),
                        "indexes": _collect_indexes(_cur),
                        "extended_properties": _collect_extended_properties(_cur),
                        "modules": _collect_modules(_cur),
                        "schemas": schema_objects["schemas"],
                        "sequences": schema_objects["sequences"],
                        "synonyms": schema_objects["synonyms"],
                        "table_types": schema_objects["table_types"],
                        "principals": security["principals"],
                        "permissions": security["permissions"],
                        "statistics": _collect_statistics(_cur),
                        "plan_guides": _collect_plan_guides(_cur),
                        "query_store": _collect_query_store(_cur),
                    }
            finally:
                _conn.close()

        # HEADERONLY LSN sidecar — always captured (unless --no-headeronly / metadata-only).
        if not no_headeronly and not args.verify_only and not metadata_only:
            print("==> capturing RESTORE HEADERONLY LSN sidecar …", file=sys.stderr)
            container_bak = f"/tmp/{bak_path.name}"
            _headeronly_sets = _collect_headeronly_info(container, password, container_bak)
            _dbinfo_lsns = _collect_dbinfo_lsns(container, password, db_name)

        # Per-cell ground truth (the row-level verifier SSOT). Captured while the
        # DB is still restored; skipped in --verify-only / --no-cells / --metadata-only.
        if not args.verify_only and not args.no_cells and not metadata_only:
            from tools.cells_capture import capture_cells

            print("==> capturing per-cell ground truth …", file=sys.stderr)
            cells_dir = bak_path.parent / (bak_path.name + ".cells")
            capture_cells(
                container, password, db_name, cells_dir,
                sample_n=args.cells_sample_n,
            )
    finally:
        if not args.keep:
            print(f"==> dropping [{db_name}] …", file=sys.stderr)
            _drop_db(container, password, db_name)

    if args.cells_only:
        print("==> cells-only: stats.json left untouched", file=sys.stderr)
        return 0

    # Write metadata sidecar.
    if _metadata:
        _write_metadata_sidecar(bak_path, bak_sha256, _metadata)

    if metadata_only:
        print("==> metadata-only: stats.json left untouched", file=sys.stderr)
        return 0

    # Write HEADERONLY sidecar (outside the try/finally so the DB is already dropped).
    if _headeronly_sets and not no_headeronly and not args.verify_only:
        _write_headeronly_sidecar(bak_path, _headeronly_sets, _dbinfo_lsns)

    total_rows = sum(t["row_count"] for t in tables)
    restore_mb_s = round(bak_size_mb / _restore_s, 1) if _restore_s > 0 else 0
    print(
        f"==> {len(tables)} tables, {total_rows} rows  |  "
        f"restore: {_restore_s:.1f}s ({restore_mb_s} MB/s on {bak_size_mb} MB bak)",
        file=sys.stderr,
    )

    if args.verify_only:
        return _verify_stats_match(out_path, tables, bak_sha256)

    stats = {
        "sql_version": sql_ver,
        "bak": bak_path.name,
        "bak_size_bytes": bak_size_bytes,
        "bak_size_mb": bak_size_mb,
        "bak_sha256": bak_sha256,
        "database": db_name,
        "registered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        # SQL Server restore timing — baseline to compare mssqlbak extraction against.
        "sqlserver_restore_s": _restore_s,
        "tables": tables,
    }
    _stable_write_stats(out_path, stats)
    return 0


def register_all(
    fixture_dir: Path,
    *,
    skip_existing: bool = True,
    keep: bool = False,
    version: str = "",
    cells_only: bool = False,
) -> int:
    """Register every .bak in fixture_dir that doesn't have a sidecar yet.

    When *cells_only* is ``True``, capture only the ``.cells/`` sidecar for
    fixtures that already have ``.stats.json`` but no ``.cells/`` directory —
    the ``register-all --cells-only`` backfill path.  Stats collection and
    ``.stats.json`` rewriting are skipped (no churn on stable sidecars).

    Returns the number of fixtures that failed (0 = all ok or nothing to do).
    """
    baks = sorted(fixture_dir.glob("*.bak"))
    todo = []
    for bak in baks:
        if bak.name in _UNREGISTERABLE_BAKS:
            print(f"  skip (unrestoreable by design): {bak.name}", file=sys.stderr)
            continue
        if cells_only:
            cells_dir = bak.parent / (bak.name + ".cells")
            if skip_existing and cells_dir.exists():
                print(f"  skip (cells already exist): {bak.name}", file=sys.stderr)
                continue
        else:
            stats = bak.with_suffix(bak.suffix + ".stats.json")
            if skip_existing and stats.exists():
                print(f"  skip (already registered): {bak.name}", file=sys.stderr)
                continue
        todo.append(bak)

    if not todo:
        label = "cells" if cells_only else "stats"
        print(f"==> all fixtures already have {label} sidecars", file=sys.stderr)
        return 0

    label = "cells" if cells_only else "fixtures"
    print(f"==> registering {len(todo)} {label} …", file=sys.stderr)
    errors: list[tuple[Path, str]] = []
    for bak in todo:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"==> {bak.name}", file=sys.stderr)
        argv = [str(bak)]
        if keep:
            argv.append("--keep")
        if cells_only:
            argv.append("--cells-only")
        try:
            rc = main(argv)
            if rc != 0:
                errors.append((bak, f"exited {rc}"))
        except Exception as exc:
            errors.append((bak, str(exc)))
            print(f"  ERROR: {exc}", file=sys.stderr)

    print(f"\n==> done: {len(todo) - len(errors)} ok, {len(errors)} failed", file=sys.stderr)
    for bak, msg in errors:
        print(f"  FAILED {bak.name}: {msg}", file=sys.stderr)
    return len(errors)


def register_headeronly_all(
    fixture_dir: Path,
    *,
    skip_existing: bool = True,
) -> int:
    """Capture ``<bak>.bak.headeronly.json`` sidecars for every .bak in fixture_dir.

    Uses ``--headeronly-only`` mode (no full restore / stats collection) so it
    only needs the container to run ``RESTORE HEADERONLY FROM DISK``.

    Skips fixtures that already have a ``.headeronly.json`` sidecar when
    *skip_existing* is ``True`` (default).

    Returns the number of fixtures that failed (0 = all ok or nothing to do).
    """
    baks = sorted(fixture_dir.glob("*.bak"))
    todo = []
    for bak in baks:
        if bak.name in _UNREGISTERABLE_BAKS:
            print(f"  skip (unregisterable by design): {bak.name}", file=sys.stderr)
            continue
        sidecar = bak.with_suffix(bak.suffix + ".headeronly.json")
        if skip_existing and sidecar.exists():
            print(f"  skip (headeronly sidecar already exists): {bak.name}", file=sys.stderr)
            continue
        todo.append(bak)

    if not todo:
        print("==> all fixtures already have .headeronly.json sidecars", file=sys.stderr)
        return 0

    print(f"==> capturing HEADERONLY for {len(todo)} fixture(s) …", file=sys.stderr)
    errors: list[tuple[Path, str]] = []
    for bak in todo:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"==> {bak.name}", file=sys.stderr)
        try:
            rc = main([str(bak), "--headeronly-only"])
            if rc != 0:
                errors.append((bak, f"exited {rc}"))
        except Exception as exc:
            errors.append((bak, str(exc)))
            print(f"  ERROR: {exc}", file=sys.stderr)

    print(f"\n==> done: {len(todo) - len(errors)} ok, {len(errors)} failed", file=sys.stderr)
    for bak, msg in errors:
        print(f"  FAILED {bak.name}: {msg}", file=sys.stderr)
    return len(errors)


if __name__ == "__main__":
    sys.exit(main())
