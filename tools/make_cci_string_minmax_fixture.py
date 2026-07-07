#!/usr/bin/env python3
"""Generate ``cci_string_minmax_full.bak`` — CCI string/binary min-max metadata (Gap C-8).

## Purpose

SQL Server 2022 added optional min/max segment metadata for string and binary
column types in CCI (previously, only numeric and date/time columns stored
per-segment min/max in the catalog).  The metadata appears in the segment blob
and affects how the columnstore catalog tables are structured.

Failure mode: if the segment decoder misinterprets the SS2022 string min/max
header bytes, it produces wrong offsets for the actual column data — yielding
garbled string values silently.  The NULL case is especially fragile: a segment
where every value is NULL stores no min/max entry, and a decoder that assumes
the entry is always present reads past the end of the header.

## Schema and data

``dbo.cci_str_minmax`` — CCI table with VARCHAR and NVARCHAR columns plus
NULL rows to exercise the NULL-min/max path.

    id     INT NOT NULL
    name   VARCHAR(50) NULL   — mix of non-NULL and NULL values
    label  NVARCHAR(30) NULL  — same NULL pattern as name
    score  INT NOT NULL       — numeric column (always-present min/max)

1,200 rows: ids 1–1200.  Every 10th row has NULL name and label (120 NULL rows),
producing segments where the string min/max is NULL.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``
  - ``TABLE``
  - ``ROW_COUNT``
  - ``NULL_STRIDE`` — rows with id % NULL_STRIDE == 0 have NULL name/label

Usage:
    python -m tools.fixture_run cci-string-minmax
    python -m tools.fixture_run all-versions --suite cci-string-minmax --version 2022 --version 2025
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
)

DB_NAME = "CciStringMinmax"
TABLE = "cci_str_minmax"
ROW_COUNT = 1200
NULL_STRIDE = 10  # id % NULL_STRIDE == 0 → NULL name and label

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_string_minmax_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        f"""CREATE TABLE dbo.{TABLE} (
    id     INT           NOT NULL,
    name   VARCHAR(50)   NULL,
    label  NVARCHAR(30)  NULL,
    score  INT           NOT NULL,
    INDEX cci CLUSTERED COLUMNSTORE
)""",
        # Every NULL_STRIDE-th row gets NULL for name/label
        f"""INSERT INTO dbo.{TABLE} (id, name, label, score)
SELECT
    pk + 1 AS id,
    CASE WHEN (pk + 1) % {NULL_STRIDE} = 0 THEN NULL
         ELSE 'name_' + CAST(pk + 1 AS VARCHAR(10))
    END AS name,
    CASE WHEN (pk + 1) % {NULL_STRIDE} = 0 THEN NULL
         ELSE N'lbl_' + CAST(pk + 1 AS NVARCHAR(10))
    END AS label,
    (pk + 1) * 3 AS score
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # Force all rows into compressed segments
        f"""ALTER INDEX cci ON dbo.{TABLE}
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} rows into CCI with VARCHAR/NVARCHAR columns …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
