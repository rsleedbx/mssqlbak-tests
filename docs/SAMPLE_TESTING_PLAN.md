# Sample-corpus testing plan

Status: **in progress** (Phase 1). How we use the downloaded real-world `.bak`
corpus in `tests/fixtures/samples/` to find regressions per commit, what an
exploratory survey of that corpus revealed, and the script + rationale behind it.

## Latest fixes (since the original survey)

The survey below drove several fixes; record them so the findings table is read
in context (the raw survey numbers predate these):

- **ROW data compression — SUPPORTED.** ROW-compressed rowsets
  (`sysrowsets.cmprlevel == 1`) are decoded via the CD (Column Descriptor) record
  format (`mssqlbak.rowcompress`): header + 4-bit-per-column CD array + short/long
  data regions, with integers reconstructed from their excess-encoded big-endian
  form (`value = BE(bytes) − 2^(8·len−1)`). Validated byte-for-byte against the
  `cmp_row` fixture (1000 rows identical to the uncompressed `cmp_none`) and
  cross-checked with the OrcaMDF reference. Supported types under ROW so far:
  the integer family, bit, money/smallmoney, char/varchar/nchar/nvarchar,
  binary/varbinary, uniqueidentifier; a ROW table with any other type still skips
  with a precise reason.
- **PAGE data compression — SUPPORTED (container).** PAGE-compressed rowsets
  (`sysrowsets.cmprlevel == 2`) are decoded by extending the CD path with the
  per-page compression-info (CI) structure (`mssqlbak.rowcompress.parse_page_ci`):
  a CI header (`u8 0x06`, `u16` dict offset, `u16` size), a column-prefix anchor
  record, and a dictionary whose entries are themselves prefix-compressed against
  the anchor. `physical_columns_page` resolves dictionary symbols (CD indicator
  `0xC`) and full-anchor (`ZeroByte` on an anchored column) values; pages where
  compression did not pay off hold plain CD records. **Partial** column prefixes
  raise and skip (not yet validated — no fixture exercises them), never
  mis-decode. Validated byte-for-byte against `cmp_page` (1000 rows identical to
  `cmp_none`, covering both a CI page and a plain-CD page). This goes beyond
  OrcaMDF, which leaves PAGE unsupported. **columnstore** remains skipped.
- **Record-type dispatch — ADDED.** Both read paths now classify each slot's
  record type before decoding (`mssqlbak.recordtype`): ghost (deleted-but-not-
  cleaned), index, blob-fragment and forwarding-stub records are skipped, while
  primary and *forwarded* records are emitted. A forwarded heap row is stored
  once as its in-place forwarded record (its stub is skipped), so no pointer
  following or de-duplication is needed; clustered indexes never forward. The
  FixedVar (status bits A/B) and CD (header) formats use different type enums,
  both cross-checked with OrcaMDF. On the all-primary fixtures this is a no-op;
  on real data it removes phantom/garbage rows.
- **Compressed `decimal`/`numeric` + classic `datetime` — DECODED.** The CD path
  now has a single value seam (`rowcompress.decode_compressed_value`) that either
  normalises bytes back to on-disk form (the integer/string/binary family) or
  dispatches to a dedicated decoder for types whose compressed encoding has no
  on-disk equivalent: `decimal`/`numeric` use the vardecimal bit-packed form
  (sign + biased exponent + 10-bit base-1000 mantissa chunks, reconstructed with
  exact `Decimal` arithmetic), and classic `datetime` (type 61) uses the
  minimal-width excess-encoded big-endian time/day split. Both ported from the
  OrcaMDF algorithm and unit-tested against hand-derived / OrcaMDF byte vectors.
  The compression support gate (`row_type_supported`) is now a single source of
  truth derived from the decode dispatch, so it can never drift from the
  decoders. Validated end-to-end against a paired ROW/uncompressed twin backup
  (decimal + classic datetime decode byte-identically across 1000 rows).
