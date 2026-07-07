"""Synthetic unit tests for the xVelocity v4 columnstore decoder.

All inputs are constructed from first principles — no .bak or .pbix files are
required.  Each test isolates a specific code path to provide fast, deterministic
regression coverage for bugs that are difficult to trigger from real fixtures.

Group S1 — _split_v4_record
    Covers all wire formats: Format B (1-byte overhead), Format A (2-byte
    overhead with 0x82 metadata byte), escape handles, empty buffers, the
    Python-fallback Format A / B paths, multi-string CHAR(n) packing, and the
    terminal fallback path that strips non-printable overhead bytes.

Group S2 — _build_huff_table
    Covers: all-zero encode_array (returns None), a 2-symbol full tree, a
    4-symbol full tree, an underfull tree (Kraft < 1.0), and an underfull tree
    with ≥3 unused max-length slots that triggers the +2 escape-prefix shift.

Group S3 — _huff_decode_page_py with synthetic bitstreams
    Covers: 2-symbol decode, 4-symbol decode, underfull tree (no escape),
    single-symbol alphabet, 8-symbol full tree, xmhuffman round-trip, and
    the escape-prefix advance fix: esc_start_code / esc_start_code+1 trigger
    max_len-1 advance while other cl=0 codes (end-of-range padding) use max_len.

Group S4 — _read_lp_entry (LP pool byte reader)
    Covers: plain entry (no metadata byte), 0x80 metadata byte skip (the
    tpcxbb_1gb.bak LP pool fix), empty content, and buffer truncation.
"""
from __future__ import annotations

from typing import Any

import pytest

from mssqlbak.columnstore.decode.dict_xvelocity import (
    _V4_CHAR_OFFSET,
    _build_huff_table,
    _huff_decode_page_py,
    _read_lp_entry,
    _split_v4_record,
)
from tests._v4_builder import (
    make_encode_array as _make_encode_array,
    make_huffman_page as _make_huffman_page,
)

OFF = _V4_CHAR_OFFSET  # = 2


# ---------------------------------------------------------------------------
# Helpers for Group S1 (_split_v4_record builders)
# ---------------------------------------------------------------------------


def _encode_str(s: str) -> bytes:
    """Encode a plain string into the raw Huffman symbol bytes (chr + OFF)."""
    return bytes(ord(c) + OFF for c in s)


def _buf_format_b(content: str) -> bytes:
    """Format B (1-byte overhead): [slen+OFF][content…]  (printable first byte)."""
    payload = _encode_str(content)
    return bytes([len(payload) + OFF]) + payload


def _buf_format_a(content: str, meta: int = 0x82) -> bytes:
    """Format A (2-byte overhead): [slen+OFF][meta][content…]."""
    payload = _encode_str(content)
    return bytes([len(payload) + OFF, meta]) + payload


def _buf_fallback_format_a_long(content: str, extra: bytes = b"") -> bytes:
    """Python-fallback Format A long (decoded0 >= 0x80) with trailing garbage.

    Encodes content, prepends the 2-byte header that encodes glen, then
    appends *extra* garbage bytes (simulating the Python fallback's over-read).
    Header: r[0] = decoded0+OFF where decoded0 = len(payload), r[1] = 0x82
    (d1 = 0x80), giving raw16 = decoded0 | 0x8000 >= 0x8000, so glen = decoded0.
    Requires len(payload) >= 0x80.
    """
    payload = _encode_str(content)
    assert len(payload) >= 0x80, "content must be ≥128 chars for Format A long"
    return bytes([len(payload) + OFF, 0x82]) + payload + extra


def _buf_fallback_format_b_py(content: str, extra: bytes = b"") -> bytes:
    """Python-fallback Format B (decoded0 > 0, decoded0 < 0x80) with garbage."""
    payload = _encode_str(content)
    assert 0 < len(payload) < 0x80, "content must be 1–127 chars for Format B py"
    return bytes([len(payload) + OFF]) + payload + extra


# ---------------------------------------------------------------------------
# Group S1 — _split_v4_record
# ---------------------------------------------------------------------------


