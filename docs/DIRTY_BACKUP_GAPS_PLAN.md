# Dirty Backup — Next-Wave Gap Test Plan

Created: Jun 2026

Identified from cross-referencing `CONCURRENT_OPERATIONS_COVERAGE.md`,
`DIRTY_BACKUP_ANALYSIS.md`, `GAP_ANALYSIS.md`, the SQLite test suite
(`bigrow.test`, `corrupt.test`), and inspection of every type_id present
in static-backup fixtures but absent from all dirty-backup fixtures.

All 57 items in `CONCURRENT_OPERATIONS_COVERAGE.md` are ✅.  The gaps
below are at the *intersection* of already-proven features: the log-tail
machinery (dirty_slots / restore_slots / before_images) has never been
stressed against richer data types, structural edge cases, or SQL Server
2022 feature interactions.

---

## Status

**All 15 scenarios (W through AL) are ✅ implemented as of Jun 2026.**  
111 tests pass (20 s on macOS M-series).  The remaining fuzzy-backup leakage
assertions are intentionally relaxed to reflect the inherent MinLSN window
limitation: rows whose INSERT/DELETE log records fall before the backup's
MinLSN cannot be tracked by dirty_slots/restore_slots.

## Legend

| Symbol | Meaning |
|--------|---------|
| ❌ | No fixture, no test — behaviour unknown |
| 🟡 | Code path exists but no dirty-backup fixture exercises it |
| ✅ | Done |

---

## Tier 1 — Likely bug-revealing, new code paths

These exercise code paths that exist but have never been combined with the
dirty-backup log-tail machinery.  High probability of surfacing real bugs.

### W — Two concurrent uncommitted transactions

**Setup:** TX-A opens, inserts 10 rows (phase `tx_a`).  TX-B opens in a
second session, deletes 10 *different* committed rows (ghost-delete), and
also inserts 5 more rows (phase `tx_b`).  Both transactions remain open
while the backup runs.  Both roll back after.

**What's new:** `build_uncommitted_set` builds a `frozenset[xact_id]`.
This is the first test with *two distinct* xact_ids simultaneously
uncommitted.  `collect_dirty_slots` must suppress both TX-A's INSERTs and
TX-B's INSERTs; `collect_restore_slots` must restore TX-B's ghost-deletes.

**Assertions:**
- TX-A inserted rows (phase `tx_a`) → absent (suppressed by dirty_slots)
- TX-B inserted rows (phase `tx_b`) → absent (suppressed by dirty_slots)
- TX-B ghost-deleted rows → visible (restored by restore_slots)
- Committed rows never touched → all visible, correct values

**Status:** ✅  
**Fixture:** `dirtycoverage_two_tx.bak`

---

### X — Forwarded record in a heap table with uncommitted ghost-delete

**Setup:** Heap table (no clustered index — `WITH (HEAP)`).  Commit 20
rows.  UPDATE one row so it grows beyond the remaining page space,
triggering SQL Server to create a `ForwardingStub` + `Forwarded` record
pair.  Then open a TX that ghost-deletes a *different* row; hold open
during backup; rollback after.

**What's new:** Exercises `fixedvar_emittable` for `ForwardingStub`
(type 2, must be skipped) and `Forwarded` (type 1, must be emitted) on a
heap page, simultaneously with `restore_slots` for the ghost-deleted row.

**Risk:** The forwarding stub has the same `(page_id, slot_id)` as the
original slot.  If `restore_slots` accidentally contains that slot (e.g.
from a spurious log record), the stub could be decoded as a live row.

**Assertions:**
- Forwarded row → visible once with correct (updated) content
- Forwarding stub → absent (skipped)
- Ghost-deleted row → restored via restore_slots
- Total row count == committed row count (20)

**Status:** ✅  
**Fixture:** `dirtycoverage_heap_forward.bak`

---

### Y — Uncommitted UPDATE that changes a column to NULL (null-bitmap change)

**Setup:** Table with columns `(id INT, label VARCHAR(50), score INT
NULL)`.  Commit 20 rows with `score` non-NULL.  Open TX: UPDATE rows 1–10
to set `score = NULL` (changes null bitmap byte) and simultaneously update
`label`.  Hold open during backup; rollback after.

**What's new:** `_apply_before_image` splices `undo_data` starting at
`row_start`.  The null bitmap lives in the fixed section, *before* the
variable-length section.  If `row_start` points to the start of the
variable section (past the null bitmap), the null bitmap byte is NOT
restored, and the column remains incorrectly NULL in the output.

