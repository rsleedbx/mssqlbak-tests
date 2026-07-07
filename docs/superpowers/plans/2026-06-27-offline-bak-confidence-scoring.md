# Offline BAK Confidence Scoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an offline confidence report that uses `.bak` internal metadata to assess extraction quality when SQL Server `.stats.json` or `.cells/` ground truth is unavailable.

**Architecture:** Build a new confidence module that produces structured checks per backup and table, then expose it through a CLI and optionally summarize it in `tools.correctness_coverage`. The score is evidence-based: it reports passed, warning, and failed invariants rather than claiming ground-truth value correctness.

**Tech Stack:** Python, `pytest`, existing `mssqlbak` catalog/page/row/columnstore readers, existing fixture and correctness coverage tooling.

---

## Scope

This plan adds offline confidence scoring. It does not replace `.stats.json` or `.cells/` verification. When SQL Server verifier sidecars exist, those remain stronger evidence.

## Design Decisions

- Confidence checks are structured results with severity, evidence, and table scope.
- The CLI reports both a summary grade and the failed/warning checks.
- Initial implementation targets rowstore and backup/page/catalog invariants.
- Columnstore segment checks are a later task after the rowstore framework is stable.
- A `.bak` SHA-256 proves file identity only; it is not counted as decode correctness.

## Files

- Create: `mssqlbak/confidence.py` — data model and offline invariant checks.
- Create: `tools/confidence_report.py` — command-line report for one or more `.bak` files.
- Create: `tests/test_confidence.py` — unit and fixture-backed tests for confidence checks.
- Modify: `tools/correctness_coverage.py` — optional confidence summary when verifier sidecars are absent.
- Modify: `docs/offline_confidence_scoring.md` — user-facing explanation of what confidence does and does not prove.

## Task 1: Add Confidence Result Model

**Files:**
- Create: `mssqlbak/confidence.py`
- Create: `tests/test_confidence.py`

- [ ] **Step 1: Write tests for the result model**

Add tests that construct several checks and verify severity rollup.

```python
from mssqlbak.confidence import ConfidenceCheck, ConfidenceReport, Severity


def test_confidence_report_rollup_prefers_failed_checks() -> None:
    report = ConfidenceReport(
        bak_name="sample.bak",
        checks=[
            ConfidenceCheck("file_identity", Severity.PASS, "sha256 recorded"),
            ConfidenceCheck("row_count", Severity.FAIL, "decoded 7 rows, expected 8"),
        ],
    )

    assert report.status is Severity.FAIL


def test_confidence_report_rollup_allows_warnings() -> None:
    report = ConfidenceReport(
        bak_name="sample.bak",
        checks=[
            ConfidenceCheck("file_identity", Severity.PASS, "sha256 recorded"),
            ConfidenceCheck("btree_order", Severity.WARN, "no clustered key available"),
        ],
    )

    assert report.status is Severity.WARN
```

- [ ] **Step 2: Run the tests and verify they fail**

```bash
.venv/bin/python -m pytest tests/test_confidence.py -q
```

Expected: import failure for `mssqlbak.confidence`.

- [ ] **Step 3: Implement the result model**

Create immutable result objects with simple rollup.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class ConfidenceCheck:
    name: str
    severity: Severity
    message: str
    table: str | None = None
    evidence: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ConfidenceReport:
    bak_name: str
    checks: list[ConfidenceCheck]

    @property
    def status(self) -> Severity:
        severities = {check.severity for check in self.checks}
        if Severity.FAIL in severities:
            return Severity.FAIL
        if Severity.WARN in severities:
            return Severity.WARN
        return Severity.PASS
```

- [ ] **Step 4: Run the tests and verify they pass**

```bash
.venv/bin/python -m pytest tests/test_confidence.py -q
```

Expected: all tests pass.

## Task 2: Add Backup-Set and File Identity Checks

**Files:**
- Modify: `mssqlbak/confidence.py`
- Modify: `tests/test_confidence.py`

- [ ] **Step 1: Write tests for `Chinook-id-pk.bak` backup-set detection**

Use `tests/fixtures_realworld/Chinook-id-pk.bak` when present. Skip when absent.

```python
from pathlib import Path

import pytest

from mssqlbak.confidence import analyze_bak, Severity


