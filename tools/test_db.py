"""Test results database — SQLite store for mssqlbak pytest runs.

Architecture
------------
``record``   Invokes ``pytest.main()`` with a built-in plugin that writes each
             test result to SQLite *as it finishes* (no text parsing).

``query``    SQL-filtered table of results across all recorded runs.

``summary``  Human-friendly per-run breakdown with failure detail.

``compare``  Regression / fix diff between any two runs.

``rerun``    Print or execute the rerun command for any test.

``sql``      Run a raw SQL query against the results database.

Schema
------
``runs``          One row per pytest invocation.
``test_results``  One row per test × run.

Usage
-----
    # Record a full run (passes extra pytest args after --):
    python -m tools.test_db record [--db PATH] [-- -k pattern --ignore=...]

    # Query failures in the latest run:
    python -m tools.test_db query --status FAILED

    # Summarise run 3:
    python -m tools.test_db summary --run-id 3

    # Compare two runs:
    python -m tools.test_db compare 2 3

    # Rerun one specific failing test:
    python -m tools.test_db rerun "tests/test_foo.py::test_bar"

    # Raw SQL:
    python -m tools.test_db sql "SELECT status, count(*) FROM test_results GROUP BY status"

The database defaults to ``~/.mssqlbak/test_results.db``.
"""
from __future__ import annotations

import gzip
import io
import json
import os
import shlex
import sqlite3
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
import typer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_DB  = Path.home() / ".mssqlbak" / "test_results.db"
DEFAULT_LOGS = Path.home() / ".mssqlbak" / "logs"

MSSQL_VERSION_MAP: dict[int, str] = {
    957: "SQL Server 2022 (16.x)",
    904: "SQL Server 2019 (15.x)",
    870: "SQL Server 2017 (14.x)",
    852: "SQL Server 2016 (13.x)",
    782: "SQL Server 2014 (12.x)",
    706: "SQL Server 2012 (11.x)",
    684: "SQL Server 2008 R2 (10.5x)",
    655: "SQL Server 2008 (10.x)",
}

PROJECT_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

_DDL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS runs (
    run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    recorded_at     TEXT    NOT NULL,
    commit_hash     TEXT    NOT NULL,
    commit_short    TEXT    NOT NULL,
    commit_message  TEXT    NOT NULL,
    branch          TEXT    NOT NULL,
    db_source_ver   TEXT    NOT NULL,
    db_internal_ver INTEGER NOT NULL,
    pytest_args     TEXT    NOT NULL,
    total           INTEGER NOT NULL DEFAULT 0,
    passed          INTEGER NOT NULL DEFAULT 0,
    failed          INTEGER NOT NULL DEFAULT 0,
    errored         INTEGER NOT NULL DEFAULT 0,
    skipped         INTEGER NOT NULL DEFAULT 0,
    xfailed         INTEGER NOT NULL DEFAULT 0,
    xpassed         INTEGER NOT NULL DEFAULT 0,
    duration_s      REAL    NOT NULL DEFAULT 0,
    log_path        TEXT                        -- path to the gzipped full pytest output
);

CREATE TABLE IF NOT EXISTS test_results (
    result_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES runs(run_id),
    test_id         TEXT    NOT NULL,
    test_module     TEXT    NOT NULL,
    test_name       TEXT    NOT NULL,
    test_params     TEXT,
    status          TEXT    NOT NULL,
    duration_s      REAL    NOT NULL DEFAULT 0,
    failure_reason  TEXT,
    failure_detail  TEXT,
    rerun_cmd       TEXT    NOT NULL,
    markers         TEXT
);

