## Schema objects metadata `[EMPIRICAL]`

### Scope
Four object kinds recovered as a single group: schemas, sequences, synonyms,
and user-defined table types (including XTP / In-Memory OLTP variants).
System-schema objects and fixed database role schemas are excluded.

---

### Source catalog tables

| Table | Object ID | Column layout | Used for |
|-------|-----------|---------------|---------|
| `sysclsobjs` | 64 | `catalog/columns.py: _SYSCLSOBJS_COLS` | schemas |
| `sysschobjs` | 34 | `catalog/columns.py: _SYSSCHOBJS_COLS` | sequences, synonyms, table types |
| `syscolpars` | 41 | `catalog/columns.py: _SYSCOLPARS_COLS` | table type columns |
| `sysscalartypes` | 50 | `catalog/columns.py: _SYSSCALARTYPES_COLS` | user-visible table type names |
| `syssingleobjrefs` | 74 | `catalog/columns.py: _SYSSINGLEOBJREFS_COLS` | type → backing object mapping |

---

### Recovery

#### Schemas — `recover_schemas(store)`
Reads `sysclsobjs` rows with `class = 0x32` (schema records) and returns
`list[SchemaInfo(schema_id, name)]`.  Rows with `schema_id >= 16384` are
fixed database role schemas excluded from the GT query.

#### Sequences — `recover_sequences(store)`
Reads `sysschobjs` rows with `type = 'SO'` (sequence objects).  Sequence
properties (data type, start, increment, min/max, cycle) come from
`sysobjvalues`.

#### Synonyms — `recover_synonyms(store)`
Reads `sysschobjs` rows with `type = 'SN'` (synonyms).  The `target_definition`
string comes from `sysobjvalues valclass=0, subobjid=0, valnum=0`.

#### User-defined table types — `recover_user_table_types(store)` `[EMPIRICAL]`

XTP (In-Memory OLTP) table types use an indirect three-table join (G62):

1. **`sysschobjs` type=`'TT'`** — internal backing objects with names like
   `TT_<schema>_<typename>_<hash>`.  These are in the `sys` schema internally.
2. **`syssingleobjrefs` (obj 74)** — maps `user_type_id → TT backing object_id`.
   Rows with `class=6` link the user-visible type to its internal object.
3. **`sysscalartypes` (obj 50)** — stores the user-visible `(schema_id, name)`
   for each user-defined type.  Rows with `schema_id != 4` (not `sys`) are
   the user-facing declarations.

The join yields the user-visible `(schema_name, type_name)` mapped to the
backing object's column list from `syscolpars`.

| Step | Query |
|------|-------|
| 1 | Collect `TT` backing `object_id`s from `sysschobjs` |
| 2 | Read `syssingleobjrefs` to get `user_type_id → backing_object_id` |
| 3 | Read `sysscalartypes` to get `(schema_id, name)` per `user_type_id` |
| 4 | Read `syscolpars` keyed by `backing_object_id` for column list |

---

### Verification natural key and compared fields

Natural key: `(kind, name)` where kind is `schema`, `sequence`, `synonym`, or
`table_type`, and name is the FQN for all but `schema`.

Compared fields:

| Kind | Compared fields |
|------|----------------|
| schema | _(name only — presence check)_ |
| sequence | _(name only — property comparison TBD)_ |
| synonym | `target` (target definition string) |
| table_type | `columns` (ordered list of column names) |

Source: `metadata_verify.py: verify_schema_objects`.

---

### Known structural differences — XTP table types

SQL Server generates internal `sys.TT_*` objects that appear in `sysschobjs`
but are not user-visible.  The verifier skips any recovered table type with
`schema_name == "sys"`:

```python
# metadata_verify.py: verify_schema_objects
if tt.schema_name == "sys":
    continue
```

This matches the GT query, which only collects types from `sys.table_types`
joined against user schemas.

---

### Guess Register entry

| ID | Guess | Evidence | Risk |
|----|-------|----------|------|
| G62 | `syssingleobjrefs class=6` links `user_type_id` to `TT` backing `object_id`; `sysscalartypes` obj 50 holds user-visible `(schema_id, name)` for `schema_id != 4` | Empirically confirmed on `AdventureWorks2016_EXT.bak`: XTP table types `Sales.SalesOrderDetailType_inmem`, `Sales.SalesOrderDetailType_ondisk` correctly recovered after implementing the three-table join | M (table types missing) |
