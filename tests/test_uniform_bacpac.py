"""Tests for the uniform .bacpac source API (BacpacSource + CLI).

Coverage:
- open_source() dispatches .bacpac URI to BacpacSource.
- BacpacSource.summary(): catalog_type=MSSQL_BACPAC, empty backup_sets.
- DacMetadata.xml reader (fail-soft on missing file).
- BacpacSource.list_schemas(), list_table_summaries(), list_tables(), list_columns().
- LIKE filters at schema/table/column level.
- Pagination (max_results / page_token).
- list_modules() returns empty page.
- Page.as_dict() / from_dict() round-trip.
- ExtractSpec.for_table(...).resolve(src) — column projection + rename via ProjectingSink.
- full_refresh mapping (full_refresh=True -> resume=False inside sink).
- CLI bacpac verb set matches BackupSource method set.
- CLI bacpac --json output matches src.summary().as_dict() / page.as_dict().
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pyarrow as pa
import pytest

# ---------------------------------------------------------------------------
# Fixture path
# ---------------------------------------------------------------------------

_TESTS_DIR = Path(__file__).parent
_FIXTURE_BACPAC = _TESTS_DIR / "fixtures_2022" / "typecoverage.bacpac"


def _skip_no_fixture(path: Path) -> pytest.MarkDecorator:
    return pytest.mark.skipif(
        not path.exists(), reason=f"fixture not found: {path}"
    )


# ---------------------------------------------------------------------------
# open_source() dispatch
# ---------------------------------------------------------------------------

class TestOpenSourceDispatch:
    def test_bacpac_extension_dispatches_to_bacpac_source(self, tmp_path):
        from mssqlbak.api.source import open_source
        from mssqlbak.sources.bacpac import BacpacSource

        # Create a minimal ZIP file (bacpac signature)
        import zipfile
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("model.xml", "<root/>")
        p = tmp_path / "demo.bacpac"
        p.write_bytes(buf.getvalue())

        src = open_source(str(p))
        assert isinstance(src, BacpacSource)

    def test_bak_extension_dispatches_to_bak_source(self):
        from mssqlbak.api.source import open_source
        from mssqlbak.sources.bak import BakSource

        # Don't actually open the file — just check dispatch by extension.
        # We patch BakSource.__init__ to avoid opening a non-existent file.
        with patch("mssqlbak.sources.bak.BakSource.__init__", return_value=None):
            src = open_source("backup.bak")
        assert isinstance(src, BakSource)

    def test_zip_magic_without_extension_dispatches_to_bacpac(self, tmp_path):
        from mssqlbak.api.source import open_source
        from mssqlbak.sources.bacpac import BacpacSource

        import zipfile
        import io
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("model.xml", "<root/>")
        p = tmp_path / "export_noext"  # no .bacpac extension
        p.write_bytes(buf.getvalue())

        src = open_source(str(p))
        assert isinstance(src, BacpacSource)


# ---------------------------------------------------------------------------
# DacMetadata.xml reader
# ---------------------------------------------------------------------------

class TestDacMetadata:
    def test_parse_dac_metadata_basic(self):
        from mssqlbak.bacpac import _parse_dac_metadata

        xml = b"""<?xml version="1.0"?>
<DacMetadata xmlns="http://schemas.microsoft.com/sqlserver/dac/Serialization/2012/02">
    <Name>MyDatabase</Name>
    <DacVersion>1.0.0.0</DacVersion>
    <ProductVersion>14.0.1000.169</ProductVersion>
