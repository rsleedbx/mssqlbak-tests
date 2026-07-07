## 2. MDF Page Layer

### 2.1 Page structure `[CONFIRMED]`

A SQL Server data file is an array of 8 192-byte pages:
- Page `k` occupies `image[k * 8192 : (k+1) * 8192]`.
- The primary data file (`.mdf`) is always file ID 1.
- Secondary files (`.ndf`) have file IDs ≥ 2.

Page layout:
```
[0:96]    page header  (96 bytes, §2.2)
[96:free_data]  records, packed forward from the header
[free_data:8192 - 2*slot_cnt]  free space
[8192 - 2*slot_cnt : 8192]     slot array, growing backward
```

### 2.2 Page header (96 bytes, little-endian) `[CONFIRMED]`

Verified against the committed fixture; matches OrcaMDF's `PageHeader`.

| Offset | Size | Type | Field | Notes |
|--------|------|------|-------|-------|
| 0 | 1 | uint8 | `header_version` | always `1` in SQL 2022 fixtures |
| 1 | 1 | uint8 | `m_type` | page type (see §2.3) |
| 2 | 1 | uint8 | `type_flag_bits` | |
| 3 | 1 | uint8 | `level` | B-tree level; 0 = leaf |
| 4 | 2 | uint16 LE | `flag_bits` | |
| 6 | 2 | uint16 LE | `index_id` | (`m_indexId`) |
| 8 | 6 | PagePointer | `prev_page` | `{uint32 page_id, uint16 file_id}`; `(0,0)` = none |
| 14 | 2 | uint16 LE | `pminlen` | min fixed-length row size |
| 16 | 6 | PagePointer | `next_page` | same format |
| 22 | 2 | uint16 LE | `slot_cnt` | number of slots in the slot array |
| 24 | 4 | uint32 LE | `obj_id` | allocation-unit id (`m_objId`) |
| 28 | 2 | uint16 LE | `free_cnt` | bytes of contiguous free space |
| 30 | 2 | uint16 LE | `free_data` | byte offset to start of free space |
| 32 | 6 | PagePointer | `page_id + file_id` | this page's own locator |
| 38 | 2 | uint16 LE | `reserved_cnt` | |
| 40 | 12 | — | `lsn` | `{uint32 vlf_seq, uint32 blk_offset, uint16 rec_pos}` LE |
| 52 | 2 | uint16 LE | `xact_reserved` | |
| 54 | 6 | — | `xdes_id` | raw; not parsed |
| 60 | 2 | uint16 LE | `ghost_rec_cnt` | deleted-but-not-reclaimed rows |
| 62 | 34 | — | remainder | reserved; not parsed |

### 2.3 Page types (`m_type`) `[CONFIRMED]`

| `m_type` | Name | Description |
|----------|------|-------------|
| 1 | DATA | Heap / B-tree leaf data pages |
| 2 | INDEX | B-tree index pages |
| 3 | LOB_DATA | LOB data pages (text/image/varchar(max)) |
| 4 | LOB_TREE | LOB B-tree interior pages |
| 10 | IAM | Index Allocation Map |
| 13 | BOOT | Database boot page (page 9) |
| 15 | FILE_HEADER | File header (always page 0) |

> **Unknown types observed but not decoded:** 7 (GAM), 8 (SGAM), 9 (PFS).
> These are allocation map pages; no row data is present.

### 2.4 Slot array `[CONFIRMED]`

The slot array occupies the last `2 × slot_cnt` bytes of the page.
- Entry `j` (0-based) is at `page[8192 - 2*(j+1) : 8192 - 2*j]`.
- Each entry is a `uint16 LE` byte offset from the page start to that record.
- Slot 0 is at the **highest** physical address (last two bytes of the page).

### 2.5 IAM page (m_type 10) `[CONFIRMED]`

An IAM page contains an 8-bit-per-extent bitmap starting at **byte offset
194** within the page (`rows.py: _IAM_BITMAP_OFFSET`).  Each set bit indicates
an allocated extent (8 consecutive pages) belonging to the tracked allocation
unit.  Bytes `[0:194]` (IAM header, single-page array, start/extent metadata)
are **not parsed** — only the bitmap region is walked.

> **Verifier (G13):** `DBCC PAGE(CatalogSS2022, 1, 239, 3)` reports
> `IAM: Extent Alloc Status Slot 1 @0x...0C2` — raw address offset 0xC2 = 194
> from the page buffer start.  Sidecar: `tests/fixtures/probe/G13.json`.

### 2.6 Boot page (m_type 13, page 9) `[CORROBORATED]`

Page 9 of file 1 is the database boot page (`dbi`).  It contains a pointer
to `sysallocunits` that bootstraps the system catalog.

**G14 `[CONFIRMED]`**: the `sysallocunits` first-page pointer
`(page_id UINT32 LE, file_id UINT16 LE)` is at byte offset **516** of boot-page
record 0.  Confirmed by programmatic scan across SS2017, SS2019, SS2022, and
SS2025 in multiple fixture types; the offset is invariant across all versions and
database sizes tested.  The parser uses a fast-path direct read at offset 516
with a full-scan fallback for unknown versions.
Sidecar: `tests/fixtures_2022/probe/G14.json`.

---

