#!/usr/bin/env python3
"""Restore dirtycoverage_cci_delete.bak to the live 2022 container and report the
authoritative post-recovery state: row count, surviving deleted ids, and
per-rowgroup deleted_rows / delta-store counts.

This is SQL Server's own recovery output — the target mssqlbak must match.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find _lib
from _lib import fixture  # noqa: E402

os.environ.setdefault("FIXTURE_DIR", "tests/fixtures_2022")

from tools.fixture_run import bootstrap_fixture_env  # noqa: E402
from tools.register_bak import _drop_db, _restore_bak, _run_sql_query  # noqa: E402

NAME = "dirtycoverage_cci_delete.bak"
TABLE = "dirty_cci"


def main() -> None:
    bak = fixture("2022", NAME)
    db = "DiagCCIDelTruth"
    _server, container = bootstrap_fixture_env()
    password = os.environ["FIXTURE_DBA_PASSWORD"]
    try:
        _restore_bak(container, password, bak, db)

        q_count = (
            f"USE [{db}]; SET NOCOUNT ON; "
            f"SELECT COUNT(*) AS total, "
            f"SUM(CASE WHEN id BETWEEN 5001 AND 6000 THEN 1 ELSE 0 END) AS deleted_range_survivors "
            f"FROM dbo.{TABLE};"
        )
        print("== row count (post-recovery) ==")
        print(_run_sql_query(container, password, q_count, sep="|").rstrip())

        q_rg = (
            f"USE [{db}]; SET NOCOUNT ON; "
            "SELECT rg.row_group_id, rg.state, rg.total_rows, rg.deleted_rows "
            "FROM sys.dm_db_column_store_row_group_physical_stats rg "
            "JOIN sys.tables t ON t.object_id = rg.object_id "
            f"WHERE t.name = '{TABLE}' ORDER BY rg.row_group_id;"
        )
        print("\n== row_group_physical_stats (state: 1=OPEN 3=COMPRESSED 4=TOMBSTONE) ==")
        print(_run_sql_query(container, password, q_rg, sep="|").rstrip())

        q_where = (
            f"USE [{db}]; SET NOCOUNT ON; "
            "SELECT CASE WHEN id<=5000 THEN '1-5000' "
            "WHEN id BETWEEN 5001 AND 6000 THEN '5001-6000' ELSE '6001-7000' END AS band, "
            "MIN(id), MAX(id), COUNT(*) "
            f"FROM dbo.{TABLE} GROUP BY CASE WHEN id<=5000 THEN '1-5000' "
            "WHEN id BETWEEN 5001 AND 6000 THEN '5001-6000' ELSE '6001-7000' END;"
        )
        print("\n== surviving id bands ==")
        print(_run_sql_query(container, password, q_where, sep="|").rstrip())

        q_phase = (
            f"USE [{db}]; SET NOCOUNT ON; "
            f"SELECT phase, COUNT(*) FROM dbo.{TABLE} GROUP BY phase ORDER BY phase;"
        )
        print("\n== rows by phase ==")
        print(_run_sql_query(container, password, q_phase, sep="|").rstrip())
    finally:
        try:
            _drop_db(container, password, db)
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
