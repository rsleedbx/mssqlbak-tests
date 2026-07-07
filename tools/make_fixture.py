#!/usr/bin/env python3
"""Build the type-coverage reference ``.bak`` from the value matrix.

Targets an existing SQL Server container provisioned by forgedb
(``setup_sqlserver_podman``) rather than spinning up its own — the database is
forgedb-owned. Creates the ``TypeCoverage`` database with one table per
:data:`tools.typematrix.TYPE_CASES` entry, inserts the known value matrix, runs
``BACKUP DATABASE``, and copies the resulting ``.bak`` out to
``tests/fixtures/typecoverage_full.bak``.

Connection:
- Prefer ``python -m tools.fixture_run make_fixture`` — loads credentials and
  container from forgedb automatically (see :mod:`tools.fixture_run`).
- Or set ``FIXTURE_DBA_PASSWORD`` / ``FIXTURE_CONTAINER`` manually; the
  container is auto-discovered from ``podman ps`` (image ``mssql/server``) when
  ``FIXTURE_CONTAINER`` is unset.

The SQL is fed to ``sqlcmd`` via an input file copied into the container (not a
giant ``-Q`` string) because the ``varbinary(max)`` ``mid`` row alone is a ~2 MB
hex literal.
"""

from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

# Allow running as a plain script (``python tools/make_fixture.py``) by putting
# the repo root — not ``tools/`` — first on the import path.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.lobmatrix import LOB_LINKS_SQL  # noqa: E402
from tools.typematrix import TYPE_CASES  # noqa: E402

DB_NAME = "TypeCoverage"
CONTAINER_BAK = f"/tmp/{DB_NAME}.bak"
CONTAINER_SQL = "/tmp/load.sql"
MSSQL_IMAGE_MATCH = "mssql/server"

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_PATH = FIXTURE_DIR / "typecoverage_full.bak"


def _run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs)


def discover_container() -> str:
    """Return the running forgedb SQL Server container name."""
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
            "no running SQL Server container found (provision one with forgedb "
            "setup_sqlserver_podman, or set FIXTURE_CONTAINER)"
        )
    if len(matches) > 1:
        raise RuntimeError(f"multiple SQL Server containers; set FIXTURE_CONTAINER: {matches}")
    return matches[0]


_SQLCMD_PATH_CACHE: dict[str, str] = {}

# Ordered candidates: mssql-tools18 ships with 2019+; mssql-tools ships with 2017.
_SQLCMD_CANDIDATES = [
    "/opt/mssql-tools18/bin/sqlcmd",
    "/opt/mssql-tools/bin/sqlcmd",
]
_BCP_CANDIDATES = [
    "/opt/mssql-tools18/bin/bcp",
    "/opt/mssql-tools/bin/bcp",
]


def discover_sqlcmd_path(container: str, binary: str = "sqlcmd") -> str:
    """Return the full path to *binary* inside *container*, probing the candidates once."""
    cache_key = f"{container}:{binary}"
    if cache_key in _SQLCMD_PATH_CACHE:
        return _SQLCMD_PATH_CACHE[cache_key]
    candidates = _BCP_CANDIDATES if binary == "bcp" else _SQLCMD_CANDIDATES
    for candidate in candidates:
        result = subprocess.run(
            ["podman", "exec", container, "test", "-f", candidate],
            capture_output=True,
        )
        if result.returncode == 0:
            _SQLCMD_PATH_CACHE[cache_key] = candidate
            return candidate
    raise RuntimeError(
        f"{binary} not found in container {container!r}; "
        f"tried: {candidates}"
    )


def sqlcmd_base(user: str, password: str, container: str | None = None) -> list[str]:
    path = (
        discover_sqlcmd_path(container)
        if container
        else _SQLCMD_CANDIDATES[0]
    )
    return [
        path,
        "-S", "localhost",
        "-U", user,
        "-P", password,
        "-C",  # trust the self-signed server cert
        "-b",  # exit non-zero on SQL errors
    ]


