# Test Fixtures to Formalize BAK Format Guesses

Each section corresponds to one or more **Guess IDs** (`Gnn`) in the Guess
Register (`BAK_FORMAT_SPEC.md` §10).  For each item we describe: what the guess
is, which existing asset already covers it (if any), what new fixture to create,
the independent verifier that confirms it, and the assertion.

---

## §0 — Method (read first)

### Rule 1: reuse before you build

The repo already has 30+ fixtures and a dozen generators.  **Most guesses can be
investigated with bytes we already have** — do not generate a new `.bak` until
you've confirmed the existing ones don't exercise the case.  Inventory:

| Existing fixture | Generator | Covers |
|------------------|-----------|--------|
| `typecoverage_full.bak` | `python -m tools.fixture_run make_fixture` | all types, FixedVar, page header, catalog, LOB pointers |
| `typecoverage_full_compressed.bak` | (compressed variant) | MSSQLBAK v2 container (G01–G05) |
| `compressioncoverage_full.bak` | `python -m tools.fixture_run compressionmatrix` | ROW/PAGE CD records, CI, vardecimal (G17–G1A, G19) |
| `layoutcoverage_full.bak` | `python -m tools.fixture_run layout` | L01–L03 PK position + column-count boundaries |
| `layoutcoverage_compressed.bak` | `python -m tools.fixture_run layout --compressed` | L01 under PAGE compression |
| `catalog_ss2022.bak` | `python -m tools.fixture_run catalog --engine 2022` | G20–G22 catalog object-id baseline |
| `catalog_ss{2012,2016,2019,2022}.bak` | `python -m tools.fixture_run version-matrix` | cross-version catalog matrix (G21) |
| `mssqlbak_v1_inspect.bak` | `python -m tools.fixture_run version-matrix --v1-inspect` | G01 MSSQLBAK v1 header (needs SQL Server 2012) |
| `dirtycoverage_aborted_xact.bak` | `python -m tools.fixture_run aborted-xact` | G52 aborted transaction log tail |
| `boundarycoverage_full.bak` | `tools/make_boundary_fixture.py` | 1 200-row groups → columnstore enc=4 (G40–G43) |
| `featurecoverage_full.bak` | (forgedb + feature gen) | temporal, COMPRESS(), UTF-8, NCCI |
| `ndfcoverage_full.bak` | `tools/make_ndf_fixture.py` | multi-file, file_id dispatch |
| `constraintcoverage_full.bak` | `tools/constraintmatrix.py` | PK/UQ/FK/CHECK/DEFAULT, identity (G21) |
| `dirtycoverage_*.bak` (20) + `dirty_ground_truth.json` | `tools/make_dirty_fixture.py` | log tail, ghost/forward, DDL/DML during backup (G15, G16, G50–G52) |
| `incrementalcoverage_*.bak` (full + 6 diff) | `tools/make_incremental_fixture.py` | differential merge |

### §0.1 — Generating fixtures

**Prerequisites**

1. A running SQL Server container provisioned by forgedb (`setup_sqlserver_podman`).
2. forgedb2 venv with keyring credentials (default:
   `~/github/forgedb2/.venv/bin/python`).  Override with `FORGEDB_PYTHON` if
   installed elsewhere.
3. mssqlbak venv active (`source .venv/bin/activate` from repo root).

**Standard command** — one invocation; no manual `FIXTURE_DBA_PASSWORD` export:

```bash
# from repo root, mssqlbak venv active
python -m tools.fixture_run <command> [options]
```

| Command | Output fixture |
|---------|----------------|
| `make_fixture` | `tests/fixtures/typecoverage_full.bak` (includes `lob_links` / G30) |
| `compressionmatrix` | `tests/fixtures/compressioncoverage_full.bak` |
| `layout` | `tests/fixtures/layoutcoverage_full.bak` |
| `layout --compressed` | `tests/fixtures/layoutcoverage_compressed.bak` |
| `catalog --engine 2022` | `tests/fixtures/catalog_ss2022.bak` |
| `version-matrix` | `catalog_ss{2012,2016,2019,2022}.bak` (one engine per forgedb container) |
| `version-matrix --engine 2022` | single-engine catalog fixture |
| `version-matrix --v1-inspect` | also `mssqlbak_v1_inspect.bak` (2012 + `--compressed`) |
| `aborted-xact` | `tests/fixtures/dirtycoverage_aborted_xact.bak` |
| `unicode-codepage` | `tests/fixtures/unicode_codepage_coverage.bak` (G55 probe) |

Regenerate the P1 surgical set in one session:

```bash
python -m tools.fixture_run layout
python -m tools.fixture_run make_fixture
python -m tools.fixture_run compressionmatrix
python -m tools.fixture_run catalog --engine 2022
python -m tools.fixture_run aborted-xact
```

**Overrides** (only when auto-discovery fails):

| Variable | Purpose |
|----------|---------|
| `FIXTURE_SERVER_NAME` | forgedb blob stem (e.g. `robert-lee-mssql-local-1779207800`) |
| `FIXTURE_CONTAINER` | podman container name |
| `FORGEDB_PYTHON` | path to forgedb2 venv `python` for keyring lookup |

Print shell exports for a manual shell session:

```bash
eval "$(python -m tools.fixture_run env)"
```

Implementation: `tools/fixture_run.py`.

#### Cursor agent — avoid repeated "Run" approval prompts

Cursor's sandbox allowlist matches the **first token** of each shell command.
Chains that start with `export`, `eval`, or a subprocess to fetch passwords
trigger a "Run" prompt on every invocation even when `python` and `podman` are
allowlisted.

**Do**

```bash
python -m tools.fixture_run make_fixture
```

Run from the repo root (or prefix with `bash -c 'cd … && python -m …'` so
`bash` is the first token — `bash` is on the allowlist).

