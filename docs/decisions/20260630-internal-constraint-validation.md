# ADR: Internal Constraint Validation

**Date:** 2026-06-30  
**Status:** Accepted

---

## Context

`mssqlbak` extracts SQL Server `.bak` files to Arrow / Parquet without access to a live SQL Server instance. The existing confidence system (`mssqlbak/confidence.py`) validated structural properties (file identity, backup-set count, catalog row counts, page-type distribution) but did not inspect the *values* produced by decoding against any constraint embedded in the backup itself.

Users asked: how do we know the decoded data is within the parameters the `.bak` declares — without any external ground truth?

---

## Decision

Add a **post-decode constraint validation pass** that runs checks derived entirely from metadata in the `.bak` itself:

| Check | Source in `.bak` | What it catches |
|-------|-----------------|-----------------|
| `type_range` | `syscolpars.xtype` + `max_length` | Integer overflow, string truncation |
| `null_contract` | `syscolpars.status` (NOT NULL bit) | Spurious NULLs from decode errors |
| `btree_key_order` | Clustered index key col + leaf-chain scan order | Page attribution bugs, byte-order errors |
| `cci_segment_contract` | `syscscolsegments` `n_rows`, `has_null`, `mn`, `cdi_max` | Row-count drift, null-inject, value-range overflow |

All checks are **post-decode** — they receive already-decoded Arrow columns and do not touch the hot extraction path. CCI segment checks are gated on `MSSQLBAK_CONSTRAINT_CHECKS=1` to avoid overhead in normal extraction.

---

## Implementation

- **`mssqlbak/confidence.py`** — three new functions: `_type_range_check`, `_null_contract_check`, `_btree_key_order_check`. `analyze_bak` collects decoded rows per rowstore table, builds Arrow arrays per column, and runs these checks. `ConfidenceReport` gains `to_markdown()` and `to_json()` methods.
- **`mssqlbak/constraint_check.py`** — new standalone module with `check_cci_segment()` and a thread-local accumulator (`record_segment_results` / `get_segment_constraint_results`).
- **`mssqlbak/columnstore/assembly/reader.py`** — after each row-group decode, when `MSSQLBAK_CONSTRAINT_CHECKS=1`, calls `check_cci_segment` for each segment and records results in the thread-local store.
- **`tools/confidence_report.py`** — `--report constraints` flag writes a markdown constraint report file (or prints to stdout).
- **`tools/correctness_coverage.py`** — no-verifier rows now show a one-line constraint summary.

---

## What this proves vs. what it cannot prove

### Proves
- All integer values are within the declared SQL type range (e.g. TINYINT ≤ 255).
- NOT NULL columns have no null values in the decoded output.
- For single-column clustered indexes, the key column is non-decreasing across rows (correct leaf-chain traversal).
- CCI segments have the declared row count, null policy, and (for enc=1/2 with known bounds) value range.

### Does not prove
- **Statblob histogram bounds** — the binary format of `statblob` is not yet reverse-engineered. Histogram bucket counts would give tighter numeric range bounds than type-level checks alone, but parsing statblobs is a significant effort for approximate bounds.
- **LOB chain integrity** — verifying forward/back pointers in BLOB page chains requires tracing per-LOB page allocations. This is a medium-effort Phase 6 candidate.
- **Page checksum / torn-page detection** — checksums are already validated at page-read time in `PageStore`; surfacing the per-page results in the constraint report is wiring only.
- **Cross-table referential integrity** — foreign-key checks require joining across tables; not yet implemented.

---

## Consequences

- `confidence_report --report constraints` now produces a richer markdown file enumerating every constraint observed and whether the decoded output satisfies it.
- `correctness_coverage` shows a one-line constraint summary for `.bak` files that have no verifier sidecars, giving signal even without a live SQL Server.
- The `MSSQLBAK_CONSTRAINT_CHECKS=1` gate keeps the default hot-path unchanged; enabling it adds a per-segment Arrow construction step.
- Tests in `tests/test_constraint_checks.py` cover all four check types with deliberately failing scenarios, acting as regression guards.
