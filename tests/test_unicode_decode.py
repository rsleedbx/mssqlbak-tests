"""Unit tests for _decode_char and _decode_nchar in mssqlbak.types.

These functions are the first line of defence against bad bytes in varchar/char
and nvarchar/nchar columns respectively.  The tests here cover every class of
failure observed or anticipated:

_decode_char
------------
* cp1252 has five undefined byte values: 0x81, 0x8D, 0x8F, 0x90, 0x9D.
  Any of these in a varchar column (e.g. copied from a Cyrillic or Japanese
  source) previously crashed the extraction.  The fix retries with
  errors='replace', then normalises the U+FFFD Python emits to the literal
  '?' (U+003F) that SQL Server's code-page conversion produces, so cell
  digests agree with the live-server ground truth.  (G54)
* UTF-8 collation flag: varchar columns with a _UTF8 collation store bytes as
  UTF-8, not cp1252.  Invalid UTF-8 bytes also fall back to '?'.

_decode_nchar
-------------
* Odd byte length → Always Encrypted ciphertext → None.  (G53)
* Even byte length but invalid UTF-16-LE (e.g. lone high surrogate) → None.
* Valid UTF-16-LE, including surrogate pairs for astral code points → str.
"""
from __future__ import annotations

import pytest

from mssqlbak.types import _codec_for_collation, _decode_char, _decode_nchar


# ---------------------------------------------------------------------------
# _codec_for_collation — collation_id → Python codec name
# ---------------------------------------------------------------------------

