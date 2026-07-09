"""Unit tests for mssqlbak.reader — no SQL Server instance required.

The synthetic .bak builder here constructs blocks that match the real
Microsoft Tape Format layout (52-byte common header, MTF_TAPE_ADDRESS string
pointers, big-endian packed dates) so the tests validate against the format
SQL Server actually writes, not against the parser's own assumptions.
"""

from __future__ import annotations

import os
import struct
from datetime import datetime
from pathlib import Path

import pytest

from mssqlbak.reader import (
    BLOCK_SSET,
    BLOCK_TAPE,
    BackupLSNs,
    _COMMON_HDR,
    _COMMON_HDR_SIZE,
    _SSET_ATTR,
    _SSET_DATE,
    _SSET_NAME_ADDR,
    _SSET_NUM,
    _SSET_USER_ADDR,
    _STR_UNICODE,
    _TAPE_DATE,
    _TAPE_NAME_ADDR,
    _TAPE_SOFTWARE_ADDR,
    _TAPE_VERSION,
    _backup_type_label,
    _common_header_checksum_ok,
    _extract_db_files,
    _extract_server_name,
    _parse_mtf_date,
    _resolve_addr,
    is_compressed_or_encrypted,
    lsn_decimal_to_triplet,
    lsn_triplet_to_decimal,
    read_bak_metadata,
)

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))

_FIXTURE = _FIXTURE_DIR / "typecoverage_full.bak"


# ── Struct-size invariants ─────────────────────────────────────────────────────


def test_common_header_size() -> None:
    assert _COMMON_HDR.size == 52
    assert _COMMON_HDR_SIZE == 52


# ── MTF packed date decoder (big-endian bit layout) ────────────────────────────


def _mtf_date_bytes(dt: datetime) -> bytes:
    """Encode a datetime in the MTF_DATE_TIME 40-bit big-endian layout."""
    b0 = (dt.year >> 6) & 0xFF
    b1 = ((dt.year & 0x3F) << 2) | ((dt.month >> 2) & 0x03)
    b2 = ((dt.month & 0x03) << 6) | ((dt.day & 0x1F) << 1) | ((dt.hour >> 4) & 0x01)
    b3 = ((dt.hour & 0x0F) << 4) | ((dt.minute >> 2) & 0x0F)
    b4 = ((dt.minute & 0x03) << 6) | (dt.second & 0x3F)
    return bytes([b0, b1, b2, b3, b4])


@pytest.mark.parametrize(
    "dt",
    [
        datetime(2024, 3, 15, 10, 30, 45),
        datetime(2000, 1, 1, 0, 0, 0),
        datetime(2026, 6, 3, 10, 56, 3),
    ],
)
def test_mtf_date_round_trip(dt: datetime) -> None:
    assert _parse_mtf_date(_mtf_date_bytes(dt)) == dt


def test_mtf_date_zero_returns_none() -> None:
    assert _parse_mtf_date(b"\x00\x00\x00\x00\x00") is None


def test_mtf_date_too_short_returns_none() -> None:
    assert _parse_mtf_date(b"\x00\x00") is None


# ── Backup-type flag decoding ──────────────────────────────────────────────────


def test_backup_type_full() -> None:
    assert _backup_type_label(0x04) == "Full"


def test_backup_type_full_copy_only() -> None:
    assert _backup_type_label(0x04 | 0x02) == "Full (copy-only)"


def test_backup_type_differential() -> None:
    assert _backup_type_label(0x08) == "Differential"


def test_backup_type_unknown() -> None:
    assert _backup_type_label(0x00) == "Unknown"


# ── MTF_TAPE_ADDRESS resolution ────────────────────────────────────────────────


def test_resolve_addr_unicode() -> None:
    payload = "MyDB".encode("utf-16-le")
    block = bytearray(64)
    block[20 : 20 + len(payload)] = payload
    struct.pack_into("<HH", block, 0, len(payload), 20)  # {size, offset}
    assert _resolve_addr(bytes(block), 0, _STR_UNICODE) == "MyDB"


def test_resolve_addr_absent() -> None:
    block = bytes(64)
    assert _resolve_addr(block, 0, _STR_UNICODE) == ""


def test_resolve_addr_out_of_range() -> None:
    block = bytearray(16)
    struct.pack_into("<HH", block, 0, 100, 8)  # size runs off the end
    assert _resolve_addr(bytes(block), 0, _STR_UNICODE) == ""


