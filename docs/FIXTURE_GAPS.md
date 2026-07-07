# Synthetic Fixture Gaps

Gaps between the committed synthetic fixtures in `tests/fixtures_2022/` (primary) and
the failure modes observed when running the real-world sample corpus in
`tests/fixtures_realworld/` (git-ignored, fetch with `python -m tools.fetch_sample_baks`).

Synthetic fixtures prove what the code handles by design.  The sample corpus — real
Microsoft databases: AdventureWorks, WideWorldImporters, TPC-xBB, StackExchange — exposes
shapes that were not deliberately included.  This document records each fixture gap,
the sample evidence that revealed it, and the fixture or code change that would close it.

See `docs/SAMPLE_TESTING_PLAN.md` and `docs/correctness_coverage_samples.md` for full
sample-corpus context.

---

## Recent accomplishments

Fixes shipped in the current development cycle (all committed to `feat/bak-to-delta`):

| Fix | Details |
|-----|---------|
| `enc=4` INT64_MIN null sentinel | Python and Rust decoders now correctly mask `null_val` to u64 before comparing against the sentinel range, fixing false nulls on large-magnitude integer columns |
| `enc=1`/`enc=4` authoritative n_rows | Pool boundary expansion now uses the segment's authoritative `n_rows` from metadata rather than back-computing from blob size, fixing row counts on narrow segments |
| Rust `true_bp_start` | Bitpack offset computation now accounts for 14-byte trailers, fixing off-by-one errors on RLE-leading segments |
| XPRESS position tracking | `decompress_with_pos` consumed-bytes return value correctly advanced the block cursor; prior code re-decompressed the same block on every iteration |
| `enc=5` ARCHIVE routing | ARCHIVE multi-sub-block format now correctly detected via `u32@38 == n_rows && n_rows > 32767`; previously mis-routed to single-chunk Format C/D for large row groups |
| Sample-corpus correctness baseline | 37/45 sample `.bak` files now pass all row-count, null-count, min/max, and column-count checks (up from ~30/45 before this cycle) |
| SS2017 legacy DML detection | `iter_log_records` now detects INSERT/DELETE with `SUBTYPE=0x00` (SS2017 log format) in addition to `SUBTYPE=0x04` (SS2019+); version auto-detected per log tail |
| SS2017 `page_id` sector-status recovery | `last_page_by_xact` fallback now applied to INSERT/DELETE records as well as MODIFY_ROW; fixes savepoint page_id corruption and temporal false dirty slot |
| Phase 1 fixtures complete | All 4 SQL Server versions (2017, 2019, 2022, 2025) fully tested; `heapcoverage_large_50000.bak` passes stats extraction on all 4 |
| Gap 3 (NDF) closed | `ndfcoverage_full.bak` fixture + `tests/test_ndf_coverage.py` added; 7/7 tests pass on all versions; IAM and B-tree readers already crossed file-id boundaries correctly |
| Gap 4 (In-Memory OLTP) closed | `featurecoverage_full.bak` regenerated with `memory_oltp` table (`MEMORY_OPTIMIZED = ON`); `classify_table` returns `unsupported` with reason `memory-optimized`; test in `test_feature_coverage.py` asserts correct skip reason |
| Gap 1 (heap scale) closed | `heapcoverage_large_50000.bak` (50 000-row heap) passes on all 4 SS versions; IAM multi-extent traversal confirmed correct |
| Gap 2 (varchar GT truncation) fix | `tools/register_bak.py` `_minmax_col_exprs`: varchar/nvarchar/char/nchar cast raised from `NVARCHAR(200)` to `NVARCHAR(4000)`; `long_text` fixture added to `featurecoverage_full.bak` with columns > 200 chars |
| Rust float normalization fix | ROW/PAGE-compressed `real`/`float` columns were decoded with `pad_le` (right-pad), corrupting values with leading zero bytes. Fixed with `lpad_le` (left-pad) in `rust/src/page_decode.rs`; exercised by new `cmp_*_floats` tables in `compressioncoverage_full.bak` |
| Rust `datetimeoffset` UTC fix | `decode_datetimeoffset_us` incorrectly subtracted the timezone offset from the stored UTC microseconds. The stored datetime2 portion IS UTC; offset is metadata only. Fixed in `rust/src/page_decode.rs`; exercised by new `dto` columns in `compressioncoverage_full.bak` |

