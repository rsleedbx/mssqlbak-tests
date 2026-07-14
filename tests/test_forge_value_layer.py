"""Thrust 1: Drive forged bytes through the full value-decode layer.

Tests in this file assert that:
  1. Authentic on-disk bytes (harvested from a real SQL Server fixture) re-forged
     into a fresh PageStore/Table, then read via ``read_table_rows`` (which calls
     ``decode_value``), produce the **same Python values** as the hand-authored
     ``TYPE_CASES`` reference matrix.

This escapes the self-consistency trap: the bytes come from SQL Server (not the
forge writer) and the expected values come from TYPE_CASES (not the forge reader).
Any disagreement is a genuine pre-existing reader bug, not a forge self-error.

Null-fallback guard
-------------------
``read_table_rows`` catches decode exceptions and silently returns ``None``
(``mssqlbak/rows/reader.py:320``).  Each test asserts that when the reference
value is non-null, the decoded cell is also non-null.  This exposes a crashing
decoder instead of letting it collapse to NULL undetected.

All tests are marked ``@pytest.mark.fixture`` and skip when the fixture is absent.
"""
from __future__ import annotations

from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.catalog.model import AllocUnit, Column, Table
from mssqlbak.forge.record_fixedvar import encode_fixedvar
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tests._forge_ground_truth import (
    RawAtom,
    harvest_atoms,
    skip_if_absent,
    _TYPECOVERAGE,
    all_type_cases,
)

# ---------------------------------------------------------------------------
# Core helper: forge a single-row table from a catalog Column + raw bytes
# ---------------------------------------------------------------------------

def _forge_single_row(atom: RawAtom) -> dict[str, Any]:
    """Re-forge one row and return the fully decoded dict from read_table_rows.

    The atom provides authentic SQL-Server bytes for every column, plus the
    catalog Column object (carrying type_id, scale, collation_id, etc.) needed
    by decode_value.  The forged PageStore/Table go through the full reader
    pipeline including decode_value so the value layer is exercised.
    """
    rec_cols = atom.rec_cols

    # Build ForgeColumn descriptors that mirror the fixture's physical layout.
    # We need them to match the catalog Column objects exactly (same type_id,
    # max_length, scale, precision, collation_id, nullable, leaf_offset, var_index).
    # The easiest approach: build a Table directly from the fixture's catalog
    # columns and AllocUnit, bypassing build_table's column-layout logic.

    # Pack one FixedVar record using the authentic bytes from the fixture.
    raw_record = encode_fixedvar(rec_cols, atom.raw_cells)

    # Assemble: one page, one record.
    from mssqlbak.forge.page import PageBuilder
    from mssqlbak.forge.image import ImageBuilder
    from mssqlbak.catalog import ALLOC_IN_ROW, COMPRESSION_NONE

    # pminlen: fixed-region end = max(leaf_offset + size) for fixed cols, else 4.
    fixed_cols = [c for c in rec_cols if not c.is_variable]
    pminlen = max((c.leaf_offset + c.size for c in fixed_cols), default=4)

    # We need the catalog Table to carry the original Column objects (with correct
    # type_id, scale, precision, collation_id, bit_shift, etc.) so that
    # decode_value works correctly.  Reconstruct a minimal Table object.

    _OBJ_ID = 998_001
    ib = ImageBuilder(file_id=1)

    # Retrieve the full catalog table so we have all Column objects.
    # (We already have rec_cols from harvest; the original Table with its
    # Column objects was recovered during harvesting.)
    # The atom stores rec_cols only; we need the catalog Table for decode_value.
    # Re-build from the fixture's recovered schema.
    store_orig = PageStore.from_bak(str(_TYPECOVERAGE))
    schema_orig = recover_schema(store_orig)
    # Find the table that owns the atom's rec_col set by matching the v-column
    # catalog Column object (which carries the type_id/scale we need).
    table_name = _find_table_name(schema_orig, atom.catalog_col)
    if table_name is None:
        pytest.skip(f"Cannot locate fixture table for column type_id={atom.catalog_col.type_id}")

    orig_table = next(t for t in schema_orig.tables if t.name == table_name)

    # Build the forge table with a fresh single-row PageStore.
    pb = PageBuilder(page_id=0, file_id=1, obj_id=_OBJ_ID, pminlen=pminlen, index_id=1)
    pb.add_record(raw_record)
    first_page = ib.add_chain([pb])
    store_forged = ib.to_page_store()

    au = AllocUnit(
        rowset_id=_OBJ_ID << 16,
        unit_type=ALLOC_IN_ROW,
        first_page=first_page,
        root_page=(0, 0),
        first_iam=(0, 0),
    )
    forged_table = Table(
        name=orig_table.name,
        object_id=_OBJ_ID,
        schema=orig_table.schema,
        index_id=1,
        columns=list(orig_table.columns),
        alloc_units=[au],
        partition_count=1,
        compression=COMPRESSION_NONE,
    )

    rows = list(read_table_rows(store_forged, forged_table))
    return rows[0] if rows else {}


