#!/usr/bin/env python3
"""Generate ``featurecoverage_full.bak`` — SQL Server feature-coverage fixture.

Covers advanced SQL Server features not tested by the type/compression matrices:

Existing tables (SS2022+ only)
-------------------------------
* ``temporal_current``  — system-versioned temporal table, 50 rows.
                          10 rows (id % 5 == 0) were updated (value += 100);
                          their old versions land in ``temporal_history``.
* ``temporal_history``  — auto-created history heap, 10 rows.
* ``compress_col``      — VARBINARY(MAX) column storing COMPRESS(nvarchar) gzip
                          blobs, 20 rows.
* ``utf8_collation``    — varchar columns with Latin-1 and UTF-8-SC collations,
                          plus nvarchar, 6 rows (3 ASCII, 3 non-ASCII).
* ``ncci_table``        — row-store table + non-clustered columnstore index,
                          1 024 rows.
* ``ledger_account``    — append-only ledger table, 3 rows.
* ``graph_person``      — AS NODE graph table, 3 nodes.
* ``graph_follows``     — AS EDGE graph table, 2 directed edges.

Gap-2 table
-----------
* ``long_text``         — varchar(MAX) / nvarchar(MAX) / char(500) columns with
                          values longer than 200 characters.  Exercises the
                          NVARCHAR(4000) ground-truth cast in register_bak.py
                          rather than the old NVARCHAR(200) path.

Gap-4 table (SS2014+)
---------------------
* ``memory_oltp``       — MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA.
                          Classified with skip_reason "memory-optimized" because
                          data lives in XTP checkpoint files, not 8 KB pages.
                          Requires a MEMORY_OPTIMIZED_DATA filegroup.

Note: ledger tables require SS2022+; graph tables require SS2017+; In-Memory
OLTP requires SS2014+.  The fixture should be generated on SS2022.
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
    skip_if_server_older_than,
)

DB_NAME = "FeatureCoverage"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

# Lima virtiofs is case-insensitive; use lowercase so the path SQL Server writes
# and the path podman cp looks up are always the same string.
CONTAINER_BAK = f"/tmp/{DB_NAME.lower()}_full.bak"


def _out_path() -> Path:
    return FIXTURE_DIR / "featurecoverage_full.bak"


_TEMPORAL_ROWS = 50
_COMPRESS_ROWS = 20
_NCCI_ROWS = 1024


def build_stmts() -> list[str]:
    """Return all statements for the feature-coverage database."""
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"ALTER DATABASE [{DB_NAME}] ADD FILEGROUP [FG_MEMORY] CONTAINS MEMORY_OPTIMIZED_DATA",
        f"""ALTER DATABASE [{DB_NAME}] ADD FILE (
    NAME = N'{DB_NAME}_mem',
    FILENAME = N'/var/opt/mssql/data/{DB_NAME}_mem'
) TO FILEGROUP [FG_MEMORY]""",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(_NCCI_ROWS)  # largest count: 1024
    stmts += [
        # temporal_current / temporal_history
        """CREATE TABLE [dbo].[temporal_current] (
    id         INT            NOT NULL,
    value      DECIMAL(10, 2) NOT NULL,
    valid_from DATETIME2(7)   GENERATED ALWAYS AS ROW START NOT NULL,
    valid_to   DATETIME2(7)   GENERATED ALWAYS AS ROW END   NOT NULL,
    PERIOD FOR SYSTEM_TIME (valid_from, valid_to),
    CONSTRAINT pk_temporal_current PRIMARY KEY CLUSTERED (id)
) WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.temporal_history))""",
        f"""INSERT INTO [dbo].[temporal_current] (id, value)
SELECT CAST(pk + 1 AS INT), CAST((pk + 1) * 1.5 AS DECIMAL(10, 2))
FROM fkr__seed
WHERE pk < {_TEMPORAL_ROWS}""",
        "UPDATE [dbo].[temporal_current] SET value = value + 100 WHERE id % 5 = 0",
        # compress_col
        """CREATE TABLE [dbo].[compress_col] (
    id         INT            NOT NULL CONSTRAINT pk_compress_col PRIMARY KEY CLUSTERED,
    raw_text   NVARCHAR(MAX)  NULL,
    compressed VARBINARY(MAX) NULL
)""",
        f"""INSERT INTO [dbo].[compress_col] (id, raw_text, compressed)
SELECT
    CAST(pk + 1 AS INT),
    N'compress_row_' + CAST(pk + 1 AS NVARCHAR(20)),
    COMPRESS(N'compress_row_' + CAST(pk + 1 AS NVARCHAR(20)))
