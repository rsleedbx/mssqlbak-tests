# Approximate Numeric Types — `real`, `float`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | Fixed width | SQL Server version |
|---|---|---|---|
| `real` | 59 | 4 bytes | All |
| `float` | 62 | 8 bytes | All |

`real` is equivalent to `float(24)` (single precision); `float` with no argument or `float(25..53)` is double precision. Both are stored in the fixed-data region of the row.

---

## 2. Binary layout — uncompressed rowstore

### `real` (xtype 59)

```
[+0:4]  IEEE-754 single-precision float (binary32), little-endian
```

Source: `scalars.py: _decode_real` — `struct.Struct("<f").unpack(raw[:4])[0]`

### `float` (xtype 62)

```
[+0:8]  IEEE-754 double-precision float (binary64), little-endian
```

Source: `scalars.py: _decode_float` — `struct.Struct("<d").unpack(raw[:8])[0]`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

Both `real` and `float` are stored as their ordinary little-endian bytes with **leading** zero bytes (LSB-side) stripped — the opposite of the temporal trimming direction. The decoder prepends zero bytes to restore the natural width before applying the IEEE-754 struct unpack.

> **Note on direction**: temporal types (date, time, datetime2, datetimeoffset) trim **trailing** (high-order) zero bytes. Float and `smalldatetime` trim **leading** (low-order) zero bytes. This is consistent because floats are not meaningful as integers and the padding zeros lie on the least-significant byte side.

Source: `rowcompress.py: decode_compressed_value`; spec `04_ROWSTORE_COMPRESSED.md §Float / smalldatetime encoding`

### Columnstore segment (`enc=1–6`)

Float/real values appear in columnstore segments with `enc=3` (dictionary) or `enc=5` (stored as raw bytes in the enc=5 payload). Double-precision values in dictionary encoding are stored as 8-byte LE IEEE-754 values.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`, `07_COLUMNSTORE_ARCHIVE.md`

Columnstore delta-store rows use the uncompressed B-tree row format — no difference from §2.

### XTP checkpoint

Same per-value IEEE-754 LE encoding as uncompressed rowstore. Record alignment padding applies at the record level, not within the float bytes themselves.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

| SQL Server type | Python value |
|---|---|
| `real` | `float` (Python 64-bit float; the 32-bit source value is widened by IEEE-754 promotion) |
| `float` | `float` (64-bit) |

Python's `float` is always 64-bit (IEEE-754 binary64). Unpacking a `float32` via `struct.Struct("<f")` promotes it to 64-bit Python float — this is exact (every 32-bit float is representable as 64-bit float), though it may add trailing precision digits in string representations.

Source: `scalars.py: _decode_real`, `_decode_float`, `_F32`, `_F64`

---

## 5. PyArrow output

| SQL Server type | Arrow type | Notes |
|---|---|---|
| `real` | `pa.float32()` | Stored as 32-bit in Arrow to preserve the original precision boundary |
| `float` | `pa.float64()` | Natural 64-bit |

Arrow `float32` is used for `real` specifically so that the Arrow schema reflects the SQL Server column's actual precision. The Python decode produces a 64-bit float but the Arrow builder accepts it and rounds to the nearest float32.

Source: `arrow.py: arrow_type`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap; no value bytes are read.
- **NaN / ±Inf**: SQL Server does not store NaN or infinity in user columns (`CHECK` constraints prevent it), but the decoder does not explicitly guard against them — they would round-trip as Python `float('nan')` / `float('inf')` if somehow present in a corrupt or legacy backup.
- **`sql_variant` base type**: Both `real` and `float` can appear inside a `sql_variant`. In that context the decoder reads the standard 4- or 8-byte IEEE-754 value beginning at offset 2 (see `13_sql_variant.md`).
- **`float(n)` notation**: `float(1..24)` → `real` (xtype 59, 4 bytes); `float(25..53)` and bare `float` → xtype 62 (8 bytes). This disambiguation happens at column-definition time; the on-disk xtype is the discriminator.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constants | `scalars.py: REAL=59, FLOAT=62` |
| Decode functions | `scalars.py: _decode_real`, `_decode_float`, `_F32 = struct.Struct("<f")`, `_F64 = struct.Struct("<d")` |
| Arrow mapping | `arrow.py: arrow_type` |
| ROW/PAGE leading-zero strip | `rowcompress.py: decode_compressed_value`; `04_ROWSTORE_COMPRESSED.md §Float / smalldatetime encoding` |

---

## 8. Confidence

`[CONFIRMED]` — both types verified against `typecoverage_full.bak` (SQL Server 2022). Leading-zero compression path is `[EMPIRICAL]` — confirmed by round-trip of `cmp_row.r` and `cmp_page.f` columns in `compressioncoverage_full.bak`.