class TestSplitV4Record:
    def test_empty_buffer_returns_single_empty_string(self) -> None:
        assert _split_v4_record(b"") == [""]

    def test_format_b_short_content(self) -> None:
        buf = _buf_format_b("Hello")
        assert _split_v4_record(buf) == ["Hello"]

    def test_format_b_single_char(self) -> None:
        buf = _buf_format_b("X")
        assert _split_v4_record(buf) == ["X"]

    def test_format_b_numbers_and_punctuation(self) -> None:
        content = "abc 123 !@#"
        assert _split_v4_record(_buf_format_b(content)) == [content]

    def test_format_a_2byte_overhead_short(self) -> None:
        """Format A with 0x82 metadata byte and short content (slen < 0x80).

        The non-fallback loop: d0 < 0x80, d1=0x80 (r[1]=0x82, non-printable).
        Falls through to v4split:fallback, which skips r[1] because it decodes
        to chr(0x80) > 127 and lands at the first printable byte.
        """
        content = "ShortContent"
        buf = _buf_format_a(content, meta=0x82)
        result = _split_v4_record(buf)
        assert result == [content]

    def test_format_a_2byte_overhead_long(self) -> None:
        """Format A non-fallback with d0 >= 0x80 and d1 >= 0x80 (both bytes big)."""
        content = "A" * 130  # decoded0 = 130 >= 0x80, d1 = 0x80 via meta=0x82
        # The 2-byte-header branch: content = r[2:2+d0]
        buf = _buf_format_a(content, meta=0x82)
        result = _split_v4_record(buf)
        assert result == [content]

    def test_escape_handle_is_escape_true(self) -> None:
        """Escape handles: is_escape=True skips the first overhead byte only."""
        content = "EscapeContent"
        buf = _buf_format_b(content)  # [slen+OFF][content...]
        result = _split_v4_record(buf, is_escape=True)
        assert result == [content]

    def test_python_fallback_format_b_truncates_garbage(self) -> None:
        """Python fallback Format B: from_python_fallback=True, decoded0 in (0,128).

        The decoder uses decoded0 as the exact content length, discarding
        any trailing garbage bytes produced by the fallback over-read.
        """
        content = "RealContent"
        garbage = bytes([0xFF, 0xFE, 0xFD])
        buf = _buf_fallback_format_b_py(content, extra=garbage)
        result = _split_v4_record(buf, from_python_fallback=True)
        assert result == [content], (
            "garbage bytes must be stripped; got {!r}".format(result)
        )

    def test_python_fallback_format_a_long_truncates_garbage(self) -> None:
        """Python fallback Format A long (decoded0 >= 0x80): glen discards tail.

        This is the core regression test for the TAIL_OVER fix: the 2-byte
        header encodes glen, and r[2:2+glen] is the true content.
        """
        content = "B" * 128  # 128 chars → decoded0=128=0x80, d1=0x80 → glen=128
        garbage = bytes([0xAA] * 50)
        buf = _buf_fallback_format_a_long(content, extra=garbage)
        result = _split_v4_record(buf, from_python_fallback=True)
        assert result == [content], (
            "50 garbage bytes must be stripped; got {!r}".format(result)
        )

    def test_python_fallback_format_a_long_glen_formula_high_bit(self) -> None:
        """glen formula: raw16 >= 0x8000 → glen = raw16 & 0x7FFF."""
        content = "C" * 200  # decoded0=200=0xC8, d1=0x80 → raw16=0x80C8 → glen=0x00C8=200
        buf = _buf_fallback_format_a_long(content)
        result = _split_v4_record(buf, from_python_fallback=True)
        assert result == [content]

    def test_char_n_multi_string_split(self) -> None:
        """CHAR(n) multi-string packing: identical length-prefix in every sub-record."""
        n = 5  # CHAR(5): each sub-record = [n+OFF][5 content bytes]
        word1 = "Hello"
        word2 = "World"
        sub1 = bytes([n + OFF]) + _encode_str(word1)
        sub2 = bytes([n + OFF]) + _encode_str(word2)
        buf = sub1 + sub2
        result = _split_v4_record(buf)
        assert result == [word1, word2]

    def test_fallback_path_strips_non_printable_overhead_bytes(self) -> None:
        """v4split:fallback skips leading non-printable overhead bytes."""
        content = "Fallback"
        payload = _encode_str(content)
        # r[0] = some overhead byte, r[1] = 0x82 (non-printable), then content.
        # The non-fallback loop fails to find a clean parse; fallback path
        # skips r[0] and r[1] (both non-printable) and returns decode(r[2:]).
        overhead1 = 0x02  # decoded = 0x02-2=0, which is ≤0 so slen<0 → ok=False
        buf = bytes([overhead1, 0x82]) + payload
        result = _split_v4_record(buf)
        assert result == [content]


