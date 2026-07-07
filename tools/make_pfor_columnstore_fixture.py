#!/usr/bin/env python3
"""Generate ``pfor_columnstore_full.bak`` — columnstore segments engineered to emit PFOR exceptions.

Why this fixture exists
=======================
Every other columnstore fixture stores integers as the monotonic sequence
``CAST(n AS INT)`` (id = 1..N).  After value encoding (subtract a base, bit-pack
the residual) a monotonic run is a perfectly smooth Frame-Of-Reference with
**zero outliers**, so SQL Server never needs to store a single exception.  As a
result the decoder's exception-walk path (docs/260616-2-fixture-dbcc-page-verifier.md
§15) has *never been exercised* — Issue 1 was ultimately a LOB-assembly bug, and
all passing tests happen to use exception-free data.

This fixture deliberately constructs columns whose value-encoded residuals are
**mostly tiny with a sparse minority of large outliers**, which is precisely the
distribution that (under PFOR / Patched Frame-Of-Reference) forces the encoder to
pick a small bit width ``b`` for the majority and patch the outliers as
exceptions.

Important honesty caveat
------------------------
We cannot *force* SQL Server to choose PFOR.  Low-cardinality columns may be
dictionary-encoded (enc_type=2) instead of bit-packed (enc_type=1).  The encoding
choice is the engine's, and discovering it is the whole point: pair this fixture
with ``tools/capture_verifier_sidecar.py`` to read back ``encoding_type`` from
``sys.column_store_segments`` and a ``DBCC PAGE`` dump for each column, then
compare the decoder output against the known inserted values.

Schema
------
Database: ``PforColumnstore``  →  single row group per table (rows < 1,048,576).

Two tables hold identical data, differing only in compression so the
XPRESS-wrapped ARCHIVE layout can be compared apples-to-apples against the plain
columnstore layout:

    pfor_plain     DATA_COMPRESSION = COLUMNSTORE
    pfor_archive   DATA_COMPRESSION = COLUMNSTORE_ARCHIVE

Each table has one monotonic join key plus five engineered INT columns, each a
different PFOR scenario (every value < INT max so no BIGINT needed):

  Column         Majority distribution        Outlier injection                 Knob exercised
  -------------- ---------------------------- ---------------------------------- ----------------------------
  id             n (monotonic 1..N)           none                               exception-free join key
  v_none         n % 1000                     none                               CONTROL: must stay clean
  v_sparse       n % 65536  (16-bit, hi-card) every 1009th row = 2,000,000,000   sparse (~0.1%) exception list
  v_deep         n % 1024                     single row (n = DEEP_ROW) = 2e9    first-exception boundary, deep
  v_compulsory   n % 8      (3-bit, lo range) every 5000th row = 1,000,000,000   compulsory exceptions (wide gap)
  v_dense        n % 32                       every 11th row = 1e9 + (n % 7)     dense (~9%) list / NewPFD path

The monotonic ``id`` column is exception-free and decodes reliably, giving a
stable key to join decoded rows back to expected values regardless of how the
CCI build orders rows within the row group.

Verification recipe (not done here; needs a live container)
-----------------------------------------------------------
1. Build the .bak:   python -m tools.fixture_run pfor-columnstore
2. Capture sidecars: python -m tools.capture_verifier_sidecar pfor_columnstore_full
   → records encoding_type + min/max/bitpack header per (col, segment).
3. Decode with mssqlbak and join on id; assert decoded v_* == inserted v_*.
   Any mismatch on v_sparse / v_deep / v_compulsory / v_dense while v_none stays
   correct localizes the bug to the exception-walk path.

Version: SS2019+ preferred (most aggressive ARCHIVE encoding); SS2017 also works.
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

DB_NAME = "PforColumnstore"
DB_NAME_RANDOM = "PforColumnstoreRandom"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

CONTAINER_BAK = "/tmp/pfor_columnstore_full.bak"
CONTAINER_BAK_RANDOM = "/tmp/pfor_columnstore_random_full.bak"
CONTAINER_SQL = "/tmp/load_pfor_columnstore.sql"
CONTAINER_SQL_RANDOM = "/tmp/load_pfor_columnstore_random.sql"

# Single row group keeps one segment per column (max row group = 1,048,576).
DEFAULT_ROWS = 200_000

# Outlier cadences / magnitudes (all < 2,147,483,647 so INT suffices).
SPARSE_EVERY = 1009          # prime: avoids aligning with 128-value block boundaries
SPARSE_OUTLIER = 2_000_000_000
COMPULSORY_EVERY = 5_000     # wide gap vs the 3-bit majority range → forces compulsory exceptions
COMPULSORY_OUTLIER = 1_000_000_000
DENSE_EVERY = 11             # ~9% outliers: just under PFOR's typical ~10% exception threshold
DENSE_OUTLIER_BASE = 1_000_000_000


def _out_path(random: bool = False) -> Path:
    name = "pfor_columnstore_random_full.bak" if random else "pfor_columnstore_full.bak"
    return FIXTURE_DIR / name


def _insert_block(table: str, rows: int, random: bool = False) -> str:
    """Return the SQL INSERT block for *table* (identical data across tables)."""
    deep_row = rows // 2 + 1  # a single deep outlier, well inside the row group
    order_clause = "\nORDER BY NEWID()" if random else ""
    return f"""\
