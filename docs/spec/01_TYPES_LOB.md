## 5. SQL Server Type On-Disk Layouts

All layouts are little-endian unless noted.  Confirmed against
`typecoverage_full.bak` (SQL Server 2022).

| `xtype` | ID | On-disk layout |
|---------|----|----------------|
| `tinyint` | 48 | 1-byte unsigned integer |
| `smallint` | 52 | 2-byte signed LE integer |
| `int` | 56 | 4-byte signed LE integer |
| `bigint` | 127 | 8-byte signed LE integer |
| `bit` | 104 | 1 byte; bit 0 holds the value |
| `decimal`/`numeric` | 106/108 | 1 sign byte (1=positive, 0=negative) + LE integer mantissa |
| `money` | 60 | 8-byte signed LE integer in units of 10^-4 `[CONFIRMED]` |
| `smallmoney` | 122 | 4-byte signed LE integer in units of 10^-4 |
| `real` | 59 | IEEE-754 float32 LE |
| `float` | 62 | IEEE-754 float64 LE |
| `date` | 40 | 3-byte LE day count from 0001-01-01 |
| `time(n)` | 41 | `_DT2_TIME_LEN[n]` bytes LE, `n`-scaled ticks since midnight |
| `smalldatetime` | 58 | `uint16` minutes since midnight + `uint16` days since 1900-01-01 |
| `datetime` | 61 | `uint32` 1/300-s ticks since midnight + `int32` days from 1900-01-01 |
| `datetime2(n)` | 42 | `_DT2_TIME_LEN[n]` bytes LE time + 3-byte date |
| `datetimeoffset(n)` | 43 | datetime2 + `int16` offset minutes |
| `char(n)` | 175 | `n` bytes, code page from collation (§5.3); undefined bytes → `?` (U+003F) — decoded with `errors='replace'`, then U+FFFD replaced with `?` |
| `varchar(n)` | 167 | variable, same encoding and same fallback |
| `nchar(n)` | 239 | `2n` bytes UTF-16LE; **AE**: odd-length AEAD ciphertext → NULL (§3.5) |
| `nvarchar(n)` | 231 | variable, UTF-16LE; **AE**: odd-length AEAD ciphertext → NULL (§3.5) |
| `text` | 35 | 16-byte text pointer (off-row); content is cp1252 |
| `ntext` | 99 | 16-byte text pointer; content is UTF-16LE; **AE**: ciphertext in pointer slot |
| `binary(n)` | 173 | `n` bytes raw |
| `varbinary(n)` | 165 | variable raw bytes |
| `image` | 34 | 16-byte text pointer; content is raw bytes |
| `uniqueidentifier` | 36 | 16 bytes, `UUID(bytes_le=...)` — mixed-endian (`Data1` LE u32, `Data2`/`Data3` LE u16, `Data4` 8 bytes as-is); corroborated by Randolph West storage-internals series (see `CORROBORATION_SOURCES.md`). Columnstore enc=5 UUID values (status G6) reuse this same transform. |
| `rowversion`/`timestamp` | 189 | 8 opaque bytes (engine-assigned) |
| `sql_variant` | 98 | `[base_type][version=1][type metadata][value]` (§5.1) |
| `xml` | 241 | Binary XML blob (MS-BINXML) — see §5.2 |
| CLR UDT | 240 | CLR serialization bytes; subtypes dispatched on `user_type_id` — see §5.4 |
| `json` (SS2025+) | 244 (`NATIVE_JSON`) | Proprietary binary blob (`MSJSONB` format, §5.5); mssqlbak decodes it to a Python `str` (UTF-8 text). Arrow mapping: `pa.string()`. |
| `vector(N)` (SS2025+) | 165 (`varbinary` on-disk; `NATIVE_VECTOR = 255` by `user_type_id`) | On-disk: `[0xA9][0x01][dims u16-LE][reserved u32-LE = 0][float32 × N]`.  mssqlbak decodes to a JSON-array string e.g. `"[1.0000000e+000,…]"`. Arrow mapping: `pa.string()`. |

