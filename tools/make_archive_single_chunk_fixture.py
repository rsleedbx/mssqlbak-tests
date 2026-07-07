#!/usr/bin/env python3
"""Generate ``archive_single_chunk_full.bak`` — TODO-F1: single-chunk enc=5 probe.

Why this fixture exists
=======================
Every existing enc=5 ARCHIVE fixture (``archivenull``, ``archive_columnstore_types``,
``archive_columnstore_partition``) uses ≥ 35,000-row tables.  Their compressed column
blobs span **multiple 65536-byte XPRESS chunks**, so the decoder always exercises the
cross-chunk ``pool_len`` formula (chunk 0 = global header, chunk 1+ = overflow +
sentinel).

If a column blob fits entirely in a **single** 64KB chunk, only chunk 0 exists and a
different code path runs.  No fixture has verified that path (docs/260616-status.md
TODO-F1).  This fixture builds a deliberately small ARCHIVE ``CHAR(10)`` table so the
compressed blob stays within one chunk.

Whether ≤ 5000 rows actually yields a single-chunk enc=5 blob is the empirical
question — confirm with the segment sidecar:

    python -m tools.fixture_run all-versions --suite archive-single-chunk
    python -m tools.fixture_run capture-verifier-sidecar   # records enc_type + blob/chunk layout

Schema
------
Database: ``ArchiveSingleChunk``  →  one table, one small ARCHIVE row group.

    archive_single_chunk
        id   INT      NOT NULL   monotonic 1..TOTAL_ROWS (decode join key)
        code CHAR(10) NULL       CAST(n AS CHAR(10)); NULL every CODE_NULL_EVERY-th row

Building the CCI on the already-populated heap compresses all rows into one ARCHIVE
row group directly (a < 102,400-row table would otherwise sit in the uncompressed
delta store and never produce an enc=5 segment).

Expected test assertions
------------------------
- Row count = TOTAL_ROWS
- code NULLs = TOTAL_ROWS // CODE_NULL_EVERY
- Non-null code values round-trip (rstrip == str(id))

Version: all SS versions (enc=5 is version-relevant 2017–2025).
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

DB_NAME = "ArchiveSingleChunk"
DB_NAME_RANDOM = "ArchiveSingleChunkRandom"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

CONTAINER_BAK = "/tmp/archive_single_chunk_full.bak"
CONTAINER_BAK_RANDOM = "/tmp/archive_single_chunk_random_full.bak"
CONTAINER_SQL = "/tmp/load_archive_single_chunk.sql"
CONTAINER_SQL_RANDOM = "/tmp/load_archive_single_chunk_random.sql"

# Small enough that the compressed CHAR(10) blob should fit in one 64KB chunk.
TOTAL_ROWS = 5_000
CODE_NULL_EVERY = 100          # 50 NULLs total
CODE_NULL_COUNT = TOTAL_ROWS // CODE_NULL_EVERY


def _out_path(random: bool = False) -> Path:
    name = "archive_single_chunk_random_full.bak" if random else "archive_single_chunk_full.bak"
    return FIXTURE_DIR / name


def build_sql(random: bool = False) -> str:
    db = DB_NAME_RANDOM if random else DB_NAME
    container_bak = CONTAINER_BAK_RANDOM if random else CONTAINER_BAK
    order_clause = "\nORDER BY NEWID()" if random else ""
    return f"""\
USE [master];
GO

IF DB_ID('{db}') IS NOT NULL BEGIN
    ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{db}];
END;
GO

CREATE DATABASE [{db}];
GO

USE [{db}];
GO

CREATE TABLE [dbo].[archive_single_chunk] (
    id   INT      NOT NULL,
    code CHAR(10) NULL
);
GO

WITH nums AS (
    SELECT TOP ({TOTAL_ROWS})
        ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n
    FROM sys.all_columns a
    CROSS JOIN sys.all_columns b
)
INSERT INTO [dbo].[archive_single_chunk] (id, code)
SELECT
    CAST(n AS INT),
    CASE WHEN n % {CODE_NULL_EVERY} = 0 THEN NULL
         ELSE CAST(n AS CHAR(10)) END
FROM nums{order_clause};
GO

-- Build the CCI on the populated heap so all {TOTAL_ROWS:,} rows compress into a
-- single ARCHIVE row group (small tables otherwise stay in the delta store).
CREATE CLUSTERED COLUMNSTORE INDEX cci_single_chunk
    ON [dbo].[archive_single_chunk]
    WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE, MAXDOP = 1);
GO

USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{container_bak}' WITH FORMAT, INIT;
GO
"""


def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    p.add_argument(
        "--random",
        action="store_true",
        help="shuffle insert order via ORDER BY NEWID() (random-order variant)",
    )
    args = p.parse_args()

    out = _out_path(random=args.random)
    if skip_if_exists(out, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    sqlcmd = sqlcmd_base(user, password, container)

    container_sql = CONTAINER_SQL_RANDOM if args.random else CONTAINER_SQL
    container_bak = CONTAINER_BAK_RANDOM if args.random else CONTAINER_BAK
    _load_and_backup(container, sqlcmd, build_sql(random=args.random), container_sql)
    size = _copy_out(container, container_bak, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
