# Internal Constraint Validation Plan

> **For agentic workers:** Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After extraction, validate decoded output against every constraint the `.bak` itself carries — with no external ground truth. Produce a per-`.bak` constraint report (markdown + JSON) listing observed constraints and whether decoded output satisfies them.

**Architecture:** A post-decode validation pass over already-extracted Arrow tables + catalog metadata already in memory. No changes to the hot extraction path.

**Context:** The existing `mssqlbak/confidence.py` already checks file identity, backup-set count, catalog row counts, and page structure. This plan extends it with value-level constraints derived entirely from internal `.bak` metadata.

---

## Background: What internal metadata the `.bak` carries

| Source | Fields available | What it proves |
|--------|-----------------|----------------|
| `syscolpars` (catalog) | `type_id`, `max_length`, `is_nullable` | Hard type bounds; null contract |
| `syscscolsegments` (CCI) | `mn` (min_data_id), `cdi_max`, `has_null`, `n_rows` | Segment value range; null presence; row count per segment |
| `sysidxstats` + clustered index key | key column + leaf chain order | B-tree ordering invariant |
| Page header | `obj_id`, `page_id`, `file_id`, page type | Already checked by `_page_structure_check` |

---

## Files

- Modify: `mssqlbak/confidence.py` — add Phase 1, 2 checks; extend `analyze_bak`
- Create: `mssqlbak/constraint_check.py` — Phase 3 CCI segment checks (standalone module)
- Modify: `mssqlbak/columnstore/assembly/reader.py` — call constraint checks after each segment decode (env-gated)
- Modify: `tools/confidence_report.py` — add `--report constraints` flag and markdown output
- Modify: `tools/correctness_coverage.py` — show constraint summary when no verifier sidecars present
- Create: `tests/test_constraint_checks.py` — unit tests for all new check functions

---

## Phase 1: Type Range & Null Contract Checks

**End state:** `confidence.py` emits `type_range` and `null_contract` `ConfidenceCheck` entries per column for every rowstore table. A TINYINT column with a value of 300 produces `Severity.FAIL`.

**Files:** `mssqlbak/confidence.py`, `mssqlbak/extract.py`

### Type range table

| SQL type | `type_id` | Valid decoded range |
|----------|-----------|---------------------|
| `TINYINT` | 48 | 0 – 255 |
| `SMALLINT` | 52 | -32768 – 32767 |
| `INT` | 56 | -2,147,483,648 – 2,147,483,647 |
| `BIGINT` | 127 | -2^63 – 2^63-1 |
| `REAL` | 59 | no `±inf`/`nan` unless all rows are such |
| `FLOAT` | 62 | same |
| `DATE` | any date type_id | 0001-01-01 – 9999-12-31 |
| `DATETIME` | 61 | 1753-01-01 – 9999-12-31 |
| `DATETIME2` | 42 | 0001-01-01 – 9999-12-31 |
| `NVARCHAR(n)` | 231 | all strings ≤ n chars (`max_length / 2`) |
| `VARCHAR(n)` | 167 | all strings ≤ n bytes (`max_length`) |

### Steps

- [ ] **Step 1: Write tests**

```python
# tests/test_constraint_checks.py
import pyarrow as pa
from mssqlbak.confidence import _type_range_check, _null_contract_check, Severity

def test_tinyint_out_of_range_is_fail():
    col = pa.array([0, 100, 300])  # 300 > 255
    check = _type_range_check("dbo.t", "val", 48, col)
    assert check.severity is Severity.FAIL

def test_tinyint_in_range_is_pass():
    col = pa.array([0, 100, 255])
    check = _type_range_check("dbo.t", "val", 48, col)
    assert check.severity is Severity.PASS

def test_not_null_col_with_nulls_is_fail():
    col = pa.array([1, None, 3])
    check = _null_contract_check("dbo.t", "val", is_nullable=False, col=col)
    assert check.severity is Severity.FAIL

def test_not_null_col_without_nulls_is_pass():
    col = pa.array([1, 2, 3])
    check = _null_contract_check("dbo.t", "val", is_nullable=False, col=col)
    assert check.severity is Severity.PASS
```

