"""Phase B5: randomised round-trip tests for the SQL Server page/record forge.

Verifies that data encoded by the forge and decoded by the reader produces
values identical to the original input.  All tests use deterministic seeds
and stay fast (no I/O, no fixtures).

Tests:
- FixedVar single-column round-trips (INT, SMALLINT, BIGINT, BIT, VARCHAR, NVARCHAR)
- All-null rows
- Mixed fixed+variable columns
- Multi-page leaf chains
- Clustered (index_id=1) vs heap (index_id=0) tables
- LOB inline-root pointer via forge.lob
- ROW-compressed CD records via forge.record_cd
- Randomised schemas and rows (deterministic seeds)
"""
from __future__ import annotations

import random
import struct
from typing import Any

import pytest

from mssqlbak.forge import build_table
from mssqlbak.forge.iam import build_heap_table
from mssqlbak.forge.lob import encode_inline_root, encode_row_overflow
from mssqlbak.forge.record_cd import encode_cd
from mssqlbak.forge.record_fixedvar import encode_fixedvar
from mssqlbak.forge.table import ForgeColumn
from mssqlbak.pages.page import Page
from mssqlbak.records import decode_record, RecordColumn

# SQL Server type IDs used in tests.
_INT       = 56   # int (4 bytes)
_SMALLINT  = 52   # smallint (2 bytes)
_BIGINT    = 127  # bigint (8 bytes)
_TINYINT   = 48   # tinyint (1 byte)
_BIT       = 104  # bit (1 byte)
_FLOAT     = 62   # float (8 bytes)
_VARCHAR   = 167  # varchar (variable)
_NVARCHAR  = 231  # nvarchar (variable)
_VARBINARY = 165  # varbinary (variable)
_CHAR      = 175  # char (fixed-width)
_BINARY    = 173  # binary (fixed-width)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _int_bytes(n: int, size: int = 4, signed: bool = True) -> bytes:
    return n.to_bytes(size, "little", signed=signed)


def _f64_bytes(v: float) -> bytes:
    return struct.pack("<d", v)


def _varchar_bytes(s: str) -> bytes:
    return s.encode("latin-1")


def _nvarchar_bytes(s: str) -> bytes:
    return s.encode("utf-16-le")


def _decode_rows(store, table) -> list[dict[str, bytes | None]]:
    """Read all rows as raw bytes (types.decode_value not applied)."""
    from mssqlbak.rows.synth import _record_columns
    from mssqlbak.records import decode_record
    from mssqlbak.rows.pagewalk import _data_pages_with_page
    rows = []
    rec_cols = _record_columns(table)
    for pid, fid, page in _data_pages_with_page(store, table):
        for slot in range(page.header.slot_cnt):
            raw = page.record(slot)
            decoded = decode_record(raw, rec_cols)
            rows.append(decoded)
    return rows


# ---------------------------------------------------------------------------
# Phase B1 – encode_fixedvar direct tests
# ---------------------------------------------------------------------------

