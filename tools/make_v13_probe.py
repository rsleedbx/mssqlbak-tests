#!/usr/bin/env python3
"""V13 syscolpars probe — generated_always_type / is_hidden status bits.

Two-phase probe:

Phase A — ``WideWorldImporters-Standard.bak`` (realworld fixture, SS2019
originally):  shows that archive-table period columns are NOT hidden and NOT
generated_always after restore to SS2022.  Confirms the 14/14 column count is
correct and that V13 is about ``generated_always_type`` metadata, not hidden
columns.

Phase B — ``featurecoverage_full.bak`` (SS2022 native): restores a small
fixture whose ``temporal_current`` table has period columns with
``generated_always_type 1/2`` (AS_ROW_START / AS_ROW_END).  Queries
``sys.syscolpars`` directly (accessible since the DB was created natively on
SS2022) to find the raw ``status`` hex for those columns, thereby identifying
which bit(s) encode ``generated_always_type`` and ``is_hidden`` in the 4-byte
``syscolpars.status`` integer.

Results written to ``tests/fixtures_realworld/V13_probe_results.txt``.

Run via the standard toolchain:

    FIXTURE_DIR=tests/fixtures_2022 python -m tools.fixture_run v13-probe
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import (  # noqa: E402
    _run_sql,
    fixture_credentials,
    sqlcmd_base,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# SQL: restore WideWorldImporters-Standard.bak, then probe syscolpars
# ---------------------------------------------------------------------------

_SQL_V13 = r"""
SET NOCOUNT ON;
GO

IF DB_ID(N'V13Probe') IS NOT NULL BEGIN
    ALTER DATABASE [V13Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V13Probe];
END;
GO

RESTORE DATABASE [V13Probe]
    FROM DISK = N'/tmp/WideWorldImporters-Standard.bak'
    WITH MOVE N'WWI_Primary'    TO N'/tmp/V13Probe.mdf',
         MOVE N'WWI_UserData'   TO N'/tmp/V13Probe_UserData.ndf',
         MOVE N'WWI_Log'        TO N'/tmp/V13Probe.ldf',
         REPLACE, RECOVERY;
GO

USE [V13Probe];
GO

DBCC TRACEON(3604);
GO

-- ----------------------------------------------------------------
-- 1.  sys.columns metadata for Application.Countries_Archive
--     showing is_hidden and generated_always_type for each column.
-- ----------------------------------------------------------------
PRINT '=== SYS.COLUMNS for Application.Countries_Archive ===';
SELECT
    c.column_id,
    c.name,
    c.system_type_id,
    c.is_hidden,
    c.generated_always_type,
    c.generated_always_type_desc,
    c.is_nullable
FROM sys.columns c
WHERE c.object_id = OBJECT_ID(N'Application.Countries_Archive')
ORDER BY c.column_id;
GO

-- ----------------------------------------------------------------
-- 2.  Raw syscolpars status values — compare hidden vs. normal cols.
--     sys.syscolpars may not be accessible in all compat levels;
--     use OPENROWSET as an alternative to read it as a heap.
-- ----------------------------------------------------------------
PRINT '=== RAW syscolpars status (hex) for Application.Countries_Archive ===';

-- Attempt via sys.syscolpars (may fail on older compat levels):
BEGIN TRY
    DECLARE @sql NVARCHAR(MAX) = N'
    SELECT
        cp.colid,
        cp.name,
        CONVERT(VARCHAR(20), CONVERT(VARBINARY(4), cp.status), 1) AS status_hex,
        cp.status AS status_dec
    FROM sys.syscolpars cp
    WHERE cp.id = OBJECT_ID(N''Application.Countries_Archive'')
      AND cp.number = 0
    ORDER BY cp.colid;';
    EXEC sp_executesql @sql;
END TRY
BEGIN CATCH
    PRINT 'sys.syscolpars not accessible: ' + ERROR_MESSAGE();
END CATCH;
GO

-- Also compare the current table (Application.Countries) — it has hidden period columns.
PRINT '=== SYS.COLUMNS for Application.Countries (current temporal table) ===';
SELECT
    c.column_id,
    c.name,
    c.system_type_id,
    c.is_hidden,
    c.generated_always_type,
    c.generated_always_type_desc,
    c.is_nullable
FROM sys.columns c
WHERE c.object_id = OBJECT_ID(N'Application.Countries')
ORDER BY c.column_id;
GO

-- ----------------------------------------------------------------
-- 3.  sys.periods — confirm period column ids for the archive table.
-- ----------------------------------------------------------------
PRINT '=== SYS.PERIODS for Application.Countries_Archive ===';
SELECT
    p.period_type,
    p.period_type_desc,
    p.start_column_id,
    p.end_column_id,
    p.start_column_name,
    p.end_column_name
FROM sys.periods p
WHERE p.object_id = OBJECT_ID(N'Application.Countries_Archive');
GO

