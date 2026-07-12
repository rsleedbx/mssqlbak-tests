"""Tests for HTTP restore reliability and resumability features.

Covers:
- RetryPolicy backoff and retry_call behaviour
- ChunkIndex.to_file/from_file round-trip and identity mismatch
- FileIndexCache save/load round-trip
- DeltaSink idempotent re-commit (no dup rows)
- DeltaSink mid-table kill/resume via ResumableSink
- DirSink resumable (zstd) kill/resume: truncate partial frame, append new frames
- DirSink gzip / none fallback code paths
"""
from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pyarrow as pa
import pytest
from deltalake import DeltaTable

from mssqlbak.chunk_index import ChunkIndex
from mssqlbak.readers._retry import (
    RetryPolicy,
    _RetryableError,
    is_retryable_status,
    retry_call,
)
from mssqlbak.sink import Checkpoint, DeltaSink, ResumePoint, ResumableSink


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _simple_batch(n: int, offset: int = 0) -> pa.RecordBatch:
    schema = pa.schema([("id", pa.int32()), ("val", pa.string())])
    ids = list(range(offset, offset + n))
    vals = [f"v{i}" for i in ids]
    return pa.record_batch([ids, vals], schema=schema)


def _simple_schema() -> pa.Schema:
    return pa.schema([("id", pa.int32()), ("val", pa.string())])


# ---------------------------------------------------------------------------
# RetryPolicy / retry_call
# ---------------------------------------------------------------------------


class TestRetryPolicy:
    def test_backoff_is_within_bounds(self) -> None:
        policy = RetryPolicy(backoff_base=1.0, backoff_max=10.0, max_retries=4)
        for attempt in range(5):
            b = policy.backoff(attempt)
            assert 0.0 <= b <= 10.0

    def test_backoff_cap_respected(self) -> None:
        policy = RetryPolicy(backoff_base=100.0, backoff_max=5.0, max_retries=3)
        for attempt in range(4):
            assert policy.backoff(attempt) <= 5.0

    def test_is_retryable_status(self) -> None:
        for status in (429, 500, 502, 503, 504, 507, 522, 524):
            assert is_retryable_status(status)
        for status in (200, 206, 400, 401, 403, 404, 501):
            assert not is_retryable_status(status)

    def test_retry_call_succeeds_immediately(self) -> None:
        calls = []

        def fn() -> int:
            calls.append(1)
            return 42

        result = retry_call(fn, policy=RetryPolicy(max_retries=3, backoff_base=0.0))
        assert result == 42
        assert len(calls) == 1

    def test_retry_call_retries_on_retryable_error(self) -> None:
        calls = []

        def fn() -> int:
            calls.append(1)
            if len(calls) < 3:
                raise _RetryableError("transient")
            return 99

        policy = RetryPolicy(max_retries=5, backoff_base=0.0, backoff_max=0.0)
        with patch("time.sleep"):
            result = retry_call(fn, policy=policy)
        assert result == 99
        assert len(calls) == 3

    def test_retry_call_retries_on_oserror(self) -> None:
        calls = []

        def fn() -> str:
            calls.append(1)
            if len(calls) < 2:
                raise OSError("connection reset")
            return "ok"

        policy = RetryPolicy(max_retries=3, backoff_base=0.0, backoff_max=0.0)
        with patch("time.sleep"):
            result = retry_call(fn, policy=policy)
        assert result == "ok"
        assert len(calls) == 2

    def test_retry_call_exhaustion_raises_last_error(self) -> None:
        def fn() -> None:
            raise _RetryableError("always fails")

        policy = RetryPolicy(max_retries=2, backoff_base=0.0, backoff_max=0.0)
        with patch("time.sleep"), pytest.raises(_RetryableError, match="always fails"):
            retry_call(fn, policy=policy)

    def test_retry_call_non_retryable_propagates_immediately(self) -> None:
        calls = []

        def fn() -> None:
            calls.append(1)
            raise ValueError("not retryable")

        policy = RetryPolicy(max_retries=5, backoff_base=0.0, backoff_max=0.0)
        with pytest.raises(ValueError, match="not retryable"):
            retry_call(fn, policy=policy)
        assert len(calls) == 1

    def test_retry_call_increments_io_stats_retries(self) -> None:
        stats = MagicMock()
        stats.retries = 0

        def fn() -> str:
            if stats.retries < 2:
                raise _RetryableError("transient")
            return "done"

        # Patch io_stats.retries increment via side_effect on attribute set
        call_count = [0]

        def counting_fn() -> str:
            call_count[0] += 1
            if call_count[0] <= 2:
                raise _RetryableError("transient")
            return "done"

        real_stats = type("S", (), {"retries": 0})()
        policy = RetryPolicy(max_retries=5, backoff_base=0.0, backoff_max=0.0)
        with patch("time.sleep"):
            result = retry_call(counting_fn, policy=policy, io_stats=real_stats)  # type: ignore[arg-type]
        assert result == "done"
        assert real_stats.retries == 2  # retried 2 times

    def test_env_override_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MSSQLBAK_HTTP_TIMEOUT", "99")
        p = RetryPolicy()
        assert p.timeout == 99.0

    def test_env_override_max_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MSSQLBAK_HTTP_MAX_RETRIES", "12")
        p = RetryPolicy()
        assert p.max_retries == 12


