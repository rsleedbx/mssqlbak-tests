#!/usr/bin/env python3
"""Generate ``utf8_collation_full.bak`` — UTF-8 collation varchar columns (Gap G-1).

## Purpose

``varchar`` / ``char`` columns with a ``_UTF8`` collation (e.g.
``Latin1_General_100_CI_AS_SC_UTF8``) store **UTF-8 bytes** on the page —
not a single-byte code page.  SQL Server 2019 introduced UTF-8 collations.

A ``varchar`` decoder that applies the database collation's code page (e.g.
CP1252) to all varchar bytes will produce **mojibake** for any non-ASCII
content, silently corrupting strings.  UTF-8 collations are common in modern
databases.

This fixture is **SS2019+ only** — UTF-8 collations do not exist on SS2017.
Exclude from ``_ALL_VERSIONS_SUITE``; run with
``all-versions --suite utf8-collation --version 2019 --version 2022 --version 2025``.

## Schema and data

  - ``dbo.utf8_tbl``  — one VARCHAR(80) column with a UTF-8 collation
  - ``dbo.nvar_tbl``  — same strings in NVARCHAR(80) with the default collation
                        (control: always decodes correctly as UTF-16)

Rows inserted (id range 1 .. ROW_COUNT):

  | id | string              | bytes in UTF-8 | bytes in UTF-16 |
  |----|---------------------|----------------|-----------------|
  | 1  | hello               | 5 (ASCII)      | 10              |
  | 2  | café                | 5              | 8               |
  | 3  | 日本語              | 9              | 6               |
  | 4  | 😀                  | 4              | 4 (surrogate)   |
  | 5  | price: €100         | 12             | 22              |
  | 6  | (empty string)      | 0              | 0               |
  | 7  | NULL                | —              | —               |

## Exported constants (imported by the coverage test)

  - ``DB_NAME``       — database name
  - ``EXPECTED``      — ``dict[int, str | None]`` mapping id → expected string
  - ``ROW_COUNT``     — total rows (7)

Usage (preferred):
    python -m tools.fixture_run all-versions --suite utf8-collation \\
        --version 2019 --version 2022 --version 2025

Direct:
    python -m tools.make_utf8_collation_fixture
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
    _load_and_backup,
    fixture_credentials,
    skip_if_exists,
    skip_if_server_older_than,
    sqlcmd_base,
)

# ---------------------------------------------------------------------------
# Constants (imported by the coverage test)
# ---------------------------------------------------------------------------

DB_NAME = "Utf8CollationCoverage"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME}.sql"

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)

# Expected decoded Python strings keyed by id.
# None means the row was inserted as NULL.
EXPECTED: dict[int, str | None] = {
    1: "hello",
    2: "café",
    3: "日本語",
    4: "😀",
    5: "price: €100",
    6: "",
    7: None,
}

ROW_COUNT = len(EXPECTED)  # 7

OUT_PATH = FIXTURE_DIR / "utf8_collation_full.bak"


# ---------------------------------------------------------------------------
# SQL builder (pure function — no side effects)
# ---------------------------------------------------------------------------

def build_sql() -> str:
    """Return complete DDL + DML + BACKUP SQL.

    Requires SQL Server 2019+ (UTF-8 collations introduced in SS2019).

    Non-ASCII characters are expressed via NCHAR() to avoid any dependency on
    sqlcmd input-file encoding.  SQL Server converts the nvarchar expressions
    to UTF-8 bytes when storing into the UTF-8-collated varchar column.

    Surrogate-pair encoding for code points outside the BMP:
      U+1F600 (😀) = NCHAR(0xD83D) + NCHAR(0xDE00)
    """
    # Row (id, nvarchar_expr) for the INSERT.  NCHAR() avoids file-encoding issues.
    rows = [
        (1, "N'hello'"),
        (2, "N'caf' + NCHAR(0x00E9)"),                           # café
        (3, "NCHAR(0x65E5) + NCHAR(0x672C) + NCHAR(0x8A9E)"),    # 日本語
        (4, "NCHAR(0xD83D) + NCHAR(0xDE00)"),                    # 😀 (U+1F600)
        (5, "N'price: ' + NCHAR(0x20AC) + N'100'"),              # price: €100
        (6, "N''"),                                               # empty string
        (7, "NULL"),                                              # NULL
    ]
    insert_rows = ",\n    ".join(f"({id_}, {expr})" for id_, expr in rows)

    return f"""\
IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
  ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{DB_NAME}];
END;
GO
CREATE DATABASE [{DB_NAME}];
GO
USE [{DB_NAME}];
GO

-- Test table: VARCHAR with a UTF-8 collation.
-- The column stores UTF-8 bytes on the page, not a single-byte code page.
-- SQL Server 2019+ only — this CREATE TABLE will fail on SS2017.
CREATE TABLE dbo.utf8_tbl (
    id  INT         NOT NULL PRIMARY KEY CLUSTERED,
    s   VARCHAR(80) COLLATE Latin1_General_100_CI_AS_SC_UTF8 NULL
);
GO

-- Control table: same strings in NVARCHAR (UTF-16 LE, always correct).
CREATE TABLE dbo.nvar_tbl (
    id  INT          NOT NULL PRIMARY KEY CLUSTERED,
    s   NVARCHAR(80) NULL
);
GO

-- Insert rows.  NCHAR() calls are encoding-safe.
-- SQL Server converts nvarchar → UTF-8 bytes for the utf8_tbl column.
INSERT INTO dbo.utf8_tbl VALUES
    {insert_rows};
GO

INSERT INTO dbo.nvar_tbl VALUES
    {insert_rows};
GO

USE [master];
GO
BACKUP DATABASE [{DB_NAME}]
  TO DISK = N'{CONTAINER_BAK}'
  WITH FORMAT, INIT, COPY_ONLY;
GO
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate utf8_collation_full.bak — VARCHAR with UTF-8 collation "
            "(Gap G-1; SS2019+ only)."
        )
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing .bak",
    )
    args = parser.parse_args()

    if skip_if_server_older_than(2019):
        return 0

    out = OUT_PATH

    if skip_if_exists(out, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"seeding {ROW_COUNT} rows with UTF-8 collation varchar …")

    _load_and_backup(
        container,
        sqlcmd_base(user, password, container),
        build_sql(),
        CONTAINER_SQL,
    )
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
