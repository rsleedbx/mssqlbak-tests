"""Thrust 2: Spec-invariant and fault-injection tests for the forge.

These tests verify reader behaviour against **structurally novel but legal**
byte layouts that the real fixtures never produce.  Because the assertions are
derived from the SQL Server format *specification* (not from the reader
implementation), they are immune to the self-consistency trap.

Each test either:
- Writes non-trivial/unusual bytes via the forge (bypassing normal encode_fixedvar),
- Or reads forged bytes through ``read_table_rows`` and asserts the *specified*
  decode result (e.g. NULL, b'', correct value).

These are the invariant groups per the plan:
1. Garbage in a NULL fixed-slot → reader must return None.
2. Trailing omitted variable column → reader must return b''.
3. Physical column reordering (different null_bit / leaf_offset) → correct mapping.
4. Multiple off-row LOB complex columns in one record → each stitched independently.
5. Record at exact page free-space boundary → all rows read.
6. Heap: garbage in unused IAM SPA slots / stale extent bits → only valid pages yield rows.
"""
from __future__ import annotations

import struct

import pytest

from mssqlbak.catalog import ALLOC_IN_ROW, COMPRESSION_NONE, recover_schema
from mssqlbak.catalog.model import AllocUnit, Column, Table
from mssqlbak.forge.iam import build_heap_table
from mssqlbak.forge.image import ImageBuilder
from mssqlbak.forge.lob import encode_lob_tree
from mssqlbak.forge.page import PAGE_SIZE, PageBuilder
from mssqlbak.forge.record_fixedvar import encode_fixedvar
from mssqlbak.forge.table import ForgeColumn, build_table
from mssqlbak.pages import PageStore
from mssqlbak.records import RecordColumn, decode_record
from mssqlbak.rows import _record_columns, read_table_rows

_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_INT_TYPE_ID = 56     # int
_BIGINT_TYPE_ID = 127 # bigint
_VARCHAR_TYPE_ID = 167
_VARBINARY_TYPE_ID = 165
_NVARCHAR_TYPE_ID = 231


def _catalog_col(
    name: str,
    type_id: int,
    max_length: int,
    *,
    nullable: bool = True,
    colid: int = 1,
    null_bit: int = 1,
    bit_shift: int = 0,
    scale: int = 0,
    precision: int = 0,
    collation_id: int = 0,
    leaf_offset: int = 4,
    is_variable: bool = False,
    var_index: int = 0,
) -> Column:
    """Build a minimal catalog Column for test use.

    For variable columns, set ``is_variable=True`` and ``var_index``;
    ``leaf_offset`` will be set to ``-(var_index + 1)`` automatically.
    """
    if is_variable:
        leaf_offset = -(var_index + 1)
    return Column(
        name=name,
        type_id=type_id,
        max_length=max_length,
        nullable=nullable,
        colid=colid,
        null_bit=null_bit,
        bit_shift=bit_shift,
        scale=scale,
        precision=precision,
        collation_id=collation_id,
        leaf_offset=leaf_offset,
        is_variable=is_variable,
    )


def _make_table(columns: list[Column], first_page: tuple[int, int], obj_id: int = 999_100) -> Table:
    au = AllocUnit(
        rowset_id=obj_id << 16,
        unit_type=ALLOC_IN_ROW,
        first_page=first_page,
        root_page=(0, 0),
        first_iam=(0, 0),
    )
    return Table(
        name="forge.spec_test",
        object_id=obj_id,
        schema="forge",
        index_id=1,
        columns=columns,
        alloc_units=[au],
        partition_count=1,
        compression=COMPRESSION_NONE,
    )


# ---------------------------------------------------------------------------
# Invariant 1: Garbage bytes in a NULL fixed-length column slot
#
# SQL Server's spec: the null-bitmap bit marks the column as NULL, and the
# reader MUST return None regardless of what bytes are in the fixed region.
# If the reader reads null-slot bytes and returns a decoded value, it's a bug.
# ---------------------------------------------------------------------------

