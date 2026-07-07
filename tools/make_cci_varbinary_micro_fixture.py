#!/usr/bin/env python3
"""Generate ``cci_varbinary_micro_full.bak`` — F1 diagnostic fixture.

## Purpose (from docs/260619-1-varbinary-bak.md, §F1)

Makes the XPRESS-decompressed Format C blob for VARBINARY(16) manually
inspectable by using 7 hand-chosen values whose pool entries and index slots
can be traced byte-by-byte.  Resolves mysteries M1 (pool entry encoding),
M2 (index encoding), and M3 (pool/index boundary).

## Tables

### cci_varbinary_micro  (7 rows — primary diagnostic)

    id=1  val=0x01                                  1-byte value  (LOW)
    id=2  val=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF    16-byte value (HIGH = all-0xFF)
    id=3  val=NULL                                  null sentinel
    id=4  val=0x0102                                2-byte value
    id=5  val=0x0201                                2-byte value, reversed byte order
    id=6  val=0xABCDEF                              3-byte value, odd width
    id=7  val=0x0000000000000001                    8-byte value = item_size (M1 probe)

With only 6 non-null entries:
  - Pool ≤ 48 bytes → M3 (straddling) cannot occur at this scale.
  - Comparing id=4 and id=5 (same length, different bytes) directly probes M2.
  - Comparing id=1 (1-byte), id=4/5 (2-byte), id=6 (3-byte), id=7 (8-byte)
    probes M1 (how varying-width values are packed into pool slots).

### cci_varbinary_micro_nullonly  (21 rows — null sentinel isolation)

    id=1  val=0x01  (only non-null row)
    id=2..21  val=NULL  (20 nulls)

Isolates the null-sentinel encoding in the index without pool interference from
many distinct values.

### cci_varbinary_micro_1byte  (20 rows — pure 1-byte pool)

    id=1..20  val=CAST(n AS VARBINARY(16))  for n=1..20

All values fit in 1 byte (n ≤ 255).  No NULLs — K3B null-polarity inversion
cannot fire.  Provides a clean 20-entry pool of 1-byte values to probe M1.

## Exported constants

    DB_NAME                 — database name
    MICRO_ROWS              — dict id → (hex_literal, bytes | None)
    NULLONLY_NON_NULL_ID    — id of the single non-null row in nullonly table
    NULLONLY_NULL_IDS       — frozenset of null row ids in nullonly table
    ONEBYTE_ROWS            — number of rows in 1byte table
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
    seed_sql,
)

DB_NAME = "CciVarbinaryMicro"

# ---------------------------------------------------------------------------
# Exported constants for tests
# ---------------------------------------------------------------------------

# id → (sql_hex_literal, expected_bytes_or_None)
MICRO_ROWS: dict[int, tuple[str, bytes | None]] = {
    1: ("0x01",                                   b"\x01"),
    2: ("0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",      b"\xff" * 16),
    3: ("NULL",                                    None),
    4: ("0x0102",                                  b"\x01\x02"),
    5: ("0x0201",                                  b"\x02\x01"),
    6: ("0xABCDEF",                                b"\xab\xcd\xef"),
    7: ("0x0000000000000001",                      b"\x00\x00\x00\x00\x00\x00\x00\x01"),
}

NULLONLY_NON_NULL_ID: int = 1
NULLONLY_NULL_IDS: frozenset[int] = frozenset(range(2, 22))  # id 2..21

ONEBYTE_ROWS: int = 20

# ---------------------------------------------------------------------------
# Internal paths
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)
OUT_PATH = FIXTURE_DIR / "cci_varbinary_micro_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"
# ---------------------------------------------------------------------------
# Statement builders
# ---------------------------------------------------------------------------


def _micro_stmts() -> list[str]:
    inserts = [
        f"INSERT INTO cci_varbinary_micro (id, val) VALUES ({rid}, {lit})"
        for rid, (lit, _) in MICRO_ROWS.items()
    ]
    return [
        "CREATE TABLE cci_varbinary_micro (id INT NOT NULL, val VARBINARY(16) NULL)",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_varbinary_micro ON cci_varbinary_micro",
        *inserts,
        "ALTER INDEX cci_cci_varbinary_micro ON cci_varbinary_micro"
        " REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def _nullonly_stmts() -> list[str]:
    null_inserts = [
        f"INSERT INTO cci_varbinary_micro_nullonly (id, val) VALUES ({rid}, NULL)"
        for rid in sorted(NULLONLY_NULL_IDS)
    ]
    return [
        "CREATE TABLE cci_varbinary_micro_nullonly (id INT NOT NULL, val VARBINARY(16) NULL)",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_varbinary_micro_nullonly"
        " ON cci_varbinary_micro_nullonly",
        f"INSERT INTO cci_varbinary_micro_nullonly (id, val) VALUES ({NULLONLY_NON_NULL_ID}, 0x01)",
        *null_inserts,
        "ALTER INDEX cci_cci_varbinary_micro_nullonly ON cci_varbinary_micro_nullonly"
        " REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def _onebyte_stmts() -> list[str]:
    return [
        "CREATE TABLE cci_varbinary_micro_1byte (id INT NOT NULL, val VARBINARY(16) NULL)",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_varbinary_micro_1byte"
        " ON cci_varbinary_micro_1byte",
        f"""INSERT INTO cci_varbinary_micro_1byte (id, val)
SELECT pk + 1                        AS id,
       CAST(pk + 1 AS VARBINARY(16)) AS val
FROM fkr__seed
WHERE pk < {ONEBYTE_ROWS}""",
        "ALTER INDEX cci_cci_varbinary_micro_1byte ON cci_varbinary_micro_1byte"
        " REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(ONEBYTE_ROWS)
    stmts += _micro_stmts()
    stmts += _nullonly_stmts()
    stmts += _onebyte_stmts()
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if OUT_PATH.exists() and not args.force:
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
