"""Decode every matrix value out of the fixture and compare to the reference."""
from __future__ import annotations

import struct

import pytest

from mssqlbak.catalog import ALLOC_IN_ROW, AllocUnit, Column, Table, _assign_bit_shifts, recover_schema
from mssqlbak.types import BIT, decode_value
from mssqlbak.pages import PAGE_SIZE, PageStore
from mssqlbak.records import decode_record
from mssqlbak.rows import _heap_data_pages, _record_columns, read_table_rows
from tools.typematrix import TYPE_CASES


@pytest.mark.fixture
@pytest.mark.parametrize("case", TYPE_CASES, ids=lambda c: c.name)
def test_decoded_values_match_matrix(fixture_bak, case) -> None:
    if case.fallback_xtype is not None:
        pytest.skip(f"t_{case.name} is version-gated (SS2025+); not in the typecoverage fixture")
    store = PageStore.from_bak(fixture_bak)
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == f"t_{case.name}")
    by_label = {row["label"]: row["v"] for row in read_table_rows(store, table)}
    if case.auto:
        # Engine-populated (rowversion): no known value to assert; the parser
        # must still decode every inserted row to a non-null value (the
        # engine-diff test checks correctness against the live engine).
        for r in case.rows:
            assert by_label[r.label] is not None, (case.name, r.label)
        return
    for r in case.rows:
        assert by_label[r.label] == r.value, (case.name, r.label)


def _locator_page(page_id: int, *, m_type: int, obj_id: int = 0) -> bytes:
    """Build a minimal 8 KB page with locator (offset 32), m_type, obj_id."""
    buf = bytearray(PAGE_SIZE)
    buf[0] = 1  # header version
    buf[1] = m_type
    struct.pack_into("<I", buf, 24, obj_id)  # m_objId at offset 24
    struct.pack_into("<IH", buf, 32, page_id, 1)  # (page_id, file_id) at offset 32
    return bytes(buf)


def _heap(first_iam: int, first_page: tuple[int, int] = (0, 0)) -> Table:
    return Table(
        name="t_heap",
        object_id=999,
        index_id=0,
        alloc_units=[
            AllocUnit(
                rowset_id=1,
                unit_type=ALLOC_IN_ROW,
                first_page=first_page,
                root_page=(0, 0),
                first_iam=(first_iam, 1),
            )
        ],
    )


def test_heap_data_pages_walk_iam_bitmap() -> None:
    """Heap pages come from the IAM extent bitmap, filtered by obj_id.

    Pages in an allocated extent that belong to a *different* allocation unit
    (stale/deallocated) or are blank must be excluded -- only file-1 data pages
    whose header obj_id matches the IAM's are real heap pages.
    """
    obj = 42
    # 24 pages: extent 0 (0..7), extent 1 (8..15), extent 2 (16..23).
    pages = [_locator_page(i, m_type=0) for i in range(24)]
    pages[8] = _locator_page(8, m_type=1, obj_id=obj)  # real heap data page
    pages[9] = _locator_page(9, m_type=1, obj_id=777)  # foreign page in extent
    pages[10] = _locator_page(10, m_type=1, obj_id=obj)  # real heap data page
    # IAM page at 16 (extent 2), obj 42, bitmap marks extent 1 (pages 8..15).
    iam = bytearray(_locator_page(16, m_type=10, obj_id=obj))
    iam[194] = 0x02  # bit 1 -> extent 1 allocated
    pages[16] = bytes(iam)
    store = PageStore.from_pages(b"".join(pages))

    got = list(_heap_data_pages(store, _heap(first_iam=16)))
    assert got == [(8, 1), (10, 1)]  # foreign (9) and blank (11..15) excluded


def _fixed_int_col(name: str, colid: int, leaf_offset: int, null_bit: int) -> Column:
    return Column(
        name=name,
        colid=colid,
        type_id=56,  # int
        max_length=4,
        precision=10,
        scale=0,
        nullable=True,
        leaf_offset=leaf_offset,
        is_variable=False,
        null_bit=null_bit,
    )


