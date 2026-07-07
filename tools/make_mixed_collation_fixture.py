#!/usr/bin/env python3
"""Generate ``mixed_collation_full.bak`` — per-column collation override fixture (Gap G-3).

## Purpose

Gap G-3 verifies that mssqlbak honours per-column collation overrides when
decoding ``char``/``varchar`` columns.  A decoder that applies the
database-level collation to all string columns will silently corrupt any column
whose per-column collation encodes bytes differently.

## Table schema

    CREATE TABLE collation_mix (
        id   INT NOT NULL PRIMARY KEY,
        lat  VARCHAR(40) COLLATE Latin1_General_CI_AS,   -- CP1252
        grk  VARCHAR(40) COLLATE Greek_CI_AS,            -- CP1253
        heb  VARCHAR(40) COLLATE Hebrew_CI_AS            -- CP1255
    )

Three rows are inserted:

    id=1  — ASCII-only; all three columns have the same bytes (0x41..0x7A range)
            and the same decoded string regardless of codec.  Sanity check.
    id=2  — Non-ASCII: each column contains a code-page-specific non-ASCII
            string whose bytes differ per codec:
              lat  → 'café'      (0x63 0x61 0x66 0xE9  in CP1252)
              grk  → 'ελλάδα'  (Greek letters in CP1253)
              heb  → 'שלום'      (Hebrew "Shalom" in CP1255)
    id=3  — NULL row: all three varchar columns are NULL.

Note: UTF-8 collation is intentionally excluded here — it requires SS2019+ and
is already covered by the G-1 ``utf8_collation_full.bak`` fixture.  This fixture
targets all SQL Server versions (2017+).

## Exported constants (imported by the coverage test)

    DB_NAME          — database name
    TABLE_NAME       — "collation_mix"
    ASCII_ID         — id of the ASCII row (1)
    NONASCII_ID      — id of the non-ASCII row (2)
    NULL_ID          — id of the all-NULL row (3)
    NONASCII_VALUES  — dict col_name → expected decoded string for id=2

Usage:
    python -m tools.fixture_run mixed-collation
    python -m tools.fixture_run all-versions --suite mixed-collation
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

DB_NAME = "MixedCollation"
TABLE_NAME = "collation_mix"

ASCII_ID = 1
NONASCII_ID = 2
NULL_ID = 3

# Expected decoded values for the non-ASCII row.
# These are the Python strings mssqlbak must return after applying the
# per-column collation to the raw on-disk bytes.
NONASCII_VALUES: dict[str, str] = {
    "lat": "caf\u00e9",          # CP1252: 'é' = 0xE9
    "grk": "\u03b5\u03bb\u03bb\u03ac\u03b4\u03b1",  # Greek: ελλάδα
    "heb": "\u05e9\u05dc\u05d5\u05dd",               # Hebrew: שלום
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "mixed_collation_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    """Return all statements for the G-3 mixed-collation fixture database."""
    return [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE [{TABLE_NAME}] (
    id   INT          NOT NULL CONSTRAINT pk_{TABLE_NAME} PRIMARY KEY CLUSTERED,
    lat  VARCHAR(40)  COLLATE Latin1_General_CI_AS NULL,
    grk  VARCHAR(40)  COLLATE Greek_CI_AS NULL,
    heb  VARCHAR(40)  COLLATE Hebrew_CI_AS NULL
)""",
        # Row 1: ASCII-only — same bytes in every code page.
        f"""INSERT INTO [{TABLE_NAME}] (id, lat, grk, heb) VALUES
    ({ASCII_ID}, 'hello', 'hello', 'hello')""",
        # Row 2: non-ASCII — code-page-specific bytes per column.
        # Use COLLATE in the value expression so SQL Server encodes each varchar
        # column in the column's own code page from a Unicode (N'') literal.
        f"""INSERT INTO [{TABLE_NAME}] (id, lat, grk, heb) VALUES
    (
        {NONASCII_ID},
        N'caf\u00e9'    COLLATE Latin1_General_CI_AS,
        N'\u03b5\u03bb\u03bb\u03ac\u03b4\u03b1' COLLATE Greek_CI_AS,
        N'\u05e9\u05dc\u05d5\u05dd' COLLATE Hebrew_CI_AS
    )""",
        # Row 3: all-NULL.
        f"INSERT INTO [{TABLE_NAME}] (id) VALUES ({NULL_ID})",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
