# Plan: CCI Correctness and Dirty-Path Min/Max Closure

**Date:** 2026-06-17  
**Status:** 🟩 C1b done · 🟩 D1+D2 done · 🟩 C2 done · 🟩 xfail done · ⚠ C1a blocked (columnstore.py) · ⚠ B blocked (columnstore.py)

**Sources:** `correctness_coverage.md` (78 engineered fixtures) · `correctness_coverage_samples.md`
(46 real-world fixtures)

| Stream | Description | Impact | Status |
|--------|-------------|--------|--------|
| C1b | CCI FOR min/max — small-to-medium segments | **6 fixtures** (3 engineered + 3 real-world) | ✅ |
| D1 + D2 | Dirty-path min/max — delete ghost + temporal update | 2 engineered | ✅ |
| C2 | LOB column min/max — PAGE/ROW-compressed tables | 1 engineered | ✅ |
| C1a | CCI small-segment null count — 100-row segments | 1 engineered | ⚠ blocked (columnstore.py) |
| B | enc=5 ARCHIVE multi-sub-block (≥32,768 rows) | 1 engineered + 17 unit tests | ⚠ blocked (columnstore.py) |
| xfail | Promote In-Memory OLTP tables from ✗ → ~ | 3 fixtures reclassified | ✅ |

**Related:**
- [`260616-status.md`](260616-status.md) — TODO-G3/G6, Phase 5 open gaps
- [`260616-3-random-order-fixtures-plan.md`](260616-3-random-order-fixtures-plan.md) — upstream context
- [`correctness_coverage.md`](correctness_coverage.md) — engineered fixture failures
- [`correctness_coverage_samples.md`](correctness_coverage_samples.md) — real-world fixture failures

---

## 0. Combined failure map

### 0.1 Engineered fixtures (`correctness_coverage.md`)

**78 fixtures · 69 pass · 1 xfail · 8 fail**

| # | Fixture | Failing metric | Root cause | Stream |
|---|---------|---------------|------------|--------|
| E1 | `archive_columnstore_partition_full.bak` | Null 1/3 on `archive_part_mixed`, `_roundtrip`, `_single` | enc=5 ARCHIVE multi-sub-block null bitmap (≥32,768 rows) | **B** |
| E2 | `columnstore_minimal.bak` | Null 9/12 on `cs_100` | Small-segment (100-row) CCI null bitmap | **C1a** |
| ~~E3~~ | ~~`columnstore_minimal.bak`~~ | ~~Min/max 22/24 on `cs_1000`; 23/24 on `cs_10000`~~ | ~~FOR-base min/max decode on medium CCI segments~~ | ~~**C1b**~~ ✅ |
| ~~E4~~ | ~~`compressioncoverage_full.bak`~~ | ~~Min/max 25/26 on `cmp_columnstore`; 25/26 on `cmp_columnstore_archive`~~ | ~~Same FOR-base issue~~ | ~~**C1b**~~ ✅ |
| E5 | `compressioncoverage_full.bak` | Min/max 10/12 on `cmp_page_lob`; 10/12 on `cmp_row_lob` | LOB column min/max under PAGE/ROW compression | **C2** |
| ~~E6~~ | ~~`cs_lob_preamble.bak`~~ | ~~Null 1/2~~ | ~~G44 Huffman decode (xmhuffman)~~ | ~~**G44**~~ ✅ |
| ~~E7~~ | ~~`cs_lob_preamble2.bak`~~ | ~~Null 1/2~~ | ~~G44 Huffman decode (xmhuffman)~~ | ~~**G44**~~ ✅ |
| E8 | `dirtycoverage_delete.bak` | Min/max 5/6 on `delete_test` | Ghost record included in min/max but not row count | **D1** |
| E9 | `dirtycoverage_temporal_update.bak` | Min/max 7/8 on `temporal_test` | Temporal UPDATE — shifted period column min/max | **D2** |
| E10 | `featurecoverage_full.bak` | `memory_oltp` row ✗ + col ✗ | XTP / In-Memory OLTP — expected behavior | **xfail** |

### 0.2 Real-world fixtures (`correctness_coverage_samples.md`)

**46 fixtures · ~38 pass · 8 fail**