**Do not**

```bash
export FIXTURE_DBA_PASSWORD="$(…forgedb…)" && export FIXTURE_CONTAINER=… && python -m tools.make_fixture
```

`fixture_run` loads credentials internally via the forgedb2 venv keyring; the
agent never needs to export secrets in the shell command string.

If prompts persist for other tools, add the binary to `~/.cursor/permissions.json`
under `terminalAllowlist`, then **Reload Window** (`Cmd+Shift+P`).  `python`,
`podman`, and `bash` are already listed on this machine.

Inspection tools that already exist — prefer these over ad-hoc scripts:

- `tools/byte_map.py` — 100 % byte accounting of a fixture (page/record/field).
- `tools/probe_log_records.py` — log-tail record dump (G50–G52).
- `tools/make_dirty_fixture.py` — builds fuzzy/dirty backups with ground truth.

### Rule 2: every confirmation needs an independent verifier

A guess is **not** resolved by "our parser round-trips it" — that is circular.
It is resolved when an verifier outside `mssqlbak/` agrees (see
`BAK_FORMAT_SPEC.md §0` for the full list).  Quick reference:

| Layer | Verifier |
|-------|--------|
| page/record/LOB bytes | `DBCC PAGE (db,file,page,3) WITH TABLERESULTS` (trace flag 3604) |
| page/extent allocation | `sys.dm_db_database_page_allocations`, `DBCC IND` |
| columnstore segments/dicts | `sys.column_store_segments`, `sys.column_store_dictionaries` |
| log tail | `sys.fn_dblog`, `sys.fn_dump_dblog` |
| catalog ids / compression | `sys.partitions`, `sys.allocation_units`, `sys.system_internals_partition_columns` |
| page header & base tables | OrcaMDF |

### Rule 3: one reusable probe harness, not snippets

Add a single `tools/spec_probe.py` with subcommands (one per investigation),
each emitting a JSON "evidence" record `{guess_id, fixture, observed, verifier,
verdict}`.  This keeps evidence reproducible and lets a test assert against the
captured verifier output instead of re-deriving it.  Do **not** scatter one-off
hex-dump scripts across the repo.

### Rule 4: version matrix

Object IDs, header versions, and container layout can shift across releases.
Where a guess is version-sensitive (G04, G20, G21), capture the same schema from
each engine.  Target matrix:

| SQL Server | Why |
|------------|-----|
| 2012 | MSSQLBAK v1 header (G01); oldest catalog layout |
| 2016 | columnstore GA changes |
| 2019 | common production baseline |
| 2022 | current reference fixture baseline |
| 2025 | `json` / `vector` types (separate from this register) |

Provision via forgedb (`setup_sqlserver_podman`), then generate with
`python -m tools.fixture_run` (§0.1).

### Rule 5: acceptance criteria (definition of done per guess)

A guess `Gnn` is **resolved** when all hold:
1. A committed fixture (existing or new) exercises the case.
2. `tools/spec_probe.py Gnn` emits an evidence record whose `observed` matches
   the verifier's `expected`.
3. A regression test in `tests/test_spec_<area>.py` asserts the layout.
4. `BAK_FORMAT_SPEC.md` is updated: tag promoted (`[HEURISTIC]`→`[EMPIRICAL]`/
   `[CONFIRMED]`) **or** the layout corrected if the guess was wrong, and the
   Guess Register row struck through with a link to the test.

### Master cross-link

| Guess | Existing asset to try first | New fixture if needed | Verifier |
|-------|-----------------------------|-----------------------|--------|
| G01–G05 | `typecoverage_full_compressed.bak` | `mssqlbak_v1_inspect.bak` (2012) | hex + decode round-trip |
| G10–G12 | `typecoverage_full.bak` | `sset_*` metadata variants | `RESTORE HEADERONLY`/`FILELISTONLY` |
| G13, G14 | `typecoverage_full.bak` | `iam_offset_verify.bak` | `sys.dm_db_database_page_allocations`, `DBCC PAGE` |
| G15, G16 | `dirtycoverage_delete/update.bak` | — (reuse) | `DBCC PAGE`, `fn_dblog` |
| G17–G1A, G19 | `compressioncoverage_full.bak` | `row_smalldatetime.bak` | `DBCC PAGE`, value compare |
| G20–G22 | `compressioncoverage_full.bak`, `constraintcoverage_full.bak` | `catalog_ss20{12,16,19}.bak` | `sys.partitions`, OrcaMDF |
| G30–G32 | `typecoverage_full.bak` (LOB rows) | `lob_link_count.bak`, `text_pointer_bytes.bak` | `DBCC PAGE` |
| G40–G43 | `boundarycoverage_full.bak` | `cs_dict_ordering.bak`, `cs_enc5_*.bak` | `sys.column_store_segments` |
| G50–G52 | `dirtycoverage_*.bak` + `probe_log_records.py` | `dirty_aborted_xact.bak` | `fn_dblog` |
| G53 | `AdventureWorks2016_EXT.bak` | `aecoverage_full.bak` if deeper coverage needed | MS-CEML spec + `sys.column_encryption_keys` |

---

## §1 — Guess Work Queue

Each row is one executable investigation.  `Existing asset` is the first input
to probe; `New fixture` is only needed if the existing asset does not exercise
the case.  `Pass condition` is the state required to promote or correct the
matching row in `BAK_FORMAT_SPEC.md` §10.

### Container and metadata {#container-and-metadata}

