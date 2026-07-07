#!/usr/bin/env python3
"""Reusable ``sys.fn_dump_dblog`` wrapper — read a ``.bak``'s transaction log directly.

This consolidates the ``fn_dump_dblog`` primitive that was hand-rolled across many
``tools/diag/_diag_*.py`` / ``diag_*.py`` scripts (and rewritten repeatedly during
fuzzy-backup debugging).  ``fn_dump_dblog`` reads the log records embedded in a
backup file without restoring it, so it is the ground-truth "verifier" for
log-tail work: committed/uncommitted INSERT/UPDATE/DELETE records, their LSNs,
and (with ``images=True``) the before/after row images that mssqlbak must
reconstruct.

Used by the ``diag dblog`` CLI subcommand and by dirty-backup investigations::

    from tools.diag._dblog import dump_dblog, inventory
    recs = dump_dblog("tests/fixtures_2022/dirtycoverage_rich_update.bak", "2022",
                      op="LOP_MODIFY_ROW", page="0001:00000158", images=True)
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Ensure the repo root is importable when run as a plain script.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_N_DEFAULTS = 63  # fn_dump_dblog: 5 explicit args + 63 DEFAULT backup-file slots


@dataclass(slots=True)
class LogRec:
    """One transaction-log record as reported by ``fn_dump_dblog``."""

    lsn: str
    op: str            # Operation, e.g. LOP_INSERT_ROWS / LOP_MODIFY_ROW / LOP_DELETE_ROWS
    ctx: str           # Context, e.g. LCX_HEAP / LCX_CLUSTERED / LCX_MARK_AS_GHOST
    xact: str          # Transaction ID
    length: int        # Log Record Length
    page: str          # Page ID (file:page, hex)
    slot: int | None   # Slot ID
    record: bytes | None = None   # full [Log Record] bytes (record=True)
    before: bytes | None = None   # [RowLog Contents 0] before-image (images=True)
    after: bytes | None = None    # [RowLog Contents 1] after-image  (images=True)


def _fn(container_bak: str) -> str:
    defaults = ", ".join(["DEFAULT"] * _N_DEFAULTS)
    return f"sys.fn_dump_dblog(NULL, NULL, N'DISK', 1, N'{container_bak}', {defaults})"


def _bootstrap(version: str) -> tuple[str, str]:
    """Resolve the version-matched container + DBA password for *version*."""
    from tools.fixture_run import bootstrap_fixture_env

    # Force re-resolution so a single process can target multiple versions.
    for k in ("FIXTURE_CONTAINER", "FIXTURE_DBA_PASSWORD", "FIXTURE_SERVER_NAME"):
        os.environ.pop(k, None)
    os.environ["FIXTURE_DIR"] = f"tests/fixtures_{version}"
    _server, container = bootstrap_fixture_env()
    return container, os.environ["FIXTURE_DBA_PASSWORD"]


def _hexs(field: str) -> bytes | None:
    s = field.strip()
    if not s or s.upper() == "NULL":
        return None
    try:
        return bytes.fromhex(s)
    except ValueError:
        return None


def _query(container: str, password: str, sql: str) -> str:
    from tools.register_bak import _run_sql_query

    return _run_sql_query(container, password, sql, sep="|").rstrip("\n")


def _with_bak(bak: Path, version: str, build_sql, parse):
    """Copy *bak* into the version container, run ``build_sql``, parse the output."""
    from tools.register_bak import _copy_bak, _run

    container, password = _bootstrap(version)
    container_bak = _copy_bak(container, bak)
    try:
        out = _query(container, password, build_sql(container_bak))
    finally:
        _run(["podman", "exec", container, "rm", "-f", container_bak])
    return parse(out)


def dump_dblog(
    bak: Path | str,
    version: str,
    *,
    op: str | None = None,
    page: str | None = None,
    slot: int | None = None,
    images: bool = False,
    record: bool = False,
    limit: int | None = None,
) -> list[LogRec]:
    """Return log records from *bak*'s log tail, optionally filtered.

    *op* / *page* / *slot* add ``WHERE`` filters; *images* includes the
    before/after row images; *record* includes the full ``[Log Record]`` bytes;
    *limit* applies ``TOP``.  Records are ordered by ``[Current LSN]``.
    """
    bak = Path(bak)
    sel = [
        "[Current LSN]", "Operation", "Context", "[Transaction ID]",
        "[Log Record Length]", "[Page ID]", "[Slot ID]",
    ]
    if record:
        sel.append("CONVERT(VARCHAR(MAX),[Log Record],2)")
    if images:
        sel.append("CONVERT(VARCHAR(MAX),[RowLog Contents 0],2)")
        sel.append("CONVERT(VARCHAR(MAX),[RowLog Contents 1],2)")
    where = []
    if op:
        where.append(f"Operation = '{op}'")
    if page:
        where.append(f"[Page ID] = '{page}'")
    if slot is not None:
        where.append(f"[Slot ID] = {slot}")

    def build(cb: str) -> str:
        top = f"TOP {int(limit)} " if limit else ""
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        return (
            "SET NOCOUNT ON; SELECT " + top + ", ".join(sel)
            + f" FROM {_fn(cb)}" + clause + " ORDER BY [Current LSN];"
        )

    def parse(out: str) -> list[LogRec]:
        recs: list[LogRec] = []
        for line in out.splitlines():
            if not line.strip():
                continue
            f = line.split("|")
            if len(f) < 7:
                continue
            i = 7
            rec = _hexs(f[i]) if record else None
            if record:
                i += 1
            before = after = None
            if images and len(f) > i + 1:
                before, after = _hexs(f[i]), _hexs(f[i + 1])
            slot_s = f[6].strip()
            len_s = f[4].strip()
            recs.append(LogRec(
                lsn=f[0].strip(), op=f[1].strip(), ctx=f[2].strip(),
                xact=f[3].strip(),
                length=int(len_s) if len_s.lstrip("-").isdigit() else 0,
                page=f[5].strip(),
                slot=int(slot_s) if slot_s.lstrip("-").isdigit() else None,
                record=rec, before=before, after=after,
            ))
        return recs

    return _with_bak(bak, version, build, parse)


def inventory(bak: Path | str, version: str) -> list[tuple[str, str, int]]:
    """Return ``(Operation, Context, count)`` rows — the LOP census, busiest first."""
    bak = Path(bak)

    def build(cb: str) -> str:
        return (
            "SET NOCOUNT ON; SELECT Operation, Context, COUNT(*) "
            f"FROM {_fn(cb)} GROUP BY Operation, Context ORDER BY COUNT(*) DESC;"
        )

    def parse(out: str) -> list[tuple[str, str, int]]:
        rows: list[tuple[str, str, int]] = []
        for line in out.splitlines():
            if not line.strip():
                continue
            f = line.split("|")
            if len(f) < 3:
                continue
            n = f[2].strip()
            rows.append((f[0].strip(), f[1].strip(), int(n) if n.isdigit() else 0))
        return rows

    return _with_bak(bak, version, build, parse)
