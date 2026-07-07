# Performance Improvement Plan

Target deployment: `.bak` files read from object storage (S3 / Azure Blob / GCS), Delta Lake sink
written to the same or a second object storage bucket.

## Throughput history (AdventureWorks samples, local disk, Apple M-series)

| Backup format | Rows | Time | Rows/sec | Notes |
|---|---|---|---|---|
| Uncompressed — v1 baseline | 760,837 | ~21.5 s | ~35,000 | Python path, BATCH=10k |
| MSSQLBAK compressed — v1 baseline | 760,810 | ~65 s | ~11,300 | Python XPRESS, BATCH=10k |
| Uncompressed — after Rust XPRESS | 760,837 | ~11.5 s | ~66,000 | native `xpress_lz77` |
| MSSQLBAK compressed — after Rust XPRESS | 760,810 | ~15 s | ~51,000 | native XPRESS |
| Uncompressed — after P3+P4 | 760,837 | ~10.7 s | ~71,000 | col accumulator, BATCH=100k |
| MSSQLBAK compressed — after P3+P4 | 760,810 | ~13.7 s | ~55,000 | col accumulator, BATCH=100k |
| Uncompressed OLTP (with XML tables) — Rust page decode | 760,837 | ~3.4 s | ~223,000 | `decode_page_to_columns` |
| MSSQLBAK compressed (with XML tables) — Rust page decode | 760,810 | ~4.0 s | ~190,000 | Rust decode + Rust XPRESS |
| DW uncompressed (no XML/CLR_UDT) — Rust page decode | 1,060,820 | ~1.1 s | ~932,000 | 100% Rust path |
| Uncompressed OLTP — CLR_UDT mixed + GIL-release + workers=2 | 760,837 | ~2.6 s | ~296,000 | CLR moved to Rust, threads |
| DW uncompressed — CLR_UDT mixed + GIL-release + workers=2 | 1,060,820 | ~1.1 s | ~932,000 | unchanged (was already 100% Rust) |
| WWI-Full page-compressed archive — after P6 Rust CD decoder | 3,654,736 | ~11.8 s | ~309,000 | `decode_compressed_page_to_columns` |
| WWI-Full total — after P6 | 4,411,164 | ~30 s | ~147,000 | was 66 s; 2.2× overall |
| AdventureWorksDW (ROW/PAGE compressed, NVARCHAR) — after P8c | 1,060,805 | ~1.5 s | ~721,000 | SCSU in Rust; was P6 path |
| StackOverflowMini.Comments (LOB NVARCHAR) — after P8a | 1,373,756 | ~3.4 s | ~404,000 | was 53 s; **15.6×** |
| StackOverflowMini.Posts (LOB NVARCHAR, large body) — after P8a | 1,565,425 | ~19.9 s | ~78,700 | was 284 s; **14.3×** |
| StackOverflowMini total — after P8a | 8,097,337 | ~46 s | ~175,000 | was ~361 s; **7.8×** |
| AdventureWorks2019 Person (XML columns) — after P9a+P9b | 19,972 | ~1.1–1.2 s | ~16,000–17,700 | XML: Rust page decode + Rust LOB stitch + Python decode_xml |

**Net improvement from v1 baseline:**
- Simple schemas (DW-class): **26×** (35k → 932k rows/sec)
- Compressed DW (NVARCHAR) — P8c: **64×** (11k → 721k rows/sec)
- OLTP with XML/LOB columns: **8×** (35k → 296k rows/sec) — CLR_UDT mixed + GIL-release + threads
- OLTP with XML/LOB columns (serial): **7×** (35k → 249k rows/sec)
- Compressed: **17×** (11k → 190k rows/sec)
- Page-compressed archive tables (WWI-class): **5×** (60k → 309k rows/sec) via P6 Rust CD decoder
- LOB NVARCHAR tables (StackOverflow-class) — P8a: **15×** (25k → 404k for Comments); Posts 5.5k → 78k (P8a+P6)
- XML OLTP tables (AW2019 Person-class) — P9a+P9b: ~25% improvement over full-Python fallback

---

## Pipeline stages

```
object storage read
        ↓
MSSQLBAK XPRESS decompress        ← Rust (xpress_lz77); ~2–3× vs Python baseline
        ↓
page assembly into PageStore      ← serial; must complete before row extraction
        ↓
schema recovery (once)
        ↓
per-table row decode              ← Rust (decode_page_to_columns / decode_compressed_page_to_columns)
                                    XML returns raw bytes (mixed path, P9a)
                                    Python fallback for TEXT/NTEXT/IMAGE, SQL_VARIANT
        ↓
off-row LOB stitching (if needed) ← Rust stitch_lob_images (P9b, zero Python callbacks)
                                    via ImageStore (PyBuffer lock on mmap); used for XML
                                    in _redecode_mixed_cols and for TEXT/NTEXT/IMAGE in
                                    read_table_rows. Falls back to stitch_lob/stitch_text_ptr
                                    (P8a) with Python page_reader for LazyPageStore sources.
        ↓
SCSU → UTF-8 decode (NVARCHAR)    ← Rust scsu_to_utf8 (P8c) called inside page decoder
                                    and LOB stitcher; Python scsu.expand() fallback kept
        ↓
Arrow batch build                 ← per-column accumulator (_col_coerce_fn); no dict pivot
        ↓
Delta write (sink)                ← BATCH=100,000 rows per write_deltalake() call
```

