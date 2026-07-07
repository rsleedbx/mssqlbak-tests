# Missing Comprehensive Fixture Coverage

Gaps between the committed synthetic fixtures and every SQL Server behavior a DBA
can exercise that would affect how mssqlbak reads a `.bak` file.

Sources: `/Users/robert.lee/github/sql-docs` —
`t-sql/statements/`, `relational-databases/indexes/`,
`relational-databases/data-compression/`, `relational-databases/backup-restore/`,
`relational-databases/blob/`, `relational-databases/tables/`,
`relational-databases/collations/`, `relational-databases/security/`.

---

## What we already have

| Fixture | Core coverage |
|---|---|
| `typecoverage_full.bak` | All scalar types incl. sql_variant, hierarchyid, geometry, geography, rowversion, text/ntext/image |
| `tabletypecoverage_full.bak` | Heap, clustered index, nonclustered index, heap+NCI |
| `compressioncoverage_full.bak` | ROW / PAGE compression; float/datetimeoffset edge cases |
| `columnstore_minimal.bak` | Basic CCI, small row groups |
| `boundarycoverage_full.bak` | Large row groups (> 32,767 rows), enc=4 bitpack |
| `archivenull_full.bak` | Unpartitioned CCI + COLUMNSTORE_ARCHIVE, known NULLs (Gap 5) |
| `archive_columnstore_partition_full.bak` | Partitioned CCI — 4 REBUILD scenarios (Gap 5 supplement) |
| `archive_columnstore_types_full.bak` | ARCHIVE CCI, 7 types (CHAR/VARCHAR/NCHAR/NVARCHAR/BINARY/VARBINARY/UUID) × 35,000 rows (Gap I-1) |
| `featurecoverage_full.bak` | Temporal tables, NCCI on rowstore, ledger, graph, long_text, COMPRESS(), memory_oltp skip |
| `ndfcoverage_full.bak` | Secondary filegroup (NDF) |
| `xmlcoverage_full.bak` | Untyped XML column on rowstore |
| `xmlheap_full.bak` | Heap + xml/varchar(MAX)/varbinary(MAX) LOB (Gap 10 guard) |
| `geocoverage_full.bak` | geometry / geography under ROW and PAGE compression |
| `computedcoverage_full.bak` | Persisted + non-persisted computed columns on rowstore |
| `heapcoverage_large_50000.bak` | 50 k-row heap, IAM multi-extent traversal |
| `unicode_codepage_coverage.bak` | Unicode collation nvarchar |
| `dirtycoverage_*.bak` | Dirty-backup scenarios (uncommitted, temporal ghost row, etc.) |

**Confirmed non-gaps (no fixture possible or needed):**
- Global temp tables / table variables — live in `tempdb`, cannot appear in a `.bak`
- External tables — no data pages; metadata-only
- Row-Level Security (RLS) — query-time predicate; all rows stored in plaintext on the page
- Dynamic Data Masking (DDM) — result-set-time masking; page bytes unchanged
- `IDENTITY` / `SEQUENCE`-defaulted columns — plain integer on the page; already covered
- `OPTIMIZE_FOR_SEQUENTIAL_KEY` — latch management hint; no on-page effect

---

## Category A — Backup container variants

These affect the MTF (Microsoft Tape Format) container that wraps all pages, not the
page content itself.  mssqlbak must handle the outer envelope before it can read any
page.

### A-1 — Backup compression (ZSTD, SS2025)

**What SQL Server does**
`BACKUP DATABASE ... WITH COMPRESSION` wraps each backup block in MS_XPRESS
compression.  SS2022 added `ALGORITHM = QAT_DEFLATE`; SS2025 adds `ZSTD`.
The current fixture `typecoverage_full_compressed.bak` covers MS_XPRESS.

**Parser failure mode**
A ZSTD-compressed block passed to the MS_XPRESS decompressor crashes or returns
garbage.  mssqlbak must detect the algorithm byte in the MTF block header.

**Proposed fixture:** `backup_compressed_zstd_full.bak` (SS2025 only)

---

### A-2 — Encrypted backup

**What SQL Server does**
`BACKUP DATABASE ... WITH ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = ...)`
encrypts each backup block with a certificate.  The pages inside are *not* TDE-
encrypted — only the backup stream is.

**Parser failure mode**
Without the certificate + private key mssqlbak cannot decrypt any block.  It must
detect the encryption header and emit a clear error rather than crashing.

**Proposed fixture:** `backup_encrypted_full.bak` — test is a *detect-and-fail-
gracefully* assertion, not a decode test.

---

### A-3 — Partial / file-filegroup backup

**What SQL Server does**
`BACKUP DATABASE ... FILEGROUP = 'FG2'` backs up one filegroup only; the resulting
`.bak` contains pages only from that filegroup.  System catalog pages (in PRIMARY)
may be absent.

**Parser failure mode**
mssqlbak trying to read the system catalog from a partial backup where PRIMARY is
absent will crash or produce empty output.  Must detect partial backup and warn.

**Proposed fixture:** `backup_partial_full.bak` (back up only a secondary
filegroup, assert graceful handling)

---

### A-4 ⛔ — Snapshot / copy-only backup (not feasible in containers)

**What SQL Server does**
`BACKUP DATABASE ... WITH COPY_ONLY` does not affect the log chain.
`BACKUP DATABASE ... WITH METADATA_ONLY` (snapshot backup, SS2022+) writes only
catalog metadata — no user data pages.

**Parser failure mode**
A METADATA_ONLY backup has an empty data section; if mssqlbak expects at least one
data page per table it will mis-report 0 rows or crash.

**Status: ⛔ NOT FEASIBLE** — `COPY_ONLY` is already used by every fixture
(implicitly covered).  `METADATA_ONLY` requires Windows VSS (Volume Shadow Copy
Service) — not available on Linux Podman containers.  Cannot generate this
fixture in the current test environment.

---

### A-5 ✅ — Non-default block size

**Status: ✅ IMPLEMENTED (2026-06-22)** — `_detect_block_size()` in
`mssqlbak/reader.py` probes all powers-of-two from 512 to 65536 bytes.
Fixture `backup_blocksize_full.bak` (BLOCKSIZE=4096) generated for all four
SS versions; 2 tests in `test_backup_blocksize_coverage.py` confirm 100 rows
with correct values.  `python -m tools.fixture_run all-versions --suite backup-blocksize`.

**What SQL Server does**
`BACKUP ... WITH BLOCKSIZE = 65536` changes the MTF block size from the default 65 KB.
Legal values: 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536 bytes.

**Parser failure mode**
A parser hardcoded to one block size will misalign all block boundaries when the
`.bak` uses a different size, producing garbled pages.

**Fixture:** `backup_blocksize_full.bak` (BLOCKSIZE=4096 — all four SS versions)

---

## Category B — LOB and off-row storage

### B-1 ⛔ — FILESTREAM column (not feasible in containers)

**Status: ⛔ NOT FEASIBLE** — FILESTREAM requires Windows NTFS and the
Windows FILESTREAM feature.  `SERVERPROPERTY('FilestreamEffectiveLevel')` returns
0 on all Linux Podman containers.  Cannot generate this fixture in the current
test environment.

**What SQL Server does**
`CREATE TABLE t (id INT, data VARBINARY(MAX) FILESTREAM)` stores the BLOB data in
the NTFS file system via a dedicated FILESTREAM filegroup; only the row's file-path
pointer (or GUID) lives in the rowstore page.  The `.bak` includes the FILESTREAM
filegroup as a separate MTF stream.

**Parser failure mode**
The in-row pointer will be decoded as a varbinary if the parser does not recognise
the FILESTREAM attribute, producing a GUID/path string instead of the binary data.
Following the file-system reference is not possible offline without the FILESTREAM
MTF stream.  Correct behavior: surface the pointer as a placeholder and skip BLOB
content; do not crash.

---

### B-2 — FileTable

**What SQL Server does**
`CREATE TABLE ft AS FILETABLE` creates a system-schema table backed by FILESTREAM
for hierarchical file storage.  Has a fixed schema (`name`, `path_locator`,
`file_stream`, etc.) and constraints.

**Parser failure mode**
The fixed schema includes hidden / system-managed columns that may not appear in
`sys.columns` normally.  A schema enumerator that iterates only user columns will
produce an incorrect column list.

**Proposed fixture:** `filetable_full.bak` — assert `classify_table` returns a
clear skip reason rather than attempting extraction on the system-managed schema.

---

### B-3 ✅ — Non-`(max)` row-overflow (varchar / nvarchar wide rows)