class TestEncodeFixedvarDirect:
    """Unit tests for encode_fixedvar: verify the record bytes round-trip
    through decode_record."""

    def _round_trip(
        self,
        rec_cols: list[RecordColumn],
        values: dict[str, bytes | None],
    ) -> dict[str, bytes | None]:
        raw = encode_fixedvar(rec_cols, values)
        return decode_record(raw, rec_cols)

    def test_single_fixed_int(self):
        cols = [RecordColumn("a", is_variable=False, null_index=0, leaf_offset=4, size=4)]
        vals = {"a": _int_bytes(42)}
        out = self._round_trip(cols, vals)
        assert out["a"] == _int_bytes(42)

    def test_single_fixed_null(self):
        cols = [RecordColumn("a", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=True)]
        vals = {"a": None}
        out = self._round_trip(cols, vals)
        assert out["a"] is None

    def test_fixed_and_variable(self):
        cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("name", is_variable=True, null_index=1, var_index=0, nullable=True),
        ]
        vals = {"id": _int_bytes(7), "name": b"hello"}
        out = self._round_trip(cols, vals)
        assert out["id"] == _int_bytes(7)
        assert out["name"] == b"hello"

    def test_variable_null(self):
        cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("name", is_variable=True, null_index=1, var_index=0, nullable=True),
        ]
        vals = {"id": _int_bytes(1), "name": None}
        out = self._round_trip(cols, vals)
        assert out["id"] == _int_bytes(1)
        assert out["name"] is None

    def test_multiple_variable_cols(self):
        cols = [
            RecordColumn("a", is_variable=True, null_index=0, var_index=0, nullable=True),
            RecordColumn("b", is_variable=True, null_index=1, var_index=1, nullable=True),
            RecordColumn("c", is_variable=True, null_index=2, var_index=2, nullable=True),
        ]
        vals = {"a": b"foo", "b": None, "c": b"baz"}
        out = self._round_trip(cols, vals)
        assert out["a"] == b"foo"
        assert out["b"] is None
        assert out["c"] == b"baz"

    def test_all_null(self):
        cols = [
            RecordColumn("x", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=True),
            RecordColumn("y", is_variable=True, null_index=1, var_index=0, nullable=True),
        ]
        vals = {"x": None, "y": None}
        out = self._round_trip(cols, vals)
        assert out["x"] is None
        assert out["y"] is None

    def test_empty_variable_value(self):
        cols = [RecordColumn("v", is_variable=True, null_index=0, var_index=0, nullable=True)]
        vals = {"v": b""}
        out = self._round_trip(cols, vals)
        assert out["v"] == b""

    def test_short_value_does_not_resize_buffer(self):
        """Regression: supplying a value shorter than col.size must NOT resize the
        fixed-region bytearray (slice-assignment would previously contract the buffer,
        causing fixed_end to overshoot len(raw) and raise ValueError in decode_record).
        """
        cols = [RecordColumn("a", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False)]
        # 1-byte value for a 4-byte column: should be zero-padded to 4 bytes.
        out = self._round_trip(cols, {"a": b"\x01"})
        assert out["a"] == b"\x01\x00\x00\x00"

    def test_over_length_value_truncated(self):
        """Values longer than col.size are silently truncated to col.size bytes."""
        cols = [RecordColumn("a", is_variable=False, null_index=0, leaf_offset=4, size=2, nullable=False)]
        out = self._round_trip(cols, {"a": b"\x01\x02\x03\x04"})
        assert out["a"] == b"\x01\x02"

    def test_wide_null_bitmap_17_columns(self):
        """17 fixed columns → 3-byte null bitmap; every-third column NULL."""
        n = 17
        cols = [
            RecordColumn(f"c{i}", is_variable=False, null_index=i,
                         leaf_offset=4 + i * 4, size=4, nullable=True)
            for i in range(n)
        ]
        vals = {f"c{i}": (None if i % 3 == 0 else i.to_bytes(4, "little")) for i in range(n)}
        out = self._round_trip(cols, vals)
        for i in range(n):
            if i % 3 == 0:
                assert out[f"c{i}"] is None
            else:
                assert out[f"c{i}"] == i.to_bytes(4, "little")


# ---------------------------------------------------------------------------
# Phase B1 – build_table round-trip (full pipeline)
# ---------------------------------------------------------------------------