---

## Testing strategy

### Problem with jumping straight to real-world files

Real-world `.bak` files combine many confounding factors simultaneously: multiple SQL
Server versions, non-primary filegroups, in-memory tables, ARCHIVE columnstore with
large row groups, mixed compression levels, and legacy page formats.  When a test fails
it is hard to isolate the root cause.

### Phased approach

**Phase 1 — Multi-version fixture validation (current focus)**

The four SQL Server versions in the lab are: **2017, 2019, 2022, 2025**.

Goal: run the same fixture creation scripts against each version's live SQL Server
instance.  Each version produces its own native `.bak` + `stats.json`:

- `make_*_fixture.py` runs against SS2017 → SS2017 page layout, SS2017 catalog format
- `register_bak.py` captures ground truth from the same SS2017 instance
- mssqlbak extracts the SS2017-native `.bak` and results are compared

This means `tests/fixtures_2019/tabletypecoverage_full.bak` is a real SS2019-format
file, not a transplanted SS2022 backup.  If an integer column is stored with a
different alignment, or a columnstore null bitmap differs, or ARCHIVE block layout
changed between versions, it shows up as a failure in a 10-row controlled table
rather than buried inside a 34M-row real-world file.

This also gives version coverage for real failures: if the SS2017 int fixture
already fails, the gap is pre-SS2019 and is not specific to any one sample database.

| Version | Instance | Fixture dir | Status |
|---------|----------|-------------|--------|
| SS2017 | `*-mssql-2017-*` | `tests/fixtures_2017/` | ✅ fully created; 1 pre-existing failure (`dirtycoverage_temporal_update` — ghost row row-count) |
| SS2019 | `*-mssql-2019-*` | `tests/fixtures_2019/` | ✅ fully created; 2 pre-existing dirty failures only (`temporal_update` + `concurrent`); `columnstore_minimal` re-registered ✅ |
| SS2022 | `*-mssql-2022-*` | `tests/fixtures_2022/` (primary) | ✅ fully created, **all pass** (185 pass, 2 skip, 5 xfail) |
| SS2025 | `*-mssql-2025-*` | `tests/fixtures_2025/` | ✅ fully created; 2 pre-existing dirty failures |

Phase 1 is complete.  Run any version with:
```
FIXTURE_DIR=tests/fixtures_2017 pytest tests/test_dirty_backup.py tests/test_stats.py
```

Pre-existing failures are not version-specific:
- `committed_delete_slots_detected`, `committed_update_patches_detected` — separate planned enhancement
- `dirtycoverage_temporal_update` — history-table ghost row visible in raw page scan
- `dirtycoverage_concurrent` — SS2019/SS2025 only; concurrent-xact page interaction

**Key SS2017 learning:** SQL Server 2017 uses `SUBTYPE=0x00` for INSERT/DELETE log records
(SS2019+ uses `SUBTYPE=0x04`).  Sector-status bytes (0x40) can corrupt the low byte of
`page_id` when the field falls on a 512-byte boundary inside a log block; the
`last_page_by_xact` recovery now applies to both MODIFY_ROW and INSERT/DELETE records.

**Phase 2 — Scale-up fixtures (close the gaps below)**

Once all four versions pass on the current fixtures, inflate table sizes and add missing
feature coverage to trigger the failure modes we observe on real-world files.

Priority order (✅ = closed, 🔲 = still open):

