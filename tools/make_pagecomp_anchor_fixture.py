#!/usr/bin/env python3
"""Generate ``pagecomp_anchor_full.bak`` — PAGE-compression Compression-Info (CI)
anchor / dictionary decode fixture.

Purpose
-------
Reproduce, in a tiny controlled database, the exact PAGE-compression page layout
that real-world temporal history tables (e.g. WideWorldImporters ``*_Archive``)
use and that the parser currently mis-decodes:

* A clustered rowstore index with ``DATA_COMPRESSION = PAGE``.
* Many rows whose non-key columns hold a **single constant value** across the
  whole page.  SQL Server stores that constant once in the page **anchor record**
  inside the Compression-Info (CI) structure and marks every row column with the
  ``_CD_ZERO`` indicator ("value comes from the anchor").  This is precisely the
  pattern that produced ``editor=0`` / ``ValidFrom=0001-01-01`` instead of the
  true anchor value in WWI.

Because every constant column is a known sentinel, any anchor/dictionary decode
bug shows up immediately as a wrong min == max in the ground-truth stats:

===========  ==============================================  ============
column       value (constant unless noted)                   detects
===========  ==============================================  ============
id           1 .. N (running, the only varying column)        row count
editor       1                                                _CD_ZERO int anchor
ts           2021-06-15 12:00:00.0000000  (datetime2(7))      _CD_ZERO datetime2 anchor
ts2          2021-12-31 23:59:59.0000000  (datetime2(7))      second datetime2 anchor
amount       12.500  (decimal(18,3))                          _CD_ZERO decimal anchor
qty          7  (bigint)                                      _CD_ZERO bigint anchor
label        'COMMON_PREFIX_LABEL'  (varchar)                 short-string anchor
geo          POINT(-122.3321 47.6062)  (geography)            off-row LOB anchor / NULL
===========  ==============================================  ============

A clean round-trip (every constant column min == max == its sentinel, ``geo``
non-null for every row) means the CI anchor decode is correct.

Requirements
------------
* Any SQL Server 2016+; the fixture uses only PAGE compression + geography, no
  version-specific features, so it builds identically on 2017/2019/2022/2025 and
  belongs in every ``fixtures_<year>/`` tree (built via ``all-versions``).

Run via::

    .venv/bin/python -m tools.fixture_run all-versions --suite pagecomp-anchor
    # or one version:
    .venv/bin/python -m tools.fixture_run --fixture-dir tests/fixtures_2022 \
        --server <stem> pagecomp-anchor
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    _load_and_backup,
    fixture_credentials,
    skip_if_exists,
    sqlcmd_base,
)

DB_NAME = "PageCompAnchor"
REPO_ROOT = Path(__file__).resolve().parent.parent
_raw_fixture_dir = os.environ.get("FIXTURE_DIR", "")
if _raw_fixture_dir:
    _fd = Path(_raw_fixture_dir)
    FIXTURE_DIR = _fd if _fd.is_absolute() else (REPO_ROOT / _fd).resolve()
else:
    FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures_2022"

CONTAINER_BAK = f"/tmp/{DB_NAME.lower()}_full.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME.lower()}.sql"

# Row count: large enough to fill several PAGE-compressed pages so the CI
# anchor/dictionary structures form (compression must "pay off" per page).
ROW_COUNT = 5000

# Sentinel constants — every non-key column is constant so it collapses into the
# page anchor (rows store the _CD_ZERO indicator).  Mirror these in the test.
EDITOR = 1
TS = "2021-06-15T12:00:00.0000000"
TS2 = "2021-12-31T23:59:59.0000000"
AMOUNT = "12.500"
QTY = 7
LABEL = "COMMON_PREFIX_LABEL"
GEO_LON = -122.3321
GEO_LAT = 47.6062


def _out_path() -> Path:
    return FIXTURE_DIR / "pagecomp_anchor_full.bak"


def build_sql() -> str:
    return f"""
USE [master];
GO

IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}];
END;
GO

CREATE DATABASE [{DB_NAME}];
GO

USE [{DB_NAME}];
GO

-- Clustered rowstore, PAGE compression.  Every non-key column is a single
-- constant across all rows so it collapses into the per-page anchor record
-- (rows store the _CD_ZERO indicator).  Only `id` varies.
CREATE TABLE [dbo].[pagecomp_anchor] (
    id     INT            NOT NULL,
    editor INT            NOT NULL,
    ts     DATETIME2(7)   NOT NULL,
    ts2    DATETIME2(7)   NOT NULL,
    amount DECIMAL(18,3)  NOT NULL,
    qty    BIGINT         NOT NULL,
    label  VARCHAR(50)    NOT NULL,
    geo    GEOGRAPHY      NULL,
    CONSTRAINT pk_pagecomp_anchor PRIMARY KEY CLUSTERED (id)
) WITH (DATA_COMPRESSION = PAGE);
GO

INSERT INTO [dbo].[pagecomp_anchor] (id, editor, ts, ts2, amount, qty, label, geo)
SELECT TOP ({ROW_COUNT})
    ROW_NUMBER() OVER (ORDER BY (SELECT NULL))            AS id,
    {EDITOR}                                              AS editor,
    CAST('{TS}'  AS DATETIME2(7))                         AS ts,
    CAST('{TS2}' AS DATETIME2(7))                         AS ts2,
    CAST({AMOUNT} AS DECIMAL(18,3))                       AS amount,
    CAST({QTY} AS BIGINT)                                 AS qty,
    '{LABEL}'                                             AS label,
    geography::Point({GEO_LAT}, {GEO_LON}, 4326)          AS geo
FROM sys.all_objects a CROSS JOIN sys.all_objects b;
GO

-- Force the clustered index to (re)compress so every leaf page carries a CI.
ALTER INDEX ALL ON [dbo].[pagecomp_anchor] REBUILD
    WITH (DATA_COMPRESSION = PAGE);
GO

USE [master];
GO
BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY;
GO
"""


def main() -> int:
    import argparse as _ap

    p = _ap.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    out = _out_path()
    if skip_if_exists(out, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}", file=sys.stderr)
    sqlcmd = sqlcmd_base(user, password, container)

    _load_and_backup(container, sqlcmd, build_sql(), CONTAINER_SQL)
    size = _copy_out(container, CONTAINER_BAK, out)
    print(f"wrote {out} ({size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
