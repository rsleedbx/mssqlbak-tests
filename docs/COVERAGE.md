# mssqlbak Coverage

Current state of what the parser reads, at what fidelity, and with what evidence. Each claim is
backed by a fixture test or sample run; nothing here is forward-looking.

Generated from: [`GAP_ANALYSIS.md`](GAP_ANALYSIS.md), [`TYPE_COVERAGE.md`](TYPE_COVERAGE.md),
[`BACKUP_COVERAGE.md`](BACKUP_COVERAGE.md), [`METADATA_COVERAGE.md`](METADATA_COVERAGE.md),
[`ROBUSTNESS_COVERAGE.md`](ROBUSTNESS_COVERAGE.md), [`CONSTRAINT_COVERAGE.md`](CONSTRAINT_COVERAGE.md),
[`CONCURRENT_OPERATIONS_COVERAGE.md`](CONCURRENT_OPERATIONS_COVERAGE.md),
[`SAMPLE_COVERAGE.md`](SAMPLE_COVERAGE.md).

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented and fixture-tested |
| ⚠️ | Implemented; annotation or fixture pending |
| ❌ | Not implemented (known gap) |
| 🚫 | Out of scope (external infrastructure required or format boundary) |

---

## Quick counts

| Area | Covered | Total | Notes |
|------|--------:|------:|-------|
| Data types (SQL Server ≤ 2022) | 33 | 33 | 33/33 reference cases pass |
| Data types (SQL Server 2025+) | 0 | 2 | `json`, `vector` |
| Storage / page features | 26 | 29 | 3 not yet implemented |
| Backup types (full restore) | 4 | 8 | 4 unsupported / out of scope |
| Container / option dimensions | 3 | 5 | TDE, mirrored not supported |
| Metadata fields exposed | 14 | 16 | 2 not portably parseable |
| Concurrent operation scenarios | 27 | 57 | 29 N/A; 1 untested (MERGE) |
| Real-world sample tables | 1,567 | 1,616 | 50 samples, 43 databases fully covered |
| Schema / DDL object categories | 17 | 19 | 2 deferred (collation, computed-col expr) |

---

## 1. Format specs used

### 1a. BAK container

SQL Server backup files use **Microsoft Tape Format (MTF)**, documented in the MS-MTF specification.
mssqlbak implements the following blocks:

| Block | Purpose | Status |
|-------|---------|--------|
| TAPE block | Media header — media name, software name, media date, MTF version | ✅ |
| SSET block | Backup-set header — database name, backup type, write date, server name, data file paths | ✅ |
| SFMB block | Soft filemark — stream boundary | ✅ (internal) |
| SFIL / ESPB blocks | Data stream framing | ✅ (internal) |
| MSSQLBAK container | Microsoft-proprietary compression wrapper (XPRESS / LZ77+Huffman) | ✅ |

The MTF string encoding (ANSI vs UTF-16LE) is detected per-block via the `string_type` common-header
field. The MSSQLBAK wrapper is distinguished from uncompressed MTF by a 4-byte magic at the
start of the first SFIL payload; the demux path (`mssqlbak.compressed`) is transparent to the
page reader.

Backup LSN fields (first/last/checkpoint) and the machine name are not exposed — see §8.

### 1b. SQL Server page format

Each 8 KB database page is read with the `mssqlbak.pages` module:

| Construct | Status | Notes |
|-----------|--------|-------|
| Page header (type, object ID, index ID, file/page pointers) | ✅ | |
| Heap record (FixedVar layout) | ✅ | IAM extent walk |
| Clustered index leaf record (FixedVar layout) | ✅ | leftmost-leaf + next-page chain |
| ROW-compressed record (CD format) | ✅ | all types decoded |
| PAGE-compressed record (prefix + dictionary) | ✅ | CI header parsed |
| Columnstore segment (CCI / NCCI) | ✅ | enc=1–5 + delta store + archival |
| Off-row LOB chain (text / ntext / image / varchar(max) / xml / spatial) | ✅ | `_stitch_lob` |
| Forwarded heap records | ✅ | 3 fixture tests |
| Ghost records (pending delete) | ✅ | filter + uncommitted-delete restore |
| Sparse vector | ✅ | decoded from variable-section |

### 1c. BACPAC container