def test_chinook_id_pk_reports_multiple_backup_sets() -> None:
    bak = Path("tests/fixtures_realworld/Chinook-id-pk.bak")
    if not bak.exists():
        pytest.skip("Chinook-id-pk.bak not downloaded")

    report = analyze_bak(bak)

    check = next(c for c in report.checks if c.name == "backup_set_selection")
    assert check.severity is Severity.WARN
    assert check.evidence["backup_sets"] == 2
```

- [ ] **Step 2: Run the test and verify it fails**

```bash
.venv/bin/python -m pytest tests/test_confidence.py::test_chinook_id_pk_reports_multiple_backup_sets -q
```

Expected: `analyze_bak` is not implemented.

- [ ] **Step 3: Implement backup-set and SHA-256 checks**

Use existing `mssqlbak.reader.read_bak_metadata` for backup sets. Compute SHA-256 with a streaming helper.

```python
from pathlib import Path
import hashlib

from mssqlbak.reader import read_bak_metadata


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def analyze_bak(path: str | Path) -> ConfidenceReport:
    bak = Path(path)
    checks: list[ConfidenceCheck] = [
        ConfidenceCheck(
            "file_identity",
            Severity.PASS,
            "computed .bak SHA-256",
            evidence={"sha256": sha256_file(bak)},
        )
    ]

    metadata = read_bak_metadata(bak)
    backup_sets = len(metadata.backup_sets)
    checks.append(
        ConfidenceCheck(
            "backup_set_selection",
            Severity.PASS if backup_sets <= 1 else Severity.WARN,
            "single backup set" if backup_sets <= 1 else "multiple backup sets; default extraction uses first set",
            evidence={"backup_sets": backup_sets},
        )
    )
    return ConfidenceReport(bak.name, checks)
```

- [ ] **Step 4: Run the tests**

```bash
.venv/bin/python -m pytest tests/test_confidence.py -q
```

Expected: all confidence tests pass.

## Task 3: Add Catalog Row Count Checks

**Files:**
- Modify: `mssqlbak/confidence.py`
- Modify: `tests/test_confidence.py`

- [ ] **Step 1: Write a row count confidence test**

Use a small fixture with known catalog row counts. Start with `Chinook-id-pk.bak` because it is fast.

```python
def test_chinook_employee_row_count_matches_catalog() -> None:
    bak = Path("tests/fixtures_realworld/Chinook-id-pk.bak")
    if not bak.exists():
        pytest.skip("Chinook-id-pk.bak not downloaded")

    report = analyze_bak(bak)

    employee = [
        c for c in report.checks
        if c.name == "row_count_consistency" and c.table == "dbo.Employee"
    ][0]
    assert employee.severity is Severity.PASS
    assert employee.evidence["decoded_rows"] == 8
```

- [ ] **Step 2: Run the test and verify it fails**

```bash
.venv/bin/python -m pytest tests/test_confidence.py::test_chinook_employee_row_count_matches_catalog -q
```

Expected: no `row_count_consistency` check yet.

- [ ] **Step 3: Implement row count checks**

Use `PageStore.from_bak`, `recover_schema`, and `read_table_rows`. Compare decoded row counts to catalog row counts only when a trusted catalog count is available. If a table lacks a trusted count, emit `WARN` with evidence.

- [ ] **Step 4: Run focused tests**

```bash
.venv/bin/python -m pytest tests/test_confidence.py -q
```

Expected: confidence tests pass.

## Task 4: Add Allocation and Page Structure Checks

**Files:**
- Modify: `mssqlbak/confidence.py`
- Modify: `tests/test_confidence.py`

- [ ] **Step 1: Write checks for page traversal**

The first implementation should validate:
- Page ids and file ids match their location.
- Visited data pages belong to the expected object/index.
- Record slot offsets stay within page bounds.
- Record decode does not raise for supported rowstore tables.

- [ ] **Step 2: Add tests with `AdventureWorksLT2012.bak` and `BaseballData.bak`**

Skip when files are absent. These are regression fixtures for prior catalog traversal bugs.

- [ ] **Step 3: Implement page checks**

Reuse existing page and row traversal code. Do not add new traversal logic unless an existing helper cannot expose the needed evidence.

- [ ] **Step 4: Run focused tests**

```bash
.venv/bin/python -m pytest tests/test_confidence.py -q
```

Expected: all confidence tests pass.

## Task 5: Add CLI Report

**Files:**
- Create: `tools/confidence_report.py`
- Modify: `tests/test_confidence.py`

- [ ] **Step 1: Write CLI test**

Use `subprocess.run` or direct `main(argv)` invocation. Assert JSON output includes `status` and at least one check.

- [ ] **Step 2: Implement CLI**

Support:

```bash
.venv/bin/python -m tools.confidence_report tests/fixtures_realworld/Chinook-id-pk.bak
.venv/bin/python -m tools.confidence_report --json tests/fixtures_realworld/Chinook-id-pk.bak
```

- [ ] **Step 3: Run CLI manually**

```bash
.venv/bin/python -m tools.confidence_report tests/fixtures_realworld/Chinook-id-pk.bak
```

Expected output includes:

```text
Chinook-id-pk.bak: warn
  pass file_identity
  warn backup_set_selection: multiple backup sets; default extraction uses first set
