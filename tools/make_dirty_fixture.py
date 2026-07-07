#!/usr/bin/env python3
"""Build the dirty/fuzzy backup reference ``.bak`` fixtures.

Produces two fixtures that characterise how mssqlbak behaves when reading a
backup taken while the source database was live (i.e. without the log-replay
step that SQL Server normally performs on restore):

Scenario A — concurrent inserts
    100 rows are committed before the backup starts ("pre_backup").  A
    background sqlcmd loop keeps inserting "concurrent_N" rows throughout the
    backup.  The backup completes, then inserts stop.
    Ground truth: ``pre_backup_rows=100``, ``backup_started_with_live_writes=True``.
    What mssqlbak sees: all 100 pre-backup rows; some but not all concurrent rows.

Scenario B — uncommitted transaction
    50 rows are committed ("pre_tx").  A second sqlcmd session opens a
    transaction, inserts 20 more rows ("in_tx_N"), and holds the transaction
    open via ``WAITFOR DELAY`` while the backup runs in the main thread.  The
    transaction is then rolled back.
    Ground truth: ``committed_rows=50``, ``uncommitted_rows=20`` (rolled back).
    What mssqlbak sees: either 50 or 70 rows depending on whether SQL Server
    had flushed the dirty pages when the backup read those pages.

Output files (``tests/fixtures/``):

- ``dirtycoverage_concurrent.bak``
- ``dirtycoverage_uncommitted.bak``
- ``dirty_ground_truth.json``

Connection (same pattern as other make_* tools):
- Container auto-discovered from ``podman ps`` (image ``mssql/server``).
- ``FIXTURE_DBA_USER`` (default ``sa``) and ``FIXTURE_DBA_PASSWORD`` (required).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "DirtyCoverage"
MSSQL_IMAGE_MATCH = "mssql/server"

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))

_DIRTY_BAK_DIR = "/tmp"
_D = "dirtycoverage"  # lowercase prefix used for all dirty BAK paths in the container

CONTAINER_BAK_CONCURRENT         = f"{_DIRTY_BAK_DIR}/{_D}_concurrent.bak"
CONTAINER_BAK_UNCOMMITTED         = f"{_DIRTY_BAK_DIR}/{_D}_uncommitted.bak"
CONTAINER_BAK_TRUNCATE            = f"{_DIRTY_BAK_DIR}/{_D}_truncate.bak"
CONTAINER_BAK_ADDCOL              = f"{_DIRTY_BAK_DIR}/{_D}_addcol.bak"
CONTAINER_BAK_DROPTABLE           = f"{_DIRTY_BAK_DIR}/{_D}_droptable.bak"
CONTAINER_BAK_DROPCOL             = f"{_DIRTY_BAK_DIR}/{_D}_dropcol.bak"
CONTAINER_BAK_ADDNOTNULL          = f"{_DIRTY_BAK_DIR}/{_D}_addnotnull.bak"
CONTAINER_BAK_ALTERCOL            = f"{_DIRTY_BAK_DIR}/{_D}_altercol.bak"
CONTAINER_BAK_CREATETABLE         = f"{_DIRTY_BAK_DIR}/{_D}_createtable.bak"
CONTAINER_BAK_REBUILDIDX          = f"{_DIRTY_BAK_DIR}/{_D}_rebuildidx.bak"
CONTAINER_BAK_CREATEIDX           = f"{_DIRTY_BAK_DIR}/{_D}_createidx.bak"
CONTAINER_BAK_DROPIDX             = f"{_DIRTY_BAK_DIR}/{_D}_dropidx.bak"
CONTAINER_BAK_DELETE              = f"{_DIRTY_BAK_DIR}/{_D}_delete.bak"
CONTAINER_BAK_UPDATE              = f"{_DIRTY_BAK_DIR}/{_D}_update.bak"
CONTAINER_BAK_ALTERCOL_REWRITE    = f"{_DIRTY_BAK_DIR}/{_D}_altercol_rewrite.bak"
CONTAINER_BAK_ALTERDB             = f"{_DIRTY_BAK_DIR}/{_D}_alterdb.bak"
CONTAINER_BAK_SAVEPOINT           = f"{_DIRTY_BAK_DIR}/{_D}_savepoint.bak"
CONTAINER_BAK_NESTED              = f"{_DIRTY_BAK_DIR}/{_D}_nested.bak"
CONTAINER_BAK_SWITCH              = f"{_DIRTY_BAK_DIR}/{_D}_switch.bak"
CONTAINER_BAK_TWO_TX              = f"{_DIRTY_BAK_DIR}/{_D}_two_tx.bak"
CONTAINER_BAK_RICH_UPDATE         = f"{_DIRTY_BAK_DIR}/{_D}_rich_update.bak"
CONTAINER_BAK_RICH_INSERT         = f"{_DIRTY_BAK_DIR}/{_D}_rich_insert.bak"
CONTAINER_BAK_NULL_UPDATE         = f"{_DIRTY_BAK_DIR}/{_D}_null_update.bak"
CONTAINER_BAK_ALLDIRTY            = f"{_DIRTY_BAK_DIR}/{_D}_alldirty.bak"
CONTAINER_BAK_NCHAR_DELETE        = f"{_DIRTY_BAK_DIR}/{_D}_nchar_delete.bak"
CONTAINER_BAK_HEAP_FORWARD        = f"{_DIRTY_BAK_DIR}/{_D}_heap_forward.bak"
CONTAINER_BAK_LARGE_DIRTY         = f"{_DIRTY_BAK_DIR}/{_D}_large_dirty.bak"
CONTAINER_BAK_LOB_UPDATE          = f"{_DIRTY_BAK_DIR}/{_D}_lob_update.bak"
CONTAINER_BAK_MAXROW              = f"{_DIRTY_BAK_DIR}/{_D}_maxrow.bak"
CONTAINER_BAK_TEMPORAL_UPDATE     = f"{_DIRTY_BAK_DIR}/{_D}_temporal_update.bak"
CONTAINER_BAK_SNAPSHOT_UPDATE     = f"{_DIRTY_BAK_DIR}/{_D}_snapshot_update.bak"
CONTAINER_BAK_COMMITTED_DELETE    = f"{_DIRTY_BAK_DIR}/{_D}_committed_delete.bak"
CONTAINER_BAK_COMMITTED_UPDATE    = f"{_DIRTY_BAK_DIR}/{_D}_committed_update.bak"
CONTAINER_BAK_COMMITTED_DELETE_V3 = f"{_DIRTY_BAK_DIR}/{_D}_committed_delete_v3.bak"
CONTAINER_BAK_COMMITTED_UPDATE_V3 = f"{_DIRTY_BAK_DIR}/{_D}_committed_update_v3.bak"
CONTAINER_SQL = "/tmp/dirty_load.sql"

PRE_BACKUP_ROWS = 100       # Scenario A: rows committed before backup starts
CONCURRENT_BATCH_SIZE = 10  # Scenario A: rows inserted per background loop iteration
PRE_TX_ROWS = 50            # Scenario B: rows committed before opening TX
UNCOMMITTED_ROWS = 20       # Scenario B: rows inserted inside the open (rolled-back) TX
TX_HOLD_SECONDS = 20        # Scenario B: how long to hold the open transaction

# Scenario C — TRUNCATE TABLE during backup
DDL_TRUNCATE_ROWS = 500     # rows pre-TRUNCATE (enough data to make backup non-trivial)
DDL_TRUNCATE_DELAY_S = 10   # seconds to hold the TRUNCATE in a background session

# Scenario D — ALTER TABLE ADD COLUMN, then take a static backup
DDL_ADDCOL_PRE_ROWS = 50    # rows inserted before ADD COLUMN
DDL_ADDCOL_POST_ROWS = 10   # rows inserted after ADD COLUMN (have the new column value)

# Scenario E — DROP TABLE during backup
DDL_DROP_ROWS = 500         # rows in the table that gets dropped mid-backup
DDL_DROP_DELAY_MS = 100     # ms delay before issuing DROP TABLE (fires during backup)


def _run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, **kwargs)


def _popen(cmd: list[str]) -> subprocess.Popen[str]:
    return subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


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


_TRANSIENT_ERRS = (
    "Login timeout expired",
    "TCP Provider",
    "prelogin failure",
    "prelogin response",
    "unable to establish connection",
    "server too busy",
    "handshakes before login",
    "Error code 0x68",  # ECONNRESET inside the ODBC driver
)


def _exec_sql(
    container: str,
    sqlcmd: list[str],
    sql: str,
    sql_file: str = CONTAINER_SQL,
    *,
    retries: int = 3,
    retry_delay: float = 8.0,
) -> str:
    """Copy SQL into container and run sqlcmd; return stdout.

    Retries up to *retries* times on transient connection errors (e.g. SS2025
    briefly refusing new connections while a concurrent backup Popen finishes).
    Delay doubles on each retry: 8 s, 16 s, 24 s.
    """
    local = "/tmp/_dirty_tmp.sql"
    with open(local, "w", encoding="utf-8") as f:
        f.write(sql)
    cp = _run(["podman", "cp", local, f"{container}:{sql_file}"])
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp failed: {cp.stderr}")

    last_proc = None
    for attempt in range(retries + 1):
        last_proc = _run(["podman", "exec", container] + sqlcmd + ["-i", sql_file])
        if last_proc.returncode == 0:
            return last_proc.stdout
        combined = last_proc.stdout + last_proc.stderr
        is_transient = any(e.lower() in combined.lower() for e in _TRANSIENT_ERRS)
        if is_transient and attempt < retries:
            wait = retry_delay * (attempt + 1)
            print(
                f"  [retry {attempt + 1}/{retries}] transient connection error; "
                f"waiting {wait:.0f}s …",
                file=sys.stderr,
            )
            time.sleep(wait)
            continue
        break

    assert last_proc is not None
    raise RuntimeError(
        f"sqlcmd failed:\nSTDOUT:\n{last_proc.stdout}\nSTDERR:\n{last_proc.stderr}"
    )


def _exec_sql_bg(container: str, sqlcmd: list[str], sql: str, sql_file: str) -> subprocess.Popen[str]:
    """Copy SQL into container, launch sqlcmd in background, return Popen handle."""
    local = f"/tmp/_dirty_bg_{os.getpid()}.sql"
    with open(local, "w", encoding="utf-8") as f:
        f.write(sql)
    cp = _run(["podman", "cp", local, f"{container}:{sql_file}"])
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp (bg) failed: {cp.stderr}")
    return _popen(["podman", "exec", container] + sqlcmd + ["-i", sql_file])


def _discover_mssql_host_port(container: str) -> tuple[str, int]:
    """Return (host, port) for direct TCP connections to the SQL Server container.

    Reads the Podman port mapping for 1433/tcp.  Falls back to 127.0.0.1:1433
    if the mapping is unavailable (e.g. host-network mode).
    """
    proc = _run(["podman", "port", container, "1433/tcp"])
    if proc.returncode == 0:
        # output: "0.0.0.0:30000\n"
        line = proc.stdout.strip()
        if ":" in line:
            _, port_str = line.rsplit(":", 1)
            return "127.0.0.1", int(port_str)
    return "127.0.0.1", 1433


def _mssqlpy_dirty_backup(
    container: str,
    user: str,
    password: str,
    db: str,
    bak_path_container: str,
    dml_sql: str,
    reset_sql: str,
    *,
    del_delay_s: float = 0.030,
    hold_s: float = 0.020,
    max_retries: int = 20,
    require_cds: bool = False,
) -> None:
    """Run a dirty backup via mssql_python so the DML COMMIT lands in the log tail.

    The technique (validated experimentally):

    1. Execute *reset_sql* on a utility connection to restore the table to its
       initial state (required between retries because the DML commits and
       removes rows, so subsequent attempts would find nothing to modify).
    2. Pre-establish two connections (no per-attempt connection overhead).
    3. Start BACKUP DATABASE on the backup connection (no ``STATS`` — using
       ``STATS=N`` causes ``execute()`` to return after the first progress
       message, producing a truncated 8 KB file instead of a real backup).
    4. Concurrently, sleep *del_delay_s*, execute the DML, sleep *hold_s*,
       then COMMIT.  The DML fires while the backup is still reading data
       pages, so pages captured before the DML see the pre-DML live state.
       The COMMIT fires while the backup is still within its data-page-read
       window, so the COMMIT record lands in the log tail.
    5. After the backup completes, verify ``committed_delete_slots`` or
       ``redo_patches`` are non-empty.  Retry up to *max_retries* times if
       the timing window was missed.

    Background: ``mssql_python`` (unlike sqlcmd) connects directly over TCP
    from the host, eliminating ~200 ms of ``podman exec`` overhead per call.
    This makes the 30–50 ms timing window reliably hit-able with a retry loop
    that averages 3–5 attempts.
    """
    import threading
    import mssql_python
    from mssqlbak.logtail import logtail_from_bak

    host, port = _discover_mssql_host_port(container)
    conn_str = (
        f"SERVER={host},{port};"
        f"UID={user};PWD={password};"
        "TrustServerCertificate=yes;"
    )

    del_conn  = mssql_python.connect(conn_str + f"DATABASE={db};", autocommit=False, timeout=300)
    bak_conn  = mssql_python.connect(conn_str + "DATABASE=master;",  autocommit=True,  timeout=300)
    util_conn = mssql_python.connect(conn_str + f"DATABASE={db};",   autocommit=True,  timeout=300)
    tmp_host  = Path("/private/tmp/_mssqlpy_dirty_verify.bak")

    try:
        for attempt in range(1, max_retries + 1):
            # Restore the table to its pre-DML state before each attempt.
            util_conn.cursor().execute(reset_sql)

            def _dml():
                time.sleep(del_delay_s)
                del_conn.cursor().execute(dml_sql)
                time.sleep(hold_s)
                del_conn.commit()

            dml_thread = threading.Thread(target=_dml, daemon=True)
            dml_thread.start()

            bak_conn.cursor().execute(
                f"BACKUP DATABASE [{db}] TO DISK=N'{bak_path_container}' "
                "WITH FORMAT,INIT,BUFFERCOUNT=1,MAXTRANSFERSIZE=65536"
            )
            dml_thread.join(timeout=del_delay_s + hold_s + 10)

            _copy_out(container, bak_path_container, tmp_host)
            result = logtail_from_bak(tmp_host)
            cds = len(result.committed_delete_slots)
            rp  = len(result.redo_patches)
            ok  = (cds > 0) if require_cds else (cds + rp > 0)
            if ok:
                print(
                    f"    attempt {attempt}: committed_delete_slots={cds}  "
                    f"redo_patches={rp}  ✓"
                )
                return
            print(f"    attempt {attempt}: timing missed (log tail empty) — retrying …")
        raise RuntimeError(
            f"_mssqlpy_dirty_backup: failed to capture DML commit in log tail "
            f"after {max_retries} attempts"
        )
    finally:
        del_conn.close()
        bak_conn.close()
        util_conn.close()
        tmp_host.unlink(missing_ok=True)


def _copy_out(container: str, src: str, dst: Path) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cp = _run(["podman", "cp", f"{container}:{src}", str(dst)])
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp out failed: {cp.stderr}")
    return dst.stat().st_size


def _create_db_sql() -> str:
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
CREATE TABLE dirty_test (
  id      INT IDENTITY PRIMARY KEY,
  label   NVARCHAR(200) NOT NULL,
  phase   VARCHAR(30)   NOT NULL,
  seq     INT           NOT NULL DEFAULT 0
);
GO
"""


# ---------------------------------------------------------------------------
# Scenario A — concurrent inserts
# ---------------------------------------------------------------------------

def _build_scenario_a(container: str, sqlcmd: list[str]) -> int:
    """Run Scenario A: backup taken while concurrent inserts are in flight.

    Returns the number of concurrent rows that were inserted during backup.
    """
    print("  creating database …")
    _exec_sql(container, sqlcmd, _create_db_sql())

    # Step 1: commit PRE_BACKUP_ROWS rows before the backup starts.
    pre_sql = "\n".join(
        f"INSERT INTO dirty_test(label, phase, seq) "
        f"VALUES(N'pre-backup row {i}', 'pre_backup', {i});"
        for i in range(1, PRE_BACKUP_ROWS + 1)
    )
    print(f"  inserting {PRE_BACKUP_ROWS} pre-backup rows …")
    _exec_sql(container, sqlcmd, f"USE [{DB_NAME}];\nGO\n{pre_sql}\nGO\n")

    # Step 2: launch a background insert loop — each iteration commits a batch.
    concurrent_sql_file = "/tmp/dirty_concurrent_bg.sql"
    concurrent_sql = f"""USE [{DB_NAME}];
GO
DECLARE @seq INT = 1;
WHILE @seq <= 200
BEGIN
  INSERT INTO dirty_test(label, phase, seq)
  VALUES(N'concurrent batch ' + CAST(@seq AS NVARCHAR), 'concurrent', @seq);
  WAITFOR DELAY '00:00:00.050';
  SET @seq = @seq + 1;
END;
GO
"""
    print("  starting background insert loop …")
    bg_proc = _exec_sql_bg(container, sqlcmd, concurrent_sql, concurrent_sql_file)

    # Give the loop a head-start (let a few rows land).
    time.sleep(0.5)

    # Step 3: take backup while the loop is running.
    print("  taking BACKUP DATABASE (concurrent writes in flight) …")
    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK_CONCURRENT}'
  WITH FORMAT, INIT;