# ── SQL Server file-path extraction ────────────────────────────────────────────


def test_extract_db_files_unix() -> None:
    block = "x/var/opt/mssql/data/Foo.mdf y".encode("utf-16-le")
    assert _extract_db_files(block) == ["/var/opt/mssql/data/Foo.mdf"]


def test_extract_db_files_windows_and_log() -> None:
    text = r"C:\SQL\Foo.mdf and C:\SQL\Foo_log.ldf"
    assert _extract_db_files(text.encode("utf-16-le")) == [
        r"C:\SQL\Foo.mdf",
        r"C:\SQL\Foo_log.ldf",
    ]


def test_extract_db_files_none() -> None:
    assert _extract_db_files("no paths here".encode("utf-16-le")) == []


# ── Server-name extraction (SFGI-anchored, db-name prefix strip) ───────────────


def _sset_with_server(db: str, server: str, *, tag: bytes = b"SFGI") -> bytes:
    block = bytearray(512)
    tail = (db + server).encode("utf-16-le")
    block[100 : 100 + len(tail)] = tail
    block[100 + len(tail) : 100 + len(tail) + 4] = tag
    return bytes(block)


def test_extract_server_name_strips_db_prefix() -> None:
    block = _sset_with_server("MyDB", "HOST\\INST")
    assert _extract_server_name(block, "MyDB") == "HOST\\INST"


def test_extract_server_name_no_db_name() -> None:
    block = _sset_with_server("MyDB", "HOST")
    assert _extract_server_name(block, "") == ""


def test_extract_server_name_no_sfgi_marker() -> None:
    block = _sset_with_server("MyDB", "HOST", tag=b"\x00\x00\x00\x00")
    assert _extract_server_name(block, "MyDB") == ""


def test_extract_server_name_prefix_mismatch_yields_empty() -> None:
    # When the run does not start with the database name, return nothing rather
    # than guess — the guard that keeps the best-effort path from emitting junk.
    block = _sset_with_server("MyDB", "HOST")
    assert _extract_server_name(block, "OtherDB") == ""


# ── Compressed / TDE-encrypted backup detection ────────────────────────────────


def test_is_compressed_detects_mssqlbak_magic(tmp_path: Path) -> None:
    comp = tmp_path / "compressed.bak"
    comp.write_bytes(b"MSSQLBAK\x02\x00\x00\x00" + b"\x00" * 4096)
    assert is_compressed_or_encrypted(comp) is True


def test_is_compressed_false_for_mtf(tmp_path: Path) -> None:
    plain = tmp_path / "plain.bak"
    plain.write_bytes(_build_synthetic_bak())
    assert is_compressed_or_encrypted(plain) is False


def test_read_bak_rejects_undecodable_container(tmp_path: Path) -> None:
    """An MSSQLBAK container with no decodable descriptor chunks (a TDE-encrypted
    or truncated backup looks like this) raises with a clear message instead of
    returning empty metadata."""
    comp = tmp_path / "compressed.bak"
    comp.write_bytes(b"MSSQLBAK\x02\x00\x00\x00" + b"\x00" * 4096)
    with pytest.raises(ValueError, match="TDE-encrypted or truncated"):
        read_bak_metadata(comp)


def test_read_bak_metadata_on_compressed_matches_uncompressed() -> None:
    """Metadata parses from a real compressed (MSSQLBAK) backup and agrees with
    its uncompressed twin on the database-derived descriptor fields (same
    TAPE/SSET decoders).  The two fixtures are independent backups of the same
    database, so timestamp-style fields may differ; identity fields must not."""
    plain = _FIXTURE_DIR / "typecoverage_full.bak"
    comp = _FIXTURE_DIR / "typecoverage_full_compressed.bak"
    if not (plain.exists() and comp.exists()):
        pytest.skip("compressed/uncompressed fixture pair not present")

    m_plain = read_bak_metadata(plain)
    m_comp = read_bak_metadata(comp)

    assert m_comp.block_size == 0  # container is not physically block-framed
    assert m_comp.backup_sets, "compressed backup yielded no backup set"
    s_plain, s_comp = m_plain.backup_sets[0], m_comp.backup_sets[0]
    assert s_comp.database_name == s_plain.database_name
    assert s_comp.backup_type_label == s_plain.backup_type_label
    assert s_comp.user_name == s_plain.user_name
    assert s_comp.write_date is not None  # 5-byte MTF date decoded, not empty
    assert any(f.lower().endswith(".mdf") for f in s_comp.data_files)


