# Unicode String Types — `nchar`, `nvarchar`, `nvarchar(max)`, `ntext`, `sysname`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | `max_length` | Storage class | SQL Server version |
|---|---|---|---|---|
| `nchar(n)` | 239 | 2n | Fixed-length, in-row | All |
| `nvarchar(n)` | 231 | 2n | Variable-length, in-row | All |
| `nvarchar(max)` | 231 | -1 | Variable-length, off-row LOB | 2005+ |
| `ntext` | 99 | — | Legacy LOB (16-byte text pointer) | All (deprecated) |
| `sysname` | 231 | 256 | nvarchar(128) alias — xtype 231 | All |

> **`sysname`**: A system-defined alias type for `nvarchar(128)`. It appears in `sys.types` as a separate named type but shares `system_type_id = 231` and `max_length = 256` (128 UTF-16 code units × 2 bytes). The mssqlbak parser decodes it identically to `nvarchar(128)` — no special-case required.

---

## 2. Binary layout — uncompressed rowstore

All Unicode types store data as **UTF-16-LE** (two bytes per BMP code unit; surrogate pairs for supplementary characters).

### `nchar(n)` (xtype 239)

```
[+0:2n]  2n bytes, UTF-16-LE
```

Fixed-width; `n` UTF-16 code units = `2n` bytes. Right-padded with `U+0020` (space) in UTF-16-LE (`0x20 0x00`) to the declared width.

### `nvarchar(n)` / `sysname` (xtype 231)

```
[variable-length slot]  k bytes, UTF-16-LE  (k is even, 0 ≤ k ≤ 2n)
```

Stored in the variable-length region. `sysname` has `n = 128` (`max_length = 256`).

### `nvarchar(max)` (xtype 231, `max_length = -1`)

When `max_length == -1`, the variable slot holds an off-row LOB pointer (inline-root or ROW_OVERFLOW). The assembled byte content is then decoded as UTF-16-LE.

See `01_TYPES_LOB.md §6` for the LOB pointer structure.

### `ntext` (xtype 99)

```
[+0:16]  16-byte text pointer (same layout as text; see 09_char_varchar.md §2)
```

Content assembled from the text B-tree is decoded as UTF-16-LE.

---

## 3. Decoding

```python
def _decode_nchar(raw: bytes) -> str | None:
    if len(raw) % 2 != 0:
        return None   # AE ciphertext (see §Always Encrypted below)
    try:
        return raw.decode("utf-16-le")
    except (UnicodeDecodeError, ValueError):
        return None
```

Source: `scalars.py: _decode_nchar`

---

## 4. Always Encrypted (AE) detection

AE ciphertext for `nchar`/`nvarchar` columns has the format:

```
[+0]      0x01   version byte
[+1:33]   32-byte HMAC-SHA-256 authentication tag
[+33:49]  16-byte AES-CBC IV
[+49+]    ciphertext (padded to AES block size = 16 bytes)
```

Total length = 1 + 32 + 16 + N×16 = **always odd** (49 + even = odd).

Valid UTF-16-LE data always has even byte length (every code unit is exactly 2 bytes). An **odd byte count** is therefore a definitive AE indicator — the decoder returns `None` without attempting to decode.

Source: `scalars.py: _decode_nchar` (docstring, `_AE_VERSION_BYTE = 0x01`)

---

## 5. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`nchar`, `nvarchar`, and `sysname` are **NOT stored as UTF-16-LE** under ROW/PAGE compression. SQL Server applies **SCSU** (Unicode Standard Compression Scheme for Unicode, UTS #6) on a per-value basis within the CD record.

Key SCSU mechanisms observed in SQL Server output (see `04_ROWSTORE_COMPRESSED.md §4.2` for full table):

| Mechanism | Byte(s) | Effect |
|---|---|---|
| Window 0 passthrough | `0x00–0x7F` | ASCII code point = byte |
| `SD0–SD7` | `0x18–0x1F` + offset | Define and select a dynamic window |
| `SCU` | `0x0F` | Enter Unicode mode (big-endian UTF-16 pairs) |
| `UC0–UC7` | `0xE0–0xE7` | Return to single-byte mode |
| `SQU` | `0x0E` + 2 bytes | Quote one Unicode char in single-byte mode |

