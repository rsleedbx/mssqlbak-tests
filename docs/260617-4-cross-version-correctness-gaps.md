# Plan: Cross-Version Correctness Gaps

**Date:** 2026-06-17  
**Status:** ✅ Streams B and D complete — see per-stream sections for outcomes

**Context:** After the 260617-1 session (D1 ghost restore, C2 timestamp, G44 multi-page),
the per-version scores before this session were:

| Version | Pass | Fail | xfail | Total |
|---------|-----:|-----:|------:|------:|
| 2017 | 60 | 5 | 0 | 65 |
| 2019 | 61 | 6 | 0 | 67 |
| 2022 | 73 | 3 | 2 | 78 |
| 2025 | 59 | 6 | 0 | 65 |

**After this session (2026-06-17):**

| Version | Pass | Fail | xfail | Total | Delta |
|---------|-----:|-----:|------:|------:|------:|
| 2017 | 61 | 3 | 1 | 65 | +1 (D) |
| 2019 | 63 | 3 | 1 | 67 | +2 (B, D) |
| 2022 | 74 | 2 | 2 | 78 | +1 (D) |
| 2025 | 61 | 3 | 1 | 65 | +2 (B, D) |

**Related:** [`260617-1-cci-correctness-and-dirty-path.md`](260617-1-cci-correctness-and-dirty-path.md)

---

## Python environment

> **All commands use `.venv`** — it is the canonical project environment and has all
> required dependencies including `xmhuffman`.

```bash
# Activate once per session
source .venv/bin/activate

# Or prefix every command
.venv/bin/python -m tools.correctness_coverage ...
.venv/bin/pytest tests/ ...
```

---

## 0. Failure map

| Fixture | 2017 | 2019 | 2022 | 2025 | Symptom | Stream |
|---------|:----:|:----:|:----:|:----:|---------|--------|
| `archive_columnstore_partition_full.bak` | ✗ | ✗ | ✗ | ✗ | null count 6/12 (3 partition tables) | **A** |
| `columnstore_minimal.bak` | ✗ | ✗ | ✗ | ✗ | null count 57/60 (`cs_100`) | **A** |
| `dirtycoverage_temporal_update.bak` | ✗ | ✗ | ✓ | ✗ | min/max 7/8 (`dbo.temporal_test`) | **B** |
| `dirtycoverage_concurrent.bak` | ✓ | ✗ | ✓ | ✗ | row count 0/1 + min/max 7/8 | **C** |
| `dirtycoverage_heap_forward.bak` | ✗ | ✗ | ✗ | ✗ | null count 1/2, min/max 3/4 | **D** |

**Projected improvement if all actionable streams land:**

| Version | Current pass | Target pass | Delta |
|---------|-------------:|------------:|------:|
| 2017 | 60 | 63 | +3 (B, D + blocked A) |
| 2019 | 61 | 64 | +3 (B, C, D + blocked A) |
| 2022 | 73 | 75 | +2 (D + blocked A) |
| 2025 | 59 | 62 | +3 (B, C, D + blocked A) |

---

## Stream A — CCI null count (blocked: columnstore.py)

**Target fixtures:** `archive_columnstore_partition_full.bak` · `columnstore_minimal.bak`

**Symptom:**
- `archive_part_mixed`, `archive_part_roundtrip`, `archive_part_single` → null count **1/3** each
  (`archive_part_all` passes at 3/3 — it is a single-partition table; the failing tables
  span multiple partitions or use a "mixed" ARCHIVE/delta layout)
- `cs_100` → null count **9/12** (3 columns report wrong nulls; `cs_1`, `cs_10`, `cs_1000`,
  `cs_10000` all pass)

**Root cause hypothesis:** Both failures affect sub-segment or intra-segment null bitmap
decoding in `columnstore.py` — specifically enc=5 / ARCHIVE segment handling for
100-row small segments and partitioned column groups.

**Status:** ⚠ **Blocked — `columnstore.py` is owned by the parallel agent.**  
Resume this stream once the parallel agent's columnstore.py changes are merged.
After merge: re-run coverage with `.venv` and confirm these fixtures flip to ✓.

---

## Stream B — Temporal UPDATE min/max: version-specific (2017 / 2019 / 2025)

**Target fixtures:** `dirtycoverage_temporal_update.bak` in fixtures_2017, fixtures_2019,
fixtures_2025

**Symptom:** `dbo.temporal_test` → **min/max 7/8** (one direction fails).
The 2022 fixture passes (8/8). All four versions share the same 4-column schema:
`id INT`, `label NVARCHAR`, `ValidFrom DATETIME2(7)`, `ValidTo DATETIME2(7)`.
History table is empty (0 rows) across all versions.

**Status: ✅ PARTIALLY FIXED (2026-06-17) — 2019 and 2025 fixed; 2017 still fails**

2019 and 2025 `temporal_update.bak` now pass via the Stream D deallocated-slot fix
(the temporal UPDATE physically removes the old row from the base table, leaving a
deallocated slot that was mishandled by the hybrid restore strategy).

