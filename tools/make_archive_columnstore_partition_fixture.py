#!/usr/bin/env python3
"""Generate ``archive_columnstore_partition_full.bak`` — partitioned columnstore ARCHIVE probe.

Gap 5 — partitioned-table supplement
-------------------------------------
The existing ``archivenull_full.bak`` tests an unpartitioned table where ALL rows
land in a single ARCHIVE row group.  This fixture adds three tables that each
use an explicit partition function so that different partitions can carry
different compression levels within the same CCI.

All three scenarios come from the SQL Server REBUILD syntax:

Scenario A — ``archive_part_single``
    REBUILD PARTITION = 1 WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)
    Only partition 1 is rebuilt with ARCHIVE; partitions 2-4 keep standard
    COLUMNSTORE.  Useful to confirm the decoder routes each row group
    independently.

Scenario B — ``archive_part_all``
    REBUILD PARTITION = ALL WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)
    All four partitions are ARCHIVE.  Behaviour should match the unpartitioned
    ``archivenull_full.bak`` fixture, but with per-partition row group boundaries
    in the segment metadata.

Scenario C — ``archive_part_mixed``
    REBUILD PARTITION = ALL WITH
        (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE ON PARTITIONS (1,3))
    Partitions 1 and 3 → ARCHIVE (enc_type=5, the failing path).
    Partitions 2 and 4 → standard COLUMNSTORE (enc_type works correctly).
    The working partitions act as an internal control: if their null counts are
    right but partitions 1/3 return 0 NULLs, the bug is strictly in the enc=5
    decoder path.

Scenario D — ``archive_part_roundtrip``
    First: REBUILD PARTITION = ALL WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)
    Then:  REBUILD PARTITION = ALL WITH (DATA_COMPRESSION = COLUMNSTORE)
    All partitions start as ARCHIVE then are converted back to standard
    COLUMNSTORE.  Verifies the decoder handles segments produced by a
    round-trip through ARCHIVE without leaving behind stale enc_type=5
    block headers or mis-aligned index offsets.

Schema
------
Database: ``ArchiveColumnstorePartition``

Partition function  pf_archive_part (INT)  RANGE LEFT  (35000, 70000, 105000)
Partition scheme    ps_archive_part         ALL TO ([PRIMARY])

  Partition | id range          | rows
  ----------|-------------------|-------
  1         | 1 – 35,000        | 35,000
  2         | 35,001 – 70,000   | 35,000
  3         | 70,001 – 105,000  | 35,000
  4         | 105,001 – 140,000 | 35,000

Each partition has 35,000 rows — well above the 32,767-row threshold that
triggers the multi-sub-block ARCHIVE format (enc_type=5).

Three tables, each with 140,000 rows total:

  archive_part_single  — partition 1 ARCHIVE, partitions 2-4 COLUMNSTORE
  archive_part_all     — all partitions ARCHIVE
  archive_part_mixed   — partitions 1+3 ARCHIVE, partitions 2+4 COLUMNSTORE

Null pattern (same across all three tables):
  code  CHAR(10)  NULL every 500th row  → 280 NULLs total (70 per partition)
  zip   CHAR(10)  NULL every 1,000th row → 140 NULLs total (35 per partition)

Expected test assertions
------------------------
- Each table: 140,000 rows
- archive_part_single / archive_part_all / archive_part_mixed:
    code → 280 NULLs, zip → 140 NULLs
- archive_part_mixed:
    partitions 2+4 (regular COLUMNSTORE) → 70 code NULLs, 35 zip NULLs each
    (internal control; if these pass while partitions 1+3 fail → Gap 5 confirmed)

Version: SS2019 preferred (most aggressively uses ARCHIVE for string columns).
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

DB_NAME = "ArchiveColumnstorePartition"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

CONTAINER_BAK = "/tmp/archive_columnstore_partition_full.bak"
CONTAINER_SQL = "/tmp/load_archive_columnstore_partition.sql"

TOTAL_ROWS = 140_000          # 35,000 per partition × 4 partitions
PARTITION_ROWS = 35_000       # > 32,767 → forces multi-sub-block enc_type=5
CODE_NULL_EVERY = 500         # 280 NULLs total, 70 per partition
ZIP_NULL_EVERY = 1_000        # 140 NULLs total, 35 per partition

# Partition boundaries (RANGE LEFT: partition N contains values <= boundary[N-1])
_P1_END = PARTITION_ROWS            # 35,000
_P2_END = PARTITION_ROWS * 2        # 70,000
_P3_END = PARTITION_ROWS * 3        # 105,000
# Partition 4: 105,001 – 140,000


def _out_path() -> Path:
    return FIXTURE_DIR / "archive_columnstore_partition_full.bak"


def _insert_block(table: str) -> str:
    """Return the SQL INSERT block for *table* (140,000 rows, same null pattern)."""
    return f"""\
