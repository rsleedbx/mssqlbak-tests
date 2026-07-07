# Gap Analysis: What mssqlbak Decodes vs What SQL Server Stores

Updated: Jun 2026 (Run #17 — Tier 1 and Tier 2 items complete; data type coverage is full for SQL Server 2022 and earlier).

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented and tested |
| — | Not applicable — this type has no such storage path by design (e.g. fixed-width types have no LOB path) |
| 🟡 | Implemented but not tested / test is stale |
| ❌ | **mssqlbak gap** — SQL Server supports this path but mssqlbak has not implemented the decoder yet |
| N/A | **SQL Server limitation** — SQL Server does not support this storage path for this type (e.g. legacy types are excluded from columnstore) |
| 🚫 | Intentionally out of scope / impossible without keys |
| 📋 | Test case needed |

---

## 1. Data Types

All SQL Server 2022 and earlier data types are implemented across every supported storage path.  The only open items are two SQL 2025+ types (`json`, `vector`) which require new type IDs and decoders.

### 1a. Numeric & Temporal

| Type | FixedVar | ROW/PAGE | CCI | LOB |
|------|----------|----------|-----|-----|
| `bit` | ✅ | ✅ | ✅ | — |
| `tinyint` | ✅ | ✅ | ✅ | — |
| `smallint` | ✅ | ✅ | ✅ | — |
| `int` | ✅ | ✅ | ✅ | — |
| `bigint` | ✅ | ✅ | ✅ | — |
| `decimal` / `numeric` | ✅ | ✅ | ✅ | — |
| `smallmoney` | ✅ | ✅ | ✅ | — |
| `money` | ✅ | ✅ | ✅ | — |
| `real` | ✅ | ✅ | ✅ | — |
| `float` | ✅ | ✅ | ✅ | — |
| `date` | ✅ | ✅ | ✅ | — |
| `time(n)` | ✅ | ✅ | ✅ | — |
| `smalldatetime` | ✅ | ✅ | ✅ | — |
| `datetime` | ✅ | ✅ | ✅ | — |
| `datetime2(n)` | ✅ | ✅ | ✅ | — |
| `datetimeoffset(n)` | ✅ | ✅ | ✅ | — |

### 1b. String & Binary

| Type | FixedVar | ROW/PAGE | CCI | LOB |
|------|----------|----------|-----|-----|
| `varchar(n)` | ✅ | ✅ | ✅ | ✅ in-row overflow |
| `varchar(max)` | ✅ | ✅ | ✅ off-row | ✅ |
| `nvarchar(max)` | ✅ | ✅ | ✅ | ✅ |
| `varbinary(max)` | ✅ | ✅ | ✅ off-row | ✅ |
| `char(n)` | ✅ | ✅ | ✅ | — |
| `nchar(n)` | ✅ | ✅ SCSU | ✅ | — |
| `nvarchar(n)` | ✅ | ✅ SCSU | ✅ | — |
| `binary(n)` | ✅ | ✅ | ✅ | — |
| `varbinary(n)` | ✅ | ✅ | ✅ | — |
| `char`/`varchar` UTF-8 collation | ✅ | ✅ | — | — |
| `text` | ✅ | ✅ | N/A | ✅ |
| `ntext` | ✅ | ✅ | N/A | ✅ |
| `image` | ✅ | ✅ | N/A | ✅ |

### 1c. Other Fixed-Width

| Type | FixedVar | ROW/PAGE | CCI | LOB |
|------|----------|----------|-----|-----|
| `uniqueidentifier` | ✅ | ✅ | ✅ | — |
| `rowversion` / `timestamp` | ✅ opaque | ✅ | N/A | — |

### 1d. Complex / Special Types

See dedicated subsections below for sql_variant (§1e), xml (§2), and spatial (§3).

| Type | FixedVar | ROW/PAGE | CCI | LOB |
|------|----------|----------|-----|-----|
| `sql_variant` | ✅ | ✅ | N/A | — |
| `xml` | ✅ | ✅ | N/A | ✅ large-LOB stitched |
| `hierarchyid` | ✅ | ✅ inline CLR | N/A | — |
| `geometry` | ✅ | ✅ | N/A | ✅ up to 15 KB+ |
| `geography` | ✅ | ✅ | N/A | ✅ (`spatial_lob_test` id=4, 500-pt MultiPoint ~15 KB; `test_geography_lob_stitches`) |

### 1e. Future Types (SQL Server 2025+)

| Type | Status | Notes |
|------|--------|-------|
| `json` (native, SQL 2025+) | ❌ | New type ID + binary JSON decoder needed |
| `vector` (SQL 2025+) | ❌ | New type ID + float32/float16 array decode needed |

---

### sql_variant Supported Base Types

| Base type in variant | Supported? |
|----------------------|------------|
| int / bigint / smallint / tinyint | ✅ |
| decimal / numeric | ✅ |
| money / smallmoney | ✅ (rows 15/16 in `t_sql_variant`; `test_sql_variant_base_type_roundtrip`) |
| float / real | ✅ |
| char / varchar | ✅ |
| nchar / nvarchar | ✅ |
| binary / varbinary | ✅ |
| date / time / datetime / datetime2 / datetimeoffset / smalldatetime | ✅ |
| uniqueidentifier | ✅ |
| bit | ✅ |
| xml / text / ntext / image / rowversion inside variant | N/A — not supported by SQL Server |

---

## 2. Binary XML Detail

Binary XML (`xtype=241`) is decoded via `xmlbin.py` (updated Jun 2026 — all practical gaps resolved).

| Token / construct | Status | Notes |
|-------------------|--------|-------|
| Element / attribute / text value | ✅ | |
| Namespace prefix / URI | ✅ | |
| CDATA sections | ✅ | normalised to escaped text |
| Comment nodes | ✅ | |
| Processing instructions | ✅ | |
| Unsupported version raises cleanly | ✅ | `test_xmlbin.py::test_unsupported_version_raises` |
| SQL-TEXT / SQL-CHAR / SQL-VARCHAR | ✅ | codepage + varint + bytes → decoded via Python `codecs` |
| SQL-NTEXT | ✅ | textdata (same as SQL-NVARCHAR) |
| SQL-BINARY / SQL-VARBINARY / SQL-IMAGE | ✅ | varint + bytes → base64 |
| SQL-DATETIME | ✅ | 4-byte days + 4-byte 1/300s ticks → ISO 8601 |
| SQL-SMALLDATETIME | ✅ | 2-byte days + 2-byte minutes → ISO 8601 |
| SQL-MONEY / SQL-SMALLMONEY | ✅ | int / 10000, 4 decimal places |
| Typed XML (XSD-typed, v2 blobs) | ✅ | XSD-DECIMAL/DATETIME2/DATE2/BOOLEAN and offset variants |
| Large XML (>8 KB, off-row LOB) | ✅ | `_stitch_lob` reassembles chain; `test_xml_large_lob_round_trip` |
| DOCTYPE / XMLDECL structural tokens | ✅ raise | SQL Server never emits these; raises `NotImplementedError` (correct) |
| Unknown token fallthrough | ✅ raise | Intentional inspect-and-skip |

---

## 3. Spatial Detail

Decoded via `spatial.py` (updated Jun 2026 — all gaps resolved):

| Feature | Status | Notes |
|---------|--------|-------|
| Point / LineString / Polygon 2D | ✅ | |
| MultiPoint / MultiLineString / MultiPolygon | ✅ | |
| GeometryCollection | ✅ | |
| Z coordinate | ✅ | Emitted in WKT; stored as separate array after all XY pairs |
| M coordinate | ✅ | Emitted in WKT |
| CircularString (version-2) | ✅ | `CIRCULARSTRING (…)` via figure_attr=2 |
| CompoundCurve (version-2) | ✅ | `COMPOUNDCURVE (CIRCULARSTRING …, (…))` |
| CurvePolygon (version-2) | ✅ | `CURVEPOLYGON (CIRCULARSTRING …)` |
| FullGlobe (geography only) | ✅ | `FULLGLOBE` — version-2, shape_type=11 |
| Large spatial as LOB | ✅ | 15 KB MultiPoint (500 pts) via `_stitch_lob` |

---

## 4. Storage & Page Features

| Feature | Status | Notes |
|---------|--------|-------|
| Uncompressed heap | ✅ | IAM walk |
| Uncompressed clustered B-tree | ✅ | leftmost-leaf + next-page chain |
| ROW compression | ✅ | All types decoded; 0 skip-table types remaining |
| PAGE compression (prefix + dictionary) | ✅ | CI header parse |
| Unicode (SCSU) compression | ✅ | Inside ROW/PAGE for nchar/nvarchar |
| Clustered columnstore (CCI) | ✅ | enc=1–5; delta store |
| Non-clustered columnstore (NCCI) | ✅ | Same code path; 3 tests |
| Columnstore archival (`COLUMNSTORE_ARCHIVE`, cmprlevel=4) | ✅ | XPRESS-compressed segments; `test_columnstore_archive_decodes` |
| Off-row LOB chain | ✅ | varchar/varbinary/xml/geometry max |
| Off-row LOB in columnstore dict | ✅ | varbinary(max) in CCI |
| Forwarded heap records | ✅ | 3 tests in `test_record_layer.py` |
| Ghost records | ✅ | 3 tests in `test_record_layer.py` |
| Uniquifier column (non-unique CI) | ✅ | 2 tests in `test_record_layer.py` |
| Sparse columns | ✅ | Sparse vector decoded; `sparse_cols` table |
| Sparse column set (xml aggregate) | ✅ | `is_column_set` flag (syscolpars bit 0x02000000); XML synthesised; 2 tests |
| Multi-file NDF | ✅ | file_id dispatch in PageStore; `ndfcoverage_full.bak` fixture + `test_ndf_secondary_file_rows_decoded` |
| Multi-partition table | ✅ | Partition → alloc unit mapping |
| Temporal tables (system-time) | ✅ | 7 tests; current + history extraction |
| COMPRESS() column value | ✅ | Raw gzip varbinary bytes; 3 roundtrip tests |
| Ledger tables (APPEND\_ONLY) | ✅ | Hidden bigint columns decoded as regular columns; 2 tests |
| Graph tables (NODE / EDGE) | ✅ | `is_node`/`is_edge` detected from `sysschobjs.status`; `$node_id`/`$from_id`/`$to_id` synthesised; 4 tests |
| Persisted computed columns | ✅ | Stored as regular columns |
| Non-persisted computed columns | ✅ skip | Omitted from schema (no sysrscols row) |
| Copy-only full backup | ✅ | |
| Differential backup | ✅ | `from_diff_bak` + `merge_diff_files` |
| Always Encrypted columns | ⚠️ | Physical storage is `varbinary` (ciphertext returned as bytes); annotation (`is_encrypted`) and real fixture pending — requires Azure Key Vault or Windows CertStore to provision |
| FileTable | ❌ | FILESTREAM + directory metadata columns |
| In-Memory OLTP (durable) | ❌ | Checkpoint file pairs — completely different format |
| Striped multi-file backup | ✅ | `PageStore.from_stripe([f1, f2])` — pages distributed round-robin by XPRESS chunk across stripe files |
| Mirrored media sets | ❌ | |
| Partial / file / filegroup backup | ❌ | Incomplete page image |
| In-Memory OLTP (SCHEMA\_ONLY) | N/A | No durable data |
| Dynamic Data Masking | N/A | No storage change; mask applied at query time |
| FILESTREAM column | 🚫 | Requires `FILESTREAM` enabled at instance level; Linux containers do not support it — cannot create a real fixture |
| Full-text index | 🚫 | Separate catalog files, not on data pages |
| TDE-encrypted database | 🚫 | Pages encrypted at rest; need DB cert |
| Backup WITH ENCRYPTION | 🚫 | Backup container encrypted |
| Transaction log backup | 🚫 | Log record format, not page parser |

---

## 5. Backup / Container

| Format | Status | Notes |
|--------|--------|-------|
| Uncompressed full backup (MTF) | ✅ | |
| Compressed full backup (XPRESS) | ✅ | |
| Copy-only full backup | ✅ | |
| Differential backup | ✅ | |
| Striped backup (multi-file) | ✅ | `PageStore.from_stripe([f1, f2])` |
| Mirrored media set | ❌ | |
| Partial / filegroup backup | ❌ | Incomplete page image |
| Azure Blob Storage URL backup | ❌ | Network, not local file |
| Encrypted backup (`WITH ENCRYPTION`) | 🚫 | |
| Transaction log backup | 🚫 | Different format |

---

## 6. Documentation Drift

| Doc claim | Reality | Fix needed |
|-----------|---------|------------|
| `README.md`: heaps not supported | Heaps implemented (IAM walk) | ✅ Updated |
| `README.md`: ROW/PAGE compression not supported | Implemented | ✅ Updated |
| `README.md`: columnstore not supported | Implemented | ✅ Updated |
| `BACKUP_COVERAGE.md`: differential PLANNED | Implemented (`from_diff_bak`) | Update doc |
| `CONSTRAINT_COVERAGE.md`: heaps not read | Heaps are extracted | Update doc |
| `tabletypematrix.py` header: diff "PLANNED; tests xfail" | `test_diff` passes | Update comment |

---

## 7. Outstanding Work

All Tier 1 and Tier 2 items are complete.  The remaining work is either Tier 3 (large scope) or blocked on external infrastructure.

### Tier 3: Lower priority / large scope

| Area | Work required |
|------|--------------|
| ~~Striped backup multi-file MTF~~ | ~~Container-layer change; no page-decoder changes~~ |
| Native `json` type (SQL 2025+) | New type ID + binary JSON decoder |
| `vector` type (SQL 2025+) | New type ID + float32/float16 array decode |
| In-Memory OLTP tables | Entirely new checkpoint-file parser |
| Always Encrypted column annotation | Needs Azure Key Vault or Windows CertStore to provision fixture; passthrough already works |
| FileTable | FILESTREAM directory metadata columns |

---

## 8. Quick Count

| Category | Count |
|----------|-------|
| Types fully implemented & tested (all storage paths, SQL Server ≤ 2022) | 35/35 |
| Types partially implemented (1+ path missing) | 0 |
| New types requiring new decoders (SQL 2025+) | 2 (`json`, `vector`) |
| Storage features implemented & tested | 26 |
| Storage features implemented, annotation pending | 1 (Always Encrypted passthrough) |
| Storage features not yet implemented | 3 |
| Intentionally out of scope | 6 (FILESTREAM added — requires instance-level config unavailable on Linux) |
