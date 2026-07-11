## 4. System Catalog Base Tables

Bootstrapped from the boot page without SQL Server.  The bootstrap uses fixed
base-table declaration lists in `catalog.py`, then uses recovered `sysrscols`
rows to decode user-table records.

### 4.1 Bootstrap order `[CORROBORATED]`

The bootstrap follows a strict dependency order (`catalog.py: _bootstrap`,
`recover_schema`):

1. **Boot page 9** (`m_type 13`, page 9 of file 1).  The primary path reads
   the `sysallocunits` first-page pointer at **fixed byte offset 516** of
   boot-page record 0 (`_SYSALLOCUNITS_PTR_OFF = 516`, G14 `[CONFIRMED]`);
   a full-scan fallback handles unknown layouts.  Additional fields also read
   at this step:
   - `DBINFO.dbi_collation` (database-default collation id) at byte **392**
     (`_DBI_COLLATION_OFF`, G57 `[CONFIRMED]`).
   - Three LSN fields: `dbi_checkptLSN` @348, `dbi_differentialBaseLSN` @360,
     `dbi_dbbackupLSN` @372, each `struct("<IIH")` (10 bytes).
2. **`sysallocunits` (object 7)** — heap, rowset id = `7 << 16`.  Builds the
   `owner_to_allocs` map: `{rowset_id: [AllocUnit(first_page, root_page, ...)]}`
   for every allocation unit in the database.  All further page lookups go
   through this map.
3. **`sysrowsets` (object 5)** — heap, rowset id = `5 << 16`.  Builds
   `obj_to_rowsets`: `{object_id: [(index_id, rowset_id), ...]}` and records
   `cmprlevel` and `rcrows` per rowset.  Also detects XTP (In-Memory OLTP)
   object ids by the sysrowsets `status` bit `0x100`.
   **Must precede sysrscols** (the leaf-page locator for sysrscols uses the
   rowset map built in this step).
4. **`sysrscols` (object 3)** — heap.  Provides `leaf_offset`, `null_bit`,
   `bit_shift`, and `status` (NOT NULL flag bit `0x80`) for every physical
   column slot in every rowset.  Indexed by `rscolid` (primary) with a
   `hbcolid` fallback for legacy partition-key rscolids
   (`_LEGACY_RSCOLID_THRESHOLD = 4096`).
5. **`sysschobjs` (object 34)** — clustered B-tree.  Provides user-table
   object names (`type = 'U '`).  Located via `sysrowsets` → B-tree root,
   descended to leftmost leaf via `_leftmost_leaf_from_root`.
6. **`syscolpars` (object 41)** — clustered B-tree.  Provides column type
   metadata (`xtype`, `length`, `collationid`, `status`, `scale`, `prec`,
   `utype`).
7. **`sysclsobjs` (object 64)** — clustered B-tree.  Schema-name lookup:
   `class=0x32` rows map `schema_id → schema_name`.
8. Optional auxiliary tables: `sysidxstats` (54), `sysiscols` (55),
   `syssingleobjrefs` (74) for FK/unique-key metadata; `sysobjvalues` (60)
   for DEFAULT definitions; `sysowners` (27) and `sysprivs` (29) for
   principals and permissions.

### 4.2 Object IDs `[CORROBORATED]`

| Object | `obj_id` | Decoded by | Description |
|--------|----------|-----------|-------------|
| `sysrscols` | 3 | `catalog.py` (`_OBJID_SYSRSCOLS`) | Column storage layout (leaf offsets, null-bitmap positions) |
| `sysrowsets` | 5 | `catalog.py` (`_OBJID_SYSROWSETS`) | Rowset → object/index, compression level, row count |
| `sysallocunits` | 7 | `catalog.py` (`_OBJID_SYSALLOCUNITS`) | Page chains (`pgfirst`, `pgroot`, `pgfirstiam`) |
| `sysowners` | 27 | `catalog.py` (`_OBJID_SYSOWNERS`) | Database principals |
| `sysprivs` | 29 | `catalog.py` (`_OBJID_SYSPRIVS`) | Object-level permissions |
| `sysschobjs` | 34 | `catalog.py` (`_OBJID_SYSSCHOBJS`) | Object catalog (name, type `'U '` = user table) |
| `syscolpars` | 41 | `catalog.py` (`_OBJID_SYSCOLPARS`) | Column metadata (xtype, length, sparse, etc.) |
| `sysidxstats` | 54 | `catalog.py` (`_OBJID_SYSIDXSTATS`) | Index / constraint metadata |
| `sysiscols` | 55 | `catalog.py` (`_OBJID_SYSISCOLS`) | Index key columns |
| `sysobjvalues` | 60 | `catalog.py` (`_OBJID_SYSOBJVALUES`) | DEFAULT / CHECK definition text |
| `syscscolsegments` | 62 | `columnstore/storage/segment_meta.py` | Columnstore segment metadata (not in catalog.py) |
| `syscsdictionaries` | 63 | `columnstore/storage/segment_meta.py` | Columnstore dictionary metadata (not in catalog.py) |
| `sysclsobjs` | 64 | `catalog.py` (`_OBJID_SYSCLSOBJS`) | Schema name → id mappings (`class=0x32` rows) |
| `syssingleobjrefs` | 74 | `catalog.py` (`_OBJID_SYSSINGLEOBJREFS`) | FK column mappings |

