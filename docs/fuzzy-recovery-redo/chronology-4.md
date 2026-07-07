# Run 4 — Deleted rows are genuine PRIMARY on allocated, newer-LSN pages

**Date**: 2026-06-27
**Back to index**: [chronology.md](chronology.md)

---

## Actions

- `_diag_cci_delta_chain.py` — dumped the exact `_data_pages` leaf chain
  `read_table_rows` follows for the included delta rowset (`…054400`), per page:
  m_type, slot_cnt, live/ghost, page LSN.
- Inline probes: decoded live-row ids via `val='original_N'`; compared the
  `next_page` chain to the IAM-allocated page set; dumped record status bytes for
  a survivor page, a deleted page, and a ghost page.

## Results

- Leaf chain = **97 pages, 2000 live PRIMARY, 13490 ghosts.** `read_table_rows`
  correctly drops the ghosts and emits the 2000 live.
- The 2000 live split into **two clusters**:
  - **pages 517–523**, LSN block `0x2b`, ids **6001–7000** = survivors (keep).
  - **pages 685–693**, LSN block `0x2d` (newer), ids **5001–6000** = the DELETED
    rows, present as **live PRIMARY** (status `0x30`, rectype 0 — *not* ghosts).
- `next_page` chain page set == IAM-allocated page set (both 97 pages incl.
  685–693): the deleted-row pages are **correctly allocated**, not stale.
- Ghost page (536) status `0x3c`/rectype 6 → `fixedvar_emittable` correctly
  rejects it. So ghost classification is **not** the bug.

## Mistakes

- Initial id decode read a fixed int at record offset 4 and got 15000–15999 (the
  CCI delta store stores an internal column there); switched to the authoritative
  `val='original_N'` string to recover real ids.

## Fix applied

- None. Findings recorded; plan/tracker updated with the narrowed mechanism.

## Conclusion (mechanism narrowed)

The 834 surplus deleted rows are **genuine pre-delete PRIMARY images** on
allocated pages whose page LSN (`0x2d`) is **newer** than the survivors (`0x2b`).
They are not ghosts and not stale allocations, and the per-row delete log records
that would ghost them are **absent** from the backup (only 166 present). The only
remaining offline signal that separates the deleted cluster from the survivor
cluster is the **page LSN vs. the backup's recovery/redo boundary** (or a
fork/differential map) — i.e. these pages post-date the backup's consistency
point and SQL Server's restore recovery does not keep them.

## Next step decided

Run 5 = pin the recovery boundary: (a) read the backup header's
`FirstLSN`/`LastLSN`/`CheckpointLSN`/`DatabaseBackupLSN` (RESTORE HEADERONLY +
`fn_dump_dblog` LSNs of the 166 deletes + checkpoint), and (b) restore live and
query `sys.dm_db_database_page_allocations` to confirm whether pages 685–693 are
allocated to the delta post-restore. Decide whether a page-LSN > recovery-LSN
rule cleanly selects the survivor cluster (correctness-preserving), per D2.

→ [5](chronology-5.md)