| # | Fixture | Failing metric | Root cause | Stream |
|---|---------|---------------|------------|--------|
| R1 | `AdventureWorksDW2016_EXT.bak` | Null 410/413; min/max 805/814 | ARCHIVE CCI FOR-base min/max (G3) | **C1b** |
| R2 | `ContosoRetailDW.bak` | Min/max 691/736 | ARCHIVE CCI FOR-base min/max (G3) | **C1b** |
| R3 | `WideWorldImporters-Full.bak` | Row 46/48 *(XTP)*; null 523/525; min/max 978/1004 | Row count: XTP xfail; null/min/max: temporal `_Archive` tables with ARCHIVE CCI (G3) | **xfail** + **C1b** |
| R4 | `WideWorldImporters-Full_old.bak` | Row 46/48 *(XTP)*; null 523/525; min/max 978/1004 | Same as R3 | **xfail** + **C1b** |
| R5 | `AdventureWorks2016_EXT.bak` | Row 85/92: 5 `_inmem` tables + 2 `Demo.*` tables missing | 5 = XTP xfail; 2 `Demo.*` = outside scope | **xfail** *(partial)* |
| R6 | `CreditBackup100.bak` | Row 9/10 on `dbo.charge`; null 85/93; min/max 181/182 | `charge` row count = unknown; null/min/max = separate legacy-encoding issue | **outside scope** |
| R7 | `NYCTaxi_Sample.bak` | Null 17/23 | Unknown — not yet investigated | **outside scope** |
| R8 | `tpcxbb_1gb.bak` | Null 377/394; min/max 773/774 | Partly G3 (ARCHIVE CCI min/max); partly G1 (inventory/web_clickstreams row counts — separate) | **C1b** *(partial)* + **outside scope** |

### 0.3 Streams not in this plan

| Item | Fixture(s) | Why deferred |
|------|-----------|--------------|
| ~~G44 binary pool~~ | ~~`cs_lob_preamble` × 2~~ | ~~Complex xVelocity inter-bookmark decode; separate plan needed~~ | ✅ Resolved — `_decode_v4_huff_dict` via xmhuffman; 1200/1200 strings (commit b8993f1) |
| `Demo.*` tables missing | `AdventureWorks2016_EXT` | Unknown root cause; not `_inmem`, not CCI |
| `dbo.charge` row count | `CreditBackup100` | Legacy SQL Server 2000 database; separate issue |
| NYCTaxi null counts | `NYCTaxi_Sample` | Not yet investigated |
| G1 row/null counts | `tpcxbb_1gb` (`inventory`, `web_clickstreams`) | Separate from min/max; prior plan item |
| **⚠ cs_lob_preamble{,2} null 1/2** | `cs_lob_preamble.bak`, `cs_lob_preamble2.bak` | Both show null 1/2 in `.venv` now `.venv` (unified). Likely in `columnstore.py` `_decode_v4_huff_dict` multi-page path. Revisit after parallel columnstore.py work merges. |

---

## 1. Execution sequence

The sequence is determined by two factors: (a) **impact** — how many fixtures a fix closes, and
(b) **investigation cost** — whether diagnosis is needed before coding.

```
Step 1: C1b  ──► closes E3, E4, R1, R2, R3/R4 (Archive tables), R8 (partial)
Step 2: D1 + D2  ──► closes E8, E9
Step 3: C2   ──► closes E5
Step 4: C1a  ──► closes E2
Step 5: B    ──► closes E1 + 17 pre-existing unit tests
Step 6: xfail ──► reclassifies E10, R3/R4 row count, R5 (_inmem)
```

**Why C1b first:** it is the single highest-impact fix, reaching across 3 engineered
fixtures and 4+ real-world databases (AW-DW2016_EXT, ContosoRetailDW, WWI-Full × 2
archive tables, tpcxbb partial). All four are long-standing failures in the real-world
scorecard. Fixing C1b is also a prerequisite for understanding whether R3/R4 and R8
pass after the Archive-table min/max is resolved.

---

## Stream C1b — CCI FOR-base min/max ✅ DONE

### Root cause (resolved 2026-06-17)

The `_bitpack_values` function was treating the first `u32` of each CCI fragment-table
entry as a per-block Frame-of-Reference (FOR) compression base and adding it to the
extracted biased stored values.  That interpretation was **wrong**.

Each 8-byte fragment table entry is a **block-type descriptor**:

