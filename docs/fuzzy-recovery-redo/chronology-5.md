# Run 5 — Header LSNs: simple page-LSN boundary disproven (in progress)

**Date**: 2026-06-27
**Back to index**: [chronology.md](chronology.md)

---

## Actions

- Read `RESTORE HEADERONLY` LSN columns for `dirtycoverage_cci_delete.bak`.

## Results

Backup header LSNs (decoded seq:offset:slot):

| field | value |
|---|---|
| FirstLSN / CheckpointLSN | **45:3448:184** (redo start) |
| LastLSN | 45:3528:1 |
| DatabaseBackupLSN | 45:2720:184 |

Captured log window = `[45:3448 .. 45:3528]` — tiny (~80 log blocks); holds the
166 deletes + checkpoint.

Page LSNs:
- survivors (517–523) = seq **43** (e.g. 43:536).
- deleted (685–693) = seq **45**, offsets **2824–3064** — i.e. *before*
  CheckpointLSN (45:3448), and after DatabaseBackupLSN (45:2720).

→ A "page LSN > recovery LSN ⇒ drop" rule does **not** work: every chain page is
*below* CheckpointLSN, and the deleted cluster (45:2824) predates the captured
redo window. The 834 deletions are **not redoable** from the captured log, yet
SQL Server reaches 6,000. Offline LSN analysis alone does not explain it.

## Mistakes

- Hypothesised a clean page-LSN/recovery boundary in run 4's conclusion; the
  header LSNs disprove the simple form of it.

## Fix applied

- None. Recorded; the next probe must be live ground truth at the page level.

## Next step decided

Run 6 = **live-restore page-level ground truth.** Restore the `.bak` and query
`sys.dm_db_database_page_allocations` (+ `%%physloc%%` / DBCC IND) for `dirty_cci`
to learn, post-restore: (a) which page ids hold the surviving delta rows, (b)
whether pages 685–693 are still allocated, and (c) the page LSNs SQL Server ends
up with. That pins whether recovery *reverts/deallocates* the deleted-cluster
pages (and via what on-disk signal we can read offline), or whether the backup
encodes the deletion somewhere not yet parsed (e.g. the differential/ML map or a
per-page "needs-redo" marker).

→ [6](chronology-6.md)
