"""Backup-level encrypted backup decryption tests.

Coverage:
  - AES key extraction from encrypted backup header         unit
  - decrypt_first_chunk returns MSSQLBAK magic (compressed) unit
  - decrypt_first_chunk returns MTF tape magic (enc-only)   unit
  - backup-level decrypt round-trip: AES-256 full           integration
  - backup-level decrypt round-trip: AES-128 full           integration
  - backup-level decrypt round-trip: AES-256 compressed     integration
  - probe-table extraction via extract_bak (backup_cert=)   integration
  - EncryptedBackupError raised without cert                integration
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

FIXTURE_ENC_BAK_CERT_PASSWORD = "EncBakCert!Fixture2024"
EXPECTED_PROBE_ROWS = [
    {"id": 1, "val": "alpha"},
    {"id": 2, "val": "beta"},
    {"id": 3, "val": "gamma"},
]


# ---------------------------------------------------------------------------
# Minimal Sink for assertion
# ---------------------------------------------------------------------------

import pyarrow as pa  # noqa: E402


class _CollectingSink:
    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, Any]]] = {}
        self._current: str | None = None

    def open_table(self, name: str, schema: pa.Schema, *, constraints: Any = None) -> None:
        self._current = name
        self.rows.setdefault(name, [])

    def write_batch(self, batch: pa.RecordBatch, *, checkpoint: Any = None) -> None:
        if self._current is None:
            return
        d = batch.to_pydict()
        for i in range(batch.num_rows):
            self.rows[self._current].append({c: d[c][i] for c in d})

    def close(self) -> None:
        self._current = None

    def finish(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_enc_bak_key(pfx_path: Path):
    from mssqlbak.tde.keys import load_tde_key
    return load_tde_key(pfx_path, FIXTURE_ENC_BAK_CERT_PASSWORD)


def _probe_rows(sink: _CollectingSink) -> list[dict[str, Any]]:
    for name, rows in sink.rows.items():
        if name.lower().endswith(".probe") or name.lower() == "probe":
            return sorted(rows, key=lambda r: r.get("id", 0))
    return []


# ---------------------------------------------------------------------------
# Unit tests: header parsing + key extraction
# ---------------------------------------------------------------------------

class TestBackupEncHeader:
    def test_is_backup_encrypted_returns_true_for_enc_backup(
        self, fixture_enc_bak_aes256: Path
    ):
        from mssqlbak.backupenc.stream import is_backup_encrypted

        hdr = fixture_enc_bak_aes256.read_bytes()[:16]
        assert is_backup_encrypted(hdr)

    def test_is_backup_encrypted_returns_false_for_plain_backup(
        self, fixture_enc_bak_plain: Path
    ):
        from mssqlbak.backupenc.stream import is_backup_encrypted

        hdr = fixture_enc_bak_plain.read_bytes()[:16]
        assert not is_backup_encrypted(hdr)

    def test_extract_aes_key_returns_32_bytes_for_aes256(
        self, fixture_enc_bak_aes256: Path, fixture_enc_bak_pfx: Path
    ):
        from mssqlbak.backupenc.descriptor import parse_enc_header
        from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx

        data = fixture_enc_bak_aes256.read_bytes()
        hdr = parse_enc_header(data)
        private_key = load_private_key_from_pfx(
            fixture_enc_bak_pfx.read_bytes(),
            FIXTURE_ENC_BAK_CERT_PASSWORD.encode(),
        )
        key = extract_aes_key(hdr.rsa_blob, private_key)
        assert len(key) == 32

    def test_extract_aes_key_returns_16_bytes_for_aes128(
        self, fixture_enc_bak_aes128: Path, fixture_enc_bak_pfx: Path
    ):
        from mssqlbak.backupenc.descriptor import parse_enc_header
        from mssqlbak.backupenc.keys import extract_aes_key, load_private_key_from_pfx

        data = fixture_enc_bak_aes128.read_bytes()
        hdr = parse_enc_header(data)
        private_key = load_private_key_from_pfx(
            fixture_enc_bak_pfx.read_bytes(),
            FIXTURE_ENC_BAK_CERT_PASSWORD.encode(),
        )
        key = extract_aes_key(hdr.rsa_blob, private_key)
        assert len(key) == 16


# ---------------------------------------------------------------------------
# Unit tests: decrypt_first_chunk
# ---------------------------------------------------------------------------

_MSSQLBAK_MAGIC = b"MSSQLBAK"
_MTF_TAPE_MAGIC_PREFIX = b"TAPE"  # first 4 bytes of a raw MTF TAPE block


class TestDecryptFirstChunk:
    def test_decrypt_first_chunk_enc_compressed_yields_mssqlbak(
        self, fixture_enc_bak_aes256_compressed: Path, fixture_enc_bak_pfx: Path
    ):
        """For enc+compressed backup, decrypt_first_chunk yields an MSSQLBAK prefix."""
        from mssqlbak.backupenc.stream import decrypt_first_chunk
        from mssqlbak.tde.keys import load_tde_key

        tde_key = load_tde_key(fixture_enc_bak_pfx, FIXTURE_ENC_BAK_CERT_PASSWORD)
        data = fixture_enc_bak_aes256_compressed.read_bytes()
        plaintext = decrypt_first_chunk(data[:256 * 1024], tde_key.private_key)
        assert plaintext[:8] == _MSSQLBAK_MAGIC, (
            f"Expected MSSQLBAK magic, got {plaintext[:8]!r}"
        )

    def test_decrypt_first_chunk_enc_only_yields_mtf_header(
        self, fixture_enc_bak_aes256: Path, fixture_enc_bak_pfx: Path
    ):
        """For enc-only (uncompressed) backup, decrypt_first_chunk yields raw MTF."""
        from mssqlbak.backupenc.stream import decrypt_first_chunk
        from mssqlbak.tde.keys import load_tde_key

        tde_key = load_tde_key(fixture_enc_bak_pfx, FIXTURE_ENC_BAK_CERT_PASSWORD)
        data = fixture_enc_bak_aes256.read_bytes()
        plaintext = decrypt_first_chunk(data[:256 * 1024], tde_key.private_key)
        # Raw MTF TAPE block starts with the 4-byte "TAPE" descriptor type at offset 0.
        assert plaintext[:4] == _MTF_TAPE_MAGIC_PREFIX, (
            f"Expected 'TAPE' at bytes [0:4], got {plaintext[:4]!r}"
        )


# ---------------------------------------------------------------------------
# Integration tests: extract_bak with backup_cert
# ---------------------------------------------------------------------------

class TestBackupEncExtract:
    def _extract_probe(self, bak_path: Path, pfx_path: Path) -> list[dict[str, Any]]:
        from mssqlbak.extract.driver import extract_bak
        from mssqlbak.tde.keys import load_tde_key

        tde_key = load_tde_key(pfx_path, FIXTURE_ENC_BAK_CERT_PASSWORD)
        sink = _CollectingSink()
        extract_bak(str(bak_path), sink=sink, backup_cert=tde_key)
        return _probe_rows(sink)

    def test_aes256_full_extracts_probe_rows(
        self, fixture_enc_bak_aes256: Path, fixture_enc_bak_pfx: Path
    ):
        rows = self._extract_probe(fixture_enc_bak_aes256, fixture_enc_bak_pfx)
        assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}: {rows}"
        assert [r["id"] for r in rows] == [1, 2, 3]
        assert [r["val"] for r in rows] == ["alpha", "beta", "gamma"]

    def test_aes128_full_extracts_probe_rows(
        self, fixture_enc_bak_aes128: Path, fixture_enc_bak_pfx: Path
    ):
        rows = self._extract_probe(fixture_enc_bak_aes128, fixture_enc_bak_pfx)
        assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}: {rows}"
        assert [r["id"] for r in rows] == [1, 2, 3]
        assert [r["val"] for r in rows] == ["alpha", "beta", "gamma"]

    def test_aes256_compressed_extracts_probe_rows(
        self,
        fixture_enc_bak_aes256_compressed: Path,
        fixture_enc_bak_pfx: Path,
    ):
        rows = self._extract_probe(fixture_enc_bak_aes256_compressed, fixture_enc_bak_pfx)
        assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}: {rows}"
        assert [r["id"] for r in rows] == [1, 2, 3]
        assert [r["val"] for r in rows] == ["alpha", "beta", "gamma"]

    def test_aes256_and_plain_row_counts_match(
        self,
        fixture_enc_bak_aes256: Path,
        fixture_enc_bak_plain: Path,
        fixture_enc_bak_pfx: Path,
    ):
        """Row counts from enc-bak must equal row counts from the plain reference."""
        from mssqlbak.extract.driver import extract_bak
        from mssqlbak.tde.keys import load_tde_key

        tde_key = load_tde_key(fixture_enc_bak_pfx, FIXTURE_ENC_BAK_CERT_PASSWORD)

        def _collect(bak_path: Path, **kw: Any) -> dict[str, int]:
            sink = _CollectingSink()
            extract_bak(str(bak_path), sink=sink, **kw)
            return {name: len(rows) for name, rows in sink.rows.items()}

        plain_counts = _collect(fixture_enc_bak_plain)
        enc_counts = _collect(fixture_enc_bak_aes256, backup_cert=tde_key)
        assert plain_counts == enc_counts, (
            f"Row-count mismatch plain vs enc-bak:\n"
            f"  plain: {plain_counts}\n"
            f"  enc:   {enc_counts}"
        )

    def test_encrypted_backup_raises_without_cert(
        self, fixture_enc_bak_aes256: Path
    ):
        from mssqlbak.errors import EncryptedBackupError
        from mssqlbak.extract.driver import extract_bak

        with pytest.raises(EncryptedBackupError):
            extract_bak(str(fixture_enc_bak_aes256), sink=_CollectingSink())
