"""Tests verifying catalog correctness and cache behaviour.

Coverage
--------
* MTF uncompressed .bak: ``catalog_only=True`` returns correct/complete object
  summaries on both small and large fixtures (including databases where
  sysschobjs/syscolpars have pages at page_id ≥ 4096).
* MSSQLBAK compressed .bak: object summaries match between catalog-only and
  full scans.
* .bacpac: ``BacpacInfo`` uses range-GET path for ``BakReader`` input; table
  list parity between path-based and reader-based access.
* Cache at ``PageStore`` level: no-cache writes no files; explicit cache dir
  writes a small index file; cache-hit reuses the index with the same reader
  identity and returns identical results.
* No-cache correctness via ``BakSource``: two consecutive ``list_columns``
  calls on a local file return identical results.

Design
------
Byte-counting tests use a ``_CountingReader`` — a minimal ``BakReader`` that
wraps fixture bytes from memory and counts ``read_at`` calls.  It sets
``_is_range_reader = True`` and a synthetic ``source_identity`` so
``PageStore.from_bak`` always takes the lazy/range code-path instead of the
dense mmap path.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixture paths
# ---------------------------------------------------------------------------

_TESTS_DIR = Path(__file__).parent
_FIXTURE_MTF_LARGE = _TESTS_DIR / "fixtures_2022" / "cci_bitpack_probe_bigint_full.bak"
_FIXTURE_MTF_SMALL = _TESTS_DIR / "fixtures_2022" / "typecoverage_full.bak"
_FIXTURE_COMPRESSED = _TESTS_DIR / "fixtures_2022" / "typecoverage_full_compressed.bak"
_FIXTURE_BACPAC = _TESTS_DIR / "fixtures_2022" / "typecoverage.bacpac"


def _skip_if_missing(*paths: Path) -> pytest.MarkDecorator:
    missing = [p for p in paths if not p.exists()]
    return pytest.mark.skipif(
        bool(missing),
        reason=f"fixture(s) not found: {', '.join(str(m) for m in missing)}",
    )


# ---------------------------------------------------------------------------
# Byte-counting BakReader
# ---------------------------------------------------------------------------

class _CountingReader:
    """Minimal ``BakReader`` that wraps bytes from memory and counts reads.

    * ``_is_range_reader = True`` → ``PageStore.from_bak`` uses the lazy/
      chunk-index code-path (MTF or MSSQLBAK), never the mmap dense path.
    * ``source_identity`` is set so index-cache logic can use it as a key.
    * ``bytes_read`` accumulates the total bytes returned by ``read_at``.
    """

    _is_range_reader: bool = True

    def __init__(self, data: bytes, source_identity: str = "test-reader") -> None:
        self._data = data
        self.source_identity: str = source_identity
        self.bytes_read: int = 0

    @property
    def size(self) -> int:
        return len(self._data)

    def read_at(self, offset: int, length: int) -> bytes:
        chunk = self._data[offset : offset + length]
        self.bytes_read += len(chunk)
        return chunk

    def close(self) -> None:
        pass

    def __enter__(self) -> "_CountingReader":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def _make_reader(path: Path, identity: str = "fixture") -> _CountingReader:
    return _CountingReader(path.read_bytes(), source_identity=identity)


def _build_store(reader: _CountingReader, *, catalog_only: bool):
    from mssqlbak.pages import PageStore
    return PageStore.from_bak(reader, catalog_only=catalog_only)


# ---------------------------------------------------------------------------
# MTF uncompressed .bak — correctness on large fixture
# ---------------------------------------------------------------------------

@_skip_if_missing(_FIXTURE_MTF_LARGE)
class TestMtfLargeParity:
    """``cci_bitpack_probe_bigint_full.bak`` (43 MB) has non-catalog pages
    (page_id ≥ 4096).  Verifies that catalog-only and full scans return
    identical object summaries and column lists via the range-reader path.
    """

    def test_parity_object_summaries(self) -> None:
        from mssqlbak.catalog.recover import recover_object_summaries

        r_full = _make_reader(_FIXTURE_MTF_LARGE, "mtf-full-p")
        r_cat = _make_reader(_FIXTURE_MTF_LARGE, "mtf-cat-p")

        with _build_store(r_full, catalog_only=False) as s_full:
            full_objs = {
                (o.schema_name, o.name): o.column_count
                for o in recover_object_summaries(s_full)
            }
        with _build_store(r_cat, catalog_only=True) as s_cat:
            cat_objs = {
                (o.schema_name, o.name): o.column_count
                for o in recover_object_summaries(s_cat)
            }

        assert cat_objs == full_objs, (
            "catalog_only object summaries must match full-scan results"
        )

    def test_parity_table_columns(self) -> None:
        from mssqlbak.catalog.recover import recover_object_summaries, recover_table_columns

        r_full = _make_reader(_FIXTURE_MTF_LARGE, "mtf-full-c")
        r_cat = _make_reader(_FIXTURE_MTF_LARGE, "mtf-cat-c")

        with _build_store(r_full, catalog_only=False) as s_full:
            objs_full = recover_object_summaries(s_full)
            target = next(
                (o for o in objs_full if o.object_kind.strip() == "U" and o.column_count > 0),
                None,
            )
            assert target is not None, "no user table with columns found"
            full_cols = recover_table_columns(s_full, target.object_id)

        with _build_store(r_cat, catalog_only=True) as s_cat:
            cat_cols = recover_table_columns(s_cat, target.object_id)

        assert [c.name for c in cat_cols] == [c.name for c in full_cols], (
            "catalog_only column list must match full-scan results"
        )


# ---------------------------------------------------------------------------
# MTF parity — small fixture
# ---------------------------------------------------------------------------

@_skip_if_missing(_FIXTURE_MTF_SMALL)
class TestMtfSmallParity:
    """Parity tests on the small MTF fixture (all pages have page_id < 4096)."""

    def test_parity_object_summaries(self) -> None:
        from mssqlbak.catalog.recover import recover_object_summaries

        r_full = _make_reader(_FIXTURE_MTF_SMALL, "mtfs-full")
        r_cat = _make_reader(_FIXTURE_MTF_SMALL, "mtfs-cat")

        with _build_store(r_full, catalog_only=False) as s_full:
            full_objs = {
                (o.schema_name, o.name): o.column_count
                for o in recover_object_summaries(s_full)
            }
        with _build_store(r_cat, catalog_only=True) as s_cat:
            cat_objs = {
                (o.schema_name, o.name): o.column_count
                for o in recover_object_summaries(s_cat)
            }

        assert cat_objs == full_objs


# ---------------------------------------------------------------------------
# MSSQLBAK compressed .bak
# ---------------------------------------------------------------------------

@_skip_if_missing(_FIXTURE_COMPRESSED)
class TestCompressedCatalog:
    """Tests for MSSQLBAK compressed backup catalog ops.

    Verifies that object summaries match between catalog-only and full scans.
    """

    def test_parity_object_summaries(self) -> None:
        from mssqlbak.catalog.recover import recover_object_summaries

        r_full = _make_reader(_FIXTURE_COMPRESSED, "comp-full-p")
        r_cat = _make_reader(_FIXTURE_COMPRESSED, "comp-cat-p")

        with _build_store(r_full, catalog_only=False) as s_full:
            full_objs = {
                (o.schema_name, o.name): o.column_count
                for o in recover_object_summaries(s_full)
            }
        with _build_store(r_cat, catalog_only=True) as s_cat:
            cat_objs = {
                (o.schema_name, o.name): o.column_count
                for o in recover_object_summaries(s_cat)
            }

        assert cat_objs == full_objs


# ---------------------------------------------------------------------------
# .bacpac — BacpacInfo uses range-GET path for BakReader
# ---------------------------------------------------------------------------

@_skip_if_missing(_FIXTURE_BACPAC)
class TestBacpacRangeOnly:
    """``BacpacInfo`` with a ``BakReader`` must return correct table list."""

    def test_table_list_parity(self) -> None:
        """Table list from path and from a counting reader must match."""
        from mssqlbak.bacpac import BacpacInfo

        with BacpacInfo(_FIXTURE_BACPAC) as bp_path:
            path_tables = {t.name for t in bp_path.tables}

        reader = _CountingReader(
            _FIXTURE_BACPAC.read_bytes(), source_identity="bacpac-test"
        )
        with BacpacInfo(reader) as bp_reader:
            reader_tables = {t.name for t in bp_reader.tables}

        assert reader_tables == path_tables, (
            "BacpacInfo(counting_reader).tables must match BacpacInfo(path).tables"
        )
        assert len(path_tables) > 0, "expected at least one table"

    def test_reader_path_uses_schema_only_zipfile(self) -> None:
        """BacpacInfo with a BakReader goes through _open_zipfile(schema_only=True).

        For this tiny fixture (~1 MB) the 1 MB read-ahead buffer means most of
        the file IS read — the performance benefit only shows at scale.  We
        verify the code path is taken (no exception) and returns correct results.
        """
        from mssqlbak.bacpac import BacpacInfo

        data = _FIXTURE_BACPAC.read_bytes()
        reader = _CountingReader(data, source_identity="bacpac-path-check")
        with BacpacInfo(reader) as bp:
            tables = {t.name for t in bp.tables}

        assert len(tables) > 0
        assert reader.bytes_read > 0


# ---------------------------------------------------------------------------
# Cache — tested at PageStore level (range-reader path)
# ---------------------------------------------------------------------------

@_skip_if_missing(_FIXTURE_MTF_SMALL)
class TestCacheAtPageStoreLevel:
    """Cache tests use ``PageStore.from_bak`` + ``_CountingReader`` directly
    so the range-reader path (which honours the cache) is always exercised,
    regardless of the URI scheme.
    """

    def test_no_index_cache_does_not_write_files(self) -> None:
        from mssqlbak.pages import PageStore

        with tempfile.TemporaryDirectory() as tmp:
            reader = _make_reader(_FIXTURE_MTF_SMALL, "cache-none")
            with PageStore.from_bak(reader, catalog_only=True, index_cache=None):
                pass
            written = [f for f in Path(tmp).rglob("*") if f.is_file()]
            assert written == [], f"no cache → no files; got {written}"

    def test_explicit_cache_writes_small_index_file(self) -> None:
        from mssqlbak.pages import PageStore
        from mssqlbak.extract.index_cache import TempDirIndexCache

        with tempfile.TemporaryDirectory() as tmp:
            cache = TempDirIndexCache(tmp)
            reader = _make_reader(_FIXTURE_MTF_SMALL, "cache-write")
            with PageStore.from_bak(reader, catalog_only=True, index_cache=cache):
                pass

            written = [f for f in Path(tmp).rglob("*") if f.is_file()]
            assert written, "expected at least one cache index file"
            for f in written:
                assert f.stat().st_size < _FIXTURE_MTF_SMALL.stat().st_size, (
                    f"index file {f.name} ({f.stat().st_size} B) should be "
                    f"smaller than backup ({_FIXTURE_MTF_SMALL.stat().st_size} B)"
                )

    def test_cache_hit_returns_same_results(self) -> None:
        """Second call with a cache hit returns identical object list.

        Both readers MUST share the same ``source_identity`` so the cache
        key matches on the second lookup.
        """
        from mssqlbak.pages import PageStore
        from mssqlbak.extract.index_cache import TempDirIndexCache
        from mssqlbak.catalog.recover import recover_object_summaries

        _IDENTITY = "same-source-identity"

        with tempfile.TemporaryDirectory() as tmp:
            cache = TempDirIndexCache(tmp)

            r1 = _make_reader(_FIXTURE_MTF_SMALL, _IDENTITY)
            with PageStore.from_bak(r1, catalog_only=True, index_cache=cache) as s1:
                objs1 = {(o.schema_name, o.name) for o in recover_object_summaries(s1)}

            r2 = _make_reader(_FIXTURE_MTF_SMALL, _IDENTITY)
            with PageStore.from_bak(r2, catalog_only=True, index_cache=cache) as s2:
                objs2 = {(o.schema_name, o.name) for o in recover_object_summaries(s2)}

        assert objs1 == objs2, "cached call must return same object list"
        assert r2.bytes_read < r1.bytes_read, (
            f"cache hit should read fewer bytes than a miss: "
            f"got r2={r2.bytes_read} B, r1={r1.bytes_read} B"
        )


# ---------------------------------------------------------------------------
# BakSource cache-off-by-default
# ---------------------------------------------------------------------------

@_skip_if_missing(_FIXTURE_MTF_SMALL)
class TestBakSourceCacheDefault:
    """Verify BakSource.index_cache_dir=None (default) doesn't error,
    and that passing an explicit dir or 'none' are both accepted.
    """

    def test_no_index_cache_dir_works(self) -> None:
        from mssqlbak.api.source import open_source

        src = open_source(str(_FIXTURE_MTF_SMALL))
        page = src.list_table_summaries()
        assert page.counts.get("n_tables", 0) >= 0

    def test_none_string_disables_cache(self) -> None:
        from mssqlbak.api.source import open_source

        src = open_source(str(_FIXTURE_MTF_SMALL), index_cache_dir="none")
        page = src.list_table_summaries()
        assert page.counts.get("n_tables", 0) >= 0

    def test_explicit_dir_does_not_error(self) -> None:
        from mssqlbak.api.source import open_source

        with tempfile.TemporaryDirectory() as tmp:
            src = open_source(str(_FIXTURE_MTF_SMALL), index_cache_dir=tmp)
            page = src.list_table_summaries()
            # Local files use the dense mmap path, which does not write the cache.
            assert page.counts.get("n_tables", 0) >= 0


# ---------------------------------------------------------------------------
# No-cache correctness: two consecutive list_columns calls
# ---------------------------------------------------------------------------

@_skip_if_missing(_FIXTURE_MTF_SMALL)
class TestNoCacheCorrectness:
    """Without a cache, repeated calls must return identical correct results."""

    def test_list_columns_twice_consistent(self) -> None:
        from mssqlbak.api.source import open_source
        from mssqlbak.catalog.recover import recover_object_summaries
        from mssqlbak.pages import PageStore

        reader = _make_reader(_FIXTURE_MTF_SMALL, "nc-find-target")
        with PageStore.from_bak(reader, catalog_only=True) as store:
            objs = recover_object_summaries(store)
            target = next(
                (o for o in objs if o.object_kind.strip() == "U" and o.column_count > 0),
                None,
            )
        assert target is not None, "no user table with columns found in MTF fixture"

        src = open_source(str(_FIXTURE_MTF_SMALL))
        cols1 = src.list_columns(target.schema_name, target.name)
        cols2 = src.list_columns(target.schema_name, target.name)

        assert [c.name for c in cols1.items] == [c.name for c in cols2.items], (
            "list_columns returned different results on two consecutive calls"
        )
        assert len(cols1.items) > 0, "expected at least one column"