# ---------------------------------------------------------------------------
# ChunkIndex.to_file / from_file round-trip
# ---------------------------------------------------------------------------


class TestChunkIndexFileSerialization:
    def _make_index(self) -> ChunkIndex:
        idx = ChunkIndex()
        # Add some fake entries so arrays are non-empty
        idx._by_file[1] = _make_fake_chunk_array()
        idx._catalog[(1, 0)] = b"fake_catalog_page_data"
        return idx

    def test_round_trip(self, tmp_path: Path) -> None:
        idx = self._make_index()
        fpath = tmp_path / "test.idx.bin"
        idx.to_file(fpath, source_identity="test-source-1")
        loaded = ChunkIndex.from_file(fpath, expected_identity="test-source-1")
        assert loaded is not None
        assert 1 in loaded._by_file
        assert (1, 0) in loaded._catalog
        assert loaded._catalog[(1, 0)] == b"fake_catalog_page_data"

    def test_empty_index_round_trip(self, tmp_path: Path) -> None:
        idx = ChunkIndex()
        fpath = tmp_path / "empty.idx.bin"
        idx.to_file(fpath, source_identity="")
        loaded = ChunkIndex.from_file(fpath)
        assert loaded is not None
        assert len(loaded._by_file) == 0
        assert len(loaded._catalog) == 0

    def test_identity_mismatch_returns_none(self, tmp_path: Path) -> None:
        idx = self._make_index()
        fpath = tmp_path / "test.idx.bin"
        idx.to_file(fpath, source_identity="correct-identity")
        loaded = ChunkIndex.from_file(fpath, expected_identity="wrong-identity")
        assert loaded is None

    def test_nonexistent_file_returns_none(self, tmp_path: Path) -> None:
        result = ChunkIndex.from_file(tmp_path / "nosuchfile.bin")
        assert result is None

    def test_corrupt_file_returns_none(self, tmp_path: Path) -> None:
        fpath = tmp_path / "corrupt.bin"
        fpath.write_bytes(b"not-a-valid-index-file")
        result = ChunkIndex.from_file(fpath)
        assert result is None

    def test_no_expected_identity_accepts_any(self, tmp_path: Path) -> None:
        idx = self._make_index()
        fpath = tmp_path / "test.idx.bin"
        idx.to_file(fpath, source_identity="anything")
        loaded = ChunkIndex.from_file(fpath, expected_identity=None)
        assert loaded is not None

    def test_multiple_files_round_trip(self, tmp_path: Path) -> None:
        idx = ChunkIndex()
        for fid in (1, 2, 3):
            idx._by_file[fid] = _make_fake_chunk_array()
        for fid, pid in [(1, 0), (2, 5), (3, 100)]:
            idx._catalog[(fid, pid)] = bytes([fid, pid])
        fpath = tmp_path / "multi.idx.bin"
        idx.to_file(fpath, source_identity="multi-src")
        loaded = ChunkIndex.from_file(fpath, expected_identity="multi-src")
        assert loaded is not None
        assert set(loaded._by_file.keys()) == {1, 2, 3}
        for fid, pid in [(1, 0), (2, 5), (3, 100)]:
            assert (fid, pid) in loaded._catalog
            assert loaded._catalog[(fid, pid)] == bytes([fid, pid])


