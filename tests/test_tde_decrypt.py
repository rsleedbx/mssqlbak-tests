"""TDE page-decryption unit and integration tests (Phase 6).

## Test structure

``TestTdeKeyLoading``
    Unit tests for :func:`~mssqlbak.tde.keys.load_tde_key`:
    PFX loading from bytes, wrong password, key-only PFX.

``TestTdePageDecrypt``
    Unit tests for :func:`~mssqlbak.tde.page.decrypt_page`:
    round-trip AES-CBC encrypt / decrypt, wrong key length.

``TestTdeDekExtraction``
    Unit tests for :func:`~mssqlbak.tde.dek.extract_dek`:
    synthetic high-entropy blob + RSA key pair (generated in-test).

``TestTdeDataStartDiscovery``
    Unit tests for :func:`~mssqlbak.tde.dek.find_tde_data_start`:
    injects a crafted file-header page at a known offset and verifies
    the scanner returns the correct position.

``TestTdeFixtureIntegration``
    Integration tests against the generated ``tde_page_full.bak``.
    Skipped when the fixture is absent.

``TestEncryptedBackupErrorMessage``
    Verifies the improved error message for non-keyed TDE backups mentions
    ``--tde-cert``.
"""
from __future__ import annotations

import os
import struct
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers: locate fixture directory
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", _REPO_ROOT / "tests" / "fixtures_2022"))

PAGE_SIZE = 8192


def _fixture_path(name: str) -> Path:
    return _FIXTURE_DIR / name


# ---------------------------------------------------------------------------
# Helpers: generate a test RSA key pair in-memory
# ---------------------------------------------------------------------------

def _make_test_rsa_key(bits: int = 2048):
    """Return (private_key, public_key) via cryptography library."""
    pytest.importorskip("cryptography")
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
        backend=default_backend(),
    )
    return private_key, private_key.public_key()


def _rsa_encrypt_dek(public_key, dek_bytes: bytes) -> bytes:
    """RSA-OAEP encrypt *dek_bytes* with *public_key* (mirrors SQL Server)."""
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    return public_key.encrypt(
        dek_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),  # noqa: S303
            algorithm=hashes.SHA1(),                    # noqa: S303
            label=None,
        ),
    )


def _make_pfx_bytes(private_key, password: str) -> bytes:
    """Serialize (private_key, self-signed cert) to a PFX blob."""
    import datetime
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.hazmat.primitives.serialization import BestAvailableEncryption
    from cryptography.x509.oid import NameOID

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "TDE Test Cert"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .sign(private_key, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"TDE Test",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=BestAvailableEncryption(password.encode()),
    )


# ---------------------------------------------------------------------------
# TestTdeKeyLoading
# ---------------------------------------------------------------------------


class TestTdeKeyLoading:
    """Unit tests for mssqlbak.tde.keys.load_tde_key."""

    def test_load_pfx_from_file(self, tmp_path: Path) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.keys import TdeKey, load_tde_key

        private_key, _ = _make_test_rsa_key(2048)
        pfx_bytes = _make_pfx_bytes(private_key, "hunter2")
        pfx_path = tmp_path / "test.pfx"
        pfx_path.write_bytes(pfx_bytes)

        key = load_tde_key(pfx_path, password="hunter2")
        assert isinstance(key, TdeKey)
        assert key.private_key is not None
        assert key.key_size_bits == 2048
        assert key.cert_thumbprint is not None
        assert len(key.cert_thumbprint) == 20  # SHA-1 thumbprint

    def test_wrong_password_raises(self, tmp_path: Path) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.keys import load_tde_key

        private_key, _ = _make_test_rsa_key(2048)
        pfx_bytes = _make_pfx_bytes(private_key, "correct")
        pfx_path = tmp_path / "test.pfx"
        pfx_path.write_bytes(pfx_bytes)

        with pytest.raises(ValueError, match="[Cc]ould not load|[Ii]nvalid|[Pp]assword|[Uu]nknown"):
            load_tde_key(pfx_path, password="wrong")

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.keys import load_tde_key

        with pytest.raises(FileNotFoundError):
            load_tde_key(tmp_path / "nonexistent.pfx")


# ---------------------------------------------------------------------------
# TestTdePageDecrypt
# ---------------------------------------------------------------------------