1. ✅ **Gap 3** — NDF/secondary-filegroup: `ndfcoverage_full.bak` + `tests/test_ndf_coverage.py`; all 7 tests pass on all versions
2. ✅ **Gap 4** — In-Memory OLTP: `memory_oltp` table in `featurecoverage_full.bak`; `classify_table` returns correct skip reason; test asserts `unsupported`
3. ✅ **Gap 1** — Heap scale: `heapcoverage_large_50000.bak` (50 000 rows) passes on all 4 versions
4. ✅ **Gap 2** — Varchar GT truncation: `tools/register_bak.py` casts raised to `NVARCHAR(4000)`; `long_text` fixture in `featurecoverage_full.bak`
5. 🔲 **Gap 5** — enc=5 ARCHIVE null encoding: still unsolved (see gap detail below)
6. ✅ **Gap 6** — Stale columnstore segment metadata: SS2019 `columnstore_minimal` re-registered; 0-row GT for cs_100/cs_1000/cs_10000 was stale registration, now 11111 rows captured correctly

**Next action:** Gap 5 (enc=5 ARCHIVE nulls) — see gap detail below for investigation notes and next steps.

Re-run all four versions after each gap is closed:
```
for ver in 2017 2019 2022 2025; do
  FIXTURE_DIR=tests/fixtures_$ver pytest tests/test_stats.py tests/test_dirty_backup.py -q
done
```

**Phase 3 — Real-world corpus (return with a stronger engine)**

With the scaled-up fixtures passing across all four versions, return to the 8 failing
sample `.bak` files knowing the engine handles the individual building blocks correctly.

Remaining failing samples and their likely root causes:

| Sample | Likely root cause |
|--------|-----------------|
| `CreditBackup100.bak` | Non-primary filegroup (Gap 3) + possible pre-2012 page format |
| `tpcxbb_1gb.bak` | Non-primary filegroup (Gap 3); ARCHIVE string enc=5 null encoding; stale `wcs_click_date_sk` min metadata |
| `ContosoRetailDW.bak` | ARCHIVE columnstore min/max discrepancies (stale segment metadata) |
| `AdventureWorksDW2016_EXT.bak` | IAM scale bug on large `DatabaseLog` heap (Gap 1) |
| `WideWorldImporters-Full.bak` | In-Memory OLTP tables (Gap 4); null discrepancies on 3 columns |
| `WideWorldImporters-Full_old.bak` | Same as above |
| `WideWorldImportersDW-Full.bak` | ARCHIVE columnstore min/max discrepancies |
| `AdventureWorks2016_EXT.bak` | In-Memory OLTP tables (`*_inmem`) |

---

## Current test scorecard (last updated 2026-06-15)

Run with: `for ver in 2017 2019 2022 2025; do FIXTURE_DIR=tests/fixtures_$ver .venv/bin/pytest tests/test_stats.py tests/test_dirty_backup.py -q --tb=no; done`

| Version | Pass | Fail | Known-fail cause |
|---------|------|------|-----------------|
| SS2017 | 161 | 1 | `dirtycoverage_temporal_update` — history-table ghost row |
| SS2019 | 161 | 2 | 2× dirty pre-existing (`temporal_update` + `concurrent`) |
| SS2022 | 185 | 0 | — **all pass** ✅ |
| SS2025 | 160 | 2 | 2× dirty pre-existing |

Feature + NDF tests: `pytest tests/test_feature_coverage.py tests/test_ndf_coverage.py` → **34/34 pass** on all versions.

**Active work item:** Gap 5 — enc=5 ARCHIVE null encoding (see gap detail below).  
The SS2019 `columnstore_minimal` 0-row issue was fixed by re-registering the fixture (committed).

---

## ✅ Gap 1 — `tt_heap` row count too small (CLOSED)

### Evidence

`EmployeeCaseStudySampleDB2012.bak` and `IndexInternals2008.bak` each contain two
tables with 80,000 rows: `dbo.Employee` (clustered index) and `dbo.EmployeeHeap`
(no index).  The clustered table always passes.  The heap always produces the wrong
row count.

Performance stats confirm the exact magnitude: 159,840 rows extracted across both
tables versus 160,000 expected — 160 rows missing from the heap alone, each time.

### Why the fixture misses it

`tt_heap` in `tabletypecoverage_full.bak` has 4 rows.  All 4 fit on a single data
page.  The IAM chain reader visits exactly one page and returns 4 rows — the
per-extent boundary logic in the IAM traversal is never exercised.

