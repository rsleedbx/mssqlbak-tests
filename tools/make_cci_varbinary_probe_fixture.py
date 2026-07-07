#!/usr/bin/env python3
"""Generate ``cci_varbinary_probe_full.bak`` — F2, F3, F5 diagnostic fixtures.

Combines three complementary probes (from docs/260619-1-varbinary-bak.md) into
one .bak to minimise generation overhead.

## Tables

### cci_varbinary_maxwidth  (F2 — 1,200 rows)

**Purpose:** Determine whether `item_size` in the XPRESS marker tracks the
*observed value width* (all values are 16 bytes here) or the column's
`max_length` (also 16 for VARBINARY(16)).  This is a degenerate probe where
the two hypotheses predict the same answer, but it provides a 16-byte-wide pool
to compare against the existing 8-byte-wide `cci_varbinary` pool.

Schema: VARBINARY(16), all non-null values are exactly 16 bytes wide.

    id=1  LOW:  0x00000000000000000000000000000001
    id=2  HIGH: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    id=3  NULL
    id=7..1203: CAST(CAST(n AS BINARY(16)) AS VARBINARY(16))

### cci_varbinary_narrowmax  (F3 — 1,200 rows)

**Purpose:** Determine whether `item_size` follows `max_length` by narrowing the
column declaration to VARBINARY(4).  The current `_enc5_item_size` returns
`col.max_length` (4 here, 16 in existing fixture).  If the XPRESS marker
`item_size` is also 4, `max_length` drives slot width.  If `item_size` stays at
8, slot width is fixed for variable-binary regardless of `max_length`.

Schema: VARBINARY(4), sparse-NULL (1 in 1,200 rows).

    id=1  LOW:  0x01
    id=2  HIGH: 0xFFFFFFFF  (4 bytes = max_length)
    id=3  NULL
    id=7..1203: CAST(n AS VARBINARY(4))

### cci_varbinary_small_rowgroup  (F5 — 128 rows)

**Purpose:** Resolve M3 (pool/index boundary) by making the pool size known by
construction.  With 128 non-null rows and item_size=8, the theoretical layout:

    Pool  = 128 × 8 = 1,024 bytes
    Index = 128 × 2 = 256 bytes
    Total = 1,280 bytes (plus alignment padding)

No NULLs → K3B null-polarity inversion cannot fire.  The exact byte at which
the pool ends (1,024) is trivially detectable in the XPRESS-decompressed buffer.
Comparing with the existing 1,199-entry pool distinguishes inherent encoding
from pool-size artifact.

Schema: VARBINARY(16), 128 rows, no NULLs.

    id=1..128: CAST(n AS VARBINARY(16)) for n=1..128

## Exported constants

    DB_NAME                      — database name
    MAXWIDTH_ROWS                — 1,200
    MAXWIDTH_STRUCTURAL_IDS      — {"low": 1, "high": 2, "null": 3}
    NARROWMAX_ROWS               — 1,200
    NARROWMAX_STRUCTURAL_IDS     — {"low": 1, "high": 2, "null": 3}
    SMALLRG_ROWS                 — 128
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

DB_NAME = "CciVarbinaryProbe"

# F2 — maxwidth
MAXWIDTH_ROWS: int = 1_200
MAXWIDTH_STRUCTURAL_IDS: dict[str, int] = {"low": 1, "high": 2, "null": 3}
_MAXWIDTH_FILLER_START: int = 7
_MAXWIDTH_FILLER_COUNT: int = MAXWIDTH_ROWS - len(MAXWIDTH_STRUCTURAL_IDS)  # 1,197

# F3 — narrowmax
NARROWMAX_ROWS: int = 1_200
NARROWMAX_STRUCTURAL_IDS: dict[str, int] = {"low": 1, "high": 2, "null": 3}
_NARROWMAX_FILLER_START: int = 7
_NARROWMAX_FILLER_COUNT: int = NARROWMAX_ROWS - len(NARROWMAX_STRUCTURAL_IDS)  # 1,197

# F5 — small rowgroup
SMALLRG_ROWS: int = 128

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)
OUT_PATH = FIXTURE_DIR / "cci_varbinary_probe_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"
def _maxwidth_stmts() -> list[str]:
    return [
        """CREATE TABLE cci_varbinary_maxwidth (
    id   INT            NOT NULL,
    val  VARBINARY(16)  NULL
)""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_varbinary_maxwidth ON cci_varbinary_maxwidth",
        "INSERT INTO cci_varbinary_maxwidth (id, val)"
        " VALUES (1, 0x00000000000000000000000000000001)",
        "INSERT INTO cci_varbinary_maxwidth (id, val)"
        " VALUES (2, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)",
        "INSERT INTO cci_varbinary_maxwidth (id, val) VALUES (3, NULL)",
        f"""INSERT INTO cci_varbinary_maxwidth (id, val)
SELECT pk + {_MAXWIDTH_FILLER_START} AS id,
       CAST(CAST(pk + 1 AS VARBINARY(4)) AS VARBINARY(16)) AS val
FROM fkr__seed
WHERE pk < {_MAXWIDTH_FILLER_COUNT}""",
        "ALTER INDEX cci_cci_varbinary_maxwidth ON cci_varbinary_maxwidth"
        " REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def _narrowmax_stmts() -> list[str]:
    return [
        """CREATE TABLE cci_varbinary_narrowmax (
    id   INT           NOT NULL,
    val  VARBINARY(4)  NULL
)""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_varbinary_narrowmax ON cci_varbinary_narrowmax",
        "INSERT INTO cci_varbinary_narrowmax (id, val) VALUES (1, 0x01)",
        "INSERT INTO cci_varbinary_narrowmax (id, val) VALUES (2, 0xFFFFFFFF)",
        "INSERT INTO cci_varbinary_narrowmax (id, val) VALUES (3, NULL)",
        f"""INSERT INTO cci_varbinary_narrowmax (id, val)
SELECT pk + {_NARROWMAX_FILLER_START} AS id,
       CAST(pk + 1 AS VARBINARY(4))  AS val
FROM fkr__seed
WHERE pk < {_NARROWMAX_FILLER_COUNT}""",
        "ALTER INDEX cci_cci_varbinary_narrowmax ON cci_varbinary_narrowmax"
        " REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def _smallrg_stmts() -> list[str]:
    return [
        """CREATE TABLE cci_varbinary_small_rowgroup (
    id   INT            NOT NULL,
    val  VARBINARY(16)  NULL
)""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_cci_varbinary_small_rowgroup"
        " ON cci_varbinary_small_rowgroup",
        f"""INSERT INTO cci_varbinary_small_rowgroup (id, val)
SELECT pk + 1                        AS id,
       CAST(pk + 1 AS VARBINARY(16)) AS val
FROM fkr__seed
WHERE pk < {SMALLRG_ROWS}""",
        "ALTER INDEX cci_cci_varbinary_small_rowgroup ON cci_varbinary_small_rowgroup"
        " REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
    ]


def build_stmts() -> list[str]:
    max_rows = max(_MAXWIDTH_FILLER_COUNT, _NARROWMAX_FILLER_COUNT, SMALLRG_ROWS)
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(max_rows)
    stmts += _maxwidth_stmts()
    stmts += _narrowmax_stmts()
    stmts += _smallrg_stmts()
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
