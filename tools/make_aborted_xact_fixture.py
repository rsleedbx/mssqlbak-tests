#!/usr/bin/env python3
"""Build ``dirtycoverage_aborted_xact.bak`` for Guess G52 (LOP_ABORT_XACT).

Opens a transaction, inserts rows, rolls back during a fuzzy backup so the log
tail captures BEGIN + INSERT + ABORT records.

Requires forgedb SQL Server container and ``FIXTURE_DBA_PASSWORD``.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_dirty_fixture import (  # noqa: E402
    _copy_out,
    _exec_sql,
    _exec_sql_bg,
    discover_container,
    sqlcmd_base,
)

DB_NAME = "DirtyAborted"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"
_REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures"))) / "dirtycoverage_aborted_xact.bak"
COMMITTED = 20
ABORTED = 10
HOLD_SECONDS = 8


def main() -> int:
    import os

    if OUT_PATH.exists():
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0
    password = os.environ.get("FIXTURE_DBA_PASSWORD")
    if not password:
        print("error: set FIXTURE_DBA_PASSWORD", file=sys.stderr)
        return 2
    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    container = discover_container()
    sqlcmd = sqlcmd_base(user, password, container)

    setup = f"""USE [master];
GO
IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
  ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{DB_NAME}];
END;
GO
CREATE DATABASE [{DB_NAME}];
GO
USE [{DB_NAME}];
GO
CREATE TABLE aborted_test (
  id INT NOT NULL PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30) NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup)

    committed_sql = "\n".join(
        f"INSERT INTO aborted_test VALUES ({i}, N'committed {i}', 'committed');"
        for i in range(1, COMMITTED + 1)
    )
    _exec_sql(container, sqlcmd, f"USE [{DB_NAME}];\nGO\n{committed_sql}\nGO\n")

    abort_inserts = "\n".join(
        f"INSERT INTO aborted_test VALUES ({100 + i}, N'abort {i}', 'aborted');"
        for i in range(1, ABORTED + 1)
    )
    tx_sql = f"""USE [{DB_NAME}];
GO
BEGIN TRANSACTION;
{abort_inserts}
WAITFOR DELAY '00:00:{HOLD_SECONDS:02d}';
ROLLBACK TRANSACTION;
GO
"""
    bg = _exec_sql_bg(container, sqlcmd, tx_sql, "/tmp/dirty_aborted_bg.sql")
    time.sleep(2)
    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK}' WITH FORMAT, INIT;
GO
"""
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_aborted_bak.sql")
    bg.communicate(timeout=HOLD_SECONDS + 10)
    size = _copy_out(container, CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
