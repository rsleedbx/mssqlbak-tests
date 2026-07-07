# Run 1 — Investigation that scoped the project

**Date**: 2026-06-26
**Back to index**: [chronology.md](chronology.md)

---

## Actions

Investigated why `mssqlbak` cannot recover `dirtycoverage_cci_delete` to the same
row set SQL Server produces on `RESTORE`. Started from the hypothesis (carried in
`known_gaps.py` and an earlier doc) that this was a **columnstore delete-bitmap**
gap and that replaying logged bitmap-B-tree inserts would fix it.

Diagnostics written (untracked, `tools/diag/`):
- `_diag_cci_bitmap_scan.py` — locate the cmprlevel=2 delete-bitmap rowset + pages.
- `_diag_cci_log_payloads.py` — dump INSERT/DELETE log payloads by target page.
- `_diag_cci_count_payloads.py` — count value-string occurrences in the whole file.
- `_diag_cci_wholefile_scan.py` — brute-force whole-file DML record scan.
- `_diag_cci_dmv_truth.py` — restore to the live 2022 container + DMV queries.

## Results

| item | outcome | artifact |
|---|---|---|
| Persisted delete-bitmap rowset | exists (cmprlevel=2) but **no allocated pages** in image | `_diag_cci_bitmap_scan` |
| Log INSERT/DELETE payloads | all are FixedVar **data rows** (delta-store), LCX=0x02 only | `_diag_cci_log_payloads` |
| Per-row delete records in entire file | **~175** for 1,000 deletions | `_diag_cci_wholefile_scan` |
| SQL Server restore | **6,000 rows**, ids 5001–6000 gone | `_diag_cci_dmv_truth` (DMV) |
| Post-recovery rowgroups | rg0 TOMBSTONE(5000), rg1 COMPRESSED(5000), rg2 OPEN delta(1000) | DMV |
| mssqlbak raw vs log-tail | 7,000 (all live PRIMARY) vs 6,834 | extraction |

**Conclusion:** this fixture is **not** a delete-bitmap case — it is rowstore
delta-store deletes amid heavy rowgroup lifecycle churn. ~825 of the 1,000
deletions are removed by SQL Server recovery via **page-deallocation / tombstone
lifecycle**, which is *not* logged as per-row delete records. Recovering it
exactly requires a slice of **general ARIES redo** over the active log, not a
targeted decode. Bitmap replay and count-only heuristics were both ruled out.

## Mistakes

- Initial framing (and an earlier doc rewrite) wrongly attributed the gap to
  delete-bitmap parsing. Corrected after DMV ground truth showed the deleted rows
  are uncompressed delta-store rows and the compressed rowgroup is untouched.

## Fix applied

- Rewrote `docs/# SQL Server Columnstore: How Deleted Bi.md` §5 to the measured
  reality (DMV truth, whole-file scan, rowgroup states).
- Rewrote the `dirtycoverage_cci_delete` reason in `tools/known_gaps.py` to the
  accurate cause (recovery-redo / lifecycle, not bitmap).
- Created this project (`docs/fuzzy-recovery-redo/`).

## Next step decided

Get user decisions D1–D4 (plan.md), then execute **Phase 0a** — full `LOP_*`
inventory of `dirtycoverage_cci_delete` to locate the deallocation/lifecycle
records.

→ [2](chronology-2.md)
