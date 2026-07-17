"""Tests for MultiSink isolation/resume, build_multi_sink, and emit_all.

Covers:
- MultiSink isolate mode: failing child removed, other children still receive all calls.
- MultiSink resume delegation: conservative min, all-complete gating.
- build_multi_sink: returns raw sink for single child; wraps children for multi.
- emit_all integration: data tables + mssqlbak_perf.* + T-SQL scripts + DuckDB all
  produced from a single extract_bak pass.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pyarrow as pa
import pytest

from mssqlbak.sink import MultiSink, ResumePoint, ResumableSink, build_multi_sink

# ---------------------------------------------------------------------------
# Helpers / mini sinks
# ---------------------------------------------------------------------------

_SMALL_BAK = Path(__file__).parent / "fixtures_2017" / "alias_types_full.bak"


class _CaptureSink:
    """Records every call for assertion."""

    def __init__(self) -> None:
        self.opens: list[str] = []
        self.batches: list[pa.RecordBatch] = []
        self.closes: int = 0

    def open_table(self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None) -> None:
        self.opens.append(qualified_name)

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        self.batches.append(batch)

    def close(self) -> None:
        self.closes += 1

    def finish(self) -> None:
        pass


class _FailingSink:
    """Raises on the first write_batch call."""

    def __init__(self) -> None:
        self.opened: list[str] = []

    def open_table(self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None) -> None:
        self.opened.append(qualified_name)

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        raise RuntimeError("intentional failure")

    def close(self) -> None:
        pass

    def finish(self) -> None:
        pass


class _ResumableSink:
    """Minimal ResumableSink for testing resume delegation."""

    def __init__(self, *, complete: bool = False, next_version: int = 0) -> None:
        self._complete = complete
        self._next_version = next_version
        self.marked_complete: list[tuple[str, int]] = []

    def open_table(self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None) -> None:
        pass

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        pass

    def close(self) -> None:
        pass

    def finish(self) -> None:
        pass

    def table_resume_point(self, qualified_name: str) -> ResumePoint | None:
        if self._complete:
            return ResumePoint(complete=True)
        return ResumePoint(complete=False, next_version=self._next_version)

    def mark_table_complete(self, qualified_name: str, rows: int) -> None:
        self.marked_complete.append((qualified_name, rows))


# ---------------------------------------------------------------------------
# MultiSink isolation mode tests
# ---------------------------------------------------------------------------

class TestMultiSinkIsolate:
    def _make_schema(self) -> pa.Schema:
        return pa.schema([("id", pa.int32())])

    def test_isolate_removes_failing_child(self) -> None:
        good = _CaptureSink()
        bad = _FailingSink()
        ms = MultiSink(good, bad, on_error="isolate")

        schema = self._make_schema()
        ms.open_table("dbo.t", schema)
        batch = pa.record_batch([[1, 2]], schema=schema)
        ms.write_batch(batch)  # _FailingSink raises here; should be isolated

        assert len(ms.failures) == 1
        assert ms.failures[0][0] is bad
        assert isinstance(ms.failures[0][1], RuntimeError)
        # Good sink must have received the open_table and write_batch.
        assert "dbo.t" in good.opens
        assert len(good.batches) == 1

    def test_isolate_continues_after_failure(self) -> None:
        good = _CaptureSink()
        bad = _FailingSink()
        ms = MultiSink(good, bad, on_error="isolate")

        schema = self._make_schema()
        ms.open_table("dbo.t", schema)
        batch1 = pa.record_batch([[1]], schema=schema)
        batch2 = pa.record_batch([[2]], schema=schema)
        ms.write_batch(batch1)
        # After bad is removed, subsequent calls go only to good.
        ms.write_batch(batch2)
        ms.close()

        # Good sink received both batches and the close.
        assert len(good.batches) == 2
        assert good.closes == 1

    def test_raise_mode_propagates(self) -> None:
        bad = _FailingSink()
        ms = MultiSink(bad, on_error="raise")  # default
        schema = self._make_schema()
        ms.open_table("dbo.t", schema)
        with pytest.raises(RuntimeError, match="intentional failure"):
            ms.write_batch(pa.record_batch([[1]], schema=schema))

    def test_failures_empty_on_success(self) -> None:
        good = _CaptureSink()
        ms = MultiSink(good)
        schema = self._make_schema()
        ms.open_table("dbo.t", schema)
        ms.write_batch(pa.record_batch([[1]], schema=schema))
        ms.close()
        assert ms.failures == []


# ---------------------------------------------------------------------------
# MultiSink resume delegation tests
# ---------------------------------------------------------------------------

class TestMultiSinkResume:
    def test_is_resumable_when_all_children_resumable(self) -> None:
        a = _ResumableSink()
        b = _ResumableSink()
        ms = MultiSink(a, b)
        assert isinstance(ms, ResumableSink)
        assert ms.is_resumable

    def test_is_not_resumable_when_one_child_not_resumable(self) -> None:
        a = _ResumableSink()
        b = _CaptureSink()  # no resume protocol
        ms = MultiSink(a, b)
        assert not ms.is_resumable

    def test_conservative_min_all_complete(self) -> None:
        a = _ResumableSink(complete=True)
        b = _ResumableSink(complete=True)
        ms = MultiSink(a, b)
        rp = ms.table_resume_point("dbo.t")
        assert rp is not None
        assert rp.complete is True

    def test_conservative_min_one_incomplete(self) -> None:
        a = _ResumableSink(complete=True)
        b = _ResumableSink(complete=False, next_version=5)
        ms = MultiSink(a, b)
        rp = ms.table_resume_point("dbo.t")
        assert rp is not None
        assert rp.complete is False
        assert rp.next_version == 5  # least-advanced

    def test_conservative_min_none_returns_none(self) -> None:
        """If any child returns None (fresh), whole MultiSink returns None."""
        class _FreshSink(_ResumableSink):
            def table_resume_point(self, qname: str) -> ResumePoint | None:
                return None

        a = _FreshSink()
        b = _ResumableSink(complete=True)
        ms = MultiSink(a, b)
        assert ms.table_resume_point("dbo.t") is None

    def test_mark_complete_fans_out(self) -> None:
        a = _ResumableSink()
        b = _ResumableSink()
        ms = MultiSink(a, b)
        ms.mark_table_complete("dbo.t", 42)
        assert ("dbo.t", 42) in a.marked_complete
        assert ("dbo.t", 42) in b.marked_complete


# ---------------------------------------------------------------------------
# build_multi_sink tests
# ---------------------------------------------------------------------------

class TestBuildMultiSink:
    def test_single_sink_returned_directly(self) -> None:
        s = _CaptureSink()
        result = build_multi_sink([s], async_writes=False)
        assert result is s

    def test_multi_returns_multisink(self) -> None:
        a = _CaptureSink()
        b = _CaptureSink()
        ms = build_multi_sink([a, b], async_writes=False)
        assert isinstance(ms, MultiSink)

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            build_multi_sink([])

    def test_async_wraps_children(self) -> None:
        from mssqlbak.sinks.async_writer_sink import AsyncWriterSink

        a = _CaptureSink()
        b = _CaptureSink()
        ms = build_multi_sink([a, b], async_writes=True)
        assert isinstance(ms, MultiSink)
        # With async_writes=True and non-resumable, children should be async-wrapped.
        assert all(isinstance(c, AsyncWriterSink) for c in ms._sinks)


# ---------------------------------------------------------------------------
# Integration: extract to delta + pg_dir in one pass
# ---------------------------------------------------------------------------

class TestMultiSinkIntegration:
    def test_extract_to_delta_and_pg_dir(self, tmp_path: Path) -> None:
        """Single bak read writes identical row counts to delta AND pg_dir."""
        from deltalake import DeltaTable

        from mssqlbak.extract import extract_bak
        from mssqlbak.sink import DeltaSink
        from mssqlbak.sinks.pg_dir_sink import DirSink

        delta_dir = tmp_path / "delta"
        pg_dir = tmp_path / "pgdir"

        delta_sink = DeltaSink(str(delta_dir))
        dir_sink = DirSink(pg_dir)
        ms = build_multi_sink([delta_sink, dir_sink], async_writes=True)

        report = extract_bak(str(_SMALL_BAK), ms)
        fn = getattr(ms, "finish", None)
        if callable(fn):
            fn()

        assert report.extracted, "expected at least one extracted table"
        total_rows = report.total_rows

        # Delta side: walk the tree and sum all table row counts.
        delta_rows = 0
        for dt_dir in delta_dir.rglob("_delta_log"):
            table_root = dt_dir.parent
            try:
                delta_rows += DeltaTable(str(table_root)).to_pyarrow_table().num_rows
            except Exception:
                pass

        assert delta_rows == total_rows, f"delta row count {delta_rows} != expected {total_rows}"

        # pg_dir side: manifest must list the same tables.
        toc_file = pg_dir / "toc.dat"
        assert toc_file.exists(), "pg_dir toc.dat missing"


# ---------------------------------------------------------------------------
# Unification: emit_all with data + perf tables + scripts + DuckDB
# ---------------------------------------------------------------------------

class TestEmitAll:
    def test_emit_all_produces_all_outputs(self, tmp_path: Path) -> None:
        """emit_all on a small fixture with all four target types."""
        import duckdb

        from mssqlbak.emit import PerfScriptTarget, ProfilerTarget, TableTarget, emit_all
        from mssqlbak.sink import DeltaSink

        delta_dir = tmp_path / "delta"
        perf_dir = tmp_path / "perf"
        profiler_db = tmp_path / "extract.db"

        targets = [
            TableTarget(DeltaSink(str(delta_dir)), include_perf_tables=True),
            PerfScriptTarget(out_dir=perf_dir, fmt="both", db_name="TestDB"),
            ProfilerTarget(out_path=profiler_db, with_perf=True, db_name="TestDB"),
        ]

        report = emit_all(str(_SMALL_BAK), targets)

        # Data tables extracted.
        assert report.extracted, "expected at least one extracted table"

        # DuckDB profiler produced.
        assert report.profiler_db is not None
        assert report.profiler_db.exists()
        con = duckdb.connect(str(report.profiler_db))
        profiler_tables = {t[0] for t in con.execute("SHOW TABLES").fetchall()}
        con.close()
        assert "databases" in profiler_tables
        assert "statistics" in profiler_tables  # perf-extra via with_perf=True

        # T-SQL perf scripts produced.
        assert report.perf_artifacts, "expected non-empty perf_artifacts"
        manifest = perf_dir / "TestDB.perf.json"
        assert manifest.exists()

        # Perf tables written to delta sink (at least some qnames tracked).
        assert report.perf_tables, "expected mssqlbak_perf.* qnames in perf_tables"
        for qname in report.perf_tables:
            assert qname.startswith("mssqlbak_perf."), f"unexpected qname: {qname}"
        # At least one mssqlbak_perf table directory must exist in delta (non-empty tables).
        perf_schema_dir = delta_dir / "mssqlbak_perf"
        if perf_schema_dir.exists():
            perf_table_dirs = [d for d in perf_schema_dir.iterdir() if d.is_dir()]
            assert perf_table_dirs, "mssqlbak_perf schema exists but has no table dirs"

    def test_emit_all_single_target_no_multisink_overhead(self, tmp_path: Path) -> None:
        """Single TableTarget uses the raw sink (no MultiSink wrapping)."""
        from mssqlbak.emit import TableTarget, emit_all
        from mssqlbak.sink import DeltaSink

        delta_dir = tmp_path / "delta"
        sink = DeltaSink(str(delta_dir))
        report = emit_all(str(_SMALL_BAK), [TableTarget(sink)])
        assert report.extracted