| field1 (u32) | field2 (u32) | meaning |
|---:|---:|--------|
| `0` | `n_null` | this original-position block is in the null zone |
| `2` | `n_rows` | this original-position block is in the compact-null-prefix data zone |

The first field encodes the block's null-encoding mode (`0` = null zone, `2` = compact
null-prefix), **not** an additive correction for the stored biased values.

**Evidence:**
- The Rust decoder (`decode_cs_segment`) ignores the fragment table entirely and
  produces exact values for DECIMAL, DATETIME2, etc. (all columns except TIME).
- TIME falls back to the Python path, which was the only path applying the correction.
- Removing the correction fixes cs_1000 TIME: min `00:01:00.003` → `00:01:00.001` ✓,
  max `16:40:00.002` → `16:40:00.000` ✓.
- All other column types that use `_bitpack_values` (no-Rust fallback) are also fixed.

**Z09 relevance:** The Zukowski PhD thesis (Z09) defines classical FOR compression:
`bitpack_stored = c[i] - block_min`.  SQL Server CCI does **not** use this encoding
in the bitpack — the stored biased values are absolute, not block-relative.  Z09 is
useful background for understanding why the fragment table looks like a FOR table but
is not; the per-block range information it stores is used purely for predicate pushdown
(skip-scan), not for decompression.

**L11 relevance:** Confirmed as the canonical formula source.  The formula
`actual = base_id + data_id × magnitude` (where `base_id` = `seg.mn`, `magnitude` =
step size, `data_id` = biased stored − 1) is correct and was already implemented
correctly in `_decode_enc1`.  The only bug was the spurious FOR correction layered on
top of this correct formula.

### Fix

`mssqlbak/columnstore.py` `_bitpack_values`:

- Removed the fragment-table read loop and the `_any_nonzero` correction block.
- Updated docstring to document the fragment table's true semantics (block-type
  descriptor, not FOR base).

### Outcome

| Table | Before | After |
|-------|--------|-------|
| `cs_1000` min/max | 22/24 | **24/24** ✓ |
| `cs_10000` min/max | 23/24 | **24/24** ✓ |
| `cmp_columnstore` min/max | 25/26 | **26/26** ✓ |
| `cmp_columnstore_archive` min/max | 25/26 | **26/26** ✓ |

Zero regressions in the test suite (1,403 pass, 141 skip, 3 xfail).

---

## Stream D1 + D2 — Dirty-path min/max

### D1 — `dirtycoverage_delete.bak` min/max 5/6

**Key clue (CORROBORATION_SOURCES §3.2 ghost record + search results):**

Status Byte A bits 1–3 = **6** = "ghost data record". `dirtycoverage_committed_delete.bak`
**passes** 6/6 min/max — same row count passes there too. The distinction: in
`committed_delete`, the deleted row was not the extreme value; in `delete`, it was.
Ghost records are filtered from the row count but the **min/max aggregation uses a
different code path** that may not apply the ghost filter.

**Path:** Find the min/max aggregation in `rows.py` or the extractor. Confirm it routes
through the same ghost-record filter as the row count. If not, add the filter.

### D2 — `dirtycoverage_temporal_update.bak` min/max 7/8

**Key clue (CORROBORATION_SOURCES V13 + search results):**

Temporal table UPDATEs do **not** create ghost records in the current table (old row →
history; current table updated in-place). `temporal_test_history` has 0 rows. The 1
wrong min/max check out of 8 (4 columns × 2) is on the live `temporal_test` table.
The UPDATE shifted the min/max of some column — most likely `valid_from` (period
column, changes to transaction timestamp on UPDATE). If mssqlbak's DATETIME2 decode
for an in-place-updated row is wrong (e.g., reads a stale version or misreads the
updated bytes), the period-column min would be wrong.

**Path:** Identify which 1 of the 8 checks fails (inspect `.stats.json` vs mssqlbak
output for each column). If it's `valid_from`, cross-check the DATETIME2 decode for
the updated-row layout.

### Success criteria

- `dirtycoverage_delete.bak` min/max 6/6 ✓
- `dirtycoverage_temporal_update.bak` min/max 8/8 ✓

---

## Stream C2 — LOB min/max

### Scope

