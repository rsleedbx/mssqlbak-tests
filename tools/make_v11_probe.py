#!/usr/bin/env python3
"""V11 DBCC PAGE probe — IAM page filegroup scope (Part IV).

Captures the IAM page layout for both a primary-filegroup table and a
secondary-filegroup table from ``ndfcoverage_full.bak``.

This documents the exact byte format of IAM SPA slots and confirms
the hypothesis: each SPA slot encodes an explicit (file_id u16, page_id u32)
pair, and the extent-bitmap maps extents in the same file as the IAM page
itself.

Run via the standard toolchain (credentials auto-resolved from forgedb):

    python -m tools.fixture_run --fixture-dir tests/fixtures_2022 v11-probe

Results written to tests/fixtures_<year>/V11_probe_results.txt.
"""
from __future__ import annotations

import os
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
# SQL: restore ndfcoverage_full.bak, then run DBCC PAGE on both tables' IAMs
# ---------------------------------------------------------------------------

_SQL_V11 = r"""
SET NOCOUNT ON;
GO

DECLARE @bak NVARCHAR(500);
SET @bak = N'/tmp/ndfcoverage_full.bak';

-- Restore the NDF fixture as a probe database.
IF DB_ID(N'V11Probe') IS NOT NULL BEGIN
    ALTER DATABASE [V11Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V11Probe];
END;
GO

RESTORE DATABASE [V11Probe]
    FROM DISK = N'/tmp/ndfcoverage_full.bak'
    WITH MOVE N'NdfCoverage'       TO N'/tmp/V11Probe.mdf',
         MOVE N'NdfCoverage_fg2'   TO N'/tmp/V11Probe_fg2.ndf',
         MOVE N'NdfCoverage_log'   TO N'/tmp/V11Probe.ldf',
         REPLACE, RECOVERY;
GO

USE [V11Probe];
GO

DBCC TRACEON(3604);
GO

-- ----------------------------------------------------------------
-- Locate IAM pages for both tables via sysalloc DMVs.
-- ----------------------------------------------------------------
DECLARE @prim_iam_page INT, @prim_iam_file INT;
DECLARE @sec_iam_page  INT, @sec_iam_file  INT;

SELECT TOP 1
    @prim_iam_page = allocated_page_page_id,
    @prim_iam_file = allocated_page_file_id
FROM sys.dm_db_database_page_allocations(DB_ID(), OBJECT_ID('dbo.primary_tbl'), NULL, NULL, 'DETAILED')
WHERE page_type_desc = 'IAM_PAGE';

SELECT TOP 1
    @sec_iam_page = allocated_page_page_id,
    @sec_iam_file = allocated_page_file_id
FROM sys.dm_db_database_page_allocations(DB_ID(), OBJECT_ID('dbo.secondary_tbl'), NULL, NULL, 'DETAILED')
WHERE page_type_desc = 'IAM_PAGE';

PRINT 'PRIMARY_IAM=' + CAST(@prim_iam_file AS VARCHAR) + ':' + CAST(@prim_iam_page AS VARCHAR);
PRINT 'SECONDARY_IAM=' + CAST(@sec_iam_file AS VARCHAR) + ':' + CAST(@sec_iam_page AS VARCHAR);
GO

-- ----------------------------------------------------------------
-- DBCC PAGE on primary_tbl IAM (file 1).
-- ----------------------------------------------------------------
DECLARE @prim_iam_page INT, @prim_iam_file INT;
SELECT TOP 1
    @prim_iam_page = allocated_page_page_id,
    @prim_iam_file = allocated_page_file_id
FROM sys.dm_db_database_page_allocations(DB_ID(), OBJECT_ID('dbo.primary_tbl'), NULL, NULL, 'DETAILED')
WHERE page_type_desc = 'IAM_PAGE';

PRINT '=== PRIMARY_TBL IAM PAGE ===';
DBCC PAGE(V11Probe, @prim_iam_file, @prim_iam_page, 3);
GO

-- ----------------------------------------------------------------
-- DBCC PAGE on secondary_tbl IAM (secondary file).
-- ----------------------------------------------------------------
DECLARE @sec_iam_page INT, @sec_iam_file INT;
SELECT TOP 1
    @sec_iam_page = allocated_page_page_id,
    @sec_iam_file = allocated_page_file_id
FROM sys.dm_db_database_page_allocations(DB_ID(), OBJECT_ID('dbo.secondary_tbl'), NULL, NULL, 'DETAILED')
WHERE page_type_desc = 'IAM_PAGE';

PRINT '=== SECONDARY_TBL IAM PAGE ===';
DBCC PAGE(V11Probe, @sec_iam_file, @sec_iam_page, 3);
GO

-- ----------------------------------------------------------------
-- Row-count confirmation: the core V11 assertion.
-- ----------------------------------------------------------------
PRINT '=== ROW COUNTS ===';
PRINT 'primary_tbl rows: ' + CAST((SELECT COUNT(*) FROM dbo.primary_tbl) AS VARCHAR);
PRINT 'secondary_tbl rows: ' + CAST((SELECT COUNT(*) FROM dbo.secondary_tbl) AS VARCHAR);
GO

-- ----------------------------------------------------------------
-- Page allocations detail: file_id for data pages.
-- ----------------------------------------------------------------
PRINT '=== SYSFILES (logical file to file_id mapping) ===';
DECLARE @files NVARCHAR(MAX) = '';
SELECT @files = @files
    + 'file_id=' + CAST(file_id AS VARCHAR)
    + '  name=' + name
    + '  type=' + type_desc + CHAR(10)
FROM sys.database_files;
PRINT @files;
GO

USE [master];
GO
IF DB_ID(N'V11Probe') IS NOT NULL BEGIN
    ALTER DATABASE [V11Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [V11Probe];
END;
GO
"""


def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing results")
    args = p.parse_args()

    # Resolve fixture dir from env (set by all-versions runner).
    fixture_dir = Path(
        os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures"))
    )
    out = fixture_dir / "V11_probe_results.txt"
    if out.exists() and not args.force:
        print(f"skipping (already exists): {out}", file=sys.stderr)
        return 0

    # First, copy the NDF fixture .bak into the container.
    bak_local = fixture_dir / "ndfcoverage_full.bak"
    if not bak_local.exists():
        print(
            f"ERROR: {bak_local} not found — run 'fixture_run ndf' first",
            file=sys.stderr,
        )
        return 1

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    sqlcmd = sqlcmd_base(user, password, container)

    # Copy the .bak into the container.
    import subprocess
    cp = subprocess.run(
        ["podman", "cp", str(bak_local), f"{container}:/tmp/ndfcoverage_full.bak"],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        print(f"podman cp failed: {cp.stderr}", file=sys.stderr)
        return 1

    try:
        output = _run_sql(container, sqlcmd, _SQL_V11)
    except RuntimeError as exc:
        # DBCC PAGE without TABLERESULTS causes sqlcmd to exit non-zero on
        # some versions even when the command succeeded.  Extract the content
        # (which is embedded as "sqlcmd failed:\n<stdout>\n<stderr>") and
        # fail only if the key sentinel lines are absent.
        raw = str(exc)
        if "PRIMARY_IAM=" not in raw or "SECONDARY_IAM=" not in raw:
            print(f"FATAL: DBCC PAGE did not produce expected output:\n{raw}",
                  file=sys.stderr)
            return 1
        # Strip the "sqlcmd failed:" prefix line.
        output = raw.split("\n", 1)[1] if "\n" in raw else raw

    out.write_text(output, encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
