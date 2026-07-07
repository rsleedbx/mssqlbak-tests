"""Coverage tests for ``mixed_collation_full.bak`` — per-column collation (Gap G-3).

The fixture contains one table (``collation_mix``) with three varchar columns,
each carrying a different collation:

    lat  VARCHAR(40) COLLATE Latin1_General_CI_AS      — CP1252
    grk  VARCHAR(40) COLLATE Greek_CI_AS               — CP1253
    heb  VARCHAR(40) COLLATE Hebrew_CI_AS              — CP1255

Three rows:
    id=1  ASCII-only   — 'hello' in every column (safe for any codec)
    id=2  non-ASCII    — code-page-specific characters in each column
    id=3  NULL row     — all three varchar columns are NULL

**Bugs fixed (G-3)**

Bug 1 — ``_AE_COLLATION_MAX`` false positive (``catalog.py``):
    Per-column CI collation IDs like 0xD007 (Greek) fell below the old threshold
    of 0x10000, causing them to be flagged as Always Encrypted and return None.
    Fixed: threshold lowered to 0x4000.

Bug 2 — codec computed but discarded (``types.py``):
    ``_dv_char`` computed the right codec via ``_codec_for_collation`` but then
    passed only ``utf8=(codec == "utf-8")``, meaning non-UTF-8 non-Latin1
    collations (Greek, Hebrew, …) were decoded as CP1252.
    Fixed: ``_decode_char`` now takes ``encoding: str``.

Generate the fixture::

    python -m tools.fixture_run mixed-collation
    python -m tools.fixture_run all-versions --suite mixed-collation
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import _AE_COLLATION_MAX, _STRING_TYPE_IDS, _is_ae_column, recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from mssqlbak.types import _COLLATION_UTF8_FLAG, _codec_for_collation, _decode_char
from tools.make_mixed_collation_fixture import (
    ASCII_ID,
    NONASCII_ID,
    NONASCII_VALUES,
    NULL_ID,
    TABLE_NAME,
)

# VARCHAR type_id used throughout AE boundary tests.
_VARCHAR = 167


# ---------------------------------------------------------------------------
# Boundary 1: _AE_COLLATION_MAX = 0x4000
#
# The threshold separates AE BIN2 collations (≤ ~0x2000, e.g. 0x808) from
# per-column CI_AS override IDs (≥ 0xD000, e.g. 0xD007 Greek).
# Any change to _AE_COLLATION_MAX will break these tests immediately.
# ---------------------------------------------------------------------------

class TestAeCollationBoundary:
    """Pin _AE_COLLATION_MAX = 0x4000 against known-good and known-bad values."""

    # --- values that MUST be flagged as AE (inside the threshold) ---

    @pytest.mark.parametrize("cid,label", [
        (0x001,  "minimum positive (id=1)"),
        (0x808,  "Latin1_General_BIN2 — documented AE example"),
        (_AE_COLLATION_MAX - 1, "one below threshold (0x3FFF)"),
    ])
    def test_is_ae_inside_threshold(self, cid: int, label: str) -> None:
        """collation_ids strictly inside [1, _AE_COLLATION_MAX) → AE."""
        assert _is_ae_column(_VARCHAR, cid), (
            f"Expected AE for {label} (0x{cid:X}); threshold=0x{_AE_COLLATION_MAX:X}"
        )

    # --- values that MUST NOT be flagged as AE (at or above threshold) ---

    @pytest.mark.parametrize("cid,label", [
        (0x000,   "zero — no collation / non-string column"),
        (_AE_COLLATION_MAX,     "at threshold (0x4000) — NOT AE"),
        (_AE_COLLATION_MAX + 1, "one above threshold (0x4001) — NOT AE"),
        (0xD007,  "Greek_CI_AS per-column override"),
        (0xD008,  "Latin1_General_CI_AS per-column override"),
        (0xD00C,  "Hebrew_CI_AS per-column override"),
        (0x4D188, "UTF-8 per-column override (SS2019+)"),
        (0x3400D008, "Latin1_General_CI_AS database-default (bits 31-16 non-zero)"),
    ])
    def test_not_ae_at_or_above_threshold(self, cid: int, label: str) -> None:
        """collation_ids at or above _AE_COLLATION_MAX → NOT AE."""
        assert not _is_ae_column(_VARCHAR, cid), (
            f"Incorrectly flagged as AE: {label} (0x{cid:X}); "
            f"threshold=0x{_AE_COLLATION_MAX:X}"
        )

    def test_non_string_type_never_ae(self) -> None:
        """INT (type_id=56) is never AE even with a small collation_id."""
        _INT = 56
        assert _INT not in _STRING_TYPE_IDS
        assert not _is_ae_column(_INT, 0x808), (
            "Non-string column should never be flagged as AE"
        )

    def test_threshold_value_is_0x4000(self) -> None:
        """Guard: the threshold constant itself must be exactly 0x4000 (16 384).

        If this test fails, the constant was changed without updating the
        boundary parametrize cases above.
        """
        assert _AE_COLLATION_MAX == 0x4000, (
            f"_AE_COLLATION_MAX changed to 0x{_AE_COLLATION_MAX:X}; "
            "update AE boundary tests to match"
        )


# ---------------------------------------------------------------------------
# Boundary 2: _COLLATION_UTF8_FLAG = 0x100 (bit 8)
#
# Bit 8 set → UTF-8 collation; codec lookup is bypassed entirely.
# Bit 8 clear → fall through to SORTID lookup (bits 7-0).
# ---------------------------------------------------------------------------

class TestUtf8FlagBoundary:
    """Pin bit 8 as the UTF-8 switch in _codec_for_collation."""

    @pytest.mark.parametrize("cid,expected,label", [
        # Bit 8 clear — SORTID path
        (0x0FF, "cp1252", "0x0FF — bit 8 clear, SORTID=0xFF unknown → fallback cp1252"),
        (0x007, "cp1253", "0x007 — bit 8 clear, SORTID=0x07 Greek"),
        (0x008, "cp1252", "0x008 — bit 8 clear, SORTID=0x08 Latin1"),
        (0x00C, "cp1255", "0x00C — bit 8 clear, SORTID=0x0C Hebrew"),
        # Bit 8 set — UTF-8 path (SORTID ignored)
        (0x100, "utf-8", "0x100 — bit 8 set, SORTID=0 → utf-8"),
        (0x101, "utf-8", "0x101 — bit 8 set, SORTID=1 (ignored) → utf-8"),
        (0x108, "utf-8", "0x108 — bit 8 set, SORTID=8 (would be cp1252 if clear) → utf-8"),
        (0x1FF, "utf-8", "0x1FF — bit 8 set, all SORTID bits set → utf-8"),
        # Real per-column IDs with sensitivity flags in bits 15-9 (must not affect SORTID)
        (0xD007, "cp1253", "0xD007 — Greek_CI_AS per-column, sensitivity flags masked"),
        (0xD008, "cp1252", "0xD008 — Latin1 per-column, sensitivity flags masked"),
        (0xD00C, "cp1255", "0xD00C — Hebrew per-column, sensitivity flags masked"),
        (0x4D188, "utf-8", "0x4D188 — UTF-8 per-column (0x4D188 & 0x100 = 0x100)"),
    ])
    def test_codec_for_collation(self, cid: int, expected: str, label: str) -> None:
        assert _codec_for_collation(cid) == expected, (
            f"{label}: got {_codec_for_collation(cid)!r}, expected {expected!r}"
        )

    def test_utf8_flag_value_is_0x100(self) -> None:
        """Guard: the UTF-8 flag constant must be bit 8 (0x100 = 256).

        If this test fails, the constant was changed without reviewing all
        callers of _codec_for_collation.
        """
        assert _COLLATION_UTF8_FLAG == 0x100, (
            f"_COLLATION_UTF8_FLAG changed to 0x{_COLLATION_UTF8_FLAG:X}"
        )

    def test_sortid_mask_isolates_bits_7_to_0(self) -> None:
        """_codec_for_collation isolates SORTID via & 0xFF — sensitivity flags in
        bits 15-9 must be transparent (changing them must not change the codec)."""
        # Greek SORTID = 0x07; add various sensitivity flag patterns and confirm
        # codec is always cp1253.
        for sens_flags in (0x00, 0x40, 0x80, 0xD0, 0xF0, 0xFE):
            cid = (sens_flags << 8) | 0x07  # bit 8 clear (no UTF-8)
            assert _codec_for_collation(cid) == "cp1253", (
                f"Sensitivity flags 0x{sens_flags:02X} changed codec "
                f"for SORTID=0x07: got {_codec_for_collation(cid)!r}"
            )


# ---------------------------------------------------------------------------
# Boundary 3: _decode_char encoding boundaries
#
# Each codec has a critical non-ASCII byte that distinguishes it from cp1252.
# Test the boundary byte for each supported non-default codec.
# ---------------------------------------------------------------------------

class TestDecodeCharEncodingBoundary:
    """Verify that _decode_char(raw, encoding=X) uses X, not cp1252."""

    def test_cp1253_greek_boundary_byte(self) -> None:
        """cp1253: 0xE5 → ε (Greek epsilon); 0xE5 in cp1252 → å (Latin)."""
        raw = bytes([0xE5])
        assert _decode_char(raw, encoding="cp1253") == "\u03b5"  # ε
        assert _decode_char(raw, encoding="cp1252") == "\u00e5"  # å — different

    def test_cp1255_hebrew_boundary_byte(self) -> None:
        """cp1255: 0xF9 → ש (shin); 0xF9 in cp1252 → ù (Latin)."""
        raw = bytes([0xF9])
        assert _decode_char(raw, encoding="cp1255") == "\u05e9"  # ש
        assert _decode_char(raw, encoding="cp1252") == "\u00f9"  # ù — different

    def test_cp1256_arabic_boundary_byte(self) -> None:
        """cp1256: 0xCE → خ (Arabic Kha); 0xCE in cp1252 → Î (Latin)."""
        raw = bytes([0xCE])
        assert _decode_char(raw, encoding="cp1256") == "\u062e"  # خ
        assert _decode_char(raw, encoding="cp1252") == "\u00ce"  # Î — different

    def test_cp1252_euro_sign(self) -> None:
        """cp1252: 0x80 → € (Euro); ISO-8859-1 leaves 0x80 undefined.

        This byte (0x80) is undefined in strict ISO-8859-1 / cp1252's five
        'holes' are at 0x81, 0x8D, 0x8F, 0x90, 0x9D — 0x80 IS defined as '€'.
        """
        assert _decode_char(bytes([0x80]), encoding="cp1252") == "\u20ac"  # €

    def test_cp1252_undefined_byte_replaced(self) -> None:
        """cp1252: 0x81 is undefined → '?' (SQL Server code-page substitution)."""
        result = _decode_char(bytes([0x81]), encoding="cp1252")
        assert result == "?"

    def test_utf8_two_byte_sequence(self) -> None:
        """UTF-8: 0xC3 0xA9 → é (U+00E9); same bytes in cp1252 → Ã©."""
        raw = bytes([0xC3, 0xA9])
        assert _decode_char(raw, encoding="utf-8") == "\u00e9"   # é
        assert _decode_char(raw, encoding="cp1252") == "\u00c3\u00a9"  # Ã© — different

    def test_default_encoding_is_cp1252(self) -> None:
        """_decode_char() with no encoding keyword defaults to cp1252."""
        # 0xE9 → é in cp1252; would be invalid start byte in UTF-8
        assert _decode_char(bytes([0xE9])) == "\u00e9"


# ---------------------------------------------------------------------------
# Regression: full Greek + Hebrew byte sequences (integration of boundaries 2+3)
# ---------------------------------------------------------------------------

def test_decode_char_greek() -> None:
    """Greek CP1253 bytes decode correctly when encoding='cp1253' is passed."""
    # ελλάδα in CP1253: ε=0xE5, λ=0xEB, λ=0xEB, ά=0xDC, δ=0xE4, α=0xE1
    raw = bytes([0xE5, 0xEB, 0xEB, 0xDC, 0xE4, 0xE1])
    result = _decode_char(raw, encoding="cp1253")
    assert result == "\u03b5\u03bb\u03bb\u03ac\u03b4\u03b1", (
        f"Greek decode failed: {result!r}"
    )


def test_decode_char_greek_corrupted_as_cp1252() -> None:
    """Same bytes decoded as CP1252 produce wrong characters (regression guard)."""
    raw = bytes([0xE5, 0xEB, 0xEB, 0xDC, 0xE4, 0xE1])
    result_wrong = _decode_char(raw, encoding="cp1252")
    # CP1252: 0xE5=å, 0xEB=ë, 0xEB=ë, 0xDC=Ü, 0xE4=ä, 0xE1=á
    assert result_wrong != "\u03b5\u03bb\u03bb\u03ac\u03b4\u03b1", (
        "Greek bytes should NOT decode as Greek via cp1252"
    )


def test_decode_char_hebrew() -> None:
    """Hebrew CP1255 bytes decode correctly when encoding='cp1255' is passed."""
    # שלום in CP1255: ש=0xF9, ל=0xEC, ו=0xE5, ם=0xED
    raw = bytes([0xF9, 0xEC, 0xE5, 0xED])
    result = _decode_char(raw, encoding="cp1255")
    assert result == "\u05e9\u05dc\u05d5\u05dd", (
        f"Hebrew decode failed: {result!r}"
    )


# ---------------------------------------------------------------------------
# Fixture-level tests (require generated mixed_collation_full.bak)
# ---------------------------------------------------------------------------

def _read_rows(fixture: Path) -> dict[int, dict[str, Any]]:
    """Return {id: row_dict} for all rows in collation_mix."""
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    tbl = next((t for t in schema.tables if t.name == TABLE_NAME), None)
    if tbl is None:
        pytest.fail(f"Table {TABLE_NAME!r} not found in {fixture.name}")
    return {row["id"]: row for row in read_table_rows(store, tbl)}


@pytest.mark.fixture
def test_table_present(fixture_bak_mixed_collation: Path) -> None:
    """Fixture opens without error and contains collation_mix."""
    store = PageStore.from_bak(fixture_bak_mixed_collation)
    schema = recover_schema(store)
    names = {t.name for t in schema.tables}
    assert TABLE_NAME in names, f"{TABLE_NAME!r} not found; available: {sorted(names)}"


@pytest.mark.fixture
def test_row_count(fixture_bak_mixed_collation: Path) -> None:
    """Table has exactly 3 rows."""
    rows = _read_rows(fixture_bak_mixed_collation)
    assert len(rows) == 3, f"expected 3 rows, got {len(rows)}"


@pytest.mark.fixture
def test_ascii_row(fixture_bak_mixed_collation: Path) -> None:
    """ASCII row (id=1): all three columns decode as 'hello'."""
    rows = _read_rows(fixture_bak_mixed_collation)
    assert ASCII_ID in rows, f"ASCII row (id={ASCII_ID}) not found"
    row = rows[ASCII_ID]
    for col in ("lat", "grk", "heb"):
        assert row.get(col) == "hello", (
            f"ASCII row {col}: expected 'hello', got {row.get(col)!r}"
        )


@pytest.mark.fixture
def test_null_row(fixture_bak_mixed_collation: Path) -> None:
    """NULL row (id=3): all three varchar columns are None."""
    rows = _read_rows(fixture_bak_mixed_collation)
    assert NULL_ID in rows, f"NULL row (id={NULL_ID}) not found"
    row = rows[NULL_ID]
    for col in ("lat", "grk", "heb"):
        assert row.get(col) is None, (
            f"NULL row {col}: expected None, got {row.get(col)!r}"
        )


@pytest.mark.fixture
@pytest.mark.parametrize("col,expected", list(NONASCII_VALUES.items()))
def test_nonascii_row(fixture_bak_mixed_collation: Path, col: str, expected: str) -> None:
    """Non-ASCII row (id=2): each column decodes using its own collation codec.

    This is the key G-3 regression test.  Before the fix, Greek bytes were
    decoded as CP1252 (producing å, ë, Ü, etc.) instead of Greek characters.
    """
    rows = _read_rows(fixture_bak_mixed_collation)
    assert NONASCII_ID in rows, f"non-ASCII row (id={NONASCII_ID}) not found"
    actual = rows[NONASCII_ID].get(col)
    assert actual == expected, (
        f"Column '{col}': decoded as {actual!r}, expected {expected!r}\n"
        f"  (hex of expected: {expected.encode('utf-8').hex()})"
    )