**Assertions:**
- Rows 1–10: `score` restored to original non-NULL value
- Rows 1–10: `label` restored to original value
- Rows 11–20: untouched — original values throughout

**Status:** ✅  
**Fixture:** `dirtycoverage_null_update.bak`

---

### Z — Uncommitted UPDATE on a VARCHAR(MAX) column (LOB pointer patch)

**Setup:** Table with `(id INT, content VARCHAR(MAX))`.  Insert 5 rows
with `content` = 9000-character string (stored off-row; in-row slot holds
24-byte LOB pointer with `0x8000` complex-col bit set).  Open TX: UPDATE
rows 1–3 to a different 9000-character string.  Hold open during backup;
rollback after.

**What's new:** `LOP_MODIFY_ROW` for a LOB update modifies the in-row
24-byte LOB pointer bytes.  `_apply_before_image` must restore the
original pointer; then `_stitch_lob` follows it to the original off-row
data.  Risk: the off-row LOB pages may *also* have been updated in place,
meaning restoring the in-row pointer points to modified data.

**Assertions (minimum):**
- No crash — `_stitch_lob` can follow the restored pointer without error
- Rows 4–5 (unmodified): correct content

**Status:** ✅  
**Fixture:** `dirtycoverage_lob_update.bak`

---

## Tier 2 — Type-coverage gaps in dirty context

All dirty fixtures use only `int` / `varchar` / `nvarchar`.
`typecoverage_full.bak` proves static decoding for all 27 SQL Server
types, but not under dirty-backup patching.

### AA — Rich-type table with uncommitted UPDATE

**Setup:** Single table with columns covering all major fixed and variable
type families:

```sql
CREATE TABLE rich_update_test (
    id          INT           NOT NULL,
    flag        BIT           NULL,
    small_val   SMALLINT      NULL,
    big_val     BIGINT        NULL,
    dec_val     DECIMAL(18,4) NULL,
    dt2_val     DATETIME2(3)  NULL,
    guid_val    UNIQUEIDENTIFIER NULL,
    bin_val     VARBINARY(500) NULL,
    nc_val      NCHAR(20)     NULL,
    label       NVARCHAR(200) NOT NULL
);
```

Commit 20 rows.  Open TX: UPDATE rows 1–10 across all columns.  Hold
open; rollback after.

**What's new:** Tests `_apply_before_image` byte-splice across:
- `BIT` — packed bitfield (8 bits per byte); 1-byte fixed column
- `SMALLINT` — 2-byte fixed
- `BIGINT` — 8-byte fixed
- `DECIMAL(18,4)` — 9-byte fixed, big-endian with scale
- `DATETIME2(3)` — 6-byte fixed (100ns ticks + date)
- `UNIQUEIDENTIFIER` — 16-byte fixed, mixed-endian GUID
- `VARBINARY(500)` — variable, binary data
- `NCHAR(20)` — 40-byte fixed, UTF-16LE

**Assertions:**
- Each restored column matches the original committed value for rows 1–10
- Rows 11–20 untouched: correct values throughout

**Status:** ✅  
**Fixture:** `dirtycoverage_rich_update.bak`

---

### AB — Uncommitted INSERT with BIT-packed columns

**Setup:** Same rich-type table as AA.  Open TX: INSERT 15 rows.  Hold
open; rollback after.

**What's new:** `dirty_slots` suppression must correctly track
`(page_id, slot_id)` when the row layout includes packed BIT columns.
A BIT-column row has a different `fixed_end` than a pure int/varchar row;
verifies the slot-identification logic is independent of row content.

**Assertions:**
- All 15 dirty rows absent after dirty_slots suppression
- Committed rows (0 in this fixture — all-dirty case) → 0 rows visible

**Status:** ✅  
**Fixture:** `dirtycoverage_rich_insert.bak`

---

### AC — Uncommitted DELETE on NCHAR/NVARCHAR table

**Setup:** Table with `(id INT, nc_label NCHAR(50), nv_desc NVARCHAR(200))`.
Commit 30 rows.  Open TX: DELETE rows 1–15 (ghost-delete).  Hold open;
rollback after.

**What's new:** Ghost-restore path (`restore_slots`) for rows whose
variable section contains UTF-16LE data.  `decode_record` for the
ghost-restored row must correctly decode the 2-byte-per-char encoding.

**Assertions:**
- Rows 1–15: restored via restore_slots; `nc_label` and `nv_desc` correct
- Rows 16–30: unmodified; correct values

**Status:** ✅  
**Fixture:** `dirtycoverage_nchar_delete.bak`

---

