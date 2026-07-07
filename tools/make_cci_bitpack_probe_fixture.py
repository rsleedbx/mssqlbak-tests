#!/usr/bin/env python3
"""Generate ``cci_bitpack_probe_full.bak`` — a controlled CCI bit-pack probe.

Purpose
-------
Crack the exact bit-packing layout SQL Server uses for enc=2
(VALUE_HASH_BASED) integer columnstore segments.  The real-world failure
(``tpcxbb_1gb`` ``web_clickstreams.wcs_click_date_sk``) decodes to a strided
artifact under the current padded ``vpw = 64 // bpv`` reader; no simple
padded/contiguous variant reproduces SQL's distribution.

This fixture builds a single clustered-columnstore table whose columns have
**known mathematical relationships** to a monotonically increasing key, so the
decoder can be validated per row without depending on physical row order:

    pk      BIGINT  = 0, 1, 2, ... N-1      (unique, monotonic; high bpv)
    mod4000 INT     = pk % 4000             (4000 distinct -> bpv = 12)
    mod2000 INT     = pk % 2000             (2000 distinct -> bpv = 11)
    mod1000 INT     = pk % 1000             (1000 distinct -> bpv = 10)
    mod100  INT     = pk %  100             ( 100 distinct -> bpv =  7)

Because adjacent rows differ by 1 in every ``modK`` column, none of them form
pure RLE runs, so SQL stores them as a single impure (bit-packed) run — exactly
the structure seen in the failing real-world segment.

Validation (done by the analysis harness, not here): for every decoded row,
``modK == pk % K`` must hold.  A correct bit-pack layout yields a clean sawtooth
for each ``modK`` column; the current reader does not.

The ``.bak.stats.json`` (collected by ``fixture_run register-bak``) records
SQL Server's own min/max/null per column as the authoritative reference.

Exported constants
------------------
    DB_NAME       — database name
    PROBE_ROWS    — total row count
    MODULI        — {column_name: modulus}
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

DB_NAME = "CciBitpackProbe"

# 200,000 rows >> 102,400 forces at least one *compressed* row group (not a
# delta store).  One row group keeps the layout analysis simple.
PROBE_ROWS: int = 200_000

# column_name -> modulus.  Each modulus picks a distinct-value count that lands
# in a specific bit-width bucket (bpv = ceil(log2(modulus))).
MODULI: dict[str, int] = {
    "mod4000": 4000,  # bpv 12 — the failing real-world width
    "mod2000": 2000,  # bpv 11
    "mod1000": 1000,  # bpv 10
    "mod100": 100,  # bpv 7
}

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)
OUT_PATH = FIXTURE_DIR / "cci_bitpack_probe_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def _probe_stmts() -> list[str]:
    mod_cols = ", ".join(f"{name} INT NOT NULL" for name in MODULI)
    mod_select = ", ".join(
        f"CAST(pk % {mod} AS INT) AS {name}" for name, mod in MODULI.items()
    )
    return [
        f"""CREATE TABLE cci_bitpack_probe (
    pk  BIGINT NOT NULL,
    {mod_cols}
)""",
        # Build the row set in the heap first, then compress to a CCI so the
        # values land in a compressed row group in key order.
        f"""INSERT INTO cci_bitpack_probe (pk, {", ".join(MODULI)})
SELECT CAST(pk AS BIGINT) AS pk, {mod_select}
FROM fkr__seed
WHERE pk < {PROBE_ROWS}""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_bitpack_probe_cci"
        " ON cci_bitpack_probe",
        "ALTER INDEX cci_bitpack_probe_cci ON cci_bitpack_probe"
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
    stmts += seed_sql(PROBE_ROWS)
    stmts += _probe_stmts()
    stmts += [
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}'"
        f" WITH FORMAT, INIT, COPY_ONLY",
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