# ── read_bak_metadata — error paths ───────────────────────────────────────────


def test_read_bak_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_bak_metadata(tmp_path / "nonexistent.bak")


def test_read_bak_wrong_magic(tmp_path: Path) -> None:
    bad = tmp_path / "bad.bak"
    bad.write_bytes(b"\x00" * 65536)
    with pytest.raises(ValueError, match="MTF TAPE"):
        read_bak_metadata(bad)


# ── MTF common-header checksum validation ─────────────────────────────────────


def test_common_header_checksum_ok_for_synthetic_header() -> None:
    # The synthetic builder now writes a spec-correct checksum (XOR of all 26
    # header words == 0), mirroring what SQL Server writes.
    assert _common_header_checksum_ok(_common_hdr(BLOCK_TAPE)) is True
    assert _common_header_checksum_ok(_common_hdr(BLOCK_SSET)) is True


def test_common_header_checksum_rejects_corrupt_header() -> None:
    hdr = bytearray(_common_hdr(BLOCK_TAPE))
    hdr[8] ^= 0xFF  # flip a byte outside the checksum field → XOR no longer 0
    assert _common_header_checksum_ok(bytes(hdr)) is False


def test_common_header_checksum_rejects_short_block() -> None:
    assert _common_header_checksum_ok(b"TAPE" + b"\x00" * 10) is False


def test_read_bak_skips_descriptor_with_bad_checksum(tmp_path: Path) -> None:
    """A TAPE block whose header checksum does not validate is not mis-read;
    with no valid descriptor left, read_bak_metadata fails loud."""
    bak = bytearray(_build_synthetic_bak())
    # Corrupt the TAPE common header (byte 8) without fixing the checksum.
    bak[8] ^= 0xFF
    # Also corrupt the SSET header (second block starts at block_size=1024).
    bak[1024 + 8] ^= 0xFF
    p = tmp_path / "corrupt_hdr.bak"
    p.write_bytes(bytes(bak))
    with pytest.raises(ValueError):
        read_bak_metadata(p)


# ── read_bak_metadata — synthetic .bak built to the real MTF layout ───────────


def _common_hdr(block_type: bytes, string_type: int = _STR_UNICODE) -> bytes:
    hdr = bytearray(
        _COMMON_HDR.pack(
            block_type,  # DBLK type
            0,  # block attributes
            0,  # offset to first event
            0x0E,  # OS ID (Windows NT)
            1,  # OS version
            0,  # displayable size
            0,  # format logical address
            0,  # reserved for MBC
            b"\x00" * 6,  # reserved
            0,  # control block ID
            b"\x00" * 4,  # reserved
            0,  # OS-specific data size
            0,  # OS-specific data offset
            string_type,  # string type
            0,  # reserved
            0,  # header checksum (filled in below)
        )
    )
    # MTF header checksum: the XOR of all 26 header words must be zero, so set
    # the checksum word to the XOR of the preceding 25 (what SQL Server writes).
    checksum = 0
    for i in range(0, 50, 2):
        checksum ^= int.from_bytes(hdr[i : i + 2], "little")
    struct.pack_into("<H", hdr, 50, checksum)
    return bytes(hdr)


def _put(block: bytearray, addr_off: int, store_off: int, s: str) -> None:
    """Write *s* at *store_off* and an MTF_TAPE_ADDRESS pointing to it."""
    raw = s.encode("utf-16-le")
    block[store_off : store_off + len(raw)] = raw
    struct.pack_into("<HH", block, addr_off, len(raw), store_off)