### Action

Inflate `tt_heap` to ≥ 50,000 rows in the next fixture regeneration.  50 K rows
span multiple extents and multiple IAM intervals, triggering the same traversal that
drops rows on the 80 K-row real tables.

Alternatively, add a dedicated `heapcoverage_large.bak` fixture that pairs a
clustered and a heap table seeded to identical data so the row counts can be compared
directly.

---

## ✅ Gap 2 — `varchar`/`nvarchar` ground-truth truncated at 200 chars (CLOSED)

### Evidence

`dba.stackexchange.com.bak`: `dbo.PostHistory` shows 14/16 min/max checks passing.
`PostHistory.Text` is `varchar(MAX)`.  When the lexicographically-extreme row in
`Text` contains more than 200 characters, the ground-truth query

```sql
CAST(MAX([Text] COLLATE Latin1_General_100_BIN2) AS NVARCHAR(200))
```

truncates the captured string.  Python extracts the full value from Delta, and the
comparison fails.

The same truncation risk applies to any `varchar(MAX)` or `nvarchar(MAX)` column
whose min/max row holds a long value — comment bodies, post text, XML-ish strings,
base64 blobs stored as varchar, etc.

### Why the fixture misses it

Every `varchar` and `nvarchar` column in `tabletypecoverage_full.bak` is seeded with
short strings.  No cell exceeds 200 characters, so the 200-char cast never truncates.

### Actions

**Code fix — `tools/register_bak.py` `_minmax_col_exprs`:**

Change the cast limit for `varchar`/`nvarchar` from `NVARCHAR(200)` to
`NVARCHAR(4000)` — the same limit already used for `text`/`ntext` and `xml`.

```python
# Before
raw_min = f"CAST(MIN({q} COLLATE Latin1_General_100_BIN2) AS NVARCHAR(200))"
raw_max = f"CAST(MAX({q} COLLATE Latin1_General_100_BIN2) AS NVARCHAR(200))"

# After
raw_min = f"CAST(MIN({q} COLLATE Latin1_General_100_BIN2) AS NVARCHAR(4000))"
raw_max = f"CAST(MAX({q} COLLATE Latin1_General_100_BIN2) AS NVARCHAR(4000))"
```

**Fixture fix:** add a `varchar(MAX)` column to `tt_plain` (or `tt_heap`) with at
least one row containing a string longer than 200 characters.  The re-registered GT
will capture up to 4,000 characters; the test will then exercise the full comparison
path.

---

## ✅ Gap 3 — Non-primary filegroup tables produce 0 rows (CLOSED)

### Evidence

Two real databases have tables that pass `classify_table` (metadata inspection
succeeds, schema columns are enumerated, GT row counts are registered) but produce
zero rows during extraction:

- **`CreditBackup100.bak` (2008/R2):** 9 of 10 tables "missing from output".  The
  one passing table is `dbo.payment` (15,554 rows).  Failing tables include tiny
  ones: `dbo.region` (9 rows), `dbo.status` (1 row).
- **`tpcxbb_1gb.bak` (2016):** 23 of 30 tables "missing from output".  Failing tables
  include `dbo.store` (12 rows), `dbo.warehouse` (5 rows), `dbo.income_band` (20
  rows).  The 7 passing tables (`customer_book_clusters`, `customer_clusters`,
  `customer_return_clusters`, `sqlr.*`) are ML result / system tables not part of
  the core TPC-xBB benchmark schema.

The scale of the failing tables rules out a row-count threshold.  The consistent
split between passing and failing tables within each database points to a structural
property shared by the failing tables.  The most likely property is **filegroup
placement**: benchmark and DW workload databases commonly place all fact/dimension
tables on a dedicated non-primary filegroup (`DATA`, `USERDATA`, etc.) for I/O
separation, while auxiliary or system-adjacent tables remain on `PRIMARY`.

