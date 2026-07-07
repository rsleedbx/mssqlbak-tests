# Engine-backed validation & fallback (design)

Status: **proposed** (no code yet). Tracks the "Option 1" engine-delegation
path discussed for validating the parser against large real-world `.bak` files
and for falling back to a real engine when the pure-Python parser cannot decode
a table.

## Why

The pure-Python parser is the product: it reads a `.bak` with **no SQL Server
and no restore**. But two needs push toward an *optional* live-engine path:

1. **Validation at scale (primary).** `tests/test_engine_diff.py` already proves
   the parser matches a live engine — but only for the hand-built
   `TypeCoverage` fixture. As we pull in big public backups
   (`tests/fixtures/samples/`, e.g. AdventureWorks / WideWorldImporters) we want
   to cross-check decoded rows against ground truth **without hand-restoring
   each database**. An automated "restore into a throwaway engine, `SELECT`, and
   diff against the parser" harness gives that.
2. **Coverage fallback (secondary).** When `classify_table` marks a table
   unsupported (heap edge cases, unsupported type, compression we don't decode)
   or `extract` hits an unanticipated structure, we can still return data by
   letting a real engine `RESTORE` the original `.bak` and run the `SELECT`.

Both needs are served by **one component**: restore a `.bak` into a SQL Server
container and expose a connection. The difference is only what the caller does
with the rows (diff vs. emit).

## Why a real RESTORE, not MDF reconstruction

`mtf.py` already rebuilds a page-addressable MDF image, so writing it out as an
`.mdf` and `ATTACH`-ing it is tempting. It is **not reliable**: a full backup's
data pages are *fuzzy* (copied while the database was live) and only become
transactionally consistent after the engine replays the captured log during
`RESTORE`. A raw page image attached directly skips recovery — SQL Server treats
it as "not cleanly shut down", and `ATTACH_REBUILD_LOG` refuses when
in-flight transactions existed. So the engine path hands the engine the
**original `.bak`** and lets `RESTORE` do recovery correctly. This also means
the path transparently handles inputs the parser intentionally does not
(TDE-encrypted, ZSTD/QAT-compressed, multi-file, differential merges).

This is deliberately **not** the HyperBac/virtual-restore approach (a
filesystem-filter driver serving pages on demand with copy-on-write delta
files). That needs a kernel/FUSE layer and on-the-fly recovery — out of scope;
see Non-goals.

### Why not `ATTACH` (it *feels* lighter, but isn't)

Attach is appealing because attaching pre-existing `.mdf`/`.ldf` skips the
restore write pass. The catch: **we don't have those files — we have a `.bak`.**
The "lightness" of attach assumes valid data files already exist on disk. To
attach, we'd first reconstruct them from the backup, and that reconstruction
erases the supposed savings while adding correctness risk:

1. **It isn't actually light.** To attach, the reconstructed `.mdf` must be a
   real file the server can open. `mtf.py` builds the page image by reading the
   whole `.bak` and allocating a full-size buffer, then we'd write the full
   `.mdf` to disk — roughly the **same read + write I/O as `RESTORE`'s data
   pass** (which IFI can shorten anyway). All attach skips is log replay, a
   fraction of the cost. So the headline benefit is largely illusory for a
   `.bak` source.
2. **Backup pages are fuzzy → require recovery.** A full backup copies pages
   while the database is live, then captures log to make them consistent.
   `RESTORE` replays that log (redo committed, undo in-flight). Attaching raw
   pages **skips recovery**: SQL Server sees "was not shut down cleanly" and
   refuses (errors 1813 / 5173), and `ATTACH_REBUILD_LOG` won't help when open
   transactions existed at backup time. Best case it fails loudly; worst case it
   attaches a **logically inconsistent** database (uncommitted rows present,
   committed rows missing, allocation/index mismatches).
3. **You must fabricate a valid log.** Attach needs an `.ldf` whose LSNs line up
   with the data files. The backup's log isn't a standalone `.ldf`, and rebuild
   only works for a cleanly-shut-down database (a backup never is).
4. **Multi-file databases multiply the problem.** Real databases span several
   data files/filegroups with cross-checked per-file LSNs and a boot page. The
   parser only handles `fileId == 1` today; attach needs **every** file,
   internally consistent. Reconstructing all of them *correctly* is exactly what
   `RESTORE` already does — so we'd be reimplementing it, worse.
5. **It's circular for the fallback use case.** The reason to involve an engine
   at all is to read backups/pages the parser **can't**. But reconstructing an
   MDF to attach requires the parser to first succeed at the page level (demux,
   decompress, reassemble). If it can do that, we mostly didn't need the engine;
   if it can't (TDE, ZSTD/QAT, odd framing), there's no MDF to attach. `RESTORE`
   sidesteps this entirely — the **engine reads the original `.bak` directly**,
   so it adds independent coverage the parser lacks. Attach can't.

In short, making an attach *safe* means reimplementing crash recovery and engine
file-consistency rules in our tool — high-risk work — to save a log-replay pass
we don't even pay for in the validation case. `RESTORE` hands that hard part to
the engine that already does it correctly.

(The one genuinely "light" attach-like product is virtual restore / HyperBac —
but it still runs real recovery behind its virtual file layer; see Non-goals.)

### Why `.bak` is the artifact that exists at all

Clean, directly-attachable `.mdf`/`.ldf` can only be produced by *quiescing* the
database — `sp_detach_db`, `ALTER DATABASE ... SET OFFLINE`, or stopping the
service. The engine writes the clean-shutdown marker on the boot page during
that shutdown; **there is no way to get clean files while transactions are
running.** That makes the MDF-copy method a *cold* operation: viable for static
sample/demo datasets (e.g. the Stack Overflow `.7z` distributions, detached
once) or a maintenance window, but **unacceptable for a 24/7 production database
— it requires downtime.**

`BACKUP DATABASE` exists precisely to avoid that: it is an **online, hot**
operation that runs while the database is fully live, copying data pages as they
change (hence "fuzzy") and capturing the slice of transaction log needed to
recover them. The log capture is the enabling feature — it's *why* a backup
needs no downtime, and *why* `RESTORE` (not attach) is the consistent path.

| | Clean MDF/LDF copy | `.bak` (BACKUP) |
| --- | --- | --- |
| DB offline required | yes (detach/offline/stop) | no — fully online |
| Tolerates constant transactions | no (must be quiescent) | yes (hot backup) |
| Consistency from | clean shutdown | data pages + captured log |
| Production-viable | maintenance window only | standard |
| Directly attachable | yes | no — needs `RESTORE` recovery |

Consequence for this tool: the artifact real/production systems actually produce
is the **`.bak`** (the only no-downtime option), so it is the correct input to
parse. The fuzzy-pages/recovery property isn't an obstacle to engineer around —
it is the price of the online backup that makes `.bak` the production format,
and the reason the engine foundation here is `RESTORE`.

## Architecture

One new runtime module plus a thin shared container helper. The bulk is reuse:
the container plumbing already exists in `tools/make_fixture.py` (in the *backup*
direction); this adds the *restore* direction.

```
                        ┌─────────────────────────────────────────┐
                        │ mssqlbak/engine_restore.py  (NEW)        │
  .bak  ───────────────▶│  RestoredDatabase (context manager):     │
                        │   1. podman cp  bak -> container:/tmp     │
                        │   2. RESTORE FILELISTONLY -> logical names│
                        │   3. RESTORE DATABASE ... WITH MOVE, REPLACE
                        │   4. yield mssql_python connection        │
                        │   5. DROP DATABASE + rm /tmp/bak (cleanup)│
                        └───────────────┬───────────────────────────┘
                                        │ reuses
                  ┌─────────────────────┴───────────────────────┐
                  │ mssqlbak/_mssql_container.py  (NEW, refactor)│
                  │  discover_container(), sqlcmd_base(),        │
                  │  podman cp / exec helpers                    │
                  │  (moved out of tools/make_fixture.py)        │
                  └──────────────────────────────────────────────┘
```

Consumers:

- **Validation harness** — `tests/test_sample_corpus.py` (NEW): for each `.bak`
  in `tests/fixtures/samples/`, open a `RestoredDatabase`, and for every table
  the parser supports, compare `read_table_rows(...)` against
  `SELECT * ... ORDER BY <pk>`. Reuses the `_normalize_pair` comparison logic
  from `test_engine_diff.py` (extracted into a shared `tests/engine_compare.py`).
- **Extraction fallback** — `extract_bak_to_delta(..., engine_fallback=True)`:
  in the per-table `except`/unsupported branch, route the table through the
  restored database instead of recording a skip.

### Reuse map

| Need | Already exists | Action |
| --- | --- | --- |
| Find the podman SQL Server container | `make_fixture.discover_container` | move to `_mssql_container.py` |
| `sqlcmd` base command, `podman cp`/`exec` | `make_fixture.sqlcmd_base`, `_run` | move to `_mssql_container.py` |
| `mssql_python` connection from env | `tests/engine_support.connect_engine` | generalize: parameterize DB name |
| Value comparison / normalization | `test_engine_diff._normalize_pair` | extract to `tests/engine_compare.py` |
| Per-table support classification | `inspect.classify_table` | call as-is to decide diff scope |
| Skip/》outcome reporting | `extract.ExtractReport` / `TableResult` | add `via_engine: bool` field |

## API / CLI surface

```python
from mssqlbak.engine_restore import RestoredDatabase

with RestoredDatabase(bak_path) as db:        # restores into container, drops on exit
    conn = db.connect()                       # mssql_python connection
    rows = db.select_all("dbo.SalesOrderHeader")
```

CLI (new subcommand, gated on the `restore` extra + a reachable container):

```
mssqlbak validate <file.bak>      # parser vs engine, per-table PASS/FAIL/SKIP summary
mssqlbak extract  <file.bak> --out DIR --engine-fallback
```

`validate` prints a per-table line (rows compared, mismatches) and exits
non-zero on any value mismatch — the same contract as `test_engine_diff`, scaled
to a whole database.

## Lifecycle, idempotency, failure modes

- **Restored DB name** is derived from the `.bak` (e.g. `val_<stem>_<pid>`) so
  concurrent runs don't collide; dropped in `__exit__` even on error.
- **Container discovery** mirrors `make_fixture`: auto-detect the `mssql/server`
  container, or `FIXTURE_CONTAINER` / env override. Missing container, missing
  `mssql_python`, or missing password ⇒ raise `EngineUnavailable` ⇒ the harness
  **skips** (never fails an ordinary `pytest` run), matching the existing
  engine-test convention.
- **`WITH MOVE`** targets are computed from `RESTORE FILELISTONLY` so multi-file
  databases relocate cleanly inside the container's data dir.
- **Big backups**: restore time/disk dominate. The harness restores once per
  `.bak` (session-scoped), diffs all tables, then drops — not once per table.

## Cost & scaling

`RESTORE` is **whole-database and all-or-nothing**: a 100 GB `.bak` inflates to
~100 GB+ of `.mdf`/`.ldf` and takes real wall-clock time (minutes to hours,
disk-bound). There is **no per-table restore** — wanting one table still costs
the whole database. Consequences baked into the design:

- **Amortize, never per-table.** Restore once per `.bak` (session-scoped), diff
  every table against that copy, drop. One big restore, not N.
- **Tier by size.** Full parser-vs-engine validation runs on the small/medium
  corpus every time (AdventureWorksLT ~7 MB; most AdventureWorks tens of MB).
  100 GB-class backups are an **opt-in, occasional deep run** (`@pytest.mark.engine`
  + a size gate), not part of the default suite. The small/medium set already
  exercises every decoder.
- **Instant File Initialization (IFI)** skips zeroing the data file on restore
  (the log still zeroes); enable it in the container to shorten — not remove —
  the data pass. SQL Server on Linux supports IFI.
- **Parser-side prerequisite (separate from this design).** The pure-Python path
  is not yet 100 GB-ready either: `mtf.py` does `buf = p.read_bytes()` (entire
  `.bak` into RAM) and `assemble_image` allocates a second full-size buffer for
  the page image — so a 100 GB backup needs ~100 GB+ of RAM as written. Reading
  pages via streaming/`mmap` instead of materializing the whole file and image
  is the **first** scaling work, and it's independent of (and arguably ahead of)
  the engine harness.

Net: engine validation targets the small/medium corpus by default; the 100 GB
case pressures the parser's memory model more than it pressures this design.

## Non-goals

- **Virtual mount / copy-on-write delta files** (HyperBac-style). Requires a
  filesystem-filter driver and on-the-fly recovery; large, OS-specific, and
  orthogonal to a Python parser. Explicitly excluded.
- **Remote / non-container SQL Server.** v1 targets the podman-on-localhost
  engine that `make_fixture` and forgedb already use (`podman cp` puts the `.bak`
  where the server can read it). A remote server needs a shared path/URL backup
  device — future work.
- **Replacing the parser.** The engine path is a validation verifier and a
  coverage safety net, not the default extraction route.

## LOC estimate

Moderate, not large — most logic is reuse/refactor of existing container and
comparison code.

| Component | New file | Est. net LOC | Notes |
| --- | --- | --- | --- |
| Container helper refactor | `mssqlbak/_mssql_container.py` | +40 / −30 in `make_fixture` | mostly *moved*, near net-zero |
| Restore-into-engine + lifecycle | `mssqlbak/engine_restore.py` | ~130–170 | FILELISTONLY parse, WITH MOVE, RESTORE, DROP, context mgr |
| Comparison helper extraction | `tests/engine_compare.py` | ~40 (moved from `test_engine_diff`) | shared `_normalize_pair` + row diff |
| Validation harness | `tests/test_sample_corpus.py` | ~90–130 | iterate `samples/`, per-table diff, skip plumbing |
| `extract` fallback wiring | edit `extract.py` (+ `ExtractReport`) | ~40–70 | `engine_fallback` branch + `via_engine` flag |
| CLI `validate` (+ `--engine-fallback`) | edit `_cli.py` | ~50–70 | new command, reuse report rendering |

**Total: ~350–500 net new LOC**, of which ~70–90 is moved (not new) code.

Phasing:

1. **Phase 1 — validation harness only** (`_mssql_container.py`,
   `engine_restore.py`, `engine_compare.py`, `test_sample_corpus.py`):
   ~250–350 LOC. Delivers the motivating use — automated parser-vs-engine
   validation over the downloaded sample corpus, no manual restore.
2. **Phase 2 — extraction fallback + CLI** (`extract.py`, `_cli.py`):
   ~90–140 LOC. Adds runtime "still get the data when we can't parse it".

## Open questions

- **Ordering for the diff.** `SELECT * ORDER BY <clustering key>` vs. parser
  emission order. For tables with a clustered PK, order by it on both sides; for
  heaps, sort both sides by a stable column tuple before comparing.
- **Type representation drift** beyond the cases `_normalize_pair` already
  handles (uuid spelling, sub-µs datetime, money/decimal). Expect a few more
  from real schemas (e.g. `float` round-trip, `xml` canonicalization) — extend
  the normalizer with the same "transform both sides identically" rule so it can
  only mask representation, never a wrong value.
- **How many sample tables to diff per run** (full corpus is GBs). Likely a
  marked slow test (`@pytest.mark.engine`) opt-in, not part of the default run.