CREATE INDEX IF NOT EXISTS idx_tr_run    ON test_results(run_id);
CREATE INDEX IF NOT EXISTS idx_tr_status ON test_results(status);
CREATE INDEX IF NOT EXISTS idx_tr_testid ON test_results(test_id);
CREATE INDEX IF NOT EXISTS idx_tr_module ON test_results(test_module);
"""


def _open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(_DDL)
    # Migrate existing databases that predate the log_path column.
    existing_cols = {row[1] for row in con.execute("PRAGMA table_info(runs)")}
    if "log_path" not in existing_cols:
        con.execute("ALTER TABLE runs ADD COLUMN log_path TEXT")
    con.commit()
    return con


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(PROJECT_ROOT), *args],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def _git_info() -> dict[str, str]:
    commit_hash = _git("rev-parse", "HEAD") or "unknown"
    commit_short = commit_hash[:8] if commit_hash != "unknown" else "unknown"
    return {
        "commit_hash": commit_hash,
        "commit_short": commit_short,
        "commit_message": _git("log", "-1", "--format=%s") or "",
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD") or "unknown",
    }


# ---------------------------------------------------------------------------
# SQL Server version detection
# ---------------------------------------------------------------------------

def _detect_db_version() -> tuple[int, str]:
    """Read the boot page of the first available fixture to find the SQL Server version."""
    try:
        from mssqlbak.mtf import extract_mdf_files
        from mssqlbak.pages import PageStore

        fixtures = sorted((PROJECT_ROOT / "tests" / "fixtures").glob("*.bak"))
        if not fixtures:
            return 0, "unknown"
        images = extract_mdf_files(str(fixtures[0]))
        store = PageStore(images)
        raw = store.page(9, 1).raw
        ver = struct.unpack_from("<H", raw, 100)[0]
        label = MSSQL_VERSION_MAP.get(ver, f"SQL Server internal v{ver}")
        return ver, label
    except Exception:
        return 0, "unknown"


# ---------------------------------------------------------------------------
# pytest plugin (records results directly into SQLite while tests run)
# ---------------------------------------------------------------------------

class _TestDBPlugin:
    """pytest plugin: write each test outcome to SQLite as it completes."""

    def __init__(
        self,
        con: sqlite3.Connection,
        run_id: int,
        log_dir: Path,
    ) -> None:
        self._con     = con
        self._run_id  = run_id
        self._log_dir = log_dir
        self._counts: dict[str, int] = {
            "passed": 0, "failed": 0, "errored": 0,
            "skipped": 0, "xfailed": 0, "xpassed": 0,
        }
        self._start   = time.monotonic()
        self._log_buf = io.StringIO()  # captures all pytest terminal output

    # ------------------------------------------------------------------

    @staticmethod
    def _node_parts(nodeid: str) -> tuple[str, str, str | None]:
        """Split nodeid → (module, test_name, params | None)."""
        module, _, rest = nodeid.partition("::")
        test_name, _, params = rest.partition("[")
        return module, test_name, params.rstrip("]") or None

    @staticmethod
    def _status(report: pytest.TestReport) -> str:
        wasxfail = hasattr(report, "wasxfail")
        if report.when == "call":
            if report.passed:
                return "XPASS" if wasxfail else "PASSED"
            if report.failed:
                return "XFAIL" if wasxfail else "FAILED"
            if report.skipped:
                return "XFAIL" if wasxfail else "SKIPPED"
        if report.when in ("setup", "teardown") and report.failed:
            return "ERROR"
        if report.when == "setup" and report.skipped:
            return "SKIPPED"
        return ""

    @staticmethod
    def _longrepr(report: pytest.TestReport) -> tuple[str | None, str | None]:
        """Extract (one-line reason, full detail) from a report."""
        if not report.longrepr:
            return None, None
        full = str(report.longrepr)
        reason = full.splitlines()[-1] if full else None
        return reason, full

    # ------------------------------------------------------------------

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        status = self._status(report)
        if not status:
            return

        nodeid   = report.nodeid
        duration = round(getattr(report, "duration", 0.0), 4)
        module, test_name, params = self._node_parts(nodeid)
        reason, detail = self._longrepr(report)

        # Append compact line to the in-memory log buffer
        self._log_buf.write(f"{status:<8} {duration:>8.3f}s  {nodeid}\n")
        if detail:
            for line in detail.splitlines():
                self._log_buf.write(f"         {line}\n")

        markers_json = None
        try:
            markers = [k for k in (report.keywords or {}) if not k.startswith("_")]
            markers_json = json.dumps(markers)
        except Exception:
            pass

        self._con.execute(
            """
            INSERT OR REPLACE INTO test_results
              (run_id, test_id, test_module, test_name, test_params,
               status, duration_s, failure_reason, failure_detail, rerun_cmd, markers)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                self._run_id,
                nodeid,
                module,
                test_name,
                params,
                status,
                duration,
                reason,
                detail,
                f"python -m pytest {shlex.quote(nodeid)} -v --tb=short",
                markers_json,
            ),
        )
        self._con.commit()

        key_map = {
            "PASSED": "passed", "FAILED": "failed", "ERROR": "errored",
            "SKIPPED": "skipped", "XFAIL": "xfailed", "XPASS": "xpassed",
        }
        key = key_map.get(status)
        if key:
            self._counts[key] = self._counts.get(key, 0) + 1

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        duration = time.monotonic() - self._start
        total = sum(self._counts.values())

        # Write gzipped log
        log_path: str | None = None
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            log_file = self._log_dir / f"run_{self._run_id:05d}.log.gz"
            payload = self._log_buf.getvalue().encode("utf-8")
            with gzip.open(log_file, "wb") as fh:
                fh.write(payload)
            log_path = str(log_file)
        except Exception:
            pass

        self._con.execute(
            """
            UPDATE runs SET
                total=?, passed=?, failed=?, errored=?,
                skipped=?, xfailed=?, xpassed=?, duration_s=?, log_path=?
            WHERE run_id=?
            """,
            (
                total,
                self._counts["passed"],
                self._counts["failed"],
                self._counts["errored"],
                self._counts["skipped"],
                self._counts["xfailed"],
                self._counts["xpassed"],
                round(duration, 2),
                log_path,
                self._run_id,
            ),
        )
        self._con.commit()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    context_settings={"max_content_width": 120},
)

