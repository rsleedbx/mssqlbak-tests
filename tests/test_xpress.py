"""Engine-independent unit tests for the XPRESS-Huffman decoder.

Two independent test groups:

1. Rust-path tests (no SQL Server) — exercise the public API that delegates
   to the xpress_lz77 Rust extension with known synthetic inputs.

2. Parity tests — run the same input through both the Rust extension and the
   pure-Python reference implementation and assert byte-for-byte equality.
   These catch any divergence between the two implementations.  If only the
   Rust path is tested (as was the case before), bugs in the Python reference
   implementation are invisible until they surface as regressions.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak import xpress
from mssqlbak.xpress import _decompress_python, _decompress_until_input_python

_VECTOR_DIR = Path(__file__).parent / "vectors"

# A complete canonical prefix code where every one of the 512 symbols has a
# 9-bit codeword: 512 * 2**(15-9) == 2**15, so the Kraft sum is exactly filled.
# With all lengths equal, the canonical code of symbol s is simply s (9 bits).
_ALL_LEN_9_TABLE = bytes([0x99]) * (xpress.NUM_SYMBOLS // 2)


def _encode_literals(payload: bytes) -> bytes:
    """Build an XPRESS chunk that decodes to *payload* using only literals.

    Uses the all-length-9 code above, emitting each byte's 9-bit codeword
    MSB-first into little-endian 16-bit coding units (the order the decoder
    consumes).
    """
    bits: list[int] = []
    for byte in payload:
        for shift in range(8, -1, -1):  # 9 bits, MSB first; code(symbol)==symbol
            bits.append((byte >> shift) & 1)
    # pad to a multiple of 16 bits
    while len(bits) % 16:
        bits.append(0)
    out = bytearray(_ALL_LEN_9_TABLE)
    for i in range(0, len(bits), 16):
        word = 0
        for b in range(16):
            word = (word << 1) | bits[i + b]  # first bit -> bit 15
        out += word.to_bytes(2, "little")
    return bytes(out)


def test_decode_literals_round_trip() -> None:
    payload = bytes(range(256)) + b"the quick brown fox" * 10
    chunk = _encode_literals(payload)
    assert xpress.decompress(chunk, 0, len(payload)) == payload


def test_decode_stops_at_out_size() -> None:
    payload = b"abcdefghij" * 50
    chunk = _encode_literals(payload)
    assert xpress.decompress(chunk, 0, 25) == payload[:25]


def test_decode_until_input_recovers_length() -> None:
    payload = b"hello world, compress me" * 8
    chunk = _encode_literals(payload)
    got = xpress.decompress_until_input(chunk, 0, len(chunk))
    # may stop a few bytes short on the final partial coding unit
    assert payload.startswith(got)
    assert len(got) >= len(payload) - 4


def test_v2_demux_includes_final_overlapped_stream_dword() -> None:
    """A v2 MSSQLBAK chunk's stream extends four bytes past ``next_h``.

    This vector is the AdventureWorks2016_EXT XTP checkpoint DATA chunk whose
    final 33 decoded bytes carry the fixed section of
    Sales.SalesOrderHeader_inmem seq 9839.  In v2 containers,
    ``next_h = H + 28 + comp_size`` while the Huffman stream starts at ``H + 32``;
    the stream therefore overlaps the next record's leading size dword.  Stopping
    the slice at ``next_h + 2`` corrupts the final coding unit.
    """
    from mssqlbak.compressed import _V2, _decode_chunk

    chunk = (_VECTOR_DIR / "xpress_soh_final_unit_seq9839.bin").read_bytes()
    expected_tail = bytes.fromhex(
        "2600006c00000000000000000075e844567f0000006ae5b25f7f0000405911c55b"
    )

    reference = xpress.decompress(chunk, 0, 65536)
    assert reference[-33:] == expected_tail

    h = 0
    data = h + _V2.huffman_off
    next_h = h + _V2.next_base + len(chunk)
    buf = bytearray(data + len(chunk))
    buf[h + _V2.tag_off : h + _V2.tag_off + 4] = (len(chunk) << 16).to_bytes(4, "little")
    buf[data:] = chunk

    got = _decode_chunk(bytes(buf), _V2, data, next_h)
    assert got is not None
    assert got[-33:] == expected_tail


def test_table_must_be_complete_prefix_code() -> None:
    # All-zero lengths describe an empty (incomplete) code; the flat table is
    # then all zeros, so the first peek decodes symbol 0 with length 0.  Guard
    # that decompress does not spin forever: it should make progress per symbol.
    chunk = bytes(xpress.NUM_SYMBOLS // 2) + bytes(16)
    out = xpress.decompress(chunk, 0, 4)
    assert out == b"\x00\x00\x00\x00"


def test_until_input_caps_output_on_stuck_bitstream() -> None:
    """A false-positive header (a Kraft-valid table over the wrong bytes) can make
    ``decompress_until_input`` spin forever: once the bitstream over-reads,
    ``ensure`` stops advancing ``next`` (it stays one byte short of ``comp_end``)
    while the loop keeps emitting literals.  A single trailing byte reproduces
    that exact shape; the output cap must turn it into a catchable ValueError so
    the demux re-syncs instead of hanging (the WideWorldImporters-Full case).
    """
    # All-length-9 table + one trailing byte: the stream starts at 256, end=257,
    # so ``ensure`` can never load a 16-bit unit and ``next`` is stuck at 256.
    stuck = _ALL_LEN_9_TABLE + b"\x00"
    with pytest.raises(ValueError, match="false-positive"):
        xpress.decompress_until_input(stuck, 0, len(stuck))


# ---------------------------------------------------------------------------
# Helpers for building synthetic XPRESS chunks with LZ77 back-references
# ---------------------------------------------------------------------------

# All-length-9 table reused from above; each symbol's 9-bit code equals its value.

def _encode_lz77_match(offset: int, length: int) -> list[int]:
    """Return the bit sequence for one LZ77 match in the all-length-9 code.

    *offset* ≥ 1, *length* ≥ 3.  Returns the raw bits (MSB first) for:
      • The 9-bit Huffman codeword for the match symbol.
      • Extra offset bits (log2_off bits after the mandatory leading 1).
    Length extension bytes (nibble == 0xF) are not handled here — keep
    length in [3, 17] to stay in the simple path.
    """
    assert offset >= 1 and length >= 3
    log2_off = max(0, offset.bit_length() - 1)   # floor(log2(offset))
    match_nibble = min(length - 3, 0xF)           # clamp (we keep length ≤ 17)
    symbol = 256 | (log2_off << 4) | match_nibble
    # 9-bit codeword for this symbol (all-length-9 table: code == symbol value)
    bits: list[int] = [(symbol >> (8 - i)) & 1 for i in range(9)]
    # Extra offset bits: the low log2_off bits of offset (the leading 1 is implicit)
    for i in range(log2_off - 1, -1, -1):
        bits.append((offset >> i) & 1)
    return bits


def _build_chunk(sequence: list[tuple[str, bytes | tuple[int, int]]]) -> bytes:
    """Assemble an XPRESS chunk from a mixed literal/match sequence.

    *sequence* is a list of either:
      ``("lit", b"...")``  — one or more literal bytes (each emitted separately)
      ``("lz", (offset, length))``  — one LZ77 back-reference

    Uses the all-length-9 table.
    """
    bits: list[int] = []
    for kind, val in sequence:
        if kind == "lit":
            assert isinstance(val, (bytes, bytearray))
            for byte in val:
                bits.extend((byte >> (8 - i)) & 1 for i in range(9))
        else:
            off, ln = val  # type: ignore[misc]
            bits.extend(_encode_lz77_match(off, ln))  # type: ignore[arg-type]
    # Pad to 16-bit boundary
    while len(bits) % 16:
        bits.append(0)
    out = bytearray(_ALL_LEN_9_TABLE)
    for i in range(0, len(bits), 16):
        word = 0
        for b in range(16):
            word = (word << 1) | bits[i + b]
        out += word.to_bytes(2, "little")
    return bytes(out)


# ---------------------------------------------------------------------------
# Parity tests: Rust extension vs pure-Python reference must agree exactly
# ---------------------------------------------------------------------------

def test_parity_literals_short() -> None:
    """Literal-only chunk: Rust and Python implementations must agree."""
    payload = bytes(range(256)) + b"mssqlbak xpress parity" * 5
    chunk = _encode_literals(payload)
    rust   = xpress.decompress(chunk, 0, len(payload))
    python = _decompress_python(chunk, 0, len(payload))
    assert rust == python, (
        f"Implementation divergence on literal chunk: "
        f"rust={rust[:20]!r} python={python[:20]!r}"
    )


def test_parity_literals_partial_size() -> None:
    """Partial out_size request: both implementations must return the same prefix."""
    payload = bytes(range(256)) * 2
    chunk = _encode_literals(payload)
    for size in (1, 64, 128, 255, 256, 511):
        rust   = xpress.decompress(chunk, 0, size)
        python = _decompress_python(chunk, 0, size)
        assert rust == python, f"Divergence at out_size={size}"


def test_parity_lz77_simple_match() -> None:
    """Single LZ77 back-reference: offset=1, length=4.

    Sequence: 'A', 'B', then copy 4 bytes from 1 byte ago.
    Expected output: A B B B B B  (overlap copy replicates 'B' four times).
    """
    chunk = _build_chunk([
        ("lit", b"AB"),
        ("lz",  (1, 4)),
    ])
    expected = b"AB" + b"B" * 4
    rust   = xpress.decompress(chunk, 0, len(expected))
    python = _decompress_python(chunk, 0, len(expected))
    assert rust   == expected, f"Rust mismatch: {rust!r}"
    assert python == expected, f"Python mismatch: {python!r}"
    assert rust   == python


def test_parity_lz77_non_overlapping_match() -> None:
    """LZ77 back-reference where offset >= length (simple bulk copy)."""
    chunk = _build_chunk([
        ("lit", b"ABCDEF"),
        ("lz",  (6, 3)),   # copy 3 bytes from 6 bytes ago: A B C
    ])
    expected = b"ABCDEFABC"
    rust   = xpress.decompress(chunk, 0, len(expected))
    python = _decompress_python(chunk, 0, len(expected))
    assert rust   == expected, f"Rust mismatch: {rust!r}"
    assert python == expected, f"Python mismatch: {python!r}"
    assert rust   == python


def test_parity_lz77_far_offset() -> None:
    """LZ77 match with a large offset (forces log2_off > 0 and extra offset bits)."""
    header = bytes(range(256))    # 256 distinct bytes as preamble
    chunk = _build_chunk([
        ("lit", header),
        ("lz",  (200, 5)),   # copy 5 bytes from 200 bytes ago
    ])
    expected = header + header[-200 : -200 + 5]
    rust   = xpress.decompress(chunk, 0, len(expected))
    python = _decompress_python(chunk, 0, len(expected))
    assert rust   == expected, f"Rust mismatch: {rust!r}"
    assert python == expected, f"Python mismatch: {python!r}"
    assert rust   == python


def test_parity_multi_sub_chunk() -> None:
    """Output > 65 536 bytes spans multiple sub-chunks; boundary handling must match."""
    # _SUB_CHUNK_OUT = 65536; use 3× to exercise at least two boundaries.
    payload = (bytes(range(256)) * 4) * 200   # 204 800 bytes
    chunk = _encode_literals(payload)
    rust   = xpress.decompress(chunk, 0, len(payload))
    python = _decompress_python(chunk, 0, len(payload))
    assert len(rust)   == len(payload), f"Rust length {len(rust)} != {len(payload)}"
    assert len(python) == len(payload), f"Python length {len(python)} != {len(payload)}"
    assert rust == python, "Multi-sub-chunk output diverges between Rust and Python"


def test_parity_until_input_literals() -> None:
    """decompress_until_input: Rust and Python agree on a literal-only chunk."""
    payload = b"xpress parity check " * 50
    chunk = _encode_literals(payload)
    rust   = xpress.decompress_until_input(chunk, 0, len(chunk))
    python = _decompress_until_input_python(chunk, 0, len(chunk))
    assert payload.startswith(rust),   "Rust output not a prefix of payload"
    assert payload.startswith(python), "Python output not a prefix of payload"
    assert rust == python, (
        f"until_input diverges: rust_len={len(rust)} python_len={len(python)}"
    )


def test_parity_until_input_lz77() -> None:
    """decompress_until_input with LZ77: both implementations agree."""
    chunk = _build_chunk([
        ("lit", b"XPRESS"),
        ("lz",  (3, 5)),    # copy 5 from 3 ago: E S S E S → XPRESSESS ES
        ("lit", b"!!"),
    ])
    rust   = xpress.decompress_until_input(chunk, 0, len(chunk))
    python = _decompress_until_input_python(chunk, 0, len(chunk))
    assert rust == python, (
        f"until_input/lz77 diverges: "
        f"rust={rust!r} python={python!r}"
    )


def test_parity_stuck_bitstream_both_raise() -> None:
    """Both implementations must raise ValueError for a stuck (false-positive) bitstream."""
    stuck = _ALL_LEN_9_TABLE + b"\x00"
    with pytest.raises(ValueError):
        xpress.decompress_until_input(stuck, 0, len(stuck))
    with pytest.raises(ValueError):
        _decompress_until_input_python(stuck, 0, len(stuck))


@pytest.mark.fixture
def test_decodes_real_sqlserver_chunk(fixture_bak_compressed: Path) -> None:
    """A real compressed backup's record chain decodes to the MTF descriptors.

    The first structurally-located record is the MTF ``TAPE`` media header; the
    next is the ``SSET`` start-of-data-set descriptor.  Decoding both exercises
    the XPRESS path against real engine-produced chunks.
    """
    from mssqlbak.compressed import _is_record_header, _layout_for, _next_header

    buf = fixture_bak_compressed.read_bytes()
    lay = _layout_for(buf)
    h = _next_header(buf, 0, lay)
    assert h is not None and _is_record_header(buf, h, lay)
    comp = int.from_bytes(buf[h + lay.tag_off : h + lay.tag_off + 4], "little") >> 16
    assert comp > 0
    out = xpress.decompress_until_input(buf, h + lay.huffman_off, h + lay.next_base + comp)
    assert out[:4] == b"TAPE"  # MTF media header (first descriptor block)

    # The small TAPE record is padded to the next sub-block boundary, so the
    # SSET record is reached by re-syncing forward, not by the contiguous chain.
    contiguous = h + lay.next_base + comp
    nxt = (
        contiguous
        if _is_record_header(buf, contiguous, lay)
        else _next_header(buf, contiguous, lay)
    )
    assert nxt is not None
    comp2 = int.from_bytes(buf[nxt + lay.tag_off : nxt + lay.tag_off + 4], "little") >> 16
    out2 = xpress.decompress(buf, nxt + lay.huffman_off, 8192)
    assert out2[:4] == b"SSET"  # MTF Start-of-data-Set descriptor
    assert comp2 > 0


@pytest.mark.fixture
def test_parity_real_sqlserver_chunk(fixture_bak_compressed: Path) -> None:
    """Real SQL Server XPRESS chunk (genuine LZ77 data): Rust and Python must agree.

    This is the most important parity test: it exercises the LZ77 path with
    actual back-references produced by SQL Server's compressor, which exercises
    edge cases (varying offsets, match lengths, sub-chunk boundaries) that
    synthetic literal-only chunks cannot reach.
    """
    from mssqlbak.compressed import _is_record_header, _layout_for, _next_header

    buf = fixture_bak_compressed.read_bytes()
    lay = _layout_for(buf)
    h = _next_header(buf, 0, lay)
    assert h is not None and _is_record_header(buf, h, lay)

    comp = int.from_bytes(buf[h + lay.tag_off : h + lay.tag_off + 4], "little") >> 16
    assert comp > 0
    start    = h + lay.huffman_off
    comp_end = h + lay.next_base + comp

    rust_out   = xpress.decompress_until_input(buf, start, comp_end)
    python_out = _decompress_until_input_python(buf, start, comp_end)

    assert rust_out[:4] == b"TAPE", f"Rust: expected TAPE header, got {rust_out[:4]!r}"
    assert python_out[:4] == b"TAPE", f"Python: expected TAPE header, got {python_out[:4]!r}"
    assert rust_out == python_out, (
        f"Parity failure on real SQL Server chunk: "
        f"rust_len={len(rust_out)} python_len={len(python_out)}"
    )
