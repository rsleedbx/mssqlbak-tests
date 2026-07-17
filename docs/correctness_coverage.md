# tools.correctness_coverage

`python -m tools.correctness_coverage` compares `mssqlbak` extraction output against SQL Server ground truth for every fixture in a directory, then writes a markdown report.

## Package layout

```
tools/correctness_coverage/
  __init__.py       re-exports public symbols
  __main__.py       entry point
  cli.py            argument parsing + orchestrator
  config.py         NodeStats and shared config types
  discovery.py      .bak / .stats.json pair discovery
  runner.py         single-fixture run + ProcessPoolExecutor scheduler
  compare.py        per-table stat diffing and mismatch labeling
  sinks.py          SinkSpec registry (delta, pg_dir)
  http_server.py    local range server for --http mode
  render.py         markdown rendering
  reports.py        per-edge JSON report tracking
  resources.py      .resources.json sidecar
```

`tools/value_verify.py` provides the cell-level verification functions called from `runner.py`.

## Extraction and edges

Each fixture is processed once by `extract_bak` writing to a `MultiSink`:

1. A `_StreamingStatsSink` accumulates per-table Arrow stats and, if `--verify` is not `none`, calls `value_verify.verify_table` for cell comparison.
2. An `AsyncWriterSink` wraps the I/O sinks (`delta_rs`, `pg_dir`) so Arrow decode and sink writes overlap.

After extraction, three comparison edges are produced per enabled sink:

| Edge | Compared sides |
|---|---|
| `mssql_arrow` | decoded Arrow stats vs `.stats.json` ground truth |
| `arrow_<sink>` | decoded Arrow vs read-back from the sink |
| `<sink>_arrow` | read-back from the sink vs `.stats.json` ground truth |

Cell verification results computed for `mssql_arrow` are re-used for `<sink>_arrow` via `_apply_precomputed_cell_results` when sinks are present.

## CLI reference

```
python -m tools.correctness_coverage [baks ...] [options]
```

| Argument | Default | Description |
|---|---|---|
| `baks` | *(scan dir)* | One or more `.bak` files to process. Omit to scan `--fixture-dir`. |
| `--no-write` | off | Print markdown to stdout instead of writing the file. |
| `--output PATH` | *(docs default)* | Write markdown to this path instead of the computed default. |
| `--fixture-dir DIR` | `tests/fixtures` | Directory to scan for `.bak` / `.stats.json` pairs. Use `tests/fixtures_realworld` for the sample suite. |
| `--threads N` | `4` | Number of fixtures processed concurrently in worker processes. Use `1` for serial execution. |
| `--mem-budget-gb GB` | `8` | Soft resident-memory budget. The scheduler sums estimated per-fixture peaks and admits a new worker only when the sum stays under this limit. At least one fixture always runs. |
| `--http` | off | Serve files over a local HTTP server and pass each `.bak` as an `http://` URL, exercising `HTTPBakReader` + `LazyPageStore`. Output doc gets an `_http` suffix. |
| `--sinks LIST` | `delta,pg_dir` | Comma-separated sink list. Valid choices: `delta`, `pg_dir`. Pass empty string to skip sinks. |
| `--verify {full,digest,none}` | `digest` | Cell verification depth. See below. |
| `--no-cell-verify` | off | Back-compat alias for `--verify none`. |
| `--outdir DIR` | `../outdir` | Root directory for sink output. Per-fixture data lands under `<outdir>/<bak-stem>/<sink>/`. |
| `--reports-dir DIR` | `docs/reports` | Root for tracked per-edge JSON reports. History accretes; existing runs are never deleted. |
| `--assemble-only` | off | Skip extraction; rebuild the `.md` from the latest on-disk JSON reports under `--reports-dir`. |
| `-v` / `--verbose` | off | Enable DEBUG logging to stderr. Equivalent to `MSSQLBAK_LOG_LEVEL=DEBUG`. |
| `--faulthandler` | off | Enable periodic stack dumps every 60 s in worker processes. Equivalent to `MSSQLBAK_FAULTHANDLER=1`. |

## Verification depth (`--verify`)

### `digest` (default)

For each table column, `_arrow_column_digest` (in `value_verify.py`) computes a SHA-256 over the sorted non-null canonical strings — a multiset hash that catches any set-level value corruption without reading GT parquet. When a key is available, `_arrow_ordered_column_digest` additionally hashes the values in key order, catching row transpositions that the multiset digest would miss.

A column mismatch is labeled:

| Label in `value_bad` | Meaning |
|---|---|
| `<col>` | Per-cell value mismatch found by full keyed compare |
| `digest:<col>` | Multiset digest differs (wrong values present, or null count differs) |
| `order:<col>` | Multiset matches but key-ordered digest differs (value-preserving row transposition) |

`value_unscored` is set on a table when no GT parquet is present. This is not a failure; it means the fixture was registered without cells capture (e.g. `--no-cell-verify` was used during `register-bak`).

### `full`

Performs an exhaustive keyed row-level compare using `pc.take` to align rows by key, then `pc.equal` with null-safe logic per column. Populates `res.samples` with `(key, column, decoded_value, expected_value)` tuples, up to `max_samples` per table. Use this mode when investigating a specific decoder issue.

### `none`

Skips all cell verification. Row counts, null counts, and min/max aggregates still run. Useful for profiling the extract/write hot path without GT overhead.

## `--http` mode

`http_server.py` starts a local HTTP server that mimics the GitHub release → CDN redirect path:

- `GET /<name>.bak` → `302 Location: /_cdn/<name>.bak`
- `GET /_cdn/<name>.bak` → `206 Partial Content` with `Content-Range` and `Accept-Ranges: bytes`

This causes `HTTPBakReader` to set `_is_range_reader = True` and exercise `LazyPageStore` + `warm_file` with Range requests, exactly as if the `.bak` were hosted behind a CDN. The output markdown is written to a path with an `_http` suffix so it does not overwrite the local-file run.

## Generated output

### Markdown report

`docs/correctness_coverage_<dir>.md` (or the path given by `--output`). Sections:

- **Summary** — pass/fail count per edge, total extraction time.
- **Per-fixture detail** — one row per fixture per edge, with `value_bad` columns highlighted.
- **Extraction timings** — wall time, extract time, and `Verify = wall − extract` phase. Phase breakdowns include Arrow verify time and per-sink write/readback times.

### `.resources.json` sidecar

Written alongside the markdown; contains file sizes and checksums used for display in the report.

### Per-edge JSON reports (`--reports-dir`)

One JSON file per `(fixture, edge)` run is appended under `--reports-dir`. `--assemble-only` rebuilds the markdown from these without re-running extraction.

## Concurrency and memory

Each fixture runs in an isolated worker process (`ProcessPoolExecutor` with `max_tasks_per_child=1`), so a crashed or memory-leaking worker does not affect the orchestrator. The scheduler gates admission against `--mem-budget-gb`; because Arrow C++ releases the GIL, `MSSQLBAK_VERIFY_THREADS` (default: `min(4, cpu_count)`) controls thread-level parallelism within a single worker for Arrow verify operations.

Memory is aggressively returned between tables: each table's Arrow batches are freed before the next table starts. Sink data is written asynchronously so decode and I/O overlap.