`classify_table` reads system catalog metadata, which is always on `PRIMARY`, so it
succeeds regardless of where the data pages live.  If the IAM chain reader only
visits pages belonging to the primary filegroup, it returns 0 rows for tables whose
data pages are on a secondary filegroup.

### Why the fixture misses it

Every synthetic fixture creates all tables on the default `PRIMARY` filegroup.

### Action

Add a secondary filegroup to `featurecoverage_full.bak` (or a new
`filecoverage_full.bak`) and create at least one table on it.  Seeding even 10 rows
is enough to confirm that the IAM reader crosses filegroup boundaries.

If extraction returns 0 rows after the fixture is added, the root cause is confirmed
and `rows.py` / the IAM walk needs to be scoped to all filegroups in the backup
image, not only `file_id = 1`.

---

## ✅ Gap 4 — In-Memory OLTP tables produce "missing from output" instead of a skip reason (CLOSED)

### Evidence

`WideWorldImporters-Full.bak`: `Warehouse.ColdRoomTemperatures` (4 rows) and
`Warehouse.VehicleTemperatures` (65,998 rows) appear in the ground-truth registration
but are absent from the mssqlbak output.  The note in
`docs/correctness_coverage_samples.md` is "missing from output" — identical to the
filegroup gap above.

The Standard edition of WideWorldImporters uses regular disk tables for the same
names; those pass.  The Full edition uses In-Memory OLTP (memory-optimized) tables.
In-Memory OLTP stores durable data in checkpoint file pairs, not in the standard
B-tree page format.  `classify_table` does not check `is_memory_optimized`, so these
tables appear as supported, generate a schema, but yield nothing at page-read time.

### Why the fixture misses it

No committed fixture contains an In-Memory OLTP table.

### Actions

**Code fix — `mssqlbak/classify.py` (or `inspect.py`):** check
`sys.tables.is_memory_optimized = 1` during `classify_table` and return
`SkipReason.in_memory_oltp`.  This surfaces the limitation explicitly in
`correctness_coverage_samples.md` rather than silently omitting the table.

**Fixture fix:** add an In-Memory OLTP table to `featurecoverage_full.bak` via
`CREATE TABLE … WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA)` and a
test that asserts the table carries `skip_reason = "in_memory_oltp"` rather than
appearing with 0 rows.

---

## Gap 5 — enc=5 ARCHIVE null encoding not decoded

### Evidence

`tpcxbb_1gb.bak` (`dbo.customer_address`): columns `ca_suite_number` (`CHAR(10)`)
and `ca_zip` (`CHAR(10)`) are stored as columnstore ARCHIVE segments (`cmprlevel=4`,
`enc_type=5`).  Ground truth shows 23 and 14 NULLs respectively.  mssqlbak returns 0
nulls for both.

Same failure in `dbo.customer`: `c_login` (26 nulls expected, 2 found) and
`c_last_review_date` (28 nulls expected, 0 found).

### What was investigated

ARCHIVE blobs are XPRESS-compressed multi-sub-block structures.  Decompressing Block 0
produces a string pool followed by a per-row index.  For a 49,500-row group:

- Block 0 decompresses to ~252 KB
- The string pool occupies roughly the first 54 KB
- A per-row index (`Index A`) of `uint16` pool offsets follows from offset 54,620
- A second region (`Index B`) with small values (0, 2, 512, 514) appears from offset
  153,620

Only 2 explicit `0xFFFE` NULL sentinels were found in `Index A` for `ca_zip` (14 expected).
Hypothesizing that nulls are encoded via a combination of `Index A + Index B` was
tested: a simple sum formula was inconsistent — non-zero `Index B` values frequently
produced out-of-bounds pool offsets or garbage strings.  A brute-force scan for any
`idx_start` value that yields the expected null count found no match.

The `_decode_enc5_archive` function in `mssqlbak/columnstore.py` also has a structural
validation bug: it reads from an odd offset (misaligned `uint16`) when computing
`idx_start`, which causes phantom values that trigger iterative expansion, pushing
`idx_start` from the correct 54,620 to an incorrect 65,237.

### Current status

