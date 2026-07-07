"""Regression coverage for bounded VARCHAR CCI string dictionaries.

The synthetic fixture mirrors the real-world TPC-BB columns that exposed
dictionary decode regressions:

* ``dbo.item.i_item_desc`` - item-description strings.
* ``dbo.product_reviews.pr_review_content`` - longer review text strings.

The test stays small enough for the fast suite but checks the whole column via
digests so silent empty/garbage dictionary lookups are caught.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.cell_canon import canon, column_digest
from tools.make_cci_string_dict_regression_fixture import (
    BATCH1_ROWS,
    BATCH2_ROWS,
    EMPTY_ID,
    NULL_ID,
    SAMPLE_IDS,
    TABLE,
    TOTAL_ROWS,
    expected_item_desc,
    expected_review_content,
)

_VARCHAR = "varchar"


def _read_rows(fixture: Path) -> list[dict[str, Any]]:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == TABLE), None)
    if table is None:
        pytest.fail(f"table {TABLE!r} not found in {fixture}")
    return list(read_table_rows(store, table))


def _expected_item_digest() -> str:
    return column_digest(
        canon(expected_item_desc(idv), _VARCHAR) for idv in range(1, TOTAL_ROWS + 1)
    )


def _expected_review_digest() -> str:
    return column_digest(
        canon(expected_review_content(idv), _VARCHAR)
        for idv in range(1, TOTAL_ROWS + 1)
    )


def test_cci_string_dict_regression_row_count(
    fixture_bak_cci_string_dict_regression: Path,
) -> None:
    rows = _read_rows(fixture_bak_cci_string_dict_regression)
    assert len(rows) == TOTAL_ROWS


def test_cci_string_dict_regression_batches_present(
    fixture_bak_cci_string_dict_regression: Path,
) -> None:
    rows = _read_rows(fixture_bak_cci_string_dict_regression)
    batch1 = [r for r in rows if r["batch"] == 1]
    batch2 = [r for r in rows if r["batch"] == 2]

    assert len(batch1) == BATCH1_ROWS
    assert len(batch2) == BATCH2_ROWS


def test_cci_string_dict_regression_null_and_empty(
    fixture_bak_cci_string_dict_regression: Path,
) -> None:
    rows_by_id = {r["id"]: r for r in _read_rows(fixture_bak_cci_string_dict_regression)}

    empty_row = rows_by_id[EMPTY_ID]
    assert empty_row["i_item_desc"] == ""
    assert empty_row["pr_review_content"] == ""

    null_row = rows_by_id[NULL_ID]
    assert null_row["i_item_desc"] is None
    assert null_row["pr_review_content"] is None


def test_cci_string_dict_regression_spot_checks(
    fixture_bak_cci_string_dict_regression: Path,
) -> None:
    rows_by_id = {r["id"]: r for r in _read_rows(fixture_bak_cci_string_dict_regression)}

    for idv in SAMPLE_IDS:
        row = rows_by_id[idv]
        assert row["i_item_desc"] == expected_item_desc(idv), (
            f"id={idv}: bad i_item_desc"
        )
        assert row["pr_review_content"] == expected_review_content(idv), (
            f"id={idv}: bad pr_review_content"
        )


def test_cci_string_dict_regression_column_digests(
    fixture_bak_cci_string_dict_regression: Path,
) -> None:
    rows = _read_rows(fixture_bak_cci_string_dict_regression)
    item_digest = column_digest(canon(r["i_item_desc"], _VARCHAR) for r in rows)
    review_digest = column_digest(canon(r["pr_review_content"], _VARCHAR) for r in rows)

    assert item_digest == _expected_item_digest()
    assert review_digest == _expected_review_digest()
