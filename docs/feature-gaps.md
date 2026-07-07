# mssqlbak — Feature Gaps

Untested, partial, and unsupported features across data types, backup formats,
storage, and the format spec.

**Risk legend:** E = error/crash · S = silent wrong data · M = missing rows/tables · L = metadata only

**Status legend:**

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented |
| 🟡 | Partial — works but incomplete |
| ❓ | Untested — code exists, no fixture confirming behavior |
| ❌ | Not Supported — known gap, not yet implemented |
| 🚫 | Not Feasible — external infrastructure required |
| ⚠️ | Inherent Limit — structural limitation of the format |

---

## Data Types

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| `json` (SS2025, type_id 244) — binary decode | 🟡 | S | Returned as raw bytes. No binary-JSON-to-text decoder; consumer must unwrap the proprietary blob. |
| `vector(N)` (SS2025) — float array unwrap | 🟡 | S | Returned as raw bytes (8-byte header + N × float32). No automatic list-of-float decode. |
| Always Encrypted — plaintext recovery | 🟡 | S | Ciphertext returned as bytes or None. Requires CEK from Azure Key Vault / Windows CertStore. |
| Unknown `sql_variant` base type | ❌ | E | Raises `NotImplementedError` when `sql_variant` stores an unrecognized subtype (`types.py:458`). |
| Unknown CLR UDT `user_type_id` | ❌ | E | Non-geometry/geography/hierarchyid CLR UDT raises `NotImplementedError`; table is skipped (`types.py:564`). |
| Columnstore enc=5 variable-length MAX (bpv=0) | 🟡 | M | `varchar(max)`/`varbinary(max)` in enc=5 off-row segments returns `None` per row. Fixed-width enc=5 is fully decoded. |

---

## Backup Format

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| TDE-encrypted backup | ❌ | E | Page images encrypted; raises `EncryptedBackupError`. Requires server certificate — out of scope. |
| Backup `WITH ENCRYPTION` (container-level) | ❌ | E | Container encrypted before page layer. Clean error added (F-1); crash-free fixture A-2 still open. |
| ZSTD backup compression (SS2025) | ❌ | E | SS2025 added ZSTD as a compression option. Not handled; may crash (fixture A-1 open). |
| Transaction log backup (`BACKUP LOG`) — "incremental" | ❌ | M | Log backups contain log records, not data pages. This is what other systems call "incremental" — chained log backups for point-in-time recovery. Needed for future PITR / CDC; currently out of scope. Differential (cumulative changes since last full) is ✅ supported via `from_diff_bak`. |
| File / filegroup backup | ❌ | E | Partial backup of specific files. PRIMARY filegroup may be absent; fixture A-3 (crash) open. |
| Partial backup (`READ_WRITE_FILEGROUPS`) | ❌ | M | Skips read-only filegroups; incomplete page image cannot reconstruct the full database. |
| Mirrored media set | ❌ | M | Redundant backup copies across media families. No merge/selection path implemented. |
| File-snapshot backup (Azure Blob) | ❌ | M | Snapshot-based backups use a different metadata structure; not handled. |
| Backup-kind `block_attributes` (VC01) | ❓ | M | The raw `block_attributes` byte in the MTF container header is read but only NORMAL (0x04) has a verifier sidecar confirming the byte value. Differential (✅ implemented via `from_diff_bak`) and copy-only (✅ implemented) are both supported at the page level; the VC01 gap is about verifying the metadata byte itself, not restore capability. |
| Large-database sparse extent layout | ❌ | E | Very large databases use a sparse extent bitmap. Raises 'not supported' (`pages.py:578,806`). |
| Non-mmap `BakReader` row extraction | ❌ | E | Streaming `BakReader` path raises `NotImplementedError`; only mmap-backed `PageStore` supported (`mtf.py:394`). |

---

