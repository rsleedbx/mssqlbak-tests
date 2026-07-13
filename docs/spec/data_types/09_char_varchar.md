# Single-Byte String Types — `char`, `varchar`, `varchar(max)`, `text`, `sysname`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | Storage class | SQL Server version |
|---|---|---|---|
| `char(n)` | 175 | Fixed-length, in-row | All |
| `varchar(n)` | 167 | Variable-length, in-row | All |
| `varchar(max)` | 167 | Variable-length, off-row LOB (`max_length = -1`) | 2005+ |
| `text` | 35 | Legacy LOB (16-byte text pointer) | All (deprecated) |
| `sysname` | 231 | **nvarchar(128) alias** — xtype 231, `max_length = 256` | All |

> **`sysname` note**: Although listed here under single-byte strings for completeness (T-SQL groups it with character types), `sysname` has `system_type_id = 231` — the same as `nvarchar` — and is decoded as UTF-16-LE. See [`10_nchar_nvarchar.md`](10_nchar_nvarchar.md) for the full decode path.

---

## 2. Binary layout — uncompressed rowstore

### `char(n)` (xtype 175)

```
[+0:n]  n bytes, encoded with the column's code page (from collation)
```

Fixed-width; occupies exactly `n` bytes in the fixed-data region of the row. Trailing space padding is included in the stored bytes (SQL Server right-pads `char` to the declared length).

### `varchar(n)` (xtype 167)

```
[variable-length slot]  k bytes, encoded with the column's code page
```

Stored in the variable-length region of the row. `k` can be 0 to `n` (up to 8000). The actual byte count is determined by the row's variable-length offset array.

### `varchar(max)` (xtype 167, `max_length = -1`)

When `max_length == -1`, the variable slot holds a **LOB pointer** rather than the value directly:

- Short values (≤ 8000 bytes): may be stored in-row as a regular variable slot.
- Long values: stored off-row via an inline-root pointer (struct_type = 4) or ROW_OVERFLOW pointer (struct_type = 2).

See `01_TYPES_LOB.md §6` for the full off-row pointer structure.

### `text` (xtype 35)

```
[+0:16]  16-byte text pointer:
    [+0:4]   uint32 LE  timestamp/uniquifier
    [+4:8]   uint32     padding = 0
    [+8:12]  uint32 LE  page_id (root LOB record)
    [+12:14] uint16 LE  file_id
    [+14:16] uint16 LE  slot_id
```

The value is stored off-row in a text B-tree. The decoder follows the pointer to reconstruct the full byte content (see `01_TYPES_LOB.md §6.3`). Encoding is cp1252 (or the database-default single-byte code page).

---

## 3. Collation → code-page mapping

The Python codec for decoding is determined by `syscolpars.collationid`:

| Field | Bits | Meaning |
|---|---|---|
| UTF-8 flag | bit 8 (`0x100`) | Set → codec is `"utf-8"` regardless of SORTID |
| SORTID | bits 7–0 | Maps to a Windows code page |

**SORTID → codec table** (source: `scalars.py: _SORTID_TO_CODEC`):

| SORTID | Codec | SQL Server collation family |
|---|---|---|
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

Unknown SORTIDs fall back to `cp1252`. The `collationid = 0` (absent) inherits the database-default collation from `DBINFO.dbi_collation`.

Source: `scalars.py: _SORTID_TO_CODEC`, `_codec_for_collation`

---

## 4. Decoding and error handling

```python
def _decode_char(raw: bytes, *, encoding: str = "cp1252") -> str:
    try:
        return raw.decode(encoding)
    except (UnicodeDecodeError, ValueError):
        return raw.decode(encoding, errors="replace").replace("\ufffd", "?")
```

SQL Server maps bytes undefined in the column's code page to literal `?` (U+003F), not the Unicode replacement character U+FFFD. mssqlbak matches this behaviour: Python's `errors="replace"` produces U+FFFD, which is then replaced with `?`.

