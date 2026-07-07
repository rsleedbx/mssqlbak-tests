"""Unit tests for ROW-compressed (CD-format) record decoding.

These exercise :mod:`mssqlbak.rowcompress` directly with crafted bytes so the
excess-encoded integer rule is covered across magnitudes and signs (including
negatives, which the all-positive ``cmp_row`` fixture does not reach), plus the
CD structure (header, column count, CD array, null / zero / true-bit indicators)
and the PAGE/complex-column skip guards.
"""
from __future__ import annotations

import decimal
import struct

import pytest

from mssqlbak.catalog import Column
from mssqlbak.rowcompress import (
    RowCompressionError,
    _is_utf16le_not_scsu,
    decode_compressed_value,
    normalize_row_value,
    parse_page_ci,
    physical_columns,
    physical_columns_page,
    row_type_supported,
)
from mssqlbak import types as T


def _col(type_id: int, *, max_length: int = 4, scale: int = 0) -> Column:
    return Column(
        name="c", colid=1, type_id=type_id, max_length=max_length,
        precision=0, scale=scale, nullable=True, leaf_offset=0, is_variable=False,
    )


# --- excess-encoded integers ----------------------------------------------
@pytest.mark.parametrize(
    "data, expected",
    [
        (b"", 0),
        (b"\x81", 1),          # 0x81 - 2^7
        (b"\xb1", 49),
        (b"\xff", 127),
        (b"\x80\x80", 128),    # 0x8080 - 2^15
        (b"\x83\xe8", 1000),   # 0x83e8 - 2^15
        (b"\x7f", -1),         # 127 - 2^7
        (b"\x00", -128),       # 0 - 2^7
        (b"\x00\x00", -32768), # 0 - 2^15
    ],
)
def test_excess_encoded_int(data: bytes, expected: int) -> None:
    norm = normalize_row_value(_col(T.INT), data)
    assert int.from_bytes(norm, "little", signed=True) == expected
    assert len(norm) == 4


def test_excess_encoded_bigint_width() -> None:
    norm = normalize_row_value(_col(T.BIGINT), b"\x80\x00\x01")
    assert len(norm) == 8
    assert int.from_bytes(norm, "little", signed=True) == 0x800001 - (1 << 23)


def test_tinyint_is_unsigned_passthrough() -> None:
    assert normalize_row_value(_col(T.TINYINT, max_length=1), b"\xff") == b"\xff"
    assert normalize_row_value(_col(T.TINYINT, max_length=1), b"") == b"\x00"


def test_bit_true_and_false() -> None:
    assert normalize_row_value(_col(T.BIT, max_length=1), b"\x01") == b"\x01"
    assert normalize_row_value(_col(T.BIT, max_length=1), b"") == b"\x00"


def test_fixed_string_and_binary_padding() -> None:
    assert normalize_row_value(_col(T.CHAR, max_length=5), b"ab") == b"ab\x20\x20\x20"
    assert normalize_row_value(_col(T.BINARY, max_length=4), b"\x01\x02") == b"\x01\x02\x00\x00"


# --- compressed nchar/nvarchar (Unicode compression / SCSU) ---------------
def test_compressed_nvarchar_scsu() -> None:
    # "Gray" + SQL Server's trailing 0x10 select-window-0 byte.
    assert decode_compressed_value(_col(T.NVARCHAR, max_length=80), bytes.fromhex("4772617910")) == "Gray"
    assert decode_compressed_value(_col(T.NVARCHAR, max_length=20), b"") == ""


def test_compressed_nchar_pads_to_width() -> None:
    # nchar(10): SCSU stores the trimmed text; the decoder re-pads to 10 chars.
    val = decode_compressed_value(_col(T.NCHAR, max_length=20), b"abc")
    assert val == "abc" + " " * 7


def test_unsupported_type_raises() -> None:
    with pytest.raises(RowCompressionError):
        normalize_row_value(_col(T.DECIMAL), b"\x01")


def test_row_type_supported() -> None:
    assert row_type_supported(_col(T.INT))
    assert row_type_supported(_col(T.VARCHAR, max_length=20))
    assert row_type_supported(_col(T.DECIMAL))   # vardecimal decoder
    assert row_type_supported(_col(T.NUMERIC))
    assert row_type_supported(_col(T.DATETIME))  # excess-BE decoder
    assert row_type_supported(_col(T.DATE))           # plain-LE normaliser
    assert row_type_supported(_col(T.TIME))
    assert row_type_supported(_col(T.DATETIME2))
    assert row_type_supported(_col(T.DATETIMEOFFSET))
    assert row_type_supported(_col(T.NVARCHAR, max_length=80))  # SCSU decoder
    assert row_type_supported(_col(T.NCHAR, max_length=20))
    assert row_type_supported(_col(T.CLR_UDT))  # geography/geometry/hierarchyid
    assert row_type_supported(_col(T.SMALLDATETIME))  # leading-zero-stripped LE
    assert row_type_supported(_col(T.REAL))            # leading-zero-stripped LE
    assert row_type_supported(_col(T.FLOAT, max_length=8))  # leading-zero-stripped LE
    # Formerly ❌ skip-table; now implemented:
    assert row_type_supported(_col(T.ROWVERSION, max_length=8))  # BE leading-zeros
    assert row_type_supported(_col(T.TEXT, max_length=16))        # LOB passthrough
    assert row_type_supported(_col(T.NTEXT, max_length=16))       # LOB passthrough
    assert row_type_supported(_col(T.IMAGE, max_length=16))       # LOB passthrough
    assert row_type_supported(_col(T.XML))


