"""Tests for pgdump.dir_reader — round-trip and idempotency verification.

Covers:
- Round-trip for all three codecs (zstd, gzip, none): write via DirSink, read
  back with read_dir_tables, assert schema + rows equal.
- Multi-frame decode: resume mode writes N frames; assert the resulting data
  file contains multiple frames and decodes to all rows.
- Simulated-crash resume idempotency: abandon a run mid-way, resume, complete;
  assert total rows == expected with no duplicates or missing rows.
- gzip-fix regression: assert resume-mode .dat.gz is real gzip (starts with
  1f 8b), not plain text.
- verify_dir_archive structural checks.
- parse_create_table_defn round-trip.
"""
from __future__ import annotations

import gzip
from pathlib import Path
from typing import Generator

import pyarrow as pa
import pytest

from mssqlbak.sinks.pg_dir_sink import DirSink
from pgdump.dir_reader import (
    DirVerifyReport,
    iter_dir_batches,
    read_dir_archive,
    read_dir_tables,
    verify_dir_archive,
)
from pgdump.schema import parse_create_table_defn


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCHEMA = pa.schema([
    ("id",   pa.int32()),
    ("name", pa.large_utf8()),
    ("val",  pa.float64()),
])

_ROWS_A = [(1, "Alice",  1.5), (2, "Bob",   2.5)]
_ROWS_B = [(3, "Carol",  3.5), (4, "Dave",  4.5)]
_ROWS_C = [(5, "Eve",    5.5)]
_ALL_ROWS = _ROWS_A + _ROWS_B + _ROWS_C


def _make_batch(rows: list[tuple], schema: pa.Schema = _SCHEMA) -> pa.RecordBatch:
    col_data: list[list] = [[] for _ in schema]
    for row in rows:
        for i, val in enumerate(row):
            col_data[i].append(val)
    arrays = [pa.array(col_data[i], type=schema.field(i).type) for i in range(len(schema))]
    return pa.RecordBatch.from_arrays(arrays, schema=schema)


def _write_simple(out_dir: Path, codec: str) -> None:
    """Write _ALL_ROWS to a fresh DirSink (non-resume) in one batch."""
    sink = DirSink(out_dir, dir_codec=codec)  # type: ignore[arg-type]
    sink.open_table("public.t1", _SCHEMA)
    sink.write_batch(_make_batch(_ALL_ROWS))
    sink.close()
    sink.finish()


def _table_rows(table: pa.Table) -> list[tuple]:
    return list(zip(*[col.to_pylist() for col in table.columns]))


# ---------------------------------------------------------------------------
# parse_create_table_defn
# ---------------------------------------------------------------------------

class TestParseCreateTableDefn:
    def test_basic_columns(self) -> None:
        defn = (
            "CREATE TABLE public.orders (\n"
            "    id integer,\n"
            "    name text,\n"
            "    amount double precision\n"
            ");\n"
        )
        tdef = parse_create_table_defn(defn)
        assert tdef.schema == "public"
        assert tdef.table == "orders"
        names = [c.name for c in tdef.columns]
        assert names == ["id", "name", "amount"]

    def test_fallback_schema_table(self) -> None:
        defn = "CREATE TABLE foo (\n    x integer\n);\n"
        tdef = parse_create_table_defn(defn, schema="myschema", table="fallback")
        # schema/table extracted from the DDL takes priority
        assert tdef.table == "foo"

    def test_no_columns_returns_empty(self) -> None:
        tdef = parse_create_table_defn("some random text", schema="s", table="t")
        assert tdef.columns == []


# ---------------------------------------------------------------------------
# Round-trip: all three codecs (non-resume)
# ---------------------------------------------------------------------------