class TestCodecForCollation:
    """Verify the known collation_id → codec mapping rules.

    Collation_id values are empirically verified from ``unicode_codepage_coverage.bak``
    (SQL Server 2022).  The format is:
      bits 0–7  : SQL Server Sort Order ID (SORTID) → code page
      bit  8    : UTF-8 flag (0x100) → return "utf-8"
      bits 9–31 : sensitivity flags / version (ignored)
    """

    # Verified against SQL Server 2022 (empirical sources shown).
    # GeneralHospital.bak (database-default collation row has upper 0x3400 set):
    LATIN1_GENERAL_CI_AS = 0x3400D008
    # unicode_codepage_coverage.bak (column-level collations, upper bits = 0):
    CYRILLIC_GENERAL_CI_AS = 0x0000D015
    GREEK_CI_AS            = 0x0000D007
    TURKISH_CI_AS          = 0x0000D01A
    HEBREW_CI_AS           = 0x0000D00C
    ARABIC_CI_AS           = 0x0000D001
    LITHUANIAN_CI_AS       = 0x0000D01F
    VIETNAMESE_CI_AS       = 0x0000D020
    THAI_CI_AS             = 0x0000D019
    JAPANESE_CI_AS         = 0x0000D010
    CHINESE_PRC_CI_AS      = 0x0000D024
    KOREAN_WANSUNG_CI_AS   = 0x0000D011
    CHINESE_TAIWAN_CI_AS   = 0x0000D003
    POLISH_CI_AS           = 0x0000D013

    def test_zero_collation_defaults_to_cp1252(self) -> None:
        # Non-string columns have collation_id=0; SORTID=0 not in table → cp1252.
        assert _codec_for_collation(0) == "cp1252"

    def test_latin1_general_ci_as_is_cp1252(self) -> None:
        # SORTID=0x08 → cp1252 (both database-default and column-level variants).
        assert _codec_for_collation(self.LATIN1_GENERAL_CI_AS) == "cp1252"
        assert _codec_for_collation(0x0000D008) == "cp1252"

    def test_utf8_flag_bit8_returns_utf8(self) -> None:
        # Any collation_id with bit 8 (0x100) set is a _SC_UTF8 collation.
        assert _codec_for_collation(0x100) == "utf-8"
        assert _codec_for_collation(self.LATIN1_GENERAL_CI_AS | 0x100) == "utf-8"

    def test_utf8_flag_does_not_bleed_into_other_bits(self) -> None:
        # Bit 7 (0x80) must NOT trigger the UTF-8 path.
        assert _codec_for_collation(0x080) == "cp1252"
        # Bit 9 (0x200) must NOT trigger the UTF-8 path.
        assert _codec_for_collation(0x200) == "cp1252"

    def test_ae_bin2_collation_id_defaults_to_cp1252(self) -> None:
        # AE columns use BIN2 collation IDs < 0x10000 (e.g. 2056 = 0x808).
        # SORTID=0x08 → cp1252.  _dv_char returns None before this is used.
        assert _codec_for_collation(2056) == "cp1252"

    # ── SBCS non-cp1252 collations (empirical, unicode_codepage_coverage.bak) ──

    @pytest.mark.parametrize("collation_id,expected_codec", [
        (CYRILLIC_GENERAL_CI_AS, "cp1251"),
        (GREEK_CI_AS,            "cp1253"),
        (TURKISH_CI_AS,          "cp1254"),
        (HEBREW_CI_AS,           "cp1255"),
        (ARABIC_CI_AS,           "cp1256"),
        (LITHUANIAN_CI_AS,       "cp1257"),
        (VIETNAMESE_CI_AS,       "cp1258"),
        (THAI_CI_AS,             "cp874"),
        (POLISH_CI_AS,           "cp1250"),
    ])
    def test_sbcs_collation_to_codec(self, collation_id: int, expected_codec: str) -> None:
        assert _codec_for_collation(collation_id) == expected_codec

    # ── DBCS (double-byte) collations ─────────────────────────────────────────

    @pytest.mark.parametrize("collation_id,expected_codec", [
        (JAPANESE_CI_AS,       "cp932"),
        (CHINESE_PRC_CI_AS,    "cp936"),
        (KOREAN_WANSUNG_CI_AS, "cp949"),
        (CHINESE_TAIWAN_CI_AS, "cp950"),
    ])
    def test_dbcs_collation_to_codec(self, collation_id: int, expected_codec: str) -> None:
        assert _codec_for_collation(collation_id) == expected_codec

    def test_upper_bits_do_not_affect_sortid(self) -> None:
        # The 0x3400 upper bits on the database-default Latin1 row must not
        # change the codec relative to the column-level variant (SORTID=0x08).
        assert _codec_for_collation(0x3400D008) == _codec_for_collation(0x0000D008)
        # Same for Cyrillic: upper bits stripped → still cp1251.
        assert _codec_for_collation(0x3400D015) == "cp1251"


# ---------------------------------------------------------------------------
# _decode_char — cp1252 (non-UTF-8 path)
# ---------------------------------------------------------------------------