`_DT2_TIME_LEN[scale]`:

| scale | bytes |
|-------|-------|
| 0–2 | 3 |
| 3–4 | 4 |
| 5–7 | 5 |

> **`money` byte order note** `[CONFIRMED]`: documented as "high dword first"
> in some sources, but on-disk it is a plain little-endian `int64` — verified
> against the fixture.

### 5.1 `sql_variant` on-disk layout `[CORROBORATED]`

```
[+0]  uint8   base_type      (system type id)
[+1]  uint8   version = 1
[+2..]         type-specific metadata:
               fixed / uniqueidentifier  → value at +2
               decimal/numeric           → precision @+2, scale @+3, value @+4
               binary/varbinary          → 2-byte max_length, value @+4
               char/varchar/nchar/nvarchar → 5-byte collation, value @+8
               datetime2/time/datetimeoffset → scale @+2, value @+3
```

### 5.2 Binary XML (MS-BINXML) `[CORROBORATED]`

Tokenized XML format.  Signature: `0xDF 0xFF` at bytes 0–1; **version byte
at offset 2**: `0x01` (v1) or `0x02` (v2).  Details in `xmlbin.py`.  Not
reproduced here (subject to change).

### 5.3 Collation → code-page mapping `[CONFIRMED]`

Source: `types.py: _SORTID_TO_CODEC`, `_codec_for_collation`.

The SORTID (bits 7–0 of `syscolpars.collationid`) selects the Python codec.
Bit 8 (`0x100`) overrides to UTF-8 regardless of SORTID.

| SORTID | Python codec | SQL Server collation family |
|--------|-------------|----------------------------|
| `0x01` | `cp1256` | Arabic |
| `0x03` | `cp950` | Chinese_Taiwan_Stroke (Traditional Chinese / Big5) |
| `0x07` | `cp1253` | Greek |
| `0x08` | `cp1252` | Latin1_General (also the unknown-SORTID fallback) |
| `0x0C` | `cp1255` | Hebrew |
| `0x10` | `cp932` | Japanese (Shift-JIS) |
| `0x11` | `cp949` | Korean_Wansung |
| `0x13` | `cp1250` | Polish / Central European |
| `0x15` | `cp1251` | Cyrillic_General (Russian) |
| `0x19` | `cp874` | Thai |
| `0x1A` | `cp1254` | Turkish |
| `0x1F` | `cp1257` | Lithuanian / Baltic |
| `0x20` | `cp1258` | Vietnamese |
| `0x24` | `cp936` | Chinese_PRC (Simplified Chinese / GBK) |

Unknown SORTIDs fall back to `cp1252`.  The `collationid` value `0` (absent)
inherits the database-default collation read from `DBINFO.dbi_collation` at
boot-page offset 392 (`catalog.py: _DBI_COLLATION_OFF`).

### 5.4 CLR UDT subtypes `[CONFIRMED]`

Source: `types.py: UT_HIERARCHYID`, `UT_GEOMETRY`, `UT_GEOGRAPHY`,
`SUPPORTED_UDT_TYPE_IDS`.

| `user_type_id` | Name | Python return |
|----------------|------|---------------|
| 128 (`UT_HIERARCHYID`) | `hierarchyid` | opaque `bytes` (ORDPATH encoded) |
| 129 (`UT_GEOMETRY`) | `geometry` | opaque `bytes` (WKB or native binary) |
| 130 (`UT_GEOGRAPHY`) | `geography` | opaque `bytes` (WKB-like, lat/lon swapped) |

Other CLR UDT `user_type_id` values are passed through as raw `bytes`.

### 5.5 MSJSONB decoder (SS2025 native json) `[EMPIRICAL]`

Source: `types.py: decode_native_json`.

