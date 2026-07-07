"""Reusable builder utilities for synthetic xVelocity v4 dictionary binary blobs.

These helpers let any test file or diagnostic script construct ``(raw, deint)``
pairs for exercising ``_decode_v4_huff_dict`` end-to-end, without needing a
real ``.bak`` or ``.pbix`` fixture file.

Public surface
--------------
make_encode_array(code_lens)        — build a 128-byte encode_array_128
canonical_codes(code_lens)          — assign canonical Huffman codes
make_huffman_page(strings, code_lens) — build one compressed Huffman page
auto_code_lens(buffers)             — derive code lengths from raw byte values
format_b_record(content)            — build a single Format B record buffer
V4DictBuilder                       — builds the complete (raw, deint) binary

Layout reference (mirrors constants in dict_xvelocity.py)
----------------------------------------------------------
deint bytes 0-3:    placeholder (not validated by the decoder)
deint bytes 4-7:    n_data_ids - 1  (uint32 LE)
deint bytes 8-63:   zeros           (56 bytes, not read)
deint bytes 64-67:  page_count      (uint32 LE)
deint bytes 68..:   record-handle array  (n_handles × 8 bytes each)
                    page directory       (page_count × 4 raw-byte-lengths)
                    16-byte gap
                    page 0 header + data
                    page 1 header + data  …

Each Huffman page header (144 deint bytes):
    [0-3]:   store_total_bits  (uint32 LE)
    [4-11]:  zeros             (8 bytes)
    [12-139]: encode_array_128 (128 bytes)
    [140-143]: zeros           (4 bytes)

Each LP pool page header (8 deint bytes):
    [0-3]:  stb = 0       (uint32 LE)
    [4-7]:  pool_size     (uint32 LE)

For blobs that fit in a single 65 536-byte LOB chunk there are no LOB
separators, so ``raw = b'\\x00' * 12 + bytes(deint)``.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass

# Mirror constants from dict_xvelocity.py — no circular import.
_V4_ENTRY_COUNT_OFF: int = 4
_V4_PAGE_COUNT_OFF: int = 64
_V4_RH_OFF: int = 68
_V4_RH_SZ: int = 8
_V4_PAGE_GAP_BASE: int = 16
_V4_PAGE_HDR_SZ: int = 144
_V4_STB_OFF_IN_HDR: int = 0
_V4_EA_OFF_IN_HDR: int = 12
_V4_UNCOMPRESSED_HDR_SZ: int = 8
_V4_CHAR_OFFSET: int = 2
_LOB_PREAMBLE: int = 12


# ---------------------------------------------------------------------------
# Low-level Huffman helpers
# ---------------------------------------------------------------------------


def make_encode_array(code_lens: dict[int, int]) -> bytes:
    """Build a 128-byte ``encode_array_128`` from a ``{symbol: code_length}`` dict.

    Nibble layout: ``encode_array[i]`` low-nibble = cl(2i),
    high-nibble = cl(2i+1).
    """
    ea = bytearray(128)
    for sym, cl in code_lens.items():
        byte_pos = sym // 2
        if sym % 2 == 0:
            ea[byte_pos] = (ea[byte_pos] & 0xF0) | (cl & 0x0F)
        else:
            ea[byte_pos] = (ea[byte_pos] & 0x0F) | ((cl & 0x0F) << 4)
    return bytes(ea)




def canonical_codes(code_lens: dict[int, int]) -> dict[int, tuple[int, int]]:
    """Compute canonical Huffman codes from a ``{symbol: code_length}`` mapping.

    Returns ``{symbol: (code_length, code)}`` with codes assigned in the
    standard canonical order (lengths ascending, then symbols ascending within
    each length group).

    Mirrors the escape-prefix shift in ``_build_huff_table``: when the
    ``max_len`` group has 3 or more unused code slots the first two positions
    are reserved (code advances by 2 before symbol assignment), exactly as
    SQL Server's encoder does.  This keeps the builder's bitstream consistent
    with what ``_build_huff_table`` / ``_huff_decode_page_py`` expect.
    """
    by_len: dict[int, list[int]] = {}
    max_len = max(code_lens.values(), default=0)
    for sym, cl in code_lens.items():
        if cl > 0:
            by_len.setdefault(cl, []).append(sym)

    n_max_syms = len(by_len.get(max_len, []))
    code = 0
    result: dict[int, tuple[int, int]] = {}
    for cl in range(1, max_len + 1):
        if cl == max_len:
            n_available = (1 << max_len) - code
            if n_available - n_max_syms >= 3:
                code += 2  # reserve escape-prefix slots (mirrors _build_huff_table)
        for sym in sorted(by_len.get(cl, [])):
            result[sym] = (cl, code)
            code += 1
        code <<= 1
    return result


def make_huffman_page(
    strings: list[bytes],
    code_lens: dict[int, int],
) -> tuple[bytes, bytes, list[int], int]:
    """Build a synthetic xVelocity v4 Huffman-compressed page.

    *strings*: list of raw byte strings (Huffman symbols, no +OFF applied).
    *code_lens*: ``{symbol: code_length}`` for every byte value in *strings*.

    Returns ``(encode_array_128, bitstream, offsets, store_total_bits)`` ready
    for direct input to ``_build_huff_table`` and
    ``_huff_decode_page_py(..., cbuf_off=0)``.

    The bitstream is produced in the pre-swap wire format expected by
    ``_huff_decode_page_py``, which internally swaps each adjacent byte pair
    (``swap=True`` convention, also used by ``xmhuffman.decode_page``).
    """
    codes = canonical_codes(code_lens)
    encode_array = make_encode_array(code_lens)

    max_bits = sum(code_lens[b] for s in strings for b in s) + 16
    n_bytes = (max_bits + 7) // 8 + 4
    if n_bytes % 2:
        n_bytes += 1
    swapped = bytearray(n_bytes)

    bit_pos = 0
    offsets: list[int] = []
    for string in strings:
        offsets.append(bit_pos)
        for sym in string:
            cl, code = codes[sym]
            for shift in range(cl - 1, -1, -1):
                if (code >> shift) & 1:
                    byte_i = bit_pos >> 3
                    bit_in_byte = bit_pos & 7
                    swapped[byte_i] |= 1 << (7 - bit_in_byte)
                bit_pos += 1
    stb = bit_pos

    # Reverse the byte-pair swap to produce the wire-format bitstream.
    wire = bytearray(swapped)
    for i in range(0, len(wire) - 1, 2):
        wire[i], wire[i + 1] = wire[i + 1], wire[i]

    return encode_array, bytes(wire), offsets, stb


def auto_code_lens(buffers: list[bytes]) -> dict[int, int]:
    """Assign equal code lengths to cover every byte value in *buffers*.

    Uses ``ceil(log2(n_symbols))`` so all symbols get the same code length.
    For a power-of-2 symbol count this gives Kraft sum = 1.0 (full tree,
    accepted by xmhuffman).  For other counts the tree is underfull (Kraft < 1)
    and is decoded by the Python fallback path.
    """
    symbols = sorted({b for buf in buffers for b in buf})
    n = len(symbols)
    if n == 0:
        return {}
    cl = max(1, math.ceil(math.log2(max(n, 2))))
    return {sym: cl for sym in symbols}


def format_b_record(content: str) -> bytes:
    """Build a Format B record buffer for *content*.

    Wire format: ``[slen + OFF][chr(c) + OFF for c in content]``.
    Requires ``len(content) < 0x80`` so slen fits in the low-7-bit range.
    This is the simplest non-escape record shape emitted by SQL Server for
    short VARCHAR values.

    .. note::
        When this record is decoded by the Python fallback path
        (``_split_v4_record(..., from_python_fallback=True)``), content of
        exactly **6 characters** triggers a special-case branch
        (``r[0] == 8``) that treats ``r[1]`` as an overhead byte and returns
        ``r[2:]``, yielding one character fewer than expected.  This is a
        real-wire-format heuristic in ``_split_v4_record``; avoid 6-char
        strings when constructing Huffman pages whose tree will be rejected by
        xmhuffman (i.e. underfull trees with non-power-of-2 symbol counts).
    """
    OFF = _V4_CHAR_OFFSET
    payload = bytes(ord(c) + OFF for c in content)
    if len(payload) >= 0x80:
        raise ValueError(
            f"content too long for Format B ({len(payload)} ≥ 128 chars); "
            "use format_a_record for longer strings"
        )
    return bytes([len(payload) + OFF]) + payload


def format_a_record(content: str) -> bytes:
    """Build a Format A record buffer for *content* (2-byte overhead).

    Wire format: ``[slen+OFF][0x82][chr(c)+OFF for c in content]``
    where slen = len(content) and ``0x82`` is the standard metadata byte.
    Requires ``len(content) >= 0x80`` so ``decoded0 >= 0x80`` (the condition
    that selects Format A in ``_split_v4_record``).
    """
    OFF = _V4_CHAR_OFFSET
    payload = bytes(ord(c) + OFF for c in content)
    if len(payload) < 0x80:
        raise ValueError(
            f"content too short for Format A ({len(payload)} < 128 chars); "
            "use format_b_record instead"
        )
    return bytes([len(payload) + OFF, 0x82]) + payload


# ---------------------------------------------------------------------------
# V4DictBuilder
# ---------------------------------------------------------------------------


@dataclass
class _PageRecord:
    page_type: str          # "huffman" or "lp"
    page_bytes: bytes       # encoded deint bytes for this page
    handle_offsets: list[int]   # per-handle bit/byte offset stored in RH


class V4DictBuilder:
    """Construct synthetic ``(raw, deint)`` pairs for ``_decode_v4_huff_dict``.

    Usage::

        builder = V4DictBuilder()
        builder.add_huffman_page(["Hello", "World"])
        raw, deint = builder.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == ["Hello", "World"]

    Or with LP pool (including the 0x80 metadata byte fix)::

        builder = V4DictBuilder()
        builder.add_lp_page(["foo", "bar"], with_meta_byte=True)
        raw, deint = builder.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == ["foo", "bar"]

    Limitations:

    - Total deint size must stay under 65 536 bytes (one LOB chunk; no
      separator handling needed).
    - ``add_huffman_page`` only emits Format B records.  For Format A or
      custom record shapes use ``add_huffman_page_raw``.
    - One decoded string per handle (CHAR(n) multi-string packing not
      supported by this builder; that path is covered by the
      Group S1 tests in ``test_decode_synthetic.py``).
    """

    def __init__(self) -> None:
        self._pages: list[_PageRecord] = []
        self._n_strings: int = 0

    @property
    def n_pages(self) -> int:
        """Number of pages added so far."""
        return len(self._pages)

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def add_huffman_page(self, strings: list[str]) -> None:
        """Encode *strings* as Format B records and append a Huffman page.

        Shorthand for ``add_huffman_page_raw([format_b_record(s) for s in strings])``.
        All strings must be < 128 characters (Format B constraint).
        """
        self.add_huffman_page_raw([format_b_record(s) for s in strings])

    def add_huffman_page_raw(self, record_bufs: list[bytes]) -> None:
        """Append a Huffman page from pre-built record byte buffers.

        The Huffman tree is derived automatically from the byte values present
        in *record_bufs* via ``auto_code_lens``.  For an underfull tree
        (non-power-of-2 symbol count) ``_decode_v4_huff_dict`` falls back to
        the Python decoder automatically.
        """
        cl = auto_code_lens(record_bufs)
        ea, bitstream, offsets, stb = make_huffman_page(record_bufs, cl)

        hdr = bytearray(_V4_PAGE_HDR_SZ)
        struct.pack_into("<I", hdr, _V4_STB_OFF_IN_HDR, stb)
        hdr[_V4_EA_OFF_IN_HDR : _V4_EA_OFF_IN_HDR + 128] = ea

        page_bytes = bytes(hdr) + bitstream
        self._pages.append(_PageRecord("huffman", page_bytes, offsets))
        self._n_strings += len(record_bufs)

    def add_lp_page(
        self,
        strings: list[str],
        *,
        with_meta_byte: bool = False,
    ) -> None:
        """Encode *strings* as LP pool entries and append an LP pool page.

        If *with_meta_byte* is ``True``, each entry is written as
        ``[length][0x80][content]``, exercising the ``_read_lp_entry`` 0x80
        metadata byte fix.  If ``False`` (default) each entry is plain
        ``[length][content]``.
        """
        pool = bytearray()
        handle_offsets: list[int] = []
        for s in strings:
            handle_offsets.append(len(pool))
            content = s.encode("latin-1")
            pool.append(len(content))
            if with_meta_byte:
                pool.append(0x80)
            pool.extend(content)

        hdr = struct.pack("<II", 0, len(pool))  # stb=0, pool_size
        page_bytes = hdr + bytes(pool)
        self._pages.append(_PageRecord("lp", page_bytes, handle_offsets))
        self._n_strings += len(strings)

    # ------------------------------------------------------------------
    # Binary assembly
    # ------------------------------------------------------------------

    def build(self) -> tuple[bytes, bytes]:
        """Assemble and return ``(raw, deint)`` for ``_decode_v4_huff_dict``.

        The returned ``raw`` is ``b'\\x00' * 12 + bytes(deint)``, which is
        valid for blobs that fit within one 65 536-byte LOB chunk.
        """
        page_count = len(self._pages)
        n_data_ids = self._n_strings

        deint = bytearray()

        # Bytes 0-3: placeholder (not read by the decoder).
        deint.extend(b"\x00" * 4)
        # Bytes 4-7: n_data_ids - 1.
        deint.extend(struct.pack("<I", n_data_ids - 1))
        # Bytes 8-63: padding (not read).
        deint.extend(b"\x00" * 56)
        # Bytes 64-67: page_count.
        deint.extend(struct.pack("<I", page_count))

        # Record-handle array: (bit_offset/byte_offset u32, page_id u32) per handle.
        for pid, page in enumerate(self._pages):
            for offset in page.handle_offsets:
                deint.extend(struct.pack("<II", offset, pid))

        # Page directory: raw byte length of each page.
        # For blobs fitting in one LOB chunk, raw length == deint length.
        for page in self._pages:
            deint.extend(struct.pack("<I", len(page.page_bytes)))

        # 16-byte gap between directory and first page header.
        deint.extend(b"\x00" * _V4_PAGE_GAP_BASE)

        # Page headers + data.
        for page in self._pages:
            deint.extend(page.page_bytes)

        # raw = 12-byte LOB preamble + deint bytes.
        raw = b"\x00" * _LOB_PREAMBLE + bytes(deint)
        return raw, bytes(deint)