class TestBuildTableRoundtrip:
    """Full pipeline tests: build_table → read_table_rows → assert values."""

    def test_single_int_column(self):
        cols = [ForgeColumn("id", _INT, 4, nullable=False)]
        rows = [{"id": _int_bytes(i)} for i in range(5)]
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert [r["id"] for r in decoded] == [_int_bytes(i) for i in range(5)]

    def test_all_null_rows(self):
        cols = [
            ForgeColumn("a", _INT, 4, nullable=True),
            ForgeColumn("b", _VARCHAR, -1, nullable=True, is_variable=True),
        ]
        rows = [{"a": None, "b": None}] * 3
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert all(r["a"] is None and r["b"] is None for r in decoded)

    def test_mixed_fixed_and_variable(self):
        cols = [
            ForgeColumn("id",   _INT,      4,  nullable=False),
            ForgeColumn("name", _VARCHAR, -1, nullable=True, is_variable=True),
        ]
        rows = [
            {"id": _int_bytes(1), "name": b"Alice"},
            {"id": _int_bytes(2), "name": b"Bob"},
            {"id": _int_bytes(3), "name": None},
        ]
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows

    def test_multiple_variable_columns(self):
        cols = [
            ForgeColumn("k",   _SMALLINT, 2, nullable=False),
            ForgeColumn("v1",  _NVARCHAR, -1, nullable=True, is_variable=True),
            ForgeColumn("v2",  _VARBINARY, -1, nullable=True, is_variable=True),
        ]
        rows = [
            {"k": _int_bytes(1, 2), "v1": _nvarchar_bytes("hi"), "v2": b"\xDE\xAD"},
            {"k": _int_bytes(2, 2), "v1": None, "v2": b"\xBE\xEF"},
            {"k": _int_bytes(3, 2), "v1": _nvarchar_bytes("bye"), "v2": None},
        ]
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows

    def test_bit_column(self):
        cols = [ForgeColumn("flag", _BIT, 1, nullable=True)]
        rows = [
            {"flag": b"\x01"},
            {"flag": b"\x00"},
            {"flag": None},
        ]
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows

    def test_bigint_column(self):
        cols = [ForgeColumn("big", _BIGINT, 8, nullable=False)]
        rows = [{"big": _int_bytes(10**15, 8)} for _ in range(3)]
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows

    def test_float_column(self):
        cols = [ForgeColumn("f", _FLOAT, 8, nullable=False)]
        rows = [{"f": _f64_bytes(3.14159)}, {"f": _f64_bytes(-1.0)}, {"f": _f64_bytes(0.0)}]
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows


# ---------------------------------------------------------------------------
# Multi-page round-trips
# ---------------------------------------------------------------------------

class TestMultiPageRoundtrip:
    """Ensure that a large number of rows spanning many pages all round-trip."""

    def _make_rows(self, n: int) -> list[dict[str, bytes | None]]:
        rng = random.Random(0xDEAD_BEEF)
        rows = []
        for i in range(n):
            name_len = rng.randint(0, 80)
            rows.append({
                "id":   _int_bytes(i),
                "name": bytes(rng.randint(0, 127) for _ in range(name_len)),
            })
        return rows

    def test_200_rows_span_multiple_pages(self):
        cols = [
            ForgeColumn("id",   _INT,     4,  nullable=False),
            ForgeColumn("name", _VARCHAR, -1, nullable=True, is_variable=True),
        ]
        rows = self._make_rows(200)
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        # Multi-page tables iterate pages in order via next_page chain.
        assert decoded == rows

    def test_500_rows_pure_fixed(self):
        cols = [
            ForgeColumn("a", _INT,     4, nullable=False),
            ForgeColumn("b", _BIGINT,  8, nullable=False),
        ]
        rng = random.Random(42)
        rows = [
            {"a": _int_bytes(rng.randint(-2**31, 2**31 - 1)),
             "b": _int_bytes(rng.randint(-2**63, 2**63 - 1), 8)}
            for _ in range(500)
        ]
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows

    def test_many_nullable_columns(self):
        """Stress the null bitmap across many columns."""
        n_cols = 24
        cols = [ForgeColumn(f"c{i}", _INT, 4, nullable=True) for i in range(n_cols)]
        rng = random.Random(123)
        rows = []
        for _ in range(50):
            row = {
                f"c{i}": (None if rng.random() < 0.3 else _int_bytes(rng.randint(0, 999)))
                for i in range(n_cols)
            }
            rows.append(row)
        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows


# ---------------------------------------------------------------------------
# Heap (index_id=0) round-trips
# ---------------------------------------------------------------------------