| ID | Current assumption | Existing asset | New fixture | Verifier | Pass condition |
|----|--------------------|----------------|-------------|--------|----------------|
| G01 | MSSQLBAK `tag` low 16 bits are not needed for record traversal. | `typecoverage_full_compressed.bak` | `mssqlbak_v1_inspect.bak` from SQL Server 2012 | header walk + XPRESS decode | v1/v2 traversal uses `tag >> 16`; low bits do not affect record boundaries. |
| G02 | v2 16-byte field at header `+8` is not needed for decode. | `typecoverage_full_compressed.bak` | `mssqlbak_v2_large.bak` | header walk + decode round-trip | Field can vary while chunk traversal and page reconstruction remain correct. |
| G03 | v2 `+0` field is housekeeping, probably previous uncompressed size. | `typecoverage_full_compressed.bak` | `mssqlbak_v2_large.bak` | probe decoded chunk sizes | Probe shows whether the value matches previous, current, or neither chunk size. |
| G04 | container version word 2 is not used for layout selection. | `typecoverage_full_compressed.bak` | version matrix backup set | header probe | Different word-2 values do not change `_V1`/`_V2` record geometry. |
| G05 | leading compressed descriptor chunks precede first data-page chunk. | `typecoverage_full_compressed.bak` | compressed backup with multiple backup sets | descriptor probe | TAPE/SSET descriptors appear before first page-header chunk, or the spec is corrected. |
| G10 | MTF block-size probe order finds legal backup block sizes. | `typecoverage_full.bak` | backups with each `BLOCKSIZE` candidate | `RESTORE HEADERONLY` | detected block size equals SQL Server metadata for every candidate. |
| G11 | SSET server name is the UTF-16 run before `SFGI` after stripping DB name. | `typecoverage_full.bak` | `sset_*` server-name variants | `RESTORE HEADERONLY` | parser server name equals SQL Server metadata or spec marks it metadata-best-effort. |
| G12 | DB name fallback from `.mdf` stem is valid when MTF dataset name is empty. | `typecoverage_full.bak` | `sset_db_name_only.bak` | `RESTORE FILELISTONLY` | parser DB name matches MTF dataset name when present, otherwise primary MDF stem. |

### Pages, records, and catalog {#pages-records-and-catalog}

| ID | Current assumption | Existing asset | New fixture | Verifier | Pass condition |
|----|--------------------|----------------|-------------|--------|----------------|
| G13 | IAM bitmap starts at page offset 194. | `typecoverage_full.bak` | `iam_offset_verify.bak` | `sys.dm_db_database_page_allocations`, `DBCC IND` | IAM-walked data pages exactly match SQL Server allocation output. |
| G14 | boot page scan finds `sysallocunits`; pointer usually near boot-record offset 516. | `typecoverage_full.bak` | version matrix backup set | `DBCC PAGE` | scan target and SQL Server boot-page pointer identify the same `sysallocunits` page. |
| G15 | `status_B & 0x01` covers ghost/forwarded rows; other bits are not decoded. | `dirtycoverage_delete.bak`, `dirtycoverage_update.bak` | none initially | `DBCC PAGE` | observed status-bit pairs are cataloged; any non-0x01 behavioral bit gets a parser rule. |
| G16 | forwarded heap row stub is 9 bytes with an embedded RID. | `dirtycoverage_update.bak` | `forwarded_record_layout.bak` if needed | `DBCC PAGE` | extracted RID points to the live row and all stub bytes are documented. |
| G20 | `sysrowsets.cmprlevel` is at derived offset 39 in current `_layout()`. | `compressioncoverage_full.bak` | version matrix backup set | `sys.partitions`, `sys.allocation_units` | recovered compression matches SQL Server for heap, row, page, CCI, and archive. |
| G21 | base-table object IDs are stable across supported versions. | `constraintcoverage_full.bak` | `catalog_ss2012.bak`, `catalog_ss2016.bak`, `catalog_ss2019.bak` | OrcaMDF, catalog DMVs | object IDs and bootstrap order match or version-specific spec rows are added. |
| G22 | heap base-table rowset seed is `object_id << 16`. | `typecoverage_full.bak` | partitioned base-schema subset | `sys.partitions` | seed locates base-table heaps; partitioned user tables use recovered rowsets, not the seed. |

### ROW/PAGE compression {#rowpage-compression}

| ID | Current assumption | Existing asset | New fixture | Verifier | Pass condition |
|----|--------------------|----------------|-------------|--------|----------------|
| G17 | CD long-data flag byte is reserved for currently supported rows. | `compressioncoverage_full.bak` | none initially | `DBCC PAGE` | observed flag values are cataloged; non-zero values are either harmless or decoded. |
| G18 | CD long-data per-cluster count bytes can be skipped. | `compressioncoverage_full.bak` | wide-row ROW/PAGE fixture | `DBCC PAGE`, engine value compare | values decode correctly across more than one 30-column cluster. |
| G19 | `smalldatetime` ROW/PAGE encoding follows `_LEADING_ZERO_WIDTH`. | `compressioncoverage_full.bak` | `row_smalldatetime.bak` | engine query | parsed values match SQL Server for min, max, midnight, and non-midnight values. |
| G1A | Page CI starts with `0x06`; CI reserved field is zero. | `compressioncoverage_full.bak` | none initially | `DBCC PAGE` | every PAGE-compressed page with CI has expected type/reserved fields, or variants are documented. |

### LOB and off-row storage {#lob-and-off-row-storage}

| ID | Current assumption | Existing asset | New fixture | Verifier | Pass condition |
|----|--------------------|----------------|-------------|--------|----------------|
| G30 | inline-root link count is `(len - 12) // 12`; header bytes `[+2:+12]` are not needed. | `typecoverage_full.bak` | `lob_link_count.bak` | `DBCC PAGE` | all LOB sizes stitch correctly and header fields are labeled or left explicitly opaque. |
| G31 | on-page LOB DATA/LARGE_ROOT layout is enough to recurse links. | `typecoverage_full.bak` | `lob_large_root.bak` | `DBCC PAGE` | DATA and LARGE_ROOT link records match documented offsets and stitch full payloads. |
| G32 | legacy text-pointer bytes 0-7 are not needed for RID traversal. | `typecoverage_full.bak` | `text_pointer_bytes.bak` | `DBCC PAGE` | bytes 8-15 identify the first text-tree node; bytes 0-7 are documented or marked opaque. |

