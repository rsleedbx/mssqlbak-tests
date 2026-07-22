"""Shared certificate export helpers for .bak fixture generators.

## Canonical procedure for exporting a SQL Server certificate to PFX

SQL Server stores certificates and their private keys internally. To use
them outside SQL Server (e.g. for mssqlbak decryption), they must be
exported and combined into a PKCS#12 (.pfx) file.

Steps performed by :func:`export_cert_to_pfx`:

1.  **Run BACKUP CERTIFICATE** inside the container (via
    :func:`backup_certificate_sql`).  This writes a DER-encoded ``.cer``
    (public certificate) and a password-encrypted Microsoft PVK file
    (private key) to the container's ``/tmp`` directory.

    Classic syntax — no ``FORMAT = 'PFX'`` and no ``ALGORITHM`` clause — so
    it works on every SQL Server version (2012–2025+) without version guards.

2.  **Copy** the ``.cer`` and ``.pvk`` out of the container to temporary
    host-side files using ``podman cp``.

3.  **Parse the PVK** (:func:`_pvk_read`) to recover the RSA private key,
    then **combine** it with the DER certificate into a PKCS#12 ``.pfx``
    (:func:`_make_pfx_from_cer_and_pvk`).

4.  **Clean up** the temporary local files and the container-side ``.cer``/
    ``.pvk`` (best effort).

## Why PVK and not direct DER?

SQL Server's ``BACKUP CERTIFICATE … WITH PRIVATE KEY (FILE = …, ENCRYPTION BY
PASSWORD = …)`` uses the Microsoft PVK format for the private key.  There is
no standard PKCS#8 / PEM output option on versions before 2022, so
:func:`_pvk_read` implements the three PVK encryption variants (0x00000000
unencrypted, 0x00000001 RC4/SHA-1, 0x80000001 3DES/SHA-1).

## Usage in fixture generators

    from tools.fixture_cert import export_cert_to_pfx

    # After running the database-setup SQL (not including BACKUP CERTIFICATE):
    export_cert_to_pfx(
        container, user, password,
        cert_name="My_Cert",
        out_pfx=FIXTURE_DIR / "my_cert.pfx",
        pvk_password="MyPvkPass!",
        pfx_password="MyPfxPass!",
    )

See :func:`backup_certificate_sql` for the SQL batch text returned by the
function, and ``make_enc_bak_fixture.py`` / ``make_tde_page_fixture.py`` /
``make_tde_fixture.py`` for complete usage examples.
"""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# PVK → RSA private key
# ---------------------------------------------------------------------------


