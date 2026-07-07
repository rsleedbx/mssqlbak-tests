# Chronology — Fuzzy-Backup Recovery Redo

Append-only index. One row per run; detail lives in `chronology-N.md`.

| Run | Date | Title | Result |
|---|---|---|---|
| [1](chronology-1.md) | 2026-06-26 | Investigation that scoped the project (cci_delete is not a bitmap case) | ✓ mechanism characterised; project created |
| [2](chronology-2.md) | 2026-06-26 | Phase 0a/0b — log framing + rowset/ghost inventory | ⚠ leads found; blocked on record-length walker |
| [3](chronology-3.md) | 2026-06-27 | Pivotal — fn_dump_dblog: no redo for the 834; ARIES premise invalidated | ✓ bug re-scoped to delta read-correctness |
| [4](chronology-4.md) | 2026-06-27 | Deleted rows = genuine PRIMARY on allocated, newer-LSN pages | ✓ mechanism narrowed to page-LSN/recovery boundary |
| [5](chronology-5.md) | 2026-06-27 | Header LSNs: simple page-LSN boundary disproven | ⚠ needs live page-level ground truth |
| [6](chronology-6.md) | 2026-06-27 | Live page truth + delete-record pages: an in-flight DELETE | ⚠ superseded by Run 7 — conclusion was wrong |
| [7](chronology-7.md) | 2026-06-27 | The `.bak` *does* contain the deletion: trailing modified-page run dropped by MTF walk | ✓ TRUE root cause: `extract_mdf_files` ignores re-copied modified pages |
| [8](chronology-8.md) | 2026-06-27 | Fix implemented: MTF merges image segments (highest-LSN-wins) | ✓ matches SQL Server restore on all versions; no regressions |
| [9](chronology-9.md) | 2026-06-27 | Phase 2 follow-ups: compressed path verified (+lazy fix); `phase` + `score` CCI decode fixed (Python+Rust) | ✓ dirtycoverage_cci_delete fully clean on all versions; gap removed; no regressions |
| [10](chronology-10.md) | 2026-06-27 | committed_delete_v4 (SS2017): 3 phantom rows were a scanner bug, not missing log records — OPEN-block records starting at 0x30 (< 0x48) were skipped | ✓ all 1000 DELETEs present & well-formed; fixed OPEN-block prefix scan; gap removed; no regressions |
