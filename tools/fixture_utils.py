"""Shared low-level helpers for fixture generator scripts.

## Design contract

New fixture generators should import ONLY from this module (not from each
other or from ``make_fixture``).  This keeps the dependency graph flat:

    fixture_utils  ←  make_heap_scale_fixture
    fixture_utils  ←  make_foo_fixture
    ...

Each generator is a thin wrapper that supplies:
  - ``DB_NAME`` and ``OUT_PATH`` constants (driven by ``FIXTURE_DIR`` env var)
  - ``build_stmts(...)`` — pure function, returns ``list[str]`` (no GO / ;)
  - ``main()`` — argparse entry point; calls helpers from this module

## Scaling pattern

Generators that participate in Phase 2 scale-up accept a ``--rows N``
argument.  ``build_stmts`` receives ``rows`` and embeds it in the DDL/DML.
The ``all-versions`` suite always uses the default row count; a direct
invocation can override with ``--rows 80000``.

## Row-generation pattern

Use ``seed_sql(n)`` to create a ``fkr__seed(pk INT PRIMARY KEY)`` table with
``n`` rows (pk 0..n-1) via efficient INSERT-SELECT doubling.  Then generate
data with ``FROM fkr__seed WHERE pk < n`` instead of slow cross-join CTEs.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import mssql_python as _mssql

# ---------------------------------------------------------------------------
# sqlcmd / bcp path discovery  (version-aware: tools18 for 2019+, tools for 2017)
# ---------------------------------------------------------------------------

_SQLCMD_PATH_CACHE: dict[str, str] = {}

_SQLCMD_CANDIDATES = [
    "/opt/mssql-tools18/bin/sqlcmd",  # SQL Server 2019+
    "/opt/mssql-tools/bin/sqlcmd",    # SQL Server 2017 and earlier
]
_BCP_CANDIDATES = [
    "/opt/mssql-tools18/bin/bcp",
    "/opt/mssql-tools/bin/bcp",
]


def discover_sqlcmd_path(container: str, binary: str = "sqlcmd") -> str:
    """Return the full path to *binary* inside *container* (probed once, cached).

    Discovery order:
    1. Container's own PATH via ``command -v <binary>`` (non-login sh so no
       ``mesg: ttyname failed`` noise).  This handles future images that add
       sqlcmd/bcp to PATH or relocate it without requiring edits here.
    2. Hardcoded candidate list (``_SQLCMD_CANDIDATES`` / ``_BCP_CANDIDATES``).
       Current SQL Server images keep sqlcmd under /opt/mssql-tools18/bin which
       is NOT on the default container PATH, so the fallback is required today.

    In both stages, a "container state improper" / "no such container" stderr
    is detected and re-raised as a clear "container is not running" error so the
    operator isn't misled into thinking the binary is missing.
    """
    cache_key = f"{container}:{binary}"
    if cache_key in _SQLCMD_PATH_CACHE:
        return _SQLCMD_PATH_CACHE[cache_key]

    def _check_container_down(r: subprocess.CompletedProcess[str]) -> None:
        combined = (r.stdout + r.stderr).lower()
        if "container state" in combined or "no such container" in combined:
            raise RuntimeError(
                f"container {container!r} is not running; "
                "start it with: forgedb start <instance>"
            )

    # Stage 1: let the container resolve via its own PATH.
    path_probe = subprocess.run(
        ["podman", "exec", container, "sh", "-c", f"command -v {binary}"],
        capture_output=True,
        text=True,
    )
    _check_container_down(path_probe)
    found = path_probe.stdout.strip()
    if path_probe.returncode == 0 and found:
        _SQLCMD_PATH_CACHE[cache_key] = found
        return found

    # Stage 2: hardcoded candidate locations (sqlcmd is off PATH in current images).
    candidates = _BCP_CANDIDATES if binary == "bcp" else _SQLCMD_CANDIDATES
    for candidate in candidates:
        r = subprocess.run(
            ["podman", "exec", container, "test", "-f", candidate],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            _SQLCMD_PATH_CACHE[cache_key] = candidate
            return candidate
        _check_container_down(r)
    raise RuntimeError(
        f"{binary} not found in container {container!r}; tried: {candidates}"
    )


# ---------------------------------------------------------------------------
# Container discovery
# ---------------------------------------------------------------------------

_MSSQL_IMAGE_MATCH = "mssql/server"


def discover_container() -> str:
    """Return the target SQL Server Podman container name.

    Reads ``FIXTURE_CONTAINER`` env var first; otherwise auto-discovers from
    ``podman ps`` (fails if 0 or 2+ containers are running).
    """
    if override := os.environ.get("FIXTURE_CONTAINER"):
        return override
    proc = subprocess.run(
        ["podman", "ps", "--format", "{{.Names}}\t{{.Image}}"],
        text=True,
        capture_output=True,
        check=True,
    )
    matches = [
        line.split("\t", 1)[0]
        for line in proc.stdout.splitlines()
        if _MSSQL_IMAGE_MATCH in line
    ]
    if not matches:
        raise RuntimeError(
            "no running SQL Server container found "
            "(provision one with forgedb, or set FIXTURE_CONTAINER)"
        )
    if len(matches) > 1:
        raise RuntimeError(
            f"multiple SQL Server containers; set FIXTURE_CONTAINER: {matches}"
        )
    return matches[0]


# ---------------------------------------------------------------------------
# sqlcmd command builder
# ---------------------------------------------------------------------------

def sqlcmd_base(user: str, password: str, container: str) -> list[str]:
    """Return the base ``sqlcmd`` invocation list for *container*."""
    return [
        discover_sqlcmd_path(container),
        "-S", "localhost",
        "-U", user,
        "-P", password,
        "-C",  # trust self-signed server certificate
        "-b",  # exit non-zero on SQL errors
    ]


# ---------------------------------------------------------------------------
# Shell / Podman helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs)


def _copy_out(container: str, container_path: str, host_path: Path) -> int:
    """Copy *container_path* out of *container* to *host_path*; return byte size."""
    host_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["podman", "cp", f"{container}:{container_path}", str(host_path)],
        check=True,
    )
    return host_path.stat().st_size


def _run_sql(
    container: str,
    sqlcmd: list[str],
    sql: str,
    sql_file: str = "/tmp/_fixture_utils_query.sql",
) -> str:
    """Write *sql* into *container* and execute it; return combined stdout+stderr.

    Like _load_and_backup but returns the sqlcmd output instead of discarding it.
    Use for probe/query scripts that emit PRINT or SELECT output the caller needs.
    """
    local = "/tmp/_fixture_utils_query_local.sql"
    with open(local, "w", encoding="utf-8") as f:
        f.write(sql)
    cp = _run(["podman", "cp", local, f"{container}:{sql_file}"])
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp failed: {cp.stderr}")
    proc = _run(["podman", "exec", container, *sqlcmd, "-i", sql_file])
    if proc.returncode != 0:
        raise RuntimeError(
            f"sqlcmd failed:\n{proc.stdout}\n{proc.stderr}"
        )
    return proc.stdout + proc.stderr


def _load_and_backup(
    container: str,
    sqlcmd: list[str],
    sql: str,
    sql_file: str,
) -> None:
    """Write *sql* into *container* as *sql_file*, then execute it with sqlcmd.

    Raises ``RuntimeError`` on any failure so callers get a clear traceback
    rather than a silent bad exit code.
    """
    local = "/tmp/_fixture_utils_tmp.sql"
    with open(local, "w", encoding="utf-8") as f:
        f.write(sql)
    cp = _run(["podman", "cp", local, f"{container}:{sql_file}"])
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp failed: {cp.stderr}")
    proc = _run(["podman", "exec", container, *sqlcmd, "-i", sql_file])
    if proc.returncode != 0:
        raise RuntimeError(
            f"sqlcmd load/backup failed:\n{proc.stdout}\n{proc.stderr}"
        )
    print("loaded SQL and ran BACKUP DATABASE")


# ---------------------------------------------------------------------------
# mssql_python connection helpers
# ---------------------------------------------------------------------------

def _mapped_port(container: str, container_port: int = 1433) -> int:
    """Return the host port Podman maps to *container_port* inside *container*."""
    out = subprocess.check_output(
        ["podman", "port", container, f"{container_port}/tcp"], text=True
    )
    # output: "0.0.0.0:56789\n"
    return int(out.strip().split(":")[-1])


def connect_dsn(
    server: str,
    port: int,
    user: str,
    password: str,
    *,
    database: str | None = None,
    autocommit: bool = True,
    timeout: int = 15,
    encrypt: bool = False,
) -> "_mssql.Connection":
    """Return an mssql_python Connection to *server*:*port*.

    This is the single place ``mssql_python.connect`` is called in the test
    tooling.  All higher-level helpers delegate here.

    Parameters
    ----------
    server:
        Hostname or IP address of the SQL Server instance.  Use ``127.0.0.1``
        (not ``localhost``) for Podman-mapped containers on macOS to avoid the
        IPv6 ``::1`` silent-hang issue.
    port:
        TCP port the instance is listening on.
    database:
        Optional initial database context.  If ``None``, the connection lands
        on the instance's default database (usually ``master``).
    autocommit:
        ``True`` (default) for DDL, BACKUP/RESTORE, and read-only queries.
        Pass ``False`` for multi-statement DML that must be committed or
        rolled back explicitly.
    timeout:
        Connection and per-statement timeout in seconds.  The default (15 s)
        prevents the silent hang caused by ``timeout=0``.
    encrypt:
        Add ``Encrypt=yes`` to the DSN (required for non-container targets
        such as Azure SQL or an environment-configured engine host).
    """
    import mssql_python
    dsn = (
        f"SERVER={server},{port};"
        f"UID={user};PWD={password};"
        "TrustServerCertificate=yes;"
    )
    if encrypt:
        dsn += "Encrypt=yes;"
    if database:
        dsn += f"DATABASE={database};"
    return mssql_python.connect(dsn, autocommit=autocommit, timeout=timeout)


def connect(
    container: str,
    user: str,
    password: str,
    *,
    database: str | None = None,
    autocommit: bool = True,
    timeout: int = 15,
) -> "_mssql.Connection":
    """Return an mssql_python Connection to SQL Server in *container*.

    Resolves the host-mapped TCP port via ``podman port`` and delegates to
    :func:`connect_dsn`.  Uses ``127.0.0.1`` (IPv4) to avoid the macOS
    ``::1`` IPv6 hang.

    Parameters
    ----------
    database:
        Optional initial database context (``USE [database]`` equivalent).
        Defaults to the server's default (``master``).
    autocommit:
        ``True`` (default) for DDL, BACKUP/RESTORE, and catalog reads.
        Pass ``False`` for DML that must be committed explicitly.
    timeout:
        Per-connection and per-statement timeout in seconds.
    """
    port = _mapped_port(container)
    return connect_dsn(
        "127.0.0.1", port, user, password,
        database=database,
        autocommit=autocommit,
        timeout=timeout,
    )


def execute_statements(conn: "_mssql.Connection", stmts: list[str]) -> None:
    """Execute each statement in *stmts* sequentially on *conn*."""
    cur = conn.cursor()
    for stmt in stmts:
        cur.execute(stmt)
    cur.close()


def load_and_backup_stmts(
    container: str,
    user: str,
    password: str,
    stmts: list[str],
    *,
    prefer_mssql_python: bool = True,
    timeout: int = 300,
) -> None:
    """Execute *stmts* inside *container*, then BACKUP DATABASE.

    Tries ``mssql_python`` (direct TCP to the mapped host port) first when
    *prefer_mssql_python* is ``True``.  Falls back to ``sqlcmd`` via
    ``podman exec`` if ``mssql_python`` is unavailable or the connection
    fails, printing a clear warning so the caller knows which path was taken.

    Each element of *stmts* is one batch.  The BACKUP DATABASE statement must
    be included in *stmts*; the caller uses ``_copy_out`` to retrieve the file.

    The sqlcmd fallback joins batches with ``GO`` and is always reliable
    because it runs inside the container and bypasses host-side TCP routing.

    *timeout* is passed directly to ``mssql_python.connect()``.  It controls
    both the TCP connection timeout and the per-statement execution timeout.
    The default (300 s) is generous enough for long DDL such as
    ``ALTER INDEX … REORGANIZE``; lower it only for generators that never run
    slow statements and need faster failure detection.
    """
    if prefer_mssql_python:
        try:
            conn = connect(container, user, password, timeout=timeout)
            execute_statements(conn, stmts)
            conn.close()
            return
        except Exception as exc:
            import warnings
            warnings.warn(
                f"[fixture_utils] mssql_python failed ({exc!r}); "
                "falling back to sqlcmd via podman exec. "
                "Check port forwarding and TrustServerCertificate=yes in connect().",
                RuntimeWarning,
                stacklevel=2,
            )

    sql = "\nGO\n".join(stmts)
    sqlcmd = sqlcmd_base(user, password, container)
    _load_and_backup(container, sqlcmd, sql, "/tmp/_fixture_stmts.sql")


# ---------------------------------------------------------------------------
# fkr__seed row-generation helper
# ---------------------------------------------------------------------------

def seed_sql(n: int) -> list[str]:
    """Return SQL statements that create fkr__seed(pk INT PRIMARY KEY) with n rows.

    Rows are pk 0..n-1.  Uses INSERT-SELECT doubling — no cross-join, no
    UNION ALL.  No separators (GO / ;): each element is one executable
    statement, ready for ``execute_statements()``.

    Works on SQL Server 2017+, MySQL 5.7+, PostgreSQL 9.4+, Oracle 12c+.
    The subquery alias form ``FROM (SELECT pk FROM fkr__seed) AS _s`` avoids
    MySQL's restriction on self-referencing the modified table directly.
    """
    stmts: list[str] = [
        "CREATE TABLE fkr__seed (pk INT PRIMARY KEY)",
        "INSERT INTO fkr__seed (pk) VALUES (0)",
    ]
    current = 1
    while current < n:
        need = n - current
        where = f" WHERE pk < {need}" if need < current else ""
        stmts.append(
            f"INSERT INTO fkr__seed"
            f" SELECT pk + {current}"
            f" FROM (SELECT pk FROM fkr__seed) AS _s{where}"
        )
        current = (current + need) if need < current else current * 2
    return stmts


# ---------------------------------------------------------------------------
# Dirty-backup concurrent helper
# ---------------------------------------------------------------------------

def dirty_backup_concurrent(
    container: str,
    user: str,
    password: str,
    db_name: str,
    bak_container_path: str,
    dml_sql: str,
    reset_stmts: list[str],
    *,
    del_delay_s: float = 0.030,
    hold_s: float = 0.020,
    max_retries: int = 20,
    require_cds: bool = False,
    compression: bool = False,
) -> None:
    """Run BACKUP DATABASE concurrently with DML until the commit lands in the log tail.

    Retries up to *max_retries* times.  Each attempt:

    1. Execute each statement in *reset_stmts* on a utility connection
       (restores the table to its pre-DML state).
    2. Start a DML thread: sleep *del_delay_s*, execute *dml_sql*, sleep
       *hold_s*, COMMIT.
    3. BACKUP DATABASE on a backup connection (no ``STATS`` — using
       ``STATS=N`` causes the driver to return after the first progress
       message, producing a truncated 8 KB file).
    4. Copy the backup out to a temporary host path and inspect it with
       ``logtail_from_bak`` for ``committed_delete_slots`` / ``redo_patches``.

    When *require_cds* is ``True`` the loop continues until
    ``committed_delete_slots > 0``; otherwise it accepts ``cds + rp > 0``.
    Raises ``RuntimeError`` after *max_retries* exhausted attempts.

    Background: ``mssql_python`` connects over TCP directly from the host,
    eliminating the ~200 ms ``podman exec`` round-trip overhead.  The 30–50 ms
    timing window is reliably hit within 3–5 attempts on average.
    """
    import threading
    import time

    from mssqlbak.logtail import logtail_from_bak

    dml_conn  = connect(container, user, password, database=db_name,  autocommit=False, timeout=300)
    bak_conn  = connect(container, user, password, database="master",  autocommit=True,  timeout=300)
    util_conn = connect(container, user, password, database=db_name,   autocommit=True,  timeout=300)
    tmp = Path("/private/tmp/_dirty_bak_concurrent_verify.bak")

    try:
        for attempt in range(1, max_retries + 1):
            for stmt in reset_stmts:
                util_conn.cursor().execute(stmt)

            def _dml(conn: object = dml_conn, sql: str = dml_sql) -> None:
                time.sleep(del_delay_s)
                conn.cursor().execute(sql)  # type: ignore[union-attr]
                time.sleep(hold_s)
                conn.commit()  # type: ignore[union-attr]

            t = threading.Thread(target=_dml, daemon=True)
            t.start()

            _comp = ",COMPRESSION" if compression else ""
            bak_conn.cursor().execute(
                f"BACKUP DATABASE [{db_name}] TO DISK=N'{bak_container_path}' "
                f"WITH FORMAT,INIT,BUFFERCOUNT=1,MAXTRANSFERSIZE=65536{_comp}"
            )
            t.join(timeout=del_delay_s + hold_s + 10)

            _copy_out(container, bak_container_path, tmp)
            result = logtail_from_bak(tmp)
            cds    = len(result.committed_delete_slots)
            rp     = len(result.redo_patches)
            ok     = (cds > 0) if require_cds else (cds + rp > 0)
            if ok:
                print(
                    f"    attempt {attempt}: "
                    f"committed_delete_slots={cds}  redo_patches={rp}  ✓",
                    file=sys.stderr,
                )
                return
            print(
                f"    attempt {attempt}: timing missed "
                f"(cds={cds} rp={rp}) — retrying …",
                file=sys.stderr,
            )

        raise RuntimeError(
            f"dirty_backup_concurrent: failed to capture DML commit in log tail "
            f"after {max_retries} attempts"
        )
    finally:
        dml_conn.close()
        bak_conn.close()
        util_conn.close()
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Skip guard
# ---------------------------------------------------------------------------

def skip_if_exists(*paths: Path, force: bool = False) -> bool:
    """Return True (and print a skip message to stderr) if ALL *paths* exist.

    Pass ``force=True`` to bypass the guard and always regenerate.

    Usage::

        if skip_if_exists(OUT_PATH, force=args.force):
            return 0
    """
    if force:
        return False
    if all(p.exists() for p in paths):
        names = ", ".join(p.name for p in paths)
        print(f"skip (already exists): {names}", file=sys.stderr)
        return True
    return False


def skip_if_server_older_than(min_year: int) -> bool:
    """Return True when the current FIXTURE_DIR targets a SQL Server older than *min_year*.

    Reads the ``FIXTURE_DIR`` environment variable (set by ``fixture_run
    all-versions``) and extracts the year from its directory name
    (e.g. ``tests/fixtures_2019`` → 2019).  If the year is below *min_year*,
    prints a skip message to stderr and returns True so the caller can exit
    cleanly with code 0.

    When ``FIXTURE_DIR`` is not set or contains no recognisable year the guard
    is not applied (returns False) so manual one-off invocations are never
    blocked.

    Usage::

        # At the top of main(), before fixture_credentials():
        if skip_if_server_older_than(2019):
            return 0
    """
    import re
    fixture_dir = os.environ.get("FIXTURE_DIR", "")
    m = re.search(r"fixtures_(\d{4})", fixture_dir)
    if not m:
        return False
    year = int(m.group(1))
    if year < min_year:
        print(
            f"skip (requires SS{min_year}+; current target is SS{year})",
            file=sys.stderr,
        )
        return True
    return False


# ---------------------------------------------------------------------------
# Credential / env helper
# ---------------------------------------------------------------------------

def fixture_credentials() -> tuple[str, str, str]:
    """Return *(user, password, container)* from environment variables.

    Exits with a helpful message if ``FIXTURE_DBA_PASSWORD`` is not set.
    """
    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    password = os.environ.get("FIXTURE_DBA_PASSWORD")
    if not password:
        sys.exit(
            "error: FIXTURE_DBA_PASSWORD not set — "
            "run via: python -m tools.fixture_run <command>"
        )
    container = discover_container()
    return user, password, container