### Columnstore {#columnstore}

| ID | Current assumption | Existing asset | New fixture | Verifier | Pass condition |
|----|--------------------|----------------|-------------|--------|----------------|
| G40 | `syscscolsegments` dict-id offset 56 is used for enc=3 lookup; offset 52 is fallback. | `boundarycoverage_full.bak` | `cs_dict_ordering.bak` | `sys.column_store_segments` | parser's selected dict id matches SQL Server primary/secondary dictionary metadata. |
| G41 | columnstore LOB blobs use 12-byte preamble and 8-byte separators every 65,536 payload bytes. | `boundarycoverage_full.bak` | `cs_lob_preamble.bak` | `DBCC PAGE`, value compare | deinterleaving recovers payload for single- and multi-chunk LOB blobs. |
| G42 | enc=5 uses `0xFEFF` sentinel, data offset 98, and scale-7 datetimeoffset. | existing enc=5 table if present | `cs_enc5_varchar.bak`, `cs_enc5_datetimeoffset.bak` | `sys.column_store_segments`, engine query | parsed enc=5 values match SQL Server values for string and datetimeoffset rows. |
| G43 | segment blob header `[+0:+33]` can remain opaque; `bpv` at +34 and `nw` at +36 are sufficient. | `boundarycoverage_full.bak` | `cs_segment_header.bak` | `sys.column_store_segments` | decoded row count, min/max, nulls, and values match SQL Server for enc=1/2/3/4. |

### Log tail {#log-tail}

| ID | Current assumption | Existing asset | New fixture | Verifier | Pass condition |
|----|--------------------|----------------|-------------|--------|----------------|
| G50 | log tail is bracketed by `APAD` and `MSLS` blocks. | `dirtycoverage_*.bak` | none initially | `tools/probe_log_records.py`, `fn_dblog` | probe finds the same log records that SQL Server reports. |
| G51 | sector-status byte `0x40` appears at 512-byte boundaries and may affect `row_start`. | `dirtycoverage_update.bak` | `dirty_sector_boundary.bak` if needed | `fn_dblog`, raw byte probe | boundary handling preserves row payload offsets and dirty-row adjustment. |
| G52 | `LOP_ABORT_XACT` uses byte `0x82` but lacks a committed fixture. | `dirtycoverage_savepoint.bak`, `dirtycoverage_nested.bak` | `dirty_aborted_xact.bak` | `fn_dblog` | aborted transactions are identified and excluded from committed row output. |

### Always Encrypted {#always-encrypted}

| ID | Current assumption | Existing asset | New fixture | Verifier | Pass condition |
|----|--------------------|-----------------|-----------|---------|--------------------|
| G53 | AE nvarchar/nchar stores AEAD_AES_256_CBC_HMAC_SHA_256 ciphertext; total byte length is always odd; catalog `collation_id` in `[1, 0x10000)` for AE string columns. | `AdventureWorks2016_EXT.bak` (`CustomerPII.SSN`, `CustomerPII.CreditCardNumber`) | `aecoverage_full.bak` (see §G53 recipe) | MS-CEML spec + `sys.column_encryption_keys` + `sys.columns.encryption_type` | Raw bytes of SSN have odd length and first byte = `0x01`; `Column.is_encrypted = True`; `read_table_rows` returns `None` for both AE columns across all 18 966 rows. |

### §1.7 Fixture recipes {#fixture-recipes}

Executable steps for rows that need a **new** `.bak`.  Rows marked **existing
only** in the work-queue tables above should be probed with committed fixtures
before building anything new.

| ID | Status | Fixture file | Generator |
|----|--------|--------------|-----------|
| G01–G05 | existing only first | — | `typecoverage_full_compressed.bak`; add `mssqlbak_v1_inspect.bak` only if 2012 v1 header differs |
| G10–G12 | new if needed | `sset_db_name_only.bak`, `sset_server_name.bak` | extend `tools/make_fixture.py` backup metadata variants |
| G13 | **recipe** | `iam_offset_verify.bak` | `tools/make_fixture.py` minimal schema |
| G14 | version matrix | `catalog_ss2012.bak` etc. | forgedb + `make_fixture.py` per engine |
| G15–G16 | existing only | — | `dirtycoverage_delete.bak`, `dirtycoverage_update.bak` |
| G17–G18, G1A | existing only first | — | `compressioncoverage_full.bak` |
| G19 | **recipe** | `row_smalldatetime.bak` | extend `tools/compressionmatrix.py` |
| G20–G22 | version matrix | `catalog_ss20{12,16,19}.bak` | forgedb + `make_fixture.py` |
| G30 | **recipe** | `lob_link_count.bak` | extend `tools/typematrix.py` or dedicated script |
| G31 | new if needed | `lob_large_root.bak` | `tools/make_fixture.py` + large `varchar(max)` |
| G32 | new if needed | `text_pointer_bytes.bak` | `typecoverage_full.bak` may suffice; add `text`/`ntext` rows if not |
| G40 | **recipe** | `cs_dict_ordering.bak` | extend `tools/make_boundary_fixture.py` |
| G41 | existing only first | `cs_lob_preamble.bak` if needed | `boundarycoverage_full.bak` |
| G42 | **recipe** | `cs_enc5_datetimeoffset.bak`, `cs_enc5_varchar.bak` | `make_boundary_fixture.py` subset |
| G43 | existing only first | `cs_segment_header.bak` if needed | `boundarycoverage_full.bak` |
| G50 | existing only | — | `dirtycoverage_*.bak` + `tools/probe_log_records.py` |
| G51 | **recipe** | `dirty_sector_boundary.bak` | extend `tools/make_dirty_fixture.py` |
| G52 | new if needed | `dirty_aborted_xact.bak` | `make_dirty_fixture.py` aborted-xact scenario |
| G53 | **existing only first** | `AdventureWorks2016_EXT.bak` | probe `CustomerPII.SSN` raw bytes; optional `aecoverage_full.bak` from forgedb |

