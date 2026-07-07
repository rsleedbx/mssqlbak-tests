# Checksum Integrity and Catalog-Based Extraction Verification

**Date:** 2026-06-17  
**Status:** ⬜ research / planning — nothing implemented yet

**Related:**
- [`BAK_FORMAT_SPEC.md`](BAK_FORMAT_SPEC.md) §1.1 (MTF headers), §2 (page layout), §1.1.5 (SSET proprietary stream)
- [`260616-2-fixture-dbcc-page-verifier.md`](260616-2-fixture-dbcc-page-verifier.md) §11.2 — `m_flagBits` page checksum bit
- [`CORROBORATION_SOURCES.md`](CORROBORATION_SOURCES.md) — `MTF`, `MTF-H`, `R-PAGE`, OrcaMDF tokens used below
- `mssqlbak/catalog.py` — `rowset_rcrows`, `rowset_compression`

---

## 1. The three checksum layers

There are three independent checksums in a `.bak` file.  They cover different scopes and
have different documentation status.

| Layer | Scope | Algorithm documented? | Reproducible? | mssqlbak status |
|-------|-------|-----------------------|---------------|-----------------|
| MTF block `header_checksum` | 52-byte MTF block header | Yes — MTF 1.0a spec | Yes — trivial | SKIPPED |
| Per-page `m_tornBits` checksum | Each 8 KB database page | Yes — community reverse-engineered | Yes — algorithm known | not read |
| Backup-stream checksum (`WITH CHECKSUM`) | Entire backup data stream | No — proprietary | No | not read |

---

### 1.1 MTF block `header_checksum` (offset 50)

**Scope:** each MTF block header (TAPE, SSET, DSCR, EOTM, every block type).

