"""Tests for PageStore.from_bak with a cert on the HTTP/range-reader path.

The range-reader path previously bypassed decryption entirely (calling
build_chunk_index or build_mtf_page_index without cert params), causing
EncryptedBackupError (MSSQLBAK) or CatalogError (MTF page-TDE).

These tests confirm the cert-gated spool branch added to from_bak routes
encrypted BakReaders through extract_mdf_files so decryption succeeds.

Coverage:
  - MSSQLBAK backup-level encrypted (enc_bak_aes256_full.bak)    integration
  - MSSQLBAK backup-level + TDE (tde_full.bak)                   integration
  - MTF page-level TDE (tde_page_full.bak)                       integration
"""
from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fake range reader: wraps a local .bak file but sets _is_range_reader=True
# so from_bak takes the range-reader branch (and now the cert-spool branch).
# ---------------------------------------------------------------------------

class _FakeRangeBakReader:
    """BakReader backed by a local file, pretending to be a range reader."""

    _is_range_reader: bool = True

    def __init__(self, path: Path) -> None:
        self._path_obj = path
        self._data = path.read_bytes()

    @property
    def size(self) -> int:
        return len(self._data)

    def read_at(self, offset: int, length: int) -> bytes:
        return self._data[offset : offset + length]

    def close(self) -> None:
        pass

    def __enter__(self) -> _FakeRangeBakReader:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_range_reader(path: Path) -> _FakeRangeBakReader:
    if not path.exists():
        pytest.skip(f"fixture missing: {path}")
    return _FakeRangeBakReader(path)


# ---------------------------------------------------------------------------
# Group A: backup-level encrypted (MSSQLBAK), range reader + backup_cert
# ---------------------------------------------------------------------------

class TestFromBakEncRangeMSSQLBAK:
    """enc_bak_* fixtures over the simulated range-reader path."""

    _ENC_BAK_CERT_PASSWORD = "EncBakCert!Fixture2024"
    _TDE_FULL_CERT_PASSWORD = "TdeFullCert!Fixture2024"

    def _load_enc_bak_cert(self, pfx_path: Path):
        from mssqlbak.tde.keys import load_tde_key
        return load_tde_key(pfx_path, self._ENC_BAK_CERT_PASSWORD)

    def _load_tde_full_cert(self, pfx_path: Path):
        from mssqlbak.tde.keys import load_tde_key
        return load_tde_key(pfx_path, self._TDE_FULL_CERT_PASSWORD)

    def test_enc_bak_aes256_range_reader_decrypts(
        self,
        fixture_enc_bak_aes256: Path,
        fixture_enc_bak_pfx: Path,
    ) -> None:
        """backup-level AES-256 encrypted MSSQLBAK over simulated range reader decrypts."""
        from mssqlbak.pages.store import PageStore

        cert = self._load_enc_bak_cert(fixture_enc_bak_pfx)
        reader = _make_range_reader(fixture_enc_bak_aes256)
        store = PageStore.from_bak(reader, backup_cert=cert)
        assert store.available_files, "expected at least one MDF file in the store"

    def test_enc_bak_aes256_compressed_range_reader_decrypts(
        self,
        fixture_enc_bak_aes256_compressed: Path,
        fixture_enc_bak_pfx: Path,
    ) -> None:
        """backup-level AES-256+COMPRESSION encrypted MSSQLBAK over simulated range reader."""
        from mssqlbak.pages.store import PageStore

        cert = self._load_enc_bak_cert(fixture_enc_bak_pfx)
        reader = _make_range_reader(fixture_enc_bak_aes256_compressed)
        store = PageStore.from_bak(reader, backup_cert=cert)
        assert store.available_files

    def test_enc_bak_aes256_range_reader_recover_schema_succeeds(
        self,
        fixture_enc_bak_aes256: Path,
        fixture_enc_bak_pfx: Path,
    ) -> None:
        """recover_schema must not raise after decryption over simulated range reader."""
        from mssqlbak.catalog.recover import recover_schema
        from mssqlbak.pages.store import PageStore

        cert = self._load_enc_bak_cert(fixture_enc_bak_pfx)
        reader = _make_range_reader(fixture_enc_bak_aes256)
        store = PageStore.from_bak(reader, backup_cert=cert)
        schema = recover_schema(store)
        assert schema.tables, "expected at least one table in recovered schema"

    def test_tde_full_range_reader_decrypts(
        self,
        fixture_tde_full_bak: Path,
        fixture_tde_full_pfx: Path,
    ) -> None:
        """backup-level + TDE (tde_full.bak) over simulated range reader decrypts."""
        from mssqlbak.pages.store import PageStore

        cert = self._load_tde_full_cert(fixture_tde_full_pfx)
        reader = _make_range_reader(fixture_tde_full_bak)
        store = PageStore.from_bak(reader, backup_cert=cert, tde_key=cert)
        assert store.available_files


# ---------------------------------------------------------------------------
# Group B: MTF page-level TDE, range reader + tde_key
# ---------------------------------------------------------------------------

class TestFromBakTdePageRangeMTF:
    """tde_page_full.bak (uncompressed MTF) over the simulated range-reader path."""

    _TDE_PAGE_CERT_PASSWORD = "TdePageCert!Fixture2024"

    def _load_tde_page_cert(self, pfx_path: Path):
        from mssqlbak.tde.keys import load_tde_key
        return load_tde_key(pfx_path, self._TDE_PAGE_CERT_PASSWORD)

    def test_tde_page_range_reader_decrypts(
        self,
        fixture_bak_tde_page: Path,
        fixture_tde_page_pfx: Path,
    ) -> None:
        """page-level TDE MTF backup over simulated range reader produces a valid store."""
        from mssqlbak.pages.store import PageStore

        tde_key = self._load_tde_page_cert(fixture_tde_page_pfx)
        reader = _make_range_reader(fixture_bak_tde_page)
        store = PageStore.from_bak(reader, tde_key=tde_key)
        assert store.available_files

    def test_tde_page_range_reader_recover_schema_succeeds(
        self,
        fixture_bak_tde_page: Path,
        fixture_tde_page_pfx: Path,
    ) -> None:
        """recover_schema must not raise CatalogError after decryption over range reader."""
        from mssqlbak.catalog.recover import recover_schema
        from mssqlbak.pages.store import PageStore

        tde_key = self._load_tde_page_cert(fixture_tde_page_pfx)
        reader = _make_range_reader(fixture_bak_tde_page)
        store = PageStore.from_bak(reader, tde_key=tde_key)
        # This was the observable failure before the fix: CatalogError because
        # ciphertext pages produced a garbage catalog.
        schema = recover_schema(store)
        assert schema.tables