## Storage Features

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| In-Memory OLTP / Hekaton (durable tables) | ❌ | M | Durable data in checkpoint file pairs, not B-tree pages. Detected and skipped; new parser needed. |
| FILESTREAM column | 🚫 | M | FILESTREAM requires NTFS + Windows instance flag. Cannot create fixtures on Linux/Podman containers. |
| FileTable | ❌ | E | FILESTREAM + directory-metadata pseudo-columns. Schema enumeration may crash (fixture B-2 open). |
| Full-text index data | ❌ | N/A | Full-text catalog files are separate from `.bak` data pages. Out of scope by design. |
| External tables (PolyBase) | ❌ | N/A | No local row data. Metadata only; skipped in `classify_table`. |
| Vector index (SS2025) | ❌ | N/A | New similarity-search index. Index structures are not row data; no extraction impact. |
| `XML_COMPRESSION` off-row (SS2022) | ❓ | S | SS2022 `XML_COMPRESSION` may produce off-row LOBs in a different format. Fixture H-5 open. |
| LOB data on absent secondary NDF file | 🟡 | S | LOB chain fragment on absent file returns empty bytes instead of raising. |

---

## Columnstore

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| Segment blob preamble bytes 0–33 (G43) | 🟡 | M | Offsets 34 (bpv) and 36 (nw) confirmed. Bytes 0–33 opaque; semantics unknown but decodes correctly empirically. |
| Columnstore `block_size` != 512 (VC05) | ❓ | S | Parser assumes 512 in all observed fixtures. No assertion guards against other values. |
| Columnstore ARCHIVE blob flags != 0 (VC06) | ❓ | M | ARCHIVE 12-byte frame flags always 0. Non-zero value semantics unknown; no guard. |

---

## LOB / Off-row

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| LOB `btyp=3` (DATA leaf) — verifier sidecar | ❓ | S | `btyp=3` implicitly traversed but no DBCC PAGE verifier sidecar (VC02). `btyp=2` and `btyp=5` confirmed. |
| LOB `btyp=2` `max_links=4` INTERNAL node (VC03) | ❓ | S | Only 2-slot (`max_links=2`) internal nodes observed. 4-slot variant unconfirmed. |

---

## Schema / DDL

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| DDL reconstruction (`CREATE TABLE` scripts) | ✅ | N/A | `mssqlbak schema` command emits full `CREATE TABLE` with PK/FK/CHECK/DEFAULT/UQ constraints and standalone indexes. See [`docs/260623-1-ddl.md`](260623-1-ddl.md). |
| View / stored procedure definitions | ✅ | N/A | `recover_module_definitions` extracts full SQL text from `sysobjvalues` for views (`V`), procs (`P`), functions (`FN`/`IF`/`TF`), and triggers (`TR`). |
| SSMS-style hierarchical DDL export | ✅ | N/A | `mssqlbak schema --explode` writes `Tables/`, `Views/`, `Stored Procedures/`, `Functions/`, `Triggers/`, `Schemas/`, `Types/`, `Sequences/`, `Synonyms/`, `Security/` directories. |
| Schema / namespace inventory | ✅ | N/A | `recover_schemas` reads `sysclsobjs` class=0x32; `emit_create_schemas` emits `CREATE SCHEMA … AUTHORIZATION …`. |
| User-defined table types (`TT`) | ✅ | N/A | `recover_user_table_types` + `emit_create_type_as_table` emit `CREATE TYPE … AS TABLE`. |
| Sequences (`SO`) | ✅ | N/A | `recover_sequences` + `emit_create_sequence`. Numeric parameters (START WITH, INCREMENT) deferred — require additional internal table read. |
| Synonyms (`SN`) | ✅ | N/A | `recover_synonyms` + `emit_create_synonym`. Target extracted from `sysobjvalues` valclass=1. |
| Database principals and roles | ✅ | N/A | `recover_principals` reads `sysowners`; emitted as comment-block inventory via `--principals` (server logins live in `master`, not user `.bak`). |
| Object-level permissions | ✅ | N/A | `recover_object_permissions` reads `sysprivs`; emitted in principals report. |
| Linked-server reference detection | ✅ | N/A | `detect_linked_server_refs` scans module text for `[server].[db].[schema].[obj]` four-part names (`--detect-deps` flag). |
| Backup metadata: machine name (NetBIOS) | ❌ | L | No stable anchor in the proprietary SSET config stream. Not portably parseable. |
| Backup metadata: LSNs (first/last/checkpoint) | ❌ | L | LSN fields not stored verbatim in the current SSET MTF implementation. |
| Collation clauses on columns | ❌ | N/A | Collation ID → name lookup table not yet implemented; `COLLATE` clause omitted from emitted DDL. |
| Computed column expressions | ❌ | N/A | Expression text is in `sysobjvalues`; plumbing into `Column` and DDL emission is deferred. |
| Temporal `PERIOD FOR SYSTEM_TIME` clause | ❌ | N/A | `generated_always_type` on `Column` is available; the period-column pair detection is deferred. |
| Sequence numeric parameters (START WITH, etc.) | ❌ | N/A | Requires reverse-engineering the sequence-value internal table beyond `sysschobjs`. |
| Role membership (`sp_addrolemember`) | ❌ | N/A | `sysprivs` class encoding for membership grants needs further reverse-engineering. |
| CLR assembly binary blob extraction | ❌ | N/A | Assembly name + version available via `sysclsobjs`; assembly binary extraction is a separate project. |

