#!/usr/bin/env python3
"""V13 is_hidden probe — identify the ``syscolpars.status`` bit for is_hidden.

Background
----------
The V13 probe (``make_v13_probe.py``) confirmed that ``syscolpars.status``
bits 28–29 (``0x10000000`` / ``0x20000000``) encode ``generated_always_type``
(AS_ROW_START / AS_ROW_END) on the current temporal table.  The ``is_hidden``
bit position was left unconfirmed because the existing fixtures did not contain
period columns declared with the ``HIDDEN`` keyword.

This probe closes that gap by restoring ``temporal_hidden_full.bak``, which
contains two structurally identical temporal tables:

* ``dbo.temporal_hidden``  — period columns with ``HIDDEN``;
  ``sys.columns.is_hidden = 1``
* ``dbo.temporal_visible`` — period columns without ``HIDDEN``;
  ``sys.columns.is_hidden = 0``

Two-phase approach (required because ``sys.syscolpars`` is never accessible
via T-SQL, even on native SS2022 databases):

Phase A — T-SQL (live SQL Server):
  Confirms ``sys.columns.is_hidden`` and ``generated_always_type`` values for
  both tables via the view-level API.  Also confirms ``sys.periods`` period
  column IDs.

Phase B — Python / PageStore (offline, reads the .bak directly):
  Uses ``mssqlbak``'s ``PageStore`` + ``_decode_table`` to iterate the raw
  ``syscolpars`` rows inside the backup file.  Extracts the 4-byte ``status``
  integer for every column in both tables, then XOR-s the matching period
  column statuses (hidden vs visible) to isolate the ``is_hidden`` bit mask.

Results are written to ``<fixture-dir>/V13_hidden_probe_results.txt``.

Run via::

    FIXTURE_DIR=tests/fixtures_2022 python -m tools.fixture_run v13-hidden-probe

Or with force-overwrite::

    FIXTURE_DIR=tests/fixtures_2022 python -m tools.fixture_run v13-hidden-probe --force
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import (  # noqa: E402
    fixture_credentials,
    sqlcmd_base,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Phase A — T-SQL: confirm sys.columns metadata via the live SQL Server.
# sys.syscolpars is intentionally NOT queried here — it is inaccessible via
# T-SQL even on native SS2022 databases (Msg 208 "Invalid object name").
# Raw status bits are read offline in Phase B using PageStore.
# ---------------------------------------------------------------------------

_SQL_PHASE_A = r"""
SET NOCOUNT ON;
GO

IF DB_ID(N'V13HiddenProbe') IS NOT NULL BEGIN
    ALTER DATABASE [V13HiddenProbe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V13HiddenProbe];
END;
GO

RESTORE DATABASE [V13HiddenProbe]
    FROM DISK = N'/tmp/temporal_hidden_full.bak'
    WITH MOVE N'TemporalHidden'     TO N'/tmp/V13HiddenProbe.mdf',
         MOVE N'TemporalHidden_log' TO N'/tmp/V13HiddenProbe.ldf',
         REPLACE, RECOVERY;
GO

USE [V13HiddenProbe];
GO

-- ----------------------------------------------------------------
-- A.1  sys.columns — confirm is_hidden=1 for hidden period cols.
-- ----------------------------------------------------------------
PRINT '=== PHASE A: sys.columns for dbo.temporal_hidden ===';
SELECT
    c.column_id,
    c.name,
    c.system_type_id,
    c.is_hidden,
    c.generated_always_type,
    c.generated_always_type_desc,
    c.is_nullable
FROM sys.columns c
WHERE c.object_id = OBJECT_ID(N'dbo.temporal_hidden')
ORDER BY c.column_id;
GO

-- ----------------------------------------------------------------
-- A.2  sys.columns — confirm is_hidden=0 for visible period cols.
-- ----------------------------------------------------------------
PRINT '=== PHASE A: sys.columns for dbo.temporal_visible ===';
SELECT
    c.column_id,
    c.name,
    c.system_type_id,
    c.is_hidden,
    c.generated_always_type,
    c.generated_always_type_desc,
    c.is_nullable