Table extraction runs in parallel via `ThreadPoolExecutor` (P5). `PageStore` reads are
read-only after construction and are safe to share across threads.

With object storage as the source, the download + decompress stage gates everything.
No table extraction begins until the full PageStore is assembled.

---

## Improvements

### P1 — Native XPRESS decompression (implemented)

**Done:** XPRESS decompression is handled by `lz77_huffman_decompress_py` and
`lz77_huffman_decompress_until_input_py` in the in-house `xpress_lz77` Rust crate
(`rust/src/xpress_lz77_huffman.rs`).  The pure-Python fallback in `mssqlbak/xpress.py`
is retained for environments where the wheel is unavailable.

Implementation and evaluation history (library comparisons, fork fixes) is in
`docs/XPRESS_IMPL_HISTORY.md`.

---

### P2 — Stream decompress pipeline (implemented)

**Status:** Implemented.

**What was built:**

`PageStore.from_bak()` and `extract_bak()` / `extract_bak_to_delta()` now accept any
`BakReader` (S3, Azure Blob, GCS) directly in addition to local file paths.  When a
cloud reader is supplied the pipeline uses `LazyPageStore` backed by a chunk index:

1. **Index pass** — one sequential forward scan builds a `ChunkIndex` (catalog pages
   stored verbatim, non-catalog pages discarded after recording their chunk offset and
   length).  This is the same elapsed time as the old "loading" phase but uses on-demand
   HTTP range GETs instead of an upfront full download.
2. **On-demand extraction** — schema recovery fetches only catalog-page extents; each
   table's row decode fetches only the extents that contain that table's pages.  For
   selective extraction (a single large table) this avoids downloading the entire file.
3. **Block-buffered `_ReaderBuffer`** — the sequential scanner downloads data in 1 MiB
   blocks and serves byte and slice requests from the cached block.  A 10 GB backup with
   ~40 KB average chunk size triggers ~10,000 HTTP GETs instead of hundreds of millions
   of single-byte reads.

**Pre-existing bug fixed:** `struct.unpack_from("<I", buf, offset)` requires the Python
buffer protocol, which `_ReaderBuffer` does not implement.  All affected call sites
(`_is_record_header`, `_iter_chunks_with_pages`) were changed to
`struct.unpack("<I", buf[offset : offset + 4])`, which works for `bytes`, `mmap`, and
`_ReaderBuffer` alike.

**Usage — object storage:**

```python
from mssqlbak.readers.s3 import S3BakReader
from mssqlbak.extract import extract_bak_to_delta

with S3BakReader(bucket="my-bucket", key="backups/prod.bak") as reader:
    report = extract_bak_to_delta(reader, out="/tmp/delta")

# Or with on_progress and explicit workers:
with S3BakReader(bucket="my-bucket", key="backups/prod.bak") as reader:
    report = extract_bak(reader, sink=DeltaSink("/tmp/delta"), workers=4)
```

**Gain for full extraction:** The index pass still reads the full file sequentially, so
total data transfer for a complete extraction is unchanged.  The benefit is that
**no temp file or full in-memory download is needed** before the first row is available.
For selective extraction (one table out of many) only the relevant extents are fetched,
potentially reducing data transfer significantly.

**Parallelism scope (unchanged from P5 table):** `.bak` download / XPRESS demux into
the chunk index is serial.  Workers only parallelise row decode and Delta writes.

---

### P3 — Column accumulator in `_to_batch` (implemented)

**Was:** `extract.py:_to_batch()` received a `list[dict]` of rows and pivoted them
column-major for Arrow — one O(rows × cols) pass plus a full `list[dict]` allocation per batch.

**Done:** `_col_coerce_fn` builds a per-column coerce callable at table-open time.  The
extract loop appends directly into per-column `list`s; no intermediate dict is built.
`pa.array()` is called once per column per batch from the pre-typed accumulator.

**Scope:** `mssqlbak/extract.py` — `_col_coerce_fn`, `_try_extract_table_rust`,
`_try_extract_table_rust_compressed`, `_extract_table_python_fallback`.

---

### P4 — Larger Delta write batches (implemented)

**Was:** `BATCH = 10_000` rows per `write_deltalake()` call (76 commits for a 760k-row table).

**Done:** `BATCH = 100_000` in `mssqlbak/extract.py`. Fewer, larger Parquet files reduce
Delta metadata overhead and improve downstream read performance.  A byte-budget flush
threshold (flush when batch exceeds N MB) remains a future option if very wide tables
accumulate too much RAM before flushing.

---

### P5 — Parallel table extraction (implemented)

See the **P5 — Parallel table extraction (implemented)** section below for details and
measured results.

---

### P6 — Row/page compression Rust decoder (implemented)

See the **P6 — Row/page compression Rust decoder (implemented)** section below for
details and measured results.

---

### P7 — Type dispatch table in `decode_value` (implemented)

**Was:** `types.py:decode_value()` dispatched on `type_id` via a chain of `if/elif` comparisons.

