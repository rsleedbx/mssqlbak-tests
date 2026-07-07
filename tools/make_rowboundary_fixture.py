#!/usr/bin/env python3
"""Generate ``rowboundary_full.bak`` — row-size and LOB-page boundary coverage.

## Purpose

Exercises three critical byte-count boundaries in the SQL Server storage engine
that the mssqlbak parser must handle correctly:

  rb_overflow  — in-row vs ROW_OVERFLOW_DATA boundary (≈8060 bytes)
  rb_lob       — LOB single-page vs two-page boundary (8096 bytes data/page)
  rb_page_fill — data page slot-array capacity (72 rows for CHAR(100) rows)

### rb_overflow — the 8060-byte in-row boundary (Bug B-3)

SQL Server stores variable-length column data in-row if the total row fits within
8060 bytes; otherwise it moves the variable columns to a separate
ROW_OVERFLOW_DATA allocation unit and leaves a 24-byte pointer in-row.

Table schema::

    rb_overflow (
        id  INT              NOT NULL,
        a   VARCHAR(8000)    NOT NULL,   -- fixed at 4000 bytes
        b   VARCHAR(8000)    NOT NULL,   -- varies 4043–4047 bytes
    )

Row overhead = 17 bytes (empirically validated: 2 status + 2 fixed_end + 4 id
                          + 2 col_count + 1 null_bits + 2 n_var_cols + 2×2 var_offsets).
In-row limit: LEN(a)+LEN(b) ≤ 8060 − 17 = 8043 bytes.
SQL Server overflows b (the last variable column) and keeps a in-row.

Rows (id → total variable bytes → expected placement):
    1 → 4000+4039 = 8039  → in-row (−4 from limit)
    2 → 4000+4040 = 8040  → in-row (−3)
    3 → 4000+4041 = 8041  → in-row (−2)
    4 → 4000+4042 = 8042  → in-row (−1)
    5 → 4000+4043 = 8043  → in-row (at limit)
    6 → 4000+4044 = 8044  → ROW_OVERFLOW (+1) ← Bug B-3 triggers
    7 → 4000+4045 = 8045  → ROW_OVERFLOW (+2) ← Bug B-3 triggers
    8 → 4000+4046 = 8046  → ROW_OVERFLOW (+3) ← Bug B-3 triggers
    9 → 4000+4047 = 8047  → ROW_OVERFLOW (+4) ← Bug B-3 triggers

Bug B-3: the mssqlbak parser reads the 24-byte ROW_OVERFLOW pointer as if it
were the column value, returning garbage instead of following the pointer to the
overflow page.  Tests for rows 6–9 are marked xfail(strict=False).
Note: column a is always decoded correctly (stays in-row even when b overflows).

### rb_lob — the 8096-byte LOB-page boundary

LOB pages (TEXT_MIX allocation) have a 96-byte header, leaving 8096 bytes of
data capacity per page.  A VARBINARY(MAX) value that fits in one LOB page is
stitched from a single blob; a larger value requires a multi-page chain.

Table schema::

    rb_lob (
        id   INT              NOT NULL,
        val  VARBINARY(MAX)   NULL,
    )

Rows (id → blob size in bytes):
    1 → 8094  (one LOB page, 2 bytes short of full)
    2 → 8095  (one LOB page, 1 byte short of full)
    3 → 8096  (exactly one LOB page)
    4 → 8097  (two LOB pages, +1)
    5 → 8098  (two LOB pages, +2)

All of these should decode correctly with the existing LOB stitcher.  If any
test fails it reveals a new parser bug at the LOB page boundary.

### rb_page_fill — data page slot-array capacity

Each 8192-byte SQL Server data page has a 96-byte header plus a 2-byte slot-
array entry per row.  For a fixed-width row of id INT + val CHAR(100):

    row size  = 2 (status) + 2 (fixed_end) + 4 (id) + 100 (val) + 1 (null_bitmap)
              = 109 bytes
    slot entry = 2 bytes
    capacity   = floor(8096 / (109 + 2)) = 72 rows per page

Table schema::

    rb_page_fill (
        id   INT       NOT NULL,
        val  CHAR(100) NOT NULL,
    )

Rows: 216 rows (3 complete pages of 72 rows each).

## Exported constants

    DB_NAME          — database name ("RowBoundary")
    ROW_OVERHEAD     — estimated fixed overhead for rb_overflow rows (15)
    VAR_LIMIT        — in-row variable-data limit for rb_overflow (8045)
    OVERFLOW_ROWS    — frozenset of rb_overflow ids that trigger ROW_OVERFLOW
    LOB_PAGE_BYTES   — LOB page data capacity (8096)
    LOB_ROW_SIZES    — mapping id → blob size for rb_lob
    PAGE_FILL_ROWS   — total row count for rb_page_fill (216)
    ROWS_PER_PAGE    — estimated rows per page for rb_page_fill (72)
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

DB_NAME = "RowBoundary"

# ---------------------------------------------------------------------------
# rb_overflow constants
# ---------------------------------------------------------------------------

# Row overhead — empirically validated against SQL Server 2017/2019/2022/2025.
#
# The null-bitmap section has a 2-byte COLUMN COUNT prefix before the actual
# bitmap bits (unlike what many docs suggest), giving:
#   status(2) + fixed_end(2) + id(4) + col_count(2) + null_bits(1) + n_var(2)
#   + var_offsets(2×2) = 17 bytes
#
# Empirical proof: with a=4000 and b=4043 (total 8043) the row stays in-row;
# with b=4044 (total 8044) SQL Server overflows column b.  8060 − 8043 = 17.
ROW_OVERHEAD: int = 17

# Maximum total variable-length bytes that keep the row in-row
VAR_LIMIT: int = 8060 - ROW_OVERHEAD  # 8043

# id → (a_len, b_len) for rb_overflow rows.
# a is fixed at 4000 bytes; b varies to bracket the overflow boundary.
# Overflow fires when a+b > VAR_LIMIT (8043).
# SQL Server overflows b (the last/longest variable column) and keeps a in-row.
_OVERFLOW_ROW_DEFS: dict[int, tuple[int, int]] = {
    1: (4000, 4039),  # total 8039 — in-row (−4 from limit)
    2: (4000, 4040),  # total 8040 — in-row (−3)
    3: (4000, 4041),  # total 8041 — in-row (−2)
    4: (4000, 4042),  # total 8042 — in-row (−1)
    5: (4000, 4043),  # total 8043 — in-row (at limit)
    6: (4000, 4044),  # total 8044 — ROW_OVERFLOW (+1)
    7: (4000, 4045),  # total 8045 — ROW_OVERFLOW (+2)
    8: (4000, 4046),  # total 8046 — ROW_OVERFLOW (+3)
    9: (4000, 4047),  # total 8047 — ROW_OVERFLOW (+4)
}

# Rows expected to trigger ROW_OVERFLOW (a+b > VAR_LIMIT)
OVERFLOW_ROWS: frozenset[int] = frozenset(
    rid for rid, (a, b) in _OVERFLOW_ROW_DEFS.items() if a + b > VAR_LIMIT
)

# ---------------------------------------------------------------------------
# rb_lob constants
# ---------------------------------------------------------------------------

# LOB page data capacity: 8192 - 96 (header) = 8096 bytes
LOB_PAGE_BYTES: int = 8096

# id → blob size in bytes
LOB_ROW_SIZES: dict[int, int] = {
    1: 8094,
    2: 8095,
    3: 8096,
    4: 8097,
    5: 8098,
}

# ---------------------------------------------------------------------------
# rb_page_fill constants
# ---------------------------------------------------------------------------

# Row size for id INT + val CHAR(100) fixed-width row (no variable section)
#   2 (status) + 2 (fixed_end) + 4 (id) + 100 (val) + 1 (null_bitmap) = 109
_PAGE_FILL_ROW_BYTES: int = 109

# Slot-array entry: 2 bytes per row
# Rows per 8192-byte page (96-byte header)
ROWS_PER_PAGE: int = (8192 - 96) // (_PAGE_FILL_ROW_BYTES + 2)  # 72

# Total rows = 3 full pages
PAGE_FILL_ROWS: int = ROWS_PER_PAGE * 3  # 216

# ---------------------------------------------------------------------------
# Internal paths
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)
OUT_PATH = FIXTURE_DIR / "rowboundary_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"

# ---------------------------------------------------------------------------
# Statement generators
# ---------------------------------------------------------------------------


def _rb_overflow_sql() -> str:
    insert_lines = "\n".join(
        f"INSERT INTO rb_overflow (id, a, b) VALUES "
        f"({rid}, REPLICATE('A', {a}), REPLICATE('B', {b}));"
        for rid, (a, b) in _OVERFLOW_ROW_DEFS.items()
    )
    return f"""\