# --- compressed decimal (vardecimal) --------------------------------------
# Byte vectors derived from the documented vardecimal bit layout and
# cross-checked digit-for-digit (e.g. decimal(5,0) 12345 -> C4 03 15 90: byte0
# 0xC4 = sign+ , exponent 4; mantissa chunks 012|345 packed 10 bits each).
@pytest.mark.parametrize(
    "data, scale, expected",
    [
        (b"", 0, "0"),
        (b"\xc4\x03\x15\x90", 0, "12345"),    # decimal(5,0) 12345
        (b"\xc1\x03\x15\x90", 3, "12.345"),   # decimal(5,3) 12.345
        (b"\x41\x03\x15\x90", 3, "-12.345"),  # negative sign bit clear
        (b"\x40\x00\x40", 3, "-1"),           # decimal(_,3) -1
    ],
)
def test_vardecimal_decode(data: bytes, scale: int, expected: str) -> None:
    value = decode_compressed_value(_col(T.DECIMAL, scale=scale), data)
    assert value == decimal.Decimal(expected)


# --- compressed classic datetime (excess-BE) ------------------------------
# Physical column bytes lifted from OrcaMDF's DateCompressionTests CD records
# (the short value after the 3-byte CD header), with the expected instant from
# the test comments.
@pytest.mark.parametrize(
    "data, expected",
    [
        # 1753-01-01 00:00:00.000  (7-byte short "7F2E46000000 00")
        (bytes.fromhex("7f2e4600000000"), (1753, 1, 1, 0, 0, 0, 0)),
        # 1900-01-01 00:00:00.000  (empty short value)
        (b"", (1900, 1, 1, 0, 0, 0, 0)),
        # 1899-01-02 18:22:11.123  (6-byte short "7E94012EB969")
        (bytes.fromhex("7e94012eb969"), (1899, 1, 2, 18, 22, 7, None)),
        # 1900-01-01 22:17:21.447  (4-byte time-only "816F50F2")
        (bytes.fromhex("816f50f2"), (1900, 1, 1, 22, 17, 21, None)),
    ],
)
def test_compressed_datetime_decode(data: bytes, expected: tuple) -> None:
    value = decode_compressed_value(_col(T.DATETIME), data)
    y, mo, d, h, mi, s, _us = expected
    assert (value.year, value.month, value.day) == (y, mo, d)
    assert (value.hour, value.minute) == (h, mi)


# --- compressed 2008+ temporal family (plain little-endian, right-padded) ---
# Compressed bytes are the ordinary on-disk little-endian value with trailing
# zero (high-order) bytes trimmed; the normaliser right-pads to the on-disk
# width.  Vectors confirmed against DBCC PAGE dumps of ROW-compressed tables and
# end-to-end against an uncompressed twin (tests/test_robustness fixture path).
@pytest.mark.parametrize(
    "type_id, scale, data, expected",
    [
        # date (3-byte day count from 0001-01-01)
        (T.DATE, 0, b"\x00\x00\x00", (1, 1, 1)),
        (T.DATE, 0, b"", (1, 1, 1)),                       # fully trimmed -> all zero
        (T.DATE, 0, bytes.fromhex("75250b"), (2001, 1, 1)),  # 730485 days
    ],
)
def test_compressed_date_decode(type_id: int, scale: int, data: bytes, expected: tuple) -> None:
    value = decode_compressed_value(_col(type_id, scale=scale), data)
    assert (value.year, value.month, value.day) == expected


@pytest.mark.parametrize(
    "scale, data, expected_micro",
    [
        (3, b"\x01\x00\x00\x00", 1000),  # 1 ms
        (3, b"\x01", 1000),               # trimmed -> padded to 4 bytes
        (3, b"\x00\x00\x00\x00", 0),
    ],
)
def test_compressed_time_decode(scale: int, data: bytes, expected_micro: int) -> None:
    value = decode_compressed_value(_col(T.TIME, scale=scale), data)
    assert value.microsecond == expected_micro


def test_compressed_datetime2_decode() -> None:
    # time(3)=7_740_129 (0x00761ae1 LE), date=730485 (0x0b2575 LE) -> 2001-01-01 02:09:00.129
    data = bytes.fromhex("e11a760075250b")
    value = decode_compressed_value(_col(T.DATETIME2, scale=3), data)
    assert (value.year, value.month, value.day) == (2001, 1, 1)
    assert (value.hour, value.minute, value.second, value.microsecond) == (2, 9, 0, 129000)


def test_compressed_temporal_normalises_to_full_width() -> None:
    # Trailing-zero trim is undone: every type pads back to its on-disk width.
    assert normalize_row_value(_col(T.DATE), b"\x01") == b"\x01\x00\x00"
    assert normalize_row_value(_col(T.TIME, scale=7), b"\x01") == b"\x01\x00\x00\x00\x00"
    assert normalize_row_value(_col(T.DATETIME2, scale=3), b"\x01") == b"\x01\x00\x00\x00\x00\x00\x00"
    assert normalize_row_value(_col(T.DATETIMEOFFSET, scale=3), b"\x01") == b"\x01" + b"\x00" * 8


# --- real / float / smalldatetime (leading-zero-stripped LE) ---------------
# Under ROW/PAGE compression the on-disk LE bytes are stored with leading (LSB-
# side) zero bytes removed.  Decompression prepends zeros to restore the full
# natural-width value; then the existing type decoders work unchanged.
import datetime as _dt  # noqa: E402  (keep alongside related tests)