- **Compressed 2008+ temporal family — DECODED.** `date`, `time`, `datetime2`
  and `datetimeoffset` store their ordinary little-endian on-disk bytes under
  ROW/PAGE compression, only trimmed of trailing zero (high-order) bytes; the
  normaliser right-pads to the fixed on-disk width (scale-driven for the
  fraction) and the existing on-disk decoders read them unchanged. Reverse-
  engineered from `DBCC PAGE` dumps (no OrcaMDF reference exists) and validated
  end-to-end against an uncompressed twin: **0 mismatches across 300 rows × 10
  temporal columns** spanning every scale (0/3/7), all four types, positive and
  negative timezone offsets, and NULL rows. `smalldatetime` (type 58) uses a
  distinct special encoding like classic `datetime` and remains deferred (low
  corpus value).
- **Wide-record CD decode — confirmed correct.** An earlier probe suggested a
  decode-misalignment / NULL bug on wide compressed records; re-checking through
  the *real* reader on a 5-column ROW table (int/int/varchar/decimal/datetime,
  1000 rows, multiple pages) showed contiguous ids and exact values — the bug was
  a standalone probe-script artifact, not in the production path.
- **Corpus impact of ROW/PAGE (measured).** All 19 real compressed tables
  (`WideWorldImporters-Full` 17, `AdventureWorks2016_EXT` 2) are **PAGE**, none
  ROW. With the container solved, every one skips only for a column **type** not
  yet decodable from its compressed form. Needed types, by table count:
  `datetime2` (type 42) — **17/17** (decoder landed); CLR UDT/`geography` (240)
  — 5; `decimal` (106) — 3 (decoder landed); `date` (40) — 1 (decoder landed).
  The remaining blocker is off-row `geography`/CLR; with the temporal family
  decoded, the 17 `datetime2` tables should now read (pending a corpus run).
- **Corpus run after temporal (WideWorldImporters-Full, measured).** `datetime2`
  no longer appears as a skip reason anywhere — confirmed end-to-end (extracted
  30 tables / 655,198 rows). Driving the system-versioned `*_Archive` history
  tables past the (now-cleared) `datetime2` gate exposed three **separate,
  non-temporal** blockers, none of which emit garbage (all skip):
  1. **Unicode compression (SCSU) — SUPPORTED.** Under ROW/PAGE compression
     `nchar`/`nvarchar`/`sysname` values are stored in the Standard Compression
     Scheme for Unicode (≈1 byte/char), *not* UTF-16LE, and *always* (a string
     that does not compress is still a valid SCSU stream via Unicode mode, so no
     per-value flag is needed). e.g. `Colors_Archive.ColorName` is stored as
     `47 72 61 79 10` = "Gray" + SQL Server's trailing `0x10` (select-window-0
     no-op). `mssqlbak.scsu` ports the Unicode TR6 reference expander (cross-
     checked with OrcaSql) and is wired in as a dedicated compressed decoder for
     `nchar`/`nvarchar`; `nchar` is re-padded to its declared width. Validated by
     TR6 byte-vector unit tests and end-to-end on the corpus (decoded values are
     real strings: "Gray", "Contra", "Van with Chiller"). The committed `cmp_*`
     fixtures use `varchar` (never Unicode-compressed), so this was invisible
     until the temporal work let these history tables be attempted.
  2. **Off-row `geography`/CLR (type 240) — still skipped, 5 tables**
     (`Cities_Archive`, `Countries_Archive`, `Customers_Archive`,
     `StateProvinces_Archive`, `Suppliers_Archive`).
  3. **Multi-file index root — 3 tables** (`ColdRoomTemperatures_Archive`,
     `People_Archive`, `StockItems_Archive`): the index root points at a
     `file_id` not in the assembled image (`IndexError`); a multi-file
     page-image / partition issue, plus 2 `partitioned` and 1 `columnstore`
     skip that are known v1 limitations.
- **WideWorldImporters-Full after temporal + SCSU (measured).** Extracted
  **37 tables / 655,205 rows**, **11 skipped** (was 30 / 18 before SCSU): the 11
  are 5 off-row `geography` (type 240), 3 multi-file index-root `IndexError`, 2
  `partitioned`, and 1 `columnstore` — all separate subsystems, none a string or
  temporal type.
