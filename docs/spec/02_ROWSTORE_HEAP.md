# Rowstore Heap — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `ROWSTORE_HEAP` (spec abstraction, not a code symbol)
**Set by:** `read_table_rows` (`mssqlbak/rows.py:1132`) when `table.compression == 0` and `table.index_id == 0` (heap).
Routing is driven by `table.compression` (`rows.py:1194`) and `table.is_memory_optimized` (`extract.py:494`).
**Catalog signal:** `sysrowsets.cmprlevel == 0`, `sys.indexes.type == 0` (heap)
**Decode entry point:** `rows.py:1132` → `decode_record()` (`records.py:69`) → FixedVar path

---

## 2. Initialization

Read slot array from page tail. No clustered key columns. Variable-length column offsets at end of fixed region.

---

## 3. Record structure

### 3.1 FixedVar record (uncompressed, `cmprlevel = 0`) `[CONFIRMED]`

Verified against `typecoverage_full.bak` (SQL Server 2022) and OrcaMDF.

```
[+0]  uint8  status_A
              bit 0x10 → null bitmap present (always set in practice)
              bit 0x20 → variable-length section present
[+1]  uint8  status_B
              bit 0x01 → ghost forwarded record
[+2]  uint16 LE  fixed_end     byte offset to end of fixed region
[+4 .. fixed_end)  fixed-length column data
  [fixed_end]    uint16 LE  ncol    column count
  [fixed_end+2]  bytes       null bitmap  ceil(ncol/8) bytes
                              bit i → column i is NULL
  if status_A & 0x20:
    [null_bitmap_end]  uint16 LE  nvar    variable column count
    [nvar_start+2]     uint16 LE[nvar]    var_end_offsets
                        top bit 0x8000 = complex/off-row LOB flag
    [nvar_start+2+2*nvar ..]  variable-column payloads, contiguous
```

Fixed columns: each column's bytes are at `[leaf_offset : leaf_offset+size]`
within `[4, fixed_end)`, where `leaf_offset` comes from `sysrscols`.

**BIT column packing** `[CONFIRMED]`: multiple `bit` columns that share the
same `leaf_offset` are packed into one byte.  The parser assigns each column a
`bit_shift` (0-based, ordered by `colid` among columns at that offset) and
decodes `(byte >> bit_shift) & 1`.  Verified on `layoutcoverage_full.bak`
(`f_bit` / `f_bit2` both at offset 8).

Variable columns: column `j` (0-based among variable columns) occupies
`[cursor, var_end_offsets[j] & ~0x8000)` where `cursor` starts immediately
after the offset array.

**Metadata-only ADD COLUMN** (`[EMPIRICAL]`): SQL Server 2012+ allows adding a
NOT NULL column with a DEFAULT without rewriting existing rows.  Pre-DDL rows
have a shorter `fixed_end` (fixed columns) or fewer variable entries (variable
columns).  The parser returns `default_bytes` for absent columns.

**Inline MAX-type value marker (`0x21`) `[EMPIRICAL]` — G56**: For some
`max`-length column types, SQL Server prepends a single `0x21` (33) type-marker
byte to the variable-column payload in a FixedVar or CD record.  The actual
value begins at offset 1.

```
[var_col bytes]  0x21  <actual_payload>
```

Decision rules (`rows.py: read_table_rows`, `col.max_length == -1` check,
source lines ~1395–1415):

- If `cell[0] != 0x21` or `max_length != -1`: no stripping; value is raw bytes.
- `nvarchar(max)` (`type_id == 231`): strip `0x21` prefix, **unless** `len(cell) % 2 == 0`.
  An even total length means `0x21` is the first byte of a two-byte UTF-16LE character
  (e.g. U+0421 Cyrillic С) — stripping would leave an odd-length buffer.
  A genuine `0x21` prefix always yields an odd total length (1 prefix + even UTF-16LE).
- `varchar(max)` (`type_id == 167`) and `varbinary(max)` (`type_id == 165`): **only strip**
  when the table name starts with `__cs_delta_` (columnstore delta-store staging tables).
  In regular rowstore tables a leading `0x21` is genuine data (e.g. a comment starting
  with `!` in varchar(max)) and must NOT be stripped.

