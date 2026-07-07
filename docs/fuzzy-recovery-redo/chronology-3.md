# Run 3 — Pivotal: log has no redo for the 834; premise invalidated

**Date**: 2026-06-27
**Back to index**: [chronology.md](chronology.md)

---

## Actions

- `_diag_fn_dump_dblog.py` — ran `sys.fn_dump_dblog` **directly against the .bak**
  (the authoritative route the repo used to confirm log offsets). Full log-tail
  Operation/Context inventory.
- `_diag_cci_delta_emit.py` — replicated `delta.py`'s rowset selection + ran
  `read_table_rows` (no log tail), tallying emitted rows by id-band.

## Results

**Authoritative log inventory (entire .bak log tail):**

| Operation | Context | n | len |
|---|---|---|---|
| LOP_DELETE_ROWS | LCX_MARK_AS_GHOST | 166 | 144 |
| LOP_COUNT_DELTA | LCX_CLUSTERED | 16 | 208 |
| LOP_SET_BITS | LCX_PFS | 1 | 56 |
| LOP_BEGIN_CKPT / XACT_CKPT / END_CKPT / COMMIT | — | 1/2/1/1 | — |

→ **No INSERT records, no page-deallocation, no lifecycle redo.** Only 166 ghost
deletes exist in the log.

**Delta read:** rowset `…054400` has `rcrows=2000`; `read_table_rows` emits all
**2000** = `{6001-7000: 1000 (survivors), 5001-6000: 1000 (DELETED)}`. The other
cmprlevel=0 rowset (`…988864`, rcrows=5000) is correctly skipped as a tombstone.
With the log tail, 166 of the 2000 are ghosted → 1834 → total 6834 (= 5000
compressed + 1834). The **834 surplus** = deleted rows the log does not cover.

## Mistakes

- **Run 1's claim "all 1000 deleted rows are live PRIMARY, recovery needs ARIES
  redo of page deallocation" was wrong.** There are no deallocation/insert log
  records at all. The project was scoped on that false premise.

## Fix applied

- None to product code. Re-planned `plan.md` (premise invalidated → targeted
  delta-store read-correctness problem, not a recovery engine).

## Next step decided

Run 4 = determine how the 834 non-logged deletions are identifiable **offline**:
(a) are they on-page ghosts on a page version `read_table_rows` doesn't read
(stale/duplicate fuzzy page copies)? (b) do the 16 `LOP_COUNT_DELTA` +
checkpoint pin the authoritative post-delete delta count (1000) and which rows?
Decide the correctness-preserving suppression signal (D2: keep gap rather than
guess which rows).

→ [4](chronology-4.md)
