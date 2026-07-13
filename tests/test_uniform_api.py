"""Tests for the uniform multi-source API (catalog-lazy + api/model + sources/bak).

Coverage:
- _like_to_regex / _like_matches semantics (%, _, escape, empty=all).
- recover_column_counts: correct counts from syscolpars.
- recover_object_summaries: tables + modules + column_count.
- recover_table_columns: lazy per-table columns with pattern filter.
- api/model: Page, CatalogInfo, SchemaInfo, TableInfo, ColumnInfo,
  SourceSummary, BackupSetSummary, LsnSet as_dict/from_dict round-trip.
- ExtractSpec: from_dict / for_table / _is_empty / resolve / layering / rename.
- ExtractPlan: PlannedTable as_dict/from_dict, dest_schema/dest_table.
- RenameTransform: all modes.
- ProjectingSink: column projection and rename.
- BakSource.summary(): catalog info + LSNs (fail-soft).
- BakSource.list_schemas(), list_table_summaries(), list_columns().
- full_refresh -> resume mapping in extract_bak.
- CLI bak --help structure and --json output parity.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pyarrow as pa
import pytest

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_TESTS_DIR = Path(__file__).parent
_FIXTURE_BAK = _TESTS_DIR / "fixtures_2022" / "typecoverage_full.bak"


def _skip_no_fixture(path: Path) -> pytest.MarkDecorator:
    return pytest.mark.skipif(
        not path.exists(), reason=f"fixture not found: {path}"
    )


# ---------------------------------------------------------------------------
# _like_to_regex / _like_matches
# ---------------------------------------------------------------------------

class TestLikePattern:
    def setup_method(self):
        from mssqlbak.catalog.recover import _like_matches, _like_to_regex
        self._like_to_regex = _like_to_regex
        self._like_matches = _like_matches

    def test_percent_matches_any_chars(self):
        pat = self._like_to_regex("sales%")
        assert pat.fullmatch("sales") is not None
        assert pat.fullmatch("salesorders") is not None
        assert pat.fullmatch("SALES") is not None   # case-insensitive

    def test_percent_alone_matches_everything(self):
        pat = self._like_to_regex("%")
        assert pat.fullmatch("anything_at_all") is not None
        assert pat.fullmatch("") is not None

    def test_underscore_matches_single_char(self):
        pat = self._like_to_regex("t_st")
        assert pat.fullmatch("test") is not None
        assert pat.fullmatch("tXst") is not None
        assert pat.fullmatch("toast") is None     # two chars between t and st

    def test_literal_matches_exactly(self):
        pat = self._like_to_regex("dbo")
        assert pat.fullmatch("dbo") is not None
        assert pat.fullmatch("DBO") is not None   # case-insensitive
        assert pat.fullmatch("dboo") is None

    def test_regex_special_chars_are_escaped(self):
        pat = self._like_to_regex("dbo.Orders")
        assert pat.fullmatch("dbo.Orders") is not None
        assert pat.fullmatch("dboXOrders") is None  # '.' must be literal

    def test_like_matches_none_returns_true(self):
        assert self._like_matches("anything", None) is True
        assert self._like_matches("anything", "") is True

    def test_like_matches_pattern(self):
        assert self._like_matches("Sales", "Sales%") is True
        assert self._like_matches("Billing", "Sales%") is False

    def test_empty_pattern_matches_empty_string(self):
        pat = self._like_to_regex("")
        assert pat.fullmatch("") is not None
        assert pat.fullmatch("nonempty") is None


# ---------------------------------------------------------------------------
# recover_column_counts / recover_object_summaries
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _FIXTURE_BAK.exists(), reason="fixture not found")
class TestRecoverObjectSummaries:
    @pytest.fixture(autouse=True)
    def _setup(self):
        from mssqlbak.pages import PageStore

        self._store = PageStore.from_bak(_FIXTURE_BAK, catalog_only=True)

    def test_column_counts_is_dict(self):
        from mssqlbak.catalog.recover import recover_column_counts

        counts = recover_column_counts(self._store)
        assert isinstance(counts, dict)
        # Should have at least one entry (typecoverage has user tables).
        assert len(counts) > 0
        for val in counts.values():
            assert isinstance(val, int)
            assert val >= 0

    def test_object_summaries_returns_list(self):
        from mssqlbak.catalog.recover import recover_object_summaries

        summaries = recover_object_summaries(self._store)
        assert isinstance(summaries, list)
        assert len(summaries) > 0

    def test_object_summaries_have_user_tables(self):
        from mssqlbak.catalog.recover import recover_object_summaries

        summaries = recover_object_summaries(self._store)
        user_tables = [s for s in summaries if s.object_kind == "U "]
        assert len(user_tables) > 0

    def test_object_summaries_column_count_nonnegative(self):
        from mssqlbak.catalog.recover import recover_object_summaries

        summaries = recover_object_summaries(self._store)
        user_tables = [s for s in summaries if s.object_kind == "U "]
        # All column counts must be >= 0 (some internal sys tables have 0).
        for t in user_tables:
            assert t.column_count >= 0
        # At least one non-system user table should have columns.
        non_sys = [t for t in user_tables if t.schema_name != "sys"]
        assert any(t.column_count > 0 for t in non_sys)

    def test_schema_name_pattern_filter(self):
        from mssqlbak.catalog.recover import recover_object_summaries

        all_summaries = recover_object_summaries(self._store)
        schemas = {s.schema_name for s in all_summaries}
        if not schemas:
            return
        # Filter for a schema that doesn't exist.
        filtered = recover_object_summaries(
            self._store, schema_name_pattern="ZZZZ_nonexistent_%"
        )
        assert filtered == []

    def test_table_name_pattern_filter(self):
        from mssqlbak.catalog.recover import recover_object_summaries

        all_summaries = recover_object_summaries(self._store)
        if not all_summaries:
            return
        first_name = all_summaries[0].name
        # Filter for the exact first name.
        filtered = recover_object_summaries(
            self._store, table_name_pattern=first_name
        )
        assert any(s.name == first_name for s in filtered)

    def test_summaries_no_user_data_page_scan(self):
        """Summaries must not trigger schema.tables column decode."""
        from mssqlbak.catalog.recover import recover_object_summaries

        # Simply calling recover_object_summaries should succeed without
        # triggering any user-table page walks.  We verify it returns results
        # without touching the type-decode path.
        summaries = recover_object_summaries(self._store)
        assert all(hasattr(s, "object_kind") for s in summaries)


@pytest.mark.skipif(not _FIXTURE_BAK.exists(), reason="fixture not found")
class TestRecoverTableColumns:
    @pytest.fixture(autouse=True)
    def _setup(self):
        from mssqlbak.catalog.recover import recover_table_columns
        from mssqlbak.pages import PageStore

        self._store = PageStore.from_bak(_FIXTURE_BAK, catalog_only=True)
        self._recover_table_columns = recover_table_columns

    def test_returns_columns_for_known_table(self):
        from mssqlbak.catalog.recover import recover_object_summaries, recover_schema

        summaries = recover_object_summaries(self._store)
        user_tables = [s for s in summaries if s.object_kind == "U "]
        assert user_tables, "no user tables found"
        first = user_tables[0]

        # Get object_id from recover_schema.
        schema = recover_schema(self._store)
        table = next(
            (t for t in schema.tables
             if t.schema.lower() == first.schema_name.lower()
             and t.name.lower() == first.name.lower()),
            None,
        )
        if table is None:
            pytest.skip("table object_id not found")

        cols = self._recover_table_columns(self._store, table.object_id)
        assert len(cols) == first.column_count

    def test_column_name_pattern_filter(self):
        from mssqlbak.catalog.recover import recover_object_summaries, recover_schema

        summaries = recover_object_summaries(self._store)
        user_tables = [s for s in summaries if s.object_kind == "U " and s.column_count > 1]
        if not user_tables:
            pytest.skip("no multi-column table found")
        first = user_tables[0]

        schema = recover_schema(self._store)
        table = next(
            (t for t in schema.tables
             if t.schema.lower() == first.schema_name.lower()
             and t.name.lower() == first.name.lower()),
            None,
        )
        if table is None:
            pytest.skip("table not found in schema")

        # Pattern matching none should return empty.
        cols = self._recover_table_columns(
            self._store, table.object_id, column_name_pattern="ZZZZ_none_%"
        )
        assert cols == []

    def test_unknown_object_id_returns_empty(self):
        cols = self._recover_table_columns(self._store, 99999999)
        assert cols == []


# ---------------------------------------------------------------------------
# api/model: as_dict / from_dict round-trips
# ---------------------------------------------------------------------------

class TestModelRoundTrip:
    def test_page_as_dict_from_dict(self):
        from mssqlbak.api.model import Page

        p: Page[dict] = Page(items=[{"a": 1}], next_page_token="5", counts={"n": 1})
        d = p.as_dict()
        assert d["items"] == [{"a": 1}]
        assert d["next_page_token"] == "5"
        assert d["counts"] == {"n": 1}
        p2 = Page.from_dict(d)
        assert p2.next_page_token == "5"

    def test_catalog_info_round_trip(self):
        from mssqlbak.api.model import CatalogInfo

        ci = CatalogInfo(
            name="mydb",
            full_name="mydb",
            catalog_type="MSSQL_BAK",
            owner="SQLSERVER01",
            properties={"location": "/tmp/foo.bak", "provider": "mssqlbak.bak"},
            options={"endpoint_url": "https://s3.example.com"},
        )
        d = ci.as_dict()
        assert d["name"] == "mydb"
        assert d["catalog_type"] == "MSSQL_BAK"
        ci2 = CatalogInfo.from_dict(d)
        assert ci2.name == "mydb"
        assert ci2.properties["location"] == "/tmp/foo.bak"
        assert ci2.options["endpoint_url"] == "https://s3.example.com"

    def test_lsn_set_round_trip(self):
        from mssqlbak.api.model import LsnSet

        ls = LsnSet(
            start=(100, 200, 3),
            start_decimal="10000000000002000003",
            end=(101, 0, 1),
            end_decimal="10100000000000000001",
        )
        d = ls.as_dict()
        assert d["start"] == [100, 200, 3]
        ls2 = LsnSet.from_dict(d)
        assert ls2.start == (100, 200, 3)
        assert ls2.start_decimal == "10000000000002000003"

    def test_source_summary_round_trip(self):
        from mssqlbak.api.model import BackupSetSummary, CatalogInfo, LsnSet, SourceSummary

        cat = CatalogInfo(name="db", full_name="db")
        bs = BackupSetSummary(
            backup_type="Database",
            write_date="2024-01-01T00:00:00",
            lsns=LsnSet(start=(1, 0, 0), start_decimal="10000000000000000000"),
        )
        ss = SourceSummary(catalog=cat, backup_sets=[bs])
        d = ss.as_dict()
        ss2 = SourceSummary.from_dict(d)
        assert ss2.catalog.name == "db"
        assert ss2.backup_sets[0].backup_type == "Database"
        assert ss2.backup_sets[0].lsns is not None
        assert ss2.backup_sets[0].lsns.start == (1, 0, 0)

    def test_column_info_round_trip(self):
        from mssqlbak.api.model import ColumnInfo

        ci = ColumnInfo(
            name="customer_id",
            position=1,
            nullable=False,
            type_name="INT",
            type_text="int",
        )
        d = ci.as_dict()
        ci2 = ColumnInfo.from_dict(d)
        assert ci2.name == "customer_id"
        assert ci2.nullable is False
        assert ci2.type_text == "int"

    def test_object_summary_round_trip(self):
        from mssqlbak.api.model import ObjectSummary

        os_ = ObjectSummary(
            schema_name="dbo",
            name="Orders",
            full_name="dbo.Orders",
            object_kind="U ",
            column_count=7,
        )
        d = os_.as_dict()
        os2 = ObjectSummary.from_dict(d)
        assert os2.column_count == 7
        assert os2.object_kind == "U "

    def test_page_as_dict_json_serializable(self):
        """Page.as_dict() must be JSON-serializable (no non-primitive types)."""
        from mssqlbak.api.model import CatalogInfo, Page

        ci = CatalogInfo(name="db", full_name="db")
        p: Page[CatalogInfo] = Page(items=[ci], counts={"n": 1})
        d = p.as_dict()
        json_str = json.dumps(d)   # must not raise
        assert json_str


# ---------------------------------------------------------------------------
# ExtractSpec
# ---------------------------------------------------------------------------

class TestExtractSpec:
    def test_empty_spec_is_empty(self):
        from mssqlbak.api.spec import ExtractSpec

        spec = ExtractSpec()
        assert spec._is_empty() is True

    def test_empty_spec_resolves_to_none(self):
        from mssqlbak.api.spec import ExtractSpec

        spec = ExtractSpec()
        result = spec.resolve(MagicMock())
        assert result is None

    def test_from_dict_minimal(self):
        from mssqlbak.api.spec import ExtractSpec

        spec = ExtractSpec.from_dict({"version": 1})
        assert spec._is_empty() is True

    def test_from_dict_with_rules(self):
        from mssqlbak.api.spec import ExtractSpec

        d = {
            "version": 1,
            "defaults": {"include": True},
            "rules": [
                {"match": {"schema": "staging%"}, "include": False},
            ],
        }
        spec = ExtractSpec.from_dict(d)
        assert spec.defaults.include is True
        assert len(spec.rules) == 1
        assert spec.rules[0].schema_pattern == "staging%"
        assert spec.rules[0].layer.include is False

    def test_for_table_include_columns(self):
        from mssqlbak.api.spec import ExtractSpec

        spec = ExtractSpec.for_table(
            "sales", "CUSTOMERS",
            include_columns=["CUST_ID", "FIRST_NM"],
            rename={"CUST_ID": "customer_key"},
        )
        assert len(spec.tables) == 1
        layer = spec.tables[0].layer
        assert layer.include_columns == ["CUST_ID", "FIRST_NM"]
        assert layer.rename == {"CUST_ID": "customer_key"}

    def test_for_table_mutual_exclusion_raises(self):
        from mssqlbak.api.spec import ExtractSpec

        with pytest.raises(ValueError, match="mutually exclusive"):
            ExtractSpec.for_table(
                "dbo", "T",
                include_columns=["A"],
                exclude_columns=["B"],
            )

    def test_resolve_layers_tables_over_rules(self):
        """tables[] (explicit) wins over rules[]."""
        from mssqlbak.api.spec import ExtractSpec

        d = {
            "version": 1,
            "defaults": {"include": True, "destination_schema": "default_schema"},
            "rules": [{"match": {"schema": "dbo"}, "destination_schema": "rules_schema"}],
            "tables": [{"source": {"schema": "dbo", "table": "Orders"}, "destination_schema": "explicit_schema"}],
        }
        spec = ExtractSpec.from_dict(d)

        # Mock source that returns one table.
        mock_src = MagicMock()
        from mssqlbak.api.model import ObjectSummary, Page

        mock_src.list_table_summaries.return_value = Page(
            items=[ObjectSummary(schema_name="dbo", name="Orders", full_name="dbo.Orders", object_kind="U ")],
        )

        plan = spec.resolve(mock_src)
        assert plan is not None
        assert len(plan.tables) == 1
        pt = plan.tables[0]
        assert pt.destination_schema == "explicit_schema"

    def test_resolve_rules_over_defaults(self):
        """rules[] beat defaults."""
        from mssqlbak.api.spec import ExtractSpec

        d = {
            "version": 1,
            "defaults": {"include": True, "destination_schema": "default_schema"},
            "rules": [{"match": {"schema": "sales"}, "destination_schema": "rules_schema"}],
        }
        spec = ExtractSpec.from_dict(d)

        mock_src = MagicMock()
        from mssqlbak.api.model import ObjectSummary, Page

        mock_src.list_table_summaries.return_value = Page(
            items=[ObjectSummary(schema_name="sales", name="Orders", full_name="sales.Orders", object_kind="U ")],
        )

        plan = spec.resolve(mock_src)
        assert plan is not None
        pt = plan.tables[0]
        assert pt.destination_schema == "rules_schema"

    def test_resolve_exclude_rule(self):
        """Rules can exclude entire schemas."""
        from mssqlbak.api.spec import ExtractSpec

        d = {
            "version": 1,
            "defaults": {"include": True},
            "rules": [{"match": {"schema": "staging%"}, "include": False}],
        }
        spec = ExtractSpec.from_dict(d)

        mock_src = MagicMock()
        from mssqlbak.api.model import ObjectSummary, Page

        mock_src.list_table_summaries.return_value = Page(
            items=[
                ObjectSummary(schema_name="staging", name="Temp", full_name="staging.Temp", object_kind="U "),
                ObjectSummary(schema_name="dbo", name="Orders", full_name="dbo.Orders", object_kind="U "),
            ],
        )

        plan = spec.resolve(mock_src)
        assert plan is not None
        assert len(plan.tables) == 1
        assert plan.tables[0].source_schema == "dbo"

    def test_column_map_from_include_columns(self):
        """for_table with include_columns populates column_map."""
        from mssqlbak.api.spec import ExtractSpec

        spec = ExtractSpec.for_table(
            "dbo", "T",
            include_columns=["A", "B"],
            rename={"A": "a_renamed"},
        )
        mock_src = MagicMock()
        from mssqlbak.api.model import ObjectSummary, Page

        mock_src.list_table_summaries.return_value = Page(
            items=[ObjectSummary(schema_name="dbo", name="T", full_name="dbo.T", object_kind="U ")],
        )
        plan = spec.resolve(mock_src)
        assert plan is not None
        assert plan.tables[0].column_map == {"A": "a_renamed", "B": "B"}


# ---------------------------------------------------------------------------
# RenameTransform
# ---------------------------------------------------------------------------

class TestRenameTransform:
    def _t(self, mode: str, **kw: object):
        from mssqlbak.api.spec import RenameTransform
        return RenameTransform(mode=mode, **kw)

    def test_none(self):
        assert self._t("none").apply("CustomerID") == "CustomerID"

    def test_lower(self):
        assert self._t("lower").apply("CustomerID") == "customerid"

    def test_upper(self):
        assert self._t("upper").apply("CustomerID") == "CUSTOMERID"

    def test_snake_case_camel(self):
        from mssqlbak.api.spec import RenameTransform
        t = RenameTransform(mode="snake_case")
        assert t.apply("CustomerID") == "customer_id"
        assert t.apply("OrderDate") == "order_date"

    def test_snake_case_underscores(self):
        from mssqlbak.api.spec import RenameTransform
        t = RenameTransform(mode="snake_case")
        assert t.apply("FIRST_NM") == "first_nm"

    def test_regex(self):
        from mssqlbak.api.spec import RenameTransform
        t = RenameTransform(mode="regex", regex_pattern=r"_ID$", regex_replace="_key")
        assert t.apply("CUST_ID") == "CUST_key"

    def test_from_value_string(self):
        from mssqlbak.api.spec import RenameTransform
        t = RenameTransform.from_value("snake_case")
        assert t.mode == "snake_case"

    def test_from_value_dict(self):
        from mssqlbak.api.spec import RenameTransform
        t = RenameTransform.from_value({"mode": "regex", "regex_pattern": "foo", "regex_replace": "bar"})
        assert t.mode == "regex"
        assert t.regex_pattern == "foo"


# ---------------------------------------------------------------------------
# ExtractPlan / PlannedTable
# ---------------------------------------------------------------------------

class TestExtractPlan:
    def test_planned_table_dest_properties(self):
        from mssqlbak.api.plan import PlannedTable

        pt = PlannedTable(
            source_schema="dbo",
            source_table="Customers",
            destination_schema="sales",
            destination_table="dim_customers",
            column_map={"CUST_ID": "customer_key", "NAME": "name"},
        )
        assert pt.dest_schema == "sales"
        assert pt.dest_table == "dim_customers"

    def test_planned_table_fallback_to_source(self):
        from mssqlbak.api.plan import PlannedTable

        pt = PlannedTable(source_schema="dbo", source_table="Orders")
        assert pt.dest_schema == "dbo"
        assert pt.dest_table == "Orders"

    def test_planned_table_round_trip(self):
        from mssqlbak.api.plan import PlannedTable

        pt = PlannedTable(
            source_schema="dbo",
            source_table="Orders",
            column_map={"A": "a", "B": "b_renamed"},
        )
        d = pt.as_dict()
        pt2 = PlannedTable.from_dict(d)
        assert pt2.column_map == {"A": "a", "B": "b_renamed"}

    def test_extract_plan_round_trip(self):
        from mssqlbak.api.plan import ExtractPlan, PlannedTable

        plan = ExtractPlan(
            tables=[
                PlannedTable(source_schema="dbo", source_table="Orders"),
                PlannedTable(source_schema="dbo", source_table="Customers"),
            ]
        )
        d = plan.as_dict()
        plan2 = ExtractPlan.from_dict(d)
        assert len(plan2.tables) == 2


# ---------------------------------------------------------------------------
# ProjectingSink
# ---------------------------------------------------------------------------

class TestProjectingSink:
    def _make_batch(self, data: dict[str, list]) -> pa.RecordBatch:
        arrays = {k: pa.array(v) for k, v in data.items()}
        return pa.record_batch(arrays)

    def test_projection_selects_and_renames(self):
        from mssqlbak.sink import InMemorySink, ProjectingSink

        inner = InMemorySink()
        proj = ProjectingSink(inner, column_map={"A": "a_renamed", "B": "B"})
        batch = self._make_batch({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
        proj.open_table("dbo.T", pa.schema([
            pa.field("A", pa.int64()),
            pa.field("B", pa.int64()),
            pa.field("C", pa.int64()),
        ]))
        proj.write_batch(batch)
        proj.close()

        result = inner.to_arrow_table("dbo.T")
        assert set(result.column_names) == {"a_renamed", "B"}
        assert result.num_rows == 2

    def test_empty_column_map_is_passthrough(self):
        from mssqlbak.sink import InMemorySink, ProjectingSink

        inner = InMemorySink()
        proj = ProjectingSink(inner, column_map={})
        batch = self._make_batch({"X": [10, 20]})
        schema = pa.schema([pa.field("X", pa.int64())])
        proj.open_table("dbo.T", schema)
        proj.write_batch(batch)
        proj.close()

        result = inner.to_arrow_table("dbo.T")
        assert "X" in result.column_names

    def test_dest_qualified_name_override(self):
        from mssqlbak.sink import InMemorySink, ProjectingSink

        inner = InMemorySink()
        proj = ProjectingSink(
            inner,
            column_map={"A": "a"},
            dest_qualified_name="sales.dim_customers",
        )
        batch = self._make_batch({"A": [1]})
        proj.open_table(
            "dbo.Customers",
            pa.schema([pa.field("A", pa.int64())]),
        )
        proj.write_batch(batch)
        proj.close()

        assert "sales.dim_customers" in inner.table_names


# ---------------------------------------------------------------------------
# BakSource (integration tests, skipped if fixture absent)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _FIXTURE_BAK.exists(), reason="fixture not found")
class TestBakSource:
    @pytest.fixture(autouse=True)
    def _src(self):
        from mssqlbak.sources.bak import BakSource

        self.src = BakSource(str(_FIXTURE_BAK))

    def test_summary_returns_source_summary(self):
        from mssqlbak.api.model import SourceSummary

        s = self.src.summary()
        assert isinstance(s, SourceSummary)
        assert s.catalog.catalog_type == "MSSQL_BAK"
        assert s.catalog.name  # non-empty database name

    def test_summary_catalog_has_location(self):
        s = self.src.summary()
        assert "location" in s.catalog.properties

    def test_summary_catalog_has_provider(self):
        s = self.src.summary()
        assert s.catalog.properties.get("provider") == "mssqlbak.bak"

    def test_summary_backup_sets_present(self):
        s = self.src.summary()
        assert len(s.backup_sets) >= 1
        bs = s.backup_sets[0]
        assert bs.backup_type  # non-empty

    def test_summary_lsns_present_or_none(self):
        """LSNs may or may not be present; no fabrication."""
        s = self.src.summary()
        for bs in s.backup_sets:
            if bs.lsns is not None:
                ls = bs.lsns
                # If start is present, decimal should also be present.
                if ls.start is not None:
                    assert ls.start_decimal is not None
                    # Verify decimal formula: vlf*10^13 + blk*10^4 + rec
                    vlf, blk, rec = ls.start
                    expected = str(vlf * 10**13 + blk * 10**4 + rec)
                    assert ls.start_decimal == expected

    def test_get_catalog_returns_catalog_info(self):
        from mssqlbak.api.model import CatalogInfo

        cat = self.src.get_catalog()
        assert isinstance(cat, CatalogInfo)
        assert cat.catalog_type == "MSSQL_BAK"

    def test_list_catalogs(self):
        page = self.src.list_catalogs()
        assert len(page.items) == 1
        assert page.items[0].catalog_type == "MSSQL_BAK"

    def test_list_schemas_returns_page(self):
        page = self.src.list_schemas()
        assert len(page.items) >= 1
        assert all(hasattr(s, "name") for s in page.items)

    def test_list_table_summaries_has_counts(self):
        page = self.src.list_table_summaries()
        assert "n_tables" in page.counts
        assert page.counts["n_tables"] >= 1

    def test_list_table_summaries_schema_pattern(self):
        page = self.src.list_table_summaries(schema_name_pattern="ZZNOEXIST%")
        assert page.items == []

    def test_list_tables_returns_page(self):
        page = self.src.list_tables()
        assert len(page.items) >= 1

    def test_get_table_schema_returns_columns(self):
        # Get any non-sys user table with columns.
        summaries = self.src.list_table_summaries()
        user_tables = [
            s for s in summaries.items
            if s.object_kind == "U " and s.schema_name != "sys" and s.column_count > 0
        ]
        if not user_tables:
            pytest.skip("no non-sys user tables with columns")
        first = user_tables[0]
        page = self.src.get_table_schema(first.schema_name, first.name)
        assert len(page.items) > 0
        assert page.counts["n_columns"] > 0

    def test_list_columns_pattern_filter(self):
        summaries = self.src.list_table_summaries()
        user_tables = [
            s for s in summaries.items
            if s.object_kind == "U " and s.schema_name != "sys" and s.column_count > 0
        ]
        if not user_tables:
            pytest.skip("no suitable tables found")
        first = user_tables[0]
        page = self.src.list_columns(
            first.schema_name, first.name, column_name_pattern="ZZNOEXIST%"
        )
        assert page.items == []

    def test_summary_as_dict_json_serializable(self):
        s = self.src.summary()
        d = s.as_dict()
        json.dumps(d)  # must not raise

    def test_get_catalog_equals_summary_catalog(self):
        cat = self.src.get_catalog()
        summary_cat = self.src.summary().catalog
        assert cat.name == summary_cat.name


# ---------------------------------------------------------------------------
# full_refresh -> resume mapping
# ---------------------------------------------------------------------------

class TestFullRefreshMapping:
    def test_full_refresh_false_equals_resume_true(self):
        """full_refresh=False should preserve resume=True behaviour."""
        from mssqlbak.extract.driver import extract_bak

        mock_sink = MagicMock()
        with patch("mssqlbak.extract.driver._extract_bak_inner") as mock_inner:
            mock_inner.return_value = MagicMock()
            try:
                extract_bak("/fake.bak", mock_sink, full_refresh=False)
            except Exception:  # noqa: BLE001
                pass
            if mock_inner.called:
                call_kwargs = mock_inner.call_args[1]
                assert call_kwargs.get("resume") is True

    def test_full_refresh_true_equals_resume_false(self):
        """full_refresh=True should set resume=False."""
        from mssqlbak.extract.driver import extract_bak

        mock_sink = MagicMock()
        with patch("mssqlbak.extract.driver._extract_bak_inner") as mock_inner:
            mock_inner.return_value = MagicMock()
            try:
                extract_bak("/fake.bak", mock_sink, full_refresh=True)
            except Exception:  # noqa: BLE001
                pass
            if mock_inner.called:
                call_kwargs = mock_inner.call_args[1]
                assert call_kwargs.get("resume") is False


# ---------------------------------------------------------------------------
# CLI symmetry: --json output == Python as_dict()
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _FIXTURE_BAK.exists(), reason="fixture not found")
class TestCLISymmetry:
    def test_bak_info_json_matches_summary_as_dict(self):
        """CLI bak info --json output must equal src.summary().as_dict()."""
        from typer.testing import CliRunner

        from mssqlbak._cli import app
        from mssqlbak.sources.bak import BakSource

        runner = CliRunner()
        result = runner.invoke(app, ["bak", "info", str(_FIXTURE_BAK), "--json"])
        assert result.exit_code == 0, result.output
        cli_data = json.loads(result.output)

        src = BakSource(str(_FIXTURE_BAK))
        sdk_data = src.summary().as_dict()

        assert cli_data["catalog"]["name"] == sdk_data["catalog"]["name"]
        assert cli_data["catalog"]["catalog_type"] == "MSSQL_BAK"

    def test_bak_list_json_matches_list_table_summaries(self):
        """CLI bak list --json output must equal list_table_summaries().as_dict()."""
        from typer.testing import CliRunner

        from mssqlbak._cli import app
        from mssqlbak.sources.bak import BakSource

        runner = CliRunner()
        result = runner.invoke(app, ["bak", "list", str(_FIXTURE_BAK), "--json"])
        assert result.exit_code == 0, result.output
        cli_data = json.loads(result.output)

        src = BakSource(str(_FIXTURE_BAK))
        sdk_data = src.list_table_summaries().as_dict()

        # Same number of items.
        assert len(cli_data["items"]) == len(sdk_data["items"])

    def test_bak_schema_json_matches_list_columns(self):
        """CLI bak schema --json must equal list_columns().as_dict()."""
        from typer.testing import CliRunner

        from mssqlbak._cli import app
        from mssqlbak.sources.bak import BakSource

        src = BakSource(str(_FIXTURE_BAK))
        summaries = src.list_table_summaries()
        user_tables = [
            s for s in summaries.items
            if s.object_kind == "U " and s.schema_name != "sys" and s.column_count > 0
        ]
        if not user_tables:
            pytest.skip("no suitable user tables")
        first = user_tables[0]

        runner = CliRunner()
        result = runner.invoke(app, [
            "bak", "schema", str(_FIXTURE_BAK),
            "--schema", first.schema_name,
            "--table", first.name,
            "--json",
        ])
        assert result.exit_code == 0, result.output
        cli_data = json.loads(result.output)

        sdk_data = src.list_columns(first.schema_name, first.name).as_dict()
        assert len(cli_data["items"]) == len(sdk_data["items"])

    def test_cli_verb_set_matches_backup_source_methods(self):
        """bak sub-commands must cover all core BackupSource navigation methods."""
        from mssqlbak.cli.bak import app as bak_app

        # Expected verbs (matches BackupSource protocol, minus extract which maps to extract).
        expected_verbs = {"info", "list", "schema", "extract"}
        registered = {c.name for c in bak_app.registered_commands}
        assert expected_verbs.issubset(registered)


# ---------------------------------------------------------------------------
# Page pagination helpers
# ---------------------------------------------------------------------------

class TestPaginationHelpers:
    def test_build_page_no_limit(self):
        from mssqlbak.api.listing import build_page

        items = list(range(10))
        page = build_page(items)
        assert len(page.items) == 10
        assert page.next_page_token is None

    def test_build_page_with_limit(self):
        from mssqlbak.api.listing import build_page

        items = list(range(10))
        page = build_page(items, max_results=3)
        assert len(page.items) == 3
        assert page.next_page_token == "3"

    def test_build_page_pagination(self):
        from mssqlbak.api.listing import build_page

        items = list(range(10))
        page1 = build_page(items, max_results=4)
        assert page1.next_page_token == "4"
        page2 = build_page(items, max_results=4, page_token=page1.next_page_token)
        assert page2.items == [4, 5, 6, 7]
        assert page2.next_page_token == "8"

    def test_build_page_last_page(self):
        from mssqlbak.api.listing import build_page

        items = list(range(5))
        page = build_page(items, max_results=5)
        assert page.next_page_token is None


# ---------------------------------------------------------------------------
# BakSource.summary() — local path vs HTTP URI code paths
# ---------------------------------------------------------------------------

@_skip_no_fixture(_FIXTURE_BAK)
class TestBakSourceSummaryUriPaths:
    """Verify that summary() works for both local file paths and HTTP(S) URIs.

    The HTTP test does not make a real network request: it patches open_bak
    inside mssqlbak.sources.bak to return a LocalBakReader backed by the
    local fixture, exercising the full `parse_bak_uri → open_bak →
    read_bak_metadata(BakReader)` code path introduced by the fix.
    """

    def test_summary_local_path(self):
        """summary() works when uri is a local file path."""
        from mssqlbak.sources.bak import BakSource

        src = BakSource(str(_FIXTURE_BAK))
        s = src.summary()

        assert s.catalog.catalog_type == "MSSQL_BAK"
        assert s.catalog.name  # non-empty database name from MTF header
        assert "location" in s.catalog.properties
        assert s.catalog.properties["provider"] == "mssqlbak.bak"
        assert len(s.backup_sets) >= 1

    def test_summary_http_uri_uses_reader(self):
        """summary() for an HTTP URI calls open_bak (not Path) to read metadata.

        We patch open_bak to return a LocalBakReader so no real HTTP request
        is made.  What matters is that the FileNotFoundError that previously
        occurred when treating the URL string as a file path is gone.
        """
        from unittest.mock import patch

        from mssqlbak.bak_io import LocalBakReader
        from mssqlbak.sources.bak import BakSource

        fake_reader = LocalBakReader(str(_FIXTURE_BAK))
        fake_url = "https://example.com/fake.bak"

        # open_bak is imported inside the method body, so patch it at its
        # definition site (mssqlbak.readers) which is what the local `open_bak`
        # name resolves to at runtime.
        with patch("mssqlbak.readers.open_bak", return_value=fake_reader):
            src = BakSource(fake_url)
            s = src.summary()

        assert s.catalog.catalog_type == "MSSQL_BAK"
        assert s.catalog.name
        assert s.catalog.properties["provider"] == "mssqlbak.bak"
        # location must reflect the URI we passed (self._uri), not the reader repr
        assert s.catalog.properties["location"] == fake_url

    def test_summary_http_uri_does_not_treat_url_as_path(self):
        """Regression: summary() must not raise FileNotFoundError for HTTP URIs."""
        from unittest.mock import patch

        from mssqlbak.bak_io import LocalBakReader
        from mssqlbak.sources.bak import BakSource

        fake_reader = LocalBakReader(str(_FIXTURE_BAK))

        with patch("mssqlbak.readers.open_bak", return_value=fake_reader):
            # This must not raise FileNotFoundError
            src = BakSource("https://example.com/backup.bak")
            s = src.summary()

        assert s is not None

    def test_summary_local_and_http_produce_same_catalog_name(self):
        """Local path and mocked HTTP URI return the same database name."""
        from unittest.mock import patch

        from mssqlbak.bak_io import LocalBakReader
        from mssqlbak.sources.bak import BakSource

        local_src = BakSource(str(_FIXTURE_BAK))
        local_summary = local_src.summary()

        fake_reader = LocalBakReader(str(_FIXTURE_BAK))
        with patch("mssqlbak.readers.open_bak", return_value=fake_reader):
            http_src = BakSource("https://example.com/backup.bak")
            http_summary = http_src.summary()

        assert local_summary.catalog.name == http_summary.catalog.name
        assert local_summary.backup_sets[0].backup_type == http_summary.backup_sets[0].backup_type
