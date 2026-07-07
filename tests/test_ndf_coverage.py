"""Level-1 NDF (secondary filegroup) coverage tests.

Gap 3 fixture: ``ndfcoverage_full.bak`` — a database backed by two files:
  * the primary MDF (file_id = 1, filegroup PRIMARY) — ``dbo.primary_tbl``
  * a secondary NDF (file_id = 2, filegroup FG_SECONDARY) — ``dbo.secondary_tbl``

Tests verify that mssqlbak reads pages from *all* filegroups present in the
backup image, not only file_id = 1.  If ``secondary_tbl`` returns 0 rows the
IAM/B-tree reader is not crossing filegroup boundaries — the bug is in
``rows.py`` and the test acts as a regression gate.

Fixture generation::

    python -m tools.make_ndf_fixture
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _tables(path: Path) -> dict:
    return {t.name: t for t in recover_schema(_store(path)).tables}


def _rows(path: Path, table: str) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# primary_tbl — baseline (PRIMARY filegroup, file_id = 1)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_primary_tbl_classify_supported(fixture_bak_ndf: Path) -> None:
    """primary_tbl on PRIMARY filegroup is classified as supported."""
    tables = _tables(fixture_bak_ndf)
    result = classify_table(tables["primary_tbl"])
    assert result.supported, f"expected supported, got: {result.reason}"


@pytest.mark.fixture
def test_primary_tbl_row_count(fixture_bak_ndf: Path) -> None:
    """primary_tbl (PRIMARY filegroup) contains exactly 10 rows."""
    rows = _rows(fixture_bak_ndf, "primary_tbl")
    assert len(rows) == 10


@pytest.mark.fixture
def test_primary_tbl_values(fixture_bak_ndf: Path) -> None:
    """primary_tbl values decode correctly: val = 'primary_row_<id>'."""
    rows = _rows(fixture_bak_ndf, "primary_tbl")
    by_id = {r["id"]: r for r in rows}
    for i in range(1, 11):
        assert by_id[i]["val"] == f"primary_row_{i}", f"id={i}"


# ---------------------------------------------------------------------------
# secondary_tbl — Gap 3 target (FG_SECONDARY filegroup, file_id = 2)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_secondary_tbl_classify_supported(fixture_bak_ndf: Path) -> None:
    """secondary_tbl on FG_SECONDARY is supported when the NDF is in the image.

    A full database backup includes pages from all filegroups.  The NDF file
    (file_id = 2) is present in the backup image, so ``classify_table`` should
    *not* return a ``multi-file`` skip reason.
    """
    tables = _tables(fixture_bak_ndf)
    store = _store(fixture_bak_ndf)
    available = store.available_files
    result = classify_table(tables["secondary_tbl"], available)
    assert result.supported, (
        f"secondary_tbl skipped as {result.reason!r}; "
        f"available file ids: {sorted(available)}"
    )


@pytest.mark.fixture
def test_secondary_tbl_row_count(fixture_bak_ndf: Path) -> None:
    """secondary_tbl (FG_SECONDARY, file_id = 2) must return all 10 rows.

    This is the core Gap-3 assertion.  If 0 rows are returned the IAM
    chain reader is discarding pages whose file_id != 1.
    """
    rows = _rows(fixture_bak_ndf, "secondary_tbl")
    assert len(rows) == 10, (
        f"expected 10 rows from secondary filegroup, got {len(rows)} "
        "(Gap-3 bug: rows.py IAM reader may be ignoring file_id != 1)"
    )


@pytest.mark.fixture
def test_secondary_tbl_values(fixture_bak_ndf: Path) -> None:
    """secondary_tbl values decode correctly: val = 'secondary_row_<id>'."""
    rows = _rows(fixture_bak_ndf, "secondary_tbl")
    by_id = {r["id"]: r for r in rows}
    for i in range(1, 11):
        assert by_id[i]["val"] == f"secondary_row_{i}", f"id={i}"


@pytest.mark.fixture
def test_available_files_includes_secondary(fixture_bak_ndf: Path) -> None:
    """The backup image must contain pages for at least two data file IDs.

    SQL Server assigns file_id=1 to the MDF, file_id=2 to the log (.ldf), and
    file_id=3 (or higher) to each NDF.  ``available_files`` only lists file IDs
    that have data pages in the backup image (log pages are excluded), so the
    set is expected to be {1, 3} for a two-filegroup database.
    """
    store = _store(fixture_bak_ndf)
    assert 1 in store.available_files, "primary MDF (file_id=1) missing from image"
    secondary_ids = store.available_files - {1}
    assert secondary_ids, (
        f"no secondary data file found in backup image (available_files={store.available_files}) — "
        "was the backup created from a single-file DB by accident?"
    )