**Status: ✅ FIXED (2026-06-19)** — `stitch_lob_core` (Rust) and `_stitch_lob`
(Python) now detect the 24-byte ROW_OVERFLOW pointer (struct_type=2) and follow
it to the ROW_OVERFLOW_DATA page. All four SQL Server versions confirmed; 46/46
tests pass in `test_rowboundary_coverage.py`. Commit `203f9c6`.

**What SQL Server does**
When the total variable-length portion of a row exceeds 8,060 bytes, SQL Server
moves one or more `varchar`/`nvarchar` columns (not `(max)`) off-row to a
`ROW_OVERFLOW_DATA` allocation unit.  A 24-byte pointer is left in-row.
This is **distinct** from `(max)` LOB overflow; the existing `xmlheap_full.bak`
only covers the `(max)` path.

**Parser failure mode**
Treating the 24-byte overflow pointer as the column value → corrupted strings.
Not following the pointer → truncated/missing values.

**Fixture:** `rowboundary_full.bak` (`dbo.rb_overflow`, ids 1–9)
```sql
CREATE TABLE rowoverflow (
    id  INT,
    a   VARCHAR(4000) NOT NULL,  -- together a+b+c exceed 8060 bytes per row
    b   VARCHAR(4000) NOT NULL,
    c   VARCHAR(2000) NOT NULL
);
```
Seed rows where `a+b+c` total > 8,060 bytes so `c` migrates off-row.

**Proposed command:** `rowoverflow`

---

### B-4 — LOB column in CCI (varchar(MAX) / nvarchar(MAX) in columnstore)

See **Gap C-6** in the Columnstore section below.

---

## Category C — Rowstore partition operations

### C-1 — Partition SPLIT / MERGE on rowstore table

**What SQL Server does**
```sql
ALTER PARTITION FUNCTION pf() SPLIT RANGE (new_boundary);
ALTER PARTITION FUNCTION pf() MERGE RANGE (old_boundary);
```
SPLIT creates a new empty partition; MERGE moves all rows from the smaller partition
into the surviving one.  Catalog and IAM entries are rewritten; the physical pages
stay where they are until a rebuild.

**Parser failure mode**
After a SPLIT the catalog shows one more partition than the IAM entries
accommodate; after a MERGE the catalog shows fewer.  If mssqlbak iterates pages
by partition count from the catalog it will over- or under-shoot the IAM walk.

**Proposed fixture:** `partition_split_merge_full.bak` — partitioned heap,
SPLIT to 5 partitions, populate, MERGE to 3, backup; assert exact row counts per
surviving partition.

**Proposed command:** `partition-split-merge`

---

### C-2 — PARTITION SWITCH with rowstore tables across filegroups

**What SQL Server does**
```sql
ALTER TABLE src SWITCH PARTITION 1 TO dest PARTITION 1;
```
A metadata-only operation that reassigns page ownership from one object/partition
to another.  Requires source and target to be on the same filegroup; data pages are
not rewritten.

**Parser failure mode**
After a SWITCH the catalog `object_id` → partition → page mapping changes but the
physical pages do not move.  A cached IAM-walk that uses stale catalog state reads
the original table's pages under the new object and either double-counts or drops
rows.

**Proposed fixture:** `partition_switch_full.bak` — staging table → target table
SWITCH; assert 0 rows in staging, correct count in target.

**Proposed command:** `partition-switch`

---

## Category D — Data type gaps

### D-1 — Sparse columns and column set (HIGHEST PRIORITY)

**What SQL Server does**
```sql
CREATE TABLE sparse_tbl (
    id     INT PRIMARY KEY,
    a      INT           SPARSE NULL,
    b      VARCHAR(20)   SPARSE NULL,
    c      DATETIME2     SPARSE NULL,
    cs     XML COLUMN_SET FOR ALL_SPARSE_COLUMNS
);
```
Sparse columns replace the standard per-column layout with a **sparse vector**
record appended to the row: a count of non-NULL sparse columns followed by an array
of `(column_id, byte_offset)` pairs and the packed non-NULL values.  NULL sparse
columns cost zero bytes.  Incompatible with data compression.

**Parser failure mode**
A record parser that walks the fixed-length block + variable-length block + NULL
bitmap will **completely misread** any sparse row — wrong values for every column
after the first sparse column.  No error is raised; output is silently corrupt.
This was confirmed: none of the existing `make_*_fixture.py` generators emit
`SPARSE`.

**Proposed fixture:** `sparse_full.bak`
```sql
CREATE TABLE sparse_wide (
    id   INT PRIMARY KEY,
    a    INT           SPARSE NULL,   -- set in half the rows
    b    VARCHAR(20)   SPARSE NULL,   -- set in a third
    c    DATETIME2     SPARSE NULL,   -- set in a quarter
    d    DECIMAL(10,2) SPARSE NULL,   -- always NULL
    cs   XML COLUMN_SET FOR ALL_SPARSE_COLUMNS
);
```
Seed 10,000 rows with varying sparsity patterns; assert correct values and NULL
counts per column.

**Proposed command:** `sparse`

---

### D-2 — sql_variant value extraction

**What SQL Server does**
`sql_variant` stores a per-value type-metadata header (base type, precision, scale,
collation, max-length) followed by the value.  A single column can hold
`INT`, `DECIMAL`, `NVARCHAR`, `DATETIME2`, and more — mixed row-to-row.

**Current coverage**
`typecoverage_full.bak` declares a `sql_variant` column but the project already
lists it in `_MINMAX_SKIP_TYPES`.  Value extraction (reading the per-value header
and dispatching to the correct decoder) is untested.

**Parser failure mode**
Reading `sql_variant` as its declared column type (it has none) → corrupt / garbage
values.  The per-value header must be parsed to select the decoder.

**Proposed fixture:** `sql_variant_extract_full.bak`
```sql
CREATE TABLE sv (
    id  INT PRIMARY KEY,
    val SQL_VARIANT
);
INSERT sv VALUES
    (1, CAST(42        AS INT)),
    (2, CAST(3.14      AS DECIMAL(8,4))),
    (3, CAST(N'hello'  AS NVARCHAR(20))),
    (4, CAST('2025-01-01' AS DATETIME2)),
    (5, NULL);
```
Assert each row's extracted value matches the inserted type and value.

**Proposed command:** `sql-variant-extract`

---

### D-3 — rowversion / timestamp column

**What SQL Server does**
`rowversion` (alias `timestamp`) is a fixed 8-byte binary auto-incremented on every
row modification.  Stored as the last fixed-length column in the record.

**Current coverage**
`typecoverage_full.bak` includes `rowversion` as a declared type but extraction and
min/max handling are untested (it is monotonic and comparison-meaningless, so it
should be in `_MINMAX_SKIP_TYPES`).

**Parser failure mode**
Decoded as a `bigint` → byte-reversed value (big-endian on page, little-endian
`bigint`); decoded as `datetime` → nonsense.  Should surface as 8-byte `varbinary`.

**Proposed fixture:** `rowversion_extract_full.bak` — table with `rowversion`
column; assert values are 8-byte `bytes` objects, distinct per row, monotonically
increasing.

**Proposed command:** `rowversion-extract`

---

### D-4 — hierarchyid extraction

**What SQL Server does**
`hierarchyid` is a variable-length bit-packed binary (typically 1–6 bytes, max 892
bytes) storing a path like `/1/2/3/`.

**Current coverage**
Present in `typecoverage_full.bak` but extraction (decoding the path bytes) is not
tested; min/max skipped.

**Parser failure mode**
Decoded as text → garbled bytes; sorted lexicographically → wrong ordering.
Should surface as raw `varbinary` or decoded path string.

**Proposed fixture:** `hierarchyid_extract_full.bak` — table with a hierarchy;
assert correct varbinary bytes or decoded path per row.

**Proposed command:** `hierarchyid-extract`

---

### D-5 ✅ — vector column (SS2025)

**Status: ✅ IMPLEMENTED (2026-06-22)** — VECTOR columns are stored on-disk as
VARBINARY (type_id 165); mssqlbak returns raw bytes without crashing.  The binary
format is: 8-byte header (`[magic uint16][dims uint16][flags uint32]`) followed by
packed float32 values in LE order.  Fixture `vector_full.bak` generated on SS2025;
3 tests in `test_vector_coverage.py` confirm 10 rows, all values decodable, known
float values match within float32 precision.  `python -m tools.fixture_run all-versions --suite vector --version 2025`.

**What SQL Server does**
```sql
CREATE TABLE vt (id INT PRIMARY KEY, v VECTOR(3));
INSERT vt VALUES (1, '[0.1, 2.0, 30.0]');
```
Stored as a proprietary binary format (header + packed `float32` elements); cannot
be used in `sql_variant`, cannot be a key column.

