"""ROW-compressed nvarchar SCSU vs UTF-16LE regression tests.

``compressed_nvarchar_full.bak`` — a single ROW-compressed table whose
``nvarchar(200)`` column contains:

  - ASCII strings  (stored as SCSU, odd byte length)
  - Cyrillic text  (stored as SCSU with a Cyrillic window-select prefix)
  - Greek text     (stored as SCSU with a Greek window-select prefix)
  - CJK ideographs (stored as UTF-16LE; SCSU would cost more bytes)
  - Mixed ASCII+Cyrillic (SCSU with a window switch mid-value)
  - NULL
  - Long ASCII     (SCSU with trailing SC0 0x10 to make length odd)

Regression for the rows.py / page_decode.rs ``_is_utf16le_not_scsu`` heuristic
(commit 57e9219): a broken heuristic would silently decode every SCSU-encoded
value as UTF-16LE (garbled text) or vice versa (garbled or exception), with no
row-count or null-count signal to alert the caller.

Fixture generation::

    python -m tools.fixture_run compressed-nvarchar
    python -m tools.fixture_run all-versions --suite compressed-nvarchar
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_compressed_nvarchar_fixture import EXPECTED, ROW_COUNT, TABLE


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _rows(path: Path) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == TABLE)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# Row count
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_compressed_nvarchar_row_count(fixture_bak_compressed_nvarchar: Path) -> None:
    """Extraction must return exactly ROW_COUNT rows."""
    rows = _rows(fixture_bak_compressed_nvarchar)
    assert len(rows) == ROW_COUNT, (
        f"expected {ROW_COUNT} rows, got {len(rows)} "
        "(wrong count hints at a decoder crash or skipped rows)"
    )


# ---------------------------------------------------------------------------
# Per-row value assertions
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_compressed_nvarchar_values(fixture_bak_compressed_nvarchar: Path) -> None:
    """Every nvarchar(200) value must decode to exactly the expected Python string.

    Exercises both branches of ``_is_utf16le_not_scsu``:
      - SCSU path  : ASCII (id=1,7), Cyrillic (id=2), Greek (id=4), mixed (id=5)
      - UTF-16LE path: CJK (id=3,8)
      - NULL path   : id=6

    A wrong decode (SCSU bytes decoded as UTF-16LE or vice versa) produces a
    garbled string that fails the equality check but leaves row and null counts
    unchanged — making this the only test that would catch the regression.
    """
    rows = _rows(fixture_bak_compressed_nvarchar)
    by_id = {r["id"]: r for r in rows}
    bad: list[tuple[int, str | None, str | None]] = []
    for row_id, expected in EXPECTED.items():
        row = by_id.get(row_id)
        if row is None:
            bad.append((row_id, expected, "<row missing>"))
            continue
        actual = row.get("val")
        if actual != expected:
            bad.append((row_id, expected, actual))
    assert not bad, (
        f"{len(bad)} row(s) decoded incorrectly:\n"
        + "\n".join(
            f"  id={rid}: expected={expected!r}, got={actual!r}"
            for rid, expected, actual in bad
        )
    )


@pytest.mark.fixture
def test_compressed_nvarchar_no_garbled_nones(fixture_bak_compressed_nvarchar: Path) -> None:
    """Non-null expected values must not decode to None.

    A None result is the hallmark of a decoder failure (odd byte count after a
    wrong SCSU/UTF-16LE choice, or an unhandled SCSU escape sequence).  This
    check is deliberately separate from the equality assertion above so the
    failure message names the exact encoding path that broke.
    """
    rows = _rows(fixture_bak_compressed_nvarchar)
    by_id = {r["id"]: r for r in rows}
    spurious_nones = [
        row_id
        for row_id, expected in EXPECTED.items()
        if expected is not None and by_id.get(row_id, {}).get("val") is None
    ]
    assert not spurious_nones, (
        f"Rows decoded as None (should be non-null): ids={spurious_nones}\n"
        "This indicates a SCSU/UTF-16LE decode path chose the wrong decoder."
    )