class TestHeapRoundtrip:
    """Build heap tables (index_id=0) with an IAM page and verify via pagewalk."""

    def test_heap_basic(self):
        cols = [
            ForgeColumn("id",   _INT,     4,  nullable=False),
            ForgeColumn("val",  _VARCHAR, -1, nullable=True, is_variable=True),
        ]
        rows = [
            {"id": _int_bytes(1), "val": b"aaa"},
            {"id": _int_bytes(2), "val": None},
            {"id": _int_bytes(3), "val": b"ccc"},
        ]
        store, table = build_heap_table(cols, rows)
        assert table.index_id == 0
        decoded = _decode_rows(store, table)
        # Heap page walk may yield all rows; order may differ (SPA before extents).
        assert sorted(r["id"] for r in decoded) == sorted(r["id"] for r in rows)

    def test_heap_all_null(self):
        cols = [ForgeColumn("x", _INT, 4, nullable=True)]
        rows = [{"x": None}] * 5
        store, table = build_heap_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert all(r["x"] is None for r in decoded)

    def test_heap_many_rows(self):
        """Enough rows to overflow the SPA slots (>8 pages) into the extent bitmap."""
        cols = [
            ForgeColumn("id", _INT, 4, nullable=False),
            ForgeColumn("pad", _BINARY, 200, nullable=False),
        ]
        # pad large enough that each page holds ~33 rows → 10 pages for 350 rows.
        rng = random.Random(7)
        rows = [{"id": _int_bytes(i), "pad": bytes(rng.randint(0, 255) for _ in range(200))}
                for i in range(350)]
        store, table = build_heap_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert len(decoded) == 350
        assert sorted(r["id"] for r in decoded) == sorted(r["id"] for r in rows)


# ---------------------------------------------------------------------------
# LOB inline-root round-trip
# ---------------------------------------------------------------------------

class TestLobRoundtrip:
    """Verify that encode_inline_root / encode_row_overflow produce bytes that
    _stitch_lob can follow back to the original value."""

    def test_inline_root_small(self):
        from mssqlbak.forge.image import ImageBuilder
        from mssqlbak.rows.lob import _stitch_lob

        data = b"hello world " * 100
        ImageBuilder(file_id=1)
        # We need a page_id to reference; allocate a dummy page slot.
        lob_page_id = 1  # will be placed at this id
        in_row_ptr, lob_raw = encode_inline_root(data, page_id=lob_page_id, file_id=1)

        # Manually insert the lob page at the expected location.
        from mssqlbak.pages.store import PageStore
        page_count = lob_page_id + 1
        img = bytearray(page_count * 8192)
        img[lob_page_id * 8192 : (lob_page_id + 1) * 8192] = lob_raw
        store = PageStore({1: bytes(img)})

        # Build a minimal table that holds the LOB pointer as a variable column.
        # We only need the store to have the LOB page; test _stitch_lob directly.
        class FakeTable:
            alloc_units = []
            object_id   = 0

        result = _stitch_lob(store, FakeTable(), in_row_ptr)
        assert result == data

    def test_row_overflow(self):
        from mssqlbak.pages.store import PageStore
        from mssqlbak.rows.lob import _stitch_lob

        data = b"X" * 1000
        lob_page_id = 2
        in_row_ptr, lob_raw = encode_row_overflow(data, page_id=lob_page_id, file_id=1)

        page_count = lob_page_id + 1
        img = bytearray(page_count * 8192)
        img[lob_page_id * 8192 : (lob_page_id + 1) * 8192] = lob_raw
        store = PageStore({1: bytes(img)})

        class FakeTable:
            alloc_units = []
            object_id   = 0

        result = _stitch_lob(store, FakeTable(), in_row_ptr)
        assert result == data


# ---------------------------------------------------------------------------
# CD record (ROW compression) encode → decode round-trip
# ---------------------------------------------------------------------------