**Parser failure mode**
Unknown binary header → garbage / crash on SS2025 `.bak` files.

**Fixture:** `vector_full.bak` (SS2025 only) — `tests/fixtures_2025/`

---

### D-6 ✅ — Native JSON column (SS2025)

**Status: ✅ IMPLEMENTED (2026-06-22)** — Native JSON (type_id 244) is now
decoded by mssqlbak as raw bytes (same as VARBINARY) via a new entry in
`_DECODERS` in `mssqlbak/types.py`.  The on-disk format is a proprietary binary
JSON encoding (NOT plain UTF-8 text) with a 2-byte header; field names and string
values are embedded as UTF-8 substrings within the binary blob.  Fixture
`native_json_full.bak` generated on SS2025; 4 tests in
`test_native_json_coverage.py` confirm 10 rows, raw bytes non-empty and distinct,
binary blob contains expected embedded string values.  `python -m tools.fixture_run all-versions --suite native-json --version 2025`.

**What SQL Server does**
Native `JSON` type (SS2025) stores JSON in a proprietary binary encoding on disk.
Uses `Latin1_General_100_BIN2_UTF8` collation; off-row when large.

**Parser failure mode**
Without a decoder for type_id 244, mssqlbak raises `NotImplementedError` on any
SS2025 .bak containing a native JSON column.  With the decoder, raw bytes are
returned; a future enhancement could implement the binary-JSON-to-text converter.

**Fixture:** `native_json_full.bak` (SS2025 only) — `tests/fixtures_2025/`

---

## Category E — Rowstore index type gaps

### E-1 — Nonclustered index with included columns (covering index)

**What SQL Server does**
```sql
CREATE NONCLUSTERED INDEX ix ON t(k) INCLUDE (a_varchar, b_decimal);
```
The NC leaf pages carry the included columns in every leaf record alongside the key.
The leaf record format has its own NULL bitmap and variable-length section for the
included columns.

**Parser failure mode**
An NC-page reader that assumes `leaf record = key columns only` mis-parses the
leaf, producing wrong offsets for every included column value.  Possible crash on
the variable-length section.

**Proposed fixture:** `covering_index_full.bak` — table with a covering NC index;
assert leaf page records decode correctly.

**Proposed command:** `covering-index`

---

### E-2 — Filtered nonclustered index (rowstore)

**What SQL Server does**
```sql
CREATE NONCLUSTERED INDEX fi ON t(code) WHERE status IS NOT NULL;
```
Only rows matching the predicate appear in the index; row count in the NC index
is less than the base-table row count.

**Parser failure mode**
Any assertion that NC-index row count == base-table row count fails for filtered
indexes.  mssqlbak should not use an NC index for row extraction — but if it does,
it silently under-counts.

**Proposed fixture:** `filtered_index_full.bak` — 10,000-row table, 3,000 with
`status IS NULL`; NC index covers 7,000 rows; assert base table returns 10,000,
NC index is not used as primary source.

**Proposed command:** `filtered-index`

---

### E-3 ✅ — XML index internal node table

**Status: ✅ IMPLEMENTED (2026-06-22)** — `recover_schema` already filters
`sysschobjs.type == 'U'` (user tables only), so internal XML node tables
(type = 'IT') are never enumerated.  Fixture `xml_index_full.bak` (100-row table
with PRIMARY + FOR PATH XML index) generated for all four SS versions; 4 tests in
`test_xml_index_coverage.py` confirm no internal tables appear in schema, user
table present, 100 rows extracted, XML content and tag values correct.  `python -m tools.fixture_run all-versions --suite xml-index`.

**What SQL Server does**
```sql
CREATE PRIMARY XML INDEX pix ON xt(doc);
CREATE XML INDEX six ON xt(doc) USING XML INDEX pix FOR PATH;
```
Each XML index materializes an internal "node table" — a system-owned clustered
B-tree with hidden columns (`pk1`, `id`, `nid`, `tag`, `value`, `hid`, etc.)
alongside the user table.

**Parser failure mode**
The internal node table appears in the catalog as a real table-like object.  If
`classify_table` enumerates it as a user table it emits a bogus table with hidden-
column layout; if it walks those pages with the rowstore reader it will crash on
the unexpected record shape.

**Fixture:** `xml_index_full.bak` — all four SS versions

---

### E-4 ✅ — Spatial index internal tessellation table

**Status: ✅ IMPLEMENTED (2026-06-22)** — `recover_schema` already filters
`sysschobjs.type == 'U'` (user tables only), so internal spatial tessellation
tables (type = 'IT') are never enumerated.  Fixture `spatial_index_full.bak`
(200-row geometry table with GEOMETRY_GRID spatial index) generated for all four
SS versions; 4 tests in `test_spatial_index_coverage.py` confirm no tessellation
table in schema, user table present, 200 rows extracted, geometry values non-NULL.
`python -m tools.fixture_run all-versions --suite spatial-index`.

**What SQL Server does**
Spatial indexes create an internal system-owned B-tree of `(cell_id, pk)` pairs
for the tessellated grid.  The geometry/geography *column values* themselves are
already covered by `geocoverage_full.bak`; the tessellation index table is not.

**Parser failure mode**
Same as E-3: the tessellation table can surface as an enumerable object; its
record layout (cell-id key + base PK) differs from the user table.

**Fixture:** `spatial_index_full.bak` — all four SS versions

---

## Category F — Security features

### F-1 ✅ — TDE (Transparent Data Encryption) — detect and fail gracefully

**What SQL Server does**
`BACKUP DATABASE … WITH ENCRYPTION (ALGORITHM = AES_128, SERVER CERTIFICATE = …)`
encrypts every page with AES before writing to disk.  The result uses the
MSSQLBAK container format but the pages are encrypted ciphertext — no valid
XPRESS Huffman chunks can be decoded.  Without the DEK + certificate, no user
page is readable.

Note: a plain `BACKUP DATABASE` of a TDE-enabled database writes **plaintext**
pages (SQL Server decrypts in memory before backup).  The F-1 fixture uses
`WITH ENCRYPTION` to produce an actually-encrypted backup file.

**Parser failure mode (before fix)**
mssqlbak scanned for valid XPRESS chunks and raised `ValueError` with a message
mentioning "likely TDE-encrypted".  This was a catch-all `ValueError` rather
than a typed error, making it hard for callers to handle the TDE case
specifically.

**Fix**
- `mssqlbak/errors.py`: new `EncryptedBackupError(ValueError)` class
- `mssqlbak/compressed.py`: raises `EncryptedBackupError` (not plain `ValueError`)
  when MSSQLBAK container yields zero decodable pages
- `mssqlbak/mtf.py`: adds `_is_tde_encrypted_mtf()` entropy heuristic; raises
  `EncryptedBackupError` for MTF-format backups where the DEK blob is detectable
  (covers the alternative `BACKUP … WITHOUT COMPRESSION, WITH ENCRYPTION` path)
- `mssqlbak/__init__.py`: exports `EncryptedBackupError`

**Fixture:** `tde_full.bak` — TDE-enabled database backed up with
`ENCRYPTION (ALGORITHM = AES_128, SERVER CERTIFICATE = TDE_Fixture_Cert)`.
Generated SS2017–SS2025.

**Test file:** `tests/test_tde_detection.py` — 17 tests (11 unit, 6 integration).
`PageStore.from_bak(tde_full.bak)` raises `EncryptedBackupError` on all versions.

**Command:** `all-versions --suite tde`

---

### F-2 — Always Encrypted column — varbinary round-trip

**What SQL Server does**
Always Encrypted stores column ciphertext as `varbinary` on the page.  The page
structure is normal; only the column values are opaque blobs.  Keys are never in
the DB.

**Parser failure mode**
If the parser expects the *plaintext* declared type and sizes the column accordingly
it will mis-read the ciphertext bytes or crash on a type mismatch.  The ciphertext
should be returned as `varbinary` of the correct length without error.

**Proposed fixture:** `always_encrypted_full.bak` — table with a deterministic
AE `INT` column and a randomized AE `NVARCHAR(20)` column; assert values are
returned as `varbinary` of the expected ciphertext length.

**Proposed command:** `always-encrypted`

---

## Category G — Collation and encoding variants

### G-1 — UTF-8 collation column (SS2019+, HIGHEST PRIORITY)

**What SQL Server does**
`varchar` / `char` columns with a `_UTF8` collation (e.g.
`Latin1_General_100_CI_AS_SC_UTF8`) store **UTF-8 bytes** — not a single-byte code
page.  A `varchar(10)` may hold fewer than 10 characters; multi-byte code points
span 2–4 bytes each.

