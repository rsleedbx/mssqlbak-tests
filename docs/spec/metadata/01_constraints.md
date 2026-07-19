## Constraints metadata `[EMPIRICAL]`

### Scope
Primary-key, unique, check, default, and foreign-key constraints attached to user
tables.  Covers `CatalogObjects.constraints` and `CatalogObjects.foreign_keys`.

---

### Source catalog tables

| Table | Object ID | Column layout |
|-------|-----------|---------------|
| `sysidxstats` | 54 | `catalog/columns.py: _SYSIDXSTATS_COLS` |
| `sysiscols` | 55 | `catalog/columns.py: _SYSISCOLS_COLS` |
| `syssingleobjrefs` | 74 | `catalog/columns.py: _SYSSINGLEOBJREFS_COLS` |
| `sysobjvalues` | 60 | `catalog/columns.py: _SYSOBJVALUES_COLS` |

---

### Recovery

Source: `catalog/recover.py: recover_catalog_objects`

- **PK / UQ / CHECK / DEFAULT**: rows in `sysidxstats` with `type` in
  `{PK, UQ, C, D}`.  Key-column ids are read from `sysiscols` rows where
  `idmajor == object_id` and `subid == index_id`.
- **Foreign keys**: `syssingleobjrefs` links the FK constraint object to its
  referenced object.  Child and reference column ids come from `sysiscols`.
- **CHECK / DEFAULT definitions**: definition text stored in `sysobjvalues`
  (`valclass=0`, `subobjid=0`, `valnum=0`) for CHECK; `valclass=1` for DEFAULT.

---

### Verification natural key and compared fields

Natural key: `(table FQN, kind, constraint name)`.

Compared fields:

| Field | Notes |
|-------|-------|
| `kind` | `primary key`, `unique constraint`, `check`, `default`, `foreign key` |
| `columns` | Key-column names (GT ⊆ recovered — `sysiscols` includes INCLUDE and XTP implicit cols not in `sys.index_columns`) |
| `definition` | SQL-normalised (whitespace-collapsed); CHECK and DEFAULT only |
| `ref_table` | FK only — referenced table FQN |
| `ref_columns` | FK only |

Source: `metadata_verify.py: verify_constraints`.

---

### Known structural differences

- **Key-column subset rule**: `sysiscols` carries covering-index INCLUDE columns
  and XTP in-memory implicit columns that `sys.index_columns` (used by GT with
  `is_included_column=0`) excludes.  GT columns must be a subset of recovered
  columns; exact equality would produce false mismatches.
- **System-named constraints**: names matching `^DF_|^PK_|^UQ_|^FK_` are
  considered system-named and excluded from the `name` comparison field.
