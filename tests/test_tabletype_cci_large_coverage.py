"""CCI large-row-group type-coverage tests (Gap K-1).

Validates that the segment decoder correctly decodes every CCI-compatible type
when the row group has 1,200 rows — enough to produce non-trivial dictionary
encoding, bit-packing, and null bit-vectors inside the compressed segment.

The 4 structural rows (id=1 low, 2 high, 3 mid, 4 null) carry the same type
values as the existing ``tabletypecoverage_full.bak`` so the reference matrix
from ``tools/tabletypematrix.py`` can be reused directly.

The 1,196 filler rows (ids 7–1,202) have all type columns NULL; they are not
individually asserted here but their presence forces the encoder to emit real
null bit-vectors and multi-entry dictionaries.

Running
-------
    pytest tests/test_tabletype_cci_large_coverage.py -q
    pytest -k "test_structural_rows and cci_large and int" -q
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import deltalake
import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.extract import extract_bak_to_delta
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools import value_verify
from tools.tabletypematrix import (
    COLUMNSTORE_LARGE_XFAIL,
    LABEL_ID,
    LABELS,
    ORG_CASES,
    supported_cases,
    table_name,
)
from tools.typematrix import TypeCase
from tools.make_tabletype_cci_large_fixture import DB_NAME, TOTAL_ROWS


# ---------------------------------------------------------------------------
# Fixture metadata
# ---------------------------------------------------------------------------

_COL_ORG = next(o for o in ORG_CASES if o.name == "column")
_CCI_CASES = supported_cases(_COL_ORG)
_CCI_IDS = [c.name for c in _CCI_CASES]
_TABLE_NAME = table_name(_COL_ORG)  # "tt_column"
_ID_TO_LABEL = {v: k for k, v in LABEL_ID.items()}  # {1: "low", 2: "high", ...}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_tt_column(
    fixture: Path,
) -> tuple[int, dict[str, dict[str, Any]]]:
    """Return (total_row_count, {col_name: {label: decoded_value}}).

    Labels are inferred from ``id`` via ``LABEL_ID``; filler rows get label
    ``"id{N}"`` and are not checked by the type-assertion tests.
    """
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == _TABLE_NAME), None)
    if table is None:
        pytest.fail(f"Table {_TABLE_NAME!r} not found in fixture (DB: {DB_NAME})")

    col_vals: dict[str, dict[str, Any]] = {}
    count = 0
    for row in read_table_rows(store, table):
        count += 1
        row_id: int = row["id"]
        label = _ID_TO_LABEL.get(row_id, f"id{row_id}")
        for col_name, val in row.items():
            if col_name == "id":
                continue
            col_vals.setdefault(col_name, {})[label] = val

    return count, col_vals


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_total_row_count(fixture_bak_tabletype_cci_large: Path) -> None:
    """Row count matches the expected total (structural + filler)."""
    count, _ = _read_tt_column(fixture_bak_tabletype_cci_large)
    assert count == TOTAL_ROWS, (
        f"expected {TOTAL_ROWS} rows in {_TABLE_NAME!r}, got {count}"
    )


@pytest.mark.fixture
def test_database_name_in_fixture(fixture_bak_tabletype_cci_large: Path) -> None:
    """The fixture's backup contains the expected database."""
    store = PageStore.from_bak(fixture_bak_tabletype_cci_large)
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == _TABLE_NAME), None)
    assert table is not None, (
        f"Table {_TABLE_NAME!r} not found — fixture may be wrong database "
        f"(expected {DB_NAME})"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("case", _CCI_CASES, ids=_CCI_IDS)
def test_structural_rows(
    fixture_bak_tabletype_cci_large: Path,
    case: TypeCase,
    request: pytest.FixtureRequest,
) -> None:
    """Each structural row (low/high/mid/null) decodes to the reference value.

    This is the core K-1 assertion: the CCI segment decoder (not the delta-store
    B-tree reader) must correctly reconstruct every type value for each of the
    four structural rows that carry the type-matrix reference data.
    """
    if case.name in COLUMNSTORE_LARGE_XFAIL:
        request.applymarker(pytest.mark.xfail(
            strict=False,
            reason=(
                f"CCI large-segment decoder bug for {case.name!r}: "
                "wrong value returned when row group uses real encoding paths "
                "(invisible in 4-row fixture; revealed by K-1/K-3 — "
                "see tabletypematrix.COLUMNSTORE_LARGE_XFAIL)"
            ),
        ))

    _, col_vals = _read_tt_column(fixture_bak_tabletype_cci_large)
    col_name = f"c_{case.name}"

    if col_name not in col_vals:
        if case.fallback_xtype is not None:
            pytest.skip(
                f"{case.name!r} is not present in {_TABLE_NAME!r}; "
                "covered by its version-specific fixture"
            )
        pytest.fail(
            f"Column {col_name!r} missing from {_TABLE_NAME!r} — "
            "fixture may need regeneration"
        )

    ref = {row.label: row.value for row in case.rows}
    decoded = col_vals[col_name]

    for label in LABELS:
        if label not in ref:
            continue  # type case doesn't define this label
        if label not in decoded:
            pytest.fail(
                f"Structural row label {label!r} not found for column {col_name!r}"
            )
        expected = ref[label]
        actual = decoded[label]

        if case.auto:
            assert actual is not None, (
                f"auto column {col_name!r} label={label!r}: expected non-NULL"
            )
        elif expected is None:
            assert actual is None, (
                f"{col_name!r} label={label!r}: expected NULL, got {actual!r}"
            )
        else:
            assert actual == expected, (
                f"{col_name!r} label={label!r}: expected {expected!r}, got {actual!r}"
            )


@pytest.mark.fixture
def test_cells_match_sidecar(fixture_bak_tabletype_cci_large: Path) -> None:
    cells_dir = value_verify.cells_dir_for(fixture_bak_tabletype_cci_large)
    if not cells_dir.exists():
        pytest.skip(f"cell sidecar missing: {cells_dir}")

    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(fixture_bak_tabletype_cci_large), tmp)
        table = deltalake.DeltaTable(str(Path(tmp) / "dbo" / _TABLE_NAME)).to_pyarrow_table()

    manifest = value_verify.load_manifest(cells_dir)
    entry = next(t for t in manifest["tables"] if t["fqn"] == f"dbo.{_TABLE_NAME}")
    res = value_verify.verify_table(table, cells_dir, entry)

    assert res.ok, (
        f"{_TABLE_NAME} value verification failed: "
        f"cells={res.cells_ok}/{res.cells_total} "
        f"bad={res.col_mismatches} digests={res.digest_mismatches} "
        f"samples={res.samples[:5]}"
    )