@pytest.mark.parametrize(
    "type_id, max_length, data, expected",
    [
        # real (float32, 4 bytes) – leading zeros stripped from LSB end
        (T.REAL, 4, b"",         0.0),           # all-zero -> EMPTY -> 0.0
        (T.REAL, 4, b"\x80\x3f", 1.0),           # LE 0000803f, 2 leading zeros stripped
        (T.REAL, 4, b"\xc3\xf5\x48\x40", 3.140000104904175),  # no leading zeros
        (T.REAL, 4, b"\xc0\xbf", -1.5),          # LE 0000c0bf, 2 leading zeros stripped
        # float (float64, 8 bytes)
        (T.FLOAT, 8, b"",         0.0),
        (T.FLOAT, 8, b"\xf0\x3f", 1.0),          # LE ...0000f03f, 6 leading zeros stripped
        (T.FLOAT, 8, b"\x18\x2d\x44\x54\xfb\x21\x09\x40", 3.141592653589793),
        (T.FLOAT, 8, b"\xf8\xbf", -1.5),
    ],
)
def test_compressed_real_float_decode(
    type_id: int, max_length: int, data: bytes, expected: float
) -> None:
    col = _col(type_id, max_length=max_length)
    value = decode_compressed_value(col, data)
    if expected == 0.0:
        assert value == 0.0
    else:
        assert abs(value - expected) / abs(expected) < 1e-6


@pytest.mark.parametrize(
    "data, expected",
    [
        # smalldatetime = [uint16 minutes LE][uint16 days LE], leading zeros stripped
        (b"",                       _dt.datetime(1900, 1, 1, 0, 0)),   # EMPTY -> 0
        (b"\x00\x00",              _dt.datetime(1900, 1, 1, 0, 0)),   # 2 zero bytes -> 0
        (b"\x01\x00\x01\x00",     _dt.datetime(1900, 1, 2, 0, 1)),   # minutes=1, days=1
        (b"\x9f\x05\xff\xff",     _dt.datetime(2079, 6, 6, 23, 59)), # minutes=1439, days=65535
    ],
)
def test_compressed_smalldatetime_decode(data: bytes, expected: _dt.datetime) -> None:
    value = decode_compressed_value(_col(T.SMALLDATETIME), data)
    assert value == expected


def test_compressed_float_normalises_to_full_width() -> None:
    """normalize_row_value left-pads to natural width for real/float/smalldatetime."""
    assert normalize_row_value(_col(T.REAL),          b"\x80\x3f") == b"\x00\x00\x80\x3f"
    assert normalize_row_value(_col(T.FLOAT, max_length=8), b"\xf0\x3f") == b"\x00" * 6 + b"\xf0\x3f"
    assert normalize_row_value(_col(T.SMALLDATETIME), b"\x00\x00") == b"\x00\x00\x00\x00"


# --- fixture-level integration: real/float/smalldatetime under ROW and PAGE compression ---
import os as _os  # noqa: E402
import pathlib as _pathlib  # noqa: E402

_FIXTURE_DIR = _pathlib.Path(_os.environ.get("FIXTURE_DIR", str(_pathlib.Path(__file__).parent / "fixtures_2022")))
_FIXTURE = _FIXTURE_DIR / "compressioncoverage_full.bak"
_SKIP_NO_BAK = pytest.mark.skipif(not _FIXTURE.exists(), reason="fixture not present")