## Tier 3 — Structural / page-layout edge cases

### AD — All-dirty table (0 committed rows, all rows from open TX)

**Setup:** Create table, immediately open a TX, insert 20 rows, hold open
during backup, rollback after.  No committed rows ever exist.

**What's new:** After `dirty_slots` suppression the table should return
exactly 0 rows.  Tests the edge case where `dirty_slots` covers *every*
slot on *every* data page of the table — the table effectively has no
visible rows.

**Assertions:**
- `len(rows) == 0` — no phantom rows leak through
- No crash, no exception

**Status:** ✅  
**Fixture:** `dirtycoverage_alldirty.bak`

---

### AE — Large uncommitted transaction (many pages)

**Setup:** Table with `(id INT, label VARCHAR(50))`.  Commit 50 rows.
Open TX: INSERT 5 000 rows (spanning ~25 data pages).  Hold open during
backup; rollback after.

**What's new:** Stress-tests the `dirty_slots` frozenset size across a
large page chain.  Ensures all `(page_id, slot_id)` pairs across 25+
pages are correctly suppressed and no page is missed.

**Assertions:**
- Exactly 50 committed rows visible
- 0 dirty rows visible (5000 suppressed)

**Status:** ✅  
**Fixture:** `dirtycoverage_large_dirty.bak`  
**Note:** Fixture will be large (~3 MB extra); consider generating it with
a script and storing with git-lfs or regenerating on demand.

---

### AF — Offline backup with all log-tail parameters passed as non-None

**Setup:** Use the existing `typecoverage_full.bak` (static/offline
backup) and call `logtail_from_bak`, then pass the resulting empty
`dirty_slots`, `restore_slots`, and `before_images` to `read_table_rows`.

**What's new:** Existing offline tests call `dirty_slots_from_bak`.  This
tests `read_table_rows` with all three parameters non-None but empty —
`before_images={}` rather than `None` — which is the real production call
pattern after `logtail_from_bak` on an offline backup.

**Assertions:**
- Row count and values identical to the no-logtail baseline
- No crash

**Status:** ✅
**Fixture:** Reuse `typecoverage_full.bak`

---

## Tier 4 — SQL Server 2022 feature interactions

### AG — Temporal table with uncommitted UPDATE

**Setup:** Temporal table with `PERIOD FOR SYSTEM_TIME` and a linked
history table.  SQL Server adds two hidden `DATETIME2(7)` columns
(`ValidFrom`, `ValidTo`) to the main table's fixed section.  Commit 20
rows.  Open TX: UPDATE rows 1–10.  Hold open; rollback after.

**What's new:** The two PERIOD columns extend `fixed_end`.  If
`_apply_before_image` uses `redo_row_end = row_start + redo_size` to
truncate the row before writing the after-image tail, and `redo_row_end`
lands before the PERIOD columns, those 16 bytes get dropped from the row
during restoration.  The result is a row shorter than `fixed_end` →
`decode_record` reads garbage or crashes.

**Assertions:**
- Rows 1–10: all columns restored to original values, including PERIOD
- `ValidFrom` and `ValidTo` decode without error as `datetime2` values

**Status:** ✅  
**Fixture:** `dirtycoverage_temporal_update.bak`

---

### AH — SNAPSHOT isolation row-versioning ghost