GO
"""
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_a.sql")
    print("  backup complete; waiting for background loop to finish …")

    # Step 4: wait for background to finish and collect its exit code.
    stdout, stderr = bg_proc.communicate(timeout=60)
    if bg_proc.returncode not in (0, None):
        print(f"  warning: background sqlcmd exited {bg_proc.returncode}: {stderr[:200]}")

    # Step 5: query the final row count to learn how many concurrent rows landed.
    count_sql = (
        f"USE [{DB_NAME}];\n"
        f"GO\n"
        f"SET NOCOUNT ON;\n"
        f"SELECT COUNT(*) FROM dirty_test WHERE phase='concurrent';\n"
        f"GO\n"
    )
    out = _exec_sql(container, sqlcmd, count_sql, "/tmp/dirty_count_a.sql")
    # Find the first line that is a plain integer.
    concurrent_inserted = next(
        int(line.strip())
        for line in out.splitlines()
        if line.strip().lstrip("-").isdigit()
    )
    print(f"  concurrent rows inserted total: {concurrent_inserted}")
    return concurrent_inserted


# ---------------------------------------------------------------------------
# Scenario B — uncommitted transaction
# ---------------------------------------------------------------------------

def _build_scenario_b(container: str, sqlcmd: list[str]) -> None:
    """Run Scenario B: backup taken while a transaction is open (then rolled back)."""
    # Drop and recreate so Scenario B has a clean table (separate from A).
    print("  re-creating database for Scenario B …")
    _exec_sql(container, sqlcmd, _create_db_sql())

    # Step 1: commit PRE_TX_ROWS rows.
    pre_sql = "\n".join(
        f"INSERT INTO dirty_test(label, phase, seq) "
        f"VALUES(N'committed row {i}', 'pre_tx', {i});"
        for i in range(1, PRE_TX_ROWS + 1)
    )
    print(f"  inserting {PRE_TX_ROWS} committed rows …")
    _exec_sql(container, sqlcmd, f"USE [{DB_NAME}];\nGO\n{pre_sql}\nGO\n")

    # Step 2: open a long-running transaction in a background sqlcmd session.
    # It inserts UNCOMMITTED_ROWS rows then waits before rolling back.
    uncommitted_inserts = "\n".join(
        f"  INSERT INTO dirty_test(label, phase, seq) "
        f"VALUES(N'uncommitted row {i}', 'in_tx', {i});"
        for i in range(1, UNCOMMITTED_ROWS + 1)
    )
    tx_sql = f"""USE [{DB_NAME}];
GO
BEGIN TRANSACTION;
{uncommitted_inserts}
WAITFOR DELAY '00:00:{TX_HOLD_SECONDS:02d}';
ROLLBACK TRANSACTION;
GO
"""
    tx_sql_file = "/tmp/dirty_tx_bg.sql"
    print(f"  opening background transaction ({UNCOMMITTED_ROWS} uncommitted rows, "
          f"held for {TX_HOLD_SECONDS}s) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, tx_sql, tx_sql_file)

    # Wait for the transaction to start and dirty pages to be written.
    time.sleep(2)

    # Step 3: take the backup while the transaction is open.
    print("  taking BACKUP DATABASE (uncommitted TX open) …")
    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK_UNCOMMITTED}'
  WITH FORMAT, INIT;
GO
"""
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_b.sql")
    print("  backup complete; waiting for TX rollback …")

    # Step 4: wait for the background TX to roll back.
    bg_proc.communicate(timeout=TX_HOLD_SECONDS + 10)
    print("  transaction rolled back")


# ---------------------------------------------------------------------------
# Scenario C — TRUNCATE TABLE during backup
# ---------------------------------------------------------------------------

def _build_scenario_c(container: str, sqlcmd: list[str]) -> int:
    """Run Scenario C: BACKUP DATABASE taken while TRUNCATE TABLE is in progress.

    Returns the number of rows that were in the table before the TRUNCATE.

    SQL Server allows TRUNCATE TABLE to run concurrently with a backup.
    TRUNCATE deallocates pages atomically in the buffer pool.  The backup may
    capture the table's pages before the TRUNCATE (seeing DDL_TRUNCATE_ROWS
    rows), after it (seeing 0 rows), or some mix if the TRUNCATE spans the
    backup window.  Either 0 or DDL_TRUNCATE_ROWS is a valid outcome;
    any other count would indicate a bug in the parser.
    """
    db2 = "DirtyTruncate"
    print(f"  creating database {db2} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db2}') IS NOT NULL BEGIN
  ALTER DATABASE [{db2}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db2}];
END;
GO
CREATE DATABASE [{db2}];
GO
USE [{db2}];
GO
CREATE TABLE trunc_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    inserts = "\n".join(
        f"INSERT INTO trunc_test(label, phase) VALUES(N'row {i}', 'pre_trunc');"
        for i in range(1, DDL_TRUNCATE_ROWS + 1)
    )
    print(f"  inserting {DDL_TRUNCATE_ROWS} rows …")
    _exec_sql(container, sqlcmd, f"USE [{db2}];\nGO\n{inserts}\nGO\n")

    # Background: wait, then TRUNCATE (fires mid-backup if timing lines up).
    trunc_sql = f"""USE [{db2}];
GO
WAITFOR DELAY '00:00:01';
TRUNCATE TABLE trunc_test;
GO
"""
    trunc_sql_file = "/tmp/dirty_trunc_bg.sql"
    print("  starting background TRUNCATE (1 s delay) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, trunc_sql, trunc_sql_file)

    # Take backup while TRUNCATE may be in progress.
    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db2}] TO DISK=N'{CONTAINER_BAK_TRUNCATE}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (TRUNCATE may fire during backup) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_c.sql")
    print("  backup complete; waiting for TRUNCATE to finish …")
    stdout, stderr = bg_proc.communicate(timeout=30)
    if bg_proc.returncode not in (0, None):
        print(f"  warning: TRUNCATE sqlcmd exited {bg_proc.returncode}: {stderr[:200]}")

    return DDL_TRUNCATE_ROWS


# ---------------------------------------------------------------------------
# Scenario D — ALTER TABLE ADD COLUMN, then take a static backup
# ---------------------------------------------------------------------------