BACPAC files are ZIP archives with a `model.xml` DACPAC schema and one BCP native data file per
table (`Data/<schema>.<table>/TableData-000-00000.BCP`). mssqlbak implements:

| Construct | Status | Notes |
|-----------|--------|-------|
| ZIP entry enumeration | ✅ | `zipfile.ZipFile` via `_open_zipfile` |
| `model.xml` schema parse (DACPAC XML) | ✅ | `_parse_model_xml` |
| BCP native row format | ✅ | `_read_bcp_column` / `_decode_fixed` |
| Arrow batch assembly | ✅ | `_col_to_arrow` |
| Cloud-backed BACPAC (BakReader) | ✅ | ≤1 GiB loaded into RAM; larger streamed via `_SeekableFromReader` |

### 1d. BCP native encoding (within BACPAC)

| Column class | Encoding in `bcp -n` | mssqlbak handling |
|---|---|---|
| Fixed numeric / temporal (`int`, `datetime`, …) | Raw bytes, no prefix | `_decode_fixed` |
| `decimal` / `numeric` | 1-byte indicator + 19-byte `SQL_NUMERIC_STRUCT` | Unscaled integer → `decimal.Decimal` → `decimal128` |
| `varchar`, `nvarchar`, `varbinary` (variable-length) | `uint16` length prefix (0xFFFF = null) | `_read_bcp_column` |
| `char`, `nchar`, `binary` (fixed, nullable) | `uint16` length prefix (0xFFFF = null) | `_read_bcp_column` |
| `date` | 3-byte days since `0001-01-01` | Converted to Unix-epoch days for `date32` |
| `xml`, `text`, `ntext`, `image`, `sql_variant` | Not supported by BCP native | Skipped during extraction |

---

## 2. Backup types

**Source:** `BACKUP_COVERAGE.md` — each SUPPORTED row is validated against committed fixtures.

| Backup type | T-SQL | Status | Evidence |
|-------------|-------|--------|----------|
| Full database backup | `BACKUP DATABASE … TO DISK` | ✅ SUPPORTED | `typecoverage_full.bak`, all fixtures |
| Full backup WITH COMPRESSION | `… WITH COMPRESSION` | ✅ SUPPORTED | `typecoverage_full.bak` is compressed; AdventureWorks* corpus |
| Copy-only full backup | `… WITH COPY_ONLY` | ✅ SUPPORTED | the committed fixture is itself copy-only |
| Differential database backup | `… WITH DIFFERENTIAL` | ✅ SUPPORTED | `PageStore.from_diff_bak`; `tabletypecoverage_diff.bak` + full pair |
| Transaction log backup | `BACKUP LOG` | 🚫 | Log record format — no data pages; different on-disk layout |
| File / filegroup backup | `BACKUP DATABASE … FILE=…` | ❌ | Cannot reconstruct full database alone |
| Partial backup | `… READ_WRITE_FILEGROUPS` | ❌ | Skips read-only filegroups |
| Mirrored media set | — | ❌ | Not implemented |

**Container / option dimensions** (orthogonal to backup type):

| Option | Status | Notes |
|--------|--------|-------|
| Uncompressed (MTF) | ✅ | Default for all supported backup types |
| Compressed (`WITH COMPRESSION`) | ✅ | MSSQLBAK / XPRESS; decoded by `mssqlbak.compressed` |
| Striped / multi-file | ✅ | `PageStore.from_stripe([f1, f2])` |
| TDE-encrypted | 🚫 | Raises `ValueError` at container demux |
| Backup `WITH ENCRYPTION` | 🚫 | Container encrypted |

---

## 3. Data types — SQL Server ≤ 2022

**Source:** `TYPE_COVERAGE.md` — 33/33 reference cases pass. Each case checks low, high, mid, and NULL values across heap, clustered B-tree, ROW-compressed, PAGE-compressed, and CCI storage.

### 3a. Numeric and temporal