The binary JSON format begins with a 2-byte header `0x10 0x00` followed by a
4-byte sentinel `0x62 0xB4 0xF0 0xDF` and a varint-encoded entry count.
Object key names and values are encoded with 1-byte type tags followed by
varint lengths for strings and nested containers.  The decoder produces a
Python `str` (via `json.dumps`) rather than raw bytes.

Value-entry tags (selected):
- `0x00`: integer (varint)
- `0x01`: string (varint length + UTF-8 bytes)
- `0x02`: float64 LE
- `0x03`: `true`
- `0x04`: `false`
- `0x05`: `null`
- `0x40xx`: nested object (varint entry count)
- `0x80xx`: nested array (varint entry count)
- `0xC0xx`: literal (`0x00`=false, `0x01`=true, `0x02`=null, `0x04`={}, `0x06`=[])

---

## 6. LOB / Off-Row Structures

There are **three distinct off-row pointer structures** in the LOB path.
Source:
`rows.py: _stitch_lob`, `_read_lob_node`,
`_BLOB_ROOT_HDR = 12`, `_BLOB_LINK_SIZE = 12`, `_BLOB_HDR = 14`, `_RID`;
parallel reader in `catalog.py: _follow_lob` / `_read_lob_node_c`.

> **Implementation note (`nlinks` field)**: `rows.py: _read_lob_node` derives
> `nlinks` from the record length: `nlinks = (len(inline) - 12) // 12` (no
> stored count).  `catalog.py: _read_lob_node_c` reads `nlinks` as a `uint32`
> at byte 16 of the inline-root.  When both paths walk the same LOB the counts
> agree for all tested fixtures, but the derivation method differs.  G31 leaves
> this open pending a DBCC verifier that explicitly prints the inline-root link
> count.

### 6.0 ROW_OVERFLOW pointer (struct_type = 2) `[EMPIRICAL]`

Source: `rows.py: _ROW_OVERFLOW_TYPE = 2`, `_ROW_OVERFLOW_PTR_SIZE = 24`.

When a fixed-width or narrow variable-width column is pushed off-row by SQL
Server's row overflow mechanism (columns that push the row past 8060 bytes), a
24-byte inline pointer replaces the value bytes in the variable column slot:

```
[+0:2]  u16 LE  struct_type = 2   (distinguishes ROW_OVERFLOW from _BLOB_INLINE_ROOT=4)
[+2:4]  u16 LE  level = 0
[+4:6]  u16 LE  file_id            database file containing the overflow page
[+6:8]  u16 LE  slot               slot index on the overflow page
[+8:12] u32     internal tracking  (not used for decode)
[+12:16] u32 LE data_len           byte length of the column value on the overflow page
[+16:20] u32 LE page_id            page number within file_id
[+20:24] u32    reserved
```

The overflow page is a `LOB_DATA` page (m_type 3 or 4); slot `slot` on page
`(file_id, page_id)` holds the column bytes directly.  The parser reads the
inline 24-byte block at `struct_type == 2` before checking for `struct_type == 4`
(the normal LOB inline-root path).

### 6.1 In-row inline root (the LOB pointer inside the data row) `[CORROBORATED]`

When a `varchar(max)`, `varbinary(max)`, or `xml` column is stored off-row, the
in-row variable-column bytes are an inline-root pointer:

```
[+0]   uint16 LE  struct_type = 4   (_BLOB_INLINE_ROOT)
[+2 .. +12]  10-byte header  [EMPIRICAL — bytes 2–11 observed as two u32 fields
                              followed by two u16 fields; semantics not confirmed
                              against DBCC PAGE verifier; parser skips this region]
[+12 ..]  link array: nlinks = (len - 12) // 12 entries, each 12 bytes:
              [+0]  uint32 LE  cumulative_length
              [+4]  uint32 LE  page_id  ┐ RID, read as _RID = "<IHH"
              [+8]  uint16 LE  file_id  │ at link offset +4
              [+10] uint16 LE  slot     ┘
```