- **Multi-file databases — CLOSED.** The page image is now reconstructed across
  *every* data file (`file_id > 1`), and `classify_table` receives the full
  `available_files` set. WideWorldImporters-Standard went from **2/48** supported
  to **48/48, 0 skipped**; WWIDW-Standard 29/29.
- **Compressed-demux hang — FIXED.** A false-positive `MSSQLBAK` record header
  (garbage whose Huffman table passes the Kraft test) made
  `xpress.decompress_until_input` spin forever; the output is now capped so it
  raises and the demux re-syncs. This unblocked WideWorldImporters-Full.
- **Metadata on compressed backups — FIXED.** `read_bak_metadata` now reads the
  `TAPE`/`SSET` descriptors out of the `MSSQLBAK` container (decompressing only
  its leading chunks), so `info`/metadata works for compressed backups; only
  TDE-encrypted containers still raise.
- **Headerless primary file / missing-catalog resilience — FIXED.**
  `assemble_files` keeps a real data file that lacks a file-header page (≥64
  pages + bounded image) while still dropping mis-decode phantoms, and
  `recover_schema` degrades to a clear `CatalogError` when `file_id=1` is truly
  absent.  `WideWorldImporters-Full_old` now extracts instead of raising.
- **Dropped-column layout — FIXED.** Variable-column index is derived from the
  catalog `leaf_offset`, so a dropped column no longer shifts later columns
  (WWI `*_Archive` history tables).
- **Observability — ADDED.** `mssqlbak.enable_logging()` / CLI `-v` emit
  per-phase and per-table timing plus demux/assemble progress to stderr, so a
  slow conversion shows *which* phase/table is responsible. The survey tool
  (below) uses it.

## Why a real-world corpus

The committed fixtures (`tests/fixtures/*.bak`) are *synthetic* — built by
`tools/make_fixture.py` to exercise specific features (type matrix, constraints,
XML, compression). They prove the parser handles what we *designed* for. The
sample corpus does the opposite job: **real databases shipped by Microsoft**
(AdventureWorks, WideWorldImporters) plus a few ML-tutorial DBs, which exercise
shapes we did *not* hand-pick — multiple filegroups, data compression, large
tables, and (importantly) the compressed-backup container that most real `.bak`
files actually use.