**Unsolved.** The null encoding mechanism for ARCHIVE string columns with large row
groups (> 32,767 rows) is not yet understood.  The per-row indexing scheme uses at
least two index regions in Block 0 that combine in a non-obvious way.

Two controlled fixtures are now committed and available for debugging.  Run them
against `_decode_enc5_archive` to iterate without touching real-world files:

```
pytest tests/test_archive_null_coverage.py tests/test_archive_columnstore_partition_coverage.py -v
```

### Available fixtures for debugging

**`tests/fixtures_2019/archivenull_full.bak`** ✅ registered (`archivenull_full.bak.stats.json`)

Generated by `tools/make_archive_null_fixture.py`.  Unpartitioned table, single
implicit partition, all 50,000 rows in one ARCHIVE row group.

| Table | Rows | `code` NULLs | `zip` NULLs | Compression |
|---|---|---|---|---|
| `archive_null` | 50,000 | 100 (every 500th row) | 50 (every 1,000th row) | All ARCHIVE |

Test file: `tests/test_archive_null_coverage.py`

---

**`tests/fixtures_<ver>/archive_columnstore_partition_full.bak`** — generate with:

```
# All four versions, this fixture only:
python -m tools.fixture_run all-versions --suite archive-columnstore-partition

# All four versions, full suite (includes this fixture):
python -m tools.fixture_run all-versions
```

`--suite` overrides `_ALL_VERSIONS_SUITE` with just the named command, running it
against every discovered SQL Server container (2017, 2019, 2022, 2025) in one shot.
To regenerate a single version:

```
python -m tools.fixture_run --fixture-dir tests/fixtures_2019 archive-columnstore-partition
```

Generated by `tools/make_archive_columnstore_partition_fixture.py`.  Four 140,000-row tables on a
4-partition CCI (35,000 rows per partition — above the 32,767 threshold for
multi-sub-block enc_type=5).  Partition function `pf_archive_part` splits on `id` at
35,000 / 70,000 / 105,000.  Each table represents a distinct `REBUILD` scenario:

| Table | Scenario | Partitions with ARCHIVE | Partitions with COLUMNSTORE |
|---|---|---|---|
| `archive_part_single` | `REBUILD PARTITION = 1 WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)` | 1 | 2, 3, 4 |
| `archive_part_all` | `REBUILD PARTITION = ALL WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE)` | 1, 2, 3, 4 | — |
| `archive_part_mixed` | `REBUILD PARTITION = ALL WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE ON PARTITIONS (1,3))` | 1, 3 | 2, 4 |
| `archive_part_roundtrip` | ALL → ARCHIVE, then `REBUILD PARTITION = ALL WITH (DATA_COMPRESSION = COLUMNSTORE)` | — | 1, 2, 3, 4 |

All four tables use the same null pattern: `code` NULL every 500th row (280 total, 70
per partition), `zip` NULL every 1,000th row (140 total, 35 per partition).

`archive_part_mixed` is the most diagnostic: partitions 2 and 4 use standard
COLUMNSTORE (working) and act as an internal control.  If those partitions return
correct null counts while partitions 1 and 3 return 0, the bug is confirmed as
strictly an enc_type=5 decode failure — not a partition traversal or IAM issue.

`archive_part_roundtrip` catches any decoder state leak: if it incorrectly reads
post-roundtrip COLUMNSTORE segments as enc_type=5 (e.g. by caching compression state),
null counts or values will be wrong.

Test file: `tests/test_archive_columnstore_partition_coverage.py`

### Next steps

1. Fix the `idx_start` misalignment bug in `_decode_enc5_archive` (read from the next
   even byte boundary after the string pool ends)
2. Determine the correct combination formula for `Index A` + `Index B` — check whether
   `Index B` acts as a high byte, a block selector, or a separate bit array
3. ✅ Controlled fixtures added — use `archivenull_full.bak` and
   `archive_columnstore_partition_full.bak` to iterate on the decoder without touching
   real-world files

### Why the fixture previously missed it