WITH nums AS (
    SELECT TOP ({rows})
        ROW_NUMBER() OVER (ORDER BY a.object_id, b.object_id) AS n
    FROM sys.all_columns a
    CROSS JOIN sys.all_columns b
)
INSERT INTO [dbo].[{table}] (id, v_none, v_sparse, v_deep, v_compulsory, v_dense)
SELECT
    CAST(n AS INT),
    CAST(n % 1000 AS INT),
    CAST(CASE WHEN n % {SPARSE_EVERY} = 0 THEN {SPARSE_OUTLIER}
              ELSE n % 65536 END AS INT),
    CAST(CASE WHEN n = {deep_row} THEN {SPARSE_OUTLIER}
              ELSE n % 1024 END AS INT),
    CAST(CASE WHEN n % {COMPULSORY_EVERY} = 0 THEN {COMPULSORY_OUTLIER}
              ELSE n % 8 END AS INT),
    CAST(CASE WHEN n % {DENSE_EVERY} = 0 THEN {DENSE_OUTLIER_BASE} + (n % 7)
              ELSE n % 32 END AS INT)
FROM nums{order_clause};
GO"""


def _table_block(table: str, compression: str, index: str, rows: int, random: bool = False) -> str:
    """CREATE TABLE + INSERT + CCI with the requested DATA_COMPRESSION."""
    return f"""\
CREATE TABLE [dbo].[{table}] (
    id           INT NOT NULL,
    v_none       INT NOT NULL,
    v_sparse     INT NOT NULL,
    v_deep       INT NOT NULL,
    v_compulsory INT NOT NULL,
    v_dense      INT NOT NULL
);
GO

{_insert_block(table, rows, random=random)}

CREATE CLUSTERED COLUMNSTORE INDEX {index}
    ON [dbo].[{table}]
    WITH (DATA_COMPRESSION = {compression}, MAXDOP = 1);
GO"""


def build_sql(rows: int = DEFAULT_ROWS, random: bool = False) -> str:
    db = DB_NAME_RANDOM if random else DB_NAME
    container_bak = CONTAINER_BAK_RANDOM if random else CONTAINER_BAK
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

-- ================================================================
-- pfor_plain — standard COLUMNSTORE (no XPRESS wrapper)
-- ================================================================
{_table_block("pfor_plain", "COLUMNSTORE", "cci_plain", rows, random=random)}

-- ================================================================
-- pfor_archive — COLUMNSTORE_ARCHIVE (XPRESS-wrapped segments)
--   Identical data to pfor_plain; lets us diff the archive layout
--   against the plain bit-pack for the same exception distribution.
-- ================================================================
{_table_block("pfor_archive", "COLUMNSTORE_ARCHIVE", "cci_archive", rows, random=random)}

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
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help=f"rows per table (default {DEFAULT_ROWS:,}; keep < 1,048,576 for a single row group)",
    )
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
    _load_and_backup(container, sqlcmd, build_sql(args.rows, random=args.random), container_sql)
    size = _copy_out(container, container_bak, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
