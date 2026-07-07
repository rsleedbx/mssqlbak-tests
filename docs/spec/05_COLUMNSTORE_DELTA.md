# Columnstore Delta — SQL Server BAK Decode Spec

_Part of the [mssqlbak spec suite](00_MASTER.md). See [01_COMMON files](01_PAGE.md) for shared page/catalog/type layouts._

---

## 1. Routing trigger

**StoragePath:** `COLUMNSTORE_DELTA`
**Set by:** `read_table_rows` (`mssqlbak/rows.py:860`) when `_read_columnstore_delta_rows` fabricates a synthetic `__cs_delta_{rs_id}` table and re-enters `read_table_rows`
**Catalog signal:** detected via `sys.column_store_row_groups` with OPEN/CLOSED state; underlying rowset has `cmprlevel == 0`
**Decode entry point:** `columnstore.py:2309` → fabricates `__cs_delta_*` table → `rows.py:860` (re-entry)

---

## 2. Initialization

Row format is IDENTICAL to ROWSTORE_BTREE (clustered B-tree rowstore rows). See `03_ROWSTORE_BTREE.md` for the record layout. The delta store is a holding area for rows not yet compressed into segments.

---

## 3. Record structure

## Row format

Delta-store rows **are** regular clustered B-tree rowstore records (FixedVar format).
The record layout is identical to `03_ROWSTORE_BTREE.md` §3. Do not duplicate it here — cross-reference only.

## Architectural note: decoder re-entry

`_read_columnstore_delta_rows` (`mssqlbak/columnstore.py:2309`) fabricates a synthetic
`__cs_delta_{rs_id}` table and re-enters `read_table_rows`. This single code-reuse decision
is the structural source of Class 3 contextual interpretation bugs (see architecture plan):
every heuristic in `read_table_rows` was originally only exercised on columnstore-originated
data, so assumptions like "all inline MAX values have a 0x21 prefix" went undetected until
a real rowstore table with a conflicting value was tested.

The `StoragePath.COLUMNSTORE_DELTA` enum value makes this re-entry explicit: when the
routing sets `COLUMNSTORE_DELTA`, every decode rule that branches on context can branch on
the enum instead of inferring it from `table.name.startswith("__cs_delta_")`.

## 4. Value decode rules

### Inline MAX-type marker (0x21) `[EMPIRICAL — fix 826ba67, 2026-07-01]`

SQL Server prepends a `0x21` type-marker byte to inline `varchar(max)`, `nvarchar(max)`,
and `varbinary(max)` values in **columnstore delta-store rows**. Regular rowstore pages
store the raw bytes without any prefix. The decoder must strip the prefix here but NOT
in regular rowstore paths.

**Current rule** (`mssqlbak/rows.py:1081`, guard at `rows.py:1095`):

```python
_do_strip = True
if col.type_id == 231:                    # nvarchar(max): even length → 0x21 is data (CJK etc.)
    if len(cell) % 2 == 0:
        _do_strip = False
elif col.type_id in (165, 167):           # varbinary(max) (165) and varchar(max) (167):
    if not table.name.startswith("__cs_delta_"):  # only delta stores carry the prefix
        _do_strip = False
if _do_strip:
    cell = cell[1:]
```

**Why the rule exists here:** delta-store rows are read by `read_table_rows` via the
`__cs_delta_*` synthetic table re-entry. The rule was originally written when delta stores
were the only source of inline MAX values reaching that code path, so stripping
unconditionally was correct at the time. Regular rowstore values that genuinely start with
`0x21` (e.g. bcrypt hashes in `WideWorldImporters.Application.People.HashedPassword`)
exposed the over-generalization.

**Open empirical question:** SQL Server docs say delta stores are "plain B-tree rowstore
rows." If true, the `0x21` prefix should appear in ALL B-tree rowstore inline MAX values,
not just delta stores. The current guard `__cs_delta_*` may be conservatively correct for
now but wrong in the broader case. To resolve: DBCC PAGE a regular rowstore table with a
`varbinary(max)` column whose first data byte is `0x21` and check whether SQL Server writes
the prefix byte in the page.

---

## 5. Diagnostic events

| tag | decision | reason | extra fields |
|---|---|---|---|
| `u21:strip-all` | `strip` | `delta_store` or `odd_nvarchar` | `type_id`, `raw_first16`, `cell_len` |
| `u21:keep-even` | `keep` | `nvarchar_even_len` (not a prefix) | `type_id`, `raw_first16`, `cell_len` |

_Note: current `record_tag` calls record only the branch name. `raw_first16` and `reason`
fields require upgrading to `record_event` (see architecture plan Goal #2)._

---

## 6. Known heuristics and open questions

| # | Heuristic | Status |
|---|---|---|
| H1 | Strip `0x21` for `varbinary(max)` (type_id 165) **and** `varchar(max)` (type_id 167) only when `table.name.startswith("__cs_delta_")` | Empirically correct (fix `826ba67`) — DBCC PAGE confirmation still needed |
| H2 | Strip `0x21` for `nvarchar(max)` only when `len(cell) % 2 != 0` (odd = prefix, even = data) | `[EMPIRICAL]` — parity is the correct discriminant (SCSU always odd) |
