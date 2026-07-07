# Run 7 — The `.bak` *does* contain the deletion: trailing modified-page run

Date: 2026-06-27

## Why this run happened

Run 6 concluded the `.bak` genuinely lacked the redo for 834 of the 1000
deletions ("in-flight DELETE") and offered the user a choice between a precise
known-gap and regenerating the fixture. The user asked the decisive question:

> then how does sqlserver figure out how to restore the .bak if option 1

`RESTORE … FROM DISK` reads **only** the `.bak` file — there is no live
instance log involved. We had already observed that restoring this same file to
a fresh database yields **6,000** rows. Therefore the information needed to
remove all 1,000 deleted rows **must** be inside the `.bak`. Run 6's conclusion
could not be correct. This run found where that information lives.

## What was measured

1. **Post-restore ghost counts** (`sys.dm_db_page_info`, restored DB):
   - Delete-cluster pages 685–693: `slot_count == ghost_rec_count` (every
     record a ghost). 693 = 34/34.
   - Survivor pages 518–522: 0 ghosts. 517 = 34 ghosts, 523 = 93 ghosts
     (the partial pages that make the survivor count exactly 6,000).
   - mssqlbak reads those same pages 685–693 as **PRIMARY** (`status 0x30`,
     `ghost_rec_cnt = 0`). So the deletion **is** applied by restore but missed
     by mssqlbak.

2. **Page LSN comparison** (`.bak` via mssqlbak vs restored via `dm_db_page_info`):

   | page | `.bak` LSN (mssqlbak) | restored LSN | post-restore |
   |---|---|---|---|
   | 685 | 45:2824 (PRIMARY) | 45:**3208** | 161 ghosts |
   | 692 | 45:3064 (PRIMARY) | 45:**3448** | 161 ghosts |
   | 518 (survivor) | 43:536 | 43:536 (same) | 0 ghosts |

   Restore holds a **newer** image of page 685 (45:3208) than the copy mssqlbak
   reads (45:2824) — yet 45:3208 is *below* the captured redo start
   (FirstLSN 45:3448). No captured log record can produce it. The only
   explanation: the `.bak` already contains the newer (ghosted) image of page
   685, and mssqlbak is reading a **stale earlier copy** of the same page.

3. **Raw `.bak` scan for duplicate page headers** — confirmed the file contains
   each modified page **twice**:

   | page | copy 1 (8K-aligned, main data stream) | copy 2 (unaligned, near EOF) |
   |---|---|---|
   | 685 | LSN 45:2824, ghost_cnt **0** | LSN 45:3208, ghost_cnt **161** |
   | 692 | LSN 45:3064, ghost_cnt **0** | LSN 45:3448, ghost_cnt **161** |
   | 518 (survivor) | LSN 43:536, ghost_cnt 0 | *(no second copy)* |

4. **Trailing-run characterisation** — beyond the main aligned data stream
   (offsets 81920 … 5718016) there is a second run of **56 unaligned page
   headers** (offsets 5853184 … 6418432), one per page **modified during the
   backup**: system/allocation pages (8 = PFS, 11, 14, 16, 17, 20) plus the
   ghosted delete cluster 685–693 (each with full ghost counts, LSN 45:3208–
   3448). Survivor pages that were never touched mid-backup (e.g. 518) have no
   second copy.

## Root cause (corrected)

This is an **online/fuzzy backup**. After the main data-file scan, SQL Server
appends a second copy of every page that was modified *while the scan ran* — the
post-modification image. RESTORE writes the main stream, then overlays this
trailing modified-page run (and redoes the captured log), so the final pages are
the ghosted ones → 6,000 rows.

mssqlbak's `mssqlbak/mtf.py::_walk_image_pages` strides through the **main** data
stream in 8 KB steps and stops at the first gap it cannot bridge within
`_MTF_GAP_SCAN_PAGES` (10) pages. The trailing run sits far past the main stream
(after the log block) and is **unaligned** to the 8 KB stride grid, so the walk
never reaches it. `extract_mdf_files` therefore keeps only the first (aligned,
pre-modification) copy of pages 685–693 and drops the trailing ghosted copies.

**Conclusion:** Run 6 was wrong. The `.bak` is *not* missing the deletion. It is
a genuine, fixable mssqlbak bug in MTF page assembly: the trailing
modified-page run is ignored. This is not columnstore-specific and not a
recovery-redo engine — it affects any fuzzy backup where pages changed
mid-scan.

## The fix (defined)

Extend MTF extraction to also ingest the trailing modified-page run and apply
**highest-LSN-wins** (equivalently, last-copy-wins, since trailing copies always
carry a ≥ LSN) when placing pages into the dense image. Then mssqlbak's
assembled image matches the state SQL Server restores, and the dirty-CCI delete
case reads 6,000.

Likely also resolves / improves other `dirtycoverage_*` fuzzy fixtures; must be
verified in Phase 2.
