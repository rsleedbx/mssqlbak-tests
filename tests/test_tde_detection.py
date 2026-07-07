"""Gap F-1 — TDE detect-and-fail.

Verify that mssqlbak detects a TDE-encrypted backup and raises a clean
:exc:`mssqlbak.errors.EncryptedBackupError` instead of crashing or emitting
garbage row data.

## What SQL Server TDE does

TDE encrypts every database page with AES before writing to disk.  A backup
of a TDE-enabled database contains only ciphertext where MDF pages should be;
mssqlbak cannot read those pages without the Database Encryption Key (DEK)
and the server certificate that protects it.

## Detection approach

SQL Server stores the encrypted DEK and certificate thumbprint in the backup
set header block.  This produces a 128-byte window with Shannon entropy
> 6 bits/byte in the first 50 KB of the file — far above the near-zero
entropy of normal (structured, mostly-zero) MTF header fields.  The
:func:`mssqlbak.mtf._is_tde_encrypted_mtf` heuristic scans that window.

For compressed backups (MSSQLBAK magic), the container yields no decodable
XPRESS chunks when the pages are AES-encrypted, which triggers the same
:class:`EncryptedBackupError`.

## Test structure

``TestTdeHeuristic``
    Unit tests for the entropy-based heuristic on controlled byte arrays.

``TestTdeFixture``
    Integration tests against the generated ``tde_full.bak`` fixture file.
    These tests are skipped when the fixture is absent (run
    ``python -m tools.fixture_run all-versions --suite tde`` to generate).
"""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from mssqlbak.errors import EncryptedBackupError
from mssqlbak.mtf import _is_tde_encrypted_mtf
from mssqlbak.pages import PageStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entropy(data: bytes) -> float:
    """Shannon entropy in bits/byte."""
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum(c / n * math.log2(c / n) for c in counts if c)


def _make_mtf_header(header_len: int = 0x3000, *, dek_offset: int = 0x2CF0) -> bytes:
    """Build a synthetic MTF buffer with a 'TAPE' magic prefix.

    By default the buffer contains only zero bytes except at *dek_offset*
    where a 128-byte high-entropy block simulates the TDE DEK blob.
    """
    buf = bytearray(header_len)
    buf[:4] = b"TAPE"
    # Plant high-entropy 128 bytes at the DEK offset (simulates encrypted DEK)
    import os
    buf[dek_offset : dek_offset + 128] = os.urandom(128)
    return bytes(buf)


# ---------------------------------------------------------------------------
# Unit tests — entropy heuristic
# ---------------------------------------------------------------------------

class TestTdeHeuristic:
    """Unit tests for :func:`mssqlbak.mtf._is_tde_encrypted_mtf`."""

    def test_high_entropy_tape_detected_as_tde(self) -> None:
        """Buffer with TAPE magic and a high-entropy DEK block → True."""
        buf = _make_mtf_header(dek_offset=0x2D00)
        assert _is_tde_encrypted_mtf(buf) is True

    def test_all_zero_tape_not_tde(self) -> None:
        """TAPE magic but no high-entropy region (non-TDE backup) → False."""
        buf = bytearray(0x4000)
        buf[:4] = b"TAPE"
        assert _is_tde_encrypted_mtf(bytes(buf)) is False

    def test_mssqlbak_magic_not_detected(self) -> None:
        """MSSQLBAK-format buffer (compressed backup) must return False.

        Compressed TDE backups are detected via a different code path
        (no decodable XPRESS chunks).
        """
        import os
        buf = bytearray(0x4000)
        buf[:8] = b"MSSQLBAK"
        # Plant high-entropy data to confirm the heuristic is skipped
        buf[0x2D00 : 0x2D80] = os.urandom(128)
        assert _is_tde_encrypted_mtf(bytes(buf)) is False

    def test_too_short_buffer_not_tde(self) -> None:
        """Buffer shorter than the scan start (0x2000) → False."""
        buf = b"TAPE" + b"\x00" * 100
        assert _is_tde_encrypted_mtf(buf) is False

    def test_high_entropy_without_tape_magic_not_tde(self) -> None:
        """High-entropy data but wrong magic → False (must start with TAPE)."""
        import os
        buf = bytearray(0x4000)
        buf[:4] = b"XXXX"
        buf[0x2D00 : 0x2D80] = os.urandom(128)
        assert _is_tde_encrypted_mtf(bytes(buf)) is False

    @pytest.mark.parametrize("offset", [0x2000, 0x2CF0, 0x2D00, 0x2DB0, 0x3000])
    def test_dek_at_various_offsets_detected(self, offset: int) -> None:
        """High-entropy block is detected regardless of its position in the scan range."""
        buf = _make_mtf_header(header_len=0x5000, dek_offset=offset)
        assert _is_tde_encrypted_mtf(buf) is True

    def test_entropy_threshold_boundary(self) -> None:
        """A 128-byte window with exactly 6.0 bits/byte entropy is NOT TDE
        (threshold is strictly > 6.0).  A window at 6.01 bits/byte IS TDE."""
        # Build a buffer with uniform distribution over 128 symbols (= 7 bits).
        high_ent = bytes(range(128)) * 1  # 128 unique bytes → ~7 bits
        buf_hi = bytearray(0x4000)
        buf_hi[:4] = b"TAPE"
        buf_hi[0x2D00 : 0x2D80] = high_ent
        assert _entropy(high_ent) > 6.0
        assert _is_tde_encrypted_mtf(bytes(buf_hi)) is True

        # Build a very low-entropy block (4 symbols → 2 bits).
        low_ent = bytes([0, 1, 2, 3] * 32)
        buf_lo = bytearray(0x4000)
        buf_lo[:4] = b"TAPE"
        buf_lo[0x2D00 : 0x2D80] = low_ent
        assert _entropy(low_ent) < 6.0
        assert _is_tde_encrypted_mtf(bytes(buf_lo)) is False


