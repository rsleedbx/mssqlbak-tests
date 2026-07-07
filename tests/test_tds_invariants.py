"""Unit tests for [MS-TDS] §2.2.5 numeric/temporal invariants (Item 3).

These pin the on-disk byte layouts of ``decimal``/``numeric``, ``datetimeoffset``
and the ``sql_variant`` base-type surface to their [MS-TDS] domains, and confirm
the domain asserts fail loud on a corrupt/mis-aligned operand rather than
emitting a plausible-but-wrong value.
"""
from __future__ import annotations

import datetime as dt
import struct
import uuid
from decimal import Decimal

import pytest

from mssqlbak import types as T


# --- decimal / numeric ------------------------------------------------------
def test_decimal_valid_operand_decodes() -> None:
    # sign=1 (positive), magnitude=314, scale=2 → 3.14
    raw = bytes([1]) + (314).to_bytes(2, "little")
    assert T._decode_decimal(raw, 2) == Decimal("3.14")


def test_decimal_negative_sign() -> None:
    raw = bytes([0]) + (314).to_bytes(2, "little")
    assert T._decode_decimal(raw, 2) == Decimal("-3.14")


def test_decimal_bad_sign_byte_raises() -> None:
    raw = bytes([2]) + (314).to_bytes(2, "little")
    with pytest.raises(ValueError):
        T._decode_decimal(raw, 2)


def test_decimal_scale_out_of_range_raises() -> None:
    raw = bytes([1]) + (314).to_bytes(2, "little")
    for bad_scale in (-1, 39, 255):
        with pytest.raises(ValueError):
            T._decode_decimal(raw, bad_scale)


# --- datetimeoffset ---------------------------------------------------------
_SAFE_DAYS = (dt.date(2020, 1, 1) - dt.date(1, 1, 1)).days  # mid-range, no over/underflow


def _dtoffset_scale0(off_min: int) -> bytes:
    """A scale-0 datetimeoffset value body: frac(3) + date(3) + tz(2)."""
    frac = (0).to_bytes(3, "little")
    date = _SAFE_DAYS.to_bytes(3, "little")
    tz = off_min.to_bytes(2, "little", signed=True)
    return frac + date + tz


def test_datetimeoffset_valid_tz_decodes() -> None:
    result = T._decode_datetimeoffset(_dtoffset_scale0(330), 0)  # +05:30
    assert result.utcoffset() == dt.timedelta(minutes=330)


def test_datetimeoffset_tz_out_of_range_raises() -> None:
    # ±840 is the SQL Server limit; Python's timezone would accept up to ±1439,
    # so this guards a corrupt offset that would otherwise fabricate a valid zone.
    for bad in (841, -841, 900, -1000):
        with pytest.raises(ValueError):
            T._decode_datetimeoffset(_dtoffset_scale0(bad), 0)


def test_datetimeoffset_tz_boundary_ok() -> None:
    assert T._decode_datetimeoffset(_dtoffset_scale0(840), 0).utcoffset() == dt.timedelta(minutes=840)
    assert T._decode_datetimeoffset(_dtoffset_scale0(-840), 0).utcoffset() == dt.timedelta(minutes=-840)


# --- sql_variant base-type completeness -------------------------------------
def _variant(base: int, *, metadata: bytes = b"", value: bytes = b"") -> bytes:
    """Build a sql_variant blob: [base][version=1][metadata][value]."""
    return bytes([base, 1]) + metadata + value


def _variant_operand(base: int) -> bytes:
    """A minimal, well-formed sql_variant blob for one base type."""
    if base in (T.DECIMAL, T.NUMERIC):
        # precision, scale in metadata; value = sign + magnitude
        return _variant(base, metadata=bytes([5, 2]), value=bytes([1]) + (314).to_bytes(2, "little"))
    if base in (T.BINARY, T.VARBINARY):
        return _variant(base, metadata=b"\x00\x00", value=b"\x01\x02")
    if base in (T.CHAR, T.VARCHAR, T.NCHAR, T.NVARCHAR):
        collation = b"\x00\x00\x00\x00\x00"  # 5-byte collation block
        value = b"\x00\x00" if base in (T.NCHAR, T.NVARCHAR) else b"AB"
        return _variant(base, metadata=collation, value=value)
    if base in (T.DATETIME2, T.TIME, T.DATETIMEOFFSET):
        scale = bytes([0])
        if base == T.TIME:
            value = (0).to_bytes(3, "little")
        elif base == T.DATETIME2:
            value = (0).to_bytes(3, "little") + (0).to_bytes(3, "little")
        else:
            value = _dtoffset_scale0(0)
        return _variant(base, metadata=scale, value=value)
    fixed = {
        T.TINYINT: b"\x01",
        T.SMALLINT: b"\x00\x00",
        T.INT: b"\x00\x00\x00\x00",
        T.BIGINT: b"\x00" * 8,
        T.BIT: b"\x01",
        T.REAL: struct.pack("<f", 1.0),
        T.FLOAT: struct.pack("<d", 1.0),
        T.MONEY: b"\x00" * 8,
        T.SMALLMONEY: b"\x00\x00\x00\x00",
        T.DATE: (0).to_bytes(3, "little"),
        T.DATETIME: b"\x00" * 8,
        T.SMALLDATETIME: b"\x00\x00\x00\x00",
        T.UNIQUEIDENTIFIER: uuid.uuid4().bytes_le,
    }
    return _variant(base, value=fixed[base])


def test_sql_variant_every_base_type_decodes() -> None:
    """Every type in ``_VARIANT_BASE_TYPES`` has a working decode branch."""
    missing = T._VARIANT_BASE_TYPES - _variant_test_bases()
    assert not missing, f"test is missing operands for base types: {sorted(missing)}"
    for base in T._VARIANT_BASE_TYPES:
        try:
            T._decode_sql_variant(_variant_operand(base))
        except NotImplementedError as exc:  # pragma: no cover - guard failure
            raise AssertionError(f"sql_variant base type {base} not decoded") from exc


def test_sql_variant_non_member_types_raise() -> None:
    """A base type outside the pinned set fails loud (no silent mis-decode)."""
    for base in (T.TEXT, T.NTEXT, T.IMAGE, T.XML, T.CLR_UDT, T.ROWVERSION, T.SQL_VARIANT):
        assert base not in T._VARIANT_BASE_TYPES
        with pytest.raises(NotImplementedError):
            T._decode_sql_variant(_variant(base, value=b"\x00" * 16))


def _variant_test_bases() -> frozenset[int]:
    """Base types this test file builds operands for (both-direction guard)."""
    return frozenset(
        {
            T.TINYINT, T.SMALLINT, T.INT, T.BIGINT, T.BIT, T.REAL, T.FLOAT,
            T.MONEY, T.SMALLMONEY, T.DATE, T.DATETIME, T.SMALLDATETIME,
            T.DATETIME2, T.TIME, T.DATETIMEOFFSET, T.UNIQUEIDENTIFIER,
            T.DECIMAL, T.NUMERIC, T.BINARY, T.VARBINARY,
            T.CHAR, T.VARCHAR, T.NCHAR, T.NVARCHAR,
        }
    )
