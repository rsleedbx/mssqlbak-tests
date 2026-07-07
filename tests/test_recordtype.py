"""Unit tests for record-type classification (ghost / forwarded / stub skip)."""
from __future__ import annotations

from mssqlbak.recordtype import (
    cd_emittable,
    cd_record_type,
    fixedvar_emittable,
    fixedvar_record_type,
)


def _fv(record_type: int, status_b: int = 0, has_nullbmp: bool = True) -> bytes:
    """A FixedVar record header: status A (type in bits 1-3) + status B byte."""
    status_a = (record_type & 0x07) << 1
    if has_nullbmp:
        status_a |= 0x10
    return bytes([status_a, status_b]) + b"\x00\x00"


def _cd(record_type: int) -> bytes:
    """A CD record header byte: CD-format bit + type in bits 2-4."""
    return bytes([0x01 | ((record_type & 0x07) << 2)])


def test_fixedvar_record_type_extraction():
    assert fixedvar_record_type(_fv(0)) == 0  # Primary
    assert fixedvar_record_type(_fv(1)) == 1  # Forwarded
    assert fixedvar_record_type(_fv(2)) == 2  # ForwardingStub
    assert fixedvar_record_type(_fv(6)) == 6  # GhostData


def test_fixedvar_emittable_primary_and_forwarded():
    assert fixedvar_emittable(_fv(0)) is True  # Primary
    assert fixedvar_emittable(_fv(1)) is True  # Forwarded read in place


def test_fixedvar_skips_stub_ghost_blob_index():
    assert fixedvar_emittable(_fv(2)) is False  # ForwardingStub
    assert fixedvar_emittable(_fv(3)) is False  # Index
    assert fixedvar_emittable(_fv(4)) is False  # BlobFragment
    assert fixedvar_emittable(_fv(5)) is False  # GhostIndex
    assert fixedvar_emittable(_fv(6)) is False  # GhostData
    assert fixedvar_emittable(_fv(7)) is False  # GhostVersion


def test_fixedvar_skips_ghost_forwarded_via_status_b():
    # A would-be Primary, but status bits B flags it ghost-forwarded.
    assert fixedvar_emittable(_fv(0, status_b=0x01)) is False


def test_fixedvar_too_short_is_not_emittable():
    assert fixedvar_emittable(b"\x10") is False
    assert fixedvar_emittable(b"") is False


def test_cd_record_type_extraction():
    assert cd_record_type(_cd(0)) == 0  # Primary
    assert cd_record_type(_cd(4)) == 4  # Forwarded
    assert cd_record_type(_cd(3)) == 3  # GhostData


def test_cd_emittable_primary_and_forwarded():
    assert cd_emittable(_cd(0)) is True  # Primary
    assert cd_emittable(_cd(4)) is True  # Forwarded


def test_cd_skips_ghosts_forwarding_index():
    assert cd_emittable(_cd(1)) is False  # GhostEmpty
    assert cd_emittable(_cd(2)) is False  # Forwarding (stub)
    assert cd_emittable(_cd(3)) is False  # GhostData
    assert cd_emittable(_cd(5)) is False  # GhostForwarded
    assert cd_emittable(_cd(6)) is False  # Index
    assert cd_emittable(_cd(7)) is False  # GhostIndex


def test_cd_empty_is_not_emittable():
    assert cd_emittable(b"") is False
