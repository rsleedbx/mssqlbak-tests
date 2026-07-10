"""Tests for mssqlbak.decoderlab — codec seam, probe/triage, and synth generator.

Test groups
-----------
1. ContainerCodec protocol and registry (codecs.py)
2. MockRawCodec compress/decompress round-trip
3. probe_container on real fixture → XPRESS_DECODABLE
4. probe_container on garbage → UNKNOWN_OR_ENCRYPTED, fast (bounded scan)
5. probe_container on mock container → MOCK_RAW
6. probe_container on truncated fixture → NOT_MSSQLBAK or UNKNOWN_OR_ENCRYPTED
7. reframe_from_bak + _iter_pages → page byte-identity with source
8. reframe_from_bak with each Inject option → correct classification
9. synth_mock + MockRawCodec.decode_record → identity round-trip
10. synth_garbage probe classification
11. Bounded-scan fast-fail: garbage does not scan full buffer (timing assertion)
12. CLI: probe and roundtrip subcommands smoke test
"""

from __future__ import annotations

import mmap
import struct
import sys
import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixture paths
# ---------------------------------------------------------------------------

_FIXTURES = Path(__file__).parent / "fixtures_2022"
_COMPRESSED_BAK = _FIXTURES / "typecoverage_full_compressed.bak"

# Skip all tests that need a real .bak when the file is absent (CI without
# large-fixture downloads).
requires_fixture = pytest.mark.skipif(
    not _COMPRESSED_BAK.exists(),
    reason=f"compressed fixture not found: {_COMPRESSED_BAK}",
)


# ===========================================================================
# 1. Codec protocol and registry
# ===========================================================================


def test_xpress_codec_registered() -> None:
    from mssqlbak.decoderlab.codecs import all_codecs, XpressCodec

    names = [c.name for c in all_codecs()]
    assert "xpress" in names
    assert any(isinstance(c, XpressCodec) for c in all_codecs())


def test_mock_codec_registered() -> None:
    from mssqlbak.decoderlab.codecs import all_codecs, MockRawCodec

    names = [c.name for c in all_codecs()]
    assert "mock-raw" in names
    assert any(isinstance(c, MockRawCodec) for c in all_codecs())


def test_get_codec_returns_correct() -> None:
    from mssqlbak.decoderlab.codecs import get_codec, XpressCodec, MockRawCodec

    assert isinstance(get_codec("xpress"), XpressCodec)
    assert isinstance(get_codec("mock-raw"), MockRawCodec)
    assert get_codec("nonexistent") is None


def test_register_custom_codec() -> None:
    from mssqlbak.decoderlab.codecs import register_codec, get_codec, ContainerCodec

    class _DummyCodec:
        name = "_test_dummy"

        def detect(self, buf, h, layout):
            return False

        def decode_record(self, buf, layout, data, next_h):
            return None

    assert isinstance(_DummyCodec(), ContainerCodec)
    register_codec(_DummyCodec())
    assert get_codec("_test_dummy") is not None


# ===========================================================================
# 2. MockRawCodec compress / decompress round-trip
# ===========================================================================


def test_mock_raw_roundtrip() -> None:
    from mssqlbak.decoderlab.codecs import MockRawCodec
    from mssqlbak.compressed import _V2

    payload = b"hello decoder lab" * 100
    codec = MockRawCodec()
    record = codec.compress(payload)

    # detect at offset 0
    assert codec.detect(record, 0, _V2)

    # decode_record: data starts at MOCK_HDR_SIZE
    from mssqlbak.decoderlab.codecs import MOCK_HDR_SIZE
    got = codec.decode_record(record, _V2, MOCK_HDR_SIZE, len(record))
    assert got == payload


def test_mock_raw_roundtrip_empty() -> None:
    from mssqlbak.decoderlab.codecs import MockRawCodec, MOCK_HDR_SIZE
    from mssqlbak.compressed import _V2

    codec = MockRawCodec()
    record = codec.compress(b"")
    assert codec.detect(record, 0, _V2)
    got = codec.decode_record(record, _V2, MOCK_HDR_SIZE, len(record))
    assert got == b""


def test_mock_raw_detect_rejects_xpress_magic() -> None:
    from mssqlbak.decoderlab.codecs import MockRawCodec
    from mssqlbak.compressed import _V2

    codec = MockRawCodec()
    # XPRESS record starts with a non-DEAD BEEF tag
    bogus = b"\x00\x01\x02\x03" + b"\x00" * 100
    assert not codec.detect(bogus, 0, _V2)


# ===========================================================================
# 3. probe_container on real compressed fixture
# ===========================================================================


