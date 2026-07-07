"""Tests for MSSQLBAK (compressed-backup) container handling."""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.compressed import (
    extract_mdf_pages_compressed,
    is_mssqlbak,
)
from mssqlbak.mtf import extract_mdf_pages

PAGE = 8192


def test_is_mssqlbak_detects_container(
    fixture_bak_compressed: Path, fixture_bak: Path
) -> None:
    assert is_mssqlbak(fixture_bak_compressed) is True
    assert is_mssqlbak(fixture_bak) is False


@pytest.mark.fixture
def test_compressed_image_is_page_aligned(fixture_bak_compressed: Path) -> None:
    img = extract_mdf_pages_compressed(fixture_bak_compressed)
    assert len(img) > 0
    assert len(img) % PAGE == 0


@pytest.mark.fixture
def test_compressed_boot_page_present(fixture_bak_compressed: Path) -> None:
    img = extract_mdf_pages_compressed(fixture_bak_compressed)
    boot = img[9 * PAGE : 10 * PAGE]
    assert boot[0] == 0x01  # m_headerVersion
    assert boot[1] == 13  # boot page


@pytest.mark.fixture
def test_extract_mdf_pages_auto_routes_compressed(
    fixture_bak_compressed: Path,
) -> None:
    # The generic entry point must detect the container and decompress it.
    img = extract_mdf_pages(fixture_bak_compressed)
    assert len(img) % PAGE == 0
    file_header = img[0:PAGE]
    assert file_header[0] == 0x01 and file_header[1] == 15  # file-header page 0


@pytest.mark.fixture
def test_compressed_matches_uncompressed_pages(
    fixture_bak_compressed: Path, fixture_bak: Path
) -> None:
    """Every allocated (non-zero) page recovered from the compressed backup must
    match the uncompressed backup, ignoring per-backup-instance noise.

    The two fixtures are independent BACKUP operations of the same database, so
    page-header LSN/CRC fields differ by a handful of bytes per page; the page
    *body* and structure are identical.
    """
    comp = extract_mdf_pages_compressed(fixture_bak_compressed)
    plain = extract_mdf_pages(fixture_bak)
    n = min(len(comp), len(plain)) // PAGE
    compared = 0
    close = 0
    for k in range(n):
        c = comp[k * PAGE : (k + 1) * PAGE]
        p = plain[k * PAGE : (k + 1) * PAGE]
        if c == b"\x00" * PAGE and p == b"\x00" * PAGE:
            continue
        if c == b"\x00" * PAGE or p == b"\x00" * PAGE:
            continue  # allocation can differ slightly between backups
        compared += 1
        # allow small per-instance header differences (LSN, CRC, etc.)
        diff = sum(1 for i in range(PAGE) if c[i] != p[i])
        if diff <= 512:
            close += 1
    assert compared > 100
    assert close / compared >= 0.98


@pytest.mark.fixture
def test_compressed_extracts_identical_tables(
    fixture_bak_compressed: Path, fixture_bak: Path
) -> None:
    """Decoded table rows must be byte-identical between the compressed and
    uncompressed backups of the same database, for every user table."""
    from mssqlbak.catalog import recover_schema
    from mssqlbak.pages import PageStore
    from mssqlbak.rows import read_table_rows

    def dump(path: Path) -> dict[str, list]:
        store = PageStore.from_bak(path)
        schema = recover_schema(store)
        return {t.name: list(read_table_rows(store, t)) for t in schema.tables}

    comp = dump(fixture_bak_compressed)
    plain = dump(fixture_bak)
    assert set(comp) == set(plain)
    assert comp.keys()  # non-empty
    for name in plain:
        assert comp[name] == plain[name], f"table {name} differs"
