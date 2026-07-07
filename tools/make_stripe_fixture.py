"""Build a 2-file striped compressed backup for stripe-parser testing.

Creates a ``StripeTest`` database with a lightweight type-coverage table,
backs it up twice:

* ``tests/fixtures/striped_full_1.bak`` and ``tests/fixtures/striped_full_2.bak``
  — two-file compressed stripe.
* ``tests/fixtures/striped_single.bak`` — identical data as a single-file
  compressed backup (baseline for row-count / value comparison).

Run via::

    python -m tools.fixture_run stripe

or directly::

    FIXTURE_DBA_PASSWORD=... FIXTURE_CONTAINER=... python tools/make_stripe_fixture.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_fixture import discover_container, sqlcmd_base  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_1 = _FIXTURE_DIR / "striped_full_1.bak"
OUT_2 = _FIXTURE_DIR / "striped_full_2.bak"
OUT_SINGLE = _FIXTURE_DIR / "striped_single.bak"

DB_NAME = "StripeTest"

_CONTAINER_SQL = "/tmp/stripe_fixture.sql"
_CONTAINER_BAK_1 = "/tmp/stripe_full_1.bak"
_CONTAINER_BAK_2 = "/tmp/stripe_full_2.bak"
_CONTAINER_BAK_SINGLE = "/tmp/stripe_single.bak"

# 20 rows with int/varchar/float/bit/NULL to give the stripe parser enough
# chunk diversity, while staying small enough for fast test runs.
_ROWS = "\n".join(
    f"INSERT INTO [probe] (id, label, score, flag) VALUES "
    f"({i}, N'row{i}', {i * 1.1:.2f}, {i % 2});"
    for i in range(1, 21)
)

_SETUP_SQL = f"""
USE [master];
GO
IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
  ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{DB_NAME}]; END;
GO
CREATE DATABASE [{DB_NAME}];
GO
USE [{DB_NAME}];
GO
CREATE TABLE [probe] (
  id    INT          NOT NULL PRIMARY KEY,
  label VARCHAR(20)  NOT NULL,
  score FLOAT        NULL,
  flag  BIT          NULL
);
GO
{_ROWS}
GO
USE [master];
GO
BACKUP DATABASE [{DB_NAME}]
  TO DISK = N'{_CONTAINER_BAK_1}',
     DISK = N'{_CONTAINER_BAK_2}'
  WITH COMPRESSION, FORMAT, INIT, STATS=10;
GO
BACKUP DATABASE [{DB_NAME}]
  TO DISK = N'{_CONTAINER_BAK_SINGLE}'
  WITH COMPRESSION, FORMAT, INIT, STATS=10;
GO
"""


def _run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs)


def main() -> int:
    if OUT_1.exists() and OUT_2.exists() and OUT_SINGLE.exists():
        print(f"skip (already exists): {OUT_1.name}, {OUT_2.name}, {OUT_SINGLE.name}", file=sys.stderr)
        return 0
    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    password = os.environ.get("FIXTURE_DBA_PASSWORD", "")
    container = discover_container()
    sqlcmd = sqlcmd_base(user, password, container)

    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as fh:
        fh.write(_SETUP_SQL)
        local_sql = fh.name
    try:
        _run(["podman", "cp", local_sql, f"{container}:{_CONTAINER_SQL}"], check=True)
    finally:
        Path(local_sql).unlink(missing_ok=True)

    proc = _run(["podman", "exec", container, *sqlcmd, "-i", _CONTAINER_SQL])
    if proc.returncode != 0:
        print(
            f"sqlcmd stripe fixture failed:\n{proc.stdout}\n{proc.stderr}",
            file=sys.stderr,
        )
        return 1
    print(proc.stdout)

    pairs = [
        (_CONTAINER_BAK_1, OUT_1),
        (_CONTAINER_BAK_2, OUT_2),
        (_CONTAINER_BAK_SINGLE, OUT_SINGLE),
    ]
    for container_path, out_path in pairs:
        proc = _run(["podman", "cp", f"{container}:{container_path}", str(out_path)])
        if proc.returncode != 0:
            print(
                f"copy failed for {container_path}:\n{proc.stderr}", file=sys.stderr
            )
            return 1
        print(f"wrote {out_path.name} ({out_path.stat().st_size:,} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
