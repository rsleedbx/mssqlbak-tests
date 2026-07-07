#!/usr/bin/env python3
"""Generate ``cci_extended_full.bak`` — targeted CCI bug-trigger tables.

## Purpose

This fixture deliberately targets five scenarios identified by reasoning about
the root causes of Bugs E3B, K3A, K3B, and the E3C/K3B interaction.  Each
table is designed to answer a specific open question:

  cci_int          — Does Bug K3B (null polarity inversion) affect enc=2 numeric
                     types?  BIT is enc=2 and fails; INT is also enc=2.  If the
                     null reader is shared, INT should also return all None with
                     sparse-NULL distribution.

  cci_varchar50    — VARCHAR(50) non-max is an entirely untested type family in
                     CCI compressed segments (the type matrix only has
                     varbinary_max / varchar_max).  With sparse-NULL, does it show
                     Bug K3B like varbinary(16) does?

  cci_char10_varied — Bug K3A fires for CHAR(20) with ≥26 distinct values.  Is
                     the bug width-specific (only CHAR(20)) or does it also affect
                     CHAR(10) with ≥26 distinct values?

  cci_binary4      — Bug E3B (no offset table for fixed-width binary) is confirmed
                     for BINARY(8) and BINARY(16).  Does it also fire for BINARY(4)?
                     The root cause (no offset table) should be width-independent.

  cci_nvarchar50_sparse — Bug E3C misdecodes the NULL row as '' in a dense-NULL
                     segment.  With sparse-NULL (1 NULL in 1,200 rows), does the
                     same type instead exhibit Bug K3B (null polarity inversion),
                     masking E3C?

## Row layout (same as K-3)

Each table:

    id   INT NOT NULL
    val  <TYPE> NULL

Rows:
    id=1  — low  structural value   (known reference)
    id=2  — high structural value   (known reference)
    id=3  — NULL sentinel           (known reference)
    id=7..1,203  — 1,197 non-null varied filler rows

Total: 1,200 rows.  All flushed to a compressed segment via REORGANIZE.

## Exported constants (imported by the coverage test)

  DB_NAME          — database name
  ROWS_PER_TABLE   — 1,200
  STRUCTURAL_IDS   — {"low": 1, "high": 2, "null": 3}
  TABLE_DEFS       — list[TableDef]
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
)

DB_NAME = "CciExtended"

_STRUCTURAL_ROWS = 3
_FILLER_ROWS = 1_197
ROWS_PER_TABLE = _STRUCTURAL_ROWS + _FILLER_ROWS  # 1,200

_FILLER_START_ID = 7

STRUCTURAL_IDS: dict[str, int] = {"low": 1, "high": 2, "null": 3}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_extended_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

@dataclass(frozen=True)
class TableDef:
    name: str
    sql_type: str
    low: Any
    high: Any
    low_sql: str
    high_sql: str
    filler_expr: str
    # Human-readable hypothesis for what bug we expect to trigger (or None if likely passes)
    hypothesis: str


TABLE_DEFS: list[TableDef] = [
    # ------------------------------------------------------------------
    # cci_int — INT, sparse-NULL (1 NULL in 1,200 rows)
    # Hypothesis: K3B null-polarity inversion affects enc=2 numeric types
    # just as it affects enc=2 BIT.  If INT returns all None, K3B is
    # confirmed as a null-reader bug shared across enc=2 and enc=3.
    # Filler: sequential ints starting at 10_000 (far from structural values)
    # ------------------------------------------------------------------
    TableDef(
        name="cci_int",
        sql_type="INT",
        low=1,
        high=9_999_999,
        low_sql="1",
        high_sql="9999999",
        filler_expr="n + 10000",
        hypothesis=(
            "Bug K3B propagates to enc=2 INT: all rows return None with sparse-NULL. "
            "Same null reader as BIT (enc=2), which failed in K-3."
        ),
    ),
    # ------------------------------------------------------------------
    # cci_varchar50 — VARCHAR(50), sparse-NULL
    # Hypothesis: K3B null-polarity bug affects VARCHAR(50) just as it
    # affects VARBINARY(16).  VARCHAR(50) is an untested type family in
    # CCI compressed segments (type matrix only has varchar_max).
    # Filler: 25 distinct 50-char strings cycling A-Y (not Z = high)
    # ------------------------------------------------------------------
    TableDef(
        name="cci_varchar50",
        sql_type="VARCHAR(50)",
        low="L" * 50,
        high="Z" * 50,
        low_sql="'" + "L" * 50 + "'",
        high_sql="'" + "Z" * 50 + "'",
        filler_expr="REPLICATE(CHAR(65 + ((n - 1) % 25)), 50)",
        hypothesis=(
            "Bug K3B propagates to VARCHAR(50): all rows return None with sparse-NULL. "
            "Also tests first compressed-segment coverage for non-max varchar family."
        ),
    ),
    # ------------------------------------------------------------------
    # cci_char10_varied — CHAR(10), 26+ distinct values, sparse-NULL
    # Hypothesis: K3A fires for CHAR(10) with ≥26 distinct values, same
    # as it does for CHAR(20).  If so, the bug is dictionary-size-dependent
    # rather than column-width-dependent.
    # Structural values use digits (0-9) to avoid overlap with A-Z fillers.
    # ------------------------------------------------------------------
    TableDef(
        name="cci_char10_varied",
        sql_type="CHAR(10)",
        low="0" * 10,
        high="9" * 10,
        low_sql="'0000000000'",
        high_sql="'9999999999'",
        filler_expr="REPLICATE(CHAR(65 + ((n - 1) % 26)), 10)",
        hypothesis=(
            "Bug K3A fires for CHAR(10) with ≥26 distinct values: structural rows "
            "return '' instead of the expected 10-char string."
        ),
    ),
    # ------------------------------------------------------------------
    # cci_binary4 — BINARY(4), sparse-NULL
    # Hypothesis: Bug E3B (no offset table for fixed-width binary) is
    # width-independent.  BINARY(4) should fail identically to BINARY(8)
    # and BINARY(16) — all non-null rows return None.
    # ------------------------------------------------------------------
    TableDef(
        name="cci_binary4",
        sql_type="BINARY(4)",
        low=b"\x00\x00\x00\x01",
        high=b"\xff\xff\xff\xff",
        low_sql="0x00000001",
        high_sql="0xFFFFFFFF",
        filler_expr="CAST(n AS BINARY(4))",
        hypothesis=(
            "Bug E3B is width-independent: BINARY(4) has no offset table just like "
            "BINARY(8) and BINARY(16); all non-null rows return None."
        ),
    ),
    # ------------------------------------------------------------------
    # cci_nvarchar50_sparse — NVARCHAR(50), sparse-NULL
    # Hypothesis: Bug E3C (dense-NULL compact RLE misdecodes null as '')
    # may be REPLACED by Bug K3B (null polarity inversion) when the null
    # distribution is sparse rather than dense.  With 1 NULL in 1,200 rows,
    # the null vector format likely switches from compact-RLE to sparse;
    # K3B then inverts polarity and all rows appear as None.
    # ------------------------------------------------------------------
    TableDef(
        name="cci_nvarchar50_sparse",
        sql_type="NVARCHAR(50)",
        low="L" * 50,
        high="Z" * 50,
        low_sql="N'" + "L" * 50 + "'",
        high_sql="N'" + "Z" * 50 + "'",
        filler_expr="REPLICATE(NCHAR(65 + ((n - 1) % 25)), 10)",
        hypothesis=(
            "Bug K3B may mask E3C for NVARCHAR(50) with sparse-NULL: all rows "
            "return None instead of the E3C symptom (null row returns '')."
        ),
    ),
]


def _table_stmts(td: TableDef) -> list[str]:
    tbl = td.name
    cci = f"cci_{tbl}"
    filler_count = _FILLER_ROWS
    filler_start = _FILLER_START_ID

    return [
        f"CREATE TABLE {tbl} (id INT NOT NULL, val {td.sql_type} NULL)",
        f"CREATE CLUSTERED COLUMNSTORE INDEX {cci} ON {tbl}",
        f"INSERT INTO {tbl} (id, val) VALUES (1, {td.low_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (2, {td.high_sql})",
        f"INSERT INTO {tbl} (id, val) VALUES (3, NULL)",
        f"INSERT INTO {tbl} (id, val)"
        f" SELECT pk + {filler_start} AS id, {td.filler_expr} AS val"
        f" FROM (SELECT pk, pk + 1 AS n FROM fkr__seed WHERE pk < {filler_count}) AS _f",
        f"ALTER INDEX {cci} ON {tbl} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
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
    stmts += seed_sql(_FILLER_ROWS)
    for td in TABLE_DEFS:
        stmts += _table_stmts(td)
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


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