@_SKIP_NO_BAK
@pytest.mark.parametrize("table_name", ["cmp_row_floats", "cmp_page_floats"])
def test_float_smalldatetime_compressed_roundtrip(table_name: str) -> None:
    """real, float, and smalldatetime rows decode correctly from the fixture under
    both ROW and PAGE compression — no RowCompressionError, no SkipTable."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}
    assert table_name in tables, f"{table_name} not in fixture"
    rows = list(read_table_rows(store, tables[table_name]))
    assert len(rows) == 7

    # Row 7 is all-NULL
    assert rows[6] == {"id": 7, "r": None, "f": None, "sdt": None}

    # Row 1: all zeros
    assert rows[0]["r"] == 0.0
    assert rows[0]["f"] == 0.0
    assert rows[0]["sdt"] == _dt.datetime(1900, 1, 1, 0, 0)

    # Row 4: -1.5 for both floats
    assert rows[3]["r"] == -1.5
    assert rows[3]["f"] == -1.5
    assert rows[3]["sdt"] == _dt.datetime(2079, 6, 6, 23, 59)

    # Row 3: pi-ish values
    assert abs(rows[2]["r"] - 3.14) < 0.001
    assert abs(rows[2]["f"] - 3.141592653589793) < 1e-14
    assert rows[2]["sdt"] == _dt.datetime(2024, 6, 15, 13, 45)


# --- CD record structure ---------------------------------------------------
def test_physical_columns_matches_fixture_record() -> None:
    # cmp_row id=1 row: header, ncol=3, CD array 22 15, then 81 81 'val1'.
    raw = bytes.fromhex("0103221581817661 6c31".replace(" ", ""))
    cols = physical_columns(raw)
    assert cols == [b"\x81", b"\x81", b"val1"]


def test_physical_columns_zero_length_and_null() -> None:
    # 2 columns: CD nibbles col0=ZeroByte(1), col1=Null(0) -> byte 0x01.
    raw = bytes([0x01, 0x02, 0x01])
    assert physical_columns(raw) == [b"", None]


def test_physical_columns_true_bit() -> None:
    # 1 column, CD nibble TrueBit (0xB) -> byte 0x0B, padded.
    raw = bytes([0x01, 0x01, 0x0B, 0x00])
    assert physical_columns(raw) == [b"\x01"]


def test_physical_columns_rejects_non_cd() -> None:
    with pytest.raises(RowCompressionError):
        physical_columns(bytes([0x00, 0x01, 0x02, 0x81]))


def test_physical_columns_rejects_dictionary_symbol() -> None:
    # 1 column with CD nibble DictionarySymbol (0xC) -> PAGE compression.
    with pytest.raises(RowCompressionError):
        physical_columns(bytes([0x01, 0x01, 0x0C, 0x00]))


# --- PAGE compression: compression-info parse + dictionary/anchor ----------
def _page_with_ci() -> tuple[bytes, int]:
    """Build a page image carrying a cmp_page-style CI structure.

    Mirrors the committed ``cmp_page`` page-376 layout: a 3-column anchor whose
    col2 prefix is ``val1`` and a 9-entry dictionary of prefix-compressed values
    (``val0, val2..val9``).  Returns ``(page_bytes, min_slot)``.
    """
    anchor = bytes.fromhex("0103001576616c31")  # CD record: col0/1 NULL, col2='val1'
    entries = [b"\x03" + d for d in (b"0", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9")]
    acc = 2 + 2 * len(entries)  # data starts after count + offset array
    offsets = b""
    for e in entries:
        acc += len(e)
        offsets += struct.pack("<H", acc)
    dictionary = struct.pack("<H", len(entries)) + offsets + b"".join(entries)
    dict_off = 7 + len(anchor)
    ci_size = dict_off + len(dictionary)
    header = bytes([0x06, 0, 0]) + struct.pack("<H", dict_off) + struct.pack("<H", ci_size)
    ci = header + anchor + dictionary
    page = bytearray(8192)
    page[96 : 96 + len(ci)] = ci
    return bytes(page), 96 + ci_size


def test_parse_page_ci_anchor_and_dictionary() -> None:
    page, min_slot = _page_with_ci()
    ci = parse_page_ci(page, min_slot)
    assert ci is not None
    assert ci.anchor[2] == b"val1"  # col2 anchor (col0/col1 are NULL prefixes)
    assert ci.anchor[0] is None and ci.anchor[1] is None
    assert len(ci.dictionary) == 9
    # Entries are prefix-compressed against the anchor: 03='val', then the suffix.
    assert ci.dictionary[0] == b"\x030"  # raw entry; expanded against the anchor


def test_parse_page_ci_absent_when_no_gap() -> None:
    # A page whose first slot is at the header end has no CI.
    assert parse_page_ci(bytes(8192), min_slot=96) is None


def test_physical_columns_page_dictionary_and_anchor() -> None:
    page, min_slot = _page_with_ci()
    ci = parse_page_ci(page, min_slot)
    # id=1, code=1, name='val1' (anchor via ZeroByte): 01 03 22 11 81 81 + slack.
    anchor_rec = bytes.fromhex("0103221181810000")
    cols = physical_columns_page(anchor_rec, ci)
    assert cols[0] == b"\x81" and cols[1] == b"\x81" and cols[2] == b"val1"
    # id=2, code=2, name='val2' (dict index 1): 01 03 22 1c 82 82 01 + slack.
    dict_rec = bytes.fromhex("0103221c82820100")
    cols = physical_columns_page(dict_rec, ci)
    assert cols[2] == b"val2"


def test_physical_columns_page_partial_prefix_decodes() -> None:
    # Partial-prefix: an anchored column (col2 anchor = b'val1') that stores an
    # in-line short value encoding [plen][suffix].  plen=3 -> base = b'val', then
    # suffix = b'2' -> result = b'val2'.  Encoded as a TwoByte nibble (0x3): plen
    # byte 0x03 and suffix byte 0x32 ('2').
    page, min_slot = _page_with_ci()
    ci = parse_page_ci(page, min_slot)
    # CD: 3 cols, nibbles col0=OneByte(2), col1=OneByte(2), col2=TwoByte(3)
    # short region: col0=\x81, col1=\x81, col2=\x03\x32  -> prefix 3 bytes of 'val1' + '2'
    rec = bytes.fromhex("010322038181" + "0332")
    cols = physical_columns_page(rec, ci)
    assert cols[2] == b"val2"


def test_physical_columns_page_no_ci_is_plain_cd() -> None:
    rec = bytes.fromhex("0103221581817661 6c31".replace(" ", ""))
    assert physical_columns_page(rec, None) == physical_columns(rec)


# --- PAGE CI flag variants (§3.6) -------------------------------------------
# Byte 96 is a *flags* byte, not a fixed magic value.  Two values are observed
# in the wild: 0x06 (anchor+dict, covered above) and 0x02 (anchor-only, common
# in temporal history tables).  These tests exercise the flag-dispatch logic
# without requiring a .bak file.
#
# Flag encoding:
#   bit 0 (0x01) = _HDR_CD_FORMAT — set on data records; CI must have this clear
#   bit 1 (0x02) = CI_HAS_ANCHOR_RECORD
#   bit 2 (0x04) = CI_HAS_DICTIONARY

def _page_with_anchor_only_ci() -> tuple[bytes, int]:
    """Build a synthetic page with a 0x02 (anchor-only, no dictionary) CI.

    Three-column anchor: col0=NULL, col1=b'\\xab' (1 byte), col2=b'name1' (5 bytes).
    Header is 5 bytes (no dict_offset field); anchor at +5.

    CD nibble encoding (_CD_SHORT_LEN: 0x2->1 byte, 0x6->5 bytes):
      status=0x01, ncol=3
      cd_array byte0=0x20: col0 low-nibble=0x0(NULL), col1 high-nibble=0x2(1 byte)
      cd_array byte1=0x06: col2 low-nibble=0x6(5 bytes), high=0x0(padding)
      short region: 0xab (col1), b'name1' (col2)
    """
    anchor = bytes([0x01, 0x03, 0x20, 0x06, 0xAB]) + b"name1"  # 10 bytes
    ci_size = 5 + len(anchor)   # 5-byte header + 10-byte anchor = 15
    # 0x02=CI_HAS_ANCHOR, [1-2]=PageModCount=0, [3-4]=ci_size LE (no dict_offset)
    header = bytes([0x02, 0x00, 0x00]) + struct.pack("<H", ci_size)
    ci = header + anchor
    page = bytearray(8192)
    page[96 : 96 + len(ci)] = ci
    return bytes(page), 96 + ci_size


def test_parse_page_ci_anchor_only_recognised() -> None:
    """0x02 CI (anchor-only) must be recognised and parsed; no dictionary."""
    page, min_slot = _page_with_anchor_only_ci()
    ci = parse_page_ci(page, min_slot)
    assert ci is not None, "0x02 CI must be recognised as a valid CI"
    assert ci.dictionary == [], "anchor-only CI must have an empty dictionary"
    # Anchor has 3 columns: NULL, one-byte int, five-byte string
    assert ci.anchor[0] is None
    assert ci.anchor[1] is not None
    assert ci.anchor[2] == b"name1"


def test_parse_page_ci_anchor_only_cd_zero_resolves() -> None:
    """_CD_ZERO on an anchored column from a 0x02 CI must return the anchor value."""
    page, min_slot = _page_with_anchor_only_ci()
    ci = parse_page_ci(page, min_slot)
    assert ci is not None
    # A row record with indicator _CD_ZERO (0x1) for col1 and col2:
    # nibbles: col0=NULL(0x0), col1=ZERO(0x1), col2=ZERO(0x1)
    # cd_array byte0=0x10: col0 low=0x0(NULL), col1 high=0x1(ZERO)
    # cd_array byte1=0x01: col2 low=0x1(ZERO), high=0x0(padding)
    # _CD_ZERO and _CD_NULL both contribute 0 bytes to the short region → no data after header
    zero_rec = bytes([0x01, 0x03, 0x10, 0x01])
    cols = physical_columns_page(zero_rec, ci)
    assert cols[0] is None, "NULL col must stay None"
    assert cols[1] == ci.anchor[1], "_CD_ZERO col1 must resolve to anchor value"
    assert cols[2] == b"name1",     "_CD_ZERO col2 must resolve to anchor value"


def test_parse_page_ci_dict_only_flag_returns_none() -> None:
    """0x04 (CI_HAS_DICTIONARY set but CI_HAS_ANCHOR_RECORD clear) is never
    observed in the wild and is treated as a plain page (returns None).
    The anchor-less case would be ambiguous to decode."""
    page = bytearray(8192)
    # Build a minimal fake dict-only CI header at byte 96
    page[96] = 0x04          # CI_HAS_DICTIONARY only — no anchor flag
    page[97] = 0x00
    page[98] = 0x00
    page[99] = 0x0a          # fake dict_off lo
    page[100] = 0x00         # fake dict_off hi
    min_slot = 96 + 20
    assert parse_page_ci(bytes(page), min_slot) is None, (
        "0x04 (dict-only, no anchor) must be treated as a plain page"
    )


def test_parse_page_ci_cd_record_byte_returns_none() -> None:
    """A page whose byte 96 has bit 0 set is a plain CD data record, not a CI.
    Common value: 0x21 (observed in cmp_page_lob, temporal_test_history, etc.)."""
    page = bytearray(8192)
    page[96] = 0x21   # bit 0 set — _HDR_CD_FORMAT → plain record
    min_slot = 96 + 50
    assert parse_page_ci(bytes(page), min_slot) is None, (
        "0x21 (CD data record byte) must not be mistaken for a CI"
    )


def test_page_prefix_expansion_supports_extended_length() -> None:
    from mssqlbak.rowcompress import _expand_prefix

    anchor = b"a" * 140 + b"old"
    entry = bytes([0x80, 140]) + b"new"

    assert _expand_prefix(entry, anchor) == (b"a" * 140) + b"new"


def test_parse_page_ci_hypothetical_0x0e_anchor_and_dict() -> None:
    """Hypothetical 0x0e = anchor + dict + unknown bit 3.  Since bits 1 and 2
    are both set, the parser should parse anchor and dictionary normally,
    ignoring unknown upper bits."""
    # Reuse the 0x06 CI page built by _page_with_ci() but flip bit 3.
    page, min_slot = _page_with_ci()
    page_mut = bytearray(page)
    page_mut[96] = 0x0e   # bits 1+2+3 set
    ci = parse_page_ci(bytes(page_mut), min_slot)
    assert ci is not None, "Unknown upper bits must not reject a valid anchor+dict CI"
    assert ci.anchor[2] == b"val1"
    assert len(ci.dictionary) == 9


# --- classify_table skip contract for ROW/PAGE compression ----------------
# These prove the end-to-end path: catalog→inspect correctly emits a
# ``compressed:`` skip for tables whose compression + column type combination
# is not yet decodable.  No fixture required — Table objects are crafted here.

from mssqlbak.catalog import COMPRESSION_PAGE, COMPRESSION_ROW, Table  # noqa: E402
from mssqlbak.inspect import classify_table  # noqa: E402


def _compressed_table(
    col_type_id: int, col_name: str, compression: int, max_length: int = 4
) -> Table:
    """Return a minimal Table with one non-nullable id + one typed column."""
    t = Table(name=f"t_{col_name}", object_id=1)
    t.compression = compression
    t.columns = [
        _col(T.INT),
        Column(
            name=col_name, colid=2, type_id=col_type_id, max_length=max_length,
            precision=0, scale=0, nullable=True, leaf_offset=8,
            is_variable=False, user_type_id=col_type_id, null_bit=2,
        ),
    ]
    return t


@pytest.mark.parametrize("col_name,type_id,max_length", [
    ("smalldatetime", T.SMALLDATETIME, 4),
    ("real",          T.REAL, 4),
    ("float",         T.FLOAT, 8),
])
@pytest.mark.parametrize("compression", [COMPRESSION_ROW, COMPRESSION_PAGE])
def test_classify_table_supports_float_smalldatetime_under_compression(
    col_name: str, type_id: int, max_length: int, compression: int
) -> None:
    """real, float, and smalldatetime must be classified as supported under
        ROW/PAGE compression now that leading-zero-stripped LE decoding is implemented."""
    table = _compressed_table(type_id, col_name, compression, max_length=max_length)
    sup = classify_table(table)
    assert sup.supported, (
        f"expected supported=True for {col_name} under compression={compression}"
    )


# --- rowversion under ROW/PAGE compression -----------------------------------
@pytest.mark.parametrize(
    "compressed, expected_be",
    [
        # Compression strips leading (high-order) zero bytes from the big-endian
        # counter; restoring gives the full 8-byte big-endian value, which the
        # uncompressed decoder also returns verbatim (matches SQL Server's
        # rowversion display order).
        (b"\x07\xe2", b"\x00\x00\x00\x00\x00\x00\x07\xe2"),  # 2018
        (b"\x07\xe6", b"\x00\x00\x00\x00\x00\x00\x07\xe6"),  # 2022
        (b"",         b"\x00\x00\x00\x00\x00\x00\x00\x00"),  # 0
        (b"\x01",     b"\x00\x00\x00\x00\x00\x00\x00\x01"),  # 1
    ],
)
def test_compressed_rowversion_normalize(compressed: bytes, expected_be: bytes) -> None:
    col = _col(T.ROWVERSION, max_length=8)
    assert normalize_row_value(col, compressed) == expected_be


def test_compressed_rowversion_decode_returns_bytes() -> None:
    col = _col(T.ROWVERSION, max_length=8)
    result = decode_compressed_value(col, b"\x07\xe2")
    assert isinstance(result, bytes)
    assert len(result) == 8
    assert int.from_bytes(result, "big") == 0x07E2  # 2018, big-endian on-disk order


# --- _long_region multi-complex regression -----------------------------------
def test_long_region_multi_complex() -> None:
    """Three consecutive complex-long entries must all be detected as off-row LOBs.

    Before the _long_region fix, only the first entry had the complex flag
    preserved in the delta; subsequent entries lost it and were returned as
    plain bytes rather than _OffRowLob sentinels.
    """
    from mssqlbak.rowcompress import _OffRowLob

    # Build a minimal CD record with ncol=3, all LONG (CD nibble = 0xA):
    #   byte[0]=0x21 (CD_FORMAT | LONG_DATA)
    #   byte[1]=0x03 (ncol=3)
    #   byte[2]=0xAA  → col0=A(LONG), col1=A(LONG); ptr++
    #   byte[3]=0x0A  → col2=A(LONG) in low nibble; ncol%2=1 → ptr++
    # Long region (flag + count + offsets + data):
    #   flag=0x01
    #   count=3 (u16 LE)
    #   offsets (each u16 LE, high bit per *offset* = complex):
    #     entry 0: complex, 6 bytes  → cumul actual = 6  → 0x8006
    #     entry 1: complex, 6 bytes  → cumul actual = 12 → 0x800C
    #     entry 2: inline, 4 bytes   → cumul actual = 16 → 0x0010
    #   data: 6 bytes + 6 bytes + 4 bytes
    offsets = struct.pack("<HHH", 0x8006, 0x800C, 0x0010)
    lob_a = b"\xaa\xaa\xaa\xaa\xaa\xaa"
    lob_b = b"\xbb\xbb\xbb\xbb\xbb\xbb"
    inline_c = b"\xcc\xcc\xcc\xcc"
    long_region = b"\x01" + struct.pack("<H", 3) + offsets + lob_a + lob_b + inline_c

    cd_hdr = bytes([0x21, 0x03, 0xAA, 0x0A]) + long_region
    cols = physical_columns(cd_hdr)
    assert len(cols) == 3
    # Entries 0 and 1 must be off-row LOBs; entry 2 must be plain inline bytes.
    assert isinstance(cols[0], _OffRowLob), "entry 0 should be _OffRowLob"
    assert isinstance(cols[1], _OffRowLob), "entry 1 should be _OffRowLob (regression)"
    assert cols[2] == inline_c, "entry 2 should be plain inline bytes"
    assert cols[0].data == lob_a
    assert cols[1].data == lob_b


# --- text/ntext/image/xml fixture roundtrip ----------------------------------
@_SKIP_NO_BAK
@pytest.mark.parametrize("table_name", ["cmp_row_lob", "cmp_page_lob"])
def test_legacy_lob_xml_compressed_roundtrip(table_name: str) -> None:
    """text, ntext, image, xml, and rowversion all decode correctly from the
    fixture under ROW and PAGE compression — no RowCompressionError, no SkipTable."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}
    assert table_name in tables, f"{table_name!r} not in fixture"

    rows = list(read_table_rows(store, tables[table_name]))
    assert len(rows) == 3

    # id=1: short values
    r1 = rows[0]
    assert r1["id"] == 1
    assert r1["tx"] == "hello text"
    assert r1["img"] == b"\x48\x65\x6c\x6c\x6f"  # 'Hello'
    assert r1["ntx"] == "hello ntext"
    assert r1["x"] == "<a>one</a>"
    assert isinstance(r1["rv"], bytes) and len(r1["rv"]) == 8

    # id=2: large values (5000 bytes)
    r2 = rows[1]
    assert r2["id"] == 2
    assert r2["tx"] == "x" * 5000
    assert len(r2["img"]) == 5000
    assert r2["ntx"] == "unicode text here"
    assert r2["x"].startswith("<b>")

    # id=3: all NULLs (rowversion is never NULL)
    r3 = rows[2]
    assert r3["id"] == 3
    assert r3["tx"] is None
    assert r3["img"] is None
    assert r3["ntx"] is None
    assert r3["x"] is None
    assert isinstance(r3["rv"], bytes)


