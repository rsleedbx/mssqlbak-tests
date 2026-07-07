"""Binary-XML decoding: each construct round-trips to the engine's serialisation.

Every row in the xml-coverage fixture isolates one XML construct (text,
attributes, namespaces, comments, processing instructions, CDATA-as-text,
escaping).  ``decode_xml`` must reproduce the engine's canonical serialisation
(``CAST(doc AS nvarchar(max))``), recorded as ``XmlCase.expected``.
"""
from __future__ import annotations

import datetime as dt
import struct
from pathlib import Path

import pytest

from mssqlbak import xmlbin
from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from mssqlbak.xmlbin import decode_xml
from tools.xmlmatrix import CASES


@pytest.mark.fixture
def test_xml_constructs_decode_to_engine_serialisation(fixture_bak_xml: Path) -> None:
    store = PageStore.from_bak(fixture_bak_xml)
    table = next(t for t in recover_schema(store).tables if t.name == "xmlcov")
    expected = {c.name: c.expected for c in CASES}
    seen: dict[str, str] = {}
    for row in read_table_rows(store, table):
        seen[row["name"]] = row["doc"]
    missing = set(expected) - set(seen)
    assert not missing, f"missing xml rows: {missing}"
    for name, exp in expected.items():
        assert seen[name] == exp, f"{name}: decoded {seen[name]!r} != {exp!r}"


# On-disk Binary XML *Version 2* (header df ff 02 b0 04) of a schema-collection
# bound ``xml`` column, captured from the engine.  The document exercises typed
# atomic values: xs:int attribute + element (XSD-DECIMAL, decimal(38,10)
# normalised), xs:decimal, xs:dateTime (XSD-DATETIME2), xs:boolean (XSD-BOOLEAN),
# xs:date (XSD-DATE2) and an xs:string (SQL-NVARCHAR), inside a default namespace.
_TYPED_V2_BLOB = bytes.fromhex(
    "dfff02b004ea050001000100f00472006f006f007400f006750072006e003a0074006300ef020001f801f00578006d006c006e007300ef000300f6021106750072006e003a0074006300ea050071000013f0016e00ef000004f6038713260a010068f3c9610000000000000000000000f5ea0901710000130a000000f0016900ef020005f804ea0500710000138713260a01008cb6611e0100000000000000000000f7ea0901130000130a000000f0016400ef020006f805ea0500130000138713260a0100fa954f070000000000000000000000f7ea0901150000150c000000f00264007400ef020007f806ea0500150000157e00252b0091400bf7ea0901100000100a000000f0016200ef020008f807ea0500100000108601f7ea0901170000170c000000f00264006400ef020009f808ea0500170000177f9b420bf7ea09010f00000f0a000000f0017300ef02000af809ea05000f00000f1105680065006c006c006f00f7f7"
)
_TYPED_V2_TEXT = (
    '<root xmlns="urn:tc" n="42">'
    "<i>123</i><d>3.14</d><dt>2020-01-02T03:04:05</dt>"
    "<b>true</b><dd>2021-06-07</dd><s>hello</s></root>"
)


def test_typed_version2_xml_decodes_to_engine_serialisation() -> None:
    """Version-2, schema-bound (typed) XML decodes to the engine's text form,
    including typed atomic values rendered in their XSD canonical lexical form."""
    assert decode_xml(_TYPED_V2_BLOB) == _TYPED_V2_TEXT


def _sqltime0(seconds: int) -> bytes:
    """sqltime with scale 0: scale byte + 3-byte whole-seconds count."""
    return bytes([0]) + seconds.to_bytes(3, "little")


def _sqldate(d: dt.date) -> bytes:
    return (d - dt.date(1, 1, 1)).days.to_bytes(3, "little")


def _sqltz(minutes: int) -> bytes:
    return int(minutes).to_bytes(2, "little", signed=True)


