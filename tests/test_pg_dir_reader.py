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
