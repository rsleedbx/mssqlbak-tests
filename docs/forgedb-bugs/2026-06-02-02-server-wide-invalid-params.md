# forgedb bug: all tools return `-32602 Invalid request parameters`

**Status:** Fixed (cleared after a Cursor MCP refresh)

## Trigger
After the PATH fix, every call failed identically, including a no-arg-required tool:
```
setup_sqlserver_podman {"version":"lts","size":"lowest","mode":"CT"}  -> -32602
setup_sqlserver_podman {}                                             -> -32602
setup_sqlserver_podman {<all 13 fields at defaults>}                  -> -32602
config_show            {"profile":"default"}                          -> -32602
```

## Observed
```
{"error":"MCP error -32602: Invalid request parameters"}
```

## Expected
Tools accept their documented arguments.

## Root-cause hypothesis
Because even `config_show` (only optional `profile`) failed identically, the
rejection was at the request-envelope/registration level, not argument validation.
The tool/schema registration was likely stale after the server restart; a Cursor
MCP refresh re-synced it.

## Suggested fix
Ensure schema/tool registration is valid immediately after server (re)start so a
client refresh isn't required; or surface a clearer error than generic `-32602`.