- [ ] **Step 2: Run the tests and verify they fail**

```bash
.venv/bin/python -m pytest tests/test_constraint_checks.py -q
```

Expected: `ImportError` for `_type_range_check`.

- [ ] **Step 3: Implement `_type_range_check` and `_null_contract_check` in `confidence.py`**

Use `pyarrow.compute` (`pc.min`, `pc.max`, `pc.sum(pc.is_null(...))`) to avoid materialising Python lists. Return a `ConfidenceCheck` with `evidence` dict containing `{observed_min, observed_max, allowed_min, allowed_max}` or `{null_count}`.

```python
import pyarrow.compute as pc

_TYPE_INT_RANGES: dict[int, tuple[int, int]] = {
    48:  (0, 255),            # TINYINT
    52:  (-32768, 32767),     # SMALLINT
    56:  (-2_147_483_648, 2_147_483_647),  # INT
    127: (-(2**63), 2**63-1),             # BIGINT
}

def _type_range_check(fqn: str, col_name: str, type_id: int, col: pa.Array) -> ConfidenceCheck:
    ...

def _null_contract_check(fqn: str, col_name: str, is_nullable: bool, col: pa.Array) -> ConfidenceCheck:
    ...
```

- [ ] **Step 4: Wire into `analyze_bak`** — after decoding each rowstore table to Arrow, call these per column.

- [ ] **Step 5: Run tests and verify they pass**

```bash
.venv/bin/python -m pytest tests/test_constraint_checks.py -q
```

---

## Phase 2: B-Tree Key Ordering Check

**End state:** For every clustered rowstore table with a single integer/date key column, `analyze_bak` emits a `btree_key_order` check. A misordered page produces `Severity.FAIL`.

**Files:** `mssqlbak/confidence.py`, `mssqlbak/catalog.py`

**How:** `recover_indexes` (already exists in `catalog.py`) returns the clustered index and its key column. After extracting the table to Arrow, compute `pc.is_sorted(arrow_table, sort_keys=[(key_col_name, "ascending")])`. If False, find the first out-of-order value pair and include it in evidence.

### Steps

- [ ] **Step 1: Write test**

```python
def test_btree_key_order_disordered_is_fail():
    # Simulate rows decoded from pages in wrong order
    tbl = pa.table({"id": [1, 3, 2], "val": ["a", "b", "c"]})
    check = _btree_key_order_check("dbo.t", "id", tbl)
    assert check.severity is Severity.FAIL

def test_btree_key_order_correct_is_pass():
    tbl = pa.table({"id": [1, 2, 3], "val": ["a", "b", "c"]})
    check = _btree_key_order_check("dbo.t", "id", tbl)
    assert check.severity is Severity.PASS
```

- [ ] **Step 2: Run the tests and verify they fail**

- [ ] **Step 3: Implement `_btree_key_order_check`**

```python
def _btree_key_order_check(fqn: str, key_col: str, arrow_table: pa.Table) -> ConfidenceCheck:
    col = arrow_table.column(key_col)
    if pc.all(pc.greater_equal(col[1:], col[:-1])).as_py():
        return ConfidenceCheck("btree_key_order", Severity.PASS, ...)
    # find first violation for evidence
    ...
```

- [ ] **Step 4: Wire into `analyze_bak`** — call after extracting each clustered rowstore table that has a single-column integer/date/datetime clustered key.

- [ ] **Step 5: Run tests**

---

## Phase 3: Columnstore Segment Metadata Cross-Check

**End state:** For every CCI table, each decoded segment emits a `cci_segment_contract` check comparing row count, null presence, and (for enc=1/2) value range against `_ColumnSegment` fields. A segment whose decoded max exceeds `cdi_max` produces `Severity.FAIL`.