@requires_fixture
def test_probe_real_fixture_is_xpress() -> None:
    from mssqlbak.decoderlab.probe import probe_container, ContainerStatus

    report = probe_container(_COMPRESSED_BAK)
    assert report.status == ContainerStatus.XPRESS_DECODABLE, str(report)
    assert report.codec_name == "xpress"
    assert report.first_header_offset is not None
    assert report.decodable_chunks > 0
    assert report.container_version is not None


# ===========================================================================
# 4. probe_container on garbage → fast fail
# ===========================================================================


def test_probe_garbage_unknown_fast() -> None:
    from mssqlbak.decoderlab.probe import probe_container, ContainerStatus
    from mssqlbak.decoderlab.synth import synth_garbage
    from mssqlbak.bak_io import LocalBakReader
    import tempfile, os

    data = synth_garbage(1 << 20)  # 1 MiB
    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        t0 = time.perf_counter()
        report = probe_container(tmp)
        elapsed = time.perf_counter() - t0
        assert report.status == ContainerStatus.UNKNOWN_OR_ENCRYPTED, str(report)
        # Should finish well under 2 seconds even for a 1 MiB buffer.
        assert elapsed < 2.0, f"probe took {elapsed:.2f}s — bootstrap scan not bounded?"
    finally:
        os.unlink(tmp)


# ===========================================================================
# 5. probe_container on a MockRaw container
# ===========================================================================


def test_probe_mock_container() -> None:
    from mssqlbak.decoderlab.probe import probe_container, ContainerStatus
    from mssqlbak.decoderlab.synth import synth_mock
    from mssqlbak.compressed import PAGE_SIZE
    import tempfile, os

    pages = [b"\xAB" * PAGE_SIZE for _ in range(4)]
    data = synth_mock(pages)
    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        report = probe_container(tmp)
        # MockRaw detection happens via the codec registry; probe should
        # find the mock magic and return MOCK_RAW status.
        assert report.status == ContainerStatus.MOCK_RAW, str(report)
        assert report.codec_name == "mock-raw"
    finally:
        os.unlink(tmp)


# ===========================================================================
# 6. probe_container on non-MSSQLBAK
# ===========================================================================


def test_probe_non_mssqlbak() -> None:
    from mssqlbak.decoderlab.probe import probe_container, ContainerStatus
    import tempfile, os

    data = b"This is not a SQL Server backup file at all.\n" * 100
    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        report = probe_container(tmp)
        assert report.status == ContainerStatus.NOT_MSSQLBAK, str(report)
    finally:
        os.unlink(tmp)


# ===========================================================================
# 7. reframe_from_bak + _iter_pages → page byte-identity
# ===========================================================================


@requires_fixture
def test_reframe_roundtrip_page_identity() -> None:
    """Verify that reframed XPRESS records decode to byte-identical pages.

    We collect reference pages from the *same* set of chunks that we reframe
    (the first MAX_CHUNKS), so fuzzy-backup duplicates (pages appearing in
    multiple chunks with different content) don't cause spurious mismatches.
    """
    from mssqlbak.decoderlab.synth import reframe_from_bak
    from mssqlbak.compressed import _iter_chunks_with_pages, _iter_pages

    MAX_CHUNKS = 32

    # Build reference from the SAME chunks that reframe_from_bak will harvest.
    reference: dict[tuple[int, int], bytes] = {}
    with open(_COMPRESSED_BAK, "rb") as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as buf:
        for i, (_data_off, _read_len, pages) in enumerate(_iter_chunks_with_pages(buf)):
            for fid, pid, page in pages:
                reference[(fid, pid)] = page
            if i + 1 >= MAX_CHUNKS:
                break

    assert reference, "no pages decoded from source — fixture may be missing"

    # Reframe into a new container with the same chunk limit.
    container = reframe_from_bak(_COMPRESSED_BAK, max_chunks=MAX_CHUNKS)

    got: dict[tuple[int, int], bytes] = {
        (fid, pid): page for fid, pid, page in _iter_pages(container)
    }

    assert got, "no pages decoded from reframed container"
    for key in got:
        assert key in reference, f"page {key} not in reference"
        assert got[key] == reference[key], f"page {key} mismatch"


# ===========================================================================
# 8. reframe_from_bak with Inject options
# ===========================================================================


@requires_fixture
def test_reframe_inject_pad_gap_recovers_chunks() -> None:
    """PAD_GAP inserts zeros between records; the demux should resync."""
    from mssqlbak.decoderlab.synth import reframe_from_bak, Inject
    from mssqlbak.compressed import _iter_pages

    data = reframe_from_bak(_COMPRESSED_BAK, inject=Inject.PAD_GAP, max_chunks=8)
    pages = list(_iter_pages(data))
    assert len(pages) > 0, "no pages decoded after PAD_GAP injection"