The code reads only `struct_type` (offset 0) and, per link, the `cumulative_length`
plus the RID at link-offset +4.  `nlinks` is **derived** from the record length,
not read from a stored count.

**G30 `[EMPIRICAL]`**: The link layout (12 bytes per link, cumulative_length at
+0, RID at +4) round-trips correctly for all LOB fixtures tested.  The 10-byte
header between `struct_type` and the link array is skipped; its field semantics
are empirically consistent but have not been verified against a DBCC PAGE dump.

### 6.2 On-page LOB record (m_type 3/4) `[CORROBORATED]`

Each LOB allocation-unit page holds slotted records with this header:

```
Common header (all btyp values):
[+0]   uint8   status_A   (always 0x08 in observed records)
[+1]   uint8   unknown
[+2]   uint16 LE  record_length  total record length in page (_BLOB_LEN_OFF)
[+4]   uint32     blob_id_low    (part of internal blob identity; not parsed)
[+8]   uint32     unknown
[+12]  uint16 LE  btyp           structure discriminator (_BLOB_TYPE_OFF):
                                  3 = DATA   (_BLOB_DATA)
                                  2 = LARGE_ROOT (_BLOB_LARGE_ROOT)
                                  5 = ROOT   (_BLOB_ROOT) — inline-root chain anchor
[+14 ..]  type-specific payload
```

**btyp = 3 (DATA)** — SQL Server name: `DATA`
```
[+14 ..]  raw fragment bytes  (record_length - 14 bytes of payload)
```

**btyp = 2 (LARGE_ROOT)** — SQL Server name: `INTERNAL`; intermediate indirection node for multi-MB objects
```
[+14]  uint16 LE  max_links    maximum child-link slots pre-allocated (SQL: MaxLinks)
                               observed: 0x0002 = 2-slot node, 0x0004 = 4-slot node
[+16]  uint16 LE  cur_links    actual number of child links present (SQL: CurLinks)
[+18]  uint16 LE  level        B-tree depth — 0 = leaf INTERNAL, 1 = one level above, …
[+20 ..]  links, cur_links × 16 bytes each:
              [+0]  uint64 LE  cumulative_end_offset  (exclusive byte end)
              [+8]  uint32 LE  child_page_id          ┐ RID of child LOB record
              [+12] uint16 LE  child_file_id          │ (btyp=3 DATA or another
              [+14] uint16 LE  child_slot_id          ┘  btyp=2 LARGE_ROOT)
```

**btyp = 5 (ROOT)** — SQL Server name: `LARGE_ROOT_YUKON`; top-level anchor referenced by in-row inline-root pointer
```
[+14]  uint16 LE  max_links    maximum slot count = 5 (always 5 per DBCC PAGE output)
[+16]  uint16 LE  cur_links    number of fragment links in use
[+18]  uint16 LE  level        always 0 for ROOT (single-level root)
[+20]  uint32     padding = 0
[+24 ..]  fragments, max_links × 12 bytes pre-allocated (only cur_links are valid):
              [+0]  uint32 LE  fragment_end_offset  (cumulative, exclusive)
              [+4]  uint32 LE  page_id  ┐ RID of btyp=3 DATA record
              [+8]  uint16 LE  file_id  │
              [+10] uint16 LE  slot_id  ┘
```

> **SQL Server naming note:** DBCC PAGE labels these record types as `3 (DATA)`,
> `2 (INTERNAL)`, and `5 (LARGE_ROOT_YUKON)`.  The spec uses the names DATA,
> LARGE_ROOT, and ROOT internally; the SQL Server names are noted above for
> cross-referencing DBCC output.

A DATA record returns `rec[14:]`.  A ROOT record concatenates its fragment
DATA payloads in order.  A LARGE_ROOT record recurses through its links to
concatenate the full value (each link may itself be DATA or another LARGE_ROOT).

