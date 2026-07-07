"""Guard: the committed type-coverage doc must match a fresh generation.

This keeps ``docs/TYPE_COVERAGE.md`` in sync with the actual parser/test results
on every run -- if a type's status changes (a new type covered, or a regression),
this test fails until the doc is regenerated with ``python -m tools.type_coverage``.
"""
from __future__ import annotations

import pytest

from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.types import SUPPORTED_TYPE_IDS
from tools.type_coverage import DOC_PATH, _matrix_results, build_report


@pytest.mark.fixture
def test_type_coverage_doc_is_current(fixture_bak) -> None:
    expected = build_report(fixture_bak)
    actual = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    assert actual == expected, (
        "docs/TYPE_COVERAGE.md is stale; regenerate it with "
        "`python -m tools.type_coverage`"
    )


@pytest.mark.fixture
def test_every_supported_type_has_a_reference_case(fixture_bak) -> None:
    """Untested is unsupported: every decodable type id must have a case."""
    store: AnyPageStore = PageStore.from_bak(fixture_bak)
    tested = _matrix_results(store)
    covered_xtypes = {xtype for xtype, _sql, _ok, _auto in tested.values()}
    missing = sorted(SUPPORTED_TYPE_IDS - covered_xtypes)
    assert not missing, (
        f"type ids {missing} are in SUPPORTED_TYPE_IDS but have no reference "
        "case in tools/typematrix.py — add one (untested is unsupported)"
    )
