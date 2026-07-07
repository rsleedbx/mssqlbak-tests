# forgedb bug: `dba.user` returned as `sqladmin` but the real admin login is `sa`

**Status:** Fixed

## Trigger
```
setup_sqlserver_podman {"version":"lts","size":"lowest","mode":"CT"}
```

## Observed (pre-fix)
Blob contained:
```json
"dba": {"user": "sqladmin", "password": "cIMJn_VFUMkBOWC5IC3K3f6L", "catalog": "lfc_test_db"}
```
But connecting with those exact values failed:
```
sqlcmd -U sqladmin -P <pw> -> Login failed for user 'sqladmin'.
```
The same password worked with user `sa`:
```
sqlcmd -U sa -P <pw> -> SUSER_NAME() = sa
```

## After fix
Blob now correctly reports:
```json
"dba": {"user": "sa", "password": "cIMJn_VFUMkBOWC5IC3K3f6L", "catalog": "lfc_test_db"}
```
Note the **password was identical** across pre/post fix — only `dba.user` was wrong.

## Root-cause hypothesis
The admin login created in the container is `sa`, but the blob hard-coded/derived
`dba.user` as `sqladmin` without creating that login (or mislabeled it).

## Suggested fix
Report `dba.user` as the login actually created in the instance (`sa`), or create
the `sqladmin` login if that name is intended.