STATUS_ICON = {
    "PASSED": "✅", "FAILED": "❌", "ERROR": "💥",
    "SKIPPED": "⏭", "XFAIL": "🔁", "XPASS": "🎉",
}


@app.command()
def record(
    db:      Path      = typer.Option(DEFAULT_DB,   help="Path to the SQLite database"),
    log_dir: Path      = typer.Option(DEFAULT_LOGS, help="Directory for gzipped run logs"),
    ctx:     typer.Context = typer.Option(None, hidden=True),
    args:    list[str] = typer.Argument(default=None, help="Extra pytest args (after --)"),
) -> None:
    """Run ALL tests and record every result to the database."""
    extra: list[str] = list(args or [])

    typer.echo(f"📁  DB : {db}")
    git = _git_info()
    typer.echo(f"🔖  Git: {git['commit_short']} ({git['branch']}) — {git['commit_message'][:70]}")
    db_ver_int, db_ver_label = _detect_db_version()
    typer.echo(f"🗄️   DB : {db_ver_label}")

    con = _open_db(db)
    cur = con.execute(
        """
        INSERT INTO runs (
            recorded_at, commit_hash, commit_short, commit_message, branch,
            db_source_ver, db_internal_ver, pytest_args
        ) VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            git["commit_hash"],
            git["commit_short"],
            git["commit_message"],
            git["branch"],
            db_ver_label,
            db_ver_int,
            json.dumps(extra),
        ),
    )
    run_id = cur.lastrowid
    con.commit()

    typer.echo(f"\n🧪  Starting run #{run_id}  (Ctrl-C safe — partial results are stored)\n")

    plugin = _TestDBPlugin(con, run_id, log_dir)
    exit_code = pytest.main(
        ["--tb=short", "-v", *extra],
        plugins=[plugin],
    )

    counts   = plugin._counts
    total    = sum(counts.values())
    duration = time.monotonic() - plugin._start

    # Fetch the log_path that was written by the plugin's sessionfinish hook
    row = con.execute("SELECT log_path FROM runs WHERE run_id=?", (run_id,)).fetchone()
    stored_log = row["log_path"] if row else None

    typer.echo(
        f"\n{'─'*70}\n"
        f"Run #{run_id} complete in {duration:.1f}s\n"
        f"  ✅ {counts['passed']:>4}  passed\n"
        f"  ❌ {counts['failed']:>4}  failed\n"
        f"  💥 {counts['errored']:>4}  error\n"
        f"  ⏭  {counts['skipped']:>4}  skipped\n"
        f"  🔁 {counts['xfailed']:>4}  xfail\n"
        f"  🎉 {counts['xpassed']:>4}  xpass\n"
        f"  ── {total:>4}  total\n"
        f"\n📄 Log : {stored_log or '(not saved)'}\n"
        f"     zcat {stored_log} | less   # read log\n"
        f"\nQuery: python -m tools.test_db summary --run-id {run_id}\n"
        f"Fails: python -m tools.test_db query --status FAILED --run-id {run_id}"
    )
    con.close()
    raise typer.Exit(int(exit_code))


@app.command()
def query(
    db:          Path = typer.Option(DEFAULT_DB, help="Path to SQLite database"),
    status:      str  = typer.Option(None,  help="FAILED|PASSED|SKIPPED|ERROR|XFAIL|XPASS"),
    commit:      str  = typer.Option(None,  help="Commit hash prefix"),
    test_id:     str  = typer.Option(None,  help="LIKE pattern for test_id"),
    run_id:      int  = typer.Option(None,  help="Restrict to a specific run ID"),
    module:      str  = typer.Option(None,  help="LIKE pattern for test_module"),
    limit:       int  = typer.Option(100,   help="Max rows"),
    show_detail: bool = typer.Option(False, "--detail/--no-detail", help="Print full failure text"),
) -> None:
    """Query individual test results."""
    con = _open_db(db)
    clauses: list[str] = []
    params:  list[Any] = []

    if status:
        clauses.append("tr.status = ?")
        params.append(status.upper())
    if commit:
        clauses.append("r.commit_hash LIKE ?")
        params.append(f"{commit}%")
    if test_id:
        clauses.append("tr.test_id LIKE ?")
        params.append(f"%{test_id}%")
    if module:
        clauses.append("tr.test_module LIKE ?")
        params.append(f"%{module}%")
    if run_id is not None:
        clauses.append("tr.run_id = ?")
        params.append(run_id)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = con.execute(
        f"""
        SELECT tr.result_id, r.run_id, r.recorded_at, r.commit_short,
               r.db_source_ver, tr.test_id, tr.status, tr.duration_s,
               tr.failure_reason, tr.rerun_cmd
        FROM   test_results tr
        JOIN   runs r ON r.run_id = tr.run_id
        {where}
        ORDER  BY r.run_id DESC, tr.test_id
        LIMIT  ?
        """,
        [*params, limit],
    ).fetchall()
    con.close()

    if not rows:
        typer.echo("No results found.")
        return

    typer.echo(
        f"{'#':<7} {'Run':<5} {'At':<20} {'Cmt':<9} {'DB':<28} {'St':<6} Test"
    )
    typer.echo("─" * 130)
    for row in rows:
        icon = STATUS_ICON.get(row["status"], " ?")
        at   = row["recorded_at"][:19].replace("T", " ")
        typer.echo(
            f"{row['result_id']:<7} {row['run_id']:<5} {at:<20} {row['commit_short']:<9} "
            f"{str(row['db_source_ver'])[:27]:<28} {icon:<6} {row['test_id']}"
        )
        if row["failure_reason"]:
            typer.echo(f"         └─ {row['failure_reason'][:110]}")
        if show_detail:
            typer.echo(f"         ↩  {row['rerun_cmd']}")

    typer.echo(f"\n{len(rows)} row(s) (limit={limit})")


@app.command()
def summary(
    db:       Path = typer.Option(DEFAULT_DB, help="Path to SQLite database"),
    run_id:   int  = typer.Option(None, help="Specific run ID (omit for last 20)"),
    failures: bool = typer.Option(False, "--failures/--all", help="Show only FAILED/ERROR"),
) -> None:
    """Print a human-readable summary of one or more runs."""
    con = _open_db(db)
    runs = (
        con.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchall()
        if run_id is not None
        else con.execute("SELECT * FROM runs ORDER BY run_id DESC LIMIT 20").fetchall()
    )
    if not runs:
        typer.echo("No runs found.")
        return

    for run in runs:
        at = run["recorded_at"][:19].replace("T", " ")
        log_line = f"  Log     : {run['log_path']}" if run["log_path"] else ""
        typer.echo(
            f"\n{'═'*80}\n"
            f"Run #{run['run_id']}   {at} UTC\n"
            f"  Commit  : {run['commit_hash'][:40]}  ({run['branch']})\n"
            f"  Message : {run['commit_message'][:72]}\n"
            f"  DB      : {run['db_source_ver']}\n"
            f"  Args    : {run['pytest_args']}\n"
            + (f"{log_line}\n" if log_line else "")
            + f"  Results : "
            f"✅{run['passed']} ❌{run['failed']} 💥{run['errored']} "
            f"⏭{run['skipped']} 🔁{run['xfailed']} 🎉{run['xpassed']} "
            f"  ({run['total']} total, {run['duration_s']:.1f}s)"
        )

        if run_id is not None or failures:
            sf = "AND tr.status IN ('FAILED','ERROR')" if failures else ""
            tests = con.execute(
                f"SELECT * FROM test_results WHERE run_id=? {sf} ORDER BY status, test_id",
                (run["run_id"],),
            ).fetchall()
            prev_st = None
            for t in tests:
                if t["status"] != prev_st:
                    typer.echo(f"\n  ── {t['status']} ──")
                    prev_st = t["status"]
                icon = STATUS_ICON.get(t["status"], "?")
                typer.echo(f"  {icon} {t['test_id']}")
                if t["failure_reason"]:
                    typer.echo(f"       └─ {t['failure_reason'][:110]}")
                    typer.echo(f"       ↩  {t['rerun_cmd']}")
    con.close()


@app.command()
def compare(
    run_a: int  = typer.Argument(..., help="Baseline run ID"),
    run_b: int  = typer.Argument(..., help="Comparison run ID"),
    db:    Path = typer.Option(DEFAULT_DB, help="Path to SQLite database"),
) -> None:
    """Show regressions and fixes between two runs."""
    con = _open_db(db)

    def _fetch(rid: int) -> dict[str, str]:
        return {
            r["test_id"]: r["status"]
            for r in con.execute("SELECT test_id, status FROM test_results WHERE run_id=?", (rid,)).fetchall()
        }

    a, b = _fetch(run_a), _fetch(run_b)
    con.close()

    regressions = [(k, a[k], b[k]) for k in a if k in b and a[k] == "PASSED" and b[k] in ("FAILED", "ERROR")]
    fixes       = [(k, a[k], b[k]) for k in a if k in b and a[k] in ("FAILED", "ERROR") and b[k] == "PASSED"]
    new_tests   = [k for k in b if k not in a]
    removed     = [k for k in a if k not in b]

    typer.echo(f"\nRun #{run_a} ──▶ Run #{run_b}")
    typer.echo(f"  🔴 Regressions (PASSED → FAILED/ERROR): {len(regressions)}")
    for tid, sa, sb in sorted(regressions):
        typer.echo(f"     [{sa}→{sb}] {tid}")
    typer.echo(f"  🟢 Fixes (FAILED/ERROR → PASSED): {len(fixes)}")
    for tid, sa, sb in sorted(fixes):
        typer.echo(f"     [{sa}→{sb}] {tid}")
    typer.echo(f"  🆕 New tests in run #{run_b}    : {len(new_tests)}")
    typer.echo(f"  🗑  Removed from run #{run_b}   : {len(removed)}")


@app.command()
def rerun(
    test_id: str  = typer.Argument(..., help="Test node ID (substring match OK)"),
    db:      Path = typer.Option(DEFAULT_DB, help="Path to SQLite database"),
    run_id:  int  = typer.Option(None, help="Restrict to a specific run"),
    dry_run: bool = typer.Option(False, "--dry-run/--exec", help="Print without running"),
) -> None:
    """Print or execute the rerun command for a stored test."""
    con = _open_db(db)
    where = "AND run_id=?" if run_id else ""
    params: list[Any] = [f"%{test_id}%"]
    if run_id:
        params.append(run_id)
    rows = con.execute(
        f"SELECT DISTINCT test_id, rerun_cmd FROM test_results WHERE test_id LIKE ? {where} LIMIT 10",
        params,
    ).fetchall()
    con.close()

    if not rows:
        typer.echo(f"No test matching '{test_id}' found.")
        return
    for row in rows:
        typer.echo(f"  {row['test_id']}")
        typer.echo(f"  {row['rerun_cmd']}\n")
        if not dry_run:
            os.execvp(sys.executable, [sys.executable, "-m", "pytest",
                                       row["test_id"], "-v", "--tb=short"])


@app.command()
def sql(
    query_str: str = typer.Argument(..., help="SQL SELECT query"),
    db:        Path = typer.Option(DEFAULT_DB, help="Path to SQLite database"),
    limit:     int  = typer.Option(200, help="Row limit appended automatically"),
) -> None:
    """Execute a raw SQL query and print the results as a table."""
    con = _open_db(db)
    try:
        stripped = query_str.rstrip().rstrip(";")
        rows = con.execute(f"{stripped} LIMIT {limit}").fetchall()
        if not rows:
            typer.echo("(no rows)")
            return
        headers = list(rows[0].keys())
        widths  = {h: max(len(h), max(len(str(r[h] or "")) for r in rows)) for h in headers}
        hline   = " │ ".join(h.ljust(widths[h]) for h in headers)
        typer.echo(hline)
        typer.echo("─" * len(hline))
        for row in rows:
            typer.echo(" │ ".join(str(row[h] or "").ljust(widths[h]) for h in headers))
        typer.echo(f"\n{len(rows)} row(s)")
    except Exception as e:
        typer.echo(f"SQL error: {e}", err=True)
        raise typer.Exit(1)
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Example queries printed for new users
# ---------------------------------------------------------------------------

@app.command()
def log(
    run_id:  int  = typer.Argument(..., help="Run ID whose log to read"),
    db:      Path = typer.Option(DEFAULT_DB, help="Path to SQLite database"),
    grep:    str  = typer.Option(None, "--grep", "-g", help="Filter lines containing this string"),
    failures_only: bool = typer.Option(False, "--failures/--all", help="Show only FAILED/ERROR lines"),
) -> None:
    """Read (decompress) the gzipped log for a run and print it to stdout."""
    con = _open_db(db)
    row = con.execute("SELECT log_path FROM runs WHERE run_id=?", (run_id,)).fetchone()
    con.close()

    if not row or not row["log_path"]:
        typer.echo(f"No log recorded for run #{run_id}.", err=True)
        raise typer.Exit(1)

    log_file = Path(row["log_path"])
    if not log_file.exists():
        typer.echo(f"Log file not found: {log_file}", err=True)
        raise typer.Exit(1)

    with gzip.open(log_file, "rt", encoding="utf-8") as fh:
        for line in fh:
            if failures_only and not any(s in line for s in ("FAILED  ", "ERROR   ")):
                continue
            if grep and grep not in line:
                continue
            typer.echo(line, nl=False)


@app.command()
def examples(
    db: Path = typer.Option(DEFAULT_DB, help="Path to SQLite database"),
) -> None:
    """Show useful SQL examples for querying the test database."""
    typer.echo(f"""
Useful queries against: {db}

  # All failed tests in the latest run
  python -m tools.test_db query --status FAILED

  # All failures across every run for a specific module
  python -m tools.test_db query --status FAILED --module test_tabletype_coverage

  # Raw SQL: failure trend by commit
  python -m tools.test_db sql \\
    "SELECT r.commit_short, r.recorded_at, r.failed, r.passed, r.total
     FROM runs r ORDER BY r.run_id DESC"

  # Tests that fail most often
  python -m tools.test_db sql \\
    "SELECT test_id, COUNT(*) AS fail_count
     FROM test_results WHERE status IN ('FAILED','ERROR')
     GROUP BY test_id ORDER BY fail_count DESC"

  # Tests that were fixed (FAILED in run 1, PASSED in run 2)
  python -m tools.test_db compare 1 2

  # Rerun a failing test interactively
  python -m tools.test_db rerun "test_full[column_varbinary_max]"

  # All tests slower than 5 s in the most recent run
  python -m tools.test_db sql \\
    "SELECT test_id, duration_s FROM test_results
     WHERE run_id=(SELECT MAX(run_id) FROM runs) AND duration_s > 5
     ORDER BY duration_s DESC"
""")


if __name__ == "__main__":
    app()
