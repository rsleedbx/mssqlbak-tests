# Unique Identifier — `uniqueidentifier`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | Fixed width | SQL Server version |
|---|---|---|---|
| `uniqueidentifier` | 36 | 16 bytes | All |

`uniqueidentifier` stores a 128-bit UUID / GUID value.

---

## 2. Binary layout — uncompressed rowstore

```
[+0:16]  16 bytes, mixed-endian UUID (Microsoft GUID format)
```

The 16 bytes are **not** in RFC 4122 network byte order. The `Data1`, `Data2`, and `Data3` fields are stored little-endian on disk:

```
bytes  0- 3  : uint32 LE  Data1
bytes  4- 5  : uint16 LE  Data2
bytes  6- 7  : uint16 LE  Data3
bytes  8-15  : 8 bytes as-is  Data4 (already big-endian per UUID spec)
```

Python's `uuid.UUID(bytes_le=raw)` decodes this mixed-endian format correctly, producing a canonical `UUID` object with the right string representation (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).

Source: `scalars.py: _decode_uuid` — `uuid.UUID(bytes_le=raw)`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`uniqueidentifier` is **stored verbatim** — the 16 mixed-endian bytes are placed directly in the CD record's data region. No reencoding or reordering under ROW or PAGE compression.

Source: `04_ROWSTORE_COMPRESSED.md §3.4`

### Columnstore segment (`enc=1–6`)

`uniqueidentifier` values appear in columnstore with `enc=5` (stored as 16-byte raw blobs). The mixed-endian byte ordering is preserved. Status G6 `[CONFIRMED]`: columnstore enc=5 UUID values reuse the same `UUID(bytes_le=...)` transform.

Cross-reference: `06_COLUMNSTORE_SEGMENT.md §G6`

### XTP checkpoint

Same mixed-endian 16-byte encoding as uncompressed rowstore.

Cross-reference: `08_XTP_CHECKPOINT.md §V04a`

---

## 4. Python intermediate

`uuid.UUID` — a Python UUID object. The string representation (`str(value)`) is the standard lowercase hyphenated form `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.

Source: `scalars.py: _decode_uuid`

---

## 5. PyArrow output

`pa.string()` — the UUID is rendered as its canonical lowercase hyphenated string before being stored as an Arrow string.

Source: `arrow.py: arrow_type` — `pa.string()` for `UNIQUEIDENTIFIER`

---

## 6. Edge cases

- **NULL**: Encoded via the row's NULL bitmap.
- **Mixed-endian**: The key subtlety is that `Data1`, `Data2`, and `Data3` are stored in little-endian byte order on disk, while `Data4` is stored as-is (big-endian per RFC 4122). This differs from both the RFC 4122 wire format (all big-endian) and a naive 16-byte copy. `uuid.UUID(bytes_le=raw)` handles the conversion correctly.
- **`sql_variant` base type**: `uniqueidentifier` can appear inside `sql_variant`. The value starts at offset 2 (16 bytes, `raw[2:18]`).

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: UNIQUEIDENTIFIER=36` |
| Mixed-endian format | `scalars.py: _decode_uuid`; `01_TYPES_LOB.md §5` note on UUID |
| Corroboration | Randolph West storage-internals series (see `CORROBORATION_SOURCES.md`) |
| Columnstore G6 | `00_MASTER.md §G6`; `06_COLUMNSTORE_SEGMENT.md` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.string()` |

---

## 8. Confidence

`[CORROBORATED]` — mixed-endian format confirmed by Randolph West storage-internals series and verified against `typecoverage_full.bak`. Columnstore enc=5 UUID transform confirmed (G6 `[CONFIRMED]`).
