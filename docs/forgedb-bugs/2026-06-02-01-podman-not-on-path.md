# forgedb bug: MCP server cannot find `podman`

**Status:** Fixed

## Trigger
```
tool: setup_sqlserver_podman
args: {"version": "lts", "size": "lowest", "mode": "CT"}
```

## Observed
```
Error executing tool setup_sqlserver_podman: [Errno 2] No such file or directory: 'podman'
```

## Expected
Provision a SQL Server podman container.

## Root-cause hypothesis
The MCP server process was launched with a PATH that does not include
`/opt/homebrew/bin` (where `podman` lives on Apple Silicon Homebrew). GUI-launched
processes on macOS often inherit a minimal PATH (`/usr/bin:/bin:/usr/sbin:/sbin`).

## Suggested fix
Ensure the MCP server launches with the user's full PATH (or resolve the `podman`
binary via an absolute path / configurable setting).
