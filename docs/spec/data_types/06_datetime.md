# Legacy Datetime Types — `smalldatetime`, `datetime`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | Fixed width | Epoch | SQL Server version |
|---|---|---|---|---|
| `smalldatetime` | 58 | 4 bytes | 1900-01-01 | All |
| `datetime` | 61 | 8 bytes | 1900-01-01 | All |

Both types use a 1900-01-01 epoch (as opposed to the 0001-01-01 epoch used by `date`, `datetime2`, `datetimeoffset`). They are "classic" types predating SQL Server 2008.

---

## 2. Binary layout — uncompressed rowstore

### `smalldatetime` (xtype 58)

```
[+0:2]  uint16 LE   minutes since midnight (time component)
[+2:4]  uint16 LE   days since 1900-01-01  (date component)
```

Note the **reversed field order** compared to `datetime`: minutes comes first (lower offset), days second.

```python
value = datetime(1900, 1, 1) + timedelta(days=days, minutes=minutes)
```

Range: 1900-01-01 00:00 to 2079-06-06 23:59. Resolution: 1 minute.

Source: `scalars.py: _decode_smalldatetime`, `_DT1900_EPOCH = dt.datetime(1900, 1, 1)`

### `datetime` (xtype 61)

```
[+0:4]  uint32 LE   ticks of 1/300 second since midnight (time component)
[+4:8]  int32 LE    days from 1900-01-01 (signed; negative = before 1900)
```

```python
micro_exact = ticks * 1_000_000 // 300          # exact microsecond value
# Round to nearest millisecond (no .5 ties — exact remainders are .000/.333/.667 ms)
micro = ((micro_exact + 500) // 1000) * 1000
value = datetime(1900, 1, 1) + timedelta(days=days, microseconds=micro)
```

Range: 1753-01-01 to 9999-12-31. Resolution: ~3.333 ms (1/300 second), but SQL Server clients always see values rounded to `.000`, `.003`, or `.007` seconds.

> **Rounding rule**: The 1/300-second tick is ≈ 3.333 ms. SQL Server rounds to the nearest millisecond at the client display layer. The three valid sub-second endings are `.000` (0 ticks mod 300), `.003` (1/300 s ≈ 3.333 ms rounds to 3 ms → .003), and `.007` (2/300 s ≈ 6.667 ms rounds to 7 ms → .007). mssqlbak applies the same rounding so decoded values match SQL Server client output.

Source: `scalars.py: _decode_datetime`, `classic_datetime_from_parts`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

**`smalldatetime`**: treated as a float-like type (leading-zero stripped), **not** the temporal trailing-zero path. Its 4 bytes are stored with LSB-side zeros stripped. The decoder prepends zeros.

> **G19 resolved**: `smalldatetime` was initially suspected to use the temporal trailing-zero path. Confirmed by `spec_probe rowcompress` against `compressioncoverage_full.bak` that it uses the float/leading-zero path (`cmp_page.sdt` round-trips correctly).

**`datetime`**: treated as an integer pair. The two fields (ticks uint32, days int32) each use excess-encoded big-endian minimal-width compression independently.

Source: `rowcompress.py: decode_compressed_value`; spec `04_ROWSTORE_COMPRESSED.md §Float / smalldatetime encoding`, `§G19 resolved`

### Columnstore segment (`enc=1–6`)

`smalldatetime` and `datetime` values appear in columnstore as integer vectors (the raw uint32/int32 on-disk integer values). Standard `enc=1/2/3` apply.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`

### XTP checkpoint

Same per-value encoding as uncompressed rowstore. Alignment padding at record level.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

| SQL Server type | Python value |
|---|---|
| `smalldatetime` | `datetime.datetime` (timezone-naive, minute resolution) |
| `datetime` | `datetime.datetime` (timezone-naive, millisecond resolution) or `None` on overflow |

`_decode_datetime` returns `None` when the days value causes a Python `OverflowError` or `ValueError` (corrupt / out-of-range row). Callers treat `None` as NULL.

Source: `scalars.py: _decode_smalldatetime`, `_decode_datetime`, `classic_datetime_from_parts`

---

## 5. PyArrow output

| SQL Server type | Arrow type | Notes |
|---|---|---|
| `smalldatetime` | `pa.timestamp("us")` | Stored as microseconds since Unix epoch (1970-01-01); timezone-naive |
| `datetime` | `pa.timestamp("us")` | Same; millisecond values fit exactly in microsecond storage |

Both use microsecond resolution (`"us"`) for Arrow compatibility with `datetime2` and Delta Lake.

Source: `arrow.py: arrow_type` — `pa.timestamp("us")` for both `SMALLDATETIME` and `DATETIME`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **`datetime` negative days**: Days before 1900-01-01 are stored as a signed `int32` (negative). The epoch subtraction correctly reconstructs dates back to 1753-01-01 (the SQL Server minimum for `datetime`).
- **`datetime` millisecond rounding**: The tick unit 1/300 s produces three patterns: ticks % 300 = 0 → `.000`; 1..149 → rounds to the nearest ms; 150..299 → rounds to the nearest ms. The repeating pattern produces the well-known `.000/.003/.007` cycle. `classic_datetime_from_parts` implements this rounding identically to SQL Server's client-side rounding.
- **`datetime` overflow guard**: `_decode_datetime` wraps the `classic_datetime_from_parts` call in a try/except for `OverflowError`/`ValueError`. Rows outside Python's `datetime` range return `None`.
- **`sql_variant` base type**: Both types can appear inside `sql_variant`. The value starts at offset 2 (no extra metadata bytes).

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constants | `scalars.py: SMALLDATETIME=58, DATETIME=61` |
| 1900 epoch | `scalars.py: _DT1900_EPOCH = dt.datetime(1900, 1, 1)` |
| Decode functions | `scalars.py: _decode_smalldatetime`, `_decode_datetime`, `classic_datetime_from_parts` |
| Rounding explanation | `scalars.py: classic_datetime_from_parts` docstring |
| Arrow mapping | `arrow.py: arrow_type` — `pa.timestamp("us")` |
| Compression path | `04_ROWSTORE_COMPRESSED.md §Float/smalldatetime encoding`, `§G19` |

---

## 8. Confidence

`[CONFIRMED]` — both types verified against `typecoverage_full.bak` (SQL Server 2022). The `.000/.003/.007` rounding rule is `[CORROBORATED]` by SQL Server Books Online and confirmed by fixture round-trips. The `smalldatetime` leading-zero compression path is `[EMPIRICAL]` — confirmed by `compressioncoverage_full.bak` probe (G19).