FROM sys.columns c
WHERE c.object_id = OBJECT_ID(N'dbo.temporal_visible')
ORDER BY c.column_id;
GO

-- ----------------------------------------------------------------
-- A.3  sys.periods — confirm period column IDs for both tables.
-- ----------------------------------------------------------------
PRINT '=== PHASE A: sys.periods for dbo.temporal_hidden ===';
SELECT
    p.name,
    p.period_type_desc,
    p.start_column_id,
    p.end_column_id
FROM sys.periods p
WHERE p.object_id = OBJECT_ID(N'dbo.temporal_hidden');
GO

PRINT '=== PHASE A: sys.periods for dbo.temporal_visible ===';
SELECT
    p.name,
    p.period_type_desc,
    p.start_column_id,
    p.end_column_id
FROM sys.periods p
WHERE p.object_id = OBJECT_ID(N'dbo.temporal_visible');
GO

USE [master];
GO
IF DB_ID(N'V13HiddenProbe') IS NOT NULL BEGIN
    ALTER DATABASE [V13HiddenProbe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V13HiddenProbe];
END;
GO
"""


# ---------------------------------------------------------------------------
# Phase B — Python / PageStore: read raw syscolpars.status from the .bak.
# sys.syscolpars is not accessible via T-SQL; mssqlbak reads it directly from
# the backup file using the same bootstrap + decode path used in recover_schema.
# ---------------------------------------------------------------------------

def _phase_b_pagstore(bak_path: Path) -> str:
    """Return a formatted report of raw syscolpars.status for both tables."""
    from mssqlbak.catalog import (
        _OBJID_SYSCOLPARS,
        _OBJID_SYSSCHOBJS,
        _SYSCOLPARS_COLS,
        _SYSSCHOBJS_COLS,
        _bootstrap,
        _decode_table,
        _u,
    )
    from mssqlbak.pages import PageStore

    lines: list[str] = []
    lines.append("=== PHASE B: raw syscolpars.status (PageStore, offline) ===")
    lines.append(f"bak: {bak_path}")
    lines.append("")

    store = PageStore.from_bak(str(bak_path))
    boot  = _bootstrap(store)

    # Resolve user table names → object IDs via sysschobjs.
    sysschobjs_pg = boot.object_table_first_page(_OBJID_SYSSCHOBJS)
    name_to_oid: dict[str, int] = {}
    for r in _decode_table(store, sysschobjs_pg, _SYSSCHOBJS_COLS):
        name_b = r.get("name")
        type_b = r.get("type")
        if name_b is None or type_b is None:
            continue
        if type_b.decode("latin1").strip() != "U":
            continue
        name_to_oid[name_b.decode("utf-16-le")] = _u(r["id"])

    hidden_oid  = name_to_oid.get("temporal_hidden")
    visible_oid = name_to_oid.get("temporal_visible")

    if hidden_oid is None or visible_oid is None:
        lines.append(
            f"ERROR: could not find both tables in sysschobjs "
            f"(found: {list(name_to_oid.keys())})"
        )
        return "\n".join(lines)

    lines.append(f"temporal_hidden  object_id = {hidden_oid}")
    lines.append(f"temporal_visible object_id = {visible_oid}")
    lines.append("")

    # Collect syscolpars rows for both tables.
    syscolpars_pg = boot.object_table_first_page(_OBJID_SYSCOLPARS)
    rows_by_oid: dict[int, list[dict]] = {hidden_oid: [], visible_oid: []}
    for r in _decode_table(store, syscolpars_pg, _SYSCOLPARS_COLS):
        if _u(r.get("number", b"\x00\x00")) != 0:
            continue
        oid = _u(r["id"])
        if oid in rows_by_oid:
            rows_by_oid[oid].append(r)

    for tbl_name, oid in [("temporal_hidden", hidden_oid), ("temporal_visible", visible_oid)]:
        lines.append(f"--- syscolpars rows for dbo.{tbl_name} (oid={oid}) ---")
        lines.append(f"{'colid':>6}  {'name':<20}  {'status_hex':>12}  {'status_dec':>12}")
        col_rows = sorted(rows_by_oid[oid], key=lambda r: _u(r["colid"]))
        for r in col_rows:
            colid  = _u(r["colid"])
            name   = r["name"].decode("utf-16-le") if r.get("name") else "?"
            status = _u(r["status"]) if r.get("status") else 0
            lines.append(f"{colid:>6}  {name:<20}  0x{status:08X}  {status:>12}")
        lines.append("")

    # XOR analysis: hidden vs visible for each matching period column name.
    lines.append("--- XOR analysis: hidden_status XOR visible_status ---")

    def col_status(oid: int, col_name: str) -> int | None:
        for r in rows_by_oid[oid]:
            if r.get("name") and r["name"].decode("utf-16-le") == col_name:
                return _u(r["status"]) if r.get("status") else 0
        return None

    for col_name in ("valid_from", "valid_to"):
        h = col_status(hidden_oid,  col_name)
        v = col_status(visible_oid, col_name)
        if h is None or v is None:
            lines.append(f"  {col_name}: NOT FOUND in one or both tables")
            continue
        xor = h ^ v
        lines.append(f"  {col_name}:")
        lines.append(f"    temporal_hidden  status = 0x{h:08X}  ({h})")
        lines.append(f"    temporal_visible status = 0x{v:08X}  ({v})")
        lines.append(f"    XOR              result = 0x{xor:08X}  ({xor})")
        if xor:
            bits = [i for i in range(32) if xor & (1 << i)]
            lines.append(f"    differing bits: {bits}  (0-indexed from LSB)")
        else:
            lines.append("    XOR = 0 — no difference found!")
        lines.append("")

    return "\n".join(lines)


def _run_phase_a(container: str, sqlcmd: list[str], bak: Path) -> str:
    """Run Phase A T-SQL; tolerate non-zero exit so Phase B always runs."""
    import subprocess as sp
    local = "/tmp/_v13_hidden_probe_a.sql"
    Path(local).write_text(_SQL_PHASE_A, encoding="utf-8")
    sp.run(["podman", "cp", local, f"{container}:/tmp/_v13_hidden_probe_a.sql"], check=True)
    result = sp.run(
        ["podman", "exec", container, *sqlcmd, "-i", "/tmp/_v13_hidden_probe_a.sql"],
        text=True, capture_output=True,
    )
    return result.stdout + result.stderr


def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing results")
    args = p.parse_args()

    _raw_fdir = os.environ.get("FIXTURE_DIR", "")
    if _raw_fdir:
        _fd = Path(_raw_fdir)
        fixture_dir = _fd if _fd.is_absolute() else (REPO_ROOT / _fd).resolve()
    else:
        fixture_dir = REPO_ROOT / "tests" / "fixtures_2022"
    out = fixture_dir / "V13_hidden_probe_results.txt"

    if out.exists() and not args.force:
        print(f"skipping (already exists): {out}", file=sys.stderr)
        return 0

    bak = fixture_dir / "temporal_hidden_full.bak"
    if not bak.exists():
        print(
            f"ERROR: {bak} not found — run 'fixture_run temporal-hidden' first",
            file=sys.stderr,
        )
        return 1

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    sqlcmd = sqlcmd_base(user, password, container)

    # Phase A — T-SQL via live SQL Server (sys.columns metadata).
    print("Phase A: copying temporal_hidden_full.bak and running T-SQL …", file=sys.stderr)
    cp = subprocess.run(
        ["podman", "cp", str(bak), f"{container}:/tmp/temporal_hidden_full.bak"],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        print(f"podman cp failed: {cp.stderr}", file=sys.stderr)
        return 1

    phase_a_out = _run_phase_a(container, sqlcmd, bak)

    # Phase B — Python PageStore (raw syscolpars.status from .bak offline).
    print("Phase B: reading raw syscolpars.status via PageStore …", file=sys.stderr)
    try:
        phase_b_out = _phase_b_pagstore(bak)
    except Exception as exc:
        phase_b_out = f"Phase B ERROR: {exc}"

    output = phase_a_out + "\n\n" + phase_b_out + "\n"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(output, encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