**G54 edge case** `[EMPIRICAL]`: cp1252 has 5 undefined byte values (`0x81`, `0x8D`, `0x8F`, `0x90`, `0x9D`). Observed in `dba.stackexchange.com.bak` `PostHistory.Text` (byte `0x8F` at position 1191). The `errors='replace'` path substitutes `?` and the row is extracted.

Source: `scalars.py: _decode_char`

---

## 5. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`char` and `varchar` values are stored **as-is** (no special reencoding) in the CD record's data region. The code-page bytes are preserved verbatim — only length trimming may apply (trailing space bytes from `char` padding may be stripped).

> Unlike `nchar`/`nvarchar` (which become SCSU under compression), single-byte char types do not change encoding.

Source: `04_ROWSTORE_COMPRESSED.md §3.5`

### Columnstore segment (`enc=1–6`)

String values are dictionary-encoded. The dictionary maps integer codes to byte strings using the column's code page. On decode, the byte strings are decoded to Python `str` via `_decode_char`.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md §VC05`

### XTP checkpoint

Same per-value byte encoding as uncompressed rowstore. The `char`/`varchar` bytes are stored verbatim in the XTP row's variable section.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 6. Always Encrypted (AE)

For `char`/`varchar` columns protected by Always Encrypted, the raw bytes are AEAD_AES_256_CBC_HMAC_SHA_256 ciphertext. Unlike `nchar`/`nvarchar` (where AE is detected by odd byte length), AE detection for single-byte strings relies on column metadata (`col.is_encrypted`). Without the Column Encryption Key (CEK), the column is excluded from extraction by `column_supported()`.

---

## 7. Python intermediate

`str` — the decoded Python string. `None` if the value is NULL (NULL bitmap) or the column is AE-encrypted.

Source: `scalars.py: _decode_char`

---

## 8. PyArrow output

`pa.string()` — UTF-8 encoded Arrow string for all of `char`, `varchar`, `varchar(max)`, `text`.

Source: `arrow.py: arrow_type` — `pa.string()` for `CHAR`, `VARCHAR`, `TEXT`

---

## 9. Edge cases

- **NULL**: Encoded via the row's NULL bitmap for in-row types. For `text`, a NULL is indicated in the text-pointer slot.
- **`char` trailing spaces**: SQL Server pads `char(n)` values with spaces to the declared length. The spaces are decoded as-is — mssqlbak does not strip them.
- **Code page 0 / missing collation**: When `collationid = 0`, `_codec_for_collation` falls back to `cp1252` (the server default). For databases with a non-Latin1 default collation, this may misrender non-ASCII bytes; a low-confidence signal is raised.
- **`varchar(max)` inline vs off-row**: When the content fits in the in-row slot, it is decoded directly. When the LOB pointer path is followed, the full byte content is assembled from LOB pages and then decoded with `_decode_char`.
- **`sql_variant` base type**: `char` and `varchar` can appear inside `sql_variant`. The collation block occupies 5 bytes at offsets 3–7; the value starts at offset 8.

---

## 10. Source references

| Claim | Source |
|---|---|
| xtype constants | `scalars.py: CHAR=175, VARCHAR=167, TEXT=35` |
| Collation bit layout | `scalars.py: _codec_for_collation` docstring; `_COLLATION_UTF8_FLAG = 0x100` |
| SORTID table | `scalars.py: _SORTID_TO_CODEC` |
| Decode function | `scalars.py: _decode_char` |
| cp1252 undefined bytes (G54) | `00_MASTER.md §G54` |
| LOB pointer layout | `01_TYPES_LOB.md §6.3` |
| Arrow mapping | `arrow.py: arrow_type` |

---

## 11. Confidence

`[CONFIRMED]` — `char`, `varchar` verified against `typecoverage_full.bak`. Code-page mapping `[CONFIRMED]` via `unicode_codepage_coverage.bak` (all 14 non-default code pages). `varchar(max)` LOB path is `[CORROBORATED]` (see `01_TYPES_LOB.md §6`). `text` LOB pointer is `[EMPIRICAL]` — G32.