**G21 resolved** — see Guess Register §10.  The object IDs are stable across SQL Server 2006–2025 based on the 50-sample real-world corpus.

### 4.3 Base-table column layouts `[CORROBORATED]`

**Important:** the parser does **not** hardcode per-field byte offsets.  It
declares each base table's column list in `catalog.py` and lets the helper
`_layout()` compute offsets with one rule:

- Fixed-length columns are packed contiguously **from byte 4** (right after the
  4-byte FixedVar record prefix, §3.1) in **declaration order**.
- Variable-length columns (`sysname`, `varbinary`, `nvarchar`) take no fixed
  space; they are indexed in declaration order and read from the record's
  variable section.
- `null_index` is the declaration ordinal.

The **declaration order tables below are the source of truth**; the offset
column is derived, shown only for cross-checking against `DBCC PAGE`.  The
resulting fixed-region size matches each page's `pminlen` (asserted in tests).
Update the declaration list in `catalog.py`; do not add a separate magic offset
table in the docs.

Source: `catalog.py: _layout`, `_SYSRSCOLS_COLS`, `_SYSROWSETS_COLS`,
`_SYSCOLPARS_COLS`, `_SYSSCHOBJS_COLS`, etc.

#### sysrscols (obj 3) — `_SYSRSCOLS_COLS`
Fixed region = 54 bytes (matches `pminlen`).

