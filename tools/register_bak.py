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

REPO_ROOT = Path(__file__).resolve().parent.parent
MSSQL_IMAGE_MATCH = "mssql/server"

_UNREGISTERABLE_BAKS = frozenset({
    "corrupt_metadata_confidence_full.bak",
    "tde_full.bak",
})


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    """Return the hex SHA-256 digest of *path* (streamed in 1 MiB chunks)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while data := f.read(chunk):
            h.update(data)
    return h.hexdigest()

_SQLCMD_CANDIDATES = [
    "/opt/mssql-tools18/bin/sqlcmd",  # 2019+
    "/opt/mssql-tools/bin/sqlcmd",    # 2017 and earlier
]
_SQLCMD_PATH_CACHE: dict[str, str] = {}


def _discover_sqlcmd(container: str) -> str:
    """Return the sqlcmd binary path inside *container* (probed once, cached)."""
    if container in _SQLCMD_PATH_CACHE:
        return _SQLCMD_PATH_CACHE[container]
    for candidate in _SQLCMD_CANDIDATES:
        r = subprocess.run(
            ["podman", "exec", container, "test", "-f", candidate],
            capture_output=True,
        )
        if r.returncode == 0:
            _SQLCMD_PATH_CACHE[container] = candidate
            return candidate
    raise RuntimeError(
        f"sqlcmd not found in container {container!r}; tried: {_SQLCMD_CANDIDATES}"
    )


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
    - CLR spatial/hierarchyid: call .STAsText() / .ToString() then take MIN/MAX.
    - ``binary``/``varbinary``: convert with style 1 (hex) after native MIN/MAX.
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


def _collect_stats(container: str, password: str, db_name: str) -> list[dict[str, Any]]:
    """Return per-table row counts, per-column null counts, and per-column min/max."""

    # Step 1: enumerate user tables.
    tables_sql = f"""
USE [{db_name}];
SET NOCOUNT ON;
SELECT s.name + '.' + t.name
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
WHERE t.is_ms_shipped = 0
ORDER BY s.name, t.name;
"""
    out = _run_sql_query(container, password, tables_sql)
    table_fqns = [
        line.strip() for line in out.splitlines()
        if "." in line.strip()
        and not line.startswith("-")
        and " " not in line.strip()  # exclude "Changed database context to '...'." noise
    ]

    if not table_fqns:
        print("  (no user tables found)", file=sys.stderr)
        return []

    tables_result: list[dict[str, Any]] = []

    for fqn in table_fqns:
        schema_name, table_name = fqn.split(".", 1)
        quoted = f"[{schema_name}].[{table_name}]"
        print(f"  collecting stats for {quoted} …", file=sys.stderr)

        # Row count.
        rc_sql = f"""
USE [{db_name}];
SET NOCOUNT ON;
SELECT COUNT_BIG(*) FROM {quoted};
"""
        rc_out = _run_sql_query(container, password, rc_sql)
        row_count = 0
        for line in rc_out.splitlines():
            line = line.strip()
            if line.isdigit():
                row_count = int(line)
                break

        # Column names and types.
        cols_sql = f"""
USE [{db_name}];
SET NOCOUNT ON;
SELECT c.name, t.name
FROM sys.columns c
JOIN sys.types t ON t.user_type_id = c.user_type_id
JOIN sys.tables tbl ON tbl.object_id = c.object_id
JOIN sys.schemas s ON s.schema_id = tbl.schema_id
WHERE s.name = '{schema_name}' AND tbl.name = '{table_name}'
  AND c.is_computed = 0