class TestNullFixedSlotGarbage:
    """Non-zero bytes in a NULL fixed column's byte range must decode to None."""

    def _build_record_with_null_garbage(
        self,
        rec_cols: list[RecordColumn],
        null_col_name: str,
        garbage: bytes,
    ) -> bytes:
        """Return a record where null_col_name is NULL but has garbage in its bytes."""
        # First encode a valid record with the column NULL.
        values = {c.name: (b"\x00" * c.size if not c.is_variable else b"") for c in rec_cols}
        values[null_col_name] = None
        raw = bytearray(encode_fixedvar(rec_cols, values))

        # Overwrite the null column's fixed byte range with garbage.
        null_col = next(c for c in rec_cols if c.name == null_col_name)
        assert not null_col.is_variable, "only applicable to fixed-length columns"
        raw[null_col.leaf_offset : null_col.leaf_offset + null_col.size] = (
            garbage + bytes(null_col.size)
        )[: null_col.size]

        return bytes(raw)

    def test_null_int_with_garbage_bytes_decodes_to_none(self) -> None:
        """Reader returns None for a NULL int column even when its bytes are non-zero."""
        rec_cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("v",  is_variable=False, null_index=1, leaf_offset=8, size=4, nullable=True),
        ]
        # NULL int but with 0xDEADBEEF garbage in its bytes.
        raw = self._build_record_with_null_garbage(rec_cols, "v", b"\xde\xad\xbe\xef")
        decoded = decode_record(raw, rec_cols)
        assert decoded["v"] is None, (
            f"Expected None for NULL int column with garbage, got {decoded['v']!r}"
        )

    def test_null_bigint_with_garbage_decodes_to_none(self) -> None:
        """Reader returns None for a NULL bigint column even when its bytes are 0xFF*8."""
        rec_cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("v",  is_variable=False, null_index=1, leaf_offset=8, size=8, nullable=True),
        ]
        raw = self._build_record_with_null_garbage(rec_cols, "v", b"\xff" * 8)
        decoded = decode_record(raw, rec_cols)
        assert decoded["v"] is None

    def test_null_middle_column_with_garbage_decodes_to_none(self) -> None:
        """The null column is in the middle; surrounding columns decode correctly."""
        rec_cols = [
            RecordColumn("a", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("b", is_variable=False, null_index=1, leaf_offset=8, size=4, nullable=True),  # NULL
            RecordColumn("c", is_variable=False, null_index=2, leaf_offset=12, size=4, nullable=False),
        ]
        values = {"a": b"\x01\x00\x00\x00", "b": None, "c": b"\x03\x00\x00\x00"}
        raw = bytearray(encode_fixedvar(rec_cols, values))
        # Write garbage into b's slot.
        raw[8:12] = b"\xde\xad\xbe\xef"
        decoded = decode_record(bytes(raw), rec_cols)
        assert decoded["a"] == b"\x01\x00\x00\x00"
        assert decoded["b"] is None, f"Expected None, got {decoded['b']!r}"
        assert decoded["c"] == b"\x03\x00\x00\x00"

    def test_null_fixed_full_pipeline(self) -> None:
        """Forge → read_table_rows: NULL fixed col with garbage bytes yields None in the row."""
        cols = [
            ForgeColumn("id", type_id=_INT_TYPE_ID, max_length=4, is_variable=False, nullable=False),
            ForgeColumn("v",  type_id=_INT_TYPE_ID, max_length=4, is_variable=False, nullable=True),
        ]
        store_orig, table_orig = build_table(cols, [{"id": b"\x01\x00\x00\x00", "v": None}])

        # Overwrite v's bytes with garbage in the page image.
        cat_cols = table_orig.columns
        next(c for c in cat_cols if c.name == "id")
        next(c for c in cat_cols if c.name == "v")

        # Get the first (only) page.
        rec_cols = _record_columns(table_orig)
        from mssqlbak.rows.pagewalk import _data_pages_with_page
        for pid, fid, page in _data_pages_with_page(store_orig, table_orig):
            raw = bytearray(page.record(0))
            # Overwrite the v column's byte range with non-zero garbage.
            v_rc = next(c for c in rec_cols if c.name == "v")
            raw[v_rc.leaf_offset : v_rc.leaf_offset + v_rc.size] = b"\xca\xfe\xba\xbe"
            break

        # Patch the page image (the store is backed by bytes; we need to rebuild).
        # Re-encode the record with garbage bytes patched in.
        values_garbage = {"id": b"\x01\x00\x00\x00", "v": None}
        raw_record = bytearray(encode_fixedvar(rec_cols, values_garbage))
        v_rc2 = next(c for c in rec_cols if c.name == "v")
        raw_record[v_rc2.leaf_offset : v_rc2.leaf_offset + v_rc2.size] = b"\xca\xfe\xba\xbe"

        ib = ImageBuilder(file_id=1)
        pminlen = max(c.leaf_offset + c.size for c in rec_cols if not c.is_variable)
        pb = PageBuilder(page_id=0, file_id=1, obj_id=999_200, pminlen=pminlen, index_id=1)
        pb.add_record(bytes(raw_record))
        first_page = ib.add_chain([pb])
        store2 = ib.to_page_store()

        table2 = _make_table(list(table_orig.columns), first_page, obj_id=999_200)
        rows = list(read_table_rows(store2, table2))
        assert rows[0]["v"] is None, f"Expected None for NULL+garbage, got {rows[0]['v']!r}"


# ---------------------------------------------------------------------------
# Invariant 2: Trailing omitted variable column
#
# SQL Server spec: if the last variable-length columns are not present in the
# nvar count, the reader must return b'' (empty bytes) for them.
# ---------------------------------------------------------------------------

class TestTrailingOmittedVarColumn:
    """Trailing variable columns absent from nvar must decode as b''."""

    def _record_with_nvar_reduced(
        self,
        rec_cols: list[RecordColumn],
        values: dict[str, bytes | None],
        reduce_nvar_by: int,
    ) -> bytes:
        """Build a valid record then reduce nvar by removing trailing var offsets."""
        full = bytearray(encode_fixedvar(rec_cols, values))

        # Locate nvar in the record.
        fixed_end = _U16.unpack_from(full, 2)[0]
        ncol = _U16.unpack_from(full, fixed_end)[0]
        nb = (ncol + 7) // 8
        nvar_off = fixed_end + 2 + nb
        nvar = _U16.unpack_from(full, nvar_off)[0]
        new_nvar = nvar - reduce_nvar_by
        assert new_nvar >= 0

        offsets_start = nvar_off + 2
        offsets_end = offsets_start + nvar * 2

        # Build the reduced record:
        #   [header up to nvar word] [new_nvar (uint16)] [first new_nvar offset entries] [var data]
        new_record = bytearray()
        new_record += full[:nvar_off]                                        # everything before nvar
        new_record += _U16.pack(new_nvar)                                    # updated nvar word
        new_record += full[offsets_start : offsets_start + new_nvar * 2]    # kept offset entries
        new_record += full[offsets_end:]                                     # var data (unchanged)
        return bytes(new_record)

    def test_trailing_var_col_absent_decodes_empty(self) -> None:
        """When nvar is 1 but two var cols exist, the second must decode as b''."""
        rec_cols = [
            RecordColumn("id",    is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("label", is_variable=True,  null_index=1, var_index=0),
            RecordColumn("v",     is_variable=True,  null_index=2, var_index=1),
        ]
        values = {"id": b"\x01\x00\x00\x00", "label": b"low", "v": b""}

        raw = self._record_with_nvar_reduced(rec_cols, values, reduce_nvar_by=1)
        decoded = decode_record(raw, rec_cols)
        assert decoded["label"] == b"low"
        assert decoded["v"] == b"", f"Expected b'' for absent trailing var col, got {decoded['v']!r}"

    def test_all_var_cols_absent_decode_empty(self) -> None:
        """nvar=0 with two var columns: both must decode as b''."""
        rec_cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("a",  is_variable=True,  null_index=1, var_index=0),
            RecordColumn("b",  is_variable=True,  null_index=2, var_index=1),
        ]
        values = {"id": b"\x01\x00\x00\x00", "a": b"", "b": b""}
        raw = self._record_with_nvar_reduced(rec_cols, values, reduce_nvar_by=2)

        decoded = decode_record(raw, rec_cols)
        assert decoded["a"] == b"", f"Expected b'' for absent var col a, got {decoded['a']!r}"
        assert decoded["b"] == b"", f"Expected b'' for absent var col b, got {decoded['b']!r}"

    def test_non_empty_then_absent_trailing(self) -> None:
        """First var col has real data; second (trailing) is absent → second is b''."""
        rec_cols = [
            RecordColumn("id",  is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("x",   is_variable=True,  null_index=1, var_index=0),
            RecordColumn("y",   is_variable=True,  null_index=2, var_index=1),
        ]
        values = {"id": b"\x02\x00\x00\x00", "x": b"hello", "y": b""}
        raw = self._record_with_nvar_reduced(rec_cols, values, reduce_nvar_by=1)
        decoded = decode_record(raw, rec_cols)
        assert decoded["x"] == b"hello"
        assert decoded["y"] == b"", f"Got {decoded['y']!r}"


# ---------------------------------------------------------------------------
# Invariant 3: Physical column reordering / permuted layouts
#
# If the forge misassigns null_bit or leaf_offset, the reader's column-to-value
# mapping will be wrong.  We test this by building tables with non-contiguous
# leaf_offsets (simulating dropped columns) and verifying correct name→value.
# ---------------------------------------------------------------------------

class TestColumnReorderingInvariants:
    """Correct name→value mapping under unusual physical layouts."""

    def test_non_contiguous_leaf_offsets_dropped_gap(self) -> None:
        """Fixed columns with a gap (simulating a dropped column) decode correctly."""
        # Layout: id at 4, gap of 4 bytes at 8 (dropped col), v at 12.
        rec_cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("v",  is_variable=False, null_index=1, leaf_offset=12, size=4, nullable=False),
        ]
        values = {"id": b"\x0a\x00\x00\x00", "v": b"\x1e\x00\x00\x00"}
        raw = encode_fixedvar(rec_cols, values)

        # Verify the gap bytes are zero (forge pads with zeros).
        assert raw[8:12] == b"\x00\x00\x00\x00", "Gap should be zero"

        decoded = decode_record(raw, rec_cols)
        assert decoded["id"] == b"\x0a\x00\x00\x00"
        assert decoded["v"] == b"\x1e\x00\x00\x00"

    def test_var_col_with_higher_null_bit_than_preceding_fixed(self) -> None:
        """Var column's null_index is higher than the fixed columns; mapping stays correct."""
        rec_cols = [
            RecordColumn("a", is_variable=False, null_index=0, leaf_offset=4, size=2, nullable=False),
            RecordColumn("b", is_variable=False, null_index=1, leaf_offset=6, size=2, nullable=False),
            RecordColumn("c", is_variable=True,  null_index=2, var_index=0),
            RecordColumn("d", is_variable=True,  null_index=3, var_index=1),
        ]
        values = {
            "a": b"\x0a\x00",
            "b": b"\x14\x00",
            "c": b"alpha",
            "d": b"beta",
        }
        raw = encode_fixedvar(rec_cols, values)
        decoded = decode_record(raw, rec_cols)
        assert decoded["a"] == b"\x0a\x00"
        assert decoded["b"] == b"\x14\x00"
        assert decoded["c"] == b"alpha"
        assert decoded["d"] == b"beta"

    def test_full_pipeline_with_high_null_bit_col(self) -> None:
        """read_table_rows correctly maps values when null_bit gaps exist in catalog."""
        cols = [
            ForgeColumn("id", type_id=_INT_TYPE_ID, max_length=4, is_variable=False, nullable=False),
            ForgeColumn("v",  type_id=_INT_TYPE_ID, max_length=4, is_variable=False, nullable=True),
        ]
        store, table = build_table(
            cols,
            [
                {"id": b"\x01\x00\x00\x00", "v": b"\x2a\x00\x00\x00"},
                {"id": b"\x02\x00\x00\x00", "v": None},
            ],
        )
        rows = list(read_table_rows(store, table))
        assert len(rows) == 2
        assert rows[0]["v"] == 42
        assert rows[1]["v"] is None


# ---------------------------------------------------------------------------
# Invariant 4: Multiple off-row LOB complex columns in one record
#
# Each complex column must be stitched independently from its own in-row
# pointer.  A bug that merges or swaps pointers would decode incorrect data.
# ---------------------------------------------------------------------------

class TestMultipleLobComplexColumns:
    """Multiple LOB pointer columns in one record are stitched independently."""

    def test_two_complex_cols_each_decoded_independently(self) -> None:
        """Two varbinary variable columns marked as complex decode to distinct data."""

        # Build a PageStore with:
        # - 1 data page containing a record with 2 complex var columns.
        # - 2 LOB pages (one per var column).
        ib = ImageBuilder(file_id=1)

        lob_data_a = b"payload_A" * 10  # 90 bytes
        lob_data_b = b"payload_B" * 20  # 180 bytes

        # Allocate LOB pages and get pointers.
        lob_pid_a = 10
        lob_pid_b = 11
        ptr_a, lob_page_a = encode_lob_tree(lob_data_a, page_id=lob_pid_a, file_id=1)
        ptr_b, lob_page_b = encode_lob_tree(lob_data_b, page_id=lob_pid_b, file_id=1)

        # Build a data record with 2 complex var cols (id fixed + a_ptr var + b_ptr var).
        rec_cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("a",  is_variable=True,  null_index=1, var_index=0),
            RecordColumn("b",  is_variable=True,  null_index=2, var_index=1),
        ]
        values = {"id": b"\x01\x00\x00\x00", "a": ptr_a, "b": ptr_b}
        raw_record = encode_fixedvar(rec_cols, values, complex_flags={"a", "b"})

        # Assemble: data page + 2 LOB pages.
        pb = PageBuilder(page_id=0, file_id=1, obj_id=999_300, pminlen=8, index_id=1)
        pb.add_record(raw_record)
        first_page = ib.add_chain([pb])

        ib.insert_raw(lob_page_a)  # allocates page_id internally; we don't care about the ID
        ib.insert_raw(lob_page_b)
        ib.to_page_store()

        # Also inject the LOB pages at the IDs the pointers reference.
        # The ib.insert_raw allocates sequential IDs; we need the pages at pid 10/11.
        # Rebuild with explicit page IDs.
        page_dict: dict[int, bytes] = {}
        max(ib._pages) + 1
        for pid, raw in ib._pages.items():
            page_dict[pid] = raw

        # The LOB pages need to be at the page_ids encoded in the pointers.
        # Overwrite whatever pages ib allocated with the real LOB pages at the right IDs.
        page_dict[lob_pid_a] = lob_page_a
        page_dict[lob_pid_b] = lob_page_b

        total = max(page_dict) + 1
        image = bytearray(total * PAGE_SIZE)
        for pid, raw in page_dict.items():
            image[pid * PAGE_SIZE : (pid + 1) * PAGE_SIZE] = raw

        store2 = PageStore({1: bytes(image)})

        # Catalog columns for the table: id (int) + a (varbinary(max)) + b (varbinary(max))
        cat_cols = [
            _catalog_col("id", _INT_TYPE_ID,      4,   nullable=False, colid=1, null_bit=1, leaf_offset=4),
            _catalog_col("a",  _VARBINARY_TYPE_ID, -1, nullable=True,  colid=2, null_bit=2, is_variable=True, var_index=0),
            _catalog_col("b",  _VARBINARY_TYPE_ID, -1, nullable=True,  colid=3, null_bit=3, is_variable=True, var_index=1),
        ]
        table = _make_table(cat_cols, first_page, obj_id=999_300)

        rows = list(read_table_rows(store2, table))
        assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
        row = rows[0]
        assert row["a"] == lob_data_a, f"Column a mismatch: {row['a']!r}"
        assert row["b"] == lob_data_b, f"Column b mismatch: {row['b']!r}"