_table_name_cache: dict[int, str | None] = {}


def _find_table_name(schema, col: Column) -> str | None:
    """Find which fixture table contains a column with the same Column identity."""
    for table in schema.tables:
        for tc in table.columns:
            if tc is col or tc.name == col.name and tc.type_id == col.type_id:
                return table.name
    return None


# ---------------------------------------------------------------------------
# Full-matrix value-layer tests (one parametrized test per type)
# ---------------------------------------------------------------------------

# Types that use LOB pages (off-row via complex flag) — these need the LOB
# page store too, which the basic forge doesn't set up.  Skip for now so the
# non-LOB types get value-layer coverage first.
_LOB_SKIP_TYPES = frozenset({
    "varbinary_max",
    "varchar_max",
    "nvarchar_max",
    "image",
    "text",
    "ntext",
    "xml",
})

# Types where the fixture table uses a CLR UDT / binary format that is
# opaque to encode_fixedvar (they come through as complex/off-row or have
# dedicated decode paths we test separately).
_CLR_SKIP_TYPES = frozenset({
    "hierarchyid",
    "geometry",
    "geography",
})

_SKIP_TYPES = _LOB_SKIP_TYPES | _CLR_SKIP_TYPES


def _simple_types():
    """Yield (type_name, label, ref_value) for all non-LOB, non-CLR types."""
    for type_name, label, ref_value in all_type_cases():
        if type_name not in _SKIP_TYPES:
            yield type_name, label, ref_value


@pytest.mark.fixture
@pytest.mark.parametrize(
    "type_name,label,ref_value",
    list(_simple_types()),
    ids=lambda x: x if isinstance(x, str) else repr(x),
)
def test_value_layer_matches_reference(type_name: str, label: str, ref_value: Any) -> None:
    """Re-forge authentic fixture bytes and assert read_table_rows == TYPE_CASES.

    Steps:
    1. Harvest authentic on-disk bytes for (type_name, label) from the fixture.
    2. Encode them into a fresh forge PageStore/Table.
    3. Read via read_table_rows (incl. decode_value).
    4. Assert decoded value == ref_value (independent TYPE_CASES ground truth).
    5. Guard null-fallback: if ref_value is non-null, assert decoded cell is also non-null.
    """
    skip_if_absent(_TYPECOVERAGE)
    atoms = harvest_atoms(f"t_{type_name}")
    if not atoms:
        pytest.skip(f"table t_{type_name} not found in fixture")

    atom = atoms.get(label)
    if atom is None:
        pytest.skip(f"label {label!r} not found in t_{type_name}")

    # NULL row: just verify decode returns None.
    if ref_value is None:
        row = _forge_single_row(atom)
        assert row.get("v") is None, (
            f"t_{type_name}.{label}: expected None, got {row.get('v')!r}"
        )
        return

    row = _forge_single_row(atom)
    decoded = row.get("v")

    # Null-fallback guard: a non-null reference must not silently decode to None.
    assert decoded is not None, (
        f"t_{type_name}.{label}: decode_value returned None (null-fallback) for "
        f"a non-null reference value {ref_value!r}.  "
        f"This indicates the value decoder crashed silently."
    )
    assert decoded == ref_value, (
        f"t_{type_name}.{label}: decoded {decoded!r} != reference {ref_value!r}"
    )


