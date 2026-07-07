"""Unit tests for SCSU (Unicode compression) expansion.

Byte vectors are the Unicode TR6 reference samples (also used by OrcaSql's
``ScsuExpanderTests``) plus the SQL-Server-specific trailing ``0x10`` select-
window-0 byte that the engine appends to compressed string values.
"""
from __future__ import annotations

import pytest

from mssqlbak import scsu
from mssqlbak.scsu import ScsuError


@pytest.mark.parametrize(
    "hexbytes, expected",
    [
        ("", ""),
        ("61", "a"),                       # ASCII passthrough
        ("313233", "123"),
        # 10x U+0468 (Cyrillic): SC2 (0x12) selects Cyrillic window, then 0x68+
        ("12E8E8E8E8E8E8E8E8E8E8", "\u0468" * 10),
        # SQL Server appends a trailing 0x10 (SC0, no-op) to many values.
        ("3132333435363738393010", "1234567890"),
        ("47726179" "10", "Gray"),         # the WideWorldImporters Colors case
        ("20" * 20 + "10", " " * 20),
        # Reference mixed-script samples (exercise quote / window definition).
        (
            "416E2065 78616D70 6C652073 656E7465 6E636520 776F756C "
            "64207368 6F772077 68617420 74686973 20776F72 64206D65 616E73",
            "An example sentence would show what this word means",
        ),
        ("08DE15A782CC08DEA782CC", "\uff5e\u3067\u3042\u308c\uff5e\u3067\u3042\u308c"),
        # UC0 (0xE0) as the terminal byte in Unicode-mode: a valid switch-back
        # to dynamic window 0 that ends the stream.  SQL Server emits this
        # pattern for some nvarchar values (e.g. in the StackOverflow Users
        # table); the expander must not raise ScsuError here.
        ("0F0041E0", "A"),           # SCU 'A' UC0
        ("0F0041004200430044E0", "ABCD"),  # SCU "ABCD" UC0
        # Arbitrary trailing bytes in Unicode mode (G54 — any single byte is a
        # no-op because it cannot form a complete UTF-16 big-endian pair).
        # 0x02 (SQ1 in single-byte mode) was the observed failing byte in the
        # StackOverflowMini.bak Users table (stream 43 00 0f 1d 80 02 8f 02).
        ("0F 0041 02", "A"),         # SCU 'A' trailing-0x02
        ("0F 0041 01", "A"),         # SCU 'A' trailing-0x01
        ("0F 0041 10", "A"),         # SCU 'A' trailing-0x10 (SC0, common case)
        ("0F 0041 7F", "A"),         # SCU 'A' trailing-0x7F
        ("0F 0041 DF", "A"),         # SCU 'A' trailing-0xDF (edge: last two-byte pair leader)
        # The exact StackOverflowMini.bak Users byte sequence (G54 fixture).
        # 0x43='C'; 0x00=U+0000; 0x0F=SCU; 0x1D80=Unicode pair; 0x028F=Unicode pair;
        # trailing 0x02 silently discarded.
        (
            "43 00 0F 1D80 028F 02",
            "C\x00\u1d80\u028f",
        ),
        # --- Astral code points (> U+FFFF) via extended window definition ------
        # SDX (0x0B) + 2-byte value 0x0000 → dynamic[0] = ((0 & 0x1FFF)<<7) + 0x10000
        # = 0x10000.  Byte 0x80 in the active window: ch = 0 + 0x10000 = U+10000.
        # _emit_code_point splits U+10000 into surrogate pair D800+DC00.
        # U+10000 = "𐀀" (Linear B Syllable B008 A).
        ("0B 0000 80", "\U00010000"),
        # Same extended window, byte 0x81 → U+10001 = "𐀁".
        ("0B 0000 81", "\U00010001"),
        # Two consecutive astral code points via one SDX (window remains active).
        ("0B 0000 80 81", "\U00010000\U00010001"),
        # --- Astral code point via SCSU Unicode mode (surrogate pair in stream) --
        # U+1F600 = 😀.  UTF-16-LE: D83D DC00 → WRONG; actually: D83D DE00.
        # In SCSU Unicode mode, bytes are big-endian pairs: D8 3D DE 00.
        # The expander emits D83D then DE00 as raw code units; UTF-16-LE then
        # decodes the surrogate pair correctly.
        ("0F D83D DE00", "\U0001F600"),   # 😀 via Unicode mode
        # --- UDX / UQU truncation in Unicode mode: no crash, no output ---------
        # UDX (0xF1) as the very last byte of a Unicode-mode run.  The while loop
        # exits because index == n-1; the trailing-byte handler skips 0xF1.
        ("0F F1", ""),
        # UDX with one orphan byte: both skipped by the n-2 guard.
        ("0F F1 00", ""),
        # UDX with a full 2-byte operand: defines a window and switches back to
        # single-byte mode.  Window = (0x0000 >> 13) = 0; offset at 0x10000.
        # No subsequent bytes → empty output.
        ("0F F1 00 00", ""),
        # UQU (0xF0) as the very last byte of a Unicode-mode run.
        ("0F F0", ""),
        # UQU with one orphan byte: both skipped.
        ("0F F0 41", ""),
        # UQU with a full 2-byte operand: emits U+0041 = 'A'.
        ("0F F0 00 41", "A"),
        # --- SQ / SQU / SQn truncation in single-byte mode: no crash -----------
        # SQ0 (0x01) as the very last byte — the operand byte is missing.
        ("01", ""),
        # SQU (0x0E) with only one operand byte — both bytes skipped.
        ("0E 41", ""),
        # SDX (0x0B) with only one operand byte — two-byte operand is incomplete.
        ("0B 41", ""),
    ],
)
def test_scsu_expand(hexbytes: str, expected: str) -> None:
    assert scsu.expand(bytes.fromhex(hexbytes.replace(" ", ""))) == expected


@pytest.mark.parametrize(
    "hexbytes, match",
    [
        # URS (0xF2) in Unicode mode is a reserved tag — ScsuError.
        ("0F F2 00 41", "reserved URS"),
        # URS immediately after entering Unicode mode.
        ("0F F2", "reserved URS"),
        # Reserved window-offset bytes in single-byte mode (0xA8–0xF8).
        # SD0 (0x18) defines window 0 with the given 1-byte offset.
        ("18 A8", "reserved window offset"),   # 0xA8 = first reserved slot
        ("18 F8", "reserved window offset"),   # 0xF8 = last reserved slot
        ("18 00", "reserved window offset"),   # 0x00 = explicit zero
    ],
)
def test_scsu_error(hexbytes: str, match: str) -> None:
    with pytest.raises(ScsuError, match=match):
        scsu.expand(bytes.fromhex(hexbytes.replace(" ", "")))
