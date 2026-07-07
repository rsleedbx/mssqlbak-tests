"""Integration tests: DDL emission against constraintcoverage_full.bak.

Verifies that the generated CREATE TABLE script for each constraint-variant
table contains the expected structural markers.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import (
    INDEX_NONCLUSTERED,
    recover_catalog_objects,
    recover_module_definitions,
    recover_schema,
)
from mssqlbak.ddl import _colid_to_ordinal, emit_create_index, emit_create_table, emit_schema
from mssqlbak.inspect import recover_object_inventory
from mssqlbak.pages import PageStore


@pytest.fixture
def constraint_store(fixture_bak_constraints: Path) -> PageStore:
    return PageStore.from_bak(fixture_bak_constraints, catalog_only=True)


@pytest.fixture
def schema_and_catalog(constraint_store: PageStore):
    sch = recover_schema(constraint_store)
    cat = recover_catalog_objects(constraint_store)
    return sch, cat


def _ddl_for(table_name: str, schema_and_catalog) -> str:
    sch, cat = schema_and_catalog
    tbl = next(t for t in sch.tables if t.name == table_name)
    colid_map = _colid_to_ordinal(tbl)
    obj_to_table = {t.object_id: t for t in sch.tables}
    return emit_create_table(
        tbl,
        cat.indexes_for(tbl.object_id),
        cat.constraints_for(tbl.object_id),
        cat.fks_for(tbl.object_id),
        colid_map,
        obj_to_table,
    )


@pytest.mark.fixture
def test_pk_table_has_primary_key_constraint(schema_and_catalog) -> None:
    sql = _ddl_for("cc_pk", schema_and_catalog)
    assert "PRIMARY KEY CLUSTERED" in sql
    assert "CREATE TABLE [dbo].[cc_pk]" in sql


@pytest.mark.fixture
def test_check_constraint_has_definition(schema_and_catalog) -> None:
    sql = _ddl_for("cc_check_constraint", schema_and_catalog)
    assert "CONSTRAINT [ck_code] CHECK" in sql
    assert "[code]>(0)" in sql


@pytest.mark.fixture
def test_default_constraint_emitted_for_correct_column(schema_and_catalog) -> None:
    sql = _ddl_for("cc_default_constraint", schema_and_catalog)
    assert "CONSTRAINT [df_name] DEFAULT" in sql
    assert "'dflt'" in sql


@pytest.mark.fixture
def test_foreign_key_references_parent_table(schema_and_catalog) -> None:
    sql = _ddl_for("cc_fk_child", schema_and_catalog)
    assert "REFERENCES [dbo].[cc_fk_parent]" in sql
    assert "FOREIGN KEY" in sql


@pytest.mark.fixture
def test_unique_constraint_present(schema_and_catalog) -> None:
    sql = _ddl_for("cc_unique_constraint", schema_and_catalog)
    assert "UNIQUE" in sql


@pytest.mark.fixture
def test_nonclustered_index_emitted_separately(schema_and_catalog) -> None:
    sch, cat = schema_and_catalog
    tbl = next(t for t in sch.tables if t.name == "cc_index_nonclustered")
    colid_map = _colid_to_ordinal(tbl)
    ncis = [
        ix
        for ix in cat.indexes_for(tbl.object_id)
        if ix.index_type == INDEX_NONCLUSTERED
        and not ix.is_primary_key
        and not ix.is_unique_constraint
    ]
    assert len(ncis) >= 1, "expected at least one NCI on cc_index_nonclustered"
    sql = emit_create_index(ncis[0], tbl, colid_map)
    assert "CREATE NONCLUSTERED INDEX" in sql
    assert "ON [dbo].[cc_index_nonclustered]" in sql


@pytest.mark.fixture
def test_emit_schema_round_trip(constraint_store: PageStore) -> None:
    """Full emit_schema produces parseable text with all expected table names."""
    sch = recover_schema(constraint_store)
    cat = recover_catalog_objects(constraint_store)
    inv = recover_object_inventory(constraint_store)
    defs = recover_module_definitions(constraint_store)
    sql = emit_schema(sch, cat, inv, defs)

    expected_tables = {
        "cc_check_constraint",
        "cc_default_constraint",
        "cc_fk_child",
        "cc_fk_parent",
        "cc_index_nonclustered",
        "cc_pk",
        "cc_unique_constraint",
        "cc_unique_index",
        "cc_pk_nonclustered",
    }
    for name in expected_tables:
        assert f"[{name}]" in sql, f"CREATE TABLE for {name!r} missing from schema output"