FROM fkr__seed
WHERE pk < {_COMPRESS_ROWS}""",
        # utf8_collation
        """CREATE TABLE [dbo].[utf8_collation] (
    id    INT           NOT NULL CONSTRAINT pk_utf8_collation PRIMARY KEY CLUSTERED,
    latin VARCHAR(100)  NULL,
    utf8  VARCHAR(100)  COLLATE Latin1_General_100_CI_AS_SC_UTF8 NULL,
    wide  NVARCHAR(100) NULL
)""",
        """INSERT INTO [dbo].[utf8_collation] (id, latin, utf8, wide) VALUES
    (1, 'ASCII',  'ASCII',  N'ASCII'),
    (2, 'hello',  'hello',  N'hello'),
    (3, 'world',  'world',  N'world'),
    (4, 'caf'  + CHAR(233), 'caf' + CHAR(233), N'caf' + NCHAR(233)),
    (5, 'na'   + CHAR(239) + 've', 'na' + CHAR(239) + 've', N'na' + NCHAR(239) + N've'),
    (6, 'r' + CHAR(233) + 'sum' + CHAR(233),
        'r' + CHAR(233) + 'sum' + CHAR(233),
        N'r' + NCHAR(233) + N'sum' + NCHAR(233))""",
        # ncci_table
        """CREATE TABLE [dbo].[ncci_table] (
    id     INT            NOT NULL CONSTRAINT pk_ncci PRIMARY KEY CLUSTERED,
    code   INT            NULL,
    name   NVARCHAR(100)  NULL,
    amount DECIMAL(10, 2) NULL
)""",
        f"""INSERT INTO [dbo].[ncci_table] (id, code, name, amount)
SELECT
    CAST(pk + 1 AS INT),
    CAST((pk + 1) % 100 AS INT),
    N'row' + CAST(pk + 1 AS NVARCHAR(10)),
    CAST((pk + 1) * 0.75 AS DECIMAL(10, 2))
FROM fkr__seed
WHERE pk < {_NCCI_ROWS}""",
        "CREATE NONCLUSTERED COLUMNSTORE INDEX ncci ON [dbo].[ncci_table] (code, amount)",
        # ledger_account
        """CREATE TABLE [dbo].[ledger_account] (
    id      INT            NOT NULL CONSTRAINT pk_ledger PRIMARY KEY CLUSTERED,
    name    NVARCHAR(100)  NULL,
    balance DECIMAL(10, 2) NULL
) WITH (LEDGER = ON (APPEND_ONLY = ON))""",
        """INSERT INTO [dbo].[ledger_account] (id, name, balance) VALUES
    (1, N'Alice', 1000.00),
    (2, N'Bob',    500.00),
    (3, N'Carol',  750.50)""",
        # graph_person / graph_follows
        "CREATE TABLE [dbo].[graph_person] (name NVARCHAR(100) NULL) AS NODE",
        "INSERT INTO [dbo].[graph_person] (name) VALUES (N'Alice'), (N'Bob'), (N'Carol')",
        "CREATE TABLE [dbo].[graph_follows] (since DATE NULL) AS EDGE",
        """INSERT INTO [dbo].[graph_follows] ($from_id, $to_id, since)
SELECT alice.$node_id, bob.$node_id, CAST('2020-01-01' AS DATE)
FROM [dbo].[graph_person] alice CROSS JOIN [dbo].[graph_person] bob
WHERE alice.name = N'Alice' AND bob.name = N'Bob'""",
        """INSERT INTO [dbo].[graph_follows] ($from_id, $to_id, since)
SELECT alice.$node_id, carol.$node_id, CAST('2021-06-01' AS DATE)
FROM [dbo].[graph_person] alice CROSS JOIN [dbo].[graph_person] carol
WHERE alice.name = N'Alice' AND carol.name = N'Carol'""",
        # long_text
        """CREATE TABLE [dbo].[long_text] (
    id            INT           NOT NULL CONSTRAINT pk_long_text PRIMARY KEY CLUSTERED,
    short_text    NVARCHAR(50)  NULL,
    long_varchar  VARCHAR(MAX)  NULL,
    long_nvarchar NVARCHAR(MAX) NULL,
    long_char     CHAR(500)     NULL
)""",
        "INSERT INTO [dbo].[long_text] (id, short_text, long_varchar, long_nvarchar, long_char)"
        " VALUES (1, N'min', REPLICATE('A', 500), REPLICATE(N'A', 500), REPLICATE('A', 500))",
        "INSERT INTO [dbo].[long_text] (id, short_text, long_varchar, long_nvarchar, long_char)"
        " VALUES (2, N'max', REPLICATE('Z', 500), REPLICATE(N'Z', 500), REPLICATE('Z', 500))",
        "INSERT INTO [dbo].[long_text] (id, short_text, long_varchar, long_nvarchar, long_char)"
        " VALUES (3, N'null', NULL, NULL, NULL)",
        # memory_oltp
        """CREATE TABLE [dbo].[memory_oltp] (
    id  INT           NOT NULL CONSTRAINT pk_memory_oltp PRIMARY KEY NONCLUSTERED,
    val NVARCHAR(100) NULL
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        "INSERT INTO [dbo].[memory_oltp] VALUES (1, N'in_memory_row_1')",
        "INSERT INTO [dbo].[memory_oltp] VALUES (2, N'in_memory_row_2')",
        "INSERT INTO [dbo].[memory_oltp] VALUES (3, N'in_memory_row_3')",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{CONTAINER_BAK}' WITH FORMAT, INIT",
    ]
    return stmts


def main() -> int:
    import argparse as _ap
    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_server_older_than(2022):
        return 0

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