**Algorithm** — [`MTF` §5 common block header](https://chenjianlong.gitbooks.io/microsoft-tape-format-specification/content/section5/01_common_blk_hdr.html) (normative); also [`MTF-H` KyleBruene/mtf C header](https://github.com/KyleBruene/mtf/blob/master/mtf.h) (struct reference):

> *"The Header Checksum field is a 16-bit word-wise XOR sum of all the fields of the
> MTF\_DB\_HDR except for the checksum field itself."*

The header is 52 bytes.  The checksum at offset 50 is excluded; the preceding 50 bytes
are treated as 25 little-endian uint16 words and XOR'd together.

```python
import struct
def mtf_header_checksum(hdr_52: bytes) -> int:
    words = struct.unpack_from('<25H', hdr_52[:50])
    return 0xFFFF & sum(words)  # alternatively: reduce(xor, words)
```

**Current status:** `mssqlbak/reader.py` reads the 52-byte common header but never
validates this field.  It is listed as `SKIPPED` in `METADATA_COVERAGE.md`.

**Value:** detects any single-bit corruption in a block header — file truncation, wrong
block size, rewritten tape address — before the parser tries to decode the variable-length
fields.

---

### 1.2 Per-page `m_tornBits` checksum (page bytes 60–63)

**Scope:** each 8 KB database page where `m_flagBits & 0x200` is set (database
configured with `PAGE_VERIFY = CHECKSUM`).

**Algorithm** — [`R-PAGE` Paul Randal, Anatomy of a page](https://www.sqlskills.com/blogs/paul/inside-the-storage-engine-anatomy-of-a-page/) documents `m_flagBits` and `m_tornBits`; algorithm reverse-engineered by sqlteutonic blog 2016 and corroborated by [Paul Randal's 2014 page-checksum bug post](https://www.sqlskills.com/blogs/paul/nasty-day-1-bug-causing-page-checksums-miss-corruptions-2008-r220122014/):

The page is treated as 16 sectors of 512 bytes (128 × uint32 each).  The `m_tornBits`
field itself (sector 0, word index 15, i.e. bytes 60–63) is excluded.

```
for each sector i in 0..15:
    sector_xor = XOR of all 128 uint32 words in sector i
                 (sector 0 skips word[15] — the m_tornBits field)
    checksum ^= ROL32(sector_xor, 15 - i)
```

`ROL32(x, n)` is a 32-bit circular left rotation.  The result is stored in `m_tornBits`.

**Notes:**
- Randal's 2014 bug post identifies a weakness: certain repeating bit patterns (all-zero vs
  all-one adjacent DWORDs) can collide.  The algorithm is a Fletcher/Adler variant, not
  a full CRC.
- `m_flagBits & 0x100` means torn-page protection (not checksum); the bit is mutually
  exclusive with `0x200`.
- mssqlbak reads raw 8 KB page bytes in `mssqlbak/pages.py`.  The page bytes are
  available.  Verification would be added to the page ingestion path.

**Current status:** `m_flagBits` is documented in `260616-2-fixture-dbcc-page-verifier.md`
§11.2 with a note that `_verify_page_checksum()` should check this bit before
verifying.  No Python implementation exists.

**Value:** detects silent disk corruption that was already present in the source database
at backup time.  `BACKUP … WITH CHECKSUM` performs this check during backup creation
(stops with error 3043 on failure); mssqlbak would perform the same check at read time.

---

### 1.3 Backup-stream checksum (`WITH CHECKSUM` aggregate)

**Scope:** the entire backup data stream, computed as a running aggregate over all pages.

**Algorithm:** not documented by Microsoft.  The value is stored in the proprietary SQL
Server config stream appended after the standard SSET block (§1.1.5 in
`BAK_FORMAT_SPEC.md`).  The offset within that stream is not mapped.

Randal notes the aggregate builds on per-page checksums but the exact combining function
is opaque.  `RESTORE VERIFYONLY` performs this check against the stored value.

**Current status:** not read, not verifiable.

**Value for mssqlbak:** none currently.  Even if the stored value were found and read,
it cannot be recomputed without the algorithm.  Detecting whether a backup _has_ a
backup-stream checksum (`has_backup_checksums` flag) is possible via the proprietary
stream, but the stream mapping at §1.1.5 is `[HEURISTIC]` and does not currently expose
that flag.

---

## 2. What verification is possible without a restore

**Hard constraint:** mssqlbak must verify from the `.bak` file alone.  Restoring a
multi-hundred-GB backup to a running SQL Server instance to recompute statistics is not
feasible in practice.  All verifiers must read from the raw bytes already parsed during
extraction.

This constraint rules out anything derived from:
- `UPDATE STATISTICS` / `DBCC SHOW_STATISTICS` — requires live SQL Server
- `sys.dm_db_stats_properties` — DMV, live SQL Server only
- `DBCC CHECKDB` — requires restore
- `RESTORE VERIFYONLY` — requires SQL Server to interpret the backup-stream checksum

What remains is what SQL Server physically embedded in the page data at backup time.

---

### 2.1 What is physically inside the `.bak` and readable without restore

| Value | Source in .bak | Table type | mssqlbak reads it? |
|-------|----------------|------------|-------------------|
| Row count per rowset | `sysrowsets.rcrows` system table pages | All | Yes — `rowset_rcrows` in `catalog.py` |
| Segment row count | `_n_rows_from_blob` at offset 52 in segment blob | CCI only | Yes |
| Segment min/max (encoded) | `syscscolsegments.min_data` / `max_data` system table pages | CCI only | Yes |
| Segment min/max (decoded string/UUID, SS2022+) | `syscscolsegments.min_deep_data` / `max_deep_data` | CCI only | Yes |
| Segment null flag | `syscscolsegments.has_null` | CCI only | Yes |
| Per-page checksum | `m_tornBits` bytes 60–63 of each 8 KB page | All (if PAGE\_VERIFY=CHECKSUM) | No |
| MTF block header checksum | Offset 50 in every MTF block header | — (file-level) | No (SKIPPED) |

**Heap / B-tree tables only** — row count (`rcrows`) is the sole structural metric
available from the `.bak` without restore.  Min, max, null count, and value distributions
for heap/B-tree tables are **not stored in the catalog pages**.  They exist only in
`sysindexstats.statblob` (histogram blob, format undocumented — see §2.3) or by
scanning the actual data pages, which is what extraction already does.

---

### 2.2 Row count via `sysrowsets.rcrows`

`sysrowsets.rcrows` is in system catalog pages embedded in the `.bak`.  No restore is
needed.  mssqlbak reads this field already (`catalog.py`, `rowset_rcrows`).  It is
currently used only for CCI delta-store tombstone detection.

**Usefulness as a post-extraction row count cross-check:**

| Table type | Reliability |
|------------|------------|
| Heap / B-tree, no ghosts | High — rcrows matches extracted rows exactly |
| Heap / B-tree with ghost records | Lower — rcrows includes not-yet-reclaimed ghost rows that extraction skips |
| CCI compressed row group | Medium — rcrows per rowset equals row group size; `_n_rows_from_blob` (offset 52 in blob) is the authoritative per-segment count |
| Delta-store rowset | Excluded from cross-check (tombstone-filtered before extraction) |

This is the only per-table structural metric available for heap/B-tree tables without
a restore.

### 2.3 Statistics histograms (`sysindexstats.statblob`)

`sysindexstats` is a system heap table physically present as pages in the `.bak`.  The
`statblob` column holds the histogram and density vector for each statistics object.

**Availability:** in the `.bak` — no restore needed to read the raw bytes.  
**Readability:** not feasible.  The blob format is proprietary and undocumented.
[OrcaMDF](https://github.com/improvedk/OrcaMDF) has a partial `StatBlob` parser but it
is not from a normative source.

Even if the blob were readable, statistics are stale — they reflect the last
`UPDATE STATISTICS` run, not the state of the data at backup time.  For a freshly
updated table with no subsequent writes, histogram step ranges would be accurate, but
this cannot be guaranteed in general.

**Conclusion:** statistics histogram cross-checks are not viable as a general-purpose
in-file verifier.

### 2.4 Column-level min/max and null count for CCI tables (existing)

For CCI tables, `syscscolsegments` pages embedded in the `.bak` expose per-segment
`min_data` / `max_data` / `has_null` ([`MS-SEG` — `sys.column_store_segments`](https://learn.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-column-store-segments-transact-sql?view=sql-server-ver17)).
These are already read by mssqlbak and already used in the correctness suite (G3/G6
streams in `260617-1-cci-correctness-and-dirty-path.md`).  No new work needed here.

This is **not available for heap/B-tree tables** — there is no equivalent per-column
min/max stored in the catalog for non-columnstore tables.

---

## 3. Implementation priority

All items below operate on `.bak` bytes already in memory during extraction — no
restore, no SQL Server instance, no additional I/O beyond what extraction already
performs.

| # | Feature | Source in .bak | Effort | What it catches |
|---|---------|---------------|--------|-----------------|
| 3-A | MTF `header_checksum` validation | MTF block header offset 50 | Trivial | Block-header corruption, wrong block size, truncation |
| 3-B | `rcrows` post-extraction row count cross-check | `sysrowsets.rcrows` (already read) | Small | Extraction logic bugs — for all table types |
| 3-C | Per-page `m_tornBits` checksum | Page bytes 60–63 | Medium | Silent source-database disk corruption at backup time |
| 3-D | Backup-stream checksum | Proprietary SSET stream | Not feasible | — algorithm undocumented |
| 3-E | `statblob` histogram value cross-check | `sysindexstats` heap pages | Not feasible | — blob format undocumented; values also stale |

**Heap/B-tree min/max/null:** no in-file source exists for these beyond rcrows (row count)
and the data pages themselves (which extraction already scans).  There is no catalog
shortcut equivalent to `syscscolsegments` for non-CCI tables.  If value-distribution
verification is required for heap/B-tree tables, the only option is a full restore and
query — outside mssqlbak's scope.

Items 3-A and 3-B are zero-new-format-research additions.  
Item 3-C requires no restore and is independent of ongoing correctness work; it fits in
the page ingestion path in `pages.py`.