**Parser failure mode**
A `varchar` decoder that assumes a single-byte code page (CP1252) will produce
mojibake for any non-ASCII UTF-8 data.  UTF-8 collations are common in modern
databases.

**Proposed fixture:** `utf8_collation_full.bak` (SS2019+)
```sql
CREATE TABLE utf8_tbl (
    id  INT PRIMARY KEY,
    s   VARCHAR(40) COLLATE Latin1_General_100_CI_AS_SC_UTF8
);
INSERT utf8_tbl VALUES (1,'café'),(2,'日本語'),(3,'😀'),(4,'hello');
```
Assert decoded strings match the inserted Unicode characters.

**Proposed command:** `utf8-collation` (SS2019+; exclude from `_ALL_VERSIONS_SUITE`)

---

### G-2 — Supplementary characters (surrogate pairs) in nvarchar

**What SQL Server does**
`nvarchar` under a `_SC` collation stores **UTF-16 surrogate pairs** (4 bytes) for
code points > U+FFFF.  The on-disk bytes are standard UTF-16; `_SC` affects
sort/comparison semantics.  SS2012+; default for compatibility level ≥ 140.

**Parser failure mode**
A UTF-16 decoder that treats every 2-byte unit as a complete character splits
surrogate pairs (emoji, rare CJK) into two broken code units → corrupt strings.

**Proposed fixture:** `surrogate_pairs_full.bak`
```sql
CREATE TABLE sc_tbl (
    id INT PRIMARY KEY,
    s  NVARCHAR(40) COLLATE Latin1_General_100_CI_AS_SC
);
INSERT sc_tbl VALUES (1,N'𠀀'),(2,N'😀 emoji'),(3,N'normal');
```

**Proposed command:** `surrogate-pairs`

---

### G-3 — Per-column collation override (mixed code pages in one table) ✅ FIXED

**What SQL Server does**
Each column can carry its own collation, independent of the database collation.  A
single table can mix `Latin1_General_CI_AS` (CP1252), `Greek_CI_AS` (CP1253),
and `Hebrew_CI_AS` (CP1255) columns.

**Bugs found and fixed**

*Bug 1 — AE detection false positive (`mssqlbak/catalog.py`):*
`_AE_COLLATION_MAX = 0x10000` (65,536) was too high.  Per-column CI collation
overrides have IDs in the 0xD000–0xFFFF range (e.g. Greek_CI_AS → 0xD007 = 53,255),
which fall below the threshold and were incorrectly treated as Always Encrypted,
causing `_dv_char` to return `None` for all non-UTF-8 varchar columns.
**Fix:** lowered `_AE_COLLATION_MAX` to `0x4000` (16,384).  Real AE BIN2 collation
IDs are ≤ ~0x2000 (e.g. Latin1_General_BIN2 = 0x808 = 2,056).

*Bug 2 — wrong codec applied (`mssqlbak/types.py`):*
`_dv_char` computed the correct per-column codec via `_codec_for_collation` but
then discarded it, passing `utf8=(codec == "utf-8")` to `_decode_char`, which only
ever used `"utf-8"` or `"cp1252"`.  Greek/Hebrew/Arabic bytes were silently decoded
as CP1252.
**Fix:** changed `_decode_char` signature from `utf8: bool = False` to
`encoding: str = "cp1252"`, and updated `_dv_char` to pass `encoding=codec`.

**Fixture:** `mixed_collation_full.bak`
```sql
CREATE TABLE collation_mix (
    id   INT PRIMARY KEY,
    lat  VARCHAR(40) COLLATE Latin1_General_CI_AS,   -- CP1252
    grk  VARCHAR(40) COLLATE Greek_CI_AS,            -- CP1253
    heb  VARCHAR(40) COLLATE Hebrew_CI_AS            -- CP1255
);
```
Three rows: ASCII-only (id=1), non-ASCII Greek+Hebrew+Latin (id=2), all-NULL (id=3).
UTF-8 collation intentionally excluded (requires SS2019+; covered by G-1).

**Results:** Generated SS2017–SS2025. 15/15 tests pass (8 unit, 7 fixture).

**Command:** `all-versions --suite mixed-collation`

---

## Category H — Page layout edge cases

### H-1 — Forwarded records on heap (HIGHEST PRIORITY)

**What SQL Server does**
When a heap row is widened (e.g. via `UPDATE` to a longer `varchar`) and no longer
fits on its original page, SQL Server writes the real row elsewhere and leaves a
**forwarding stub** (record type `0x04`) on the original page pointing to the new
RID.

**Parser failure mode**
A heap scan that counts forwarding stubs **and** the real row **double-counts**; one
that reads the stub bytes as row data produces garbage values; one that skips
forwarded targets **under-counts**.  This is a high-probability match for the silent
row-count errors seen on real-world heaps.

**Proposed fixture:** `forwarded_records_full.bak`
```sql
CREATE TABLE fwd (id INT, val VARCHAR(8000)); -- narrow at insert
INSERT fwd SELECT n, REPLICATE('x', 10) FROM ...;  -- fill with short strings
UPDATE fwd SET val = REPLICATE('x', 7000)           -- force forward
    WHERE id % 2 = 0;
BACKUP DATABASE ...;
```
Assert row count = total rows, each `val` column decodes to the correct string.

**Proposed command:** `forwarded-records`

---

### H-2 — Ghost / logically deleted records

**What SQL Server does**
`DELETE` marks rows as **ghost** (bit in the record header) but leaves them
physically on the page.  Ghost cleanup runs asynchronously; a backup taken before
cleanup contains both live and ghost records.

**Parser failure mode**
Counting ghost records as live rows **over-counts**.  The project already has a
known temporal ghost-row failure (`dirtycoverage_temporal_update`); a dedicated
rowstore ghost fixture isolates this from the temporal-table complexity.

**Proposed fixture:** `ghost_records_full.bak`
```sql
-- Insert 1,000 rows; delete 200; backup immediately.
DELETE TOP (200) FROM ghost_tbl; BACKUP DATABASE ...;
```
Assert row count = 800 (not 1,000).

**Proposed command:** `ghost-records`

---

### H-3 — Max-row-width boundary (single row per page)

**What SQL Server does**
Maximum in-row data per page is **8,060 bytes**.  Rows engineered to occupy nearly
the whole page produce a page with a single slot.

**Parser failure mode**
Off-by-one errors in free-space or slot-count arithmetic surface when a page
contains exactly one slot.  The slot array (at the page end) may overlap the
row data under assumptions that ≥ 2 rows exist.

**Proposed fixture:** `max_row_width_full.bak`
```sql
CREATE TABLE wide_row (id INT, data CHAR(8000)); -- ~8,004 bytes per row
```
Seed a few rows; assert all rows decoded correctly with no off-by-one.

**Proposed command:** `max-row-width`

---

### H-4 — High slot density (many tiny rows per page)

**What SQL Server does**
Very small rows (e.g. a single `tinyint`) pack hundreds of slots per page.  The
slot array at the end of the page grows accordingly.

**Parser failure mode**
Slot-array iteration bugs (wrong slot count, reading past the last slot) surface
when the slot array is large.

**Proposed fixture:** `high_slot_density_full.bak`
```sql
CREATE TABLE tiny_row (a TINYINT NOT NULL);
INSERT tiny_row SELECT TOP(100000) ...;
```
Assert row count == 100,000.

**Proposed command:** `high-slot-density`

---

### H-5 — XML_COMPRESSION on off-row LOB (SS2022)

**What SQL Server does**
SS2022 adds `WITH (XML_COMPRESSION = ON)` to XML indexes, compressing the off-row
LOB pages that store large XML values.

**Parser failure mode**
An off-row LOB-page reader that does not check for XML_COMPRESSION will pass
compressed bytes to the XML decoder → crash or garbage.

**Proposed fixture:** `xml_compression_full.bak` (SS2022 only) — XML-column table
with `XML_COMPRESSION = ON`, large XML documents that go off-row; assert decoded
XML matches inserted values.

**Proposed command:** `xml-compression` (SS2022+ only)

---

## Category I — ARCHIVE CCI: missing string/binary data type coverage

### I-1 — String and binary types not yet tested under COLUMNSTORE_ARCHIVE ✅ IMPLEMENTED

**Context**
`archive_columnstore_partition_full.bak` and `archivenull_full.bak` test the
enc_type=5 (ARCHIVE multi-sub-block) decoder only for `CHAR(10)`.  All other
string/binary types that use dictionary encoding — and therefore also produce
enc_type=5 segments under ARCHIVE — are absent.

