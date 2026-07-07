# SQL Server Columnstore: How Deleted Bitmaps Are Logged

The "deleted bitmap" is an abstract concept. Physically, SQL Server implements
it as a **hidden, internal B-tree rowset** attached to each columnstore
partition (the `COLUMN_STORE_DELETE_BITMAP` allocation unit). Because it is an
ordinary B-tree, every modification to it is logged exactly like a modification
to any other rowstore index — there is no special "bitmap" log record type.

This matters for backup tooling: a compressed columnstore segment is immutable,
so a row is never physically removed from it. A DELETE/UPDATE only *records the
position* of the dead row in the bitmap. Whether a reader sees that deletion
depends entirely on whether it consults the bitmap — and, for a fuzzy backup,
whether it also **replays the bitmap's log records**.

---

## 1. Log operations and contexts

Through `sys.fn_dblog` / `sys.fn_dump_dblog` you do not see a specialized
"bitmap log record." You see standard DML against an internal system object:

* **`LOP_INSERT_ROWS`** — deleting (or updating) a compressed row inserts a row
  into the hidden deleted-bitmap B-tree. (An UPDATE on a CCI is a delete of the
  old compressed row plus an insert of the new row into the delta store.)
* **`LCX_INDEX_LEAF` / `LCX_INDEX_INTERIOR`** — the log context columns show
  that a standard index-page modification is taking place, on the internal
  rowset's `allocation_unit_id`, not on the user table's.

So a columnstore DELETE produces **no** `LOP_DELETE_ROWS` against your visible
rowset. The deletion lives as an *insert* into a different, hidden object. A
log-tail reader that only looks for deletes against the user table will miss it.

---

## 2. What data is actually logged?

Instead of flipping a bit in a large array, SQL Server logs a short physical
tuple — the row added to the bitmap B-tree:

* **`RowGroupID`** — the physical ID of the compressed rowgroup that owns the
  deleted row.
* **`RowIndex`** — the 0-based ordinal of the row within that rowgroup
  (`0 … 1,048,575`).

The live/deleted counts surfaced by
`sys.dm_db_column_store_row_group_physical_stats` are derived from this
structure, but the DMV itself is an in-memory projection and is not part of the
backup. Only the B-tree pages and their log records are.

---

## 3. Nonclustered columnstore (NCCI) variant

For an NCCI, SQL Server can defer the merge using a **delete buffer**
(`COLUMN_STORE_DELETE_BUFFER`):

1. The transaction first logs the dead row's RID / clustered key into the delete
   buffer.
2. A background **tuple mover** (or an explicit `ALTER INDEX … REORGANIZE`)
   later drains the buffer into the primary deleted-bitmap B-tree in batches.

This means a freshly-deleted NCCI row may be recorded in the delete buffer
rather than the bitmap at backup time — a second internal structure a reader
must account for.

---

## 4. Why this matters for backup and restore

A full backup is two things: a **fuzzy (transaction-inconsistent) copy of the
data pages** plus the **slice of transaction log active during that copy**. The
backup engine guarantees the log slice spans from `MinLSN` (the earliest LSN any
recovery could need) through end-of-copy, so the backup always contains enough
log to reach a consistent state.

There are therefore two distinct ways a deletion reaches a restored database,
and the distinction is what determines whether an offline parser gets it right:

* **Persisted (hardened) bitmap pages** — if the delete was committed *and*
  checkpointed before the data copy reached those pages, the bitmap B-tree pages
  in the data copy already reflect it. A reader only needs to *read* the bitmap.
* **Logged-but-not-yet-hardened bitmap inserts** — if the delete happened during
  the backup window, the fuzzy data copy may not yet contain the bitmap update.
  The truth exists only as `LOP_INSERT_ROWS` records (Section 1) in the backup's
  log slice. A reader must *replay* them.

On `RESTORE`, SQL Server runs full crash recovery (analysis → **redo** →
**undo**) over the entire captured log, in LSN order, against **every**
structure — including this hidden B-tree — so both cases resolve correctly.

---

## 5. How this maps to `mssqlbak`

`mssqlbak` handles the **persisted** case: it reads the deleted-bitmap rowset
(a `cmprlevel=2` internal rowset) and suppresses the listed `(seg_id, row_pos)`
positions — see `read_columnstore_rows` in
`mssqlbak/columnstore/assembly/reader.py`.

For the **logged** case, `mssqlbak`'s log-tail replay only handles *rowstore*
DML against user-visible slots (`LOP_INSERT_ROWS` / `LOP_DELETE_ROWS` /
`LOP_MODIFY_ROW` with `LCX = LCX_XACT`). It does **not** replay log records that
target internal structures (the hidden delete-bitmap B-tree, allocation/PFS/GAM
pages, page (de)allocation, or delta-rowgroup lifecycle).

### Measured behaviour on `dirtycoverage_cci_delete`

DELETE of 1,000 rows, ids 5001–6000. Probed with the `tools/diag/_diag_cci_*`
scripts and corroborated against a live restore (DMV) of the same `.bak`:

| Measurement | Result |
|---|---|
| SQL Server `RESTORE` of the `.bak` (DMV) | **6,000 rows**; ids 5001–6000 all gone; `phase` = {compressed: 5000, delete: 1000 (ids 6001–7000)} |
| `mssqlbak` extraction (log tail applied) | 6,834 (834 deletes missed) |
| `mssqlbak` extraction (log tail neutralized) | 7,000 — all 1,000 deleted rows physically **live PRIMARY** on captured pages, zero on-page ghosts |
| `committed_delete_slots` derived | 166 |
| Per-row `LOP_DELETE_ROWS` in the **entire file** (brute-force scan) | **175** (pages 692/693/665/576) |
| Post-recovery rowgroup states (DMV) | rg0 = TOMBSTONE (5000), rg1 = COMPRESSED (5000, ids 1–5000), rg2 = OPEN delta (1000, ids 6001–7000) |

What this rules in/out, all **measured**:

* It is **not** a delete-bitmap case. The deleted rows are uncompressed
  delta-store rows (`phase='delete'`, `val='original_N'` stored as plaintext);
  the compressed rowgroup (ids 1–5000) is untouched. So Sections 1–2 describe a
  real mechanism, but it is *not* what this fixture exercises.
* It is **not** an on-page-ghost miss. With the log tail off, all 1,000 deleted
  rows decode as live PRIMARY records — their pages were captured before the
  delete committed.
* It is **not** a too-small log window. The whole `.bak` contains only ~175
  per-row delete records, all already inside `find_log_range`'s window.

The unresolved core: SQL Server removes 1,000 rows on restore, but the backup
contains only ~175 individual delete records. So ~825 deletions are applied by
**recovery actions other than per-row delete log records** — most plausibly
page-deallocation / allocation (PFS/GAM/IAM) redo and/or delta-rowgroup
lifecycle operations that SQL Server's full ARIES redo replays and `mssqlbak`
does not. Closing this gap is therefore not a single targeted decode; it is a
slice of general crash-recovery redo over the complete active log against
allocation and internal structures. The information is in the file — the gap is
the breadth of replay, exactly the trade-off noted at the top of this document.