**Done:** `_DECODERS: dict[int, Any]` is built once at module import in `mssqlbak/types.py`.
`decode_value()` does a single `_DECODERS.get(col.type_id)` lookup and calls the result.

---

### P8c — SCSU decode in Rust for compressed NVARCHAR (implemented)

**Status:** Implemented.

**What was built:**

`rust/src/scsu.rs` contains a full Rust port of the SCSU (Unicode TR6) state-machine
decoder (`Expander` struct, `scsu_to_utf8` public function). `push_compressed_value` in
`rust/src/page_decode.rs` now calls `scsu_to_utf8` directly for `NCHAR`/`NVARCHAR`/`NTEXT`
and emits UTF-8 via `out.push_var_str(...)`. The `_MIXED_TYPES` NVARCHAR entry and the
`_redecode_compressed_mixed_cols` Python step are eliminated for compressed tables.
Python's `scsu.expand()` retains its original Python `_Expander` so the `ScsuError`
contract is preserved for callers that need error signalling on malformed input.

**Collateral fix:** The Rust compressed page decoder (`decode_compressed_page_cols`) had
a pre-existing record-type filter bug introduced in P6: it filtered out `Forwarded` (type 4,
emittable) and passed `GhostIndex` (type 6, not emittable). Fixed to emit only `Primary (0)`
and `Forwarded (4)`, matching Python's `cd_emittable` contract.

**Measured results:**

| Table | Before | After | Speedup |
|---|---|---|---|
| AdventureWorksDW (compressed NVARCHAR) | ~190k rows/s | ~721k rows/s | **3.8×** |

---

### P8a — Rust LOB stitching: follow off-row pointer chains in Rust (implemented)

**Status:** Implemented.

**What was built:**

`rust/src/lob.rs` implements `stitch_lob` and `stitch_text_ptr` as PyO3 functions.
Each function parses the LOB root structure (large-object pointer or text pointer),
walks the child-node chain in Rust, and calls back into Python only for raw page-record
access via a `page_reader` callable. NVARCHAR/NCHAR LOBs are SCSU-decoded inline via
`scsu_to_utf8` (P8c) before returning a UTF-8 Python string. `mssqlbak/rows.py` uses
the Rust path when `xpress_lz77` is available and no log-tail recovery is in progress.

The remaining per-row overhead is the Python callback for each LOB page-node fetch.
For `Posts` (large `Body NVARCHAR(4000)` spanning many LOB pages per row) this callback
cost is still visible; batching page-node fetches is the next lever (P9-candidate).

**Measured results (StackOverflowMini.bak, local disk, Apple M-series, workers=1):**

| Table | Rows | Before P8a | After P8a | Speedup |
|---|---|---|---|---|
| `Posts` | 1,565,425 | ~284 s (5,500 rows/s) | ~19.9 s (78,700 rows/s) | **14.3×** |
| `Comments` | 1,373,756 | ~53 s (25,900 rows/s) | ~3.4 s (404,000 rows/s) | **15.6×** |
| Total (all tables) | 8,097,337 | ~361 s | ~46 s | **7.8×** |

---

### P9a — XML columns: mixed Rust+Python path (implemented)

**Status:** Implemented.

**Problem:** Tables containing `XML`-typed columns (e.g., `AdventureWorks2019.Person`) fell
entirely to the Python fallback path because `XML` was in `_FORCE_PYTHON_TYPES`. The page
decoder was never called for these tables, so all rows paid full Python decode cost even
for the non-XML columns.

**What was built:**

- `rust/src/page_decode.rs` — removed `XML` from the `is_rust_type` exclusion list. Rust
  now extracts XML columns as raw bytes (inline binary XML or LOB pointer) and returns them
  via `push_var_bytes`, the same path as `CLR_UDT`.
- `mssqlbak/extract.py` — moved `XML` from `_FORCE_PYTHON_TYPES` to `_MIXED_TYPES`.
  `_redecode_mixed_cols` accepts a `store` parameter; for XML columns it calls
  `stitch_lob_images(raw_bytes, XML, file_images)` (zero-callback Rust, P9b) when
  `PageStore.file_images` is available, otherwise `_py_stitch_lob(store, None, raw_bytes)`,
  then `decode_value` → `decode_xml` to parse the binary XML format.
  `_CMPRS_MIXED_TYPES` keeps XML excluded: compressed tables with MAX-length columns
  (`max_length = -1`) are still blocked by the existing guard in
  `_build_rs_col_info_compressed`, so XML on the compressed path is unchanged.

**Measured results (AdventureWorks2019, Apple M-series, workers=1):**

| Table | Rows | Before (full-Python fallback) | After (XML mixed path) |
|---|---|---|---|
| `Person.Person` | 19,972 | ~1.5–1.7 s | ~1.1 s |

---

### P9b — Zero-callback LOB stitching via `ImageStore` (implemented)

**Status:** Implemented.

**Problem:** After P8a, `stitch_lob` and `stitch_text_ptr` in Rust walked the LOB node
chain in Rust but called back into Python for each page-record fetch. For `Posts` (large
`Body NVARCHAR(4000)` typically spanning 6–8 LOB pages per row) this produced millions of
Python callback round-trips per table extraction.

