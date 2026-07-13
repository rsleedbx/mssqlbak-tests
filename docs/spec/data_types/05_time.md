# Time Type — `time(n)`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | On-disk width | SQL Server version |
|---|---|---|---|
| `time(n)` | 41 | 3–5 bytes (scale-dependent) | 2008+ |

`time(n)` stores a time-of-day with no date component. `n` (the scale) specifies fractional-second precision: 0 = seconds, 7 = 100-nanosecond ticks. The scale is stored in `syscolpars.scale` for each column.

---

## 2. Binary layout — uncompressed rowstore

```
[+0 .. time_len-1]  uint LE   n-scaled ticks since midnight
```

Width by scale:

| Scale (n) | Bytes (`time_len`) | Tick unit |
|---|---|---|
| 0, 1, 2 | 3 | 10^-n seconds |
| 3, 4 | 4 | 10^-n seconds |
| 5, 6, 7 | 5 | 10^-7 s (100 ns) for scale 7; 10^-5/10^-6 for scale 5/6 |

Source: `scalars.py: _DT2_TIME_LEN = {0: 3, 1: 3, 2: 3, 3: 4, 4: 4, 5: 5, 6: 5, 7: 5}`

Decoding:

```python
frac = int.from_bytes(raw[:time_len], "little")
micro = _frac_to_micro(frac, scale)          # converts to microseconds, flooring
value = (datetime(1,1,1) + timedelta(microseconds=micro)).time()
```

`_frac_to_micro` converts the n-scaled fraction to microseconds:
- scale ≥ 6: `micro = frac // 10^(scale - 6)` (scale 7 → floor to microseconds)
- scale < 6: `micro = frac * 10^(6 - scale)`

Source: `scalars.py: _decode_time`, `_frac_to_micro`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`time` stores its ordinary little-endian bytes with **trailing** (high-order) zero bytes stripped. The decoder right-pads to `time_len` bytes before calling the standard decode.

Source: `rowcompress.py: decode_compressed_value`; spec `04_ROWSTORE_COMPRESSED.md §Temporal encoding under ROW compression`

### Columnstore segment (`enc=1–6`)

`time` values are stored as integer tick vectors in the columnar path (the unsigned integer tick count at the given scale). Standard `enc=1/2/3` encoding applies.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`

### XTP checkpoint

Same per-value encoding as uncompressed rowstore. Alignment padding at record level.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

`datetime.time` — a standard Python time object (no date, no timezone).

Precision is floored to microseconds. Scale-7 values (100 ns ticks) lose the sub-microsecond remainder — documented v1 behaviour.

Source: `scalars.py: _decode_time`

---

## 5. PyArrow output

| Arrow type | `pa.string()` |
|---|---|
| Format | ISO 8601 time string: `HH:MM:SS` or `HH:MM:SS.ffffff` |
| Field metadata | `{b"ss_type": b"time"}` set on every `time(n)` Arrow field |

Delta Lake has no native time-of-day type. mssqlbak emits the value as an ISO 8601 string. The field metadata allows downstream sinks (e.g. PostgreSQL via `pg_dir_sink`) to detect `time(n)` columns and use `TIME WITHOUT TIME ZONE` instead of `TEXT`.

```python
_TIME_FIELD_META: dict[bytes, bytes] = {b"ss_type": b"time"}
```

Source: `dispatch.py: _TIME_FIELD_META`; `arrow.py: arrow_schema_for` (metadata attachment); `arrow.py: arrow_type` — `pa.string()`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **Scale 7 precision loss**: `time(7)` stores 100-ns ticks. The decode floors to microseconds (`frac // 10`). The lost 100-ns remainder is intentional — Python's `datetime.time` cannot represent sub-microsecond values.
- **Scale 0 (`time(0)`)**: Stores whole seconds as a 3-byte integer. Range is 0..86399 (seconds in a day). Decodes to `datetime.time` with zero microseconds.
- **`sql_variant` base type**: `time` can appear inside a `sql_variant` with scale at offset 2, value at offset 3.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: TIME=41` |
| Scale-width table | `scalars.py: _DT2_TIME_LEN` |
| Decode function | `scalars.py: _decode_time`, `_frac_to_micro` |
| Field metadata constant | `dispatch.py: _TIME_FIELD_META` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.string()`; `arrow_schema_for` (metadata) |
| Compression | `04_ROWSTORE_COMPRESSED.md §Temporal encoding` |

---

## 8. Confidence

`[CONFIRMED]` — verified against `typecoverage_full.bak` (SQL Server 2022) for all eight scales (0–7). Scale-width table is `[CORROBORATED]` by [MS-TDS] §2.2.5.5.1.5.