**Files:** New `mssqlbak/constraint_check.py`, `mssqlbak/columnstore/assembly/reader.py`

**Key formula** (already used in `dict_string.py` and `value_for.py`):

```
actual_min = seg.mn * seg.magnitude
actual_max = seg.cdi_max * seg.magnitude   # cdi_max = 0 means unknown
```

Gate on env var `MSSQLBAK_CONSTRAINT_CHECKS=1` so the hot extraction path is untouched by default.

### Steps

- [ ] **Step 1: Create `mssqlbak/constraint_check.py`**

```python
"""Post-decode constraint checks against _ColumnSegment metadata."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import pyarrow as pa
import pyarrow.compute as pc
from mssqlbak.columnstore.storage.segment_meta import _ColumnSegment

@dataclass(frozen=True)
class SegmentConstraintResult:
    seg_id: int
    col_id: int
    check: str
    passed: bool
    evidence: dict[str, object]

def check_cci_segment(seg: _ColumnSegment, decoded_col: pa.Array) -> list[SegmentConstraintResult]:
    results = []
    # row count
    results.append(SegmentConstraintResult(
        seg.seg_id, seg.col_id, "row_count",
        len(decoded_col) == seg.n_rows,
        {"decoded": len(decoded_col), "expected": seg.n_rows},
    ))
    # null contract
    if not seg.has_null:
        null_count = pc.sum(pc.is_null(decoded_col)).as_py() or 0
        results.append(SegmentConstraintResult(
            seg.seg_id, seg.col_id, "null_contract",
            null_count == 0,
            {"null_count": null_count},
        ))
    # value range for enc=1/2 with known max
    if seg.enc_type in (1, 2) and seg.cdi_max != 0 and seg.magnitude != 0.0:
        expected_min = seg.mn * seg.magnitude
        expected_max = seg.cdi_max * seg.magnitude
        non_null = decoded_col.drop_null()
        if len(non_null) > 0:
            obs_min = pc.min(non_null).as_py()
            obs_max = pc.max(non_null).as_py()
            results.append(SegmentConstraintResult(
                seg.seg_id, seg.col_id, "value_range",
                obs_min >= expected_min and obs_max <= expected_max,
                {"obs_min": obs_min, "obs_max": obs_max,
                 "seg_min": expected_min, "seg_max": expected_max},
            ))
    return results
```

- [ ] **Step 2: Write tests for `check_cci_segment`**

- [ ] **Step 3: Wire into `columnstore/assembly/reader.py`** — after each `_decode_enc1`/`_decode_enc3`/`_decode_enc5` call, if `os.environ.get("MSSQLBAK_CONSTRAINT_CHECKS")` is set, call `check_cci_segment` and accumulate results in a thread-local list (same pattern as `decode_trace`).

- [ ] **Step 4: Expose accumulated results** — add `get_segment_constraint_results() -> list[SegmentConstraintResult]` to `constraint_check.py`.

- [ ] **Step 5: Run tests**

---

## Phase 4: Constraint Report Generation

**End state:** `tools/confidence_report.py --report constraints path/to.bak` writes a markdown file and prints a summary. `ConfidenceReport` gains `to_markdown()` and `to_json()` methods.

**Files:** `mssqlbak/confidence.py`, `tools/confidence_report.py`, `tools/correctness_coverage.py`

### Markdown report format

```markdown
## Constraint Report: AdventureWorksDW2025.bak

Generated: 2026-06-30T18:00:00Z  
Status: PASS (3 FAIL, 0 WARN, 847 PASS)

### Summary by check type

| Check | PASS | WARN | FAIL |
|-------|------|------|------|
| type_range | 120 | 0 | 0 |
| null_contract | 85 | 0 | 1 |
| btree_key_order | 14 | 0 | 0 |
| cci_segment_contract | 628 | 0 | 2 |

### Failures

| Table | Column | Check | Observed | Constraint |
|-------|--------|-------|----------|------------|
| dbo.FactSales | Quantity | null_contract | null_count=3 | NOT NULL |
| dbo.FactSales | UnitPrice | cci_segment_contract | max=9999.99 | seg_max=1000.00 |
```

