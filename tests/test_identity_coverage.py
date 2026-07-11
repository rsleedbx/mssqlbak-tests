"""Identity column decode coverage — all six SQL Server IDENTITY-capable types.

Verifies that ``_decode_idtval`` (via ``recover_schema``) correctly populates
``Column.identity_seed`` and ``Column.identity_increment`` for every xtype that
SQL Server allows with the ``IDENTITY`` property:

  - tinyint  (xtype  48) — 1-byte integer path
  - smallint (xtype  52) — 2-byte integer path
  - int      (xtype  56) — 4-byte integer path
  - bigint   (xtype 127) — 8-byte integer path
  - decimal(9,0) (xtype 106) — sign+magnitude path (4-byte magnitude)
  - numeric(9,0) (xtype 108) — sign+magnitude path (4-byte magnitude, alias)

Integer types assert exact values (seed=1, increment=1).
Decimal / numeric start with not-None guards; once the ``idtval`` sign+magnitude
format is confirmed via the diagnostic step in the plan, upgrade these to exact
equality (``== 1``).

Fixture: ``identity_coverage_full.bak``
Build:   python -m tools.fixture_run all-versions --suite identity-coverage
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from tools.make_identity_coverage_fixture import (
    ALL_TABLES,
    BIGINT_TABLE,
    DECIMAL_TABLE,
    INT_TABLE,
    NUMERIC_TABLE,
    ROW_COUNT,
    SMALLINT_TABLE,
    TINYINT_TABLE,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _schema(fixture: Path) -> dict[str, Any]:
    """Return {table_name: Table} for the fixture database."""
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    return {t.name: t for t in schema.tables}


def _id_col(fixture: Path, table_name: str) -> Any:
    """Return the Column object for the ``id`` identity column of *table_name*."""
    tables = _schema(fixture)
    tbl = tables.get(table_name)
    if tbl is None:
        pytest.fail(f"Table {table_name!r} not found in fixture")
    col = next((c for c in tbl.columns if c.name == "id"), None)
    if col is None:
        pytest.fail(f"Column 'id' not found in table {table_name!r}")
    return col


# ---------------------------------------------------------------------------
# integer types — exact seed and increment assertions
# ---------------------------------------------------------------------------

def test_identity_tinyint_seed_increment(fixture_bak_identity_coverage: Path) -> None:
    """tinyint IDENTITY(1,1): seed and increment must both be 1."""
    col = _id_col(fixture_bak_identity_coverage, TINYINT_TABLE)
    assert col.identity_seed == 1, f"tinyint seed: expected 1, got {col.identity_seed!r}"
    assert col.identity_increment == 1, f"tinyint increment: expected 1, got {col.identity_increment!r}"


def test_identity_smallint_seed_increment(fixture_bak_identity_coverage: Path) -> None:
    """smallint IDENTITY(1,1): seed and increment must both be 1."""
    col = _id_col(fixture_bak_identity_coverage, SMALLINT_TABLE)
    assert col.identity_seed == 1, f"smallint seed: expected 1, got {col.identity_seed!r}"
    assert col.identity_increment == 1, f"smallint increment: expected 1, got {col.identity_increment!r}"


def test_identity_int_seed_increment(fixture_bak_identity_coverage: Path) -> None:
    """int IDENTITY(1,1): seed and increment must both be 1."""
    col = _id_col(fixture_bak_identity_coverage, INT_TABLE)
    assert col.identity_seed == 1, f"int seed: expected 1, got {col.identity_seed!r}"
    assert col.identity_increment == 1, f"int increment: expected 1, got {col.identity_increment!r}"


def test_identity_bigint_seed_increment(fixture_bak_identity_coverage: Path) -> None:
    """bigint IDENTITY(1,1): seed and increment must both be 1."""
    col = _id_col(fixture_bak_identity_coverage, BIGINT_TABLE)
    assert col.identity_seed == 1, f"bigint seed: expected 1, got {col.identity_seed!r}"
    assert col.identity_increment == 1, f"bigint increment: expected 1, got {col.identity_increment!r}"


# ---------------------------------------------------------------------------
# decimal / numeric — not-None guards (upgrade to == 1 after format confirmed)
# ---------------------------------------------------------------------------

def test_identity_decimal_seed_not_none(fixture_bak_identity_coverage: Path) -> None:
    """decimal(9,0) IDENTITY: seed must be decoded (not None)."""
    col = _id_col(fixture_bak_identity_coverage, DECIMAL_TABLE)
    assert col.identity_seed is not None, (
        "decimal identity_seed is None — wrong xtype key or idtval format mismatch"
    )


def test_identity_decimal_increment_not_none(fixture_bak_identity_coverage: Path) -> None:
    """decimal(9,0) IDENTITY: increment must be decoded (not None)."""
    col = _id_col(fixture_bak_identity_coverage, DECIMAL_TABLE)
    assert col.identity_increment is not None, (
        "decimal identity_increment is None — wrong xtype key or idtval format mismatch"
    )


def test_identity_numeric_seed_not_none(fixture_bak_identity_coverage: Path) -> None:
    """numeric(9,0) IDENTITY: seed must be decoded (not None)."""
    col = _id_col(fixture_bak_identity_coverage, NUMERIC_TABLE)
    assert col.identity_seed is not None, (
        "numeric identity_seed is None — wrong xtype key or idtval format mismatch"
    )


def test_identity_numeric_increment_not_none(fixture_bak_identity_coverage: Path) -> None:
    """numeric(9,0) IDENTITY: increment must be decoded (not None)."""
    col = _id_col(fixture_bak_identity_coverage, NUMERIC_TABLE)
    assert col.identity_increment is not None, (
        "numeric identity_increment is None — wrong xtype key or idtval format mismatch"
    )


# ---------------------------------------------------------------------------
# row counts for all six tables
# ---------------------------------------------------------------------------

def test_identity_row_counts(fixture_bak_identity_coverage: Path) -> None:
    """Every identity table must contain exactly ROW_COUNT rows."""
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(fixture_bak_identity_coverage)
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}

    wrong: list[tuple[str, int]] = []
    for name in ALL_TABLES:
        tbl = tables.get(name)
        if tbl is None:
            pytest.fail(f"Table {name!r} not found in fixture")
        rows = list(read_table_rows(store, tbl))
        if len(rows) != ROW_COUNT:
            wrong.append((name, len(rows)))

    assert not wrong, (
        f"Row count mismatch (expected {ROW_COUNT}): "
        + ", ".join(f"{n}={c}" for n, c in wrong)
    )