**What was built:**

- `rust/src/lob.rs` — added `page_slot_record` (Rust-side raw page slot extraction),
  `ImageStore` (holds `PyBuffer<u8>` locks for each file image, providing zero-copy page
  access via raw pointers), `read_lob_node_images` / `read_text_node_images` (zero-callback
  LOB node readers), and two new `#[pyfunction]`s: `stitch_lob_images` and
  `stitch_text_ptr_images`. These accept a `dict[file_id → mmap | bytes]` instead of a
  Python `page_reader` callable.
- `rust/Cargo.toml` — updated `pyo3` feature from `abi3-py39` to `abi3-py311`.
  `pyo3::buffer::PyBuffer` is only included in the stable ABI for Python 3.11+. The project
  already required Python ≥ 3.11 in `pyproject.toml`.
- `mssqlbak/pages.py` — added `PageStore.file_images` property (exposes `_images` dict).
- `mssqlbak/rows.py` — added `_HAS_RUST_LOB_IMAGES` capability flag; when true and `store`
  is a `PageStore` (not `LazyPageStore`), passes `store.file_images` to
  `stitch_lob_images` / `stitch_text_ptr_images` instead of a Python `page_reader` callback.
- `mssqlbak/extract.py` — `_redecode_mixed_cols` now uses `stitch_lob_images` for XML
  stitching when `file_images` is available, eliminating Python callbacks for LOB-stored
  XML values (P9a + P9b combined path).
- `stubs/xpress_lz77/__init__.pyi` — added type signatures for the two new functions.

**Where P9b applies:**

P9b benefits tables that go through the Python `read_table_rows` path (i.e., tables with
`TEXT`/`NTEXT`/`IMAGE` columns, sparse columns, or XML columns via `_redecode_mixed_cols`)
and store their large values as LOB trees (off-row, multiple pages per value).

StackOverflowMini.Posts/Comments use ROW compression (compression=1) and the Rust CD
decoder directly — they do not go through `read_table_rows` or LOB stitching at all.
The Posts bottleneck (17–18s for 1.5M rows) is the CD decoder throughput for wide rows
with many NVARCHAR columns, not Python callbacks.

**Measured results (AdventureWorks2019, Apple M-series, workers=1):**

| Table | Rows | Before P9a | After P9a+P9b | Notes |
|---|---|---|---|---|
| `Person` | 19,972 | ~1.5–1.7 s | ~1.1–1.2 s | XML: Rust page decode + Rust LOB stitch + Python decode_xml |

The remaining time (~1.2s) is dominated by `decode_xml` (Python binary XML parser) called
~40k times (2 XML columns × 20k rows). Further gain requires porting `decode_xml` to Rust.

**Remaining overhead:** `ImageStore::build()` is called once per `stitch_lob_images` call.
Further gain is possible by caching `ImageStore` across the batch at the table level.

---

### P9c — Columnstore blob index (one pass) (not implemented)

**Status:** Not implemented. Only matters for databases with multiple columnstore tables.
The current per-table scan (`_collect_blobs`) is fast enough for the single-columnstore-table
case. Worth implementing if a database with many columnstore tables shows long blob-index
build time in profiles.

**Current:** `columnstore.py:_collect_blobs()` scans every page in file 1 to find LOB
pages for a columnstore table. This scan runs once per columnstore table, so databases
with N columnstore tables pay O(N × page_count) total scan cost.

**Target:** Run one scan at `PageStore` build time and cache a `dict[lob_page_id, bytes]`
result. All columnstore tables share the same index; subsequent calls read from the cache.

**Expected gain:** Eliminates O(page_count) scan per additional columnstore table.

**Scope:** `mssqlbak/columnstore.py:_collect_blobs()` and `mssqlbak/pages.py:PageStore`.

---

## Sequencing

| Priority | Item | Effort | Gain | Status |
|---|---|---|---|---|
| P1 | Native XPRESS | Low–Medium | 2–3× compressed | **Done** — `xpress_lz77` Rust crate ships |
| Rust page decode | decode_record + decode_value in Rust | Medium | 6–26× total | **Done** — `decode_page_to_columns` in `rust/src/page_decode.rs` |
| CLR_UDT mixed | Rust page parse + Python column re-decode | Low | +11% OLTP | **Done** — CLR_UDT/SQL_VARIANT no longer force Python path |
| GIL release | `py.allow_threads` in `decode_page_to_columns` | Trivial | enables real threads | **Done** — Rust page decode releases GIL |
| P2 | Stream decompress pipeline | Medium | Hides download latency | **Done** — `BakReader` wired through `from_bak`; block-buffered `_ReaderBuffer` |
| P3 | Column accumulator | Low | ~8% | **Done** — `_col_coerce_fn` + direct accumulation |
| P4 | Larger Delta batches | Trivial | ~5% | **Done** — `BATCH = 100_000` |
| P5 | Parallel table extraction | Medium | +22% @ workers=2 | **Done** — `ThreadPoolExecutor` + per-thread `DeltaSink`; `--workers` CLI flag |
| P6 | Row/page compression Rust decoder | High | 5× page-compressed archive | **Done** — `decode_compressed_page_to_columns`; 309k rows/s on WWI archive tables |
| P7 | Type dispatch table | Low | 5–10% | **Done** — `_DECODERS` dict |
| P8c | SCSU decode in Rust (compressed NVARCHAR) | Medium | 3.8× compressed NVARCHAR tables | **Done** — `rust/src/scsu.rs`; ghost-index filter bug also fixed |
| P8a | Rust LOB stitching | High | 14–16× LOB-heavy tables | **Done** — `rust/src/lob.rs`; Posts 284s→20s, Comments 53s→3.4s |
| P9a | XML mixed path | Low | removes full-Python fallback for XML tables | **Done** — `page_decode.rs` + `extract.py` |
| P9b | Zero-callback LOB via `ImageStore` | Medium | eliminates Python callbacks for LOB-stored XML and TEXT/NTEXT values | **Done** — `lob.rs` `ImageStore`; used in `_redecode_mixed_cols` (XML) and `read_table_rows` (TEXT/NTEXT/IMAGE) |
| P9c | Columnstore blob index (one pass) | Low | proportional to columnstore table count | Pending |

