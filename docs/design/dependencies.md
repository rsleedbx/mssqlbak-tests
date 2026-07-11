# Dependencies — third-party vs hand-rolled

Source of truth for runtime dependencies: [`pyproject.toml`](../../../pyproject.toml).

---

## Third-party libraries

### PyArrow (`pyarrow>=16`)

The canonical in-memory representation for all decoded data.
Every decode path (rowstore, columnstore, XTP) produces Python values that
`types.py` maps to Arrow types.  `extract.py` assembles those values into
`pyarrow.RecordBatch` objects and flushes them to a sink at a fixed batch size.

Key call sites:
- `types.py` — SQL type → Arrow type dispatch (all types)
- `columnstore/assembly/reader.py` — Arrow column assembly for CCI segments
- `extract.py` — `RecordBatch` construction and sink writes
- `sinks/`, `confidence.py` — Arrow-table consumers

PyArrow is the only library used for data representation; there is no pandas or
polars layer.

### deltalake / delta-rs (`deltalake>=1.0`)

The Delta Lake write target.  `DeltaSink` in `sinks/delta.py` calls
`write_deltalake()` from this package.  Because the delta-rs writer is
implemented in Rust, it releases the GIL during I/O, which allows the
threaded extractor in `extract.py` to overlap decoding (Python, GIL-bound)
with writing (Rust, GIL-released) across tables.

delta-rs is only used at the sink layer; it plays no role in decoding.

### numpy (`numpy>=2.0`)

Used in two narrow locations inside the columnstore decode path:

- `columnstore/decode/bitpack.py` — vectorized bit-unpack and frame-of-reference
  (FOR) decode via `np.frombuffer`, shift/mask arrays, and `np.arange`.
- `columnstore/decode/dict_numeric.py` — dictionary gather (`np.unique`) for
  numeric-dictionary encoded segments.

numpy is not used anywhere in the rowstore, XTP, container, or page paths.
The choice to use it here is a performance tradeoff: CCI segment decode is the
hottest path for large analytic tables.

### xmhuffman (`xmhuffman>=0.3`)

Decodes the Huffman-compressed string dictionary pages produced by SQL Server's
xVelocity (v4/v7) columnstore engine.  Called from
`columnstore/decode/dict_xvelocity.py` via `xmhuffman.decode_page` and
`xmhuffman.build_table`.

The import is lazy: the decoder checks for `xmhuffman` at call time and falls
back to `_huff_decode_page_py` (a pure-Python Huffman implementation inside
`dict_xvelocity.py`) when `xmhuffman` is absent or when the table's code
lengths are underfull — a condition that `xmhuffman.build_table` rejects but
the SQL Server encoder produces on real data.

### typer (`typer>=0.12`)

CLI framework for `mssqlbak._cli` and `pgdump._cli`.  Not involved in decode.

### PyO3 / maturin (build toolchain, not a runtime dep)