class TestDecodeCharCp1252:
    def test_ascii_passthrough(self) -> None:
        assert _decode_char(b"hello world") == "hello world"

    def test_empty(self) -> None:
        assert _decode_char(b"") == ""

    @pytest.mark.parametrize("b", [0x81, 0x8D, 0x8F, 0x90, 0x9D])
    def test_undefined_cp1252_byte_yields_replacement(self, b: int) -> None:
        """Each of the 5 cp1252-undefined bytes should map to '?', not crash.

        SQL Server's code-page conversion emits the literal '?' (U+003F) for a
        byte that has no code-page representation, so mssqlbak normalises the
        U+FFFD from Python's errors='replace' to '?' to match cell digests.
        """
        result = _decode_char(bytes([b]))
        assert result == "?", f"byte 0x{b:02X} should map to '?'"

    def test_undefined_byte_mid_string_replaces_only_bad_byte(self) -> None:
        # 0x41='A', 0x8F=undefined, 0x42='B'
        assert _decode_char(bytes([0x41, 0x8F, 0x42])) == "A?B"

    def test_multiple_undefined_bytes(self) -> None:
        payload = bytes([0x81, 0x8D, 0x8F, 0x90, 0x9D])
        result = _decode_char(payload)
        assert result == "?" * 5

    def test_valid_cp1252_extended_chars(self) -> None:
        # 0x80=€, 0x82=‚, 0xA3=£ — all defined in cp1252
        assert _decode_char(bytes([0x80, 0x82, 0xA3])) == "€‚£"

    def test_0x8f_is_cyrillic_dzhe_in_cp1251(self) -> None:
        # 0x8F maps to Cyrillic 'Џ' (U+040F) in cp1251 but is undefined in cp1252.
        # We decode as cp1252 and replace — not mis-decode as a different encoding.
        result = _decode_char(bytes([0x8F]))
        assert result == "?"

    def test_all_defined_high_bytes_roundtrip(self) -> None:
        undefined = {0x81, 0x8D, 0x8F, 0x90, 0x9D}
        for b in range(0x80, 0x100):
            if b in undefined:
                continue
            raw = bytes([b])
            decoded = _decode_char(raw)
            # Must not crash and must not be a substituted replacement character.
            assert decoded not in ("\ufffd", "?"), (
                f"byte 0x{b:02X} is defined in cp1252 but got a replacement char"
            )
            # Must round-trip through cp1252.
            assert decoded.encode("cp1252") == raw


# ---------------------------------------------------------------------------
# _decode_char — UTF-8 collation path (encoding="utf-8")
# ---------------------------------------------------------------------------

class TestDecodeCharUtf8:
    def test_ascii_utf8(self) -> None:
        assert _decode_char(b"hello", encoding="utf-8") == "hello"

    def test_multibyte_utf8(self) -> None:
        raw = "héllo".encode("utf-8")
        assert _decode_char(raw, encoding="utf-8") == "héllo"

    def test_cjk_utf8(self) -> None:
        raw = "日本語".encode("utf-8")
        assert _decode_char(raw, encoding="utf-8") == "日本語"

    def test_invalid_utf8_byte_yields_replacement(self) -> None:
        # 0xFF is never valid in UTF-8; the U+FFFD is normalised to '?'.
        result = _decode_char(bytes([0x41, 0xFF, 0x42]), encoding="utf-8")
        assert result == "A?B"

    def test_truncated_utf8_sequence_yields_replacement(self) -> None:
        # é (U+00E9) encodes as 0xC3 0xA9 in UTF-8; 0xC3 alone is invalid.
        result = _decode_char(bytes([0x41, 0xC3]), encoding="utf-8")
        assert result == "A?"

    def test_empty_utf8(self) -> None:
        assert _decode_char(b"", encoding="utf-8") == ""


# ---------------------------------------------------------------------------
# _decode_nchar — nchar/nvarchar (UTF-16-LE) path
# ---------------------------------------------------------------------------