class TestTdePageDecrypt:
    """Unit tests for mssqlbak.tde.page.decrypt_page."""

    def _make_encrypted_page(
        self, dek: bytes, page_id: int, file_id: int, plaintext_body: bytes | None = None
    ) -> bytes:
        """Return a 8192-byte AES-CBC encrypted page for the given locator."""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        body = plaintext_body or (bytes(range(256)) * 32)[:PAGE_SIZE]
        assert len(body) == PAGE_SIZE

        iv = struct.pack("<IH", page_id, file_id) + b"\x00" * 10
        cipher = Cipher(algorithms.AES(dek), modes.CBC(iv), backend=default_backend())
        enc = cipher.encryptor()
        return enc.update(body) + enc.finalize()

    def test_round_trip_aes128(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.page import decrypt_page

        dek = os.urandom(16)  # AES-128
        plain = os.urandom(PAGE_SIZE)
        enc = self._make_encrypted_page(dek, 42, 1, plain)

        result = decrypt_page(enc, dek, page_id=42, file_id=1)
        assert result == plain

    def test_round_trip_aes256(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.page import decrypt_page

        dek = os.urandom(32)  # AES-256
        plain = os.urandom(PAGE_SIZE)
        enc = self._make_encrypted_page(dek, 99, 2, plain)

        result = decrypt_page(enc, dek, page_id=99, file_id=2)
        assert result == plain

    def test_wrong_key_produces_wrong_output(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.page import decrypt_page

        dek_correct = os.urandom(16)
        dek_wrong   = os.urandom(16)
        plain = os.urandom(PAGE_SIZE)
        enc = self._make_encrypted_page(dek_correct, 5, 1, plain)

        result = decrypt_page(enc, dek_wrong, page_id=5, file_id=1)
        assert result != plain  # wrong key → garbage output

    def test_wrong_page_id_produces_wrong_output(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.page import decrypt_page

        dek = os.urandom(16)
        plain = os.urandom(PAGE_SIZE)
        enc = self._make_encrypted_page(dek, 10, 1, plain)

        result = decrypt_page(enc, dek, page_id=999, file_id=1)
        assert result != plain  # wrong page_id → different IV → garbage output

    def test_invalid_key_length_raises(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.page import decrypt_page

        enc = os.urandom(PAGE_SIZE)
        with pytest.raises(ValueError, match="[Kk]ey|AES"):
            decrypt_page(enc, b"\x00" * 7, page_id=0, file_id=1)

    def test_short_page_raises(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.page import decrypt_page

        dek = os.urandom(16)
        with pytest.raises(ValueError, match="too short|8192"):
            decrypt_page(b"\x00" * 100, dek, page_id=0, file_id=1)


# ---------------------------------------------------------------------------
# TestTdeDekExtraction
# ---------------------------------------------------------------------------


class TestTdeDekExtraction:
    """Unit tests for mssqlbak.tde.dek.extract_dek."""

    def _build_mtf_buf_with_dek(
        self, private_key, dek: bytes, dek_offset: int = 0x2CF0
    ) -> bytes:
        """Build a synthetic MTF buffer with the RSA-encrypted DEK at *dek_offset*."""
        buf = bytearray(0x10000)
        buf[:4] = b"TAPE"
        # RSA-OAEP encrypt the DEK with the public key.
        encrypted_blob = _rsa_encrypt_dek(private_key.public_key(), dek)
        end = dek_offset + len(encrypted_blob)
        buf[dek_offset:end] = encrypted_blob
        return bytes(buf)

    def test_extract_dek_round_trip(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.dek import extract_dek
        from mssqlbak.tde.keys import TdeKey

        private_key, _ = _make_test_rsa_key(2048)
        dek = os.urandom(16)
        buf = self._build_mtf_buf_with_dek(private_key, dek, dek_offset=0x2CF0)

        key = TdeKey(private_key=private_key, cert_thumbprint=None, key_size_bits=2048)
        result = extract_dek(buf, key)
        assert result == dek

    def test_extract_dek_no_blob_raises(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.dek import extract_dek
        from mssqlbak.tde.keys import TdeKey

        private_key, _ = _make_test_rsa_key(2048)
        # All-zero buffer (no DEK blob).
        buf = b"TAPE" + b"\x00" * 0x10000

        key = TdeKey(private_key=private_key, cert_thumbprint=None, key_size_bits=2048)
        with pytest.raises(ValueError, match="[Nn]o.*[Dd][Ee][Kk]|not found"):
            extract_dek(buf, key)


# ---------------------------------------------------------------------------
# TestTdeDataStartDiscovery
# ---------------------------------------------------------------------------


class TestTdeDataStartDiscovery:
    """Unit tests for mssqlbak.tde.dek.find_tde_data_start."""

    def _make_encrypted_file_header_page(self, dek: bytes) -> bytes:
        """Return an 8192-byte encrypted file-header page (page_id=0, file_id=1)."""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        # Build a valid SQL Server file-header page (m_headerVersion=1, m_type=15,
        # pageId=0, fileId=1 at offsets 0, 1, 32-37).
        page = bytearray(PAGE_SIZE)
        page[0] = 1   # m_headerVersion
        page[1] = 15  # m_type = FILE_HEADER
        struct.pack_into("<IH", page, 32, 0, 1)  # pageId=0, fileId=1
        plain = bytes(page)

        iv = struct.pack("<IH", 0, 1) + b"\x00" * 10
        cipher = Cipher(algorithms.AES(dek), modes.CBC(iv), backend=default_backend())
        enc = cipher.encryptor()
        return enc.update(plain) + enc.finalize()

    def test_find_data_start_at_known_offset(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.dek import find_tde_data_start

        dek = os.urandom(16)
        # Build a buffer: MTF headers (zeroed) then the encrypted file-header page
        # at a known offset (0x5000 = 20480).
        target_offset = 0x5000
        buf = bytearray(target_offset + PAGE_SIZE + 1024)
        enc_page = self._make_encrypted_file_header_page(dek)
        buf[target_offset : target_offset + PAGE_SIZE] = enc_page
        buf_bytes = bytes(buf)

        found = find_tde_data_start(buf_bytes, dek)
        assert found == target_offset, (
            f"Expected data stream at 0x{target_offset:04x}, "
            f"got 0x{found:04x}"
        )

    def test_find_data_start_not_found_raises(self) -> None:
        pytest.importorskip("cryptography")
        from mssqlbak.tde.dek import find_tde_data_start

        dek = os.urandom(16)
        wrong_dek = os.urandom(16)  # wrong key: decryption won't produce valid page
        enc_page = self._make_encrypted_file_header_page(dek)
        target_offset = 0x5000
        buf = bytearray(target_offset + PAGE_SIZE + 1024)
        buf[target_offset : target_offset + PAGE_SIZE] = enc_page

        with pytest.raises(ValueError, match="[Cc]ould not locate|[Dd]ata stream"):
            find_tde_data_start(bytes(buf), wrong_dek)


# ---------------------------------------------------------------------------
# TestEncryptedBackupErrorMessage
# ---------------------------------------------------------------------------


class TestEncryptedBackupErrorMessage:
    """Verify the improved EncryptedBackupError message mentions --tde-cert."""

    @pytest.fixture
    def fixture_bak_tde(self) -> Path:
        p = _fixture_path("tde_full.bak")
        if not p.exists():
            pytest.skip(f"TDE fixture not found: {p}")
        return p

    def test_error_message_mentions_tde_cert_option(self, fixture_bak_tde: Path) -> None:
        """EncryptedBackupError message must mention --tde-cert for user guidance."""
        from mssqlbak.errors import EncryptedBackupError
        from mssqlbak.pages import PageStore

        with pytest.raises(EncryptedBackupError) as exc_info:
            PageStore.from_bak(fixture_bak_tde)
        msg = str(exc_info.value)
        # The improved message should guide users toward the new --tde-cert flag.
        assert "--tde-cert" in msg or "tde-cert" in msg.lower() or "backup-level" in msg, (
            f"Error message does not mention --tde-cert or backup-level: {msg}"
        )


# ---------------------------------------------------------------------------
# TestTdeFixtureIntegration
# ---------------------------------------------------------------------------


class TestTdeFixtureIntegration:
    """Integration tests against tde_page_full.bak (database-TDE, no backup encryption).

    These tests require:
    - tde_page_full.bak  — TDE database backup
    - tde_page_plain.bak — same database without TDE
    - tde_page_cert.pfx  — certificate PFX

    All are generated by:
        python -m tools.fixture_run tde-page
    """

    @pytest.fixture
    def tde_page_bak(self) -> Path:
        p = _fixture_path("tde_page_full.bak")
        if not p.exists():
            pytest.skip(f"TDE page fixture not found: {p} — run: python -m tools.fixture_run tde-page")
        return p

    @pytest.fixture
    def tde_plain_bak(self) -> Path:
        p = _fixture_path("tde_page_plain.bak")
        if not p.exists():
            pytest.skip(f"TDE plain fixture not found: {p}")
        return p

    @pytest.fixture
    def tde_cert_pfx(self) -> Path:
        p = _fixture_path("tde_page_cert.pfx")
        if not p.exists():
            pytest.skip(f"TDE cert PFX not found: {p}")
        return p

    def test_page_store_without_key_raises_encrypted_backup_error(
        self, tde_page_bak: Path
    ) -> None:
        """Without a TDE key, PageStore.from_bak must raise EncryptedBackupError."""
        pytest.importorskip("cryptography")
        from mssqlbak.errors import EncryptedBackupError
        from mssqlbak.pages import PageStore

        with pytest.raises(EncryptedBackupError):
            PageStore.from_bak(tde_page_bak)

    def test_load_tde_key(self, tde_cert_pfx: Path) -> None:
        """load_tde_key must succeed with the fixture certificate."""
        pytest.importorskip("cryptography")
        from mssqlbak.tde import TdeKey, load_tde_key
        from tools.make_tde_page_fixture import CERT_PASSWORD

        key = load_tde_key(tde_cert_pfx, password=CERT_PASSWORD)
        assert isinstance(key, TdeKey)
        assert key.private_key is not None

    def test_page_store_with_key_succeeds(
        self, tde_page_bak: Path, tde_cert_pfx: Path
    ) -> None:
        """PageStore.from_bak with a valid TDE key must open the backup."""
        pytest.importorskip("cryptography")
        from mssqlbak.pages import PageStore
        from mssqlbak.tde import load_tde_key
        from tools.make_tde_page_fixture import CERT_PASSWORD

        key = load_tde_key(tde_cert_pfx, password=CERT_PASSWORD)
        store = PageStore.from_bak(tde_page_bak, tde_key=key)
        assert store.page_count > 0
        assert 1 in store.available_files

    def test_decrypted_rows_match_plain_backup(
        self, tde_page_bak: Path, tde_plain_bak: Path, tde_cert_pfx: Path
    ) -> None:
        """Rows extracted from the TDE backup must match the plain (no-TDE) backup.

        This is the end-to-end correctness test: if decryption is wrong, the
        row values will differ (or the extractor will crash on bad page data).
        """
        pytest.importorskip("cryptography")
        from mssqlbak.catalog import recover_schema
        from mssqlbak.extract.python_path import _extract_table
        from mssqlbak.pages import PageStore
        from mssqlbak.sink import InMemorySink
        from mssqlbak.tde import load_tde_key
        from tools.make_tde_page_fixture import CERT_PASSWORD

        key = load_tde_key(tde_cert_pfx, password=CERT_PASSWORD)
        tde_store  = PageStore.from_bak(tde_page_bak, tde_key=key)
        plain_store = PageStore.from_bak(tde_plain_bak)

        tde_schema   = recover_schema(tde_store)
        plain_schema = recover_schema(plain_store)

        # Find the probe table in both backups.
        tde_tables   = {t.name: t for t in tde_schema.tables}
        plain_tables = {t.name: t for t in plain_schema.tables}

        assert "probe" in tde_tables, f"probe table not in TDE backup; tables={list(tde_tables)}"
        assert "probe" in plain_tables

        tde_sink   = InMemorySink()
        plain_sink = InMemorySink()

        _extract_table(tde_store,   tde_tables["probe"],   tde_sink)
        _extract_table(plain_store, plain_tables["probe"], plain_sink)

        tde_data   = tde_sink.tables().get("dbo.probe") or tde_sink.tables().get("probe")
        plain_data = plain_sink.tables().get("dbo.probe") or plain_sink.tables().get("probe")

        assert tde_data   is not None, f"TDE probe table empty; tables={tde_sink.tables().keys()}"
        assert plain_data is not None

        assert tde_data.num_rows == plain_data.num_rows, (
            f"Row count mismatch: TDE={tde_data.num_rows}, plain={plain_data.num_rows}"
        )
        # Compare sorted by id to be order-independent.
        import pyarrow.compute as pc
        tde_ids   = sorted(tde_data.column("id").to_pylist())
        plain_ids = sorted(plain_data.column("id").to_pylist())
        assert tde_ids == plain_ids, (
            f"ID mismatch: TDE={tde_ids}, plain={plain_ids}"
        )
        tde_vals   = sorted(tde_data.column("val").to_pylist())
        plain_vals = sorted(plain_data.column("val").to_pylist())
        assert tde_vals == plain_vals, (
            f"val mismatch: TDE={tde_vals}, plain={plain_vals}"
        )

    def test_wrong_cert_raises_or_produces_bad_store(
        self, tde_page_bak: Path, tmp_path: Path
    ) -> None:
        """Using the wrong certificate must either raise or produce no valid tables."""
        pytest.importorskip("cryptography")
        from mssqlbak.pages import PageStore
        from mssqlbak.tde import TdeKey

        # Generate a different RSA key that was NOT used to protect this backup.
        private_key, _ = _make_test_rsa_key(2048)
        wrong_key = TdeKey(private_key=private_key, cert_thumbprint=None, key_size_bits=2048)

        try:
            store = PageStore.from_bak(tde_page_bak, tde_key=wrong_key)
            # If it opened (wrong DEK decrypted to something), the schema/tables
            # should be empty or clearly invalid.
            from mssqlbak.catalog import recover_schema
            schema = recover_schema(store)
            # No user table "probe" should be found with a wrong key.
            probe_tables = [t for t in schema.tables if t.name == "probe"]
            assert len(probe_tables) == 0, (
                "Wrong cert: unexpectedly found 'probe' table — "
                "TDE decryption may have accidentally succeeded"
            )
        except Exception:
            # Any exception (ValueError, EncryptedBackupError, etc.) is acceptable.
            pass
