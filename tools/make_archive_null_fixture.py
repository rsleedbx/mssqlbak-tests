#!/usr/bin/env python3
"""Generate ``archivenull_full.bak`` — columnstore ARCHIVE (enc_type=5) null probe.

Gap 5 fixture
-------------
The ARCHIVE columnstore format (``cmprlevel=4``, ``enc_type=5``) is used for
string columns when ``DATA_COMPRESSION = COLUMNSTORE_ARCHIVE`` is applied and
the row group is large (> 32,767 rows).  mssqlbak currently returns 0 NULLs
for ARCHIVE string segments instead of the correct count.

This fixture creates a controlled environment where the null count per column is
*known exactly* so a test can assert the correct value without guessing.

Schema
------
Database: ``ArchiveNull``

Table: ``dbo.archive_null``
    id    INT       NOT NULL   — row number, 1-50,000
    code  CHAR(10)  NULL       — NULL every 500th row → 100 NULLs total
    zip   CHAR(10)  NULL       — NULL every 1,000th row → 50 NULLs total

The clustered columnstore index is created with ``DATA_COMPRESSION =
COLUMNSTORE_ARCHIVE``, then rebuilt with the same option to guarantee all
50,000 rows land in a compressed (not delta) row group using enc_type=5 for
both string columns.

Expected test assertions
------------------------
- ``archive_null``: 50,000 rows
- ``code``: 100 NULL values (rows 500, 1000, …, 50000)
- ``zip``:   50 NULL values (rows 1000, 2000, …, 50000)
- If mssqlbak reports 0 NULLs for either column, Gap 5 is confirmed.

Version: SS2019 preferred (most aggressively uses ARCHIVE for strings);
SS2022 also works.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    _load_and_backup,
    fixture_credentials,
    skip_if_exists,
    sqlcmd_base,
)

DB_NAME = "ArchiveNull"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

# Lowercase paths avoid Lima virtiofs case-sensitivity issues.
CONTAINER_BAK = f"/tmp/{DB_NAME.lower()}_full.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME.lower()}.sql"

# Null positions are expressed as divisors; total rows = TOTAL_ROWS.
TOTAL_ROWS = 50_000
CODE_NULL_EVERY = 500   # 100 NULLs
ZIP_NULL_EVERY = 1_000  # 50 NULLs


def _out_path() -> Path:
    return FIXTURE_DIR / "archivenull_full.bak"


def build_sql() -> str:
    return f"""
USE [master];
GO

IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}];
END;
GO

CREATE DATABASE [{DB_NAME}];
GO

USE [{DB_NAME}];
GO

-- ----------------------------------------------------------------
-- archive_null
-- code  NULL every {CODE_NULL_EVERY} rows → {TOTAL_ROWS // CODE_NULL_EVERY} NULLs
-- zip   NULL every {ZIP_NULL_EVERY} rows  → {TOTAL_ROWS // ZIP_NULL_EVERY} NULLs
-- ----------------------------------------------------------------
CREATE TABLE [dbo].[archive_null] (
    id   INT      NOT NULL,
    code CHAR(10) NULL,
    zip  CHAR(10) NULL
);
GO

-- Insert {TOTAL_ROWS:,} rows using a tally generated from cross-joined system views.
WITH nums AS (
    SELECT TOP ({TOTAL_ROWS})
        ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n
    FROM sys.all_columns a
    CROSS JOIN sys.all_columns b
)
INSERT INTO [dbo].[archive_null] (id, code, zip)
SELECT
    CAST(n AS INT),
    CASE WHEN n % {CODE_NULL_EVERY} = 0 THEN NULL
         ELSE CAST(n AS CHAR(10)) END,
    CASE WHEN n % {ZIP_NULL_EVERY}  = 0 THEN NULL
         ELSE CAST(n AS CHAR(10)) END
FROM nums;
GO

-- Create clustered columnstore index with explicit ARCHIVE compression so that
-- string segments use enc_type=5.  MAXDOP=1 ensures a single row group.
CREATE CLUSTERED COLUMNSTORE INDEX cci
    ON [dbo].[archive_null]
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE, MAXDOP = 1);
GO

-- Rebuild to guarantee all rows are in compressed (non-delta) row groups with
-- ARCHIVE compression rather than the standard COLUMNSTORE (cmprlevel=3).
ALTER TABLE [dbo].[archive_null]
    REBUILD PARTITION = ALL
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE);
GO

USE [master];
GO
BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK}' WITH FORMAT, INIT;
GO
"""


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
    sqlcmd = sqlcmd_base(user, password, container)

    _load_and_backup(container, sqlcmd, build_sql(), CONTAINER_SQL)
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