The corpus is **git-ignored** (large) and fetched with
`python -m tools.fetch_sample_baks` (see that script's manifest). Tests must
therefore `skip` cleanly when a file is absent, matching the existing
fixture/engine convention.

## Data-gathering survey

Before designing tests, we ran each `.bak` through the parser's read paths to
see what breaks and where coverage drops. The throwaway script (not committed;
reproduced here for the record):

```python
"""Run the parser over every sample .bak and report outcomes."""
from __future__ import annotations

import sys
import time
import traceback
from collections import Counter
from pathlib import Path

SAMPLES = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "samples"


def survey_one(bak: Path) -> None:
    size_mb = bak.stat().st_size / 1e6
    t0 = time.time()
    print(f"\n=== {bak.name}  ({size_mb:.0f} MB) ===", flush=True)
    try:
        from mssqlbak.reader import read_bak_metadata
        read_bak_metadata(bak)
        print("  info: OK", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  info: FAIL {type(exc).__name__}: {exc}", flush=True)

    try:
        from mssqlbak.catalog import recover_schema
        from mssqlbak.inspect import classify_table
        from mssqlbak.pages import PageStore
        store = PageStore.from_bak(bak)
        tables = recover_schema(store).tables
        reasons: Counter[str] = Counter()
        ok = 0
        for t in tables:
            sup = classify_table(t)
            if sup.supported:
                ok += 1
            else:
                reasons[(sup.reason or "?").split(":")[0]] += 1
        print(f"  schema: OK  {len(tables)} tables, {ok} supported", flush=True)
        for r, n in reasons.most_common():
            print(f"      skip {n:>4}  {r}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  schema: FAIL {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
    print(f"  elapsed {time.time() - t0:.1f}s", flush=True)


def main() -> None:
    pats = sys.argv[1:]
    baks = sorted(SAMPLES.glob("*.bak"), key=lambda p: p.stat().st_size)
    if pats:
        baks = [b for b in baks if any(p.lower() in b.name.lower() for p in pats)]
    print(f"surveying {len(baks)} sample .bak files (ascending size)")
    for bak in baks:
        survey_one(bak)


if __name__ == "__main__":
    main()
```

Method: run ascending by size (fast signal first), per `.bak` capture three
things — does metadata (`read_bak_metadata`) parse, does schema recovery parse,
and the per-table `classify_table` supported/skip histogram — plus wall-clock
time. Exceptions are caught per file so one failure doesn't stop the survey.

## What the survey found

Surveyed the small/medium corpus plus WideWorldImporters (the large compressed
files time out — itself a finding).

| Finding | Evidence |
| --- | --- |
| **Most real backups are compressed (MSSQLBAK)** | ~20 of ~23 non-LT backups; only older `AdventureWorksLT2012–2019` and `NYCTaxi_Sample` are uncompressed MTF |
| **`info`/metadata failed on compressed backups** | every compressed file → `ValueError … MSSQLBAK container`; **now FIXED** — `read_bak_metadata` decompresses the container's leading descriptor blocks |
| **`multi-file` was the dominant coverage gap** | originally `WideWorldImporters-Standard` **2 of 48** (46 `multi-file`); **now CLOSED** — 48/48 after multi-file support landed |
| **Compressed decode is ~1000× slower per MB** | `NYCTaxi` 102 MB *uncompressed* → 0.1 s; `WideWorldImporters-Standard` 127 MB *compressed* → ~125 s; `AdventureWorksDW` 22 MB compressed → ~20 s *(steady, no longer hangs)* |
| **`supported` ≠ correct values** | `classify_table` is metadata-only; row values are unverified without the engine verifier (see `ENGINE_VALIDATION.md`) |

Of the concrete defects surfaced before checking a single value, **multi-file
tables**, the **compressed-path hang**, and **`info`/metadata on compressed
backups** are fixed; **compressed-path throughput/memory** remains open.

### First generated snapshot (`SAMPLE_COVERAGE.md`)

`python -m tools.sample_coverage --max-mb 205` surveyed 30 of 32 downloaded
samples (~18 min; `AdventureWorksDW2016_EXT` 883 MB and `tpcxbb_1gb` 234 MB are
over the cap). Results are the data-driven Phase 2 worklist — see
[SAMPLE_COVERAGE.md](SAMPLE_COVERAGE.md):

- **29 surveyed clean; 25 databases fully supported** (every table extractable,
  0 skips). **1066 of 1095 user tables supported.** All AdventureWorks
  OLTP/DW/LT, WWI-Standard (48/48) and WWIDW-Standard (29/29) are 100%.
- **Remaining skips, by impact (confirms the worklist order):**
  ROW/PAGE compression **×19** (`WideWorldImporters-Full` 17, `AdventureWorks2016_EXT` 2)
  > columnstore **×8** (`WideWorldImportersDW-Full` 6, `NYCTaxi_Sample` 1, `WideWorldImporters-Full` 1)
  > partitioned **×2** (`WideWorldImporters-Full`). **Zero `multi-file` skips** — that gap is closed.
- **Finding (now FIXED) — `info`/metadata FAILed on every compressed backup**
  (24 of 24 MSSQLBAK files; uncompressed MTF backups parsed fine). Closed in
  Phase 1.3: `read_bak_metadata` decompresses the container's leading
  descriptor blocks. The regenerated snapshot's `Metadata` column now shows
  `ok` for every surveyed compressed backup.
- **Finding (now FIXED) — resilience-contract violation on
  `WideWorldImporters-Full_old`.** `assemble` dropped `file_id=1` (1073 real
  pages incl. the boot page) because its page 0 is not a file-header page in that
  older backup, leaving only `file_id=3`; schema recovery then raised a raw
  `IndexError`. Closed by two changes: (a) `assemble_files` now keeps a
  *headerless* file that is unambiguously real (≥64 pages **and** a bounded
  dense-image size), which keeps file 1 while still dropping mis-decode phantoms
  (e.g. the observed `file_id=62706`, 4 pages at page id 3.9e9 → a 30 TB image);
  (b) `recover_schema` raises a clear `CatalogError` ("no primary data file")
  when `file_id=1` is genuinely absent, instead of `IndexError`. After the fix
  `WideWorldImporters-Full_old` surveys identically to `WideWorldImporters-Full`
  (files [1, 3], 48 tables, 28 supported).

## Rationale: why these tests

- **Resilience contract is the cheapest, highest-value guard.** `extract` is
  designed to never abort — every table is `extracted` or carries a
  `skip_reason`. Asserting that over real databases catches the most damaging
  regression class (a commit starts crashing or silently dropping tables) for
  almost no code.
- **A committed coverage snapshot makes per-commit deltas visible.** The survey
  output (tables total / supported / skip histogram per `.bak`) is the exact
  signal for "looking at bugs on each commit": counts rise when a feature lands,
  fall on a regression. Same generated-doc + test pattern already used by
  `BACKUP_COVERAGE.md` et al.
- **Tiering is forced by the perf finding.** A 127 MB compressed file at ~135 s
  (and the 883 MB `AdventureWorksDW2016_EXT` at minutes + GBs of RAM) cannot run
  per commit. Split into a fast lane (uncompressed/small, every commit) and a
  slow lane (compressed/large, nightly/opt-in).
- **Value-correctness stays on the fast lane.** The engine-diff verifier
  (`ENGINE_VALIDATION.md`) is restored-backed and slow, so it diffs only the
  small/uncompressed samples per commit.

## Plan (phased)

### Phase 1 — measure & guard (tooling + tests)

1. **Promote the survey** into a committed tool + generated doc — **DONE**:
   - `tools/sample_coverage.py` — regenerates a `docs/SAMPLE_COVERAGE.md`
     snapshot (per-`.bak` container, table count, supported/skip histogram,
     elapsed). Surveys whichever samples are downloaded; writes incrementally
     (ascending by size) and uses the package progress logging.
2. **Corpus test** — **DONE** as `tests/test_samples.py` (not a new
   `test_sample_corpus.py`): one parametrized case per manifest sample, which
   - *skips* when the file is absent (clean checkout stays green);
   - asserts the **resilience contract** (no raise; every table extracted or
     carries a `skip_reason`);
   - for samples in the `VERIFIED` snapshot, asserts **0 skips** and the exact
     table/row counts; unverified-but-present samples are `xfail`.
   23 samples are currently in `VERIFIED`.
3. **Close the remaining survey defects:**
   - **Metadata on compressed backups — DONE (fix + test).** *Fix:*
     `read_bak_metadata` now routes `MSSQLBAK` containers through the demux —
     `mssqlbak.compressed.iter_mtf_descriptor_blocks` decompresses only the
     container's leading chunks (the `TAPE`/`SSET` descriptor blocks, which
     precede the data pages) and reuses the existing TAPE/SSET decoders, so
     metadata works for compressed backups and only TDE-encrypted containers
     (no decodable descriptors) still raise. *Test:*
     `tests/test_reader.py::test_read_bak_metadata_on_compressed_matches_uncompressed`
     asserts the compressed fixture agrees with its uncompressed twin on the
     database-derived fields; `test_read_bak_rejects_undecodable_container`
     pins the TDE/truncated message.
   - **Compressed-decode perf budget — open.** A time/memory ceiling assertion
     on compressed decode, leveraging the new `mssqlbak.enable_logging` timing.