# ---------------------------------------------------------------------------
# Group S2 — _build_huff_table
# ---------------------------------------------------------------------------


class TestBuildHuffTable:
    def test_all_zero_encode_array_returns_none(self) -> None:
        table, max_len, esc_start = _build_huff_table(bytes(128))
        assert table is None
        assert max_len == 0

    def test_two_symbol_full_tree(self) -> None:
        """2-symbol cl=1 tree: Kraft sum = 1/2+1/2 = 1.0.  esc_start_code = -1."""
        ea = _make_encode_array({65: 1, 66: 1})  # 'A'=1 bit, 'B'=1 bit
        table, max_len, esc_start = _build_huff_table(ea)
        assert table is not None
        assert max_len == 1
        assert esc_start == -1  # full tree, no escape shift
        # Table has 2 entries; code 0 → 'A', code 1 → 'B'.
        assert (table[0] & 0xFF) == 1 and (table[0] >> 8) == 65
        assert (table[1] & 0xFF) == 1 and (table[1] >> 8) == 66

    def test_four_symbol_full_tree(self) -> None:
        """4-symbol cl=2 tree: Kraft sum = 4/4 = 1.0.  esc_start_code = -1."""
        ea = _make_encode_array({67: 2, 68: 2, 69: 2, 70: 2})
        table, max_len, esc_start = _build_huff_table(ea)
        assert table is not None
        assert max_len == 2
        assert esc_start == -1

    def test_underfull_tree_no_escape_shift(self) -> None:
        """3-symbol tree (n_unused=1): Kraft < 1.0 but < 3 unused → no escape shift."""
        # 3 symbols at cl=2: n_available=4, n_max_syms=3, unused=1 < 3.
        ea = _make_encode_array({65: 2, 66: 2, 67: 2})
        table, max_len, esc_start = _build_huff_table(ea)
        assert table is not None
        assert max_len == 2
        assert esc_start == -1  # unused=1, not enough for escape shift

    def test_underfull_tree_escape_shift_triggered(self) -> None:
        """5-symbol tree at cl=3: n_available=8, n_max_syms=5, unused=3 ≥ 3.

        The +2 escape shift fires: esc_start_code is set to the base code of
        the max_len group (code before the +2 advance).
        """
        # 5 symbols at cl=3.
        ea = _make_encode_array({65: 3, 66: 3, 67: 3, 68: 3, 69: 3})
        table, max_len, esc_start = _build_huff_table(ea)
        assert table is not None
        assert max_len == 3
        assert esc_start >= 0  # +2 shift triggered
        # The two leading table entries (at codes esc_start and esc_start+1)
        # must be cl=0 (the reserved escape slots).
        assert (table[esc_start] & 0xFF) == 0
        assert (table[esc_start + 1] & 0xFF) == 0


# ---------------------------------------------------------------------------
# Group S3 — _huff_decode_page_py with synthetic bitstreams
# ---------------------------------------------------------------------------