def test_offset_datetime_atomic_tokens() -> None:
    """The timezone-bearing date/time atomic types (XSD-DATEOFFSET/
    DATETIMEOFFSET/TIMEOFFSET) render in XSD canonical lexical form: offset 0 as
    ``Z``, others as ``+HH:MM`` / ``-HH:MM``.  Byte layout and the ``Z`` rendering
    were confirmed byte-exact against the engine on AdventureWorks2022."""
    d = dt.date(2020, 1, 2)
    secs = 3 * 3600 + 4 * 60 + 5
    # XSD-DATEOFFSET (0x7C): date + tz; time part ignored; offset 0 -> Z.
    blob = bytes([0x7C]) + _sqltime0(0) + _sqldate(d) + _sqltz(0)
    assert xmlbin._read_atomic(blob, 0)[0] == "2020-01-02Z"
    # XSD-DATETIMEOFFSET (0x7B): date + T + time + offset.
    blob = bytes([0x7B]) + _sqltime0(secs) + _sqldate(d) + _sqltz(330)
    assert xmlbin._read_atomic(blob, 0)[0] == "2020-01-02T03:04:05+05:30"
    # XSD-TIMEOFFSET (0x7A): time + offset; date part ignored.
    blob = bytes([0x7A]) + _sqltime0(secs) + _sqldate(d) + _sqltz(-300)
    assert xmlbin._read_atomic(blob, 0)[0] == "03:04:05-05:00"