WITH nums AS (
    SELECT TOP ({TOTAL_ROWS})
        ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n
    FROM sys.all_columns a
    CROSS JOIN sys.all_columns b
)
INSERT INTO [dbo].[{table}] (id, code, zip)
SELECT
    CAST(n AS INT),
    CASE WHEN n % {CODE_NULL_EVERY} = 0 THEN NULL
         ELSE CAST(n AS CHAR(10)) END,
    CASE WHEN n % {ZIP_NULL_EVERY}  = 0 THEN NULL
         ELSE CAST(n AS CHAR(10)) END
FROM nums;
GO"""


def build_sql() -> str:  # noqa: PLR0915  (long but linear SQL generation)
    return f"""\
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
-- Shared partition infrastructure
-- Partition 1: id  1 – {_P1_END:,}
-- Partition 2: id  {_P1_END + 1:,} – {_P2_END:,}
-- Partition 3: id  {_P2_END + 1:,} – {_P3_END:,}
-- Partition 4: id  {_P3_END + 1:,} – {TOTAL_ROWS:,}
-- ----------------------------------------------------------------
CREATE PARTITION FUNCTION pf_archive_part (INT)
    AS RANGE LEFT FOR VALUES ({_P1_END}, {_P2_END}, {_P3_END});
GO

CREATE PARTITION SCHEME ps_archive_part
    AS PARTITION pf_archive_part ALL TO ([PRIMARY]);
GO

-- ================================================================
-- Scenario A: archive_part_single
--   Partition 1 → COLUMNSTORE_ARCHIVE
--   Partitions 2-4 → standard COLUMNSTORE
-- ================================================================
CREATE TABLE [dbo].[archive_part_single] (
    id   INT      NOT NULL,
    code CHAR(10) NULL,
    zip  CHAR(10) NULL
) ON ps_archive_part(id);
GO

{_insert_block("archive_part_single")}

-- Create standard CCI first (all partitions COLUMNSTORE).
CREATE CLUSTERED COLUMNSTORE INDEX cci_single
    ON [dbo].[archive_part_single]
    WITH (MAXDOP = 1);
GO

-- Rebuild only partition 1 with ARCHIVE so that partition 1 uses enc_type=5
-- while partitions 2-4 retain standard COLUMNSTORE encoding.
ALTER TABLE [dbo].[archive_part_single]
    REBUILD PARTITION = 1
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE);
GO

-- ================================================================
-- Scenario B: archive_part_all
--   All partitions → COLUMNSTORE_ARCHIVE
-- ================================================================
CREATE TABLE [dbo].[archive_part_all] (
    id   INT      NOT NULL,
    code CHAR(10) NULL,
    zip  CHAR(10) NULL
) ON ps_archive_part(id);
GO

{_insert_block("archive_part_all")}

CREATE CLUSTERED COLUMNSTORE INDEX cci_all
    ON [dbo].[archive_part_all]
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE, MAXDOP = 1);
GO

ALTER TABLE [dbo].[archive_part_all]
    REBUILD PARTITION = ALL
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE);
GO

-- ================================================================
-- Scenario C: archive_part_mixed
--   Partitions 1+3 → COLUMNSTORE_ARCHIVE  (enc_type=5, failing path)
--   Partitions 2+4 → standard COLUMNSTORE (enc_type works, internal control)
-- ================================================================
CREATE TABLE [dbo].[archive_part_mixed] (
    id   INT      NOT NULL,
    code CHAR(10) NULL,
    zip  CHAR(10) NULL
) ON ps_archive_part(id);
GO

{_insert_block("archive_part_mixed")}

CREATE CLUSTERED COLUMNSTORE INDEX cci_mixed
    ON [dbo].[archive_part_mixed]
    WITH (MAXDOP = 1);
GO

-- Rebuild all partitions; apply ARCHIVE only to partitions 1 and 3.
ALTER TABLE [dbo].[archive_part_mixed]
    REBUILD PARTITION = ALL
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE ON PARTITIONS (1, 3));
GO

-- ================================================================
-- Scenario D: archive_part_roundtrip
--   Step 1: REBUILD ALL → COLUMNSTORE_ARCHIVE  (all partitions enc_type=5)
--   Step 2: REBUILD ALL → COLUMNSTORE          (turn ARCHIVE off)
--   Final state: all partitions standard COLUMNSTORE.
--   Tests the decoder on segments produced by a round-trip through ARCHIVE.
-- ================================================================
CREATE TABLE [dbo].[archive_part_roundtrip] (
    id   INT      NOT NULL,
    code CHAR(10) NULL,
    zip  CHAR(10) NULL
) ON ps_archive_part(id);
GO

{_insert_block("archive_part_roundtrip")}

CREATE CLUSTERED COLUMNSTORE INDEX cci_roundtrip
    ON [dbo].[archive_part_roundtrip]
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE, MAXDOP = 1);
GO

-- First rebuild: confirm all partitions are ARCHIVE.
ALTER TABLE [dbo].[archive_part_roundtrip]
    REBUILD PARTITION = ALL
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE);
GO

-- Second rebuild: convert all partitions back to standard COLUMNSTORE.
ALTER TABLE [dbo].[archive_part_roundtrip]
    REBUILD PARTITION = ALL
    WITH (DATA_COMPRESSION = COLUMNSTORE);
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
