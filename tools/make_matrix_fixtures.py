#!/usr/bin/env python3
"""Generate columnstore matrix fixtures for empty MATRIX_CELLS.

This generator covers the 7 categories of targets the plan identifies as
"generators for empty matrix cells":

1. **enc=5 / XPRESS Format A** — var-length MAX types in a CCI where the
   engine picks XPRESS-compressed segments (format determined by the engine,
   `>32 767` rows forces the engine into a format that stores off-row LOB
   data via the encoding-5 path).
2. **ARCHIVE double-compressed CCI** — a CCI rebuilt with
   ``DATA_COMPRESSION = COLUMNSTORE_ARCHIVE`` at the partition level, which
   applies a second XPRESS pass over already-columnstore-compressed data.
3. **Ordered CCI (SS2022+)** — a CCI created with ``ORDER (col)``; the
   ascending distribution is important because it preserves the ordering.
4. **NCCI on heap** — nonclustered columnstore index on a heap table; read
   via the NCCI path (different code path from clustered CCI).
5. **Delta store** — a CCI with fewer than ``DELTA_THRESHOLD`` (~102 400)
   rows whose rowgroups have not yet been compressed (``state = OPEN``).
6. **Delete bitmap** — a CCI with rows deleted after compression, so the
   delete-bitmap allocation is non-empty and suppresses those rows.
7. **MAX bpv=0 in CCI** — a CCI with ``varchar(max)``/``nvarchar(max)``/
   ``varbinary(max)`` columns that end up in compressed rowgroups (off-row
   LOB) so ``bpv=0`` is recorded in ``sys.column_store_segments``.

Each generator function returns a list of SQL statements (no GO, no
semicolons — one statement per list element), a ``cs__`` filename token,
and the DB name.  A shared ``main()`` CLI accepts ``--suite`` to choose
which fixture(s) to build, and ``--dist``/``--null``/``--rows`` to
parameterize them.

Usage examples::

    # Build all suites (SS2022 container)
    python -m tools.make_matrix_fixtures --suite all

    # Only the NCCI-on-heap suite with cycling distribution
    python -m tools.make_matrix_fixtures --suite nccihp --dist cycle --rows 200000

    # Ordered CCI (requires SS2022+)
    python -m tools.make_matrix_fixtures --suite cciord --dist asc

    # Delete-bitmap suite
    python -m tools.make_matrix_fixtures --suite delbmp --dist runs

Fixtures are named using :func:`tools.fixture_name.fixture_name` and
written to ``FIXTURE_DIR`` (default: ``tests/fixtures_2022``).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_name import fixture_name  # noqa: E402
from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
)
from tools.seed_cast import cast_int_to, dist_expr  # noqa: E402

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_MULTI_TYPES: list[tuple[str, str]] = [
    # (column_name, sql_type)
    ("col_int",        "int"),
    ("col_bigint",     "bigint"),
    ("col_smallint",   "smallint"),
    ("col_tinyint",    "tinyint"),
    ("col_bit",        "bit"),
    ("col_real",       "real"),
    ("col_float",      "float"),
    ("col_dec",        "decimal(18,4)"),
    ("col_date",       "date"),
    ("col_dt2",        "datetime2(7)"),
    ("col_nvc50",      "nvarchar(50)"),
    ("col_char10",     "char(10)"),
    ("col_bin8",       "binary(8)"),
    ("col_uuid",       "uniqueidentifier"),
]

_MAX_TYPES: list[tuple[str, str]] = [
    ("col_vcmax",  "varchar(max)"),
    ("col_nvcmax", "nvarchar(max)"),
    ("col_vbmax",  "varbinary(max)"),
]


def _col_defs(col_types: list[tuple[str, str]], nullable: bool = True) -> str:
    """Return a comma-separated column-definition fragment."""
    null_kw = "NULL" if nullable else "NOT NULL"
    return ",\n    ".join(f"{name} {sql_type} {null_kw}" for name, sql_type in col_types)


def _col_insert(col_types: list[tuple[str, str]], dist: str, span: int = 1_000_000,
                k: int = 512, r: int = 32, null_mask: str | None = None) -> str:
    """Return a comma-separated SELECT column expression for seed-based INSERT."""
    parts = []
    idx = dist_expr(dist, span=span, k=k, r=r)
    for name, sql_type in col_types:
        val = cast_int_to(sql_type, idx)
        if null_mask:
            val = f"CASE WHEN ({null_mask}) THEN NULL ELSE {val} END"
        parts.append(f"{val} AS {name}")
    return ",\n    ".join(parts)


def _reorganize(table: str) -> list[str]:
    """Return SQL to force a delta store into compressed rowgroups."""
    return [
        f"ALTER INDEX ALL ON {table} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)"
    ]


# ---------------------------------------------------------------------------
# 1. enc=5 XPRESS Format A — MAX types in CCI
# ---------------------------------------------------------------------------

def build_enc5fa(
    dist: str = "rand",
    null: str | None = None,
    rows: int = 40_000,
) -> tuple[str, str, list[str]]:
    """CCI with MAX-type columns (varchar/nvarchar/varbinary MAX).

    SQL Server stores these as off-row LOB data with encoding_type=5 in the
    compressed rowgroup.  At >32 767 rows the engine uses XPRESS Format A.

    Returns (db_name, bak_name, sql_stmts).
    """
    db = "MatrixEnc5fa"
    bak = fixture_name("cci", "enc5fa", "multi", dist, null=null, rows=rows)
    table = "dbo.cs_enc5fa"
    col_types = _MAX_TYPES
    null_mask = "pk % 10 = 0" if null == "spnull" else ("pk / 100 % 2 = 0" if null == "nullrun" else None)
    stmts: list[str] = [f"CREATE DATABASE {db}"]
    stmts.append(f"USE {db}")
    stmts += seed_sql(rows)
    stmts.append(
        f"CREATE TABLE {table} (\n"
        f"    pk INT NOT NULL,\n"
        f"    {_col_defs(col_types)}\n"
        f") WITH (DATA_COMPRESSION = COLUMNSTORE)"
    )
    cols_select = _col_insert(col_types, dist, span=rows, k=min(512, rows), r=32, null_mask=null_mask)
    stmts.append(
        f"INSERT INTO {table} (pk, {', '.join(n for n, _ in col_types)})\n"
        f"SELECT pk, {cols_select} FROM fkr__seed WHERE pk < {rows}"
    )
    stmts += _reorganize(table)
    return db, bak, stmts


# ---------------------------------------------------------------------------
# 2. ARCHIVE double-compressed CCI
# ---------------------------------------------------------------------------

def build_arch2(
    dist: str = "rand",
    null: str | None = None,
    rows: int = 200_000,
) -> tuple[str, str, list[str]]:
    """CCI with ``DATA_COMPRESSION = COLUMNSTORE_ARCHIVE`` — double-compressed.

    The engine applies XPRESS over the already-columnstore-compressed data,
    producing the ARCHIVE enc-path (cmprlevel=4).  This exercises
    ``_unwrap_archive_blob`` and the enc=5 ARCHIVE inner-layout code paths.

    Returns (db_name, bak_name, sql_stmts).
    """
    db = "MatrixArch2"
    bak = fixture_name("cci", "arch2", "multi", dist, null=null, rows=rows)
    table = "dbo.cs_arch2"
    col_types = _MULTI_TYPES
    null_mask = "pk % 10 = 0" if null == "spnull" else None
    stmts: list[str] = [f"CREATE DATABASE {db}"]
    stmts.append(f"USE {db}")
    stmts += seed_sql(rows)
    stmts.append(
        f"CREATE TABLE {table} (\n"
        f"    pk INT NOT NULL,\n"
        f"    {_col_defs(col_types)}\n"
        f") WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)"
    )
    cols_select = _col_insert(col_types, dist, span=rows, k=min(512, rows), r=32, null_mask=null_mask)
    stmts.append(
        f"INSERT INTO {table} (pk, {', '.join(n for n, _ in col_types)})\n"
        f"SELECT pk, {cols_select} FROM fkr__seed WHERE pk < {rows}"
    )
    stmts += _reorganize(table)
    return db, bak, stmts


# ---------------------------------------------------------------------------
# 3. Ordered CCI (SS2022+)
# ---------------------------------------------------------------------------

def build_cciord(
    dist: str = "asc",
    null: str | None = None,
    rows: int = 200_000,
) -> tuple[str, str, list[str]]:
    """Ordered CCI — requires SS2022+.

    The ascending distribution exercises the ordered-CCI path where the
    engine can exploit physical ordering during rowgroup compression.

    Returns (db_name, bak_name, sql_stmts).
    """
    db = "MatrixCciOrd"
    bak = fixture_name("cciord", "enc1for", "bigint", dist, null=null, rows=rows)
    table = "dbo.cs_cciord"
    null_mask = "pk % 10 = 0" if null == "spnull" else None
    stmts: list[str] = [f"CREATE DATABASE {db}"]
    stmts.append(f"USE {db}")
    stmts += seed_sql(rows)
    stmts.append(
        f"CREATE TABLE {table} (\n"
        f"    pk BIGINT NOT NULL,\n"
        f"    val BIGINT NULL,\n"
        f"    INDEX ix_cs CLUSTERED COLUMNSTORE ORDER (pk)\n"
        f")"
    )
    idx = dist_expr(dist, span=rows)
    val_expr = cast_int_to("bigint", idx)
    if null_mask:
        val_expr = f"CASE WHEN ({null_mask}) THEN NULL ELSE {val_expr} END"
    stmts.append(
        f"INSERT INTO {table} (pk, val)\n"
        f"SELECT pk, {val_expr} FROM fkr__seed WHERE pk < {rows}"
    )
    stmts += _reorganize(table)
    return db, bak, stmts


# ---------------------------------------------------------------------------
# 4. NCCI on heap
# ---------------------------------------------------------------------------

def build_nccihp(
    dist: str = "asc",
    null: str | None = None,
    rows: int = 200_000,
) -> tuple[str, str, list[str]]:
    """Nonclustered columnstore index on a heap table.

    A heap underlies the rowstore; an NCCI scans it and stores compressed
    rowgroups.  This exercises the NCCI code path (seg_type / index_id
    differentiation in the page reader).

    Returns (db_name, bak_name, sql_stmts).
    """
    db = "MatrixNcciHp"
    bak = fixture_name("nccihp", "enc1for", "multi", dist, null=null, rows=rows)
    table = "dbo.cs_nccihp"
    col_types = _MULTI_TYPES
    null_mask = "pk % 10 = 0" if null == "spnull" else None
    stmts: list[str] = [f"CREATE DATABASE {db}"]
    stmts.append(f"USE {db}")
    stmts += seed_sql(rows)
    # Create as a heap (no clustered index), then add an NCCI.
    stmts.append(
        f"CREATE TABLE {table} (\n"
        f"    pk INT NOT NULL,\n"
        f"    {_col_defs(col_types)}\n"
        f")"
    )
    cols_select = _col_insert(col_types, dist, span=rows, k=min(512, rows), r=32, null_mask=null_mask)
    stmts.append(
        f"INSERT INTO {table} (pk, {', '.join(n for n, _ in col_types)})\n"
        f"SELECT pk, {cols_select} FROM fkr__seed WHERE pk < {rows}"
    )
    # Add NCCI after data is loaded (forces a columnstore build scan over heap).
    stmts.append(
        f"CREATE NONCLUSTERED COLUMNSTORE INDEX ix_ncci ON {table} "
        f"({', '.join(n for n, _ in col_types)})"
    )
    return db, bak, stmts


# ---------------------------------------------------------------------------
# 5. Delta store (open rowgroups)
# ---------------------------------------------------------------------------

def build_delta(
    dist: str = "asc",
    null: str | None = None,
    rows: int = 50_000,
) -> tuple[str, str, list[str]]:
    """CCI with a delta (open) rowgroup — below the compression threshold.

    Inserts fewer rows than the delta-threshold (~102 400) and does NOT call
    REORGANIZE, so the rowgroup stays in state ``OPEN``.  This exercises the
    delta-store reader (``_read_columnstore_delta_rows``).

    Returns (db_name, bak_name, sql_stmts).
    """
    db = "MatrixDelta"
    bak = fixture_name("delta", "enc1for", "multi", dist, null=null, rows=rows)
    table = "dbo.cs_delta"
    col_types = _MULTI_TYPES
    null_mask = "pk % 10 = 0" if null == "spnull" else None
    stmts: list[str] = [f"CREATE DATABASE {db}"]
    stmts.append(f"USE {db}")
    stmts += seed_sql(rows)
    stmts.append(
        f"CREATE TABLE {table} (\n"
        f"    pk INT NOT NULL,\n"
        f"    {_col_defs(col_types)}\n"
        f") WITH (DATA_COMPRESSION = COLUMNSTORE)"
    )
    cols_select = _col_insert(col_types, dist, span=rows, k=min(512, rows), r=32, null_mask=null_mask)
    stmts.append(
        f"INSERT INTO {table} (pk, {', '.join(n for n, _ in col_types)})\n"
        f"SELECT pk, {cols_select} FROM fkr__seed WHERE pk < {rows}"
    )
    # No REORGANIZE — leaves the rowgroup in OPEN/delta state.
    return db, bak, stmts


# ---------------------------------------------------------------------------
# 6. Delete bitmap
# ---------------------------------------------------------------------------

def build_delbmp(
    dist: str = "runs",
    null: str | None = None,
    rows: int = 200_000,
) -> tuple[str, str, list[str]]:
    """CCI with a non-empty delete bitmap.

    Loads and compresses a full rowgroup, then deletes every 10th row so
    SQL Server allocates a delete bitmap for that rowgroup.  This is the
    state that triggers the ``deleted_rows`` code path.

    Returns (db_name, bak_name, sql_stmts).
    """
    db = "MatrixDelBmp"
    bak = fixture_name("delbmp", "enc1for", "multi", dist, null=null, rows=rows)
    table = "dbo.cs_delbmp"
    col_types = _MULTI_TYPES
    null_mask = None
    stmts: list[str] = [f"CREATE DATABASE {db}"]
    stmts.append(f"USE {db}")
    stmts += seed_sql(rows)
    stmts.append(
        f"CREATE TABLE {table} (\n"
        f"    pk INT NOT NULL,\n"
        f"    {_col_defs(col_types)}\n"
        f") WITH (DATA_COMPRESSION = COLUMNSTORE)"
    )
    cols_select = _col_insert(col_types, dist, span=rows, k=min(512, rows), r=32, null_mask=null_mask)
    stmts.append(
        f"INSERT INTO {table} (pk, {', '.join(n for n, _ in col_types)})\n"
        f"SELECT pk, {cols_select} FROM fkr__seed WHERE pk < {rows}"
    )
    stmts += _reorganize(table)
    # Delete every 10th row — triggers delete bitmap allocation.
    stmts.append(f"DELETE FROM {table} WHERE pk % 10 = 0")
    return db, bak, stmts


# ---------------------------------------------------------------------------
# 7. MAX bpv=0 in CCI
# ---------------------------------------------------------------------------

def build_maxbpv0(
    dist: str = "rand",
    null: str | None = None,
    rows: int = 200_000,
) -> tuple[str, str, list[str]]:
    """CCI with MAX-type columns that force bpv=0 in compressed rowgroups.

    Large varchar(max)/nvarchar(max)/varbinary(max) values stored off-row in
    a CCI produce segments with encoding_type=3 or enc=5 and bpv=0 in
    ``sys.column_store_segments``.  This is the ``enc=5 MAX bpv=0`` blind spot.
    We use REPLICATE to generate values larger than the inline threshold.

    Returns (db_name, bak_name, sql_stmts).
    """
    db = "MatrixMaxBpv0"
    bak = fixture_name("cci", "enc5fa", "multi", dist, null=null, rows=rows)
    table = "dbo.cs_maxbpv0"
    null_mask = "pk % 10 = 0" if null == "spnull" else None

    # Generate values long enough to be stored off-row (>8000 bytes).
    idx = dist_expr(dist, span=rows, k=min(512, rows))
    vc_val = f"REPLICATE(CAST({idx} AS VARCHAR(20)), 400)"   # ~8000 chars
    nvc_val = f"REPLICATE(CAST(CAST({idx} AS VARCHAR(20)) AS NVARCHAR(20)), 200)"  # ~4000 nchars
    vb_val = f"CONVERT(VARBINARY(MAX), REPLICATE(CONVERT(BINARY(20), {idx}), 400))"  # ~8000 bytes
    if null_mask:
        vc_val  = f"CASE WHEN ({null_mask}) THEN NULL ELSE {vc_val} END"
        nvc_val = f"CASE WHEN ({null_mask}) THEN NULL ELSE {nvc_val} END"
        vb_val  = f"CASE WHEN ({null_mask}) THEN NULL ELSE {vb_val} END"

    stmts: list[str] = [f"CREATE DATABASE {db}"]
    stmts.append(f"USE {db}")
    stmts += seed_sql(rows)
    stmts.append(
        f"CREATE TABLE {table} (\n"
        f"    pk INT NOT NULL,\n"
        f"    col_vcmax  VARCHAR(MAX) NULL,\n"
        f"    col_nvcmax NVARCHAR(MAX) NULL,\n"
        f"    col_vbmax  VARBINARY(MAX) NULL\n"
        f") WITH (DATA_COMPRESSION = COLUMNSTORE)"
    )
    stmts.append(
        f"INSERT INTO {table} (pk, col_vcmax, col_nvcmax, col_vbmax)\n"
        f"SELECT pk, {vc_val}, {nvc_val}, {vb_val} FROM fkr__seed WHERE pk < {rows}"
    )
    stmts += _reorganize(table)
    return db, bak, stmts


# ---------------------------------------------------------------------------
# Suite registry
# ---------------------------------------------------------------------------

_SUITES: dict[str, object] = {
    "enc5fa":  build_enc5fa,
    "arch2":   build_arch2,
    "cciord":  build_cciord,
    "nccihp":  build_nccihp,
    "delta":   build_delta,
    "delbmp":  build_delbmp,
    "maxbpv0": build_maxbpv0,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate columnstore matrix fixtures for empty MATRIX_CELLS.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Suites: {', '.join(sorted(_SUITES))} or 'all'",
    )
    parser.add_argument("--suite", default="all",
                        help="which suite to build (default: all)")
    parser.add_argument("--dist", default=None,
                        help="override distribution token (default: per suite)")
    parser.add_argument("--null", default=None,
                        help="null pattern: spnull | nullrun | none (default: none)")
    parser.add_argument("--rows", type=int, default=None,
                        help="row count override (default: per suite)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print SQL statements without connecting to SQL Server")
    parser.add_argument("--container", default=None,
                        help="Podman container name (default: auto-detect)")
    args = parser.parse_args(argv)

    suite_keys = sorted(_SUITES) if args.suite == "all" else [args.suite]
    for key in suite_keys:
        if key not in _SUITES:
            print(f"error: unknown suite {key!r}; valid: {sorted(_SUITES)}", file=sys.stderr)
            return 1

    null_tok = args.null if args.null and args.null != "none" else None

    for key in suite_keys:
        fn = _SUITES[key]
        kwargs: dict[str, object] = {}
        if args.dist is not None:
            kwargs["dist"] = args.dist
        if null_tok is not None:
            kwargs["null"] = null_tok
        if args.rows is not None:
            kwargs["rows"] = args.rows

        db_name, bak_name, stmts = fn(**kwargs)  # type: ignore[operator]
        out_path = FIXTURE_DIR / bak_name
        container_bak = f"/tmp/{bak_name}"

        if args.dry_run:
            print(f"\n-- Suite: {key}  db={db_name}  out={out_path}")
            for s in stmts:
                print(s + ";")
            continue

        user, password, container_default = fixture_credentials()
        container = args.container or container_default
        load_and_backup_stmts(container, user, password, stmts)
        _copy_out(container, container_bak, out_path)
        print(f"==> {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