### Phase 2 — full sample-corpus coverage (prerequisite for Phase 4)

Goal: **every user table in every downloaded sample `.bak` extracts** (no
`skip_reason`, no crash). The survey skip histogram is the worklist, ordered by
real-world impact:

| Skip code | Where it hurts most | Work to close it | Size | Status |
| --- | --- | --- | --- | --- |
| `multi-file` | WWI-Standard, WWI-DW | assemble the page image across **all** data files (fileId > 1), then pass the full `available_files` set to `classify_table` | medium | **DONE** |
| `compressed` → ROW | AdventureWorks2016_EXT, WWI-Full `*_Archive` | decode ROW CD-format records (`mssqlbak.rowcompress`) | medium | **ROW done** (integer/string/binary family + `decimal`/`numeric` vardecimal + classic `datetime`); remaining ROW types (`datetime2`/`date`/`time`/`datetimeoffset`, real/float) + long-data/LOB columns open |
| `compressed` → PAGE | WWI-Full | decode the per-page dictionary/anchor on top of CD records | medium–large | **container DONE** (dictionary + full-anchor + plain-CD pages; partial-prefix skips); shares the type-decode seam with ROW |
| `compressed` → **columnstore** | WWI-DW fact tables, NYCTaxi, WWI-Full | decode columnstore segments (column-segment + dictionary + RLE + deltastore) — a distinct, larger storage format, **not** row compression | large | open |
| `partitioned` | large fact tables (WWI-Full transactions) | follow every partition's page chain, not just the first | small–medium | open |
| `unsupported-type` | scattered | add decoders for any remaining column types surfaced by the corpus | per-type | open |
| backup-compression perf | all large compressed `.bak` | fix `mssqlbak.compressed` throughput + the whole-file-in-RAM model in `mtf.py` so large compressed backups process in reasonable time/memory (enabler, not a row feature) | medium | open |

