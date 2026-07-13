# Variant Type — `sql_variant`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | On-disk width | SQL Server version |
|---|---|---|---|
| `sql_variant` | 98 | Variable | All |

`sql_variant` is a heterogeneous type: each row can store a value of a different base type. The base type, any required metadata (scale, precision, collation, max_length), and the value bytes are all packed inline.

---

## 2. Binary layout — uncompressed rowstore

```
[+0]    uint8   base_type    (system_type_id of the stored value)
[+1]    uint8   version = 1
[+2..]  type-specific metadata + value
```

The metadata and value offset depend on the base type:

| Base type group | Metadata at [+2..] | Value offset |
|---|---|---|
| Fixed numerics, uniqueidentifier, date, smalldatetime, datetime | None | +2 |
| decimal / numeric | precision @+2, scale @+3 | +4 |
| binary / varbinary | uint16 LE `max_length` @+2 | +4 |
| char / varchar / nchar / nvarchar | 5-byte collation block @+2 | +8 |
| time / datetime2 / datetimeoffset | scale @+2 | +3 |
| bit | None (value is 0 or 1 at +2) | +2 |
| real | None | +2 |
| float | None | +2 |
| money | None | +2 |
| smallmoney | None | +2 |
| bigint | None | +2 |
| smallint | None | +2 |
| int | None | +2 |
| tinyint | None | +2 |

Source: `scalars.py` constants `_VARIANT_VALUE=2`, `_VARIANT_DECIMAL_VALUE=4`, `_VARIANT_BINARY_VALUE=4`, `_VARIANT_STRING_VALUE=8`, `_VARIANT_SCALE=2`, `_VARIANT_SCALE_VALUE=3`

---

## 3. Permitted base types

Only a subset of SQL Server types can be stored in a `sql_variant` — the engine forbids LOB types (`varchar(max)`, `nvarchar(max)`, `varbinary(max)`), `text`, `ntext`, `image`, `xml`, CLR UDTs, `rowversion`/`timestamp`, and `sql_variant` itself.

Permitted base types (source: `scalars.py: _VARIANT_BASE_TYPES`):

```python
_VARIANT_BASE_TYPES = frozenset({
    TINYINT, SMALLINT, INT, BIGINT, BIT, REAL, FLOAT, MONEY, SMALLMONEY,
    DATE, DATETIME, SMALLDATETIME, DATETIME2, TIME, DATETIMEOFFSET,
    UNIQUEIDENTIFIER, DECIMAL, NUMERIC, BINARY, VARBINARY,
    CHAR, VARCHAR, NCHAR, NVARCHAR,
})
```

An unrecognised base type byte raises `NotImplementedError`.

---

## 4. Dispatch logic

```python
def _decode_sql_variant(raw: bytes) -> Any:
    base = raw[0]
    body = raw[_VARIANT_VALUE:]   # raw[2:]
    if base == TINYINT:
        return _decode_int(body, signed=False)
    if base in (SMALLINT, INT, BIGINT):
        return _decode_int(body, signed=True)
    if base == BIT:
        return _decode_bit(body)
    if base == REAL:
        return _decode_real(body)
    if base == FLOAT:
        return _decode_float(body)
    if base == MONEY:
        return _decode_money(body)
    if base == SMALLMONEY:
        return _decode_smallmoney(body)
    if base == DATE:
        return _decode_date(body)
    if base == DATETIME:
        return _decode_datetime(body)
    if base == SMALLDATETIME:
        return _decode_smalldatetime(body)
    if base in (DATETIME2, TIME, DATETIMEOFFSET):
        scale = raw[_VARIANT_SCALE]          # raw[2]
        value = raw[_VARIANT_SCALE_VALUE:]   # raw[3:]
        ...
    if base == UNIQUEIDENTIFIER:
        return _decode_uuid(body[:16])
    if base in (DECIMAL, NUMERIC):
        return _decode_decimal(raw[_VARIANT_DECIMAL_VALUE:], raw[3])  # scale @+3
    if base in (BINARY, VARBINARY):
        return bytes(raw[_VARIANT_BINARY_VALUE:])
    if base in (CHAR, VARCHAR):
        return _decode_char(raw[_VARIANT_STRING_VALUE:])
    if base in (NCHAR, NVARCHAR):
        return _decode_nchar(raw[_VARIANT_STRING_VALUE:])
    raise NotImplementedError(...)
```

Source: `scalars.py: _decode_sql_variant`

---

## 5. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`sql_variant` values in compressed rows are stored in the CD record. The base type dispatch header is preserved verbatim; individual value bytes may be subject to the type-specific compression (e.g. integer base types use excess-encoded big-endian). In practice, `sql_variant` columns are uncommon in compressed tables.

### Columnstore segment (`enc=1–6`)

`sql_variant` columns are not typically stored in a clustered columnstore index (the engine restricts columnstore to fixed-schema columns). In a non-clustered CCI, the delta store uses the uncompressed rowstore format.

### XTP checkpoint

`sql_variant` values use the same base-type-dispatch layout as uncompressed rowstore.

---

## 6. Python intermediate

The Python value of the **base type** — not a wrapper object. For example, a `sql_variant` storing `int 42` returns Python `int` 42; one storing `varchar 'hello'` returns Python `str` `'hello'`.

Source: `scalars.py: _decode_sql_variant`

---

## 7. PyArrow output

`pa.string()` — the Python value is converted to its string representation before Arrow storage. Since each row may have a different base type, a heterogeneous column cannot be stored in a typed Arrow column; `str` is used as the common carrier.

Source: `arrow.py: arrow_type` — `pa.string()` for `SQL_VARIANT`

---

## 8. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **`NCHAR`/`NVARCHAR` base type returning `None`**: `_decode_nchar` returns `None` for AE ciphertext. In a `sql_variant`, this becomes a Python `None` (treated as SQL NULL by the sink).
- **`DATETIME` base type returning `None`**: `_decode_datetime` returns `None` for out-of-range values.
- **Collation block ignored**: For `char`/`varchar`/`nchar`/`nvarchar` base types, the 5-byte collation block at offsets 3–7 is not used by the decoder — the default `cp1252` fallback (for byte types) or UTF-16-LE (for unicode types) is applied. Downstream callers needing collation-aware decoding would need to parse the collation block.
- **Version byte**: Always `1` in all observed fixtures. A version byte other than `1` is not explicitly rejected but would not be expected.

---

## 9. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: SQL_VARIANT=98` |
| Permitted base types | `scalars.py: _VARIANT_BASE_TYPES` |
| Layout constants | `scalars.py: _VARIANT_VALUE`, `_VARIANT_DECIMAL_VALUE`, `_VARIANT_BINARY_VALUE`, `_VARIANT_STRING_VALUE`, `_VARIANT_SCALE`, `_VARIANT_SCALE_VALUE` |
| Dispatch function | `scalars.py: _decode_sql_variant` |
| [MS-TDS] reference | `scalars.py: _decode_sql_variant` docstring §2.2.5.5 |
| Arrow mapping | `arrow.py: arrow_type` — `pa.string()` |

---

## 10. Confidence

`[CORROBORATED]` — `sql_variant` layout per [MS-TDS] §2.2.5.5. Base-type coverage pinned by `test_sql_variant_base_types_all_decode` (guards that every `_VARIANT_BASE_TYPES` member has a decode branch). Verified against `typecoverage_full.bak`.