P1, P2, P3, P4, P5, P6, P7, P8c, P8a, P9a, P9b, Rust page decoder, CLR_UDT mixed decode, and GIL-release are complete.

Pending items:
- **P9c** — columnstore blob index (one-pass scan at `PageStore` build time)

---

## P5 — Parallel table extraction (implemented)

Tables are extracted in parallel via `ThreadPoolExecutor`.  Each worker thread creates
its own `DeltaSink` so `open_table`/`write_batch`/`close` state is thread-local.
`PageStore` reads are safe concurrently (read-only after construction).

Real parallelism requires the Rust page decoder to release the GIL, which it does via
`py.allow_threads()` in both `decode_page_to_columns` (uncompressed) and
`decode_compressed_page_to_columns` (row/page compressed, P6).  Only XML and MAX-LOB
fallback tables still hold the GIL.

**Measured results (AW2022, local disk, Apple M-series):**

| workers | Rows | Time | Rows/sec |
|---|---|---|---|
| 1 (serial) | 760,837 | ~2.9 s | ~249,000 |
| 2 | 760,837 | ~2.6 s | ~296,000 |
| 4 | 760,837 | ~2.6 s | ~298,000 |
| 8 | 760,837 | ~2.7 s | ~284,000 |

The gain from 1→2 workers is small (~11%) for AW2022 for three reasons:
1. AW2022 has 6 XML-fallback tables that hold the GIL; when one thread decodes XML it
   blocks all others.
2. Total time is only ~2.9 s — thread-pool and per-table `DeltaSink` open/close overhead
   is proportionally large.
3. All 71 tables write to the same local output directory, creating local I/O contention.

**Parallelism scope and object-storage behaviour:**

`workers > 1` only parallelises the **row decode + Delta write** phase.  The .bak
download and full demux into `PageStore` are serial and must complete before any worker
can start.  Pages from different tables are interleaved in the .bak stream, so there
is no way to begin extracting a table until all its pages have been seen.

Consequence for object-storage sources:

| Phase | Parallelisable by workers? | What would help |
|---|---|---|
| .bak download (index pass) | No — serial index scan | P2 streaming (implemented, see below) |
| XPRESS demux into PageStore | No — serial per-chunk | P2 on-demand fetch per extent |
| Row decode (Rust tables) | Yes — GIL released | More workers |
| Row decode (XML/LOB fallback) | No — GIL held | P9a moves XML to mixed path; TEXT/NTEXT remain Python |
| Delta write to object storage | Yes — concurrent PUTs | More workers |

The main benefit of `workers > 1` for object-storage **sinks** (S3/Azure/GCS) is
concurrent Delta table writes: multiple workers issue PUT requests for different tables
simultaneously, keeping upload bandwidth saturated.  For databases with many large
tables this can halve the write phase.

For object-storage **sources** (reading the .bak from S3/Azure/GCS), `workers` helps
with concurrent Delta writes but the chunk index scan (P2) is still serial — each table's
pages are fetched on demand as workers start, so the index scan no longer blocks the
start of extraction.

**API:** `extract_bak(bak, sink, workers=N)`, `extract_bak_to_delta(bak, out, workers=N)`,
CLI `mssqlbak extract backup.bak --out DIR --workers 4`.

Workers only activate when `sink` is a `DeltaSink`; other sink types (PgDump, Spark) run
serially.

---

## P6 — Row/page compression Rust decoder (implemented)

**Problem:** Tables with `DATA_COMPRESSION = ROW` or `PAGE` (`compression=1` or `2`) bypassed
`_try_extract_table_rust` and fell to the Python CD-format decoder in `rowcompress.py`.

**Impact on WideWorldImporters-Full (before P6):**

| Table | Rows | Time | Rows/sec |
|---|---|---|---|
| ColdRoomTemperatures_Archive | 3,654,736 | ~61 s | ~60,000 |
| All other tables | 756,428 | ~5 s | ~151,000 |

`ColdRoomTemperatures_Archive` alone accounted for 92% of total extraction time.

**Implementation:**

