"""Phase F tests for mssqlbak.perf and mssqlbak.profiler_duckdb.

Tests cover:
  A. Phase A resolver: resolve_internal_table_page returns None gracefully for
     absent internal tables (all existing fixtures pre-date Query Store).
  B. recover_perf runs without error on any fixture and returns a PerfData with
     correct types.
  C. recover_statistics returns list[Statistic] with plausible contents.
  D. emit_perf_scripts writes a perf.json manifest and T-SQL script files.
  E. emit_perf_tabular returns Arrow tables with the correct column names.
  F. emit_profiler_extract writes a .db file that (a) exists, (b) is queryable
     with duckdb, (c) has every profiler-parity table, (d) tables/columns counts
     match recovered catalog counts.
  G. profiler DDL schema guard: the vendored *_ddl.sql file column names match
     the Arrow table columns produced by the builders.

Tests use the smallest available real fixture (alias_types_full.bak 2.6 MB)
so they complete quickly without downloading large files.
"""
from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pytest

# Fixtures path (relative to this file).
_FIXTURES_2017 = Path(__file__).parent / "fixtures_2017"
_SMALL_BAK = _FIXTURES_2017 / "alias_types_full.bak"

# Skip all tests in this module when the fixture doesn't exist.
pytestmark = pytest.mark.skipif(
    not _SMALL_BAK.exists(),
    reason=f"fixture not found: {_SMALL_BAK}",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_store(bak: Path):
    from mssqlbak.pages import PageStore
    return PageStore.from_bak(str(bak), catalog_only=True)


# ---------------------------------------------------------------------------
# Phase A — resolver
# ---------------------------------------------------------------------------

class TestSysobjResolver:
    def test_absent_internal_table_returns_none(self):
        from mssqlbak.catalog.recover import resolve_internal_table_page
        store = _open_store(_SMALL_BAK)
        page = resolve_internal_table_page(store, "plan_persist_query_text")
        # All pre-QS fixtures don't have this table; should return None cleanly.
        assert page is None

    def test_absent_returns_empty_rows(self):
        from mssqlbak.catalog.recover import resolve_internal_table_rows
        from mssqlbak.catalog.columns import _layout
        store = _open_store(_SMALL_BAK)
        cols = _layout([("id", "int")])
        rows = resolve_internal_table_rows(store, "plan_persist_query_text", cols)
        assert rows == []

    def test_existing_table_returns_page(self):
        """sysschobjs exists in every .bak; verify the resolver finds it by name."""
        from mssqlbak.catalog.recover import resolve_internal_table_page
        store = _open_store(_SMALL_BAK)
        # sysschobjs is at fixed objid 34, but also resolvable by name.
        page = resolve_internal_table_page(store, "sysschobjs")
        assert page is not None
        assert page > 0


# ---------------------------------------------------------------------------
# Phase B — statistics recovery
# ---------------------------------------------------------------------------

class TestStatisticsRecovery:
    def test_recover_statistics_returns_list(self):
        from mssqlbak.perf import recover_statistics
        store = _open_store(_SMALL_BAK)
        stats = recover_statistics(store)
        assert isinstance(stats, list)

    def test_statistics_have_valid_fields(self):
        from mssqlbak.perf import recover_statistics
        from mssqlbak.catalog.model import Statistic
        store = _open_store(_SMALL_BAK)
        stats = recover_statistics(store)
        # Auto-statistics are created for every indexed column; should be non-empty.
        assert len(stats) > 0
        for s in stats:
            assert isinstance(s, Statistic)
            assert s.name
            assert s.object_id > 0
            assert s.stat_id > 0
            assert isinstance(s.auto_created, bool)
            assert isinstance(s.no_recompute, bool)
            assert isinstance(s.key_column_ids, list)
            assert isinstance(s.histogram, list)

    def test_statistics_key_column_ids_are_ints(self):
        from mssqlbak.perf import recover_statistics
        store = _open_store(_SMALL_BAK)
        for s in recover_statistics(store):
            for cid in s.key_column_ids:
                assert isinstance(cid, int)


# ---------------------------------------------------------------------------
# Phase C — plan guide recovery
# ---------------------------------------------------------------------------

class TestPlanGuideRecovery:
    def test_recover_plan_guides_returns_list(self):
        from mssqlbak.perf import recover_plan_guides
        store = _open_store(_SMALL_BAK)
        guides = recover_plan_guides(store)
        assert isinstance(guides, list)
        # This fixture has no plan guides; that's fine.

    def test_emit_plan_guide_script_format(self):
        from mssqlbak.perf import emit_plan_guide_script
        from mssqlbak.catalog.model import PlanGuide
        pg = PlanGuide(
            name="guide1",
            scope_type=2,
            scope_type_desc="SQL",
            query_text="SELECT 1",
            hints="OPTION (MAXDOP 1)",
        )
        script = emit_plan_guide_script(pg)
        assert "sp_create_plan_guide" in script
        assert "@name = N'guide1'" in script
        assert "@stmt = N'SELECT 1'" in script
        assert "@hints = N'OPTION (MAXDOP 1)'" in script
        assert "@type = N'SQL'" in script


# ---------------------------------------------------------------------------
# Phase D — Query Store recovery
# ---------------------------------------------------------------------------

class TestQueryStoreRecovery:
    def test_recover_query_store_returns_qs_data(self):
        from mssqlbak.perf import recover_query_store
        from mssqlbak.catalog.model import QueryStoreData
        store = _open_store(_SMALL_BAK)
        qs = recover_query_store(store)
        assert isinstance(qs, QueryStoreData)

    def test_query_store_disabled_on_pre_qs_fixture(self):
        from mssqlbak.perf import recover_query_store
        store = _open_store(_SMALL_BAK)
        qs = recover_query_store(store)
        # alias_types fixture doesn't have QS; enabled should be False.
        assert not qs.enabled
        assert qs.query_texts == []
        assert qs.queries == []
        assert qs.plans == []

    def test_emit_qs_settings_script(self):
        from mssqlbak.perf import emit_qs_settings_script
        from mssqlbak.catalog.model import QueryStoreOptions
        opts = QueryStoreOptions(
            desired_state=2,
            desired_state_desc="READ_WRITE",
            max_storage_size_mb=200,
            stale_query_threshold_days=14,
        )
        sql = emit_qs_settings_script(opts, "TestDB")
        assert "ALTER DATABASE [TestDB]" in sql
        assert "QUERY_STORE = ON" in sql
        assert "MAX_STORAGE_SIZE_MB = 200" in sql
        assert "STALE_QUERY_THRESHOLD_DAYS = 14" in sql


# ---------------------------------------------------------------------------
# Phase E — PerfData orchestrator
# ---------------------------------------------------------------------------

class TestRecoverPerf:
    def test_recover_perf_returns_perf_data(self):
        from mssqlbak.perf import recover_perf, PerfData
        store = _open_store(_SMALL_BAK)
        perf = recover_perf(store)
        assert isinstance(perf, PerfData)
        assert isinstance(perf.statistics, list)
        assert isinstance(perf.plan_guides, list)

    def test_emit_perf_scripts_writes_manifest(self, tmp_path: Path):
        from mssqlbak.perf import recover_perf, emit_perf_scripts
        store = _open_store(_SMALL_BAK)
        perf = recover_perf(store)
        written = emit_perf_scripts(perf, db_name="TestDB", out_dir=tmp_path)
        # Manifest is always written.
        manifest_path = tmp_path / "TestDB.perf.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest["db"] == "TestDB"
        assert "objects" in manifest
        assert manifest_path in written

    def test_emit_perf_tabular_returns_arrow_tables(self):
        from mssqlbak.perf import recover_perf, emit_perf_tabular
        store = _open_store(_SMALL_BAK)
        perf = recover_perf(store)
        tables = emit_perf_tabular(perf)
        assert isinstance(tables, dict)
        # All expected table names must be present.
        expected = {
            "statistics", "statistics_histogram", "plan_guides",
            "query_store_options", "query_store_query_text",
            "query_store_query", "query_store_plan",
            "query_store_runtime_stats", "query_store_wait_stats",
            "query_store_forced_plans",
        }
        assert expected.issubset(tables.keys())
        for name, tbl in tables.items():
            assert isinstance(tbl, pa.Table), f"{name} is not a pa.Table"

    def test_statistics_tabular_columns(self):
        from mssqlbak.perf import recover_perf, emit_perf_tabular
        store = _open_store(_SMALL_BAK)
        perf = recover_perf(store)
        tables = emit_perf_tabular(perf)
        stat_tbl = tables["statistics"]
        expected_cols = {
            "stat_name", "table_schema", "table_name", "stat_id",
            "auto_created", "no_recompute", "filter_definition",
            "rows_sampled", "rows_in_table", "has_stats_stream",
        }
        assert expected_cols.issubset(set(stat_tbl.column_names))

    def test_statistics_rows_match_recover_statistics(self):
        from mssqlbak.perf import recover_perf, emit_perf_tabular, recover_statistics
        store = _open_store(_SMALL_BAK)
        perf = recover_perf(store)
        tables = emit_perf_tabular(perf)
        stat_tbl = tables["statistics"]
        direct_stats = recover_statistics(store)
        assert len(stat_tbl) == len(direct_stats)


# ---------------------------------------------------------------------------
# Phase G — Profiler DuckDB extract
# ---------------------------------------------------------------------------

class TestProfilerDuckDB:
    def test_emit_profiler_extract_creates_db(self, tmp_path: Path):
        from mssqlbak.profiler_duckdb import emit_profiler_extract
        store = _open_store(_SMALL_BAK)
        db_path = emit_profiler_extract(
            store,
            out=tmp_path / "test_extract.db",
            db_name="TestDB",
            with_perf=False,
        )
        assert db_path.exists()
        assert db_path.suffix == ".db"

    def test_db_is_queryable_with_duckdb(self, tmp_path: Path):
        import duckdb
        from mssqlbak.profiler_duckdb import emit_profiler_extract
        store = _open_store(_SMALL_BAK)
        db_path = emit_profiler_extract(
            store, out=tmp_path / "q.db", db_name="TestDB"
        )
        con = duckdb.connect(str(db_path))
        tables = con.execute("SHOW TABLES").fetchall()
        table_names = {t[0] for t in tables}
        con.close()
        # Core profiler tables must be present.
        for name in ("databases", "tables", "columns", "views", "routines", "indexed_views",
                     "db_sizes", "table_sizes", "query_stats", "proc_stats"):
            assert name in table_names, f"missing table: {name}"

    def test_databases_table_has_one_row(self, tmp_path: Path):
        import duckdb
        from mssqlbak.profiler_duckdb import emit_profiler_extract
        store = _open_store(_SMALL_BAK)
        db_path = emit_profiler_extract(
            store, out=tmp_path / "d.db", db_name="MyDB"
        )
        con = duckdb.connect(str(db_path))
        rows = con.execute("SELECT NAME FROM databases").fetchall()
        con.close()
        assert len(rows) == 1
        assert rows[0][0] == "MyDB"

    def test_tables_count_matches_catalog(self, tmp_path: Path):
        import duckdb
        from mssqlbak.profiler_duckdb import emit_profiler_extract
        from mssqlbak.catalog.recover import recover_schema
        store = _open_store(_SMALL_BAK)
        sch = recover_schema(store)
        expected_count = len(sch.tables)

        db_path = emit_profiler_extract(
            store, out=tmp_path / "t.db", db_name="TestDB"
        )
        con = duckdb.connect(str(db_path))
        row = con.execute("SELECT COUNT(*) FROM tables").fetchone()
        con.close()
        assert row is not None
        assert row[0] == expected_count

    def test_columns_count_matches_catalog(self, tmp_path: Path):
        import duckdb
        from mssqlbak.profiler_duckdb import emit_profiler_extract
        from mssqlbak.catalog.recover import recover_schema
        store = _open_store(_SMALL_BAK)
        sch = recover_schema(store)
        expected_count = sum(len(t.columns) for t in sch.tables)

        db_path = emit_profiler_extract(
            store, out=tmp_path / "c.db", db_name="TestDB"
        )
        con = duckdb.connect(str(db_path))
        row = con.execute("SELECT COUNT(*) FROM columns").fetchone()
        con.close()
        assert row is not None
        assert row[0] == expected_count

    def test_with_perf_adds_extra_tables(self, tmp_path: Path):
        import duckdb
        from mssqlbak.profiler_duckdb import emit_profiler_extract
        store = _open_store(_SMALL_BAK)
        db_path = emit_profiler_extract(
            store, out=tmp_path / "p.db", db_name="TestDB", with_perf=True
        )
        con = duckdb.connect(str(db_path))
        tables = {t[0] for t in con.execute("SHOW TABLES").fetchall()}
        con.close()
        perf_tables = {
            "statistics", "statistics_histogram", "plan_guides",
            "query_store_options", "query_store_query_text",
            "query_store_plan", "query_store_runtime_stats",
        }
        assert perf_tables.issubset(tables)

    def test_columns_table_has_correct_schema_columns(self, tmp_path: Path):
        """Column names in the DuckDB 'columns' table match the vendored DDL."""
        import duckdb
        from mssqlbak.profiler_duckdb import emit_profiler_extract, _load_ddl
        store = _open_store(_SMALL_BAK)
        db_path = emit_profiler_extract(
            store, out=tmp_path / "col.db", db_name="TestDB"
        )
        con = duckdb.connect(str(db_path))
        desc = con.execute("DESCRIBE columns").fetchall()
        actual_col_names = {row[0].upper() for row in desc}
        con.close()

        # Parse expected column names from the vendored DDL.
        ddl = _load_ddl("columns") or ""
        expected = set()
        for line in ddl.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith(("CREATE", ")")):
                col_name = stripped.split()[0].upper().rstrip(",")
                if col_name:
                    expected.add(col_name)

        # All DDL-declared columns must be present.
        assert expected.issubset(actual_col_names), (
            f"missing columns: {expected - actual_col_names}"
        )

    def test_default_out_dir_creates_dated_filename(self, tmp_path: Path):
        from mssqlbak.profiler_duckdb import emit_profiler_extract
        store = _open_store(_SMALL_BAK)
        db_path = emit_profiler_extract(store, out=tmp_path, db_name="TestDB")
        # Should be named profiler_extract_mssql_<ver>_<YYYYMMDD>.db
        assert db_path.name.startswith("profiler_extract_mssql_")
        assert db_path.suffix == ".db"
        assert db_path.exists()


class TestSinglePassExtraction:
    """extract_bak emits data + perf artifacts + profiler DB in one PageStore pass."""

    def test_single_pass_produces_all_outputs(self, tmp_path: Path):
        """
        Run extract_bak with emit_perf + emit_profiler specs on the small fixture
        and assert that:
          - delta sink tables are written
          - report.perf_artifacts is non-empty and perf.json exists
          - report.profiler_db points to an existing .db file
        All from a single extract_bak call.
        """
        import duckdb
        from mssqlbak.extract import extract_bak
        from mssqlbak.perf import PerfEmitSpec
        from mssqlbak.profiler_duckdb import ProfilerEmitSpec
        from mssqlbak.sink import DeltaSink

        delta_dir = tmp_path / "delta"
        perf_dir = tmp_path / "perf"
        profiler_db = tmp_path / "extract.db"

        sink = DeltaSink(str(delta_dir))
        report = extract_bak(
            str(_SMALL_BAK),
            sink,
            emit_perf=PerfEmitSpec(out_dir=perf_dir, fmt="both", db_name="TestDB"),
            emit_profiler=ProfilerEmitSpec(
                out_path=profiler_db, with_perf=True, db_name="TestDB"
            ),
        )

        # Data extraction succeeded.
        assert report.extracted, "expected at least one extracted table"

        # Perf artifacts were written.
        assert report.perf_artifacts, "expected non-empty perf_artifacts on report"
        # emit_perf_scripts writes <db_name>.perf.json
        manifest = perf_dir / "TestDB.perf.json"
        assert manifest.exists(), f"perf manifest not found at {manifest}"

        # Profiler DB was written.
        assert report.profiler_db is not None, "expected profiler_db path on report"
        assert report.profiler_db.exists(), f"profiler DB not found at {report.profiler_db}"

        # DuckDB file is queryable.
        con = duckdb.connect(str(report.profiler_db))
        tables = {t[0] for t in con.execute("SHOW TABLES").fetchall()}
        con.close()
        assert "databases" in tables
        assert "tables" in tables
        assert "statistics" in tables  # perf-extra table included via with_perf=True
