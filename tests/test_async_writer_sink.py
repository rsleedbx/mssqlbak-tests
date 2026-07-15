"""Tests for AsyncWriterSink.

Covers:
- Round-trip parity: a multi-table, multi-batch workload written through
  AsyncWriterSink produces the same output as writing directly.
- Call ordering: open_table → write_batch... → close is seen in exact order.
- Exception propagation: a worker-side exception surfaces at write_batch/finish.
- Attribute delegation: wants_constraints and _sinks are readable through the wrapper.
"""
from __future__ import annotations

import threading
from typing import Any

import pyarrow as pa
import pytest

from mssqlbak.sinks.async_writer_sink import AsyncWriterSink


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _RecordingSink:
    """Sink that records every call in order for assertion."""

    wants_constraints = True

    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []
        self._lock = threading.Lock()
        self._current: str | None = None

    def open_table(self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None) -> None:
        with self._lock:
            self._current = qualified_name
            self.calls.append(("open_table", qualified_name))

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        with self._lock:
            self.calls.append(("write_batch", len(batch)))

    def close(self) -> None:
        with self._lock:
            # Tag close with the current table name for ordering assertions.
            self.calls.append(("close", self._current))
            self._current = None

    def finish(self) -> None:
        with self._lock:
            self.calls.append(("finish", None))


class _AccumulatingSink:
    """Sink that accumulates all batches per table for round-trip checks."""

    def __init__(self) -> None:
        self._current: str | None = None
        self._current_schema: pa.Schema | None = None
        self.tables: dict[str, pa.Table] = {}

    def open_table(self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None) -> None:
        self._current = qualified_name
        self._current_schema = schema
        self._batches: list[pa.RecordBatch] = []

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        self._batches.append(batch)

    def close(self) -> None:
        assert self._current is not None
        self.tables[self._current] = pa.Table.from_batches(
            self._batches, schema=self._current_schema
        )

    def finish(self) -> None:
        pass


class _BrokenSink:
    """Sink that raises on the second write_batch call."""

    def __init__(self) -> None:
        self._count = 0

    def open_table(self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None) -> None:
        pass

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        self._count += 1
        if self._count >= 2:
            raise RuntimeError("simulated sink failure")

    def close(self) -> None:
        pass

    def finish(self) -> None:
        pass


def _schema() -> pa.Schema:
    return pa.schema([("id", pa.int32()), ("val", pa.large_utf8())])


def _batch(rows: list[tuple[int, str]]) -> pa.RecordBatch:
    schema = _schema()
    return pa.RecordBatch.from_arrays(
        [pa.array([r[0] for r in rows], type=pa.int32()),
         pa.array([r[1] for r in rows], type=pa.large_utf8())],
        schema=schema,
    )


def _drive(sink: Any, tables: dict[str, list[pa.RecordBatch]]) -> None:
    """Write a set of tables to sink and call finish."""
    schema = _schema()
    for name, batches in tables.items():
        sink.open_table(name, schema)
        for b in batches:
            sink.write_batch(b)
        sink.close()
    sink.finish()


# ---------------------------------------------------------------------------
# Round-trip parity
# ---------------------------------------------------------------------------

class TestRoundTripParity:
    def test_single_table_single_batch(self) -> None:
        direct = _AccumulatingSink()
        async_s = AsyncWriterSink(_AccumulatingSink())

        rows = [(1, "a"), (2, "b"), (3, "c")]
        tables = {"public.t1": [_batch(rows)]}
        _drive(direct, tables)
        _drive(async_s, tables)

        expected = direct.tables["public.t1"].to_pydict()
        got = async_s._sink.tables["public.t1"].to_pydict()
        assert got == expected

    def test_single_table_multi_batch(self) -> None:
        async_s = AsyncWriterSink(_AccumulatingSink())
        rows_a = [(1, "a"), (2, "b")]
        rows_b = [(3, "c"), (4, "d")]
        _drive(async_s, {"public.t1": [_batch(rows_a), _batch(rows_b)]})

        tbl = async_s._sink.tables["public.t1"]
        assert tbl.column("id").to_pylist() == [1, 2, 3, 4]

    def test_multiple_tables(self) -> None:
        async_s = AsyncWriterSink(_AccumulatingSink())
        _drive(async_s, {
            "dbo.A": [_batch([(1, "x")])],
            "dbo.B": [_batch([(2, "y")])],
            "dbo.C": [_batch([(3, "z")])],
        })
        assert set(async_s._sink.tables.keys()) == {"dbo.A", "dbo.B", "dbo.C"}

    def test_empty_table(self) -> None:
        async_s = AsyncWriterSink(_AccumulatingSink())
        schema = _schema()
        async_s.open_table("public.empty", schema)
        async_s.close()
        async_s.finish()
        assert "public.empty" in async_s._sink.tables
        assert len(async_s._sink.tables["public.empty"]) == 0