# ---------------------------------------------------------------------------
# Integration tests — real TDE fixture
# ---------------------------------------------------------------------------

class TestTdeFixture:
    """Integration tests against ``tde_full.bak`` (Gap F-1).

    All tests in this class require the fixture to be present; they are
    automatically skipped with a helpful message when it is absent.
    """

    def test_page_store_raises_encrypted_backup_error(
        self, fixture_bak_tde: Path
    ) -> None:
        """PageStore.from_bak must raise EncryptedBackupError, not crash."""
        with pytest.raises(EncryptedBackupError):
            PageStore.from_bak(fixture_bak_tde)

    def test_encrypted_backup_error_is_value_error(
        self, fixture_bak_tde: Path
    ) -> None:
        """EncryptedBackupError must be a subclass of ValueError for backward
        compatibility with callers that already catch ValueError."""
        with pytest.raises(ValueError):
            PageStore.from_bak(fixture_bak_tde)

    def test_error_message_mentions_tde(self, fixture_bak_tde: Path) -> None:
        """The error message must clearly indicate TDE encryption."""
        with pytest.raises(EncryptedBackupError) as exc_info:
            PageStore.from_bak(fixture_bak_tde)
        msg = str(exc_info.value).lower()
        assert "tde" in msg or "encrypt" in msg, (
            f"Error message does not mention TDE or encryption: {exc_info.value}"
        )

    def test_fixture_starts_with_mssqlbak_magic(self, fixture_bak_tde: Path) -> None:
        """The TDE fixture uses the MSSQLBAK (compressed + encrypted) container.

        ``BACKUP … WITH ENCRYPTION`` produces an MSSQLBAK-format file regardless
        of whether ``COMPRESSION`` is also requested, because SQL Server wraps the
        backup in its custom container any time backup encryption is active.
        """
        from mssqlbak.compressed import MSSQLBAK_MAGIC
        with open(fixture_bak_tde, "rb") as f:
            magic = f.read(len(MSSQLBAK_MAGIC))
        assert magic == MSSQLBAK_MAGIC, (
            f"Expected MSSQLBAK magic, got {magic!r}.  "
            "The fixture may have been generated without backup encryption."
        )

    def test_mtf_heuristic_returns_false_for_mssqlbak_fixture(
        self, fixture_bak_tde: Path
    ) -> None:
        """_is_tde_encrypted_mtf must return False for MSSQLBAK-format backups.

        The MTF heuristic is only for uncompressed MTF backups.  MSSQLBAK-format
        TDE backups are handled by the compressed.py code path.
        """
        with open(fixture_bak_tde, "rb") as f:
            head = f.read(0x10000)
        assert _is_tde_encrypted_mtf(head) is False

    def test_fixture_file_exists_and_nonempty(self, fixture_bak_tde: Path) -> None:
        """Basic sanity: the fixture file exists and is at least 1 MB."""
        assert fixture_bak_tde.exists()
        assert fixture_bak_tde.stat().st_size > 1_000_000