class TestHuffDecodePagePySynthetic:
    """Verify _huff_decode_page_py on hand-built Huffman pages.

    All bitstreams are generated by _make_huffman_page, which accounts for the
    byte-pair swap convention used internally by _huff_decode_page_py.
    Decoded bytes are the raw Huffman symbols (no _V4_CHAR_OFFSET applied here).
    """

    def _decode(
        self, strings: list[bytes], code_lens: dict[int, int]
    ) -> tuple[list[bytes], set[int], dict[int, bytes], set[int]]:
        ea, bitstream, offsets, stb = _make_huffman_page(strings, code_lens)
        table, max_len, esc_start = _build_huff_table(ea)
        assert table is not None, "expected valid Huffman table"
        result = _huff_decode_page_py(bitstream, 0, table, max_len, offsets, stb, esc_start)
        assert result is not None, "_huff_decode_page_py returned None"
        return result

    def test_two_symbol_decode(self) -> None:
        """2-symbol full tree (cl=1): decode two single-symbol strings."""
        strings = [bytes([65]), bytes([66])]
        code_lens = {65: 1, 66: 1}
        decoded, escapes, extras, eors = self._decode(strings, code_lens)
        assert decoded == strings
        assert not escapes
        assert not extras
        assert not eors

    def test_four_symbol_multi_byte_decode(self) -> None:
        """4-symbol full tree (cl=2): decode two 2-symbol strings."""
        strings = [bytes([67, 68]), bytes([69, 70])]
        code_lens = {67: 2, 68: 2, 69: 2, 70: 2}
        decoded, escapes, extras, eors = self._decode(strings, code_lens)
        assert decoded == strings
        assert not escapes
        assert not extras
        assert not eors

    def test_mixed_length_strings(self) -> None:
        """Multiple strings of varying lengths using a 4-symbol tree."""
        code_lens = {65: 2, 66: 2, 67: 2, 68: 2}
        strings = [
            bytes([65]),
            bytes([66, 67]),
            bytes([68, 65, 66]),
            bytes([67, 68, 65, 66, 67]),
        ]
        decoded, escapes, extras, eors = self._decode(strings, code_lens)
        assert decoded == strings
        assert not escapes
        assert not extras
        assert not eors

    def test_underfull_tree_decode(self) -> None:
        """3-symbol underfull tree (Kraft < 1.0, no escape shift): decode works."""
        # 3 symbols at cl=2 → Kraft = 3/4 < 1.
        code_lens = {65: 2, 66: 2, 67: 2}
        strings = [bytes([65, 66]), bytes([67, 65])]
        decoded, escapes, extras, eors = self._decode(strings, code_lens)
        assert decoded == strings
        assert not escapes
        assert not extras
        assert not eors

    def test_single_symbol_alphabet(self) -> None:
        """Degenerate 1-symbol tree (cl=1, only code 0): repeated symbol."""
        code_lens = {72: 1}  # only symbol 'H'
        strings = [bytes([72, 72, 72])]
        decoded, escapes, extras, eors = self._decode(strings, code_lens)
        assert decoded == strings
        assert not escapes
        assert not extras
        assert not eors

    def test_eight_symbol_full_tree(self) -> None:
        """8-symbol full tree (cl=3, Kraft=1.0): round-trip 3-bit codes."""
        syms = list(range(65, 73))  # A-H
        code_lens = {s: 3 for s in syms}
        strings = [bytes(syms), bytes(reversed(syms))]
        decoded, escapes, extras, eors = self._decode(strings, code_lens)
        assert decoded == strings
        assert not escapes
        assert not extras
        assert not eors

    def test_matches_xmhuffman_when_available(self) -> None:
        """Byte-for-byte identity with xmhuffman on a synthetic 4-symbol page.

        Skips when xmhuffman is not installed.
        """
        try:
            import xmhuffman as xmh  # noqa: PLC0415
        except ImportError:
            pytest.skip("xmhuffman not available")

        xmh_: Any = xmh  # give pyright a typed handle for the keyword-only stub
        code_lens = {67: 2, 68: 2, 69: 2, 70: 2}
        strings = [bytes([67, 68]), bytes([69, 70]), bytes([67, 69, 70, 68])]
        ea, bitstream, offsets, stb = _make_huffman_page(strings, code_lens)

        table, max_len, esc_start = _build_huff_table(ea)
        assert table is not None

        ref = xmh_.decode_page(
            bitstream=bitstream,
            encode_array_128=ea,
            offsets=offsets,
            store_total_bits=stb,
            swap=True,
        )
        raw = _huff_decode_page_py(
            bitstream, 0, table, max_len, offsets, stb, esc_start
        )
        assert raw is not None, "_huff_decode_page_py returned None on synthetic page"
        py_result, _, _, _ = raw

        assert py_result == list(ref), (
            "mismatch vs xmhuffman on synthetic 4-symbol page; "
            f"got {py_result!r}, expected {list(ref)!r}"
        )

    # ------------------------------------------------------------------
    # Escape-prefix advance tests (regression for esc_start_code fix)
    #
    # Use a 5-symbol underfull tree at cl=3 (n_unused=3 >= 3).
    # _build_huff_table sets esc_start_code=0, reserving table entries 0
    # and 1 as cl=0 escape slots.  Symbols are assigned codes 2..6.
    #
    # When a handle's first idx is esc_start_code (0) or esc_start_code+1
    # (1), the decoder must advance max_len-1=2 bits (not max_len=3) so
    # that the overlapping "parent" code is consumed correctly, and the
    # handle index is added to escape_indices.
    #
    # Bitstreams are constructed manually because _make_huffman_page only
    # encodes normal data symbols (no escape prefixes).
    #
    # Wire-format note: _huff_decode_page_py byte-pair-swaps the input
    # internally, so the pre-swap wire bytes are the pair-reverse of the
    # "swapped" view used here.  For a 2-byte prefix:
    #   swapped[0] = wire[1], swapped[1] = wire[0]
    # ------------------------------------------------------------------

    @staticmethod
    def _escape_tree() -> tuple[bytes, int, int]:
        """Return (encode_array, max_len, esc_start_code) for a 5-symbol cl=3 tree."""
        ea = _make_encode_array({65: 3, 66: 3, 67: 3, 68: 3, 69: 3})
        table, max_len, esc_start = _build_huff_table(ea)
        assert table is not None
        assert max_len == 3
        assert esc_start == 0
        return ea, max_len, esc_start

    def test_escape_prefix_esc_start_code_advances_max_len_minus_1(self) -> None:
        """Handle starting with escape code 0 (idx=esc_start_code=0, 0b000).

        The decoder should advance max_len-1=2 bits (not 3), then decode
        the overlapping symbol starting at bit 2 (symbol A=65, code=2=0b010).

        Swapped view bits: 0,0,0,1,0 → byte0=0b00010000=0x10
        Pre-swap wire:     [0x00, 0x10, 0x00, 0x00]
        """
        ea, max_len, esc_start = self._escape_tree()
        table, ml, es = _build_huff_table(ea)
        assert table is not None

        # Bits 0-2 = 0b000 (escape idx=0); bits 2-4 = 0b010 (symbol 65, code=2).
        # Bit 2 is shared — allowed because escape advance = max_len-1 = 2.
        wire = bytes([0x00, 0x10, 0x00, 0x00])
        offsets = [0]
        stb = 5  # 2-bit escape advance + 3-bit symbol

        raw = _huff_decode_page_py(wire, 0, table, ml, offsets, stb, es)
        assert raw is not None
        decoded, escapes, _, _ = raw

        assert decoded == [bytes([65])], f"expected [b'A'], got {decoded!r}"
        assert escapes == {0}, f"handle 0 must be in escape_indices; got {escapes!r}"

    def test_escape_prefix_esc_start_code_plus_1_advances_max_len_minus_1(self) -> None:
        """Handle starting with escape code 1 (idx=esc_start_code+1=1, 0b001).

        Advance max_len-1=2 bits, then decode symbol C=67 (code=4=0b100) at
        bit 2 (bits 2-4 = 0b100; bit 2 is shared with the escape read).

        Swapped view bits: 0,0,1,0,0 → byte0=0b00100000=0x20
        Pre-swap wire:     [0x00, 0x20, 0x00, 0x00]
        """
        ea, max_len, esc_start = self._escape_tree()
        table, ml, es = _build_huff_table(ea)
        assert table is not None

        # Bits 0-2 = 0b001 (escape idx=1); bits 2-4 = 0b100 (symbol 67, code=4).
        wire = bytes([0x00, 0x20, 0x00, 0x00])
        offsets = [0]
        stb = 5

        raw = _huff_decode_page_py(wire, 0, table, ml, offsets, stb, es)
        assert raw is not None
        decoded, escapes, _, _ = raw

        assert decoded == [bytes([67])], f"expected [b'C'], got {decoded!r}"
        assert escapes == {0}, f"handle 0 must be in escape_indices; got {escapes!r}"

    def test_non_escape_cl0_advances_max_len(self) -> None:
        """End-of-range padding code (idx=7, 0b111) advances max_len=3, not 2.

        idx=7 is also cl=0 but is NOT esc_start_code (0) or esc_start_code+1 (1),
        so the decoder uses the else branch: bit_pos += max_len.

        Swapped view bits: 1,1,1,0,1,0 → byte0=0b11101000=0xE8
        Pre-swap wire:     [0x00, 0xE8, 0x00, 0x00]
        After 3-bit advance (escape via idx=7): bit_pos=3.
        Symbol A (code=2=0b010) at bits 3-5: → correct decode.
        """
        ea, max_len, esc_start = self._escape_tree()
        table, ml, es = _build_huff_table(ea)
        assert table is not None

        # Bits 0-2 = 0b111 (idx=7, cl=0, not esc_start_code).
        # Advance max_len=3; symbol A (code=2=0b010) at bits 3-5.
        # Bits 0-5: 1,1,1,0,1,0 → byte0 = 0b11101000 = 0xE8, stb=6
        wire = bytes([0x00, 0xE8, 0x00, 0x00])
        offsets = [0]
        stb = 6

        raw = _huff_decode_page_py(wire, 0, table, ml, offsets, stb, es)
        assert raw is not None
        decoded, escapes, _, _ = raw

        assert decoded == [bytes([65])], f"expected [b'A'], got {decoded!r}"
        assert escapes == {0}, "idx=7 is still a leading cl=0 → escape_indices"