# --- sql_variant under ROW/PAGE compression ----------------------------------
@pytest.mark.parametrize(
    "compressed, expected",
    [
        # Fixed types: [type_id][01][value_LE]
        (bytes.fromhex("300100"), 0),           # TINYINT 0
        (bytes.fromhex("38012a000000"), 42),    # INT 42
        (bytes.fromhex("680101"), True),         # BIT 1
        (bytes.fromhex("280153460b"), None),     # DATE 2024-01-15 (checked separately)
    ],
)
def test_compressed_sql_variant_fixed_types(compressed: bytes, expected: object) -> None:
    """Fixed-width sql_variant base types decode directly via _decode_sql_variant."""
    col = _col(T.SQL_VARIANT)
    result = decode_compressed_value(col, compressed)
    if expected is None:
        import datetime as _dt2
        assert isinstance(result, _dt2.date)
    elif isinstance(expected, bool):
        assert result is True
    else:
        assert result == expected


def test_compressed_sql_variant_varchar() -> None:
    """VARCHAR base type inside compressed sql_variant decodes the string value."""
    # a7=VARCHAR, 01, max_len=10(2B LE), collation(4B), value='hello'
    data = bytes.fromhex("a7010a0008d0003468656c6c6f")
    col = _col(T.SQL_VARIANT)
    assert decode_compressed_value(col, data) == "hello"


