# Non-Extractable Types — `cursor`, `table`

_Part of the [mssqlbak spec suite](../00_MASTER.md) · [← Index](00_INDEX.md)_

---

## 1. Header

| SQL Server type | xtype (system_type_id) | Reason not extractable | SQL Server version |
|---|---|---|---|
| `cursor` | — (no user-table xtype) | Procedure-only; cannot be a column in a user table or view | All |
| `table` | — (no column xtype) | Procedure-only variable type; cannot be a persisted column | All |

Both types appear in `sys.types` (as `is_user_defined = 0` rows) and are counted among SQL Server's 41 system data types. However, neither can appear as a column in a user table — they are exclusively for use in stored procedure scope.

---

## 2. Why these types cannot be extracted

### `cursor`

A `cursor` variable holds a reference to a server-side cursor object. It:
- Cannot be a column in a `CREATE TABLE` statement.
- Cannot be stored in `syscolpars` (SQL Server's column metadata catalog).
- Has no physical on-disk row representation.
- Exists only in the scope of a T-SQL batch or stored procedure.

SQL Server documentation states explicitly: "Columns of cursor data type cannot be part of an index or a primary key, and are not allowed in a `CREATE TABLE` statement."

### `table`

A `table` variable holds a result set in memory for use within a procedure or batch. It:
- Cannot be a column in a `CREATE TABLE` statement.
- Cannot be stored in `syscolpars`.
- Has no physical on-disk row representation (table variables are stored in `tempdb` but only for the duration of the batch).
- **User-defined table types** (`CREATE TYPE ... AS TABLE`) are persisted as metadata (`sysschobjs type='TT'`) but their columns are only instantiated when a table variable is declared — the column data is never in a backup's data pages.

---

## 3. Impact on mssqlbak

`column_supported(type_id, user_type_id)` in `dispatch.py` checks `type_id not in SUPPORTED_TYPE_IDS`. Since `cursor` and `table` have no `system_type_id` entry in `SUPPORTED_TYPE_IDS`, they can never be returned by `column_supported()`. In practice, they will never appear in `syscolpars` for any user table in any `.bak` file.

If a future SQL Server version were to introduce a storable `cursor`-like or `table`-valued column type, it would require a new `system_type_id` allocation and a corresponding mssqlbak decoder.

Source: `scalars.py: SUPPORTED_TYPE_IDS`; `dispatch.py: column_supported`

---

## 4. User-defined table types (related, but distinct)

`CREATE TYPE MyTableType AS TABLE (...)` creates a user-defined table type. This appears in:
- `sysschobjs` with `type = 'TT'` (table type)
- `syscolpars` with the type's column definitions

mssqlbak recovers these type definitions via `catalog.py: recover_user_table_types`, but the column data of table-type instances is never in the `.bak` data pages — table variables are transient. The type definition recovery is for schema introspection only.

Source: `catalog/model.py: TableType`; `catalog/__init__.py: recover_user_table_types`

---

## 5. Source references

| Claim | Source |
|---|---|
| SQL Server documentation | "Columns of cursor data type cannot be part of an index..." — SQL Server Books Online, `cursor` type |
| `SUPPORTED_TYPE_IDS` | `scalars.py: SUPPORTED_TYPE_IDS` |
| `column_supported` | `dispatch.py: column_supported` |
| User-defined table types | `catalog/model.py: TableType`; `catalog/__init__.py: recover_user_table_types` |
