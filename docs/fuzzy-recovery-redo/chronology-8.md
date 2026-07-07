# Run 8 — Fix implemented: MTF ingests the trailing modified-page run

Date: 2026-06-27

## What was done

Implemented the run-7 fix in `mssqlbak/mtf.py`: MDF extraction now treats a
backup as **one or more image segments** and merges them with
**highest-page-LSN-wins**, so the trailing re-scan pass an online/fuzzy backup
appends (the post-modification image of every page changed mid-scan) overrides
the stale main-stream copy — exactly what SQL Server's RESTORE does.

Changes:
- `_scan_image_start(buf, start_off)` — find the next file-header-anchored image
  segment at/after an offset (512-byte stride; the trailing pass is off the main
  8 KB grid). `_find_image_start` now delegates to it.
- `_walk_image_pages` returns its stop offset (generator return value) so the
  next segment can be found beyond it.
- `_collect_pages_by_file(buf)` — walk every segment, keep the highest-LSN copy
  per `(file_id, page_id)`. Both `extract_mdf_files` and
  `_gather_raw_pages_by_file` (diff base) route through it.

For an ordinary single-segment backup the behaviour is unchanged (each page
appears once).

## Verification

- **Target tests (TDD red→green):** `test_dirty_cci_delete_row_count` and
  `test_dirty_cci_delete_deleted_ids_suppressed` were failing (6,834; ids
  5001–6000 leaked) → now pass on 2022.
- **Cross-version ground truth** (live `RESTORE` of each `.bak` and the `.cells`
  manifests agree): 2017 = 7000, 2019 = 6000, 2022 = 6000, 2025 = 7000. mssqlbak
  now matches **all four** exactly. (7000 = the mid-backup DELETE committed too
  late to be captured in that version's race — SQL Server restores 7000 too.)
  The two tests were made ground-truth-driven (assert the manifest count; skip
  suppression when the DELETE was not captured) instead of a fixed 6,000.
- **No regressions:** `test_mtf`, `test_mtf_gap_bridging`, `test_pages`,
  `test_striped_backup`, `test_engine_diff`, `test_compressed`,
  `test_rowcompress`, `test_pagecomp_anchor_coverage` → 154 passed. The 13
  value-correctness failures and the `committed_*` dirty-backup failures are
  pre-existing (verified by stashing the change). `ruff` + `pyright` clean.

## Remaining (separate issue, re-scoped in known_gaps)

`dirtycoverage_cci_delete` still has a non-fuzzy defect: the 5,000 compressed-
rowgroup rows' constant `phase` = 'compressed' (varchar(10)) decodes to '' while
`val` decodes correctly. That is a CCI compressed-segment decode bug for a
constant/single-dictionary string column, independent of this project. The
known-gap entry was re-scoped to it; the fuzzy over-read is closed.
