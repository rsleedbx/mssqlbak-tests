# Run 2 — Phase 0a/0b: log framing + rowset/ghost inventory

**Date**: 2026-06-26
**Back to index**: [chronology.md](chronology.md)

Decisions D1–D4 accepted at defaults; started Phase 0.

---

## Actions

- Studied `logtail.py` framing: the scanner keys on `LCX=0x02` (byte `0x0e`) +
  `SUBTYPE` (`0x0f`) + discriminant (`0x16`) and **slides in 8-byte steps**,
  not a record-length walk. Allocation/lifecycle records use other LCX contexts
  and are not surfaced.
- `_diag_log_reclen.py` — tried to locate a record-length field by inter-record
  stride. Inconclusive: sliding hits land inside DELETE before-image payloads.
- `_diag_cci_delta_pages.py` — enumerated the two cmprlevel=0 rowsets of
  `dirty_cci` and classified each page with the **real** `fixedvar_emittable`.

## Results

| item | outcome |
|---|---|
| dirty_cci rowsets | cmprlevel=3 (compressed segs), =2 (bitmap, **no pages**), two =0 heaps |
| rowset `…988864` | pages 438–445, all live (band 1–5000) — small |
| rowset `…054400` | **mostly ghost records** (`live=0 ghost=161` per page); live rows only on pages 517–523, totalling **exactly 1000** (`127+161×5+68`) |
| record-length field | **not yet located** — blocks a clean non-DML record walk |

Interpretation (lead, not yet byte-proven): the deleted rows are tied up in a
tombstoned/superseded heap full of ghosts; SQL Server's recovery resolves this
via page/lifecycle redo. The **1000 live** cluster was reconfirmed by a corrected
probe (every page in `…054400` holds 161 `original_` rows; live only on pages
517–523 = `127 + 161×5 + 68 = 1000`). NOTE: the first probe's content-substring
counts were **bogus** (`page.data` returned the whole buffer) and were removed;
only the `fixedvar_emittable` live/ghost numbers are trusted.

## Mistakes

- `_diag_cci_delta_pages.py` content counts (`original_=13041`) are invalid —
  `page.data` is not the per-page slice. Only the `live`/`ghost` columns (from
  `page.record(slot)` + `fixedvar_emittable`) are reliable.
- Earlier offset-4 id decode produced garbage on non-data pages.

## Fix applied

- None to product code (Phase 0 is read-only RE). Probes left untracked.

## Next step decided

Run 3 = **build the record-length walker** (locate the log-record length field so
non-DML records can be walked exactly), then complete the 0a LOP inventory and
decode the deallocation/lifecycle record(s) on the ghost-heavy rowset.

→ [3](chronology-3.md)