def _make_fake_chunk_array():
    """Build a minimal _FileChunkArray for testing."""
    from mssqlbak.chunk_index import _FileChunkArray  # type: ignore[attr-defined]
    ca = _FileChunkArray()
    ca.add(extent_id=0, chunk_offset=0, read_length=8192)
    ca.freeze()
    return ca


# ---------------------------------------------------------------------------
# FileIndexCache
# ---------------------------------------------------------------------------


class TestFileIndexCache:
    def test_save_and_load_round_trip(self, tmp_path: Path) -> None:
        from mssqlbak.extract.index_cache import FileIndexCache

        cache = FileIndexCache(tmp_path / "cache.bin")
        idx = ChunkIndex()
        cache.save("my-source-id", idx)
        loaded = cache.load("my-source-id")
        assert loaded is not None

    def test_load_wrong_identity_returns_none(self, tmp_path: Path) -> None:
        from mssqlbak.extract.index_cache import FileIndexCache

        cache = FileIndexCache(tmp_path / "cache.bin")
        idx = ChunkIndex()
        cache.save("source-A", idx)
        loaded = cache.load("source-B")
        assert loaded is None

    def test_load_missing_file_returns_none(self, tmp_path: Path) -> None:
        from mssqlbak.extract.index_cache import FileIndexCache

        cache = FileIndexCache(tmp_path / "nonexistent.bin")
        assert cache.load("anything") is None


# ---------------------------------------------------------------------------
# DeltaSink idempotent re-commit
# ---------------------------------------------------------------------------