class TestRoundTripNonResume:
    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_write_read_roundtrip(self, tmp_path: Path, codec: str) -> None:
        _write_simple(tmp_path, codec)
        tables = read_dir_tables(tmp_path)
        assert "public.t1" in tables
        got = _table_rows(tables["public.t1"])
        assert sorted(got) == sorted(_ALL_ROWS)

    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_schema_preserved(self, tmp_path: Path, codec: str) -> None:
        _write_simple(tmp_path, codec)
        tables = read_dir_tables(tmp_path)
        tbl = tables["public.t1"]
        assert tbl.schema.names == list(_SCHEMA.names)

    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_row_count(self, tmp_path: Path, codec: str) -> None:
        _write_simple(tmp_path, codec)
        tables = read_dir_tables(tmp_path)
        assert len(tables["public.t1"]) == len(_ALL_ROWS)

    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_iter_dir_batches_yields_correct_name(self, tmp_path: Path, codec: str) -> None:
        _write_simple(tmp_path, codec)
        names = {qname for qname, _ in iter_dir_batches(tmp_path)}
        assert names == {"public.t1"}

    def test_multiple_tables(self, tmp_path: Path) -> None:
        schema2 = pa.schema([("x", pa.int64()), ("y", pa.large_utf8())])
        sink = DirSink(tmp_path, dir_codec="zstd")
        sink.open_table("dbo.A", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A))
        sink.close()
        sink.open_table("dbo.B", schema2)
        batch_b = pa.RecordBatch.from_arrays(
            [pa.array([10, 20], type=pa.int64()),
             pa.array(["p", "q"], type=pa.large_utf8())],
            schema=schema2,
        )
        sink.write_batch(batch_b)
        sink.close()
        sink.finish()

        tables = read_dir_tables(tmp_path)
        assert set(tables.keys()) == {"dbo.A", "dbo.B"}
        assert len(tables["dbo.A"]) == 2
        assert len(tables["dbo.B"]) == 2


# ---------------------------------------------------------------------------
# Multi-frame decode (resume mode)
# ---------------------------------------------------------------------------

class TestMultiFrameDecode:
    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_multi_frame_round_trip(self, tmp_path: Path, codec: str) -> None:
        """Write three separate batches in resume mode; read back all rows."""
        sink = DirSink(tmp_path, resume=True, dir_codec=codec)  # type: ignore[arg-type]
        sink.open_table("public.t1", _SCHEMA)
        for batch_rows in [_ROWS_A, _ROWS_B, _ROWS_C]:
            sink.write_batch(_make_batch(batch_rows))
        sink.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink.finish()

        tables = read_dir_tables(tmp_path)
        assert "public.t1" in tables
        got = sorted(_table_rows(tables["public.t1"]))
        assert got == sorted(_ALL_ROWS)

    @pytest.mark.parametrize("codec", ["zstd", "gzip"])
    def test_data_file_is_compressed(self, tmp_path: Path, codec: str) -> None:
        """Assert the data file is actually a compressed file."""
        sink = DirSink(tmp_path, resume=True, dir_codec=codec)  # type: ignore[arg-type]
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A))
        sink.mark_table_complete("public.t1", len(_ROWS_A))
        sink.finish()

        archive = read_dir_archive(tmp_path)
        _, entry = archive.tables["public.t1"]
        data_path = tmp_path / entry.filename
        raw = data_path.read_bytes()

        if codec == "zstd":
            # zstd frame magic: 0xFD2FB528 stored as bytes 28 b5 2f fd
            assert raw[:4] == b"\x28\xb5\x2f\xfd", "Expected zstd magic"
        elif codec == "gzip":
            assert raw[:2] == b"\x1f\x8b", "Expected gzip magic"


# ---------------------------------------------------------------------------
# gzip fix regression
# ---------------------------------------------------------------------------