`compressioncoverage_full.bak`: `cmp_page_lob` and `cmp_row_lob` each 10/12 min/max.
Both tables have 3 source rows. The 2 wrong checks per table are almost certainly
`VARCHAR(MAX)` or `NVARCHAR(MAX)` columns.

### Key clue (`MS-PAGE-EXT` + search results)

`MS-PAGE-EXT` (Microsoft Page and Extent Architecture Guide) confirms:
> *"By default for LOB columns, the data is stored in row if there's sufficient space.
> Otherwise, the row contains a 16-byte pointer to a separate tree of text/LOB pages."*

> "Off-row data is **not compressed** even under PAGE/ROW compression." LOB data stored
> off-row goes through the btyp=5→2→3 chain, same as uncompressed. For values ≤8,000
> bytes (which 3-row test data likely is), the data may be stored **in-row** as part of
> the compressed row record (CD record decoder path), not through the LOB chain at all.

**C2 root cause hypothesis (from `MS-PAGE-EXT`):** when the LOB value is stored
off-row, mssqlbak reads the 16-byte LOB pointer from the row record instead of the
actual string, producing a garbage min/max. Check whether the two failing columns are
stored off-row vs in-row (3 rows × small strings likely fit in-row; if not, the
off-row LOB decode path is missing).

The failure is likely one of:
- String comparison done on raw bytes instead of decoded string (latin1 vs UTF-8 vs UTF-16 mismatch)
- In-row LOB value routed through a different decode path than expected
- Off-row LOB pointer being returned as the min/max value instead of dereferencing the LOB chain

**Path:** Identify which 2 columns per table fail. Check if they are stored in-row or
off-row. Compare the raw bytes mssqlbak returns against `stats.json` expected values.

### Success criteria

- `compressioncoverage_full.bak` LOB tables min/max 12/12 ✓ (was 10/12 × 2)

---

## Stream C1a — CCI small-segment null count (100-row segments)

### Scope

`columnstore_minimal.bak`: `cs_100` null 9/12 (3 wrong). `cs_1` and `cs_10` pass 12/12.
The failure starts at 100 rows.

### Key clue (`STAIR4` + `DARLING-RGE`)

`STAIR4` confirms: *"`null_value` represents the magic value SQL Server has chosen to
use to represent NULL values in this segment."* The `has_nulls` flag is 1 if any NULL
exists; `null_value` is the sentinel used in the bitpacked data.

`DARLING-RGE` confirms: *"Information about NULLs is stored internally and can be used
for rowgroup elimination."* The `has_nulls` / `null_value` metadata is the segment-level
signal; the actual per-row null bitmap is a separate structure.

### Path

The 3 wrong null counts are on specific column types. At 100 rows a CCI segment is a
single block (well below the enc=5 multi-sub-block boundary of ~32,768 rows). The null
bitmap for non-ARCHIVE CCI at this size should be straightforward. Identify which 3
column types fail (likely a specific scalar type: FLOAT, DATE, DECIMAL?). Check if the
null sentinel value for that type differs from what `_decode_null_bitmap` expects.
Cross-reference `has_nulls` and `null_value` from the `*.segments.json` sidecar to
confirm the segment-level NULL metadata matches the expected column types.

### Success criteria

- `columnstore_minimal.bak` null 12/12 ✓ (was 9/12 on `cs_100`)

---

## Stream B — enc=5 ARCHIVE multi-sub-block (highest unit test count)

### Scope

`archive_columnstore_partition_full.bak`: null 1/3 on `archive_part_mixed`,
`_roundtrip`, `_single`. Each has 140,000 rows / 4 partitions = 35,000 rows per
segment — above the 32,256-row chunk boundary.

17 pre-existing unit test failures in `test_archive_columnstore_partition_coverage.py`
provide full regression coverage.

### Key clue (CORROBORATION_SOURCES G6 note — Paul White)

> "64-bit bitpack unit = 7 × 9-bit subunits → 4,608 units = **32,256** rows; boundary
> is a bitpack-unit/chunk artifact."

The chunk boundary is 32,256, not 32,768 (2^15). The `_decode_enc5_archive` null-bitmap
logic for the multi-sub-block case needs to account for this exact boundary. The
`DBCC CSINDEX(object_type=1)` output is the A1 verifier (per `260616-status.md`).
The `*.segments.json` sidecars for all 4 SS versions are already committed.

### Path

