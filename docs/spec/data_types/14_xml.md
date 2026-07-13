# XML Type — `xml`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | On-disk format | SQL Server version |
|---|---|---|---|
| `xml` | 241 | MS-BINXML binary blob | 2005+ |

`xml` stores XML document fragments in a proprietary tokenized binary format (MS-BINXML). mssqlbak decodes the binary blob back to a text XML string.

---

## 2. Binary layout — uncompressed rowstore

`xml` is always stored off-row (regardless of size) via the standard LOB pointer mechanism. The variable-length column slot holds an inline-root pointer (struct_type = 4) to a chain of LOB pages.

The assembled byte content is a **MS-BINXML** binary blob:

```
[+0]    0xDF    signature byte 1
[+1]    0xFF    signature byte 2
[+2]    uint8   version  (0x01 = v1, 0x02 = v2)
[+3..]  tokenized XML payload
```

The signature `0xDF 0xFF` and version byte are checked by the decoder before parsing. Details of the tokenized format are in `xmlbin.py` (subject to change; not reproduced here).

Source: `01_TYPES_LOB.md §5.2`; `xmlbin.py`

---

## 3. Storage-path variations

### ROW/PAGE compression (`cmprlevel = 1/2`)

`xml` is always off-row via LOB pointer; the CD record's variable slot contains the LOB pointer bytes, which are **verbatim** (not reencoded). The LOB content itself is not affected by ROW/PAGE compression.

### Columnstore segment

`xml` columns are not supported in clustered columnstore indexes. Delta-store rows use the uncompressed B-tree format.

### XTP checkpoint

`xml` columns are not supported in memory-optimized tables.

---

## 4. Python intermediate

`str` — the decoded XML text as a Python string (UTF-8). `None` if NULL or if the binary XML blob cannot be decoded.

The decoder (`xmlbin.py: decode_binxml`) reconstructs the original XML text from the tokenized binary representation, including element names, attributes, and text nodes.

---

## 5. PyArrow output

`pa.string()` — the XML text string.

Source: `arrow.py: arrow_type` — `pa.string()` for `XML`

---

## 6. Edge cases

- **NULL**: Indicated by the LOB pointer slot being empty or the NULL bitmap being set.
- **Typed XML**: SQL Server supports XML schema collections (`xml(CONTENT mySchema)`). The on-disk format is the same MS-BINXML; schema validation is a server-side concern not reflected in the binary layout.
- **LOB pointer structure**: `xml` always uses the inline-root (struct_type = 4) LOB path — it is never stored in-row. See `01_TYPES_LOB.md §6.1` for the pointer layout.
- **Version byte**: Both v1 (`0x01`) and v2 (`0x02`) MS-BINXML versions are decoded. v2 introduced changes to namespace handling; the decoder handles both.
- **Large XML documents**: Multi-MB XML values follow the standard LOB multi-link chain (ROOT → LARGE_ROOT → DATA records). See `01_TYPES_LOB.md §6.2`.

---

## 7. Source references

| Claim | Source |
|---|---|
| xtype constant | `scalars.py: XML=241` |
| MS-BINXML signature | `01_TYPES_LOB.md §5.2`; `xmlbin.py` |
| LOB pointer structure | `01_TYPES_LOB.md §6.1` |
| Arrow mapping | `arrow.py: arrow_type` — `pa.string()` |

---

## 8. Confidence

`[CORROBORATED]` — MS-BINXML format corroborated from multiple SQL Server internals sources. Decoder verified against `typecoverage_full.bak` and real-world XML fixtures. Version byte and signature are `[CONFIRMED]` against DBCC PAGE output.
