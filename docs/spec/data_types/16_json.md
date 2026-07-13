# Native JSON Type — `json` (SS2025+)

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | On-disk format | SQL Server version |
|---|---|---|---|
| `json` | 244 (`NATIVE_JSON`) | MSJSONB proprietary binary | SQL Server 2025+ |

`json` is a first-class type in SQL Server 2025 (previously JSON was stored as `nvarchar`). Values are stored in a compact proprietary binary format (MSJSONB) on disk and decoded to standard UTF-8 JSON text by mssqlbak.

---

## 2. Binary layout — uncompressed rowstore

The `json` column is stored as a variable-length value. The binary payload begins with a 2-byte header:

```
[+0:2]   0x10 0x00   MSJSONB header
[+2:6]   0x62 0xB4 0xF0 0xDF   4-byte sentinel
[+6..]   varint-encoded entry count
[+N..]   key-value pairs (objects) or value entries (arrays)
```

Value entries are type-tagged:

| Tag | Type |
|---|---|
| `0x00` | Integer (varint) |
| `0x01` | String (varint length + UTF-8 bytes) |
| `0x02` | float64 LE |
| `0x03` | `true` |
| `0x04` | `false` |
| `0x05` | `null` |
| `0x40xx` | Nested object (varint entry count) |
| `0x80xx` | Nested array (varint entry count) |
| `0xC0xx` | Literal (`0x00`=false, `0x01`=true, `0x02`=null, `0x04`=`{}`, `0x06`=`[]`) |

Source: `01_TYPES_LOB.md §5.5`; `native_json.py`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

The `json` variable slot is stored verbatim (MSJSONB bytes) in the CD record. No special reencoding of the binary JSON payload.

### Columnstore segment

`json` columns are not currently supported in clustered columnstore indexes in SQL Server 2025.

### XTP checkpoint

`json` columns are not currently supported in memory-optimized tables in SQL Server 2025.

---

## 4. Python intermediate

`str` — the decoded JSON as a compact UTF-8 string (via `json.dumps`). Falls back to raw bytes (`bytes`) for unrecognised MSJSONB layouts or truncated payloads.

Source: `native_json.py: decode_native_json` (referenced as `decode_native_json` in dispatch)

---

## 5. PyArrow output

`pa.string()` — the JSON text string.

Source: `arrow.py: arrow_type` — `pa.string()` for `NATIVE_JSON`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **Unrecognised MSJSONB layout**: If the header signature (`0x10 0x00` or sentinel) does not match, the decoder falls back to returning the raw bytes (or `None`). This guards against future format versions.
- **Nested documents**: Nested objects and arrays recurse through the same entry-count + tag dispatch. Deeply nested JSON may produce large Python `str` values.
- **Number precision**: Integer values use varint encoding (arbitrary precision); float64 values are decoded as IEEE-754 doubles. `json.dumps` renders them using Python's default float formatting.
- **Pre-2025 JSON stored as nvarchar**: Before SQL Server 2025, JSON was stored as `nvarchar(max)` text. Those columns have `system_type_id = 231` (NVARCHAR), not 244. mssqlbak decodes them as plain text strings via the nvarchar path.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: NATIVE_JSON=244` |
| MSJSONB header/sentinel | `01_TYPES_LOB.md §5.5`; `native_json.py` |
| Value-entry tags | `01_TYPES_LOB.md §5.5` |
| Decoder | `native_json.py: decode_native_json` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.string()` for `NATIVE_JSON` |

---

## 8. Confidence

`[EMPIRICAL]` — MSJSONB format reverse-engineered from SQL Server 2025 Preview fixtures. Header signature and varint encoding confirmed. Complex nested structures and edge-case tags are `[EMPIRICAL]` with ongoing fixture coverage.