**G31 `[CORROBORATED]`**: Full btyp=2 and btyp=5 layouts confirmed from
`cs_lob_preamble2.bak` (SS2022) by tracing multi-level LOB chains from ROOT →
LARGE_ROOT → DATA.  Sub-header fields (`max_links`, `cur_links`, `level`)
corroborated by Kazamiya forensicist blog and Korotkevitch `aboutsqlserver.com`
LOB storage article (see CORROBORATION_SOURCES.md §6.2); DBCC PAGE output labels
them `MaxLinks`, `CurLinks`, `Level` in printed results.  Confirmed that btyp=5
(ROOT / LARGE_ROOT_YUKON) always has `MaxLinks = 5`; btyp=2 (LARGE_ROOT /
INTERNAL) has `MaxLinks = 2 or 4` depending on the node.
**Parser fix (2026-06-17):** the parser formerly read `cur_links` as part of a
`uint32` at +16, which was equivalent when `level = 0` (all tested fixtures) but
would have produced a wrong link count (`CurLinks + 65536`) for a `level = 1`
INTERNAL node (3-level LOB tree, required for LOB > ~8 MB spanning > 5 INTERNAL
children).  Now reads `uint16` at +16 explicitly.  The 4-byte padding in btyp=5
(`[+20..+23]`) and the upper 32 bits of `cumulative_end_offset` in btyp=2 have
never been non-zero, so those semantics remain unverified.

### 6.3 Legacy text pointer (text/ntext/image) `[CORROBORATED]`

Legacy large-value columns store a 16-byte text pointer in the FixedVar record:

```
[+0]   uint32 LE  timestamp   (internal BLOB sequence / uniquifier; not interpreted)
[+4]   uint32     padding = 0  (always zero in all observed records)
[+8]   uint32 LE  page_id     ┐ RID of the root text-tree LOB record
[+12]  uint16 LE  file_id     │
[+14]  uint16 LE  slot_id     ┘
```

Text-tree node types (`rows.py`): `0`=`_TEXT_SMALL_ROOT`, `2`=`_TEXT_INTERNODE`,
`3`=`_TEXT_DATA`, `5`=`_TEXT_LARGE_ROOT` (same btyp=5 layout as §6.2).

**btyp = 0 (SMALL_ROOT)** — entire value fits in the page slot.
```
body[0:2]  u16 LE  data_len     length of inline data
body[2:6]          unknown      (4 bytes; skipped by parser)
body[6:]           data bytes   data_len bytes of raw content
```
Source: `rows.py: _TEXT_SMALL_ROOT`, `_TEXT_SMALL_DATA_OFF = 6`.

**btyp = 2 (INTERNODE)** — B-tree interior node for very large objects.
Each interior node holds 16-byte links to child nodes (which may be DATA,
LARGE_ROOT, or further INTERNODE nodes).
```
body[0:2]  u16 LE  unknown
body[2:4]  u16 LE  nlinks       number of child links
body[4:6]          unknown
body[6 ..]         nlinks × 16-byte links:
    [+0]  u64 LE  cumulative_end_offset  (exclusive byte end of this child's span)
    [+8]  u32 LE  child_page_id
    [+12] u16 LE  child_file_id
    [+14] u16 LE  child_slot_id
```
Source: `rows.py: _TEXT_INTERNODE = 2`, `_TEXT_ILINK`, `_TEXT_ILINK_OFF = 6`.

**G32 `[EMPIRICAL]`**: Confirmed against `legacytext.bak` (SS2022).  The data
page for the `legacy_lob` heap table was found with DBCC IND; DBCC PAGE
(style=3) printed each row's 16-byte text pointer slot.  Bytes 8–15 match the
RID of the LOB root record returned by the DBCC PAGE output.  Bytes 0–3 are a
monotonically-increasing integer per row (timestamp/uniquifier); bytes 4–7 were
`00 00 00 00` in all rows.  Verified for `text`, `ntext`, and `image` column
types simultaneously.

---

