# forgedb MCP — Bug Log

One markdown file per bug hit while using the forgedb MCP, so the forgedb
maintainers can fix them. Newest issues get a new numbered file.

Naming: `YYYY-MM-DD-NN-<slug>.md`.

Each report records: what tool/args triggered it, the observed vs expected
behavior, the raw error, a root-cause hypothesis, and the current status.

| File | Bug | Status |
|------|-----|--------|
| 2026-06-02-01-podman-not-on-path.md | MCP server can't find `podman` | Fixed |
| 2026-06-02-02-server-wide-invalid-params.md | All tools return `-32602` until Cursor refresh | Fixed (needs refresh) |
| 2026-06-02-03-conn-blob-not-persisted.md | `setup` returns blob but doesn't persist; `check_connections` fails | Fixed |
| 2026-06-02-04-setup-idempotent-stale-blob.md | `setup` short-circuits, returns stale `ready_at`, skips persistence | Open/Needs docs |
| 2026-06-02-05-dba-user-mislabeled.md | `dba.user` returned as `sqladmin` but real login is `sa` | Fixed |