**Why these types matter specifically**
Only dictionary-compressed column types produce enc_type=5 segments.  Numeric and
date/time types use RLE or bitpack encoding under ARCHIVE (enc_type=1/3/4), which
are the same paths exercised by `compressioncoverage_full.bak` and
`boundarycoverage_full.bak` without ARCHIVE.  The types below all store data in a
string pool (Block 0 of the ARCHIVE blob) but differ in pool structure:

| Type | Pool entry format | In fixture? |
|---|---|---|
| `CHAR(n)` | fixed `n` bytes (space-padded) | ✅ `CHAR(10)` |
| `VARCHAR(n)` | variable-length bytes, length-prefixed | ✅ `VARCHAR(20)` |
| `NCHAR(n)` | fixed `n × 2` bytes (UTF-16) | ✅ `NCHAR(10)` |
| `NVARCHAR(n)` | variable-length UTF-16, length-prefixed | ✅ `NVARCHAR(20)` |
| `BINARY(n)` | fixed `n` bytes | ✅ `BINARY(10)` |
| `VARBINARY(n)` | variable-length bytes, length-prefixed | ✅ `VARBINARY(20)` |
| `UNIQUEIDENTIFIER` | fixed 16 bytes | ✅ |
| `NVARCHAR(MAX)` ¹ | off-row LOB pointer | ❌ (tracked as C-6) |
| `VARCHAR(MAX)` ¹ | off-row LOB pointer | ❌ (tracked as C-6) |
| `VARBINARY(MAX)` ¹ | off-row LOB pointer | ❌ (tracked as C-6) |

¹ CCI only, SS2017+.  LOB-pointer variant tracked separately as Gap C-6.

**Parser failure modes by type**
- `VARCHAR`/`NVARCHAR` — variable-length pool entries: the pool offset index
  (`Index A`) now points into a variable-width pool; a fixed-stride assumption
  (correct for `CHAR`) produces wrong offsets → garbled strings.
- `NCHAR`/`NVARCHAR` — UTF-16 pool entries: a single-byte (CP1252) pool reader
  will decode each char as two separate characters → corrupt strings.
- `BINARY`/`VARBINARY` — binary pool: treating pool bytes as text → wrong values.
- `UNIQUEIDENTIFIER` — 16-byte fixed entries: a stride mismatch (e.g. treating
  the pool as a `CHAR` pool with 10-byte strides) corrupts every GUID.

**Fixture:** `archive_columnstore_types_full.bak`
- Generator: `tools/make_archive_columnstore_types_fixture.py`
- 7 tables × 35,000 rows each = 245,000 rows total
- NULL pattern: every 500th row → 70 NULLs per table
- ARCHIVE compression applied via `ALTER TABLE … REBUILD … WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)`
- Tests: `tests/test_archive_columnstore_types_coverage.py`

**Command:** `all-versions --suite archive-columnstore-types` ✅ generated SS2017–SS2025

---

## Category J — Columnstore-specific gaps (from ongoing Gap 5 work)

See `docs/FIXTURE_GAPS.md` §Gap 5 for full status and active debug fixtures
(`archivenull_full.bak`, `archive_columnstore_partition_full.bak`).

Additional columnstore gaps not covered by Gap 5 work:

| ID | Gap | Failure risk | Proposed fixture |
|---|---|---|---|
| C-1 | Delta store (open rowgroup in backup) | Silent row loss | `delta_rowgroup_full.bak` |
| C-2 | TOMBSTONE rowgroup | Duplicate rows | `tombstone_rowgroup_full.bak` |
| C-3 | Multiple small compressed rowgroups | Segment-index mis-read | `multi_rowgroup_full.bak` |
| C-4 | Filtered NCCI (WHERE clause) | Row count assertion failure | `filtered_ncci_full.bak` |
| C-5 | NCCI on heap | RID lookup failure | `ncci_heap_full.bak` |
| C-6 | LOB columns in CCI (varchar(MAX)/nvarchar(MAX)) | Corrupt decode / crash | `cci_lob_full.bak` |
| C-7 | Ordered CCI (SS2022+, ORDER clause) | Min/max extraction accuracy | `ordered_cci_full.bak` |
| C-8 ✅ | String/binary/GUID min-max segment metadata (SS2022+) | NULL vs non-null metadata handling | `cci_string_minmax_full.bak` |
| C-9 | PARTITION SWITCH with CCI | Wrong row counts post-switch | `cci_switch_full.bak` |
| C-10 | REORGANIZE + deleted-row bitmap | Row over-count after deletes | `cci_reorganize_full.bak` |
| C-11 | Non-persisted computed columns in CCI (SS2017+) | Missing column / wrong count | `cci_computed_full.bak` |
| C-12 | CCI + rowstore B-tree nonclustered index on same table | Decoder misrouted to wrong format | `cci_with_btree_full.bak` |

---

## Master priority order (across all categories)

Generation commands (once the fixture script exists):
- **`all-versions --suite <cmd>`** — builds for SS2017, SS2019, SS2022, SS2025 in one shot
- **`all-versions --suite <cmd> --version 2019 --version 2022 --version 2025`** — version-restricted
- **`--fixture-dir tests/fixtures_2025 <cmd>`** — SS2025-only

