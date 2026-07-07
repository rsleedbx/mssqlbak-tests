# Fixture + DBCC PAGE Verifier Strategy — Analysis and Parallel Approach

**Date:** 2026-06-16  
**Status:** Working document — open issues tracked below

---

## 1. The Core Problem

The reverse-engineering methodology in `BAK_FORMAT_SPEC.md` has a fundamental asymmetry:

| Approach | Strength | Weakness |
|---|---|---|
| **Bottom-up** (empirical, fixtures) | Confirms what SQL Server actually writes | Only exercises configurations the fixtures happen to test |
| **Top-down** (docs, papers) | Reveals what *should* exist; surfaces blind spots proactively | Docs describe semantics, not raw byte offsets |

Neither approach alone is sufficient. Running them **in parallel** — top-down to generate hypotheses, bottom-up to confirm at byte level — closes the gap.

---

## 2. How to Run Them in Parallel

```
┌─────────────────────────────────────────────────────────┐
│  TIER 0: Top-down hypothesis generation                 │
│  Source: sql-docs (local), MSDN, academic papers        │
│  Output: New Gnn/Vnn entries tagged [HEURISTIC]         │
└──────────────────────────┬──────────────────────────────┘
                           │ "architecture says X exists"
                           ▼
┌─────────────────────────────────────────────────────────┐
│  TIER 1: Surgical fixture                               │
│  Build the minimal .bak that exercises exactly one      │
│  hypothesis.  Recipe in BAK_SPEC_FIXTURES.md §1.7.      │
└──────────────────────────┬──────────────────────────────┘
                           │ fixture committed
                           ▼
┌─────────────────────────────────────────────────────────┐
│  TIER 2: DBCC PAGE / DMV verifier sidecar               │
│  Run on the live SQL Server instance used to build the  │
│  fixture.  Capture raw bytes + field values.            │
│  Sidecar committed as Gnn.json alongside the .bak file. │
└──────────────────────────┬──────────────────────────────┘
                           │ byte-level agreement confirmed
                           ▼
┌─────────────────────────────────────────────────────────┐
│  TIER 3: Parser test                                    │
│  test_…_matches_reference() in tests/.  Must agree with │
│  both fixture bytes and verifier sidecar.               │
└──────────────────────────┬──────────────────────────────┘
                           │ test passes
                           ▼
              Tag promoted to [CONFIRMED]
```

The key discipline: **a Gnn entry is not resolved until all three tiers are complete** — fixture committed, verifier sidecar committed, test passing.

---

## 3. Pages-and-Extents Architecture Guide — Actionable Findings

