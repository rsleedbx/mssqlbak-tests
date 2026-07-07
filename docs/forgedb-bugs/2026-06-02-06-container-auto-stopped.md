# forgedb bug: provisioned container stops on its own (prelogin/handshake failures)

**Status:** Open

## Trigger
A SQL Server instance provisioned earlier via `setup_sqlserver_podman` was used
successfully (created the `TypeCoverage` DB, ran `BACKUP`, queried via
`podman exec sqlcmd`). ~30–40 min later, host TCP connections to the mapped port
began failing.

## Observed
- Host `sqlcmd -S 127.0.0.1,30004` and `mssql_python` over TCP both failed with:
  `Client unable to establish connection ... error encountered during handshakes
  before login` (ODBC error code 0x36 / connection reset).
- TCP `connect()` to `127.0.0.1:30004` *succeeded* (port-forward up), so it looked
  like a TLS/prelogin issue at first.
- Root cause: the container had actually **stopped**. `podman stats` showed
  `mem=0B / 0B`; `podman exec` returned
  `can only create exec sessions on running containers: container state improper`.
- `podman start <name>` brought it back; SQL Server was ready in ~4s and both
  host `sqlcmd` and `mssql_python` over TCP then worked perfectly.

## Expected
A provisioned instance stays running for the session (or forgedb documents the
auto-stop/idle behavior and offers a `start`/`ensure-running` operation).

## Root-cause hypothesis
Either the podman machine reclaimed/stopped the container (resource pressure on
the `size=lowest` instance), or an idle/auto-stop policy. The misleading part is
that the failure surfaces as a TDS *prelogin handshake* error rather than a clear
"container not running", because the gvproxy port-forward still accepts the TCP
connection and then resets.

## Suggested fix
- Keep the instance running for the session, or expose an explicit
  `start`/`ensure_running` lifecycle op and document idle-stop behavior.
- `check_connections` / `list_running_containers` should report when the
  container is stopped (distinct from a credential/handshake error) so callers
  know to restart rather than chase a phantom TLS problem.
