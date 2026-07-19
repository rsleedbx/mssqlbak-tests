## Security metadata `[EMPIRICAL]`

### Scope
Database principals (users, roles, groups) and object-level / database-level
permission grants and denials.  Built-in principals (`dbo`, `guest`,
`INFORMATION_SCHEMA`, `sys`, `public`) and fixed database roles are excluded.

---

### Source catalog tables

| Table | Object ID | Column layout |
|-------|-----------|---------------|
| `sysowners` | 27 | `catalog/columns.py: _SYSOWNERS_COLS` |
| `sysprivs` | 29 | `catalog/columns.py: _SYSPRIVS_COLS` |

---

### sysowners column layout `[EMPIRICAL]`

Source: `catalog/columns.py: _SYSOWNERS_COLS`

| Decl # | Field | Type |
|--------|-------|------|
| 0 | `id` | `int` (principal_id) |
| 1 | `status` | `int` |
| 2 | `name` | `nvarchar` (variable col 0) |

Fixed region = 8 bytes.  Principal type is recovered from the `sysschobjs` row
for the same `id` where `type` codes map to:
`R`=DATABASE_ROLE, `S`=SQL_USER, `U`=WINDOWS_USER, `G`=WINDOWS_GROUP,
`E`=EXTERNAL_USER, `X`=EXTERNAL_GROUP, `A`=APPLICATION_ROLE.

---

### sysprivs column layout `[EMPIRICAL]`

Source: `catalog/columns.py: _SYSPRIVS_COLS`

Fixed region = 22 bytes.

| Decl # | Field | Type | Notes |
|--------|-------|------|-------|
| 0 | `class` | `tinyint` | 0 = database-level, 1 = object-level |
| 1 | `objid` | `int` | Object id (0 for database-level) |
| 2 | `subid` | `int` | Column/parameter sub-id (usually 0) |
| 3 | `grantee` | `int` | Grantee principal id |
| 4 | `grantor` | `int` | Grantor principal id |
| 5 | `actid` | `int` | Action id (e.g. 193=SELECT, 195=INSERT, 196=DELETE, 197=UPDATE, 224=EXECUTE) |
| 6 | `privattrib` | `tinyint` | Permission state as ASCII character — see below |

**`privattrib` state decode** (empirically confirmed on `AdventureWorks2016_EXT.bak`):

| Byte value | ASCII char | State |
|------------|------------|-------|
| 0x47 | `G` | GRANT |
| 0x57 | `W` | GRANT WITH GRANT OPTION |
| 0x44 | `D` | DENY |
| 0x52 | `R` | REVOKE |

Source: `catalog/recover.py: recover_object_permissions` — `privattrib` is decoded
as `chr(raw_byte)`.

**`class == 0` handling**: database-level permissions (`class=0`) apply to the
database itself rather than a named object; `object_id` is set to `0` in the
recovered `ObjectPermission`.

---

### Recovery

Source: `catalog/recover.py: recover_principals`, `recover_object_permissions`

- `recover_principals(store) -> list[Principal]` — reads `sysowners` rows,
  resolves `principal_type` from `sysschobjs`.
- `recover_object_permissions(store) -> list[ObjectPermission]` — reads
  `sysprivs` rows, decodes `privattrib`, maps `actid` to action name string.

---

### Verification natural key and compared fields

Principals natural key: `(kind="principal", name)`.
Compared field: `type` (type description string).

Permissions natural key: `(kind="permission", grantee name, object FQN, action name)`.
Compared field: `state` (GRANT / GRANT WITH GRANT OPTION / DENY / REVOKE).

Source: `metadata_verify.py: verify_security`.

---

### Known structural differences

- **Fixed database roles** (`db_owner`, `db_datareader`, etc.) exist in
  `sysowners` but GT's `register_bak.py` filters them with `is_fixed_role=0`.
  The verifier excludes a hardcoded set of nine fixed role names from the
  recovered side.
- **Built-in principals** (`dbo`, `guest`, `INFORMATION_SCHEMA`, `sys`,
  `public`) are always present in any database; both sides exclude them from
  the comparison.
- **Database-level permissions** (`class=0`): `CONNECT` permission for database
  users is recovered with `object_id=0` (no named object); the GT representation
  uses an empty string for `object`.
