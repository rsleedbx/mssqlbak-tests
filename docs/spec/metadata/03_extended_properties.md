## Extended properties metadata `[EMPIRICAL]`

### Scope
Extended properties at three levels:
- **Table-level** — `class=1` rows in `sysobjvalues` attached to a user table object.
- **Column-level** — `class=1`, `subid > 0` rows attached to a specific column.
- **Schema-level** — `class=3` rows attached to a schema.

Views, stored procedures, functions, and DDL triggers that also store `class=1`
properties in `sysobjvalues` are excluded to match the GT collection scope.

---

### Source catalog table

| Table | Object ID | Column layout |
|-------|-----------|---------------|
| `sysobjvalues` | 60 | `catalog/columns.py: _SYSOBJVALUES_COLS` |

---

### Recovery

Source: `catalog/recover.py: recover_extended_properties`

`sysobjvalues` rows with `valclass=1` (object/column) and `valclass=3` (schema)
where `subobjid` is the column id (0 for object-level).  Values are stored as
`nvarchar` in the variable section of the record.

The result is a nested dict:
- `obj_props: dict[object_id, dict[subid, dict[property_name, value]]]`
- `schema_props: dict[schema_id, dict[property_name, value]]`

Both are stored in `RecoveredMetadata.obj_props` and `RecoveredMetadata.schema_props`.

---

### Verification natural key and compared fields

Natural key: `(level, object FQN or schema name, column name if any, property name)`.

Compared field: `value` (string).

Source: `metadata_verify.py: verify_extended_properties`.

---

### Scoping filter

GT collects extended properties via `JOIN sys.tables` (base tables only).
Views, procs, and functions also appear in `sysobjvalues class=1`, but the GT
query never includes them.  The verifier skips any `obj_id` not in
`rm.base_table_ids`:

```python
# metadata_verify.py: verify_extended_properties
if rm.base_table_ids and obj_id not in rm.base_table_ids:
    continue
```
