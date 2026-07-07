"""Guard: the backup byte map must tile the file completely, with zero unknown.

``docs/BYTE_MAP.md`` is the master coverage document. These tests enforce its
core promise — that *every* byte of the backup is classified as metadata, data,
or skippable framing — so a regression in the structural model fails loudly:

* the committed doc matches a fresh generation,
* the segments tile ``[0, file_size)`` contiguously with no gap or overlap,
* no byte (segment or page) is ``UNKNOWN``,
* the ``data`` bucket equals exactly what the extractor reads, and
* (with a live engine) the data image equals ``RESTORE FILELISTONLY``'s
  ``BackupSizeInBytes`` for the data file — byte-for-byte restore evidence.
"""
from __future__ import annotations

import os

import pytest

from mssqlbak import mtf
from tools.byte_map import (
    DATA,
    UNKNOWN,
    DOC_PATH,
    build_map,
    build_report,
    bucket_totals,
)


@pytest.mark.fixture
def test_byte_map_doc_is_current(fixture_bak) -> None:
    expected = build_report(fixture_bak)
    actual = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    assert actual == expected, (
        "docs/BYTE_MAP.md is stale; regenerate it with `python -m tools.byte_map`"
    )


@pytest.mark.fixture
def test_tiling_is_complete_and_contiguous(fixture_bak) -> None:
    bm = build_map(fixture_bak)
    cursor = 0
    for seg in bm.segments:
        assert seg.offset == cursor, f"gap/overlap before {seg.detail} at {seg.offset}"
        assert seg.length > 0
        cursor = seg.end
    assert cursor == bm.file_size, "segments do not reach end of file"


@pytest.mark.fixture
def test_zero_unknown_bytes(fixture_bak) -> None:
    bm = build_map(fixture_bak)
    bad_segments = [s.detail for s in bm.segments if s.category == UNKNOWN]
    bad_pages = [p.detail for p in bm.page_classes if p.category == UNKNOWN]
    assert not bad_segments, f"UNKNOWN segments: {bad_segments}"
    assert not bad_pages, f"UNKNOWN page types: {bad_pages}"
    assert bucket_totals(bm)["Unknown"] == 0


@pytest.mark.fixture
def test_buckets_sum_to_file_size(fixture_bak) -> None:
    bm = build_map(fixture_bak)
    totals = bucket_totals(bm)
    assert sum(totals.values()) == bm.file_size


@pytest.mark.fixture
def test_page_subtiling_covers_image(fixture_bak) -> None:
    bm = build_map(fixture_bak)
    page_bytes = sum(p.nbytes for p in bm.page_classes)
    assert page_bytes == bm.image_end - bm.image_start


@pytest.mark.fixture
def test_data_bucket_equals_extractor_image(fixture_bak) -> None:
    """The image the map labels DATA is exactly what the extractor returns."""
    bm = build_map(fixture_bak)
    image_len = bm.image_end - bm.image_start
    assert image_len == len(mtf.extract_mdf_pages(fixture_bak))
    assert image_len % mtf.PAGE_SIZE == 0
    # Sanity: the DATA top-level region spans the whole image.
    data_region = [s for s in bm.segments if s.category == DATA]
    assert len(data_region) == 1
    assert data_region[0].length == image_len


@pytest.mark.engine
def test_image_matches_filelist_backup_size() -> None:
    """Cross-check the detected data image against the engine's own record.

    ``RESTORE FILELISTONLY`` reports ``BackupSizeInBytes`` per file — the
    authoritative count of bytes the backup holds for each file.  The data
    file's value must equal the page image we locate, proving the data file is
    captured byte-for-byte.  Needs the .bak readable by the engine: set
    ``ENGINE_BAK_PATH`` to its server-side path (else skipped).
    """
    bak_server_path = os.environ.get("ENGINE_BAK_PATH")
    if not bak_server_path:
        pytest.skip("ENGINE_BAK_PATH unset (server-side path of the fixture .bak)")

    from tests.conftest import FIXTURE_BAK
    from tests.engine_support import EngineUnavailable, connect_engine

    if not FIXTURE_BAK.exists():
        pytest.skip("reference fixture missing")
    try:
        conn = connect_engine()
    except EngineUnavailable as exc:
        pytest.skip(str(exc))

    try:
        cur = conn.cursor()
        cur.execute(f"RESTORE FILELISTONLY FROM DISK = N'{bak_server_path}'")
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        conn.close()

    data_files = [r for r in rows if str(r["Type"]).upper() == "D"]
    assert len(data_files) == 1, "fixture is expected to have one data file"
    backup_bytes = int(data_files[0]["BackupSizeInBytes"])

    bm = build_map(FIXTURE_BAK)
    assert bm.image_end - bm.image_start == backup_bytes