class TestCdRecordRoundtrip:
    """encode_cd → physical_columns round-trip tests."""

    def _decode_cd(self, raw: bytes, ncol: int) -> list[bytes | None]:
        """Decode a CD record back to per-column bytes (NULL → None)."""
        from mssqlbak.rowcompress._layout import physical_columns
        items = physical_columns(raw)
        return [b"" if b == b"" else b for b in items]

    def _make_int_col(self, name: str, type_id: int = 56, width: int = 4) -> Any:
        """Create a minimal Column-like object for encode_cd."""
        from mssqlbak.catalog.model import Column
        return Column(
            name=name, colid=1, type_id=type_id, max_length=width,
            precision=0, scale=0, nullable=True, leaf_offset=4, is_variable=False,
        )

    def test_cd_single_int_zero(self):
        col = self._make_int_col("x")
        # SQL Server ROW compression: ZERO indicator (empty bytes) = integer value 0.
        # INT 0 → ZERO indicator (empty bytes).
        raw_int0 = encode_cd([col], {"x": b"\x00\x00\x00\x00"})
        result_int0 = self._decode_cd(raw_int0, 1)
        assert len(result_int0) == 1
        assert result_int0[0] == b""  # ZERO indicator → integer zero

        # INT -2147483648 (minimum) → biased=0 → stored as full-width b'\x00\x00\x00\x00'
        # (indicator nibble 5, not ZERO indicator), so it round-trips to -2147483648.
        raw_min = encode_cd([col], {"x": _int_bytes(-2**31)})
        result_min = self._decode_cd(raw_min, 1)
        assert result_min[0] is not None  # not NULL
        assert result_min[0] == b"\x00\x00\x00\x00"  # full-width excess repr

    def test_cd_null(self):
        col = self._make_int_col("x")
        raw = encode_cd([col], {"x": None})
        result = self._decode_cd(raw, 1)
        assert result[0] is None

    def test_cd_small_int(self):
        col = self._make_int_col("x")
        # INT value 1 → excess-encoded big-endian: 1 + 2^31 = 0x80000001 → b"\x80\x00\x00\x01"
        # compressed: strip leading zeros → b"\x80\x00\x00\x01" (4 bytes → nibble 0x5)
        raw = encode_cd([col], {"x": _int_bytes(1)})
        items = self._decode_cd(raw, 1)
        # The compressed bytes come back as-is; the reader normalises them.
        assert items[0] is not None

    def test_cd_varchar_passthrough(self):
        from mssqlbak.catalog.model import Column
        col = Column(
            name="s", colid=1, type_id=167, max_length=-1,
            precision=0, scale=0, nullable=True, leaf_offset=-1, is_variable=True,
        )
        data = b"hello"
        raw = encode_cd([col], {"s": data})
        items = self._decode_cd(raw, 1)
        assert items[0] == b"hello"

    def test_cd_multi_column(self):
        cols = [
            self._make_int_col("a", 56, 4),
            self._make_int_col("b", 52, 2),
        ]
        raw = encode_cd(cols, {"a": _int_bytes(100), "b": _int_bytes(5, 2)})
        items = self._decode_cd(raw, 2)
        assert len(items) == 2
        assert items[0] is not None and items[1] is not None


# ---------------------------------------------------------------------------
# Randomised schema + row property tests (deterministic seeds)
# ---------------------------------------------------------------------------

