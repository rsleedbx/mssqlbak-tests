# Plan: Checkpoint ATT + Page-Level XDE Slots for Pre-MinLSN Dirty-Row Suppression

**Date:** 2026-06-18  
**Status:** 🔄 Phase 0 complete — checkpoint ATT required; deferred pending format research

**Targets:**
- `dirtycoverage_large_dirty.bak` — currently xfail across all four SQL Server versions
- `dirtycoverage_concurrent.bak` — currently xfail (timing-dependent, harder)

---

## 1. Root-cause analysis

### What SQL Server knows that mssqlbak does not

SQL Server restores a fuzzy backup using a full REDO + UNDO engine:

1. **Active Transaction Table (ATT) in the checkpoint record.**
   The log tail contains a checkpoint record (`LOP_BEGIN_CKPT` / `LOP_END_CKPT`) that
   embeds every transaction ID that was uncommitted at backup time, including those whose
   `LOP_BEGIN_XACT` predates MinLSN and therefore does not appear anywhere in the captured
   VLF window.  SQL Server reads the ATT and rolls back all listed transactions during UNDO.

2. **Page-level XDE (Transaction Descriptor Entry) slots.**
   When a transaction inserts rows, SQL Server writes an XDE record into the page's slot
   array alongside the data rows.  The XDE record maps the transaction ID to the set of
   slot indices it owns on that page.  During restore, SQL Server reads XDE slots to
   identify exactly which rows belong to each uncommitted transaction — without needing the
   corresponding log records.

3. **Page header `xdes_id` field (offset 54, 6 bytes).**
   The page header stores the transaction ID of the most recent uncommitted writer to the
   page.  If non-zero, the page has at least one uncommitted row.  Cross-referencing
   `xdes_id` with the ATT identifies pages that require XDE-based suppression.

### Why the 8 large_dirty rows escape suppression

The `large_dirty` fixture inserts 5 000 dirty rows in a single transaction
(`8d0300000000`).  The transaction is correctly placed in the uncommitted set by
`build_uncommitted_set` (its `LOP_BEGIN_XACT` is in the captured log window).

`collect_dirty_slots` loops over `LOP_INSERT_ROWS` records whose `xact_id` is in the
uncommitted set.  For 5 000 − 8 = 4 992 rows, the INSERT records fall inside the captured
VLF window and are correctly added to `dirty_slots`.

For 8 rows, the INSERT records were written to an earlier VLF block before MinLSN.
`iter_log_records` never finds those records; `collect_dirty_slots` never adds those
`(file_id, page_id, slot_id)` triples.  The rows pass through the row reader as if they
were committed.

The page header on each of those 8 pages has `xdes_id = 8d0300000000`.  An XDE slot on
each page carries the same xact_id and the list of slot indices it owns.  Reading the XDE
slot would give us those missing triples.

### Why the concurrent case is harder

A concurrent INSERT that commits before MinLSN has neither a BEGIN nor a COMMIT in the
captured log window.  The page as read by the backup may have the row with "uncommitted"
status bits (if the backup read the page during the INSERT).  SQL Server's REDO pass
replays committed changes forward; without full REDO, mssqlbak cannot distinguish this
from a genuinely uncommitted row.  The concurrent fix requires the ATT (to know the
transaction committed before MinLSN, hence not in the ATT) and is treated as a
**deferred enhancement** in Phase 2.

---

## 2. Approach

### Phase 0 — Probe XDE slot format (experiment)

Write `tools/diag/diag_xde_slots.py` to:
- Iterate all data pages in `dirtycoverage_large_dirty.bak`
- For each page with `xdes_id != b'\x00'*6`, dump all slots with their raw bytes and
  status bytes
- Identify XDE records by their distinctive status byte (not `0x10` / Primary /
  Forwarded) and size
- Record: XDE status-byte value, byte layout, xact_id offset, owned-slot encoding

**End state:** XDE record format documented in this file with byte-level offsets confirmed
against at least two pages from the fixture.

### Phase 1 (deferred) — Parse XDE slots in `pages.py`

**Blocked by Phase 0 finding**: `xdes_id` is zero for all pages in the BAK.  XDE slots
are not persisted in the BAK page images.  This approach is not viable for on-disk BAK
files.

### Phase 2 (deferred) — Wire ATT into `LogTailResult`

Once the checkpoint record format is understood (Phase 4), the ATT can be added to the
uncommitted set and `dirty_row_bytes` can be extended to cover the 8 pre-MinLSN rows.

### Phase 3 (deferred) — Tests and coverage docs

Remains pending on Phases 1 and 2.

### Phase 4 (deferred) — ATT from checkpoint records

Parse `LOP_BEGIN_CKPT` / `LOP_END_CKPT` records to extract the Active Transaction Table.
This would:
- Catch pre-MinLSN uncommitted transactions that have zero log records in the captured
  window (not present in `large_dirty` but theoretically possible)
- Potentially improve the `concurrent` case (transaction in ATT → was still active →
  its rows from before MinLSN are genuinely uncommitted → suppress)

Deferred: requires reverse-engineering the checkpoint record payload format.