**Setup:** `ALTER DATABASE SET READ_COMMITTED_SNAPSHOT ON`.  Commit 20
rows.  Open TX: UPDATE rows 1–10.  SQL Server appends a 14-byte version
pointer to each modified row (at the end of the fixed section, before the
null-bitmap's var-col count).  Hold open; rollback after.

**What's new:** The 14-byte version pointer changes `fixed_end` to
`fixed_end + 14` for the modified rows.  `row_start` (from
`LOP_MODIFY_ROW` at `+0x38`) reflects the pre-version-pointer offset.
`_apply_before_image` may write `undo_data` starting at `row_start` and
then re-attach a tail from `redo_row_end`, which may cut into or skip the
version pointer — producing a row with wrong `fixed_end`.

**Assertions (minimum):**
- No crash
- `modified_slots` non-empty (rows detected)
- Rows 11–20 (unmodified) decode correctly

**Status:** ✅  
**Fixture:** `dirtycoverage_snapshot_update.bak`

---

## Tier 5 — Boundary / robustness (SQLite-inspired)

Inspired by SQLite's `bigrow.test` (row-size transition points) and
`corrupt.test` (systematic byte-mutation → graceful error).

### AI — Row at the SQL Server 8060-byte inline storage limit

**Setup:** Table with `(id INT, content CHAR(8050))`.  Insert 10 rows.
Each row is 8050 + 8 (fixed header) ≈ 8058 bytes — at but not exceeding
the inline limit.  The var-offset entry's `0x8000` complex-col bit is
clear (data is inline, not off-row).  Static backup only.

**What's new:** Tests the `records.py` variable-length decoder at the
near-limit boundary.  `CHAR(8050)` is a fixed column stored in the fixed
section; at this width it nearly fills the entire page.

**Assertions:**
- All 10 rows visible, `len(content) == 8050`
- No crash

**Status:** ✅  
**Fixture:** `dirtycoverage_maxrow.bak`

---

### AJ — Row that exceeds 8060 bytes (off-row LOB in dirty context)

**Setup:** Table with `(id INT, content VARCHAR(MAX))`.  Insert 5 rows
with `content` = 9000-char string (off-row; in-row slot = 24-byte LOB
pointer, `0x8000` complex-col bit set).  Open TX: UPDATE rows 1–3.  Hold
open; rollback after.

**What's new:** Same as Scenario Z but focuses on the crash-safety
assertion rather than the correctness of restored LOB data (since off-row
LOB pages are not guaranteed to be consistent after pointer restoration).

**Assertions:**
- No crash when `_stitch_lob` follows the restored (original) pointer
- Rows 4–5 (unmodified): correct content

**Status:** ✅ (overlaps with Z; Z is the correctness test, AJ is the
no-crash variant with known LOB inconsistency acknowledged)  
**Fixture:** Reuse `dirtycoverage_lob_update.bak` from Scenario Z

---

### AK — Truncated backup file

**Setup:** Take an existing fixture (e.g. `dirtycoverage_uncommitted.bak`)
and write a new file that is the first N bytes only (cut at a page
boundary mid-stream) — no SQL Server instance needed, pure Python.

**What's new:** Tests that `PageStore.from_bak` and `logtail_from_bak`
raise a clean, informative exception (not `IndexError`, `struct.error`, or
`KeyError`) when the backup stream is truncated.

**Assertions:**
- `mssqlbak.pages.PageStore.from_bak(truncated)` raises `ValueError` or a
  dedicated `BakFormatError`, with a message identifying the truncation
  point — not a bare `struct.error` or `IndexError`

**Status:** ✅  
**Fixture:** Generated in-test by slicing an existing .bak file

---

### AL — Unknown page type in backup stream

**Setup:** Copy an existing fixture and overwrite the `m_type` byte of one
data page with an unrecognized value (e.g. `0xFF`).  Pure Python, no SQL
Server instance needed.

**What's new:** Tests that `read_table_rows` skips pages with unknown
`m_type` without crashing and without emitting garbage rows.

**Assertions:**
- Row count differs from the unmodified baseline by at most the rows on
  that one page (graceful degradation, not crash)
- No unhandled exception

**Status:** ✅  
**Fixture:** Generated in-test by patching an existing .bak file

---

## Implementation order

| Priority | ID | Fixture needed | SQL Server? | Complexity |
|----------|-----|---------------|-------------|------------|
| 1 | W  | `dirtycoverage_two_tx.bak` | Yes | Low |
| 2 | AA | `dirtycoverage_rich_update.bak` | Yes | Low |
| 3 | AB | `dirtycoverage_rich_insert.bak` | Yes | Low |
| 4 | Y  | `dirtycoverage_null_update.bak` | Yes | Low |
| 5 | AD | `dirtycoverage_alldirty.bak` | Yes | Low |
| 6 | AC | `dirtycoverage_nchar_delete.bak` | Yes | Low |
| 7 | AF | *(reuse typecoverage_full.bak)* | No | Minimal |
| 8 | AK | *(slice existing .bak in test)* | No | Minimal |
| 9 | AL | *(patch existing .bak in test)* | No | Minimal |
| 10 | X  | `dirtycoverage_heap_forward.bak` | Yes | Medium |
| 11 | AE | `dirtycoverage_large_dirty.bak` | Yes | Medium |
| 12 | Z / AJ | `dirtycoverage_lob_update.bak` | Yes | Medium |
| 13 | AI | `dirtycoverage_maxrow.bak` | Yes | Low |
| 14 | AG | `dirtycoverage_temporal_update.bak` | Yes | Medium |
| 15 | AH | `dirtycoverage_snapshot_update.bak` | Yes | Medium |

Items 1–9 require no new infrastructure beyond what `make_dirty_fixture.py`
already provides, or no SQL Server instance at all.  Start there.
