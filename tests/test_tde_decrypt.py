"""Tests for TDE page decryption (Phase 6).

Coverage:
  - key loading (load_tde_key)           unit — PFX round-trip
  - per-page AES-CBC decryption          unit — known-vector
  - DEK extraction from real backup      integration — tde_page_full.bak
  - data-stream start discovery          integration — tde_page_full.bak
  - end-to-end table extraction          integration — mssqlbak extract with tde_key=
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

import pyarrow as pa
import pytest

FIXTURE_TDE_PAGE_CERT_PASSWORD = "TdePageCert!Fixture2024"


# ---------------------------------------------------------------------------
# Minimal in-memory Sink for test assertions
# ---------------------------------------------------------------------------

class _CollectingSink:
    """Sink that accumulates all rows into self.rows keyed by table name."""

    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, Any]]] = {}
        self._current_table: str | None = None
        self._current_schema: pa.Schema | None = None

    def open_table(
        self,
        qualified_name: str,
        schema: pa.Schema,
        *,
        constraints: Any = None,
    ) -> None:
        self._current_table = qualified_name
        self._current_schema = schema
        self.rows.setdefault(qualified_name, [])

    def write_batch(
        self, batch: pa.RecordBatch, *, checkpoint: Any = None
    ) -> None:
        if self._current_table is None:
            return
        pydict = batch.to_pydict()
        n = batch.num_rows
        for i in range(n):
            row = {col: pydict[col][i] for col in pydict}
            self.rows[self._current_table].append(row)

    def close(self) -> None:
        self._current_table = None

    def finish(self) -> None:
        pass

# ---------------------------------------------------------------------------
# Helpers shared across test classes
# ---------------------------------------------------------------------------

def _make_test_key_and_pfx(tmp_path: Path, password: str = "test-pw"):
    """Generate a throwaway RSA key+cert and write a PFX to tmp_path."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, pkcs12
    from cryptography.x509.oid import NameOID
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    pfx = pkcs12.serialize_key_and_certificates(
        name=b"test",
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=BestAvailableEncryption(password.encode()),
    )
    pfx_path = tmp_path / "test.pfx"
    pfx_path.write_bytes(pfx)
    return key, cert, pfx_path


# ---------------------------------------------------------------------------
# Unit tests: key loading
# ---------------------------------------------------------------------------

class TestTdeKeyLoading:
    def test_load_pfx_returns_tde_key(self, tmp_path):
        from mssqlbak.tde.keys import load_tde_key, TdeKey

        key, cert, pfx_path = _make_test_key_and_pfx(tmp_path, "secret")
        tde_key = load_tde_key(pfx_path, "secret")

        assert isinstance(tde_key, TdeKey)
        assert tde_key.key_size_bits == 2048
        assert tde_key.cert_thumbprint is not None
        assert len(tde_key.cert_thumbprint) == 20  # SHA-1

    def test_wrong_password_raises_value_error(self, tmp_path):
        from mssqlbak.tde.keys import load_tde_key

        _, _, pfx_path = _make_test_key_and_pfx(tmp_path, "correct")
        with pytest.raises(ValueError, match="Could not load PFX"):
            load_tde_key(pfx_path, "wrong")

    def test_missing_file_raises_file_not_found(self, tmp_path):
        from mssqlbak.tde.keys import load_tde_key

        with pytest.raises(FileNotFoundError):
            load_tde_key(tmp_path / "nonexistent.pfx", "")


# ---------------------------------------------------------------------------
# Unit tests: per-page AES-CBC decryption
# ---------------------------------------------------------------------------