| Priority | ID | Gap | Failure risk | Generation |
|---|---|---|---|---|
| 1 | D-1 ✅ | Sparse columns + column set | **IMPLEMENTED** — `sparse_full.bak`: 10,000-row heap with 4 sparse columns + `XML COLUMN_SET`; 9 tests (row count, per-column null patterns, value content). Generated SS2019–SS2025; all tests pass. | `all-versions --suite sparse` |
| 2 | H-1 ✅ | Forwarded records on heap | **IMPLEMENTED** — `forwarded_records_full.bak`: 1,000-row heap where even IDs are widened to force forwarding stubs; 9 tests (heap type, row count, short/long val length/content, control-table match). Generated SS2019–SS2025; all tests pass. | `all-versions --suite forwarded-records` |
| 3 | H-2 ✅ | Ghost / deleted records | **IMPLEMENTED** — `ghost_records_full.bak`: 1,000 rows inserted, 200 deleted under TF 661 before backup; 5 tests (heap type, row count = 800, no deleted IDs, all live IDs present, val content). Generated SS2019–SS2025; all tests pass. | `all-versions --suite ghost-records` |
| 4 | G-1 ✅ | UTF-8 collation | **IMPLEMENTED** — `utf8_collation_full.bak`: `Latin1_General_100_CI_AS_SC_UTF8` varchar column with café, 日本語, 😀, €, ASCII, empty, NULL; 9 tests including nvarchar control match. Generated SS2019–SS2025; all tests pass. | `all-versions --suite utf8-collation --version 2019 --version 2022 --version 2025` |
| 5 | K-1 ✅ | tabletypecoverage tt_column: 4-row CCI = deltastore only, segment decoder never invoked for any of 25 types | **IMPLEMENTED** — `tabletype_cci_large_full.bak`: 1,200-row CCI per type, REORGANIZE forces real segments; 5 previously-xfailed types (`decimal_38_10`, `datetimeoffset_7`, `nvarchar_50`, `binary_8`, `uniqueidentifier`) now pass — bugs fixed during K-3 work. Generated SS2019–SS2025; all tests pass. | `all-versions --suite tabletype-cci-large` |
| 6 | C-1 ✅ | CCI delta store (open rowgroup) | **IMPLEMENTED** — `delta_rowgroup_full.bak`: CCI with compressed segment (1,200 rows) + open delta store (50 rows); 9 tests (total count, compressed/delta rows present, no duplicates, value content). Generated SS2019–SS2025; all tests pass. | `all-versions --suite delta-rowgroup` |
| 7 | K-3 ✅ | Large-row-group CCI missing char(n)/binary(n)/varbinary(n)/uniqueidentifier/bit | **IMPLEMENTED** — `cci_types_large_full.bak`: one table per type, 1,200+ rows with REORGANIZE; per-type tests for row count, NULL, low/high boundaries, `classify_table`. Generated SS2019–SS2025; all tests pass. | `all-versions --suite cci-types-large` |
| 8 | B-3 ✅ | Non-`(max)` row-overflow | Corrupted wide-row values | `all-versions --suite rowoverflow` |
| 9 | I-1 ✅ | ARCHIVE CCI: VARCHAR/NVARCHAR/BINARY/VARBINARY/UNIQUEIDENTIFIER types | Wrong pool-stride → garbled values for all non-CHAR string/binary columns under ARCHIVE | `archive_columnstore_types_full.bak` generated SS2017–SS2025 |
| 10 | C-6 ✅ | LOB in CCI | **FIXED** — two bugs: (1) 2-byte varint in max-dict wrong when `byte2 < 0x80` (VARCHAR(MAX)/VARBINARY(MAX) ≥128 bytes silently truncated); (2) NVARCHAR(MAX) payload decoded as cp1252 instead of UTF-16LE. `cci_lob_full.bak` generated SS2017–SS2025; 16/16 tests pass. | `all-versions --suite cci-lob` |
| 11 | K-4 ✅ | compressioncoverage ROW/PAGE missing bigint/char/binary/uniqueidentifier | **FIXED** — extended `_COLS` with 10 types (bigint, smallint, tinyint, bit, money, smallmoney, char(10), binary(10), varbinary(20), uniqueidentifier); added `test_k4_extra_cols_match_baseline` cross-table comparison test. Re-run `all-versions --suite compressionmatrix`. | extend existing `all-versions --suite compressionmatrix` |
| 12 | K-5 ✅ | featurecoverage ncci_table: only 4 types in NCCI | **IMPLEMENTED** — `ncci_types_full.bak`: 19 rowstore tables × 1,203 rows each with NCCI on value column covering all missing types; 5 tests per table (row count, NULL, low, high, classify). Run `all-versions --suite ncci-types` to generate. | `all-versions --suite ncci-types` |
| 13 | G-3 ✅ | Per-column collation override | **FIXED** — two bugs: (1) `_AE_COLLATION_MAX` was 0x10000 (65,536), incorrectly flagging per-column CI collation overrides (0xD007–0xD00C) as Always Encrypted, returning None for all non-UTF-8 varchar columns. (2) `_dv_char` discarded the codec name, always decoding non-UTF-8 columns as cp1252. `mixed_collation_full.bak` (Latin1/Greek/Hebrew) generated SS2017–SS2025; 15/15 tests pass. | `all-versions --suite mixed-collation` |
| 14 | F-1 ✅ | TDE detect-and-fail | **FIXED** — new `EncryptedBackupError(ValueError)` in `mssqlbak/errors.py`; `BACKUP … WITH ENCRYPTION` produces an MSSQLBAK-format file with AES-encrypted pages; `compressed.py` raises `EncryptedBackupError` when no decodable XPRESS chunks found; MTF-format TDE backups covered by entropy heuristic in `mtf.py`; `tde_full.bak` generated SS2017–SS2025; 17/17 tests pass. | `all-versions --suite tde` |
| 15 | K-2 ✅ | boundarycoverage missing decimal/numeric/bit/date-time types from enc=4 boundary tests | **FIXED** — `boundarycoverage_datetime_full.bak` with 9 tables (bit, decimal(9,4), decimal(18,4), date, datetime, datetime2(3), time(3), smalldatetime, datetimeoffset(3)), 6 labeled boundary rows + 1,194 filler per table; two bugs fixed: (1) Rust `decode_cs_segment` returns `None` for enc=1/2 Hybrid RLE (n_stored < n_rows) — BITPACK_REF 0xFFFFFFFF was misidentified as compact-null sentinel producing all-None output; (2) Python `_decode_enc1` Hybrid RLE bitpack for enc=2 now uses `null_val − sv` debiased offset (values stored descending) instead of `sv − 1` (ascending), fixing BIT value inversion. `boundarycoverage_datetime_full.bak` generated SS2017–SS2025; 9/9 tests pass. | `all-versions --suite boundary-datetime` |
| 16 | C-9 ✅ | CCI PARTITION SWITCH | **IMPLEMENTED** — `cci_switch_full.bak`: 1,200 rows compressed into `cci_switch_src`, metadata-only SWITCH to `cci_switch_dst`; 4 tests (src empty, dst row count, no duplicates, spot check). All tests pass. | `all-versions --suite cci-switch` |
| 17 | C-10 ✅ | CCI REORGANIZE + deleted bitmap | **IMPLEMENTED + BUG FIXED** — `cci_reorganize_full.bak`: two tables with 1,200 rows, 200 deleted (id%6==0). Bug: mssqlbak ignored the CCI delete bitmap (cmprlevel=2 PAGE-compressed rowset), returning all 1,200 rows instead of 1,000. Fix: `read_columnstore_rows` now reads CD-encoded bitmap entries (col[0]=seg_id, col[1]=0-based position) and skips deleted rows. 6 tests pass. | `all-versions --suite cci-reorganize` |
| 18 | C-3 ✅ | Multiple small CCI rowgroups | **IMPLEMENTED + 2 BUGS FIXED** — `multi_rowgroup_full.bak`: 3 batches (1200/600/300) with REORGANIZE between each. Bugs fixed: (1) TOMBSTONE rowgroups: REORGANIZE merges compressed rowgroups — greedy descending seg_id selection using sysrowsets.rcrows; (2) Tombstoned deltas: expanded check to include per-rowgroup n_rows. 6 tests pass. | `all-versions --suite multi-rowgroup` |
| 19 | E-1 ✅ | Covering index (included columns) | **IMPLEMENTED** — `covering_index_full.bak`: 1,000-row table with NC index `INCLUDE(name, amount)`; 4 tests (row count, columns, spot check, no duplicates). All tests pass. | `all-versions --suite covering-index` |
| 20 | D-2 ✅ | sql_variant value extraction | **IMPLEMENTED** — `sql_variant_extract_full.bak`: 6-row mixed SQL_VARIANT table (INT, DECIMAL, NVARCHAR, BIGINT, DATETIME2, NULL); 7 tests. All tests pass. | `all-versions --suite sql-variant-extract` |
| 21 | F-2 | Always Encrypted varbinary round-trip | Type-size mismatch / crash | `all-versions --suite always-encrypted --version 2019 --version 2022 --version 2025` |
| 22 | H-3 ✅ | Max-row-width (single row per page) | **IMPLEMENTED** — `max_row_width_full.bak`: 5-row `CHAR(8000)` table, each row fills an 8KB page; 4 tests. All tests pass. | `all-versions --suite max-row-width` |
| 23 | G-2 ✅ | Surrogate pairs in nvarchar | **IMPLEMENTED** — `surrogate_pairs_full.bak`: 5-row NVARCHAR table with UTF-16 surrogate pairs (CJK Extension B, emoji, flag emoji), ASCII, NULL; 4 tests. All tests pass. | `all-versions --suite surrogate-pairs` |
| 24 | H-4 ✅ | High slot density | **IMPLEMENTED** — `high_slot_density_full.bak`: 100,000-row TINYINT table; 3 tests (row count, distribution, no nulls). All tests pass. | `all-versions --suite high-slot-density` |
| 25 | C-4 ✅ | Filtered NCCI | **IMPLEMENTED** — `filtered_ncci_full.bak`: 400-row clustered + heap tables each with filtered NCCI (WHERE active=1 covers 200 rows); mssqlbak reads base table and returns all 400 rows; 7 tests. No parser bug found. | `all-versions --suite filtered-ncci` |
| 26 | C-5 ✅ | NCCI on heap | **IMPLEMENTED** — `ncci_heap_full.bak`: 400-row heap with NCCI on (id, val); mssqlbak reads heap IAM chain, returns all 400 rows with exactly 3 columns (no RID leakage); 4 tests. No parser bug found. | `all-versions --suite ncci-heap` |
| 27 | E-3 ✅ | XML index internal node table | **IMPLEMENTED** — `xml_index_full.bak`: 100-row XML table with PRIMARY + FOR PATH XML index; `recover_schema` skips IT-type node tables (type='IT' filtered out by sysschobjs.type=='U' check); 4 tests. All tests pass. | `all-versions --suite xml-index` |
| 28 | A-1 | ZSTD backup compression (SS2025) | Block decompressor crash | `--fixture-dir tests/fixtures_2025 backup-compressed-zstd` |
| 29 | A-2 | Encrypted backup | Crash instead of clean error | `all-versions --suite backup-encrypted` |
| 30 | D-3 ✅ | rowversion extraction | **IMPLEMENTED** — `rowversion_extract_full.bak`: 100-row table; rowversion column returned as 8-byte `bytes`, distinct, monotonically increasing; 5 tests. No parser bug found. | `all-versions --suite rowversion-extract` |
| 31 | D-4 ✅ | hierarchyid extraction | **IMPLEMENTED** — `hierarchyid_extract_full.bak`: 6-row table; mssqlbak decodes hierarchyid as path string (/, /1/, /2/, /1/1/, /1/2/, /1/1/1/), matching persisted `path` column; 4 tests. No parser bug. | `all-versions --suite hierarchyid-extract` |
| 32 | C-7 ✅ | Ordered CCI (SS2022+) | **IMPLEMENTED** — `ordered_cci_full.bak`: 1,200-row ordered CCI (ORDER id) vs regular CCI; both return all 1,200 rows, no duplicates, correct values; 8 tests. Segment format identical to regular CCI — no parser bug. | `all-versions --suite ordered-cci --version 2022 --version 2025` |
| 33 | C-8 ✅ | String min-max metadata (SS2022+) | **IMPLEMENTED** — `cci_string_minmax_full.bak`: 1,200-row CCI with VARCHAR/NVARCHAR columns; 120 NULL rows exercise the NULL-minmax path in SS2022+ segment metadata; 3 tests (row count, NULL rows, non-NULL values). All tests pass. | `all-versions --suite cci-string-minmax` |
| 34 | C-11 ✅ | Computed column in CCI | **IMPLEMENTED** — `cci_computed_full.bak`: 1,200-row CCI table; non-persisted computed column added via ALTER TABLE absent from segments; mssqlbak returns stored columns without crash; 4 tests. | `all-versions --suite cci-computed` |
| 35 | C-12 ✅ | CCI + rowstore B-tree on same table | **IMPLEMENTED** — `cci_btree_nci_full.bak`: 1,200-row CCI table with 2 B-tree NC indexes; mssqlbak reads only CCI segments — exactly 1,200 rows, correct 4 columns, no duplicates; 4 tests. No parser bug. | `all-versions --suite cci-btree-nci` |
| 36 | B-1 ⛔ | FILESTREAM column | **NOT FEASIBLE** — FILESTREAM requires Windows NTFS; disabled on all Linux Podman containers (`FilestreamEffectiveLevel=0`). Cannot generate this fixture in current environment. | N/A |
| 37 | D-5 ✅ | vector column (SS2025) | **IMPLEMENTED** — `vector_full.bak`: 10-row VECTOR(3) table; stored as VARBINARY (type_id 165); 8-byte header + float32 array; 3 tests (row count, no crash, known float values). All tests pass. | `all-versions --suite vector --version 2025` |
| 38 | D-6 ✅ | Native JSON column (SS2025) | **IMPLEMENTED** — `native_json_full.bak`: 10-row JSON table; type_id 244 now decoded as raw bytes (not UCS-2 nvarchar); binary format with UTF-8 field names embedded; 4 tests (row count, bytes type, embedded strings, distinct blobs). All tests pass. | `all-versions --suite native-json --version 2025` |
| 39 | H-5 | XML_COMPRESSION off-row (SS2022) | Compressed LOB decoded raw | `all-versions --suite xml-compression --version 2022 --version 2025` |
| 40 | E-4 ✅ | Spatial index internal table | **IMPLEMENTED** — `spatial_index_full.bak`: 200-row geometry table with GEOMETRY_GRID spatial index; `recover_schema` skips IT-type tessellation tables; 4 tests. All tests pass. | `all-versions --suite spatial-index` |
| 41 | A-3 | Partial / filegroup backup | Crash on absent PRIMARY | `all-versions --suite backup-partial` |
| 42 | A-4 ⛔ | Snapshot / METADATA_ONLY backup | **NOT FEASIBLE** — requires Windows VSS; not available on Linux Podman containers. COPY_ONLY is implicitly covered by all existing fixtures. | N/A |
| 43 | A-5 ✅ | Non-default block size | **IMPLEMENTED** — `backup_blocksize_full.bak`: BLOCKSIZE=4096; `_detect_block_size()` auto-detects; 2 tests (row count, values). All tests pass. | `all-versions --suite backup-blocksize` |
| 44 | C-2 ✅ | CCI TOMBSTONE rowgroup | **FIXED as part of C-3** — tombstoned rowgroups are excluded by the greedy descending-seg_id filter added in `read_columnstore_rows`; verified by `multi_rowgroup_full.bak` which exercises exactly this scenario. No separate fixture needed. | covered by `multi-rowgroup` |
| 45 | B-2 | FileTable | Schema enumeration crash | `all-versions --suite filetable` |

