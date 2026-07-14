"""Tests for extended-property extraction and rendering.

Covers:
- DDL: sp_addextendedproperty generation and inline MS_Description comment in
  column definitions via emit_extended_properties / _col_def.
- PG plain sink: COMMENT ON TABLE / COLUMN rendered from Arrow schema metadata.
- Delta sink: TBLPROPERTIES configuration derived from Arrow schema metadata.
- Fixture-based round-trip: extraction from the extended_properties_full.bak
  fixture via catalog/recover + API model (skipped when fixture is absent).
"""
from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pytest

import mssqlbak.types as t
from mssqlbak.catalog import CatalogObjects, Schema
from mssqlbak.catalog.model import Column, Table
from mssqlbak.ddl import emit_extended_properties, emit_schema
from mssqlbak.sinks.pg_plain_sink import PgDumpSink


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _col(
    name: str,
    type_id: int,
    colid: int = 1,
    *,
    max_length: int = 0,
    nullable: bool = True,
    extended_properties: dict[str, str] | None = None,
) -> Column:
    return Column(
        name=name,
        colid=colid,
        type_id=type_id,
        max_length=max_length,
        precision=0,
        scale=0,
        nullable=nullable,
        leaf_offset=-1,
        is_variable=False,
        extended_properties=extended_properties or {},
    )


def _table(
    name: str,
    cols: list[Column],
    schema: str = "dbo",
    extended_properties: dict[str, str] | None = None,
) -> Table:
    return Table(
        name=name,
        object_id=1,
        schema=schema,
        columns=cols,
        extended_properties=extended_properties or {},
    )


# ---------------------------------------------------------------------------
# DDL: emit_extended_properties
# ---------------------------------------------------------------------------

class TestEmitExtendedProperties:
    def test_table_level_ms_description(self) -> None:
        tbl = _table("Orders", [_col("id", t.INT)],
                     extended_properties={"MS_Description": "Order header table"})
        schema = Schema(tables=[tbl])
        sql = emit_extended_properties(schema)
        assert "sp_addextendedproperty" in sql
        assert "MS_Description" in sql
        assert "Order header table" in sql
        assert "@level1type = N'TABLE'" in sql

    def test_column_level_ms_description(self) -> None:
        col = _col("price", t.INT,
                   extended_properties={"MS_Description": "Unit price"})
        tbl = _table("Orders", [col])
        schema = Schema(tables=[tbl])
        sql = emit_extended_properties(schema)
        assert "Unit price" in sql
        assert "@level2type = N'COLUMN'" in sql

    def test_arbitrary_property_name(self) -> None:
        tbl = _table("Orders", [_col("id", t.INT)],
                     extended_properties={"SensitivityLabel": "Confidential"})
        schema = Schema(tables=[tbl])
        sql = emit_extended_properties(schema)
        assert "SensitivityLabel" in sql
        assert "Confidential" in sql

    def test_no_properties_produces_no_exec(self) -> None:
        tbl = _table("Orders", [_col("id", t.INT)])
        schema = Schema(tables=[tbl])
        sql = emit_extended_properties(schema)
        assert "sp_addextendedproperty" not in sql

    def test_column_comment_in_col_def(self) -> None:
        col = _col("total", t.INT,
                   extended_properties={"MS_Description": "Grand total"})
        tbl = _table("T", [col])
        schema = Schema(tables=[tbl])
        catalog = CatalogObjects()
        sql = emit_schema(schema, catalog, [], {})
        assert "-- Grand total" in sql

    def test_single_quote_escaped_in_value(self) -> None:
        tbl = _table("T", [_col("id", t.INT)],
                     extended_properties={"MS_Description": "Robert's table"})
        schema = Schema(tables=[tbl])
        sql = emit_extended_properties(schema)
        assert "Robert''s table" in sql


# ---------------------------------------------------------------------------
# PG plain sink: COMMENT ON statements
# ---------------------------------------------------------------------------

class TestPgPlainSinkComments:
    def _make_schema(
        self,
        tbl_comment: str | None = None,
        col_comment: str | None = None,
    ) -> pa.Schema:
        field_meta: dict[bytes, bytes] = {}
        if col_comment:
            field_meta[b"MS_Description"] = col_comment.encode()
        schema_meta: dict[bytes, bytes] = {}
        if tbl_comment:
            schema_meta[b"MS_Description"] = tbl_comment.encode()
        return pa.schema(
            [pa.field("id", pa.int32(), metadata=field_meta)],
            metadata=schema_meta,
        )

    def _dump(self, schema: pa.Schema, tmp_path: Path, **kw: object) -> str:
        out = tmp_path / "dump.sql"
        sink = PgDumpSink(out, **kw)  # type: ignore[arg-type]
        sink.open_table("public.orders", schema)
        sink.close()
        sink.finish()
        return out.read_text()

    def test_table_comment_emitted(self, tmp_path: Path) -> None:
        output = self._dump(self._make_schema(tbl_comment="Order header table"), tmp_path)
        assert "COMMENT ON TABLE" in output
        assert "Order header table" in output

    def test_column_comment_emitted(self, tmp_path: Path) -> None:
        output = self._dump(self._make_schema(col_comment="Primary key"), tmp_path)
        assert "COMMENT ON COLUMN" in output
        assert "Primary key" in output

    def test_no_comment_no_statement(self, tmp_path: Path) -> None:
        output = self._dump(self._make_schema(), tmp_path)
        assert "COMMENT ON" not in output

    def test_single_quote_escaped(self, tmp_path: Path) -> None:
        output = self._dump(self._make_schema(tbl_comment="Robert's orders"), tmp_path)
        assert "Robert''s orders" in output

    def test_schema_only_emits_comment(self, tmp_path: Path) -> None:
        output = self._dump(
            self._make_schema(tbl_comment="Test table"), tmp_path, schema_only=True
        )
        assert "COMMENT ON TABLE" in output


