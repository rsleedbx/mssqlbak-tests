# Rowstore Heap — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `ROWSTORE_HEAP`
**Set by:** `read_table_rows` (`mssqlbak/rows.py:860`) when `table.index_id == 0` (heap, no clustered index) and `cmprlevel == 0`
**Catalog signal:** `sysrowsets.cmprlevel == 0`, `sys.indexes.type == 0` (heap)
**Decode entry point:** `rows.py:860` → `decode_record()` → FixedVar path

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

**Inline MAX-type value marker (`0x21`) `[EMPIRICAL]` — G56**: When a
`varchar(max)`, `nvarchar(max)`, or `varbinary(max)` column stores its value
**inline** (the full value fits in the row, below the off-row threshold of roughly
8 000 bytes), SQL Server prepends a single `0x21` (33) type-marker byte to the
variable-column payload in a FixedVar or CD record.  The actual value begins at
offset 1.

```
[var_col bytes]  0x21  <actual_payload>
```

Decision rules (`rows.py: read_table_rows`, col.max_length == -1 check):

- If `cell[0] != 0x21` or `max_length != -1`: no stripping; value is the raw bytes.
- If `col.type_id == 231` (nvarchar(max)) **and** `len(cell) % 2 == 0`: **do NOT strip**.
  An even total length means `0x21` is the first byte of a two-byte UTF-16LE character
  (e.g. U+0421 Cyrillic С, U+7121 CJK 無) — stripping would leave an odd-length
  buffer that decodes as `None`.  A genuine `0x21` prefix always yields an odd total
  length (1 prefix + even-length UTF-16LE payload).
- Otherwise: strip the leading `0x21` byte.

Applies to all three MAX types (varchar/nvarchar/varbinary).
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