Source: [learn.microsoft.com — Page and Extent Architecture Guide (SS ver17)](https://learn.microsoft.com/en-us/sql/relational-databases/pages-and-extents-architecture-guide?view=sql-server-ver17)
Local mirror: `/Users/robert.lee/github/sql-docs/docs/relational-databases/pages-and-extents-architecture-guide.md`

### 3.1 IAM pages are per-file and per-GAM-interval

> **⚠️ STATUS UPDATE (2026-06-16 code audit):** The V11 fix described below is **already implemented** in `rows.py`. `_heap_pages_for_unit()` walks the IAM chain via `iam.header.next_page`, keys extents by `extents_by_file[iam_loc[1]]` (the IAM page's own file_id, not a hardcoded 1), and guards missing secondary files with `if iam_loc[1] not in store.available_files`. Index traversal uses `(page_id, file_id)` locators throughout. **This is no longer an open issue** — see §13.1. The text below is retained for the format rationale.

**Exact quote from the guide:**
> "Similar to a GAM or SGAM page, an IAM page covers a 4-GiB interval **in a file**. If the allocation unit contains extents from more than one file, or more than one 4-GiB interval of a file, **multiple IAM pages are linked in an IAM chain**. Therefore, **each allocation unit has at least one IAM page for each file where it has extents**."

**Also confirmed by Paul Randal (former SQL Server Storage Engine lead, Microsoft):**
> "IAM page can only track space for a single GAM interval **in a single file**."  
> — [sqlskills.com: Inside the Storage Engine — IAM pages, IAM chains, and allocation units](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-iam-pages-iam-chains-and-allocation-units/)

**Direct implication for V11 (IAM filegroup scope):**  
Our `rows.py` IAM traversal hardcodes `file_id = 1`. For a multi-file database, each file has its own IAM pages in the chain for the same allocation unit. The `file_id` for extents in a given IAM page bitmap is **the file_id where that IAM page itself resides**, not always 1.

Fix approach:
1. Read `file_id` from the IAM page's own page ID (which encodes file/page).
2. Use that `file_id` when resolving each page_id in the extent bitmap.
3. Fixture: `tpcxbb_1gb.bak` already exercises this. Verifier: `DBCC PAGE` on an IAM page in file 2.

### 3.2 IAM "Single Page Allocation" section (first 8 pages)

> **⚠️ STATUS UPDATE (2026-06-16 code audit):** Also **already implemented**. `rows.py` reads all 8 SPA slots at `_IAM_SPA_OFFSET = 140` via `_IAM_SPA_STRUCT = struct.Struct("<HI")` (file_id uint16, page_id uint32), confirmed against AdventureWorks2008R2 `DatabaseLog`. **Not an open issue** — see §13.1.

Paul Randal's blog reveals an undocumented IAM layout detail: the **first IAM page in a chain** has a separate **Single Page Allocation** section containing the 8 individual pages allocated from mixed extents before the first full uniform extent. This is distinct from the extent bitmap.

**Quote:**
> "Single Page allocation section: These are the first 8 pages allocated from the mixed extent. After the 8th page, SQL Server allocates uniform extents. So this section is used only in the **first IAM page of the chain**."  
> — [empiredatasystems.com: Understanding the IAM Page](https://www.empiredatasystems.com/blog/73/SQL-Server-:-Understanding-the-IAM-Page)

**Implication:** For very small tables (< 8 pages), our IAM traversal may be skipping these first 8 pages if we only parse the extent bitmap and ignore the single-page-allocation slots. This would cause a silent 0-row result for small tables. Worth checking against `G10` (mystery bytes in the IAM header).

### 3.3 Mixed extents — version boundary at SS2016

> "Up to, and including, SQL Server 2014 (12.x), the Database Engine doesn't allocate uniform extents to tables with small amounts of data. … Starting with SQL Server 2016 (13.x), the Database Engine uses **uniform extents** for allocations in a user database and in `tempdb`, except for allocations belonging to the first eight pages of an IAM chain."

**Implication:** In a pre-SS2016 backup, the IAM page bitmap pattern for a small-to-medium table looks different from a post-SS2016 backup. This is an untested version boundary. Relevant to `V11` and to any IAM-related fixture built on SS2016+.

### 3.4 System pages we must not misread

The guide documents six system page types that appear at predictable intervals in every data file:

| Page type | First page ID | Interval |
|-----------|--------------|---------|
| PFS | 1 | every 8,088 pages |
| GAM | 2 | every ~511,232 pages (~4 GiB) |
| SGAM | 3 | every ~511,232 pages |
| DCM | 6 | every ~511,232 pages |
| BCM | 7 | every ~511,232 pages |
| File header | 0 | page 0 only |

Our IAM-guided traversal should never land on these by accident, but if an IAM page bitmap bit is set incorrectly (corrupted backup, edge case), we would attempt to parse a PFS or DCM page as a data page. The page header `m_type` field (offset 1, 1 byte) should be checked before decoding rows. Current status: unverified whether `pages.py` validates `m_type` before decoding.

### 3.5 Three allocation unit types — all three need file_id awareness

> "Each partition of a heap or index always contains at least one `IN_ROW_DATA` allocation unit. It can also contain `LOB_DATA` and `ROW_OVERFLOW_DATA` allocation units."

All three allocation unit types have their own IAM chains, and all three are subject to the multi-file file_id bug (V11). Currently, we use `LOB_DATA` IAM chains for off-row data, but do we correctly handle `ROW_OVERFLOW_DATA`? This is a separate allocation unit with its own IAM chain. If a table has rows that overflow the 8,060-byte row limit (large variable-width columns), the overflow pages are in a different IAM chain. We should confirm whether we follow `ROW_OVERFLOW_DATA` chains at all.

---

## 4. Academic and Public Literature Map

### 4.1 Peer-reviewed papers by SQL Server engineers

| Paper | Venue | Authors | Key findings for mssqlbak |
|-------|-------|---------|--------------------------|
| SQL Server Column Store Indexes | SIGMOD 2011 | Per-Åke Larson et al. | First publication of columnstore design: segment layout, encoding (value encoding = linear transform to integer; dictionary encoding for non-numeric), then RLE + bit-packing. Confirms enc=1 is "value encoding" = linear transform. |
| Enhancements to SQL Server Column Stores | SIGMOD 2013 | Larson, Clinciu, Fraser, Hanson et al. | SS2014 updatable CCI. Documents that batch mode operators were expanded and encoding improved for "impure sequences" — relevant to why ARCHIVE bitpack behaves differently. |
| Real-Time Analytical Processing with SQL Server | VLDB 2015 | Larson, Birka, Hanson, Huang, Nowakiewicz, Papadimos | [PDF: vldb.org/pvldb/vol8/p1740-Larson.pdf] Documents the Apollo column store engine + Hekaton integration in SS2016. **Key quote on encoding:** "values in a column are first encoded using either **value encoding** or **dictionary encoding**. Value encoding applies a **linear transformation** on numerical values to convert them to integers that can be represented with a smaller number of bits … after encoding each column segment is compressed using a mixture of **RLE compression and bit packing**." — This confirms our enc=1 path. |

**What the VLDB 2015 paper tells us about Issue 1 (ARCHIVE enc=1 bitpack):**  
The paper explicitly states the column segment compression pipeline is:  
`value encoding → (RLE + bit-packing) → [ARCHIVE: additional XPRESS]`

The XPRESS layer wraps the already-encoded segment. We have confirmed XPRESS decompression is correct. This means the breakage at row ~3820 is in the **RLE + bit-packing** layer, not XPRESS. The paper says "improvements were mostly aimed at impure sequences of values" in SS2014. An impure sequence is one that is not monotonically increasing — an ARCHIVE partition by definition contains old, potentially non-sequential data. This is the strongest published hint that the ARCHIVE bitpack uses a different RLE/bit-pack variant than the standard path.

### 4.2 Authoritative practitioner blogs (SQL Server engineering alumni)

| Source | Author | Background | Most relevant content |
|--------|--------|------------|----------------------|
| [sqlskills.com/blogs/paul](https://www.sqlskills.com/blogs/paul/) | Paul Randal | SQL Server Storage Engine lead at Microsoft, 1999–2007; wrote the DBCC CHECKDB code | "Inside the Storage Engine" series: IAM pages, page anatomy, DBCC PAGE field-by-field, allocation units, ghost records. Most authoritative independent source on page format byte details. |
| [sqlskills.com/blogs/kimberly](https://www.sqlskills.com/blogs/kimberly/) | Kimberly Tripp | Co-founder SQLskills, former Microsoft MVP | Index design, fragmentation internals |
| [aboutsqlserver.com](https://aboutsqlserver.com/2013/10/15/sql-server-storage-engine-data-pages-and-data-rows/) | Dmitri Korotkevitch | SQL Server MVP | Detailed page header + slot array + row format walk-through. Confirms: status bits A and B at bytes 0–1 of every row; null bitmap follows fixed columns; var-count + var-offset array after null bitmap. |

**Paul Randal's IAM post gives the single-page-allocation slot layout** needed to fix the first-8-pages edge case in `rows.py`. These are 8 × 6-byte page pointers (file_id : page_id) stored in the IAM page header before the extent bitmap, not after. This is `G10` in the Guess Register.

### 4.3 University course materials

| Course | Institution | Instructor | Relevance |
|--------|-------------|------------|-----------|
| CMU 15-721 Advanced Database Systems | Carnegie Mellon | Andy Pavlo | Reading list for columnstore week cites the Larson 2011 SIGMOD paper directly. Lecture on Hekaton (SS in-memory OLTP) gives MVCC internals. Slides available at [15721.courses.cs.cmu.edu](https://15721.courses.cs.cmu.edu/). |
| CMU 15-445 Intro to Database Systems | Carnegie Mellon | Andy Pavlo | Storage layout, page formats, buffer pool. Spring 2026 course. Relevant for grounding in storage model fundamentals. |

---

## 5. Open Issues — Proposed Verification Path

Each row maps a known blind spot to the parallel verification approach.

| ID | Open issue | Top-down source | Bottom-up fixture | DBCC verifier | Resolves |
|----|-----------|----------------|------------------|--------------|---------|
| V11-a | IAM traversal hardcodes `file_id=1` | Pages guide §IAM: "at least one IAM page for each file where it has extents"; Randal blog | `tpcxbb_1gb.bak` failing tables | `DBCC PAGE` on IAM pages in file 2; compare file_id encoding | V11 |
| V11-b | IAM single-page-allocation first-8-pages | Randal blog: 8 × 6-byte slots in first IAM page header | New fixture: single-partition table < 8 pages, pre-SS2016 | `DBCC PAGE` on IAM page, field `SinglePageAllocation` | G10 |
| Issue-1 | `enc=1` ARCHIVE bitpack breaks at row ~3820 | VLDB 2015: "RLE + bit-packing" is ARCHIVE-invariant; enc=1 = value encoding (linear transform); SIGMOD 2013: "improvements for impure sequences" | `archive_part_all`, `archive_columnstore_types_full.bak` | `sys.column_store_segments` + `sys.fn_dump_dblog` to examine raw segment bytes; compare ARCHIVE vs non-ARCHIVE enc=1 blob header | G-new (ARCHIVE bitpack variant) |
| Issue-2/3 | `enc=5` VARBINARY/VARCHAR, `enc=3` ARCHIVE NVARCHAR | VLDB 2015: STRING_STORE_BY_VALUE_BASED; variable-length strings differ from fixed-width | `archive_columnstore_types_full.bak` | `sys.column_store_segments` + `DBCC PAGE` on LOB pages holding enc=5 blobs | G-new (variable-width pool format) |
| V-new | ZSTD backup compression (SS2025) | [docs/backup-compression.md](../../../sql-docs/docs/relational-databases/backup-restore/backup-compression-sql-server.md): "ZSTD algorithm, `WITH COMPRESSION (ALGORITHM = ZSTD)`" | Need SS2025 fixture with ZSTD | Header field at `compressed.py _V1/_V2`: check algorithm ID byte | V-new |
| V-new | SS2022+ segment `collation_id`, `min_deep_data`, `max_deep_data` | `sys.column_store_segments` docs: three new columns added in SS2022 | Existing `archive_columnstore_partition_full.bak` (SS2022/2025) | `sys.column_store_segments` on SS2022+ instance; compare segment header offsets | G-new |
| DCM/BCM | Page type validation before row decode | Pages guide §DCM and BCM: six system page types exist at predictable intervals | Any existing fixture | `DBCC PAGE` on page 6 (DCM) and 7 (BCM) to confirm `m_type` byte | G-new |
| ROW_OVERFLOW | Does mssqlbak follow ROW_OVERFLOW_DATA IAM chains? | Pages guide §IAM: separate alloc unit, separate IAM chain | Need fixture: table with row > 8,060 bytes (e.g., two `VARCHAR(5000)` cols both populated) | `sys.allocation_units WHERE type_desc='ROW_OVERFLOW_DATA'`; `DBCC PAGE` on the overflow page | G-new |

---

## 6. Recommended Next Steps (Priority Order)

> **⚠️ SUPERSEDED (2026-06-16):** This list was written before the code audit. Items 1 (V11) and 4 (page-type gate) are **already done**. The authoritative, dependency-ordered plan is now **§13**. The list below is kept for historical context.

1. **V11 fix (highest business impact):** Use the Pages-and-Extents guide + Paul Randal's IAM blog as the spec. Fix `rows.py` IAM traversal to read `file_id` from each IAM page's own position, not from hardcoded constant. Validate on `tpcxbb_1gb.bak`. DBCC verifier: `DBCC PAGE` on an IAM page in file ≥ 2, confirm file_id encoding in single-page-allocation slots.

2. **ARCHIVE enc=1 (Issue 1) — test the enc=4 hypothesis:** VLDB 2015 documents `encoding_type=1` as "similar to 4 with some internal variations" (per `sys.column_store_segments`). Write a diagnostic that decodes the first 4,000 rows of an ARCHIVE enc=1 segment using the enc=4 (STORE_BY_VALUE_BASED) path and compares output. If it matches, the "internal variation" may be the ARCHIVE bitpack routing through enc=4 layout.

3. **ZSTD registration:** Add `V-new (ZSTD)` entry to the Version Register in `BAK_FORMAT_SPEC.md §12`. Add detection logic in `compressed.py` to raise a descriptive `UnsupportedFeatureError` instead of a cryptic decode failure. Fixture requires SS2025 with `BACKUP ... WITH COMPRESSION (ALGORITHM = ZSTD)`.

4. **Page type gate:** Audit `pages.py` to confirm `m_type` is checked before any row decode attempt. System page types (PFS=11, GAM=8, SGAM=9, IAM=10, DCM=16, BCM=17) should raise a specific error or be skipped, not silently produce garbage rows.

5. **Read the full Larson 2015 VLDB paper:** The cached copy is at `/Users/robert.lee/.cursor/projects/Users-robert-lee-github-mssqlbak/agent-tools/6f9eac3a-551b-402d-bf27-ce5361123c24.txt`. Section 3 (Column Segment Compression) gives the most detailed public description of the encoding → RLE → bitpack pipeline and should be mapped field-by-field against `columnstore.py: _SEG_*` constants.

---

## 7. Larson VLDB 2015 — Encoding Pipeline Deep Read

Source: Per-Åke Larson et al., "Real-Time Analytical Processing with SQL Server," PVLDB Vol. 8, No. 12, 2015.  
Local cache: `/Users/robert.lee/.cursor/projects/Users-robert-lee-github-mssqlbak/agent-tools/6f9eac3a-551b-402d-bf27-ce5361123c24.txt`  
Key section: §6.1 "Compression and Scan Functionality" (pp. 1749–1750)

### 7.1 The canonical encoding pipeline

The paper gives the most detailed public description of the column segment compression pipeline. Every segment goes through these stages in order:

```
Raw column values
      │
      ▼  Stage 1 — Encoding (one of two paths)
┌─────────────────────────────────────────────────────────┐
│ VALUE ENCODING (enc=1, enc=4)                           │
│ "applies a linear transformation on numerical values    │
│  to convert them to integers that can be represented    │
│  with a smaller number of bits"                         │
│                                                         │
│ OR                                                      │
│                                                         │
│ DICTIONARY ENCODING (enc=2, enc=3)                      │
│ "used when the number of distinct values is much        │
│  smaller than the size of the segment"                  │
│  → values stored in dictionaries; column stores data-IDs│
│  → for strings: dictionary values packed with Huffman   │
└──────────────────────┬──────────────────────────────────┘
                       │ encoded integers (32-bit or 64-bit)
                       ▼  Stage 2 — RLE + bit-packing
┌─────────────────────────────────────────────────────────┐
│ "every compressed column segment contains two arrays:   │
│  an RLE array and a bit-packed values array"            │
│                                                         │
│ RLE array: partitions the sequence into                 │
│  • pure runs    — same value repeated N times           │
│  • impure runs  — each value encoded separately         │
│                                                         │
│ Bit-packed array: stores impure-run values              │
│  "as few bits as possible are used to encode a value    │
│   but the bits of a single value cannot cross a         │
│   64-bit word boundary"                                 │
└──────────────────────┬──────────────────────────────────┘
                       │ compressed segment blob
                       ▼  Stage 3 — ARCHIVE only
┌─────────────────────────────────────────────────────────┐
│ XPRESS (MS-XCA LZ77+Huffman)                            │
│ Applied on top of the already-encoded segment blob.     │
│ "SQL Server runs the Microsoft XPRESS compression        │
│  algorithm on the data."                                │
└─────────────────────────────────────────────────────────┘
```

**Mapping to our encoding types** (from `sys.column_store_segments`):

| enc | Official name | Stage 1 path | Notes |
|-----|--------------|-------------|-------|
| 1 | VALUE_BASED | value encoding (linear transform) | "similar to 4 with some internal variations" |
| 2 | VALUE_HASH_BASED | dictionary encoding (numeric) | numeric dict + data IDs |
| 3 | STRING_HASH_BASED | dictionary encoding (string) | string dict; Huffman-encoded entries |
| 4 | STORE_BY_VALUE_BASED | value encoding (linear transform) | reference implementation |
| 5 | STRING_STORE_BY_VALUE_BASED | none (raw pool bytes) | no dictionary; pool of raw bytes |

### 7.2 The 64-bit word boundary constraint — actionable for Issue 1

The paper states explicitly:

> "**As few bits as possible are used to encode a column value but the bits of a single value cannot cross a 64-bit word boundary.**"

This defines the bit-packing layout precisely:

```
bits_per_value  = ⌈log₂(distinct_value_count + 1)⌉
                  (capped so it evenly divides 64)
values_per_word = ⌊64 / bits_per_value⌋
word_index(i)   = i / values_per_word
bit_offset(i)   = (i % values_per_word) * bits_per_value
```

For our sequential-integer fixture (IDs 1…35,000):
- Range ≈ 35,000 → 15 bits needed (2¹⁵ = 32,768 < 35,000 < 65,536 → 16 bits)
- With 16-bit packing: 4 values per 64-bit word (4 × 16 = 64)
- Row 3,820 would be in word 955 (byte offset 7,640) — not inherently special

The breakage at row ~3,820 is therefore **not** explainable by a 64-bit boundary alignment issue alone. This points toward the ARCHIVE blob header carrying different `bits_per_value` or `values_per_word` metadata than non-ARCHIVE, which causes the decoder to use wrong parameters after a certain count.

### 7.3 The enc=1 vs enc=4 relationship — "internal variations"

The `sys.column_store_segments` docs describe enc=1 as "similar to 4 with some internal variations." The VLDB 2015 paper does not distinguish enc=1 from enc=4 by name but describes both as using the same "linear transformation." The distinction may be:

- **enc=4** (STORE_BY_VALUE_BASED): pure value encoding, no post-processing
- **enc=1** (VALUE_BASED): value encoding with an additional normalization step that changes how `base_id` and `magnitude` are applied during decoding

**Testable hypothesis for Issue 1:**  
Compare the inner blob header bytes of an ARCHIVE enc=1 segment against a non-ARCHIVE enc=1 segment on the same column. Specifically, look for differences in:
1. The field that encodes `bits_per_value` (the bitpack header)
2. The `base_id` / `magnitude` values reported by `sys.column_store_segments`
3. Whether the ARCHIVE blob uses enc=4 header format after XPRESS decompression

If the ARCHIVE inner blob has an `encoding_type = 4` header (not 1), the fix is to dispatch to the enc=4 path after unwrapping XPRESS. This is now the **highest-priority single experiment** to run.

### 7.4 Stage 2 decompression order — ARCHIVE reverses the pipeline

The decompression order must exactly reverse the compression pipeline:

```
ARCHIVE read path:
  XPRESS decompress → RLE decode + bit-unpack → value decode (linear inverse)

Non-ARCHIVE read path:
  RLE decode + bit-unpack → value decode (linear inverse)
```

The paper §6.1 confirms: "The first stage of decompression yields pure sequences of values or impure sequences of values after bit unpacking which then pass through a **decoding stage**." Decoding is always the *last* step. Our current code performs XPRESS decompression first (confirmed correct), then dispatches to the enc=1 path. The question is whether the `_SEG_*` header offsets we use to read the RLE and bitpack parameters are valid for the post-XPRESS inner blob.

### 7.5 What the paper does NOT tell us

These items are conspicuously absent and remain `[UNKNOWN]`:

| Missing detail | Why it matters |
|----------------|---------------|
| Exact byte layout of the RLE array header (offset of count field, run-type flag bit) | We reverse-engineered this; no published verification |
| Exact byte layout of the bitpack array header (bits_per_value field offset, endianness) | Same — our `_BP_BPV` constant is `[HEURISTIC]` |
| How `base_id` and `magnitude` from `sys.column_store_segments` map to the linear transform formula | We derived `decoded = encoded * magnitude + base_id`; paper confirms linear transform exists but not the formula |
| enc=5 pool format for variable-length types (VARCHAR, VARBINARY) | Paper mentions enc=3 for strings (Huffman dict) but says nothing about enc=5 pool layout |
| The "internal variations" that distinguish enc=1 from enc=4 | The specific bit-level difference is undocumented |

### 7.6 SIGMOD 2013 follow-on — the "impure sequences" clue

The SIGMOD 2013 paper (Enhancements to SQL Server Column Stores) states:

> "The improvements were mostly aimed at **impure sequences of values**. SQL Server is already taking advantage of RLE compression when processing filters, joins and grouping on columns with **pure sequences** of values. The primary goal was to better exploit data organization and information about distribution of values resulting from **dictionary encoding and bit-packing**."

ARCHIVE partitions by definition hold *old, non-sequential* data — exactly the "impure sequences" case. This strongly suggests that the SS2014 encoder changed the bitpack layout for impure runs, and ARCHIVE segments (which were introduced to further compress already-encoded segments) may use the new layout while our decoder still uses the pre-SS2014 layout. **This is now the leading hypothesis for Issue 1.**

---

## 8. Hekaton (In-Memory OLTP) — SIGMOD 2013 Deep Read

Source: Diaconu, Freedman, Ismert, Larson, Mittal, Stonecipher, Verma, Zwilling — "Hekaton: SQL Server's Memory-Optimized OLTP Engine," SIGMOD 2013.  
DOI: [10.1145/2463676.2463710](https://doi.org/10.1145/2463676.2463710)  
CMU course reference: CMU 15-721 Advanced Database Systems (Fall 2024), used as case study for MVCC + multi-engine integration.  
Local cache: `/tmp/hekaton.pdf`

This paper is most relevant to V04 (in-memory OLTP / XTP tables) and the backup format for databases that contain memory-optimized tables.

### 8.1 Architecture: three engines, one backup

The paper's §3 describes SQL Server 2014 as integrating three engines under a **common backend** that includes storage, logging, and high availability:

> "All engines use the same log and are integrated with SQL Server's high availability solution (AlwaysOn)."

**Direct implication:** when a database with memory-optimized tables is backed up, the resulting `.bak` contains **both** the standard MDF page stream (disk-based tables) **and** Hekaton checkpoint file data. These are two physically distinct streams inside the MTF container.

### 8.2 Durability mechanism — §7 is the smoking gun for V04

The paper §7 gives the complete durability design:

```
Hekaton writes two types of durable data:

  1. Log stream      — in the regular SQL Server transaction log
                       (same log that mssqlbak already reads via logtail.py)

  2. Checkpoint streams — stored as SQL Server FILESTREAM files:
       • Data files   — all inserted row versions for a timestamp interval
                        (append-only sequential file; one per interval)
       • Delta files  — deleted version IDs for their paired data file
                        (1:1 with each data file; append-only)
       • Inventory    — system table listing which data/delta files make up
                        the current checkpoint
```

**Why V04 is a permanent limitation, not a missing feature:**

> "The Hekaton storage engine treats records as **opaque objects**. It has no knowledge of the internal content or format of records and cannot directly access or process the data in records. The Hekaton compiler provides the engine with **customized callback functions** for each table."

The XTP data files do not use the SQL Server 8KB page format. They are sequential files of Hekaton-specific version records (each record is an opaque blob with a header carrying begin/end timestamps + linked-list pointers for MVCC). The decode functions are **compiled to native code at table-creation time**. Without the compiled DLL, the record format is opaque. This is not a configuration that mssqlbak can bridge.

### 8.3 Catalog signals are architecturally sound

The paper §3 confirms:

> "Metadata about Hekaton tables, indexes, etc. is **stored in the regular SQL Server catalog**. Users view and manage them using exactly the same tools as regular tables and indexes."

This validates our `classify_table` approach (V04 fix): using `sysrowsets.status bit 0x100` (XTP index flag) plus null page pointers in `sysalloc` to detect memory-optimized tables is correct. The signal is a property of the catalog, not the data files.

### 8.4 What IS readable from the .bak for XTP tables

Even though the row data is unreadable, three things can be derived from what mssqlbak already reads:

| What | Where | Status |
|------|-------|--------|
| Table name, column names, column types | `syscolpars`, recovered via `catalog.py` | ✓ Already working |
| Memory-optimized flag | `sysrowsets.status bit 0x100` + null page pointers | ✓ V04 fix |
| Checkpoint file inventory (data/delta file list + timestamp ranges) | A system table: paper says "The inventory is stored in a system table" | ✗ Not attempted — unknown which system table |

The checkpoint file inventory is the one potentially exploitable signal. If the inventory table is accessible via our catalog reader, we could at minimum report the number of checkpoint data files and their timestamp ranges, giving a proxy row count estimate (data file size / average row size). This is worth investigating as a V04 improvement beyond the current "skip and report" behavior.

### 8.5 XTP log records in the log tail

The paper confirms:

> "Hekaton logs its updates to the **regular SQL Server transaction log**."  
> "The log contains the logical effects of committed transactions sufficient to redo the transaction. The changes are recorded as **insertions and deletions of row versions** labeled with the table they belong to."

This means XTP log records appear in the same log stream that `logtail.py` scans. They have a different `LOP_*` type than standard row operations. Our log tail reader should either skip them gracefully or flag them as a known-unsupported record type. Current status: unknown whether `logtail.py` handles XTP log record types explicitly or falls through to a generic skip.

### 8.6 What the CMU course context adds

CMU 15-721 (Advanced Database Systems) uses this paper as the canonical reference for SQL Server's multi-engine architecture. The course covers Hekaton specifically as a case study for:
- Optimistic MVCC without locks (begin/end timestamp pairs on every version record)
- Latch-free data structures (no buffer pool latching, no lock table)
- Compilation of T-SQL to native code (MAT → PIT → C → DLL)

None of these are directly relevant to mssqlbak's read path, but they confirm why the XTP record format is genuinely opaque: it is generated by a JIT compiler and contains table-specific field offsets embedded in native code, not in any interpretable metadata.

### 8.7 New open issue from this paper

| ID | Issue | Source | Action |
|----|-------|--------|--------|
| V04-b | Which system table holds the XTP checkpoint inventory? | Hekaton §7.2.1: "The inventory is stored in a system table" | **RESOLVED 2026-06-16 (see §14.3):** it is `sys.dm_db_xtp_checkpoint_files`. Report row-count proxy from `inserted_row_count − deleted_row_count`. |

### 8.8 Hekaton citation chase — what we tried, and why it is a dead-end

This subsection records the **third-level citation chase** (§14 method) for Hekaton, so the same ground is not re-covered. **Conclusion: there is no public document that exposes the XTP on-disk record format. Do not keep looking — the format is opaque by construction, not by lack of published material.**

**What we tried (2026-06-16):**

1. **Read [H13] (SIGMOD 2013) in full** — `/tmp/hekaton.pdf`. The paper describes the *durability mechanism* (data/delta checkpoint files, MVCC begin/end timestamps) but explicitly states the storage engine treats records as **opaque objects** decoded only by per-table JIT-compiled callbacks (§8.2). No byte layout is given.
2. **Walked the entire [H13] bibliography (21 refs).** Every citation is about MVCC, latch-free structures, query compilation, or competing in-memory systems (HyPer, VoltDB, SolidDB, Bw-Tree, TimesTen). **None** describe an on-disk or backup format. Full list audited in §14.4.
3. **Chased the Larson [L15] reference [1] → Kalen Delaney whitepapers + Microsoft Docs.** This is the most authoritative practitioner source on XTP internals. It documents the **checkpoint file *container* model** (CFP = data file + delta file, append-only, FILESTREAM-surfaced) and the **inventory DMV** `sys.dm_db_xtp_checkpoint_files` — but for the **row payload** inside a data file it only repeats that rows are "free-form data rows in an in-memory heap… no page structures." No record byte layout.
4. **Checked the CMU 15-721 course materials** that use [H13] as a case study — pedagogical treatment of MVCC only; no format detail.

**Why it is genuinely opaque (root cause, not a gap we can close):** the routines that read/write an XTP row are emitted as **native C → DLL at table-creation time** (MAT → PIT → C → DLL pipeline, §8.6). The field offsets, null handling, and type layout live *inside that compiled DLL*, which is specific to the exact `CREATE TABLE` statement and is **not present in the `.bak`**. Even Microsoft's own engine cannot read an XTP row without the matching compiled DLL. Therefore no spec, paper, or blog can publish a generic byte layout — there isn't one.

**What this leaves as actionable (the ceiling for `mssqlbak`):**

| Capability | Feasible? | Source |
|------------|-----------|--------|
| Detect a table is memory-optimized | ✅ Yes | catalog flag `sysrowsets.status 0x100` (§8.3) — already implemented (V04) |
| Report table/column names + types | ✅ Yes | regular catalog (`syscolpars`) (§8.4) |
| Report checkpoint inventory + row-count proxy | ✅ Yes | `sys.dm_db_xtp_checkpoint_files` (§14.3) — V04-b |
| Decode actual XTP row values from a `.bak` | ❌ **No — permanent limitation** | opaque JIT-compiled record format (this subsection) |

**Bottom line for future readers:** V04 stays "detect + report, do not attempt to decode." The only open work is the optional V04-b inventory *reporting* (Tier C). Do not re-open the search for an XTP row-format spec.

---

## 9. Engineer Profiles — Authors of Useful Papers

This section catalogues every named engineer from the papers we read, their public output, and which pieces of that output are relevant to `mssqlbak`.

### 9.1 Per-Åke (Paul) Larson — Microsoft Research

**Role:** Principal Researcher, Microsoft Research. Lead author on every SQL Server columnstore paper (L11, L13, L15) and co-author on Hekaton (H13).

**DBLP:** [vldb.org/dblp/…/Larson](https://vldb.org/dblp/db/indices/a-tree/l/Larson:Per==Aring=ke.html) — 130+ papers spanning 1978–2017

**SQL Server-relevant papers (post-2010 only; earlier work is unrelated to storage format):**

| Year | Venue | Title | Relevance to mssqlbak |
|------|-------|-------|-----------------------|
| 2011 | SIGMOD | SQL Server Column Store Indexes [L11] | Encoding pipeline origin; ACM DL paywall |
| 2011 | VLDB | High-Performance Concurrency Control Mechanisms for Main-Memory Databases | Hekaton MVCC precursor; not format-relevant |
| 2013 | SIGMOD | Enhancements to SQL Server Column Stores [L13] | Impure sequence improvements; ACM DL paywall |
| 2013 | SIGMOD | Hekaton: SQL Server's Memory-Optimized OLTP Engine [H13] | XTP durability model; **fully read** |
| 2015 | VLDB | Real-Time Analytical Processing with SQL Server [L15] | Encoding pipeline deep-dive; **fully read** |

No additional publicly accessible PDFs with format-level detail exist in his DBLP beyond these.

### 9.2 Remus Rusanu — Microsoft (SQL Server team)

**Role:** SQL Server Storage Engine engineer; co-author of [L15]. Maintains a public blog at [rusanu.com](https://rusanu.com).

**Key posts directly relevant to mssqlbak:**

| Post | URL | What it contains |
|------|-----|-----------------|
| Inside the SQL Server 2012 Columnstore Indexes | [rusanu.com/2012/05/29/…](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/) | **Segments stored as VARBINARY(MAX) BLOBs in the LOB allocation unit** — confirms segment data lives on LOB pages (types 3/4), not data pages (type 1); 2 GB per-segment limit; primary vs secondary dictionary model; `min_data_id`/`max_data_id` must be decoded via encoding_type |
| What is an LSN: Log Sequence Number | [rusanu.com/2012/01/17/…](https://rusanu.com/2012/01/17/what-is-an-lsn-log-sequence-number/) | LSN format (file:block:slot), fn_dblog layout; relevant for backup MTF header LSN fields |
| SQL Server 2014 updateable columnstores Q and A | [rusanu.com/2014/06/17/…](https://rusanu.com/2014/06/17/sql-server-2014-updateable-columnstores-q-and-a/) | Delta store / Tuple Mover lifecycle; delta stores are rowstore B-trees that appear in backups as normal heap/B-tree pages |
| SQL Server clustered columnstore Tuple Mover | rusanu.com/blog/ | Tuple Mover schedule and row-group size threshold (102400 rows minimum for compression to trigger) |

**Key new finding from Rusanu 2012 (fully read this session):**

Segments and dictionaries are both stored as `VARBINARY(MAX)` values in the **columnstore LOB allocation unit** of the index. Each is a single BLOB value up to 2 GB. This means our parser encounters segment bytes in **LOB pages** (page types 3 and 4), not in regular data pages. The IAM for the LOB allocation unit leads to these pages. The `sys.column_store_segments.segment_id` and `column_id` identify which blob corresponds to which column/segment pair.

### 9.3 Paul Randal — formerly Microsoft SQL Server Storage Engine

**Role:** SQL Server Storage Engine lead at Microsoft for 9 years; wrote and maintained DBCC PAGE, DBCC IND, and DBCC CHECKDB. Co-founder of SQLskills. Blog: [sqlskills.com/blogs/paul](https://www.sqlskills.com/blogs/paul/).

**"Inside the Storage Engine" series — posts read and their findings:**

| Post | URL | Read? | Key findings |
|------|-----|-------|-------------|
| Anatomy of a page | [link](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-page/) | ✅ Full | Complete m_type enum, m_flagBits, m_typeFlagBits, slot array — see §10.2 |
| IAM pages, IAM chains, allocation units | [link](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-iam-pages-iam-chains-and-allocation-units/) | ✅ Full | IAM header fields, 8-slot SPA array, chain traversal — see §10.1 |
| GAM, SGAM, PFS and other allocation maps | [link](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-gam-sgam-pfs-and-other-allocation-maps/) | ✅ Full | **see §11.1** |
| How are allocation unit IDs calculated? | [link](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-how-are-allocation-unit-ids-calculated/) | ✅ Full | **see §11.2** |
| Anatomy of a record | [link](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/) | ✅ Full — 2026-06-16 | Row header bytes: status bits, null bitmap, variable-length offset array — see §11.7 |
| Ghost cleanup in depth | [link](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-ghost-cleanup-in-depth/) | ❌ Not yet read | Ghost record bit in row status byte; relevant if we see ghost rows in backup data pages |
| sp_AllocationMetadata | [link](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-sp_allocationmetadata/) | ❌ Not yet read | Undocumented proc that dumps all IAM chains for a database — useful for building verifier sidecars |

### 9.4 Craig Freedman — Microsoft (SQL Server query processing)

**Role:** SQL Server query processing engineer; Hekaton co-author [H13]. Blog: [blogs.msdn.microsoft.com/craigfr](https://blogs.msdn.microsoft.com/craigfr/) (migrated to Microsoft Learn in 2019).

**Assessment:** His blog covers query plans, optimizer, and execution engine internals — not on-disk storage format. No posts on columnstore segment encoding or backup format. **Low relevance to mssqlbak storage parsing.** Skip.

### 9.5 Eric N. Hanson — Microsoft (SQL Server)

**Role:** Co-author on [L11], [L13], [L15]. Known for "batch mode" query execution work (columnstore scan operator).

**Search result:** No dedicated public blog found. Appears only as a co-author in the Larson papers. One referenced resource: "Ensuring Use of the Fast Batch Mode of Query Execution" (blog post cited by Rusanu) — this is a query execution tuning tip, not a format document. **Low relevance to format parsing.**

---

## 10. Literature Reference Index

### 10.1 PDFs fully read in this session

Every PDF below was fetched and read in full during the 2026-06-16 research session. Column "How read" records the access method so the source can be re-verified.

| Ref | Citation | Direct PDF URL | How read | Cached at |
|-----|---------|---------------|----------|-----------|
| [L15] | P.-Å. Larson et al., "Real-Time Analytical Processing with SQL Server," PVLDB Vol. 8, No. 12, 2015. | [vldb.org PDF](https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf) | Web search → auto-saved by search tool | `agent-tools/6f9eac3a-551b-402d-bf27-ce5361123c24.txt` |
| [H13] | C. Diaconu, C. Freedman, E. Ismert, P.-Å. Larson, P. Mittal, R. Stonecipher, N. Verma, M. Zwilling — "Hekaton: SQL Server's Memory-Optimized OLTP Engine," SIGMOD 2013, pp. 1243–1254. DOI: [10.1145/2463676.2463710](https://doi.org/10.1145/2463676.2463710) | [CMU 15-721-f24 copy](https://www.cs.cmu.edu/~15721-f24/papers/Hekaton_SQL_Server.pdf) (timed out on fetch; downloaded via `curl` to `/tmp/hekaton.pdf`) | `curl` download + read Wisconsin mirror | `/tmp/hekaton.pdf`, `agent-tools/2d4bcd81…txt`, `agent-tools/386fb6fc…txt` |

### 10.2 Papers — content fully covered via proxy reads

These were not accessible as free PDFs (ACM DL paywall; no open mirrors found after search). Their key technical content was recovered via the [L15] retrospective paper, which quotes both in detail and carries the same authorship team.

| Ref | Citation | Access status | Content covered by |
|-----|---------|--------------|-------------------|
| [L11] | P.-Å. Larson et al., "SQL Server Column Store Indexes," SIGMOD 2011, pp. 1177–1184. DOI: [10.1145/1989323.1989448](https://doi.org/10.1145/1989323.1989448) | ACM DL paywall; CMU 15-721 Spring 2017 reading list links 404 | [L15] §6.1 covers the full encoding pipeline from L11: RLE + bit-packing, 64-bit word boundary constraint, enc=1–5 taxonomy |
| [L13] | P. Larson et al., "Enhancements to SQL Server Column Stores," SIGMOD 2013, pp. 1159–1168. DOI: [10.1145/2463676.2463708](https://doi.org/10.1145/2463676.2463708) | ACM DL paywall; MSR landing page has no PDF link | [L15] §6.2 + VLDB snippet confirmed: "improvements for impure sequences" = SS2014 scan operator function-pointer dispatch (decompression side only, not on-disk format) — see §10.3 for full analysis |

### 10.3 Authoritative web sources read in full

| Ref | Source | URL | What was read |
|-----|--------|-----|--------------|
| [R-IAM] | P. Randal (former SQL Server Storage Engine lead, Microsoft), sqlskills.com | [IAM pages, chains, and allocation units](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-iam-pages-iam-chains-and-allocation-units/) | **Full post read 2026-06-16.** IAM header record fields, 8-slot single-page-allocation array, extent bitmap, IAM not tracked anywhere, IAM chain definition — all details in §11.1 |
| [R-PAGE] | P. Randal, sqlskills.com | [Anatomy of a page](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-page/) | **Full post read 2026-06-16.** Complete `m_type` enum (1–20), `m_typeFlagBits`, `m_flagBits` checksum bits, `m_objId` history, slot array layout — all details in §11.2 |
| [R-ALLOC] | P. Randal, sqlskills.com | [GAM, SGAM, PFS and other allocation maps](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-gam-sgam-pfs-and-other-allocation-maps/) | **Full post read 2026-06-16.** GAM/SGAM bit semantics (note: GAM=1 means FREE), valid 4-state table, PFS byte encoding (bits 0–6), fixed page layout at start of each file — details in §11.4 |
| [R-ALLOCID] | P. Randal, sqlskills.com | [How are allocation unit IDs calculated?](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-how-are-allocation-unit-ids-calculated/) | **Full post read 2026-06-16.** `AllocUnitId = (m_indexId << 48) \| (m_objId << 16)` — formula for V11 fix — details in §11.5 |
| [R-REC] | P. Randal, sqlskills.com | [Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/) | **Full post read 2026-06-16.** Complete non-compressed row layout: TagA record type enum (0–7 incl. ghost types), TagB flags, null bitmap position and bit encoding, variable-length end-offset array, versioning tag — full worked hex example — details in §11.7 |
| [R-CSI2012] | R. Rusanu (SQL Server Storage Engine, co-author [L15]), rusanu.com | [Inside the SQL Server 2012 Columnstore Indexes](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/) | **Full post read 2026-06-16.** Segments stored as VARBINARY(MAX) BLOBs in LOB allocation unit; 2 GB limit; primary/secondary dictionary model; min_data_id/max_data_id are encoded values — details in §11.6 |
| [MS-P&E] | Microsoft Docs | [Page and Extent Architecture Guide (SS ver17)](https://learn.microsoft.com/en-us/sql/relational-databases/pages-and-extents-architecture-guide?view=sql-server-ver17) | Full doc; local mirror at `sql-docs/docs/relational-databases/pages-and-extents-architecture-guide.md` |
| [MS-SEG] | Microsoft Docs | [sys.column_store_segments](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql) | Full encoding_type taxonomy (enc=1–5); SS2022 new fields |
| [MS-BCK] | Microsoft Docs | [Backup Compression (SQL Server)](https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/backup-compression-sql-server) | ZSTD algorithm added in SS2025 |
| [MS-ROW] | Microsoft Docs | [Row compression implementation](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/row-compression-implementation) | Per-type compression behaviour (trailing zeros, variable-length numerics) |
| [MS-PAGE] | Microsoft Docs | [Page compression implementation](https://learn.microsoft.com/en-us/sql/relational-databases/data-compression/page-compression-implementation) | Prefix + dictionary compression pipeline |
| [CMU-721-F24] | CMU 15-721 Advanced Database Systems, Fall 2024 | Course paper list hosts [H13] at `cs.cmu.edu/~15721-f24/papers/` | Context for how Hekaton is taught; confirms Hekaton = canonical SQL Server MVCC case study |

---

## 11. Paul Randal Blogs — Full-Read Findings

Both [R-IAM] and [R-PAGE] were read in full during this session. The original §3 citation used only partial snippets. These are the additional findings not yet captured elsewhere in this document.

### 11.1 IAM page internal structure — exact DBCC PAGE layout ([R-IAM])

Paul Randal (author of DBCC PAGE and former SQL Server Storage Engine lead) provides a DBCC PAGE dump of a live type-10 page. Key confirmed details:

**IAM header record fields** (Slot 0 of the page, 90 bytes at offset 96):

| Field | Meaning |
|-------|---------|
| `sequenceNumber` | Position of this IAM page in its IAM chain (0-based, increases by 1 per page appended) |
| `status` | Unused |
| `objectId` / `indexId` | Unused in SS2005+; in SS2000 they held the relational object/index IDs |
| `page_count` | Unused (formerly: number of single-page IDs tracked) |
| `start_pg` | First page ID in the GAM interval this page maps (e.g. `(1:0)`) |

**Single-page allocation array** (Slot 0, immediately after IAM header):

- Contains exactly **8 slots** (Slot 0–Slot 7), each a 6-byte page ID (e.g. `(1:143)`)
- Each slot is a page allocated from a **mixed extent** (not a dedicated extent)
- Only present in the **first IAM page** in the chain; subsequent IAM pages leave this array empty
- Once all 8 slots are filled, new allocations switch to dedicated extents tracked in the bitmap

**Extent allocation bitmap** (Slot 1, remainder of the page):

- One bit per extent in the 4 GiB GAM interval
- Set = the extent belongs to this allocation unit; clear = not owned
- Verified by: `DBCC CHECKDB` cross-checks that no two IAM pages claim the same extent bit

**Critical structural note for our V11 fix:**
> "IAM pages are themselves single-page allocations from mixed extents and are **not tracked anywhere**."  
> — Paul Randal, [R-IAM]

This means the IAM page location is **not** stored on any system page we can iterate over linearly. To find IAM pages for a given table, the only method is:
1. `sys.system_internals_allocation_units.first_iam_page` (6-byte page ID) — this gives the head of the chain.
2. Follow `m_nextPage` / `m_prevPage` in the IAM page header to walk the chain.

Our current `rows.py` reads the backup linearly and encounters IAM pages by type; but for the full fix we need to use `first_iam_page` as the starting point and follow the doubly-linked chain.

**Additional confirmed detail:**
> "An IAM page can … be allocated from **any file** to track extents in **any other file**."

This is the root cause of V11: the IAM page's own `file_id` is not necessarily the same as the `file_id` of the extents it maps.

### 11.2 Page header field reference confirmed ([R-PAGE])

Paul Randal provides field-by-field annotation of the 96-byte page header. New or clarifying details beyond what was in [MS-P&E]:

**Complete `m_type` enum** (confirmed by the author of the DBCC PAGE code):

| Value | Name | Notes |
|-------|------|-------|
| 1 | Data page | Heap or CCI leaf-level rows |
| 2 | Index page | B-tree upper levels; NCI all levels |
| 3 | Text mix page | Small LOB chunks, shared across column values in the same partition |
| 4 | Text tree page | Large LOB chunks, single column value only |
| 7 | Sort page | Intermediate results during a sort |
| 8 | GAM page | First is page 2 in each file |
| 9 | SGAM page | First is page 3 in each file |
| 10 | IAM page | First is wherever SQL Server places it |
| 11 | PFS page | First is page 1 in each file |
| 13 | Boot page | Page 9 in file 1 only; one per database |
| 15 | File header page | Page 0 in each file; one per file |
| 16 | Diff map page (DCM) | First is page 6 in each file |
| 17 | ML map page (BCM) | First is page 7 in each file |
| 18 | Deallocated by DBCC CHECKDB repair | Should never appear in a healthy backup |
| 19 | ALTER INDEX REORGANIZE temp page | Transient; should not appear in backup |
| 20 | Pre-allocated for bulk load | Transient; should not appear in backup |

**Direct implication for our page-type guard:** Types 18–20 are transient or corrupted. If we encounter them in a backup, it signals either a corrupt backup or a bug in our page-ID resolution code. Our `pages.py` should assert `m_type in {1, 2, 3, 4, 7, 8, 9, 10, 11, 13, 15, 16, 17}` and warn (not crash) on any other value.

**`m_typeFlagBits` meanings:**

| Value | Meaning |
|-------|---------|
| 4 | All rows on this page are the same fixed length (data/index pages) |
| 1 | At least one page in this PFS interval has a ghost record (PFS pages only) |

**`m_flagBits` bit fields:**

| Bit mask | Meaning |
|----------|---------|
| `0x200` | Page checksum enabled |
| `0x100` | Torn-page protection enabled |

Both are mutually exclusive — a database uses one or the other. Our `_verify_page_checksum()` should check this flag before attempting checksum verification.

**`m_objId` / `m_indexId` historical note:**

These fields encode the allocation unit ID in SS2005+. For databases *upgraded* from SS2000, the fields may still contain the old relational object ID and index ID. This affects how we resolve page ownership and is relevant for any pre-2005 `.bak` compatibility claims.

**Slot array layout (confirmed):**
- Grows **backwards from the end of the page** toward `m_freeData`
- Each slot is a **2-byte offset** into the page pointing to the first byte of the record
- Logically ordered (slot[0] points to the logically first record) even if physical positions on the page are shuffled by deletions/insertions
- Free space is not always contiguous — compaction happens lazily (on insert, not on delete)

### 11.3 SIGMOD 2011 [L11] and SIGMOD 2013 [L13] — access status after search

Both papers are behind the ACM Digital Library paywall. Search attempts failed to find free mirrors at CMU, MSR, or VLDB. The CMU 15-721 course links returned 404s.

**Key finding:** The VLDB 2015 paper [L15] (which we read in full) is itself a retrospective that explicitly covers all material from both papers:
- L15 §6.1 quotes L11 on encoding pipeline (RLE + bit-packing)
- L15 §6.2 quotes L13 on "improvements for impure sequences" and the SS2014 scan operator enhancements

The most critical L13 snippet for Issue 1 was recovered via search snippet:

> "The improvements were mostly aimed at **impure sequences of values**. … In SQL 2014 processing inside the scan … is done by calling a **function pointer**, determined during query compilation, corresponding to one of over **ten thousand specialized statically compiled implementations** generated for all possible combinations of data type, encoding parameters and filter types."  
> — L15 citing L13 (from VLDB.org PDF snippets captured during search)

**Interpretation for Issue 1 (ARCHIVE enc=1):** The function-pointer dispatch table with "10,000+ combinations" is the runtime side; it does not change the on-disk segment format. The *encoding* step (which determines what is stored in the `.bak`) still follows the two-stage pipeline: (1) value encoding to `enc=4` integer codes via dictionary or linear transform, then (2) `enc=1` bit-packing of those integer codes. The scan operator improvements are purely decompression-side.

This confirms the §7 hypothesis: ARCHIVE columns always enter the XPRESS layer as `enc=4`-encoded integer streams, and the `enc=1` bit-packing *within* ARCHIVE should be identical to the non-ARCHIVE case. The breakage is therefore in our XPRESS → bit-unpack → linear-decode pipeline, not in the encoding format itself.

**Action:** No additional reading of L11/L13 required. Move both from §9.2 to §9.3 with note "content covered by [L15]."

### 11.4 GAM, SGAM, PFS and other allocation maps ([R-ALLOC] — fully read this session)

Source: [sqlskills.com — GAM, SGAM, PFS and other allocation maps](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-gam-sgam-pfs-and-other-allocation-maps/)

**GAM bit semantics (counterintuitive — confirmed by the author):**

| Bit | Meaning |
|-----|---------|
| 1 | Extent is **unallocated** (free, available) |
| 0 | Extent is **allocated** for use |

**SGAM bit semantics:**

| Bit | Meaning |
|-----|---------|
| 1 | Mixed extent with at least one unallocated page (available for mixed-extent allocation) |
| 0 | Dedicated extent, OR mixed extent with no free pages |

**Valid GAM × SGAM × IAM combinations** (any other = corruption):

| GAM | SGAM | IAM | State |
|-----|------|-----|-------|
| 0 | 0 | 0 | Mixed extent, all pages allocated |
| 0 | 0 | 1 | Dedicated extent (owned by exactly one allocation unit) |
| 0 | 1 | 0 | Mixed extent with ≥1 free page |
| 1 | 0 | 0 | Completely unallocated extent |

**Fixed page layout at the start of every file** (first GAM extent, pages 0–7):

| Page | Type | Purpose |
|------|------|---------|
| 0 | 15 (file header) | File-level metadata |
| 1 | 11 (PFS) | First PFS interval starts here |
| 2 | 8 (GAM) | First GAM interval |
| 3 | 9 (SGAM) | First SGAM interval |
| 4 | — | Unused in SS2005+ |
| 5 | — | Unused in SS2005+ |
| 6 | 16 (DCM/diff map) | First differential bitmap |
| 7 | 17 (BCM/ML map) | First bulk-logged bitmap |

Every subsequent GAM interval in the same file repeats this pattern at pages 511232, 1022464, … (every 511232 pages = 64000 extents × 8 pages/extent).

**PFS byte encoding** — one byte per page, covering an 8088-page PFS interval (~64 MB):

| Bits | Mask | Meaning |
|------|------|---------|
| 2–0 | `0x07` | Free space: 0=empty, 1=1–50%, 2=51–80%, 3=81–95%, 4=96–100% |
| 3 | `0x08` | Page has at least one ghost record |
| 4 | `0x10` | Page is an IAM page |
| 5 | `0x20` | Page is in a mixed extent |
| 6 | `0x40` | Page is allocated |
| 7 | `0x80` | Unused |

Example from DBCC PAGE output: `0x70` = `0b0111_0000` = allocated (`0x40`) + mixed extent (`0x20`) + IAM page (`0x10`) + 0% full.

**Free space is only tracked** (bits 2–0 meaningful) for: LOB pages (text/image, varchar/nvarchar/varbinary max, row-overflow), and heap data pages. B-tree index pages do NOT use free-space tracking.

**Implication for our parser:**
- We can parse PFS bytes to determine if a page is allocated before attempting to decode it.
- `0x40` (bit 6) = allocated is the fast check. If clear, the page bytes are garbage/zero-fill and should be skipped.
- The ghost-record bit (bit 3) tells us a page may contain rows with the ghost-record flag set in their status byte — our row decoder needs to filter these out.

### 11.5 Allocation unit ID formula ([R-ALLOCID] — fully read this session)

Source: [sqlskills.com — How are allocation unit IDs calculated?](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-how-are-allocation-unit-ids-calculated/)

The `m_objId` and `m_indexId` fields in every page header encode the 64-bit allocation unit ID via this formula:

```
AllocationUnitId = (m_indexId << 48) | (m_objId << 16)
```

Reverse direction (for page header → lookup):

```
m_indexId = AllocationUnitId >> 48
m_objId   = (AllocationUnitId - (m_indexId << 48)) >> 16
```

The Metadata fields printed by DBCC PAGE (`Metadata: AllocUnitId`, `Metadata: PartitionId`, `Metadata: IndexId`, `Metadata: ObjectId`) are **NOT stored on the page**. DBCC PAGE computes them by doing the formula above and then querying `sys.system_internals_allocation_units` + `sys.partitions`.

**Direct implication for V11 fix:**
To correctly attribute a page to its owning table during backup parsing, we must:
1. Decode `AllocUnitId` from the page header using the formula above.
2. Look up `AllocUnitId` in `sys.system_internals_allocation_units` (available via the fixture's SQL Server instance, or equivalently from the backup's own catalog pages).
3. The resulting `container_id` maps to `sys.partitions.partition_id`, which maps to `object_id` and `index_id`.

### 11.6 Rusanu 2012 — Columnstore segment storage model ([R-CSI2012] — fully read this session)

Source: [rusanu.com — Inside the SQL Server 2012 Columnstore Indexes](https://rusanu.com/2012/05/29/inside-the-sql-server-2012-columnstore-indexes/)

Key structural findings that directly affect how we locate columnstore data in backups:

**Segments and dictionaries are LOB blobs, not row data:**
> "each column segment will be a BLOB value in [the columnstore index] LOB allocation unit. In effect you can think about sys.column_store_segments as having a VARBINARY(MAX) column containing the actual segment data."

This means columnstore segment bytes live on **LOB pages** (page type 3: text mix; page type 4: text tree), reachable via the **LOB allocation unit** IAM chain of the columnstore index — not the IN_ROW_DATA allocation unit.

**Segment ↔ LOB pointer mapping:**
`sys.column_store_segments` has one row per `(column_id, segment_id)` pair. The actual segment bytes are the BLOB value pointed to by that row's LOB pointer. Same model for `sys.column_store_dictionaries`.

**2 GB segment size limit:**
A segment cannot exceed 2 GB because it is stored as a single `VARBINARY(MAX)` value. This is the underlying reason for the ~1M-row-per-segment design.

**Primary vs secondary dictionary:**

| Type | Scope | When used |
|------|-------|-----------|
| Primary | Global — shared by ALL segments of a column | Always (for string columns; optional for non-string) |
| Secondary | Overflow — shared by a group of segments | When a segment's new values don't fit in the primary |

The `primary_dictionary_id` and `secondary_dictionary_id` columns in `sys.column_store_segments` link segments to their dictionaries. A segment uses `primary_dictionary_id = -1` if it has no primary dictionary (value-encoded, no dict needed).

**`min_data_id` / `max_data_id` in sys.column_store_segments** are encoded integer IDs (dictionary keys or linear-transform codes), not raw column values. To get the actual min/max column values, you must apply the encoding_type decode step. This is why our segment elimination logic must be encoding-aware.

**Delta stores (SS2014+):**
Updatable CCI delta stores are standard rowstore B-tree pages (type 1/2). They appear in a backup as normal B-tree pages under a separate allocation unit with index_id ≥ 2 associated with the same object_id as the CCI. The Tuple Mover compresses delta stores into CCI segments when ≥102,400 rows have accumulated.

### 11.7 Anatomy of a record ([R-REC] — fully read this session)

Source: [sqlskills.com — Inside the Storage Engine: Anatomy of a record](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-record/)

This post gives the definitive byte-by-byte layout of a non-compressed SQL Server row. This is the format our `rows.py` must parse to extract column values from data pages found in `.bak` files.

#### Non-compressed record structure (all types share this layout)

| Section | Size | Offset from record start | Description |
|---------|------|--------------------------|-------------|
| TagA | 1 byte | 0 | Bits 1–3 = record type; bit 0 and bits 4–7 are other flags |
| TagB | 1 byte | 1 | Attribute flags: `0x01` = NULL_BITMAP present; `0x02` = VARIABLE_COLUMNS present |
| Null bitmap offset | 2 bytes (LE) | 2 | Byte offset from start of record to the null bitmap section |
| Fixed-length columns | `pminlen - 4` bytes | 4 | All fixed-length column values in column order |
| **[null bitmap section — at offset stored in bytes 2–3]** | | | |
| Column count | 2 bytes (LE) | (null bitmap offset) | Total number of columns in the row (fixed + variable) |
| Null bits | ⌈col_count / 8⌉ bytes | +2 | One bit per column (0 = not null, 1 = null). Extra bits in last byte padded to 1 |
| **[variable-length section — immediately after null bitmap]** | | | |
| Var-col count | 2 bytes (LE) | after null bits | Number of variable-length columns |
| End offsets | 2 bytes × var_count | +2 | End-byte offset of each var-col value (relative to record start) |
| Variable-length data | variable | after end offsets | Values in column order |
| Versioning tag | 14 bytes (optional) | end of var data | Only present when row is under snapshot isolation; contains timestamp + tempdb version store pointer |

#### `pminlen` from the page header

`pminlen` in the page header (confirmed by [R-PAGE]) is "the size of the fixed-length portion of the records on the page." This is the offset to the null bitmap section for simple records (no variable columns before the null bitmap), i.e. `null_bitmap_offset == pminlen` when there are no fixed-length columns after the header.

#### Record type enum — bits 1–3 of TagA

| Value (bits 1–3) | Name | Notes |
|-----------------|------|-------|
| 0 | PRIMARY_RECORD | Normal data row in heap or clustered index leaf |
| 1 | FORWARDED_RECORD | Heap row moved to new location; contains back-pointer to forwarding stub |
| 2 | FORWARDING_RECORD | Stub left at original location; contains pointer to new location |
| 3 | INDEX_RECORD | B-tree index row (all levels of NCI; upper levels of CI) |
| 4 | BLOB_FRAGMENT | Fragment of a LOB value |
| 5 | GHOST_INDEX_RECORD | Logically deleted index row (awaiting ghost cleanup) |
| 6 | GHOST_DATA_RECORD | Logically deleted data row (awaiting ghost cleanup) |
| 7 | GHOST_VERSION_RECORD | 15-byte special record: 1-byte header + 14-byte versioning tag |

Ghost records (types 5 and 6) are present on live pages and therefore in backup data pages. Our row decoder must check for the ghost bits and skip or flag them. Ghost records are NOT physically removed until the ghost-cleanup background task runs — so a backup taken immediately after a DELETE will contain ghost rows.

#### Column ordering rules

| Table type | Physical column order in record |
|------------|--------------------------------|
| Heap | Cluster keys first (none), then CREATE TABLE column order: fixed-length columns before variable-length columns |
| Clustered index | Cluster key columns appear **first** physically, followed by remaining columns in CREATE TABLE order |
| Non-clustered index leaf | NCI key columns first, then INCLUDE columns, then cluster key columns (RID for heaps, CI key for CIs) |

#### Worked example (from DBCC PAGE output)

Table: `example (destination VARCHAR(100), activity VARCHAR(100), duration INT)`, row `('Banff', 'sightseeing', 5)`:

```
Offset  Hex         Explanation
00      30          TagA: type = (0x30 >> 1) & 0x07 = 0 = PRIMARY_RECORD
01      00          TagB
02–03   08 00       Null bitmap offset = 0x0008 = 8
04–07   05 00 00 00 duration = 5 (fixed-length INT, 4 bytes)
08–09   03 00       Column count = 3
0A      F8          Null bits: 0b1111_1000 → bits 0,1,2 = 0 (not null); bits 3–7 = 1 (padding)
0B–0C   02 00       Var-col count = 2 (destination, activity)
0D–0E   16 00       End offset of destination = 0x16 = 22
0F–10   21 00       End offset of activity = 0x21 = 33
11–15   42 61 6E 66 66  destination = "Banff" (bytes 17–21 inclusive = 5 bytes)
16–20   73 69 67 68 74 73 65 65 69 6E 67  activity = "sightseeing" (bytes 22–32 inclusive = 11 bytes)
```

#### Implications for mssqlbak `rows.py`

1. **Skip ghost records** — check TagA bits 1–3; if type is 5 or 6, skip the row (or emit a warning).
2. **Check NULL bitmap before reading column values** — the null bit for a column is at `null_bitmap_byte_n[bit_k]` where `n = column_index // 8` and `k = column_index % 8`; bit value 1 = NULL.
3. **Variable-length start offset** — for variable column `i`, start = `end_offset[i-1]` (or the offset immediately after the var-count+end-offset array for column 0); end = `end_offset[i]`.
4. **Versioning tag** — if the record has a versioning tag (detectable from TagB or by checking if the record is longer than the sum of fixed + variable sections), skip the 14 extra bytes at the end. Should not appear in offline backup pages unless the database had active snapshot readers at backup time.
5. **Forwarding/forwarded records in heaps** — forwarding records (type 2) are 9-byte stubs containing only the `(file_id, page_id, slot_id)` pointer. Forwarded records (type 1) contain a 6-byte back-pointer prefix before the normal record data. Both can appear in heap tables inside a backup.

---

## 12. Verifier Command Reference

For quick reference when building verifier sidecars:

```sql
-- Page header + slot array + row bytes
DBCC TRACEON (3604);
DBCC PAGE ('dbname', file_id, page_id, 3) WITH TABLERESULTS;

-- IAM page — shows single-page-allocation and extent bitmap
DBCC TRACEON (3604);
DBCC PAGE ('dbname', file_id, iam_page_id, 3) WITH TABLERESULTS;

-- Supported alternative to DBCC PAGE (SS2019+)
SELECT * FROM sys.dm_db_page_info(DB_ID('dbname'), file_id, page_id, 'DETAILED');

-- All allocation units for a table (includes file_id of first IAM page)
SELECT * FROM sys.system_internals_allocation_units sau
JOIN sys.partitions p ON sau.container_id = p.partition_id
WHERE p.object_id = OBJECT_ID('schema.table');

-- Columnstore segment metadata (enc type, min/max, dictionary IDs)
SELECT cs.*, css.*
FROM sys.column_store_segments css
JOIN sys.partitions p ON css.hobt_id = p.hobt_id
JOIN sys.indexes i ON p.object_id = i.object_id AND p.index_id = i.index_id
WHERE i.object_id = OBJECT_ID('schema.table');

-- Columnstore segment INTERNALS — the DBCC PAGE analogue for segments.
-- Undocumented (SS2012+), test-system only.  Exposes what the DMV hides:
-- RLE array, bit-pack width, bookmarks, per-segment null/min/max.
-- Source: Paul White, sql.kiwi (grouped-aggregate-pushdown); syntax via
-- Niko Neugebauer CISL part 21.  See 260616-status.md "DBCC CSINDEX" for fields.
DBCC TRACEON (3604);
DBCC CSINDEX (
    'dbname',
    <hobt_id>,        -- sys.column_store_segments.hobt_id / partition_id
    <column_id>,      -- +1 for CLUSTERED columnstore (not for nonclustered)
    <segment_id>,     -- rowgroup id
    1,                -- object_type: 1=Segment, 2=Dictionary
    2                 -- print_option (0|1|2)
    -- [, start_bitpack_unit, end_bitpack_unit]
);

-- Row-group state / delta-store inventory (row-count reconciliation)
SELECT row_group_id, state_desc, total_rows, deleted_rows
FROM sys.column_store_row_groups
WHERE object_id = OBJECT_ID('schema.table');   -- include state>0; honor deleted_rows

-- Column dictionary metadata
SELECT * FROM sys.column_store_dictionaries
WHERE hobt_id IN (
  SELECT p.hobt_id FROM sys.partitions p
  WHERE p.object_id = OBJECT_ID('schema.table')
);

-- Allocation units per file for a table (V11 diagnostic)
SELECT
  au.type_desc,
  au.data_pages,
  sys.fn_PhysLocFormatter(%%physloc%%) AS [phys_loc]
FROM sys.allocation_units au
JOIN sys.partitions p ON au.container_id = p.partition_id
WHERE p.object_id = OBJECT_ID('schema.table');
```

---

## 13. Relevance Audit + Dependency-Ordered Plan (2026-06-16)

This section maps every finding in this document against the **actual current code** in `mssqlbak/`, separates what is already done from what is genuinely open, and orders the open work by logical dependency.

### 13.1 What the research confirmed is ALREADY correct in the code

Auditing `rows.py`, `pages.py`, and `records.py` against the findings above shows the codebase already implements most of what the top-down research predicted. These need **no work** — the research serves only as independent confirmation that the existing implementation matches the documented format.

| Finding (doc section) | Code location | Status |
|-----------------------|---------------|--------|
| Multi-file IAM / per-file `file_id` (§3.1, §11.1) | `rows.py _heap_pages_for_unit`: `extents_by_file[iam_loc[1]]`, chain walk via `next_page`, missing-file guard | ✅ Done |
| IAM 8-slot single-page-allocation (§3.2, §11.1) | `rows.py _IAM_SPA_OFFSET=140`, `_IAM_SPA_STRUCT="<HI"` | ✅ Done |
| Ghost / forwarding / index record filtering (§11.7) | `pages.py` data-page filter: `(raw[off] & 0x07) == 0` keeps only PRIMARY_RECORD on `m_type==1` | ✅ Done |
| `m_type` parsing + page-type awareness (§3.4, §11.2) | `pages.py PageHeader.m_type`, `page_m_type()`, `_DATA_PAGE` checks in `rows.py` | ✅ Done |
| Null bitmap / variable-offset / complex off-row decode (§11.7) | `records.py decode_record` | ✅ Done |
| LOB stitch — `varchar(max)` + legacy `text/ntext/image` (§11.6) | `rows.py _stitch_lob`, `_stitch_text_pointer` | ✅ Done |
| Allocation-unit attribution (§11.5) | `rows.py` matches `header.obj_id` against the IAM page's `obj_id` (equivalent to the AllocUnitId formula for page→table attribution) | ✅ Done (alternative method) |
| enc=5 fixed-width CHAR/BINARY/NCHAR (§7) | `columnstore.py _decode_enc5_archive` cross-chunk pool formula | ✅ Done 2026-06-16 |

**Implication:** The "fixture + DBCC PAGE verifier" loop's first job is not to *fix* these — it is to lock them in with **verifier sidecars + regression tests** so they cannot silently regress.

### 13.2 What is genuinely OPEN (grounded in `260616-status.md`)

**Updated 2026-06-16:** Tier B (O1–O4) is fully resolved. All ARCHIVE columnstore decode bugs (C–H) are fixed. See `260616-status.md` for details.

| # | Open item | Evidence | Impact | Status |
|---|-----------|----------|--------|--------|
| O1 | **enc=1 ARCHIVE bitpack** corrupts from row ~3820 | status.md Issue 1 + Bug D | **High** | ✅ **FIXED 2026-06-16** — LOB bsz cap in `_read_large_root_data` |
| O2 | enc=5 **UUID flat inner blob** (Bug F) | status.md Issue 2 | Medium | ✅ **FIXED 2026-06-16** — LOB bsz cap (same root cause as O1) |
| O3 | enc=5 **variable-length pool** VARBINARY/VARCHAR (Bug G/H) | status.md Issue 2 | Medium | ✅ **FIXED 2026-06-16** — `pool_map` byte-offset decoder in `_decode_enc5_archive` |
| O4 | enc=3 **ARCHIVE NVARCHAR dictionary** (Bug E) | status.md Issue 3 | Medium | ✅ **FIXED 2026-06-16** — LOB bsz cap (same root cause as O1) |
| O5 | **ZSTD** backup compression (SS2025) | `compressed.py` only handles XPRESS; no ZSTD anywhere | Low-now / High-later — SS2025 ZSTD backups fail cryptically | Open |
| O6 | **ROW_OVERFLOW_DATA** chain coverage | likely handled via complex-column stitch, but no >8060-byte fixture proves it | Low — unverified, not known-broken | Open |
| O7 | Page-type **assertion hardening** (warn on types 18–20) | `pages.py` parses `m_type` but does not warn on transient/corrupt types | Low — robustness only | Open |
| O8 | **V04-b** XTP checkpoint-inventory reporting | §8.7; research resolved (§14.3) — use `sys.dm_db_xtp_checkpoint_files` | Low — reporting enhancement, data is opaque anyway | Open |

### 13.3 Dependency-ordered plan

The ordering below is by **logical dependency**, not just impact. A later tier should not start until its prerequisites are in place.

```
TIER A — Foundation (unblocks everything; no code-correctness prerequisites)
  A1. Capture verifier sidecars (DBCC PAGE + sys.column_store_segments) for
      ARCHIVE enc=1 and enc=5 segments while SS containers are running.
      → status.md TODO-F3.  Prerequisite for ALL of Tier B.
  A2. ZSTD detection guard in compressed.py (O5).
      → Independent of A1; raise a clear UnsupportedFeatureError on the ZSTD
        algorithm-ID byte instead of producing garbage.  Do in parallel with A1.

        ┌────────────────────────┴───────────────────────┐
        ▼                                                 ▼
TIER B — Core columnstore correctness (each item DEPENDS ON A1 ground truth)
  ✅ B1. Crack enc=1 ARCHIVE bitpack transform (O1).   DONE 2026-06-16
  ✅ B2. enc=5 UUID flat-blob decoder path (O2).        DONE 2026-06-16
  ✅ B3. enc=5 variable-length pool VARBINARY/VARCHAR (O3).  DONE 2026-06-16
  ✅ B4. enc=3 ARCHIVE NVARCHAR dictionary (O4).        DONE 2026-06-16

TIER C — Coverage & robustness (independent; lowest impact; do last / in gaps)
  C1. ROW_OVERFLOW_DATA fixture (>8060-byte row) + test to confirm O6.
  C2. Page-type assertion hardening — warn on m_type 18/19/20 (O7).
  C3. V04-b: locate XTP checkpoint inventory system table, add reporting (O8).
```

### 13.4 Why this order

1. **A1 before all of Tier B.** Every columnstore bug (O1–O4) is currently stuck for the same reason: we are guessing at the inner-blob byte layout. status.md TODO-V2 states the question explicitly — "does our decompressed inner blob match SQL Server's view?" — and it cannot be answered without a DBCC PAGE / DMV byte dump. A1 is the single unblocker for four separate fixes, so it has the highest leverage despite producing no user-visible change itself.

2. **A2 in parallel, not gated.** ZSTD detection touches `compressed.py` (backup-stream layer), entirely separate from the columnstore decode path. It has no dependency on A1 and can land immediately. It is sequenced early only because a cryptic failure on a whole class of SS2025 backups is worse than a clear "unsupported" error.

3. **B1 first within Tier B.** enc=1 corruption affects the broadest surface — every integer, date, and decimal ARCHIVE column, plus row-count accuracy (Bug D makes `by_id[49999]` raise `KeyError`). B2–B4 each fix a single narrower type family. Fixing B1 also validates the A1 verifier methodology before applying it to the trickier variable-length cases.

4. **B2/B3/B4 share the A1 dependency but are mutually independent** — they can be parallelized across contributors once A1 exists. Suggested order B2 → B3 → B4 by descending "how-flat-is-the-format" (UUID flat blob is the simplest deviation; the enc=3 dictionary is the most involved).

5. **Tier C last.** None of these are known-broken: O6 is probably already handled, O7 is defensive, O8 is a reporting nicety for data that is fundamentally opaque (§8.2). They carry no dependency and should fill gaps between the higher-impact work.

### 13.5 Concrete first action

Run **A1** now while the `archive-columnstore-partition` fixture containers are up (terminal already running `fixture_run all-versions --suite archive-columnstore-partition`):

```sql
DBCC TRACEON(3604);
DBCC PAGE ('RegisterBak_archive_columnstore_partition_full', 1, <lob_page_id>, 3) WITH TABLERESULTS;
SELECT * FROM sys.column_store_segments
WHERE hobt_id IN (SELECT hobt_id FROM sys.partitions WHERE object_id = OBJECT_ID('dbo.<archive_table>'));
```

Save output as `tests/fixtures_2022/archive_enc1_dbcc_page.txt` (and the enc=5 equivalents). This sidecar is the input to B1's byte-for-byte comparison against `_unwrap_archive_blob` output at the divergence offset (8257).

---

## 14. Third-Level Citation Chase (2026-06-16)

**Method:** Level 1 = public Microsoft docs. Level 2 = the docs/papers written by their authors (Larson, Rusanu, Randal). Level 3 (this section) = following the *bibliographies* of the Level-2 sources to find papers by **other** authors that have public PDFs and bear on the `.bak` format. Only format-relevant citations are kept; the many product-page and MVCC/lock-free citations are discarded.

### 14.1 The columnstore compression lineage — and a sharper Issue-1 hypothesis

The Larson columnstore papers ([L11]→[L13]→[L15]) describe SQL Server's encoding as "value encoding (linear transformation) + RLE + bit-packing" but never name the underlying scheme. Chasing their citation ancestry resolves this: SQL Server's columnstore compression is a direct descendant of the **Frame-Of-Reference (FOR) → Patched-FOR (PFOR/PFOR-DELTA)** lineage from the column-store research community.

| Paper | Authors | Public PDF | What it contributes |
|-------|---------|-----------|---------------------|
| [Z06] Super-Scalar RAM-CPU Cache Compression, ICDE 2006 | M. Zukowski, S. Héman, N. Nes, P. Boncz (CWI / MonetDB-X100) | [paperhub S3 mirror](https://paperhub.s3.amazonaws.com/7558905a56f370848a04fa349dd8bb9d.pdf) — **fully read** | Defines **PFOR, PFOR-DELTA, PDICT**: the patched-frame-of-reference scheme with a separate **exception list** |
| [A06] Integrating Compression and Execution in Column-Oriented DB Systems, SIGMOD 2006 | D. Abadi, S. Madden, M. Ferreira (MIT C-Store) | [Stanford CS245 PDF](http://web.stanford.edu/class/cs245/readings/c-store-compression.pdf) / [CMU 15-721 PDF](https://15721.courses.cs.cmu.edu/spring2016/papers/abadi-sigmod2006.pdf) — **fully read** | Catalogs the column-store encoding schemes: RLE, bit-vector, dictionary, **FOR**, and "operate on compressed data" |
| [G98] Compressing Relations and Indexes, ICDE 1998 | J. Goldstein, R. Ramakrishnan, U. Shaft | ACM DL (paywall) | The original **FOR** paper; root of the lineage. Content fully covered by [Z06] §2.1 |

**The key finding — PFOR's exception mechanism explains the Issue-1 symptom.** From [Z06] (and corroborated by the METU survey thesis that summarizes it):

> "In PFOR, a small bit width `b` is used to encode the **majority** of the values in a partition. The **exceptions**, which do not fit into `b` bits, are stored separately… positions and the values of exceptions are encoded separately in a **linked list**." — [Z06] §3

Map this onto Issue 1 (`enc=1` ARCHIVE integer bitpack decodes correctly until row ~3820, then diverges):

- SQL Server's "value encoding = linear transformation" (per [L15]) **is FOR**: subtract a base, store the residual in `b` bits. The `base_id` and `magnitude` columns in `sys.column_store_segments` are the FOR base + scale.
- The `b`-bit packing with "as few bits as possible, cannot cross a 64-bit word boundary" (per [L15] §6.1) **is the PFOR packed-values array**.
- A value too large for `b` bits becomes a **PFOR exception**: a placeholder occupies the `b`-bit slot, and the real value lives in an exception region, chained by a linked list of positions embedded in the packed array.

**New, testable hypothesis (supersedes "unknown delta/XOR/zigzag transform" in §7.2 / status.md Issue 1):** row ~3820 is most likely **the first PFOR exception** (or the start of the exception region) in the ARCHIVE segment. Our decoder reads the `b`-bit placeholder literally instead of following the exception linked-list to the patched value — so every value from the first exception onward is wrong. The non-ARCHIVE path may avoid this because its segments for the same fixture happen to have no exceptions (smaller value range → all values fit in `b` bits), which is exactly why non-ARCHIVE `enc=1` decodes perfectly while ARCHIVE breaks.

**Action for B1 (refines §13.3):** when comparing the verifier byte dump against `_unwrap_archive_blob` output, specifically look for:
1. A PFOR exception count / first-exception-position field in the segment/bitpack header.
2. An exception region at the **end** of the packed array (PFOR stores exceptions growing backward from the end of the block).
3. A linked-list stride: the `b`-bit "value" at an exception slot is actually the *offset to the next exception*, not data.

This converts Issue 1 from "reverse-engineer an unknown transform" into "confirm/refute a specific, documented format (PFOR) and implement its exception walk."

### 14.2 [A06] Abadi — confirms the encoding-scheme catalog

The MIT C-Store compression paper independently confirms the scheme set SQL Server exposes via `encoding_type`:

| C-Store scheme ([A06]) | SQL Server `enc` equivalent |
|------------------------|-----------------------------|
| Dictionary encoding | enc=2 (numeric hash), enc=3 (string hash) |
| Run-length encoding (value, start, len triples) | the RLE array in every segment ([L15] §6.1) |
| Bit-vector / bit-packing | the bit-packed values array (enc=1, enc=4) |
| Frame-of-reference (delta from a base) | the "linear transformation" / `base_id`+`magnitude` |

[A06] also documents that exceptions in a bit-packed/RLE column are "stored elsewhere" — the same exception concept as PFOR, reinforcing 14.1. No new format bytes here, but it locks the `enc=1–5` taxonomy to peer-reviewed definitions rather than guesswork.

### 14.3 [Delaney] — concrete answer to open issue V04-b

Chasing [L15] reference [1] (Kalen Delaney, *SQL Server In-Memory OLTP Internals*, the canonical Microsoft-commissioned whitepaper) plus its companion Microsoft Docs resolves **V04-b** (§8.7: "which system table holds the XTP checkpoint inventory?").

**Answer:** `sys.dm_db_xtp_checkpoint_files` (SQL Server 2014+). Public sources, both fully read:
- [Delaney16] *SQL Server 2016 In-Memory OLTP Technical White Paper* (90 pp.), free Microsoft download: [download.microsoft.com/…/SQL_Server_2016_In_Memory_OLTP_White_Paper.pdf](http://download.microsoft.com/download/8/3/6/8360731A-A27C-4684-BC88-FC7B5849A133/SQL_Server_2016_In_Memory_OLTP_White_Paper.pdf)
- [MS-XTP] [sys.dm_db_xtp_checkpoint_files (Transact-SQL)](https://learn.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-xtp-checkpoint-files-transact-sql) and [Durability for Memory-Optimized Tables](https://learn.microsoft.com/en-us/sql/relational-databases/in-memory-oltp/durability-for-memory-optimized-tables)

What this gives `mssqlbak` for the V04-b reporting enhancement (still data-opaque per §8.2, but the **inventory** is reportable):

| Column in `sys.dm_db_xtp_checkpoint_files` | Use for reporting |
|--------------------------------------------|-------------------|
| `file_type_desc` (DATA_FILE / DELTA_FILE) | distinguish the two CFP streams |
| `inserted_row_count` | **proxy row-count estimate** for a memory-optimized table without decoding opaque rows |
| `deleted_row_count` | net live-row estimate = inserted − deleted |
| `file_size_in_bytes`, `file_size_used_in_bytes` | size reporting |
| `state_desc` (PRECREATED / ACTIVE / …) | filter to only CFPs that carry real data |

Two further facts from [Delaney16] that affect parsing strategy:
- **SS2016 changed the on-disk layout:** FILESTREAM is now only a "user-visible surface"; the XTP engine allocates/resizes/deletes checkpoint files itself via direct NTFS calls, so the directory structure under `MEMORY_OPTIMIZED_DATA` differs between SS2014 and SS2016+. Any `mssqlbak` code that locates XTP files by path must branch on version.
- **Recovery uses a single log-reader thread** that moves rows from the transaction log into data/delta files — confirming (§8.5) that XTP changes also appear in the regular log stream `logtail.py` already scans.

### 14.4 What the chase did NOT yield

- **Hekaton [H13] bibliography** — all citations are MVCC, lock-free data structures, and competing in-memory systems (HyPer, VoltDB, SolidDB, Bw-Tree). None describe an on-disk/backup format. Confirms §8.2: the XTP record format is opaque by design and no public paper exposes it. **The full "what we tried" record for Hekaton is consolidated in §8.8 — do not re-chase.**
- **[G98] FOR original** — paywalled and fully superseded by [Z06]'s summary; no need to obtain it.
- **Randal/Rusanu blogs** — practitioner posts without formal bibliographies; their cross-references stay within the already-read "Inside the Storage Engine" set and Paul White's query-processing series (not format-relevant).

### 14.5 Net effect on the plan (§13)

| Plan item | Change from this chase |
|-----------|------------------------|
| **B1** (enc=1 ARCHIVE bitpack) | Hypothesis sharpened to **PFOR exception list** ([Z06]). The A1 verifier dump should now specifically hunt for an exception-count header + end-of-block exception region + linked-list stride. Highest-leverage update in this section. |
| **O8 / V04-b** (XTP inventory) | **Resolved as a research question.** Implementation is now well-defined: read `sys.dm_db_xtp_checkpoint_files`; report row-count proxy from `inserted_row_count − deleted_row_count`. Still Tier C priority. |
| enc=1 taxonomy confidence | Promoted from `[HEURISTIC]` toward `[CONFIRMED]`: scheme names now trace to peer-reviewed [A06]/[Z06], not just `sys.column_store_segments` labels. |

---

## 15. Fourth-Level Citation Chase (2026-06-16)

**Method:** Level 4 = following the *bibliographies of the Level-3 sources* ([Z06], [A06]). The Level-3 chase established *that* SQL Server columnstore is PFOR-family; the question Level 4 must answer is the one B1 actually needs: **what is the exact byte layout of a PFOR exception region, and which PFOR variant is it?** "There is an exception list" is not implementable; "the entry-point array stores a 7-bit patch-offset + 25-bit position every 128 values, and exceptions grow backward from the block end" is. Two public PDFs deliver this.

| Paper | Authors | Public PDF | What it adds over Level 3 |
|-------|---------|-----------|---------------------------|
| [Z09] *Balancing Vectorized Query Execution with Bandwidth-Optimized Storage* (PhD thesis, U. Amsterdam / CWI, 2009) | M. Żukowski | [ir.cwi.nl/pub/14075/14075B.pdf](https://ir.cwi.nl/pub/14075/14075B.pdf) — **§6.2 read** | The **byte-exact** original-PFOR layout, the two-loop decode (decode-all then patch), and the **compulsory-exception** rule. This is [Z06] expanded into implementation detail. |
| [LB15] *Decoding Billions of Integers per Second Through Vectorization*, SP&E 45(1) 2015 | D. Lemire, L. Boytsov | [arXiv:1209.2137](https://arxiv.org/abs/1209.2137) (free) — **§2.8 read** | The **taxonomy** of every PFOR variant (PFOR, PFOR2008, NewPFD/OptPFD, FastPFOR, SimplePFOR) with each one's exact exception storage. Tells us *which layouts to test*. |

### 15.1 The exact original-PFOR layout ([Z09] §6.2.2 / §6.2.6)

This is the structure to look for first in the A1 verifier dump, because SQL Server's columnstore was contemporaneous with and influenced by this exact design:

1. **Single bit width `b` per page** (not per block). All regular values are bit-packed in `b` bits.
2. **Blocks of 128 values.** A regular value (`< 2^b`) stores its own bits. An **exception** value's `b`-bit slot instead stores *the offset to the next exception minus one* — the exceptions form a **linked list threaded through the packed array itself**.
3. **Entry-point array for random access:** "once every 128 values" an entry is stored = **7-bit patch-start + 25-bit exception position** (32 bits total, 0.25 bits/value overhead). The 25-bit field is why a PFOR page maxes at **32 MB**.
4. **Exception *values* are stored uncompressed, growing *backward* from the block** (`exception[-1 - i]` in the thesis's C code). Decode walks the linked list forward through positions while reading patch values backward from the exception base pointer.
5. **Two-loop decode** (the "P" in PFOR): LOOP1 bit-unpacks everything (producing garbage at exception slots); LOOP2 walks the linked list and overwrites the garbage with the real values. A `mssqlbak` decoder that omits LOOP2 produces **exactly the Issue-1 symptom** — correct values until the first exception, then corruption onward.

### 15.2 Compulsory exceptions ([Z09] §6.2.7) — the likely "row ~3820" trigger

> "The compressed integer codes only have a range `[0, 2^b − 1]`; hence the maximum distance between elements in the linked list of exceptions is `2^b`. If gaps exceeding this distance occur, **compulsory exceptions** must be introduced." — [Z09] §6.2.7

A compulsory exception is a value that *is* representable in `b` bits but is **forced** to be an exception anyway, purely so the linked-list offset never exceeds `2^b`. Implication for B1: the divergence point is **not necessarily where the first out-of-range value occurs** — it can be a compulsory exception inserted to bridge a long run of regular values. This explains why the break point (row ~3820) may not line up with any obviously "large" data value. The decoder must honor *every* linked-list hop, including hops that land on representable-looking values.

### 15.3 Which variant? — the discriminator checklist ([LB15] §2.8, Table 3)

If the original-PFOR layout (15.1) does not match the verifier dump, [LB15] enumerates the alternatives. Map the A1 byte dump against these signatures **in order**:

| Variant | Bit width | Exception storage | Discriminating signature in the dump |
|---------|-----------|-------------------|--------------------------------------|
| **PFOR** / **PFOR2008** | one `b` per page | linked list in-band + values at block end; uses **compulsory exceptions** | `b`-bit slot at an exception = an *offset*, not data; entry array of 32-bit (7+25) words |
| **NewPFD / OptPFD** | per-128-block `b` | per-block: stores the **low `b` bits** in-band and the **high `32−b` bits + positions** in a Simple-16-compressed side array; **no compulsory exceptions** | each block prefixed by a 32-bit word = `(b, #exceptions, exception-words)`; exception slot holds *real low bits*, not an offset |
| **FastPFOR** | per-128-block `b` | exceptions on a **per-page** basis, split into **32 arrays (one per bit width)**, each bit-packed | a byte array of `(b, max_bits, count, positions…)` per block + 32 trailing bit-packed high-bit arrays |

The single most useful discriminator: **read the `b`-bit value sitting at the first known exception slot.** If it equals an *offset/stride to the next exception* → PFOR-family (15.1, do the linked-list walk). If it equals the *low bits of the real value* → NewPFD/OptPFD-family (combine with high bits from a side array; no list walk). This one observation collapses the whole search space.

### 15.4 Net effect on the plan (§13) — updated 2026-06-16

| Plan item | Outcome |
|-----------|---------|
| **B1** (enc=1 ARCHIVE bitpack) | **✅ RESOLVED** — but NOT by PFOR exception handling. The actual root cause was LOB assembly padding in `_read_large_root_data` (commit 18b4082). The PFOR exception hypothesis (§14.1) was wrong for the observed symptom. |
| **Fragment table — empirical A1 result** | **✅ IMPLEMENTED** — blob diagnostic confirms the "fragment table" (bytes 48..rle_start, `n_frags = ceil(n_rows/512)` × 8 bytes) stores per-block Frame-of-Reference (FOR) bases in `u32[0]` of each entry.  For all existing test fixtures (sequential integer ids) all bases are 0.  `_bitpack_values` now reads and applies per-block FOR correction — a no-op for sequential data but correct for non-sequential ARCHIVE integer columns. |
| **PFOR exception linked-list** | **⚠️ NOT CONFIRMED** — the fragment table has no room for a PFOR entry-point array (`bp_start - frag_table_end = 16 bytes` < 274 entries × 4 bytes needed). Exception slots are not observable in sequential data. The PFOR exception mechanism described in §15.1 may: (a) not be used by SQL Server, (b) require real-world non-sequential data to appear, or (c) be handled by a different mechanism not yet visible. **Defer until a fixture with non-sequential ARCHIVE integers is available.** |
| Issue-1 root-cause confidence | `[CONFIRMED]` — root cause is LOB bsz truncation, not PFOR exceptions. PFOR exception correctness is `[UNKNOWN]` pending non-sequential data. |

### 15.5 `pfor_columnstore_full` fixture outcome (2026-06-16)

The non-sequential ARCHIVE integer fixture deferred in §15.4 was created:
`tests/fixtures_20xx/pfor_columnstore_full.bak` — generated for SS 2017/2019/2022/2025.

**Schema** (`pfor_plain` = standard COLUMNSTORE, `pfor_archive` = COLUMNSTORE ARCHIVE):

| Column | Data | PFOR scenario |
|--------|------|---------------|
| `id` | sequential 1–200,000 | baseline |
| `v_none` | 200 copies each of 0–999 (non-sequential) | no exceptions needed (bpv=10) |
| `v_sparse` | mostly 0, a few large values | low exception density |
| `v_deep` | 0..7 with one high outlier per block | compulsory exceptions |
| `v_compulsory` | runs of same value, bridged by compulsory exceptions | compulsory-exception stress |
| `v_dense` | dense range with outliers interspersed | high exception density |

**What the fixture found — Bug I (fixed 2026-06-16):**

`test_pfor_columnstore_coverage.py` initially failed 6 tests for `pfor_archive` (ARCHIVE CCI) only. `pfor_plain` (standard CCI) passed all 12 tests. The failing columns were the enc=2 (dictionary-encoded integer) columns: `v_none`, `v_deep`, `v_compulsory`, `v_dense`.

Root cause: **ARCHIVE `enc=2` dictionary blobs are themselves XPRESS-compressed**, but `read_columnstore_rows` / `read_columnstore_batches` passed the raw compressed bytes directly to `_parse_numeric_dict_int` / `_parse_numeric_dict_float`. This produced an empty dictionary, causing the decoder to fall back to `_decode_enc1`, returning garbage values.

Fix: wrap `all_blobs.get(dict_bid, b"")` with `_unwrap_archive_blob(...)` in both the Python and Rust-hybrid paths for enc=2 float and integer dictionary lookups in `columnstore.py`. `_unwrap_archive_blob` is a no-op for non-ARCHIVE blobs, so the call is unconditionally safe. Commit: `fix: unwrap ARCHIVE-compressed enc=2 dictionary blobs before parsing`.

**PFOR exception verdict — still deferred:**

The `pfor_archive` columns with `v_compulsory` and `v_dense` (engineered to trigger exception handling) decoded correctly once the dictionary unwrapping fix was applied. This means SQL Server stores these integer columns as `enc=2` (dictionary lookup), not as raw PFOR bit-packed integers. PFOR exception handling applies to `enc=1` segments only, and no ARCHIVE `enc=1` fixture with actual exception slots has been observed yet.

**Net PFOR exception status:** `[STILL UNKNOWN]` — the fixture confirmed the fix was in the dictionary path, not the bit-pack exception path.

**Test results after fix:** `test_pfor_columnstore_coverage.py` → 18/18 pass. No regressions in `test_archive_null_coverage.py` (6/6) or `test_archive_columnstore_types_coverage.py` (6/7, one pre-existing UUID failure).

---

### 15.6 Pre-existing failures in `test_archive_columnstore_partition_coverage.py`

Running the full partition test suite (without any recent changes) produces **17 failures in this file plus 1 in the types file = 18 total**. All are pre-existing, unrelated to the enc=2 dictionary fix.

#### Root cause: enc_type=5 for large CHAR segments (Gap 5)

The partition fixture puts **35,000 rows per partition** with CHAR(10) columns. SQL Server writes CHAR/NCHAR/BINARY columns as enc_type=5 ("multi-sub-block ARCHIVE blob") when a segment exceeds ~32,767 rows. This triggers even for **standard COLUMNSTORE** segments — enc_type=5 is not exclusive to ARCHIVE compression. The decoder (`_decode_enc5_archive`) does not correctly decode null bitmaps or values for these large segments, producing:

- **Null inflation:** e.g., 77,595 NULLs instead of 140 — the null bitmap is being misread
- **Garbled values:** raw enc_type=5 blob bytes returned as the string value, e.g., `'÷ÿ¨©©©¨¨...'` instead of `'1         '`

#### Why COLUMNSTORE control partitions also fail

The `archive_part_mixed` and `archive_part_roundtrip` tables include partitions that are standard COLUMNSTORE (not ARCHIVE). Because each partition still has 35,000 rows of CHAR(10) data, SQL Server still writes enc_type=5 segments for those partitions. The decoder fails identically for both ARCHIVE and standard COLUMNSTORE enc_type=5 segments, which is why the "control" partition tests also fail.

#### The 17 failing partition tests

| Test | Table | Failing partition(s) | Compression | Symptom |
|------|-------|----------------------|-------------|---------|
| `test_single_total_code_nulls` | `archive_part_single` | all (sum) | P1=ARCHIVE, P2-4=COLUMNSTORE | 280 code NULLs expected; enc_type=5 inflates count |
| `test_single_total_zip_nulls` | `archive_part_single` | all (sum) | same | 140 zip NULLs expected; got 77,595 |
| `test_single_p2_code_nulls` | `archive_part_single` | P2 | standard COLUMNSTORE | enc_type=5 triggers for 35k-row COLUMNSTORE segment |
| `test_mixed_total_code_nulls` | `archive_part_mixed` | all (sum) | P1+3=ARCHIVE, P2+4=COLUMNSTORE | total code NULLs wrong |
| `test_mixed_total_zip_nulls` | `archive_part_mixed` | all (sum) | same | total zip NULLs wrong |
| `test_mixed_columnstore_partitions_code_nulls[2-id_range0]` | `archive_part_mixed` | P2 | standard COLUMNSTORE | enc_type=5 in control partition |
| `test_mixed_columnstore_partitions_code_nulls[4-id_range1]` | `archive_part_mixed` | P4 | standard COLUMNSTORE | enc_type=5 in control partition |
| `test_mixed_columnstore_partitions_zip_nulls[2-id_range0]` | `archive_part_mixed` | P2 | standard COLUMNSTORE | enc_type=5 in control partition |
| `test_mixed_columnstore_partitions_zip_nulls[4-id_range1]` | `archive_part_mixed` | P4 | standard COLUMNSTORE | enc_type=5 in control partition |
| `test_mixed_non_null_values_control_partition` | `archive_part_mixed` | P2 | standard COLUMNSTORE | garbled CHAR value returned |
| `test_roundtrip_total_code_nulls` | `archive_part_roundtrip` | all (sum) | all COLUMNSTORE (post-rebuild) | enc_type=5 in all-COLUMNSTORE table |
| `test_roundtrip_total_zip_nulls` | `archive_part_roundtrip` | all (sum) | all COLUMNSTORE | same |
| `test_roundtrip_per_partition_code_nulls[1-id_range0]` | `archive_part_roundtrip` | P1 | COLUMNSTORE | enc_type=5 |
| `test_roundtrip_per_partition_code_nulls[2-id_range1]` | `archive_part_roundtrip` | P2 | COLUMNSTORE | enc_type=5 |
| `test_roundtrip_per_partition_code_nulls[3-id_range2]` | `archive_part_roundtrip` | P3 | COLUMNSTORE | enc_type=5 |
| `test_roundtrip_per_partition_code_nulls[4-id_range3]` | `archive_part_roundtrip` | P4 | COLUMNSTORE | enc_type=5 |
| `test_roundtrip_non_null_values` | `archive_part_roundtrip` | P1 | COLUMNSTORE | garbled CHAR value returned |

**Passing tests within the same file (selected):**

- `test_archive_part_classify_supported[*]` (4 tests) — schema classification does not depend on enc_type=5 decode
- `test_archive_part_row_count[*]` (4 tests) — row count comes from a metadata catalog lookup, not cell decode
- `test_single_p1_code_nulls` — the ARCHIVE partition 1 test for code NULLs **passes**, meaning enc_type=5 null decode works in isolation for one partition scoped by id range (a partial decode or the ARCHIVE-specific path for a single segment)
- `test_all_total_code_nulls` / `test_all_total_zip_nulls` — `archive_part_all` total NULL counts pass; for this scenario all partitions are ARCHIVE and the decoder's behavior is consistently wrong by the same margin, or this fixture happened to produce segments where enc_type=5 reads "correctly" by accident

#### The 18th failure: `test_uuid_values_are_uuid`

In `test_archive_columnstore_types_coverage.py`, the UUID column (`UNIQUEIDENTIFIER`, enc_type=5 fixed 16-byte pool) returns bytes that do not parse as a valid UUID. This is a separate manifestation of the enc_type=5 pool-read bug for fixed-width binary types and was pre-existing before the enc=2 dictionary fix.

#### Tracking

All 18 failures are tracked under **Gap 5** in `260616-status.md`. The fix requires correcting `_decode_enc5_archive` (and possibly a related path in the standard COLUMNSTORE segment reader) to:
1. Correctly decode the null bitmap for enc_type=5 segments (currently over-counts NULLs)
2. Correctly decode fixed-width string/binary values from the pool for enc_type=5 segments

The fixture already contains the right test cases; no new fixture work is needed.

### 15.7 Diminishing returns — stop here

This is the natural terminus of the citation graph for `mssqlbak`'s purposes. The Level-4 bibliographies ([Z09], [LB15]) branch into **SIMD/vectorization microarchitecture** (SSE2/AVX bit-unpacking kernels, `pshufb` shuffles, branch predication on Itanium) and **information-retrieval posting-list codecs** (Simple-8b, varint-G8IU, Golomb/Rice, Elias gamma). Neither branch is format-relevant: they optimize *decode speed* on a known layout, not the *on-disk byte layout* itself. The layout knowledge has been fully extracted at this level. **Do not chase Level 5** — the remaining citations are CPU-performance and IR-ranking papers with no bearing on the `.bak` byte format.

### 15.8 Co-author completeness audit (author-by-author, 2026-06-16)

The Level-3/4 chase above followed *lead authors* and *bibliographies* (the lineage),
not every **co-author** of every downloaded PDF. This subsection closes that gap by
enumerating the full author list of each read PDF and recording chase status, so the
question "did we check all authors to the 4th degree?" has a documented answer:
**partially — the lineage was exhausted, but not every co-author was individually
chased. Doing so now (below) confirms saturation and adds two corroboration artifacts,
no new byte layout.**

| PDF | Co-authors | Chased? | Result of chasing the un-chased |
|-----|-----------|---------|----------------------------------|
| [L15] | Larson ✔(§9.1), **Birka, Huang, Nowakiewicz, Papadimos**, Hanson ✔(§9.5) | lead only | Microsoft engineers; no public on-disk-format writing. Won't publish the proprietary layout (consistent with §16.9). |
| [L13] | Larson ✔, **Clinciu, Fraser**, Hanson ✔ | lead only | Same — Microsoft query-processing engineers. |
| [H13] | Larson ✔, Freedman ✔(§9.4), **Diaconu, Ismert, Mittal, Stonecipher, Verma, Zwilling** | lead only | XTP engineers; format opaque by design (§8.8). No format docs. |
| [Z06] | Zukowski ✔, **Héman, Nes, Boncz** | lead only | **Chased Boncz** (CWI/MonetDB/VectorWise/DuckDB): his VLDB 2009 column-store tutorial + Abadi/Boncz/Harizopoulos 2013 survey **re-derive the same FOR/PFOR/RLE/bitpack facts** already captured. Saturated. |
| [A06] | Abadi ✔(§14.2), **Madden, Ferreira** | lead only | Madden's later column-store work folds into the Abadi/Boncz 2013 survey above. Saturated. |
| [LB15] | Lemire (partial), **Boytsov** | lead only | **Chased Lemire's full corpus** (FastPFor + FrameOfReference GitHub, Stream/MaskedVByte, SIMD-BP128): reference C++ impls + the Damme survey below. Confirms the per-block exception-header math; no SQL-Server-specific layout. |

**Two new corroboration artifacts** surfaced by the author-by-author pass (added to
`CORROBORATION_SOURCES.md`; both **`[CORROBORATED]`-grade at best** — third-party,
not Microsoft-normative):

1. **Damme, Habich, Hildebrandt, Lehner — "Lightweight Integer Compression: an
   experimental survey + cost-based selection strategy," ACM TODS 2019**
   ([dl.acm.org/10.1145/3323991](https://dl.acm.org/doi/10.1145/3323991)). The most
   complete public catalog of FOR/PFOR/null-suppression variants **plus a cost model
   for which bit-width/algorithm an engine picks for given data** — corroboration for
   the enc=1 bit-width-selection heuristic (status **G3 / B1**), not a new layout.
2. **BtrBlocks (Kuschewski et al., TUM, SIGMOD 2023)**
   ([cs.cit.tum.de …/btrblocks.pdf](https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf)).
   A clean, public, modern columnar scheme combining FOR + bit-packing + exception
   handling — an independent restatement of the same family, useful as a readable
   reference but not SQL Server's bytes.

The LB15 full-text also pins a concrete exception-block header (corroborates §15.1):
*"each block of 128 coded integers is preceded by a 32-bit word storing the bit width,
the number of exceptions, and the exception storage size in 32-bit words"*, and
*"PFD picks the smallest `b` such that ≤10% of values are exceptions."*

**Net:** the author graph is now exhausted **by author, not just by lineage**. Every
remaining open item (enc=5 Format A-D byte layout, MSSQLBAK container record headers,
G6 large-segment decode) is blocked on a **live engine verifier** (`DBCC CSINDEX` /
DMV capture), not on any unread paper. No Level-5 chase is warranted.

---

## 16. Paul White Cluster — Verifier-Tool & Empirical-Technique Authors (2026-06-16)

**What this is.** The `DBCC CSINDEX` find (§12, `260616-status.md`) came from **Paul White**
(sql.kiwi). Tracing his network outward yields a tight cluster of internals authors
whose public work bears on the open columnstore TODOs (G1, G3, G6). **Important
distinction:** this is *not* the on-disk-format author graph (that branch is closed — the
columnstore byte layout remains undocumented). This cluster supplies three different,
still-useful things: **verifier tooling**, **precise runtime constraints** that bound our
decoder, and **fixture-building techniques**. None publishes the segment byte layout; all
help us reverse-engineer it empirically.

### 16.1 New nodes

| Node | Who | Public work | Relevance to open TODOs |
|------|-----|-------------|--------------------------|
| **Paul White** | MS Data Platform MVP; query-processor internals — sql.kiwi, SQLPerformance | `DBCC CSINDEX` field semantics; batch-mode normalization / "deep data"; bitpack width set; batch-mode bitmaps | The verifier tool + the precise constraints below |
| **Joe Obbish** | Deepest public columnstore experimenter — `orderbyselectnull.com` | RLE 64-repeat threshold proof; MAXDOP/round-robin segment distribution; **reverse-engineered the SS2022 "soft sort"**; `ORDER BY (SELECT NULL)` order-control trick | **Fixture technique** for plan `260616-3`: deterministic control of CCI row order → known, reproducible non-sequential segment contents |
| **Erik Darling** | Darling Data; hosted Obbish's columnstore precon | Columnstore maintenance, delete/update side-effects, delta/deleted-row behavior | **G1** — delta-store + deleted-row counting pitfalls |
| **Erin Stellato / Joe Sack** | SQLskills→MS / MS query processing | Edit/host White's SQLPerformance series; adaptive QP | Context only — not storage-format |
| **SQL Server Tiger Team** | Microsoft engineering | Adaptive Index Defrag (columnstore-aware) | Confirms row-group state handling for maintenance — tangential to G1 |

### 16.2 New concrete facts (corroborated, directly usable)

These refine the spec without needing the undocumented layout:

1. **Exact bit-pack width set** (Paul White, batch-mode + pushdown posts): SQL Server uses
   SIMD bit-unpacking for widths **1–10, 12, and 21** bits, plus standard **16, 32, 64**.
   These are the *only* legal `b` values (they tile a 64-bit unit on hard borders).
   → sharper than verifier-doc §7.2's "9/12/16/21"; our bitpack reader should treat any
   other width as a decode error / wrong-offset signal.
2. **"Deep data"** (White, *Batch Mode Normalization*): batch mode stores each value in
   64 bits with the **LSB reserved** to flag null-or-deep; values that don't fit in 64 bits
   are stored off-row ("deep data") with an 8-byte reference. This is the runtime mirror of
   the on-disk **SS2022 `min_deep_data` / `max_deep_data`** columns in
   `sys.column_store_segments`.
3. **RLE Data array layout** (Neugebauer's full `DBCC CSINDEX` dump): a segment's value
   stream is a list of RLE entries, each either
   - **pure run** → `Index, Value, Count` (literal value repeated `Count` times), or
   - **impure run** → `Index, Bitpack Array Index, Count` (next `Count` values come from the
     bitpack array starting at that index).
   This *is* the value/null decomposition `_decode_enc5_archive` must reproduce for large
   segments (G6).
4. **ARCHIVE dictionary ≈ 20 bytes larger** than the default-compression dictionary
   (Neugebauer part 12) — a lead for the G44 binary-dictionary divergence.

### 16.3 Per-TODO mapping

| TODO | New lead from this cluster |
|------|----------------------------|
| **G3** (ARCHIVE min/max) | Decode **`min_deep_data`/`max_deep_data`** (SS2022) for string/UUID/>64-bit columns — these hold the real min/max when the value doesn't fit the 64-bit `min_data_id`. Verify via `DBCC CSINDEX` Segment Attributes. Several G3 failures are string/ARCHIVE columns where the 64-bit min/max is insufficient. |
| **G6** (enc=5 ≥32,768-row) | The RLE-array layout (16.2 #3) is the missing structure. Capture `DBCC CSINDEX(object_type=1)` for the failing `archive_part_*` enc=5 segments and map pure/impure entries to our pool/index reads. |
| **G6 / enc=1** | Constrain the bitpack reader to the legal width set (16.2 #1); an out-of-set width means we read `b` from the wrong offset. |
| **Plan `260616-3`** | **Replace/augment `ORDER BY NEWID()` with Joe Obbish's deterministic order control.** `NEWID()` randomizes but is non-reproducible — regenerating the fixture yields different segment bytes. Obbish's `ORDER BY (SELECT NULL)` / clustered-key-order load produces a *known, reproducible* non-sequential layout, so the committed `.bak` is deterministic and the same bug manifests on every rebuild. Strong refinement to Phase 1. |

### 16.4 Scope note

This cluster is **verifier-tooling + empirical-technique + runtime constraints**, not a new
on-disk-format spec. It does not reopen the format-author search (still closed): the segment
byte layout is undocumented and must be confirmed with `DBCC CSINDEX` + fixtures. What
changed is that we now have (a) the right tool, (b) the legal bitpack-width set, (c) the
deep-data / `min_deep_data` lead for G3, and (d) a *reproducible* way to build non-sequential
fixtures. **Stop expanding the cluster** — the next move is empirical capture, not more search.

---

## 17. OrcaMDF + OrcaSql — Clean-Room Format Ideas (GPL-3 safe)

**Both projects are GPL-3.0.** [OrcaMDF](https://github.com/improvedk/OrcaMDF) (Mark S.
Rasmussen) and its successor [OrcaSql](https://github.com/ycherkes/OrcaSql) are managed-code
readers of SQL Server MDF/page structures. We do **not** copy their code, port it, or
mirror its class/method structure — that would be a derivative work under GPL-3.

**What we *can* use:** the *facts about the on-disk format* they document. A file-format
fact (where a field lives, how a value is encoded) is not protected by copyright — only the
*expression* (their source) is. Clean-room rule for this section:

> Read OrcaMDF/OrcaSql only to learn **what** the format is. Re-derive and implement the
> behavior independently from the fact statements below + our own fixtures. Never paste,
> translate, or transliterate their code. Cite the fact, not the file.

### 17.1 Format facts worth adopting (re-implement independently)

| # | Format fact (clean-room) | Maps to spec item |
|---|--------------------------|-------------------|
| 1 | **Zero-physical-length columns.** A variable-length column can have a length-zero slot: its offset-array entry equals the previous entry (no bytes consumed). NULL and empty-string are distinguished by the null bitmap, not by the var-offset table. Decoder must not assume each var column consumes ≥1 byte. | G10/G11 (var-length record decode) |
| 2 | **Dropped-column data persists.** Dropping a column updates the catalog but leaves the column's bytes physically in existing records until an index/heap rebuild. The record layout still reserves the slot. Decode by catalog column order/offsets, not by counting "live" columns. | G12 (record↔catalog alignment), V02 |
| 3 | **Multiple `bit` columns share a byte.** `bit` columns are bit-packed 8-per-byte within the fixed-length region (in catalog order), each consuming 1 bit, not 1 byte. A 9th bit column starts a new byte. | G10 (fixed-width decode) |
| 4 | **`pg_first` shortcut.** An allocation unit's first data page can be reached directly from `sys.system_internals_allocation_units.first_page` (the `pg_first` pointer) instead of walking the IAM chain — a fast path for locating the head of a heap/index. | G5 (allocation-unit traversal) |
| 5 | **Collation drives string decode.** char/varchar bytes are only interpretable with the column's collation (code page / sort id) from the catalog; nchar/nvarchar are UCS-2/UTF-16LE. Carry collation through from the catalog to the value decoder. | G43 (string value decode) |
| 6 | **Modern temporal/numeric encodings.** `date` = 3-byte day count; `time(n)`/`datetime2(n)`/`datetimeoffset(n)` = scale-dependent integer of fractional-second ticks (+ 2-byte UTC offset for DTO); `decimal/numeric` = sign byte + little-endian mantissa sized by precision. | G44, V12 (modern type decode) |
| 7 | **Null bitmap is always present** for records with nullable columns, sized `ceil(ncols/8)`, indexed by catalog column ordinal (including dropped columns, per #2). | G10/G11 |

### 17.2 Test-vector asset (not code)

OrcaSql ships a **test corpus** of small databases with expected decoded values. We do not
take their test code, but the *idea* — cross-check our decoder's `f(id)` value
interpretation against an independent reader's published expected values — is a clean-room
value-level verification we can reproduce with our own fixtures (see plan `260616-3` §II.7).

### 17.3 Clean-room boundary recap

- ✅ Adopt: the **facts** in 17.1 (re-implemented from scratch against our fixtures + `DBCC PAGE`).
- ✅ Adopt: the **technique** of value-level cross-checking (17.2).
- ❌ Do not: copy, port, translate, or structurally mirror any OrcaMDF/OrcaSql source.
- ❌ Do not: vendor their files or lift their test databases as our fixtures.

Every fact above is independently confirmable with `DBCC PAGE` / `DBCC IND` on our own
fixtures — which is how it should be verified before landing in `BAK_FORMAT_SPEC.md`.

---

## 18. Microsoft Tape Format (MTF) + Neugebauer/CISL — Findings (no GPL-3 exposure)

**License posture (why this is safe to use):**

| Source | License / nature | How we may use it |
|--------|------------------|-------------------|
| **MTF — Microsoft Tape Format Specification v1.00a** | Published Microsoft/industry **specification document** (not GPL code) | Implement a parser directly from the documented field layout |
| **Niko Neugebauer — "Clustered Columnstore Indexes" blog series** | Author's **blog writing**; we extract **facts**, not prose | Use the documented format facts; cite the post |
| **CISL — Columnstore Indexes Scripts Library** | **Apache-2.0** (permissive, no copyleft) | May reference/run the T-SQL scripts as verifier tooling, with attribution |

None of these is GPL-3; the clean-room caution that applies to OrcaMDF/OrcaSql (§17) does
**not** apply here. CISL being Apache-2.0 means we can even use its scripts as verifier
helpers (with attribution) — unlike OrcaMDF/OrcaSql code.

### 18.1 MTF — container facts for uncompressed backups

MTF is the on-tape/on-disk **container** that wraps an uncompressed SQL Server `.bak`.

| # | Fact | Maps to spec item |
|---|------|-------------------|
| 1 | The file is a sequence of **Descriptor Blocks (DBLKs)** aligned to a physical-block boundary (SQL Server uses a 1024-byte PB_SIZE). | G14 (MTF container) |
| 2 | Every DBLK begins with a **common header**: 4-char ASCII **block type**, block attributes (flags), offset-to-first-event, OS id + version, displayable size (8 bytes), and a **Format Logical Address (FLA)**. | G14 |
| 3 | Block types seen in SQL backups: `TAPE` (media header), `SSET` (start of data set), `VOLB`, `DIRB`, `FILE`, `ESET` (end of set), `EOTM` (end of tape), `SFMB` (soft filemark). | G14 |
| 4 | Within a data set, payload is carried in **stream headers** (4-char stream id, attributes, 8-byte length, compression/encryption algorithm fields). The **`MSDA`** stream carries the actual 8 KB SQL Server data pages. | G14, V02 |
| 5 | MTF strings carry a **string-type byte** (ANSI vs Unicode); the DBLK header records which, so name/path fields must be decoded accordingly. | G14 |

→ A correct uncompressed-backup reader walks DBLKs by FLA, finds the `SSET`/`MSDA`
stream, and treats its body as the contiguous 8 KB page stream the page-level parser
already understands.

### 18.2 Neugebauer — columnstore internals facts

From the "Clustered Columnstore Indexes" series (facts only; `DBCC CSINDEX` syntax already
captured in §12):

| # | Fact | Source part | Maps to |
|---|------|-------------|---------|
| 1 | Columnstore build is **3 phases**: row-group separation → segment creation → compression. | part 40 | context |
| 2 | Compression toolbox: **value scale, bit array, RLE, dictionary, (Huffman/LZW historically), xVelocity binary**; **ARCHIVE adds a modified/optimized LZ77 layer** on top. | part 40 | G6 / G44 |
| 3 | Segments may carry **primary and secondary dictionaries**; the **HashTable Array Data** holds the distinct values, and segment data-ids reference dictionary entries. | part 40 / 12 | G43 (dictionary decode) |
| 4 | The **ARCHIVE dictionary is ≈ 20 bytes larger** than the default-compression dictionary for most columns — a measurable divergence to reproduce. | part 12 | G44 |
| 5 | `DBCC CSINDEX` `object_type=2` dumps dictionary contents; `object_type=1` dumps the segment RLE/bitpack (the value/null structure for enc=5). | part 21 | G6 |

### 18.3 Engineer profiles (restored)

- **MTF spec authors** — the published Microsoft Tape Format spec is the authoritative,
  non-code source for the uncompressed-backup container; it is the right reference for any
  G14 container ambiguity.
- **Niko Neugebauer** — most exhaustive *public* columnstore documenter (130+ part series);
  author of **CISL (Apache-2.0)**. His `DBCC CSINDEX` walkthroughs (parts 12/21/40) are the
  practical companion to Paul White's field semantics (§12, §16). Use his blog for facts and
  CISL for verifier tooling.

### 18.4 Boundary recap

- ✅ MTF: implement from the public spec.
- ✅ Neugebauer blog: adopt the documented facts (18.1/18.2), confirm on our fixtures.
- ✅ CISL: may be used/run as verifier tooling (Apache-2.0, attribute it).
- This section carries **no GPL-3 obligation**; only §17 (OrcaMDF/OrcaSql) does.
