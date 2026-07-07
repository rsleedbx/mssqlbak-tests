#!/usr/bin/env python3
"""Generate ``xtp_probe_full.bak`` — controlled XTP checkpoint format probe fixture.

## Purpose

Uses bit-distinctive "canary" values (e.g. 0x11223344, 0xDEADBEEF) so that
exact byte positions of each column can be found unambiguously in the backup
stream.  Each table isolates one variable:

  * **probe_1i1r**  — 1 INT column, 1 row  (minimal possible XTP row)
  * **probe_2i1r**  — 2 INT columns, 1 row (adds a second fixed column)
  * **probe_1i3r**  — 1 INT column, 3 rows (tests row packing / stride)
  * **probe_nv1r**  — 1 INT + 1 NVARCHAR(16), 1 non-null row
  * **probe_nv1r_null** — 1 INT + 1 NVARCHAR(16), 1 NULL row

## Canary values (chosen to be visually distinctive in hex dumps)

    id   = 0x11223344 (LE: 44 33 22 11)
    id2  = 0x55667788 (LE: 88 77 66 55)
    id_a = 0xAABBCCDD (LE: DD CC BB AA)   — row 1 of 1i3r
    id_b = 0x11BEEF22 (LE: 22 EF BE 11)   — row 2 of 1i3r
    id_c = 0xDEAD0001 (LE: 01 00 AD DE)   — row 3 of 1i3r
    score= 0x99887766 (LE: 66 77 88 99)   — second column in 2i1r
    label= 'XtpProbe'                     — nvarchar value (UTF-16LE)

Usage:
    python -m tools.fixture_run xtp-probe
    python -m tools.diag_xtp_blocks tests/fixtures_2022/xtp_probe_full.bak \\
        --search-values 0x11223344 0x55667788 0x99887766 XtpProbe
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

DB_NAME = "XtpProbe"

# Canary values — chosen for visual distinctiveness in hex dumps.
# All must fit in a signed INT (< 0x80000000) so T-SQL INSERT doesn't overflow.
ID_1COL  = 0x11223344   # LE bytes: 44 33 22 11
ID_2COL  = 0x55667788   # LE bytes: 88 77 66 55
SCORE    = 0x11887766   # LE bytes: 66 77 88 11
ID_A     = 0x1ABBCCDD   # LE bytes: DD CC BB 1A
ID_B     = 0x11BEEF22   # LE bytes: 22 EF BE 11
ID_C     = 0x7EAD0001   # LE bytes: 01 00 AD 7E
NV_LABEL = "XtpProbe"   # UTF-16LE: 58 00 74 00 70 00 50 00 72 00 6f 00 62 00 65 00

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
_OUT_PATH = _FIXTURE_DIR / "xtp_probe_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    return [
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"ALTER DATABASE [{DB_NAME}] ADD FILEGROUP [FG_XTP] CONTAINS MEMORY_OPTIMIZED_DATA",
        f"""ALTER DATABASE [{DB_NAME}] ADD FILE (
    NAME = N'xtp_probe_data',
    FILENAME = N'/var/opt/mssql/data/xtp_probe_data'
) TO FILEGROUP [FG_XTP]""",
        f"USE [{DB_NAME}]",

        # --- probe_1i1r: 1 INT column, 1 row ---
        """CREATE TABLE dbo.probe_1i1r (
    id INT NOT NULL,
    CONSTRAINT pk_1i1r PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.probe_1i1r VALUES ({ID_1COL})",

        # --- probe_2i1r: 2 INT columns, 1 row ---
        """CREATE TABLE dbo.probe_2i1r (
    id    INT NOT NULL,
    score INT NOT NULL,
    CONSTRAINT pk_2i1r PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.probe_2i1r VALUES ({ID_2COL}, {SCORE})",

        # --- probe_1i3r: 1 INT column, 3 rows (row packing) ---
        """CREATE TABLE dbo.probe_1i3r (
    id INT NOT NULL,
    CONSTRAINT pk_1i3r PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.probe_1i3r VALUES ({ID_A})",
        f"INSERT INTO dbo.probe_1i3r VALUES ({ID_B})",
        f"INSERT INTO dbo.probe_1i3r VALUES ({ID_C})",

        # --- probe_nv1r: 1 INT + 1 NVARCHAR, 1 non-null row ---
        """CREATE TABLE dbo.probe_nv1r (
    id    INT           NOT NULL,
    label NVARCHAR(16)  NULL,
    CONSTRAINT pk_nv1r PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.probe_nv1r VALUES ({ID_1COL}, N'{NV_LABEL}')",

        # --- probe_nv1r_null: same schema, 1 NULL row ---
        """CREATE TABLE dbo.probe_nv1r_null (
    id    INT           NOT NULL,
    label NVARCHAR(16)  NULL,
    CONSTRAINT pk_nv1r_null PRIMARY KEY NONCLUSTERED (id)
) WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)""",
        f"INSERT INTO dbo.probe_nv1r_null VALUES ({ID_2COL}, NULL)",

        "CHECKPOINT",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def main(force: bool = False) -> int:
    if skip_if_exists(_OUT_PATH, force=force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print("creating XTP probe fixture (5 tables, canary values)")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, _OUT_PATH)
    print(f"wrote {_OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()
    sys.exit(main(force=args.force))
