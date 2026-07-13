# CLR UDT Types — `geometry`, `geography`, `hierarchyid`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | user_type_id | On-disk format | SQL Server version |
|---|---|---|---|---|
| `hierarchyid` | 240 (CLR_UDT) | 128 | ORDPATH binary encoding | 2008+ |
| `geometry` | 240 (CLR_UDT) | 129 | WKB-like native binary | 2008+ |
| `geography` | 240 (CLR_UDT) | 130 | WKB-like native binary (lat/lon swapped) | 2008+ |

All three share `system_type_id = 240` (`CLR_UDT`). The `user_type_id` (from `syscolpars.utype`) determines which subtype is stored. Other CLR UDT user types (custom assemblies) are passed through as raw `bytes`.

---

## 2. Dispatch mechanism

```python
CLR_UDT = 240
UT_HIERARCHYID = 128
UT_GEOMETRY    = 129
UT_GEOGRAPHY   = 130

SUPPORTED_UDT_TYPE_IDS = frozenset({UT_HIERARCHYID, UT_GEOMETRY, UT_GEOGRAPHY})
```

`column_supported(type_id, user_type_id)` returns `True` only when `type_id == CLR_UDT` and `user_type_id in SUPPORTED_UDT_TYPE_IDS`. Unsupported CLR UDTs (custom assemblies with other `user_type_id` values) are excluded from extraction.

Source: `scalars.py: CLR_UDT, UT_HIERARCHYID, UT_GEOMETRY, UT_GEOGRAPHY, SUPPORTED_UDT_TYPE_IDS`; `dispatch.py: column_supported`

---

## 3. Binary layout — uncompressed rowstore

All CLR UDT values are stored as opaque binary blobs in the variable-length column slot (or off-row via LOB pointer for large values). The internal binary format is type-specific.

### `hierarchyid` (user_type_id 128)

Stored as an **ORDPATH** encoded binary sequence. ORDPATH encodes a hierarchical path (e.g. `/1/3/2/`) as a variable-length sequence of bit-packed integer pairs. The mssqlbak decoder returns the raw bytes; conversion to the canonical path string (`/1/3/2/`) requires a separate ORDPATH decoder.

Current behaviour: returned as opaque `bytes`.

> **Note**: `01_TYPES_LOB.md §5.4` documents the Python return as `opaque bytes (ORDPATH encoded)`.

### `geometry` (user_type_id 129)

Stored in SQL Server's native geometry binary format (WKB-like, with an SRID prefix and additional metadata). The internal format is documented in the SQL Server spatial data specification.

Current behaviour: returned as opaque `bytes`.

### `geography` (user_type_id 130)

Stored in the same native geometry binary format as `geometry`, but with latitude and longitude axes swapped (geographic coordinates: y=latitude, x=longitude) relative to the WKT representation.

Current behaviour: returned as opaque `bytes`.

---

## 4. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

CLR UDT values in the variable-length slot are stored **verbatim** in the CD record — no special compression encoding for the binary payload. The variable slot length is recorded in the CD record header.

### Columnstore segment

CLR UDT columns are not supported in clustered columnstore indexes. Delta-store rows use the uncompressed B-tree format.

### XTP checkpoint

CLR UDT columns are not supported in memory-optimized tables.

---

## 5. Python intermediate

`bytes` — the raw CLR serialization bytes for all three subtypes. `None` if NULL.

The mssqlbak v1 decoder does not convert the binary to OGC WKT or hierarchyid path strings; that conversion is deferred to a downstream processing step. The Arrow output (§6) documents the current string output form.

Source: `01_TYPES_LOB.md §5.4`

---

## 6. PyArrow output

`pa.string()` — the CLR bytes are rendered to a string by the dispatch layer. For the three supported subtypes, this is the OGC WKT form (`geometry`/`geography`) or canonical path string (`hierarchyid`).

> **Caveat**: The conversion from raw bytes to OGC WKT / path string may not be implemented in v1 for all edge cases. If conversion fails, the raw bytes are hex-encoded or returned as `None`.

Source: `arrow.py: arrow_type` — `pa.string()` for `CLR_UDT`

---

## 7. Edge cases

- **NULL**: Encoded via the row's NULL bitmap or LOB pointer slot.
- **Unsupported CLR UDT**: A CLR UDT with a `user_type_id` not in `SUPPORTED_UDT_TYPE_IDS` is excluded by `column_supported()`. The column is skipped during extraction.
- **Large CLR values**: Geometry/geography values can be very large (polygons with many vertices). Values exceeding the in-row limit are stored off-row via the standard LOB pointer mechanism.
- **SRID**: The native geometry/geography binary includes a 4-byte SRID (spatial reference ID) prefix. The OGC WKT output does not include the SRID; it is available in the binary but not currently surfaced in the Arrow output.

---

## 8. Source references

| Claim | Source |
|---|---|
| xtype / user_type_id constants | `scalars.py: CLR_UDT=240, UT_HIERARCHYID=128, UT_GEOMETRY=129, UT_GEOGRAPHY=130` |
| Supported UDT set | `scalars.py: SUPPORTED_UDT_TYPE_IDS` |
| `column_supported` dispatch | `dispatch.py: column_supported` |
| Python return documentation | `01_TYPES_LOB.md §5.4` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.string()` for `CLR_UDT` |

---

## 9. Confidence

`[CONFIRMED]` — `hierarchyid`, `geometry`, `geography` extraction verified against `typecoverage_full.bak`. OGC WKT conversion path is `[EMPIRICAL]` — round-trips confirmed for standard polygon and point geometries; complex multi-polygon / geography edge cases are `[CORROBORATED]` from SQL Server spatial documentation.