### Steps

- [ ] **Step 1: Add `to_markdown()` and `to_json()` to `ConfidenceReport`**

- [ ] **Step 2: Add `--report constraints` flag to `tools/confidence_report.py`**

Writes `<bak_stem>.constraints.md` alongside the `.bak` when `--output-dir` is given, or prints to stdout.

- [ ] **Step 3: Update `tools/correctness_coverage.py`**

When no `.cells/` or `.stats.json` verifier sidecars are present for a `.bak`, show a one-line constraint summary:

```
  (no verifier) constraints: 847 pass · 3 fail  [type_range: 0F, null_contract: 1F, cci_segment: 2F]
```

- [ ] **Step 4: Write CLI test**

```bash
.venv/bin/python -m pytest tests/test_confidence.py -q -k constraint_report
```

---

## Phase 5: Integration & Docs

**End state:** `python -m tools.confidence_report --report constraints tests/fixtures_realworld/Chinook-id-pk.bak` runs clean. A decisions doc records the constraint check design.

- [ ] **Step 1: Run full constraint report against `Chinook-id-pk.bak`**

```bash
MSSQLBAK_CONSTRAINT_CHECKS=1 \
  .venv/bin/python -m tools.confidence_report --report constraints \
  tests/fixtures_realworld/Chinook-id-pk.bak
```

Expected: all constraint checks PASS for Chinook.

- [ ] **Step 2: Run against a fixture with a known failure**

Use `pagecomp_long_prefix_full.bak` or `compressed_nvarchar_full.bak`. Verify the report emits checks.

- [ ] **Step 3: Write `docs/decisions/20260630-internal-constraint-validation.md`**

Record why each check is self-contained and what it proves vs. what it cannot prove (no statblob histogram parsing; no LOB chain integrity yet).

- [ ] **Step 4: Commit**

```bash
git add mssqlbak/confidence.py mssqlbak/constraint_check.py \
    mssqlbak/columnstore/assembly/reader.py \
    tools/confidence_report.py tools/correctness_coverage.py \
    tests/test_constraint_checks.py \
    docs/decisions/20260630-internal-constraint-validation.md
git commit -m "feat(confidence): internal constraint validation from .bak metadata"
```

---

## Verification Checklist

- [ ] `.venv/bin/python -m pytest tests/test_constraint_checks.py -q`
- [ ] `.venv/bin/python -m pytest tests/test_confidence.py -q`
- [ ] `MSSQLBAK_CONSTRAINT_CHECKS=1 .venv/bin/python -m tools.confidence_report --report constraints tests/fixtures_realworld/Chinook-id-pk.bak`
- [ ] `.venv/bin/python -m pytest tests/ -q -x --ignore=tests/fixtures_realworld` (no regressions)

---

## What This Plan Intentionally Excludes

| Item | Reason |
|------|--------|
| SQL Server statistics histogram bounds (`statblob`) | Binary format not yet reverse-engineered; large effort for approximate bounds only |
| LOB chain integrity (forward/back pointers in blob pages) | Requires tracing blob page chains; medium effort, Phase 6 candidate |
| Page checksum / torn-page detection | Already validated at page-read time in `PageStore`; surfacing it in the report is wiring only — add if needed |

---

## Acceptance Criteria

- Running `confidence_report --report constraints` on any `.bak` produces a markdown file listing every constraint check and its result.
- A decoded column whose values violate a type range, null contract, or CCI segment bound produces `Severity.FAIL` — with no SQL Server connection and no external ground truth.
- No regression in existing `test_confidence.py` or `test_correctness_coverage_cli.py` tests.
- `correctness_coverage` shows the constraint summary line for `.bak` files that have no verifier sidecars.
