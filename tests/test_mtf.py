from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.mtf import extract_mdf_pages

PAGE = 8192

# Known MDF page-type bytes (m_type at page offset 1).  1=data, 2=index,
# 3/4=text, 7=sort, 8=GAM, 9=SGAM, 10=IAM, 11=PFS, 13=boot, 14=server-cfg,
# 15=file-header, 16/17=diff/ML maps, 18/19/20/21/22=allocation/system.
_KNOWN_PAGE_TYPES = {1, 2, 3, 4, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22}


@pytest.mark.fixture
def test_mdf_stream_is_page_aligned(fixture_bak: Path) -> None:
    data = extract_mdf_pages(fixture_bak)
    assert len(data) > 0
    assert len(data) % PAGE == 0


@pytest.mark.fixture
def test_boot_page_present(fixture_bak: Path) -> None:
    data = extract_mdf_pages(fixture_bak)
    # Boot page is page 9 of file 1 in every SQL Server MDF.  Verified against
    # the fixture: the contiguous page image starts at the file-header page
    # (page 0), so the boot page lands at index 9 of the returned bytes.
    boot = data[9 * PAGE : 10 * PAGE]
    assert len(boot) == PAGE
    assert boot[0] == 0x01  # m_headerVersion
    assert boot[1] == 13  # m_type == boot page


@pytest.mark.fixture
def test_first_pages_look_like_mdf(fixture_bak: Path) -> None:
    data = extract_mdf_pages(fixture_bak)
    npages = min(40, len(data) // PAGE)
    assert npages > 0
    good = 0
    for k in range(npages):
        off = k * PAGE
        page = data[off : off + PAGE]
        if page == b"\x00" * PAGE:
            # Unallocated pages are zero-filled but still part of the image.
            good += 1
            continue
        if page[0] == 0x01 and page[1] in _KNOWN_PAGE_TYPES:
            good += 1
    assert good / npages >= 0.90
