#!/usr/bin/env python3
"""Generate ``ndfcoverage_full.bak`` — a database with a primary MDF and a
secondary NDF filegroup.

Gap 3 fixture
-------------
Every synthetic fixture prior to this one places all tables on the default
``PRIMARY`` filegroup.  Real-world databases (CreditBackup100, tpcxbb_1gb)
frequently use a secondary filegroup (``DATA``, ``USERDATA``, etc.) for their
fact and dimension tables, and mssqlbak was returning 0 rows for those tables.

This fixture verifies that mssqlbak correctly reads pages from *all* filegroups
present in the backup image — not only ``file_id = 1`` (the primary MDF).

Schema
------
Database: ``NdfCoverage``
Files:
    NdfCoverage.mdf   — primary MDF (file_id = 1, filegroup PRIMARY)
    NdfCoverage_fg2.ndf — secondary NDF (file_id = 2, filegroup FG_SECONDARY)

Tables:
    dbo.primary_tbl    — 10 rows, stored on PRIMARY  (baseline)
    dbo.secondary_tbl  — 10 rows, stored on FG_SECONDARY  (Gap-3 target)

If extraction of ``secondary_tbl`` returns 0 rows, the IAM/B-tree reader is
not crossing file-id boundaries and the bug is confirmed in ``rows.py``.
If it returns 10 rows, Gap 3 is closed.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
    skip_if_exists,
)

DB_NAME = "NdfCoverage"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

# Lima virtiofs is case-insensitive; use lowercase so the path SQL Server writes
# and the path podman cp looks up are always the same string.
CONTAINER_BAK = f"/tmp/{DB_NAME.lower()}_full.bak"


def _out_path() -> Path:
    return FIXTURE_DIR / "ndfcoverage_full.bak"


_NDF_ROWS = 10


def build_stmts() -> list[str]:
    """Return statements to create and populate the NDF-coverage database."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"ALTER DATABASE [{DB_NAME}] ADD FILEGROUP [FG_SECONDARY]",
        f"""ALTER DATABASE [{DB_NAME}] ADD FILE (
    NAME = N'{DB_NAME}_fg2',
    FILENAME = N'/var/opt/mssql/data/{DB_NAME}_fg2.ndf',
    SIZE = 8MB,
    FILEGROWTH = 8MB
) TO FILEGROUP [FG_SECONDARY]""",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(_NDF_ROWS)
    stmts += [
        """CREATE TABLE [dbo].[primary_tbl] (
    id  INT           NOT NULL CONSTRAINT pk_primary_tbl PRIMARY KEY CLUSTERED,
    val NVARCHAR(100) NULL
)""",
        f"""INSERT INTO [dbo].[primary_tbl] (id, val)
SELECT CAST(pk + 1 AS INT), N'primary_row_' + CAST(pk + 1 AS NVARCHAR(10))
FROM fkr__seed
WHERE pk < {_NDF_ROWS}""",
        """CREATE TABLE [dbo].[secondary_tbl] (
    id  INT           NOT NULL CONSTRAINT pk_secondary_tbl PRIMARY KEY CLUSTERED,
    val NVARCHAR(100) NULL
) ON [FG_SECONDARY]""",
        f"""INSERT INTO [dbo].[secondary_tbl] (id, val)
SELECT CAST(pk + 1 AS INT), N'secondary_row_' + CAST(pk + 1 AS NVARCHAR(10))
FROM fkr__seed
WHERE pk < {_NDF_ROWS}""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' WITH FORMAT, INIT",
    ]
    return stmts


def main() -> int:
    import argparse as _ap
    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    out = _out_path()
    if skip_if_exists(out, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