def _build_scenario_d(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Run Scenario D: ADD COLUMN backup.

    Returns (pre_rows, post_rows):
      pre_rows  — rows inserted BEFORE the ADD COLUMN (column will be NULL in backup)
      post_rows — rows inserted AFTER the ADD COLUMN (column will have a value)

    This scenario is deterministic: the entire DDL + inserts happen before the
    backup starts.  It tests whether mssqlbak correctly handles the SQL Server
    metadata-only column addition, where existing rows do not have a physical
    slot for the new column and the engine returns NULL for them.
    """
    db3 = "DirtyAddCol"
    print(f"  creating database {db3} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db3}') IS NOT NULL BEGIN
  ALTER DATABASE [{db3}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db3}];
END;
GO
CREATE DATABASE [{db3}];
GO
USE [{db3}];
GO
CREATE TABLE addcol_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    pre_inserts = "\n".join(
        f"INSERT INTO addcol_test(label, phase) VALUES(N'pre-col row {i}', 'pre_ddl');"
        for i in range(1, DDL_ADDCOL_PRE_ROWS + 1)
    )
    print(f"  inserting {DDL_ADDCOL_PRE_ROWS} rows before ADD COLUMN …")
    _exec_sql(container, sqlcmd, f"USE [{db3}];\nGO\n{pre_inserts}\nGO\n")

    # ALTER TABLE ADD COLUMN — nullable with no default triggers metadata-only
    # operation in SQL Server 2019+.  Existing rows return NULL for the new column.
    print("  ALTER TABLE ADD COLUMN extra VARCHAR(100) NULL …")
    _exec_sql(
        container, sqlcmd,
        f"USE [{db3}];\nGO\nALTER TABLE addcol_test ADD extra VARCHAR(100) NULL;\nGO\n",
    )

    post_inserts = "\n".join(
        f"INSERT INTO addcol_test(label, phase, extra) "
        f"VALUES(N'post-col row {i}', 'post_ddl', N'extra_value_{i}');"
        for i in range(1, DDL_ADDCOL_POST_ROWS + 1)
    )
    print(f"  inserting {DDL_ADDCOL_POST_ROWS} rows after ADD COLUMN …")
    _exec_sql(container, sqlcmd, f"USE [{db3}];\nGO\n{post_inserts}\nGO\n")

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db3}] TO DISK=N'{CONTAINER_BAK_ADDCOL}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (static, post-DDL) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_d.sql")

    return DDL_ADDCOL_PRE_ROWS, DDL_ADDCOL_POST_ROWS


# ---------------------------------------------------------------------------
# Scenario E — DROP TABLE during backup
# ---------------------------------------------------------------------------

def _build_scenario_e(container: str, sqlcmd: list[str]) -> int:
    """Run Scenario E: DROP TABLE fires while a backup is in progress.

    Returns the number of rows that were in the table before the DROP.

    SQL Server allows DROP TABLE to run concurrently with a backup.  Depending
    on timing the backup may capture the table's pages (seeing the rows) or
    capture only the catalog update (table absent from schema).  Either
    outcome is valid; the test verifies mssqlbak does not crash in either case.
    """
    db4 = "DirtyDropTable"
    print(f"  creating database {db4} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db4}') IS NOT NULL BEGIN
  ALTER DATABASE [{db4}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db4}];
END;
GO
CREATE DATABASE [{db4}];
GO
USE [{db4}];
GO
-- survivor_test is a stable table that ensures the backup always has content.
CREATE TABLE survivor_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL
);
GO
CREATE TABLE drop_target (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    # Fill survivor_test so the backup has enough data to be non-trivial.
    survivor_inserts = "\n".join(
        f"INSERT INTO survivor_test(label) VALUES(N'survivor row {i}');"
        for i in range(1, 201)
    )
    drop_inserts = "\n".join(
        f"INSERT INTO drop_target(label, phase) VALUES(N'drop row {i}', 'pre_drop');"
        for i in range(1, DDL_DROP_ROWS + 1)
    )
    print("  inserting rows into both tables …")
    _exec_sql(
        container, sqlcmd,
        f"USE [{db4}];\nGO\n{survivor_inserts}\n{drop_inserts}\nGO\n",
    )

    # Background: small delay then DROP TABLE.
    drop_sql = f"""USE [{db4}];
GO
WAITFOR DELAY '00:00:01';
DROP TABLE drop_target;
GO
"""
    drop_sql_file = "/tmp/dirty_drop_bg.sql"
    print("  starting background DROP TABLE (1 s delay) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, drop_sql, drop_sql_file)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db4}] TO DISK=N'{CONTAINER_BAK_DROPTABLE}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (DROP TABLE may fire during backup) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_e.sql")
    print("  backup complete; waiting for DROP to finish …")
    stdout, stderr = bg_proc.communicate(timeout=30)
    if bg_proc.returncode not in (0, None):
        print(f"  warning: DROP sqlcmd exited {bg_proc.returncode}: {stderr[:200]}")

    return DDL_DROP_ROWS


# ---------------------------------------------------------------------------
# Scenario F — ALTER TABLE DROP COLUMN, then static backup
# ---------------------------------------------------------------------------

def _build_scenario_f(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Run Scenario F: backup of a table where a column was dropped.

    Returns (pre_drop_rows, post_drop_rows):
      pre_drop_rows  — rows inserted before DROP COLUMN (have ghost byte in record)
      post_drop_rows — rows inserted after DROP COLUMN (clean format)

    SQL Server marks the dropped column in syscolpars as deleted and removes its
    sysrscols storage entry.  mssqlbak will either skip it (if syscolpars row is
    gone) or include it (if a ghost row remains).  The test empirically determines
    which case applies and whether row decoding is correct.
    """
    db = "DirtyDropCol"
    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE dropcol_test (
  id     INT IDENTITY PRIMARY KEY,
  label  NVARCHAR(200) NOT NULL,
  extra  VARCHAR(100) NULL,
  phase  VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    pre = 50
    pre_inserts = "\n".join(
        f"INSERT INTO dropcol_test(label, extra, phase) "
        f"VALUES(N'pre-drop row {i}', 'extra_{i}', 'pre_drop');"
        for i in range(1, pre + 1)
    )
    print(f"  inserting {pre} rows with extra column …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{pre_inserts}\nGO\n")

    print("  ALTER TABLE DROP COLUMN extra …")
    _exec_sql(
        container, sqlcmd,
        f"USE [{db}];\nGO\nALTER TABLE dropcol_test DROP COLUMN extra;\nGO\n",
    )

    post = 10
    post_inserts = "\n".join(
        f"INSERT INTO dropcol_test(label, phase) "
        f"VALUES(N'post-drop row {i}', 'post_drop');"
        for i in range(1, post + 1)
    )
    print(f"  inserting {post} rows after DROP COLUMN …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{post_inserts}\nGO\n")

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_DROPCOL}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (static, post-DROP COLUMN) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_f.sql")
    return pre, post


# ---------------------------------------------------------------------------
# Scenario G — ALTER TABLE ADD COLUMN NOT NULL WITH DEFAULT, then static backup
# ---------------------------------------------------------------------------

def _build_scenario_g(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Run Scenario G: backup after ADD COLUMN NOT NULL with a default value.

    Returns (pre_rows, post_rows).

    SQL Server rewrites ALL existing rows when a NOT NULL column with a DEFAULT
    is added in older compat modes, or uses a metadata-only approach with a
    persisted default in SQL Server 2012+.  Either way, mssqlbak must return the
    default value for pre-DDL rows.
    """
    db = "DirtyAddNotNull"
    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE addnotnull_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    pre = 50
    pre_inserts = "\n".join(
        f"INSERT INTO addnotnull_test(label, phase) VALUES(N'pre-col row {i}', 'pre_ddl');"
        for i in range(1, pre + 1)
    )
    print(f"  inserting {pre} rows before ADD COLUMN NOT NULL …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{pre_inserts}\nGO\n")

    print("  ALTER TABLE ADD COLUMN score INT NOT NULL DEFAULT 42 …")
    _exec_sql(
        container, sqlcmd,
        (
            f"USE [{db}];\nGO\n"
            f"ALTER TABLE addnotnull_test ADD score INT NOT NULL DEFAULT 42;\n"
            f"GO\n"
        ),
    )

    post = 10
    post_inserts = "\n".join(
        f"INSERT INTO addnotnull_test(label, phase, score) "
        f"VALUES(N'post-col row {i}', 'post_ddl', {i * 10});"
        for i in range(1, post + 1)
    )
    print(f"  inserting {post} rows after ADD COLUMN …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{post_inserts}\nGO\n")

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_ADDNOTNULL}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (static, post-DDL) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_g.sql")
    return pre, post


# ---------------------------------------------------------------------------
# Scenario H — ALTER TABLE ALTER COLUMN (compatible type), then static backup
# ---------------------------------------------------------------------------

def _build_scenario_h(container: str, sqlcmd: list[str]) -> int:
    """Run Scenario H: metadata-only column type change, then static backup.

    Returns the number of rows.

    Widening a VARCHAR column (e.g. VARCHAR(50) → VARCHAR(200)) is a
    metadata-only operation in SQL Server — no row rewrites occur.  Existing
    rows retain their original byte lengths; mssqlbak should decode them
    correctly using the new max_length from the catalog.
    """
    db = "DirtyAlterCol"
    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE altercol_test (
  id    INT IDENTITY PRIMARY KEY,
  label VARCHAR(50)  NOT NULL,
  phase VARCHAR(30)  NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    rows = 50
    inserts = "\n".join(
        f"INSERT INTO altercol_test(label, phase) VALUES('label_{i:03d}', 'pre_ddl');"
        for i in range(1, rows + 1)
    )
    print(f"  inserting {rows} rows with VARCHAR(50) label …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{inserts}\nGO\n")

    print("  ALTER TABLE ALTER COLUMN label VARCHAR(200) …")
    _exec_sql(
        container, sqlcmd,
        (
            f"USE [{db}];\nGO\n"
            f"ALTER TABLE altercol_test ALTER COLUMN label VARCHAR(200) NOT NULL;\n"
            f"GO\n"
        ),
    )

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_ALTERCOL}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (static, post-ALTER COLUMN) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_h.sql")
    return rows


# ---------------------------------------------------------------------------
# Scenario I — CREATE TABLE during backup
# ---------------------------------------------------------------------------

def _build_scenario_i(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Run Scenario I: CREATE TABLE fires during backup.

    Returns (stable_rows, new_rows).

    A large stable table ensures the backup takes long enough for the CREATE
    to potentially fire mid-scan.  The new table's visibility in mssqlbak's
    schema is timing-dependent.
    """
    db = "DirtyCreateTable"
    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE stable_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    stable = 300
    stable_inserts = "\n".join(
        f"INSERT INTO stable_test(label) VALUES(N'stable row {i}');"
        for i in range(1, stable + 1)
    )
    print(f"  inserting {stable} rows into stable_test …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{stable_inserts}\nGO\n")

    new_rows = 10
    create_sql = f"""USE [{db}];
GO
WAITFOR DELAY '00:00:01';
CREATE TABLE new_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL
);
GO
""" + "\n".join(
        f"INSERT INTO new_test(label) VALUES(N'new row {i}');"
        for i in range(1, new_rows + 1)
    ) + "\nGO\n"

    create_sql_file = "/tmp/dirty_create_bg.sql"
    print("  starting background CREATE TABLE (1 s delay) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, create_sql, create_sql_file)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_CREATETABLE}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (CREATE TABLE may fire during backup) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_i.sql")
    print("  backup complete; waiting for CREATE TABLE to finish …")
    bg_proc.communicate(timeout=30)
    return stable, new_rows


# ---------------------------------------------------------------------------
# Scenario J — ALTER INDEX REBUILD during backup
# ---------------------------------------------------------------------------

def _build_scenario_j(container: str, sqlcmd: list[str]) -> int:
    """Run Scenario J: ALTER INDEX REBUILD fires during backup.

    Returns the row count.  Index rebuild does not alter data page content
    (only the clustered index leaf order may change); mssqlbak must return
    all rows without crashing.
    """
    db = "DirtyRebuildIdx"
    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE ridx_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  score INT           NOT NULL DEFAULT 0
);
GO
CREATE NONCLUSTERED INDEX ix_ridx_score ON ridx_test(score);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    rows = 300
    inserts = "\n".join(
        f"INSERT INTO ridx_test(label, score) VALUES(N'row {i}', {i % 100});"
        for i in range(1, rows + 1)
    )
    print(f"  inserting {rows} rows …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{inserts}\nGO\n")

    rebuild_sql = f"""USE [{db}];
GO
WAITFOR DELAY '00:00:01';
ALTER INDEX ix_ridx_score ON ridx_test REBUILD;
GO
"""
    rebuild_sql_file = "/tmp/dirty_rebuild_bg.sql"
    print("  starting background ALTER INDEX REBUILD (1 s delay) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, rebuild_sql, rebuild_sql_file)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_REBUILDIDX}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (ALTER INDEX REBUILD may fire during backup) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_j.sql")
    print("  backup complete; waiting for REBUILD to finish …")
    bg_proc.communicate(timeout=30)
    return rows


# ---------------------------------------------------------------------------
# Scenario K — CREATE INDEX and DROP INDEX during backup
# ---------------------------------------------------------------------------

def _build_scenario_k(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Run Scenario K: CREATE INDEX and DROP INDEX during backup (two sub-fixtures).

    Returns (create_rows, drop_rows).  Both index operations affect only
    non-clustered index pages; data pages are unchanged and mssqlbak must
    return all rows without crashing.
    """
    db_create = "DirtyCreateIdx"
    db_drop   = "DirtyDropIdx"
    rows = 300

    for db, tag, bak_path in [
        (db_create, "create", CONTAINER_BAK_CREATEIDX),
        (db_drop,   "drop",   CONTAINER_BAK_DROPIDX),
    ]:
        print(f"  creating database {db} …")
        has_idx = tag == "drop"
        setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE kidx_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  score INT           NOT NULL DEFAULT 0
);
GO
"""
        if has_idx:
            setup_sql += "CREATE NONCLUSTERED INDEX ix_kidx_score ON kidx_test(score);\nGO\n"
        _exec_sql(container, sqlcmd, setup_sql)

        inserts = "\n".join(
            f"INSERT INTO kidx_test(label, score) VALUES(N'row {i}', {i % 100});"
            for i in range(1, rows + 1)
        )
        print(f"  inserting {rows} rows …")
        _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{inserts}\nGO\n")

        if tag == "create":
            ddl_sql = f"""USE [{db}];
GO
WAITFOR DELAY '00:00:01';
CREATE NONCLUSTERED INDEX ix_kidx_score ON kidx_test(score);
GO
"""
        else:
            ddl_sql = f"""USE [{db}];
GO
WAITFOR DELAY '00:00:01';
DROP INDEX ix_kidx_score ON kidx_test;
GO
"""
        ddl_sql_file = f"/tmp/dirty_{tag}idx_bg.sql"
        print(f"  starting background {tag.upper()} INDEX (1 s delay) …")
        bg_proc = _exec_sql_bg(container, sqlcmd, ddl_sql, ddl_sql_file)

        backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{bak_path}'
  WITH FORMAT, INIT;
GO
"""
        print(f"  taking BACKUP DATABASE ({tag.upper()} INDEX may fire during backup) …")
        _exec_sql(container, sqlcmd, backup_sql, f"/tmp/dirty_bak_k_{tag}.sql")
        print("  backup complete; waiting for DDL to finish …")
        bg_proc.communicate(timeout=30)

    return rows, rows


# ---------------------------------------------------------------------------
# Scenario L — Uncommitted DELETE (ghost rows) during backup
# ---------------------------------------------------------------------------

def _build_scenario_l(container: str, sqlcmd: list[str]) -> tuple[int, int, int]:
    """Run Scenario L: backup while an uncommitted DELETE is open.

    Returns (committed_rows, delete_target_rows, hold_seconds).

    Setup:
      - ``committed_rows`` rows with phase='committed' are inserted and committed.
      - ``delete_target_rows`` rows with phase='delete_target' are inserted and committed.
      - A background session opens a transaction, DELETEs all delete_target rows, and
        holds the transaction open via WAITFOR DELAY while the backup runs.
      - The transaction is rolled back after the backup.

    What SQL Server does:
      When a row is deleted, SQL Server immediately marks the slot as a *ghost*
      (status bits A bit 6 set, record type 6 = GhostData) and holds an exclusive
      row lock.  The backup reads pages without acquiring row locks, so it may
      capture the page with the ghost slot.  mssqlbak's ``fixedvar_emittable``
      already filters ghost records — so the deleted rows are invisible even though
      the delete was rolled back afterwards.

    Gap: mssqlbak has no log-tail mechanism to undo ghost DELETEs, so the backup
    may show fewer rows than SQL Server would return after applying the log tail.
    """
    db = "DirtyDeleteRows"
    committed = 50
    delete_target = 20
    hold_seconds = 20

    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE delete_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    committed_inserts = "\n".join(
        f"INSERT INTO delete_test(label, phase) VALUES(N'committed row {i}', 'committed');"
        for i in range(1, committed + 1)
    )
    target_inserts = "\n".join(
        f"INSERT INTO delete_test(label, phase) VALUES(N'delete target {i}', 'delete_target');"
        for i in range(1, delete_target + 1)
    )
    print(f"  inserting {committed} committed rows + {delete_target} delete-target rows …")
    _exec_sql(
        container, sqlcmd,
        f"USE [{db}];\nGO\n{committed_inserts}\n{target_inserts}\nGO\n",
    )

    delete_sql = f"""USE [{db}];
GO
BEGIN TRANSACTION;
DELETE FROM delete_test WHERE phase = 'delete_target';
WAITFOR DELAY '00:00:{hold_seconds:02d}';
ROLLBACK TRANSACTION;
GO
"""
    delete_sql_file = "/tmp/dirty_delete_bg.sql"
    print(f"  opening background DELETE transaction (held for {hold_seconds} s) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, delete_sql, delete_sql_file)

    time.sleep(2)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_DELETE}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (uncommitted DELETE open) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_l.sql")
    print("  backup complete; waiting for DELETE rollback …")
    bg_proc.communicate(timeout=hold_seconds + 10)
    print("  DELETE rolled back")
    return committed, delete_target, hold_seconds


# ---------------------------------------------------------------------------
# Scenario M — Uncommitted UPDATE (in-place modification) during backup
# ---------------------------------------------------------------------------

def _build_scenario_m(container: str, sqlcmd: list[str]) -> tuple[int, int, int]:
    """Run Scenario M: backup while an uncommitted UPDATE is open.

    Returns (total_rows, modified_rows, hold_seconds).

    Setup:
      - ``total_rows`` rows are inserted and committed.
      - ``modified_rows`` of those rows have orig_label='original_N'.
      - A background session opens a transaction, UPDATEs those rows to
        label='modified_N', and holds the transaction open via WAITFOR DELAY.
      - The backup runs while the UPDATE is in-flight.
      - The transaction is rolled back.

    What SQL Server does (without snapshot isolation):
      The UPDATE modifies the row in-place on the data page.  The buffer pool holds
      the modified page.  If the backup reads that page after the UPDATE (but before
      rollback), mssqlbak sees the modified (phantom) values.  After rollback, SQL
      Server rewrites the original values using the undo log — but the backup already
      captured the modified state.

    Gap: mssqlbak has no log-tail mechanism to undo in-place UPDATEs, so modified
    values from rolled-back transactions may appear in the output.
    """
    db = "DirtyUpdateRows"
    total = 50
    modified = 20
    hold_seconds = 20

    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE update_test (
  id     INT IDENTITY PRIMARY KEY,
  label  NVARCHAR(200) NOT NULL,
  score  INT           NOT NULL DEFAULT 0,
  phase  VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    all_inserts = "\n".join(
        (
            f"INSERT INTO update_test(label, score, phase) "
            f"VALUES(N'original_{i}', {i}, 'pre_update');"
        )
        for i in range(1, total + 1)
    )
    print(f"  inserting {total} rows …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{all_inserts}\nGO\n")

    update_sql = f"""USE [{db}];
GO
BEGIN TRANSACTION;
UPDATE update_test
  SET label = N'modified_' + CAST(id AS NVARCHAR(10)),
      score = score + 1000,
      phase = 'in_update'
WHERE id <= {modified};
WAITFOR DELAY '00:00:{hold_seconds:02d}';
ROLLBACK TRANSACTION;
GO
"""
    update_sql_file = "/tmp/dirty_update_bg.sql"
    print(f"  opening background UPDATE transaction (held for {hold_seconds} s) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, update_sql, update_sql_file)

    time.sleep(2)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_UPDATE}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (uncommitted UPDATE open) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_m.sql")
    print("  backup complete; waiting for UPDATE rollback …")
    bg_proc.communicate(timeout=hold_seconds + 10)
    print("  UPDATE rolled back")
    return total, modified, hold_seconds


# ---------------------------------------------------------------------------
# Scenario N — ALTER COLUMN type rewrite (NVARCHAR → VARCHAR), static backup
# ---------------------------------------------------------------------------

def _build_scenario_n(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Run Scenario N: static backup after a column type-change that rewrites rows.

    Returns (pre_rows, post_rows).

    Changing a NVARCHAR(200) column to VARCHAR(200) forces SQL Server to rewrite
    every row: UTF-16LE encoding (2 bytes per ASCII char) → single-byte encoding
    (1 byte per ASCII char).  This is NOT a metadata-only operation; the entire
    clustered index is rebuilt.

    After the rewrite all rows share the same VARCHAR physical format.  mssqlbak
    must decode them using the new VARCHAR type_id from the catalog.  Any page that
    was captured mid-rewrite (concurrent backup) could have a mix of NVARCHAR and
    VARCHAR bytes — but this fixture takes a static backup after the rewrite
    completes, so all rows are in the new format.
    """
    db = "DirtyAlterColRewrite"
    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE rewrite_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    pre = 50
    pre_inserts = "\n".join(
        f"INSERT INTO rewrite_test(label, phase) VALUES(N'pre_{i:03d}', 'pre_ddl');"
        for i in range(1, pre + 1)
    )
    print(f"  inserting {pre} rows as NVARCHAR …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{pre_inserts}\nGO\n")

    print("  ALTER COLUMN label NVARCHAR(200) → VARCHAR(200) (row rewrite) …")
    _exec_sql(
        container, sqlcmd,
        (
            f"USE [{db}];\nGO\n"
            f"ALTER TABLE rewrite_test ALTER COLUMN label VARCHAR(200) NOT NULL;\n"
            f"GO\n"
        ),
    )

    post = 10
    post_inserts = "\n".join(
        f"INSERT INTO rewrite_test(label, phase) VALUES('post_{i:03d}', 'post_ddl');"
        for i in range(1, post + 1)
    )
    print(f"  inserting {post} rows as VARCHAR …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{post_inserts}\nGO\n")

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_ALTERCOL_REWRITE}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (static, post-rewrite) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_n.sql")
    return pre, post


# ---------------------------------------------------------------------------
# Scenario O — ALTER DATABASE SET during backup
# ---------------------------------------------------------------------------

def _build_scenario_o(container: str, sqlcmd: list[str]) -> int:
    """Run Scenario O: ALTER DATABASE SET COMPATIBILITY_LEVEL fires during backup.

    Returns the row count.  Changing the database compatibility level updates a
    flag in the database boot page (system page).  Data pages are unchanged.
    mssqlbak reads user data pages, not the boot page, so this should have no
    effect on row decoding.
    """
    db = "DirtyAlterDb"
    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE alterdb_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    rows = 300
    inserts = "\n".join(
        f"INSERT INTO alterdb_test(label) VALUES(N'row {i}');"
        for i in range(1, rows + 1)
    )
    print(f"  inserting {rows} rows …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{inserts}\nGO\n")

    # Fire ALTER DATABASE SET mid-backup via a background sqlcmd session.
    # Use COMPATIBILITY_LEVEL 130 (SQL Server 2016) — safe to change.
    alterdb_sql = f"""USE [master];
GO
WAITFOR DELAY '00:00:01';
ALTER DATABASE [{db}] SET COMPATIBILITY_LEVEL = 130;
GO
"""
    alterdb_sql_file = "/tmp/dirty_alterdb_bg.sql"
    print("  starting background ALTER DATABASE SET COMPATIBILITY_LEVEL (1 s delay) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, alterdb_sql, alterdb_sql_file)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_ALTERDB}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_o.sql")
    print("  backup complete; waiting for ALTER DATABASE to finish …")
    bg_proc.communicate(timeout=15)
    return rows


# ---------------------------------------------------------------------------
# Scenario P — SAVE TRANSACTION (savepoint), open TX rolled back
# ---------------------------------------------------------------------------

def _build_scenario_p(container: str, sqlcmd: list[str]) -> tuple[int, int, int]:
    """Run Scenario P: backup during an open TX that used SAVE TRANSACTION.

    Returns (committed_rows, before_save_rows, after_save_rows).

    Setup:
      - committed_rows committed rows (phase 'committed').
      - A background session: BEGIN TX → insert before_save_rows (phase 'before_save')
        → SAVE TRANSACTION sp1 → insert after_save_rows (phase 'after_save')
        → ROLLBACK TO sp1 (after_save rows removed from TX pages)
        → WAITFOR DELAY (backup runs with before_save dirty rows still open)
        → ROLLBACK outer TX.

    The key question: does the log tail parser see all before_save xact_ids with
    neither COMMIT nor ABORT?  Those rows should be suppressed by dirty_slots_from_bak.
    The after_save rows were rolled back to the savepoint before the backup started;
    their pages should show those slots as ghosts or reclaimed.
    """
    db = "DirtySavepoint"
    committed = 50
    before_save = 20
    after_save = 10
    hold_seconds = 20

    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE savepoint_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    committed_inserts = "\n".join(
        f"INSERT INTO savepoint_test(label, phase) VALUES(N'committed {i}', 'committed');"
        for i in range(1, committed + 1)
    )
    print(f"  inserting {committed} committed rows …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{committed_inserts}\nGO\n")

    before_inserts = "\n".join(
        f"INSERT INTO savepoint_test(label, phase) VALUES(N'before_save {i}', 'before_save');"
        for i in range(1, before_save + 1)
    )
    after_inserts = "\n".join(
        f"INSERT INTO savepoint_test(label, phase) VALUES(N'after_save {i}', 'after_save');"
        for i in range(1, after_save + 1)
    )

    savepoint_sql = (
        f"USE [{db}];\nGO\n"
        f"BEGIN TRANSACTION;\n"
        f"{before_inserts}\n"
        f"SAVE TRANSACTION sp1;\n"
        f"{after_inserts}\n"
        f"ROLLBACK TRANSACTION sp1;\n"
        f"WAITFOR DELAY '00:00:{hold_seconds:02d}';\n"
        f"ROLLBACK TRANSACTION;\n"
        f"GO\n"
    )
    savepoint_sql_file = "/tmp/dirty_savepoint_bg.sql"
    print(
        f"  opening background TX (insert {before_save}, save, insert {after_save}, "
        f"rollback to save, hold {hold_seconds} s, rollback) …"
    )
    bg_proc = _exec_sql_bg(container, sqlcmd, savepoint_sql, savepoint_sql_file)

    time.sleep(2)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_SAVEPOINT}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (savepoint TX open) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_p.sql")
    print("  backup complete; waiting for TX rollback …")
    bg_proc.communicate(timeout=hold_seconds + 10)
    print("  TX rolled back")
    return committed, before_save, after_save