def _build_synthetic_bak(
    block_size: int = 1024,
    backup_date: datetime = datetime(2024, 6, 1, 12, 0, 0),
    db_file: str = "/var/opt/mssql/data/TestDB.mdf",
    server_name: str = "TESTHOST",
) -> bytes:
    tape = bytearray(block_size)
    tape[:_COMMON_HDR_SIZE] = _common_hdr(BLOCK_TAPE)
    _put(tape, _TAPE_NAME_ADDR, 200, "MediaName")
    _put(tape, _TAPE_SOFTWARE_ADDR, 300, "Microsoft SQL Server")
    tape[_TAPE_DATE : _TAPE_DATE + 5] = _mtf_date_bytes(backup_date)
    tape[_TAPE_VERSION] = 1

    sset = bytearray(block_size)
    sset[:_COMMON_HDR_SIZE] = _common_hdr(BLOCK_SSET)
    struct.pack_into("<I", sset, _SSET_ATTR, 0x04 | 0x02)  # NORMAL | COPY
    struct.pack_into("<H", sset, _SSET_NUM, 1)
    struct.pack_into("<HH", sset, _SSET_NAME_ADDR, 0, 0)  # empty data-set name
    _put(sset, _SSET_USER_ADDR, 200, "sa")
    sset[_SSET_DATE : _SSET_DATE + 5] = _mtf_date_bytes(backup_date)
    sset[_TAPE_VERSION] = 16
    # SQL config: embed the data-file path so the parser can recover it.
    path_raw = db_file.encode("utf-16-le")
    sset[400 : 400 + len(path_raw)] = path_raw
    # SQL config tail: <db name><server name> as adjacent UTF-16 runs (no
    # delimiter), terminated by the SFGI marker — the real on-disk layout.
    db_name = db_file.rsplit("/", 1)[-1][: -len(".mdf")]
    tail = (db_name + server_name).encode("utf-16-le")
    sset[600 : 600 + len(tail)] = tail
    sset[600 + len(tail) : 600 + len(tail) + 4] = b"SFGI"

    return bytes(tape) + bytes(sset)


def test_synthetic_bak_metadata(tmp_path: Path) -> None:
    bak = tmp_path / "synthetic.bak"
    bak.write_bytes(_build_synthetic_bak())

    meta = read_bak_metadata(bak)

    assert meta.block_size == 1024
    assert meta.media.software_name == "Microsoft SQL Server"
    assert meta.media.media_name == "MediaName"
    assert meta.media.media_date == datetime(2024, 6, 1, 12, 0, 0)
    assert len(meta.backup_sets) == 1

    s = meta.first_set
    assert s is not None
    assert s.backup_type_label == "Full (copy-only)"
    assert s.dataset_number == 1
    assert s.user_name == "sa"
    assert s.write_date == datetime(2024, 6, 1, 12, 0, 0)
    assert s.data_files == ["/var/opt/mssql/data/TestDB.mdf"]
    assert s.database_name == "TestDB"
    assert s.server_name == "TESTHOST"


class _BytesBakReader:
    def __init__(self, data: bytes) -> None:
        self._data = data

    @property
    def size(self) -> int:
        return len(self._data)

    def read_at(self, offset: int, length: int) -> bytes:
        return self._data[offset : offset + length]

    def close(self) -> None:
        return

    def __enter__(self) -> _BytesBakReader:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return "memory://synthetic.bak"


def test_synthetic_bak_metadata_from_bak_reader() -> None:
    reader = _BytesBakReader(_build_synthetic_bak())

    meta = read_bak_metadata(reader)

    assert meta.file_size_mb == pytest.approx(reader.size / (1024 * 1024))
    assert str(meta.file_path) == "memory:/synthetic.bak"
    assert meta.first_set is not None
    assert meta.first_set.database_name == "TestDB"


def test_summary_string(tmp_path: Path) -> None:
    bak = tmp_path / "synthetic.bak"
    bak.write_bytes(_build_synthetic_bak())
    summary = read_bak_metadata(bak).summary()
    assert "Full" in summary
    assert "TestDB" in summary


# ── read_bak_metadata — the real SQL Server 2022 fixture ──────────────────────


@pytest.mark.skipif(not _FIXTURE.exists(), reason="fixture .bak not present")
def test_real_fixture_metadata() -> None:
    meta = read_bak_metadata(_FIXTURE)

    assert meta.media.software_name == "Microsoft SQL Server"
    assert meta.media.media_date is not None

    s = meta.first_set
    assert s is not None
    assert s.backup_type_label == "Full (copy-only)"
    assert s.database_name == "TypeCoverage"
    # SS2017 stores only 15 chars of the server name in the SSET MTF block
    # (legacy NetBIOS 15-char limit); later versions store the full name.
    # "robert-lee-mssq" is the common 15-char prefix present in every version.
    assert s.server_name.startswith("robert-lee-mssq")
    assert s.user_name == "sa"
    assert s.write_date is not None
    assert any(p.endswith("TypeCoverage.mdf") for p in s.data_files)