1. Run `DBCC CSINDEX` on one failing column to expose the exact `hasNulls`, `NullValue`,
   RLE layout, and bitpack boundaries for a 35,000-row segment.
2. Compare the DBCC output against `_decode_enc5_archive`'s null-bitmap logic for the
   multi-block case.
3. Fix the null-bitmap position/sentinel for blocks beyond the first sub-block.

### Success criteria

- `archive_columnstore_partition_full.bak` null 12/12 ✓ (was 6/12)
- All 17 tests in `test_archive_columnstore_partition_coverage.py` pass

---

## Stream xfail — In-Memory OLTP reclassification

### Tables to promote

| Fixture | Tables | Action |
|---------|--------|--------|
| `featurecoverage_full.bak` | `dbo.memory_oltp` | ✗ fail → ~ xfail |
| `AdventureWorks2016_EXT.bak` | `Production.Product_inmem`, `Sales.SalesOrderDetail_inmem`, `Sales.SalesOrderHeader_inmem`, `Sales.SpecialOffer_inmem`, `Sales.SpecialOfferProduct_inmem` | ✗ → ~ xfail (XTP tables) |
| `WideWorldImporters-Full.bak` × 2 | `Warehouse.ColdRoomTemperatures`, `Warehouse.VehicleTemperatures` | ✗ → ~ xfail (XTP tables) |

All are In-Memory OLTP (Hekaton/XTP) tables. mssqlbak correctly classifies them as
`skip_reason = "memory-optimized"`. The ✗ is a reporting artifact — the correctness
scorer does not respect the skip classification. Fix: update `correctness_coverage.py`
to mark XTP-skipped tables as expected absences.