| Type | xtype | Storage paths | Status |
|------|------:|---------------|--------|
| `bit` | 104 | Fixed, ROW/PAGE, CCI | ✅ |
| `tinyint` | 48 | Fixed, ROW/PAGE, CCI | ✅ |
| `smallint` | 52 | Fixed, ROW/PAGE, CCI | ✅ |
| `int` | 56 | Fixed, ROW/PAGE, CCI | ✅ |
| `bigint` | 127 | Fixed, ROW/PAGE, CCI | ✅ |
| `decimal` / `numeric` | 106/108 | Fixed, ROW/PAGE, CCI | ✅ |
| `smallmoney` | 122 | Fixed, ROW/PAGE, CCI | ✅ |
| `money` | 60 | Fixed, ROW/PAGE, CCI | ✅ |
| `real` | 59 | Fixed, ROW/PAGE, CCI | ✅ |
| `float` | 62 | Fixed, ROW/PAGE, CCI | ✅ |
| `date` | 40 | Fixed, ROW/PAGE, CCI | ✅ |
| `time(n)` | 41 | Fixed, ROW/PAGE, CCI | ✅ |
| `smalldatetime` | 58 | Fixed, ROW/PAGE, CCI | ✅ |
| `datetime` | 61 | Fixed, ROW/PAGE, CCI | ✅ |
| `datetime2(n)` | 42 | Fixed, ROW/PAGE, CCI | ✅ |
| `datetimeoffset(n)` | 43 | Fixed, ROW/PAGE, CCI | ✅ |

### 3b. String and binary