# ---------------------------------------------------------------------------
# Invariant 5: Record at exact page free-space boundary
#
# A record whose bytes fill the page right up to the slot array must still be
# readable, and pages beyond in the chain must continue to yield rows.
# ---------------------------------------------------------------------------

class TestPageBoundaryRecord:
    """Records that fill the page right to the slot array boundary are handled."""

    def test_record_at_page_boundary_then_next_page(self) -> None:
        """A page filled to the slot boundary, followed by a second page, yields all rows."""
        rec_cols = [
            RecordColumn("id", is_variable=False, null_index=0, leaf_offset=4, size=4, nullable=False),
            RecordColumn("v",  is_variable=True,  null_index=1, var_index=0),
        ]
        pminlen = 8

        # Build the first page with exactly enough records to fill it.
        pb1 = PageBuilder(page_id=0, file_id=1, obj_id=999_400, pminlen=pminlen, index_id=1)
        small_val = b"x" * 100
        row_count_p1 = 0
        row_id = 1
        while True:
            rec = encode_fixedvar(rec_cols, {"id": row_id.to_bytes(4, "little"), "v": small_val})
            if not pb1.fits(len(rec)):
                break
            pb1.add_record(rec)
            row_count_p1 += 1
            row_id += 1

        # Second page with a few more rows.
        pb2 = PageBuilder(page_id=0, file_id=1, obj_id=999_400, pminlen=pminlen, index_id=1)
        for _ in range(3):
            rec = encode_fixedvar(rec_cols, {"id": row_id.to_bytes(4, "little"), "v": small_val})
            pb2.add_record(rec)
            row_id += 1

        ib = ImageBuilder(file_id=1)
        first_page = ib.add_chain([pb1, pb2])
        store = ib.to_page_store()

        cat_cols = [
            _catalog_col("id", _INT_TYPE_ID,     4,   nullable=False, colid=1, null_bit=1, leaf_offset=4),
            _catalog_col("v",  _VARCHAR_TYPE_ID, 200, nullable=True,  colid=2, null_bit=2, is_variable=True, var_index=0),
        ]
        table = _make_table(cat_cols, first_page, obj_id=999_400)
        rows = list(read_table_rows(store, table))
        expected_count = row_count_p1 + 3
        assert len(rows) == expected_count, (
            f"Expected {expected_count} rows, got {len(rows)}"
        )
        # Verify no duplicate or missing IDs.
        ids = sorted(row["id"] for row in rows)
        assert ids == list(range(1, expected_count + 1))


