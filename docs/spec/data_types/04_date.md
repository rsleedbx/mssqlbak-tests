# Date Type — `date`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | Fixed width | SQL Server version |
|---|---|---|---|
| `date` | 40 | 3 bytes | 2008+ |

`date` stores a calendar date with no time component, ranging from 0001-01-01 to 9999-12-31.

---

## 2. Binary layout — uncompressed rowstore

```
[+0:3]  uint24 LE   day count from epoch 0001-01-01 (inclusive)
```

Epoch is `datetime.date(1, 1, 1)` (the Python minimum date, equivalent to 0001-01-01 in the proleptic Gregorian calendar).

```
value = datetime.date(1, 1, 1) + datetime.timedelta(days=day_count)
```

Source: `scalars.py: _decode_date`, `_DATE_EPOCH = dt.date(1, 1, 1)`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`date` is stored as its ordinary 3-byte little-endian bytes with **trailing** (high-order) zero bytes stripped — the same trimming direction as all 2008+ temporal types. The decoder right-pads with zero bytes to restore the 3-byte width before calling `_decode_date`.

Source: `rowcompress.py: decode_compressed_value`; spec `04_ROWSTORE_COMPRESSED.md §Temporal encoding under ROW compression`

### Columnstore segment (`enc=1–6`)

`date` values appear in columnstore as integer day-count vectors. The encoding follows the standard numeric columnar path (`enc=1/2` RLE/bitpack or `enc=3` dictionary).

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`

### XTP checkpoint

Same per-value 3-byte LE encoding as uncompressed rowstore. Alignment padding applies at the record level.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

`datetime.date` — the standard Python date object from the `datetime` module.

Range: `datetime.date(1, 1, 1)` to `datetime.date(9999, 12, 31)`, matching SQL Server's documented range.

Source: `scalars.py: _decode_date`

---

## 5. PyArrow output

| Arrow type | `pa.date32()` |
|---|---|
| Encoding | 32-bit signed integer: days since the Arrow epoch of **1970-01-01** (Unix epoch) |
| Conversion | Arrow automatically converts `datetime.date` values when building a `date32` array |

Note: the Arrow `date32` epoch (1970-01-01) differs from the SQL Server `date` epoch (0001-01-01). The Python `datetime.date` intermediate value carries the correct calendar date; PyArrow converts it to the 1970-relative day offset when building the column.

Source: `arrow.py: arrow_type` — `pa.date32()`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap; no value bytes are read.
- **Pre-1970 dates**: Day counts before the Arrow epoch produce negative `date32` values. This is correct and standard; negative `date32` values represent dates before 1970-01-01.
- **Minimum value 0001-01-01**: Day count = 0. Python `datetime.date(1, 1, 1)` is the minimum representable date in both SQL Server and Python.
- **`sql_variant` base type**: `date` can be stored inside a `sql_variant`. The value starts at offset 2 (no extra metadata bytes), decoded by `_decode_date` (see `13_sql_variant.md`).

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: DATE=40` |
| Epoch | `scalars.py: _DATE_EPOCH = dt.date(1, 1, 1)` |
| Decode function | `scalars.py: _decode_date` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.date32()` |
| Compression | `rowcompress.py: decode_compressed_value`; `04_ROWSTORE_COMPRESSED.md §Temporal encoding` |

---

## 8. Confidence

`[CONFIRMED]` — verified against `typecoverage_full.bak` (SQL Server 2022). Pre-epoch dates (before 0001-01-01 is not representable; above 1970-01-01 range) and the 3-byte epoch-offset format are `[CORROBORATED]` by [MS-TDS] §2.2.5.5.1.5.
