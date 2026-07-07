"""End-to-end tests for _decode_v4_huff_dict using synthetic binary fixtures.

All (raw, deint) pairs are constructed by V4DictBuilder — no .bak or .pbix
files required.  Each test exercises a specific code path that was either a
historical bug (from tpcxbb_1gb.bak) or an important boundary condition.

Group E1 — Single Huffman page
    Basic round-trip: strings → Format B records → Huffman page → decode.

Group E2 — Single LP pool page (plain)
    LP pool with plain length-prefixed entries.

Group E3 — LP pool with 0x80 metadata byte (regression: tpcxbb_1gb.bak fix)
    Each LP entry has a 0x80 metadata byte between the length and the content.
    The fix (in _read_lp_entry) must skip the metadata byte and return only
    the true content.

Group E4 — Mixed page (Huffman + LP)
    One Huffman page followed by one LP page in the same dictionary.  Exercises
    the mixed-dict path where lp_strs_by_k is populated separately from
    raw_by_k and merged in the reconstruction loop.

Group E5 — Underfull Huffman tree (Python fallback path)
    Symbol count that is not a power of 2 produces an underfull tree (Kraft < 1)
    that xmhuffman rejects.  The decoder must fall back to _huff_decode_page_py
    and still return the correct strings.
"""
from __future__ import annotations

from mssqlbak.columnstore.decode.dict_xvelocity import _decode_v4_huff_dict
from tests._v4_builder import V4DictBuilder, format_a_record


# ---------------------------------------------------------------------------
# Group E1 — Single Huffman page
# ---------------------------------------------------------------------------


class TestSingleHuffmanPage:
    def test_two_strings(self) -> None:
        b = V4DictBuilder()
        b.add_huffman_page(["Hello", "World"])
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == ["Hello", "World"]

    def test_single_string(self) -> None:
        b = V4DictBuilder()
        b.add_huffman_page(["abc"])
        raw, deint = b.build()
        assert _decode_v4_huff_dict(raw, deint) == ["abc"]

    def test_many_strings(self) -> None:
        # Avoid 6-char strings: the Python-fallback path in _split_v4_record
        # has a special case for r[0]==8 (slen=6) that treats r[1] as an
        # overhead byte.  That heuristic is correct for real .bak data but
        # produces one dropped character for synthetic Format B records.
        words = ["apple", "bana", "cherries", "day", "elderberry", "fig", "grape"]
        b = V4DictBuilder()
        b.add_huffman_page(words)
        raw, deint = b.build()
        assert _decode_v4_huff_dict(raw, deint) == words

    def test_strings_with_spaces_and_punctuation(self) -> None:
        strings = ["Hello, World!", "foo bar", "test_123"]
        b = V4DictBuilder()
        b.add_huffman_page(strings)
        raw, deint = b.build()
        assert _decode_v4_huff_dict(raw, deint) == strings

    def test_format_a_record(self) -> None:
        """Format A records (≥128-char strings) decoded end-to-end."""
        long_str = "A" * 128
        b = V4DictBuilder()
        b.add_huffman_page_raw([format_a_record(long_str)])
        raw, deint = b.build()
        assert _decode_v4_huff_dict(raw, deint) == [long_str]


# ---------------------------------------------------------------------------
# Group E2 — LP pool, plain entries
# ---------------------------------------------------------------------------


class TestLpPoolPlain:
    def test_two_strings(self) -> None:
        b = V4DictBuilder()
        b.add_lp_page(["alpha", "beta"])
        raw, deint = b.build()
        assert _decode_v4_huff_dict(raw, deint) == ["alpha", "beta"]

    def test_single_string(self) -> None:
        b = V4DictBuilder()
        b.add_lp_page(["only"])
        raw, deint = b.build()
        assert _decode_v4_huff_dict(raw, deint) == ["only"]

    def test_latin1_characters(self) -> None:
        """Latin-1 code points above 0x7F round-trip via LP pool."""
        strings = ["caf\xe9", "na\xefve", "r\xe9sum\xe9"]
        b = V4DictBuilder()
        b.add_lp_page(strings)
        raw, deint = b.build()
        assert _decode_v4_huff_dict(raw, deint) == strings


# ---------------------------------------------------------------------------
# Group E3 — LP pool with 0x80 metadata byte (tpcxbb_1gb.bak regression)
# ---------------------------------------------------------------------------


