# Fuzzy backup — trailing modified-page run — Implementation Plan

> **Premise revised twice. Final root cause (run 7).** Restoring
> `dirtycoverage_cci_delete.bak` to a fresh DB yields **6,000**, and `RESTORE`
> reads *only* the file — so the deletion **is** in the `.bak`. It lives in a
> **trailing run of re-copied modified pages** that an online/fuzzy backup
> appends after the main data-file scan (the post-modification image of every
> page changed mid-scan). mssqlbak's `mtf.py::_walk_image_pages` never reaches
> that run (unaligned, far past the main stream), so `extract_mdf_files` keeps
> the stale pre-delete copy of pages 685–693 → 6,834.
>
> Earlier premises are retracted: run 1 "ARIES page-dealloc redo" and run 6
> "in-flight DELETE; `.bak` lacks the redo" were both wrong.

**Status:** Phase 0 done (root cause proven). Phase 1 ready to implement.
**Chronology:** see `chronology.md` (run 7 has the proof).

---

## Goal

`extract_bak_to_delta(dirtycoverage_cci_delete.bak)` returns **6,000 rows** with
**zero** ids in 5001–6000 (today: 6,834), matching the SQL Server restore, by
making MTF page assembly ingest the trailing modified-page run. No regressions
in other fixtures; other `dirtycoverage_*` cases re-checked.

## What we now know (run 7, authoritative)

- The `.bak` contains each page modified during the backup **twice**: an
  8K-aligned main-stream copy (pre-modification) and an unaligned trailing copy
  (post-modification, higher page-header LSN). Untouched pages appear once.
- Trailing run = 56 unaligned 8 KB SQL page headers (offsets 5853184…6418432):
  PFS (8), system pages (11,14,16,17,20), and the ghosted delete cluster
  685–693 (ghost_cnt full, LSN 45:3208–3448).
- SQL Server RESTORE overlays this run → pages 685–693 become all-ghost →
  6,000 rows. mssqlbak drops it → keeps PRIMARY copies → 6,834.

## Tech stack

Python (`mssqlbak/mtf.py`, `mssqlbak/compressed.py`, `mssqlbak/pages.py`),
pytest, forgedb SQL Server containers, `tools/register_bak` for restore +
`dm_db_page_info` ground truth.

## Design decisions

- **Highest-LSN-wins** when placing pages into the dense image (page-header LSN
  at offset 40). Equivalent to last-copy-wins for this fixture, but the
  LSN rule is principled and robust to copy ordering.
- **D2 — correctness-first** (accepted): the overlay is driven by the file's own
  page images, not a count guess.
- **D4 — prove on 2022, fast-follow** other versions and the compressed path.

---

## Phases

### Phase 0 — Pin the root cause *(done, run 7)*

Proven: trailing modified-page run exists in the `.bak`, carries the ghosted
post-delete images, and is dropped by `_walk_image_pages`. ✓

### Phase 1 — Ingest the trailing modified-page run (TDD)

- **Failing test:** `extract` of `dirtycoverage_cci_delete` yields 6,000 rows,
  0 ids in 5001–6000 (assert against the DMV restore).
- **Fix (`mtf.py`):** after the main `_walk_image_pages`, continue discovering
  unaligned trailing SQL page headers to EOF and ingest them into
  `pages_by_file` with **highest-LSN-wins**. Apply the same overlay to the
  compressed (`MSSQLBAK`) path if it carries the analogous region.
- **Guardrails:** only accept well-formed SQL page headers (header_version 1,
  m_type 1/2, self-locator at +32, sane slot_cnt); never let a phantom locator
  spawn a file or shrink/replace a valid page with a lower-LSN one.
- Test passes.

**End state:** `extract_bak_to_delta(dirtycoverage_cci_delete)` → **6,000 rows,
0 ids in 5001–6000**, equal to the DMV restore.

### Phase 2 — Corroborate + close

**End state:**
- Holds on 2017/2019/2022/2025 (`tools.fixture_run all-versions`).
- Other `dirtycoverage_*` re-checked; pass or keep a precise gap.
- Full coverage + `test_stats` + `test_value_correctness` green; no regressions
  in rowstore/columnstore/archive suites; `ruff` + `pyright` clean.
- `tools/known_gaps.py` corrected (remove the wrong "lacks redo" gap) and
  `docs/BAK_FORMAT_SPEC.md` documents the trailing modified-page run with
  `Evidence:` lines (fixtures + versions).

---

## What I cannot do without your input

| Item | Why |
|---|---|
| Confirm autonomy through Phase 1 | The fix touches the shared MTF assembly path that every backup goes through; a regression there affects all fixtures, so a checkpoint around the code change is prudent. |
