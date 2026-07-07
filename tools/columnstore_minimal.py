"""Minimal columnstore fixture — controlled row counts for segment decoding.

Creates one table per row-count tier (1, 2, 5, 10, 100) with a clustered
columnstore index, then forces every row group into a compressed segment via

    ALTER INDEX … REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)

so there is never a deltastore: every row lands in a binary column segment that
our decoder must read.

The column set is intentionally identical to ``cmp_columnstore`` in
compressionmatrix.py so the same decode paths are exercised, but each tier gives
us a *known-value* ground truth:

  tier 1  → bitpack has exactly 1 real value + padding zeros  (simplest)
  tier 2  → 2 real values
  tier 5  → 5 real values
  tier 10 → 10 real values
  tier 100→ 100 real values  (still << 1 048 576 row-group limit)

Every 7th row NULLs the nullable columns (same rule as compressionmatrix.py) so
the null-bitmap path is exercised once the tier is ≥ 7 rows.

Usage::

    FIXTURE_DBA_PASSWORD=<sa-password> python tools/columnstore_minimal.py

The ``.bak`` is written to ``tests/fixtures/columnstore_minimal.bak``.
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "ColumnstoreMinimal"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_PATH = FIXTURE_DIR / "columnstore_minimal.bak"

# Exact same columns as cmp_columnstore in compressionmatrix.py
_COLS = (
    "id int NOT NULL, "
    "code int NOT NULL, "
    "name varchar(20) NULL, "
    "nm nvarchar(40) NULL, "
    "ncf nchar(10) NULL, "
    "amount decimal(18,4) NULL, "
    "qty numeric(9,2) NULL, "
    "dt datetime NULL, "
    "dt2 datetime2(3) NULL, "
    "d date NULL, "
    "t time(3) NULL, "
    "dto datetimeoffset(3) NULL"
)
_COL_NAMES = "id, code, name, nm, ncf, amount, qty, dt, dt2, d, t, dto"

_BASE_DT = dt.datetime(2001, 1, 1, 0, 0, 0)

# Cyrillic "Привет" — same as compressionmatrix.py
_CYRILLIC_NM = "+".join(
    f"NCHAR({cp})" for cp in (0x041F, 0x0440, 0x0438, 0x0432, 0x0435, 0x0442)
)

# Row counts for each tier.  Covers 1 → 10,000 to observe when columnstore
# switches encoding strategy (pure-run RLE → bit-packed → dictionary) and
# whether a large row group (10 k < 1 M limit) stays in one segment.
TIERS = [1, 10, 100, 1_000, 10_000]


def _row_literal(i: int) -> str:
    """One VALUES tuple for row i (1-indexed).  Identical logic to compressionmatrix.py."""
    code = i % 50
    name = f"val{i % 10}"
    if i % 7 == 0:
        return f"({i}, {code}, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)"
    inst = _BASE_DT + dt.timedelta(minutes=i, milliseconds=(i % 1000))
    nm = _CYRILLIC_NM if i % 5 == 0 else f"N'name{i % 10}'"
    ncf = f"N'ncf{i % 10}'"
    amount = f"{i}.{i % 10000:04d}"
    qty = f"{i % 1000000}.{i % 100:02d}"
    dtv = inst.strftime("%Y-%m-%d %H:%M:%S.") + f"{inst.microsecond // 1000:03d}"
    datev = inst.strftime("%Y-%m-%d")
    timev = inst.strftime("%H:%M:%S.") + f"{inst.microsecond // 1000:03d}"
    dtov = f"{dtv} +05:30"
    return (
        f"({i}, {code}, N'{name}', {nm}, {ncf}, {amount}, {qty}, "
        f"'{dtv}', '{dtv}', '{datev}', '{timev}', '{dtov}')"
    )


def _build_tier(n: int) -> list[str]:
    """DDL + DML + CCI + REORGANIZE for one tier of *n* rows."""
    tbl = f"cs_{n}"
    parts: list[str] = []

    # Create table (heap — no clustered B-tree key)
    parts.append(f"CREATE TABLE [{tbl}] ({_COLS});")
    parts.append("GO")

    # Insert in batches of 200 to keep the script small
    for start in range(1, n + 1, 200):
        chunk = range(start, min(start + 200, n + 1))
        values = ", ".join(_row_literal(i) for i in chunk)
        parts.append(f"INSERT INTO [{tbl}] ({_COL_NAMES}) VALUES {values};")
    parts.append("GO")

    # Create the clustered columnstore index
    parts.append(f"CREATE CLUSTERED COLUMNSTORE INDEX cci_{tbl} ON [{tbl}];")
    parts.append("GO")

    # Force all rows into compressed row groups (no deltastore)
    parts.append(
        f"ALTER INDEX cci_{tbl} ON [{tbl}] REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON);"
    )
    parts.append("GO")

    return parts


def build_sql() -> str:
    """Full idempotent T-SQL script for all tiers."""
    parts: list[str] = [
        "USE [master];",
        "GO",
        f"IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN "
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
        f"DROP DATABASE [{DB_NAME}]; END;",
        "GO",
        f"CREATE DATABASE [{DB_NAME}];",
        "GO",
        f"USE [{DB_NAME}];",
        "GO",
    ]
    for n in TIERS:
        parts.extend(_build_tier(n))
    return "\n".join(parts) + "\n"


def main() -> int:
    from tools.make_fixture import generate_fixture

    return generate_fixture(DB_NAME, build_sql(), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
