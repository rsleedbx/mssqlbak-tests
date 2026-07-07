# Constraint & index coverage

How SQL Server encodes keys, indexes and constraints in a backup, and what
the parser recovers.  **Generated** by `python -m tools.constraint_coverage`
from the committed constraint fixture (one constraint isolated per table);
`tests/test_constraint_coverage.py` fails if the decode regresses or this
file drifts.

Sibling coverage docs: [TYPE_COVERAGE.md](TYPE_COVERAGE.md) (column data), [METADATA_COVERAGE.md](METADATA_COVERAGE.md) (backup metadata), [BACKUP_COVERAGE.md](BACKUP_COVERAGE.md) (backup types), anchored by [BYTE_MAP.md](BYTE_MAP.md).

## Where constraints live in the backup

A `.bak` is a physical page image, so every constraint and index is present in the system base-table pages (and, for indexes, as physical B-tree pages):

- **`sysschobjs` (object id 34)** — one row per *constraint object*: `type` ∈ {`PK`, `UQ`, `F`, `C`, `D`} with `pid` = the parent table's object id. A plain index is **not** a constraint and produces no row here.
- **`sysidxstats` (object id 54)** — one row per index/heap: `type` 0=heap, 1=clustered, 2=nonclustered; `status` bits `0x20`=primary key, `0x08`=unique, `0x40`=unique constraint.
- **`sysiscols` (object id 55)** — one row per index key column: `intprop` is the table column id, `subid` the key ordinal.
- **Physical index pages** — a clustered index *is* the table's data pages; nonclustered indexes get their own B-tree pages (separate rowsets), classified *skippable* in the byte map and never read as table rows.

For a full database -> Delta restore the parser reads the clustered data rowset (index_id=1) or heap (index_id=0, traversed via IAM chain); FK/CHECK/DEFAULT are metadata-only and do not affect row decoding.

**Coverage:** 9/9 constraint-variant tables extract their rows (clustered indexes and heaps; both paths supported); all 9 have their constraints and indexes decoded from the catalog.

## Per-variant encoding (recovered from the fixture)

| Variant table | Constraint under test | `sysschobjs` objects | Indexes (`sysidxstats`/`sysiscols`) | Rows |
|---------------|-----------------------|----------------------|-------------------------------------|------|
| `cc_pk` | primary key (clustered) — baseline | `PK`:PK__cc_pk__3213E83F1F80E58A | clustered [PK, unique] on (id) | yes |
| `cc_fk_parent` | FK target (clustered PK) | `PK`:PK__cc_fk_pa__3213E83F035FB219 | clustered [PK, unique] on (id) | yes |
| `cc_pk_nonclustered` | primary key (nonclustered) → heap | `PK`:PK__cc_pk_no__3213E83EBE1457AB | heap (no clustered index); nonclustered [PK, unique] on (id) | yes |
| `cc_unique_constraint` | unique constraint | `PK`:PK__cc_uniqu__3213E83FFA6EBECC, `UQ`:uq_code | clustered [PK, unique] on (id); nonclustered [unique-constraint] on (code) | yes |
| `cc_unique_index` | unique index (no constraint object) | `PK`:PK__cc_uniqu__3213E83F930E71C0 | clustered [PK, unique] on (id); nonclustered [unique] on (code) | yes |
| `cc_index_nonclustered` | nonclustered index (no constraint object) | `PK`:PK__cc_index__3213E83FE54B696C | clustered [PK, unique] on (id); nonclustered on (code) | yes |
| `cc_fk_child` | foreign key | `PK`:PK__cc_fk_ch__3213E83FFFF57787, `F`:fk_code | clustered [PK, unique] on (id) | yes |
| `cc_check_constraint` | check constraint | `PK`:PK__cc_check__3213E83F032D880F, `C`:ck_code | clustered [PK, unique] on (id) | yes |
| `cc_default_constraint` | default constraint | `PK`:PK__cc_defau__3213E83F24647F0B, `D`:df_name | clustered [PK, unique] on (id) | yes |

## Key findings

- **Primary key** always yields an auto-named `PK` object in `sysschobjs`; a *clustered* PK is the data rowset (`indid=1`), a *nonclustered* PK leaves a heap (`indid=0`) plus a separate nonclustered index.
- **Unique constraint** vs **unique index**: both create a unique nonclustered index, but only the constraint adds a `UQ` object (`status` bit `0x40`); a bare `CREATE UNIQUE INDEX` does not.
- **Plain nonclustered index** adds an index with no `sysschobjs` object and no unique bit.
- **Foreign key / check / default** add `F` / `C` / `D` objects with no new index or data pages.

See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.
