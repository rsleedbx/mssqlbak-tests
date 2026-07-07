#!/usr/bin/env python3
"""Generate ``sparse_full.bak`` — sparse columns + column set (Gap D-1).

## Purpose

Sparse columns replace the standard per-column layout with a **sparse vector**
record appended to the row: a count of non-NULL sparse columns followed by an
array of ``(column_id, byte_offset)`` pairs and the packed non-NULL values.
NULL sparse columns cost zero bytes.

A record parser that walks the fixed-length block + variable-length block +
NULL bitmap will **completely misread** any sparse row — wrong values for every
column after the first sparse column — with no error.

This fixture creates one table with 4 SPARSE columns and 1 COLUMN_SET column
across 10,000 rows with varying sparsity patterns:

  - ``a INT SPARSE``           — non-NULL when id % 2 = 0 (5,000 rows)
  - ``b VARCHAR(20) SPARSE``   — non-NULL when id % 3 = 0 (3,333 rows)
  - ``c DATETIME2(3) SPARSE``  — non-NULL when id % 4 = 0 (2,500 rows)
  - ``d DECIMAL(10,2) SPARSE`` — always NULL (0 rows)
  - ``cs XML COLUMN_SET``      — virtual aggregate; physically present in row

## Exported constants (imported by the coverage test)

  - ``DB_NAME``       — database name used in the backup
  - ``ROW_COUNT``     — total rows inserted (10,000)
  - ``A_VALUE_FN``    — callable(id) → int; expected value when non-NULL
  - ``B_VALUE_FN``    — callable(id) → str; expected value when non-NULL
  - ``A_NON_NULL``    — predicate: id % 2 = 0 (evaluates as int)
  - ``B_NON_NULL``    — predicate: id % 3 = 0
  - ``C_NON_NULL``    — predicate: id % 4 = 0
  - ``C_VALUE_FN``    — callable(id) → datetime.datetime; expected value when non-NULL

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run sparse
    python -m tools.fixture_run all-versions --suite sparse

Direct (set env vars manually):
    python -m tools.make_sparse_fixture
"""
from __future__ import annotations

import argparse
import datetime
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
    skip_if_exists,
)

# ---------------------------------------------------------------------------
# Constants (imported by the coverage test)
# ---------------------------------------------------------------------------

DB_NAME = "SparseCoverage"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)

ROW_COUNT = 10_000

OUT_PATH = FIXTURE_DIR / "sparse_full.bak"


def A_VALUE_FN(id_: int) -> int:  # noqa: N802
    """Expected value of column ``a`` for a given ``id`` (when non-NULL)."""
    return id_ * 7


def B_VALUE_FN(id_: int) -> str:  # noqa: N802
    """Expected value of column ``b`` for a given ``id`` (when non-NULL)."""
    return f"str_{id_}"


def A_NON_NULL(id_: int) -> bool:  # noqa: N802
    """True when ``a`` should be non-NULL."""
    return id_ % 2 == 0


def B_NON_NULL(id_: int) -> bool:  # noqa: N802
    """True when ``b`` should be non-NULL."""
    return id_ % 3 == 0


def C_NON_NULL(id_: int) -> bool:  # noqa: N802
    """True when ``c`` should be non-NULL."""
    return id_ % 4 == 0


def C_VALUE_FN(id_: int) -> datetime.datetime:  # noqa: N802
    """Expected DATETIME2(3) value for column ``c`` for a given ``id`` (when non-NULL).

    Mirrors the SQL: DATEADD(day, (pk + 1) % 365, CAST('2020-01-01' AS DATETIME2(3)))
    where pk = id - 1 (pk is 0-based, id is 1-based).
    """
    return datetime.datetime(2020, 1, 1) + datetime.timedelta(days=id_ % 365)


# ---------------------------------------------------------------------------
# SQL builder (pure function — no side effects)
# ---------------------------------------------------------------------------

def build_stmts() -> list[str]:
    """Return DDL + DML + BACKUP statements for the sparse-columns fixture."""
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
        """CREATE TABLE dbo.sparse_wide (
    id  INT           NOT NULL PRIMARY KEY CLUSTERED,
    a   INT           SPARSE NULL,
    b   VARCHAR(20)   SPARSE NULL,
    c   DATETIME2(3)  SPARSE NULL,
    d   DECIMAL(10,2) SPARSE NULL,
    cs  XML COLUMN_SET FOR ALL_SPARSE_COLUMNS
)""",
        f"""INSERT INTO dbo.sparse_wide (id, a, b, c, d)
SELECT
    CAST(pk + 1 AS INT),
    CASE WHEN (pk + 1) % 2 = 0 THEN CAST((pk + 1) * 7 AS INT) ELSE NULL END,
    CASE WHEN (pk + 1) % 3 = 0 THEN 'str_' + CAST(pk + 1 AS VARCHAR(10)) ELSE NULL END,
    CASE WHEN (pk + 1) % 4 = 0
         THEN DATEADD(day, CAST((pk + 1) % 365 AS INT), CAST('2020-01-01' AS DATETIME2(3)))
         ELSE NULL END,
    NULL
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate sparse_full.bak — sparse columns + column set (Gap D-1)."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing .bak",
    )
    args = parser.parse_args()

    out = OUT_PATH

    if skip_if_exists(out, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"seeding {ROW_COUNT:,} rows …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