# ---------------------------------------------------------------------------
# Scenario Q — Nested transactions (BEGIN inside BEGIN), outer TX rolled back
# ---------------------------------------------------------------------------

def _build_scenario_q(container: str, sqlcmd: list[str]) -> tuple[int, int, int]:
    """Run Scenario Q: backup during an open TX with a nested BEGIN / COMMIT.

    Returns (committed_rows, outer_rows, inner_rows).

    SQL Server flattens nested transactions: the inner COMMIT just decrements
    @@TRANCOUNT; a final ROLLBACK on the outer transaction rolls back all rows
    from both the outer and inner BEGIN.

    The log tail parser tracks rows by xact_id.  Since SQL Server assigns a
    single xact_id to the entire nested group, all rows (outer + inner) should
    appear under the same uncommitted transaction and be suppressable together.
    """
    db = "DirtyNested"
    committed = 50
    outer_rows = 10
    inner_rows = 10
    hold_seconds = 20

    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE nested_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    committed_inserts = "\n".join(
        f"INSERT INTO nested_test(label, phase) VALUES(N'committed {i}', 'committed');"
        for i in range(1, committed + 1)
    )
    print(f"  inserting {committed} committed rows …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{committed_inserts}\nGO\n")

    outer_inserts = "\n".join(
        f"INSERT INTO nested_test(label, phase) VALUES(N'outer {i}', 'outer_tx');"
        for i in range(1, outer_rows + 1)
    )
    inner_inserts = "\n".join(
        f"INSERT INTO nested_test(label, phase) VALUES(N'inner {i}', 'inner_tx');"
        for i in range(1, inner_rows + 1)
    )

    nested_sql = (
        f"USE [{db}];\nGO\n"
        f"BEGIN TRANSACTION;\n"          # @@TRANCOUNT = 1
        f"{outer_inserts}\n"
        f"BEGIN TRANSACTION;\n"          # @@TRANCOUNT = 2
        f"{inner_inserts}\n"
        f"COMMIT TRANSACTION;\n"         # @@TRANCOUNT = 1 — does NOT actually commit
        f"WAITFOR DELAY '00:00:{hold_seconds:02d}';\n"
        f"ROLLBACK TRANSACTION;\n"       # rolls back everything
        f"GO\n"
    )
    nested_sql_file = "/tmp/dirty_nested_bg.sql"
    print(
        f"  opening background nested TX (outer {outer_rows} rows, "
        f"inner {inner_rows} rows, hold {hold_seconds} s, outer ROLLBACK) …"
    )
    bg_proc = _exec_sql_bg(container, sqlcmd, nested_sql, nested_sql_file)

    time.sleep(2)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_NESTED}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (nested TX open) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_q.sql")
    print("  backup complete; waiting for nested TX rollback …")
    bg_proc.communicate(timeout=hold_seconds + 10)
    print("  nested TX rolled back")
    return committed, outer_rows, inner_rows


# ---------------------------------------------------------------------------
# Scenario R — ALTER TABLE SWITCH PARTITION during backup
# ---------------------------------------------------------------------------

def _build_scenario_r(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Run Scenario R: SWITCH PARTITION fires during backup.

    Returns (partitioned_rows, staged_rows).

    SWITCH PARTITION is an atomic metadata operation: it reassigns a range of
    pages from one table (or partition) to another by updating allocation bitmaps.
    The data pages themselves do not move.  For mssqlbak, the risk is that the
    catalog snapshot (which table 'owns' which pages) may be inconsistent with
    the data page snapshot if the SWITCH fires between the catalog scan and the
    data page scan.

    Setup:
      - part_test: partitioned table, partitions 1–3 (id values 1–300).
      - staging_test: flat table constrained to id > 300 (will SWITCH to partition 4).
      - During backup: SWITCH staging_test → part_test PARTITION 4.
      - Outcomes for mssqlbak:
          a) Backup captured catalog before SWITCH: staging_test exists as separate
             table, part_test has only 3 partitions worth of rows.
          b) Backup captured catalog after SWITCH: staging_test absent (or empty),
             part_test has all 4 partitions worth of rows.
          c) Split: catalog shows one state, pages show another (worst case).
      - Expected: no crash in any case; combined row count between 'stable' rows
        and the staged rows is consistent.
    """
    db = "DirtySwitch"
    partitioned_per_partition = 50   # rows per partition (3 partitions = 150 rows)
    staged = 50                      # rows in staging_test (will SWITCH to partition 4)

    print(f"  creating database {db} …")
    setup_sql = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE PARTITION FUNCTION pf_switch (INT)
  AS RANGE LEFT FOR VALUES (100, 200, 300);
GO
CREATE PARTITION SCHEME ps_switch
  AS PARTITION pf_switch ALL TO ([PRIMARY]);
GO
CREATE TABLE part_test (
  id    INT           NOT NULL,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL,
  CONSTRAINT pk_part PRIMARY KEY CLUSTERED (id)
) ON ps_switch(id);
GO
CREATE TABLE staging_test (
  id    INT           NOT NULL,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL,
  CONSTRAINT pk_staging PRIMARY KEY CLUSTERED (id),
  CONSTRAINT chk_staging_id CHECK (id > 300 AND id IS NOT NULL)
) ON [PRIMARY];
GO
"""
    _exec_sql(container, sqlcmd, setup_sql)

    # Insert rows into partitions 1–3 (id 1..150)
    part_inserts = "\n".join(
        f"INSERT INTO part_test(id, label, phase) "
        f"VALUES({i}, N'part row {i}', 'partitioned');"
        for i in range(1, partitioned_per_partition * 3 + 1)
    )
    print(f"  inserting {partitioned_per_partition * 3} rows into part_test (3 partitions) …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{part_inserts}\nGO\n")

    # Insert rows into staging (id 301..350)
    staging_inserts = "\n".join(
        f"INSERT INTO staging_test(id, label, phase) "
        f"VALUES({300 + i}, N'staged row {300 + i}', 'staged');"
        for i in range(1, staged + 1)
    )
    print(f"  inserting {staged} rows into staging_test …")
    _exec_sql(container, sqlcmd, f"USE [{db}];\nGO\n{staging_inserts}\nGO\n")

    # SWITCH staging_test → part_test PARTITION 4 (id > 300)
    switch_sql = f"""USE [{db}];
GO
WAITFOR DELAY '00:00:01';
ALTER TABLE staging_test SWITCH TO part_test PARTITION 4;
GO
"""
    switch_sql_file = "/tmp/dirty_switch_bg.sql"
    print("  starting background SWITCH PARTITION (1 s delay) …")
    bg_proc = _exec_sql_bg(container, sqlcmd, switch_sql, switch_sql_file)

    backup_sql = f"""USE [master];
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_SWITCH}'
  WITH FORMAT, INIT;
GO
"""
    print("  taking BACKUP DATABASE (SWITCH PARTITION may fire during backup) …")
    _exec_sql(container, sqlcmd, backup_sql, "/tmp/dirty_bak_r.sql")
    print("  backup complete; waiting for SWITCH to finish …")
    bg_proc.communicate(timeout=15)
    return partitioned_per_partition * 3, staged


# ---------------------------------------------------------------------------
# Scenario W — two concurrent uncommitted transactions
# ---------------------------------------------------------------------------

