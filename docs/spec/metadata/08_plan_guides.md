## Plan guides metadata — Phase C `[EMPIRICAL]`

### Scope
Database-scoped plan guides (`sys.plan_guides`).  Recovered from the internal
`sysschobjs type='G'` rows and their associated text blobs in `sysobjvalues`.

---

### Source catalog tables

| Table | Object ID | Column layout |
|-------|-----------|---------------|
| `sysschobjs` | 34 | `catalog/columns.py: _SYSSCHOBJS_COLS` |
| `sysobjvalues` | 60 | `catalog/columns.py: _SYSOBJVALUES_COLS` |

---

### Recovery

Source: `mssqlbak/perf.py: recover_plan_guides`

1. Scan `sysschobjs` for rows with `type = 'G'` (plan guide object type).
   Collect `object_id → name` pairs.
2. Read `sysobjvalues` rows with `valclass == _VALCLASS_SQL_TEXT` (`=1`) for
   those object ids.  Sub-object id layout:

| `subobjid` | Content |
|------------|---------|
| 0 | `query_text` |
| 1 | `hints` |
| 2 | `scope_batch` |
| 3 | `parameters` |

3. Scope type (OBJECT/SQL/TEMPLATE) is read from `sysschobjs.intprop` for the
   matching row.  `_SCOPE_MAP = {1: "OBJECT", 2: "SQL", 3: "TEMPLATE"}`.

Text blobs are `nvarchar` stored via LOB if large; `_follow_lob` resolves them.

---

### Data model

Source: `mssqlbak/catalog/model.py: PlanGuide`

```python
@dataclass
class PlanGuide:
    name:            str
    scope_type:      int              # 1=OBJECT, 2=SQL, 3=TEMPLATE
    scope_type_desc: str
    query_text:      str
    scope_batch:     str | None
    parameters:      str | None
    hints:           str | None
    is_disabled:     bool
```

---

### Verification natural key and compared fields

Natural key: plan guide `name`.

Compared fields:

| Field | Notes |
|-------|-------|
| `scope_type_desc` | OBJECT / SQL / TEMPLATE |
| `query_text` | SQL-normalised (`_norm_sql` whitespace collapse) |
| `parameters` | Nullable |
| `hints` | Nullable |

Source: `metadata_verify.py: verify_plan_guides`.

---

### Emit

Source: `mssqlbak/perf.py: emit_perf_scripts`

Produces `EXEC sp_create_plan_guide @name=…, @stmt=…, @type=…, @hints=…` T-SQL
statements.  `emit_perf_tabular` returns plan guide rows as an Arrow table keyed
by `"plan_guides"`.
