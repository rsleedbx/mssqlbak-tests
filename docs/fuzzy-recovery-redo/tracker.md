# Tracker — Fuzzy backup: trailing modified-page run dropped

**DONE (run 8): fix implemented and verified.** An online/fuzzy backup appends a
**trailing run of re-copied modified pages** (the post-modification image of
every page changed mid-scan) after the main data-file scan. `mssqlbak/mtf.py`
now merges all image segments with **highest-page-LSN-wins**, so it reflects the
same final state SQL Server's RESTORE produces. Row counts now match the live
restore + `.cells` manifest on every version: 2017=7000, 2019=6000, 2022=6000,
2025=7000 (7000 = DELETE committed too late to be captured). No regressions.

Run 6's "in-flight DELETE / `.bak` lacks the redo" conclusion was wrong and is
retracted (run 7). No fixture change was needed.

## Phase status

| Phase | Goal | Status |
|---|---|---|
| 0 | Pin the offline signal | **done — trailing modified-page run dropped by `extract_mdf_files`** |
| 1 | Fix MTF assembly: merge image segments, highest-LSN-wins | **done (run 8)** |
| 2 | Corroborate across versions + other `dirtycoverage_*`; update known_gaps/spec | **done (run 9)** |

## The fix (Phase 1, implemented run 8)

`mssqlbak/mtf.py`:
- `_scan_image_start(buf, off)` finds the next file-header-anchored image segment
  (512-byte stride; the trailing pass is off the main 8 KB grid).
- `_walk_image_pages` returns its stop offset.
- `_collect_pages_by_file(buf)` walks every segment and keeps the highest-LSN
  copy per `(file_id, page_id)`. `extract_mdf_files` and
  `_gather_raw_pages_by_file` route through it. Single-segment backups behave
  exactly as before.

## Follow-ups — DONE (run 9, see chronology-9.md)

- **Compressed (`MSSQLBAK`) path**: verified with a generated compressed fuzzy
  fixture. The container re-stores modified pages (`_iter_pages` yields 42 dup
  page_ids); the **eager** path already merges them correctly (last-wins =
  higher-LSN-later → 6,000, matches RESTORE). Fixed a latent **lazy**-path bug:
  `_FileChunkArray.lookup` now returns the latest chunk for a duplicated extent
  (`tests/test_chunk_index.py`). `tools/diag/_diag_compressed_fuzzy.py`;
  `dirty_backup_concurrent(compression=…)`.
- **`dirtycoverage_cci_delete` residual**: both the constant `phase` string
  (enc=3 compact-RLE non-nullable shift) and the `score` FLOAT (enc=4 non-nullable
  base = `mn`, not `null_val`) are fixed — in the Python decoders **and** the Rust
  fast path. The fixture is now fully clean on all four versions; known_gaps entry
  removed.

## Follow-up — DONE (run 10, see chronology-10.md)

- **`dirtycoverage_committed_delete_v4` (SS2017)**: 3 phantom deleted rows
  (id=328/656/984) were NOT missing log records — all 1000 committed DELETEs are
  present and well-formed (`fn_dump_dblog`: 1000 × `LOP_DELETE_ROWS`, all
  sub=0x00/disc=0x03). The 3 records each begin at block offset **0x30** in an
  OPEN log block (first record of a flush segment), below the hardcoded
  `_BLOCK_HDR=0x48` where the OPEN-block scan starts, so the scan landed
  mid-record and dropped them. Fixed: `_iter_cont_records` now also scans the
  `[0, 0x48)` prefix of OPEN blocks. Fixture clean on all versions; known_gaps
  entry removed. The old gap text (`sub=0x00/disc=0x00`, "id=372") was wrong.

## Still open (separate, pre-existing — NOT this project)

- `dirtycoverage_cci_update` on 2017/2019: REDO sector-framing NUL byte
  (`updat\x00d_…`) and 6686-vs-7000 row count. Same class as `committed_update_*`
  gaps; registered under its own known_gaps entry.

## Design decisions

| ID | Decision | Chosen | Resolved? |
|---|---|---|---|
| D2 | Ambiguity policy | correctness-first | ✓ |
| D4 | Version-drift investment | prove 2022, fast-follow | ✓ |
| D1/D3 | recovery-engine scope | **moot** — not a recovery engine; MTF assembly fix | — |

## Blockers

| ID | Blocker | State |
|---|---|---|
| B1 | forgedb 2022 container running | ✓ up |

## Verified facts (run 7)

- SQL Server `RESTORE` (reads only the file) → **6,000**; ids 5001–6000 gone.
- Post-restore `dm_db_page_info`: pages 685–693 are **all ghosts**
  (`slot_count == ghost_rec_count`); survivors 517/523 partially ghosted
  (34/93) to land on exactly 6,000.
- The `.bak` contains each modified page **twice**: an 8K-aligned main-stream
  copy (pre-modification, ghost_cnt 0) and an unaligned trailing copy
  (post-modification, ghost_cnt full, higher LSN). Survivor pages not touched
  mid-scan (e.g. 518) appear once.
- Trailing run = **56 unaligned page headers**, offsets 5853184…6418432: PFS
  (8), system pages (11,14,16,17,20), and the ghosted delete cluster 685–693
  (LSN 45:3208–3448).
- mssqlbak main aligned stream = 398 page headers, offsets 81920…5718016;
  `_walk_image_pages` stops before the trailing run (gap > `_MTF_GAP_SCAN_PAGES`
  and off-grid).

## Diagnostics

- Raw duplicate-page-header scan + trailing-run characterisation: ad-hoc
  (see chronology-7.md).
- Post-restore page truth: `sys.dm_db_page_info` via restore into 2022 container.
- Authoritative log inventory: `tools/diag/_diag_fn_dump_dblog.py`.
- Fixture: `tests/fixtures_2022/dirtycoverage_cci_delete.bak`.

## Superseded (now known wrong)

- ❌ Run 1: "needs ARIES redo of page deallocation."
- ❌ Run 6: "in-flight DELETE; the `.bak` lacks the redo for 834 rows."
  Disproven by run 7 — the deletion is present as the trailing modified-page run.
