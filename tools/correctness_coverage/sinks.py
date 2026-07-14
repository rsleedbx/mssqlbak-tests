"""Sink registry — delta + pg_dir round-trip sinks."""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pyarrow as pa

from mssqlbak.sink import DeltaSink, sanitize_uc_column, sanitize_uc_id
from mssqlbak.sinks.pg_dir_sink import DirSink
from pgdump.dir_reader import iter_dir_batches, read_dir_tables


class _TimingSink:
    """Wraps a real sink, accumulating wall time spent inside its own calls.

    Used by _run_one to estimate per-sink write time when multiple sinks are
    driven by a single MultiSink pass.  Because all sinks share the single
    extract pass the measurement is a best-effort estimate consistent with the
    coarse perf_counter approach used elsewhere in this module.
    """

    def __init__(self, sink: Any) -> None:
        self._sink = sink
        self._elapsed: float = 0.0

    @property
    def elapsed_s(self) -> float:
        return round(self._elapsed, 3)

    def open_table(
        self, qualified_name: str, schema: pa.Schema, *, constraints: Any = None
    ) -> None:
        t0 = time.perf_counter()
        self._sink.open_table(qualified_name, schema, constraints=constraints)
        self._elapsed += time.perf_counter() - t0

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        t0 = time.perf_counter()
        self._sink.write_batch(batch, checkpoint=checkpoint)
        self._elapsed += time.perf_counter() - t0

    def close(self) -> None:
        t0 = time.perf_counter()
        self._sink.close()
        self._elapsed += time.perf_counter() - t0

    def finish(self) -> None:
        t0 = time.perf_counter()
        finish = getattr(self._sink, "finish", None)
        if callable(finish):
            finish()
        self._elapsed += time.perf_counter() - t0


@dataclass(frozen=True)
class SinkSpec:
    """Registry entry for a round-trip sink."""

    name: str
    make: Callable[[Path], Any]
    read_back: Callable[[Path, list[str]], dict[str, pa.Table]]
    normalize_col: Callable[[str], str]
    #: Yield (fqn, table) one at a time — keeps peak bounded to one table.
    iter_tables: Callable[[Path, list[str]], Iterator[tuple[str, pa.Table]]]


def _read_delta(root: Path, fqns: list[str]) -> dict[str, pa.Table]:
    from deltalake import DeltaTable

    result: dict[str, pa.Table] = {}
    for fqn in fqns:
        schema_name, _, table_name = fqn.partition(".")
        path = root / sanitize_uc_id(schema_name) / sanitize_uc_id(table_name)
        if not path.exists():
            continue
        try:
            result[fqn] = DeltaTable(str(path)).to_pyarrow_table()
        except Exception:
            pass
    return result


def _iter_delta_tables(root: Path, fqns: list[str]) -> Iterator[tuple[str, pa.Table]]:
    """Yield one Delta table at a time, releasing each before loading the next."""
    from deltalake import DeltaTable

    for fqn in fqns:
        schema_name, _, table_name = fqn.partition(".")
        path = root / sanitize_uc_id(schema_name) / sanitize_uc_id(table_name)
        if not path.exists():
            continue
        try:
            yield fqn, DeltaTable(str(path)).to_pyarrow_table()
        except Exception:
            pass


def _read_pg_dir(root: Path, _fqns: list[str]) -> dict[str, pa.Table]:
    try:
        return read_dir_tables(root)
    except Exception:
        return {}


def _iter_pg_dir_tables(root: Path, _fqns: list[str]) -> Iterator[tuple[str, pa.Table]]:
    """Stream pg_dir tables one at a time from the archive.

    Accumulates batches for the current table and yields a complete Arrow
    Table when the fqn changes.  Peak memory is bounded to one table's data
    plus the next batch being decoded, not the whole archive.
    """
    try:
        current_fqn: str | None = None
        current_batches: list[pa.RecordBatch] = []
        for qname, batch in iter_dir_batches(root):
            if qname != current_fqn:
                if current_fqn is not None and current_batches:
                    yield current_fqn, pa.Table.from_batches(current_batches)
                    current_batches = []
                current_fqn = qname
            current_batches.append(batch)
        if current_fqn is not None and current_batches:
            yield current_fqn, pa.Table.from_batches(current_batches)
    except Exception:
        pass


SINKS: dict[str, SinkSpec] = {
    "delta": SinkSpec(
        name="delta",
        make=lambda root: DeltaSink(root),
        read_back=_read_delta,
        normalize_col=sanitize_uc_column,
        iter_tables=_iter_delta_tables,
    ),
    "pg_dir": SinkSpec(
        name="pg_dir",
        make=lambda root: DirSink(root),
        read_back=_read_pg_dir,
        normalize_col=lambda col: col,
        iter_tables=_iter_pg_dir_tables,
    ),
}