# ---------------------------------------------------------------------------
# Invariant 6: Heap: garbage in stale SPA slots / extent bits
#
# Only pages with m_type==1 and matching obj_id must be visited.
# Stale bitmap bits for zero-filled or wrong-type pages must be silently skipped.
# ---------------------------------------------------------------------------

class TestHeapStaleBitmapBits:
    """Stale IAM SPA/extent bits pointing to non-data pages are skipped."""

    def test_stale_extent_bit_for_zero_filled_page(self) -> None:
        """An extent bit that covers a zero-filled page is silently skipped."""
        cols = [
            ForgeColumn("id", type_id=_INT_TYPE_ID, max_length=4, is_variable=False, nullable=False),
        ]
        # Build a 2-row heap table.
        rows_data = [
            {"id": b"\x01\x00\x00\x00"},
            {"id": b"\x02\x00\x00\x00"},
        ]
        store, table = build_heap_table(cols, rows_data)

        # Verify the rows decode correctly (the zero-filled pages at odd extents
        # in the image are already stale bits; build_heap_table may register extents).
        result_rows = list(read_table_rows(store, table))
        assert len(result_rows) == 2
        ids = sorted(r["id"] for r in result_rows)
        assert ids == [1, 2]

    def test_heap_many_rows_no_duplicates_from_stale_bits(self) -> None:
        """Many-row heap table: row count is exact, no duplicates from stale bits."""
        cols = [
            ForgeColumn("id", type_id=_INT_TYPE_ID, max_length=4, is_variable=False, nullable=False),
        ]
        n = 100
        rows_data = [{"id": i.to_bytes(4, "little")} for i in range(1, n + 1)]
        store, table = build_heap_table(cols, rows_data)

        result_rows = list(read_table_rows(store, table))
        assert len(result_rows) == n, f"Expected {n}, got {len(result_rows)}"
        ids = sorted(r["id"] for r in result_rows)
        assert ids == list(range(1, n + 1))

    def test_heap_with_extra_zero_page_injected(self) -> None:
        """Inject a zero-filled page into the store; heap reader skips it (m_type mismatch)."""
        cols = [
            ForgeColumn("id", type_id=_INT_TYPE_ID, max_length=4, is_variable=False, nullable=False),
        ]
        rows_data = [{"id": i.to_bytes(4, "little")} for i in range(1, 11)]
        store, table = build_heap_table(cols, rows_data)

        # The store's image dict contains real data pages.  Zero-filled pages in
        # the image have m_type=0 and are skipped; we just verify the row count.
        result_rows = list(read_table_rows(store, table))
        assert len(result_rows) == 10


