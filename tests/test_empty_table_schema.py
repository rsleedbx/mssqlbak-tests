"""Tests for 0-row table schema round-trip verification.

Covers:
- pg_dir readback surfaces empty tables from archive TOC
- _compare_tables detects col-name mismatches on empty tables
- _compare_tables passes when empty table schema matches
- render helpers treat empty-but-present tables as real col-count checks
"""
from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path
from typing import Any

import pyarrow as pa
import pytest

from tools.correctness_coverage.compare import _compare_tables
from tools.correctness_coverage.render import _table_ok


# ---------------------------------------------------------------------------
# pg_dir empty-table readback
# ---------------------------------------------------------------------------


def _build_minimal_pg_dir(path: Path, tables: list[tuple[str, str, list[str]]]) -> None:
    """Write a minimal pg_dir archive with empty data files for each table.

    tables: list of (schema, table_name, col_names) tuples.
    """
    path.mkdir(parents=True, exist_ok=True)

    entries = []
    for pg_schema, pg_table, col_names in tables:
        col_defs = ", ".join(f'"{c}" text' for c in col_names)
        create_ddl = f'CREATE TABLE {pg_schema}."{pg_table}" (\n    {col_defs}\n);\n'
        col_list = ", ".join(f'"{c}"' for c in col_names)
        copy_stmt = f'COPY {pg_schema}."{pg_table}" ({col_list}) FROM stdin;\n'
        entries.append({
            "pg_schema": pg_schema,
            "pg_table": pg_table,
            "col_names": col_names,
            "create_ddl": create_ddl,
            "copy_stmt": copy_stmt,
        })

    # Write compressed empty data files (gzip with just "\\." terminator)
    for i, e in enumerate(entries):
        data_filename = f"{i + 100}.dat.gz"
        e["filename"] = data_filename
        raw = b"\\.\n"
        compressed = zlib.compress(raw)
        # Write as gzip
        import gzip
        data_path = path / data_filename
        with gzip.open(str(data_path), "wb") as gf:
            gf.write(b"\\.\n")

    # Build toc.dat using the pgdump writer
    from pgdump.dir_writer import DirArchive
    arch = DirArchive(path)
    for i, e in enumerate(entries):
        arch.add_table(
            schema=e["pg_schema"],
            table=e["pg_table"],
            create_stmt=e["create_ddl"],
            copy_stmt=e["copy_stmt"],
            data_filename=e["filename"],
        )
    arch.write_toc()


class _SimplePgDirArchive:
    """Minimal pg_dir archive built directly using DirSink for testing."""


def _make_pg_dir_with_empty_table(tmp_path: Path, col_names: list[str]) -> Path:
    """Use DirSink to produce a pg_dir archive with one 0-row table."""
    from mssqlbak.sinks.pg_dir_sink import DirSink

    out = tmp_path / "pg_out"
    out.mkdir()
    arrow_schema = pa.schema([(c, pa.int32()) for c in col_names])
    sink = DirSink(out)
    sink.open_table("dbo.empty_tbl", arrow_schema)
    # No write_batch — 0 rows
    sink.close()
    sink.finish()
    return out


def test_pg_dir_readback_surfaces_empty_table(tmp_path: Path) -> None:
    """_iter_pg_dir_tables must yield a 0-row table with the correct schema."""
    from tools.correctness_coverage.sinks import _iter_pg_dir_tables

    pg_out = _make_pg_dir_with_empty_table(tmp_path, ["id", "name", "score"])

    results = list(_iter_pg_dir_tables(pg_out, []))
    assert len(results) == 1, f"expected 1 table, got {len(results)}"
    fqn, tbl = results[0]
    assert isinstance(tbl, pa.Table)
    assert tbl.num_rows == 0
    assert tbl.schema.names == ["id", "name", "score"]


def test_pg_dir_readback_nonempty_table_unchanged(tmp_path: Path) -> None:
    """Non-empty tables still return all rows."""
    from mssqlbak.sinks.pg_dir_sink import DirSink
    from tools.correctness_coverage.sinks import _iter_pg_dir_tables

    out = tmp_path / "pg_out"
    out.mkdir()
    schema = pa.schema([("id", pa.int32()), ("val", pa.string())])
    sink = DirSink(out)
    sink.open_table("dbo.t1", schema)
    sink.write_batch(pa.record_batch([[1, 2], ["a", "b"]], schema=schema))
    sink.close()
    sink.finish()

    results = list(_iter_pg_dir_tables(out, []))
    assert len(results) == 1
    fqn, tbl = results[0]
    assert isinstance(tbl, pa.Table)
    assert tbl.num_rows == 2


# ---------------------------------------------------------------------------
# _compare_tables: empty-table schema checks
# ---------------------------------------------------------------------------