# ---------------------------------------------------------------------------
# Delta sink: TBLPROPERTIES / configuration
# ---------------------------------------------------------------------------

class TestDeltaSinkExtendedProperties:
    def test_ms_description_set_as_table_description(self, tmp_path: Path) -> None:
        pytest.importorskip("deltalake")
        from deltalake import DeltaTable
        from mssqlbak.sink import DeltaSink

        schema_meta = {b"MS_Description": b"My table comment"}
        arrow_schema = pa.schema(
            [pa.field("id", pa.int32())],
            metadata=schema_meta,
        )
        sink = DeltaSink(tmp_path / "out")
        sink.open_table("dbo.t1", arrow_schema)
        sink.write_batch(pa.record_batch([[1, 2]], schema=arrow_schema))
        sink.close()

        dt = DeltaTable(str(tmp_path / "out" / "dbo" / "t1"))
        assert dt.metadata().description == "My table comment"

    def test_arrow_schema_metadata_preserved_in_parquet(self, tmp_path: Path) -> None:
        """Other extended properties flow through as Arrow schema metadata in Parquet."""
        pytest.importorskip("deltalake")
        from deltalake import DeltaTable
        from mssqlbak.sink import DeltaSink

        # Column-level MS_Description is carried as Arrow field metadata.
        field_meta = {b"MS_Description": b"The identifier"}
        arrow_schema = pa.schema(
            [pa.field("id", pa.int32(), metadata=field_meta)],
        )
        sink = DeltaSink(tmp_path / "out")
        sink.open_table("dbo.t2", arrow_schema)
        sink.write_batch(pa.record_batch([[42]], schema=arrow_schema))
        sink.close()

        dt = DeltaTable(str(tmp_path / "out" / "dbo" / "t2"))
        read_schema = dt.to_pyarrow_table().schema
        col_meta = read_schema.field("id").metadata or {}
        assert col_meta.get(b"MS_Description") == b"The identifier"

    def test_no_metadata_no_configuration(self, tmp_path: Path) -> None:
        pytest.importorskip("deltalake")
        from deltalake import DeltaTable
        from mssqlbak.sink import DeltaSink

        arrow_schema = pa.schema([pa.field("id", pa.int32())])
        sink = DeltaSink(tmp_path / "out")
        sink.open_table("dbo.t3", arrow_schema)
        sink.write_batch(pa.record_batch([[7]], schema=arrow_schema))
        sink.close()

        dt = DeltaTable(str(tmp_path / "out" / "dbo" / "t3"))
        config = dt.metadata().configuration
        assert "delta.description" not in config


# ---------------------------------------------------------------------------
# Fixture-based round-trip (skipped when fixture absent)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
class TestExtendedPropertiesFixture:
    def test_table_has_ms_description(self, fixture_bak_extended_properties: Path) -> None:
        from mssqlbak.sources.bak import BakSource

        src = BakSource(fixture_bak_extended_properties)
        tables = src.list_tables().items
        found = any(tbl.extended_properties.get("MS_Description") for tbl in tables)
        assert found, "No table with MS_Description found in fixture"

    def test_column_has_ms_description(self, fixture_bak_extended_properties: Path) -> None:
        from mssqlbak.sources.bak import BakSource

        src = BakSource(fixture_bak_extended_properties)
        for tbl_info in src.list_tables().items:
            cols = src.list_columns(tbl_info.schema_name, tbl_info.name).items
            for col_info in cols:
                if col_info.extended_properties.get("MS_Description"):
                    return
        pytest.fail("No column with MS_Description found in fixture")

    def test_arbitrary_property_extracted(self, fixture_bak_extended_properties: Path) -> None:
        from mssqlbak.sources.bak import BakSource

        src = BakSource(fixture_bak_extended_properties)
        for tbl_info in src.list_tables().items:
            for k in tbl_info.extended_properties:
                if k != "MS_Description":
                    return
            for col_info in src.list_columns(tbl_info.schema_name, tbl_info.name).items:
                for k in col_info.extended_properties:
                    if k != "MS_Description":
                        return
        pytest.fail("No arbitrary (non-MS_Description) extended property found in fixture")

    def test_ddl_contains_sp_addextendedproperty(
        self, fixture_bak_extended_properties: Path
    ) -> None:
        from mssqlbak.catalog.recover import recover_schema
        from mssqlbak.pages import PageStore
        from mssqlbak.ddl import emit_extended_properties

        store = PageStore.from_bak(fixture_bak_extended_properties, catalog_only=True)
        schema_obj = recover_schema(store)
        sql = emit_extended_properties(schema_obj)
        assert "sp_addextendedproperty" in sql, (
            "No sp_addextendedproperty found — extended properties may not have been extracted"
        )

    def test_pg_plain_comment_on_emitted(
        self, fixture_bak_extended_properties: Path, tmp_path: Path
    ) -> None:
        from mssqlbak.catalog.recover import recover_schema
        from mssqlbak.pages import PageStore
        from mssqlbak.types.arrow import arrow_schema_for

        store = PageStore.from_bak(fixture_bak_extended_properties, catalog_only=True)
        schema_obj = recover_schema(store)

        out_file = tmp_path / "dump.sql"
        sink = PgDumpSink(out_file)
        for tbl in schema_obj.tables:
            arrow_schema = arrow_schema_for(tbl)
            sink.open_table(f"public.{tbl.name}", arrow_schema)
            sink.close()
        sink.finish()
        content = out_file.read_text()
        assert "COMMENT ON" in content, "No COMMENT ON statement generated from fixture"
