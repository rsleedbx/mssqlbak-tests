"""Constraint/index encoding tests + coverage-doc guard.

Validates the empirically-recovered encoding map against the constraint fixture
(one constraint isolated per table) and keeps ``docs/CONSTRAINT_COVERAGE.md``
in sync.  The seeded verifier (``tools/constraintmatrix.expected_rows``) checks
extraction is unaffected by indexes; the catalog reader checks each constraint
is decoded as designed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import (
    INDEX_CLUSTERED,
    INDEX_HEAP,
    INDEX_NONCLUSTERED,
    Index,
    recover_catalog_objects,
    recover_schema,
)
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.constraint_coverage import DOC_PATH, build_report
from tools.constraintmatrix import CASES, expected_rows, table_name


@pytest.mark.fixture
def test_constraint_coverage_doc_is_current(fixture_bak_constraints: Path) -> None:
    expected = build_report(fixture_bak_constraints)
    actual = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    assert actual == expected, (
        "docs/CONSTRAINT_COVERAGE.md is stale; regenerate with "
        "`python -m tools.constraint_coverage`"
    )


@pytest.mark.fixture
def test_all_variant_tables_recovered(fixture_bak_constraints: Path) -> None:
    store = PageStore.from_bak(fixture_bak_constraints)
    names = {t.name for t in recover_schema(store).tables}
    expected = {table_name(c) for c in CASES}
    assert expected <= names, f"missing variant tables: {expected - names}"


@pytest.mark.fixture
def test_clustered_rows_match_seeded_verifier(fixture_bak_constraints: Path) -> None:
    """Indexes must not disturb extraction: every table -- clustered or the
    nonclustered-PK heap -- reads exactly the seeded rows.  A heap returns its
    rows in physical (page/slot) order rather than key order, so compare sorted
    by id."""
    store = PageStore.from_bak(fixture_bak_constraints)
    by_name = {t.name: t for t in recover_schema(store).tables}
    for case in CASES:
        table = by_name[table_name(case)]
        rows = [{k: r[k] for k in ("id", "code", "name")} for r in read_table_rows(store, table)]
        assert sorted(rows, key=lambda r: r["id"]) == expected_rows(case), table.name


@pytest.mark.fixture
def test_constraint_objects_decoded(fixture_bak_constraints: Path) -> None:
    """Each constraint kind appears (or not) in sysschobjs exactly as designed."""
    store = PageStore.from_bak(fixture_bak_constraints)
    objs = recover_catalog_objects(store)
    by_name = {t.name: t for t in recover_schema(store).tables}

    def codes(tbl: str) -> set[str]:
        return {c.type_code for c in objs.constraints_for(by_name[tbl].object_id)}

    # Every table has an auto-named PK object.
    for case in CASES:
        assert "PK" in codes(table_name(case)), table_name(case)

    # The extra constraint object appears only on its variant.
    assert "UQ" in codes("cc_unique_constraint")
    assert "F" in codes("cc_fk_child")
    assert "C" in codes("cc_check_constraint")
    assert "D" in codes("cc_default_constraint")

    # An index is not a constraint: no extra object on the pure-index tables.
    assert codes("cc_unique_index") == {"PK"}
    assert codes("cc_index_nonclustered") == {"PK"}


@pytest.mark.fixture
def test_index_encoding_decoded(fixture_bak_constraints: Path) -> None:
    """Index type / unique flags / key columns decode as designed."""
    store = PageStore.from_bak(fixture_bak_constraints)
    objs = recover_catalog_objects(store)
    by_name = {t.name: t for t in recover_schema(store).tables}

    def idx(tbl: str) -> dict[int, Index]:
        return {i.index_id: i for i in objs.indexes_for(by_name[tbl].object_id)}

    # Clustered PK on column 1 (id) for the baseline.
    pk = idx("cc_pk")[1]
    assert pk.index_type == INDEX_CLUSTERED and pk.is_primary_key
    assert pk.key_columns == [1]

    # Nonclustered PK leaves a heap plus a nonclustered PK index.
    np = idx("cc_pk_nonclustered")
    assert np[0].index_type == INDEX_HEAP
    assert np[2].index_type == INDEX_NONCLUSTERED and np[2].is_primary_key

    # Unique CONSTRAINT sets the unique-constraint bit; a unique INDEX does not.
    uc = idx("cc_unique_constraint")[2]
    assert uc.is_unique and uc.is_unique_constraint and uc.key_columns == [2]
    ui = idx("cc_unique_index")[2]
    assert ui.is_unique and not ui.is_unique_constraint and ui.key_columns == [2]

    # Plain nonclustered index is neither unique nor a constraint.
    ni = idx("cc_index_nonclustered")[2]
    assert ni.index_type == INDEX_NONCLUSTERED
    assert not ni.is_unique and not ni.is_unique_constraint and ni.key_columns == [2]


@pytest.mark.fixture
def test_byte_map_complete_with_indexes(fixture_bak_constraints: Path) -> None:
    """The index-heavy fixture still tiles fully with zero unclassified bytes
    (nonclustered index pages classify as data 'index page', not UNKNOWN)."""
    from tools.byte_map import UNKNOWN, build_map

    bm = build_map(fixture_bak_constraints)
    # Segments tile [0, file_size) with no gap/overlap.
    pos = 0
    for seg in bm.segments:
        assert seg.offset == pos, f"gap/overlap at {pos}"
        assert seg.category != UNKNOWN
        pos = seg.end
    assert pos == bm.file_size
    # No page classified UNKNOWN, and at least one index page is present.
    assert all(pc.category != UNKNOWN for pc in bm.page_classes)
    assert any("index page" in pc.detail for pc in bm.page_classes)