---

## Category K — Data type coverage gaps in existing fixtures

All gaps below share the same root cause: an existing fixture is
*purpose-narrowed* to a small set of types even though it exercises a code
path that is type-sensitive.  Unlike categories A–J (entirely missing
scenarios), these gaps require extending or supplementing fixtures that already
exist.

---

### K-1 ✅ — `tabletypecoverage_full.bak` tt_column: 4-row CCI = deltastore only

**Problem**
`tt_column` is the table that carries every supported CCI type column
(`tinyint`, `smallint`, `int`, `bigint`, `bit`, `decimal(38,10)`,
`numeric(18,4)`, `money`, `smallmoney`, `real`, `float`, `date`,
`datetime2(7)`, `time(7)`, `smalldatetime`, `datetime`, `datetimeoffset(7)`,
`char(10)`, `nchar(10)`, `varchar(max)`, `nvarchar(50)`, `binary(8)`,
`varbinary(max)`, `uniqueidentifier`).  However, it has only **4 rows**
(low/high/mid/null).  SQL Server never compresses a row group with fewer than
~102,400 rows into a column segment without an explicit `REORGANIZE` or
`REBUILD`.  With 4 rows:

- All 4 rows stay in the **delta store** (a B-tree heap, not column segments).
- The CCI segment decoder is **never invoked** for any of these 25 types.
- The `tabletypecoverage` test therefore validates the delta-store read path,
  not the CCI segment encoding/decoding path.

**Impact:** Silent wrong value or crash for every CCI-compatible type is
undetected.  The only large-row-group CCI fixtures with type coverage are:

| Fixture | Types with compressed CCI segments |
|---|---|
| `boundarycoverage_full.bak` | `bigint`, `int`, `smallint`, `tinyint`, `money`, `smallmoney`, `real`, `float` |
| `compressioncoverage_full.bak` | `int`, `varchar(20)`, `nvarchar(40)`, `nchar(10)`, `decimal(18,4)`, `numeric(9,2)`, `datetime`, `datetime2(3)`, `date`, `time(3)`, `datetimeoffset(3)`, `smalldatetime` |
| `columnstore_minimal.bak` | same set as compressioncoverage (same `_COLS`) |

Types with **zero** large-row-group CCI segment coverage:
`bigint`+8 basics covered, but **`char(n)`**, **`binary(n)`**,
**`varbinary(n)`**, **`uniqueidentifier`** appear in no large-row-group CCI.
`bit` is also absent.

**Proposed fix:** Add a `tabletype_cci_large` fixture that rebuilds (or
mirrors) `tt_column` with ≥ 1,200 rows and an explicit `REORGANIZE` so every
column type produces a compressed segment:

```sql
-- Mirror of tt_column but with 1,200 rows per type table, then:
ALTER INDEX cci_tt_column_large ON tt_column_large
    REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON);
```

**Status: ✅ FIXED** — `tabletype_cci_large_full.bak` generated SS2019–SS2025; all 25 type structural rows decode correctly. Five decoder bugs fixed during K-3 work (`decimal_38_10`, `datetimeoffset_7`, `nvarchar_50`, `binary_8`, `uniqueidentifier` no longer in `COLUMNSTORE_LARGE_XFAIL`). Tests: `tests/test_tabletype_cci_large_coverage.py`.

**Command:** `tabletype-cci-large`
**Generation:** `all-versions --suite tabletype-cci-large`

---

### K-2 ✅ — `boundarycoverage_datetime_full.bak`: decimal / bit / date-time boundary tests

**Status: FIXED**

**Problem**
`boundary_matrix.py` covered 8 types (`bigint`, `int`, `smallint`, `tinyint`,
`money`, `smallmoney`, `real`, `float`) but was missing integer-mapped CCI types
with their own boundary/encoding challenges.

**Fix**
Created `tools/boundary_datetime_matrix.py` and `tools/make_boundary_datetime_fixture.py`
producing `boundarycoverage_datetime_full.bak` with 9 tables × 1,200 rows (6 labeled
boundary rows + 1,194 fillers, enough for a compressed CCI segment):

| Table | SQL type | Labeled rows |
|---|---|---|
| `tb_bit` | `BIT` | zero, one (×3), null |
| `tb_decimal_9_4` | `DECIMAL(9,4)` | min, max, zero, near_min, near_max, null |
| `tb_decimal_18_4` | `DECIMAL(18,4)` | min, max, zero, near_min, near_max, null |
| `tb_date` | `DATE` | min, max, epoch, pre_epoch, near_max, null |
| `tb_datetime` | `DATETIME` | min, max, sec_min, sec_max, mid, null |
| `tb_datetime2_3` | `DATETIME2(3)` | min, max, epoch, pre_epoch, near_max, null |
| `tb_time_3` | `TIME(3)` | min, max, midnight, near_max, mid, null |
| `tb_smalldatetime` | `SMALLDATETIME` | min, max, epoch, near_max, mid, null |
| `tb_datetimeoffset_3` | `DATETIMEOFFSET(3)` | min, max, epoch, plus14, minus14, null |

