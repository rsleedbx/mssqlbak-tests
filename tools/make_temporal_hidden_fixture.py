#!/usr/bin/env python3
"""Generate ``temporal_hidden_full.bak`` — is_hidden temporal period column fixture.

Purpose
-------
Provides a minimal fixture whose sole goal is to let the V13 ``is_hidden``
probe (`make_v13_hidden_probe.py`) identify the exact ``syscolpars.status``
bit position for ``is_hidden``.

The fixture contains two structurally identical system-versioned temporal
tables that differ only in the presence of the ``HIDDEN`` keyword on their
period columns:

* ``dbo.temporal_hidden``  — period columns declared ``GENERATED ALWAYS AS
  ROW START HIDDEN``.  ``sys.columns.is_hidden = 1`` for these columns.

* ``dbo.temporal_visible`` — period columns declared ``GENERATED ALWAYS AS
  ROW START`` (no ``HIDDEN``).  ``sys.columns.is_hidden = 0``.

By XOR-ing the raw ``syscolpars.status`` of the two matching period columns
the probe can isolate the exact bit(s) that encode ``is_hidden``.

Each table ships with 5 rows (plus 2 updated rows in the corresponding
history table) so that ``register_bak`` produces non-trivial ground-truth
stats.

Requirements
------------
* SQL Server 2016 or later (``HIDDEN`` keyword on period columns requires
  SS2016+; ledger/graph require SS2022 but are NOT used here).
* This fixture is SS2016+ compatible and belongs in ``fixtures_2022/``
  by convention (SS2022 is the standard native format).

Run via::

    FIXTURE_DIR=tests/fixtures_2022 python -m tools.fixture_run temporal-hidden
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

DB_NAME = "TemporalHidden"
REPO_ROOT = Path(__file__).resolve().parent.parent
_raw_fixture_dir = os.environ.get("FIXTURE_DIR", "")
if _raw_fixture_dir:
    _fd = Path(_raw_fixture_dir)
    FIXTURE_DIR = _fd if _fd.is_absolute() else (REPO_ROOT / _fd).resolve()
else:
    FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures_2022"

CONTAINER_BAK = f"/tmp/{DB_NAME.lower()}_full.bak"
CONTAINER_SQL = f"/tmp/load_{DB_NAME.lower()}.sql"


def _out_path() -> Path:
    return FIXTURE_DIR / "temporal_hidden_full.bak"


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

-- ----------------------------------------------------------------
-- temporal_hidden / temporal_hidden_history
--   Period columns carry the HIDDEN keyword.
--   sys.columns.is_hidden = 1 for valid_from / valid_to.
-- ----------------------------------------------------------------
CREATE TABLE [dbo].[temporal_hidden] (
    id         INT            NOT NULL,
    value      NVARCHAR(50)   NULL,
    valid_from DATETIME2(7)   GENERATED ALWAYS AS ROW START HIDDEN NOT NULL,
    valid_to   DATETIME2(7)   GENERATED ALWAYS AS ROW END   HIDDEN NOT NULL,
    PERIOD FOR SYSTEM_TIME (valid_from, valid_to),
    CONSTRAINT pk_temporal_hidden PRIMARY KEY CLUSTERED (id)
) WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.temporal_hidden_history));
GO

INSERT INTO [dbo].[temporal_hidden] (id, value) VALUES
    (1, N'alpha'),
    (2, N'beta'),
    (3, N'gamma'),
    (4, N'delta'),
    (5, N'epsilon');
GO

-- Update rows 1 and 2 so the history table gets some rows too.
UPDATE [dbo].[temporal_hidden] SET value = N'alpha_v2'  WHERE id = 1;
UPDATE [dbo].[temporal_hidden] SET value = N'beta_v2'   WHERE id = 2;
GO

-- ----------------------------------------------------------------
-- temporal_visible / temporal_visible_history
--   Identical structure, but period columns have NO HIDDEN keyword.
--   sys.columns.is_hidden = 0 for valid_from / valid_to.
--   Side-by-side comparison with temporal_hidden exposes the bit.
-- ----------------------------------------------------------------
CREATE TABLE [dbo].[temporal_visible] (
    id         INT            NOT NULL,
    value      NVARCHAR(50)   NULL,
    valid_from DATETIME2(7)   GENERATED ALWAYS AS ROW START NOT NULL,
    valid_to   DATETIME2(7)   GENERATED ALWAYS AS ROW END   NOT NULL,
    PERIOD FOR SYSTEM_TIME (valid_from, valid_to),
    CONSTRAINT pk_temporal_visible PRIMARY KEY CLUSTERED (id)
) WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.temporal_visible_history));
GO

INSERT INTO [dbo].[temporal_visible] (id, value) VALUES
    (1, N'alpha'),
    (2, N'beta'),
    (3, N'gamma'),
    (4, N'delta'),
    (5, N'epsilon');
GO

UPDATE [dbo].[temporal_visible] SET value = N'alpha_v2'  WHERE id = 1;
UPDATE [dbo].[temporal_visible] SET value = N'beta_v2'   WHERE id = 2;
GO

USE [master];
GO
BACKUP DATABASE [{DB_NAME}] TO DISK=N'{CONTAINER_BAK}' WITH FORMAT, INIT;
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
