## Indexes metadata `[EMPIRICAL]`

### Scope
All non-heap indexes on base user tables (`type = 'U'` in `sysschobjs`).
Indexed views and system-schema objects are excluded to match the GT collection
scope.

---

### Source catalog tables

| Table | Object ID | Column layout |
|-------|-----------|---------------|
| `sysidxstats` | 54 | `catalog/columns.py: _SYSIDXSTATS_COLS` |
| `sysiscols` | 55 | `catalog/columns.py: _SYSISCOLS_COLS` |

---

### Recovery

Source: `catalog/recover.py: recover_catalog_objects` → `CatalogObjects.indexes`

`sysidxstats` rows with `type != 0` (non-heap) and a non-empty `name` are
recovered as index objects.  Key-column ids come from `sysiscols` rows with
matching `idmajor` and `subid`.

---

### Verification natural key and compared fields

Natural key: `(table FQN, index name)`.

Compared fields:

| Field | Notes |
|-------|-------|
| `type` | `clustered`, `nonclustered`, `xml`, `spatial`, `clustered columnstore`, `nonclustered columnstore`, `nonclustered hash` |
| `is_unique` | bool |
| `is_primary_key` | bool |
| `key_columns` | Column names; omitted for columnstore (SQL Server `sys.index_columns` returns no rows for CCI) |

Source: `metadata_verify.py: verify_indexes`.

---

### Scoping filter

GT collects indexes via `JOIN sys.tables` (base tables only).  Indexed-view
indexes are never in the GT sidecar.  The verifier skips any recovered index
whose `object_id` is not in `rm.base_table_ids`:

```python
# metadata_verify.py: verify_indexes
if rm.base_table_ids and idx.object_id not in rm.base_table_ids:
    continue
```

---

### Known structural differences

- **Columnstore key columns**: `sysiscols` records every column ID for a CCI,
  whereas `sys.index_columns` returns no rows (STUFF→NULL).  Key columns are
  omitted from the comparison for columnstore indexes.
- **Key-column subset**: same as constraints — `sysiscols` includes INCLUDE and
  XTP implicit cols.  GT key columns must be a subset of recovered key columns.
- **Index type code map**:

| `index_type` | Description |
|---|---|
| 0 | heap (skipped — no `name`) |
| 1 | clustered |
| 2 | nonclustered |
| 3 | xml |
| 4 | spatial |
| 5 | clustered columnstore |
| 6 | nonclustered columnstore |
| 7 | nonclustered hash |
