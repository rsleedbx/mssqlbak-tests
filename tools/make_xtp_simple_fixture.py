#!/usr/bin/env python3
"""Generate ``xtp_simple_full.bak`` — minimal XTP (In-Memory OLTP) reverse-engineering fixture.

## Purpose

XTP (eXtreme Transaction Processing, a.k.a. Hekaton) stores durable row data in
checkpoint file pairs (CFP), not in the standard 8 KB MDF page format.  The
checkpoint data is embedded in the ``.bak`` file as an additional file stream
alongside the MDF/LDF.

This fixture provides the smallest possible surface area for reverse-engineering
the XTP checkpoint data format:

  * A single memory-optimized table with only **fixed-length columns** (Phase 1).
  * A second table that adds one **variable-length column** (Phase 2 — same .bak).
  * Known row values so decoded bytes can be cross-referenced directly.

## Tables

### dbo.xtp_fixed — Phase 1: fixed-length columns only

    CREATE TABLE dbo.xtp_fixed (
        id      INT           NOT NULL,
        score   BIGINT        NOT NULL,
        flag    TINYINT       NOT NULL,
        CONSTRAINT pk_xtp_fixed PRIMARY KEY NONCLUSTERED (id)
    ) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)

| id | score         | flag |
|----|---------------|------|
|  1 |      100      |   1  |
|  2 |      200      |   0  |
|  3 | 999999999999  |  255 |

### dbo.xtp_var — Phase 2: adds one NVARCHAR column

    CREATE TABLE dbo.xtp_var (
        id      INT            NOT NULL,
        label   NVARCHAR(32)   NULL,
        CONSTRAINT pk_xtp_var PRIMARY KEY NONCLUSTERED (id)
    ) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)

| id | label          |
|----|----------------|
|  1 | 'Alfa'         |
|  2 | NULL           |
|  3 | 'Omega'        |

## Exported constants

  - ``DB_NAME``         — database name
  - ``XTP_FIXED_TABLE`` — table name for Phase 1
  - ``XTP_VAR_TABLE``   — table name for Phase 2
  - ``FIXED_EXPECTED``  — dict id → (score, flag) for xtp_fixed
  - ``VAR_EXPECTED``    — dict id → label (or None) for xtp_var

Usage:
    python -m tools.fixture_run xtp-simple
    python -m tools.fixture_run all-versions --suite xtp-simple
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
    skip_if_exists,
)

DB_NAME = "XtpSimple"
XTP_FIXED_TABLE = "xtp_fixed"
XTP_VAR_TABLE = "xtp_var"

# Expected column values — imported by the diagnostic/test scripts.
FIXED_EXPECTED: dict[int, tuple[int, int]] = {
    # id → (score, flag)
    1: (100, 1),
    2: (200, 0),
    3: (999_999_999_999, 255),
}

VAR_EXPECTED: dict[int, str | None] = {
    # id → label
    1: "Alfa",
    2: None,
    3: "Omega",
}

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
_OUT_PATH = _FIXTURE_DIR / "xtp_simple_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return T-SQL statements that build and back up XtpSimple."""
    fixed_rows = ",\n    ".join(
        f"({id_}, {score}, {flag})"
        for id_, (score, flag) in FIXED_EXPECTED.items()
    )
    var_rows_parts = []
    for id_, label in VAR_EXPECTED.items():
        lbl = f"N'{label}'" if label is not None else "NULL"
        var_rows_parts.append(f"({id_}, {lbl})")
    var_rows = ",\n    ".join(var_rows_parts)

    return [
        # Clean slate.
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        # XTP requires a MEMORY_OPTIMIZED_DATA filegroup.
        f"ALTER DATABASE [{DB_NAME}] ADD FILEGROUP [FG_XTP] CONTAINS MEMORY_OPTIMIZED_DATA",
        f"""ALTER DATABASE [{DB_NAME}] ADD FILE (
    NAME = N'xtp_simple_data',
    FILENAME = N'/var/opt/mssql/data/xtp_simple_data'
) TO FILEGROUP [FG_XTP]""",
        f"USE [{DB_NAME}]",
        # Phase 1: fixed-length columns only.
        f"""CREATE TABLE dbo.{XTP_FIXED_TABLE} (
    id    INT     NOT NULL,
    score BIGINT  NOT NULL,
    flag  TINYINT NOT NULL,
    CONSTRAINT pk_{XTP_FIXED_TABLE} PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.{XTP_FIXED_TABLE} (id, score, flag) VALUES\n    {fixed_rows}",
        # Phase 2: one variable-length column; NULL for id=2 to test null handling.
        f"""CREATE TABLE dbo.{XTP_VAR_TABLE} (
    id    INT           NOT NULL,
    label NVARCHAR(32)  NULL,
    CONSTRAINT pk_{XTP_VAR_TABLE} PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.{XTP_VAR_TABLE} (id, label) VALUES\n    {var_rows}",
        "CHECKPOINT",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def main(force: bool = False) -> int:
    if skip_if_exists(_OUT_PATH, force=force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"creating XTP simple fixture: {len(FIXED_EXPECTED)} fixed rows, {len(VAR_EXPECTED)} var rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, _OUT_PATH)
    print(f"wrote {_OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()
    sys.exit(main(force=args.force))