CREATE TABLE rb_overflow (
    id  INT           NOT NULL,
    a   VARCHAR(8000) NOT NULL,
    b   VARCHAR(8000) NOT NULL
);
GO
{insert_lines}
GO
"""


def _rb_lob_sql() -> str:
    insert_lines = "\n".join(
        f"INSERT INTO rb_lob (id, val) VALUES ("
        f"{rid}, CAST(REPLICATE(CAST('A' AS VARCHAR(MAX)), {sz}) AS VARBINARY(MAX)));"
        for rid, sz in LOB_ROW_SIZES.items()
    )
    return f"""\
CREATE TABLE rb_lob (
    id   INT            NOT NULL,
    val  VARBINARY(MAX) NULL
);
GO
{insert_lines}
GO
"""


def _rb_page_fill_sql() -> str:
    return f"""\
CREATE TABLE rb_page_fill (
    id   INT       NOT NULL,
    val  CHAR(100) NOT NULL
);
GO
INSERT INTO rb_page_fill (id, val)
SELECT pk + 1                AS id,
       REPLICATE('X', 100)  AS val
FROM fkr__seed
WHERE pk < {PAGE_FILL_ROWS};
GO
"""


def build_stmts() -> list[str]:
    overflow_stmts = _split_go(_rb_overflow_sql())
    lob_stmts = _split_go(_rb_lob_sql())
    page_fill_stmts = _split_go(_rb_page_fill_sql())
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(PAGE_FILL_ROWS)
    stmts += overflow_stmts + lob_stmts + page_fill_stmts
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def _split_go(sql: str) -> list[str]:
    """Split a GO-delimited SQL string into a list of non-empty statements."""
    return [s.strip() for s in sql.split("\nGO\n") if s.strip()]


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