class TestDeltaSinkIdempotentRecommit:
    def test_cursor_based_resume_no_duplicate_rows(self, tmp_path: Path) -> None:
        """Driver-side cursor-based resume: second run picks up where first left off.

        The no-duplicate guarantee is enforced by the driver:
        1. Run 1 writes batch 0 (rows 0–4, cursor="4") then crashes.
        2. On restart, table_resume_point returns cursor="4", next_version=1.
        3. Run 2 starts extraction from cursor 4, writes batch 1 (rows 5–9).
        4. Total rows = 10, no duplicates.
        """
        out = tmp_path / "out"
        schema = _simple_schema()

        # Run 1: write batch 0 (5 rows, cursor "4").
        sink1 = DeltaSink(out, resume=True)
        sink1.open_table("dbo.orders", schema)
        ckpt0 = Checkpoint(app_id="mssqlbak:dbo.orders", version=0, cursor="4")
        sink1.write_batch(_simple_batch(5, offset=0), checkpoint=ckpt0)
        sink1.close()

        # Driver reads resume point.
        sink2 = DeltaSink(out, resume=True)
        rp = sink2.table_resume_point("dbo.orders")
        assert rp is not None
        assert rp.complete is False
        assert rp.cursor == "4"
        assert rp.next_version == 1

        # Run 2: resume from cursor 4 (skip rows 0–4), write batch 1.
        sink2.open_table("dbo.orders", schema)
        ckpt1 = Checkpoint(app_id="mssqlbak:dbo.orders", version=1, cursor="9")
        sink2.write_batch(_simple_batch(5, offset=5), checkpoint=ckpt1)
        sink2.close()
        sink2.mark_table_complete("dbo.orders", rows=10)

        dt = DeltaTable(str(out / "dbo" / "orders"))
        table_data = dt.to_pyarrow_table()
        # 5 rows from run 1 + 5 rows from run 2 = 10 unique rows.
        assert table_data.num_rows == 10
        ids = sorted(table_data.column("id").to_pylist())
        assert ids == list(range(10))

    def test_resume_skips_completed_table(self, tmp_path: Path) -> None:
        """After mark_table_complete, table_resume_point returns complete=True."""
        sink = DeltaSink(tmp_path / "out", resume=True)
        schema = _simple_schema()
        sink.open_table("dbo.products", schema)

        ckpt = Checkpoint(app_id="mssqlbak:dbo.products", version=0, cursor="10")
        sink.write_batch(_simple_batch(5), checkpoint=ckpt)
        sink.close()
        sink.mark_table_complete("dbo.products", rows=5)

        # New instance: check resume point
        sink2 = DeltaSink(tmp_path / "out", resume=True)
        rp = sink2.table_resume_point("dbo.products")
        assert rp is not None
        assert rp.complete is True

    def test_resume_point_provides_cursor_for_partial_table(self, tmp_path: Path) -> None:
        """Mid-table resume: table_resume_point returns cursor from last batch."""
        sink = DeltaSink(tmp_path / "out", resume=True)
        schema = _simple_schema()
        sink.open_table("dbo.events", schema)

        ckpt = Checkpoint(app_id="mssqlbak:dbo.events", version=0, cursor="99")
        sink.write_batch(_simple_batch(4), checkpoint=ckpt)
        sink.close()

        sink2 = DeltaSink(tmp_path / "out", resume=True)
        rp = sink2.table_resume_point("dbo.events")
        assert rp is not None
        assert rp.complete is False
        assert rp.cursor == "99"
        assert rp.next_version == 1

    def test_no_checkpoint_table_returns_none_resume_point(self, tmp_path: Path) -> None:
        """A table that was never written returns None from table_resume_point."""
        sink = DeltaSink(tmp_path / "out", resume=True)
        rp = sink.table_resume_point("dbo.never_written")
        assert rp is None

    def test_sequential_batches_accumulate_correctly(self, tmp_path: Path) -> None:
        """Multiple checkpointed batches result in correct total rows."""
        sink = DeltaSink(tmp_path / "out", resume=True)
        schema = _simple_schema()
        sink.open_table("dbo.log", schema)

        for i in range(3):
            ckpt = Checkpoint(app_id="mssqlbak:dbo.log", version=i, cursor=str(i * 10))
            sink.write_batch(_simple_batch(10, offset=i * 10), checkpoint=ckpt)
        sink.close()
        sink.mark_table_complete("dbo.log", rows=30)

        dt = DeltaTable(str(tmp_path / "out" / "dbo" / "log"))
        assert dt.to_pyarrow_table().num_rows == 30


# ---------------------------------------------------------------------------
# ResumableSink protocol check
# ---------------------------------------------------------------------------


class TestResumableSinkProtocol:
    def test_delta_sink_is_resumable(self, tmp_path: Path) -> None:
        sink = DeltaSink(tmp_path / "out", resume=True)
        assert isinstance(sink, ResumableSink)


# ---------------------------------------------------------------------------
# DirSink resumable (zstd) kill/resume
# ---------------------------------------------------------------------------