ORDER BY c.column_id;
"""
        cols_out = _run_sql_query(container, password, cols_sql)
        columns: list[dict[str, Any]] = []
        col_names: list[str] = []
        for line in cols_out.splitlines():
            parts = line.strip().split()
            # Require exactly 2 tokens: column_name type_name.  Lines with more
            # tokens are sqlcmd informational messages (e.g. "Changed database
            # context to '...'.") not data rows.
            if len(parts) == 2 and not parts[0].startswith("-"):
                col_names.append(parts[0])
                columns.append({"name": parts[0], "sql_type": parts[1]})

        # Null counts via one query per table (dynamic SQL → single round trip).
        if col_names and row_count > 0:
            null_parts = ",\n    ".join(
                f"SUM(CASE WHEN [{c}] IS NULL THEN 1 ELSE 0 END) AS [{c}]"
                for c in col_names
            )
            null_sql = f"""
USE [{db_name}];
SET NOCOUNT ON;
SELECT {null_parts}
FROM {quoted};
"""
            null_out = _run_sql_query(container, password, null_sql)
            # The output is one data line with space-separated null counts.
            null_vals: list[int] = []
            for line in null_out.splitlines():
                line = line.strip()
                if line and not line.startswith("-") and not line.startswith("("):
                    parts_n = line.split()
                    if all(p.isdigit() or (p.startswith("-") and p[1:].isdigit()) for p in parts_n):
                        null_vals = [int(p) for p in parts_n]
                        break
            for i, col in enumerate(columns):
                col["null_count"] = null_vals[i] if i < len(null_vals) else None
        else:
            for col in columns:
                col["null_count"] = 0

        # Min/max via UNION ALL — one row per column, pipe-separated:
        #   col_name | min_val | max_val
        # NULL values are replaced by _NULL_SENTINEL to distinguish from
        # the empty string that sqlcmd emits for NULL without this guard.
        if col_names and row_count > 0:
            union_terms: list[str] = []
            for col in columns:
                min_e, max_e = _minmax_col_exprs(col["name"], col["sql_type"])
                name_lit = col["name"].replace("'", "''")
                union_terms.append(
                    f"SELECT N'{name_lit}', {min_e}, {max_e} FROM {quoted}"
                )
            minmax_sql = f"""
USE [{db_name}];
SET NOCOUNT ON;
{chr(10).join(f"{'UNION ALL' if i else ''} {t}" for i, t in enumerate(union_terms))};
"""
            minmax_out = _run_sql_query(container, password, minmax_sql, sep="|")
            minmax_map: dict[str, tuple[str | None, str | None]] = {}
            for line in minmax_out.splitlines():
                if "|" not in line:
                    continue
                # Split on first two pipes only — max_val may contain '|'.
                parts_mm = line.split("|", 2)
                if len(parts_mm) < 3:
                    continue
                cname = parts_mm[0].strip()
                raw_min = parts_mm[1].strip()
                raw_max = parts_mm[2].strip()
                if not cname or cname.startswith("-"):
                    continue
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

    if args.cells_only:
        bak_sha256 = ""
    else:
        print("==> hashing bak …", file=sys.stderr)
        bak_sha256 = _sha256(bak_path)

    tables: list[dict[str, Any]] = []
    try:
        t0 = time.perf_counter()
        _restore_bak(container, password, bak_path, db_name)
        restore_s = round(time.perf_counter() - t0, 3)
        print(f"==> restore took {restore_s:.1f}s", file=sys.stderr)

        if not args.cells_only:
            print("==> collecting statistics …", file=sys.stderr)
            tables = _collect_stats(container, password, db_name)

        # Per-cell ground truth (the row-level verifier SSOT). Captured while the
        # DB is still restored; skipped in --verify-only / --no-cells.
        if not args.verify_only and not args.no_cells:
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

    total_rows = sum(t["row_count"] for t in tables)
    restore_mb_s = round(bak_size_mb / restore_s, 1) if restore_s > 0 else 0
    print(
        f"==> {len(tables)} tables, {total_rows} rows  |  "
        f"restore: {restore_s:.1f}s ({restore_mb_s} MB/s on {bak_size_mb} MB bak)",
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
        "sqlserver_restore_s": restore_s,
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


if __name__ == "__main__":
    sys.exit(main())
