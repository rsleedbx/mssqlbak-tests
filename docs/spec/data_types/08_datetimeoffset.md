# Timezone-Aware Datetime — `datetimeoffset(n)`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | On-disk width | Epoch | SQL Server version |
|---|---|---|---|---|
| `datetimeoffset(n)` | 43 | 8–10 bytes (scale-dependent) | 0001-01-01 UTC | 2008+ |

`datetimeoffset(n)` is `datetime2(n)` with an appended signed 16-bit timezone offset in minutes. The stored date/time is UTC; the offset preserves the original wall-clock zone.

---

## 2. Binary layout — uncompressed rowstore

```
[+0 .. time_len-1]      uint LE   n-scaled UTC ticks since midnight
[+time_len .. +tl+2]    uint24 LE UTC day count from 0001-01-01
[+time_len+3 .. +tl+4]  int16 LE  timezone offset in minutes (signed, range ±840)
```

Scale-to-width mapping (same as `datetime2` and `time`):

| Scale (n) | `time_len` | Total bytes |
|---|---|---|
| 0, 1, 2 | 3 | 8 |
| 3, 4 | 4 | 9 |
| 5, 6, 7 | 5 | 10 |

Domain constraint: SQL Server limits timezone offsets to ±14:00 (±840 minutes). An offset outside this range in a backup indicates a corrupt or mis-aligned read; mssqlbak raises `ValueError` rather than emitting a plausible-but-wrong timezone.

Decoding:

```python
time_len = _DT2_TIME_LEN[scale]
frac  = int.from_bytes(raw[:time_len], "little")
days  = int.from_bytes(raw[time_len:time_len + 3], "little")
off_min = int.from_bytes(raw[time_len + 3:time_len + 5], "little", signed=True)
if not -840 <= off_min <= 840:
    raise ValueError(...)
micro = _frac_to_micro(frac, scale)
utc_naive = datetime(1, 1, 1) + timedelta(days=days, microseconds=micro)
tz = timezone(timedelta(minutes=off_min))
value = (utc_naive + timedelta(minutes=off_min)).replace(tzinfo=tz)
```

The stored UTC instant is shifted by `off_min` to produce the local wall-clock time, then the timezone is attached. This means the returned `datetime` equals both the UTC instant (via `.astimezone(utc)`) and the original local wall-clock reading.

Source: `scalars.py: _decode_datetimeoffset`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`datetimeoffset` stores its ordinary little-endian bytes with **trailing** (high-order) zero bytes stripped. The decoder right-pads to the full `time_len + 5` bytes before calling `_decode_datetimeoffset`.

Source: `rowcompress.py: decode_compressed_value`; spec `04_ROWSTORE_COMPRESSED.md §Temporal encoding`

### Columnstore segment (`enc=1–6`)

`datetimeoffset` values appear in columnstore as combined integer vectors (UTC tick count + date), with the offset potentially stored separately or alongside. Standard columnstore numeric encoding applies.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`

### XTP checkpoint

Same per-value encoding as uncompressed rowstore. Alignment padding at record level.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

`datetime.datetime` — **timezone-aware**, microsecond resolution. The `tzinfo` is a `datetime.timezone` fixed-offset object matching the original offset in minutes.

The returned value represents the **local wall-clock time** in the original timezone, not normalised to UTC. Callers can call `.astimezone(datetime.timezone.utc)` to get the UTC instant.

Source: `scalars.py: _decode_datetimeoffset`

---

## 5. PyArrow output

| Arrow type | `pa.timestamp("us", tz="UTC")` |
|---|---|
| Normalisation | Arrow `timestamp` with tz="UTC" stores values as UTC microseconds since Unix epoch. The Python tz-aware `datetime` is automatically converted to UTC by PyArrow when building the column. |

The UTC normalisation discards the original timezone offset during storage. The offset is not preserved in the Arrow / Delta output. This is the documented v1 behaviour.

Source: `arrow.py: arrow_type` — `pa.timestamp("us", tz="UTC")` for `DATETIMEOFFSET`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **UTC offset ±14:00**: The maximum valid SQL Server offset is ±840 minutes (±14 hours). mssqlbak raises `ValueError` for out-of-range offsets detected during decode.
- **UTC+00:00 (offset=0)**: The returned datetime has `tzinfo=timezone.utc`; the local time equals the UTC time.
- **Scale 7 precision loss**: 100-ns ticks floor to microseconds, same as `datetime2`.
- **UTC offset lost in Arrow**: The Arrow output normalises to UTC, discarding the original offset. If the original offset needs to be preserved, it must be extracted via a separate column or metadata before conversion.
- **`sql_variant` base type**: `datetimeoffset` can appear inside `sql_variant` with scale at offset 2 and value beginning at offset 3.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: DATETIMEOFFSET=43` |
| Scale-width table | `scalars.py: _DT2_TIME_LEN` |
| 0001 UTC epoch | `scalars.py: _DT_EPOCH = dt.datetime(1, 1, 1)` |
| Decode function | `scalars.py: _decode_datetimeoffset` (docstring cites [MS-TDS] §2.2.5.5.1.5) |
| Timezone domain constraint | `scalars.py: _decode_datetimeoffset` — `if not -840 <= off_min <= 840` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.timestamp("us", tz="UTC")` |
| Compression | `04_ROWSTORE_COMPRESSED.md §Temporal encoding` |

---

## 8. Confidence

`[CONFIRMED]` — verified against `typecoverage_full.bak` (SQL Server 2022) for multiple scales and offset values including ±, UTC+0, and maximum offsets. Format is `[CORROBORATED]` by [MS-TDS] §2.2.5.5.1.5.