Priority now that **multi-file is closed**, **ROW + PAGE containers are
decoded**, and a **record-type dispatch + per-type compressed decode seam**
exist: the corpus blocker is the **compressed encoding of the remaining column
types**. Measured demand (above): `datetime2` (17 tables) ≫ `geography`/CLR UDT
(5) > `decimal` (3, decoder landed) > `date` (1). `decimal`/`numeric` and classic
`datetime` are now decoded (vardecimal + excess-BE), but their **corpus
round-trip is unvalidated** until the fixture carries them.
Next (Phase A): regenerate the `compressionmatrix` fixture so the `cmp_*` tables
include `decimal`/`datetime`/`datetime2`/`date`/`time`/`datetimeoffset`/
`smalldatetime` columns (current `cmp_*` are int/varchar only) — this both
validates the new `decimal`/`datetime` decoders row-for-row against `cmp_none`
**and** provides the ground truth to reverse-engineer compressed `datetime2`/
`date` (no OrcaMDF reference for those). The same regen should add a
**uniquifier** (non-unique clustered index), **sparse columns**, and a
**ghost/forwarded** table so all record-layer features are validated in one
provisioning pass. That unblocks ~12 of 17 WWI PAGE tables. Then off-row/CLR
(`geography`) and partial column prefix; then backup-compression perf/streaming
(so the big compressed files are testable per commit); then **columnstore** (the
largest single item) and partitioned. Each closed gap shows up as rising
`supported` counts in `SAMPLE_COVERAGE.md`.

**Exit criterion:** `SAMPLE_COVERAGE.md` shows 100% supported across all
downloaded samples, and the corpus extracts end-to-end within the slow-lane
budget. (Columnstore-only tables such as `NYCTaxi_Sample` may remain a
documented exception until columnstore decode lands.)

### Phase 3 — value correctness (engine verifier)

Cross-check decoded rows against a live engine via `docs/ENGINE_VALIDATION.md`
(restore-backed). Runs on the fast lane (small/uncompressed) per commit; the
large corpus is opt-in.

### Phase 4 — fuzzy / online-backup characterization (last)