# ---------------------------------------------------------------------------
# Call ordering
# ---------------------------------------------------------------------------

class TestCallOrdering:
    def test_ordering_single_table(self) -> None:
        rec = _RecordingSink()
        async_s = AsyncWriterSink(rec)
        _drive(async_s, {"t": [_batch([(1, "a")]), _batch([(2, "b")])]})

        assert rec.calls == [
            ("open_table", "t"),
            ("write_batch", 1),
            ("write_batch", 1),
            ("close", "t"),
            ("finish", None),
        ]

    def test_ordering_multiple_tables(self) -> None:
        rec = _RecordingSink()
        async_s = AsyncWriterSink(rec)
        _drive(async_s, {"A": [_batch([(1, "x")])], "B": [_batch([(2, "y")])]})

        call_names = [c[0] for c in rec.calls]
        # finish comes last
        assert call_names[-1] == "finish"
        # open_table always before close for the same table name
        open_idx = {v: i for i, (k, v) in enumerate(rec.calls) if k == "open_table"}
        close_idx = {v: i for i, (k, v) in enumerate(rec.calls) if k == "close"}
        for name in ("A", "B"):
            assert open_idx[name] < close_idx[name]


# ---------------------------------------------------------------------------
# Exception propagation
# ---------------------------------------------------------------------------

class TestExceptionPropagation:
    def test_exception_surfaces_at_write_or_finish(self) -> None:
        broken = _BrokenSink()
        async_s = AsyncWriterSink(broken, maxsize=8)

        schema = _schema()
        async_s.open_table("t", schema)
        async_s.write_batch(_batch([(1, "a")]))  # first write — ok
        # Subsequent calls will either propagate the error or finish() will.
        with pytest.raises(RuntimeError, match="simulated sink failure"):
            # Keep writing until the error surfaces.
            for _ in range(20):
                async_s.write_batch(_batch([(2, "b")]))
            async_s.close()
            async_s.finish()

    def test_finish_raises_on_worker_error(self) -> None:
        """Even if writes don't re-raise, finish() must raise the worker error."""
        class _LateFailSink:
            def open_table(self, *a: Any, **kw: Any) -> None: pass
            def write_batch(self, *a: Any, **kw: Any) -> None: pass
            def close(self) -> None: raise ValueError("close failure")
            def finish(self) -> None: pass

        async_s = AsyncWriterSink(_LateFailSink(), maxsize=8)
        async_s.open_table("t", _schema())
        async_s.write_batch(_batch([(1, "x")]))
        async_s.close()  # enqueued — error happens in worker

        with pytest.raises((ValueError, Exception)):
            async_s.finish()


# ---------------------------------------------------------------------------
# Attribute delegation
# ---------------------------------------------------------------------------

class TestAttributeDelegation:
    def test_wants_constraints_delegated(self) -> None:
        rec = _RecordingSink()
        async_s = AsyncWriterSink(rec)
        assert async_s.wants_constraints is True

    def test_sinks_attribute_delegated(self) -> None:
        from mssqlbak.sink import MultiSink

        rec = _RecordingSink()
        multi = MultiSink(rec)
        async_s = AsyncWriterSink(multi)
        # _sink_wants_ddl reads ._sinks on the wrapped MultiSink via __getattr__
        assert hasattr(async_s, "_sinks")
        assert async_s._sinks == [rec]

    def test_wrapped_sink_accessible(self) -> None:
        rec = _RecordingSink()
        async_s = AsyncWriterSink(rec)
        assert async_s._sink is rec