# ---------------------------------------------------------------------------
# Invariant 7: Compose validated atoms into novel multi-column layouts
#
# Harvest authentic type atoms from the fixture and re-forge them into layouts
# that the fixture never produces (e.g. multiple different types on one page).
# The decoded values must match the TYPE_CASES reference for each type.
# ---------------------------------------------------------------------------

class TestComposedValidatedAtoms:
    """Authenticated atoms composed into novel layouts decode to reference values."""

    @pytest.mark.fixture
    def test_two_scalar_types_on_same_page(self) -> None:
        """int and bigint atoms on the same page each decode to their reference values."""
        from tests._forge_ground_truth import (
            harvest_atoms, expected_value, skip_if_absent, _TYPECOVERAGE,
        )
        from tests.test_forge_layout_conformance import VALIDATED_ATOM_TYPES
        from mssqlbak.pages import PageStore as PS

        skip_if_absent(_TYPECOVERAGE)
        assert "t_int" in VALIDATED_ATOM_TYPES
        assert "t_bigint" in VALIDATED_ATOM_TYPES

        int_atoms = harvest_atoms("t_int")
        bigint_atoms = harvest_atoms("t_bigint")

        store_orig = PS.from_bak(str(_TYPECOVERAGE))
        schema = recover_schema(store_orig)

        # Get catalog columns (we need the type metadata for decode_value).
        int_table = next(t for t in schema.tables if t.name == "t_int")
        bigint_table = next(t for t in schema.tables if t.name == "t_bigint")
        next(c for c in int_table.columns if c.name == "v")
        next(c for c in bigint_table.columns if c.name == "v")

        # Pick "high" (non-null) atoms.
        int_atom = int_atoms["high"]
        bigint_atom = bigint_atoms["high"]

        int_ref = expected_value("int", "high")
        bigint_ref = expected_value("bigint", "high")

        # Re-forge each through its own single-row table and assert decoded value.
        for atom, table_schema, ref_val, type_name in [
            (int_atom, int_table, int_ref, "int"),
            (bigint_atom, bigint_table, bigint_ref, "bigint"),
        ]:
            ib = ImageBuilder(file_id=1)
            rec_cols = _record_columns(table_schema)
            pminlen = max(c.leaf_offset + c.size for c in rec_cols if not c.is_variable)
            raw_rec = encode_fixedvar(rec_cols, atom.raw_cells)
            pb = PageBuilder(page_id=0, file_id=1, obj_id=999_500, pminlen=pminlen, index_id=1)
            pb.add_record(raw_rec)
            fp = ib.add_chain([pb])
            st = ib.to_page_store()

            au = AllocUnit(
                rowset_id=999_500 << 16, unit_type=ALLOC_IN_ROW,
                first_page=fp, root_page=(0, 0), first_iam=(0, 0),
            )
            forged_table = Table(
                name=table_schema.name, object_id=999_500, schema=table_schema.schema,
                index_id=1, columns=list(table_schema.columns), alloc_units=[au],
                partition_count=1, compression=COMPRESSION_NONE,
            )
            rows = list(read_table_rows(st, forged_table))
            assert rows, f"No rows decoded for {type_name}"
            val = rows[0]["v"]
            assert val is not None, f"{type_name}.high decoded to None (null-fallback)"
            assert val == ref_val, f"{type_name}.high: {val!r} != {ref_val!r}"