def test_compressed_sql_variant_nvarchar() -> None:
    """NVARCHAR base type inside compressed sql_variant decodes the string value."""
    data = bytes.fromhex("e701140008d0003468006900")  # NVARCHAR(10) 'hi'
    col = _col(T.SQL_VARIANT)
    assert decode_compressed_value(col, data) == "hi"


@_SKIP_NO_BAK
@pytest.mark.parametrize("table_name", ["cmp_row_variant", "cmp_page_variant"])
def test_sql_variant_compressed_roundtrip(table_name: str) -> None:
    """sql_variant with diverse base types decodes correctly under ROW and PAGE
    compression — no RowCompressionError, no SkipTable."""
    import datetime as _dt2
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}
    assert table_name in tables, f"{table_name!r} not in fixture"

    rows = {r["id"]: r["v"] for r in read_table_rows(store, tables[table_name])}

    assert rows[1] == 0            # TINYINT
    assert rows[2] == 42           # INT
    assert rows[3] == 100000       # BIGINT
    assert abs(rows[4] - 3.14) < 0.001  # FLOAT
    assert rows[5] == "hello"      # VARCHAR
    assert rows[6] == "hi"         # NVARCHAR
    assert rows[7] == _dt2.date(2024, 1, 15)  # DATE
    assert rows[8] is True         # BIT
    assert rows[9] is None         # NULL


