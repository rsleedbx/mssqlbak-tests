# Quality attributes

How the decoder is designed against seven quality dimensions.

---

## Performance

**Chosen approach:** Rust native extensions for all hot-path operations;
narrow numpy use for columnstore bitpack; streaming Arrow batches; mmap +
LRU chunk cache for page access; optional threading for Delta write.

**Rust hot paths** (`rust/src/`):
- XPRESS LZ77+Huffman decompress — by far the most CPU-intensive operation on
  a large `WITH COMPRESSION` backup.
- Page → columnar value decode (`decode_page_to_columns`,
  `decode_compressed_page_to_columns`).
- SCSU Unicode expand (`scsu_expand`).
- LOB chain stitch (`stitch_lob`, `stitch_lob_images`, `stitch_text_ptr`).
- Columnstore segment decode inner loop (`decode_cs_segment`).

**numpy** is used only in `columnstore/decode/bitpack.py` (FOR + bit-unpack)
and `columnstore/decode/dict_numeric.py` (dictionary gather).  It is not used
in the rowstore or XTP paths where the overhead of array construction exceeds
the gain.

**Lazy decompression + LRU cache** (`pages.py: LazyPageStore`) — XPRESS
extents are decompressed on first page access and held in a bounded LRU cache.
The cache size is auto-tuned by `_memcap.py` based on available RAM.

**mmap** — used in `bak_io.py`, `pages.py`, `mtf.py`, `compressed.py`,
`rows.py`, `chunk_index.py`, `logtail.py`, `bacpac.py` to avoid kernel copies
for local file access.

**Threading** — `extract.py` uses a `ThreadPoolExecutor` for parallel
per-table extraction.  Because most decode work is GIL-bound (Python +
pyarrow), threading only helps when the Delta sink (Rust, GIL-released) can
overlap I/O with decode on an adjacent table.  The default is `workers=1`
(serial); thread count is opt-in via `MSSQLBAK_VERIFY_THREADS`.

**HTTP coalescing** — when reading from a remote URL, adjacent chunk-cache
misses are coalesced into a single range request (`pages.py`).

See [`docs/PERFORMANCE_PLAN.md`](../PERFORMANCE_PLAN.md) for benchmark targets
and measurement methodology.

**Tradeoff:** Rust hot paths introduce build complexity (maturin, abi3 wheel).
The Python fallbacks ensure correctness but are not intended to be fast; they
exist as safety nets and executable specs.

---

## Simplicity

**Chosen approach:** Clear Python for all paths where the binary format logic
is the complexity; native code only where a profiled hot path justifies it.

No broad numpy or pandas pipeline was introduced.  Column decode is done
value-by-value in Python (via `types.py` dispatch) except for the CCI bitpack
path where the array construction cost is dominated by the volume of values per
segment (potentially millions per column).

The Rust layer covers exactly the operations that are CPU-bound and well-defined
at the byte level.  Complex branching logic (catalog bootstrap, LOB topology
traversal, XTP completeness gating, log-tail LSN gating) remains in Python.

**Tradeoff:** Two implementations of each hot path (Rust + Python) must be
kept consistent.  `xpress.py` enforces this explicitly by raising
`XpressPythonFallbackError` at runtime, preventing the slower path from running
silently.

---

## Readability

**Chosen approach:** Modular package structure with one clear job per module;
format algorithms documented in `docs/spec/`; Python kept as readable reference
for all format logic.

- `mssqlbak/columnstore/` was split from a monolithic `columnstore.py` into
  `storage/`, `decode/`, and `assembly/` sub-packages, each with one
  responsibility.
- `mssqlbak/xpress.py` is kept even though its runtime use is disabled; it
  serves as a line-for-line Python translation of the MS-XCA decode loop for
  readers without a Rust toolchain.
- [`docs/spec/`](../spec/00_MASTER.md) is the normative byte-layout reference.
  Code comments cross-reference spec section numbers rather than duplicating
  offset tables inline.

**Tradeoff:** The dual Rust/Python implementation means two files to read for
any given operation.  The Python file is the spec; the Rust file is the
performance implementation.

---

## Scalability

**Chosen approach:** Streaming generators end-to-end; no full table
materialization; lazy decompression index; per-table LOB memory cap.

- All decode paths (`rows.py`, `columnstore/assembly/reader.py`, `xtp.py`)
  are Python generators.  `extract.py` drives them in a fixed-batch loop:
  rows are collected into an Arrow `RecordBatch`, written to the sink, and
  released before the next batch.