#### G13 — IAM bitmap offset (`iam_offset_verify.bak`)

**Generator:** `tools/make_fixture.py` (forgedb SQL Server 2022).

**SQL sketch:**
```sql
CREATE TABLE dbo.iam_probe (id INT NOT NULL PRIMARY KEY, payload CHAR(8000) NOT NULL);
INSERT INTO dbo.iam_probe SELECT n, REPLICATE('X', 8000) FROM (SELECT TOP 200 ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) n FROM sys.all_objects) t;
BACKUP DATABASE iam_probe_db TO DISK = '/var/opt/mssql/backup/iam_probe.bak' WITH INIT, CHECKSUM;
```

**Verifier capture** (restore, then):
```sql
SELECT allocated_page_file_id, allocated_page_page_id, page_type_desc, object_id
FROM sys.dm_db_database_page_allocations(DB_ID(), NULL, NULL, NULL, 'DETAILED')
WHERE object_id = OBJECT_ID('dbo.iam_probe') AND page_type_desc IN ('DATA_PAGE','IAM_PAGE');
-- DBCC PAGE ('iam_probe_db', <iam_file>, <iam_page>, 3) WITH TABLERESULTS;
```

**Commit path:** `tests/fixtures/iam_offset_verify.bak`, verifier sidecar
`tests/fixtures/probe/G13.json` (DMV page list + IAM page hex dump at offset 194).

#### G19 — PAGE-compressed `smalldatetime` (`row_smalldatetime.bak`)

**Generator:** extend `tools/compressionmatrix.py` (currently excludes
`smalldatetime`; add a `cmp_page_sdt` table).

**SQL sketch:**
```sql
CREATE TABLE dbo.cmp_page_sdt (
  id INT NOT NULL PRIMARY KEY,
  v_min SMALLDATETIME NOT NULL,
  v_max SMALLDATETIME NOT NULL,
  v_midnight SMALLDATETIME NOT NULL,
  v_noon SMALLDATETIME NOT NULL
) WITH (DATA_COMPRESSION = PAGE);
INSERT INTO dbo.cmp_page_sdt VALUES
  (1, '1900-01-01', '2079-06-06', '2020-01-01', '2020-06-15 12:34:56');
```

**Verifier capture:** `SELECT * FROM dbo.cmp_page_sdt;` plus `DBCC PAGE` on a
PAGE-compressed data page for the table.

**Commit path:** fold into `compressioncoverage_full.bak` or standalone
`tests/fixtures/row_smalldatetime.bak`, verifier `tests/fixtures/probe/G19.json`.

#### G30 — inline-root link count (`lob_link_count.bak`)

**Generator:** `tools/lobmatrix.py` (wired into `make_fixture.py`);
regenerate with `python -m tools.fixture_run make_fixture`.

**SQL sketch:** one row per link-count boundary.  Sizes chosen so the in-row
inline root has 1, 2, and 3 twelve-byte links (parser derives
`nlinks = (len - 12) // 12`).

**Provisioning note:** T-SQL `REPLICATE()` is capped at **8000** characters.
Grow a ``DECLARE @v varchar(max)`` in a ``WHILE`` loop (see
`tools/lobmatrix.py` ``_insert_lob_sql()``) — chained ``+`` / ``CONCAT`` in
``INSERT VALUES`` can still cap at 8000 bytes.
```sql
CREATE TABLE dbo.lob_links (id INT PRIMARY KEY, v VARCHAR(MAX) NOT NULL);
DECLARE @v varchar(max);
SET @v = REPLICATE('B', 8000);
WHILE LEN(@v) < 50000
  SET @v = @v + REPLICATE('B', CASE WHEN 50000 - LEN(@v) > 8000 THEN 8000 ELSE 50000 - LEN(@v) END);
INSERT INTO dbo.lob_links VALUES (2, @v);
```

**Verifier capture:** `DBCC PAGE` on heap data pages; record the inline-root byte
length and link RIDs from `DBCC PAGE` LOB columns.

**Commit path:** `tests/fixtures/lob_link_count.bak`, verifier `G30.json`.

#### G40 — columnstore dictionary ordering (`cs_dict_ordering.bak`)

**Generator:** extend `tools/make_boundary_fixture.py`.

**SQL sketch:** two `varchar` columns in one CCI table with disjoint value sets
so each column gets its own dictionary in the same segment:
```sql
CREATE TABLE dbo.cs_dict2 (
  id INT NOT NULL,
  col_a VARCHAR(100) NOT NULL,
  col_b VARCHAR(100) NOT NULL,
  INDEX cci_cs_dict2 CLUSTERED COLUMNSTORE
);
-- Insert 1200+ rows: col_a cycles 'AAA'..'ZZZ', col_b cycles '111'..'999'
```

**Verifier capture:**
```sql
SELECT hobt_id, column_id, segment_id, encoding_type,
       primary_dictionary_id, secondary_dictionary_id
FROM sys.column_store_segments
WHERE hobt_id = (SELECT hobt_id FROM sys.partitions WHERE object_id = OBJECT_ID('dbo.cs_dict2'));
```