The in-repo Rust extension (`rust/`) is built with maturin and linked as
`mssqlbak_rs`.  maturin and PyO3 are build-time tools, not runtime
dependencies.  The extension is part of this repository, not an external
library — see [Hand-rolled: Rust extension](#rust-extension-mssqlbak_rs) below.

---

## Hand-rolled — what was written instead of using a library

SQL Server's binary formats are either proprietary (no public third-party
decoder with acceptable correctness and licensing), documented only via
Microsoft's open specifications (MS-XCA, MS-BINXML, etc.), or simply absent
from the ecosystem.  OrcaMDF (a C# open-source page reader) was used as a
cross-check reference during development but is not a dependency; its
algorithms were re-implemented independently for correctness (notably the
compressed-decimal precision, which OrcaMDF loses via `double`).

### XPRESS (LZ77 + Huffman)

`mssqlbak/xpress.py` + `rust/src/xpress_lz77_huffman.rs`, `xpress_lz77_plain.rs`

Implements MS-XCA (the XPRESS codec used in MSSQLBAK containers).  The Rust
version is the production path; the Python version is kept as an executable
spec and raises `XpressPythonFallbackError` when invoked at runtime to prevent
accidental use.  See [`docs/XPRESS_IMPL_HISTORY.md`](../XPRESS_IMPL_HISTORY.md)
for the implementation history.  Algorithm details are in
[`docs/spec/01_XPRESS.md`](../spec/01_XPRESS.md).

### SCSU (Standard Compression Scheme for Unicode)

`mssqlbak/scsu.py` + `rust/src/scsu.rs`

Decodes SQL Server's compressed `nchar`/`nvarchar` values per Unicode TR6.
Used in the ROW/PAGE compressed record path (`rowcompress.py`).  The Rust
`scsu_expand` function is the production path; the Python file is the reference.

### MTF / MSSQLBAK container demux

`mssqlbak/mtf.py`, `mssqlbak/compressed.py`, `mssqlbak/chunk_index.py`

`mtf.py` reconstructs the embedded MDF page stream from an uncompressed
(non-`WITH COMPRESSION`) `.bak` using the Microsoft Tape Format block
structure.  `compressed.py` handles MSSQLBAK `WITH COMPRESSION` backups,
assembling the XPRESS-compressed chunk stream and applying the v2 +4-byte
overlap rule.  `chunk_index.py` builds a lazy index for on-demand
decompression of individual extents.

### Page / record / catalog / LOB layer

| Module | What it handles |
|---|---|
| `mssqlbak/pages.py` | 96-byte page header, slot array, torn-page restoration, `LazyPageStore` + LRU chunk cache |
| `mssqlbak/records.py` | FixedVar record decoding — null bitmap, fixed + variable columns |
| `mssqlbak/rowcompress.py` | ROW/PAGE (CD-format) compressed record decoding, including `vardecimal` and SCSU |
| `mssqlbak/catalog.py` | Base system-table bootstrap → user-table schema; `_catalog_iam_pages`, `_walk_leaf`, legacy/dropped-column recovery |
| `mssqlbak/rows.py` | Per-table orchestration — alloc units → IAM chain → pages → records → typed rows; LOB stitching |
| `mssqlbak/logtail.py` | Log-tail parser for online / fuzzy backups — REDO/UNDO patches |

### Type decoders

`mssqlbak/types.py` dispatches to a set of hand-written leaf decoders:

| Module | Types handled |
|---|---|
| `mssqlbak/xmlbin.py` | Binary XML ([MS-BINXML]) |
| `mssqlbak/hierarchyid.py` | `hierarchyid` ORDPATH encoding |
| `mssqlbak/spatial.py` | Spatial geometry/geography → WKT (SRID, props, figures, shapes; lat/lon swap for geography) |
| `mssqlbak/types.py` (inline) | MSJSONB, `sql_variant`, `vector`, native CLR UDT subtypes, LOB structs |

### Columnstore codecs

The entire `mssqlbak/columnstore/` package is hand-rolled.  There is no
external columnstore codec library.

| Module | What it handles |
|---|---|
| `columnstore/storage/segment_meta.py` | CCI segment + dictionary metadata extraction from catalog |
| `columnstore/storage/lob.py` | Columnstore LOB preamble, deinterleave, ARCHIVE blob unwrap |
| `columnstore/decode/bitpack.py` | FOR + bit-pack decode (numpy-accelerated) |
| `columnstore/decode/value_for.py` | enc=1/4 integer/temporal/float decode (`_decode_enc1`, `_int_to_python`) |
| `columnstore/decode/dict_numeric.py` | enc=2 numeric hash-dictionary decode |
| `columnstore/decode/dict_string.py` | enc=3 string dictionary decode modes |
| `columnstore/decode/dict_xvelocity.py` | v4/v7 xVelocity Huffman dict decode + Python fallback |
| `columnstore/decode/enc5_raw.py` | enc=5 ARCHIVE format A/B/C/D — VLD, multichunk, headerless |
| `columnstore/assembly/delta.py` | Delta store — tombstone suppression, rowstore re-entry |
| `columnstore/assembly/reader.py` | CCI top-level batch reader → Arrow |

Rust accelerates the hot inner loop: `decode_cs_segment` in `rust/src/columnstore.rs`.

### Rust extension (`mssqlbak_rs`)

`rust/src/` — built with maturin into the `mssqlbak_rs` extension module.

This is first-party code, not a library dependency.  It provides:

| Export | Purpose |
|---|---|
| `lz77_huffman_decompress` / `lz77_plain_decompress` | XPRESS decompress |
| `find_next_mssqlbak_header_py` | MSSQLBAK header scanner |
| `decode_page_to_columns` / `decode_compressed_page_to_columns` | Page → columnar values (fast path) |
| `scsu_expand` | SCSU decoder |
| `stitch_lob` / `stitch_lob_images` / `stitch_text_ptr` | LOB chain stitch |
| `parse_bcp_columns` | BCP native format (BACPAC) |
| `decode_cs_segment` | Columnstore segment decode inner loop |

Every Rust export has a Python fallback.  The fallback is used when the
extension is unavailable (e.g. during development without a native build) or
when the Rust path encounters an unhandled encoding variant.

### XTP CFP decoder

`mssqlbak/xtp.py`

Decodes In-Memory OLTP checkpoint file pair (CFP) blocks — compact
(`0x0001000d`) and WAL (`0x00030050`) formats — and applies the
seq-contiguity + dense-identity completeness gate before emitting rows.

---

## Summary table

| Component | Third-party | Hand-rolled |
|---|---|---|
| In-memory columnar representation | PyArrow | — |
| Delta Lake write | deltalake (delta-rs) | — |
| Columnstore bit-unpack | numpy | — |
| xVelocity string-dict Huffman | xmhuffman (w/ Python fallback) | underfull fallback in `dict_xvelocity.py` |
| CLI | typer | — |
| XPRESS LZ77+Huffman | — | `xpress.py` + Rust |
| SCSU | — | `scsu.py` + Rust |
| MTF / MSSQLBAK container | — | `mtf.py`, `compressed.py` |
| Page / record / catalog / rows | — | `pages.py`, `records.py`, `rowcompress.py`, `catalog.py`, `rows.py` |
| Columnstore codecs | — | `columnstore/decode/*` + Rust |
| Binary XML, hierarchyid, spatial | — | `xmlbin.py`, `hierarchyid.py`, `spatial.py` |
| XTP CFP | — | `xtp.py` |
| Log-tail REDO/UNDO | — | `logtail.py` |
| Native acceleration (all of above) | — | `rust/` (first-party, PyO3) |