- `chunk_index.py` holds only a decompression index (offsets + sizes), not
  decompressed data.  Extents are inflated on demand and evicted by the LRU
  when the cache limit is reached.
- `_memcap.py` auto-detects available RAM and sets the LOB blob memory limit
  accordingly.  When the limit is reached, LOB data spills to a temporary
  buffer instead of accumulating in RAM.
- HTTP coalescing (`pages.py`) amortizes round-trip overhead for remote backups
  without requiring the full file to be downloaded first.

**Tradeoff:** Generator-based streaming means the decode path cannot random-
access rows by index.  Column-at-a-time vectorization (as in a true column-
oriented database) is not possible outside the CCI segment decode path.

---

## Availability

**Chosen approach:** Resilient per-table skip; `ExtractReport`; multiple I/O
backends; no hard runtime requirements beyond pyarrow + deltalake.

- `extract.py` wraps each table extraction in a try/except.  A table that
  raises an unhandled decode error is recorded in `ExtractReport` as `FAILED`
  and the extract continues with the next table.
- `ExtractReport` collects every table's outcome (extracted, skipped, failed,
  row count) and is returned to the caller; `--verbose` logging surfaces which
  tables were skipped and why.
- I/O backends: `bak_io.py` + `readers/` support local file, HTTP/HTTPS, S3,
  GCS, and Azure Blob Storage, so the backup does not need to be locally
  accessible.
- `mssql_python` (live SQL Server restore) is an optional extra; the decode
  path has no dependency on a running SQL Server instance.

**Tradeoff:** Per-table resilience means a silent decode bug can produce a
partially correct extract without surfacing as a top-level error.  The
`confidence.py` checks and `MSSQLBAK_DECODE_TRACE` are the primary mechanisms
for detecting this.

---

## Observability

**Chosen approach:** Structured logger; progress callbacks; opt-in decode
trace; offline confidence checks.

**Logging** (`mssqlbak/_log.py`):
- `logging.getLogger("mssqlbak")` with a `NullHandler` — silent by default,
  no output unless the caller opts in.
- `enable_logging()` attaches a stderr handler with `%(relativeCreated)8.0fms`
  timestamps.  Exposed via `--verbose` in the CLI.
- Log messages at the INFO level cover: container format detection, per-table
  start/done, alloc unit counts, page counts, batch writes, and timing.

**Progress callbacks** (`extract.py:259–266`):
- `on_progress(event, payload)` is called for `loading`, `loaded`, `schema`,
  `table_start`, `table_done`, and `table_skip` events.
- `on_pct(pct)` is called from `pages.py` and `compressed.py` as pages are
  read.

**Decode trace** (`mssqlbak/decode_trace.py`):
- Enabled via `MSSQLBAK_DECODE_TRACE=1`.
- Records which decode branches were exercised per table (encoding variants,
  fallback paths, LOB topology).
- Zero overhead when disabled (the trace context is a no-op).

**Offline confidence checks** (`mssqlbak/confidence.py`):
- After extraction, checks decoded Arrow output against metadata embedded in
  the `.bak` (row count bounds, type range constraints, null contract, CCI
  segment bounds, B-tree key ordering).
- All checks are read-only and side-effect-free.

**Tradeoff:** There is no Databricks-style structured event log or metrics bus.
Observability is push-based (callbacks, logging) rather than pull-based
(metrics endpoint, event table).  For pipeline integration, the caller is
responsible for forwarding `on_progress` events to its own telemetry system.

---

## Idempotency

**Chosen approach:** The decode function is a pure function of the `.bak`
bytes; sink write semantics are configured at the sink layer, not the decoder.

- `extract_bak(path, sink, ...)` reads from the `.bak` and writes to `sink`.
  Given the same `.bak` and the same `sink` configuration, it produces the
  same output every time.
- The decoder holds no mutable state between calls.  `LazyPageStore` and the
  LRU cache are created fresh per extraction.
- `DeltaSink` supports both overwrite (`mode="overwrite"`) and append
  (`mode="append"`); the choice is a sink-level configuration, not a decoder
  concern.
- `confidence.py` checks are fully side-effect-free: they read the extracted
  Arrow table and the original `.bak` metadata and produce a report.

**Tradeoff:** Delta `mode="append"` is not idempotent — re-running appends
duplicate rows.  Callers that require idempotency must use `mode="overwrite"`
or implement their own deduplication at the sink layer.
