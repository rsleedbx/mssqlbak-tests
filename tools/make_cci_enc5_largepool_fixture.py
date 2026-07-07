#!/usr/bin/env python3
"""Generate ``cci_enc5_largepool_full.bak`` — regular-CCI enc=5 CHAR with >64 KB pool.

## Purpose (discriminating fixture for the enc=5 ARCHIVE false-positive)

A *regular* (non-ARCHIVE) CCI ``CHAR(n)`` column is stored with enc=5 (raw).
When the column has enough distinct values that its per-segment string pool
exceeds 64 KiB, the u16 offset/index region contains the ``0xFFFF`` sentinel.

``_decode_enc5`` used to probe every enc=5 blob with ``unc=1, cmp=0`` for an
ARCHIVE compressed-sub-block signature (``0xFFFF`` followed by a u16 in
``[0xFFF0, 0xFFFF]``).  That signature *also* occurs in the index region of these
ordinary large-pool CHAR segments, so the column was misrouted to the ARCHIVE
decoder and decoded as **all-NULL** — silently inflating the null count.

This was found in the wild on ``tpcxbb_1gb.bak`` (``dbo.customer.c_login`` CHAR(13),
``dbo.customer_address.ca_zip`` CHAR(10), etc.) but no checked-in fixture exercised
a *regular* CCI enc=5 CHAR column with a >64 KiB pool.  The fix gates the probe
behind ``is_archive``; this fixture is the regression guard.

## Schema and data

``dbo.cci_char_pool`` — regular CCI, two high-cardinality / high-entropy CHAR
columns plus sparse NULLs (the discriminating signal):

    id      INT         NOT NULL          — 1 .. ROW_COUNT
    login   CHAR(13)    NULL              — distinct MD5-hex, VARYING effective length; pool > 64 KiB
    code    CHAR(10)    NULL              — distinct MD5-hex, VARYING effective length; pool > 64 KiB

``ROW_COUNT`` rows (> 65536 on purpose — see below); every ``NULL_STRIDE``-th row
has NULL login and code.  On the pre-fix decoder the misrouted ARCHIVE path reads
garbage and inflates the null count far above the true ``ROW_COUNT // NULL_STRIDE``;
the fixed decoder returns exactly ``ROW_COUNT // NULL_STRIDE`` nulls.

## Why ROW_COUNT > 65536, and the value-decode gap it exposes

The misrouted ARCHIVE decoder only *diverges* (wrong null count) once the u16
segment index spans the 64 Ki-row boundary — below that it coincidentally decodes
correctly, so the fixture would not discriminate.  Above that boundary the segment
also uses enc=5 **Format D** VLD pages with a value pool that spans multiple
XPRESS page envelopes.  The coverage test asserts both the original null-count
guard and the decoded row values/null positions.

## Exported constants (imported by the coverage test)

  - ``DB_NAME``, ``TABLE``, ``ROW_COUNT``, ``NULL_STRIDE``

Usage:
    python -m tools.fixture_run cci-enc5-largepool
    python -m tools.fixture_run all-versions --suite cci-enc5-largepool
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

DB_NAME = "CciEnc5LargePool"
TABLE = "cci_char_pool"
# > 65536 so the u16 segment index spans the 64 Ki-row boundary — the condition
# under which the misrouted fixed-width ARCHIVE decoder loses alignment and emits
# garbage NULLs (tpcxbb's failing segments had n_rows = 99000).
ROW_COUNT = 80000
NULL_STRIDE = 1000  # id % NULL_STRIDE == 0 → NULL login and code

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_enc5_largepool_full.bak"
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
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        f"""CREATE TABLE dbo.{TABLE} (
    id     INT        NOT NULL,
    login  CHAR(13)   NULL,
    code   CHAR(10)   NULL,
    INDEX cci CLUSTERED COLUMNSTORE
)""",
        # Distinct, HIGH-ENTROPY, VARYING-LENGTH CHAR values (deterministic MD5 hex
        # of the row number, truncated to a per-row length then space-padded to the
        # column width).  Two ingredients reproduce the bug:
        #   1. high cardinality → per-segment string pool > 64 KiB → the u16 index
        #      emits the 0xFFFF sentinel that fires the ARCHIVE probe; and
        #   2. varying effective length → the pool packs entries at natural length,
        #      so the misrouted *fixed-width* ARCHIVE decoder misaligns and emits
        #      garbage NULLs (mirrors tpcxbb's space-padded random login/date data).
        # Full-width / low-entropy values decode identically either way and do NOT
        # reproduce the bug.  Every NULL_STRIDE-th row is NULL.
        f"""INSERT INTO dbo.{TABLE} (id, login, code)
SELECT
    pk + 1 AS id,
    CASE WHEN (pk + 1) % {NULL_STRIDE} = 0 THEN NULL
         ELSE CAST(LEFT(CONVERT(CHAR(32), HASHBYTES('MD5', CAST(pk + 1 AS VARCHAR(12))), 2), 13) AS CHAR(13))
    END AS login,
    CASE WHEN (pk + 1) % {NULL_STRIDE} = 0 THEN NULL
         ELSE CAST(LEFT(CONVERT(CHAR(32), HASHBYTES('MD5', CAST(pk + 1000003 AS VARCHAR(12))), 2), 10) AS CHAR(10))
    END AS code
FROM fkr__seed
WHERE pk < {ROW_COUNT}""",
        # Force all rows into a single compressed row group (regular CCI, not ARCHIVE).
        f"""ALTER INDEX cci ON dbo.{TABLE}
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)""",
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
    print(f"inserting {ROW_COUNT} rows into regular CCI with CHAR(13)/CHAR(10) columns …")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