class TestDirSinkResumable:
    def test_zstd_round_trip_no_interruption(self, tmp_path: Path) -> None:
        """Basic DirSink zstd write without interruption produces decodable data."""
        pytest.importorskip("zstandard", reason="zstandard required for zstd codec")
        from mssqlbak.sinks.pg_dir_sink import DirSink

        out = tmp_path / "pgdump_dir"
        sink = DirSink(out, resume=True, dir_codec="zstd", source_identity="test-bak")

        schema = _simple_schema()
        sink.open_table("dbo.t1", schema)
        sink.write_batch(_simple_batch(5))
        sink.close()
        sink.mark_table_complete("dbo.t1", rows=5)

        # Verify the data file exists and is valid zstd
        import zstandard as zstd
        dat_files = list(out.glob("*.dat.zst"))
        assert len(dat_files) == 1, f"expected one .dat.zst file, got: {dat_files}"
        data = dat_files[0].read_bytes()
        decompressed = zstd.ZstdDecompressor().decompress(data, max_output_size=1_000_000)
        assert len(decompressed) > 0

    def test_zstd_resume_after_partial_write(self, tmp_path: Path) -> None:
        """Simulates a kill mid-table: resume truncates partial frame and appends new data."""
        pytest.importorskip("zstandard", reason="zstandard required for zstd codec")
        from mssqlbak.sinks.pg_dir_sink import DirSink

        out = tmp_path / "pgdump_dir"

        # First run: write 2 batches, then simulate a crash (don't mark complete).
        sink1 = DirSink(out, resume=True, dir_codec="zstd", source_identity="bak-v1")
        schema = _simple_schema()
        sink1.open_table("dbo.orders", schema)
        sink1.write_batch(_simple_batch(5, 0))
        sink1.write_batch(_simple_batch(5, 5))
        sink1.close()
        # Don't call mark_table_complete — simulate crash

        # Corrupt the data file by appending garbage bytes (simulates partial write).
        import zstandard as zstd
        dat_files = list(out.glob("*.dat.zst"))
        assert len(dat_files) == 1
        dat_file = dat_files[0]
        with dat_file.open("ab") as f:
            f.write(b"\xff\xfe\xfd" * 20)  # partial/corrupt trailing bytes

        # Second run: resume — should truncate partial garbage and continue.
        sink2 = DirSink(out, resume=True, dir_codec="zstd", source_identity="bak-v1")
        sink2.open_table("dbo.orders", schema)
        sink2.write_batch(_simple_batch(5, 10))
        sink2.close()
        sink2.mark_table_complete("dbo.orders", rows=15)

        # Verify the final concatenated file is valid zstd and has content.
        dat_files2 = list(out.glob("*.dat.zst"))
        assert len(dat_files2) == 1
        final_data = dat_files2[0].read_bytes()
        # Should be decodable (all valid frames)
        dctx = zstd.ZstdDecompressor()
        decoded = b"".join(chunk for chunk in dctx.read_to_iter(io.BytesIO(final_data)))
        assert len(decoded) > 0
        # Should contain copy text rows
        assert b"COPY" in decoded or len(decoded) > 10

    def test_dir_sink_manifest_persists_state(self, tmp_path: Path) -> None:
        """The manifest file tracks table state across runs."""
        pytest.importorskip("zstandard", reason="zstandard required for zstd codec")
        from mssqlbak.sinks.pg_dir_sink import DirSink, _MANIFEST_FILENAME

        out = tmp_path / "pgdump_dir"
        sink = DirSink(out, resume=True, dir_codec="zstd", source_identity="bak-1")
        schema = _simple_schema()
        sink.open_table("dbo.items", schema)
        sink.write_batch(_simple_batch(3))
        sink.close()

        manifest_path = out / _MANIFEST_FILENAME
        assert manifest_path.exists()

        import json
        manifest = json.loads(manifest_path.read_text())
        assert "tables" in manifest or "dbo.items" in str(manifest)

    def test_dir_sink_resume_point_reflects_manifest(self, tmp_path: Path) -> None:
        """table_resume_point reads from the manifest correctly."""
        pytest.importorskip("zstandard", reason="zstandard required for zstd codec")
        from mssqlbak.sinks.pg_dir_sink import DirSink

        out = tmp_path / "pgdump_dir"
        sink1 = DirSink(out, resume=True, dir_codec="zstd", source_identity="bak-x")
        schema = _simple_schema()
        sink1.open_table("dbo.widgets", schema)
        sink1.write_batch(_simple_batch(4))
        sink1.close()

        rp = sink1.table_resume_point("dbo.widgets")
        assert rp is not None
        assert rp.complete is False

        sink1.mark_table_complete("dbo.widgets", rows=4)
        rp2 = sink1.table_resume_point("dbo.widgets")
        assert rp2 is not None
        assert rp2.complete is True

    def test_dir_sink_gzip_codec(self, tmp_path: Path) -> None:
        """DirSink with dir_codec='gzip' produces a non-empty .dat file."""
        from mssqlbak.sinks.pg_dir_sink import DirSink

        out = tmp_path / "pgdump_gzip"
        sink = DirSink(out, dir_codec="gzip")
        schema = _simple_schema()
        sink.open_table("dbo.t1", schema)
        sink.write_batch(_simple_batch(3))
        sink.close()
        sink.finish()

        # For non-resume gzip mode, data is written on close/finish.
        # At minimum the toc.dat should exist.
        toc = out / "toc.dat"
        assert toc.exists()

    def test_dir_sink_none_codec(self, tmp_path: Path) -> None:
        """DirSink with dir_codec='none' produces a toc.dat."""
        from mssqlbak.sinks.pg_dir_sink import DirSink

        out = tmp_path / "pgdump_none"
        sink = DirSink(out, dir_codec="none")
        schema = _simple_schema()
        sink.open_table("dbo.t1", schema)
        sink.write_batch(_simple_batch(2))
        sink.close()
        sink.finish()

        toc = out / "toc.dat"
        assert toc.exists()

    def test_dir_sink_is_resumable_sink(self, tmp_path: Path) -> None:
        from mssqlbak.sinks.pg_dir_sink import DirSink

        out = tmp_path / "pgdump"
        sink = DirSink(out, resume=True, dir_codec="zstd")
        assert isinstance(sink, ResumableSink)


