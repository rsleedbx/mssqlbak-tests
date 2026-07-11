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
| 4 | 2 | uint16 LE | `flag_bits` (`m_flagBits`) | `0x100` = TORN_PAGE_DETECTION; `0x200` = CHECKSUM |
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
| 54 | 4 | — | `xdes_id` | raw 4 bytes; not parsed |
| 58 | 2 | uint16 LE | `ghost_rec_cnt` | deleted-but-not-reclaimed rows |
| 60 | 4 | uint32 LE | `m_tornBits` | torn-page bit-pairs (§2.7) or page checksum |
| 64 | 32 | — | remainder | reserved; not parsed |

Source: `pages.py` constants `_H_FLAG_BITS=4`, `_H_XDES_ID=54`, `_H_GHOST_REC_CNT=58`, `_H_TORN_BITS=60`.

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

An IAM page records which pages/extents belong to a particular allocation
unit.  Two regions within the 8 KB page body are decoded
(`rows.py` and `catalog.py`):

**Single-page-allocation (SPA) slots** — 8 entries at byte offset **140**,
each 6 bytes `(file_id uint16 LE, page_id uint32 LE)`.  These record
individual pages allocated from mixed extents (extents shared between
allocation units), and may reference any file in the database.

```python
_IAM_SPA_OFFSET = 140
_IAM_SPA_SLOTS  = 8
_IAM_SPA_STRUCT = struct.Struct("<HI")   # (file_id, page_id)
```

**Extent allocation bitmap** — an 8-bit-per-extent bitmap starting at byte
offset **194** (`_IAM_BITMAP_OFFSET`).  Each set bit indicates an allocated
extent (8 consecutive 8 KB pages) belonging to the tracked allocation unit.
All extent-bitmap pages belong to the same file as the IAM page itself
(determined by the IAM `start_pg` pointer).

```python
_IAM_BITMAP_OFFSET = 194   # first bitmap byte within the page body
```

Sources: `rows.py: _IAM_SPA_OFFSET/SLOTS/STRUCT/BITMAP_OFFSET`,
`catalog.py: _IAM_SPA_OFFSET/SLOTS/STRUCT/BITMAP_OFFSET`.

> **Verifier (G13):** `DBCC PAGE(CatalogSS2022, 1, 239, 3)` reports
> `IAM: Extent Alloc Status Slot 1 @0x...0C2` — raw address offset 0xC2 = 194
> from the page buffer start.  Sidecar: `tests/fixtures_2022/probe/G13.json`.

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

### 2.7 Torn-page restoration `[EMPIRICAL]`

Source: `pages.py: restore_torn_page` (lines 102–137).

Databases with `PAGE_VERIFY TORN_PAGE_DETECTION` (the SQL Server 2000 default,
preserved until a page is rewritten) protect sector-boundary writes by
overwriting the **low 2 bits of byte `sector×512+511`** for sectors 1–15 with
an alternating 01/10 signature.  The displaced bits are saved in `m_tornBits`
(offset 60): bit pair `[2k : 2k+2]` holds the real low 2 bits of sector `k`
(for k = 1..15).

**Restoration algorithm** (applied to every page before record/slot parsing):

```python
_FLAG_TORN_PAGE_DETECTION = 0x100

def restore_torn_page(raw: bytes) -> bytes:
    flag_bits = struct.unpack_from("<H", raw, 4)[0]       # m_flagBits at offset 4
    if not (flag_bits & _FLAG_TORN_PAGE_DETECTION):
        return raw                                         # no action for CHECKSUM pages
    torn = struct.unpack_from("<I", raw, 60)[0]           # m_tornBits at offset 60
    out = bytearray(raw)
    for sector in range(1, 16):
        pair = (torn >> (2 * sector)) & 0x3
        off  = sector * 512 + 511
        out[off] = (out[off] & 0xFC) | pair
    return bytes(out)
```

Pages protected by CHECKSUM (`m_flagBits & 0x200`) are returned unchanged;
their sector bytes are genuine data.

---

### 2.8 Record-boundary reconstruction `[EMPIRICAL]`

Source: `pages.py: Page.__post_init__` (lines 254–304).

After restoration, individual record bytes are sliced by finding each record's
end offset.  The algorithm differs between DATA pages and INDEX pages.

**DATA pages (m_type = 1):**

1. **Primary-record filter**: keep only slot-array offsets `off` where
   `raw[off] & 0x07 == 0` (status byte low 3 bits = `PRIMARY_RECORD`).
   This discards forwarding stubs, ghost records, and index entries that happen
   to appear at non-zero offsets.
2. **Stride filter**: after sorting the surviving offsets, drop any offset
   closer than `pminlen` bytes to its predecessor.  This removes sub-slot
   artifacts from corruption or sparse allocation.
3. Append `free_data` as a sentinel.
4. A record's end = the next-higher entry in the sorted boundary list,
   found with `bisect.bisect_right`.

**INDEX pages (m_type = 2)**: neither filter is applied — all slot offsets
are kept and the sorted set includes `free_data`.

```python
# Simplified from pages.py Page.__post_init__
pminlen = header.pminlen
if header.m_type == 1 and pminlen > 0:
    primary = sorted(off for off in slots if raw[off] & 0x07 == 0)
    filtered = []
    prev = -pminlen
    for off in primary:
        if off - prev >= pminlen:
            filtered.append(off)
            prev = off
    sorted_slots = tuple(filtered) + (header.free_data,)
else:
    sorted_slots = tuple(sorted(set(slots) | {header.free_data}))

def record_bytes(slot: int) -> bytes:
    start = slots[slot]
    idx = bisect.bisect_right(sorted_slots, start)
    end = sorted_slots[idx]
    return raw[start:end]
```

---