| Decl # | Field | Type | Derived offset |
|--------|-------|------|----------------|
| 0 | rsid | bigint | 4 |
| 1 | rscolid | int | 12 |
| 2 | hbcolid | int | 16 |
| 3 | rcmodified | bigint | 20 |
| 4 | ti | int | 28 |
| 5 | cid | int | 32 |
| 6 | ordkey | smallint | 36 |
| 7 | maxinrowlen | smallint | 38 |
| 8 | status | int | 40 (bit `0x80` = NOT NULL) |
| 9 | offset | smallint | 44 (the column's leaf offset; `< 0` ⇒ variable) |
| 10 | nullbit | smallint | 46 |
| 11 | bitpos | smallint | 48 (1-based null-bitmap position = `Column.null_bit`) |
| 12 | colguid | varbinary | variable col 0 |
| 13 | ordlock | int | 50 |

#### sysrowsets (obj 5) — `_SYSROWSETS_COLS`

| Decl # | Field | Type | Derived offset |
|--------|-------|------|----------------|
| 0 | rowsetid | bigint | 4 |
| 1 | ownertype | tinyint | 12 |
| 2 | idmajor | int | 13 (object id) |
| 3 | idminor | int | 17 (index id) |
| 4 | numpart | int | 21 |
| 5 | status | int | 25 |
| 6 | fgidfs | smallint | 29 |
| 7 | rcrows | bigint | 31 (row-count estimate) |
| 8 | cmprlevel | tinyint | 39 (0=NONE 1=ROW 2=PAGE 3=CCI 4=CCI_ARCHIVE) |

> **`cmprlevel` `[CONFIRMED]` — G20:** `DBCC PAGE(TypeCoverage, 1, 17, 3) WITH TABLERESULTS`
> reports `Slot 0 Column 9 Offset 0x27 Length 1 cmprlevel 0`.  0x27 = 39 decimal,
> matching the `_layout`-computed offset.  Sidecar: `tests/fixtures/probe/G20.json`.

#### syscolpars (obj 41) — `_SYSCOLPARS_COLS`

| Decl # | Field | Type | Derived offset |
|--------|-------|------|----------------|
| 0 | id | int | 4 |
| 1 | number | smallint | 8 |
| 2 | colid | int | 10 |
| 3 | name | sysname | variable col 0 |
| 4 | xtype | tinyint | 14 (system type id, §5) |
| 5 | utype | int | 15 (user type id; CLR subtype) |
| 6 | length | smallint | 19 (`max_length`; -1 for MAX) |
| 7 | prec | tinyint | 21 |
| 8 | scale | tinyint | 22 |
| 9 | collationid | int | 23 (bit `0x100` = UTF-8) |
| 10 | status | int | 27 (`0x01000000`=sparse, `0x02000000`=column_set) |
| 11 | maxinrow | smallint | 31 |
| 12 | xmlns | int | 33 |
| 13 | dflt | int | 37 (DEFAULT constraint object id) |
| 14 | chk | int | 41 |
| 15 | idtval | varbinary | variable col 1 (IDENTITY seed/increment) |

Other declared base tables (same `_layout` rule): `_SYSALLOCUNITS_COLS`,
`_SYSSCHOBJS_COLS`, `_SYSIDXSTATS_COLS`, `_SYSISCOLS_COLS`,
`_SYSSINGLEOBJREFS_COLS`, `_SYSOBJVALUES_COLS` — see `catalog.py` for the
declaration lists, each annotated with the fixture that verified it.

### 4.4 Partition rowset id seed `[CONFIRMED]`

System-table heap rowsets have `rowsetid = object_id << 16`.  This is the seed
from which the catalog bootstrap locates each base table's pages.

> **Verifier (G22):** `sys.allocation_units` in `TypeCoverage` shows
> `container_id = 327680 = 5 × 65536` for `sys.sysrowsets` (object_id 5),
> `196608 = 3 × 65536` for `sys.sysrscols` (object_id 3),
> `458752 = 7 × 65536` for `sys.sysallocunits` (object_id 7).
> Confirmed on SQL Server 2022.  Sidecar: `tests/fixtures_2022/probe/G22.json`.

---

### 4.5 Catalog page-walking algorithms `[EMPIRICAL]`

Source: `catalog.py: _catalog_iam_pages`, `_walk_leaf`, `_primary_records_from_page`.

**IAM walk** (`_catalog_iam_pages`):

1. Find the `pgfirstiam` pointer for the allocation unit from `sysallocunits`.
2. Read SPA slots at offset 140 (`_IAM_SPA_OFFSET`, 8 × 6-byte `(file_id u16, page_id u32)`) to collect mixed-extent pages.
3. Read the extent bitmap at offset 194 (`_IAM_BITMAP_OFFSET`): each set bit → pages `[b×8 .. b×8+7]`.
4. Follow the IAM `next_page` chain in the page header.

**Primary-record filter** (`_primary_records_from_page`):

- Skip slots where `slot_offset >= free_data` (ghost/version rows above the free-space marker).
- Skip records where `raw[0] & 0x07 != 0` (not `PRIMARY_RECORD` type).

**B-tree descent for clustered base tables** (`_Bootstrap._leftmost_leaf_from_root`):

Given the root page from the `pgroot` allocation-unit pointer:
- While `page.header.m_type == 2` (INDEX): read the 6-byte child pointer from the **last 6 bytes** of slot-0's record: `page_id = struct.unpack_from("<I", rec, len(rec)-6)[0]`, `file_id = struct.unpack_from("<H", rec, len(rec)-2)[0]`.
- Stop when `m_type != 2` (leaf data page).

---

### 4.6 Legacy and dropped-column recovery `[EMPIRICAL]`

Source: `catalog.py: _reconstruct_legacy_rscols`, `_infer_dropped_col_offsets`.

**Legacy sysrscols reconstruction** (SQL Server 2000 → 2005+ upgrades):

When `sysrscols` is empty for a table (`rscolid`-lookup misses), the parser
synthesizes storage metadata from `syscolpars` alone via
`_reconstruct_legacy_rscols`:

1. Sort columns by `colid`.
2. BIT columns are packed 8-per-byte immediately after all other fixed columns.
3. Fixed-length non-BIT columns are packed from byte 4 (after the 4-byte row
   header) in colid order; size = `max(1, abs(length))`.
4. Variable-length columns get negative `leaf_offset` values (−1, −2, …).
5. All columns are treated as nullable (cannot recover NOT NULL without sysrscols).

**Dropped-column offset inference** (`_infer_dropped_col_offsets`):

When a fixed-length column is dropped from a SQL Server table, the `sysrscols`
row is removed but the bytes remain in existing rows.  The gap detection:
1. Collect the `leaf_offset` values present in `sysrscols` for a rowset.
2. Compute expected fixed-column boundaries based on `syscolpars` column sizes.
3. Where a gap exists in the offset sequence, match it to a `syscolpars` column
   by size and colid order — that column is dropped but its bytes are still
   physically present in old rows.

---

### 4.7 rscolid / hbcolid dual lookup `[EMPIRICAL]`

Source: `catalog.py: _LEGACY_RSCOLID_THRESHOLD = 4096`, `recover_schema`.

`sysrscols` has two column-id fields:
- `rscolid` — physical slot index in the partition's storage (sequential, starts near 1).
- `hbcolid` — logical column id matching `syscolpars.colid`.

In modern tables the two are the same or very close.  In tables with legacy
partition-key rowsets (from SQL Server 2000-era schemas migrated to 2005+),
`rscolid` is a large partition-key-derived value (`>> 4096`).

The lookup strategy: try `rscolid` first; if no match and `rscolid > 4096`,
fall back to looking up by `hbcolid`.  The threshold prevents the hbcolid
fallback from firing on computed/dropped columns where `hbcolid` coincidentally
equals a modern `rscolid`.

---

### 4.8 XTP (memory-optimized) table detection `[EMPIRICAL]`

Source: `catalog.py: _bootstrap`, line ~1504; `catalog.py: recover_schema`, line ~2200.

A user table is memory-optimized (XTP) when:
1. `sysrowsets.status & 0x100` is set for any of the table's rowsets.
2. **All** allocation-unit first/root/IAM page pointers for those rowsets are
   null (`(0,0)`).  XTP tables have no B-tree pages — their data lives in
   checkpoint files, not the page stream.

The resulting `Table.is_memory_optimized = True` flag causes the extractor to
skip the normal page-walk and route to the XTP checkpoint scanner instead
(`xtp.py: decode_cfp_log_records`).

---