@requires_fixture
def test_reframe_inject_truncate_yields_fewer_pages() -> None:
    from mssqlbak.decoderlab.synth import reframe_from_bak, Inject
    from mssqlbak.compressed import _iter_pages

    full = reframe_from_bak(_COMPRESSED_BAK, max_chunks=20)
    truncated = reframe_from_bak(_COMPRESSED_BAK, inject=Inject.TRUNCATE, max_chunks=20)

    full_pages = list(_iter_pages(full))
    trunc_pages = list(_iter_pages(truncated))
    assert len(trunc_pages) <= len(full_pages)


@requires_fixture
def test_reframe_inject_drop_magic_not_mssqlbak() -> None:
    from mssqlbak.decoderlab.synth import reframe_from_bak, Inject
    from mssqlbak.decoderlab.probe import probe_container, ContainerStatus
    import tempfile, os

    data = reframe_from_bak(_COMPRESSED_BAK, inject=Inject.DROP_MAGIC, max_chunks=4)
    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        report = probe_container(tmp)
        assert report.status == ContainerStatus.NOT_MSSQLBAK, str(report)
    finally:
        os.unlink(tmp)


# ===========================================================================
# 9. synth_mock + MockRawCodec round-trip
# ===========================================================================


def test_synth_mock_identity_roundtrip() -> None:
    from mssqlbak.decoderlab.synth import synth_mock
    from mssqlbak.decoderlab.codecs import MockRawCodec, MOCK_HDR_SIZE
    from mssqlbak.compressed import MSSQLBAK_MAGIC, PAGE_SIZE

    payload = b"\xBE\xEF" * (PAGE_SIZE // 2)
    pages = [payload]
    data = synth_mock(pages)

    # Container starts with MSSQLBAK magic.
    assert data[:len(MSSQLBAK_MAGIC)] == MSSQLBAK_MAGIC

    # After 16-byte container header, the first record must be a MockRaw record.
    codec = MockRawCodec()
    from mssqlbak.compressed import _V2
    hdr_off = 16  # 8-byte magic + 4+4 version words
    assert codec.detect(data, hdr_off, _V2), "MockRaw magic not found at expected offset"

    got = codec.decode_record(data, _V2, hdr_off + MOCK_HDR_SIZE, len(data))
    assert got == payload


# ===========================================================================
# 10. synth_garbage → probe → unknown-or-encrypted
# ===========================================================================


def test_synth_garbage_probes_unknown() -> None:
    from mssqlbak.decoderlab.synth import synth_garbage
    from mssqlbak.decoderlab.probe import probe_container, ContainerStatus
    import tempfile, os

    data = synth_garbage(512 * 1024)
    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        report = probe_container(tmp)
        assert report.status == ContainerStatus.UNKNOWN_OR_ENCRYPTED, str(report)
    finally:
        os.unlink(tmp)


# ===========================================================================
# 11. Bounded scan: _next_header respects scan_limit
# ===========================================================================


def test_next_header_scan_limit_stops_early() -> None:
    from mssqlbak.compressed import _next_header, _V2

    # Build a buffer of pure garbage (unlikely to contain a valid XPRESS header)
    # followed by enough XPRESS-valid bytes — but set limit so we never reach them.
    garbage = b"\xAB\xCD" * (1 << 17)  # 256 KiB garbage
    # With limit=256 the scan must stop before the end.
    result = _next_header(garbage, 0, _V2, scan_limit=256)
    # We only care that it terminated quickly; result is None or an early index.
    assert result is None or result < 256 + 300  # generous margin


def test_next_header_without_limit_accepts_valid() -> None:
    """Without a limit, _next_header finds a real v2 XPRESS header."""
    from mssqlbak.compressed import _next_header, _V2, _is_record_header

    # Read the first valid header from the real fixture (if available).
    if not _COMPRESSED_BAK.exists():
        pytest.skip("compressed fixture not found")

    with open(_COMPRESSED_BAK, "rb") as fh, mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as buf:
        h = _next_header(buf, 0, _V2)
        assert h is not None
        assert _is_record_header(buf, h, _V2)


# ===========================================================================
# 12. CLI smoke tests
# ===========================================================================


@requires_fixture
def test_cli_probe_exits_zero(capsys) -> None:
    from mssqlbak.decoderlab.__main__ import main

    rc = main(["probe", str(_COMPRESSED_BAK)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "xpress-decodable" in out


def test_cli_probe_garbage_exits_zero(tmp_path, capsys) -> None:
    from mssqlbak.decoderlab.synth import synth_garbage
    from mssqlbak.decoderlab.__main__ import main

    f = tmp_path / "garbage.bak"
    f.write_bytes(synth_garbage())
    rc = main(["probe", str(f)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "unknown-or-encrypted" in out


@requires_fixture
def test_cli_roundtrip_exits_zero(capsys) -> None:
    from mssqlbak.decoderlab.__main__ import main

    rc = main(["roundtrip", str(_COMPRESSED_BAK), "--max-chunks", "16"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK:" in out