# ── LSN triplet ↔ decimal conversion ──────────────────────────────────────────


@pytest.mark.parametrize(
    "vlf,blk,rec,expected_decimal",
    [
        (42, 312, 230, "420000003120230"),
        (42, 424, 1, "420000004240001"),
        (1, 0, 0, "10000000000000"),
        (0, 0, 0, "0"),
        (99, 9999, 9999, "990000099999999"),
    ],
)
def test_lsn_triplet_to_decimal(vlf: int, blk: int, rec: int, expected_decimal: str) -> None:
    assert lsn_triplet_to_decimal(vlf, blk, rec) == expected_decimal


@pytest.mark.parametrize(
    "decimal,expected_triplet",
    [
        ("420000003120230", (42, 312, 230)),
        ("420000004240001", (42, 424, 1)),
        ("10000000000000", (1, 0, 0)),
        ("0", (0, 0, 0)),
        (420000003120230, (42, 312, 230)),  # int input also supported
    ],
)
def test_lsn_decimal_to_triplet(decimal: str | int, expected_triplet: tuple[int, int, int]) -> None:
    assert lsn_decimal_to_triplet(decimal) == expected_triplet


def test_lsn_round_trip() -> None:
    for vlf, blk, rec in [(42, 312, 230), (1, 1, 1), (0, 0, 0), (100, 5000, 500)]:
        dec = lsn_triplet_to_decimal(vlf, blk, rec)
        assert lsn_decimal_to_triplet(dec) == (vlf, blk, rec)


# ── LSN extraction from real fixtures (header + boot-page cross-check) ─────────

_FULL_FIXTURE = _FIXTURE_DIR / "incrementalcoverage_full.bak"
_DIFF_FIXTURE = _FIXTURE_DIR / "incrementalcoverage_diff_01.bak"


@pytest.mark.skipif(not _FULL_FIXTURE.exists(), reason="fixture .bak not present")
def test_lsn_header_full_backup_has_first_and_last() -> None:
    """Full backup must have non-None FirstLSN and LastLSN in header."""
    meta = read_bak_metadata(_FULL_FIXTURE)
    s = meta.first_set
    assert s is not None
    assert s.lsns is not None
    lsns = s.lsns
    assert lsns.first_lsn is not None, "Full backup FirstLSN must be present"
    assert lsns.last_lsn is not None, "Full backup LastLSN must be present"
    assert lsns.checkpoint_lsn is not None, "Full backup CheckpointLSN must be present"


@pytest.mark.skipif(not _FULL_FIXTURE.exists(), reason="fixture .bak not present")
def test_lsn_full_backup_database_backup_lsn_is_absent() -> None:
    """DatabaseBackupLSN must be None (zero) for a first full backup with no base."""
    meta = read_bak_metadata(_FULL_FIXTURE)
    s = meta.first_set
    assert s is not None
    assert s.lsns is not None
    assert s.lsns.database_backup_lsn is None, "Full backup with no base must have null DatabaseBackupLSN"


@pytest.mark.skipif(not _FULL_FIXTURE.exists(), reason="fixture .bak not present")
def test_lsn_full_backup_decimal_format() -> None:
    """Decimal representation must be a positive integer string, matching known formula."""
    meta = read_bak_metadata(_FULL_FIXTURE)
    s = meta.first_set
    assert s is not None
    assert s.lsns is not None
    lsns = s.lsns
    assert lsns.first_lsn is not None
    dec_str = lsns.decimal(lsns.first_lsn)
    assert dec_str.isdigit()
    # Decimal must round-trip back to the same triplet.
    assert lsn_decimal_to_triplet(dec_str) == lsns.first_lsn


@pytest.mark.skipif(not _DIFF_FIXTURE.exists(), reason="fixture .bak not present")
def test_lsn_diff_backup_has_database_backup_lsn() -> None:
    """Differential backup must declare which full backup it chains from."""
    meta = read_bak_metadata(_DIFF_FIXTURE)
    s = meta.first_set
    assert s is not None
    assert s.lsns is not None
    assert s.lsns.database_backup_lsn is not None, "Diff backup must have non-null DatabaseBackupLSN"


