#!/usr/bin/env python3
"""Generate ``xmlheap_full.bak`` — heap table with xml/varchar(MAX)/varbinary(MAX) LOBs.

Gap 10 regression-guard fixture
--------------------------------
SQL Server 2008R2–2014 used a different byte layout for LOB pointers stored
inside heap data pages when the LOB column type is ``xml``.  mssqlbak fails to
read rows from those databases while correctly reading the same table structure
from SQL Server 2016+ (see `docs/FIXTURE_GAPS.md` Gap 10).

This fixture creates the SS2016+-format baseline:

* ``dbo.xml_heap`` — a **heap** (no clustered index) with four LOB columns:
    - ``xml_event   XML           NOT NULL`` — ~9 KB XML payload → LOB pages
    - ``xml_small   XML           NOT NULL`` — ~200 byte inline XML (fits in-row)
    - ``text_payload VARCHAR(MAX)  NULL``    — ~500 byte varchar LOB
    - ``bin_payload  VARBINARY(MAX) NULL``   — ~200 byte binary LOB
  200 rows modelled after AdventureWorks ``dbo.DatabaseLog``.

Purpose
-------
When a future fix to the pre-2016 LOB pointer parser is applied, running this
fixture's tests confirms the fix did not accidentally break the SS2016+ path.
The test also documents the expected in-row vs. LOB thresholds for each column
type, which is useful reference for the LOB pointer format investigation.

Version: SS2016+ (any); the fixture does NOT reproduce the pre-2016 bug.
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

DB_NAME = "XmlHeap"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

# Lowercase paths avoid Lima virtiofs case-sensitivity issues.
CONTAINER_BAK = f"/tmp/{DB_NAME.lower()}_full.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME.lower()}.sql"

ROW_COUNT = 200


def _out_path() -> Path:
    return FIXTURE_DIR / "xmlheap_full.bak"


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
-- xml_heap  — heap table (no clustered index) with xml + LOB columns.
-- The IDENTITY column does NOT create an index; the table is a heap.
-- ----------------------------------------------------------------
CREATE TABLE [dbo].[xml_heap] (
    id            INT            IDENTITY(1,1) NOT NULL,
    event_time    DATETIME2(3)   NOT NULL DEFAULT SYSUTCDATETIME(),
    event_type    NVARCHAR(100)  NOT NULL,
    -- Large XML payload (~9 KB): forces out-of-row LOB storage.
    xml_event     XML            NOT NULL,
    -- Small XML payload (~200 bytes): typically stored inline.
    xml_small     XML            NOT NULL,
    -- varchar(MAX): ~500-byte payload, stored as LOB.
    text_payload  VARCHAR(MAX)   NULL,
    -- varbinary(MAX): ~200-byte binary blob.
    bin_payload   VARBINARY(MAX) NULL
);
-- No PRIMARY KEY, no INDEX = heap; verify with sys.indexes where type = 0.
GO

-- Insert {ROW_COUNT} rows.
-- xml_event: ~9 KB payload (forces LOB page chain on the heap).
-- xml_small: small self-contained element (stays in-row on most pages).
WITH nums AS (
    SELECT TOP ({ROW_COUNT})
        ROW_NUMBER() OVER (ORDER BY a.object_id) AS n
    FROM sys.all_columns a
)
INSERT INTO [dbo].[xml_heap]
    (event_type, xml_event, xml_small, text_payload, bin_payload)
SELECT
    N'EventType_' + CAST(n AS NVARCHAR(10)),
    CAST(
        CAST(
            N'<event id="' + CAST(n AS NVARCHAR(10)) + N'" type="DatabaseLog">' +
            N'<data>' + REPLICATE(CAST(N'abcdefghij' AS NVARCHAR(MAX)), 900) + N'</data>' +
            N'</event>'
        AS NVARCHAR(MAX)) AS XML),
    CAST(
        N'<e id="' + CAST(n AS NVARCHAR(10)) + N'"><v>' +
        CAST(n * 7 AS NVARCHAR(20)) + N'</v></e>'
        AS XML),
    REPLICATE('X', 500),
    CAST(REPLICATE('B', 200) AS VARBINARY(MAX))
FROM nums;
GO

-- A second batch with NULL text_payload and bin_payload (rows {ROW_COUNT // 2 + 1}–{ROW_COUNT}).
-- These rows test NULL handling for optional LOB columns on a heap.
UPDATE [dbo].[xml_heap]
SET text_payload = NULL, bin_payload = NULL
WHERE id % 2 = 0;
GO

USE [master];
GO
-- Flush ghost-record cleanup before backup to prevent false logtail before_images.
CHECKPOINT;
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