def _build_scenario_w(container: str, sqlcmd: list[str]) -> tuple[int, int, int]:
    """TX-A inserts 10 rows (held open) + TX-B ghost-deletes 10 and inserts 5.

    Returns (committed, tx_a_dirty, tx_b_ghost_deleted).
    """
    db = f"{DB_NAME}_TwoTx"
    committed_rows = 30
    tx_a_rows = 10
    tx_b_delete_rows = 10
    tx_b_insert_rows = 5
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE two_tx_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
INSERT INTO two_tx_test (label, phase)
SELECT 'committed_' + CAST(n AS NVARCHAR), 'committed'
FROM (SELECT TOP({committed_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_tx_a = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
INSERT INTO two_tx_test (label, phase)
SELECT 'tx_a_' + CAST(n AS NVARCHAR), 'tx_a'
FROM (SELECT TOP({tx_a_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_tx_b = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
DELETE FROM two_tx_test WHERE id <= {tx_b_delete_rows};
INSERT INTO two_tx_test (label, phase)
SELECT 'tx_b_' + CAST(n AS NVARCHAR), 'tx_b'
FROM (SELECT TOP({tx_b_insert_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_TWO_TX}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)

    bg_a = _exec_sql_bg(container, sqlcmd, sql_tx_a, "/tmp/dirty_w_a.sql")
    bg_b = _exec_sql_bg(container, sqlcmd, sql_tx_b, "/tmp/dirty_w_b.sql")
    time.sleep(3)

    print("  taking BACKUP DATABASE (two open TXs in flight) …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  backup complete; waiting for both TXs to finish …")
    bg_a.communicate(timeout=30)
    bg_b.communicate(timeout=30)
    return committed_rows, tx_a_rows, tx_b_delete_rows


# ---------------------------------------------------------------------------
# Scenario AA + AB — rich-type table (shared schema)
# ---------------------------------------------------------------------------

_RICH_TABLE_DDL = """\
CREATE TABLE rich_update_test (
  id        INT              NOT NULL,
  flag      BIT              NULL,
  small_val SMALLINT         NULL,
  big_val   BIGINT           NULL,
  dec_val   DECIMAL(18,4)    NULL,
  dt2_val   DATETIME2(3)     NULL,
  guid_val  UNIQUEIDENTIFIER NULL,
  bin_val   VARBINARY(500)   NULL,
  nc_val    NCHAR(20)        NULL,
  label     NVARCHAR(200)    NOT NULL
);
"""

_RICH_COMMITTED_ROWS = 20
_RICH_UPDATE_ROWS = 10
_RICH_INSERT_ROWS = 15


def _build_scenario_aa_ab(container: str, sqlcmd: list[str]) -> tuple[int, int, int]:
    """AA: rich-type UPDATE; AB: rich-type INSERT — both in the same database.

    Returns (committed, updated, inserted_dirty).
    """
    db_aa = f"{DB_NAME}_RichUpdate"
    db_ab = f"{DB_NAME}_RichInsert"
    hold_s = 20

    def setup_sql(db: str) -> str:
        return f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
{_RICH_TABLE_DDL}
GO
INSERT INTO rich_update_test
  (id, flag, small_val, big_val, dec_val, dt2_val, guid_val, bin_val, nc_val, label)
SELECT
  n,
  CAST(n % 2 AS BIT),
  CAST(n AS SMALLINT),
  CAST(n * 1000000 AS BIGINT),
  CAST(n AS DECIMAL(18,4)) * 1.25,
  DATEADD(SECOND, n * 17, '2020-01-01'),
  NEWID(),
  CAST(REPLICATE('A', n % 50 + 1) AS VARBINARY(500)),
  CAST(REPLICATE(N'X', 20) AS NCHAR(20)),
  'original_label_' + CAST(n AS NVARCHAR)
FROM (SELECT TOP({_RICH_COMMITTED_ROWS}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""

    sql_update_tx = f"""USE [{db_aa}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
UPDATE rich_update_test SET
  flag      = CAST((id + 1) % 2 AS BIT),
  small_val = CAST(id * 10 AS SMALLINT),
  big_val   = CAST(id * 9999999 AS BIGINT),
  dec_val   = CAST(id AS DECIMAL(18,4)) * 99.99,
  dt2_val   = DATEADD(YEAR, 10, dt2_val),
  guid_val  = NEWID(),
  bin_val   = CAST(REPLICATE('Z', id % 50 + 1) AS VARBINARY(500)),
  nc_val    = CAST(REPLICATE(N'Y', 20) AS NCHAR(20)),
  label     = 'modified_label_' + CAST(id AS NVARCHAR)
WHERE id <= {_RICH_UPDATE_ROWS};
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""

    sql_insert_tx = f"""USE [{db_ab}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
INSERT INTO rich_update_test
  (id, flag, small_val, big_val, dec_val, dt2_val, guid_val, bin_val, nc_val, label)
SELECT
  100 + n,
  CAST(n % 2 AS BIT),
  CAST(n AS SMALLINT),
  CAST(n * 1000000 AS BIGINT),
  CAST(n AS DECIMAL(18,4)) * 1.25,
  DATEADD(SECOND, n * 17, '2020-01-01'),
  NEWID(),
  CAST(REPLICATE('B', n % 50 + 1) AS VARBINARY(500)),
  CAST(REPLICATE(N'Z', 20) AS NCHAR(20)),
  'dirty_label_' + CAST(n AS NVARCHAR)
FROM (SELECT TOP({_RICH_INSERT_ROWS}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""

    sql_bak_aa = f"""USE [master];
BACKUP DATABASE [{db_aa}] TO DISK=N'{CONTAINER_BAK_RICH_UPDATE}' WITH FORMAT, INIT, STATS=10;
GO
"""
    sql_bak_ab = f"""USE [master];
BACKUP DATABASE [{db_ab}] TO DISK=N'{CONTAINER_BAK_RICH_INSERT}' WITH FORMAT, INIT, STATS=10;
GO
"""

    print("  setting up AA database …")
    _exec_sql(container, sqlcmd, setup_sql(db_aa))
    print("  setting up AB database …")
    _exec_sql(container, sqlcmd, setup_sql(db_ab))

    bg_aa = _exec_sql_bg(container, sqlcmd, sql_update_tx, "/tmp/dirty_aa.sql")
    bg_ab = _exec_sql_bg(container, sqlcmd, sql_insert_tx, "/tmp/dirty_ab.sql")
    time.sleep(3)

    print("  taking AA BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_bak_aa)
    print("  taking AB BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_bak_ab)
    print("  waiting for both TXs to finish …")
    bg_aa.communicate(timeout=30)
    bg_ab.communicate(timeout=30)
    return _RICH_COMMITTED_ROWS, _RICH_UPDATE_ROWS, _RICH_INSERT_ROWS


# ---------------------------------------------------------------------------
# Scenario Y — uncommitted UPDATE that sets column to NULL
# ---------------------------------------------------------------------------

def _build_scenario_y(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """20 rows committed with score non-NULL.  TX updates rows 1–10 to score=NULL.

    Returns (committed_rows, updated_rows).
    """
    db = f"{DB_NAME}_NullUpdate"
    committed_rows = 20
    updated_rows = 10
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE null_update_test (
  id    INT  NOT NULL PRIMARY KEY,
  label VARCHAR(50) NOT NULL,
  score INT  NULL
);
GO
INSERT INTO null_update_test (id, label, score)
SELECT n, 'label_' + CAST(n AS VARCHAR), n * 100
FROM (SELECT TOP({committed_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
UPDATE null_update_test SET score = NULL, label = 'modified_' + label
WHERE id <= {updated_rows};
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_NULL_UPDATE}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_y.sql")
    time.sleep(3)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=30)
    return committed_rows, updated_rows


# ---------------------------------------------------------------------------
# Scenario AD — all-dirty table (0 committed rows)
# ---------------------------------------------------------------------------

def _build_scenario_ad(container: str, sqlcmd: list[str]) -> int:
    """Create table, immediately open TX, insert 20 rows, hold for backup.

    Returns the number of dirty rows.
    """
    db = f"{DB_NAME}_AllDirty"
    dirty_rows = 20
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE alldirty_test (
  id    INT IDENTITY PRIMARY KEY,
  label NVARCHAR(200) NOT NULL,
  phase VARCHAR(30)   NOT NULL
);
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
INSERT INTO alldirty_test (label, phase)
SELECT 'dirty_' + CAST(n AS NVARCHAR), 'dirty'
FROM (SELECT TOP({dirty_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_ALLDIRTY}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_ad.sql")
    time.sleep(3)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=30)
    return dirty_rows


# ---------------------------------------------------------------------------
# Scenario AC — uncommitted DELETE on NCHAR/NVARCHAR table
# ---------------------------------------------------------------------------

def _build_scenario_ac(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """30 rows committed; TX ghost-deletes rows 1–15; both held during backup.

    Returns (committed_rows, deleted_rows).
    """
    db = f"{DB_NAME}_NcharDelete"
    committed_rows = 30
    deleted_rows = 15
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE nchar_delete_test (
  id       INT        NOT NULL PRIMARY KEY,
  nc_label NCHAR(50)  NOT NULL,
  nv_desc  NVARCHAR(200) NOT NULL
);
GO
INSERT INTO nchar_delete_test (id, nc_label, nv_desc)
SELECT n,
  CAST(REPLICATE(N'A', 50) AS NCHAR(50)),
  N'description_' + CAST(n AS NVARCHAR)
FROM (SELECT TOP({committed_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
DELETE FROM nchar_delete_test WHERE id <= {deleted_rows};
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_NCHAR_DELETE}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_ac.sql")
    time.sleep(3)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=30)
    return committed_rows, deleted_rows


# ---------------------------------------------------------------------------
# Scenario X — forwarded record in heap + uncommitted ghost-delete
# ---------------------------------------------------------------------------

def _build_scenario_x(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Heap table; UPDATE one row to trigger forwarding; TX ghost-deletes another.

    Returns (committed_rows, ghost_deleted_rows).
    """
    db = f"{DB_NAME}_HeapForward"
    committed_rows = 20
    ghost_deleted = 1
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE heap_forward_test (
  id    INT NOT NULL,
  label VARCHAR(8000) NOT NULL
);
GO
-- Insert 20 short rows so they all fit on a small number of pages.
INSERT INTO heap_forward_test (id, label)
SELECT n, REPLICATE('A', 50)
FROM (SELECT TOP({committed_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
-- UPDATE row 1 to a very long label so it grows and gets forwarded.
UPDATE heap_forward_test SET label = REPLICATE('B', 7900) WHERE id = 1;
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
DELETE FROM heap_forward_test WHERE id = {committed_rows};
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_HEAP_FORWARD}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_x.sql")
    time.sleep(3)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=30)
    return committed_rows, ghost_deleted


# ---------------------------------------------------------------------------
# Scenario AE — large uncommitted transaction (many pages)
# ---------------------------------------------------------------------------

def _build_scenario_ae(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """50 committed rows; TX inserts 5000 rows spanning ~25 pages.

    Returns (committed_rows, dirty_rows).
    """
    db = f"{DB_NAME}_LargeDirty"
    committed_rows = 50
    dirty_rows = 5000
    hold_s = 25

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE large_dirty_test (
  id    INT IDENTITY PRIMARY KEY,
  label VARCHAR(50) NOT NULL,
  phase VARCHAR(30) NOT NULL
);
GO
INSERT INTO large_dirty_test (label, phase)
SELECT 'committed_' + CAST(n AS VARCHAR), 'committed'
FROM (SELECT TOP({committed_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
INSERT INTO large_dirty_test (label, phase)
SELECT 'dirty_' + CAST(n AS VARCHAR), 'dirty'
FROM (SELECT TOP({dirty_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM master.sys.all_columns AS a CROSS JOIN master.sys.all_columns AS b) x;
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_LARGE_DIRTY}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_ae.sql")
    time.sleep(5)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=40)
    return committed_rows, dirty_rows


# ---------------------------------------------------------------------------
# Scenario Z/AJ — uncommitted UPDATE on VARCHAR(MAX) LOB column
# ---------------------------------------------------------------------------

def _build_scenario_z(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """5 rows with 9000-char content (off-row LOB); TX updates rows 1–3.

    Returns (total_rows, updated_rows).
    """
    db = f"{DB_NAME}_LobUpdate"
    total_rows = 5
    updated_rows = 3
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE lob_update_test (
  id      INT NOT NULL PRIMARY KEY,
  content VARCHAR(MAX) NOT NULL
);
GO
INSERT INTO lob_update_test (id, content)
SELECT n, REPLICATE(CAST('X' AS VARCHAR(MAX)), 9000)
FROM (SELECT TOP({total_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
UPDATE lob_update_test SET content = REPLICATE(CAST('Y' AS VARCHAR(MAX)), 9000)
WHERE id <= {updated_rows};
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_LOB_UPDATE}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_z.sql")
    time.sleep(3)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=30)
    return total_rows, updated_rows


# ---------------------------------------------------------------------------
# Scenario AI — row at the SQL Server 8060-byte inline storage limit
# ---------------------------------------------------------------------------

def _build_scenario_ai(container: str, sqlcmd: list[str]) -> int:
    """Static backup; 10 rows with CHAR(8050) — at the inline limit.

    Returns the row count.
    """
    db = f"{DB_NAME}_MaxRow"
    row_count = 10

    # SQL Server max for a single fixed-length column is 8000 bytes (CHAR/BINARY).
    # A row with CHAR(8000) + INT(4) + row overhead approaches the 8060-byte
    # inline page limit — the boundary this scenario is designed to test.
    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE maxrow_test (
  id      INT  NOT NULL PRIMARY KEY,
  content CHAR(8000) NOT NULL
);
GO
INSERT INTO maxrow_test (id, content)
SELECT n, REPLICATE('R', 8000)
FROM (SELECT TOP({row_count}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_MAXROW}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    return row_count


# ---------------------------------------------------------------------------
# Scenario AG — temporal table with uncommitted UPDATE
# ---------------------------------------------------------------------------

def _build_scenario_ag(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """Temporal table; 20 rows committed; TX updates rows 1–10; held during backup.

    Returns (committed_rows, updated_rows).
    """
    db = f"{DB_NAME}_Temporal"
    committed_rows = 20
    updated_rows = 10
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
USE [{db}];
GO
CREATE TABLE temporal_test (
  id         INT          NOT NULL PRIMARY KEY,
  label      NVARCHAR(200) NOT NULL,
  ValidFrom  DATETIME2(7) GENERATED ALWAYS AS ROW START NOT NULL,
  ValidTo    DATETIME2(7) GENERATED ALWAYS AS ROW END   NOT NULL,
  PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.temporal_test_history));
GO
INSERT INTO temporal_test (id, label)
SELECT n, 'original_' + CAST(n AS NVARCHAR)
FROM (SELECT TOP({committed_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
UPDATE temporal_test SET label = 'modified_' + label WHERE id <= {updated_rows};
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_TEMPORAL_UPDATE}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_ag.sql")
    time.sleep(3)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=30)
    return committed_rows, updated_rows


# ---------------------------------------------------------------------------
# Scenario AH — SNAPSHOT isolation row-versioning ghost
# ---------------------------------------------------------------------------

def _build_scenario_ah(container: str, sqlcmd: list[str]) -> tuple[int, int]:
    """READ_COMMITTED_SNAPSHOT ON; 20 rows; TX updates rows 1–10 (14-byte version tail).

    Returns (committed_rows, updated_rows).
    """
    db = f"{DB_NAME}_Snapshot"
    committed_rows = 20
    updated_rows = 10
    hold_s = 20

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
ALTER DATABASE [{db}] SET READ_COMMITTED_SNAPSHOT ON;
GO
USE [{db}];
GO
CREATE TABLE snapshot_update_test (
  id    INT NOT NULL PRIMARY KEY,
  label NVARCHAR(200) NOT NULL
);
GO
INSERT INTO snapshot_update_test (id, label)
SELECT n, 'original_' + CAST(n AS NVARCHAR)
FROM (SELECT TOP({committed_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM sys.objects) x;
GO
"""
    sql_tx = f"""USE [{db}];
SET NOCOUNT ON;
BEGIN TRANSACTION;
UPDATE snapshot_update_test SET label = 'modified_' + label WHERE id <= {updated_rows};
WAITFOR DELAY '00:00:{hold_s:02d}';
ROLLBACK;
"""
    sql_backup = f"""USE [master];
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_SNAPSHOT_UPDATE}' WITH FORMAT, INIT, STATS=10;
GO
"""
    print("  setting up database …")
    _exec_sql(container, sqlcmd, sql_setup)
    bg = _exec_sql_bg(container, sqlcmd, sql_tx, "/tmp/dirty_ah.sql")
    time.sleep(3)
    print("  taking BACKUP DATABASE …")
    _exec_sql(container, sqlcmd, sql_backup)
    print("  waiting for TX to finish …")
    bg.communicate(timeout=30)
    return committed_rows, updated_rows


# ---------------------------------------------------------------------------
# Scenario AM — committed DELETE during backup (REDO Gap A)
# ---------------------------------------------------------------------------

def _build_scenario_am(container: str, sqlcmd: list[str], user: str = "", password: str = "") -> tuple[int, int]:
    """committed_delete_test: 1 000 rows (500 will_delete + 500 keep).

    The fixture captures all 1 000 rows in the backup (pre-deletion state).
    ``committed_delete_slots`` will be empty because SQL Server's backup log
    tail only spans the 3 checkpoint records (BEGIN/XACT/END_CKPT) — for an
    in-memory containerised database the checkpoint completes in microseconds
    and LastLSN is set before any DML can fire.  The test
    ``test_committed_delete_slots_detected`` is therefore xfail; the other
    AM tests pass (500 keep rows present, no crash).

    Returns (total_rows, deleted_rows).
    """
    db           = f"{DB_NAME}_CommittedDelete"
    total_rows   = 1_000
    deleted_rows = 500

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
ALTER DATABASE [{db}] SET RECOVERY FULL;
GO
USE [{db}];
GO
CREATE TABLE committed_delete_test (
  id    INT NOT NULL PRIMARY KEY,
  phase VARCHAR(50) NOT NULL,
  label VARCHAR(200) NOT NULL
);
GO
INSERT INTO committed_delete_test (id, phase, label)
SELECT n,
       CASE WHEN n <= {deleted_rows} THEN 'will_delete' ELSE 'keep' END,
       REPLICATE('X', 200)
FROM (SELECT TOP({total_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM master.dbo.spt_values AS a CROSS JOIN master.dbo.spt_values AS b) x;
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_COMMITTED_DELETE}' WITH FORMAT, INIT;
GO
"""
    print("  setting up database and taking backup …")
    _exec_sql(container, sqlcmd, sql_setup)
    return total_rows, deleted_rows


# ---------------------------------------------------------------------------
# Scenario AN — committed UPDATE during backup (REDO Gap B)
# ---------------------------------------------------------------------------

def _build_scenario_an(container: str, sqlcmd: list[str], user: str = "", password: str = "") -> tuple[int, int]:
    """committed_update_test: 1 000 rows with original labels/scores.

    The fixture captures all 1 000 rows in their original (pre-update) state.
    ``redo_patches`` will be empty for the same reason as scenario AM: SQL
    Server's backup log tail only spans the 3 checkpoint records for an
    in-memory containerised database.  ``test_committed_update_patches_detected``
    is therefore xfail; the other AN tests pass (1 000 rows present, no crash).

    Returns (total_rows, updated_rows).
    """
    db = f"{DB_NAME}_CommittedUpdate"
    total_rows   = 1_000
    updated_rows = 500

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
ALTER DATABASE [{db}] SET RECOVERY FULL;
GO
USE [{db}];
GO
CREATE TABLE committed_update_test (
  id    INT NOT NULL PRIMARY KEY,
  label VARCHAR(200) NOT NULL,
  score INT NOT NULL
);
GO
INSERT INTO committed_update_test (id, label, score)
SELECT n,
       LEFT('original_' + CAST(n AS VARCHAR) + REPLICATE('_', 200), 200),
       n
FROM (SELECT TOP({total_rows}) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
      FROM master.dbo.spt_values AS a CROSS JOIN master.dbo.spt_values AS b) x;
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_COMMITTED_UPDATE}' WITH FORMAT, INIT;
GO
"""
    print("  setting up database and taking backup …")
    _exec_sql(container, sqlcmd, sql_setup)
    return total_rows, updated_rows


# ---------------------------------------------------------------------------
# Shared DDL / data helpers for the all-types v3 scenarios
# ---------------------------------------------------------------------------

# Unicode samples from 10 scripts, drawn from tools/unicode_codepage_matrix.py.
# Rows cycle through UNICODE_SAMPLES[n % 10] so each script appears ~30 times
# across 300 inserted rows.
_UNICODE_SAMPLES_SQL = """\
DECLARE @us TABLE (i INT PRIMARY KEY, nv NVARCHAR(200));
INSERT INTO @us VALUES
  (0, N'Ą ą Ć ć Č č Ď ď Ě ě Ł ł Ń ń Ő ő Ř ř Ś ś Š š Ź ź Ż ż Ž ž'),
  (1, N'А Б В Г Д Е Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я'),
  (2, N'Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω'),
  (3, N'ء آ أ ؤ إ ئ ا ب ة ت ث ج ح خ د ذ ر ز س ش ص ض'),
  (4, N'א ב ג ד ה ו ז ח ט י ך כ ל ם מ ן נ ס ע ף פ ץ צ ק ר ש ת'),
  (5, N'ก ข ฃ ค ฅ ฆ ง จ ฉ ช ซ ฌ ญ ฎ ฏ ฐ ฑ ฒ ณ ด ต ถ ท ธ น'),
  (6, N'あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の'),
  (7, N'一 丁 七 万 三 上 下 中 不 与 东 两 严 久 之 也 乘 乙 九 乞 书 乡 买'),
  (8, N'가 각 간 갈 감 갑 강 개 거 건 결 경 고 공 관 교 구 국 군 그 기 길 김'),
  (9, N'à á â ã ả ạ ặ ắ ằ ẳ è é ê ề ế ể ễ ệ ì í ỉ ị ò ó ô ơ ờ');"""

_ALL_TYPES_DDL = """\
CREATE TABLE all_types_test (
  id                  INT              NOT NULL,
  -- Exact integer
  col_tinyint         TINYINT          NULL,
  col_smallint        SMALLINT         NULL,
  col_bigint          BIGINT           NULL,
  col_bit             BIT              NULL,
  -- Exact decimal / money
  col_decimal         DECIMAL(18,4)    NULL,
  col_numeric         NUMERIC(10,3)    NULL,
  col_money           MONEY            NULL,
  col_smallmoney      SMALLMONEY       NULL,
  -- Approximate numeric
  col_float           FLOAT            NULL,
  col_real            REAL             NULL,
  -- Date / time
  col_date            DATE             NULL,
  col_time            TIME(3)          NULL,
  col_datetime        DATETIME         NULL,
  col_smalldatetime   SMALLDATETIME    NULL,
  col_datetime2       DATETIME2(3)     NULL,
  col_datetimeoffset  DATETIMEOFFSET(3) NULL,
  -- Character (ASCII)
  col_char            CHAR(10)         NULL,
  col_varchar         VARCHAR(200)     NULL,
  -- Character (Unicode — multi-script)
  col_nchar           NCHAR(20)        NULL,
  col_nvarchar        NVARCHAR(200)    NULL,
  -- Binary
  col_binary          BINARY(10)       NULL,
  col_varbinary       VARBINARY(200)   NULL,
  -- Misc
  col_uniqueidentifier UNIQUEIDENTIFIER NULL,
  col_xml             XML              NULL,
  col_sql_variant     SQL_VARIANT      NULL,
  col_rowversion      ROWVERSION       NULL,
  CONSTRAINT pk_all_types PRIMARY KEY (id)
);"""

# INSERT expression — n is the 1-based row number, @nv is the unicode sample
# for this row (resolved via UNICODE_SAMPLES_SQL above).
_ALL_TYPES_INSERT_COLS = """\
  id, col_tinyint, col_smallint, col_bigint, col_bit,
  col_decimal, col_numeric, col_money, col_smallmoney,
  col_float, col_real,
  col_date, col_time, col_datetime, col_smalldatetime, col_datetime2, col_datetimeoffset,
  col_char, col_varchar, col_nchar, col_nvarchar,
  col_binary, col_varbinary,
  col_uniqueidentifier, col_xml, col_sql_variant"""

_ALL_TYPES_INSERT_VALS = """\
  n,
  CAST(n % 255 + 1             AS TINYINT),
  CAST(n % 32767               AS SMALLINT),
  CAST(n                       AS BIGINT) * 1000000,
  CAST(n % 2                   AS BIT),
  CAST(n                       AS DECIMAL(18,4)) * 1.2345,
  CAST(n                       AS NUMERIC(10,3)) * 3.14,
  CAST(n                       AS MONEY) * 9.99,
  CAST(n % 214 + 1             AS SMALLMONEY) * 1.11,
  CAST(n                       AS FLOAT) * 2.71828,
  CAST(n % 10000 + 1           AS REAL) * 1.5,
  DATEADD(DAY,   n,            '2020-01-01'),
  CAST(DATEADD(SECOND, n % 86400, '00:00:00') AS TIME(3)),
  DATEADD(SECOND, n,           '2020-01-01 00:00:00'),
  CAST(DATEADD(MINUTE, n % 65535, '2000-01-01') AS SMALLDATETIME),
  DATEADD(MILLISECOND, n * 100,'2020-01-01'),
  TODATETIMEOFFSET(DATEADD(SECOND, n, '2020-01-01'), '+05:30'),
  LEFT(CAST(n AS CHAR(10)), 10),
  LEFT('v_' + CAST(n AS VARCHAR(10)) + REPLICATE('x', 200), 200),
  LEFT(us.nv + REPLICATE(N' ', 20), 20),
  LEFT(CAST(n AS NVARCHAR(10)) + N' ' + us.nv, 200),
  CONVERT(BINARY(10),   HASHBYTES('MD5',     CAST(n AS VARCHAR(10)))),
  CONVERT(VARBINARY(200), HASHBYTES('SHA2_256', CAST(n AS VARCHAR(10)))),
  NEWID(),
  CAST('<r n="' + CAST(n AS VARCHAR) + '"/>' AS XML),
  CAST(n AS SQL_VARIANT)"""


def _all_types_insert_sql(db: str, total_rows: int) -> str:
    """Return a GO-separated T-SQL block that inserts *total_rows* all-types rows."""
    return f"""USE [{db}];
GO
{_UNICODE_SAMPLES_SQL}
INSERT INTO all_types_test ({_ALL_TYPES_INSERT_COLS})
SELECT
{_ALL_TYPES_INSERT_VALS}
FROM (
  SELECT TOP({total_rows})
         ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
  FROM master.dbo.spt_values AS a CROSS JOIN master.dbo.spt_values AS b
) AS x
JOIN @us AS us ON us.i = (n - 1) % 10;
GO"""


# ---------------------------------------------------------------------------
# Scenario AM-v3 — all-types committed DELETE (REDO Gap A, v3)
# ---------------------------------------------------------------------------

def _build_scenario_am_v3(
    container: str, sqlcmd: list[str], user: str = "", password: str = ""
) -> tuple[int, int]:
    """all_types_test: 300 rows, all SQL Server column types.

    INSERT 300 rows spanning 10 Unicode scripts (30 rows per script).
    DELETE ids 1-100 (committed, pre-backup).
    Backup captures the surviving 200 rows (ids 101-300).

    Returns (total_rows, deleted_rows).
    """
    db           = f"{DB_NAME}_CommittedDeleteV3"
    total_rows   = 300
    deleted_rows = 100

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
ALTER DATABASE [{db}] SET RECOVERY FULL;
GO
USE [{db}];
GO
{_ALL_TYPES_DDL}
GO"""
    sql_insert = _all_types_insert_sql(db, total_rows)
    sql_dml = f"""USE [{db}];
GO
DELETE FROM all_types_test WHERE id <= {deleted_rows};
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_COMMITTED_DELETE_V3}' WITH FORMAT, INIT;
GO"""

    print("  setting up AM-v3 database …")
    _exec_sql(container, sqlcmd, sql_setup)
    print("  inserting 300 all-types rows …")
    _exec_sql(container, sqlcmd, sql_insert)
    print("  deleting 100 rows and taking backup …")
    _exec_sql(container, sqlcmd, sql_dml)
    return total_rows, deleted_rows


# ---------------------------------------------------------------------------
# Scenario AN-v3 — all-types committed UPDATE (REDO Gap B, v3)
# ---------------------------------------------------------------------------

def _build_scenario_an_v3(
    container: str, sqlcmd: list[str], user: str = "", password: str = ""
) -> tuple[int, int]:
    """all_types_test: 300 rows, all SQL Server column types.

    INSERT 300 rows spanning 10 Unicode scripts.
    UPDATE ids 1-100 with new values (committed, pre-backup).
    Backup captures all 300 rows with updated values for ids 1-100.

    Returns (total_rows, updated_rows).
    """
    db           = f"{DB_NAME}_CommittedUpdateV3"
    total_rows   = 300
    updated_rows = 100

    sql_setup = f"""USE [master];
GO
IF DB_ID('{db}') IS NOT NULL BEGIN
  ALTER DATABASE [{db}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE [{db}];
END;
GO
CREATE DATABASE [{db}];
GO
ALTER DATABASE [{db}] SET RECOVERY FULL;
GO
USE [{db}];
GO
{_ALL_TYPES_DDL}
GO"""
    sql_insert = _all_types_insert_sql(db, total_rows)
    sql_dml = f"""USE [{db}];
GO
UPDATE all_types_test SET
  col_tinyint        = CAST((id * 3) % 255         AS TINYINT),
  col_smallint       = CAST(id * 7                  AS SMALLINT),
  col_bigint         = CAST(id AS BIGINT) * -999999,
  col_bit            = CAST((id + 1) % 2            AS BIT),
  col_decimal        = CAST(id AS DECIMAL(18,4)) * 99.9999,
  col_numeric        = CAST(id AS NUMERIC(10,3))    * 2.718,
  col_money          = CAST(id AS MONEY)             * 100.01,
  col_smallmoney     = CAST(id % 214 + 1 AS SMALLMONEY) * 2.22,
  col_float          = CAST(id AS FLOAT)             * -1.41421,
  col_real           = CAST(id % 10000 + 1 AS REAL)  * 3.3,
  col_date           = DATEADD(YEAR,   1, col_date),
  col_time           = CAST(DATEADD(HOUR, 1, CAST(col_time AS DATETIME2)) AS TIME(3)),
  col_datetime       = DATEADD(YEAR,   5, col_datetime),
  col_smalldatetime  = CAST(DATEADD(MONTH, 6, CAST(col_smalldatetime AS DATETIME)) AS SMALLDATETIME),
  col_datetime2      = DATEADD(YEAR,   2, col_datetime2),
  col_datetimeoffset = SWITCHOFFSET(col_datetimeoffset, '-08:00'),
  col_char           = LEFT('upd' + CAST(id AS CHAR(10)), 10),
  col_varchar        = LEFT('updated_' + CAST(id AS VARCHAR(10)) + REPLICATE('y', 200), 200),
  col_nchar          = LEFT(N'更新 ' + CAST(id AS NVARCHAR(10)) + REPLICATE(N' ', 20), 20),
  col_nvarchar       = LEFT(N'更新済み ' + CAST(id AS NVARCHAR(10)), 200),
  col_binary         = CONVERT(BINARY(10),   HASHBYTES('MD5',     CAST(id * 17 AS VARCHAR(10)))),
  col_varbinary      = CONVERT(VARBINARY(200), HASHBYTES('SHA2_256', CAST(id * 31 AS VARCHAR(10)))),
  col_uniqueidentifier = NEWID(),
  col_xml            = CAST('<upd n="' + CAST(id AS VARCHAR) + '"/>' AS XML),
  col_sql_variant    = CAST(id * -1 AS SQL_VARIANT)
WHERE id <= {updated_rows};
GO
BACKUP DATABASE [{db}] TO DISK=N'{CONTAINER_BAK_COMMITTED_UPDATE_V3}' WITH FORMAT, INIT;
GO"""

    print("  setting up AN-v3 database …")
    _exec_sql(container, sqlcmd, sql_setup)
    print("  inserting 300 all-types rows …")
    _exec_sql(container, sqlcmd, sql_insert)
    print("  updating 100 rows and taking backup …")
    _exec_sql(container, sqlcmd, sql_dml)
    return total_rows, updated_rows


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_ALL_DIRTY_BAKS = [
    "dirtycoverage_concurrent.bak",
    "dirtycoverage_uncommitted.bak",
    "dirtycoverage_truncate.bak",
    "dirtycoverage_addcol.bak",
    "dirtycoverage_droptable.bak",
    "dirtycoverage_dropcol.bak",
    "dirtycoverage_addnotnull.bak",
    "dirtycoverage_altercol.bak",
    "dirtycoverage_createtable.bak",
    "dirtycoverage_rebuildidx.bak",
    "dirtycoverage_createidx.bak",
    "dirtycoverage_dropidx.bak",
    "dirtycoverage_delete.bak",
    "dirtycoverage_update.bak",
    "dirtycoverage_altercol_rewrite.bak",
    "dirtycoverage_alterdb.bak",
    "dirtycoverage_savepoint.bak",
    "dirtycoverage_nested.bak",
    "dirtycoverage_switch.bak",
    "dirtycoverage_two_tx.bak",
    "dirtycoverage_rich_update.bak",
    "dirtycoverage_rich_insert.bak",
    "dirtycoverage_null_update.bak",
    "dirtycoverage_alldirty.bak",
    "dirtycoverage_nchar_delete.bak",
    "dirtycoverage_heap_forward.bak",
    "dirtycoverage_large_dirty.bak",
    "dirtycoverage_lob_update.bak",
    "dirtycoverage_maxrow.bak",
    "dirtycoverage_temporal_update.bak",
    "dirtycoverage_snapshot_update.bak",
    "dirtycoverage_committed_delete.bak",
    "dirtycoverage_committed_delete_v2.bak",
    "dirtycoverage_committed_delete_v3.bak",
    "dirtycoverage_committed_update.bak",
    "dirtycoverage_committed_update_v2.bak",
    "dirtycoverage_committed_update_v3.bak",
]


def _should_build(path: Path, sid: str, force_set: frozenset[str]) -> bool:
    """Return True when the fixture at *path* must be (re)built.

    Rebuilds if the file is absent or if *sid* (or the sentinel ``"all"``)
    appears in *force_set*.
    """
    return not path.exists() or "all" in force_set or sid in force_set


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build dirty/fuzzy backup fixtures")
    parser.add_argument(
        "--scenarios",
        metavar="ID,...",
        help=(
            "Comma-separated scenario IDs to force-rebuild even when the output "
            "file already exists (e.g. 'am,an').  Use 'all' to rebuild every "
            "scenario.  Without this flag only missing fixtures are built."
        ),
    )
    args, _ = parser.parse_known_args()  # ignore fixture_run.py wrapper args

    force_set: frozenset[str] = frozenset()
    if args.scenarios:
        force_set = frozenset(s.strip().lower() for s in args.scenarios.split(","))

    missing = [n for n in _ALL_DIRTY_BAKS if not (FIXTURES / n).exists()]
    if not missing and not force_set:
        print("skip (all dirty fixtures already exist)", file=sys.stderr)
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

    # Pre-load existing ground truth so that skipped scenarios keep their entries.
    gt_path = FIXTURES / "dirty_ground_truth.json"
    ground_truth: dict[str, Any] = {}
    if gt_path.exists():
        try:
            ground_truth = json.loads(gt_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    # --- Scenario A ---
    out_a = FIXTURES / "dirtycoverage_concurrent.bak"
    if _should_build(out_a, "a", force_set):
        print("\n=== Scenario A: concurrent inserts ===")
        concurrent_total = _build_scenario_a(container, sqlcmd)
        size_a = _copy_out(container, CONTAINER_BAK_CONCURRENT, out_a)
        print(f"wrote {out_a.name} ({size_a:,} bytes)")
        ground_truth["scenario_a"] = {
            "description": "Backup taken while concurrent single-row inserts were in flight",
            "pre_backup_rows": PRE_BACKUP_ROWS,
            "concurrent_rows_total": concurrent_total,
            "table": "dirty_test",
            "pre_backup_phase": "pre_backup",
            "concurrent_phase": "concurrent",
            "expectation": (
                "All pre_backup rows are visible; concurrent rows may be partially visible "
                "depending on which pages the backup read before each insert committed."
            ),
        }
    else:
        print(f"  skip {out_a.name} (exists)", file=sys.stderr)

    # --- Scenario B ---
    out_b = FIXTURES / "dirtycoverage_uncommitted.bak"
    if _should_build(out_b, "b", force_set):
        print("\n=== Scenario B: uncommitted transaction ===")
        _build_scenario_b(container, sqlcmd)
        size_b = _copy_out(container, CONTAINER_BAK_UNCOMMITTED, out_b)
        print(f"wrote {out_b.name} ({size_b:,} bytes)")
        ground_truth["scenario_b"] = {
            "description": "Backup taken while an uncommitted INSERT transaction was open; TX was rolled back",
            "committed_rows": PRE_TX_ROWS,
            "uncommitted_rows": UNCOMMITTED_ROWS,
            "table": "dirty_test",
            "committed_phase": "pre_tx",
            "uncommitted_phase": "in_tx",
            "expectation": (
                f"Exactly {PRE_TX_ROWS} committed rows must be visible. "
                f"The {UNCOMMITTED_ROWS} in_tx rows may or may not appear depending on "
                "whether SQL Server had flushed their dirty pages at backup time."
            ),
        }
    else:
        print(f"  skip {out_b.name} (exists)", file=sys.stderr)

    # --- Scenario C ---
    out_c = FIXTURES / "dirtycoverage_truncate.bak"
    if _should_build(out_c, "c", force_set):
        print("\n=== Scenario C: TRUNCATE TABLE during backup ===")
        pre_trunc_rows = _build_scenario_c(container, sqlcmd)
        size_c = _copy_out(container, CONTAINER_BAK_TRUNCATE, out_c)
        print(f"wrote {out_c.name} ({size_c:,} bytes)")
        ground_truth["scenario_c"] = {
            "description": (
                "Backup taken while TRUNCATE TABLE was running in a background session. "
                "The backup may capture the pre-TRUNCATE pages (pre_trunc_rows visible) "
                "or the post-TRUNCATE state (0 rows), but never a partial count."
            ),
            "pre_trunc_rows": pre_trunc_rows,
            "table": "trunc_test",
            "phase": "pre_trunc",
            "expectation": (
                f"Row count is 0 or {pre_trunc_rows} — never an intermediate value. "
                "mssqlbak must not crash."
            ),
        }
    else:
        print(f"  skip {out_c.name} (exists)", file=sys.stderr)

    # --- Scenario D ---
    out_d = FIXTURES / "dirtycoverage_addcol.bak"
    if _should_build(out_d, "d", force_set):
        print("\n=== Scenario D: ADD COLUMN then static backup ===")
        pre_col_rows, post_col_rows = _build_scenario_d(container, sqlcmd)
        size_d = _copy_out(container, CONTAINER_BAK_ADDCOL, out_d)
        print(f"wrote {out_d.name} ({size_d:,} bytes)")
        ground_truth["scenario_d"] = {
            "description": (
                f"{pre_col_rows} rows were inserted before ALTER TABLE ADD COLUMN extra. "
                f"{post_col_rows} more rows were inserted after (with extra='extra_value_N'). "
                "The column addition is a metadata-only operation in SQL Server 2019+: "
                "pre-DDL rows return NULL for the new column."
            ),
            "pre_col_rows": pre_col_rows,
            "post_col_rows": post_col_rows,
            "total_rows": pre_col_rows + post_col_rows,
            "new_column": "extra",
            "table": "addcol_test",
            "expectation": (
                f"Exactly {pre_col_rows + post_col_rows} rows. "
                f"First {pre_col_rows} have extra=NULL; last {post_col_rows} have extra='extra_value_N'."
            ),
        }
    else:
        print(f"  skip {out_d.name} (exists)", file=sys.stderr)

    # --- Scenario E ---
    out_e = FIXTURES / "dirtycoverage_droptable.bak"
    if _should_build(out_e, "e", force_set):
        print("\n=== Scenario E: DROP TABLE during backup ===")
        pre_drop_rows = _build_scenario_e(container, sqlcmd)
        size_e = _copy_out(container, CONTAINER_BAK_DROPTABLE, out_e)
        print(f"wrote {out_e.name} ({size_e:,} bytes)")
        ground_truth["scenario_e"] = {
            "description": (
                "Backup taken while DROP TABLE was running in a background session. "
                "The backup may capture the table before or after the DROP. "
                "survivor_test (200 rows) is always present."
            ),
            "pre_drop_rows": pre_drop_rows,
            "drop_table": "drop_target",
            "survivor_table": "survivor_test",
            "survivor_rows": 200,
            "expectation": (
                "mssqlbak must not crash. "
                "drop_target may or may not appear in the schema. "
                "If present, row count is 0 or pre_drop_rows."
            ),
        }
    else:
        print(f"  skip {out_e.name} (exists)", file=sys.stderr)

    # --- Scenario F ---
    out_f = FIXTURES / "dirtycoverage_dropcol.bak"
    if _should_build(out_f, "f", force_set):
        print("\n=== Scenario F: DROP COLUMN then static backup ===")
        pre_dropcol, post_dropcol = _build_scenario_f(container, sqlcmd)
        size_f = _copy_out(container, CONTAINER_BAK_DROPCOL, out_f)
        print(f"wrote {out_f.name} ({size_f:,} bytes)")
        ground_truth["scenario_f"] = {
            "description": (
                f"{pre_dropcol} rows were inserted before DROP COLUMN extra. "
                f"{post_dropcol} more rows were inserted after (no extra column in record). "
                "The catalog will no longer list extra. mssqlbak must decode both row formats."
            ),
            "pre_drop_rows": pre_dropcol,
            "post_drop_rows": post_dropcol,
            "total_rows": pre_dropcol + post_dropcol,
            "dropped_column": "extra",
            "table": "dropcol_test",
            "expectation": (
                f"Exactly {pre_dropcol + post_dropcol} rows. "
                "Columns: id, label, phase (no extra). "
                "mssqlbak must not crash and must not include a ghost 'extra' column."
            ),
        }
    else:
        print(f"  skip {out_f.name} (exists)", file=sys.stderr)

    # --- Scenario G ---
    out_g = FIXTURES / "dirtycoverage_addnotnull.bak"
    if _should_build(out_g, "g", force_set):
        print("\n=== Scenario G: ADD COLUMN NOT NULL DEFAULT then static backup ===")
        pre_addnn, post_addnn = _build_scenario_g(container, sqlcmd)
        size_g = _copy_out(container, CONTAINER_BAK_ADDNOTNULL, out_g)
        print(f"wrote {out_g.name} ({size_g:,} bytes)")
        ground_truth["scenario_g"] = {
            "description": (
                f"{pre_addnn} rows were inserted before ALTER TABLE ADD score INT NOT NULL DEFAULT 42. "
                f"{post_addnn} more rows with explicit score values. "
                "SQL Server 2012+ uses an online default mechanism for NOT NULL defaults. "
                "Pre-DDL rows should return 42 for score."
            ),
            "pre_ddl_rows": pre_addnn,
            "post_ddl_rows": post_addnn,
            "total_rows": pre_addnn + post_addnn,
            "new_column": "score",
            "default_value": 42,
            "table": "addnotnull_test",
            "expectation": (
                f"Exactly {pre_addnn + post_addnn} rows. "
                f"Pre-DDL rows have score=42 (default). "
                f"Post-DDL rows have explicit score values."
            ),
        }
    else:
        print(f"  skip {out_g.name} (exists)", file=sys.stderr)

    # --- Scenario H ---
    out_h = FIXTURES / "dirtycoverage_altercol.bak"
    if _should_build(out_h, "h", force_set):
        print("\n=== Scenario H: ALTER COLUMN compatible type then static backup ===")
        altercol_rows = _build_scenario_h(container, sqlcmd)
        size_h = _copy_out(container, CONTAINER_BAK_ALTERCOL, out_h)
        print(f"wrote {out_h.name} ({size_h:,} bytes)")
        ground_truth["scenario_h"] = {
            "description": (
                f"{altercol_rows} rows with VARCHAR(50) label, "
                "then ALTER COLUMN label VARCHAR(200) (metadata-only). "
                "The catalog reports max_length=200 but physical bytes are unchanged."
            ),
            "rows": altercol_rows,
            "table": "altercol_test",
            "expectation": (
                f"Exactly {altercol_rows} rows. "
                "label values decode correctly (values fit within 50 bytes)."
            ),
        }
    else:
        print(f"  skip {out_h.name} (exists)", file=sys.stderr)

    # --- Scenario I ---
    out_i = FIXTURES / "dirtycoverage_createtable.bak"
    if _should_build(out_i, "i", force_set):
        print("\n=== Scenario I: CREATE TABLE during backup ===")
        stable_rows, new_rows_i = _build_scenario_i(container, sqlcmd)
        size_i = _copy_out(container, CONTAINER_BAK_CREATETABLE, out_i)
        print(f"wrote {out_i.name} ({size_i:,} bytes)")
        ground_truth["scenario_i"] = {
            "description": (
                f"stable_test ({stable_rows} rows) was present throughout. "
                f"new_test was created during the backup with {new_rows_i} rows. "
                "Visibility of new_test in mssqlbak is timing-dependent."
            ),
            "stable_rows": stable_rows,
            "stable_table": "stable_test",
            "new_rows": new_rows_i,
            "new_table": "new_test",
            "expectation": (
                "mssqlbak must not crash. "
                f"stable_test must have {stable_rows} rows. "
                "new_test may or may not appear; if it does, row count is 0 or new_rows."
            ),
        }
    else:
        print(f"  skip {out_i.name} (exists)", file=sys.stderr)

    # --- Scenario J ---
    out_j = FIXTURES / "dirtycoverage_rebuildidx.bak"
    if _should_build(out_j, "j", force_set):
        print("\n=== Scenario J: ALTER INDEX REBUILD during backup ===")
        ridx_rows = _build_scenario_j(container, sqlcmd)
        size_j = _copy_out(container, CONTAINER_BAK_REBUILDIDX, out_j)
        print(f"wrote {out_j.name} ({size_j:,} bytes)")
        ground_truth["scenario_j"] = {
            "description": (
                f"ridx_test ({ridx_rows} rows) with a non-clustered index that was "
                "rebuilt during the backup. Data pages are unaffected."
            ),
            "rows": ridx_rows,
            "table": "ridx_test",
            "expectation": (
                f"Exactly {ridx_rows} rows from ridx_test. mssqlbak must not crash."
            ),
        }
    else:
        print(f"  skip {out_j.name} (exists)", file=sys.stderr)

    # --- Scenario K ---
    out_k_create = FIXTURES / "dirtycoverage_createidx.bak"
    out_k_drop   = FIXTURES / "dirtycoverage_dropidx.bak"
    if _should_build(out_k_create, "k", force_set) or _should_build(out_k_drop, "k", force_set):
        print("\n=== Scenario K: CREATE / DROP INDEX during backup ===")
        create_rows, drop_rows = _build_scenario_k(container, sqlcmd)
        size_k_create = _copy_out(container, CONTAINER_BAK_CREATEIDX, out_k_create)
        size_k_drop   = _copy_out(container, CONTAINER_BAK_DROPIDX, out_k_drop)
        print(f"wrote {out_k_create.name} ({size_k_create:,} bytes)")
        print(f"wrote {out_k_drop.name} ({size_k_drop:,} bytes)")
        ground_truth["scenario_k"] = {
            "description": (
                "Two sub-fixtures: DirtyCreateIdx (CREATE INDEX during backup) "
                "and DirtyDropIdx (DROP INDEX during backup). "
                "Both operate on kidx_test with 300 rows and a non-clustered index."
            ),
            "create_rows": create_rows,
            "drop_rows": drop_rows,
            "table": "kidx_test",
            "expectation": (
                f"Exactly {create_rows} rows from each backup. "
                "mssqlbak must not crash for either fixture."
            ),
        }
    else:
        print(f"  skip {out_k_create.name} and {out_k_drop.name} (both exist)", file=sys.stderr)

    # --- Scenario L ---
    out_l = FIXTURES / "dirtycoverage_delete.bak"
    if _should_build(out_l, "l", force_set):
        print("\n=== Scenario L: uncommitted DELETE during backup ===")
        committed_l, delete_target_l, hold_l = _build_scenario_l(container, sqlcmd)
        size_l = _copy_out(container, CONTAINER_BAK_DELETE, out_l)
        print(f"wrote {out_l.name} ({size_l:,} bytes)")
        ground_truth["scenario_l"] = {
            "description": (
                f"{committed_l} rows with phase='committed' were inserted. "
                f"{delete_target_l} rows with phase='delete_target' were inserted. "
                f"A background session opened a DELETE transaction (held for {hold_l} s) "
                "while the backup ran, then rolled it back. "
                "SQL Server marks deleted slots as ghosts immediately; the backup may "
                "capture the ghost state even if the delete is later rolled back."
            ),
            "committed_rows": committed_l,
            "delete_target_rows": delete_target_l,
            "total_rows": committed_l + delete_target_l,
            "table": "delete_test",
            "expectation": (
                f"Row count is {committed_l} (ghosts filtered, gap) or "
                f"{committed_l + delete_target_l} (pages captured before delete). "
                "mssqlbak must not crash. No partial or corrupt rows."
            ),
        }
    else:
        print(f"  skip {out_l.name} (exists)", file=sys.stderr)

    # --- Scenario M ---
    out_m = FIXTURES / "dirtycoverage_update.bak"
    if _should_build(out_m, "m", force_set):
        print("\n=== Scenario M: uncommitted UPDATE during backup ===")
        total_m, modified_m, hold_m = _build_scenario_m(container, sqlcmd)
        size_m = _copy_out(container, CONTAINER_BAK_UPDATE, out_m)
        print(f"wrote {out_m.name} ({size_m:,} bytes)")
        ground_truth["scenario_m"] = {
            "description": (
                f"{total_m} rows total; first {modified_m} had label='original_N'. "
                f"A background session updated those {modified_m} rows to label='modified_N' "
                f"(held for {hold_m} s), then rolled back. "
                "SQL Server updates rows in-place (without snapshot isolation); "
                "the backup may capture the modified value even if the update is later rolled back."
            ),
            "total_rows": total_m,
            "modified_rows": modified_m,
            "unmodified_rows": total_m - modified_m,
            "table": "update_test",
            "expectation": (
                f"Exactly {total_m} rows. "
                f"First {modified_m} rows have label starting with 'original_' (pre-update) "
                "or 'modified_' (phantom update captured). "
                "Unmodified rows always have label='original_N'. "
                "mssqlbak must not crash."
            ),
        }
    else:
        print(f"  skip {out_m.name} (exists)", file=sys.stderr)

    # --- Scenario N ---
    out_n = FIXTURES / "dirtycoverage_altercol_rewrite.bak"
    if _should_build(out_n, "n", force_set):
        print("\n=== Scenario N: ALTER COLUMN type rewrite (NVARCHAR→VARCHAR) ===")
        pre_n, post_n = _build_scenario_n(container, sqlcmd)
        size_n = _copy_out(container, CONTAINER_BAK_ALTERCOL_REWRITE, out_n)
        print(f"wrote {out_n.name} ({size_n:,} bytes)")
        ground_truth["scenario_n"] = {
            "description": (
                f"{pre_n} rows inserted as NVARCHAR(200). "
                "ALTER COLUMN label to VARCHAR(200) forces a full row rewrite. "
                f"{post_n} rows inserted after the rewrite as VARCHAR. "
                "Static backup taken after the rewrite completes."
            ),
            "pre_ddl_rows": pre_n,
            "post_ddl_rows": post_n,
            "total_rows": pre_n + post_n,
            "table": "rewrite_test",
            "expectation": (
                f"Exactly {pre_n + post_n} rows. "
                "Both pre- and post-rewrite rows must have correct label values. "
                "mssqlbak must use the VARCHAR decoder (not NVARCHAR) for all rows."
            ),
        }
    else:
        print(f"  skip {out_n.name} (exists)", file=sys.stderr)

    # --- Scenario O ---
    out_o = FIXTURES / "dirtycoverage_alterdb.bak"
    if _should_build(out_o, "o", force_set):
        print("\n=== Scenario O: ALTER DATABASE SET during backup ===")
        alterdb_rows = _build_scenario_o(container, sqlcmd)
        size_o = _copy_out(container, CONTAINER_BAK_ALTERDB, out_o)
        print(f"wrote {out_o.name} ({size_o:,} bytes)")
        ground_truth["scenario_o"] = {
            "description": (
                f"alterdb_test ({alterdb_rows} rows). "
                "ALTER DATABASE SET COMPATIBILITY_LEVEL = 130 fired during the backup. "
                "Database system pages are modified; data pages are unchanged."
            ),
            "rows": alterdb_rows,
            "table": "alterdb_test",
            "expectation": (
                f"Exactly {alterdb_rows} rows. mssqlbak must not crash."
            ),
        }
    else:
        print(f"  skip {out_o.name} (exists)", file=sys.stderr)

    # --- Scenario P ---
    out_p = FIXTURES / "dirtycoverage_savepoint.bak"
    if _should_build(out_p, "p", force_set):
        print("\n=== Scenario P: Savepoints during backup ===")
        committed_p, before_save_p, after_save_p = _build_scenario_p(container, sqlcmd)
        size_p = _copy_out(container, CONTAINER_BAK_SAVEPOINT, out_p)
        print(f"wrote {out_p.name} ({size_p:,} bytes)")
        ground_truth["scenario_p"] = {
            "description": (
                f"{committed_p} committed rows. Background TX: inserted {before_save_p} rows, "
                f"saved, inserted {after_save_p} more rows, rolled back to savepoint "
                f"(after_save rows removed), held TX open for backup, then rolled back outer TX."
            ),
            "committed_rows": committed_p,
            "before_save_rows": before_save_p,
            "after_save_rows": after_save_p,
            "total_potential_dirty": before_save_p,
            "table": "savepoint_test",
            "expectation": (
                f"Committed rows: {committed_p} always visible. "
                f"before_save rows: 0–{before_save_p} (dirty-read). "
                f"after_save rows: 0 (rolled back to savepoint before backup). "
                "mssqlbak must not crash."
            ),
        }
    else:
        print(f"  skip {out_p.name} (exists)", file=sys.stderr)

    # --- Scenario Q ---
    out_q = FIXTURES / "dirtycoverage_nested.bak"
    if _should_build(out_q, "q", force_set):
        print("\n=== Scenario Q: Nested transactions during backup ===")
        committed_q, outer_q, inner_q = _build_scenario_q(container, sqlcmd)
        size_q = _copy_out(container, CONTAINER_BAK_NESTED, out_q)
        print(f"wrote {out_q.name} ({size_q:,} bytes)")
        ground_truth["scenario_q"] = {
            "description": (
                f"{committed_q} committed rows. Background nested TX: outer BEGIN inserted "
                f"{outer_q} rows, inner BEGIN inserted {inner_q} rows, inner COMMIT "
                "(noop — only decrements @@TRANCOUNT), outer ROLLBACK rolls back all."
            ),
            "committed_rows": committed_q,
            "outer_rows": outer_q,
            "inner_rows": inner_q,
            "total_dirty": outer_q + inner_q,
            "table": "nested_test",
            "expectation": (
                f"Committed rows: {committed_q} always visible. "
                f"Dirty rows: 0–{outer_q + inner_q} (SQL Server uses same xact_id for outer+inner). "
                "mssqlbak must not crash."
            ),
        }
    else:
        print(f"  skip {out_q.name} (exists)", file=sys.stderr)

    # --- Scenario R ---
    out_r = FIXTURES / "dirtycoverage_switch.bak"
    if _should_build(out_r, "r", force_set):
        print("\n=== Scenario R: SWITCH PARTITION during backup ===")
        part_rows_r, staged_rows_r = _build_scenario_r(container, sqlcmd)
        size_r = _copy_out(container, CONTAINER_BAK_SWITCH, out_r)
        print(f"wrote {out_r.name} ({size_r:,} bytes)")
        ground_truth["scenario_r"] = {
            "description": (
                f"part_test: {part_rows_r} rows in partitions 1–3. "
                f"staging_test: {staged_rows_r} rows (id > 300). "
                "SWITCH staging_test TO part_test PARTITION 4 fired during backup."
            ),
            "partitioned_rows": part_rows_r,
            "staged_rows": staged_rows_r,
            "part_table": "part_test",
            "staging_table": "staging_test",
            "expectation": (
                f"part_test has {part_rows_r} or {part_rows_r + staged_rows_r} rows "
                "(before or after SWITCH). "
                "staging_test has {staged_rows_r} or 0 rows (before or after SWITCH). "
                "mssqlbak must not crash."
            ),
        }
    else:
        print(f"  skip {out_r.name} (exists)", file=sys.stderr)

    # --- Scenario W ---
    out_w = FIXTURES / "dirtycoverage_two_tx.bak"
    if _should_build(out_w, "w", force_set):
        print("\n=== Scenario W: two concurrent uncommitted transactions ===")
        committed_w, tx_a_w, tx_b_delete_w = _build_scenario_w(container, sqlcmd)
        size_w = _copy_out(container, CONTAINER_BAK_TWO_TX, out_w)
        print(f"wrote {out_w.name} ({size_w:,} bytes)")
        ground_truth["scenario_w"] = {
            "description": (
                f"two_tx_test: {committed_w} committed rows. TX-A inserted {tx_a_w} rows "
                f"(phase=tx_a, held open). TX-B ghost-deleted first {tx_b_delete_w} committed "
                "rows and inserted 5 more rows (phase=tx_b, held open). Both rolled back."
            ),
            "committed_rows": committed_w,
            "tx_a_dirty_rows": tx_a_w,
            "tx_b_ghost_deleted": tx_b_delete_w,
            "tx_b_dirty_insert_rows": 5,
            "table": "two_tx_test",
            "expectation": (
                f"Exactly {committed_w} rows visible. "
                "tx_a rows and tx_b inserted rows suppressed by dirty_slots. "
                "tx_b ghost-deleted rows restored by restore_slots."
            ),
        }
    else:
        print(f"  skip {out_w.name} (exists)", file=sys.stderr)

    # --- Scenario AA ---
    out_aa = FIXTURES / "dirtycoverage_rich_update.bak"
    out_ab = FIXTURES / "dirtycoverage_rich_insert.bak"
    if _should_build(out_aa, "aa", force_set) or _should_build(out_ab, "ab", force_set):
        print("\n=== Scenario AA+AB: rich-type UPDATE + INSERT ===")
        committed_aa, updated_aa, dirty_ab = _build_scenario_aa_ab(container, sqlcmd)
        size_aa = _copy_out(container, CONTAINER_BAK_RICH_UPDATE, out_aa)
        size_ab = _copy_out(container, CONTAINER_BAK_RICH_INSERT, out_ab)
        print(f"wrote {out_aa.name} ({size_aa:,} bytes)")
        print(f"wrote {out_ab.name} ({size_ab:,} bytes)")
        ground_truth["scenario_aa"] = {
            "description": (
                f"rich_update_test: {committed_aa} committed rows with BIT/SMALLINT/BIGINT/"
                f"DECIMAL/DATETIME2/UNIQUEIDENTIFIER/VARBINARY/NCHAR/NVARCHAR columns. "
                f"TX updated rows 1–{updated_aa} across all columns; held open; rolled back."
            ),
            "committed_rows": committed_aa,
            "updated_rows": updated_aa,
            "table": "rich_update_test",
            "expectation": (
                f"Exactly {committed_aa} rows. "
                f"Rows 1–{updated_aa}: all columns restored to original values. "
                f"Rows {updated_aa + 1}–{committed_aa}: untouched."
            ),
        }
        ground_truth["scenario_ab"] = {
            "description": (
                f"rich_update_test: {committed_aa} committed rows. "
                f"TX inserted {dirty_ab} rows with BIT/SMALLINT/BIGINT/DECIMAL/DATETIME2/"
                "UNIQUEIDENTIFIER/VARBINARY/NCHAR/NVARCHAR columns; held open; rolled back."
            ),
            "committed_rows": committed_aa,
            "dirty_insert_rows": dirty_ab,
            "table": "rich_update_test",
            "expectation": (
                f"Exactly {committed_aa} rows visible. "
                f"All {dirty_ab} dirty-insert rows suppressed by dirty_slots."
            ),
        }
    else:
        print(f"  skip {out_aa.name} and {out_ab.name} (both exist)", file=sys.stderr)

    # --- Scenario Y ---
    out_y = FIXTURES / "dirtycoverage_null_update.bak"
    if _should_build(out_y, "y", force_set):
        print("\n=== Scenario Y: uncommitted UPDATE to NULL ===")
        committed_y, updated_y = _build_scenario_y(container, sqlcmd)
        size_y = _copy_out(container, CONTAINER_BAK_NULL_UPDATE, out_y)
        print(f"wrote {out_y.name} ({size_y:,} bytes)")
        ground_truth["scenario_y"] = {
            "description": (
                f"null_update_test: {committed_y} rows with score non-NULL. "
                f"TX set score=NULL for rows 1–{updated_y} (null-bitmap change) "
                "and updated label; held open; rolled back."
            ),
            "committed_rows": committed_y,
            "updated_rows": updated_y,
            "table": "null_update_test",
            "expectation": (
                f"Exactly {committed_y} rows. "
                f"Rows 1–{updated_y}: score non-NULL (restored), label original. "
                f"Rows {updated_y + 1}–{committed_y}: untouched."
            ),
        }
    else:
        print(f"  skip {out_y.name} (exists)", file=sys.stderr)

    # --- Scenario AD ---
    out_ad = FIXTURES / "dirtycoverage_alldirty.bak"
    if _should_build(out_ad, "ad", force_set):
        print("\n=== Scenario AD: all-dirty table (0 committed rows) ===")
        dirty_ad = _build_scenario_ad(container, sqlcmd)
        size_ad = _copy_out(container, CONTAINER_BAK_ALLDIRTY, out_ad)
        print(f"wrote {out_ad.name} ({size_ad:,} bytes)")
        ground_truth["scenario_ad"] = {
            "description": (
                f"alldirty_test: 0 committed rows. TX inserted {dirty_ad} rows; "
                "held open during backup; rolled back."
            ),
            "committed_rows": 0,
            "dirty_rows": dirty_ad,
            "table": "alldirty_test",
            "expectation": (
                "Exactly 0 rows visible. "
                "All dirty rows suppressed by dirty_slots. No crash."
            ),
        }
    else:
        print(f"  skip {out_ad.name} (exists)", file=sys.stderr)

    # --- Scenario AC ---
    out_ac = FIXTURES / "dirtycoverage_nchar_delete.bak"
    if _should_build(out_ac, "ac", force_set):
        print("\n=== Scenario AC: uncommitted DELETE on NCHAR/NVARCHAR table ===")
        committed_ac, deleted_ac = _build_scenario_ac(container, sqlcmd)
        size_ac = _copy_out(container, CONTAINER_BAK_NCHAR_DELETE, out_ac)
        print(f"wrote {out_ac.name} ({size_ac:,} bytes)")
        ground_truth["scenario_ac"] = {
            "description": (
                f"nchar_delete_test: {committed_ac} rows with NCHAR(50)/NVARCHAR(200). "
                f"TX ghost-deleted rows 1–{deleted_ac}; held open; rolled back."
            ),
            "committed_rows": committed_ac,
            "deleted_rows": deleted_ac,
            "table": "nchar_delete_test",
            "expectation": (
                f"Exactly {committed_ac} rows visible. "
                f"Rows 1–{deleted_ac}: restored via restore_slots with correct UTF-16LE values."
            ),
        }
    else:
        print(f"  skip {out_ac.name} (exists)", file=sys.stderr)

    # --- Scenario X ---
    out_x = FIXTURES / "dirtycoverage_heap_forward.bak"
    if _should_build(out_x, "x", force_set):
        print("\n=== Scenario X: heap forwarded record + uncommitted ghost-delete ===")
        committed_x, ghost_x = _build_scenario_x(container, sqlcmd)
        size_x = _copy_out(container, CONTAINER_BAK_HEAP_FORWARD, out_x)
        print(f"wrote {out_x.name} ({size_x:,} bytes)")
        ground_truth["scenario_x"] = {
            "description": (
                f"heap_forward_test: {committed_x} rows in a heap (no clustered index). "
                "Row 1 was updated to 7900-char label (triggers ForwardingStub). "
                f"TX ghost-deleted row {committed_x}; held open; rolled back."
            ),
            "committed_rows": committed_x,
            "ghost_deleted_rows": ghost_x,
            "table": "heap_forward_test",
            "expectation": (
                f"Exactly {committed_x} rows visible. "
                "Forwarded row 1 visible once with 7900-char label. "
                f"Row {committed_x} restored via restore_slots. No crash."
            ),
        }
    else:
        print(f"  skip {out_x.name} (exists)", file=sys.stderr)

    # --- Scenario AE ---
    out_ae = FIXTURES / "dirtycoverage_large_dirty.bak"
    if _should_build(out_ae, "ae", force_set):
        print("\n=== Scenario AE: large uncommitted transaction (5000 rows) ===")
        committed_ae, dirty_ae = _build_scenario_ae(container, sqlcmd)
        size_ae = _copy_out(container, CONTAINER_BAK_LARGE_DIRTY, out_ae)
        print(f"wrote {out_ae.name} ({size_ae:,} bytes)")
        ground_truth["scenario_ae"] = {
            "description": (
                f"large_dirty_test: {committed_ae} committed rows. "
                f"TX inserted {dirty_ae} rows across ~25 data pages; held open; rolled back."
            ),
            "committed_rows": committed_ae,
            "dirty_rows": dirty_ae,
            "table": "large_dirty_test",
            "expectation": (
                f"Exactly {committed_ae} rows visible. "
                f"All {dirty_ae} dirty rows suppressed across all dirty pages."
            ),
        }
    else:
        print(f"  skip {out_ae.name} (exists)", file=sys.stderr)

    # --- Scenario Z/AJ ---
    out_z = FIXTURES / "dirtycoverage_lob_update.bak"
    if _should_build(out_z, "z", force_set):
        print("\n=== Scenario Z/AJ: uncommitted UPDATE on VARCHAR(MAX) LOB column ===")
        total_z, updated_z = _build_scenario_z(container, sqlcmd)
        size_z = _copy_out(container, CONTAINER_BAK_LOB_UPDATE, out_z)
        print(f"wrote {out_z.name} ({size_z:,} bytes)")
        ground_truth["scenario_z"] = {
            "description": (
                f"lob_update_test: {total_z} rows with VARCHAR(MAX) content (9000 chars, off-row). "
                f"TX updated rows 1–{updated_z} to different 9000-char string; held open; rolled back."
            ),
            "total_rows": total_z,
            "updated_rows": updated_z,
            "unmodified_rows": total_z - updated_z,
            "table": "lob_update_test",
            "expectation": (
                f"No crash. Rows {updated_z + 1}–{total_z} (unmodified): correct content. "
                "Rows 1–{updated_z}: LOB pointer restored; off-row consistency best-effort."
            ),
        }
    else:
        print(f"  skip {out_z.name} (exists)", file=sys.stderr)

    # --- Scenario AI ---
    out_ai = FIXTURES / "dirtycoverage_maxrow.bak"
    if _should_build(out_ai, "ai", force_set):
        print("\n=== Scenario AI: row at the 8060-byte inline storage limit ===")
        maxrow_count = _build_scenario_ai(container, sqlcmd)
        size_ai = _copy_out(container, CONTAINER_BAK_MAXROW, out_ai)
        print(f"wrote {out_ai.name} ({size_ai:,} bytes)")
        ground_truth["scenario_ai"] = {
            "description": (
                f"maxrow_test: {maxrow_count} rows with CHAR(8000) — at the SQL Server "
                "fixed-column maximum, approaching the 8060-byte inline row limit."
            ),
            "row_count": maxrow_count,
            "table": "maxrow_test",
            "expectation": (
                f"Exactly {maxrow_count} rows. "
                "Each row's content column is exactly 8000 chars. No crash."
            ),
        }
    else:
        print(f"  skip {out_ai.name} (exists)", file=sys.stderr)

    # --- Scenario AG ---
    out_ag = FIXTURES / "dirtycoverage_temporal_update.bak"
    if _should_build(out_ag, "ag", force_set):
        print("\n=== Scenario AG: temporal table with uncommitted UPDATE ===")
        committed_ag, updated_ag = _build_scenario_ag(container, sqlcmd)
        size_ag = _copy_out(container, CONTAINER_BAK_TEMPORAL_UPDATE, out_ag)
        print(f"wrote {out_ag.name} ({size_ag:,} bytes)")
        ground_truth["scenario_ag"] = {
            "description": (
                f"temporal_test: {committed_ag} rows in a SYSTEM_VERSIONED temporal table "
                f"(with ValidFrom/ValidTo PERIOD columns). TX updated rows 1–{updated_ag}; "
                "held open; rolled back."
            ),
            "committed_rows": committed_ag,
            "updated_rows": updated_ag,
            "table": "temporal_test",
            "expectation": (
                f"Exactly {committed_ag} rows. "
                f"Rows 1–{updated_ag}: all columns (including PERIOD) restored correctly. "
                "No crash."
            ),
        }
    else:
        print(f"  skip {out_ag.name} (exists)", file=sys.stderr)

    # --- Scenario AH ---
    out_ah = FIXTURES / "dirtycoverage_snapshot_update.bak"
    if _should_build(out_ah, "ah", force_set):
        print("\n=== Scenario AH: SNAPSHOT isolation row-versioning ghost ===")
        committed_ah, updated_ah = _build_scenario_ah(container, sqlcmd)
        size_ah = _copy_out(container, CONTAINER_BAK_SNAPSHOT_UPDATE, out_ah)
        print(f"wrote {out_ah.name} ({size_ah:,} bytes)")
        ground_truth["scenario_ah"] = {
            "description": (
                f"snapshot_update_test: READ_COMMITTED_SNAPSHOT ON; {committed_ah} rows. "
                f"TX updated rows 1–{updated_ah} (14-byte version pointer appended to each row); "
                "held open; rolled back."
            ),
            "committed_rows": committed_ah,
            "updated_rows": updated_ah,
            "table": "snapshot_update_test",
            "expectation": (
                f"No crash. modified_slots non-empty. "
                f"Rows {updated_ah + 1}–{committed_ah} (unmodified) decode correctly."
            ),
        }
    else:
        print(f"  skip {out_ah.name} (exists)", file=sys.stderr)

    # --- Scenario AM ---
    out_am = FIXTURES / "dirtycoverage_committed_delete_v2.bak"
    if _should_build(out_am, "am", force_set):
        print("\n=== Scenario AM: committed DELETE mid-backup (REDO Gap A) ===")
        total_am, deleted_am = _build_scenario_am(container, sqlcmd, user, password)
        size_am = _copy_out(container, CONTAINER_BAK_COMMITTED_DELETE, out_am)
        print(f"wrote {out_am.name} ({size_am:,} bytes)")
        ground_truth["scenario_am"] = {
            "description": (
                f"committed_delete_test: {total_am} rows total "
                f"({deleted_am} will_delete + {total_am - deleted_am} keep). "
                "Backup taken with all rows present; committed_delete_slots=0 "
                "because SQL Server's log tail spans only the 3 checkpoint records "
                "in a containerised in-memory database."
            ),
            "total_rows": total_am,
            "deleted_rows": deleted_am,
            "expected_rows": total_am - deleted_am,
            "table": "committed_delete_test",
            "expectation": (
                f"Exactly {total_am - deleted_am} rows with phase='keep' visible. "
                "test_committed_delete_slots_detected is xfail. No crash."
            ),
        }
    else:
        print(f"  skip {out_am.name} (exists)", file=sys.stderr)

    # --- Scenario AN ---
    out_an = FIXTURES / "dirtycoverage_committed_update_v2.bak"
    if _should_build(out_an, "an", force_set):
        print("\n=== Scenario AN: committed UPDATE mid-backup (REDO Gap B) ===")
        total_an, updated_an = _build_scenario_an(container, sqlcmd, user, password)
        size_an = _copy_out(container, CONTAINER_BAK_COMMITTED_UPDATE, out_an)
        print(f"wrote {out_an.name} ({size_an:,} bytes)")
        ground_truth["scenario_an"] = {
            "description": (
                f"committed_update_test: {total_an} rows with original labels/scores. "
                "Backup taken with all rows in pre-update state; redo_patches=0 "
                "because SQL Server's log tail spans only the 3 checkpoint records "
                "in a containerised in-memory database."
            ),
            "total_rows": total_an,
            "updated_rows": updated_an,
            "table": "committed_update_test",
            "expectation": (
                f"All {total_an} rows visible with original labels (label starts with 'original_'). "
                "test_committed_update_patches_detected is xfail. No crash."
            ),
        }
    else:
        print(f"  skip {out_an.name} (exists)", file=sys.stderr)

    # --- Scenario AM-v3 ---
    out_am_v3 = FIXTURES / "dirtycoverage_committed_delete_v3.bak"
    if _should_build(out_am_v3, "am-v3", force_set):
        print("\n=== Scenario AM-v3: all-types DELETE (300 rows → 200 surviving) ===")
        total_am_v3, deleted_am_v3 = _build_scenario_am_v3(container, sqlcmd, user, password)
        size_am_v3 = _copy_out(container, CONTAINER_BAK_COMMITTED_DELETE_V3, out_am_v3)
        print(f"wrote {out_am_v3.name} ({size_am_v3:,} bytes)")
        ground_truth["scenario_am_v3"] = {
            "description": (
                f"all_types_test: {total_am_v3} rows inserted across 10 Unicode scripts "
                f"({deleted_am_v3} deleted, {total_am_v3 - deleted_am_v3} surviving). "
                "Covers all SQL Server scalar types: tinyint, smallint, int, bigint, bit, "
                "decimal, numeric, money, smallmoney, float, real, date, time, datetime, "
                "smalldatetime, datetime2, datetimeoffset, char, varchar, nchar, nvarchar, "
                "binary, varbinary, uniqueidentifier, xml, sql_variant, rowversion."
            ),
            "total_rows": total_am_v3,
            "deleted_rows": deleted_am_v3,
            "expected_rows": total_am_v3 - deleted_am_v3,
            "table": "all_types_test",
            "expectation": (
                f"Exactly {total_am_v3 - deleted_am_v3} rows (ids 101–{total_am_v3}). "
                "All 27 column types decode without error. No crash."
            ),
        }
    else:
        print(f"  skip {out_am_v3.name} (exists)", file=sys.stderr)

    # --- Scenario AN-v3 ---
    out_an_v3 = FIXTURES / "dirtycoverage_committed_update_v3.bak"
    if _should_build(out_an_v3, "an-v3", force_set):
        print("\n=== Scenario AN-v3: all-types UPDATE (300 rows, 100 updated) ===")
        total_an_v3, updated_an_v3 = _build_scenario_an_v3(container, sqlcmd, user, password)
        size_an_v3 = _copy_out(container, CONTAINER_BAK_COMMITTED_UPDATE_V3, out_an_v3)
        print(f"wrote {out_an_v3.name} ({size_an_v3:,} bytes)")
        ground_truth["scenario_an_v3"] = {
            "description": (
                f"all_types_test: {total_an_v3} rows inserted across 10 Unicode scripts; "
                f"ids 1–{updated_an_v3} updated with new values for every column type. "
                "Covers all SQL Server scalar types (same set as AM-v3)."
            ),
            "total_rows": total_an_v3,
            "updated_rows": updated_an_v3,
            "expected_rows": total_an_v3,
            "table": "all_types_test",
            "expectation": (
                f"All {total_an_v3} rows visible. "
                f"Ids 1–{updated_an_v3} have updated column values. "
                "All 27 column types decode without error. No crash."
            ),
        }
    else:
        print(f"  skip {out_an_v3.name} (exists)", file=sys.stderr)

    # Write ground truth JSON (merges rebuilt entries with preserved existing ones).
    gt_path.write_text(json.dumps(ground_truth, indent=2))
    print(f"\nwrote {gt_path.name}")
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