# ---------------------------------------------------------------------------
# Group S4 — _read_lp_entry (LP pool byte reader)
# ---------------------------------------------------------------------------


class TestReadLpEntry:
    """Regression tests for the LP pool 0x80 metadata byte fix.

    The bug: SQL Server writes [length][0x80][content] in the LP pool but
    the original code read [length] as the length, then treated 0x80 as
    the first content byte, producing b'\x80' + real_content.

    The fix (extracted into _read_lp_entry): detect 0x80 at raw_pos+1 and
    consume it as a metadata byte, so content starts at raw_pos+2.
    """

    def test_plain_entry_no_metadata(self) -> None:
        """[3][A][B][C] → content=b'ABC', new_pos=4."""
        raw = bytes([3, 65, 66, 67])
        content, new_pos = _read_lp_entry(raw, 0)
        assert content == b"ABC"
        assert new_pos == 4

    def test_0x80_metadata_byte_is_skipped(self) -> None:
        """[3][0x80][A][B][C] → content=b'ABC', not b'\\x80ABC'."""
        raw = bytes([3, 0x80, 65, 66, 67])
        content, new_pos = _read_lp_entry(raw, 0)
        assert content == b"ABC", (
            "0x80 metadata byte must be skipped; got {!r}".format(content)
        )
        assert new_pos == 5

    def test_non_0x80_second_byte_not_treated_as_metadata(self) -> None:
        """[3][0x41=A][B][C] → content=b'ABC' (0x41 is NOT a metadata marker)."""
        raw = bytes([3, 0x41, 0x42, 0x43])
        content, new_pos = _read_lp_entry(raw, 0)
        assert content == b"ABC"
        assert new_pos == 4

    def test_empty_content_no_metadata(self) -> None:
        """[0][…] → content=b'', new_pos=1."""
        raw = bytes([0, 0xFF])
        content, new_pos = _read_lp_entry(raw, 0)
        assert content == b""
        assert new_pos == 1

    def test_entry_not_at_start_of_buffer(self) -> None:
        """Reader respects raw_pos offset into the buffer."""
        padding = bytes([99, 99])
        raw = padding + bytes([2, 0x80, 72, 105])  # entry at pos 2: [2][0x80][H][i]
        content, new_pos = _read_lp_entry(raw, 2)
        assert content == b"Hi"
        assert new_pos == 6

    def test_0x80_length_entry_with_content(self) -> None:
        """Length=0x80 (128 bytes) without a metadata byte: returns 128 content bytes."""
        raw = bytes([0x80]) + bytes(range(128))
        content, new_pos = _read_lp_entry(raw, 0)
        # raw[1] = 0x00, not 0x80 → no metadata skip
        assert content == bytes(range(128))
        assert new_pos == 129

    def test_buffer_too_short_raises_index_error(self) -> None:
        """Truncated buffer raises IndexError (caller must handle)."""
        raw = bytes([5, 65, 66])  # length=5 but only 2 content bytes
        with pytest.raises(IndexError):
            _read_lp_entry(raw, 0)