-- Also check the non-archive (current) table:
PRINT '=== SYS.PERIODS for Application.Countries (current table) ===';
SELECT
    p.period_type,
    p.period_type_desc,
    p.start_column_id,
    p.end_column_id,
    p.start_column_name,
    p.end_column_name
FROM sys.periods p
WHERE p.object_id = OBJECT_ID(N'Application.Countries');
GO

-- ----------------------------------------------------------------
-- 4.  DBCC PAGE on the syscolpars page that contains the hidden
--     period column rows.  We need to locate which page holds the
--     Countries_Archive rows (object_id × colid 13/14).
-- ----------------------------------------------------------------
PRINT '=== DBCC PAGE for syscolpars rows of Countries_Archive ===';

DECLARE @db     SYSNAME = N'V13Probe';
DECLARE @obj_id INT     = OBJECT_ID(N'Application.Countries_Archive');

-- Locate the data pages for syscolpars (objid 41) that contain the
-- relevant rows using dm_db_database_page_allocations.
DECLARE @file_id INT, @page_id INT;

-- Find which page holds the ValidFrom/ValidTo rows for Countries_Archive.
-- Use DBCC IND to get all pages for syscolpars, then inspect.
-- Since syscolpars is small, dump the first data page.
SELECT TOP 1
    @file_id = allocated_page_file_id,
    @page_id  = allocated_page_page_id
FROM sys.dm_db_database_page_allocations(
    DB_ID(N'V13Probe'), 41 /*syscolpars*/, 1 /*index_id*/, NULL, N'LIMITED'
)
WHERE page_type_desc = N'DATA_PAGE'
ORDER BY allocated_page_page_id;

PRINT 'syscolpars first data page: file=' + CAST(@file_id AS VARCHAR) + ' page=' + CAST(@page_id AS VARCHAR);
DBCC PAGE(V13Probe, @file_id, @page_id, 3);
GO

-- ----------------------------------------------------------------
-- 5.  Confirm syscolpars rows with number != 0 for Countries_Archive
--     (stored proc parameter rows) — should be none for a table.
-- ----------------------------------------------------------------
PRINT '=== syscolpars rows with number != 0 for Countries_Archive ===';
SELECT cp.colid, cp.number, cp.name, cp.status
FROM sys.syscolpars cp
WHERE cp.id = OBJECT_ID(N'Application.Countries_Archive')
  AND cp.number != 0;
GO

USE [master];
GO
IF DB_ID(N'V13Probe') IS NOT NULL BEGIN
    ALTER DATABASE [V13Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V13Probe];
END;
GO
"""

# Phase B: featurecoverage_full.bak — SS2022 native DB where sys.syscolpars
# is accessible. Queries the raw status bits for the temporal_current table's
# period columns to identify is_hidden / generated_always_type encoding.
_SQL_V13_PHASE_B = r"""
SET NOCOUNT ON;
GO

IF DB_ID(N'V13ProbeB') IS NOT NULL BEGIN
    ALTER DATABASE [V13ProbeB] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V13ProbeB];
END;
GO

RESTORE DATABASE [V13ProbeB]
    FROM DISK = N'/tmp/featurecoverage_full.bak'
    WITH MOVE N'FeatureCoverage'      TO N'/tmp/V13ProbeB.mdf',
         MOVE N'FeatureCoverage_mem'  TO N'/tmp/V13ProbeB_mem',
         MOVE N'FeatureCoverage_log'  TO N'/tmp/V13ProbeB.ldf',
         REPLACE, RECOVERY;
GO

USE [V13ProbeB];
GO

DBCC TRACEON(3604);
GO

-- ----------------------------------------------------------------
-- Phase B.1 — sys.columns for temporal_current
-- ----------------------------------------------------------------
PRINT '=== PHASE B: SYS.COLUMNS for dbo.temporal_current ===';
SELECT
    c.column_id,
    c.name,
    c.system_type_id,
    c.is_hidden,
    c.generated_always_type,
    c.generated_always_type_desc,
    c.is_nullable
FROM sys.columns c
WHERE c.object_id = OBJECT_ID(N'dbo.temporal_current')
ORDER BY c.column_id;
GO

-- ----------------------------------------------------------------
-- Phase B.2 — Raw syscolpars.status for temporal_current
--             Compare period columns vs non-period columns.
-- ----------------------------------------------------------------
PRINT '=== PHASE B: RAW syscolpars.status for dbo.temporal_current ===';
SELECT
    cp.colid,
    cp.name,
    CONVERT(VARCHAR(20), CONVERT(VARBINARY(4), cp.status), 1) AS status_hex,
    cp.status AS status_dec
FROM sys.syscolpars cp
WHERE cp.id = OBJECT_ID(N'dbo.temporal_current')
  AND cp.number = 0