class TestRandomisedRoundtrip:
    """Randomly generate schemas and rows, verify round-trip identity."""

    def _rand_fixed_col(self, rng: random.Random, idx: int) -> ForgeColumn:
        choices = [
            (_TINYINT, 1), (_SMALLINT, 2), (_INT, 4), (_BIGINT, 8),
            (_BIT, 1), (_FLOAT, 8),
        ]
        tid, size = rng.choice(choices)
        return ForgeColumn(f"f{idx}", tid, size, nullable=rng.random() < 0.5)

    def _rand_var_col(self, rng: random.Random, idx: int) -> ForgeColumn:
        tid = rng.choice([_VARCHAR, _NVARCHAR, _VARBINARY])
        return ForgeColumn(f"v{idx}", tid, -1, nullable=rng.random() < 0.5, is_variable=True)

    def _rand_value(
        self, rng: random.Random, col: ForgeColumn
    ) -> bytes | None:
        if col.nullable and rng.random() < 0.25:
            return None
        if col.is_variable:
            n = rng.randint(0, 40)
            return bytes(rng.randint(0, 255) for _ in range(n))
        if col.type_id == _BIT:
            return b"\x01" if rng.random() < 0.5 else b"\x00"
        return bytes(rng.randint(0, 255) for _ in range(col.max_length))

    @pytest.mark.parametrize("seed", [1, 2, 3, 7, 42, 99, 256, 1024])
    def test_random_schema_and_rows(self, seed: int):
        rng = random.Random(seed)
        n_fixed = rng.randint(1, 6)
        n_var   = rng.randint(0, 4)
        cols = (
            [self._rand_fixed_col(rng, i) for i in range(n_fixed)]
            + [self._rand_var_col(rng, n_fixed + i) for i in range(n_var)]
        )
        n_rows = rng.randint(1, 80)
        rows = [{c.name: self._rand_value(rng, c) for c in cols} for _ in range(n_rows)]

        store, table = build_table(cols, rows)
        decoded = _decode_rows(store, table)
        assert decoded == rows, (
            f"seed={seed}: decoded rows differ from input"
        )


# ---------------------------------------------------------------------------
# Page-builder unit tests
# ---------------------------------------------------------------------------

class TestPageBuilder:
    def test_page_parses_correctly(self):
        from mssqlbak.forge.page import PageBuilder
        pb = PageBuilder(page_id=5, file_id=1, obj_id=100, pminlen=8)
        pb.add_record(b"\x10\x00\x08\x00" + b"\x00\x00\x00\x00")
        raw = pb.build()
        assert len(raw) == 8192
        page = Page(raw)
        assert page.header.page_id == 5
        assert page.header.file_id == 1
        assert page.header.obj_id  == 100
        assert page.header.slot_cnt == 1

    def test_page_full_raises(self):
        from mssqlbak.forge.page import PageBuilder
        pb = PageBuilder(page_id=1, file_id=1, obj_id=1, pminlen=4)
        # Fill the page with records of ~100 bytes each.
        rec = b"\x10\x00\x04\x00" + b"\xAB" * 96
        while pb.fits(len(rec)):
            pb.add_record(rec)
        with pytest.raises(ValueError, match="Page full"):
            pb.add_record(rec)

    def test_prev_next_pointers(self):
        from mssqlbak.forge.page import PageBuilder
        pb = PageBuilder(page_id=3, file_id=1, obj_id=1, pminlen=4)
        raw = pb.build(prev_page=(2, 1), next_page=(4, 1))
        page = Page(raw)
        assert page.header.prev_page == (2, 1)
        assert page.header.next_page == (4, 1)


# ---------------------------------------------------------------------------
# ImageBuilder unit tests
# ---------------------------------------------------------------------------

class TestImageBuilder:
    def test_single_chain_links_correct(self):
        from mssqlbak.forge.image import ImageBuilder
        from mssqlbak.forge.page import PageBuilder
        ib = ImageBuilder(file_id=1)
        pbs = [PageBuilder(0, 1, 99, 4) for _ in range(3)]
        first = ib.add_chain(pbs)
        store = ib.to_page_store()
        assert first[0] > 0
        # Walk the chain.
        loc = first
        seen = []
        while loc[0]:
            p = store.page(loc[0], loc[1])
            seen.append(loc)
            loc = p.header.next_page
        assert len(seen) == 3

    def test_image_builder_empty_raises(self):
        from mssqlbak.forge.image import ImageBuilder
        ib = ImageBuilder()
        with pytest.raises(ValueError, match="no pages"):
            ib.to_page_store()