---

## 3. Skill / capability inventory

| Capability | Status |
|------------|--------|
| Page header parsing (`xdes_id` already parsed) | ✓ |
| Slot iteration on a page | ✓ (via `pages.py`) |
| XDE slot format | ✗ gap — Phase 0 experiment required |
| `build_uncommitted_set` | ✓ |
| `collect_dirty_slots` API | ✓ |
| Checkpoint record ATT parse | ✗ gap — Phase 4 |

---

## 4. Current score (2026-06-18)

| Version | Pass | xfail | Fail | Total |
|---------|-----:|------:|-----:|------:|
| 2017 | 67 | 1 | 0 | 68 |
| 2019 | 69 | 2 | 0 | 71 |
| 2022 | 80 | 3 | 0 | 83 |
| 2025 | 67 | 2 | 0 | 69 |

**Target after this plan (large_dirty fixed):**

| Version | Pass | xfail | Fail | Total | Delta |
|---------|-----:|------:|-----:|------:|------:|
| 2017 | 68 | 0 | 0 | 68 | +1 |
| 2019 | 70 | 1 | 0 | 71 | +1 |
| 2022 | 81 | 2 | 0 | 83 | +1 |
| 2025 | 68 | 1 | 0 | 69 | +1 |

---

## 5. Phase 0 findings

### XDE slots — not visible on disk in BAK

All 150 data pages in `dirtycoverage_large_dirty.bak` have `xdes_id = 0x000000000000`
(all six bytes zero).  The page-level xdes_id and XDE slot mechanism exists in SQL
Server's buffer pool (in memory) but is not persisted into the BAK page images.
**The xdes_id / XDE approach does not apply here.**

### Source of the 8 leaked rows

- `iter_log_records` (regular OPEN blocks): 339 records
- `_iter_cont_records` (CONT blocks): 4 715 records → brings `dirty_slots` to 4 989

Of the 5 000 dirty rows:
- 4 992 are correctly suppressed (4 989 via `dirty_slots` + some via `dirty_row_bytes`)
- 8 rows slip through: `(pid=344,s=199)`, `(385,79)`, `(389,78)`, `(393,93)`, `(395,101)`,
  `(397,108)`, `(399,116)`, `(401,123)`

Confirmed: none of those 8 (file_id, page_id, slot_id) triples appear in either regular
or CONT log records.  Their raw bytes are not in `dirty_row_bytes` either.  The page
header `xdes_id` is zero for all their pages.  On disk, those 8 rows are byte-for-byte
identical to committed rows.

### Root cause (confirmed)

The INSERT records for the 8 rows reside in a log block that predates the captured log
window.  The only way SQL Server can suppress them during restore is via the **Active
Transaction Table (ATT)** in the checkpoint record embedded in the log tail.  The ATT
contains the xact_id (`8d0300000000`) even though its BEGIN record is in an older VLF.

### Revised implementation path

| Phase | What | Feasibility |
|-------|------|-------------|
| P0 ✓ | Confirm XDE/xdes_id approach is viable | ✗ — not persisted in BAK |
| P1 | Find and parse `LOP_BEGIN_CKPT` in log tail to extract ATT | ⚠ requires reverse-engineering |
| P2 | Add ATT xact_ids to uncommitted set → dirty_row_bytes covers the leaked rows | ✓ (if ATT found) |
| P3 | Tests pass; update coverage docs | ✓ |
| Deferred | concurrent fix via ATT | May follow naturally |

**Key insight for P2:** if we expand the uncommitted set to include xact_ids from the ATT,
and also scan page data looking for row bytes from uncommitted transactions on those pages,
we can add those bytes to `dirty_row_bytes`.  Concretely: for every page whose `xdes_id`
turns out to be non-zero (in a future fixture where SQL Server preserves it), OR for every
page that contains slots from an ATT-listed transaction (identified via checkpoint parsing),
those row bytes can be added to the content-fingerprint set.

### Checkpoint record search (Phase 0 extension)

The diag script scanned for all LCX byte values, searched for ASCII 'CKPT' (not found),
and searched for raw occurrences of the 3 uncommitted xact_ids:

| xact_id | occurrences |
|---------|-------------|
| `8d0300000000` | 5 035 (all in INSERT/CONT record payloads) |
| `400300000000` | 84 |
| `780100000100` | 90 |

No checkpoint record was identifiable in the log tail using either the raw LCX histogram
(mostly noise from non-record-start positions) or the xact_id payload search.

### Conclusion: checkpoint ATT parsing is required but non-trivial

SQL Server embeds the Active Transaction Table in a checkpoint log record whose format
requires reverse-engineering.  `iter_log_records` only recognises LCX=0x02 records; the
checkpoint operation uses a different LCX value not yet determined.  This remains a
**deferred Phase 4** enhancement.

The `large_dirty` and `concurrent` xfails cannot be resolved without either:
(a) Parsing the checkpoint ATT, or  
(b) Running `sys.fn_dump_dblog` on a live SQL Server to map the checkpoint record format.

Current status: xfails remain; plan and diag infrastructure committed for future research.