**Gated on Phase 2** (we must extract clean backups fully before we can
meaningfully reason about messy ones). Real backups are taken *online*: SQL
Server permits concurrent DDL/DML/TCL during `BACKUP` and keeps the restore
consistent by capturing the **log**, which `RESTORE` later replays. `mssqlbak`
reads only data pages and **does not replay the log**, so a backup taken with
writes in flight can make the parser show **uncommitted** data (undo not
applied) or miss **committed** data (still only in the log). Today's synthetic
fixtures are built quiescent, so this boundary is untested.

**Assertion model — characterization, not equality.** For these fixtures the
parser and a recovered engine *should* disagree; the test asserts only that the
parser (1) does not crash on an in-flight image, (2) returns the on-disk
pre-recovery state, and (3) the divergence from the engine is **measured and
recorded**. This quantifies the "no log replay" limitation and becomes the
acceptance test for the PLANNED log-backup/replay feature (`BACKUP_COVERAGE.md`)
— when that lands, the divergence goes to zero and the same test proves it.

**Deterministic technique (not a concurrency race).** Racing a workload against
`BACKUP` is non-deterministic on a small DB. Force the fuzzy state instead:

```sql
BEGIN TRAN;
UPDATE dbo.t SET v = 'uncommitted' WHERE id = 1;
CHECKPOINT;                       -- flush the uncommitted dirty page to the data file
BACKUP DATABASE db TO DISK = ...  WITH COPY_ONLY;   -- backup reads it from disk
ROLLBACK;                         -- engine reverts; the .bak keeps the uncommitted page
```

The `.bak` now contains a value `RESTORE` would roll back but `mssqlbak` will
show — a repeatable demonstration of the gap. Build via a new
`tools/fuzzymatrix.py` → `tests/fixtures/fuzzycoverage_full.bak`.

**Page-state edge cases (independent of the log question).** The same online-DDL
menu generates on-disk shapes worth dedicated fixtures, exercising the
record/page reader directly:

- `ALTER TABLE` add/drop column → mixed row versions, dropped-but-present columns, NULL-bitmap shifts.
- online `ALTER INDEX REBUILD` → allocation churn, lingering old/ghost pages.
- `TRUNCATE` → rapid page de-allocation.

**Source note.** The motivating reference mixes authoritative (MS Learn) and
non-authoritative (blog) citations; the load-bearing claims — online backup
permits concurrent DDL/DML, and recovery (log replay) is what makes the restore
consistent — are MS-documented and correct. The Error 3023 exceptions
(`ALTER DATABASE ADD/REMOVE FILE`, `DBCC SHRINK`, overlapping backups) don't
affect this tool.

## Size/perf reference (observed)

| Backup | MB | Container | Schema-parse time |
| --- | --- | --- | --- |
| `AdventureWorksLT2014` | 14 | uncompressed | 0.1 s |
| `NYCTaxi_Sample` | 102 | uncompressed | 0.1 s |
| `AdventureWorksDW2014` | 22 | compressed | ~20 s |
| `AdventureWorks2014` | 47 | compressed | ~42 s |
| `WideWorldImporters-Standard` | 127 | compressed | ~136 s |

Uncompressed scales fine; compressed time grows ~linearly but with a ~1000×
constant — the signal that `mssqlbak.compressed` (and the whole-file-in-RAM
model in `mtf.py`) is the first performance target. The per-phase logging
(`mssqlbak.enable_logging` / CLI `-v`) now attributes that time to the demux
(steady, CPU-bound XPRESS — note each chunk is currently decoded twice) and to
the dense-image assembly (a sparse secondary file can allocate a multi-GB
mostly-zero image — e.g. WWI-Full file 3 is ~2 GB for ~49k real pages).

## Related

- `tools/fetch_sample_baks.py` — fetches the corpus (manifest + sources).
- `tools/sample_coverage.py` — surveys the downloaded corpus → `docs/SAMPLE_COVERAGE.md`.
- `tests/test_samples.py` — per-sample resilience + verified-snapshot test.
- `docs/ENGINE_VALIDATION.md` — engine-backed value validation & the restore-vs-attach rationale.
- `docs/BACKUP_COVERAGE.md` — backup-type coverage (multi-file listed PLANNED).