def test_null_bitmap_uses_physical_bitpos_not_colid() -> None:
    """The null bitmap is indexed by physical column position (sysrscols bitpos),
    not colid.  When the engine stores a lower-colid column physically later (as
    AdventureWorks BillOfMaterials does with its identity PK), a set null bit must
    follow the physical position -- otherwise a NULL in the physically-first
    column is wrongly attributed to the colid-first column.
    """
    # colid 1 ("a") is stored *second* (offset 8, bitpos 2); colid 2 ("b") is
    # stored *first* (offset 4, bitpos 1) -- the BillOfMaterials shape.
    table = Table(
        name="t",
        object_id=1,
        columns=[
            _fixed_int_col("a", colid=1, leaf_offset=8, null_bit=2),
            _fixed_int_col("b", colid=2, leaf_offset=4, null_bit=1),
        ],
    )
    # Record: status A = 0x10 (null bitmap present), fixed_end = 12, two int
    # columns, null bitmap = 0x01 -> physical bit 0 set -> "b" (bitpos 1) is NULL.
    raw = (
        bytes([0x10, 0x00])
        + struct.pack("<H", 12)
        + struct.pack("<I", 0xBBBBBBBB)  # offset 4: column "b"
        + struct.pack("<I", 0x0000002A)  # offset 8: column "a" == 42
        + struct.pack("<H", 2)
        + bytes([0x01])
    )
    cells = decode_record(raw, _record_columns(table))
    assert cells["b"] is None  # physically-first column carries bit 0
    assert cells["a"] == struct.pack("<I", 42)  # not mis-flagged as NULL


def _var_col(name: str, colid: int, leaf_offset: int, null_bit: int) -> Column:
    return Column(
        name=name,
        colid=colid,
        type_id=167,  # varchar
        max_length=-1,
        precision=0,
        scale=0,
        nullable=True,
        leaf_offset=leaf_offset,
        is_variable=True,
        null_bit=null_bit,
    )


def test_dropped_variable_column_does_not_shift_var_index() -> None:
    """A dropped column leaves a physical variable slot with no live syscolpars
    entry; the engine encodes each live variable column's slot in its negative
    leaf_offset (-(var_index+1)).  Mapping var_index from that offset -- not a
    running counter over live columns -- keeps later variable columns aligned.

    Models the WideWorldImporters ``*_Archive`` shape: a dropped variable column
    occupies slot 0 (offset -1), so the two live variable columns are at -2/-3
    and must read variable payloads 1 and 2, not 0 and 1.
    """
    table = Table(
        name="t",
        object_id=1,
        columns=[
            _fixed_int_col("n", colid=1, leaf_offset=4, null_bit=1),
            _var_col("x", colid=2, leaf_offset=-2, null_bit=3),
            _var_col("y", colid=3, leaf_offset=-3, null_bit=4),
        ],
    )
    # 4 physical columns (1 fixed + 3 variable incl. the dropped slot 0).
    # Variable section: slot 0 empty (dropped), slot 1 = "AB", slot 2 = "CD".
    raw = (
        bytes([0x30, 0x00])          # status A: null bitmap + variable columns
        + struct.pack("<H", 8)       # fixed_end
        + struct.pack("<I", 42)      # offset 4: column "n"
        + struct.pack("<H", 4)       # ncol = 4
        + bytes([0x00])              # null bitmap: none null
        + struct.pack("<H", 3)       # nvar = 3
        + struct.pack("<HHH", 19, 21, 23)  # var end offsets
        + b"ABCD"                    # slot1="AB", slot2="CD" (slot0 empty)
    )
    cells = decode_record(raw, _record_columns(table))
    assert cells["x"] == b"AB"  # not the empty dropped slot
    assert cells["y"] == b"CD"


def test_heap_with_pages_but_no_iam_is_skipped_loudly() -> None:
    """A heap that has a first page but no recorded IAM fails loudly.

    This is a genuine "cannot locate the pages" case (the safety net turns it
    into a per-table skip), distinct from an empty heap with no pages at all.
    """
    store = PageStore.from_pages(b"\x00" * (PAGE_SIZE * 2))
    with pytest.raises(NotImplementedError, match="IAM"):
        list(read_table_rows(store, _heap(first_iam=0, first_page=(1, 1))))


def test_packed_bit_columns_share_byte() -> None:
    """Multiple BIT columns at the same leaf_offset use distinct bit positions."""
    columns = _assign_bit_shifts([
        Column("f_bit", 2, BIT, 1, 0, 0, False, 8, False, bit_shift=0),
        Column("f_bit2", 5, BIT, 1, 0, 0, False, 8, False, bit_shift=0),
    ])
    assert columns[0].bit_shift == 0
    assert columns[1].bit_shift == 1
    shared = bytes([0x82])  # bit0=0, bit1=1
    assert decode_value(columns[0], shared) is False
    assert decode_value(columns[1], shared) is True


def test_empty_heap_yields_no_rows() -> None:
    """A heap with no allocated pages (no IAM, no first/root page) has zero rows.

    Common for ETL staging tables; it must not be mistaken for a failure.
    """
    store = PageStore.from_pages(b"\x00" * (PAGE_SIZE * 2))
    assert list(read_table_rows(store, _heap(first_iam=0))) == []