---

## Platform / Version

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| Pre-2008 system catalog page format (V02) | 🟡 | M | SQL Server 2006 backup skips all 5 tables as 'no-columns'. 2006 catalog layout (`syscolpars` offsets) unknown. |
| Log-tail MinLSN window: pre-dated dirty rows (`dirtycoverage_large_dirty`) | ⚠️ | S | 8 rows whose INSERT log record predates MinLSN cannot be detected and suppressed. They appear as committed rows in output. Xfail in all 4 SS version correctness docs. |
| Log-tail VLF window: late-concurrent rows (`dirtycoverage_concurrent`) | ⚠️ | S | Concurrent INSERTs committed after their page was captured but before the VLF window opens may be missing (1–2 rows). Timing-dependent; passes most runs. Xfail in all 4 SS version correctness docs. |

---

## Format Unknowns

| Feature | Status | Risk | Notes |
|---------|--------|:----:|-------|
| MSSQLBAK v2 16-byte field @+8 (G02) | ❓ | L | Field in 32-byte v2 record header. Possibly a hash or pointer; meaning unknown. |
| MSSQLBAK version word 2 \[12:16\] (G04/VC04) | ❓ | L | Values 0/1/2 observed across SS versions but not catalogued per fixture. Meaning unknown. |
| MSSQLBAK tag bits 0–15 (G01) | ❓ | L | Heuristically inferred; no verifier confirms bit meanings. |
| MSSQLBAK v2 `prev_uncompressed_size` @+0 (G03) | ❓ | L | Guessed field name; not confirmed against verifier. |

---

## Highest-priority gaps

### 🔴 Crash / error risk (E)

TDE backup, ZSTD compression (SS2025), file/filegroup backup on absent PRIMARY,
FileTable schema crash, large-database sparse extent layout, unknown CLR UDT /
`sql_variant` subtypes. Need clean-error handling or explicit skip contracts.

### 🟡 Silent wrong data (S)

Backup-kind VC01 metadata byte unverified by sidecar (differential and copy-only
restore both work; the concern is that the raw `block_attributes` byte interpretation
has no verifier confirmation), Always Encrypted columns returned as `None`/bytes
without annotation, `json`/`vector` returned as raw bytes without semantic decode,
enc=5 variable-MAX columns silently return `None` per row.

### 🔵 Missing rows / tables (M)

In-Memory OLTP durable tables (checkpoint-file storage engine, separate parser needed),
FILESTREAM/FileTable (Linux not feasible), file/filegroup/partial/mirrored backup
formats, and the pre-2008 catalog layout (V02).