class TestGzipFixRegression:
    def test_resume_gzip_file_starts_with_gzip_magic(self, tmp_path: Path) -> None:
        """Resume-mode .dat.gz must be real gzip, not plain text."""
        sink = DirSink(tmp_path, resume=True, dir_codec="gzip")
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A))
        sink.mark_table_complete("public.t1", len(_ROWS_A))
        sink.finish()

        archive = read_dir_archive(tmp_path)
        _, entry = archive.tables["public.t1"]
        data_path = tmp_path / entry.filename

        assert data_path.suffix == ".gz", "Expected .dat.gz file"
        raw = data_path.read_bytes()
        assert raw[:2] == b"\x1f\x8b", (
            f"Expected gzip magic 1f 8b, got {raw[:4].hex()}. "
            "The file appears to be plain text (gzip fix regression)."
        )
        # Also assert it decompresses without error.
        decompressed = gzip.decompress(raw)
        assert b"\\." in decompressed, "Expected COPY terminator in decompressed output"

    def test_resume_gzip_multi_member_decodes(self, tmp_path: Path) -> None:
        """Multiple gzip members decode as one stream."""
        sink = DirSink(tmp_path, resume=True, dir_codec="gzip")
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A))
        sink.write_batch(_make_batch(_ROWS_B))
        sink.mark_table_complete("public.t1", len(_ROWS_A) + len(_ROWS_B))
        sink.finish()

        tables = read_dir_tables(tmp_path)
        got = sorted(_table_rows(tables["public.t1"]))
        assert got == sorted(_ROWS_A + _ROWS_B)


# ---------------------------------------------------------------------------
# Simulated-crash resume idempotency
# ---------------------------------------------------------------------------

class TestResumeCrashIdempotency:
    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_no_duplicates_after_resume(self, tmp_path: Path, codec: str) -> None:
        """Write some batches, 'crash' (abandon without mark_table_complete),
        then resume with a new DirSink and write remaining batches.
        Final row count must equal the total with no duplicates.
        """
        # First run: write _ROWS_A and _ROWS_B, then abandon.
        sink1 = DirSink(
            tmp_path, resume=True, dir_codec=codec,  # type: ignore[arg-type]
            source_identity="test-source-v1",
        )
        sink1.open_table("public.t1", _SCHEMA)
        sink1.write_batch(_make_batch(_ROWS_A))
        sink1.write_batch(_make_batch(_ROWS_B))
        # Simulate crash: do NOT call mark_table_complete or finish toc.
        # Just close the segment writer so the file is flushed.
        sink1.close()

        # Second run: resume and write the remaining batch.
        sink2 = DirSink(
            tmp_path, resume=True, dir_codec=codec,  # type: ignore[arg-type]
            source_identity="test-source-v1",
        )
        sink2.open_table("public.t1", _SCHEMA)
        sink2.write_batch(_make_batch(_ROWS_C))
        sink2.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink2.finish()

        tables = read_dir_tables(tmp_path)
        assert "public.t1" in tables
        got = _table_rows(tables["public.t1"])
        assert len(got) == len(_ALL_ROWS), (
            f"Expected {len(_ALL_ROWS)} rows, got {len(got)}. "
            f"Rows: {got}"
        )
        assert sorted(got) == sorted(_ALL_ROWS), (
            "Row values do not match after resume (duplicates or missing rows)."
        )

    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_complete_table_not_reprocessed(self, tmp_path: Path, codec: str) -> None:
        """Once a table is marked complete, a second run skips it entirely."""
        sink1 = DirSink(tmp_path, resume=True, dir_codec=codec,  # type: ignore[arg-type]
                        source_identity="si")
        sink1.open_table("public.t1", _SCHEMA)
        sink1.write_batch(_make_batch(_ALL_ROWS))
        sink1.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink1.finish()

        from mssqlbak.sink import ResumePoint
        sink2 = DirSink(tmp_path, resume=True, dir_codec=codec,  # type: ignore[arg-type]
                        source_identity="si")
        rp = sink2.table_resume_point("public.t1")
        assert rp is not None and rp.complete, "Table should be marked complete on resume"


# ---------------------------------------------------------------------------
# verify_dir_archive
# ---------------------------------------------------------------------------