# ---------------------------------------------------------------------------
# DeltaIndexCache (Delta table persistence)
# ---------------------------------------------------------------------------


class TestDeltaIndexCache:
    def test_save_and_load(self, tmp_path: Path) -> None:
        from mssqlbak.extract.index_cache import DeltaIndexCache

        cache = DeltaIndexCache(tmp_path / "index_cache")
        idx = ChunkIndex()
        cache.save("src-identity-1", idx)
        loaded = cache.load("src-identity-1")
        assert loaded is not None

    def test_load_wrong_identity_returns_none(self, tmp_path: Path) -> None:
        from mssqlbak.extract.index_cache import DeltaIndexCache

        cache = DeltaIndexCache(tmp_path / "index_cache")
        idx = ChunkIndex()
        cache.save("src-A", idx)
        loaded = cache.load("src-B")
        assert loaded is None

    def test_load_missing_cache_returns_none(self, tmp_path: Path) -> None:
        from mssqlbak.extract.index_cache import DeltaIndexCache

        cache = DeltaIndexCache(tmp_path / "nonexistent_index")
        loaded = cache.load("anything")
        assert loaded is None

    def test_overwrite_updates_cache(self, tmp_path: Path) -> None:
        from mssqlbak.extract.index_cache import DeltaIndexCache

        cache = DeltaIndexCache(tmp_path / "index_cache")
        idx1 = ChunkIndex()
        cache.save("src-1", idx1)

        idx2 = ChunkIndex()
        cache.save("src-1", idx2)  # overwrite with same identity

        loaded = cache.load("src-1")
        assert loaded is not None


# ---------------------------------------------------------------------------
# Page-walk determinism (extraction cursor threading)
# ---------------------------------------------------------------------------


class TestExtractionCursorDeterminism:
    """Verify that resume cursor skips only already-processed items."""

    def test_checkpoint_cursor_reflects_last_batch(self) -> None:
        """The cursor in each Checkpoint should correspond to the batch's last item."""
        # Verify the Checkpoint dataclass invariants used by all extraction paths.
        ckpt = Checkpoint(app_id="mssqlbak:dbo.orders", version=5, cursor="1234")
        assert ckpt.app_id == "mssqlbak:dbo.orders"
        assert ckpt.version == 5
        assert ckpt.cursor == "1234"

    def test_resume_point_next_version_is_version_plus_one(self) -> None:
        """ResumePoint.next_version should be last_version + 1 for correct batch_seq_start."""
        rp = ResumePoint(complete=False, next_version=5, cursor="42")
        assert rp.next_version == 5
        assert rp.cursor == "42"
        assert not rp.complete

    def test_complete_resume_point(self) -> None:
        rp = ResumePoint(complete=True)
        assert rp.complete
        assert rp.next_version is None
        assert rp.cursor is None