def _xml_elem(tag: str, atom_bytes: bytes) -> bytes:
    """Build a minimal binary-XML blob: <tag>{atom}</tag> with the given atomic bytes."""
    hdr = bytes.fromhex("dfff01b004")
    tag_utf16 = tag.encode("utf-16-le")
    namedef = bytes([0xF0, len(tag_utf16) // 2]) + tag_utf16
    qnamedef = bytes([0xEF, 0x00, 0x00, 0x01])
    element = bytes([0xF8, 0x01])
    endelement = bytes([0xF7])
    return hdr + namedef + qnamedef + element + atom_bytes + endelement


def test_unimplemented_token_raises() -> None:
    """An unrecognised structural token raises NotImplementedError (inspect-and-skip).

    Token 0x19 is not assigned by [MS-BINXML] and is not in _ATOMIC_TOKENS, so it
    triggers the final ``else`` branch in the decode loop.
    """
    blob = bytes.fromhex("dfff01b004") + bytes([0x19])
    with pytest.raises(NotImplementedError):
        decode_xml(blob)


def _decimal_operand(precision: int, scale: int, sign: int, coeff: int) -> bytes:
    """Build a [MS-BINXML] decimal operand body (what ``_decimal_str`` consumes)."""
    coeff_bytes = coeff.to_bytes((coeff.bit_length() + 7) // 8 or 1, "little")
    body = bytes([precision, scale, sign]) + coeff_bytes
    return bytes([len(body)]) + body


def test_decimal_atomic_decodes_valid_operand() -> None:
    """A well-formed decimal operand normalises to its lexical string (3.14)."""
    text, end = xmlbin._decimal_str(_decimal_operand(3, 2, 1, 314), 0)
    assert text == "3.14"
    assert end == 6  # 1 length byte + 3 header bytes + 2 coefficient bytes


def test_decimal_bad_precision_raises() -> None:
    """Precision outside 1..38 means a corrupt/mis-aligned operand → fail loud."""
    for bad_precision in (0, 39, 255):
        with pytest.raises(ValueError):
            xmlbin._decimal_str(_decimal_operand(bad_precision, 2, 1, 314), 0)


def test_decimal_scale_exceeds_precision_raises() -> None:
    with pytest.raises(ValueError):
        xmlbin._decimal_str(_decimal_operand(3, 5, 1, 314), 0)


def test_decimal_bad_sign_byte_raises() -> None:
    with pytest.raises(ValueError):
        xmlbin._decimal_str(_decimal_operand(3, 2, 2, 314), 0)


def test_every_atomic_token_is_decoded() -> None:
    """Every token in ``_ATOMIC_TOKENS`` is handled by ``_read_atomic``.

    Guards the [MS-BINXML] coverage claim: a token may not be added to the
    atomic set without a matching decode branch (which would otherwise fall
    through to ``NotImplementedError`` and silently skip the document).
    """
    time0 = bytes([0]) + (0).to_bytes(3, "little")  # sqltime, scale 0
    date0 = (0).to_bytes(3, "little")                # sqldate
    tz0 = (0).to_bytes(2, "little", signed=True)     # sqltimezone
    cp_str = struct.pack("<H", 1252) + bytes([0])    # codepage + 0-length text
    dec = _decimal_operand(3, 2, 1, 314)
    operands = {
        xmlbin._SQL_SMALLINT: b"\x00\x00",
        xmlbin._SQL_INT: b"\x00\x00\x00\x00",
        xmlbin._SQL_REAL: b"\x00\x00\x00\x00",
        xmlbin._SQL_FLOAT: b"\x00" * 8,
        xmlbin._SQL_MONEY: b"\x00" * 8,
        xmlbin._SQL_BIT: b"\x00",
        xmlbin._SQL_TINYINT: b"\x00",
        xmlbin._SQL_BIGINT: b"\x00" * 8,
        xmlbin._SQL_UUID: b"\x00" * 16,
        xmlbin._SQL_DECIMAL: dec,
        xmlbin._SQL_NUMERIC: dec,
        xmlbin._SQL_SMALLDATETIME: b"\x00\x00\x00\x00",
        xmlbin._SQL_DATETIME: b"\x00" * 8,
        xmlbin._SQL_NCHAR: b"\x00",
        xmlbin._SQL_CHAR: cp_str,
        xmlbin._SQL_SMALLMONEY: b"\x00\x00\x00\x00",
        xmlbin._SQL_NVARCHAR: b"\x00",
        xmlbin._SQL_VARCHAR: cp_str,
        xmlbin._SQL_BINARY: b"\x00",
        xmlbin._SQL_VARBINARY: b"\x00",
        xmlbin._SQL_IMAGE: b"\x00",
        xmlbin._SQL_TEXT: cp_str,
        xmlbin._SQL_NTEXT: b"\x00",
        xmlbin._XSD_TIME2: time0,
        xmlbin._XSD_DATETIME2: time0 + date0,
        xmlbin._XSD_DATE2: date0,
        xmlbin._XSD_BOOLEAN: b"\x00",
        xmlbin._XSD_DECIMAL: dec,
        xmlbin._XSD_TIMEOFFSET: time0 + date0 + tz0,
        xmlbin._XSD_DATETIMEOFFSET: time0 + date0 + tz0,
        xmlbin._XSD_DATEOFFSET: time0 + date0 + tz0,
    }
    missing = xmlbin._ATOMIC_TOKENS - operands.keys()
    assert not missing, f"test is missing operands for tokens: {sorted(missing)}"
    for token in xmlbin._ATOMIC_TOKENS:
        blob = bytes([token]) + operands[token]
        try:
            xmlbin._read_atomic(blob, 0)
        except NotImplementedError as exc:  # pragma: no cover - guard failure
            raise AssertionError(f"atomic token 0x{token:02x} not decoded") from exc


def test_sql_ntext_decodes_as_nvarchar() -> None:
    """SQL-NTEXT (0x17) uses the same textdata layout as SQL-NVARCHAR (0x11)."""
    # <a>hello</a> via SQL-NTEXT
    blob = _xml_elem("a", bytes([0x17, 0x05]) + "hello".encode("utf-16-le"))
    assert decode_xml(blob) == "<a>hello</a>"


def test_sql_char_codepage_decodes_text() -> None:
    """SQL-CHAR (0x0F) stores text as codepage bytes; we decode to Unicode."""
    import struct
    # "hello" in cp1252 (0x04E4), 5 bytes
    payload = struct.pack("<H", 1252) + bytes([5]) + b"hello"
    blob = _xml_elem("a", bytes([0x0F]) + payload)
    assert decode_xml(blob) == "<a>hello</a>"


def test_sql_varchar_codepage_decodes_text() -> None:
    """SQL-VARCHAR (0x12) same layout as SQL-CHAR: codepage + varint + bytes."""
    import struct
    payload = struct.pack("<H", 1252) + bytes([5]) + b"world"
    blob = _xml_elem("a", bytes([0x12]) + payload)
    assert decode_xml(blob) == "<a>world</a>"


def test_sql_text_codepage_decodes_text() -> None:
    """SQL-TEXT (0x16) same layout as SQL-CHAR: codepage + varint + bytes."""
    import struct
    payload = struct.pack("<H", 1252) + bytes([5]) + b"there"
    blob = _xml_elem("a", bytes([0x16]) + payload)
    assert decode_xml(blob) == "<a>there</a>"


def test_sql_binary_renders_base64() -> None:
    """SQL-BINARY (0x13): varint byte count + bytes → base64-encoded text."""
    import base64
    data = b"Hello"
    payload = bytes([len(data)]) + data
    blob = _xml_elem("a", bytes([0x13]) + payload)
    assert decode_xml(blob) == f"<a>{base64.b64encode(data).decode()}</a>"


def test_sql_varbinary_renders_base64() -> None:
    """SQL-VARBINARY (0x14) same format as SQL-BINARY."""
    import base64
    data = b"\x00\xff\x42"
    payload = bytes([len(data)]) + data
    blob = _xml_elem("a", bytes([0x14]) + payload)
    assert decode_xml(blob) == f"<a>{base64.b64encode(data).decode()}</a>"


def test_sql_smalldatetime_decodes() -> None:
    """SQL-SMALLDATETIME (0x0C): 2-byte days from 1900-01-01 + 2-byte minutes."""
    import struct
    # 2023-06-15T12:30:00 → days=45090, minutes=750
    payload = struct.pack("<HH", 45090, 750)
    blob = _xml_elem("a", bytes([0x0C]) + payload)
    assert decode_xml(blob) == "<a>2023-06-15T12:30:00</a>"


def test_sql_datetime_decodes_whole_seconds() -> None:
    """SQL-DATETIME (0x0D): 4-byte signed days + 4-byte 1/300s ticks → ISO 8601."""
    import struct
    # 2023-06-15T12:30:45 → days=45090, ticks=45045*300=13513500
    payload = struct.pack("<iI", 45090, 13513500)
    blob = _xml_elem("a", bytes([0x0D]) + payload)
    assert decode_xml(blob) == "<a>2023-06-15T12:30:45</a>"


def test_sql_money_decodes() -> None:
    """SQL-MONEY (0x05): 8-byte LE signed int, value/10000 → 4 decimal places."""
    import struct
    # $12.34 → 123400
    payload = struct.pack("<q", 123400)
    blob = _xml_elem("a", bytes([0x05]) + payload)
    assert decode_xml(blob) == "<a>12.3400</a>"


def test_sql_smallmoney_decodes() -> None:
    """SQL-SMALLMONEY (0x10): 4-byte LE signed int, value/10000 → 4 decimal places."""
    import struct
    # $3.99 → 39900
    payload = struct.pack("<i", 39900)
    blob = _xml_elem("a", bytes([0x10]) + payload)
    assert decode_xml(blob) == "<a>3.9900</a>"


def test_unknown_header_raises() -> None:
    with pytest.raises(NotImplementedError, match="header"):
        decode_xml(b"\x00\x01\x02\x03\x04rest")


@pytest.mark.fixture
def test_xml_large_lob_round_trip(fixture_bak_xml: Path) -> None:
    """Large XML values (>8 KB binary representation) are stored off-row as
    a LOB chain.  _stitch_lob must reassemble all fragments before decode_xml
    runs, so the full document is returned intact.

    The fixture row ``name='large_lob'`` is a <root> with 300 <item> children,
    whose binary XML representation is ~33 KB (well above the 8 KB in-row limit).
    We verify both the structure (root element, correct child count) and the
    total decoded length.
    """
    store = PageStore.from_bak(fixture_bak_xml)
    table = next(t for t in recover_schema(store).tables if t.name == "xmlcov")
    row = next(r for r in read_table_rows(store, table) if r["name"] == "large_lob")
    doc: str = row["doc"]
    assert doc.startswith("<root><item id=\"1\">")
    assert doc.endswith("300</item></root>")
    assert doc.count("<item ") == 300
    assert len(doc) > 10_000
