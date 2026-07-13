# Integer Types — `tinyint`, `smallint`, `int`, `bigint`, `bit`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | Fixed width | SQL Server version |
|---|---|---|---|
| `tinyint` | 48 | 1 byte | All |
| `smallint` | 52 | 2 bytes | All |
| `int` | 56 | 4 bytes | All |
| `bigint` | 127 | 8 bytes | All |
| `bit` | 104 | 1 byte (packed, shares byte with adjacent bit columns) | All |

---

## 2. Binary layout — uncompressed rowstore

All integer types are fixed-width values stored in the fixed-data region of the heap/B-tree row.

### `tinyint` (xtype 48)

```
[+0]  uint8   value (0..255, unsigned)
```

Source: `scalars.py: _decode_int(raw, signed=False)` — `int.from_bytes(raw, "little", signed=False)`

### `smallint` (xtype 52)

```
[+0:2]  int16 LE   value (-32768..32767, signed)
```

Source: `scalars.py: _decode_int(raw, signed=True)`

### `int` (xtype 56)

```
[+0:4]  int32 LE   value (-2147483648..2147483647, signed)
```

Source: `scalars.py: _decode_int(raw, signed=True)`

### `bigint` (xtype 127)

```
[+0:8]  int64 LE   value, signed
```

Source: `scalars.py: _decode_int(raw, signed=True)`

### `bit` (xtype 104)

```
[+0]    uint8   byte shared with adjacent bit columns
        bit 0   this column's boolean value (0 or 1)
```

SQL Server packs multiple `bit` columns from the same row into a single byte, one bit per column (lowest bit = first `bit` column in the fixed region). The shift amount is tracked via `col.leaf_offset` (which byte) and the bit position within that byte.

Source: `scalars.py: _decode_bit(raw, shift=0)` — `bool((raw[0] >> shift) & 1)`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

Fixed-width integers use **excess-encoded big-endian minimal-width** representation in the CD record's short- or long-data region:

```
value_stored = int.from_bytes(data, "big") - 2^(8*len(data) - 1)
```

Trailing zero bytes are stripped (`_CD_ZERO` → value 0; empty entry means zero). The decoder right-pads to the type's natural width then interprets as big-endian excess-encoded.

Applies to: `smallint`, `int`, `bigint`. `tinyint` is unsigned and uses the same mechanism with a 1-byte natural width. `bit` uses a NULL-bitmap slot (0/1 stored as a CD flag; no separate data bytes for a non-NULL bit column).

Source: `rowcompress.py: decode_compressed_value`; spec `04_ROWSTORE_COMPRESSED.md §3.5 Integer encoding`

### Columnstore segment (`enc=1–6`)

All integer types are stored as column vectors. Typical encodings:

- `enc=1/2`: RLE or bitpacked with a bias offset; `tinyint`/`smallint`/`int`/`bigint` values are encoded in the natural integer domain.
- `enc=3`: dictionary reference.
- `bit` is stored as a `tinyint` (0/1) in the columnstore path.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`, `07_COLUMNSTORE_ARCHIVE.md`

Columnstore delta-store rows use the uncompressed B-tree row format — no difference from §2.

Cross-reference: `05_COLUMNSTORE_DELTA.md`

### XTP checkpoint (memory-optimized tables)

Same per-value LE integer encoding as uncompressed rowstore (§2). The record framing differs: fixed columns are packed widest-slot-first with alignment padding (see `08_XTP_CHECKPOINT.md §V04a`). No change to the integer byte layout itself.

---

## 4. Python intermediate

| SQL Server type | Python value |
|---|---|
| `tinyint` | `int` (0..255) |
| `smallint` | `int` (signed) |
| `int` | `int` (signed) |
| `bigint` | `int` (signed) |
| `bit` | `bool` (`True`/`False`) |

Source: `scalars.py: _decode_int`, `_decode_bit`

---

## 5. PyArrow output

| SQL Server type | Arrow type | Reason |
|---|---|---|
| `tinyint` | `pa.int16()` | Widened from 1-byte unsigned (0..255) to signed int16 so the maximum value 255 round-trips through Delta Lake, which has no unsigned integer type `[CONFIRMED]` |
| `smallint` | `pa.int16()` | Natural signed 16-bit |
| `int` | `pa.int32()` | Natural signed 32-bit |
| `bigint` | `pa.int64()` | Natural signed 64-bit |
| `bit` | `pa.int8()` | **Not `pa.bool_()`** — delta-rs has a bug where bit-packed boolean columns cause `decimal128` parse-overflow errors when large-precision decimals appear in the same `RecordBatch`; `int8` (0/1) is used as a safe workaround `[CONFIRMED]` |

Source: `arrow.py: arrow_type`

---

## 6. Edge cases

- **NULL**: SQL Server encodes NULL via the row's NULL bitmap (one bit per nullable column); the decoder returns `None` without reading any value bytes.
- **Bit packing**: Multiple consecutive `bit` columns share a byte. `col.leaf_offset` gives the byte; the bit position within the byte is derived from the column ordering. Decoding a single `bit` column from a multi-bit byte requires masking at the correct shift.
- **`tinyint` vs unsigned**: mssqlbak decodes `tinyint` as a Python `int` (0..255) and emits `int16` in Arrow. Downstream systems that expect unsigned semantics should note this widening.
- **Always Encrypted**: integer columns may be AE-encrypted. The raw bytes do not match the type's natural width; `column_supported()` marks AE columns as unsupported and they are excluded from extraction.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constants | `scalars.py: TINYINT=48, SMALLINT=52, INT=56, BIGINT=127, BIT=104` |
| Decode functions | `scalars.py: _decode_int`, `_decode_bit` |
| Arrow mapping | `arrow.py: arrow_type` |
| Bit workaround comment | `arrow.py: arrow_type` (BIT branch) |
| ROW/PAGE compression | `rowcompress.py: decode_compressed_value`; `04_ROWSTORE_COMPRESSED.md §Integer encoding` |

---

## 8. Confidence

`[CONFIRMED]` — all five types verified against `typecoverage_full.bak` (SQL Server 2022). Arrow widening for `tinyint` and `int8` workaround for `bit` are confirmed by Delta sink round-trip tests.
