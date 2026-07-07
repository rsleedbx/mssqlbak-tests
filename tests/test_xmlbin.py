"""Binary-XML token decoder, exercised against real on-disk byte sequences.

The hex blobs below were captured from the committed fixture's ``t_xml`` table
(SQL Server's on-disk tokenised form).  Keeping them here pins the grammar
without needing the fixture or a live engine.
"""
from __future__ import annotations

import pytest

from mssqlbak.xmlbin import decode_xml

CASES = [
    ("simple", "dfff01b004f0016100ef000001f80111013100f7", "<a>1</a>"),
    (
        "attrs",
        "dfff01b004f00472006f006f007400ef000001f801f00269006400ef000002"
        "f60211013700f5f0017800ef000003f803110268006900f7f0017900ef000004"
        "f8041103740077006f00f7f7",
        '<root id="7"><x>hi</x><y>two</y></root>',
    ),
    ("empty", "dfff01b004f0016500ef000001f801f7", "<e/>"),
    (
        "repeat",
        "dfff01b004f0017200ef000001f801f0017800ef000002f80211013100f7f80211013200f7f7",
        "<r><x>1</x><x>2</x></r>",
    ),
    (
        "escape",
        "dfff01b004f0017400ef000001f8011109610020003c00200062002000260020006300f7",
        "<t>a &lt; b &amp; c</t>",
    ),
    (
        "attresc",
        "dfff01b004f0016100ef000001f801f0017000ef000002f6021103780022007900f5f7",
        '<a p="x&quot;y"/>',
    ),
    (
        "cdata",
        "dfff01b004f00364006f006300ef000001f801110361003c006200f7",
        "<doc>a&lt;b</doc>",
    ),
]


@pytest.mark.parametrize("name,blob,expected", CASES, ids=[c[0] for c in CASES])
def test_decode_xml(name: str, blob: str, expected: str) -> None:
    assert decode_xml(bytes.fromhex(blob)) == expected


def test_varint_length_long_text() -> None:
    # 300-char text node: length is LEB128-encoded as ``ac 02`` (44 + 256).
    blob = bytes.fromhex("dfff01b004f0016200ef000001f80111ac02") + ("x".encode("utf-16-le") * 300) + b"\xf7"
    assert decode_xml(blob) == "<b>" + "x" * 300 + "</b>"


def test_unknown_token_raises() -> None:
    with pytest.raises(NotImplementedError):
        decode_xml(bytes.fromhex("dfff01b004aa"))


def test_bad_header_raises() -> None:
    with pytest.raises(NotImplementedError):
        decode_xml(bytes.fromhex("0001020304f7"))


def test_unsupported_version_raises() -> None:
    """A binary-XML blob whose version byte is not 0x01/0x02 raises NotImplementedError.

    Header layout: [signature 2B][version 1B][encoding 2B].
    Valid signatures = 0xDFFF, valid encoding = 0xB004 (UTF-16LE).
    Only version 0x01 and 0x02 are understood; 0x03+ triggers the error.
    """
    # signature(0xDFFF) + version=0x03 + encoding(0xB004)
    bad_version = bytes.fromhex("dfff") + bytes([0x03]) + bytes.fromhex("b004")
    with pytest.raises(NotImplementedError, match="unsupported binary-XML version"):
        decode_xml(bad_version)