New files and changes:
- `rust/src/page_compress.rs` — `CdRecord` (CD nibble parser), `PageCI` (page-level CI header with
  anchor/dictionary tables). Handles 4-bit nibble indicators, short-data cluster layout,
  long-data region, and PAGE CI header with prefix expansion.
- `rust/src/page_decode.rs` — `excess_be_int`, `decode_vardecimal`, `decode_compressed_datetime_us`,
  `push_compressed_value`, `decode_compressed_page_cols`, and `decode_compressed_page_to_columns`
  (PyO3 `#[pyfunction]` with `py.allow_threads()` GIL release).
- `mssqlbak/extract.py` — `_try_extract_table_rust_compressed` tries the Rust path first for
  `compression in (1, 2)`. `NCHAR`/`NVARCHAR` columns use a mixed path: Rust returns raw SCSU bytes,
  `_redecode_compressed_mixed_cols` calls `scsu.expand` post-decode. MAX-type LOB columns fall back
  to the Python path (avoids LOB-stitching complexity in Rust).

Physical column mapping uses `null_bit - 1` (stored as `null_index` in `ColSchema`) to locate each
column's slot in the CD record, matching SQL Server's physical ordering.

**Measured results after P6 (WideWorldImporters-Full, Apple M-series, workers=1):**

| Table | Rows | Before | After | Speedup |
|---|---|---|---|---|
| ColdRoomTemperatures_Archive | 3,654,736 | ~61 s (60k/s) | ~11.8 s (309k/s) | **5.2×** |
| WWI-Full total | 4,411,164 | ~66 s | ~30 s | **2.2×** |

The Python `rowcompress.py` is retained as the reference implementation and fallback for
unsupported column families (LOB/MAX types, SQL_VARIANT without fixed-width backing).

---

## P10 — ROW/PAGE compression decoder hot-path optimizations

### Root-cause analysis (StackOverflowMini.Posts: 17 s, 1.5 M rows, 20 cols)

Profiling the `_try_extract_table_rust_compressed` path revealed three distinct bottlenecks,
ordered by their impact:

**Bottleneck 1 — SCSU decoder allocation cascade (~11 s, dominant)**

`scsu_to_utf8` allocated a `Vec<u16>` starting empty and grew it via ~12 reallocation-copy
cycles per call (capacity sequence 0→1→2→4→…→2048 for a typical 1 KB Body value).  After
accumulation, `String::from_utf16_lossy` allocated a second `String` and converted every
`u16` to UTF-8.

With 1.5 M rows × 4 NVARCHAR columns (Body 1 KB avg, Title, Tags, LastEditorDisplayName)
= 6 M SCSU calls:
- ~6 M × 12 realloc cycles ≈ 72 M malloc/free/memcpy round-trips  
- ~6 M × 1 `from_utf16_lossy` call + ~1 KB u16→u8 conversion

**Bottleneck 2 — `CdRecord::parse()` heap allocations + O(n²) inner loop (~1 s)**

`CdRecord::parse()` allocated three `Vec`s per row (indicators, cluster_ptrs, long_entries).
`CdRecord::get(phys_idx)` did an O(n) linear scan for `CD_LONG` columns and an O(n)
scan for short-value offsets — O(n²) total per row across all columns.  For 1.5 M rows
× 20 cols: 4.5 M `Vec` allocs + ~285 M redundant scans.

**Bottleneck 3 — `pa.concat_batches()` on thousands of tiny Arrow batches (~1.5 s)**

Each page produces ~7 rows.  For a 100 k-row `BATCH`, Python collects ~14,285 tiny Arrow
`RecordBatch` objects before calling `pa.concat_batches()`.  Concatenating 14 k×20-column
fragments causes ~285 k Arrow array copy operations per flush, plus the overhead of the
Python list iteration.

---

### P10b — SCSU direct-UTF-8 output with ASCII run detection (implemented)

**Problem:** `Expander` accumulated decoded characters in a `Vec<u16>`, then called
`String::from_utf16_lossy` for conversion — double allocation, ~12 realloc cycles per
value.

**Fix:**
1. Replaced `Vec<u16>` with a `String` pre-allocated at `data.len()` capacity (1 allocation, 0
   reallocations for values shorter than the SCSU input — always true since SCSU ≥ input size).
2. `emit(code_unit)` now pushes UTF-8 directly, handling surrogate pairs inline with a
   1-`u16` lookahead buffer (`pending_high`).  BMP non-surrogates use
   `char::from_u32_unchecked`; surrogate pairs are combined and emitted as a 4-byte
   UTF-8 sequence.
3. **ASCII run detection:** in single-byte mode, printable ASCII bytes (0x20–0x7F) are
   bulk-copied with a single `extend_from_slice` instead of one character at a time.
   StackOverflow posts are ~95% ASCII; a typical 1 KB Body is one run.
4. `into_string()` returns `self.out` directly — no `from_utf16_lossy` step.

**Expected gain:** ~7–11 s savings on Posts; SCSU decode becomes ~0.5–1 s instead of ~11 s.

**Files changed:** `rust/src/scsu.rs` (full rewrite of `Expander`).

**Compatibility:** `from_utf16_lossy` semantics preserved: orphan high surrogates and orphan
low surrogates each emit U+FFFD.