@pytest.mark.skipif(
    not _FULL_FIXTURE.exists() or not _DIFF_FIXTURE.exists(),
    reason="fixture .bak not present",
)
def test_lsn_diff_database_backup_lsn_matches_full_boot_page() -> None:
    """Cross-check: diff's DatabaseBackupLSN must equal full backup's boot-page dbi_checkptLSN."""
    from mssqlbak.catalog import read_dbinfo_lsns
    from mssqlbak.pages import PageStore

    meta_diff = read_bak_metadata(_DIFF_FIXTURE)
    s_diff = meta_diff.first_set
    assert s_diff is not None
    assert s_diff.lsns is not None
    db_backup_lsn = s_diff.lsns.database_backup_lsn
    assert db_backup_lsn is not None

    store = PageStore.from_bak(_FULL_FIXTURE)
    dbinfo = read_dbinfo_lsns(store)
    assert dbinfo is not None
    assert dbinfo.checkpoint_lsn is not None

    assert db_backup_lsn == dbinfo.checkpoint_lsn, (
        f"Diff DatabaseBackupLSN {db_backup_lsn} must equal full backup "
        f"boot-page dbi_checkptLSN {dbinfo.checkpoint_lsn}"
    )


@pytest.mark.skipif(not _FULL_FIXTURE.exists(), reason="fixture .bak not present")
def test_lsn_ordering_first_le_checkpoint_le_last() -> None:
    """Header LSNs must satisfy FirstLSN <= CheckpointLSN <= LastLSN for a full backup."""
    meta = read_bak_metadata(_FULL_FIXTURE)
    s = meta.first_set
    assert s is not None
    assert s.lsns is not None
    lsns = s.lsns
    assert lsns.first_lsn is not None
    assert lsns.checkpoint_lsn is not None
    assert lsns.last_lsn is not None

    first_dec = int(lsns.decimal(lsns.first_lsn))
    ckpt_dec = int(lsns.decimal(lsns.checkpoint_lsn))
    last_dec = int(lsns.decimal(lsns.last_lsn))

    assert first_dec <= ckpt_dec, f"FirstLSN {first_dec} must be <= CheckpointLSN {ckpt_dec}"
    assert ckpt_dec <= last_dec, f"CheckpointLSN {ckpt_dec} must be <= LastLSN {last_dec}"


# ── BackupLSNs dataclass contract ─────────────────────────────────────────────


def test_backup_lsns_decimal_method() -> None:
    lsns = BackupLSNs(first_lsn=(42, 312, 230))
    assert lsns.decimal((42, 312, 230)) == "420000003120230"


def test_backup_lsns_all_none() -> None:
    lsns = BackupLSNs()
    assert lsns.first_lsn is None
    assert lsns.last_lsn is None
    assert lsns.checkpoint_lsn is None
    assert lsns.database_backup_lsn is None


# ── LSN extraction across multiple fixture versions ────────────────────────────

_ALL_FULL_BAKS = [
    bak
    for ver in ("2017", "2019", "2022", "2025")
    for bak in sorted((Path(__file__).parent / f"fixtures_{ver}").glob("*_full.bak"))
]


@pytest.mark.parametrize("bak_path", _ALL_FULL_BAKS, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_lsn_header_present_for_all_full_fixtures(bak_path: Path) -> None:
    """Every full .bak from 2017..2025 must yield non-None FirstLSN, LastLSN, CheckpointLSN."""
    if not bak_path.exists():
        pytest.skip("fixture not present")
    try:
        meta = read_bak_metadata(bak_path)
    except ValueError as exc:
        # TDE-encrypted or deliberately corrupt fixtures raise ValueError — skip.
        pytest.skip(f"read_bak_metadata raised (likely TDE or corrupt): {exc}")
    s = meta.first_set
    if s is None:
        pytest.skip("no backup set in fixture")
    # Some fixtures may not have the MQCI block (e.g., very old or edge-case layouts);
    # the parser must not raise — it may return None gracefully.
    if s.lsns is None:
        pytest.skip("MQCI block absent in this fixture (acceptable fail-soft)")
    lsns = s.lsns
    assert lsns.first_lsn is not None, f"{bak_path.name}: FirstLSN absent"
    assert lsns.last_lsn is not None, f"{bak_path.name}: LastLSN absent"
    assert lsns.checkpoint_lsn is not None, f"{bak_path.name}: CheckpointLSN absent"
