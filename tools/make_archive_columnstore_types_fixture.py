#!/usr/bin/env python3
"""Build ``archive_columnstore_types_full.bak`` — Gap I-1 fixture.

Tests that the ARCHIVE (enc_type=5) decoder handles every dictionary-encoded
column type, not just CHAR.  SQL Server encodes the following types into a
string-pool segment under COLUMNSTORE_ARCHIVE, but each has a different pool
structure (fixed-stride vs variable-length vs UTF-16 vs binary vs 16-byte GUID):

    CHAR(10)         fixed single-byte stride (already in archivenull + archive_columnstore_partition)
    VARCHAR(20)      variable-length single-byte, length-prefixed pool entries
    NCHAR(10)        fixed UTF-16LE stride (20 bytes per entry)
    NVARCHAR(20)     variable-length UTF-16LE, length-prefixed pool entries
    BINARY(10)       fixed binary stride
    VARBINARY(20)    variable-length binary, length-prefixed pool entries
    UNIQUEIDENTIFIER fixed 16-byte stride

A decoder that assumes CHAR(10)'s fixed-10-byte stride would silently corrupt
every row for the other six types.

Architecture note
-----------------
This is the first fixture in mssqlbak to use the new ``SqlDialect`` /
``EngineAdapter`` layer introduced as the reference pattern for the pgbak
project.  The ``build_sql()`` function is pure and dialect-agnostic; only
``main()`` binds it to SQL Server.  To generate the equivalent PostgreSQL
fixture, swap in ``PostgresDialect`` and ``PostgresAdapter``.

Usage::

    python -m tools.fixture_run archive-columnstore-types
    python -m tools.fixture_run --fixture-dir tests/fixtures_2019 archive-columnstore-types
    python -m tools.fixture_run all-versions --suite archive-columnstore-types
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.dialects.base import SqlDialect  # noqa: E402
from tools.dialects.sqlserver import SqlServerDialect  # noqa: E402
from tools.engines.base import EngineAdapter  # noqa: E402
from tools.engines.sqlserver import SqlServerAdapter  # noqa: E402
from tools.fixture_utils import skip_if_exists  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DB_NAME = "ArchiveColumnstoreTypes"
DB_NAME_RANDOM = "ArchiveColumnstoreTypesRandom"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"
CONTAINER_BAK_RANDOM = f"/tmp/{DB_NAME_RANDOM}.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME}.sql"
CONTAINER_SQL_RANDOM = f"/tmp/load_{DB_NAME_RANDOM}.sql"

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures"))
)

# 35,000 rows > 32,767 → forces multi-sub-block enc_type=5 under ARCHIVE.
TOTAL_ROWS = 35_000
# NULL every 500th row → 70 NULLs per table.
NULL_EVERY = 500
NULL_COUNT = TOTAL_ROWS // NULL_EVERY  # 70


def _out_path(random: bool = False) -> Path:
    name = "archive_columnstore_types_random_full.bak" if random else "archive_columnstore_types_full.bak"
    return FIXTURE_DIR / name


# ---------------------------------------------------------------------------
# Archive type registry
# ---------------------------------------------------------------------------
# Each entry: (canonical, dialect params, table suffix, non-null value SQL expr)
# The value expression uses `n` (the row number CTE column) to produce a
# deterministic, distinct value for each row.
#
# BINARY: CAST(CAST(n AS VARBINARY(4)) AS BINARY(10)) — zero-pads n to 10 bytes.
# UNIQUEIDENTIFIER: HASHBYTES('MD5', CAST(n AS VARCHAR)) → 16-byte deterministic GUID.
# All others use direct CAST from the integer row number.
_ARCHIVE_TYPES: list[tuple[str, dict[str, int], str, str]] = [
    # (canonical, params, table_suffix, non_null_value_expr)
    ("char",      {"n": 10}, "char10",      "CAST(n AS CHAR(10))"),
    ("varchar",   {"n": 20}, "varchar20",   "CAST(n AS VARCHAR(20))"),
    ("nchar",     {"n": 10}, "nchar10",     "CAST(n AS NCHAR(10))"),
    ("nvarchar",  {"n": 20}, "nvarchar20",  "CAST(n AS NVARCHAR(20))"),
    ("binary",    {"n": 10}, "binary10",    "CAST(CAST(n AS VARBINARY(4)) AS BINARY(10))"),
    ("varbinary", {"n": 20}, "varbinary20", "CAST(n AS VARBINARY(4))"),
    ("uuid",      {},        "uuid",
     "CAST(HASHBYTES('MD5', CAST(n AS VARCHAR(10))) AS UNIQUEIDENTIFIER)"),
]


# ---------------------------------------------------------------------------
# SQL builder  (pure function — dialect-agnostic, engine-agnostic)
# ---------------------------------------------------------------------------

def _nums_cte() -> str:
    """CTE that generates TOTAL_ROWS sequential integers as column ``n``."""
    return (
        f"WITH nums AS (\n"
        f"    SELECT TOP ({TOTAL_ROWS})\n"
        f"        ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n\n"
        f"    FROM sys.all_columns a\n"
        f"    CROSS JOIN sys.all_columns b\n"
        f")"
    )


def _one_table_sql(
    suffix: str,
    sql_type: str,
    value_expr: str,
    random: bool = False,
) -> list[str]:
    """Return DDL + DML for one type table.

    Schema: ``id INT NOT NULL, val <sql_type> NULL``
    Compression: CLUSTERED COLUMNSTORE + REBUILD COLUMNSTORE_ARCHIVE
    Null pattern: every {NULL_EVERY}th row is NULL  → {NULL_COUNT} NULLs total
    """
    tbl = f"archive_{suffix}"
    parts = [
        f"-- ---- {tbl} ({sql_type}) ----",
        f"CREATE TABLE [dbo].[{tbl}] (",
        "    id   INT          NOT NULL,",
        f"    val  {sql_type}   NULL",
        ");",
        "GO",
        f"CREATE CLUSTERED COLUMNSTORE INDEX cci ON [dbo].[{tbl}] WITH (MAXDOP = 1);",
        "GO",
        f"{_nums_cte()}",
        f"INSERT INTO [dbo].[{tbl}] (id, val)",
        "SELECT",
        "    CAST(n AS INT),",
        f"    CASE WHEN n % {NULL_EVERY} = 0 THEN NULL",
        f"         ELSE {value_expr} END",
        "FROM nums" + ("\nORDER BY NEWID()" if random else "") + ";",
        "GO",
        # Force all rows from delta store into compressed column segments.
        f"ALTER TABLE [dbo].[{tbl}]",
        "    REBUILD PARTITION = ALL",
        "    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE);",
        "GO",
    ]
    return parts


def build_sql(dialect: SqlDialect, random: bool = False) -> str:
    """Assemble the complete T-SQL script for the archive-types database.

    Accepts any ``SqlDialect``; only the ``sql_type()`` call depends on the
    dialect — the structural logic (CTE, INSERT pattern, REBUILD) is
    dialect-agnostic and reusable for pgbak/mybak equivalents.
    """
    db = DB_NAME_RANDOM if random else DB_NAME
    container_bak = CONTAINER_BAK_RANDOM if random else CONTAINER_BAK
    parts: list[str] = [
        "USE [master];",
        "GO",
        f"IF DB_ID('{db}') IS NOT NULL BEGIN",
        f"    ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;",
        f"    DROP DATABASE [{db}];",
        "END;",
        "GO",
        f"CREATE DATABASE [{db}];",
        "GO",
        f"USE [{db}];",
        "GO",
    ]
    for canonical, params, suffix, value_expr in _ARCHIVE_TYPES:
        sql_type = dialect.sql_type(canonical, **params)
        parts.extend(_one_table_sql(suffix, sql_type, value_expr, random=random))

    parts += [
        "USE [master];",
        "GO",
        dialect.backup_sql(db, container_bak),
        "GO",
    ]
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate archive_columnstore_types_full.bak — Gap I-1: "
            "all dictionary-encoded types under COLUMNSTORE_ARCHIVE."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing fixture",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="shuffle insert order via ORDER BY NEWID() (random-order variant)",
    )
    args = parser.parse_args()

    out = _out_path(random=args.random)
    if skip_if_exists(out, force=args.force):
        return 0

    dialect: SqlDialect = SqlServerDialect()
    engine: EngineAdapter = SqlServerAdapter()
    container_sql = CONTAINER_SQL_RANDOM if args.random else CONTAINER_SQL
    container_bak = CONTAINER_BAK_RANDOM if args.random else CONTAINER_BAK

    sql = build_sql(dialect, random=args.random)
    engine.run_sql(sql, container_sql)
    size = engine.extract_backup(container_bak, out)
    print(f"wrote {out} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
