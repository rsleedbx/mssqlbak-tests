#!/usr/bin/env python3
"""Generate ``cci_bitpack_probe_bigint_full.bak`` — tpcxbb-shaped CCI probe.

The INT probe (``cci_bitpack_probe_full.bak``) proved the enc=2 padded+dict
decoder is correct for a single 200k-row row group with ``min_data_id = 0``.
The real-world failure (``tpcxbb_1gb`` ``web_clickstreams.wcs_click_date_sk``)
differs in three ways this fixture reproduces exactly:

    * column type is **BIGINT**, not INT;
    * values start at a **high base** (36890), so the segment ``min_data_id`` is
      a large value rather than 0;
    * the table has **multiple full (~1,048,576-row) row groups** sharing one
      global dictionary, like tpcxbb's 7 segments.

Schema (one CCI table):

    pk    BIGINT = 0, 1, 2, ... N-1          (anchor; enc=1 value-encoded)
    dt    BIGINT = 36890 + (pk % 4000)        (4000 distinct -> bpv 12, enc=2)

``dt`` mirrors ``wcs_click_date_sk``: a BIGINT date-key-like column whose value
space is a contiguous run starting at 36890.  Per-row ground truth is exact:
``dt == 36890 + (pk % 4000)``.

Exported constants
------------------
    DB_NAME, PROBE_ROWS, DT_BASE, DT_MOD
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

DB_NAME = "CciBitpackProbeBigint"

# 2.2M rows -> two full 1,048,576-row compressed row groups + a partial third,
# matching tpcxbb's multi-segment / shared-global-dictionary layout.
PROBE_ROWS: int = 2_200_000
DT_BASE: int = 36890
DT_MOD: int = 4000  # bpv = ceil(log2(4000)) = 12

FIXTURE_DIR = Path(
    os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022"))
)
OUT_PATH = FIXTURE_DIR / "cci_bitpack_probe_bigint_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def _probe_stmts() -> list[str]:
    return [
        """CREATE TABLE cci_bitpack_probe_bigint (
    pk  BIGINT NOT NULL,
    dt  BIGINT NOT NULL
)""",
        f"""INSERT INTO cci_bitpack_probe_bigint (pk, dt)
SELECT CAST(pk AS BIGINT) AS pk,
       CAST({DT_BASE} + (pk % {DT_MOD}) AS BIGINT) AS dt
FROM fkr__seed
WHERE pk < {PROBE_ROWS}""",
        "CREATE CLUSTERED COLUMNSTORE INDEX cci_bitpack_probe_bigint_cci"
        " ON cci_bitpack_probe_bigint",
        "ALTER INDEX cci_bitpack_probe_bigint_cci ON cci_bitpack_probe_bigint"
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
