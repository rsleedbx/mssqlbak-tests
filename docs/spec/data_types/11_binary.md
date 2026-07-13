# Binary Types — `binary`, `varbinary`, `varbinary(max)`, `image`, `rowversion`, `timestamp`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | `max_length` | Storage class | SQL Server version |
|---|---|---|---|---|
| `binary(n)` | 173 | n | Fixed-length, in-row | All |
| `varbinary(n)` | 165 | n | Variable-length, in-row | All |
| `varbinary(max)` | 165 | -1 | Variable-length, off-row LOB | 2005+ |
| `image` | 34 | — | Legacy LOB (16-byte text pointer) | All (deprecated) |
| `rowversion` | 189 | 8 | Fixed-length, in-row | All |
| `timestamp` | 189 | 8 | **Deprecated alias for `rowversion`** — identical xtype and wire format | All (deprecated) |

> **`timestamp` alias**: `timestamp` is a deprecated T-SQL keyword that creates a `rowversion` column. Both names result in `system_type_id = 189` in `syscolpars`. The mssqlbak parser sees only xtype 189 and treats both identically. Do not confuse with `datetime`-family types — SQL Server `timestamp`/`rowversion` is an opaque 8-byte database-wide counter, not a date/time value.

---

## 2. Binary layout — uncompressed rowstore

### `binary(n)` (xtype 173)

```
[+0:n]  n bytes, opaque raw data
```

Fixed-width; occupies exactly `n` bytes in the fixed-data region. SQL Server right-pads with `0x00` bytes to the declared length.

### `varbinary(n)` (xtype 165)

```
[variable-length slot]  k bytes, opaque raw data  (0 ≤ k ≤ n ≤ 8000)
```

Stored in the variable-length region.

### `varbinary(max)` (xtype 165, `max_length = -1`)

When `max_length == -1`, the variable slot holds an off-row LOB pointer:

- Short values (≤ 8000 bytes): may be stored in-row.
- Long values: inline-root pointer (struct_type = 4) or ROW_OVERFLOW pointer (struct_type = 2).

The assembled bytes are returned as `bytes`. See `01_TYPES_LOB.md §6`.

### `image` (xtype 34)

```
[+0:16]  16-byte text pointer (same layout as text; see 09_char_varchar.md §2)
```

Content assembled from the text B-tree is returned as raw `bytes`. Unlike `text`/`ntext`, no character decoding is applied.

### `rowversion` / `timestamp` (xtype 189)

```
[+0:8]  8 bytes, opaque engine-assigned binary counter (big-endian monotonic sequence)
```

The 8-byte value is the database-wide row version counter maintained by SQL Server. It is not meaningful to the user as an integer; mssqlbak returns it as opaque `bytes`.

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`binary`, `varbinary`, and `rowversion` are **stored verbatim** — no transformation under ROW or PAGE compression. The byte content is placed directly in the CD record's data region without reencoding.

Source: `04_ROWSTORE_COMPRESSED.md §3.4` (CD record; binary types have no special compression handling)

### Columnstore segment (`enc=1–6`)

`varbinary` columns appear in columnstore with `enc=3` (dictionary) or `enc=5`. In the enc=5 path, the raw bytes are stored inline. In the dictionary path, unique byte strings are stored in the dictionary and referenced by integer code.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`

### XTP checkpoint

Same raw-byte encoding as uncompressed rowstore. No transformation within the XTP row structure.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

`bytes` — the raw byte content as a Python `bytes` object. `None` if NULL.

No decoding is applied: the bytes are returned exactly as they appear on disk (after LOB assembly if applicable).

---

## 5. PyArrow output

`pa.binary()` — variable-length binary Arrow type for all binary types.

> **Note on `varbinary(max)` Arrow type**: The Arrow `binary()` type supports variable-length byte strings of arbitrary length. Large values (> 2 GiB) would require `pa.large_binary()`, but SQL Server's max LOB size (2 GB) fits within `binary()` in practice.

Source: `arrow.py: arrow_type` — `pa.binary()` for `BINARY`, `VARBINARY`, `IMAGE`, `ROWVERSION`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap for in-row types. For `image`, NULL is indicated in the text-pointer slot.
- **`binary(n)` null padding**: SQL Server stores `binary(n)` right-padded with `0x00` bytes. mssqlbak returns the full `n`-byte value including the padding — no stripping.
- **`rowversion` byte order**: The 8 bytes are the internal counter in big-endian byte order as maintained by SQL Server. This is opaque; do not interpret as a little-endian integer.
- **`timestamp` name collision**: SQL Server's `timestamp` has nothing to do with dates or times. It is a binary monotonic counter. The T-SQL keyword `timestamp` is deprecated; `rowversion` is the current name.
- **`varbinary(max)` as NATIVE_VECTOR**: When `system_type_id = 165` and `user_type_id = 255` (`NATIVE_VECTOR`), the column is a SS2025 `vector` type, not a plain `varbinary`. See [`17_vector.md`](17_vector.md).
- **`sql_variant` base type**: `binary` and `varbinary` can appear inside `sql_variant`. The 2-byte `max_length` field occupies offsets 2–3; the value starts at offset 4.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constants | `scalars.py: BINARY=173, VARBINARY=165, IMAGE=34, ROWVERSION=189` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.binary()` |
| NATIVE_VECTOR disambiguation | `scalars.py: NATIVE_VECTOR=255` (user_type_id); `arrow.py: arrow_type` VARBINARY branch |
| LOB pointer layout | `01_TYPES_LOB.md §6.3` |
| Compression verbatim | `04_ROWSTORE_COMPRESSED.md §3.4` |

---

## 8. Confidence

`[CONFIRMED]` — `binary`, `varbinary`, `rowversion` verified against `typecoverage_full.bak`. `varbinary(max)` LOB path `[CORROBORATED]` (see `01_TYPES_LOB.md §6`). `image` LOB path `[EMPIRICAL]` — G32.