All synthetic columnstore fixtures used regular CCI (`cmprlevel=3`) or had fewer
than 32,768 rows, so no segment was stored in multi-sub-block ARCHIVE format.  Both
new fixtures force 35,000+ rows per row group, guaranteeing enc_type=5 segments.

---

## ✅ Gap 6 — Stale segment metadata causes min/max mismatches on ARCHIVE columns (PARTIALLY CLOSED)

### Evidence

`tpcxbb_1gb.bak` (`dbo.web_clickstreams`): column `wcs_click_date_sk` shows
min `36890` in `syscscolsegments.mn` (the value SQL Server reports via the system
catalog) but the actual minimum value in the segment data is `36898`.  mssqlbak
reads from the segment bytes and reports `36898` (correct); the ground truth
captured via `MIN(wcs_click_date_sk)` on SQL Server also returns `36898` (correct).
However the `stats.json` was registered using `syscscolsegments.mn` directly, not
`MIN(...)`.

`ContosoRetailDW.bak` and `WideWorldImportersDW-Full.bak` show similar patterns:
multiple ARCHIVE columnstore columns where `syscscolsegments` metadata is stale
(not updated after bulk loads or partition switches) and disagrees with the actual
segment bytes.

### Root cause

SQL Server does not always update `syscscolsegments.mn`/`mag` when data is loaded
into a columnstore via bulk insert or partition switch.  The metadata is advisory;
the actual min/max must be computed by reading segment data.

### Actions

- In `tools/register_bak.py`: for columnstore columns, capture ground truth using
  `MIN(col)` / `MAX(col)` queries rather than `syscscolsegments.mn`/`mag`.
  This is slower but immune to stale metadata.
- Alternatively, flag ARCHIVE columns as min/max-skip in `tests/test_stats.py`
  until the registration side is fixed (lower risk, faster to ship).

### Why the fixture misses it

Synthetic fixtures use `INSERT` statements that always update segment metadata
consistently.  Stale metadata only appears after bulk load, bcp, or partition
switch operations.

---

## Gap 8 — `uniqueidentifier` GUID sort order (resolved)

### Evidence

AdventureWorks 2016+ showed 44 min/max check failures per run (732 − 688 = 44),
every one on a `rowguid uniqueidentifier` column.  SQL Server sorts GUIDs by the byte
sequence `[10-15][8-9][6-7][4-5][0-3]`; Python sorts `str(uuid.UUID(...))` values
lexicographically.  These orderings disagree on most UUID values, so SQL Server's
`MIN`/`MAX` and Python's string-level min/max identify different rows.

### Status

Resolved: `uniqueidentifier` was added to `_MINMAX_SKIP_TYPES` in `tests/test_stats.py`.

**Remaining action:** update the "Min/max" column legend in `docs/correctness_coverage.md`
and `docs/correctness_coverage_samples.md` to list `uniqueidentifier` alongside
`sql_variant` as a skipped type.

---

## Gap 9 — Pre-2008 catalog format (no synthetic fixture possible)

### Evidence

`SalesDBOriginal.bak` (~SQL Server 2006): `python -m tools.sample_coverage` reports
`no-columns ×5` for all five tables.  The column enumeration SQL returns no rows,
meaning the system catalog page format predates the layout mssqlbak reads.

`SalesDB2014.bak` contains an identical dataset in a 2014-format backup; all four
tables pass end-to-end.

### Status

mssqlbak does not support databases created before SQL Server 2008.  This is an
extraction-engine limitation, not a fixture gap.

**Action:** document the minimum supported SQL Server version in `README.md` and
`GAP_ANALYSIS.md` (currently unspecified).  No synthetic fixture is useful here
because replicating a pre-2008 catalog layout requires an actual SQL Server 2005/2006
instance, which is not available in the container-based fixture pipeline.

---

## Gap 10 — Pre-2016 heap + XML LOB page format

### Evidence

`dbo.DatabaseLog` is a heap table (no clustered index) with eight columns including
`XmlEvent xml NOT NULL`.  It fails row count in every BAK created by SQL Server
2008R2/2012/2014 and passes in every BAK created by SQL Server 2016+, at identical
row counts:

