"""Resolve backup-level and TDE-page encryption certificates for test fixtures.

Mapping rules
-------------
* ``enc_bak_*``        → ``enc_bak_cert.pfx`` / ``EncBakCert!Fixture2024``
                         kind = ``"backup"``  (passed as ``backup_cert=``)
* ``tde_page_*``       → ``tde_page_cert.pfx`` / ``TdePageCert!Fixture2024``
                         kind = ``"tde_page"``  (passed as ``tde_key=``)
* ``tde_full*``        → ``tde_full_cert.pfx`` / ``TdeFullCert!Fixture2024``
                         kind = ``"backup_tde"``  (passed as BOTH ``backup_cert=``
                         and ``tde_key=``; same key protects both layers)

Exclusion rule
--------------
Fixtures whose stem ends with ``_plain`` (e.g. ``enc_bak_plain``,
``tde_page_plain``) are plaintext reference backups and require no certificate.
:func:`resolve_cert` returns ``None`` for them.

The constants are intentionally hard-coded here (not read from env or config)
because the PFX files are checked into the repo alongside the fixtures they
protect; the passwords appear in the fixture-generation scripts.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# PFX password constants — match make_enc_bak_fixture.py, make_tde_page_fixture.py,
# and make_tde_fixture.py.
_ENC_BAK_PFX_PASSWORD  = "EncBakCert!Fixture2024"
_TDE_PAGE_PFX_PASSWORD = "TdePageCert!Fixture2024"
_TDE_FULL_PFX_PASSWORD = "TdeFullCert!Fixture2024"


@dataclass(frozen=True)
class CertInfo:
    """Certificate resolved for a given fixture.

    ``kind`` controls which kwargs are passed to
    :func:`~mssqlbak.extract.extract_bak` / :func:`~mssqlbak.confidence.analyze_bak`:

    * ``kind="backup"``    → ``backup_cert=cert_info.tde_key``
      (backup-level ``WITH ENCRYPTION`` only; no TDE)
    * ``kind="tde_page"``  → ``tde_key=cert_info.tde_key``
      (database-level TDE only; backup stream is plaintext)
    * ``kind="backup_tde"`` → ``backup_cert=cert_info.tde_key``
      **and** ``tde_key=cert_info.tde_key``
      (double-encrypted: TDE + ``WITH ENCRYPTION``; same key both layers)
    """

    tde_key: Any   # TdeKey loaded via mssqlbak.tde.load_tde_key
    kind: str      # "backup" | "tde_page" | "backup_tde"


# (name_prefix, pfx_filename, password, kind)
_CERT_TABLE: list[tuple[str, str, str, str]] = [
    ("enc_bak_",   "enc_bak_cert.pfx",   _ENC_BAK_PFX_PASSWORD,   "backup"),
    ("tde_full",   "tde_full_cert.pfx",  _TDE_FULL_PFX_PASSWORD,  "backup_tde"),
    ("tde_page_",  "tde_page_cert.pfx",  _TDE_PAGE_PFX_PASSWORD,  "tde_page"),
]


def resolve_cert(bak_path: Path) -> CertInfo | None:
    """Return a :class:`CertInfo` for *bak_path* if it is an encrypted fixture.

    Looks up the PFX file relative to the fixture's parent directory.

    Returns ``None`` when:
    - The fixture stem ends with ``_plain`` (plaintext reference backup), or
    - No cert-table prefix matches, or
    - The PFX file does not exist.
    """
    from mssqlbak.tde import load_tde_key

    stem = bak_path.stem
    # Plaintext reference twins never need a certificate.
    if stem.endswith("_plain"):
        return None

    fixture_dir = bak_path.parent

    for prefix, pfx_name, password, kind in _CERT_TABLE:
        if stem.startswith(prefix):
            pfx_path = fixture_dir / pfx_name
            if not pfx_path.exists():
                return None
            tde_key = load_tde_key(pfx_path, password)
            return CertInfo(tde_key=tde_key, kind=kind)

    return None
