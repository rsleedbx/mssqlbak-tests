"""Chunk-index lookup semantics, including the fuzzy-backup re-copy case.

An online (fuzzy) backup can store the same extent twice — once in the main
data-file scan and again in a re-scan pass that re-copies pages modified during
the backup.  The compressed lazy path must resolve such a duplicated extent to
the **latest** copy (the post-modification image SQL Server's RESTORE keeps),
matching the eager ``extract_mdf_files_compressed`` last-wins behaviour.
"""
from __future__ import annotations

from mssqlbak.chunk_index import EXTENT_PAGES, ChunkIndex, _FileChunkArray


def test_filechunkarray_unique_extents_roundtrip() -> None:
    arr = _FileChunkArray()
    arr.add(extent_id=5, chunk_offset=1000, read_length=40)
    arr.add(extent_id=2, chunk_offset=200, read_length=30)
    arr.freeze()
    e2 = arr.lookup(2)
    e5 = arr.lookup(5)
    assert e2 is not None and e2.chunk_offset == 200 and e2.read_length == 30
    assert e5 is not None and e5.chunk_offset == 1000 and e5.read_length == 40
    assert arr.lookup(99) is None


def test_filechunkarray_duplicate_extent_returns_latest() -> None:
    """A re-copied extent (added twice) resolves to the last-inserted chunk."""
    arr = _FileChunkArray()
    # Main scan copy first, then the re-scan (post-modification) copy.
    arr.add(extent_id=7, chunk_offset=100, read_length=40)   # stale, pre-modification
    arr.add(extent_id=7, chunk_offset=900, read_length=44)   # latest, post-modification
    arr.freeze()
    e = arr.lookup(7)
    assert e is not None
    assert (e.chunk_offset, e.read_length) == (900, 44), (
        "duplicated extent must resolve to the latest (re-copied) chunk"
    )


def test_filechunkarray_duplicate_among_many() -> None:
    arr = _FileChunkArray()
    arr.add(extent_id=1, chunk_offset=10, read_length=8)
    arr.add(extent_id=4, chunk_offset=40, read_length=8)     # stale dup
    arr.add(extent_id=2, chunk_offset=20, read_length=8)
    arr.add(extent_id=4, chunk_offset=400, read_length=9)    # latest dup
    arr.add(extent_id=9, chunk_offset=90, read_length=8)
    arr.freeze()
    e = arr.lookup(4)
    assert e is not None and (e.chunk_offset, e.read_length) == (400, 9)
    # Neighbours unaffected.
    assert arr.lookup(2) is not None and arr.lookup(2).chunk_offset == 20  # type: ignore[union-attr]
    assert arr.lookup(9) is not None and arr.lookup(9).chunk_offset == 90  # type: ignore[union-attr]


def test_chunkindex_duplicate_page_resolves_to_latest_chunk() -> None:
    """ChunkIndex.lookup returns the latest chunk for a re-copied page's extent."""
    idx = ChunkIndex()
    page_id = 9 * EXTENT_PAGES + 3  # extent 9, a non-catalog page
    idx.add_chunk(file_id=1, first_page_id=page_id, chunk_offset=100, read_length=40)
    idx.add_chunk(file_id=1, first_page_id=page_id, chunk_offset=7000, read_length=44)
    idx.freeze()
    entry = idx.lookup(1, page_id)
    assert entry is not None
    assert (entry.chunk_offset, entry.read_length) == (7000, 44)