class TestVerifyDirArchive:
    def test_verify_fresh_write_all_ok(self, tmp_path: Path) -> None:
        _write_simple(tmp_path, "zstd")
        report = verify_dir_archive(tmp_path)
        assert report.all_ok, [
            f"{t.qualified_name}: {t.error}" for t in report.tables if not t.ok
        ]
        assert report.total_rows == len(_ALL_ROWS)

    def test_verify_reports_row_count(self, tmp_path: Path) -> None:
        _write_simple(tmp_path, "gzip")
        report = verify_dir_archive(tmp_path)
        assert report.tables[0].row_count == len(_ALL_ROWS)

    def test_verify_missing_data_file(self, tmp_path: Path) -> None:
        _write_simple(tmp_path, "zstd")
        archive = read_dir_archive(tmp_path)
        for _, entry in archive.tables.values():
            (tmp_path / entry.filename).unlink()
        report = verify_dir_archive(tmp_path)
        assert not report.all_ok
        assert any(not t.file_exists for t in report.tables)

    def test_verify_missing_toc_dat(self, tmp_path: Path) -> None:
        report = verify_dir_archive(tmp_path)
        assert not report.all_ok

    @pytest.mark.parametrize("codec", ["zstd", "gzip", "none"])
    def test_verify_all_codecs(self, tmp_path: Path, codec: str) -> None:
        _write_simple(tmp_path, codec)
        report = verify_dir_archive(tmp_path)
        assert report.all_ok


# ---------------------------------------------------------------------------
# read_dir_archive
# ---------------------------------------------------------------------------

class TestReadDirArchive:
    def test_archive_has_table_entry(self, tmp_path: Path) -> None:
        _write_simple(tmp_path, "zstd")
        archive = read_dir_archive(tmp_path)
        assert "public.t1" in archive.tables

    def test_archive_toc_entries_populated(self, tmp_path: Path) -> None:
        _write_simple(tmp_path, "zstd")
        archive = read_dir_archive(tmp_path)
        assert len(archive.toc_entries) > 0

    def test_missing_toc_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_dir_archive(tmp_path)

    def test_db_name_preserved(self, tmp_path: Path) -> None:
        sink = DirSink(tmp_path, db_name="mydb", dir_codec="zstd")
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A))
        sink.close()
        sink.finish()
        archive = read_dir_archive(tmp_path)
        assert archive.db_name == "mydb"


# ---------------------------------------------------------------------------
# C++ stringify codec parity (float, naive timestamp, all-null, escapes)
# ---------------------------------------------------------------------------