# ---------------------------------------------------------------------------
# Quick smoke test: run the full pipeline on all harvested atoms for a
# representative type and assert no silent null-fallbacks occur.
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_no_silent_null_fallbacks_for_int() -> None:
    """All t_int rows decode to non-null values (no silent null-fallback)."""
    skip_if_absent(_TYPECOVERAGE)
    atoms = harvest_atoms("t_int")
    assert atoms, "t_int not found in fixture"
    for label, atom in atoms.items():
        row = _forge_single_row(atom)
        if label == "null":
            assert row.get("v") is None
        else:
            assert row.get("v") is not None, (
                f"t_int.{label}: unexpected null-fallback"
            )


@pytest.mark.fixture
def test_no_silent_null_fallbacks_for_decimal() -> None:
    """All t_decimal_38_10 rows decode to non-null values."""
    skip_if_absent(_TYPECOVERAGE)
    atoms = harvest_atoms("t_decimal_38_10")
    if not atoms:
        pytest.skip("t_decimal_38_10 not in fixture")
    for label, atom in atoms.items():
        row = _forge_single_row(atom)
        if label == "null":
            assert row.get("v") is None
        else:
            assert row.get("v") is not None, f"t_decimal_38_10.{label}: null-fallback"


@pytest.mark.fixture
def test_no_silent_null_fallbacks_for_money() -> None:
    """All t_money rows decode to non-null values."""
    skip_if_absent(_TYPECOVERAGE)
    atoms = harvest_atoms("t_money")
    if not atoms:
        pytest.skip("t_money not in fixture")
    for label, atom in atoms.items():
        row = _forge_single_row(atom)
        if label == "null":
            assert row.get("v") is None
        else:
            assert row.get("v") is not None, f"t_money.{label}: null-fallback"


@pytest.mark.fixture
def test_no_silent_null_fallbacks_for_datetime2() -> None:
    """All t_datetime2_7 rows decode to non-null values."""
    skip_if_absent(_TYPECOVERAGE)
    atoms = harvest_atoms("t_datetime2_7")
    if not atoms:
        pytest.skip("t_datetime2_7 not in fixture")
    for label, atom in atoms.items():
        row = _forge_single_row(atom)
        if label == "null":
            assert row.get("v") is None
        else:
            assert row.get("v") is not None, f"t_datetime2_7.{label}: null-fallback"


@pytest.mark.fixture
def test_no_silent_null_fallbacks_for_sql_variant() -> None:
    """All t_sql_variant rows decode to non-null where the reference is non-null."""
    skip_if_absent(_TYPECOVERAGE)
    atoms = harvest_atoms("t_sql_variant")
    if not atoms:
        pytest.skip("t_sql_variant not in fixture")

    from tools.typematrix import TYPE_CASES
    tc = next((c for c in TYPE_CASES if c.name == "sql_variant"), None)
    if tc is None:
        pytest.skip("sql_variant not in TYPE_CASES")

    ref_by_label = {r.label: r.value for r in tc.rows}
    for label, atom in atoms.items():
        ref = ref_by_label.get(label)
        row = _forge_single_row(atom)
        decoded = row.get("v")
        if ref is None:
            assert decoded is None, f"t_sql_variant.{label}: expected None, got {decoded!r}"
        else:
            assert decoded is not None, (
                f"t_sql_variant.{label}: null-fallback for ref={ref!r}"
            )
            assert decoded == ref, (
                f"t_sql_variant.{label}: {decoded!r} != {ref!r}"
            )
