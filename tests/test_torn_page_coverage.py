"""Coverage tests for ``torn_page_full.bak`` — PAGE_VERIFY TORN_PAGE_DETECTION.

``torn_page_full.bak`` is a database created with ``PAGE_VERIFY TORN_PAGE_DETECTION``
active before any rows are inserted, so every data page in the backup carries
the torn-page bit signature.

Before commit ``2ed478b``, ``mssqlbak.pages.restore_torn_page`` was never called,
so the low 2 bits of every sector-boundary byte were left as the write signature
instead of the real data.  For clustered-index leaf pages this corrupts the
slot-array offset that sits at or near a sector boundary, causing some record
offsets to point into the wrong place and silently dropping rows.

These tests verify that all 300 rows are recovered and that label/score values
decode correctly — the same class of check that would have caught the 9,303-row
loss in CreditBackup100.bak.

Generate the fixture::

    python -m tools.fixture_run torn-page
    python -m tools.fixture_run all-versions --suite torn-page
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.make_torn_page_fixture import LABEL_FN, ROW_COUNT, SCORE_FN, TABLE


def _rows(fixture: Path) -> dict[int, dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE!r} not found in {fixture.name}")
    return {row["id"]: row for row in read_table_rows(store, tbl)}


@pytest.mark.fixture
def test_torn_page_row_count(fixture_bak_torn_page: Path) -> None:
    """All ROW_COUNT rows must be returned.

    With the old bug, the slot-0 offset on clustered-index leaf pages landing
    near a sector boundary decoded one bit too high, dropping the first record
    on those pages.
    """
    rows = _rows(fixture_bak_torn_page)
    assert len(rows) == ROW_COUNT, (
        f"expected {ROW_COUNT} rows, got {len(rows)} "
        "(missing rows indicate restore_torn_page is not being called)"
    )


@pytest.mark.fixture
def test_torn_page_all_ids_present(fixture_bak_torn_page: Path) -> None:
    """Every id from 1 to ROW_COUNT must be present — no gap anywhere."""
    rows = _rows(fixture_bak_torn_page)
    missing = [i for i in range(1, ROW_COUNT + 1) if i not in rows]
    assert not missing, f"missing ids: {missing[:20]}"


@pytest.mark.fixture
def test_torn_page_label_values(fixture_bak_torn_page: Path) -> None:
    """label column must decode correctly for a sample of rows."""
    rows = _rows(fixture_bak_torn_page)
    # Probe non-NULL rows, NULL rows, and rows near sector boundaries.
    probe_ids = list(range(1, 21)) + list(range(98, 108)) + [169, 170, 171, 300]
    bad: list[tuple[int, Any, Any]] = []
    for id_ in probe_ids:
        row = rows.get(id_)
        if row is None:
            bad.append((id_, LABEL_FN(id_), "MISSING ROW"))
            continue
        expected = LABEL_FN(id_)
        actual = row.get("label")
        if actual != expected:
            bad.append((id_, expected, actual))
    assert not bad, (
        "label mismatch for ids:\n"
        + "\n".join(f"  id={i}: expected={exp!r}, actual={act!r}" for i, exp, act in bad)
    )


@pytest.mark.fixture
def test_torn_page_score_values(fixture_bak_torn_page: Path) -> None:
    """score column (INT id²) must decode correctly — fixed-length column
    bytes that land on a sector boundary would read one bit too high without
    restore_torn_page.
    """
    rows = _rows(fixture_bak_torn_page)
    probe_ids = list(range(1, 21)) + [99, 100, 101, 110, 170, 200, 299, 300]
    bad: list[tuple[int, Any, Any]] = []
    for id_ in probe_ids:
        row = rows.get(id_)
        if row is None:
            bad.append((id_, SCORE_FN(id_), "MISSING ROW"))
            continue
        expected = SCORE_FN(id_)
        actual = row.get("score")
        if actual != expected:
            bad.append((id_, expected, actual))
    assert not bad, (
        "score mismatch for ids:\n"
        + "\n".join(f"  id={i}: expected={exp!r}, actual={act!r}" for i, exp, act in bad)
    )