def sql_literal(value: Any) -> str:
    """Render ``value`` as a SQL literal matching its canonical Python type."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):  # before int — bool is a subclass of int
        return "1" if value else "0"
    if isinstance(value, int):
        return repr(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, Decimal):
        return format(value, "f")  # fixed-point, never scientific notation
    if isinstance(value, (bytes, bytearray)):
        return "0x" + bytes(value).hex()  # "0x" alone for the empty blob
    if isinstance(value, dt.datetime):  # before date — datetime subclasses date
        # isoformat carries the UTC offset for tz-aware values (datetimeoffset).
        return "N'" + value.isoformat(sep=" ") + "'"
    if isinstance(value, dt.date):
        return "N'" + value.isoformat() + "'"
    if isinstance(value, dt.time):
        return "N'" + value.isoformat() + "'"
    if isinstance(value, UUID):
        return "N'" + str(value) + "'"
    if isinstance(value, str):
        return "N'" + value.replace("'", "''") + "'"
    raise TypeError(f"no SQL literal for {type(value)!r}")


def build_sql() -> str:
    """Assemble the full create/insert/backup script for ``sqlcmd -i``.

    Idempotent: drops a pre-existing ``TypeCoverage`` DB first, since the forgedb
    container persists across runs.
    """
    parts: list[str] = [
        "USE [master];",
        "GO",
        f"IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN "
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
        f"DROP DATABASE [{DB_NAME}]; END;",
        "GO",
        f"CREATE DATABASE [{DB_NAME}];",
        "GO",
        f"USE [{DB_NAME}];",
        "GO",
    ]
    for case in TYPE_CASES:
        table = f"t_{case.name}"
        # ``auto`` columns (rowversion) are engine-populated and cannot be
        # declared NULL or written to; everything else is a nullable value column.
        col_def = f"v {case.sql_type}" if case.auto else f"v {case.sql_type} NULL"
        parts.append(
            f"CREATE TABLE [{table}] "
            f"(id int IDENTITY PRIMARY KEY, label varchar(8) NOT NULL, {col_def});"
        )
        for row in case.rows:
            if case.auto:
                parts.append(
                    f"INSERT INTO [{table}] (label) VALUES ({sql_literal(row.label)});"
                )
            else:
                v_literal = row.sql if row.sql is not None else sql_literal(row.value)
                parts.append(
                    f"INSERT INTO [{table}] (label, v) "
                    f"VALUES ({sql_literal(row.label)}, {v_literal});"
                )
        parts.append("GO")
    parts.extend(LOB_LINKS_SQL)
    parts += [
        "USE [master];",
        "GO",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY;",
        "GO",
    ]
    return "\n".join(parts) + "\n"


def _load_and_backup(
    container: str, sqlcmd: list[str], sql: str, container_sql: str = CONTAINER_SQL
) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as fh:
        fh.write(sql)
        local_sql = fh.name
    try:
        _run(["podman", "cp", local_sql, f"{container}:{container_sql}"], check=True)
    finally:
        Path(local_sql).unlink(missing_ok=True)
    proc = _run(["podman", "exec", container, *sqlcmd, "-i", container_sql])
    if proc.returncode != 0:
        raise RuntimeError(f"sqlcmd load/backup failed:\n{proc.stdout}\n{proc.stderr}")
    print("loaded matrix and ran BACKUP DATABASE")


def _copy_out(container: str, container_bak: str, out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _run(["podman", "cp", f"{container}:{container_bak}", str(out_path)], check=True)
    return out_path.stat().st_size


def backup_statement(db_name: str, container_bak: str) -> str:
    """T-SQL to back up *db_name* (copy-only full) to *container_bak*."""
    return (
        "USE [master];\nGO\n"
        f"BACKUP DATABASE [{db_name}] TO DISK=N'{container_bak}' "
        "WITH FORMAT, INIT, COPY_ONLY;\nGO\n"
    )


def generate_fixture(db_name: str, body_sql: str, out_path: Path) -> int:
    """Load *body_sql*, back up *db_name*, and copy the ``.bak`` to *out_path*.

    Reusable across fixtures (type-coverage, constraint-coverage, wide-table):
    callers supply the create/insert SQL; this appends the BACKUP and handles the
    container plumbing.  Reads the DBA password from ``FIXTURE_DBA_PASSWORD``.
    """
    if out_path.exists():
        print(f"skip (already exists): {out_path.name}", file=sys.stderr)
        return 0
    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    password = os.environ.get("FIXTURE_DBA_PASSWORD")
    if not password:
        print("error: set FIXTURE_DBA_PASSWORD (forgedb setup blob -> dba.password)", file=sys.stderr)
        return 2
    container = discover_container()
    print(f"using container {container} as {user}")
    container_bak = f"/tmp/{db_name}.bak"
    container_sql = f"/tmp/load_{db_name}.sql"
    sql = body_sql + backup_statement(db_name, container_bak)
    _load_and_backup(container, sqlcmd_base(user, password, container), sql, container_sql)
    size = _copy_out(container, container_bak, out_path)
    print(f"wrote {out_path} ({size:,} bytes)")
    return 0


def main() -> int:
    # build_sql() already appends its own BACKUP DATABASE; keep that path intact.
    if OUT_PATH.exists():
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0
    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    password = os.environ.get("FIXTURE_DBA_PASSWORD")
    if not password:
        print("error: set FIXTURE_DBA_PASSWORD (forgedb setup blob -> dba.password)", file=sys.stderr)
        return 2
    container = discover_container()
    print(f"using container {container} as {user}")
    _load_and_backup(container, sqlcmd_base(user, password, container), build_sql())
    size = _copy_out(container, CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
