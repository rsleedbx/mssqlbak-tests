"""Tests for mssqlbak.delta_reader — Delta round-trip and idempotency verification.

Covers:
- Round-trip (non-resume): write via DeltaSink, read back with read_delta_tables,
  assert schema + row values equal; multi-table case.
- Round-trip (resume mode): write with Checkpoint, mark_table_complete; read back.
- Multi-batch: N batches as N commits; version advances; all rows decode.
- Idempotency after simulated crash: run 1 writes some batches and abandons;
  run 2 consults table_resume_point, writes remaining; total == expected, no dups.
- SetTransaction caller-side dedup: re-running a version already committed
  by checking transaction_version first does NOT produce duplicate rows.
- Completion-marker regression: after mark_table_complete, table_resume_point
  returns complete=True and verify_delta_root classifies it as "complete".
- verify_delta_root structural checks: all_ok + total_rows; missing table dir
  flagged; in_progress vs complete classification.
"""
from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pytest

from mssqlbak.delta_reader import (
    read_delta_root,
    read_delta_table,
    read_delta_tables,
    verify_delta_root,
)
from mssqlbak.sink import Checkpoint, DeltaSink, ResumePoint, _COMPLETE_MARKER_VERSION


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCHEMA = pa.schema([
    ("id",   pa.int32()),
    ("name", pa.large_utf8()),
    ("val",  pa.float64()),
])

_ROWS_A = [(1, "Alice",  1.5), (2, "Bob",    2.5)]
_ROWS_B = [(3, "Carol",  3.5), (4, "Dave",   4.5)]
_ROWS_C = [(5, "Eve",    5.5)]
_ALL_ROWS = _ROWS_A + _ROWS_B + _ROWS_C


def _make_batch(rows: list[tuple], schema: pa.Schema = _SCHEMA) -> pa.RecordBatch:
    col_data: list[list] = [[] for _ in schema]
    for row in rows:
        for i, val in enumerate(row):
            col_data[i].append(val)
    arrays = [pa.array(col_data[i], type=schema.field(i).type) for i in range(len(schema))]
    return pa.RecordBatch.from_arrays(arrays, schema=schema)


def _table_rows(table: pa.Table) -> list[tuple]:
    return list(zip(*[col.to_pylist() for col in table.columns]))


def _write_simple(root: Path) -> None:
    """Write _ALL_ROWS to a fresh DeltaSink (non-resume) in one batch."""
    sink = DeltaSink(root)
    sink.open_table("public.t1", _SCHEMA)
    sink.write_batch(_make_batch(_ALL_ROWS))
    sink.close()
    sink.finish()


# ---------------------------------------------------------------------------
# Round-trip, non-resume
# ---------------------------------------------------------------------------

