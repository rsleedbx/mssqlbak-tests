"""Resolve backup-level and TDE-page encryption certificates for test fixtures.

Mapping rules
-------------
* ``enc_bak_*``    → ``<fixture_dir>/enc_bak_cert.pfx`` / password ``EncBakCert!Fixture2024``
                     kind = ``"backup"``  (passed as ``backup_cert=`` to extract_bak / analyze_bak)
* ``tde_page_*``   → ``<fixture_dir>/tde_page_cert.pfx`` / password ``TdePageCert!Fixture2024``
                     kind = ``"tde_page"``  (passed as ``tde_key=`` to extract_bak / analyze_bak)

The constants are intentionally hard-coded here (not read from env or config)
because the PFX files are checked into the repo alongside the fixtures they
protect; the passwords appear in the fixture-generation scripts.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# PFX password constants — match tools/make_enc_bak_fixture.py and make_tde_page_fixture.py
_ENC_BAK_PFX_PASSWORD = "EncBakCert!Fixture2024"
_TDE_PAGE_PFX_PASSWORD = "TdePageCert!Fixture2024"


@dataclass(frozen=True)
class CertInfo:
    """Certificate resolved for a given fixture.

    ``kind`` is either ``"backup"`` (backup-level encryption) or ``"tde_page"``
    (page-level TDE).  Pass the ``tde_key`` to the appropriate parameter of
    :func:`~mssqlbak.extract.extract_bak` / :func:`~mssqlbak.confidence.analyze_bak`:

    * ``kind="backup"``   → ``backup_cert=cert_info.tde_key``
    * ``kind="tde_page"`` → ``tde_key=cert_info.tde_key``
    """

    tde_key: Any          # TdeKey (loaded via mssqlbak.tde.load_tde_key)
    kind: str             # "backup" | "tde_page"


# (name_prefix, pfx_filename, password, kind)
_CERT_TABLE: list[tuple[str, str, str, str]] = [
    ("enc_bak_",   "enc_bak_cert.pfx",   _ENC_BAK_PFX_PASSWORD,   "backup"),
    ("tde_page_",  "tde_page_cert.pfx",  _TDE_PAGE_PFX_PASSWORD,  "tde_page"),
]


def resolve_cert(bak_path: Path) -> CertInfo | None:
    """Return a :class:`CertInfo` for *bak_path* if it is an encrypted fixture.

    Looks up the PFX file relative to the fixture's parent directory.
    Returns ``None`` when no cert mapping matches (plain backup).
    """
    from mssqlbak.tde import load_tde_key

    stem = bak_path.stem
    fixture_dir = bak_path.parent

    for prefix, pfx_name, password, kind in _CERT_TABLE:
        if stem.startswith(prefix):
            pfx_path = fixture_dir / pfx_name
            if not pfx_path.exists():
                return None
            tde_key = load_tde_key(pfx_path, password)
            return CertInfo(tde_key=tde_key, kind=kind)

    return None
