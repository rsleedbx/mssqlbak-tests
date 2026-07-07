"""Level-1 UTF-8 collation coverage tests (Gap G-1).

``utf8_collation_full.bak`` — a table with a ``VARCHAR(80) COLLATE
Latin1_General_100_CI_AS_SC_UTF8`` column, storing UTF-8 bytes on the page
instead of a single-byte code page.

Gap G-1 context: a ``varchar`` decoder that applies the database collation's
code page (CP1252) to all varchar bytes will produce mojibake for any
non-ASCII UTF-8 content — silently corrupting strings.  UTF-8 collations are
common in modern databases and are the only supported collation for per-column
UTF-8 storage in SQL Server 2019+.

Schema:
    dbo.utf8_tbl  — VARCHAR(80) COLLATE Latin1_General_100_CI_AS_SC_UTF8
    dbo.nvar_tbl  — NVARCHAR(80) with default collation (always correct)

Data (same rows in both tables; id range 1 .. ROW_COUNT):
    1 → 'hello'       (ASCII only; sanity check)
    2 → 'café'        (é = U+00E9; 2 UTF-8 bytes)
    3 → '日本語'       (3 CJK chars × 3 UTF-8 bytes each)
    4 → '😀'          (emoji U+1F600; 4 UTF-8 bytes / surrogate pair in UTF-16)
    5 → 'price: €100' (€ = U+20AC; 3 UTF-8 bytes)
    6 → ''            (empty string)
    7 → NULL

Fixture generation::

    python -m tools.fixture_run all-versions --suite utf8-collation \\
        --version 2019 --version 2022 --version 2025
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_utf8_collation_fixture import EXPECTED, ROW_COUNT


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _rows(path: Path, table: str) -> dict[int, str | None]:
    """Return {id: s} for every row in *table*."""
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return {r["id"]: r.get("s") for r in read_table_rows(store, tbl, schema.obj_to_name)}


# ---------------------------------------------------------------------------
# Row count
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_row_count(fixture_bak_utf8_collation: Path) -> None:
    """utf8_tbl must return exactly ROW_COUNT rows."""
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert len(rows) == ROW_COUNT, (
        f"expected {ROW_COUNT} rows, got {len(rows)}"
    )


# ---------------------------------------------------------------------------
# NULL handling
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_null_row(fixture_bak_utf8_collation: Path) -> None:
    """Row id=7 was inserted as NULL and must decode as None."""
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert rows[7] is None, f"id=7: expected None, got {rows[7]!r}"


# ---------------------------------------------------------------------------
# ASCII sanity check (id=1 and id=6)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_ascii_hello(fixture_bak_utf8_collation: Path) -> None:
    """Row id=1 ('hello') must round-trip correctly (ASCII baseline)."""
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert rows[1] == EXPECTED[1], (
        f"id=1: expected {EXPECTED[1]!r}, got {rows[1]!r}"
    )


@pytest.mark.fixture
def test_utf8_empty_string(fixture_bak_utf8_collation: Path) -> None:
    """Row id=6 (empty string) must round-trip as an empty string, not None."""
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert rows[6] == EXPECTED[6], (
        f"id=6: expected {EXPECTED[6]!r}, got {rows[6]!r}"
    )


# ---------------------------------------------------------------------------
# Latin extended (id=2: café, é = 2-byte UTF-8)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_cafe(fixture_bak_utf8_collation: Path) -> None:
    """Row id=2 ('café') must decode with the accented é, not as mojibake.

    CP1252 would decode the UTF-8 bytes C3 A9 as 'Ã©' instead of 'é'.
    """
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert rows[2] == EXPECTED[2], (
        f"id=2: expected {EXPECTED[2]!r}, got {rows[2]!r} "
        f"(CP1252 mojibake would be 'cafÃ©')"
    )


# ---------------------------------------------------------------------------
# CJK (id=3: 日本語, 3-byte per char)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_cjk(fixture_bak_utf8_collation: Path) -> None:
    """Row id=3 ('日本語') must decode as three CJK ideographs.

    CP1252 would produce 9 garbage bytes; a UTF-8 decoder that applies
    the wrong code-page produces garbled output.
    """
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert rows[3] == EXPECTED[3], (
        f"id=3: expected {EXPECTED[3]!r}, got {rows[3]!r}"
    )


# ---------------------------------------------------------------------------
# Emoji (id=4: 😀, 4-byte UTF-8 / surrogate pair in UTF-16)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_emoji(fixture_bak_utf8_collation: Path) -> None:
    """Row id=4 ('😀') must decode as a single emoji code point.

    The UTF-8 encoding is 4 bytes (F0 9F 98 80).  A decoder that treats
    each byte as a CP1252 character produces 4 garbage characters.
    """
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert rows[4] == EXPECTED[4], (
        f"id=4: expected {EXPECTED[4]!r}, got {rows[4]!r}"
    )


# ---------------------------------------------------------------------------
# 3-byte BMP symbol (id=5: price: €100, € = U+20AC)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_euro(fixture_bak_utf8_collation: Path) -> None:
    """Row id=5 ('price: €100') must decode with the Euro sign (U+20AC).

    The Euro sign is E2 82 AC in UTF-8 (3 bytes).  CP1252 maps 0x80 → €
    but the bytes E2 82 AC in CP1252 decode as 'â€¦' (garbled).
    """
    rows = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    assert rows[5] == EXPECTED[5], (
        f"id=5: expected {EXPECTED[5]!r}, got {rows[5]!r}"
    )


# ---------------------------------------------------------------------------
# Cross-check: utf8_tbl vs nvar_tbl
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_matches_nvarchar_control(fixture_bak_utf8_collation: Path) -> None:
    """utf8_tbl values must match nvar_tbl (the always-correct UTF-16 control).

    This is the definitive cross-check: if the UTF-8 varchar decoder is
    correct, every non-NULL row in utf8_tbl must equal the corresponding
    row in nvar_tbl.
    """
    utf8 = _rows(fixture_bak_utf8_collation, "utf8_tbl")
    nvar = _rows(fixture_bak_utf8_collation, "nvar_tbl")

    mismatches = [
        (id_, utf8.get(id_), nvar.get(id_))
        for id_ in sorted(set(utf8) | set(nvar))
        if utf8.get(id_) != nvar.get(id_)
    ]
    assert not mismatches, (
        f"utf8_tbl vs nvar_tbl mismatch for {len(mismatches)} rows: "
        f"{mismatches[:3]}"
    )