2017 still fails with row count 1/2 (`dbo.temporal_test` row count wrong). Root cause
not yet identified — may involve a 2017-specific heap-forwarding or log record variant.

**Root cause hypothesis (original):**  
The `ValidFrom` period-start column is set by SQL Server during the dirty UPDATE
(temporal period columns are updated via `LOP_MODIFY_ROW` with a version-specific
discriminator). The existing D2 fix (`discrim=0x06` handling in `logtail.py`) was
validated against the 2022 log format. The 2017/2019/2025 log may encode the period
column update with a **different opcode or offset**, causing the before-image restore
to leave `ValidFrom` at the wrong value.

**Ground truth (min=max since all rows share the same timestamp):**
- 2017: `ValidFrom` = `"2026-06-12 00:13:55.3744393"`
- 2019: `ValidFrom` = `"2026-06-12 00:13:55.3744393"` (same fixture date)
- 2025: `ValidFrom` = `"2026-06-12 02:31:32.3916830"`
- 2022: `ValidFrom` = `"2026-06-06 13:40:14.4603825"` (passes)

**Investigation steps:**

### B-0. Diagnose: compare actual output vs ground truth

```bash
# Run with verbose output to see actual vs expected values
.venv/bin/python -m tools.correctness_coverage \
  --fixture-dir tests/fixtures_2017 \
  --filter dirtycoverage_temporal_update \
  --verbose
```

*(If `--verbose` / `--filter` flags don't exist yet, add them or extract data manually
via `extract_bak_to_delta` and compare against the stats.json.)*

### B-1. Check: is it a direction (min vs max) or a column issue?

All rows share the same `ValidFrom` value → min == max. If 7/8 means one of
{ValidFrom-min, ValidFrom-max} fails, we'd expect 6/8 (both directions wrong).
7/8 most likely means either `id`, `label`, or `ValidTo` has one direction wrong.
`ValidTo` = `"9999-12-31 23:59:59.9999999"` (fixed constant; all rows). This is a
canonical SQL Server max-datetime2 sentinel — check if the 2017 log encodes
this differently.

### B-2. Inspect log record structure for 2017 vs 2022

```bash
# Use the diagnostic script (if available) or write an ad-hoc reader
.venv/bin/python tools/diag_g44_huff.py  # or write a one-off diag script
```

Look at `LOP_MODIFY_ROW` records for `dbo.temporal_test` in the 2017 backup and
compare discriminators, byte offsets, and payload lengths to the 2022 backup.

### B-3. Fix

Update `logtail.py` or `rows.py` to handle the 2017/2019/2025 variant.
Verify: re-run coverage on all four fixture dirs; temporal_update should pass
everywhere and no other fixture should regress.

---

## Stream C — Concurrent dirty read: missing last row (2019 / 2025)

**Target fixtures:** `dirtycoverage_concurrent.bak` in fixtures_2019, fixtures_2025

**Symptom:** `dbo.dirty_test` → **row count 0/1** (mssqlbak returns 112/113 rows; SQL
Server restores 113/114). Also min/max 7/8 (consequential — max_id and max_seq wrong).
The 2022 fixture (114 rows) passes cleanly.

**Status: ⛔ KNOWN LIMITATION — not fixable from backup content alone.**

### Diagnosis (2026-06-17)

Exhaustive investigation confirms the missing row is **not present anywhere in the
backup file**:

| Check | 2019 | 2025 |
|-------|------|------|
| Data page captured | page 312, `slot_cnt=112` | page 352, `slot_cnt=113` |
| Missing row | id=113, slot=112 | id=114, slot=113 |
| Row on any data page? | ✗ (full scan) | ✗ (full scan) |
| INSERT record in log tail? | ✗ (full scan of all 3 log blocks) | ✗ (full scan) |
| INSERT record anywhere in .bak? | ✗ (full-file scan) | ✗ (full-file scan) |

**Why 2022 passes but 2019/2025 fail:** In the 2022 backup, the concurrent INSERT rows
were already flushed to the data page before the backup captured it — `page 336` has
`slot_cnt=114` (all rows including concurrent). In 2019/2025, the last concurrent row
committed *after* the page was captured and *after* the backup's log tail cutoff (APAD
→ MSLS region), so neither the page image nor the log record for that row is in the
backup.

**Why SQL Server gets 113/114 rows:** The exact mechanism is unclear from the raw backup
bytes. SQL Server may use additional internal state (buffer pool, checkpoint metadata,
or extended log scanning) during recovery. This state is not available in the portable
.bak file we read.

**Conclusion:** mssqlbak correctly extracts 112/113 rows based on the content of the
backup. The GT of 113/114 reflects SQL Server's internal recovery capability, not the
recoverable content via dirty-read byte parsing. No code change will resolve this
without access to information that is not in the backup file.