---

### P10a — `CdParser`: buffer reuse + O(1) column lookup (implemented)

**Problem:** `CdRecord::parse()` allocates three `Vec`s per row; `CdRecord::get(phys)` scans
O(n) bytes to locate short-data and count prior `CD_LONG` columns.

**Fix:** Added `CdParser` to `rust/src/page_compress.rs`:

- `CdParser::parse(&mut self, raw)` — single O(ncol) forward scan; pre-computes
  `(kind, byte_offset, byte_len)` per physical column into a `Vec<CdEntry>` that is
  **cleared** (not re-allocated) between rows, so the backing memory is reused.
- `CdParser::get(&self, raw, phys)` — O(1) `Vec::get` + match; no linear scan.
- In `decode_compressed_page_cols`, one `CdParser` is created per page (or reused
  across pages with minimal cost) and `parse()` is called once per row.

`CdRecord` is retained for `PageCI::parse()` (called once per PAGE-compressed page, not
per row; its performance is not critical).

**Expected gain:** ~0.5–1 s savings on Posts; eliminates 4.5 M `Vec` allocations and
~285 M redundant offset scans per Posts table.

**Files changed:** `rust/src/page_compress.rs` (new `CdParser`), `rust/src/page_decode.rs`
(import and usage of `CdParser`).

---

## Language rewrite reference (informational only — not planned)

Estimates of what a full Go or Zig rewrite would achieve. Included for context;
the current plan is to extend the in-house Rust extension (`rust/`) rather than
rewrite the orchestration layer.

Full rewrite throughput estimates for AdventureWorks-class databases:

| Path | Python (measured) | Go | Zig |
|---|---|---|---|
| Compressed backup | ~11K rows/sec | ~400K–700K rows/sec | ~700K–1.5M rows/sec |
| Uncompressed backup | ~35K rows/sec | ~300K–600K rows/sec | ~500K–1.2M rows/sec |
| Speedup (compressed) | 1× | 35–65× | 65–140× |
| Speedup (uncompressed) | 1× | 9–17× | 14–35× |

The compressed speedup is larger because Go/Zig eliminates both the XPRESS bottleneck and
the Python row loop. The uncompressed speedup is the row loop only.

The practical ceiling in Go/Zig is Parquet encode speed (~1–5M rows/sec for OLTP schemas
via `apache/arrow-go`). Object storage PUT bandwidth is not the bottleneck at these row counts.

Go has a mature ecosystem for this pipeline (`apache/arrow-go`, `parquet-go`, `delta-go`).
Zig has no Delta Lake or Arrow library; it requires FFI to delta-rs or the C++ Arrow library,
adding ~6–10 weeks of integration work on top of the rewrite.

---

## In-house Rust extension (`rust/`)

The hot path is implemented as the `xpress_lz77` PyO3 crate in `rust/` (built with
`maturin`). It is the same `xpress_lz77` package installed in the venv; there is no
separate upstream dependency.

**Source files (3,054 lines total):**

| File | Lines | What it does |
|---|---|---|
| `xpress_lz77_plain.rs` | 157 | LZ77 plain (no Huffman) decompression |
| `xpress_lz77_huffman.rs` | 359 | LZ77+Huffman (XPRESS MS-XCA §2.2) decompression |
| `compressed.rs` | 101 | MSSQLBAK container header scanner (`find_next_mssqlbak_header_py`) |
| `page_decode.rs` | 1,121 | Uncompressed + compressed page → Arrow column buffers |
| `page_compress.rs` | 408 | CD-record and CI-header parsers for ROW/PAGE compressed pages |
| `scsu.rs` | 264 | SCSU (Unicode TR6) decoder; `scsu_to_utf8` called by page decoder and LOB stitcher (P8c) |
| `lob.rs` | 565 | LOB and text-pointer stitching; callback path (P8a) and zero-callback `ImageStore` path (P9b) |
| `lib.rs` | 79 | PyO3 module glue; registers all twelve public functions |

**Public Python API (all in the `xpress_lz77` module):**

| Function | Source | Called by |
|---|---|---|
| `lz77_plain_decompress_py(in_buf)` | `xpress_lz77_plain.rs` | `mssqlbak/xpress.py` |
| `lz77_huffman_decompress_py(in_buf, output_size)` | `xpress_lz77_huffman.rs` | `mssqlbak/xpress.py` |
| `lz77_huffman_decompress_until_input_py(in_buf, comp_end)` | `xpress_lz77_huffman.rs` | `mssqlbak/xpress.py` |
| `find_next_mssqlbak_header_py(buf, frm, huffman_offset, zero_offset, tag_offset)` | `compressed.rs` | `mssqlbak/compressed.py` |
| `decode_page_to_columns(page_raw, col_info, is_heap)` | `page_decode.rs` | `mssqlbak/extract.py` |
| `decode_compressed_page_to_columns(page_raw, col_info, is_heap, compression)` | `page_decode.rs` + `page_compress.rs` | `mssqlbak/extract.py` |
| `is_rust_decodable(type_id)` | `page_decode.rs` | `mssqlbak/extract.py` |
| `scsu_expand(data)` | `scsu.rs` via `page_decode.rs` | testing / fallback |
| `stitch_lob(page_reader, ptr_bytes, type_id)` | `lob.rs` | `mssqlbak/rows.py` |
| `stitch_text_ptr(page_reader, ptr_bytes, type_id)` | `lob.rs` | `mssqlbak/rows.py` |
| `stitch_lob_images(inline, type_id, file_images)` | `lob.rs` | `mssqlbak/rows.py` |
| `stitch_text_ptr_images(inline, file_images)` | `lob.rs` | `mssqlbak/rows.py` |