SQL Server also appends a **trailer byte** (commonly `0x10` = SC0 no-op) after SCSU-encoded values. The decoder ignores lone trailing bytes that cannot complete a multi-byte opcode.

Source: `rowcompress.py: _decode_scsu`; spec `04_ROWSTORE_COMPRESSED.md §3.5 nchar/nvarchar encoding`, `§4.2`

### Columnstore segment (`enc=1–6`)

String values are dictionary-encoded. Dictionary strings for `nvarchar`/`nchar` columns are stored as UTF-16-LE in the dictionary blob (with `unicode_first=True` decode ordering).

Cross-reference: `06_COLUMNSTORE_SEGMENT.md §VC05`

### XTP checkpoint

Same UTF-16-LE encoding as uncompressed rowstore. The `nchar`/`nvarchar` bytes are stored verbatim in the XTP row's variable section.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 6. Python intermediate

`str` — the decoded Python string. `None` if NULL, AE-encrypted, or an invalid UTF-16-LE sequence.

Source: `scalars.py: _decode_nchar`

---

## 7. PyArrow output

`pa.string()` — UTF-8 encoded Arrow string for all of `nchar`, `nvarchar`, `nvarchar(max)`, `ntext`, `sysname`.

Source: `arrow.py: arrow_type` — `pa.string()` for `NCHAR`, `NVARCHAR`, `NTEXT`

---

## 8. Edge cases

- **NULL**: Encoded via the row's NULL bitmap for in-row types. For `ntext`, NULL is indicated in the text-pointer slot.
- **Surrogate pairs**: Valid UTF-16-LE surrogate pairs (for supplementary characters > U+FFFF) are decoded correctly by Python's `utf-16-le` codec.
- **Lone surrogates**: A lone high or low surrogate as the last code unit raises `UnicodeDecodeError`; `_decode_nchar` catches it and returns `None`.
- **`nchar` trailing spaces**: SQL Server pads `nchar(n)` with `U+0020` (space) code units to the declared length. The spaces are decoded as-is.
- **`nvarchar(max)` inline vs off-row**: Same path as `varchar(max)` — LOB pointer assembled, then decoded as UTF-16-LE.
- **`sql_variant` base type**: `nchar` and `nvarchar` can appear inside `sql_variant`. The collation occupies 5 bytes at offsets 3–7; the UTF-16-LE value starts at offset 8.
- **SCSU astral characters** `[EMPIRICAL]`: Extended-window instructions (`SDX`, `UDX`) access Plane 1+ code points. Surrogate pairs are produced for values above U+FFFF. Confirmed by unit tests with Linear B Syllable U+10000 and emoji `U+1F600` (😀).

---

## 9. Source references

| Claim | Source |
|---|---|
| xtype constants | `scalars.py: NCHAR=239, NVARCHAR=231, NTEXT=99` |
| sysname alias | `sys.types` — xtype 231, max_length 256 |
| AE detection | `scalars.py: _decode_nchar` docstring, `_AE_VERSION_BYTE = 0x01` |
| Decode function | `scalars.py: _decode_nchar` |
| SCSU spec | `04_ROWSTORE_COMPRESSED.md §3.5`, `§4.2` |
| Columnstore dict order | `06_COLUMNSTORE_SEGMENT.md §VC05` |
| Arrow mapping | `arrow.py: arrow_type` |
| LOB pointer | `01_TYPES_LOB.md §6.3` |

---

## 10. Confidence

`[CONFIRMED]` — `nchar`, `nvarchar` verified against `typecoverage_full.bak`. AE detection `[CONFIRMED]` (odd-length invariant mathematically guaranteed). SCSU compression path `[EMPIRICAL]` — G17/G18 (`compressioncoverage_full.bak`) and `unicode_codepage_coverage.bak` CJK/Arabic. `ntext` LOB path `[EMPIRICAL]` — G32.