**Commit path:** `tests/fixtures/cs_dict_ordering.bak`, verifier `G40.json`.

#### G42 — enc=5 confirmation (`cs_enc5_*.bak`)

**Generator:** `tools/make_boundary_fixture.py` (or a dedicated enc=5 table).

**SQL sketch:**
```sql
CREATE TABLE dbo.cs_enc5 (
  id INT NOT NULL,
  v_str VARCHAR(8000) NOT NULL,
  v_dto DATETIMEOFFSET(7) NOT NULL,
  INDEX cci_cs_enc5 CLUSTERED COLUMNSTORE
);
-- 1200+ rows with long distinct strings and varied datetimeoffset values
```

**Verifier capture:** `sys.column_store_segments` (`encoding_type = 5`) plus
`SELECT v_str, v_dto FROM dbo.cs_enc5 ORDER BY id`.

**Commit path:** `tests/fixtures/cs_enc5_datetimeoffset.bak` (and optional
`cs_enc5_varchar.bak`), verifier `G42.json`.

#### G51 — log-tail sector boundary (`dirty_sector_boundary.bak`)

**Generator:** extend `tools/make_dirty_fixture.py`.

**SQL sketch:** fuzzy backup (`NO_CHECKPOINT`) with a DML operation timed so a
log record spans a 512-byte sector boundary; document expected `row_start`
adjustment in `dirty_ground_truth.json`.

**Verifier capture:** `sys.fn_dblog(NULL, NULL)` filtered to the scenario xact;
raw log-tail bytes via `tools/probe_log_records.py`; note sector-status byte
`0x40` offsets.

**Commit path:** `tests/fixtures/dirty_sector_boundary.bak`, verifier `G51.json`.

#### G53 — Always Encrypted ciphertext in nvarchar columns

**Existing asset:** `tests/fixtures/samples/AdventureWorks2016_EXT.bak`.  No new
fixture is needed to probe the current assumption; the existing sample exercises
the full detection path.

**Probe steps** (add `spec_probe always-encrypted` subcommand):
```python
# In tools/spec_probe.py, subcommand 'always-encrypted':
store = PageStore.from_bak("tests/fixtures/samples/AdventureWorks2016_EXT.bak")
schema = recover_schema(store)
pii = next(t for t in schema.tables if t.name == "CustomerPII")
ssn_col = next(c for c in pii.columns if c.name == "SSN")
assert ssn_col.is_encrypted, "SSN must be detected as Always Encrypted"
# Read first row raw bytes for SSN slot, confirm odd length + 0x01 version byte
raw = <first SSN raw bytes from page>
assert len(raw) % 2 == 1, "AE ciphertext must have odd byte length"
assert raw[0] == 0x01, "AE version byte must be 0x01"
rows = list(read_table_rows(store, pii))
assert all(r["SSN"] is None for r in rows), "All AE SSN values must be None"
```

**Verifier capture:** no SQL Server needed — the MS-CEML wire-format spec
(`AEAD_AES_256_CBC_HMAC_SHA_256`) defines the ciphertext layout independently.
Cross-check with `sys.columns.encryption_type = 2` (RANDOMIZED) and
`sys.column_encryption_keys` on a live restore.

**Optional new fixture** (`aecoverage_full.bak`): if deeper AE coverage is
needed (deterministic vs randomised, varchar vs nvarchar, non-nullable AE
columns), generate via forgedb SQL Server 2016+ with the following SQL sketch:

```sql
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'StrongP@ssw0rd!';
CREATE CERTIFICATE AETestCert WITH SUBJECT = 'AE test cert';
CREATE COLUMN MASTER KEY AE_CMK WITH (
    KEY_STORE_PROVIDER_NAME = 'MSSQL_CERTIFICATE_STORE',
    KEY_PATH = 'CurrentUser/My/AETestCert'
);
CREATE COLUMN ENCRYPTION KEY AE_CEK WITH VALUES (
    COLUMN_MASTER_KEY = AE_CMK,
    ALGORITHM = 'RSA_OAEP',
    ENCRYPTED_VALUE = 0x...  -- generated by SSMS or PowerShell New-SqlColumnEncryptionKey
);
CREATE TABLE dbo.ae_probe (
    id     INT NOT NULL PRIMARY KEY,
    det    NVARCHAR(50)  COLLATE Latin1_General_BIN2 ENCRYPTED WITH (
               ENCRYPTION_TYPE = DETERMINISTIC,
               ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256',
               COLUMN_ENCRYPTION_KEY = AE_CEK) NULL,
    rand   NVARCHAR(50)  COLLATE Latin1_General_BIN2 ENCRYPTED WITH (
               ENCRYPTION_TYPE = RANDOMIZED,
               ALGORITHM = 'AEAD_AES_256_CBC_HMAC_SHA_256',
               COLUMN_ENCRYPTION_KEY = AE_CEK) NULL
);
INSERT INTO dbo.ae_probe (id) VALUES (1), (2), (3);
BACKUP DATABASE ae_probe_db TO DISK = '/var/opt/mssql/backup/aecoverage_full.bak'
    WITH INIT, CHECKSUM;
```

**Commit path:** `tests/fixtures/aecoverage_full.bak`, verifier
`tests/fixtures/probe/G53.json`.

## §2 — `tools/spec_probe.py` Harness

Add one reusable probe script instead of one-off dump scripts.  Each subcommand
emits one JSON object per checked guess:

```json
{
  "guess_id": "G13",
  "fixture": "typecoverage_full.bak",
  "observed": {"iam_bitmap_offset": 194},
  "verifier": {"source": "sys.dm_db_database_page_allocations"},
  "verdict": "match"
}
```

Planned subcommands:

| Subcommand | Guess IDs | Inputs | Output |
|------------|-----------|--------|--------|
| `container` | G01-G05 | compressed `.bak` | header geometry, chunk sizes, descriptor order |
| `metadata` | G10-G12 | `.bak` + optional SQL Server metadata JSON | block size, DB/server/file names |
| `pages` | G13-G16 | `.bak` + DMV/DBCC JSON | IAM pages, boot pointer, status bytes, forwarding RID |
| `rowcompress` | G17-G1A, G19 | `compressioncoverage_full.bak` | CD flags, long-region bytes, CI headers, value comparison |
| `catalog` | G20-G22 | `.bak` + catalog DMV JSON | object IDs, rowset IDs, compression levels |
| `lob` | G30-G32 | `.bak` + `DBCC PAGE` JSON | inline-root header, link count, LOB node links, text pointer |
| `columnstore` | G40-G43 | `.bak` + columnstore DMV JSON | dict IDs, segment headers, LOB deinterleave, enc=5 values |
| `logtail` | G50-G52 | dirty `.bak` + `fn_dblog` JSON | markers, sector bytes, transaction operation codes |
| `layout` | L01-L03 | `layoutcoverage_full.bak` | PK-position table recovery, column-count tables |
| `columnstore` | G42 | `boundarycoverage_full.bak` | columnstore table presence |

## §3 — Priority

Risk codes match `BAK_FORMAT_SPEC.md` §10: `S` = silent wrong data, `M` =
table skipped, `L` = metadata only.

| Priority | Guesses | Risk | Reason |
|----------|---------|------|--------|
| P1 | G42 (enc=5) | S | Active decoder; confirm before trusting raw/off-row columnstore values. |
| P1 | G19 (smalldatetime ROW) | S | Current decoder may silently return the wrong timestamp. |
| P1 | G30 (inline-root nlinks) | S | Wrong link count can truncate or reorder large LOB values. |
| P1 | G40 (dict-id ordering) | S | Wrong dictionary selection corrupts string columnstore values. |
| P1 | G51 (log-tail sector byte) | S | Wrong row-start adjustment corrupts dirty-backup repair. |
| P1 | L01 (PK position) | S | Wrong `leaf_offset` / null-bit index silently mis-decodes multi-column rows. |
| P1 | L03 (1024 columns) | M | CD 30-column clusters and max null-bitmap size untested. |
| P2 | G13, G14 | M | Page traversal and catalog bootstrap fail if these are wrong. |
| P2 | G16-G18, G1A | M | Affected tables should skip cleanly, but coverage is incomplete. |
| P2 | G20-G22 | M | Cross-version catalog support depends on these assumptions. |
| P3 | G01-G05, G10-G12, G15, G32, G50, G52 | L/M | Lower immediate row-data risk or already isolated to metadata/log-tail paths. |
| P2 | L02, L04, L05 | S/M | PK type variety and multi-page B-tree; lower urgency once L01/L03 pass. |

## §4 — Layout coverage fixtures

Record-topology fixtures complement the byte-layout Guess Work Queue (§1).
They exercise **where** columns sit in a row, not **what** individual field bytes
mean.  SSOT: `tools/layoutmatrix.py`; generator: `python -m tools.fixture_run layout`.

| Fixture | Generator | Layout IDs | Verifier |
|---------|-----------|------------|--------|
| `layoutcoverage_full.bak` | `python -m tools.fixture_run layout` | L01–L03, L05 | Engine `SELECT` + `spec_probe layout` |
| `layoutcoverage_compressed.bak` | `python -m tools.fixture_run layout --compressed` | L01 under PAGE | value compare vs engine |
| `catalog_ss2012.bak` | `python -m tools.fixture_run catalog --engine 2012` | G21, G14 | `sys.partitions`, OrcaMDF |
| `catalog_ss2016.bak` | `python -m tools.fixture_run catalog --engine 2016` | G21 | catalog DMVs |
| `catalog_ss2019.bak` | `python -m tools.fixture_run catalog --engine 2019` | G21 | catalog DMVs |
| `catalog_ss2022.bak` | `python -m tools.fixture_run catalog --engine 2022` | G21, G20 | catalog DMVs |
| `mssqlbak_v1_inspect.bak` | `python -m tools.fixture_run version-matrix --v1-inspect` | G01 | header walk + XPRESS decode |

### Layout matrix design (deterministic, not random)

**PK position** — for each PK-eligible type `T`, four tables isolate PK at
column 1, 2, penultimate, and last.  Filler columns are fixed (`bit`, `int`,
`varchar(20)`) so diffs attribute failures to layout only.

**Column-count boundaries** — `layout_cols_1`, `layout_cols_30`, `layout_cols_31`,
`layout_cols_1023`, `layout_cols_1024` use `tinyint NOT NULL` fillers to stay
under the 8060-byte row limit while hitting CD 30-column cluster boundaries and
SQL Server's 1024-column cap.

**Verifier sidecars** — `tests/fixtures/probe/L01.json`, `G13.json` store
`DBCC PAGE` / DMV evidence captured at fixture generation time.

### §4.1 Layout fixture recipes

#### L01 — PK position matrix (`layoutcoverage_full.bak`)

**Generator:** `python -m tools.fixture_run layout`

**SQL sketch:** 52 tables `layout_pk_{type}_{position}` plus 5 column-count
tables.  See `tools/layoutmatrix.py` for the full case list.

**Verifier capture:** `SELECT * FROM dbo.layout_pk_int_first ORDER BY pk_col;` for
each table; `DBCC PAGE` on one representative multi-column page.

**Commit path:** `tests/fixtures/layoutcoverage_full.bak`,
`tests/fixtures/probe/L01.json`.

#### G19 — PAGE-compressed `smalldatetime` (`row_smalldatetime.bak`)