class TestTdePageDecrypt:
    def _make_page(self, dek: bytes, page_id: int, file_id: int) -> tuple[bytes, bytes]:
        """Build a 8192-byte TDE backup page (plaintext header + encrypted data).

        SQL Server TDE leaves the first 96 bytes (page header) in plaintext and
        AES-CBC-encrypts bytes 96–8191 with the per-page IV.
        """
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        from mssqlbak.tde.page import PAGE_HEADER_SIZE

        header_plain = b"\xAA" * PAGE_HEADER_SIZE
        data_plain   = (b"\xAB" * 16 + b"\xCD" * 16) * ((8192 - PAGE_HEADER_SIZE) // 32)

        iv = struct.pack("<IH", page_id, file_id) + b"\x00" * 10
        cipher = Cipher(algorithms.AES(dek), modes.CBC(iv), backend=default_backend())
        enc = cipher.encryptor()
        data_enc = enc.update(data_plain) + enc.finalize()

        # Backup page = plaintext header + encrypted data
        backup_page = header_plain + data_enc
        # Expected output of decrypt_page = plaintext header + decrypted data
        expected_plaintext = header_plain + data_plain
        return backup_page, expected_plaintext

    def test_decrypt_round_trip(self):
        from mssqlbak.tde.page import decrypt_page

        dek = b"\x01" * 16
        backup_page, expected = self._make_page(dek, page_id=1, file_id=1)
        result = decrypt_page(backup_page, dek, page_id=1, file_id=1)
        assert result == expected

    def test_wrong_dek_gives_different_output(self):
        from mssqlbak.tde.page import decrypt_page

        dek = b"\x02" * 16
        backup_page, expected = self._make_page(dek, page_id=0, file_id=1)
        wrong_result = decrypt_page(backup_page, b"\x03" * 16, page_id=0, file_id=1)
        assert wrong_result != expected

    def test_page_too_short_raises(self):
        from mssqlbak.tde.page import decrypt_page

        with pytest.raises(ValueError, match="too short"):
            decrypt_page(b"\x00" * 100, b"\x00" * 16, page_id=0, file_id=1)

    def test_invalid_dek_length_raises(self):
        from mssqlbak.tde.page import decrypt_page

        with pytest.raises(ValueError, match="Invalid AES key length"):
            decrypt_page(b"\x00" * 8192, b"\x00" * 7, page_id=0, file_id=1)


# ---------------------------------------------------------------------------
# Integration tests: DEK extraction + data-stream discovery (real fixture)
# ---------------------------------------------------------------------------

class TestTdeDekExtraction:
    def test_extract_dek_from_real_backup(
        self,
        fixture_bak_tde_page: Path,
        fixture_tde_page_pfx: Path,
    ):
        from mssqlbak.tde.keys import load_tde_key
        from mssqlbak.tde.dek import extract_dek

        tde_key = load_tde_key(fixture_tde_page_pfx, FIXTURE_TDE_PAGE_CERT_PASSWORD)
        buf = fixture_bak_tde_page.read_bytes()
        dek = extract_dek(buf, tde_key)

        # AES-128 from the fixture (ALGORITHM = AES_128 in make_tde_page_fixture.py).
        assert len(dek) == 16

    def test_extract_dek_wrong_key_raises(
        self,
        fixture_bak_tde_page: Path,
        tmp_path: Path,
    ):
        from mssqlbak.tde.keys import TdeKey, load_tde_key
        from mssqlbak.tde.dek import extract_dek

        _, _, pfx_path = _make_test_key_and_pfx(tmp_path, "x")
        wrong_key = load_tde_key(pfx_path, "x")
        buf = fixture_bak_tde_page.read_bytes()
        with pytest.raises(ValueError):  # thumbprint not found or RSA failed
            extract_dek(buf, wrong_key)


class TestTdeDataStartDiscovery:
    def test_find_data_start_returns_valid_offset(
        self,
        fixture_bak_tde_page: Path,
        fixture_tde_page_pfx: Path,
    ):
        from mssqlbak.tde.keys import load_tde_key
        from mssqlbak.tde.dek import extract_dek, find_tde_data_start

        tde_key = load_tde_key(fixture_tde_page_pfx, FIXTURE_TDE_PAGE_CERT_PASSWORD)
        buf = fixture_bak_tde_page.read_bytes()
        dek = extract_dek(buf, tde_key)
        offset = find_tde_data_start(buf, dek)

        assert offset > 0
        assert offset % 512 == 0          # MTF-aligned
        assert offset + 8192 <= len(buf)  # room for at least one page


# ---------------------------------------------------------------------------
# Integration test: end-to-end extraction of TDE backup
# ---------------------------------------------------------------------------

class TestTdeEndToEnd:
    def test_tde_extract_probe_table(
        self,
        fixture_bak_tde_page: Path,
        fixture_tde_page_pfx: Path,
    ):
        """Extract the TDE backup and verify the three known probe rows."""
        from mssqlbak.tde.keys import load_tde_key
        from mssqlbak.extract.driver import extract_bak

        tde_key = load_tde_key(fixture_tde_page_pfx, FIXTURE_TDE_PAGE_CERT_PASSWORD)
        sink = _CollectingSink()
        extract_bak(str(fixture_bak_tde_page), sink=sink, tde_key=tde_key)

        # Find the probe table regardless of schema prefix.
        probe_rows: list[dict] = []
        for name, rows in sink.rows.items():
            if name.lower().endswith(".probe") or name.lower() == "probe":
                probe_rows.extend(rows)

        assert len(probe_rows) == 3, (
            f"Expected 3 probe rows, got {len(probe_rows)}: {probe_rows}"
        )
        ids = {r.get("id") for r in probe_rows}
        vals = {r.get("val") for r in probe_rows}
        assert ids == {1, 2, 3}
        assert vals == {"hello", "world", "tde_test"}

    def test_tde_backup_raises_without_key(self, fixture_bak_tde_page: Path):
        """Extracting without a TDE key should raise EncryptedBackupError.

        The DEK blob in the MTF headers is high-entropy; _find_image_start
        detects this and raises EncryptedBackupError rather than silently
        returning garbled results.
        """
        from mssqlbak.errors import EncryptedBackupError
        from mssqlbak.extract.driver import extract_bak

        with pytest.raises(EncryptedBackupError):
            extract_bak(str(fixture_bak_tde_page), sink=_CollectingSink())

    def test_plain_and_tde_row_counts_match(
        self,
        fixture_bak_tde_page: Path,
        fixture_bak_tde_plain: Path,
        fixture_tde_page_pfx: Path,
    ):
        """Row counts from TDE backup must equal row counts from plain backup."""
        from mssqlbak.tde.keys import load_tde_key
        from mssqlbak.extract.driver import extract_bak

        tde_key = load_tde_key(fixture_tde_page_pfx, FIXTURE_TDE_PAGE_CERT_PASSWORD)

        def _collect(bak_path: Path, **kw) -> dict[str, int]:
            sink = _CollectingSink()
            extract_bak(str(bak_path), sink=sink, **kw)
            return {name: len(rows) for name, rows in sink.rows.items()}

        plain_counts = _collect(fixture_bak_tde_plain)
        tde_counts = _collect(fixture_bak_tde_page, tde_key=tde_key)

        assert plain_counts == tde_counts, (
            f"Row-count mismatch between plain and TDE backups:\n"
            f"  plain: {plain_counts}\n"
            f"  tde:   {tde_counts}"
        )
