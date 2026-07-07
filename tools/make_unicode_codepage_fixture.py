#!/usr/bin/env python3
"""Build ``unicode_codepage_coverage.bak`` — the G55 collation-id probe fixture.

Creates a ``UniCodePageCoverage`` database with one table per code page.  Each
table has:

* ``label``       VARCHAR(60)    — script name in the database default collation
* ``varchar_col`` VARCHAR(1000)  — text in the code-page-specific COLLATE
* ``nvarchar_col`` NVARCHAR(1000) — same text as UTF-16LE (comparison baseline)

Sample text is drawn from the Unicode 2.0 and 3.2 test pages:
    https://www.cogsci.ed.ac.uk/~richard/unicode-sample.html
    https://www.cogsci.ed.ac.uk/~richard/unicode-sample-3-2.html

After the BAK is written, the tool immediately probes the BAK's ``syscolpars``
records to emit the discovered ``collation_id`` for every ``varchar_col`` column.
These values are the empirical data needed to close G55 (the LCID bit layout in
``syscolpars.collationid`` for non-UTF-8, non-cp1252 collations).

Run via fixture_run::

    python -m tools.fixture_run unicode-codepage

Or directly (requires FIXTURE_DBA_PASSWORD and, optionally, FIXTURE_CONTAINER)::

    python -m tools.make_unicode_codepage_fixture
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_fixture import (
    _copy_out,
    _load_and_backup,
    backup_statement,
    discover_container,
    sqlcmd_base,
)
from tools.unicode_codepage_matrix import CODEPAGE_ENTRIES, CodepageEntry

DB_NAME = "UniCodePageCoverage"
REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures"))) / "unicode_codepage_coverage.bak"

# ── SQL helpers ────────────────────────────────────────────────────────────────

def _sql_nstr(text: str) -> str:
    """Return ``text`` as a T-SQL N'' literal with single-quotes doubled."""
    return "N'" + text.replace("'", "''") + "'"


def _table_name(entry: CodepageEntry) -> str:
    """Derive a deterministic SQL identifier from the codec name."""
    return f"cp_{entry.python_codec}"


def _create_table_sql(entry: CodepageEntry) -> str:
    tbl = _table_name(entry)
    return (
        f"CREATE TABLE [{tbl}] (\n"
        f"    id          INT IDENTITY PRIMARY KEY,\n"
        f"    label       VARCHAR(60)   NOT NULL,\n"
        f"    varchar_col VARCHAR(1000) COLLATE {entry.sql_collation} NULL,\n"
        f"    nvarchar_col NVARCHAR(1000) NULL\n"
        f");"
    )


def _insert_row_sql(entry: CodepageEntry, label: str, text: str, ntext: str | None = None) -> str:
    tbl = _table_name(entry)
    label_lit = _sql_nstr(label)
    varchar_lit = _sql_nstr(text)
    nvarchar_lit = _sql_nstr(ntext if ntext is not None else text)
    return (
        f"INSERT INTO [{tbl}] (label, varchar_col, nvarchar_col)\n"
        f"VALUES ({label_lit}, {varchar_lit}, {nvarchar_lit});"
    )


# ── SQL script builder ─────────────────────────────────────────────────────────

def build_sql() -> str:
    """Assemble the CREATE DATABASE / CREATE TABLE / INSERT / BACKUP script.

    The script is idempotent: it drops a pre-existing ``UniCodePageCoverage``
    database before recreating it.  BACKUP DATABASE is appended by the caller
    via :func:`tools.make_fixture.backup_statement`.
    """
    parts: list[str] = [
        "USE [master];",
        "GO",
        # Drop-if-exists
        (
            f"IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN "
            f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
            f"DROP DATABASE [{DB_NAME}]; END;"
        ),
        "GO",
        # Create with a known neutral Latin-1 collation so the varchar_col
        # column-level COLLATE clauses are the only variable.
        f"CREATE DATABASE [{DB_NAME}] COLLATE Latin1_General_CI_AS;",
        "GO",
        f"USE [{DB_NAME}];",
        "GO",
    ]

    for entry in CODEPAGE_ENTRIES:
        parts.append(f"-- {entry.script_name}  ({entry.python_codec} / {entry.sql_collation})")
        parts.append(_create_table_sql(entry))

        # Row 1: primary sample text (all characters encodable in code page)
        parts.append(
            _insert_row_sql(entry, f"sample:{entry.python_codec}", entry.varchar_sample)
        )

        # Row 2: nvarchar_extra (characters outside the code page → stored as ?
        # in varchar_col, full Unicode in nvarchar_col)
        if entry.nvarchar_extra:
            parts.append(
                _insert_row_sql(
                    entry,
                    f"extra:{entry.python_codec}",
                    entry.nvarchar_extra,   # varchar_col: SQL Server converts, ? for unmappable
                    entry.nvarchar_extra,   # nvarchar_col: stored verbatim as UTF-16LE
                )
            )

        parts.append("GO")

    return "\n".join(parts) + "\n"


# ── Probe: read collation_id values from the BAK ────────────────────────────

def probe_collation_ids(bak_path: Path) -> None:
    """Read ``varchar_col`` collation_id from the BAK and print a summary.

    This resolves G55 by showing the actual ``syscolpars.collationid`` stored
    for each per-code-page varchar column.  Compare to the Latin1_General
    baseline (0x3400D008) to determine the LCID bit position.
    """
    try:
        from mssqlbak.catalog import recover_schema
        from mssqlbak.pages import PageStore
    except ImportError as exc:
        print(f"warning: mssqlbak not importable; skipping collation_id probe: {exc}", file=sys.stderr)
        return

    LATIN1_BASELINE = 0x3400D008

    print("\n==> Probing collation_id values in the BAK", file=sys.stderr)
    print("    (Latin1_General_CI_AS baseline = 0x3400D008)", file=sys.stderr)
    print(f"    {'Table':<20}  {'collation_name':<35}  {'collation_id (hex)':<20}  {'XOR baseline'}", file=sys.stderr)
    print(f"    {'-'*20}  {'-'*35}  {'-'*20}  {'-'*20}", file=sys.stderr)

    try:
        store = PageStore.from_bak(bak_path)
        schema = recover_schema(store)
    except Exception as exc:
        print(f"warning: cannot probe BAK: {exc}", file=sys.stderr)
        return

    # Build a lookup: table_name -> {col_name -> collation_id}
    table_col_ids: dict[str, dict[str, int]] = {
        t.name: {c.name: c.collation_id for c in t.columns}
        for t in schema.tables
    }

    for entry in CODEPAGE_ENTRIES:
        tbl = _table_name(entry)
        col_id = table_col_ids.get(tbl, {}).get("varchar_col")
        if col_id is None:
            print(f"    {tbl:<20}  {'<not found>':<35}  {'?':<20}  ?", file=sys.stderr)
        else:
            xor = col_id ^ LATIN1_BASELINE
            print(
                f"    {tbl:<20}  {entry.sql_collation:<35}  "
                f"0x{col_id:08X}  (XOR=0x{xor:08X})",
                file=sys.stderr,
            )


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> int:
    if OUT_PATH.exists():
        print(f"skip (already exists): {OUT_PATH.name}", file=sys.stderr)
        return 0
    user = os.environ.get("FIXTURE_DBA_USER", "sa")
    password = os.environ.get("FIXTURE_DBA_PASSWORD")
    if not password:
        print(
            "error: FIXTURE_DBA_PASSWORD not set; "
            "run via: python -m tools.fixture_run unicode-codepage",
            file=sys.stderr,
        )
        return 2

    container = discover_container()
    print(f"==> using container {container} as {user}", file=sys.stderr)

    sql = build_sql() + backup_statement(DB_NAME, f"/tmp/{DB_NAME}.bak")

    _load_and_backup(
        container,
        sqlcmd_base(user, password, container),
        sql,
        container_sql=f"/tmp/load_{DB_NAME}.sql",
    )

    size = _copy_out(container, f"/tmp/{DB_NAME}.bak", OUT_PATH)
    print(f"==> wrote {OUT_PATH} ({size:,} bytes)", file=sys.stderr)

    probe_collation_ids(OUT_PATH)

    return 0


if __name__ == "__main__":
    sys.exit(main())