**Column buffer contract** (`decode_page_to_columns` and `decode_compressed_page_to_columns`):

Each column is returned as `(validity_bytes, offsets_or_None, data_bytes)`:
- `validity_bytes` — bit-packed null bitmap (1 = valid, LSB-first), one bit per row
- `offsets_or_None` — `None` for fixed-width columns; little-endian i32 array for variable-width
- `data_bytes` — packed values: LE numerics, UTF-8 for strings, raw bytes for binary

The caller (`extract.py`) reconstructs `pa.Array` via `pa.Array.from_buffers`.  GIL is
released inside both `decode_page_to_columns` and `decode_compressed_page_to_columns` via
`py.allow_threads()`, enabling real concurrency under `ThreadPoolExecutor` (P5).

**Python fallback:** `mssqlbak/xpress.py`, `mssqlbak/records.py`, and `mssqlbak/types.py`
remain as reference implementations and fallbacks for column types not yet handled in Rust
(geometry/geography, MAX-LOB on compressed tables, SQL_VARIANT with non-fixed backing,
TEXT/NTEXT/IMAGE). XML is now a mixed path (P9a): Rust extracts raw bytes, Python decodes.
The orchestration layer (`extract.py`, `compressed.py`, `rows.py`) is pure Python.

---

## P11 — Rust BCP parser for `.bacpac` (implemented)

### Root-cause analysis (WideWorldImporters-Full: 24.8 s, 4.7 M rows, 46 tables)

The `.bacpac` extraction path was entirely Python:

| Phase | Time | % |
|---|---|---|
| ZIP decompress (`zipfile`) | 0.16 s | 1% |
| **BCP parse** (`_parse_bcp_data`) | **13.15 s** | **81%** |
| **Arrow build** (`pa.array(list)`) | **2.91 s** | **18%** |
| Total (ColdRoomTemperatures_Archive) | 16.21 s | |

Python per-row cost for `ColdRoomTemperatures_Archive` (6 non-nullable fixed-width columns):
- `struct.unpack_from` × 6 = ~1.2 µs/row
- `data[pos:pos+n]` slice × 6 = ~0.6 µs/row
- Python value boxing + `list.append` × 6 = ~1.5 µs/row
- Loop overhead = ~1.0 µs/row
- `pa.array(list_of_3.65M)` × 6 cols = ~2.9 s total

Total: ~4.3 µs/row → 230k rows/s (observed: 278k rows/s).

### Fix: `rust/src/bcp.rs` + `mssqlbak/bacpac.py`

New `parse_bcp_columns(data, col_specs)` PyO3 function:

- Single linear scan over concatenated BCP bytes — no page boundaries, no slot arrays
- All BCP column types: fixed-width (u8/i16/i32/i64/f32/f64), bit (SQLBITN), decimal
  (SQL_NUMERIC_STRUCT → decimal128), date/datetime/datetime2/time/datetimeoffset,
  varchar/nvarchar/char/nchar (uint16 prefix), varbinary/binary, MAX types (int64 prefix),
  uniqueidentifier (UUID string), rowversion (binary(8) with uint16 prefix)
- Writes directly into Arrow-compatible column buffers (validity bitmap + data/offsets)
- Caller (`_buf_to_bcp_array`) uses `pa.Array.from_buffers` — zero Python iteration

Python side change in `BacpacInfo.read_table`: guarded by `_HAS_RUST_BCP` flag; pure-Python
`_parse_bcp_data` / `_col_to_arrow` remain as fallback.

### Measured results (WideWorldImporters-Full.bacpac)

**`Warehouse.ColdRoomTemperatures_Archive`** (3,654,736 rows, 204.7 MB BCP, 6 fixed-width cols):

| Phase | Before (Python) | After (Rust) | Speedup |
|---|---|---|---|
| ZIP decompress | 0.16 s | 0.14 s | ~1× (unchanged) |
| BCP parse → Arrow buffers | 13.15 s | **0.133 s** | **99×** |
| Arrow `from_buffers` | 2.91 s | **0.021 s** | **139×** |
| **Total** | **16.21 s** | **0.291 s** | **55×** |

Rust throughput for this table: **27.4 M rows/s** (memory-bandwidth limited).

**End-to-end (46 tables, 4.7 M rows):**

| | Before | After |
|---|---|---|
| Total time | 24.8 s | **0.91 s** |
| Throughput | 190 k rows/s | **5.18 M rows/s** |
| Speedup | — | **27×** |

String-heavy tables (`Sales.Invoices`, `Application.Cities`) are slower than
the fixed-width hot path due to UTF-16-LE → UTF-8 decoding overhead, but still
reach 700 k – 2 M rows/s — a large improvement over the Python baseline.
