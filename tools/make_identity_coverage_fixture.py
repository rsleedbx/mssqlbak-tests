#!/usr/bin/env python3
"""Generate ``identity_coverage_full.bak`` — all SQL Server IDENTITY-capable types.

## Purpose

Exercises all six data types that SQL Server's DDL allows for the ``IDENTITY``
property: ``tinyint``, ``smallint``, ``int``, ``bigint``, ``decimal(9,0)``, and
``numeric(9,0)``.  One table per type, each with 5 rows, gives ``_decode_idtval``
full coverage across every branch of ``_IDENTITY_TYPE_SIZE`` and
``_IDENTITY_DECIMAL_MAG_SIZE``.

Failure modes caught by this fixture:
  - ``identity_seed`` / ``identity_increment`` returns ``None`` for a valid
    identity column (wrong or missing xtype key in the size dicts).
  - Wrong byte-size assumption for decimal / numeric (sign+magnitude vs. plain int).
  - Seed or increment decoded with the wrong sign or magnitude.

## Schema

Six tables, all in ``dbo``, each with a single identity column ``id`` and a
``val VARCHAR(20)`` filler column:

  - ``dbo.tinyint_identity``   — ``TINYINT  IDENTITY(1, 1)``  (xtype 48)
  - ``dbo.smallint_identity``  — ``SMALLINT IDENTITY(1, 1)``  (xtype 52)
  - ``dbo.int_identity``       — ``INT      IDENTITY(1, 1)``  (xtype 56)
  - ``dbo.bigint_identity``    — ``BIGINT   IDENTITY(1, 1)``  (xtype 127)
  - ``dbo.decimal_identity``   — ``DECIMAL(9,0) IDENTITY(1, 1)``  (xtype 106)
  - ``dbo.numeric_identity``   — ``NUMERIC(9,0) IDENTITY(1, 1)``  (xtype 108)

## Exported constants (imported by the coverage test)

  - ``DB_NAME``       — database name
  - ``TINYINT_TABLE`` / ``SMALLINT_TABLE`` / ``INT_TABLE`` / ``BIGINT_TABLE``
  - ``DECIMAL_TABLE`` / ``NUMERIC_TABLE``
  - ``ALL_TABLES``    — ordered list of all six table names
  - ``ROW_COUNT``     — rows inserted per table (5)

Usage (preferred — credentials auto-loaded):
    python -m tools.fixture_run identity-coverage
    python -m tools.fixture_run all-versions --suite identity-coverage

Direct (set env vars manually):
    python -m tools.make_identity_coverage_fixture
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

DB_NAME = "IdentityCoverage"

TINYINT_TABLE  = "tinyint_identity"
SMALLINT_TABLE = "smallint_identity"
INT_TABLE      = "int_identity"
BIGINT_TABLE   = "bigint_identity"
DECIMAL_TABLE  = "decimal_identity"
NUMERIC_TABLE  = "numeric_identity"

ALL_TABLES = [
    TINYINT_TABLE,
    SMALLINT_TABLE,
    INT_TABLE,
    BIGINT_TABLE,
    DECIMAL_TABLE,
    NUMERIC_TABLE,
]

ROW_COUNT = 5

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "identity_coverage_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def _table_sql(name: str, col_type: str) -> str:
    return f"""CREATE TABLE dbo.{name} (
    id   {col_type} NOT NULL PRIMARY KEY CLUSTERED,
    val  VARCHAR(20) NOT NULL
)"""


def _insert_sql(name: str) -> str:
    return (
        f"INSERT INTO dbo.{name} (val)\n"
        f"SELECT 'row_' + CAST(pk + 1 AS VARCHAR(10))\n"
        f"FROM fkr__seed\n"
        f"WHERE pk < {ROW_COUNT}"
    )


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

    table_defs = [
        (TINYINT_TABLE,  "TINYINT      IDENTITY(1, 1)"),
        (SMALLINT_TABLE, "SMALLINT     IDENTITY(1, 1)"),
        (INT_TABLE,      "INT          IDENTITY(1, 1)"),
        (BIGINT_TABLE,   "BIGINT       IDENTITY(1, 1)"),
        (DECIMAL_TABLE,  "DECIMAL(9,0) IDENTITY(1, 1)"),
        (NUMERIC_TABLE,  "NUMERIC(9,0) IDENTITY(1, 1)"),
    ]

    for name, col_type in table_defs:
        stmts.append(_table_sql(name, col_type))
        stmts.append(_insert_sql(name))

    stmts += [
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
    print(f"building identity_coverage_full.bak — 6 tables × {ROW_COUNT} rows …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
