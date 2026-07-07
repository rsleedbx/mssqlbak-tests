# SQL Server `.bak` → Delta Parser — Design

Date: 2026-06-02
Status: Approved (pending written-spec review)

## Goal

Read SQL Server backup files **directly** (no running engine, no restore) and
write their table data to **Delta** tables, to hydrate analytics and — later —
CDC. SQL Server is the first engine; Postgres, MySQL, and Oracle are intended to
plug into the same framework afterward.

## Context and constraints

- We **receive backup files**; the source database is **not reachable** to us.
  Debezium-against-source is therefore not an option; CDC must come from shipped
  incremental artifacts (transaction-log backups) and is deferred to phase 2.
- We can **dictate the backup format** customers produce, but production happens
  elsewhere.
- Backups are **large** (target: 100 GB+). Restore-then-extract needs a live
  engine, ~2× disk, and a full restore before the first row is readable — too
  heavy at this scale. **Direct parsing is the only viable production path.**
- The existing prototype (`mssqlbak/reader.py`) reads MTF *container metadata*
  only (backup type, dates, db/server/machine names). It does **not** decode
  data pages. This design extends it to full row extraction.

## Approach

**Native pure-Python parser is the production path.** A `.bak` is read directly
from storage → typed rows + schema → Delta, with no engine.

**Restore exists only as a dev-time correctness reference** on small (few-GB)
backups we generate ourselves — never on 100 GB+ customer backups. If the parser
cannot read a real backup, that is a parser gap to close, not a restore to fall
back to.

Prior art proving feasibility: OrcaMDF (SQL Server MDF), innodb_ruby /
undrop-for-innodb (MySQL).

### Scope ladder

1. **v1 (minimum):** SQL Server **full** `.bak` → typed rows + schema → Delta.
2. **v1.x (stretch):** **differential** `.bak` reader — merge changed extents
   over the full → fresher snapshot.
3. **Phase 2 (deferred):** transaction-log CDC.
4. **Later:** Postgres / MySQL logical readers behind the same interface; Oracle
   last.

## Component architecture

A pipeline of small, independently-testable modules, each with one job:

```
.bak file
  │
  ▼
[1] mtf      demux MTF blocks → extract the embedded MDF page stream(s)
  │
  ▼
[2] pages    MDF page layer: boot page, page-by-id fetch, GAM/IAM/DCM maps
  │
  ├─────────────► [3] catalog   bootstrap system base tables → schema
  │                               (tables, columns, types, rowsets→alloc units)
  ▼
[4] records  slot-array + record decoder (fixed/var cols, null bitmap, sparse)
  │                └► row-overflow / LOB page resolution
  ▼
[5] types    SQL Server type → (Python value, Spark/Delta type)
  │
  ▼
[6] rows     orchestrator: per table → alloc units → pages → records → row stream
  │
  ▼
[7] sink     Delta writer interface  →  deltalake implementation (batched stream)
```

Cross-cutting:

- **[8] validation/reference** (dev/test only): restore a small `.bak` into an
  ephemeral SQL Server container, extract via query/BCP, diff against parser
  output type-by-type.
- **[9] surface**: CLI (`mssqlbak extract <file.bak> --out <delta-path>`) +
  Python API, on the same core.

Boundaries: `pages` knows nothing about schemas; `catalog` and `records` depend
only on `pages`; `rows` is the only module that assembles a table; `sink` is
swappable (deltalake now, Spark/Databricks later). The existing `reader.py`
becomes `[1] mtf` plus the metadata surface.

## Data flow and schema recovery

### Bootstrap chain (resolves the schema chicken-and-egg)

1. **Boot page** (file 1, page 9) → DB version, default collation, and the
   anchor to the base system tables. Hard-code the (stable, known) schemas of
   the base tables:
   - `sysallocunits` → allocation units: first data page, root page, first IAM
     page, and unit type (`IN_ROW_DATA` / `LOB_DATA` / `ROW_OVERFLOW_DATA`).
   - `sysrowsets` → links objects/indexes to allocation units.
   - `sysrscols` → real column definitions (type, max length, precision, scale,
     null bit, leaf offset).
   - `sysschobjs` → object names & ids.
   - `syscolpars` → column names per object.
2. Read the base tables using those hard-coded schemas, then join to produce,
   for each user table: ordered columns
   `(name, type, max_length, precision, scale, nullable, leaf_offset, is_variable)`
   and the allocation units holding its data.

### Reading a table's rows (streaming)

- Resolve the table's HoBT → its `IN_ROW_DATA` allocation unit.
- **Heap:** walk the IAM page chain → data pages. **Clustered index:** descend
  from root to leftmost leaf, then follow the leaf page linked list.
- **Per page (8 KB):** parse the 96-byte page header, read the slot array at the
  page tail (record offsets), decode each record.
- **Per record:** status bits → fixed-length portion (placed by `leaf_offset`),
  null bitmap, variable-column offset array → variable columns. LOB / `(max)`
  columns store a pointer → follow into `LOB_DATA` (text/image) or
  `ROW_OVERFLOW_DATA` pages and stitch the value.
- Emit a typed row; never hold more than a page (+ current LOB) in memory →
  constant memory on 100 GB+ files.

### Encoding

Non-Unicode `char/varchar` use the column's collation → Windows code page →
Python codec. v1 supports common Latin1/CP1252 + UTF-16 `nchar`; unknown code
pages raise a clear error rather than guessing.

### Detect-and-fail (v1 boundary, no silent corruption)

ROW/PAGE **compression** and **TDE** change the record/page format. v1 detects
them from page/boot metadata and raises a precise error naming the feature, so
they are known parser gaps, not silent data corruption.