Folded into `compressioncoverage_full.bak` via extended `compressionmatrix.py`
(table `cmp_page_sdt`).  See §1.7 G19 recipe (unchanged).

#### G30 — inline-root link count

Folded into `typecoverage_full.bak` via `lob_links` in `tools/lobmatrix.py`.
Regenerate: `python -m tools.fixture_run make_fixture`.  See §1.7 G30 recipe.

---

## §5 — G55: `collation_id` LCID bit layout (`unicode_codepage_coverage.bak`)

### Guess G55

`syscolpars.collationid` is a 32-bit integer.  Bit 8 (`0x100`) is the UTF-8
flag (known empirically).  The remaining bits encode LCID and collation
properties, but the exact bit positions are unknown — the LCID field cannot be
decoded without empirical data from diverse collations.  G55 documents this gap
and defines how to close it.

### Purpose of the fixture

The `unicode_codepage_coverage.bak` fixture creates 13 tables — one per
non-cp1252 Windows code page — each holding a `varchar_col VARCHAR(1000)
COLLATE <sql_collation>` column and a matching `nvarchar_col NVARCHAR(1000)`
column.  The `collation_id` values for each `varchar_col` are distinct because
each column carries a different LCID.  XOR-ing each value against the
Latin1_General baseline (0x3400D008) isolates the bits that differ, identifying
the LCID bit field position.

### Code pages and collations

| Python codec | SQL Server collation | Windows LCID | Script |
|---|---|---|---|
| `cp1250` | `Polish_CI_AS` | 0x0415 | Central European (Polish / Czech / Hungarian) |
| `cp1251` | `Cyrillic_General_CI_AS` | 0x0419 | Russian / Cyrillic |
| `cp1253` | `Greek_CI_AS` | 0x0408 | Greek |
| `cp1254` | `Turkish_CI_AS` | 0x041F | Turkish |
| `cp1255` | `Hebrew_CI_AS` | 0x040D | Hebrew |
| `cp1256` | `Arabic_CI_AS` | 0x0401 | Arabic |
| `cp1257` | `Lithuanian_CI_AS` | 0x0427 | Baltic / Lithuanian |
| `cp1258` | `Vietnamese_CI_AS` | 0x042A | Vietnamese |
| `cp874` | `Thai_CI_AS` | 0x041E | Thai |
| `cp932` | `Japanese_CI_AS` | 0x0411 | Japanese (Shift-JIS) |
| `cp936` | `Chinese_PRC_CI_AS` | 0x0804 | Chinese Simplified (GBK) |
| `cp949` | `Korean_Wansung_CI_AS` | 0x0412 | Korean (EUC-KR) |
| `cp950` | `Chinese_Taiwan_Stroke_CI_AS` | 0x0404 | Chinese Traditional (Big5) |

### Text sources

Characters for each code page are taken from the Unicode 2.0 and 3.2 test
pages:
- `https://www.cogsci.ed.ac.uk/~richard/unicode-sample.html` (Unicode 2.0)
- `https://www.cogsci.ed.ac.uk/~richard/unicode-sample-3-2.html` (Unicode 3.2)

SQL uses `N'...'` Unicode literals; SQL Server converts them to the column's
code page encoding on INSERT, replacing unmappable characters with `?`.  The
companion `nvarchar_col` column stores the same text as UTF-16LE, providing an
uncorrupted baseline for round-trip comparison tests.

### Generator

```bash
python -m tools.fixture_run unicode-codepage
# output: tests/fixtures/unicode_codepage_coverage.bak
```

The tool prints a collation_id probe table to stderr immediately after the BAK
is written:

```
==> Probing collation_id values in the BAK
    (Latin1_General_CI_AS baseline = 0x3400D008)
    Table                 collation_name                       collation_id (hex)    XOR baseline
    cp_cp1251             Cyrillic_General_CI_AS               0x3400????            (XOR=0x????????)
    ...
```

### Verifier

**Step 1** (inside SQL Server before backup):

```sql
SELECT c.name, c.collation_name
FROM sys.columns c
JOIN sys.objects o ON o.object_id = c.object_id
WHERE o.name LIKE 'cp_%' AND c.name = 'varchar_col'
ORDER BY o.name;
```

Expected: one row per table, `collation_name` matches the `sql_collation` column
above.

**Step 2** (from the BAK via mssqlbak probe output):

Record the `collation_id` value for each table; compare to the expected LCID to
verify the LCID extraction formula in `_codec_for_collation()`.

### Assertion (once G55 is resolved)

After the LCID bit positions are determined, `_codec_for_collation(collation_id)`
must return the correct Python codec string for every `collation_id` observed in
this fixture.  Add a parametrized test to `tests/test_unicode_decode.py` using
the probed `collation_id` values as input.

### Files

| File | Role |
|---|---|
| `tools/unicode_codepage_matrix.py` | Code page / collation / LCID / sample-text definitions |
| `tools/make_unicode_codepage_fixture.py` | BAK builder + post-creation collation_id probe |
| `tests/fixtures/unicode_codepage_coverage.bak` | Generated fixture (not in git — too large) |

## See Also

- [docs/BAK_FORMAT_SPEC.md](BAK_FORMAT_SPEC.md) — current parser contract and Guess Register.
- [§1.7 Fixture recipes](#fixture-recipes) — generator/SQL/verifier steps for new `.bak` files.
- [docs/GAP_ANALYSIS.md](GAP_ANALYSIS.md) — supported storage features and out-of-scope areas.
- [docs/DIRTY_BACKUP_ANALYSIS.md](DIRTY_BACKUP_ANALYSIS.md) — dirty/fuzzy backup scenarios.
- [docs/CONCURRENT_OPERATIONS_COVERAGE.md](CONCURRENT_OPERATIONS_COVERAGE.md) — concurrent-operation coverage.
