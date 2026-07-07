#!/usr/bin/env python3
"""Generate ``cci_binary_varbinary_compare_full.bak`` — F4 diagnostic fixture.

## Purpose (from docs/260619-1-varbinary-bak.md, §F4)

Places BINARY(8) and VARBINARY(8) in the same row group with identical inserted
values.  BINARY(8) is a known-working Format C type (Bug E3B aside for enc=3);
side-by-side byte comparison of the two column blobs at the same item_size=8
directly shows what VARBINARY adds or changes relative to BINARY.

Resolves mysteries M1 (pool entry encoding) and M2 (index encoding).

## Schema

    cci_binary_varbinary_compare (
        id   INT          NOT NULL,
        bin8 BINARY(8)    NULL,    -- known-baseline Format C layout
        vb8  VARBINARY(8) NULL,    -- VARBINARY variant with same values
    )

## Rows

    id=1  bin8=0x0000000000000001  vb8=0x0000000000000001  (LOW)
    id=2  bin8=0xFFFFFFFFFFFFFFFF  vb8=0xFFFFFFFFFFFFFFFF  (HIGH)
    id=3  bin8=NULL                vb8=NULL                (null sentinel)
    id=7..1203: bin8=CAST(n AS BINARY(8)), vb8=CAST(n AS VARBINARY(8))
               for n=1..1197 (1,197 filler rows)

Total: 1,200 rows — same as K-3 fixtures, ensuring a single compressed segment.

## Notes on expected bug behaviour

Both columns are in a regular CCI (not ARCHIVE), so:
  - bin8 → enc=3, Bug E3B fires (BINARY offset-table absent) → non-null rows
    return None in the current decoder.  Tests for bin8 values are xfail.
  - vb8  → enc=3, Bug K3B fires (sparse-NULL polarity inversion, 1 NULL in
    1,200 rows) → all rows return None.  Tests for vb8 values are xfail.

Despite both columns being buggy under the current decoder, this fixture
provides the raw binary blob for manual XPRESS inspection.

## Exported constants

    DB_NAME          — database name
    ROWS_PER_TABLE   — 1,200
    STRUCTURAL_IDS   — {"low": 1, "high": 2, "null": 3}
    FILLER_START     — 7
    FILLER_COUNT     — 1,197
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

DB_NAME = "CciBinaryVarbinaryCompare"

ROWS_PER_TABLE: int = 1_200
STRUCTURAL_IDS: dict[str, int] = {"low": 1, "high": 2, "null": 3}
FILLER_START: int = 7
FILLER_COUNT: int = ROWS_PER_TABLE - len(STRUCTURAL_IDS)  # 1,197

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)
OUT_PATH = FIXTURE_DIR / "cci_binary_varbinary_compare_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"
def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(FILLER_COUNT)
    stmts += [
        """CREATE TABLE cci_binary_varbinary_compare (
    id   INT          NOT NULL,
    bin8 BINARY(8)    NULL,
    vb8  VARBINARY(8) NULL
)""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_binary_varbinary_compare"
        " ON cci_binary_varbinary_compare",
        "INSERT INTO cci_binary_varbinary_compare (id, bin8, vb8)"
        " VALUES (1, 0x0000000000000001, 0x0000000000000001)",
        "INSERT INTO cci_binary_varbinary_compare (id, bin8, vb8)"
        " VALUES (2, 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF)",
        "INSERT INTO cci_binary_varbinary_compare (id, bin8, vb8) VALUES (3, NULL, NULL)",
        f"""INSERT INTO cci_binary_varbinary_compare (id, bin8, vb8)
SELECT pk + {FILLER_START} AS id,
       CAST(pk + 1 AS BINARY(8))    AS bin8,
       CAST(pk + 1 AS VARBINARY(8)) AS vb8
FROM fkr__seed
WHERE pk < {FILLER_COUNT}""",
        "ALTER INDEX cci_cci_binary_varbinary_compare ON cci_binary_varbinary_compare"
        " REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
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
