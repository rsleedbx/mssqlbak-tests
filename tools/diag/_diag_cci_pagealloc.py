#!/usr/bin/env python3
"""Run 6 (0g): live page-level ground truth for dirtycoverage_cci_delete.

Restores the .bak and queries sys.dm_db_database_page_allocations + %%physloc%%
to learn, POST-RESTORE:
  - which page ids are still allocated to dbo.dirty_cci (focus 480..700),
  - which pages the surviving delta rows (6001-7000) physically live on,
  - whether the .bak's deleted-cluster pages (685-693, ids 5001-6000) and
    survivor-cluster pages (517-523, ids 6001-7000) survive recovery.

Restore preserves page ids, so these compare directly to the offline .bak walk.
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
    db = "DiagCCIPageAlloc"
    _server, container = bootstrap_fixture_env()
    password = os.environ["FIXTURE_DBA_PASSWORD"]
    try:
        _restore_bak(container, password, bak, db)

        q_alloc = (
            f"USE [{db}]; SET NOCOUNT ON; "
            "SELECT allocated_page_page_id, page_type_desc, is_allocated, "
            "is_iam_page, page_level "
            "FROM sys.dm_db_database_page_allocations(DB_ID(), "
            f"OBJECT_ID('dbo.{TABLE}'), NULL, NULL, 'DETAILED') "
            "WHERE allocated_page_page_id BETWEEN 480 AND 700 "
            "ORDER BY allocated_page_page_id;"
        )
        print("== page allocations 480..700 (post-restore) ==")
        print(_run_sql_query(container, password, q_alloc, sep="|").rstrip())

        # Are the .bak's clusters still allocated?
        for label, lo, hi in (("survivor pages 517-523", 517, 523),
                               ("deleted pages 685-693", 685, 693)):
            q = (
                f"USE [{db}]; SET NOCOUNT ON; "
                "SELECT COUNT(*) AS allocated_data_pages "
                "FROM sys.dm_db_database_page_allocations(DB_ID(), "
                f"OBJECT_ID('dbo.{TABLE}'), NULL, NULL, 'DETAILED') "
                f"WHERE allocated_page_page_id BETWEEN {lo} AND {hi} "
                "AND is_allocated = 1 AND page_type_desc = 'DATA_PAGE';"
            )
            print(f"\n== {label}: still-allocated DATA pages ==")
            print(_run_sql_query(container, password, q, sep="|").rstrip())

        # Where do surviving rows physically live now?
        q_phys = (
            f"USE [{db}]; SET NOCOUNT ON; "
            "SELECT sys.fn_PhysLocFormatter(%%physloc%%) AS loc, id "
            f"FROM dbo.{TABLE} "
            "WHERE id IN (1, 5000, 5001, 5500, 6000, 6001, 6500, 7000) "
            "ORDER BY id;"
        )
        print("\n== physloc of sample rows (deleted ids 5001-6000 should be ABSENT) ==")
        print(_run_sql_query(container, password, q_phys, sep="|").rstrip())
    finally:
        try:
            _drop_db(container, password, db)
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