class TestDecodeNchar:
    def test_empty_returns_empty_string(self) -> None:
        assert _decode_nchar(b"") == ""

    def test_ascii_utf16le(self) -> None:
        raw = "hello".encode("utf-16-le")
        assert _decode_nchar(raw) == "hello"

    def test_multibyte_bmp(self) -> None:
        raw = "日本語".encode("utf-16-le")
        assert _decode_nchar(raw) == "日本語"

    def test_surrogate_pair_astral(self) -> None:
        # 😀 = U+1F600; UTF-16-LE surrogate pair: D83D DE00
        raw = "😀".encode("utf-16-le")
        assert _decode_nchar(raw) == "😀"

    # --- AE / invalid cases ------------------------------------------------

    def test_odd_length_returns_none(self) -> None:
        """One-byte input: impossible for UTF-16-LE → AE or corruption → None."""
        assert _decode_nchar(b"\x01") is None

    def test_odd_length_three_bytes_returns_none(self) -> None:
        assert _decode_nchar(b"\x01\x02\x03") is None

    def test_ae_minimum_size_returns_none(self) -> None:
        # AE minimum ciphertext: 1 version + 32 auth tag + 16 IV = 49 bytes (odd).
        fake_ae = b"\x01" + b"\xaa" * 48
        assert len(fake_ae) == 49
        assert _decode_nchar(fake_ae) is None

    def test_lone_high_surrogate_returns_none(self) -> None:
        # U+D800 as a standalone (no trailing low surrogate) is invalid UTF-16-LE.
        raw = b"\x00\xD8"   # D800 LE
        assert _decode_nchar(raw) is None

    def test_lone_low_surrogate_returns_none(self) -> None:
        # U+DC00 without a preceding high surrogate is invalid UTF-16-LE.
        raw = b"\x00\xDC"   # DC00 LE
        assert _decode_nchar(raw) is None

    def test_high_surrogate_without_low_returns_none(self) -> None:
        # Two high surrogates in a row are not a valid UTF-16-LE pair.
        raw = b"\x3D\xD8\x3D\xD8"  # D83D D83D
        assert _decode_nchar(raw) is None

    def test_valid_string_after_odd_bytes_detected_first(self) -> None:
        # Build a payload that would decode fine as UTF-16-LE if it were even,
        # but is made odd by a one-byte suffix — ensure None is returned.
        raw = "hello".encode("utf-16-le") + b"\x00"
        assert len(raw) % 2 == 1
        assert _decode_nchar(raw) is None


# ---------------------------------------------------------------------------
# _dv_char / _dv_nchar — Always Encrypted guard at dispatcher level
# ---------------------------------------------------------------------------

class TestDispatcherAEGuard:
    """_dv_char and _dv_nchar must preserve ciphertext when encrypted.

    _dv_nchar was already guarded (G53).  _dv_char was not — AE ciphertext in
    a varchar/char column would produce garbage U+FFFD strings instead of stable
    ciphertext text.
    """

    def _make_col(self, *, is_encrypted: bool, collation_id: int = 0) -> object:
        class _FakeCol:
            pass
        col = _FakeCol()
        col.is_encrypted = is_encrypted  # type: ignore[attr-defined]
        col.collation_id = collation_id  # type: ignore[attr-defined]
        return col

    def test_dv_nchar_ae_column_returns_ciphertext_repr(self) -> None:
        from mssqlbak.types import _dv_nchar
        col = self._make_col(is_encrypted=True)
        raw = b"\x01" + b"\xaa" * 48
        assert _dv_nchar(raw, col) == repr(raw)

    def test_dv_nchar_non_ae_column_decodes_normally(self) -> None:
        from mssqlbak.types import _dv_nchar
        col = self._make_col(is_encrypted=False)
        raw = "hello".encode("utf-16-le")
        assert _dv_nchar(raw, col) == "hello"

    def test_dv_char_ae_column_returns_ciphertext_repr(self) -> None:
        """AE-encrypted varchar column: _dv_char must return ciphertext text."""
        from mssqlbak.types import _dv_char
        col = self._make_col(is_encrypted=True, collation_id=2056)  # BIN2
        # AE ciphertext will contain cp1252-undefined bytes; without the guard
        # _decode_char would mangle them to U+FFFD strings instead of preserving bytes.
        ae_payload = b"\x01" + b"\x8f" * 32 + b"\x81" * 16 + b"\x9d" * 32
        assert _dv_char(ae_payload, col) == repr(ae_payload)

    def test_dv_char_non_ae_column_decodes_normally(self) -> None:
        from mssqlbak.types import _dv_char
        col = self._make_col(is_encrypted=False, collation_id=0)
        assert _dv_char(b"hello", col) == "hello"

    def test_dv_char_non_ae_utf8_column_decodes_normally(self) -> None:
        from mssqlbak.types import _dv_char
        col = self._make_col(is_encrypted=False, collation_id=0x100)  # UTF-8 flag
        raw = "héllo".encode("utf-8")
        assert _dv_char(raw, col) == "héllo"
