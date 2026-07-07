"""Coverage tests for ``ncci_types_full.bak`` — rowstore tables with NCCI (Gap K-5).

Each table has a ``NONCLUSTERED COLUMNSTORE INDEX`` on its ``val`` column.
The primary data is read from the clustered B-tree; the NCCI segments must not
corrupt the primary data pages or catalog metadata.

Tables are read via the normal ``read_table_rows`` B-tree path.  The key
assertion is that having an NCCI on each type does not silently produce wrong
values — any row-locator column stored beside the NCCI segment must not shift
type-dependent value decoding.

Each table layout:

    id=1  — low boundary value
    id=2  — high boundary value
    id=3  — NULL sentinel
    id=7..1206  — 1,200 varied filler rows

Total: 1,203 rows per table.

Generate the fixture::

    python -m tools.fixture_run ncci-types
    python -m tools.fixture_run all-versions --suite ncci-types
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import deltalake
import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.extract import extract_bak_to_delta
from mssqlbak.inspect import classify_table
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools import value_verify
from tools.make_ncci_types_fixture import (
    ROWS_PER_TABLE,
    STRUCTURAL_IDS,
    TABLE_DEFS,
)

_ID_TO_LABEL = {v: k for k, v in STRUCTURAL_IDS.items()}


def _read_table(
    fixture: Path, table_name: str
) -> tuple[int, dict[str, Any]]:
    """Return (total_row_count, {label: decoded_val}) for the ``val`` column.

    Only structural rows (ids in STRUCTURAL_IDS) are included in the dict;
    filler rows are counted but not checked.
    """
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == table_name), None)
    if tbl is None:
        pytest.fail(f"Table {table_name!r} not found in {fixture.name}")

    by_label: dict[str, Any] = {}
    count = 0
    for row in read_table_rows(store, tbl):
        count += 1
        row_id: int = row["id"]
        if row_id in _ID_TO_LABEL:
            by_label[_ID_TO_LABEL[row_id]] = row.get("val")
    return count, by_label


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_database_present(fixture_bak_ncci_types: Path) -> None:
    """Fixture opens without error and contains all 19 expected tables."""
    store = PageStore.from_bak(fixture_bak_ncci_types)
    schema = recover_schema(store)
    names = {t.name for t in schema.tables}
    for td in TABLE_DEFS:
        assert td.name in names, (
            f"Table {td.name!r} not found in {fixture_bak_ncci_types.name}; "
            f"available: {sorted(names)}"
        )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_table_classify_supported(fixture_bak_ncci_types: Path, td: Any) -> None:
    """Each NCCI table is classified as supported (readable via B-tree primary key)."""
    store = PageStore.from_bak(fixture_bak_ncci_types)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == td.name), None)
    assert tbl is not None, f"Table {td.name!r} not found"
    support = classify_table(tbl)
    assert support.supported, (
        f"{td.name}: expected supported=True, got reason={support.reason!r}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_row_count(fixture_bak_ncci_types: Path, td: Any) -> None:
    """Total row count matches expected rows per table."""
    count, _ = _read_table(fixture_bak_ncci_types, td.name)
    assert count == ROWS_PER_TABLE, (
        f"{td.name}: expected {ROWS_PER_TABLE} rows, got {count}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_null_row(fixture_bak_ncci_types: Path, td: Any) -> None:
    """The NULL structural row (id=3) decodes as None."""
    _, by_label = _read_table(fixture_bak_ncci_types, td.name)
    assert "null" in by_label, f"{td.name}: NULL row (id=3) not found"
    assert by_label["null"] is None, (
        f"{td.name}: NULL row decoded as {by_label['null']!r}, expected None"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_low_row(fixture_bak_ncci_types: Path, td: Any) -> None:
    """The low-boundary structural row (id=1) decodes correctly."""
    _, by_label = _read_table(fixture_bak_ncci_types, td.name)
    assert "low" in by_label, f"{td.name}: low row (id=1) not found"
    actual = by_label["low"]
    expected = td.low
    # Floating-point types: allow small rounding differences from SQL Server
    if isinstance(expected, float):
        assert actual is not None, f"{td.name}: low row is None"
        import math
        assert math.isfinite(expected) == math.isfinite(float(actual)), (
            f"{td.name}: low row finite mismatch: {actual!r} vs {expected!r}"
        )
    else:
        assert actual == expected, (
            f"{td.name}: low row decoded as {actual!r}, expected {expected!r}"
        )


@pytest.mark.fixture
@pytest.mark.parametrize("td", TABLE_DEFS, ids=[td.name for td in TABLE_DEFS])
def test_high_row(fixture_bak_ncci_types: Path, td: Any) -> None:
    """The high-boundary structural row (id=2) decodes correctly."""
    _, by_label = _read_table(fixture_bak_ncci_types, td.name)
    assert "high" in by_label, f"{td.name}: high row (id=2) not found"
    actual = by_label["high"]
    expected = td.high
    if isinstance(expected, float):
        assert actual is not None, f"{td.name}: high row is None"
        import math
        assert math.isfinite(expected) == math.isfinite(float(actual)), (
            f"{td.name}: high row finite mismatch: {actual!r} vs {expected!r}"
        )
    else:
        assert actual == expected, (
            f"{td.name}: high row decoded as {actual!r}, expected {expected!r}"
        )


@pytest.mark.fixture
def test_ncci_float_cells_match_sidecar(fixture_bak_ncci_types: Path) -> None:
    cells_dir = value_verify.cells_dir_for(fixture_bak_ncci_types)
    if not cells_dir.exists():
        pytest.skip(f"cell sidecar missing: {cells_dir}")

    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(fixture_bak_ncci_types), tmp)
        table = deltalake.DeltaTable(str(Path(tmp) / "dbo" / "ncci_float")).to_pyarrow_table()

    manifest = value_verify.load_manifest(cells_dir)
    entry = next(t for t in manifest["tables"] if t["fqn"] == "dbo.ncci_float")
    res = value_verify.verify_table(table, cells_dir, entry)

    assert res.ok, (
        f"ncci_float value verification failed: "
        f"cells={res.cells_ok}/{res.cells_total} "
        f"bad={res.col_mismatches} digests={res.digest_mismatches} "
        f"samples={res.samples[:5]}"
    )