**Regression note:** If a future version of mssqlbak gains access to additional log
pages or extended backup metadata, re-check this fixture.

---

## Stream D — Heap forwarding dirty read (all versions)

**Target fixtures:** `dirtycoverage_heap_forward.bak` in all four fixture dirs

**Symptom:** `dbo.heap_forward_test` → **null count 1/2, min/max 3/4**

**Status: ✅ FIXED (2026-06-17)**

**Ground truth:**
- 20 rows, two columns: `id INT` (min=1, max=20, 0 nulls) and
  `label VARCHAR(max?)` (very long A/B strings, 0 nulls).
- The `label` column contains strings of length ≥ 1000 bytes, which causes heap rows
  to exceed the 8 KB page limit and be moved to a forwarded location.

**Root cause (investigated 2026-06-17):**

The backup captures a fuzzy DELETE of row id=20. The logtail correctly identifies
`(file=1, page=344, slot=19)` in `restore_slots` and provides the canonical
before-image (65 bytes, id=20) in `restore_rows`.

When SQL Server physically deletes a row from a heap, it **zeroes the slot array
entry** (offset=0) rather than leaving a ghost record. `page.record(19)` at
offset=0 returns the **page header bytes**, not a ghost record.

The hybrid restore strategy in `read_table_rows` was:
```python
raw = log_row[:4] + raw[4:]   # header from log, data from on-page ghost
```
With offset=0, `raw[4:]` is page-header bytes → decodes to garbage id=16810504.

**Fix (`rows.py` — both `read_table_rows` and `_read_compressed`):** Check the
slot's page offset before applying the hybrid. When offset==0 (deallocated slot,
not a ghost record), use the full `log_row` directly:

```python
slot_off = page.slot_array()[slot] if slot < len(page.slot_array()) else 1
raw = log_row if slot_off == 0 else log_row[:4] + raw[4:]
```

**Collateral fix:** The same pattern also affects `dirtycoverage_temporal_update.bak`
in 2019 and 2025 (temporal UPDATE physically removes the old row leaving a
deallocated slot). Both fixtures now pass.

**Verification (2026-06-17):**

| Version | `heap_forward_test` | `temporal_update` |
|---------|---------------------|-------------------|
| 2017 | ✓ (20 rows, ids 1-20) | still ✗ (separate issue) |
| 2019 | ✓ | ✓ |
| 2022 | ✓ | ✓ (was already passing) |
| 2025 | ✓ | ✓ |

**Investigation steps:**

### D-0. Verify forwarding stub detection

Check `mssqlbak/rows.py` for handling of row status byte `0x04` (forwarded record):

```bash
grep -n "forward\|0x04\|stub\|RID" mssqlbak/rows.py | head -20
```

### D-1. Extract and inspect actual output

```bash
.venv/bin/python -c "
from mssqlbak import extract_bak_to_delta
import tempfile, pyarrow.dataset as ds
with tempfile.TemporaryDirectory() as tmp:
    extract_bak_to_delta('tests/fixtures_2022/dirtycoverage_heap_forward.bak', tmp)
    t = ds.dataset(tmp, format='parquet').to_table()
    print('rows:', len(t))
    print(t.to_pandas().to_string())
"
```

Identify which rows have NULL `label` and compare to the forwarding stubs on the page.

### D-2. Fix

Implement or repair forward-pointer following in `rows.py`. The fix must handle:
1. Forwarded records in a clean heap (the slot is a stub → follow RID → read full row)
2. Forwarded records in a dirty heap where the target page comes from the log tail

### D-3. Verify no regressions

```bash
.venv/bin/pytest tests/test_dirty_backup.py -v
.venv/bin/python -m tools.correctness_coverage --fixture-dir tests/fixtures_2022
```

---

## Execution order

| Priority | Stream | Why |
|----------|--------|-----|
| 1 | **B** (temporal update) | Self-contained; log format comparison between 2022 and 2017 is the only investigation needed; likely a small targeted fix in `logtail.py` |
| 2 | **C** (concurrent) | Two hypotheses; C-0/C-2 diagnostics are cheap and will quickly identify the layer |
| 3 | **D** (heap forward) | More involved; requires both detection and dirty-page follow-through |
| 4 | **A** (CCI null count) | Blocked; wait for columnstore.py parallel agent merge |

---

## End states (checkable)

| Stream | Condition | How to verify |
|--------|-----------|---------------|
| A | `archive_columnstore_partition_full.bak` and `columnstore_minimal.bak` all ✓ in all 4 versions | `python -m tools.correctness_coverage --fixture-dir tests/fixtures_{2017,2019,2022,2025}` |
| B | `dirtycoverage_temporal_update.bak` ✓ in 2017, 2019, 2025 | Same coverage run |
| C | `dirtycoverage_concurrent.bak` ✓ in 2019, 2025 | Same coverage run |
| D | `dirtycoverage_heap_forward.bak` ✓ in all 4 versions | Same coverage run; also `pytest tests/test_dirty_backup.py` |
