#!/usr/bin/env python3
"""Generate ``cci_enc5_largepool_matrix_full.bak`` evidence tables.

The fixture varies row count, declared type, effective string width, and
cardinality for regular clustered columnstore enc=5 string pools.  It is intended
to produce byte-level evidence for the remaining large-pool Format D decoder gap
without replacing ``cci_enc5_largepool_full.bak``.

Usage:
    python -m tools.fixture_run cci-enc5-largepool-matrix
    python -m tools.fixture_run all-versions --suite cci-enc5-largepool-matrix
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
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

DB_NAME = "CciEnc5LargePoolMatrix"
NULL_STRIDE = 1000

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_enc5_largepool_matrix_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


@dataclass(frozen=True)
class TableCase:
    name: str
    row_count: int
    sql_type: str
    width: int
    cardinality: int | None
    variable_effective_width: bool


TABLE_CASES: tuple[TableCase, ...] = (
    TableCase("char_32767_distinct_var", 32_767, "CHAR(13)", 13, None, True),
    TableCase("char_32768_distinct_var", 32_768, "CHAR(13)", 13, None, True),
    TableCase("char_65536_distinct_var", 65_536, "CHAR(13)", 13, None, True),
    TableCase("char_80000_distinct_var", 80_000, "CHAR(13)", 13, None, True),
    TableCase("varchar_80000_distinct_var", 80_000, "VARCHAR(13)", 13, None, True),
    TableCase("char_80000_lowcard_var", 80_000, "CHAR(13)", 13, 4096, True),
    TableCase("char_80000_fullwidth", 80_000, "CHAR(13)", 13, None, False),
)


def _hash_seed(case: TableCase) -> str:
    if case.cardinality is None:
        return "pk + 1"
    return f"(pk % {case.cardinality}) + 1"


def _value_expr(case: TableCase) -> str:
    hash_expr = f"CONVERT(CHAR(32), HASHBYTES('MD5', CAST({_hash_seed(case)} AS VARCHAR(12))), 2)"
    if case.variable_effective_width:
        length_expr = f"1 + (pk % {case.width})"
        return f"CAST(LEFT({hash_expr}, {length_expr}) AS {case.sql_type})"
    return f"CAST(LEFT({hash_expr}, {case.width}) AS {case.sql_type})"


def _table_stmts(case: TableCase) -> list[str]:
    return [
        f"""CREATE TABLE dbo.{case.name} (
    id   INT NOT NULL,
    val  {case.sql_type} NULL,
    INDEX cci CLUSTERED COLUMNSTORE
)""",
        f"""INSERT INTO dbo.{case.name} (id, val)
SELECT
    pk + 1 AS id,
    CASE WHEN (pk + 1) % {NULL_STRIDE} = 0 THEN NULL
         ELSE {_value_expr(case)}
    END AS val
FROM fkr__seed
WHERE pk < {case.row_count}""",
        f"""ALTER INDEX cci ON dbo.{case.name}
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)""",
    ]


def build_stmts() -> list[str]:
    max_rows = max(case.row_count for case in TABLE_CASES)
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(max_rows)
    for case in TABLE_CASES:
        stmts.extend(_table_stmts(case))
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"building {len(TABLE_CASES)} enc=5 large-pool evidence tables")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
