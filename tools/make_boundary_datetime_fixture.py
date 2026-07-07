#!/usr/bin/env python3
"""Build the datetime/bit/decimal boundary-value columnstore fixture (Gap K-2).

Creates ``BoundaryDatetimeCoverage`` — one table per
:data:`tools.boundary_datetime_matrix.BOUNDARY_DATETIME_CASES` entry:

    tb_bit, tb_decimal_9_4, tb_decimal_18_4, tb_date, tb_datetime,
    tb_datetime2_3, tb_time_3, tb_smalldatetime, tb_datetimeoffset_3

Each table has:
  - 6 labeled boundary rows (validated by ``tests/test_boundary_datetime_coverage.py``)
  - 1 194 filler rows (total 1 200 → enc=4 CCI segment)

The full 1 200 rows force SQL Server to flush the delta store into a compressed
CCI row group (enc=4), which is the segment encoding path under test.

Usage::

    python -m tools.fixture_run boundary-datetime
    python -m tools.fixture_run all-versions --suite boundary-datetime
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)
from tools.boundary_datetime_matrix import BOUNDARY_DATETIME_CASES, N_FILLER  # noqa: E402
from tools.make_fixture import sql_literal  # noqa: E402


def _dt_sql_literal(value: object, sql_type: str) -> str:
    """SQL literal that respects SQL Server's per-type fractional-second precision.

    Python ``datetime.isoformat()`` produces 6-digit microseconds, but:
    * classic ``DATETIME``: only accepts 3-digit milliseconds in string literals
    * ``DATETIME2(n)`` / ``TIME(n)`` / ``DATETIMEOFFSET(n)``: accepts exactly n digits
    * ``DATE`` / ``SMALLDATETIME``: no fractional seconds
    """
    if value is None:
        return "NULL"

    type_lower = sql_type.lower()

    # --- classic DATETIME: 3-digit milliseconds only ---
    if isinstance(value, dt.datetime) and type_lower == "datetime":
        ms = value.microsecond // 1000
        return (
            f"N'{value.year:04d}-{value.month:02d}-{value.day:02d} "
            f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}.{ms:03d}'"
        )

    # --- SMALLDATETIME: no fractional seconds ---
    if isinstance(value, dt.datetime) and "smalldatetime" in type_lower:
        return (
            f"N'{value.year:04d}-{value.month:02d}-{value.day:02d} "
            f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}'"
        )

    # --- DATETIME2(n): exactly n fractional digits ---
    if isinstance(value, dt.datetime) and "datetime2" in type_lower:
        m = re.search(r"\((\d+)\)", sql_type)
        scale = int(m.group(1)) if m else 7
        divisor = 10 ** (6 - scale)
        frac = value.microsecond // divisor
        return (
            f"N'{value.year:04d}-{value.month:02d}-{value.day:02d} "
            f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}.{frac:0{scale}d}'"
        )

    # --- DATETIMEOFFSET(n): datetime2(n) + ' +HH:MM' offset ---
    if isinstance(value, dt.datetime) and "datetimeoffset" in type_lower:
        m = re.search(r"\((\d+)\)", sql_type)
        scale = int(m.group(1)) if m else 7
        divisor = 10 ** (6 - scale)
        frac = value.microsecond // divisor
        offset = value.utcoffset() or dt.timedelta(0)
        total_min = int(offset.total_seconds()) // 60
        sign = "+" if total_min >= 0 else "-"
        abs_min = abs(total_min)
        return (
            f"N'{value.year:04d}-{value.month:02d}-{value.day:02d} "
            f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}.{frac:0{scale}d} "
            f"{sign}{abs_min // 60:02d}:{abs_min % 60:02d}'"
        )

    # --- TIME(n): exactly n fractional digits ---
    if isinstance(value, dt.time) and "time" in type_lower:
        m = re.search(r"\((\d+)\)", sql_type)
        scale = int(m.group(1)) if m else 7
        divisor = 10 ** (6 - scale)
        frac = value.microsecond // divisor
        return (
            f"N'{value.hour:02d}:{value.minute:02d}:{value.second:02d}.{frac:0{scale}d}'"
        )

    # Fallback: use the generic sql_literal (handles bool, int, Decimal, date, str, etc.)
    return sql_literal(value)

DB_NAME = "BoundaryDatetimeCoverage"
CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "boundarycoverage_datetime_full.bak"


def _tbl(case_name: str) -> str:
    return f"tb_{case_name}"


def build_stmts() -> list[str]:
    """Return the list of SQL batches (no GO needed) to set up the fixture DB."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]

    for case in BOUNDARY_DATETIME_CASES:
        tbl = _tbl(case.name)

        # Create heap table with CCI (delta store receives inserts).
        stmts.append(
            f"CREATE TABLE [{tbl}] (\n"
            f"    id    INT IDENTITY(1,1) NOT NULL,\n"
            f"    label VARCHAR(10) NULL,\n"
            f"    v     {case.sql_type} NULL\n"
            f")"
        )
        stmts.append(
            f"CREATE CLUSTERED COLUMNSTORE INDEX [cci_{tbl}] ON [{tbl}]"
        )

        # Insert the labeled boundary rows one by one.
        for row in case.rows:
            v_lit = _dt_sql_literal(row.value, case.sql_type)
            stmts.append(
                f"INSERT INTO [{tbl}] (label, v) VALUES ({sql_literal(row.label)}, {v_lit})"
            )

        # Insert filler rows via a recursive CTE to hit 1 200 total rows.
        stmts.append(
            f"WITH n(n) AS (\n"
            f"    SELECT 1 UNION ALL SELECT n + 1 FROM n WHERE n < {N_FILLER}\n"
            f")\n"
            f"INSERT INTO [{tbl}] (label, v)\n"
            f"SELECT NULL, {case.filler_sql} FROM n\n"
            f"OPTION (MAXRECURSION {N_FILLER})"
        )

        # Flush delta store into compressed CCI segments.
        stmts.append(
            f"ALTER INDEX [cci_{tbl}] ON [{tbl}]"
            f" REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)"
        )

    # Backup.
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
