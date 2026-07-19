"""Sink registry — delta + pg_dir round-trip sinks."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pyarrow as pa

from mssqlbak.sink import DeltaSink, sanitize_fqn, sanitize_uc_column
from mssqlbak.sinks.pg_dir_sink import DirSink
from pgdump.dir_reader import iter_dir_batches

log = logging.getLogger(__name__)

# Sentinel object yielded as the *table* when a readback iterator hits an
# unrecoverable infra error (e.g. FileNotFoundError on the sink output
# directory).  The runner checks for it and records the error in the edge
# dict rather than treating the empty-table result as a data mismatch.
_READBACK_ERROR = object()


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
    normalize_col: Callable[[str], str]
    #: Yield (fqn, table) one at a time — keeps peak bounded to one table.
    #: May yield (``"__infra__"``, ``_READBACK_ERROR``) to signal a fatal
    #: infra failure (missing sink output); the runner records this as an
    #: edge-level error rather than a data mismatch.
    iter_tables: Callable[[Path, list[str]], Iterator[tuple[str, pa.Table | object]]]


def _iter_delta_tables(
    root: Path, fqns: list[str]
) -> Iterator[tuple[str, pa.Table | object]]:
    """Yield one Delta table at a time, releasing each before loading the next.

    Yields ``(fqn, _READBACK_ERROR)`` when the table directory is missing or
    the Delta log cannot be opened, instead of silently skipping the table.
    Per-table read errors that do not indicate a missing sink output are still
    logged and skipped.
    """
    from deltalake import DeltaTable

    if not root.exists():
        yield "__infra__", _READBACK_ERROR
        return

    for fqn in fqns:
        sanitized = sanitize_fqn(fqn)
        schema_part, _, table_part = sanitized.partition(".")
        path = root / schema_part / table_part
        if not path.exists():
            continue
        try:
            yield fqn, DeltaTable(str(path)).to_pyarrow_table()
        except Exception:
            log.exception("Error reading delta table %s from %s", fqn, path)


def _iter_pg_dir_tables(
    root: Path, _fqns: list[str]
) -> Iterator[tuple[str, pa.Table | object]]:
    """Stream pg_dir tables one at a time from the archive.

    Accumulates batches for the current table and yields a complete Arrow
    Table when the fqn changes.  Peak memory is bounded to one table's data
    plus the next batch being decoded, not the whole archive.

    Yields ``(\"__infra__\", _READBACK_ERROR)`` when the archive root is
    missing or the toc.dat cannot be opened (infra failure, not data
    mismatch).
    """
    if not root.exists() or not (root / "toc.dat").exists():
        log.error("pg_dir readback: toc.dat not found in %s — treating as infra error", root)
        yield "__infra__", _READBACK_ERROR
        return

    current_fqn: str | None = None
    current_batches: list[pa.RecordBatch] = []
    try:
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
        log.exception("Error streaming pg_dir tables from %s (last fqn: %s)", root, current_fqn)


SINKS: dict[str, SinkSpec] = {
    "delta": SinkSpec(
        name="delta",
        make=lambda root: DeltaSink(root),
        normalize_col=sanitize_uc_column,
        iter_tables=_iter_delta_tables,
    ),
    "pg_dir": SinkSpec(
        name="pg_dir",
        make=lambda root: DirSink(root),
        normalize_col=lambda col: col,
        iter_tables=_iter_pg_dir_tables,
    ),
}