class TestLpPool0x80MetadataByte:
    """Regression tests for the LP pool 0x80 metadata byte fix.

    Bug: SQL Server writes [length][0x80][content] in the LP pool, but the
    original code read [length], then treated 0x80 as the first content byte,
    producing b'\\x80' + real_content (the value '\x80FUNNY PEOPLE...' that
    appeared in got_only errors on tpcxbb_1gb.bak).

    Fix: _read_lp_entry detects 0x80 at raw_pos+1 and skips it.
    """

    def test_single_string_with_meta_byte(self) -> None:
        b = V4DictBuilder()
        b.add_lp_page(["Hello"], with_meta_byte=True)
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == ["Hello"], (
            f"0x80 metadata byte was not skipped; got {result!r}"
        )

    def test_multiple_strings_with_meta_byte(self) -> None:
        strings = ["FUNNY PEOPLE", "test string", "another one"]
        b = V4DictBuilder()
        b.add_lp_page(strings, with_meta_byte=True)
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == strings

    def test_meta_byte_does_not_corrupt_0x80_prefixed_content(self) -> None:
        """Without the fix the first char would be '\\x80'; with the fix it's 'F'."""
        b = V4DictBuilder()
        b.add_lp_page(["FUNNY PEOPLE are not real"], with_meta_byte=True)
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result is not None
        assert result[0].startswith("F"), (
            f"expected result to start with 'F', got {result[0]!r}"
        )
        assert "\x80" not in result[0], "0x80 byte leaked into decoded string"

    def test_plain_and_meta_pages_give_same_strings(self) -> None:
        """LP entries with and without 0x80 metadata must decode identically."""
        strings = ["alpha", "beta", "gamma"]
        b_plain = V4DictBuilder()
        b_plain.add_lp_page(strings, with_meta_byte=False)
        r_plain = _decode_v4_huff_dict(*b_plain.build())

        b_meta = V4DictBuilder()
        b_meta.add_lp_page(strings, with_meta_byte=True)
        r_meta = _decode_v4_huff_dict(*b_meta.build())

        assert r_plain == strings
        assert r_meta == strings
        assert r_plain == r_meta


# ---------------------------------------------------------------------------
# Group E4 — Mixed Huffman + LP dictionary
# ---------------------------------------------------------------------------


class TestMixedHuffmanAndLpPages:
    """Exercises the mixed-dict path: some handles on a Huffman page, others
    on an LP pool page.  SQL Server occasionally emits these in production
    (observed in tpcxbb_1gb.bak pr_review_content: 53 Huffman pages + 1 LP).
    """

    def test_huffman_then_lp(self) -> None:
        """Two pages: page 0 Huffman, page 1 LP (plain)."""
        b = V4DictBuilder()
        b.add_huffman_page(["from_huffman_A", "from_huffman_B"])
        b.add_lp_page(["from_lp_C", "from_lp_D"])
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == ["from_huffman_A", "from_huffman_B", "from_lp_C", "from_lp_D"]

    def test_huffman_then_lp_with_meta_byte(self) -> None:
        """Mixed dict where the LP page uses 0x80 metadata bytes."""
        b = V4DictBuilder()
        b.add_huffman_page(["huff_str"])
        b.add_lp_page(["lp_str_with_meta"], with_meta_byte=True)
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == ["huff_str", "lp_str_with_meta"]

    def test_two_huffman_pages(self) -> None:
        b = V4DictBuilder()
        b.add_huffman_page(["page0_A", "page0_B"])
        b.add_huffman_page(["page1_C", "page1_D"])
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == ["page0_A", "page0_B", "page1_C", "page1_D"]


# ---------------------------------------------------------------------------
# Group E5 — Underfull Huffman tree (Python fallback path)
# ---------------------------------------------------------------------------


class TestUnderfullHuffmanTree:
    """When the symbol count is not a power of 2, auto_code_lens produces an
    underfull tree (Kraft sum < 1.0).  xmhuffman rejects underfull trees and
    raises an exception; _decode_v4_huff_dict falls back to the Python decoder.

    This path is where all the escape-prefix / TAIL_OVER bugs lived.
    """

    @staticmethod
    def _underfull_strings() -> list[str]:
        """Strings that guarantee an underfull tree.

        3 unique characters → 3 symbols → underfull tree at cl=2 (Kraft=3/4).
        """
        return ["abc", "bca", "cab"]

    def test_decode_with_underfull_tree(self) -> None:
        strings = self._underfull_strings()
        b = V4DictBuilder()
        b.add_huffman_page(strings)
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result == strings

    def test_underfull_result_contains_no_garbage(self) -> None:
        """Python fallback must not over-read into padding bytes."""
        strings = ["xy", "yz", "zx"]  # 3 symbols → underfull
        b = V4DictBuilder()
        b.add_huffman_page(strings)
        raw, deint = b.build()
        result = _decode_v4_huff_dict(raw, deint)
        assert result is not None
        for expected, got in zip(strings, result):
            assert got == expected, f"expected {expected!r}, got {got!r}"