</DacMetadata>"""
        result = _parse_dac_metadata(xml)
        assert result.get("source_database") == "MyDatabase"
        assert result.get("dac_version") == "1.0.0.0"
        assert result.get("product_version") == "14.0.1000.169"

    def test_parse_dac_metadata_empty_returns_empty_dict(self):
        from mssqlbak.bacpac import _parse_dac_metadata

        assert _parse_dac_metadata(b"not xml at all!!") == {}

    def test_parse_dac_metadata_partial(self):
        from mssqlbak.bacpac import _parse_dac_metadata

        xml = b"<DacMetadata><Name>DB</Name></DacMetadata>"
        result = _parse_dac_metadata(xml)
        assert result.get("source_database") == "DB"
        assert "dac_version" not in result


# ---------------------------------------------------------------------------
# BacpacSource — summary / catalog metadata
# ---------------------------------------------------------------------------

@_skip_no_fixture(_FIXTURE_BACPAC)
class TestBacpacSourceSummary:
    def _src(self):
        from mssqlbak.sources.bacpac import BacpacSource
        return BacpacSource(str(_FIXTURE_BACPAC))

    def test_summary_catalog_type_is_mssql_bacpac(self):
        src = self._src()
        s = src.summary()
        assert s.catalog.catalog_type == "MSSQL_BACPAC"

    def test_summary_backup_sets_empty(self):
        src = self._src()
        s = src.summary()
        assert s.backup_sets == []

    def test_summary_properties_has_provider_and_location(self):
        src = self._src()
        s = src.summary()
        assert s.catalog.properties["provider"] == "mssqlbak.bacpac"
        assert "location" in s.catalog.properties
        assert s.catalog.properties["external"] == "true"

    def test_catalog_name_derived_from_stem_when_no_dacmeta_name(self, tmp_path):
        """Falls back to filename stem when DacMetadata has no Name."""
        import zipfile
        import io
        from mssqlbak.sources.bacpac import BacpacSource

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("model.xml", "<root/>")
        p = tmp_path / "mysales.bacpac"
        p.write_bytes(buf.getvalue())

        src = BacpacSource(str(p))
        s = src.summary()
        assert s.catalog.name == "mysales"

    def test_get_catalog_returns_catalog_info(self):
        src = self._src()
        cat = src.get_catalog()
        assert cat.catalog_type == "MSSQL_BACPAC"

    def test_list_catalogs_returns_one(self):
        src = self._src()
        page = src.list_catalogs()
        assert len(page.items) == 1
        assert page.counts["n_catalogs"] == 1

    def test_list_catalogs_pattern_filter(self):
        src = self._src()
        # Match by exact name
        cat_name = src.get_catalog().name
        page = src.list_catalogs(catalog_name_pattern=cat_name)
        assert len(page.items) == 1

        # Non-matching pattern
        page2 = src.list_catalogs(catalog_name_pattern="ZZZ_no_match_%")
        assert len(page2.items) == 0

    def test_as_dict_from_dict_round_trip(self):
        src = self._src()
        s = src.summary()
        d = s.as_dict()
        from mssqlbak.api.model import SourceSummary
        s2 = SourceSummary.from_dict(d)
        assert s2.catalog.name == s.catalog.name
        assert s2.catalog.catalog_type == "MSSQL_BACPAC"
        assert s2.backup_sets == []


# ---------------------------------------------------------------------------
# BacpacSource — list_schemas / list_table_summaries / list_tables
# ---------------------------------------------------------------------------

@_skip_no_fixture(_FIXTURE_BACPAC)
class TestBacpacSourceListing:
    def _src(self):
        from mssqlbak.sources.bacpac import BacpacSource
        return BacpacSource(str(_FIXTURE_BACPAC))

    def test_list_schemas_returns_schemas(self):
        src = self._src()
        page = src.list_schemas()
        assert len(page.items) > 0
        assert all(hasattr(s, "name") for s in page.items)

    def test_list_schemas_pattern_filter(self):
        src = self._src()
        all_page = src.list_schemas()
        first_schema = all_page.items[0].name
        filtered = src.list_schemas(schema_name_pattern=first_schema)
        assert len(filtered.items) == 1
        assert filtered.items[0].name == first_schema

    def test_list_schemas_non_matching_pattern(self):
        src = self._src()
        page = src.list_schemas(schema_name_pattern="ZZZ_no_match_%")
        assert page.items == []

    def test_list_table_summaries_returns_tables(self):
        src = self._src()
        page = src.list_table_summaries()
        assert page.counts["n_tables"] > 0
        assert page.counts["n_modules"] == 0  # bacpac has no modules yet

    def test_list_table_summaries_all_object_kind_U(self):
        src = self._src()
        page = src.list_table_summaries()
        for obj in page.items:
            assert obj.object_kind == "U "

    def test_list_table_summaries_column_count_positive(self):
        src = self._src()
        page = src.list_table_summaries()
        assert any(obj.column_count > 0 for obj in page.items)

    def test_list_table_summaries_schema_filter(self):
        src = self._src()
        all_page = src.list_table_summaries()
        first_schema = all_page.items[0].schema_name
        filtered = src.list_table_summaries(schema_name_pattern=first_schema)
        assert all(obj.schema_name == first_schema for obj in filtered.items)

    def test_list_table_summaries_table_filter(self):
        src = self._src()
        all_page = src.list_table_summaries()
        first_table = all_page.items[0].name
        filtered = src.list_table_summaries(table_name_pattern=first_table)
        assert len(filtered.items) >= 1
        assert any(obj.name == first_table for obj in filtered.items)

    def test_list_table_summaries_pagination(self):
        src = self._src()
        page1 = src.list_table_summaries(max_results=2)
        assert len(page1.items) <= 2
        if page1.next_page_token is not None:
            page2 = src.list_table_summaries(max_results=2, page_token=page1.next_page_token)
            assert len(page2.items) > 0
            # No overlap
            names1 = {o.name for o in page1.items}
            names2 = {o.name for o in page2.items}
            assert not names1 & names2

    def test_list_tables_returns_table_info(self):
        src = self._src()
        page = src.list_tables()
        assert len(page.items) > 0
        for t in page.items:
            assert t.table_type == "TABLE"

    def test_list_tables_schema_filter_positional(self):
        src = self._src()
        all_page = src.list_table_summaries()
        first_schema = all_page.items[0].schema_name
        page = src.list_tables(schema_name=first_schema)
        assert all(t.schema_name == first_schema for t in page.items)

    def test_list_modules_returns_empty(self):
        src = self._src()
        page = src.list_modules()
        assert page.items == []
        assert page.counts["n_modules"] == 0

    def test_page_as_dict_round_trip(self):
        src = self._src()
        page = src.list_table_summaries()
        d = page.as_dict()
        from mssqlbak.api.model import Page, ObjectSummary
        page2 = Page.from_dict(d, item_cls=ObjectSummary)
        assert len(page2.items) == len(page.items)
        assert page2.counts == page.counts


# ---------------------------------------------------------------------------
# BacpacSource — list_columns / get_table_schema
# ---------------------------------------------------------------------------

@_skip_no_fixture(_FIXTURE_BACPAC)
class TestBacpacSourceColumns:
    def _src(self):
        from mssqlbak.sources.bacpac import BacpacSource
        return BacpacSource(str(_FIXTURE_BACPAC))

    def _pick_table(self):
        src = self._src()
        page = src.list_table_summaries()
        # Pick first table with > 0 columns
        tbl = next((o for o in page.items if o.column_count > 0), None)
        assert tbl is not None, "no table with columns found"
        return src, tbl.schema_name, tbl.name

    def test_list_columns_returns_columns(self):
        src, schema, table = self._pick_table()
        page = src.list_columns(schema, table)
        assert len(page.items) > 0

    def test_list_columns_positions_are_one_based(self):
        src, schema, table = self._pick_table()
        page = src.list_columns(schema, table)
        positions = [c.position for c in page.items]
        assert positions[0] == 1

    def test_list_columns_column_name_pattern(self):
        src, schema, table = self._pick_table()
        all_cols = src.list_columns(schema, table)
        first_col = all_cols.items[0].name
        filtered = src.list_columns(schema, table, column_name_pattern=first_col)
        assert len(filtered.items) >= 1
        assert any(c.name == first_col for c in filtered.items)

    def test_list_columns_no_match_returns_empty(self):
        src, schema, table = self._pick_table()
        page = src.list_columns(schema, table, column_name_pattern="ZZZ_no_match_%")
        assert page.items == []
        assert page.counts["n_columns"] == 0

    def test_list_columns_unknown_table_returns_empty(self):
        src = self._src()
        page = src.list_columns("dbo", "ZZZ_no_such_table")
        assert page.items == []

    def test_get_table_schema_equals_list_columns(self):
        src, schema, table = self._pick_table()
        via_schema = src.get_table_schema(schema, table)
        via_list = src.list_columns(schema, table)
        assert len(via_schema.items) == len(via_list.items)
        for a, b in zip(via_schema.items, via_list.items):
            assert a.name == b.name

    def test_type_text_present(self):
        src, schema, table = self._pick_table()
        page = src.list_columns(schema, table)
        assert any(c.type_text for c in page.items)


# ---------------------------------------------------------------------------
# ExtractSpec resolution + ProjectingSink column rename
# ---------------------------------------------------------------------------

@_skip_no_fixture(_FIXTURE_BACPAC)
class TestBacpacSpecAndRename:
    def _src(self):
        from mssqlbak.sources.bacpac import BacpacSource
        return BacpacSource(str(_FIXTURE_BACPAC))

    def _pick_non_empty_table(self):
        src = self._src()
        page = src.list_table_summaries()
        tbl = next((o for o in page.items if o.column_count >= 2), None)
        if tbl is None:
            pytest.skip("no table with >= 2 columns found")
        return src, tbl.schema_name, tbl.name

    def test_spec_for_table_resolves_to_plan(self):
        from mssqlbak.api.spec import ExtractSpec
        src, schema, table = self._pick_non_empty_table()

        spec = ExtractSpec.for_table(schema, table)
        plan = spec.resolve(src)
        # for_table creates an explicit entry but defaults include all tables,
        # so the plan covers all source tables; the named table must be present.
        assert plan is not None
        assert len(plan.tables) >= 1
        matching = [
            pt for pt in plan.tables
            if pt.source_schema.lower() == schema.lower()
            and pt.source_table.lower() == table.lower()
        ]
        assert len(matching) == 1

    def test_spec_column_rename_propagates(self):
        """include_columns + rename builds a column_map with the renamed destination."""
        from mssqlbak.api.spec import ExtractSpec
        src, schema, table = self._pick_non_empty_table()
        cols = src.list_columns(schema, table).items
        old_name = cols[0].name
        new_name = "renamed_col"

        spec = ExtractSpec.for_table(
            schema, table,
            include_columns=[old_name],  # explicit include forces column_map build
            rename={old_name: new_name},
        )
        plan = spec.resolve(src)
        assert plan is not None
        pt = next(
            (p for p in plan.tables
             if p.source_schema.lower() == schema.lower()
             and p.source_table.lower() == table.lower()),
            None,
        )
        assert pt is not None
        assert pt.column_map is not None
        assert new_name in pt.column_map.values()

    def test_spec_destination_table_override(self):
        from mssqlbak.api.spec import ExtractSpec
        src, schema, table = self._pick_non_empty_table()

        spec = ExtractSpec.for_table(schema, table, destination_table="new_table_name")
        plan = spec.resolve(src)
        assert plan is not None
        pt = next(
            (p for p in plan.tables
             if p.source_schema.lower() == schema.lower()
             and p.source_table.lower() == table.lower()),
            None,
        )
        assert pt is not None
        assert pt.destination_table == "new_table_name"

    def test_projecting_sink_renames_column(self):
        """ProjectingSink rewrites the column name in the RecordBatch schema."""
        from mssqlbak.sink import ProjectingSink, InMemorySink

        inner = InMemorySink()
        schema = pa.schema([("id", pa.int32()), ("value", pa.string())])
        column_map = {"id": "customer_id", "value": "value"}
        proj = ProjectingSink(inner, column_map=column_map, dest_qualified_name="dbo.Customers")

        rb = pa.record_batch({"id": [1, 2], "value": ["a", "b"]}, schema=schema)
        proj.open_table("dbo.Customers", rb.schema)
        proj.write_batch(rb)
        proj.close()

        batches = inner._batches.get("dbo.Customers", [])
        assert batches, "InMemorySink received no batches"
        out = batches[0]
        assert "customer_id" in out.schema.names
        assert "value" in out.schema.names
        assert "id" not in out.schema.names

    def test_empty_spec_is_none(self):
        from mssqlbak.api.spec import ExtractSpec
        spec = ExtractSpec()
        assert spec._is_empty()


# ---------------------------------------------------------------------------
# full_refresh mapping
# ---------------------------------------------------------------------------

class TestFullRefreshMapping:
    def test_full_refresh_false_means_resume(self, tmp_path):
        """full_refresh=False → resume=True → DeltaSink created with resume=True."""
        import zipfile
        import io
        from mssqlbak.sources.bacpac import BacpacSource

        # Minimal bacpac
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("model.xml", "<root/>")
        p = tmp_path / "empty.bacpac"
        p.write_bytes(buf.getvalue())

        src = BacpacSource(str(p))

        sink_kwargs: dict = {}

        def fake_extract_bacpac(source, sink, **kwargs):
            sink_kwargs["resume"] = getattr(sink, "_resume", None)
            from mssqlbak.extract import ExtractReport
            return ExtractReport()

        with patch("mssqlbak.bacpac.extract_bacpac", side_effect=fake_extract_bacpac):
            dest = tmp_path / "out"
            src.extract(None, format="delta", destination=str(dest), full_refresh=False)

        # DeltaSink should have been opened with resume=True
        assert sink_kwargs.get("resume") is True

    def test_full_refresh_true_means_no_resume(self, tmp_path):
        import zipfile
        import io
        from mssqlbak.sources.bacpac import BacpacSource

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("model.xml", "<root/>")
        p = tmp_path / "empty2.bacpac"
        p.write_bytes(buf.getvalue())

        src = BacpacSource(str(p))

        sink_kwargs: dict = {}

        def fake_extract_bacpac(source, sink, **kwargs):
            sink_kwargs["resume"] = getattr(sink, "_resume", None)
            from mssqlbak.extract import ExtractReport
            return ExtractReport()

        with patch("mssqlbak.bacpac.extract_bacpac", side_effect=fake_extract_bacpac):
            dest = tmp_path / "out2"
            src.extract(None, format="delta", destination=str(dest), full_refresh=True)

        assert sink_kwargs.get("resume") is False


# ---------------------------------------------------------------------------
# CLI verb set == BackupSource method set (symmetry)
# ---------------------------------------------------------------------------

class TestCliBackpacSymmetry:
    def test_bacpac_cli_subcommands_exist(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        for verb in ("info", "list", "schema", "extract"):
            assert verb in result.output, f"missing verb: {verb}"

    def test_bacpac_info_help(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app

        runner = CliRunner()
        result = runner.invoke(app, ["info", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output

    def test_bacpac_list_help(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app

        runner = CliRunner()
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "--schema-pattern" in result.output
        assert "--counts-only" in result.output

    def test_bacpac_schema_help(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app

        runner = CliRunner()
        result = runner.invoke(app, ["schema", "--help"])
        assert result.exit_code == 0
        assert "--schema" in result.output
        assert "--table" in result.output

    def test_bacpac_extract_help(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app

        runner = CliRunner()
        result = runner.invoke(app, ["extract", "--help"])
        assert result.exit_code == 0
        assert "--rename" in result.output
        assert "--full-refresh" in result.output
        # index-cache must NOT appear (it's .bak-only)
        assert "--index-cache" not in result.output


@_skip_no_fixture(_FIXTURE_BACPAC)
class TestCliBackpacJsonParity:
    """CLI --json output must match src.summary().as_dict() / page.as_dict()."""

    def test_bacpac_info_json_matches_summary(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app
        from mssqlbak.sources.bacpac import BacpacSource

        uri = str(_FIXTURE_BACPAC)
        runner = CliRunner()
        result = runner.invoke(app, ["info", uri, "--json"])
        assert result.exit_code == 0, result.output

        cli_data = json.loads(result.output)
        sdk_data = BacpacSource(uri).summary().as_dict()

        assert cli_data["catalog"]["catalog_type"] == sdk_data["catalog"]["catalog_type"]
        assert cli_data["catalog"]["name"] == sdk_data["catalog"]["name"]
        assert cli_data["backup_sets"] == []

    def test_bacpac_list_json_matches_sdk(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app
        from mssqlbak.sources.bacpac import BacpacSource

        uri = str(_FIXTURE_BACPAC)
        runner = CliRunner()
        result = runner.invoke(app, ["list", uri, "--json"])
        assert result.exit_code == 0, result.output

        cli_data = json.loads(result.output)
        sdk_page = BacpacSource(uri).list_table_summaries()

        assert cli_data["counts"]["n_tables"] == sdk_page.counts["n_tables"]
        assert len(cli_data["items"]) == len(sdk_page.items)

    def test_bacpac_schema_json_matches_sdk(self):
        from typer.testing import CliRunner
        from mssqlbak.cli.bacpac import app
        from mssqlbak.sources.bacpac import BacpacSource

        uri = str(_FIXTURE_BACPAC)
        src = BacpacSource(uri)
        sums = src.list_table_summaries()
        tbl = next((o for o in sums.items if o.column_count > 0), None)
        if tbl is None:
            pytest.skip("no table with columns")

        runner = CliRunner()
        result = runner.invoke(app, [
            "schema", uri,
            "--schema", tbl.schema_name,
            "--table", tbl.name,
            "--json",
        ])
        assert result.exit_code == 0, result.output

        cli_data = json.loads(result.output)
        sdk_page = src.list_columns(tbl.schema_name, tbl.name)
        assert len(cli_data["items"]) == len(sdk_page.items)
        assert cli_data["counts"]["n_columns"] == sdk_page.counts["n_columns"]


# ---------------------------------------------------------------------------
# mssqlbak --help includes bacpac group
# ---------------------------------------------------------------------------

class TestMainCliHasBackpac:
    def test_main_cli_has_bacpac_group(self):
        from typer.testing import CliRunner
        from mssqlbak._cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "bacpac" in result.output