**Two decoder bugs fixed in the process:**

1. **Rust `decode_cs_segment` Hybrid RLE fallback** (`rust/src/columnstore.rs`): For
   enc=1/2 segments where `nw × vpw < n_rows`, the segment uses Hybrid RLE encoding
   with BITPACK_REF entries (`0xFFFFFFFF`).  The Rust compact-null sentinel scan
   misidentified these entries as null-prefix sentinels, producing all-None output for
   `cci_bit` (1,200 rows → 1,200 None).  Fix: return `None` for enc=1/2 when
   `n_stored < n_rows`, delegating to the Python Hybrid RLE path.

2. **Python `_decode_enc1` enc=2 Hybrid RLE bitpack ordering** (`mssqlbak/columnstore.py`):
   For enc=2 segments (SQL Server 2016 and earlier, negative `mag`), the Hybrid RLE
   bitpack stores values in **descending** order: `sv=1` → maximum value, `sv=2` → next
   lower, etc.  The previous code used bias-1 (`sv − 1`) which is correct for enc=1
   (ascending), but inverted all non-null BIT values for enc=2.  Fix: use
   `null_val − sv` as the debiased offset for enc=2 Hybrid RLE bitpack entries.

**Tests:** `tests/test_boundary_datetime_coverage.py` — 9/9 pass across SS2017–SS2025.

**Command:** `boundary-datetime`
**Generation:** `all-versions --suite boundary-datetime`

---

### K-3 ✅ — Large-row-group CCI: `char(n)`, `binary(n)`, `varbinary(n)`, `uniqueidentifier` never in compressed segments

**Problem**
Combining all existing large-row-group CCI fixtures, the following
dictionary-encoded types still have zero compressed-segment coverage:

| Type | Why it matters in CCI | Present in small CCI? | Present in large CCI? |
|---|---|---|---|
| `char(n)` | Fixed-stride dict pool (vs `varchar` variable-stride) | ✅ tt_column deltastore | ❌ |
| `binary(n)` | Fixed binary pool | ✅ tt_column deltastore | ❌ |
| `varbinary(n)` | Variable binary pool | ✅ tt_column deltastore | ❌ |
| `uniqueidentifier` | Fixed 16-byte pool entries | ✅ tt_column deltastore | ❌ |
| `bit` | Boolean bitpack | ✅ tt_column deltastore | ❌ |

All five types encode differently in a compressed CCI segment from how they
encode in an uncompressed rowstore (`typecoverage`) or in a deltastore
(`tabletypecoverage`).  A stride or pool-format bug for any of these produces
silent wrong values without a large-row-group CCI fixture.

**Proposed fix:** A dedicated `cci_types_large` fixture with one table per
type, 1,200+ rows, REORGANIZE to force segment compression:

```sql
CREATE TABLE cci_char (id INT NOT NULL, val CHAR(20) NULL);
CREATE CLUSTERED COLUMNSTORE INDEX cci ON cci_char;
-- insert 1200 rows, then REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)
```

**Status: ✅ FIXED** — `cci_types_large_full.bak` generated SS2019–SS2025; one table per type, 1,200+ rows with REORGANIZE forcing real segment compression. Per-type tests for row count, NULL row, low/high boundary values, and `classify_table`. Tests: `tests/test_cci_types_large_coverage.py`.

**Command:** `cci-types-large`
**Generation:** `all-versions --suite cci-types-large`

---

### K-4 ✅ — `compressioncoverage_full.bak`: main column set missing `bigint`, `char(n)`, `binary(n)`, `varbinary(n)`, `uniqueidentifier` under ROW/PAGE compression

**Status:** FIXED

**What was missing:** `_COLS` in `compressionmatrix.py` (shared across `cmp_none`, `cmp_row`,
`cmp_page`, `cmp_columnstore`, `cmp_columnstore_archive`) did not include:

| Type | ROW/PAGE compressed encoding difference |
|---|---|
| `bigint` | 8-byte with leading-zero stripping under ROW |
| `smallint` | 2-byte with leading-zero stripping |
| `tinyint` | 1-byte; trivial but absent from the round-trip test |
| `bit` | Boolean packing in CD record |
| `money` / `smallmoney` | 8/4-byte money types |
| `char(n)` | Trailing-space stripping under ROW/PAGE |
| `binary(n)` | Trailing-zero stripping under ROW/PAGE |
| `varbinary(n)` | Variable binary in CD record |
| `uniqueidentifier` | 16-byte GUID round-trip |

**Fix applied:**
- Extended `_COLS` with all 10 types (`big bigint`, `si smallint`, `ti tinyint`, `bf bit`, `mon money`, `smon smallmoney`, `ch char(10)`, `bn binary(10)`, `vbn varbinary(20)`, `uid uniqueidentifier`).
- Updated `_COL_NAMES` and `_row_literal()` with deterministic values chosen to trigger the relevant encoding paths (e.g., `binary(10)` hex literal with 8 trailing zero bytes to exercise trailing-zero stripping; `char(10)` 4-char value padded to 10 by SQL Server for trailing-space stripping; `bigint = i × 10,000,000` for multi-byte excess encoding).
- Added `test_k4_extra_cols_match_baseline` in `tests/test_rowcompress.py`: parametrised over `cmp_row` / `cmp_page`, compares all K-4 columns against the `cmp_none` baseline row-for-row with graceful skip if fixture predates the fix.

**Command:** `compressionmatrix` (extended existing fixture, no new command)
**Generation:** re-run `all-versions --suite compressionmatrix`

---

### K-5 — `featurecoverage_full.bak` ncci_table: only 4 types in NCCI ✅ IMPLEMENTED

**Problem**
The `ncci_table` table that carries the Non-Clustered Columnstore Index has only
four column types: `INT` (id), `INT` (code), `NVARCHAR(100)` (name),
`DECIMAL(10,2)` (amount).  The NCCI is built on `code` and `amount` only.

NCCI uses the same segment encoding as CCI.  All CCI-compatible types that are
absent from `ncci_table` have never been tested via the NCCI decoder:
`bigint`, `smallint`, `tinyint`, `bit`, `money`, `smallmoney`, `real`, `float`,
`date`, `datetime2`, `time`, `smalldatetime`, `datetime`, `datetimeoffset`,
`char(n)`, `nchar(n)`, `varchar(n)`, `binary(n)`, `varbinary(n)`,
`uniqueidentifier`.

The NCCI also differs from CCI in that it stores a separate row-locator column
(the RID or clustered-key pointer) beside each segment.  A type-dependent
row-locator parsing bug would be masked without broader type coverage.

**Fix applied:** Standalone `ncci_types_full.bak` fixture created with 19 tables,
one per type, each with a `NONCLUSTERED COLUMNSTORE INDEX` on the value column
and 1,203 rows (structural low/high/null + 1,200 fillers flushed to a compressed
row group via `REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)`):

```sql
CREATE TABLE ncci_bigint (id INT NOT NULL PRIMARY KEY CLUSTERED, val BIGINT NULL);
CREATE NONCLUSTERED COLUMNSTORE INDEX ncci_ncci_bigint ON ncci_bigint (val);
-- insert 1203 rows, then REORGANIZE
```

Types covered: `BIGINT`, `SMALLINT`, `TINYINT`, `BIT`, `FLOAT`, `REAL`, `MONEY`,
`SMALLMONEY`, `DATE`, `DATETIME2(3)`, `TIME(3)`, `DATETIMEOFFSET(3)`, `CHAR(10)`,
`NCHAR(10)`, `VARCHAR(50)`, `NVARCHAR(50)`, `BINARY(8)`, `VARBINARY(8)`,
`UNIQUEIDENTIFIER`.

Tests in `tests/test_ncci_types_coverage.py`: row count, NULL row, low boundary,
high boundary, and `classify_table` support check — all parametrised over all 19
table definitions.

**Command:** `ncci-types`
**Generation:** `all-versions --suite ncci-types`

---

## Related files

- `docs/FIXTURE_GAPS.md` — existing per-gap tracker with status, evidence, and next steps
- `tools/make_archive_null_fixture.py` — Gap 5 unpartitioned CCI fixture
- `tools/make_archive_columnstore_partition_fixture.py` — Gap 5 partitioned CCI fixture
- `tests/test_archive_null_coverage.py`
- `tests/test_archive_columnstore_partition_coverage.py`
