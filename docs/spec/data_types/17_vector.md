# Native Vector Type — `vector(N)` (SS2025+)

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | system_type_id | user_type_id | On-disk format | SQL Server version |
|---|---|---|---|---|
| `vector(N)` | 165 (VARBINARY) | 255 (`NATIVE_VECTOR`) | Fixed header + float32 array | SQL Server 2025+ |

`vector(N)` is physically stored as `varbinary` on disk (`system_type_id = 165`). It is distinguished from a plain `varbinary` column by its dedicated `user_type_id = 255`. mssqlbak checks `user_type_id` to route the column to the vector decoder.

---

## 2. Binary layout — uncompressed rowstore

```
[+0]     0xA9        layout / version marker
[+1]     0x01        element base type (1 = float32; other values reserved)
[+2:4]   uint16 LE   dimension count (N)
[+4:8]   uint32 LE   reserved = 0
[+8..]   N × float32 LE   element values (little-endian IEEE-754 single precision)
```

Total size: `8 + N × 4` bytes.

Example for a 3-dimensional vector `[1.0, 2.0, 3.0]`:
```
A9 01 03 00 00 00 00 00   header
00 00 80 3F               1.0f
00 00 00 40               2.0f
00 00 40 40               3.0f
```

Source: `scalars.py: decode_vector` docstring

---

## 3. String rendering

Each float element is formatted as SQL Server renders it: scientific notation with exactly 7 fractional digits and a **3-digit** exponent:

```python
def _fmt_vector_float(x: float) -> str:
    mantissa, _, exp = f"{x:.7e}".partition("e")
    sign, digits = exp[0], exp[1:]
    return f"{mantissa}e{sign}{int(digits):03d}"
```

Example output: `1.0000000e+000`, `2.0000000e+000`, `3.0000000e+000`

Full array string: `[1.0000000e+000,2.0000000e+000,3.0000000e+000]`

Source: `scalars.py: _fmt_vector_float`, `decode_vector`

---

## 4. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

The `vector` variable slot (physically `varbinary`) is stored verbatim in the CD record — no special compression encoding for the float32 array bytes.

### Columnstore segment

`vector` columns are not supported in columnstore indexes in SQL Server 2025.

### XTP checkpoint

`vector` columns are not supported in memory-optimized tables in SQL Server 2025.

---

## 5. Python intermediate

`str` — the JSON-array style string representation (e.g. `"[1.0000000e+000,2.0000000e+000]"`). Returns `None` if the payload is shorter than 8 bytes, the header byte is not `0xA9`, or the payload is truncated.

Source: `scalars.py: decode_vector`

---

## 6. PyArrow output

`pa.string()` — the JSON-array string.

Source: `arrow.py: arrow_type` — VARBINARY branch: `if t == VARBINARY and getattr(col, "user_type_id", None) == NATIVE_VECTOR: return pa.string()`

---

## 7. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **Unknown element type**: The layout byte at offset 1 is checked; only `0x01` (float32) is defined. Any other value causes `decode_vector` to return `None`.
- **Truncated buffer**: If `len(raw) < 8 + N * 4`, `decode_vector` returns `None`.
- **`NATIVE_VECTOR` user_type_id**: The `user_type_id = 255` is a special value allocated by SQL Server 2025. Regular `varbinary` columns have `user_type_id = 165` (same as their `system_type_id`). The parser must check both fields to distinguish a `vector` column from a plain `varbinary`.
- **N=0 (zero-dimensional vector)**: Technically valid (empty float array); rendered as `[]`.

---

## 8. Source references

| Claim | Source |
|---|---|
| user_type_id constant | `scalars.py: NATIVE_VECTOR=255` |
| system_type_id | same as `VARBINARY=165` |
| On-disk layout | `scalars.py: decode_vector` docstring; `01_TYPES_LOB.md §5` vector row |
| Float formatting | `scalars.py: _fmt_vector_float` |
| Decoder | `scalars.py: decode_vector` |
| Arrow mapping | `arrow.py: arrow_type` — VARBINARY/NATIVE_VECTOR branch |

---

## 9. Confidence

`[EMPIRICAL]` — `vector(N)` format reverse-engineered from SQL Server 2025 Preview fixtures. Header byte `0xA9`, element type `0x01`, and dimension count confirmed against fixture data. Float32 LE encoding and the SQL Server 3-digit exponent rendering convention are confirmed by round-trip tests.
