# forgedb bug: `setup` returns a blob but does not persist it; `check_connections` fails

**Status:** Fixed

## Trigger
```
setup_sqlserver_podman {"version":"lts","size":"lowest","mode":"CT"}   -> returns full conn blob
check_connections      {"profile":"default"}                           -> 0/1 OK
list_running_containers{"profile":"default"}                           -> engine:"", ports:[], blob:""
```

## Observed
```
check_connections: {"summary":"0/1 connections OK","results":[{"name":"robert-lee-mssql-2022--host-local-1779207800","ok":false,"error":"no conn_blob found in secrets dir"}]}
```
`setup` returned a rich blob inline (host/port/dba/users), but it was never written
to the secrets dir, and `list_running_containers` reported empty engine/ports/blob.

## Expected
After a successful `setup`, the conn_blob is persisted so `check_connections`,
`reconfigure`, and `list_running_containers` can read it.

## Root-cause hypothesis
The persistence step (write conn_blob to secrets dir) was missing or keyed by a
different identifier than the lookup (see bug 05 / name mismatch:
`server_name=robert-lee-mssql-local-…` vs container
`robert-lee-mssql-2022--host-local-…`).

## Suggested fix
Persist the blob on `setup` success; key save and lookup on the same canonical id.