class TestCppCodecParity:
    """Validate that the all-C++ _encode_batch_copy_text / _copy_text_to_table
    pipeline round-trips values correctly for the types affected by the new
    C++ stringify path."""

    def _rt(self, schema: pa.Schema, batch: pa.RecordBatch, tmp_path: Path) -> pa.Table:
        """Write one batch and read it back."""
        sink = DirSink(tmp_path, dir_codec="zstd")
        sink.open_table("public.t", schema)
        sink.write_batch(batch)
        sink.close()
        sink.finish()
        return read_dir_tables(tmp_path)["public.t"]

    def test_float_values_round_trip(self, tmp_path: Path) -> None:
        """float64 columns: C++ cast emits different text but same value."""
        import datetime as dt
        schema = pa.schema([("f", pa.float64())])
        vals = [0.0, 100.0, -3.14, 1e20, 1e-7, 1.23456789]
        batch = pa.RecordBatch.from_arrays(
            [pa.array(vals, type=pa.float64())], schema=schema
        )
        result = self._rt(schema, batch, tmp_path)
        got = result.column("f").to_pylist()
        assert got == vals

    def test_float_nulls_round_trip(self, tmp_path: Path) -> None:
        schema = pa.schema([("f", pa.float64())])
        vals = [1.5, None, 2.5]
        batch = pa.RecordBatch.from_arrays(
            [pa.array(vals, type=pa.float64())], schema=schema
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.column("f").to_pylist() == vals

    def test_naive_timestamp_round_trip(self, tmp_path: Path) -> None:
        """Naive timestamp[us] now stringified and parsed in C++."""
        import datetime as dt
        schema = pa.schema([("ts", pa.timestamp("us"))])
        vals = [
            dt.datetime(2020, 1, 2, 3, 4, 5, 123456),
            dt.datetime(2020, 1, 2, 3, 4, 5, 0),       # zero microseconds
            dt.datetime(1999, 12, 31, 23, 59, 59, 1),
            None,
        ]
        batch = pa.RecordBatch.from_arrays(
            [pa.array(vals, type=pa.timestamp("us"))], schema=schema
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.column("ts").to_pylist() == vals

    def test_all_null_column_round_trip(self, tmp_path: Path) -> None:
        """A column with every value null must survive the COPY round-trip."""
        schema = pa.schema([("id", pa.int32()), ("x", pa.float64())])
        batch = pa.RecordBatch.from_arrays(
            [
                pa.array([1, 2, 3], type=pa.int32()),
                pa.array([None, None, None], type=pa.float64()),
            ],
            schema=schema,
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.column("id").to_pylist() == [1, 2, 3]
        assert result.column("x").to_pylist() == [None, None, None]

    def test_string_with_embedded_tab_newline_backslash(self, tmp_path: Path) -> None:
        """Strings containing tab, newline, CR, and backslash are escaped on
        write and unescaped on read to identical values."""
        schema = pa.schema([("s", pa.large_utf8())])
        vals = [
            "hello\tworld",     # embedded tab
            "line1\nline2",     # embedded newline
            "cr\r end",         # embedded CR
            "back\\slash",      # embedded backslash
            "mixed\t\n\\",      # all three
            None,
        ]
        batch = pa.RecordBatch.from_arrays(
            [pa.array(vals, type=pa.large_utf8())], schema=schema
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.column("s").to_pylist() == vals

    def test_bool_and_int8_round_trip(self, tmp_path: Path) -> None:
        """bool and int8 (SQL Server bit) encode as t/f and decode back."""
        schema = pa.schema([("b", pa.bool_()), ("i8", pa.int8())])
        batch = pa.RecordBatch.from_arrays(
            [
                pa.array([True, False, None], type=pa.bool_()),
                pa.array([1, 0, None], type=pa.int8()),
            ],
            schema=schema,
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.column("b").to_pylist() == [True, False, None]
        assert result.column("i8").to_pylist() == [1, 0, None]

    def test_decimal_round_trip(self, tmp_path: Path) -> None:
        """decimal128 values survive C++ cast → read_csv round-trip."""
        import decimal
        schema = pa.schema([("d", pa.decimal128(19, 4))])
        vals = [decimal.Decimal("12345.6789"), decimal.Decimal("0.0001"), None]
        batch = pa.RecordBatch.from_arrays(
            [pa.array(vals, type=pa.decimal128(19, 4))], schema=schema
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.column("d").to_pylist() == vals


# ---------------------------------------------------------------------------
# Regression: reserved-word column names must not be dropped by the DDL parser
# ---------------------------------------------------------------------------

class TestReservedWordColumnNames:
    """A column whose name is a SQL/PG constraint keyword (PRIMARY, UNIQUE, etc.)
    must round-trip correctly when the name is quoted in the CREATE TABLE DDL.

    Regression for: _parse_column_line stripped quotes before the constraint-
    keyword guard, so 'Primary' was mistaken for a PRIMARY KEY clause and the
    column was silently dropped, falling back to text on readback.
    """

    def _rt(self, schema: pa.Schema, batch: pa.RecordBatch, tmp_path: Path) -> pa.Table:
        sink = DirSink(tmp_path, dir_codec="none")
        sink.open_table("dbo.T", schema)
        sink.write_batch(batch)
        sink.close()
        sink.finish()
        return read_dir_tables(tmp_path)["dbo.T"]

    def test_primary_column_round_trips_as_boolean(self, tmp_path: Path) -> None:
        """Column named 'Primary' (int8 / SQL Server bit) must decode as boolean."""
        schema = pa.schema([
            pa.field("Primary", pa.int8()),
            pa.field("Flag", pa.int8()),
        ])
        batch = pa.RecordBatch.from_arrays(
            [
                pa.array([1, 1, 0], type=pa.int8()),
                pa.array([1, 0, 0], type=pa.int8()),
            ],
            schema=schema,
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.schema.names == ["Primary", "Flag"], (
            "Column 'Primary' was dropped by the DDL parser"
        )
        # int8 (bit workaround) is written as 't'/'f' and read back as bool
        assert result.column("Primary").to_pylist() == [True, True, False]
        assert result.column("Flag").to_pylist() == [True, False, False]

    def test_unique_constraint_column_round_trips(self, tmp_path: Path) -> None:
        """Column named 'Unique' (large_utf8) must not be silently dropped."""
        schema = pa.schema([
            pa.field("id", pa.int32()),
            pa.field("Unique", pa.large_utf8()),
        ])
        batch = pa.RecordBatch.from_arrays(
            [
                pa.array([1, 2], type=pa.int32()),
                pa.array(["a", "b"], type=pa.large_utf8()),
            ],
            schema=schema,
        )
        result = self._rt(schema, batch, tmp_path)
        assert "Unique" in result.schema.names, (
            "Column 'Unique' was dropped by the DDL parser"
        )
        assert result.column("Unique").to_pylist() == ["a", "b"]

    def test_check_foreign_columns_round_trip(self, tmp_path: Path) -> None:
        """Columns named 'Check' and 'Foreign' must both survive the round-trip."""
        schema = pa.schema([
            pa.field("Check", pa.int32()),
            pa.field("Foreign", pa.large_utf8()),
        ])
        batch = pa.RecordBatch.from_arrays(
            [
                pa.array([10, 20], type=pa.int32()),
                pa.array(["x", "y"], type=pa.large_utf8()),
            ],
            schema=schema,
        )
        result = self._rt(schema, batch, tmp_path)
        assert result.schema.names == ["Check", "Foreign"]
        assert result.column("Check").to_pylist() == [10, 20]
        assert result.column("Foreign").to_pylist() == ["x", "y"]


# ---------------------------------------------------------------------------
# Regression: _arrow_minmax_equal must compare string-encoded time vs time64
# ---------------------------------------------------------------------------

class TestArrowMinmaxEqualTemporal:
    """_arrow_minmax_equal must handle the write-fidelity case where one side is
    a string (extractor representation for TIME/DATE/DATETIME columns) and the
    other is a native Python temporal value (pg_dir reader output).
    """

    def setup_method(self) -> None:
        from tools.correctness_coverage.compare import _arrow_minmax_equal
        self._eq = _arrow_minmax_equal

    def test_time_str_vs_time_obj_equal(self) -> None:
        import datetime as dt
        assert self._eq("07:00:00.0000000", dt.time(7, 0))
        assert self._eq(dt.time(23, 0), "23:00:00.0000000")

    def test_time_str_vs_time_obj_not_equal(self) -> None:
        import datetime as dt
        assert not self._eq("07:00:00.0000000", dt.time(8, 0))
        assert not self._eq(dt.time(7, 0), "08:00:00.0000000")

    def test_time_both_native_equal(self) -> None:
        import datetime as dt
        assert self._eq(dt.time(7, 0), dt.time(7, 0))

    def test_date_str_vs_date_obj_equal(self) -> None:
        import datetime as dt
        assert self._eq("2020-01-15", dt.date(2020, 1, 15))
        assert self._eq(dt.date(2020, 1, 15), "2020-01-15")

    def test_date_str_vs_date_obj_not_equal(self) -> None:
        import datetime as dt
        assert not self._eq("2020-01-15", dt.date(2020, 1, 16))

    def test_numeric_tolerance_unchanged(self) -> None:
        assert self._eq(1.0000001, 1.0)
        assert not self._eq(2.0, 1.0)

    def test_none_handling_unchanged(self) -> None:
        assert self._eq(None, None)
        assert not self._eq(None, 1)
        assert not self._eq(1, None)