**Note:** After xfail promotion, `AdventureWorks2016_EXT.bak` would still show 87/92
(7 tables missing → 5 xfail + 2 `Demo.*` unexplained — outside this plan's scope).

---

## 0.4 Net correctness target after this plan

### Engineered fixtures (`correctness_coverage.md`)

**Current:** 69 pass · 1 xfail · 8 fail  
**Target (updated):** 77 pass · 3 xfail · 0 fail (G44 also resolved)

| Change | Count |
|--------|-------|
| B, C1a, C1b, C2, D1, D2 fixed | +6 → pass |
| featurecoverage xfail promoted | 1 ✗ → ~ |
| cs_lob_preamble × 2 (G44) | ✅ +2 → pass (requires xmhuffman wheel) |

### Real-world fixtures (`correctness_coverage_samples.md`)

**Current:** ~38 pass · 8 fail  
**Target:** ~43 pass · 3 fail (outside scope) · 2 partial-xfail

| Change | Fixture |
|--------|---------|
| C1b fixes ARCHIVE CCI min/max | AW-DW2016_EXT → ✓; ContosoRetailDW → ✓ |
| C1b fixes Archive table null/min/max | WWI-Full × 2: Archive portion ✓; XTP row count → ~ xfail |
| xfail promotion | AW2016_EXT: 5 inmem → ~; still 87/92 (2 Demo.* outside scope) |
| Outside scope | CreditBackup100, NYCTaxi, tpcxbb (G1 portion) remain ✗ |

---

## 0.5 Historical progress — baseline → current

Baseline commit: `ac6a710` ("fix: extend min/max coverage to all types")  
Current state: local working tree (uncommitted regeneration, 2026-06-17)

| Fixture | Baseline | Current | Movement |
|---------|----------|---------|----------|
| `AdventureWorks2008R2.bak` – `2022.bak` (8 DBs) | 3/71 ⚠ each | **71/71 ✓** | fully fixed |
| `AdventureWorksLT2012.bak` – `2022.bak` (6 DBs) | 1–2/12 ⚠ each | **12/12 ✓** | fully fixed |
| `AdventureWorksDW2012.bak` | 30/31 ⚠ | **31/31 ✓** | fully fixed |
| `AdventureWorksDW2016_EXT.bak` | 32/33 ⚠ | **33/33 ✓** | fully fixed |
| `CreditBackup100.bak` | 1/10 ⚠ | **10/10 ✓** | fully fixed (inc. uncommitted regen: 4/10 → 10/10) |
| `Pubs.bak` | 10/11 ⚠ | **11/11 ✓** | fully fixed |
| `SalesDBOriginal.bak` | 0/5 ⚠ | **5/5 ✓** | fully fixed |
| `WideWorldImporters-Standard.bak` (both variants) | 2/48 ⚠ each | **48/48 ✓** | fully fixed |
| `WideWorldImportersDW-Standard.bak` | 13/24 ⚠ | **24/24 ✓** | fully fixed |
| `tpcxbb_1gb.bak` *(row count)* | 3/30 ⚠ | **30/30 ✓** | fully fixed |
| `WideWorldImportersDW-Full.bak` | *(not in suite)* | **24/24 ✓** | new fixture, passing |
| `AdventureWorks2016_EXT.bak` | 5/92 ⚠ | 85/92 ⚠ | improved, not fixed (7 missing tables) |
| `WideWorldImporters-Full.bak` (both variants) | 2/48 ⚠ each | 46/48 ⚠ | improved, not fixed (2 XTP + Archive tables) |

### Net scorecard

| | Baseline (`ac6a710`) | Current |
|-|---------------------|---------|
| Fully passing fixtures | ~30 | 45 |
| Failing fixtures | 16 | 3 |
| Worst miss | `SalesDBOriginal` 0/5; `tpcxbb` 3/30 | `AW2016_EXT` 85/92; `WWI-Full` 46/48 |

22 rows of ⚠ warnings were eliminated. All AdventureWorks OLTP and LT variants, all DW
variants, both WWI-Standard variants, tpcxbb, Pubs, SalesDB, CreditBackup100 are now
fully passing. The 3 remaining failing fixtures — `AdventureWorks2016_EXT`, `ContosoRetailDW`,
`WideWorldImporters-Full` × 2 — are all tracked in this plan (Streams C1b and xfail).

---

## Open questions (to be answered in each stream)

| ID | Question | Stream |
|----|----------|--------|
| OQ-1 | Which 2 column types fail min/max in `cs_1000`? Are they enc_type=1 or enc_type=3? | C1b |
| OQ-2 | Does the `*.segments.json` sidecar `min_data_id` match `stats.json` for failing columns? | C1b |
| OQ-3 | Is the D1 ghost filter applied in the min/max aggregation path? | D1 |
| OQ-4 | Which of the 8 min/max checks fails in `temporal_test`? Is it `valid_from`? | D2 |
| OQ-5 | Are `cmp_page_lob` LOB values stored in-row or off-row in the PAGE-compressed record? | C2 |
| OQ-6 | Which 3 column types produce wrong null counts in `cs_100`? | C1a |
| OQ-7 | What is the exact multi-sub-block null bitmap layout — verified by DBCC CSINDEX output? | B |
| OQ-8 | Are WWI-Full `_Archive` null failures also G3 (FOR-base), or a separate issue? | C1b |

### New source corroboration added (2026-06-17 4-degree sweep)

| Stream | New source token | Key finding |
|--------|-----------------|-------------|
| C1b | `L11 §2.2.1` (Larson et al. SIGMOD 2011, CMU mirror) | **Canonical source**: decimal exponent positive (scale up), integer exponent negative (scale down); `actual = (stored + base_id) / 10^exponent`; free mirror at 15721.courses.cs.cmu.edu |
| C1b | `STAIR4` (Hugo Kornelis / SQLServerCentral) | Best public explanation of `base_id`/`magnitude`: *"base_id is subtracted from the value, magnitude scales it"* |
| C1b | Paul White `sql.kiwi` "Grouped Aggregate Pushdown" | `DBCC CSINDEX` shows `BaseId`/`Magnitude`/`MinDataId`/`MaxDataId` as ground-truth verifier |
| C1a | `STAIR4` | `null_value` = *"magic value SQL Server chosen to represent NULL in this segment"* |
| C1a | `DARLING-RGE` (Erik Darling) | NULLs stored internally; `has_nulls`/`null_value` is the segment-level null signal |
| C2 | `MS-PAGE-EXT` (MS Page/Extent Architecture Guide) | Off-row LOB → 16-byte pointer; mssqlbak reads pointer not value → garbage min/max for off-row LOB columns |
| D1 | (no new source) | Ghost record min/max filter remains empirical |
| D2 | (no new source) | Temporal UPDATE period-column min/max remains empirical |
| B | (no new source) | enc=5 32,768-row null bitmap boundary remains empirical |
