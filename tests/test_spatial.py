"""Spatial (geometry/geography) decoder, exercised on real on-disk byte blobs.

The hex blobs below are ``CAST(<value> AS varbinary(max))`` captured from a live
SQL Server (the exact bytes stored on disk); the expected text is the matching
``.STAsText()`` output. Keeping them here pins the format without a live engine.
"""
from __future__ import annotations

import pytest

from mssqlbak.spatial import decode_spatial

GEOMETRY = [
    ("point", "00000000010c00000000000008400000000000001040", "POINT (3 4)"),
    ("empty", "000000000104000000000000000001000000ffffffffffffffff01", "POINT EMPTY"),
    (
        "line",
        "0000000001040300000000000000000000000000000000000000000000000000f03f0000"
        "00000000f03f0000000000000040000000000000104001000000010000000001000000ff"
        "ffffff0000000002",
        "LINESTRING (0 0, 1 1, 2 4)",
    ),
    (
        "poly",
        "00000000010405000000000000000000000000000000000000000000000000001040000000"
        "0000000000000000000000104000000000000010400000000000000000000000000000104000"
        "00000000000000000000000000000001000000020000000001000000ffffffff0000000003",
        "POLYGON ((0 0, 4 0, 4 4, 0 4, 0 0))",
    ),
    (
        "polyhole",
        "0000000001040a00000000000000000000000000000000000000000000000000244000000000000000"
        "000000000000002440000000000000244000000000000000000000000000002440000000000000000000"
        "000000000000000000000000000040000000000000004000000000000000400000000000001040000000"
        "0000001040000000000000104000000000000010400000000000000040000000000000004000000000000"
        "00040020000000200000000000500000001000000ffffffff0000000003",
        "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0), (2 2, 2 4, 4 4, 4 2, 2 2))",
    ),
    (
        "mpoint",
        "00000000010402000000000000000000f03f00000000000000400000000000000840000000000000"
        "1040020000000100000000010100000003000000ffffffff0000000004000000000000000001000000000100000001",
        "MULTIPOINT ((1 2), (3 4))",
    ),
    (
        "mline",
        "0000000001040400000000000000000000000000000000000000000000000000f03f000000000000f03f"
        "00000000000000400000000000000040000000000000084000000000000008400200000001000000000102"
        "00000003000000ffffffff0000000005000000000000000002000000000100000002",
        "MULTILINESTRING ((0 0, 1 1), (2 2, 3 3))",
    ),
    (
        "mpoly",
        "0000000001040800000000000000000000000000000000000000000000000000f03f0000000000000000000000"
        "000000f03f000000000000f03f0000000000000000000000000000000000000000000024400000000000002440"
        "000000000000284000000000000024400000000000002840000000000000284000000000000024400000000000"
        "002440020000000200000000020400000003000000ffffffff0000000006000000000000000003000000000100000003",
        "MULTIPOLYGON (((0 0, 1 0, 1 1, 0 0)), ((10 10, 12 10, 12 12, 10 10)))",
    ),
    (
        "gc",
        "00000000010403000000000000000000f03f000000000000f03f00000000000000400000000000000040000000000000"
        "08400000000000000840020000000100000000010100000003000000ffffffff0000000007000000000000000001000000000100000002",
        "GEOMETRYCOLLECTION (POINT (1 1), LINESTRING (2 2, 3 3))",
    ),
]

GEOGRAPHY = [
    ("point", "e6100000010ccdcccccccccc47403333333333935ec0", "POINT (-122.3 47.6)"),
    (
        "line",
        "e6100000011400000000008047400000000000805ec000000000000047400000000000405ec0",
        "LINESTRING (-122 47, -121 46)",
    ),
    (
        "poly",
        "e610000001040500000000000000008047400000000000805ec000000000008047400000000000405ec0000000"
        "00000048400000000000405ec000000000000048400000000000805ec000000000008047400000000000805ec0"
        "01000000020000000001000000ffffffff0000000003",
        "POLYGON ((-122 47, -121 47, -121 48, -122 48, -122 47))",
    ),
    (
        "mpoint",
        "e610000001040200000000000000008047400000000000805ec000000000000047400000000000405ec00200000001"
        "00000000010100000003000000ffffffff0000000004000000000000000001000000000100000001",
        "MULTIPOINT ((-122 47), (-121 46))",
    ),
]


@pytest.mark.parametrize("name,blob,expected", GEOMETRY, ids=[c[0] for c in GEOMETRY])
def test_decode_geometry(name: str, blob: str, expected: str) -> None:
    assert decode_spatial(bytes.fromhex(blob), geography=False) == expected


