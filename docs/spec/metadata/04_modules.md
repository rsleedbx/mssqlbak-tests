## Modules metadata `[EMPIRICAL]`

### Scope
SQL module definition text (views, stored procedures, scalar and table-valued
functions, DML triggers, and table-valued functions with schema binding).
Database-level DDL triggers and ledger-generated history views are excluded.

---

### Source catalog tables

| Table | Object ID | Column layout |
|-------|-----------|---------------|
| `sysschobjs` | 34 | `catalog/columns.py: _SYSSCHOBJS_COLS` |
| `sysobjvalues` | 60 | `catalog/columns.py: _SYSOBJVALUES_COLS` (definition text) |

---

### Recovery

Two recovery functions work together:

- `recover_module_objects(store) -> dict[int, tuple[str, str, str]]`
  Returns `object_id → (schema_name, object_name, type_desc)` for all module
  objects (`type` in `sysschobjs` from the set `{V, P, FN, IF, TF, TR, R, RF, FS, FT}`).

- `recover_module_definitions(store) -> dict[int, str]`
  Returns `object_id → definition_text`.  Definitions are stored as `nvarchar`
  values in `sysobjvalues` with `valclass=0`, `subobjid=0`, `valnum=0`.

Both return id-keyed dicts; `build_recovered_metadata` resolves them to
FQN-keyed lists using `obj_to_fqn`.

---

### Verification natural key and compared fields

Natural key: object FQN (`schema.name`).

Compared field: SQL-normalised `definition` (whitespace collapsed to single
spaces via `_norm_sql`).

Source: `metadata_verify.py: verify_modules`.

---

### Exclusions applied by the verifier

1. **Database-level DDL triggers** (`pid == 0` in `sysschobjs`): recovered by
   `recover_ddl_trigger_object_ids(store) -> set[int]`; their FQNs are stored in
   `rm.ddl_trigger_fqns`.  The verifier skips any recovered module whose FQN is
   in `ddl_trigger_fqns`:

   ```python
   # metadata_verify.py: verify_modules
   and m.get("object", "") not in rm.ddl_trigger_fqns
   ```

   GT uses `sys.sql_modules JOIN sys.objects`, which only lists objects with a
   `parent_object_id != 0`; database-level DDL triggers have `parent_object_id=0`
   and are absent from GT.

2. **Ledger history views** — SQL Server auto-generates views with a `_Ledger`
   suffix.  They appear in `sys.sql_modules` on the live server but are not stored
   as user objects in the page store.  Both sides filter them by name suffix.

---

### DDL trigger identification

Source: `catalog/recover.py: recover_ddl_trigger_object_ids`

```python
# Rows where type='TR' (DML/DDL trigger) and pid (parent_object_id)==0
# indicate database-level DDL triggers.
```

`pid == 0` in `sysschobjs` means "no parent table" — only database-scoped
triggers satisfy this.  Table-level DML triggers have `pid == parent_table_id`.
