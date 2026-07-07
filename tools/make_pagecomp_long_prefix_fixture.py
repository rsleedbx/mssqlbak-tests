#!/usr/bin/env python3
"""Generate ``pagecomp_long_prefix_full.bak`` — PAGE-compressed nvarchar with
an anchor prefix ≥ 128 bytes.

## Purpose

SQL Server's PAGE-compression prefix encoder stores the prefix length of each
row's column value relative to the page anchor using:

  - A **single byte** ``[plen]`` when plen < 128.
  - A **two-byte** ``[0x80][plen]`` extended form when plen ≥ 128.

The Rust ``PageCI::expand_prefix`` (``page_compress.rs``) initially only
handled the single-byte form.  When a PAGE-compressed NVARCHAR column had
≥ 128 bytes of shared prefix between rows on the same page (e.g. 65 ASCII
characters = 130 UTF-16LE bytes), the extended ``0x80 <len>`` plen byte was
misread as a literal 0x80 prefix length, and the real length byte was
inadvertently included in the expanded value, corrupting the output.  The fix
was to detect ``entry[0] == 0x80`` and consume the next byte as the actual
plen, mirroring Python's ``_expand_prefix`` in ``mssqlbak/rowcompress.py``.

This fixture exercises exactly that path:

  - A PAGE-compressed clustered rowstore.
  - An NVARCHAR(400) column whose rows share a 70-character ASCII prefix
    (70 × 2 = 140 UTF-16LE bytes > 128) so SQL Server emits the extended plen
    form in the CI prefix array.
  - Each row has a unique 3–15 character suffix so the anchor/prefix expansion
    is required to reconstruct the full value.

A correct round-trip produces the exact expected strings for every row.  Before
the fix, rows with the long prefix would decode to corrupted values containing
a stray ``0x82``/``0x84``/… byte (the literal plen byte embedded in the
output).

## Table schema

    CREATE TABLE dbo.long_prefix_probe (
        id    INT            NOT NULL PRIMARY KEY CLUSTERED,
        descr NVARCHAR(400)  NULL
    ) WITH (DATA_COMPRESSION = PAGE)

## Row count

100 rows — enough to force PAGE compression to engage and emit CI anchor
structures, while keeping the fixture tiny.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``     — database name
  - ``TABLE``       — table name
  - ``SHARED_PREFIX`` — the 70-character ASCII prefix shared by all rows
  - ``EXPECTED``    — dict mapping id → expected Python str
  - ``ROW_COUNT``   — total rows inserted

Usage::

    python -m tools.fixture_run pagecomp-long-prefix
    python -m tools.fixture_run all-versions --suite pagecomp-long-prefix
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

DB_NAME = "PageCompLongPrefix"
TABLE = "long_prefix_probe"

REPO_ROOT = Path(__file__).resolve().parent.parent
_raw_fixture_dir = os.environ.get("FIXTURE_DIR", "")
if _raw_fixture_dir:
    _fd = Path(_raw_fixture_dir)
    FIXTURE_DIR = _fd if _fd.is_absolute() else (REPO_ROOT / _fd).resolve()
else:
    FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures_2022"

CONTAINER_BAK = f"/tmp/{DB_NAME.lower()}_full.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME.lower()}.sql"

# 70-character ASCII prefix → 140 UTF-16LE bytes, triggering the extended
# 0x80 <len> plen form in PAGE-compression CI prefix records.
SHARED_PREFIX = "Product description: digital camera compact model series X100 version "

ROW_COUNT = 100

# Unique suffixes for each row — short enough that the shared prefix dominates.
_SUFFIXES = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
    "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
    "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9",
    "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9",
    "3.0", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9",
    "rev1", "rev2", "rev3", "rev4", "rev5", "rev6", "rev7", "rev8", "rev9", "rev10",
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa",
    "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon",
    "v1.0", "v1.1", "v1.2", "v1.3", "v1.4", "v1.5", "v1.6", "v1.7", "v1.8", "v1.9",
    "w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10",
]

EXPECTED: dict[int, str] = {
    i + 1: SHARED_PREFIX + _SUFFIXES[i]
    for i in range(ROW_COUNT)
}

assert len(SHARED_PREFIX) == 70, f"prefix length must be 70, got {len(SHARED_PREFIX)}"
assert len(EXPECTED) == ROW_COUNT


def build_sql() -> str:
    rows = ", ".join(
        f"({row_id}, N'{val}')" for row_id, val in EXPECTED.items()
    )
    return f"""
USE [master];
GO

IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}];
END;
GO

CREATE DATABASE [{DB_NAME}];
GO

USE [{DB_NAME}];
GO

-- PAGE-compressed clustered rowstore with a long shared nvarchar prefix.
-- 70-char ASCII prefix × 2 = 140 UTF-16LE bytes > 128, forcing the extended
-- 0x80 <len> plen form in PAGE-compression CI anchor prefix records.
CREATE TABLE dbo.{TABLE} (
    id    INT           NOT NULL,
    descr NVARCHAR(400) NOT NULL,
    CONSTRAINT pk_{TABLE} PRIMARY KEY CLUSTERED (id)
) WITH (DATA_COMPRESSION = PAGE);
GO

INSERT INTO dbo.{TABLE} (id, descr)
VALUES {rows};
GO

-- Force (re)compression so every leaf page carries a CI structure.
ALTER INDEX ALL ON dbo.{TABLE} REBUILD WITH (DATA_COMPRESSION = PAGE);
GO

USE [master];
GO
BACKUP DATABASE [{DB_NAME}]
    TO DISK = N'{CONTAINER_BAK}'
    WITH FORMAT, INIT, COPY_ONLY;
GO
"""


def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    out = FIXTURE_DIR / "pagecomp_long_prefix_full.bak"
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
