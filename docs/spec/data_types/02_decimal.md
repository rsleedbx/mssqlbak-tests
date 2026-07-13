# Decimal / Fixed-Point Types — `decimal`, `numeric`, `money`, `smallmoney`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | On-disk width | SQL Server version |
|---|---|---|---|
| `decimal(p,s)` | 106 | 5–17 bytes (sign + mantissa) | All |
| `numeric(p,s)` | 108 | 5–17 bytes (sign + mantissa) | All |
| `money` | 60 | 8 bytes | All |
| `smallmoney` | 122 | 4 bytes | All |

`decimal` and `numeric` are synonyms at the T-SQL level. They differ only in their `system_type_id` but share an identical on-disk layout and decoder.

---

## 2. Binary layout — uncompressed rowstore

### `decimal` / `numeric` (xtype 106 / 108)

```
[+0]    uint8   sign   (1 = positive, 0 = negative)
[+1..]  LE uint integer magnitude (unsigned, little-endian)
```

Width of the magnitude field depends on precision:

| Precision (p) | Total bytes (sign + magnitude) |
|---|---|
| 1–9 | 5 |
| 10–19 | 9 |
| 20–28 | 13 |
| 29–38 | 17 |

The final Python value is:

```
value = magnitude / 10**scale           (if sign == 1, positive)
value = -magnitude / 10**scale          (if sign == 0, negative)
```

Domain asserts: scale ∈ [0, 38]; sign ∈ {0, 1}. Values outside these ranges indicate a corrupt operand and raise `ValueError`.

Source: `scalars.py: _decode_decimal`

### `money` (xtype 60)

```
[+0:8]  int64 LE   units in 10⁻⁴ currency units
```

Value = `units / 10000` as a `Decimal`. Despite documentation describing `money` as "high dword first", the on-disk format is a plain little-endian `int64` — verified against fixtures.

> **`[CONFIRMED]`**: money byte order confirmed as plain LE int64 against `typecoverage_full.bak` (see `01_TYPES_LOB.md §5` money note).

Source: `scalars.py: _decode_money`

### `smallmoney` (xtype 122)

```
[+0:4]  int32 LE   units in 10⁻⁴ currency units
```

Identical semantics to `money` but 4-byte range (approx ±214,748.3647). Source: `scalars.py: _decode_smallmoney`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`decimal`/`numeric` use a **vardecimal** compressed format. The CD record stores a shortened representation rather than the full 5–17 byte on-disk layout. The `rowcompress.py: decode_compressed_value` function reconstructs the sign+magnitude form before applying `_decode_decimal`.

`money` and `smallmoney` are treated as fixed-width integers under ROW/PAGE compression: they use the same excess-encoded big-endian minimal-width scheme as the integer types (see `01_integer.md §3`), operating on their raw `int64`/`int32` unit values.

Cross-reference: `04_ROWSTORE_COMPRESSED.md §3.5 Integer encoding`; `04_ROWSTORE_COMPRESSED.md §4.3 Vardecimal compressed decoder`

### Columnstore segment (`enc=1–6`)

- `enc=5` path: `decimal`/`numeric` values are stored with the full sign-byte + LE-magnitude format (same as uncompressed rowstore) inside the enc=5 payload.
- `money`/`smallmoney`: stored as int64/int32 column vectors with the standard columnstore numeric encoding.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md`

### XTP checkpoint

Same per-value encoding as uncompressed rowstore. Record framing uses widest-slot-first alignment padding; no change to decimal byte layout.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

| SQL Server type | Python value |
|---|---|
| `decimal(p,s)` | `decimal.Decimal` (exact, scale-preserved via `_scaled_decimal`) |
| `numeric(p,s)` | `decimal.Decimal` (identical to decimal) |
| `money` | `decimal.Decimal` (scale 4) |
| `smallmoney` | `decimal.Decimal` (scale 4) |

`_scaled_decimal(mantissa, scale)` uses `Decimal(mantissa).scaleb(-scale, _DEC_CTX)` with a 80-digit precision context, ensuring no rounding for any valid SQL Server value.

Source: `scalars.py: _decode_decimal`, `_decode_money`, `_decode_smallmoney`, `_scaled_decimal`

---

## 5. PyArrow output

| SQL Server type | Arrow type | Notes |
|---|---|---|
| `decimal(p,s)` | `pa.decimal128(p, s)` | Precision and scale taken from `col.precision` and `col.scale`; falls back to `decimal128(38, s)` when `col.precision` is None |
| `numeric(p,s)` | `pa.decimal128(p, s)` | Same as decimal |
| `money` | `pa.decimal128(19, 4)` | Fixed: covers full money range (approx ±922 trillion) at scale 4 |
| `smallmoney` | `pa.decimal128(10, 4)` | Fixed: covers smallmoney range (approx ±214,748) at scale 4 |

Source: `arrow.py: arrow_type`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap; no value bytes are read.
- **`decimal` vs `numeric` identity**: Both types decode identically. The only difference is the `system_type_id` (106 vs 108). The dispatch table (`dispatch.py: _DECODERS`) maps both to the same decoder.
- **`money` byte order misconception**: Some SQL Server documentation describes `money` as "high dword first". This applies to the T-SQL presentation layer only; the physical on-disk format is a plain `int64` LE. The mssqlbak decoder reads `int64 LE` directly.
- **Scale 0 decimal**: Valid — `decimal(p,0)` stores integers as exact Decimal values with no fractional component.
- **`sql_variant` base type**: Both `decimal` and `numeric` can be stored inside a `sql_variant`. In that context, the layout is `[base_type][version=1][precision @+2][scale @+3][sign + magnitude @+4]` (see `13_sql_variant.md`).

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constants | `scalars.py: DECIMAL=106, NUMERIC=108, MONEY=60, SMALLMONEY=122` |
| Decimal layout ([MS-TDS] §2.2.5.5.1.2) | `scalars.py: _decode_decimal` docstring |
| Money layout ([MS-TDS] §2.2.5.5.1.1) | `scalars.py: _decode_money` docstring |
| `_scaled_decimal` precision context | `scalars.py: _DEC_CTX = decimal.Context(prec=80)` |
| Arrow mapping | `arrow.py: arrow_type` |
| ROW/PAGE vardecimal | `rowcompress.py: decode_compressed_value`; `04_ROWSTORE_COMPRESSED.md §4.3` |

---

## 8. Confidence

`[CONFIRMED]` — all four types verified against `typecoverage_full.bak` (SQL Server 2022). Money byte-order note confirmed empirically (see `01_TYPES_LOB.md §5`). Vardecimal compression path is `[EMPIRICAL]` — confirmed by round-trip decode of `cmp_page.dec` and `cmp_row.nm` columns in `compressioncoverage_full.bak`.
