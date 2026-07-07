#!/usr/bin/env python3
"""Build the incremental (full + 6 differential) reference ``.bak`` fixtures.

Creates the ``IncrementalCoverage`` database with a single ``sync_batch``
table, seeds it with 10 rows, takes a full backup, then performs 6 rounds of
inserts + updates — each followed by a ``WITH DIFFERENTIAL`` backup.

Output files (``tests/fixtures/``):

- ``incrementalcoverage_full.bak``
- ``incrementalcoverage_diff_01.bak`` … ``incrementalcoverage_diff_06.bak``

The full backup must **not** use ``COPY_ONLY`` so that SQL Server records it as
a valid differential base.  Each differential is cumulative: diff_N captures all
changes since the full, so ``PageStore.from_diff_bak(diff_N, full)`` directly
reconstructs the state at step N without chaining diffs.

Connection (same pattern as ``make_tabletype_fixture.py``):
- Container auto-discovered from ``podman ps`` (image ``mssql/server``).
- ``FIXTURE_DBA_USER`` (default ``sa``) and ``FIXTURE_DBA_PASSWORD`` (required).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "IncrementalCoverage"
MSSQL_IMAGE_MATCH = "mssql/server"

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
CONTAINER_SQL = "/tmp/incremental_load.sql"

CONTAINER_BAK_FULL = f"/tmp/{DB_NAME}_full.bak"
CONTAINER_BAK_DIFF = "/tmp/{DB_NAME}_diff_{n:02d}.bak"

# Per-diff change plan:
# Each round inserts 5 new rows (batch=n) and updates one earlier row.
# Row ids to update per diff (identity starts at 1):
# diff 1: insert ids 11-15 (batch=1), no update (only inserts at first step)
# diff 2: insert ids 16-20 (batch=2), update id=3
# diff 3: insert ids 21-25 (batch=3), update id=7
# diff 4: insert ids 26-30 (batch=4), update id=12
# diff 5: insert ids 31-35 (batch=5), update id=18
# diff 6: insert ids 36-40 (batch=6), update id=24
DIFF_STEPS: list[dict[str, Any]] = [
    {"n": 1, "batch": 1, "update_id": None},
    {"n": 2, "batch": 2, "update_id": 3},
    {"n": 3, "batch": 3, "update_id": 7},
    {"n": 4, "batch": 4, "update_id": 12},
    {"n": 5, "batch": 5, "update_id": 18},
    {"n": 6, "batch": 6, "update_id": 24},
]


def _run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs)


def discover_container() -> str:
    override = os.environ.get("FIXTURE_CONTAINER")
    if override:
        return override
    proc = _run(["podman", "ps", "--format", "{{.Names}}\t{{.Image}}"], check=True)
    matches = [
        line.split("\t", 1)[0]
        for line in proc.stdout.splitlines()
        if MSSQL_IMAGE_MATCH in line
    ]
    if not matches:
        raise RuntimeError(
            "no running SQL Server container found; set FIXTURE_CONTAINER "
            "or provision one with: forgedb sqlserver"
        )
    if len(matches) > 1:
        raise RuntimeError(f"multiple SQL Server containers; set FIXTURE_CONTAINER: {matches}")
    return matches[0]


def sqlcmd_base(user: str, password: str, container: str | None = None) -> list[str]:
    from tools.make_fixture import discover_sqlcmd_path
    path = (
        discover_sqlcmd_path(container)
        if container
        else "/opt/mssql-tools18/bin/sqlcmd"
    )
    return [
        path,
        "-S", "localhost",
        "-U", user,
        "-P", password,
        "-C",
        "-b",
    ]


def _sqlcmd_exec(container: str, sqlcmd: list[str], sql: str, sql_file: str) -> None:
    with open("/tmp/_incremental_tmp.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    cp = _run(["podman", "cp", "/tmp/_incremental_tmp.sql", f"{container}:{sql_file}"])
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp failed: {cp.stderr}")
    proc = _run(["podman", "exec", container] + sqlcmd + ["-i", sql_file])
    if proc.returncode != 0:
        raise RuntimeError(f"sqlcmd failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    if proc.stdout.strip():
        print(proc.stdout.strip())


def _copy_out(container: str, src: str, dst: Path) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cp = _run(["podman", "cp", f"{container}:{src}", str(dst)])
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp failed: {cp.stderr}")
    return dst.stat().st_size


def _build_full_sql() -> str:
    """Create database, seed 10 rows, then full backup."""
    rows_sql = "\n".join(
        f"INSERT INTO sync_batch(batch, action, val) "
        f"VALUES(0, 'insert', N'seed row {i:02d} — batch 0');"
        for i in range(1, 11)
    )
    return f"""USE [master];
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
CREATE TABLE sync_batch (
  id      INT IDENTITY PRIMARY KEY,
  batch   INT          NOT NULL,
  action  VARCHAR(10)  NOT NULL,
  val     NVARCHAR(200) NOT NULL
);
GO
{rows_sql}
GO
USE [master];
GO
BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK_FULL}'
  WITH FORMAT, INIT;
