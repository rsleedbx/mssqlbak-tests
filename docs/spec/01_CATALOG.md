## 4. System Catalog Base Tables

Bootstrapped from the boot page without SQL Server.  The bootstrap uses fixed
base-table declaration lists in `catalog.py`, then uses recovered `sysrscols`
rows to decode user-table records.

### 4.1 Bootstrap order `[CORROBORATED]`

1. Scan page 9 (`m_type 13`) for the `sysallocunits` root page pointer.
2. Walk `sysallocunits` (object 7) to find all page chains.
3. Walk `sysrscols` (object 3) to get column leaf offsets.
4. Walk `sysrowsets` (object 5) to map rowsets to objects.
5. Walk `sysschobjs` (object 34) for object names/types.
6. Walk `syscolpars` (object 41) for column metadata.

### 4.2 Object IDs `[CORROBORATED]`

| Object | `obj_id` | Description |
|--------|----------|-------------|
| `sysrscols` | 3 | Column storage layout (leaf offsets) |
| `sysrowsets` | 5 | Rowset → object/index, compression level |
| `sysallocunits` | 7 | Page chains (`pgfirst`, `pgroot`, `pgfirstiam`) |
| `sysschobjs` | 34 | Object catalog (name, type) |
| `syscolpars` | 41 | Column metadata (xtype, length, sparse, etc.) |
| `sysidxstats` | 54 | Index / constraint metadata |
| `sysiscols` | 55 | Index key columns |
| `sysobjvalues` | 60 | DEFAULT / CHECK definition text |
| `syscscolsegments` | 62 | Columnstore segment metadata |
| `syscsdictionaries` | 63 | Columnstore dictionary metadata |
| `syssingleobjrefs` | 74 | FK column mappings |

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
> Confirmed on SQL Server 2022.  Sidecar: `tests/fixtures/probe/G22.json`.

---