Census tag: `u21:strip-all` when stripped; `u21:keep-even` when the nvarchar
even-length guard fires.
Fixture: `tests/fixtures_2022/nvarchar_max_u21_full.bak`; test:
`tests/test_nvarchar_max_u21_coverage.py`.

### 3.2 Ghost record `[CORROBORATED]`

A ghost record is a deleted row retained for snapshot isolation.  It is
identified by `status_B & 0x01`.  The parser skips ghost records.

**G15 `[EMPIRICAL]`**: `status_B bit 0` = ghost-forwarded marker (confirmed by
`recordtype.py` and code inspection).  Bits 1–7 have never been observed as
non-zero across any fixture in the test matrix.  Their meaning remains
undocumented and is believed to be reserved.

### 3.3 Forwarded heap record `[CORROBORATED]`

A heap row moved to another page (due to variable-column expansion) leaves a
9-byte forwarding stub at the original slot.  The parser emits the **forwarded**
record (found at the destination slot) and skips the stub.

**G16 `[EMPIRICAL]`**: Forwarding stub is exactly 9 bytes, confirmed against
`dirtycoverage_heap_forward.bak` (SS2022):

```
[+0]  uint8   status_A  bits 1–3 = 0b010 = type FORWARDING_STUB (0x04 observed)
[+1]  uint32 LE  forwarded_page_id
[+5]  uint16 LE  forwarded_file_id  (= 1 in all observed cases)
[+7]  uint16 LE  forwarded_slot_id
```

There is no `status_B` byte in the forwarding stub; the RID occupies bytes 1–8
immediately following `status_A`.  The back-pointer in the forwarded record
(trailing after column data) is ignored by the current parser.

---

## 4. Heap / IAM enumeration `[EMPIRICAL]`

Source: `rows.py: _iter_heap_pages`, lines ~542–616.

A heap table's pages are enumerated via its IAM chain:

1. Get the `pgfirstiam` pointer from `sysallocunits` (the `AllocUnit.first_iam` field).
2. Walk the IAM page chain (following `next_page` in each IAM page header).
   For each IAM page:
   a. Read 8 SPA slots at offset 140 (`_IAM_SPA_OFFSET`), each `(file_id u16, page_id u32)`.
      Non-zero slots are individual pages from mixed extents; yield each.
   b. Read the extent bitmap at offset 194 (`_IAM_BITMAP_OFFSET`):
      each set bit at position `k` → pages `[k×8 .. k×8+7]` in the file.
   c. For each page: verify `m_type == 1` (DATA) and `obj_id == expected_obj_id`.
      Skip pages that do not match.
3. Collect all primary records from each page (see §2.8 in `01_PAGE.md`).

---

## 5. FixedVar record decoding rules `[CONFIRMED]`

Source: `records.py: decode_record` (line 69), `_record_columns` (`rows.py:80`).

**NOT-NULL trailing omission**: sysrscols `status & 0x80` marks a column as NOT NULL.
If a NOT NULL fixed column's bytes lie beyond `fixed_end` (the row is shorter
than `leaf_offset + col_size`), the column is still decoded — SQL Server pads
with zeroes for pre-DDL rows before a NOT NULL default column was added.

**Trailing column omission** (variable columns): if the variable-column count
`nvar` in the record is less than the number of variable columns in the schema,
the trailing variable columns are absent from the record.  The parser returns
`None` (NULL) for absent trailing variable columns.

**Dropped fixed columns**: if `sysrscols` has no entry for a column that
`syscolpars` declares as fixed-length, the column's bytes remain in the row
at their original offset (SQL Server does not reclaim fixed bytes on `ALTER TABLE
DROP COLUMN`).  The `_infer_dropped_col_offsets` fallback (§4.6 in `01_CATALOG.md`)
maps the gap to the dropped column so callers can skip it.

Source: `records.py:119-140`, `catalog.py: _infer_dropped_col_offsets`.