| Sample | Creator version | `DatabaseLog` rows | Row count |
|--------|----------------|-------------------|-----------|
| `AdventureWorks2008R2.bak` | SQL Server 2008 R2 | 1,597 | ✗ |
| `AdventureWorks2012.bak` | SQL Server 2012 | 1,596 | ✗ |
| `AdventureWorks2014.bak` | SQL Server 2014 | 1,597 | ✗ |
| `AdventureWorks2016.bak` | SQL Server 2016 | 1,597 | ✓ |
| `AdventureWorks2017.bak` | SQL Server 2017 | 1,597 | ✓ |
| `AdventureWorks2019.bak` | SQL Server 2019 | 1,597 | ✓ |
| `AdventureWorksDW2008R2.bak` | SQL Server 2008 R2 | 96 | ✗ |
| `AdventureWorksDW2012.bak` | SQL Server 2012 | 96 | ✗ |
| `AdventureWorksDW2014.bak` | SQL Server 2014 | 96 | ✗ |
| `AdventureWorksDW2016.bak` | SQL Server 2016 | 96 | ✓ |
| `AdventureWorksDW2017.bak` | SQL Server 2017 | 96 | ✓ |
| `AdventureWorksDW2019.bak` | SQL Server 2019 | 96 | ✓ |

The failure is present even with only 96 rows — far below the ~50 K threshold of
the IAM scale bug (Gap 1) — ruling out the IAM traversal as the cause.  The failure
is also isolated to the single table with an `xml NOT NULL` column; all other heap
tables in those databases pass.

The most likely root cause is that SQL Server 2008R2–2014 used a different byte layout
for LOB pointer structures stored inside heap data pages when the LOB type is `xml`
(as opposed to `varbinary(max)` or `varchar(max)`).  SQL Server 2016 changed this
internal representation.  When mssqlbak follows the LOB pointer to fetch the XML blob,
it applies the current format's parsing rules and either reads garbage or skips the row.

Note: `dbo.DatabaseLog` in `AdventureWorks2016_EXT.bak` also fails, but that is due to
the IAM scale bug (Gap 1) — the extended database has a much larger `DatabaseLog` than
the standard edition.

### Why SS2022 fixtures cannot reproduce this

The SQL Server 2022 instance that creates synthetic fixtures always writes pages in
2022 format.  There is no way to generate pre-2016 LOB pointer layouts from a 2022
instance.

### Action

1. Obtain the raw bytes of a failing heap page from `AdventureWorks2012.bak` and a
   passing heap page from `AdventureWorks2016.bak` for `dbo.DatabaseLog` and compare
   the LOB pointer layout at the field offset for `XmlEvent`.
2. Add pre-2016 LOB pointer handling to `mssqlbak/lob.py` (or wherever inline LOB
   pointers are decoded).
3. Because a synthetic fixture cannot reproduce this format, regression testing for the
   fix must use the real sample BAK files.  Add
   `AdventureWorks2012.bak::dbo.DatabaseLog` as a named CI expectation once the fix
   lands.

---

## Related

- `docs/GAP_ANALYSIS.md` — extraction-engine gaps (storage formats, data types, backup
  container variants)
- `docs/SAMPLE_TESTING_PLAN.md` — sample corpus methodology and phased plan
- `docs/SAMPLE_COVERAGE.md` — per-sample extractability snapshot
- `docs/correctness_coverage.md` — correctness results for committed fixtures
- `docs/correctness_coverage_samples.md` — correctness results for the real-world corpus
- `tests/fixtures_2022/` — SS2022-generated synthetic fixtures (primary; default `FIXTURE_DIR`)
- `tests/fixtures_2017/` — SS2017-generated fixtures (empty, creation pending)
- `tests/fixtures_2019/` — SS2019-generated fixtures (partially created)
- `tests/fixtures_2025/` — SS2025-generated fixtures (empty, creation pending)
- `tests/fixtures_realworld/` — downloaded real-world corpus (git-ignored)