ORDER BY cp.colid;
GO

-- ----------------------------------------------------------------
-- Phase B.3 — sys.columns for temporal_history (history table)
--             Its period columns should NOT be generated_always.
-- ----------------------------------------------------------------
PRINT '=== PHASE B: SYS.COLUMNS for dbo.temporal_history ===';
SELECT
    c.column_id,
    c.name,
    c.is_hidden,
    c.generated_always_type,
    c.generated_always_type_desc
FROM sys.columns c
WHERE c.object_id = OBJECT_ID(N'dbo.temporal_history')
ORDER BY c.column_id;
GO

-- ----------------------------------------------------------------
-- Phase B.4 — Raw syscolpars.status for temporal_history
-- ----------------------------------------------------------------
PRINT '=== PHASE B: RAW syscolpars.status for dbo.temporal_history ===';
SELECT
    cp.colid,
    cp.name,
    CONVERT(VARCHAR(20), CONVERT(VARBINARY(4), cp.status), 1) AS status_hex,
    cp.status AS status_dec
FROM sys.syscolpars cp
WHERE cp.id = OBJECT_ID(N'dbo.temporal_history')
  AND cp.number = 0
ORDER BY cp.colid;
GO

-- ----------------------------------------------------------------
-- Phase B.5 — DBCC PAGE on syscolpars for the period columns.
-- ----------------------------------------------------------------
PRINT '=== PHASE B: DBCC PAGE for syscolpars rows of temporal_current ===';

DECLARE @file_id INT, @page_id INT;
SELECT TOP 1
    @file_id = allocated_page_file_id,
    @page_id  = allocated_page_page_id
FROM sys.dm_db_database_page_allocations(
    DB_ID(N'V13ProbeB'), 41 /*syscolpars*/, 1, NULL, N'LIMITED'
)
WHERE page_type_desc = N'DATA_PAGE'
ORDER BY allocated_page_page_id;

PRINT 'syscolpars first data page: file=' + CAST(@file_id AS VARCHAR)
    + ' page=' + CAST(@page_id AS VARCHAR);
DBCC PAGE(V13ProbeB, @file_id, @page_id, 3);
GO

USE [master];
GO
IF DB_ID(N'V13ProbeB') IS NOT NULL BEGIN
    ALTER DATABASE [V13ProbeB] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V13ProbeB];
END;
GO
"""


def _run_phase(container: str, sqlcmd: list[str], sql: str, sentinel: str) -> str:
    """Run a SQL block; tolerate non-zero exit if sentinel is present."""
    try:
        return _run_sql(container, sqlcmd, sql)
    except RuntimeError as exc:
        raw = str(exc)
        if sentinel.upper() not in raw.upper():
            raise
        return raw.split("\n", 1)[1] if "\n" in raw else raw


def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing results")
    args = p.parse_args()

    # The realworld fixture directory is always fixtures_realworld/, regardless
    # of FIXTURE_DIR (which only selects the SQL Server container version).
    realworld_dir = REPO_ROOT / "tests" / "fixtures_realworld"
    fixture_2022_dir = Path(
        os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022"))
    )
    out = realworld_dir / "V13_probe_results.txt"
    if out.exists() and not args.force:
        print(f"skipping (already exists): {out}", file=sys.stderr)
        return 0

    bak_wwi = realworld_dir / "WideWorldImporters-Standard.bak"
    if not bak_wwi.exists():
        print(f"ERROR: {bak_wwi} not found", file=sys.stderr)
        return 1

    bak_feat = fixture_2022_dir / "featurecoverage_full.bak"
    if not bak_feat.exists():
        print(f"ERROR: {bak_feat} not found — run 'fixture_run feature' first", file=sys.stderr)
        return 1

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    sqlcmd = sqlcmd_base(user, password, container)

    # Phase A — WideWorldImporters-Standard.bak
    print("Phase A: copying WideWorldImporters-Standard.bak …", file=sys.stderr)
    cp = subprocess.run(
        ["podman", "cp", str(bak_wwi), f"{container}:/tmp/WideWorldImporters-Standard.bak"],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        print(f"podman cp failed: {cp.stderr}", file=sys.stderr)
        return 1
    phase_a = _run_phase(container, sqlcmd, _SQL_V13, "SYS.COLUMNS")

    # Phase B — featurecoverage_full.bak (SS2022 native)
    print("Phase B: copying featurecoverage_full.bak …", file=sys.stderr)
    cp = subprocess.run(
        ["podman", "cp", str(bak_feat), f"{container}:/tmp/featurecoverage_full.bak"],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        print(f"podman cp failed: {cp.stderr}", file=sys.stderr)
        return 1
    phase_b = _run_phase(container, sqlcmd, _SQL_V13_PHASE_B, "PHASE B")

    output = phase_a + "\n\n" + phase_b
    realworld_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(output, encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