```

## Task 6: Integrate With Correctness Coverage

**Files:**
- Modify: `tools/correctness_coverage.py`
- Modify: `tests/test_correctness_coverage_cli.py`

- [ ] **Step 1: Write tests for confidence fallback**

Create a temp fixture layout with a `.bak`-like file is not enough because confidence needs a real `.bak`. Use a helper that verifies rendering behavior with injected confidence data, or structure the renderer so the confidence summary can be unit-tested without a real backup.

- [ ] **Step 2: Add confidence notes only when verifier sidecars are absent**

Rules:
- If `.cells/` exists, cell verification remains primary.
- If `.stats.json` exists, row/null/min/max checks remain primary.
- If neither exists, show confidence status and failed checks.

- [ ] **Step 3: Run correctness coverage CLI tests**

```bash
.venv/bin/python -m pytest tests/test_correctness_coverage_cli.py -q
```

Expected: tests pass.

## Task 7: Add Columnstore Metadata Checks

**Files:**
- Modify: `mssqlbak/confidence.py`
- Modify: `tests/test_confidence.py`

- [ ] **Step 1: Inventory available columnstore metadata readers**

Identify existing helpers for rowgroups, segments, dictionaries, and delete bitmaps.

- [ ] **Step 2: Add segment count checks**

Validate decoded row count against rowgroup metadata minus deleted rows.

- [ ] **Step 3: Add segment null/min/max checks where supported**

Emit `WARN` for unsupported types rather than failing.

- [ ] **Step 4: Run columnstore fixture tests**

```bash
FIXTURE_DIR=tests/fixtures_2022 .venv/bin/python -m pytest tests/test_confidence.py -q -k columnstore
```

Expected: supported checks pass; unsupported checks produce warnings.

## Task 8: Documentation

**Files:**
- Create: `docs/offline_confidence_scoring.md`

- [ ] **Step 1: Document what confidence proves**

State:
- Confidence checks validate internal consistency.
- They do not prove every decoded cell matches SQL Server.
- `.cells/` verification is stronger when available.

- [ ] **Step 2: Document commands**

Include:

```bash
.venv/bin/python -m tools.confidence_report <path-to.bak>
.venv/bin/python -m tools.correctness_coverage <path-to.bak>
```

- [ ] **Step 3: Link from relevant docs**

Add a short link from correctness coverage docs if there is an existing overview page.

## Verification Checklist

- [ ] `.venv/bin/python -m pytest tests/test_confidence.py -q`
- [ ] `.venv/bin/python -m pytest tests/test_correctness_coverage_cli.py -q`
- [ ] `FIXTURE_DIR=tests/fixtures_realworld .venv/bin/python -m pytest tests/test_stats.py -q -k Chinook`
- [ ] `.venv/bin/python -m tools.confidence_report tests/fixtures_realworld/Chinook-id-pk.bak`

## Acceptance Criteria

- Users can run an offline confidence report for a `.bak` without SQL Server.
- Reports identify multiple backup sets and file identity.
- Rowstore tables get table-level row count and structural checks.
- Correctness coverage can show confidence status when verifier sidecars are missing.
- Documentation states that confidence is weaker than SQL Server `.cells/` verification.
