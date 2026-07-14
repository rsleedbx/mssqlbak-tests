"""Harvest authentic per-(type, label) on-disk bytes from the typecoverage
fixture and expose the TYPE_CASES reference values.

This module is the bridge between:
- The forge (structural encoder): it provides authenticated raw-column bytes
  extracted directly from SQL Server-produced on-disk records.
- The TYPE_CASES reference (independent value ground truth): the hand-authored
  Python values a correct reader must produce for each (type, label) pair.

Because the raw bytes come from a real SQL Server backup and the expected
values are independent of the reader code, tests built on these helpers can
find pre-existing reader bugs (not just self-consistency bugs).

Usage example::

    atoms = harvest_atoms("t_int")
    for label, atom in atoms.items():
        store, table = build_forged_table([atom])
        rows = list(read_table_rows(store, table))
        assert rows[0]["v"] == expected_value("int", label)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.catalog.model import Column
from mssqlbak.pages import PageStore
from mssqlbak.records import RecordColumn, decode_record
from mssqlbak.rows.pagewalk import _data_pages_with_page
from mssqlbak.rows.synth import _record_columns

_FIXTURE_DIR = Path(__file__).parent / "fixtures_2022"
_TYPECOVERAGE = _FIXTURE_DIR / "typecoverage_full.bak"
_TYPECOVERAGE_COMPRESSED = _FIXTURE_DIR / "typecoverage_full_compressed.bak"


def skip_if_absent(path: Path) -> None:
    """Skip the calling test when *path* does not exist."""
    if not path.exists():
        pytest.skip(f"fixture absent: {path.name}")


# ---------------------------------------------------------------------------
# Atom: an authentic raw column bytes record from the fixture
# ---------------------------------------------------------------------------

@dataclass
class RawAtom:
    """Authentic on-disk column bytes for one row, harvested from a real fixture.

    ``raw_v`` is the raw bytes of the ``v`` column as returned by
    ``decode_record`` — i.e. the physical on-disk bytes SQL Server wrote, not
    yet decoded through ``decode_value``.  ``is_complex`` is ``True`` when the
    variable-length column is marked as off-row (LOB/row-overflow); in that
    case ``raw_v`` holds the in-row pointer bytes.

    ``catalog_col`` is the catalog ``Column`` object for the ``v`` column,
    carrying type_id, scale, collation_id, etc. required by ``decode_value``.

    ``rec_cols`` is the full list of ``RecordColumn`` descriptors for the table,
    in physical record order.  Supply it together with ``raw_record`` to
    reconstruct the complete FixedVar record for re-forging.
    """

    label: str
    raw_v: bytes | None
    is_complex: bool
    catalog_col: Column
    rec_cols: list[RecordColumn]
    # Full decoded raw-bytes dict (all columns), for re-forging complete records.
    raw_cells: dict[str, bytes | None]


def harvest_atoms(
    table_name: str,
    *,
    bak: Path = _TYPECOVERAGE,
) -> dict[str, RawAtom]:
    """Return ``{label: RawAtom}`` for every row of *table_name*.

    Reads on-disk bytes via ``decode_record`` only — no ``decode_value`` — so
    the result is independent of the reader's value-decode layer.  The ``label``
    column (varchar) identifies each row.
    """
    skip_if_absent(bak)
    store = PageStore.from_bak(str(bak))
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == table_name), None)
    if table is None:
        return {}

    rec_cols = _record_columns(table)
    v_col = next((c for c in table.columns if c.name == "v"), None)

    atoms: dict[str, RawAtom] = {}
    for _pid, _fid, page in _data_pages_with_page(store, table):
        for slot in range(page.header.slot_cnt):
            raw_rec = page.record(slot)
            complex_flags: dict[str, bool] = {}
            try:
                cells = decode_record(raw_rec, rec_cols, complex_flags)
            except (ValueError, IndexError):
                continue
            label_raw = cells.get("label")
            if label_raw is None:
                continue
            label = label_raw.decode("latin-1", errors="replace").rstrip()
            if table_name.startswith("t_nchar") or table_name.startswith("t_char"):
                label = label_raw.decode("latin-1", errors="replace").rstrip()
            raw_v = cells.get("v")
            atoms[label] = RawAtom(
                label=label,
                raw_v=raw_v,
                is_complex=bool(complex_flags.get("v")),
                catalog_col=v_col or table.columns[0],
                rec_cols=rec_cols,
                raw_cells=dict(cells),
            )
    return atoms


# ---------------------------------------------------------------------------
# TYPE_CASES reference-value lookup
# ---------------------------------------------------------------------------

def expected_value(type_name: str, label: str) -> Any:
    """Return the reference Python value for *type_name* / *label*.

    Raises ``KeyError`` when the type or label is not in the matrix.
    Uses the hand-authored ``TYPE_CASES`` from tools/typematrix.py — the
    canonical independent ground truth.
    """
    from tools.typematrix import TYPE_CASES  # noqa: PLC0415 (late import ok in test helpers)
    tc = next((c for c in TYPE_CASES if c.name == type_name), None)
    if tc is None:
        raise KeyError(f"type {type_name!r} not in TYPE_CASES")
    row = next((r for r in tc.rows if r.label == label), None)
    if row is None:
        raise KeyError(f"label {label!r} not in TYPE_CASES[{type_name!r}]")
    return row.value


def all_type_cases():
    """Yield (type_name, label, expected_value) triples for all non-auto types."""
    from tools.typematrix import TYPE_CASES  # noqa: PLC0415
    for tc in TYPE_CASES:
        if tc.auto or tc.fallback_xtype is not None:
            continue
        for row in tc.rows:
            yield tc.name, row.label, row.value


# ---------------------------------------------------------------------------
# Compressed (CD) atom harvesting
# ---------------------------------------------------------------------------

@dataclass
class CdAtom:
    """Physical column data from one row of a ROW/PAGE-compressed table.

    ``physical_data`` is the list returned by ``physical_columns(raw)``,
    indexed by the CD array slot position (= ``null_bit - 1`` for each column).

    ``catalog_cols`` are the table's catalog Column objects (with the type
    metadata needed by ``decode_compressed_value``).
    """

    label: str
    physical_data: list  # list[bytes | None | _OffRowLob] from physical_columns
    catalog_cols: list[Column]
    # Mapping col.name -> physical_data index (same order as catalog_cols).
    col_idx: dict[str, int]


def harvest_cd_atoms(
    table_name: str,
    *,
    bak: Path = _TYPECOVERAGE_COMPRESSED,
) -> dict[str, CdAtom]:
    """Return ``{label: CdAtom}`` for every row of a compressed fixture table.

    Uses ``physical_columns(raw)`` from the CD path to extract per-column data
    in their compressed physical form.  The label is decoded via the catalog's
    label column decoder — not the compressed decoder — so it is always a
    plain string.
    """
    skip_if_absent(bak)
    from mssqlbak.rowcompress import physical_columns  # noqa: PLC0415

    store = PageStore.from_bak(str(bak))
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == table_name), None)
    if table is None:
        return {}

    phys_cols = [
        c for c in table.columns
        if not c.is_sparse and not c.is_column_set
    ]
    col_idx = {c.name: i for i, c in enumerate(phys_cols)}
    label_col = next((c for c in table.columns if c.name == "label"), None)
    label_idx = col_idx.get("label", 0) if label_col else 0

    from mssqlbak.rows.pagewalk import _data_pages_with_page  # noqa: PLC0415
    from mssqlbak.recordtype import cd_emittable  # noqa: PLC0415

    atoms: dict[str, CdAtom] = {}
    for _pid, _fid, page in _data_pages_with_page(store, table):
        for slot in range(page.header.slot_cnt):
            raw = page.record(slot)
            if not cd_emittable(raw):
                continue
            try:
                phys = physical_columns(raw)
            except Exception:
                continue
            label_data = phys[label_idx] if label_idx < len(phys) else None
            if label_data is None:
                continue
            # Decode label as varchar (label is always a varchar column).
            label = label_data.decode("latin-1", errors="replace").rstrip()
            atoms[label] = CdAtom(
                label=label,
                physical_data=list(phys),
                catalog_cols=phys_cols,
                col_idx=col_idx,
            )
    return atoms