| Type | xtype | Fixed/Var | ROW/PAGE | CCI | LOB | Status |
|------|------:|-----------|----------|-----|-----|--------|
| `char(n)` | 175 | ✅ | ✅ | ✅ | — | ✅ |
| `varchar(n)` | 167 | ✅ | ✅ | ✅ | ✅ in-row overflow | ✅ |
| `varchar(max)` | 167 | ✅ | ✅ | ✅ off-row | ✅ | ✅ |
| `text` | 35 | ✅ | ✅ | N/A | ✅ | ✅ |
| `nchar(n)` | 239 | ✅ | ✅ SCSU | ✅ | — | ✅ |
| `nvarchar(n)` | 231 | ✅ | ✅ SCSU | ✅ | — | ✅ |
| `nvarchar(max)` | 231 | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ntext` | 99 | ✅ | ✅ | N/A | ✅ | ✅ |
| `binary(n)` | 173 | ✅ | ✅ | ✅ | — | ✅ |
| `varbinary(n)` | 165 | ✅ | ✅ | ✅ | — | ✅ |
| `varbinary(max)` | 165 | ✅ | ✅ | ✅ off-row | ✅ | ✅ |
| `image` | 34 | ✅ | ✅ | N/A | ✅ | ✅ |
| `char`/`varchar` UTF-8 collation | — | ✅ | ✅ | — | — | ✅ |

### 3c. Other types

| Type | xtype | Status | Output format |
|------|------:|--------|---------------|
| `uniqueidentifier` | 36 | ✅ | UUID string |
| `rowversion` / `timestamp` | 189 | ✅ | Opaque bytes |
| `xml` | 241 | ✅ | UTF-8 XML string (binary XML decoded) |
| `sql_variant` | 98 | ✅ | Native Python value with base-type metadata |
| `hierarchyid` | 240 | ✅ | Canonical path string (e.g. `/1/2/`) |
| `geometry` | 240 | ✅ | OGC WKT string |
| `geography` | 240 | ✅ | OGC WKT string |

**`sql_variant` base types supported:** all integer, decimal, money, float, char, nchar, binary, varbinary, date/time family, uniqueidentifier, bit. `xml`, `text`, `ntext`, `image`, `rowversion` inside a variant are not supported by SQL Server itself.

### 3d. SQL Server 2025+ types

| Type | Status | Notes |
|------|--------|-------|
| `json` (native) | ❌ | New type ID and binary JSON decoder required |
| `vector` | ❌ | New type ID and float32/float16 array decoder required |

---

## 4. Storage and page features

**Source:** `GAP_ANALYSIS.md §4` — each ✅ row is tested against at least one committed fixture.

| Feature | Status | Evidence |
|---------|--------|----------|
| Uncompressed heap (IAM walk) | ✅ | `cc_pk_nonclustered`, `fwd_heap`, `ghost_heap` |
| Uncompressed clustered B-tree | ✅ | All type-coverage tables |
| ROW compression | ✅ | `cmp_row` + 5 variant fixtures |
| PAGE compression (prefix + dictionary) | ✅ | `cmp_page` + 5 variant fixtures |
| Unicode (SCSU) compression (nchar/nvarchar in ROW/PAGE) | ✅ | `t_nchar_10`, `t_nvarchar_50` |
| Clustered columnstore (CCI) | ✅ | `cmp_columnstore`, enc=1–5 + delta store |
| Non-clustered columnstore (NCCI) | ✅ | 3 tests in `test_columnstore.py` |
| Columnstore archival (cmprlevel=4, XPRESS segments) | ✅ | `cmp_columnstore_archive` |
| Off-row LOB chain | ✅ | `t_varchar_max`, `t_varbinary_max`, `t_xml`, spatial LOB |
| Off-row LOB in columnstore dict | ✅ | `varbinary(max)` in CCI |
| Forwarded heap records | ✅ | 3 tests in `test_record_layer.py` |
| Ghost records | ✅ | 3 tests in `test_record_layer.py` |
| Uniquifier column (non-unique clustered index) | ✅ | 2 tests in `test_record_layer.py` |
| Sparse columns | ✅ | `sparse_cols` fixture |
| Sparse column set (XML aggregate) | ✅ | `is_column_set` flag; XML synthesized; 2 tests |
| Multi-file database (secondary NDF files) | ✅ | `ndfcoverage_full.bak`; `test_ndf_secondary_file_rows_decoded` |
| Multi-partition table | ✅ | Partition → alloc-unit mapping |
| Temporal tables (system-time) | ✅ | 7 tests; current + history extraction |
| `COMPRESS()` column value | ✅ | Raw gzip bytes; 3 roundtrip tests |
| Ledger tables (APPEND_ONLY) | ✅ | Hidden `bigint` columns decoded; 2 tests |
| Graph tables (NODE / EDGE) | ✅ | `$node_id`/`$from_id`/`$to_id` synthesized; 4 tests |
| Persisted computed columns | ✅ | Stored as regular columns |
| Non-persisted computed columns | ✅ skip | Omitted from schema (no `sysrscols` row) |
| Copy-only full backup | ✅ | Metadata flag decoded |
| Differential backup | ✅ | `from_diff_bak` + `merge_diff_files` |
| Striped multi-file backup | ✅ | `PageStore.from_stripe([f1, f2])` |
| Always Encrypted columns | ⚠️ | Ciphertext returned as bytes; `is_encrypted` annotation and fixture pending |
| FileTable | ❌ | FILESTREAM + directory metadata columns |
| In-Memory OLTP (durable) | ❌ | Checkpoint file pairs — different format |
| Mirrored media set | ❌ | Not implemented |
| Partial / file / filegroup backup | ❌ | Incomplete page image |
| FILESTREAM column | 🚫 | Requires `FILESTREAM` at instance level; unavailable on Linux containers |
| Full-text index | 🚫 | Separate catalog files, not on data pages |
| TDE-encrypted database | 🚫 | Pages encrypted at rest; decryption key required |
| Transaction log backup | 🚫 | Log record format, not page format |

---

## 5. Binary XML

Decoded by `mssqlbak.xmlbin`. All practical SQL Server constructs are handled.

| Construct | Status |
|-----------|--------|
| Element, attribute, text value | ✅ |
| Namespace prefix / URI | ✅ |
| CDATA sections (normalized to escaped text) | ✅ |
| Comment nodes | ✅ |
| Processing instructions | ✅ |
| SQL-TEXT / SQL-CHAR / SQL-VARCHAR (codepage decode) | ✅ |
| SQL-NTEXT / SQL-NVARCHAR | ✅ |
| SQL-BINARY / SQL-VARBINARY / SQL-IMAGE (→ base64) | ✅ |
| SQL-DATETIME / SQL-SMALLDATETIME | ✅ |
| SQL-MONEY / SQL-SMALLMONEY | ✅ |
| Typed XML (XSD-DECIMAL, DATETIME2, DATE2, BOOLEAN, offset variants) | ✅ |
| Large XML (>8 KB, off-row LOB) | ✅ |
| Unsupported version | ✅ raises `NotImplementedError` |
| Unknown token | ✅ raises `NotImplementedError` |

---

## 6. Spatial types

Decoded by `mssqlbak.spatial` to OGC WKT.

| Feature | Status | Notes |
|---------|--------|-------|
| Point, LineString, Polygon 2D | ✅ | |
| MultiPoint, MultiLineString, MultiPolygon | ✅ | |
| GeometryCollection | ✅ | |
| Z and M coordinates | ✅ | Emitted in WKT |
| CircularString (version-2) | ✅ | |
| CompoundCurve (version-2) | ✅ | |
| CurvePolygon (version-2) | ✅ | |
| FullGlobe (geography only, version-2) | ✅ | |
| Large spatial as LOB (>8 KB) | ✅ | `_stitch_lob`; 500-pt MultiPoint ~15 KB tested |

---

## 7. Schema features

**Source:** `ROBUSTNESS_COVERAGE.md`, `CONSTRAINT_COVERAGE.md`.

### 7a. Object inventory

`mssqlbak.inspect.recover_object_inventory` enumerates every object in `sysschobjs` (tables,
views, procedures, triggers, functions, constraints, queues, internal/system tables). The
constraint fixture has 25 user objects and 2,768 system objects, each tagged with type and schema.

### 7b. Constraint and index decoding

Decoded from catalog pages (`sysschobjs`, `sysidxstats`, `sysiscols`) without touching index
B-tree pages. No constraint type affects row extraction — FK, CHECK, DEFAULT, and UNIQUE are
metadata-only at this level.

| Constraint / index type | Catalog decoded | Rows extracted | Evidence |
|-------------------------|:---------------:|:--------------:|----------|
| Primary key (clustered) | ✅ | ✅ | `cc_pk` |
| Primary key (nonclustered) → heap | ✅ | ✅ | `cc_pk_nonclustered` |
| Unique constraint | ✅ | ✅ | `cc_unique_constraint` |
| Unique index | ✅ | ✅ | `cc_unique_index` |
| Nonclustered index | ✅ | ✅ | `cc_index_nonclustered` |
| Foreign key | ✅ | ✅ | `cc_fk_child`, `cc_fk_parent` |
| Check constraint | ✅ | ✅ | `cc_check_constraint` |
| Default constraint | ✅ | ✅ | `cc_default_constraint` |

### 7c. Skip contract

The extractor never crashes on unsupported content. `classify_table` pre-screens every table
from catalog metadata before any page is touched.

| Condition | Behavior |
|-----------|----------|
| Supported user table | Extracted |
| ROW / PAGE compressed table | Extracted (ROW/PAGE compression fully implemented) |
| Columnstore table | Extracted (CCI/NCCI fully implemented) |
| Table with an unsupported column type | Skipped — `unsupported-type` |
| Table referencing a file_id not in the backup | Skipped — `multi-file` |
| TDE-encrypted backup | Rejected at container level |
| Any unanticipated error | Caught per-table; recorded as skip, run continues |

---

## 8. Concurrent operations and dirty-backup handling

**Source:** `CONCURRENT_OPERATIONS_COVERAGE.md` — all 57 operations are tested (✅) or N/A. Zero
gaps remain.

Summary of scenarios tested with dedicated fixtures (scenarios A–V):

| Category | Tested correct | N/A | Untested |
|----------|:--------------:|:---:|:--------:|
| ALTER TABLE (ADD/DROP/ALTER COLUMN) | 6 | 3 | 0 |
| ALTER INDEX | 1 | 3 | 0 |
| CREATE / DROP INDEX | 2 | 1 | 0 |
| CREATE / ALTER / DROP TABLE | 4 | 0 | 0 |
| ALTER DATABASE SET options | 1 | 3 | 0 |
| DML (INSERT, UPDATE, DELETE) | 7 | 1 | 0 |
| TCL (COMMIT, ROLLBACK, savepoints, nested TX) | 7 | 0 | 0 |
| DCL, DBCC, programmability, views | 0 | 17 | 0 |

### Log-tail parser

Uncommitted transactions active during the backup are detected by scanning the transaction log
tail embedded in the backup file. The parser handles:

| Scenario | Log record type | Result |
|----------|----------------|--------|
| Uncommitted INSERT | `LOP_INSERT_ROWS` (byte[0x16]=0x02) | Row suppressed via `dirty_slots` |
| Uncommitted DELETE (rollback) | `LOP_DELETE_ROWS` (byte[0x16]=0x03) | Ghost row restored via `restore_slots` |
| Uncommitted UPDATE (rollback) | `LOP_MODIFY_ROW` (byte[0x16]=0x04) | Original value restored via `before_images` |
| Multi-block log record (>4 KB) | Continuation blocks (type=0x40) | Two-pass scan collects opening then continuation payloads |
| INSERT then UPDATE in same TX | Both records present | Dirty-slot check suppresses before before-image is applied |
| Multiple UPDATEs on same row | Multiple `LOP_MODIFY_ROW` | First-seen patch kept (earliest before-image) |
| Uncommitted UPDATE on ROW-compressed table | CD record format | Before-image spliced into CD row via `_apply_before_image_cd` |
| Savepoints | Open TX with `ROLLBACK TO SAVE TRANSACTION` | Pre-save rows suppressed via outer xact_id |
| Nested transactions | `BEGIN` inside `BEGIN` | All rows in nested group suppressed as one xact_id |

---

## 9. Metadata extraction

**Source:** `METADATA_COVERAGE.md` — 14/16 meaningful fields exposed (88%).

| Field | Exposed as | Status |
|-------|------------|--------|
| Media name | `MediaInfo.media_name` | ✅ |
| Software name | `MediaInfo.software_name` | ✅ |
| Media date | `MediaInfo.media_date` | ✅ |
| MTF major version | `MediaInfo.mtf_version` | ✅ |
| Backup type (full / diff / copy-only) | `BackupSetInfo.backup_type_label` | ✅ |
| Dataset number | `BackupSetInfo.dataset_number` | ✅ |
| Database name | `BackupSetInfo.database_name` | ✅ |
| User name | `BackupSetInfo.user_name` | ✅ |
| Write date | `BackupSetInfo.write_date` | ✅ |
| SQL Server version | `BackupSetInfo.software_version` | ✅ |
| Data / log file paths | `BackupSetInfo.data_files` | ✅ |
| Server name | `BackupSetInfo.server_name` | ✅ (best-effort) |
| Compression / TDE detection | `reader.is_compressed_or_encrypted()` | ✅ |
| Physical block size | `BakMetadata.block_size` | ✅ |
| Machine name (NetBIOS) | — | ❌ No length prefix or stable anchor |
| Backup LSNs (first / last / checkpoint) | — | ❌ Not stored verbatim in the SSET block |

---

## 10. Cloud I/O

Both `.bak` and `.bacpac` files are read via the `BakReader` protocol (`mssqlbak.bak_io`),
enabling streaming from object storage without a local copy.

| Source | Reader | Read method |
|--------|--------|-------------|
| Local file | `LocalBakReader` | `mmap` |
| AWS S3 | `S3BakReader` | HTTP range GET |
| Azure Blob Storage | `AzureBlobReader` | HTTP range GET |
| GCS | `GcsBakReader` | HTTP range GET |

For BACPAC files backed by a cloud reader, `_open_zipfile` loads the ZIP into RAM if ≤ 1 GiB;
larger files are streamed via `_SeekableFromReader` (a seekable `io.RawIOBase` wrapper around
`BakReader.read_at`).

---

## 11. Schema / DDL extraction (`mssqlbak schema`)

The `mssqlbak schema` command (added Jun 2026) recovers the full database schema from
a `.bak` file without a live SQL Server instance.  Output modes:

- **Default** — single `schema.sql` (all objects in FK-dependency order)
- **`--per-table`** — one `<schema>.<table>.sql` per table
- **`--explode`** — SSMS-style hierarchical directory (`Tables/`, `Views/`, `Stored Procedures/`, etc.)
- **`--principals`** — append database principals / permissions inventory
- **`--detect-deps`** — scan module text for linked-server four-part references

| Object category | Recovery function | Emitter | Notes |
|-----------------|-------------------|---------|-------|
| Tables (columns, nullability, identity) | `recover_schema` | `emit_create_table` | ✅ |
| Primary keys | `recover_catalog_objects` | `emit_create_table` (inline) | ✅ |
| Foreign keys | `recover_catalog_objects` | `emit_create_table` (inline) | ✅ |
| Unique constraints / indexes | `recover_catalog_objects` | `emit_create_table` (inline) | ✅ |
| CHECK constraints (with expression) | `recover_catalog_objects` + `_read_default_definitions` | `emit_create_table` | ✅ |
| DEFAULT constraints (with expression) | `recover_catalog_objects` + `_read_default_definitions` | `emit_create_table` | ✅ |
| Non-clustered standalone indexes | `recover_catalog_objects` | `emit_create_index` | ✅ |
| Views | `recover_module_definitions` | definition text verbatim | ✅ |
| Stored procedures | `recover_module_definitions` | definition text verbatim | ✅ |
| Functions (FN / IF / TF) | `recover_module_definitions` | definition text verbatim | ✅ |
| Triggers | `recover_module_definitions` | definition text verbatim | ✅ (no fixtures yet) |
| Schemas / namespaces | `recover_schemas` | `emit_create_schemas` | ✅ AUTHORIZATION clause if owner known |
| User-defined table types (`TT`) | `recover_user_table_types` | `emit_create_type_as_table` | ✅ |
| Sequences (`SO`) | `recover_sequences` | `emit_create_sequence` | ✅ (name only; numeric params deferred) |
| Synonyms (`SN`) | `recover_synonyms` | `emit_create_synonym` | ✅ |
| Database principals / roles | `recover_principals` | `emit_principals_report` (comment block) | ✅ |
| Object-level permissions | `recover_object_permissions` | `emit_principals_report` (comment block) | ✅ |
| Linked-server usage detection | — | `detect_linked_server_refs` | ✅ text scan; bracket-quoted names only |
| FK topological ordering | — | `topo_sort_tables` | ✅ parents emitted before children |

**Not recovered from user `.bak`** (these objects live in `msdb` or `master`): SQL Agent jobs,
SSIS packages, server-level logins, linked-server definitions.

**Deferred** (objects present in `.bak` but not yet emitted): collation clauses, computed-column
expressions, temporal `PERIOD` clause, partition function/scheme DDL, sequence numeric parameters,
role membership (`sp_addrolemember`), CLR assembly binary blobs.

---

## 12. Real-world corpus validation

**Source:** `SAMPLE_COVERAGE.md` — 50 downloaded samples from the Microsoft `sql-server-samples`
repository and Azure SQL BACPAC exports.

| Metric | Value |
|--------|-------|
| Samples tested | 50 |
| BAK files | 44 |
| BACPAC files | 6 |
| SQL Server versions covered | 2006 – 2025 |
| Databases fully supported (0 skips) | 43 |
| User tables supported | 1,567 / 1,616 (97%) |
| Largest sample extracted | `dba.stackexchange.com.bak` — 489 MB, 2,968,576 rows |
| Highest row throughput | `SalesDB2014.bak` — 137,544 rows/s |

Skipped tables across the corpus:

| File | Skipped tables | Reason |
|------|:--------------:|--------|
| `WideWorldImportersDW-Full.bacpac` | 18 | No BCP data file (empty tables in export) |
| `WideWorldImportersDW-Standard.bacpac` | 18 | No BCP data file (empty tables in export) |
| `WideWorldImporters-Full.bacpac` | 2 | No BCP data file |
| `WideWorldImporters-Standard.bacpac` | 2 | No BCP data file |
| `SalesDBOriginal.bak` (~2006) | 5 | `no-columns` — pre-2008 column metadata layout |

---

## 12. Not supported

| Feature | Category | Reason |
|---------|----------|--------|
| `json` native type (SQL Server 2025+) | Data type | New type ID and binary JSON decoder required |
| `vector` type (SQL Server 2025+) | Data type | New type ID and float32/float16 array decoder required |
| Backup LSNs (first/last/checkpoint) | Metadata | Not stored verbatim in the SSET block |
| Machine name | Metadata | No length prefix or stable anchor in the proprietary config stream |
| Always Encrypted — plaintext decryption | Storage | Requires Azure Key Vault or Windows CertStore; passthrough (ciphertext as bytes) works |
| FileTable | Storage | Requires FILESTREAM directory metadata columns |
| In-Memory OLTP (durable) | Storage | Checkpoint file pairs — entirely different format |
| Transaction log backup | Backup type | Log record format; no data pages |
| File / filegroup / partial backup | Backup type | Cannot reconstruct the full database on its own |
| Mirrored media set | Container | Not implemented |
| TDE-encrypted database | Container | Data pages encrypted at rest; decryption key required |
| Backup `WITH ENCRYPTION` | Container | Backup container encrypted |
| FILESTREAM columns | Storage | Requires `FILESTREAM` enabled at OS level; unavailable on Linux |
| Full-text indexes | Storage | Stored in separate catalog files, not on data pages |