def _pvk_read(pvk_bytes: bytes, password: str):
    """Parse a Microsoft PVK file and return an RSA private key object.

    Supports PVK encryption types:
      0x00000000  unencrypted PRIVATEKEYBLOB
      0x00000001  RC4-based (SHA-1 key derivation from salt + password)
      0x80000001  "strong" (SHA-1 derived 3-key-3DES, UTF-16LE password)

    Returns a ``cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey``.
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers
    from cryptography.hazmat.backends import default_backend

    if len(pvk_bytes) < 24:
        raise ValueError("PVK file too short")
    magic, version, _key_spec, enc_type, cb_salt, cb_blob = struct.unpack_from(
        "<IIIIII", pvk_bytes, 0
    )
    if magic != 0xB0B5F11E:
        raise ValueError(f"Bad PVK magic: {magic:#010x}")
    if version != 0:
        raise ValueError(f"Unsupported PVK version: {version}")

    salt = pvk_bytes[24 : 24 + cb_salt]
    enc_blob = pvk_bytes[24 + cb_salt : 24 + cb_salt + cb_blob]

    if enc_type == 0x00000000:
        blob = enc_blob

    elif enc_type == 0x00000001:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

        pw_bytes = password.encode("ascii")
        d = hashes.Hash(hashes.SHA1(), backend=default_backend())  # noqa: S303
        d.update(salt)
        d.update(pw_bytes)
        rc4_key = d.finalize()[:16]
        cipher = Cipher(algorithms.ARC4(rc4_key), mode=None, backend=default_backend())
        dec = cipher.decryptor()
        _BLOB_HEADER_LEN = 8
        blob = enc_blob[:_BLOB_HEADER_LEN] + (
            dec.update(enc_blob[_BLOB_HEADER_LEN:]) + dec.finalize()
        )

    elif enc_type == 0x80000001:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        pw_bytes = password.encode("utf-16-le")
        d1 = hashes.Hash(hashes.SHA1(), backend=default_backend())  # noqa: S303
        d1.update(salt)
        d1.update(pw_bytes)
        h1 = d1.finalize()
        d2 = hashes.Hash(hashes.SHA1(), backend=default_backend())  # noqa: S303
        d2.update(bytes([x ^ 0x36 for x in h1]))
        d2.update(pw_bytes)
        h2 = d2.finalize()
        key3des = (h1 + h2)[:24]
        iv = b"\x00" * 8
        cipher = Cipher(algorithms.TripleDES(key3des), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor()
        blob = dec.update(enc_blob) + dec.finalize()

    else:
        raise ValueError(f"Unsupported PVK encryption type: {enc_type:#010x}")

    if len(blob) < 20:
        raise ValueError("Decrypted PVK blob too short (wrong password?)")
    if blob[0] != 0x07:
        raise ValueError(
            f"Expected PRIVATEKEYBLOB (0x07), got {blob[0]:#x} "
            "(PVK password may be wrong)"
        )
    if blob[8:12] != b"RSA2":
        raise ValueError(f"Expected RSA2 magic, got {blob[8:12]!r}")
    bit_len, pub_exp = struct.unpack_from("<II", blob, 12)
    full = bit_len // 8
    half = bit_len // 16

    def _le(off: int, length: int) -> int:
        return int.from_bytes(blob[off : off + length], "little")

    base = 20
    n  = _le(base, full); base += full  # noqa: E702
    p  = _le(base, half); base += half  # noqa: E702
    q  = _le(base, half); base += half  # noqa: E702
    dp = _le(base, half); base += half  # noqa: E702
    dq = _le(base, half); base += half  # noqa: E702
    qi = _le(base, half); base += half  # noqa: E702
    d  = _le(base, full)

    pub  = RSAPublicNumbers(pub_exp, n)
    priv = RSAPrivateNumbers(p, q, d, dp, dq, qi, pub)
    return priv.private_key(backend=default_backend())


# ---------------------------------------------------------------------------
# .cer + .pvk → PKCS#12 .pfx
# ---------------------------------------------------------------------------


def _make_pfx_from_cer_and_pvk(
    cer_bytes: bytes,
    pvk_bytes: bytes,
    pvk_password: str,
    pfx_password: str,
    out_pfx: Path,
    *,
    cert_alias: bytes = b"cert",
) -> None:
    """Parse SQL Server's exported .cer + .pvk and write a PKCS#12 .pfx file.

    *cert_alias* sets the ``name`` field inside the PKCS#12 bag (purely
    informational; use the cert/database name for clarity).
    """
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, pkcs12

    private_key = _pvk_read(pvk_bytes, pvk_password)
    cert = x509.load_der_x509_certificate(cer_bytes)

    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=cert_alias,
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=BestAvailableEncryption(pfx_password.encode()),
    )
    out_pfx.parent.mkdir(parents=True, exist_ok=True)
    out_pfx.write_bytes(pfx_bytes)


# ---------------------------------------------------------------------------
# SQL batch builder
# ---------------------------------------------------------------------------


def backup_certificate_sql(
    cert_name: str,
    container_cer_path: str,
    container_pvk_path: str,
    pvk_password: str,
) -> str:
    """Return the T-SQL batch that exports *cert_name* to ``.cer`` + ``.pvk``.

    The batch uses the classic ``BACKUP CERTIFICATE … TO FILE … WITH PRIVATE
    KEY (FILE = …, ENCRYPTION BY PASSWORD = …)`` syntax — no ``FORMAT`` or
    ``ALGORITHM`` clause — so it works on SQL Server 2012–2025+.

    Parameters
    ----------
    cert_name:
        The SQL Server certificate name (used in ``BACKUP CERTIFICATE [name]``).
    container_cer_path:
        Absolute path inside the container where the public ``.cer`` is written.
    container_pvk_path:
        Absolute path inside the container where the private-key ``.pvk`` is written.
    pvk_password:
        Password used to encrypt the ``.pvk`` file (RC4 / 3DES depending on
        SQL Server version).
    """
    return (
        f"BACKUP CERTIFICATE [{cert_name}] "
        f"TO FILE = N'{container_cer_path}' "
        f"WITH PRIVATE KEY ("
        f"    FILE = N'{container_pvk_path}', "
        f"    ENCRYPTION BY PASSWORD = N'{pvk_password}'"
        f")"
    )


# ---------------------------------------------------------------------------
# Orchestrated export: SQL → copy → PFX
# ---------------------------------------------------------------------------


def export_cert_to_pfx(
    container: str,
    user: str,
    password: str,
    cert_name: str,
    out_pfx: Path,
    *,
    pvk_password: str,
    pfx_password: str,
    container_cer_path: str | None = None,
    container_pvk_path: str | None = None,
    cert_alias: bytes | None = None,
) -> None:
    """Export *cert_name* from SQL Server and write a PKCS#12 ``.pfx``.

    This is the canonical single-call entry point for fixture generators.
    It runs :func:`backup_certificate_sql` inside *container*, copies the
    resulting ``.cer`` and ``.pvk`` to temporary host-side files, combines
    them into a PKCS#12 ``.pfx``, and cleans up the intermediates.

    Parameters
    ----------
    container:
        Podman container name.
    user:
        SQL Server login (typically ``sa``).
    password:
        SQL Server login password.
    cert_name:
        The SQL Server certificate name to export.
    out_pfx:
        Destination ``.pfx`` path on the host.
    pvk_password:
        Password used to encrypt the private-key ``.pvk`` file.
    pfx_password:
        Password for the output PKCS#12 ``.pfx``.
    container_cer_path:
        Path inside the container for the temporary ``.cer`` file.
        Defaults to ``/tmp/<cert_name>_export.cer``.
    container_pvk_path:
        Path inside the container for the temporary ``.pvk`` file.
        Defaults to ``/tmp/<cert_name>_export.pvk``.
    cert_alias:
        PKCS#12 bag alias (bytes).  Defaults to the cert_name encoded as UTF-8.
    """
    from tools.fixture_utils import _copy_out, load_and_backup_stmts

    safe = cert_name.replace(" ", "_")
    _container_cer = container_cer_path or f"/tmp/{safe}_export.cer"
    _container_pvk = container_pvk_path or f"/tmp/{safe}_export.pvk"
    _alias = cert_alias or cert_name.encode()

    # Pre-clean stale files from a previous run so BACKUP CERTIFICATE doesn't
    # fail with "file already exists".
    for cpath in (_container_cer, _container_pvk):
        subprocess.run(
            ["podman", "exec", container, "rm", "-f", cpath],
            check=False,
        )

    sql_stmt = backup_certificate_sql(cert_name, _container_cer, _container_pvk, pvk_password)
    load_and_backup_stmts(container, user, password, [sql_stmt])

    tmp_cer = out_pfx.parent / f"_tmp_{safe}_export.cer"
    tmp_pvk = out_pfx.parent / f"_tmp_{safe}_export.pvk"
    try:
        _copy_out(container, _container_cer, tmp_cer)
        _copy_out(container, _container_pvk, tmp_pvk)

        _make_pfx_from_cer_and_pvk(
            tmp_cer.read_bytes(),
            tmp_pvk.read_bytes(),
            pvk_password=pvk_password,
            pfx_password=pfx_password,
            out_pfx=out_pfx,
            cert_alias=_alias,
        )
    finally:
        tmp_cer.unlink(missing_ok=True)
        tmp_pvk.unlink(missing_ok=True)
        # Best-effort cleanup of container-side files.
        for cpath in (_container_cer, _container_pvk):
            subprocess.run(
                ["podman", "exec", container, "rm", "-f", cpath],
                check=False,
            )

    print(
        f"exported {cert_name!r} → {out_pfx.name} ({out_pfx.stat().st_size:,} bytes)",
        file=sys.stderr,
    )
