# tools.fixture_run

`python -m tools.fixture_run` serves two jobs:

1. **Fixture generation** — runs the `make_*.py` generator scripts with forgedb credentials pre-loaded, so you do not need to hand-export `FIXTURE_DBA_PASSWORD` or `FIXTURE_CONTAINER` before every run.
2. **Ground-truth capture** — restores a `.bak` to a live SQL Server container and writes the sidecar files that `tools.correctness_coverage` uses for comparison.

Most commands require a live SQL Server container provisioned by forgedb (via the `user-forgedb` MCP tools). `mssql_python` must be installed in the current virtualenv for cells capture.

## Ground-truth artifacts

For each `.bak`, `register-bak` writes three sidecars:

### `<bak>.stats.json`

Per-table aggregate statistics collected directly from SQL Server:

- Row count per table.
- Per-column null count.
- Per-column min and max, as canonical NVARCHAR strings under `Latin1_General_100_BIN2` collation (see `register_bak.py:631`).

The file is written with `_stable_write_stats`, which skips volatile fields (`database`, `registered_at`, timing) when the content is otherwise unchanged, preventing spurious git churn on re-runs.

### `<bak>.cells/`

A directory of per-table parquet files plus a manifest:

- `<schema.table>.parquet` — one row per captured row, columns are the canonical string representation of each cell (`cell_canon.canon`).
- `_manifest.json` — per-column SHA-256 digests over the full non-null column (not just the sampled rows).

Canonicalization is handled by `cell_canon.canon` (`cell_canon.py:235`), the single source of truth for turning SQL values into stable strings for comparison. Two digest functions are defined there:

- `column_digest` (`:309`) — multiset hash: sorts values before hashing. Catches wrong values and wrong null counts regardless of row order.
- `column_ordered_digest` (`:329`) — hashes values in the order they are supplied. Catches value-preserving row transpositions that the multiset digest would miss.

### `<bak>.bak.headeronly.json`

The output of `RESTORE HEADERONLY`, recording per-backup-set LSNs (`dbi_checkptLSN`, `dbi_differentialBaseLSN`, `dbi_dbbackupLSN`). Used to cross-check LSN fields decoded by `mssqlbak` against values SQL Server reports directly. Written unless `--no-headeronly` is passed.

## Cells capture modes

`cells_capture.capture_cells` chooses one of three modes per table based on table size and whether a stable key exists (`cells_capture.py:259`):

| Mode | Trigger | What is stored |
|---|---|---|
| `full` | keyed table, row count ≤ `sample_threshold` (default 1 000 000) | all rows, key-sorted |
| `sample` | keyed table, row count > `sample_threshold` | strided sample of `sample_n` (default 200 000) rows; digest is still computed over the full column |
| `digest-only` | no usable key (no PK, unique index, or identity column) | sorted column values up to `digest_values_cap` (default 100 000) per column; no row-level parquet |

Key resolution order: primary key → unique index → identity column → no key (digest-only). The resolved key columns are recorded in `_manifest.json`.

## Command structure

```
python -m tools.fixture_run [--fixture-dir DIR] [--server NAME] <command> [args]
```

Global flags:

| Flag | Description |
|---|---|
| `--fixture-dir DIR` | Directory where `.bak` files are written and sidecars are stored. Sets `FIXTURE_DIR` env var for subprocess calls. |
| `--server NAME` | forgedb blob stem to target (e.g. `robert-lee-mssql-2022-mcr-local-…`). Overrides `FIXTURE_SERVER_NAME`. |

### Generator subcommands

Each maps to a `make_*.py` script (e.g. `compressionmatrix`, `layout`, `heap-scale`, `catalog`, `version-matrix`). See `python -m tools.fixture_run --help` for the full list.

### `register-bak <bak>`

Runs the full ground-truth capture pipeline for a single `.bak` file:

1. Bootstrap credentials from the forgedb keyring.
2. Run `RESTORE HEADERONLY` to detect differential/striped layout and check compatibility.
3. Restore the database (full, differential, or striped) with auto-generated `MOVE` clauses so all data files land under the container's data directory.
4. Call `_collect_stats` — queries SQL Server for row counts, null counts, and min/max per column.
5. Write the `HEADERONLY` LSN sidecar (unless `--no-headeronly`).
6. Call `capture_cells` — canonicalizes every cell and writes `.cells/` parquet + `_manifest.json`.
7. Drop the database (unless `--keep`).
8. Write `.stats.json` with `_stable_write_stats`.

Additional flags:

| Flag | Description |
|---|---|
| `--keep` | Do not drop the database after collecting stats. Useful for manual inspection. |
| `--cells-only` | Backfill the `.cells/` sidecar without re-collecting `.stats.json`. Use when stats already exist but cells were not captured. |
| `--no-headeronly` | Skip writing the `<bak>.bak.headeronly.json` LSN sidecar. |

### `register-all`

Calls `register-bak` for every `.bak` in `--fixture-dir` that either has no `.stats.json` or whose stats are outdated.

Flags: `--keep`, `--cells-only` (same semantics as `register-bak`).

### `register-headeronly-all`

Writes `<bak>.bak.headeronly.json` for every `.bak` that does not have one yet, using only `RESTORE HEADERONLY` (no full restore). Pass `--force` to overwrite existing sidecars.

### `all-versions`

Runs a suite of generator commands against every discovered SQL Server version (2017, 2019, 2022, 2025), then runs `register-all` on each version's fixture directory.

Each `(version, command)` pair runs in a fresh subprocess so that module-level `OUT_PATH` constants in the generator scripts re-evaluate with the correct `FIXTURE_DIR` for that version.

Generator scripts that require a newer engine call `skip_if_server_older_than()`; known skips are recorded in `_ALL_VERSIONS_EXPECTED_SKIPS` and printed as `xfail/skip` without failing the run.

After all generators complete, a trailing `register-all` pass is run per version to capture ground-truth sidecars for every newly generated `.bak`.

Flags:

| Flag | Description |
|---|---|
| `--suite CMD [...]` | Run only these commands from `_ALL_VERSIONS_SUITE` (repeatable). |
| `--suite-all` | Run the complete `_ALL_VERSIONS_SUITE` (overrides explicit `--suite`). |
| `--keep` | Propagated to each `register-all` invocation. |
| `--cells-only` | Propagated to each `register-all` invocation. |

## Server discovery

`discover_server_name` resolves the target SQL Server instance in this order:

1. `FIXTURE_SERVER_NAME` environment variable (or `--server` flag, which sets this var).
2. A single running `mssql/server` Podman container — used automatically when there is exactly one.
3. When multiple containers are running: the year embedded in `--fixture-dir` (e.g. `tests/fixtures_2022` → `2022`) is used to narrow the match. If the year still matches multiple containers, the command fails with an error.

When multiple SQL Server containers are running and `--fixture-dir` contains no year, set `FIXTURE_SERVER_NAME` or `--server` explicitly.

## Notes

- forgedb SQL Server containers are provisioned with the `setup_sqlserver_podman` MCP tool from the `user-forgedb` server. Teardown uses `teardown_sqlserver_podman`.
- `mssql_python` must be installed in the project virtualenv for cells capture (`pip install mssql_python`).
- The `env` subcommand prints `export FIXTURE_SERVER_NAME=… FIXTURE_DBA_PASSWORD=…` lines suitable for `eval "$(python -m tools.fixture_run env)"`.
