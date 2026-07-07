#!/usr/bin/env python3
"""Generate ``xtp_checkpoint_straddle_full.bak``.

A large, COMPRESSED memory-optimized fixture whose frozen rows flush into 64 KB
XTP checkpoint DATA chunks.  Variable-width nvarchar payloads make row images
straddle chunk boundaries — the exact condition that clobbers a row's tail in
the log stream and forces checkpoint DATA-file recovery.  A dense IDENTITY(1,1)
key gives an exact {1..N} completeness signal.
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
    skip_if_exists,
)

DB_NAME = "XtpCheckpointStraddle"
TABLE = "xtp_ckpt"

# Number of rows.  100k variable-width rows (avg ~200 B) → ~20 MB of checkpoint
# data → hundreds of 64 KB chunks → dozens of straddle rows.  Large enough to
# force checkpoint DATA files, small enough for a 12 GB cap.
ROW_COUNT = 100_000
# payload width cycles 1..PAYLOAD_MOD chars so row images are variable-length.
PAYLOAD_MOD = 400

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "xtp_checkpoint_straddle_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def expected_payload_len(id_: int) -> int:
    """Deterministic nvarchar length for a 1-based id.

    Mirrors the generator SQL exactly: pk is 0-based (pk = id - 1), width =
    1 + (pk % PAYLOAD_MOD).  Kept importable so the coverage test derives
    expected values from the SQL, not from memory.
    """
    pk = id_ - 1
    return 1 + (pk % PAYLOAD_MOD)


def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"ALTER DATABASE [{DB_NAME}] ADD FILEGROUP [FG_XTP] CONTAINS MEMORY_OPTIMIZED_DATA",
        f"""ALTER DATABASE [{DB_NAME}] ADD FILE (
    NAME = N'xtp_ckpt_data',
    FILENAME = N'/var/opt/mssql/data/xtp_ckpt_data'
) TO FILEGROUP [FG_XTP]""",
        f"USE [{DB_NAME}]",
    ]
    # fkr__seed(pk INT PRIMARY KEY) with pk = 0..ROW_COUNT-1 (disk table).
    stmts += seed_sql(ROW_COUNT)
    stmts += [
        f"""CREATE TABLE dbo.{TABLE} (
    id      INT            NOT NULL IDENTITY(1,1),
    width   INT            NOT NULL,
    payload NVARCHAR(400)  NOT NULL,
    CONSTRAINT pk_{TABLE} PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        # Insert in seed (pk) order so IDENTITY id == pk + 1 deterministically.
        f"""INSERT INTO dbo.{TABLE} (width, payload)
SELECT 1 + (pk % {PAYLOAD_MOD}) AS width,
       REPLICATE(N'x', 1 + (pk % {PAYLOAD_MOD})) AS payload
FROM (SELECT pk FROM fkr__seed WHERE pk < {ROW_COUNT}) AS _f
ORDER BY pk""",
        # Freeze rows into XTP checkpoint DATA files.
        "CHECKPOINT",
        "USE [master]",
        # COMPRESSION is REQUIRED — Pass 3 only runs for MSSQLBAK-compressed input.
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' "
        f"WITH FORMAT, INIT, COPY_ONLY, COMPRESSION",
    ]
    return stmts


def main(force: bool = False) -> int:
    if skip_if_exists(OUT_PATH, force=force):
        return 0
    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"creating XTP checkpoint-straddle fixture: {ROW_COUNT:,} rows")
    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()
    sys.exit(main(force=args.force))
