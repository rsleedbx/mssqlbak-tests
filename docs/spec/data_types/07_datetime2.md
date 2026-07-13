# High-Precision Datetime — `datetime2(n)`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | On-disk width | Epoch | SQL Server version |
|---|---|---|---|---|
| `datetime2(n)` | 42 | 6–8 bytes (scale-dependent) | 0001-01-01 | 2008+ |

`datetime2(n)` extends `datetime` with a wider date range (0001-01-01 to 9999-12-31), finer precision (up to 100 ns = scale 7), and a different on-disk format. The scale `n` (0..7) is stored in `syscolpars.scale`.

---

## 2. Binary layout — uncompressed rowstore

```
[+0 .. time_len-1]  uint LE   n-scaled ticks since midnight (time component)
[+time_len .. +time_len+2]  uint24 LE   day count from 0001-01-01 (date component)
```

Width by scale (same table as `time`):

| Scale (n) | `time_len` (bytes) | Total bytes |
|---|---|---|
| 0, 1, 2 | 3 | 6 |
| 3, 4 | 4 | 7 |
| 5, 6, 7 | 5 | 8 |

Source: `scalars.py: _DT2_TIME_LEN = {0: 3, 1: 3, 2: 3, 3: 4, 4: 4, 5: 5, 6: 5, 7: 5}`

Decoding:

```python
time_len = _DT2_TIME_LEN[scale]
frac = int.from_bytes(raw[:time_len], "little")
days = int.from_bytes(raw[time_len : time_len + 3], "little")
micro = _frac_to_micro(frac, scale)
value = datetime(1, 1, 1) + timedelta(days=days, microseconds=micro)
```

The date field always occupies 3 bytes regardless of scale; only the time field width varies.

Source: `scalars.py: _decode_datetime2`, `_frac_to_micro`, `_DT_EPOCH = dt.datetime(1, 1, 1)`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`datetime2` stores its ordinary little-endian bytes with **trailing** (high-order) zero bytes stripped — the standard temporal trimming direction. The decoder right-pads to the full `time_len + 3` bytes before calling `_decode_datetime2`.

Source: `rowcompress.py: decode_compressed_value`; spec `04_ROWSTORE_COMPRESSED.md §Temporal encoding under ROW compression`

### Columnstore segment (`enc=1–6`)

`datetime2` values appear in columnstore segments as scaled tick-count integers. The date and time components are typically stored as combined integer values in the columnar path.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`

### XTP checkpoint

Same per-value encoding as uncompressed rowstore. Alignment padding at record level.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

`datetime.datetime` — timezone-naive, microsecond resolution (scale 7 loses the 100-ns sub-microsecond remainder by flooring).

Source: `scalars.py: _decode_datetime2`

---

## 5. PyArrow output

| Arrow type | `pa.timestamp("us")` |
|---|---|
| Timezone | None (naive) |
| Epoch | Unix epoch (1970-01-01) for Arrow storage; Python `datetime` carries the correct calendar value |

Source: `arrow.py: arrow_type` — `pa.timestamp("us")` for `DATETIME2`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **Scale 7 precision loss**: Same as `time(7)` — 100-ns ticks floor to microseconds. Documented v1 behaviour.
- **Epoch distinction from `datetime`**: `datetime2` uses 0001-01-01 as epoch, while `datetime` uses 1900-01-01. Never mix the decoders.
- **`sql_variant` base type**: `datetime2` can appear inside `sql_variant` with scale at offset 2, value beginning at offset 3. The value is decoded as `time_len + 3` bytes at offset 3, where `time_len = _DT2_TIME_LEN[scale]`.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: DATETIME2=42` |
| Scale-width table | `scalars.py: _DT2_TIME_LEN` |
| 0001 epoch | `scalars.py: _DT_EPOCH = dt.datetime(1, 1, 1)` |
| Decode function | `scalars.py: _decode_datetime2`, `_frac_to_micro` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.timestamp("us")` |
| Compression | `04_ROWSTORE_COMPRESSED.md §Temporal encoding` |

---

## 8. Confidence

`[CONFIRMED]` — verified against `typecoverage_full.bak` (SQL Server 2022) for all eight scales. Scale-width table is `[CORROBORATED]` by [MS-TDS] §2.2.5.5.1.5.
