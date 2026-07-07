# Run 6 — Live page truth + delete-record pages: an in-flight DELETE

**Date**: 2026-06-27
**Back to index**: [chronology.md](chronology.md)

---

## Actions

- `_diag_cci_pagealloc.py` — restored the `.bak` live and queried
  `sys.dm_db_database_page_allocations` (pages 480–700) + `%%physloc%%` of sample
  rows.
- `fn_dump_dblog` — grouped `LOP_DELETE_ROWS` / `LOP_COUNT_DELTA` by `[Page ID]`.

## Results

- **Both clusters survive recovery as allocated DATA pages**: pages 517–523 (7)
  and 685–693 (7) all `is_allocated=1` post-restore. Recovery does **not**
  deallocate the deleted cluster.
- `%%physloc%%` of surviving rows are **columnstore pseudo-locations** (compressed
  `0x1000000`, delta `0x2000000`); deleted ids 5001/5500/6000 are **absent**
  (→ 6,000 confirmed again).
- **The 166 `LOP_DELETE_ROWS` target only pages 692 (132) + 693 (34)** — the last
  two pages of the deleted cluster. `LOP_COUNT_DELTA` hit low catalog pages
  (17/20/64/161/189/195), not the delta data pages.

## Interpretation (mechanism finally explained)

The deleted cluster (pages 685–693, seq-45 LSNs) is the **RESET re-insert** of ids
5001–6000 done immediately before the backup; the survivors (pages 517–523, seq
43) are the original setup insert. During the fuzzy backup a `DELETE id 5001–6000`
ran, but by the time the captured log ended (LastLSN `45:3528`) it had only
ghosted **166** rows (pages 692–693). Pages 685–691 still carry page LSN
`45:2824` — the delete **had not reached them yet** in the captured image, so they
are PRIMARY with no ghost and no log record.

→ The backup **does not contain** the information to remove the other 834 rows by
any offline rule: not ghosts, not dealloc, not per-row log, not a page-LSN cutoff
(deleted pages are *below* the redo start). SQL Server reaches 6,000 only because
its live restore replays a log tail that (on the live instance) continues past
what this particular fuzzy `.bak` captured, plus the committed DELETE's full
effect. This fixture captured a **DELETE in flight**; the `.bak` is genuinely
missing the redo for 834 of the deletions.

## Mistakes

- Pursued "recovery reverts/deallocates the deleted pages" (run 5→6 hypothesis);
  the DMV shows the pages stay allocated — the rows leave via columnstore
  rowgroup/count semantics, not page deallocation.

## Fix applied

- None yet — this is now a **design decision** (see plan D2): the `.bak` lacks the
  data to reproduce 6,000 exactly, so the correctness-first choice is to keep a
  precise known-gap rather than emit a heuristic guess.

## Next step decided

Decision point for the user (run 7 depends on it):
1. **Keep as precise known-gap (D2 default).** Document that `dirtycoverage_cci_delete`
   captured an in-flight DELETE whose redo for 834 rows is absent from the `.bak`;
   mssqlbak's 6,834 is the faithful read of what the file contains.
2. **Regenerate the fixture** so the DELETE fully commits + checkpoints *before*
   backup end (so the `.bak` actually contains all 1,000 ghostings), then the
   existing committed-delete path already handles it — turning this into a real,
   reproducible test instead of a pathological in-flight capture.

→ [7](chronology-7.md)