@pytest.mark.parametrize("name,blob,expected", GEOGRAPHY, ids=[c[0] for c in GEOGRAPHY])
def test_decode_geography(name: str, blob: str, expected: str) -> None:
    assert decode_spatial(bytes.fromhex(blob), geography=True) == expected


def test_z_coordinate_emitted() -> None:
    """Z ordinate is included in the WKT output when HasZ is set.

    Blob: POINT Z (3 4 10) — single-point shortcut with HasZ.
    The Z value stored in the blob is 10.0 (0x4024000000000000 LE).
    """
    blob = "00000000010900000000000008400000000000001040" + "0000000000002440"
    assert decode_spatial(bytes.fromhex(blob), geography=False) == "POINT (3 4 10)"


def test_z_coordinates_multipoint_linestring() -> None:
    """Z values are stored as a separate array after all XY pairs (not interleaved).

    Blob built to match geometry::Parse('LINESTRING (0 0 1, 1 1 2, 2 4 3)').
    HasZ=True, 3 points.  XY pairs stored first (stride 16), then Z array.
    Layout: x0 y0 x1 y1 x2 y2 [z0 z1 z2] figures shapes
    """
    # Verified hex built via struct (matches SQL Server geometry::Parse output)
    blob = "0000000001050300000000000000000000000000000000000000000000000000F03F000000000000F03F00000000000000400000000000001040000000000000F03F0000000000000040000000000000084001000000010000000001000000FFFFFFFF0000000002"
    assert decode_spatial(bytes.fromhex(blob), geography=False) == "LINESTRING (0 0 1, 1 1 2, 2 4 3)"


def test_zm_coordinates_decode() -> None:
    """POINT ZM: both Z and M ordinates appear in the WKT output."""
    # Blob for POINT (3 4 5 6): SinglePoint, HasZ, HasM
    # Built from geometry::Parse('POINT (3 4 5 6)') via SQL Server
    blob = "00000000010F0000000000000840000000000000104000000000000014400000000000001840"
    result = decode_spatial(bytes.fromhex(blob), geography=False)
    assert result == "POINT (3 4 5 6)"


def test_fullglobe_decode() -> None:
    """geography FullGlobe (shape_type=11) decodes to the literal 'FULLGLOBE'."""
    blob = "E61000000224000000000000000001000000FFFFFFFFFFFFFFFF0B"
    assert decode_spatial(bytes.fromhex(blob), geography=True) == "FULLGLOBE"


def test_circularstring_decode() -> None:
    """CircularString (version-2, shape_type=8) decodes correctly."""
    blob = "0000000002040300000000000000000000000000000000000000000000000000F03F000000000000F03F0000000000000040000000000000000001000000020000000001000000FFFFFFFF0000000008"
    assert decode_spatial(bytes.fromhex(blob), geography=False) == "CIRCULARSTRING (0 0, 1 1, 2 0)"


def test_compoundcurve_decode() -> None:
    """CompoundCurve (version-2, shape_type=9) with arc + line segments.

    Blob built to match geometry::Parse('COMPOUNDCURVE (CIRCULARSTRING (0 0, 1 1, 2 0), (2 0, 3 0))')
    """
    blob = "0000000002040400000000000000000000000000000000000000000000000000F03F000000000000F03F000000000000004000000000000000000000000000000840000000000000000001000000030000000001000000FFFFFFFF0000000009020000000302"
    assert (
        decode_spatial(bytes.fromhex(blob), geography=False)
        == "COMPOUNDCURVE (CIRCULARSTRING (0 0, 1 1, 2 0), (2 0, 3 0))"
    )


def test_curvepolygon_decode() -> None:
    """CurvePolygon (version-2, shape_type=10) with a circular ring."""
    blob = "00000000020405000000000000000000000000000000000000000000000000000040000000000000004000000000000010400000000000000000000000000000004000000000000000C00000000000000000000000000000000001000000020000000001000000FFFFFFFF000000000A"
    assert (
        decode_spatial(bytes.fromhex(blob), geography=False)
        == "CURVEPOLYGON (CIRCULARSTRING (0 0, 2 2, 4 0, 2 -2, 0 0))"
    )


def test_null_spatial_returns_none() -> None:
    """Zero-length spatial blob decodes to ``None`` (SQL NULL semantics)."""
    assert decode_spatial(b"", geography=False) is None
    assert decode_spatial(b"", geography=True) is None