class TestRoundTripNonResume:
    def test_read_delta_tables(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        tables = read_delta_tables(tmp_path)
        assert "public.t1" in tables
        got = sorted(_table_rows(tables["public.t1"]))
        assert got == sorted(_ALL_ROWS)

    def test_schema_preserved(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        tables = read_delta_tables(tmp_path)
        tbl = tables["public.t1"]
        # DeltaSink sanitizes column names, all _SCHEMA names are safe here.
        assert tbl.schema.names == list(_SCHEMA.names)

    def test_row_count(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        tables = read_delta_tables(tmp_path)
        assert len(tables["public.t1"]) == len(_ALL_ROWS)

    def test_read_delta_table_direct(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        dr = read_delta_root(tmp_path)
        info = dr.tables["public.t1"]
        table = read_delta_table(info.path)
        assert len(table) == len(_ALL_ROWS)

    def test_multiple_tables(self, tmp_path: Path) -> None:
        schema2 = pa.schema([("x", pa.int64()), ("y", pa.large_utf8())])
        sink = DeltaSink(tmp_path)
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

        tables = read_delta_tables(tmp_path)
        assert set(tables.keys()) == {"dbo.A", "dbo.B"}
        assert len(tables["dbo.A"]) == 2
        assert len(tables["dbo.B"]) == 2


# ---------------------------------------------------------------------------
# Multi-batch (N commits)
# ---------------------------------------------------------------------------

class TestMultiBatch:
    def test_multiple_batches_all_rows(self, tmp_path: Path) -> None:
        """Write three batches as three overwrite+append commits; all rows present."""
        sink = DeltaSink(tmp_path)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A))   # first write → overwrite
        sink.write_batch(_make_batch(_ROWS_B))   # second → append
        sink.write_batch(_make_batch(_ROWS_C))   # third → append
        sink.close()
        sink.finish()

        tables = read_delta_tables(tmp_path)
        got = sorted(_table_rows(tables["public.t1"]))
        assert got == sorted(_ALL_ROWS)

    def test_delta_version_advances(self, tmp_path: Path) -> None:
        """Each write_batch with a Checkpoint advances the Delta log version."""
        from deltalake import DeltaTable
        from mssqlbak.sink import sanitize_uc_id

        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        app_id = "mssqlbak:public.t1"

        for i, rows in enumerate([_ROWS_A, _ROWS_B, _ROWS_C]):
            sink.write_batch(
                _make_batch(rows),
                checkpoint=Checkpoint(app_id=app_id, version=i, cursor=f"p{i}"),
            )
        sink.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink.close()
        sink.finish()

        path = tmp_path / sanitize_uc_id("public") / sanitize_uc_id("t1")
        dt = DeltaTable(str(path))
        # Versions: 0=first write (overwrite), 1=append, 2=append, 3=complete marker
        assert dt.version() >= 3


# ---------------------------------------------------------------------------
# Round-trip, resume mode
# ---------------------------------------------------------------------------

class TestRoundTripResume:
    def test_write_read_with_checkpoints(self, tmp_path: Path) -> None:
        """Write batches under resume=True with Checkpoint objects; read back."""
        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.write_batch(_make_batch(_ROWS_B), checkpoint=Checkpoint(app_id, 1, "p1"))
        sink.write_batch(_make_batch(_ROWS_C), checkpoint=Checkpoint(app_id, 2, "p2"))
        sink.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink.close()
        sink.finish()

        tables = read_delta_tables(tmp_path)
        got = sorted(_table_rows(tables["public.t1"]))
        assert got == sorted(_ALL_ROWS)

    def test_resume_point_complete(self, tmp_path: Path) -> None:
        """After mark_table_complete, table_resume_point returns complete=True."""
        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.mark_table_complete("public.t1", len(_ROWS_A))
        sink.close()
        sink.finish()

        sink2 = DeltaSink(tmp_path, resume=True)
        rp = sink2.table_resume_point("public.t1")
        assert rp is not None
        assert rp.complete is True


# ---------------------------------------------------------------------------
# Simulated-crash resume idempotency
# ---------------------------------------------------------------------------

class TestResumeCrashIdempotency:
    def test_no_duplicates_after_resume(self, tmp_path: Path) -> None:
        """Run 1 writes v0+v1 and abandons; run 2 picks up with v2; total == expected."""
        app_id = "mssqlbak:public.t1"

        # Run 1: write versions 0 and 1, then abandon (no mark_table_complete).
        sink1 = DeltaSink(tmp_path, resume=True)
        sink1.open_table("public.t1", _SCHEMA)
        sink1.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink1.write_batch(_make_batch(_ROWS_B), checkpoint=Checkpoint(app_id, 1, "p1"))
        sink1.close()
        # Do NOT call sink1.finish() — crash simulation.

        # Confirm intermediate state: in_progress, next_version=2.
        sink_check = DeltaSink(tmp_path, resume=True)
        rp: ResumePoint | None = sink_check.table_resume_point("public.t1")
        assert rp is not None and not rp.complete
        assert rp.next_version == 2
        assert rp.cursor == "p1"

        # Run 2: resume from next_version=2, write only the remaining batch.
        sink2 = DeltaSink(tmp_path, resume=True)
        sink2.open_table("public.t1", _SCHEMA)  # detects existing txn → append mode
        sink2.write_batch(_make_batch(_ROWS_C), checkpoint=Checkpoint(app_id, 2, "p2"))
        sink2.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink2.close()
        sink2.finish()

        tables = read_delta_tables(tmp_path)
        got = _table_rows(tables["public.t1"])
        assert len(got) == len(_ALL_ROWS), (
            f"Expected {len(_ALL_ROWS)} rows, got {len(got)}: {got}"
        )
        assert sorted(got) == sorted(_ALL_ROWS), (
            "Duplicate or missing rows after resume (idempotency failure)."
        )

    def test_completed_table_skipped(self, tmp_path: Path) -> None:
        """After complete, a second DeltaSink reports complete=True."""
        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ALL_ROWS), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink.close()
        sink.finish()

        sink2 = DeltaSink(tmp_path, resume=True)
        rp = sink2.table_resume_point("public.t1")
        assert rp is not None and rp.complete


# ---------------------------------------------------------------------------
# SetTransaction caller-side dedup
# ---------------------------------------------------------------------------

class TestSetTransactionDedup:
    def test_skip_already_committed_version(self, tmp_path: Path) -> None:
        """Caller checks transaction_version before writing; skips already-committed
        batches so no duplicates are written despite delta-rs not auto-deduping."""
        from deltalake import DeltaTable
        from mssqlbak.sink import sanitize_uc_id

        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.write_batch(_make_batch(_ROWS_B), checkpoint=Checkpoint(app_id, 1, "p1"))
        sink.close()

        # Simulate what the driver does on resume: check next_version before writing.
        sink2 = DeltaSink(tmp_path, resume=True)
        rp = sink2.table_resume_point("public.t1")
        assert rp is not None and not rp.complete
        next_ver = rp.next_version
        assert next_ver == 2  # should skip 0 and 1

        # Driver writes only from next_version onward.
        sink2.open_table("public.t1", _SCHEMA)
        # Batch for version 2 only (versions 0 and 1 already committed → skip).
        sink2.write_batch(_make_batch(_ROWS_C), checkpoint=Checkpoint(app_id, next_ver, "p2"))
        sink2.mark_table_complete("public.t1", len(_ALL_ROWS))
        sink2.close()
        sink2.finish()

        path = tmp_path / sanitize_uc_id("public") / sanitize_uc_id("t1")
        table = DeltaTable(str(path)).to_pyarrow_table()
        assert len(table) == len(_ALL_ROWS), (
            f"Expected {len(_ALL_ROWS)} rows, got {len(table)}: "
            f"{table['id'].to_pylist()}"
        )

    def test_transaction_version_reports_last_committed(self, tmp_path: Path) -> None:
        """transaction_version(app_id) returns the highest committed version."""
        from deltalake import DeltaTable
        from mssqlbak.sink import sanitize_uc_id

        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        for i, rows in enumerate([_ROWS_A, _ROWS_B]):
            sink.write_batch(_make_batch(rows), checkpoint=Checkpoint(app_id, i, f"p{i}"))
        sink.close()

        path = tmp_path / sanitize_uc_id("public") / sanitize_uc_id("t1")
        dt = DeltaTable(str(path))
        assert dt.transaction_version(app_id) == 1


# ---------------------------------------------------------------------------
# Completion-marker regression
# ---------------------------------------------------------------------------

class TestCompletionMarker:
    def test_completion_marker_persists(self, tmp_path: Path) -> None:
        """mark_table_complete persists; table_resume_point → complete=True."""
        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.mark_table_complete("public.t1", len(_ROWS_A))
        sink.close()
        sink.finish()

        sink2 = DeltaSink(tmp_path, resume=True)
        rp = sink2.table_resume_point("public.t1")
        assert rp is not None, "Expected a ResumePoint, got None"
        assert rp.complete, "Expected complete=True after mark_table_complete"

    def test_completion_marker_txn_version(self, tmp_path: Path) -> None:
        """The completion marker uses _COMPLETE_MARKER_VERSION as txn version."""
        from deltalake import DeltaTable
        from mssqlbak.sink import sanitize_uc_id

        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.mark_table_complete("public.t1", len(_ROWS_A))
        sink.close()
        sink.finish()

        path = tmp_path / sanitize_uc_id("public") / sanitize_uc_id("t1")
        dt = DeltaTable(str(path))
        assert dt.transaction_version(app_id) == _COMPLETE_MARKER_VERSION

    def test_verify_delta_root_complete_classification(self, tmp_path: Path) -> None:
        """verify_delta_root classifies a completed table as 'complete'."""
        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.mark_table_complete("public.t1", len(_ROWS_A))
        sink.close()
        sink.finish()

        report = verify_delta_root(tmp_path)
        t1_result = next(
            t for t in report.tables if t.qualified_name == "public.t1"
        )
        assert t1_result.resume_state == "complete", (
            f"Expected 'complete', got {t1_result.resume_state!r}"
        )


# ---------------------------------------------------------------------------
# verify_delta_root structural checks
# ---------------------------------------------------------------------------

class TestVerifyDeltaRoot:
    def test_fresh_write_all_ok(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        report = verify_delta_root(tmp_path)
        assert report.all_ok, [
            f"{t.qualified_name}: {t.error}" for t in report.tables if not t.ok
        ]
        assert report.total_rows == len(_ALL_ROWS)

    def test_total_rows_correct(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        report = verify_delta_root(tmp_path)
        assert report.tables[0].row_count == len(_ALL_ROWS)

    def test_empty_root_reports_no_tables(self, tmp_path: Path) -> None:
        report = verify_delta_root(tmp_path)
        assert not report.all_ok

    def test_missing_table_dir_flagged(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        # Remove the Delta table dir.
        import shutil
        dr = read_delta_root(tmp_path)
        info = dr.tables["public.t1"]
        shutil.rmtree(info.path)

        report = verify_delta_root(tmp_path)
        # No Delta tables discoverable → all_ok is False.
        assert not report.all_ok

    def test_in_progress_classification(self, tmp_path: Path) -> None:
        """Without mark_table_complete, resume_state is 'in_progress'."""
        app_id = "mssqlbak:public.t1"
        sink = DeltaSink(tmp_path, resume=True)
        sink.open_table("public.t1", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A), checkpoint=Checkpoint(app_id, 0, "p0"))
        sink.close()
        # No finish / no mark_table_complete → in_progress.

        report = verify_delta_root(tmp_path)
        t1 = next(t for t in report.tables if t.qualified_name == "public.t1")
        assert t1.resume_state == "in_progress"

    def test_multiple_tables_all_ok(self, tmp_path: Path) -> None:
        schema2 = pa.schema([("x", pa.int64())])
        sink = DeltaSink(tmp_path)
        sink.open_table("dbo.A", _SCHEMA)
        sink.write_batch(_make_batch(_ROWS_A))
        sink.close()
        sink.open_table("dbo.B", schema2)
        sink.write_batch(pa.RecordBatch.from_arrays(
            [pa.array([7, 8], type=pa.int64())],
            schema=schema2,
        ))
        sink.close()
        sink.finish()

        report = verify_delta_root(tmp_path)
        assert report.all_ok
        assert report.total_rows == 4


# ---------------------------------------------------------------------------
# read_delta_root discovery
# ---------------------------------------------------------------------------

class TestReadDeltaRoot:
    def test_discovers_tables(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        dr = read_delta_root(tmp_path)
        assert "public.t1" in dr.tables

    def test_empty_root(self, tmp_path: Path) -> None:
        dr = read_delta_root(tmp_path)
        assert dr.tables == {}

    def test_nonexistent_root(self, tmp_path: Path) -> None:
        dr = read_delta_root(tmp_path / "nonexistent")
        assert dr.tables == {}

    def test_table_info_fields(self, tmp_path: Path) -> None:
        _write_simple(tmp_path)
        dr = read_delta_root(tmp_path)
        info = dr.tables["public.t1"]
        assert info.exists is True
        assert "public" in info.path or "t1" in info.path
        assert info.app_id == "mssqlbak:public.t1"