# --- G17/G18: CD long-data region (>30 columns) ----------------------------

@_SKIP_NO_BAK
@pytest.mark.parametrize("table_name", ["cmp_row_wide", "cmp_page_wide"])
def test_wide_table_row_count(table_name: str) -> None:
    """G17/G18: 40-column wide tables under ROW/PAGE compression decode all 50 rows."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}
    assert table_name in tables, f"{table_name} not in fixture (regenerate compressioncoverage)"
    rows = list(read_table_rows(store, tables[table_name]))
    assert len(rows) == 50, f"expected 50 rows, got {len(rows)}"


@_SKIP_NO_BAK
@pytest.mark.parametrize("table_name", ["cmp_row_wide", "cmp_page_wide"])
def test_wide_table_all_columns_present(table_name: str) -> None:
    """G17/G18: all 40 data columns (c01..c40) are decoded, not truncated at column 30."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}
    rows = list(read_table_rows(store, tables[table_name]))
    first = rows[0]  # id=1, non-null row
    assert len(first) == 41, f"expected 41 columns (id + c01..c40), got {len(first)}"
    assert first["c01"] == 1
    assert first["c10"] == 10
    assert first["c40"] == 40


@_SKIP_NO_BAK
@pytest.mark.parametrize("table_name", ["cmp_row_wide", "cmp_page_wide"])
def test_wide_table_null_row(table_name: str) -> None:
    """G17/G18: null row (id=7) has all data columns as None."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}
    rows = {r["id"]: r for r in read_table_rows(store, tables[table_name])}
    null_row = rows[7]
    for col in [f"c{n:02d}" for n in range(1, 41)]:
        assert null_row[col] is None, f"{col} should be None in id=7 row"


@_SKIP_NO_BAK
@pytest.mark.parametrize("table_name", ["cmp_row_wide", "cmp_page_wide"])
def test_wide_table_values_deterministic(table_name: str) -> None:
    """G17/G18: each data cell matches the deterministic formula (i*n) % 1000."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}
    rows = {r["id"]: r for r in read_table_rows(store, tables[table_name])}
    for i in (1, 2, 3, 5, 6, 8, 10, 20, 50):  # skip id=7 (null row)
        row = rows[i]
        for n in range(1, 41):
            col = f"c{n:02d}"
            expected = (i * n) % 1000
            assert row[col] == expected, (
                f"{table_name} row id={i} {col}: expected {expected}, got {row[col]}"
            )


# --- K-4: cross-table comparison for previously missing types ---------------

# Columns added by K-4 to _COLS (bigint, smallint, tinyint, bit, money,
# smallmoney, char, binary, varbinary, uniqueidentifier).
_K4_COLS = ["big", "si", "ti", "bf", "mon", "smon", "ch", "bn", "vbn", "uid"]


@_SKIP_NO_BAK
@pytest.mark.parametrize("compressed_table", ["cmp_row", "cmp_page"])
def test_k4_extra_cols_match_baseline(compressed_table: str) -> None:
    """K-4: bigint/smallint/tinyint/bit/money/smallmoney/char/binary/varbinary/
    uniqueidentifier decode identically from ROW/PAGE compressed tables vs the
    uncompressed cmp_none baseline.

    The new columns exercise:
    - leading-zero stripping: bigint, smallint, money, smallmoney
    - trailing-space stripping: char(10)
    - trailing-zero stripping: binary(10)
    - variable-binary CD record: varbinary(20)
    - TrueBit / ZeroByte encoding: bit
    - 16-byte round-trip: uniqueidentifier
    """
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    tables = {t.name: t for t in recover_schema(store).tables}

    for tbl_name in ("cmp_none", compressed_table):
        if tbl_name not in tables:
            pytest.skip(
                f"table '{tbl_name}' not in fixture — regenerate compressionmatrix"
            )

    baseline = {r["id"]: r for r in read_table_rows(store, tables["cmp_none"])}
    compressed = {r["id"]: r for r in read_table_rows(store, tables[compressed_table])}

    assert set(baseline) == set(compressed), "row id sets differ between tables"

    # Detect whether the fixture predates K-4 (columns absent from schema).
    sample = next(iter(baseline.values()))
    present_k4 = [c for c in _K4_COLS if c in sample]
    if not present_k4:
        pytest.skip("K-4 columns not in fixture — regenerate compressionmatrix")

    mismatches: list[str] = []
    for row_id, ref in baseline.items():
        cmp_row = compressed[row_id]
        for col in present_k4:
            ref_val = ref[col]
            cmp_val = cmp_row[col]
            if ref_val != cmp_val:
                mismatches.append(
                    f"id={row_id} col={col}: "
                    f"baseline={ref_val!r} {compressed_table}={cmp_val!r}"
                )

    assert not mismatches, (
        f"{compressed_table} differs from cmp_none on K-4 columns "
        f"({len(mismatches)} mismatches):\n" + "\n".join(mismatches[:20])
    )