### Differential (stretch)

A differential `.bak` carries only changed extents (DCM map). Parse those pages
through the same record decoder and re-emit affected rows for a `MERGE`.

## Correctness strategy (type-coverage fixture + engine diff)

Principle: we insert **known** values (source of truth); the restored engine is
an independent second check. The parser must reproduce both exactly.

### Per-type value matrix

For every supported type, generate at least four rows:

| Row | Value |
|-----|-------|
| `low` | type minimum / boundary (e.g. `int` = -2147483648, `datetime2` = `0001-01-01`) |
| `high` | type maximum / boundary (e.g. `int` = 2147483647, `datetime2(7)` = `9999-12-31 23:59:59.9999999`) |
| `mid` | seeded-random value in range (deterministic RNG seed) |
| `null` | `NULL` (every nullable column) |

### Type coverage (v1)

- Exact numeric: `tinyint, smallint, int, bigint, bit, decimal/numeric(p,s),
  money, smallmoney`
- Approximate: `real, float`
- Date/time: `date, time(n), smalldatetime, datetime, datetime2(n),
  datetimeoffset(n)` — n ∈ {0, 3, 7}; include ±14:00 offset extremes
- Character: `char(n), varchar(n), nchar(n), nvarchar(n)` — empty, 1-char,
  full-length; `nvarchar` includes a multi-byte/emoji surrogate-pair case
- Binary: `binary(n), varbinary(n)`
- Identifier/misc: `uniqueidentifier` (all-zero, all-F, random), `rowversion`
- LOB / `(max)`: `varchar(max), nvarchar(max), varbinary(max)` (+ legacy
  `text/ntext/image` if cheap) — rows = empty, 1 byte/char, and **~1 MB capped**
  (exercises the row-overflow / LOB page path)

Deferred from v1 (must fail loudly): `sql_variant`, `xml`, `hierarchyid`,
`geometry/geography`, sparse-column sets, computed/persisted columns.

### Fixture production & checks

1. Generator spins up an ephemeral SQL Server container, creates one table per
   type-group, inserts the matrix rows from a fixed seed, then `BACKUP DATABASE`
   → a small `.bak` (a few MB even with 1 MB blobs).
2. **Test A (self-truth):** parser reads the `.bak`; assert each decoded value ==
   the known generated value.
3. **Test B (engine diff):** query the same rows from the live container;
   assert parser output == engine output, type-by-type.
4. Commit the small `.bak` as a fast-CI fixture; the generator regenerates it on
   demand (and is the basis for testing new SQL Server versions).

Differential stretch: after the full backup, mutate a known subset, take a
differential `.bak`, assert the parser's merged snapshot matches the engine's
post-mutation state — reusing the same matrix.

## Delta output contract

**Writer interface (swappable):** `Sink` protocol —
`open_table(qualified_name, delta_schema)` → `write_batch(arrow_record_batch)` →
`close()`. v1 implements it with the `deltalake` (delta-rs) library; a
Spark/Databricks-native sink can implement the same protocol later.

**Batching:** `rows` yields typed rows → Arrow `RecordBatch`es (flush by
row-count or byte threshold) → appended to the Delta table. Constant memory,
streaming.

**Table mapping:** one Delta table per source table. Source `schema.table` →
`<out_root>/<schema>/<table>` (Parquet + `_delta_log`). Column names sanitized to
Delta-legal names via a documented, reversible mapping.

**Type mapping (SQL Server → Arrow/Delta):**

| SQL Server | Delta/Arrow | Note |
|---|---|---|
| `tinyint/smallint/int/bigint` | int16/int16/int32/int64 | `tinyint` is unsigned 0–255 → int16 to avoid overflow |
| `bit` | boolean | |
| `decimal/numeric(p,s)`, `money`, `smallmoney` | decimal128(p,s) | money → decimal(19,4) |
| `real/float` | float32/float64 | |
| `date` | date32 | |
| `datetime/smalldatetime/datetime2(n)` | timestamp_ntz (µs) | datetime2(7) is 100 ns → truncated to µs; documented. Opt-in string column to preserve exact. |
| `datetimeoffset(n)` | timestamp (µs, UTC-normalized) | original offset preserved in an optional sidecar column |
| `char/varchar/text` | string | via collation→codepage decode |
| `nchar/nvarchar/ntext` | string | UTF-16 |
| `binary/varbinary/image` | binary | |
| `uniqueidentifier` | string | canonical GUID form |
| `rowversion` | binary(8) | |

**Write mode:** full backup → create/overwrite the table (idempotent).
Differential stretch → `MERGE` on the catalog's primary key; a changed table with
no PK falls back to overwrite from the merged page set (documented limitation).

**Provenance columns** per table: `_src_database`, `_backup_type`,
`_backup_finish_lsn`, `_ingested_at` (also provides differential ordering key).

**Databricks handoff:** the sink writes to a storage URI (`abfss://…`, `s3://…`,
local). Unity Catalog registration (`CREATE TABLE … USING DELTA LOCATION …`) is a
thin, separate step, kept out of the parser so the core runs anywhere.

## Dependencies

| Scope | Package | Why |
|-------|---------|-----|
| parser core | stdlib (`struct`, `dataclasses`, …) | zero-dependency byte parsing |
| Delta write | `deltalake`, `pyarrow` | real Delta tables without Spark |
| validation/reference (dev) | container tooling + `mssql_python` | restore small fixtures, diff |

## Open items / risks

- Reverse-engineered MDF internals are version-sensitive; mitigated by the
  reference fixture and version-tagged regeneration.
- Compression / TDE are out of v1 scope (detect-and-fail).
- `datetime2(7)` µs truncation is a deliberate, documented tradeoff.