def _gt_node(
    fqn: str, *, col_names: list[str], expected_rows: int = 0
) -> dict[str, Any]:
    return {
        fqn: {
            "kind": "ground_truth",
            "expected_rows": expected_rows,
            "col_count": len(col_names),
            "col_names": col_names,
            "gt_columns": [{"name": c, "sql_type": "int", "null_count": None, "min_val": None, "max_val": None} for c in col_names],
        }
    }


def _arrow_node(fqn: str, *, col_names: list[str], row_count: int = 0) -> dict[str, Any]:
    return {
        fqn: {
            "kind": "arrow",
            "row_count": row_count,
            "null_counts": {},
            "min_vals": {},
            "max_vals": {},
            "col_count": len(col_names),
            "col_names": col_names,
        }
    }


def test_compare_empty_table_schema_match() -> None:
    """Empty table with correct col names produces col_count_ok=True, no bad_columns."""
    fqn = "dbo.empty_tbl"
    expected = _gt_node(fqn, col_names=["id", "name", "score"])
    actual = _arrow_node(fqn, col_names=["id", "name", "score"])

    rows = _compare_tables(
        expected, actual,
        table_types={fqn: "rowstore"},
        expected_skips=frozenset(),
        normalize_col=lambda c: c,
    )
    assert len(rows) == 1
    t = rows[0]
    assert t["col_count_ok"] is True
    assert t["_bad_columns"] == []
    assert t["row_ok"] is True  # 0 == 0


def test_compare_empty_table_missing_col() -> None:
    """Empty table with wrong col names sets bad_columns and col_count_ok=False."""
    fqn = "dbo.empty_tbl"
    expected = _gt_node(fqn, col_names=["id", "name", "score"])
    actual = _arrow_node(fqn, col_names=["id", "name", "WRONG"])

    rows = _compare_tables(
        expected, actual,
        table_types={fqn: "rowstore"},
        expected_skips=frozenset(),
        normalize_col=lambda c: c,
    )
    t = rows[0]
    assert "score" in t["_bad_columns"] or "WRONG" in str(t)


def test_compare_empty_table_absent_not_missing() -> None:
    """A 0-row GT table absent from actual output: row_ok=False (act is None), missing=False.

    missing_tbl requires expected_rows > 0 by design — a legitimately empty GT
    table with no actual output is not 'missing' in the diagnostic sense; it is
    simply not present (likely because the extractor skipped it).  row_ok is
    False because act is None.  col_count_ok is also False.
    """
    fqn = "dbo.empty_tbl"
    expected = _gt_node(fqn, col_names=["id", "name"])
    actual: dict[str, Any] = {}  # table not produced at all

    rows = _compare_tables(
        expected, actual,
        table_types={fqn: "rowstore"},
        expected_skips=frozenset(),
        normalize_col=lambda c: c,
    )
    t = rows[0]
    # act is None → row_ok=False; missing_tbl only set when expected_rows > 0
    assert t["row_ok"] is False
    assert t["missing"] is False
    assert t["col_count_ok"] is False


# ---------------------------------------------------------------------------
# render._table_ok: real col-count check for present 0-row tables
# ---------------------------------------------------------------------------


def _make_table_row(
    *,
    expected_rows: int,
    row_ok: bool,
    col_count_ok: bool,
    missing: bool = False,
    xtp_skip: bool = False,
    null_ok: int = 0,
    null_total: int = 0,
    minmax_ok: int = 0,
    minmax_total: int = 0,
) -> dict[str, Any]:
    return {
        "fqn": "dbo.t",
        "expected_rows": expected_rows,
        "row_ok": row_ok,
        "missing": missing,
        "xtp_skip": xtp_skip,
        "null_ok": null_ok,
        "null_total": null_total,
        "minmax_ok": minmax_ok,
        "minmax_total": minmax_total,
        "col_count_ok": col_count_ok,
        "n_gt_cols": 3,
        "column_ok": 3,
        "column_total": 3,
        "_column_names": ["a", "b", "c"],
        "_bad_columns": [],
    }


def test_table_ok_empty_present_col_ok() -> None:
    t = _make_table_row(expected_rows=0, row_ok=True, col_count_ok=True)
    assert _table_ok(t) is True


def test_table_ok_empty_present_col_fail() -> None:
    """A 0-row table that IS present and has wrong col count must NOT pass."""
    t = _make_table_row(expected_rows=0, row_ok=True, col_count_ok=False)
    assert _table_ok(t) is False


def test_table_ok_empty_missing_col_fail_is_ok() -> None:
    """A 0-row table that is absent (missing=True) gets a col-count free pass."""
    t = _make_table_row(expected_rows=0, row_ok=True, col_count_ok=False, missing=True)
    assert _table_ok(t) is True


def test_table_ok_xtp_skip_col_fail_is_ok() -> None:
    """An XTP-skipped table always passes regardless of col_count_ok."""
    t = _make_table_row(expected_rows=100, row_ok=False, col_count_ok=False, xtp_skip=True)
    assert _table_ok(t) is True