GO
"""


def _build_diff_sql(step: dict[str, Any]) -> str:
    """Insert 5 rows for this batch; optionally update one earlier row; diff backup."""
    n = step["n"]
    batch = step["batch"]
    update_id = step["update_id"]
    container_bak = f"/tmp/{DB_NAME}_diff_{n:02d}.bak"

    parts = [f"USE [{DB_NAME}];", "GO"]
    for i in range(1, 6):
        parts.append(
            f"INSERT INTO sync_batch(batch, action, val) "
            f"VALUES({batch}, 'insert', N'batch {batch} row {i}');"
        )
    parts.append("GO")
    if update_id is not None:
        parts.append(
            f"UPDATE sync_batch SET action='update', "
            f"val=N'updated by diff {n:02d} (was batch 0 or earlier)' "
            f"WHERE id={update_id};"
        )
        parts.append("GO")

    parts += [
        "USE [master];",
        "GO",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK=N'{container_bak}'",
        "  WITH FORMAT, INIT, DIFFERENTIAL;",
        "GO",
    ]
    return "\n".join(parts) + "\n"


def main() -> int:
    _expected = [FIXTURES / "incrementalcoverage_full.bak"] + [
        FIXTURES / f"incrementalcoverage_diff_{n:02d}.bak" for n in range(1, 7)
    ]
    if all(p.exists() for p in _expected):
        print("skip (all incremental fixtures already exist)", file=sys.stderr)
        return 0
    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    password = os.environ.get("FIXTURE_DBA_PASSWORD")
    if not password:
        print(
            "error: set FIXTURE_DBA_PASSWORD (forgedb setup blob -> dba.password)",
            file=sys.stderr,
        )
        return 2

    container = discover_container()
    print(f"using container: {container}")
    sqlcmd = sqlcmd_base(user, password, container)

    # --- full backup ---
    print("building full backup …")
    _sqlcmd_exec(container, sqlcmd, _build_full_sql(), CONTAINER_SQL)
    out_full = FIXTURES / "incrementalcoverage_full.bak"
    size = _copy_out(container, CONTAINER_BAK_FULL, out_full)
    print(f"wrote {out_full.name} ({size:,} bytes)")

    # --- 6 differential backups ---
    for step in DIFF_STEPS:
        n = step["n"]
        print(f"building diff {n:02d} …")
        _sqlcmd_exec(container, sqlcmd, _build_diff_sql(step), CONTAINER_SQL)
        container_bak = f"/tmp/{DB_NAME}_diff_{n:02d}.bak"
        out_diff = FIXTURES / f"incrementalcoverage_diff_{n:02d}.bak"
        size = _copy_out(container, container_bak, out_diff)
        print(f"wrote {out_diff.name} ({size:,} bytes)")

    print(f"done — 7 fixtures written to {FIXTURES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