# --- SCSU vs UTF-16LE detection (Unicode compression) -----------------------

@pytest.mark.parametrize(
    "hexbytes, expected_utf16le",
    [
        # --- even byte count → UTF-16LE (parity rule) ---
        # "山田" (U+5C71 U+7530): UTF-16LE 4 bytes, SCSU would need 6.
        ("715c3075", True),
        # "山" alone (U+5C71): UTF-16LE 2 bytes, SCSU 3 bytes.
        ("715c", True),
        # U+2020 DAGGER: both bytes 0x20, which are in 0x20-0x7F.
        ("2020", True),
        # "我要测试" (U+6211 U+8981 U+6D4B U+8BD5): UTF-16LE bytes 11 62 81 89 4B 6D D5 8B.
        # 0x11 < 0x20 — the old heuristic incorrectly classified this as SCSU.
        ("116281894b6dd58b", True),
        # Even-length buffer with low/high bytes outside 0x20-0x7F is still UTF-16LE.
        # Decodes to U+0043 U+1D0F U+0280 U+028F = "Cᴏʀʏ" (StackOverflowMini case).
        ("43000f1d80028f02", True),
        # --- odd byte count → SCSU (cannot be UTF-16LE) ---
        ("6e616d6531", False),         # "name1" passthrough (5 bytes)
        ("129fc0b8b2b5c2", False),     # "Привет" window-mode (7 bytes)
        ("6e63663110", False),         # "ncf1" + SC0 trailer (5 bytes)
        ("48690e5c71", False),         # "Hi山" SQU sequence (5 bytes)
        ("13c5b1ada8a710", False),     # "مرحبا" (7 bytes)
        # --- empty → not UTF-16LE ---
        ("", False),
    ],
)
def test_is_utf16le_not_scsu(hexbytes: str, expected_utf16le: bool) -> None:
    assert _is_utf16le_not_scsu(bytes.fromhex(hexbytes)) == expected_utf16le


def test_decode_compressed_nvarchar_cjk_utf16le() -> None:
    """CJK nvarchar stored as UTF-16LE (SCSU would be longer) decodes correctly."""
    col = _col(T.NVARCHAR, max_length=80)  # nvarchar(40)
    # "山田" = U+5C71 U+7530; UTF-16LE 71 5C 30 75
    assert decode_compressed_value(col, bytes.fromhex("715c3075")) == "山田"
    # "山" alone = U+5C71; UTF-16LE 71 5C
    assert decode_compressed_value(col, bytes.fromhex("715c")) == "山"
    # "我要测试" = U+6211 U+8981 U+6D4B U+8BD5; UTF-16LE 11 62 81 89 4B 6D D5 8B.
    # 0x11 is the low byte of 我 — the old heuristic (required all bytes 0x20-0x7F)
    # incorrectly routed this through SCSU and produced garbled output.
    assert decode_compressed_value(col, bytes.fromhex("116281894b6dd58b")) == "我要测试"


def test_decode_compressed_nvarchar_scsu_ascii_preserved() -> None:
    """ASCII nvarchar (SCSU passthrough) still decodes correctly after the change."""
    col = _col(T.NVARCHAR, max_length=40)
    # "name1" → 6e 61 6d 65 31 (5 bytes, odd → SCSU)
    assert decode_compressed_value(col, bytes.fromhex("6e616d6531")) == "name1"
    # "Привет" (Cyrillic) → SCSU window mode (has bytes > 0x7F)
    assert decode_compressed_value(col, bytes.fromhex("129fc0b8b2b5c2")) == "Привет"


@_SKIP_NO_BAK
@pytest.mark.parametrize("compressed_table", ["cmp_row", "cmp_page"])
def test_cjk_nm_matches_baseline(compressed_table: str) -> None:
    """CJK nm values (stored as UTF-16LE) round-trip correctly from compressed tables.

    Rows where id % 3 == 0 use CJK "山田"; this exercises the UTF-16LE decode
    path that was previously broken (decoded as SCSU passthrough → "q\\0u").
    """
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    store = PageStore.from_bak(str(_FIXTURE))
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}

    baseline = {r["id"]: r for r in read_table_rows(store, tables["cmp_none"])}
    compressed = {r["id"]: r for r in read_table_rows(store, tables[compressed_table])}

    cjk_ids = [rid for rid in baseline if rid % 3 == 0]
    assert cjk_ids, "no CJK rows found — fixture may be empty"

    mismatches = [
        f"id={rid}: baseline={baseline[rid]['nm']!r} {compressed_table}={compressed[rid]['nm']!r}"
        for rid in cjk_ids
        if baseline[rid]["nm"] != compressed[rid]["nm"]
    ]
    assert not mismatches, (
        f"{compressed_table} nm mismatch on CJK rows "
        f"({len(mismatches)}):\n" + "\n".join(mismatches[:10])
    )
