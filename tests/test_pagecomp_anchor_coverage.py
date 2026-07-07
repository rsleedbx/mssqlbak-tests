"""Coverage test for the PAGE-compression CI anchor/dictionary decode fixture.

The ``pagecomp_anchor`` fixture is a clustered, PAGE-compressed table whose
non-key columns each hold a single constant value across every row.  SQL Server
stores that constant once in the per-page **anchor record** inside the
Compression-Info (CI) structure and marks each row column with the ``_CD_ZERO``
indicator.  This is the exact shape used by real-world temporal history tables
(WideWorldImporters ``*_Archive``) and the layout that exposed the
``CI_HAS_ANCHOR_RECORD``-only (``0x02``) CI variant the parser previously
rejected.

Every constant column is a known sentinel, so a correct round-trip means
``min == max == sentinel`` for each one and ``geo`` is non-null for all rows.
A regression in the CI anchor decode would surface as ``0`` / ``0001-01-01`` /
empty values (the pre-fix symptom).
"""
from __future__ import annotations

import datetime as _dt
from decimal import Decimal
from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import _data_pages, read_table_rows  # type: ignore[attr-defined]
from tools.make_pagecomp_anchor_fixture import (
    AMOUNT,
    EDITOR,
    LABEL,
    QTY,
    ROW_COUNT,
    TS,
    TS2,
)

pytestmark = pytest.mark.fixture

TABLE = "pagecomp_anchor"


def _expected_ts() -> _dt.datetime:
    return _dt.datetime.fromisoformat(TS)


def _expected_ts2() -> _dt.datetime:
    return _dt.datetime.fromisoformat(TS2)


def _rows(bak: Path) -> tuple[list[dict], object]:
    store = PageStore.from_bak(str(bak))
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == TABLE)
    return list(read_table_rows(store, tbl, schema.obj_to_name)), (store, tbl)


def test_fixture_uses_anchor_only_ci(fixture_bak_pagecomp_anchor: Path) -> None:
    """The fixture must actually exercise the 0x02 (anchor, no dictionary) CI;
    otherwise the regression guard below would pass trivially on a plain page."""
    store = PageStore.from_bak(str(fixture_bak_pagecomp_anchor))
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == TABLE)
    ci_bytes = {store.page(pid, fid).raw[96] for pid, fid in _data_pages(store, tbl)}
    assert 0x02 in ci_bytes, f"expected an anchor-only (0x02) CI page, saw {ci_bytes!r}"


def test_row_count(fixture_bak_pagecomp_anchor: Path) -> None:
    rows, _ = _rows(fixture_bak_pagecomp_anchor)
    assert len(rows) == ROW_COUNT


def test_id_is_dense_running_key(fixture_bak_pagecomp_anchor: Path) -> None:
    rows, _ = _rows(fixture_bak_pagecomp_anchor)
    ids = sorted(r["id"] for r in rows)
    assert ids == list(range(1, ROW_COUNT + 1))


def test_constant_columns_decode_to_anchor_value(
    fixture_bak_pagecomp_anchor: Path,
) -> None:
    """Each constant column collapses into the CI anchor (stored _CD_ZERO per
    row); every row must decode back to the exact sentinel — no 0 / 0001-01-01."""
    rows, _ = _rows(fixture_bak_pagecomp_anchor)
    expected = {
        "editor": EDITOR,
        "ts": _expected_ts(),
        "ts2": _expected_ts2(),
        "amount": Decimal(AMOUNT),
        "qty": QTY,
        "label": LABEL,
    }
    for col, want in expected.items():
        vals = {r[col] for r in rows}
        assert vals == {want}, f"{col}: expected all == {want!r}, got {sorted(vals)[:5]!r}…"
        assert all(r[col] is not None for r in rows), f"{col} has unexpected NULLs"


def test_geography_anchor_is_non_null(fixture_bak_pagecomp_anchor: Path) -> None:
    """The geography column is a constant off-row LOB stored in the anchor; it
    must be non-null for every row (the pre-fix bug nulled it)."""
    rows, _ = _rows(fixture_bak_pagecomp_anchor)
    assert all(r["geo"] is not None for r in rows)
    # All rows share the one constant geography value stored in the anchor.
    assert len({repr(r["geo"]) for r in rows}) == 1
