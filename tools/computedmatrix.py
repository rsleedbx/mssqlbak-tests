"""Computed-column matrix — isolate persisted vs non-persisted computed columns.

A computed column appears in ``syscolpars`` but only a **persisted** one has a
``sysrscols`` row (physical storage in the data record).  A non-persisted
computed column has no storage: it is absent from the record, the null bitmap,
and the variable-offset array.  Including it in the layout shifts every later
column (observed corrupting AdventureWorks ``SalesOrderHeader``).

Two tables on the same shared layout isolate the two cases:

* ``comp_nonpersisted`` — ``total AS (a + b)``            (not stored)
* ``comp_persisted``    — ``total AS (a + b) PERSISTED``  (stored)

Both have a clustered PK and identical seeded rows, so a correct parser drops
``total`` for the first table and keeps it (== a + b) for the second.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "ComputedCoverage"

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_PATH = FIXTURE_DIR / "computedcoverage_full.bak"

# Shared seeded rows: (id, a, b, label) -> total computed as a + b.
_ROWS: list[tuple[int, int, int, str]] = [
    (1, 10, 5, "alpha"),
    (2, 20, 7, "beta"),
    (3, 30, 9, "gamma"),
]


@dataclass(frozen=True)
class ComputedCase:
    name: str          # table is ``comp_<name>``
    kind: str
    computed_sql: str  # the computed-column definition
    persisted: bool


CASES: list[ComputedCase] = [
    ComputedCase("nonpersisted", "non-persisted computed column",
                 "total AS (a + b)", persisted=False),
    ComputedCase("persisted", "persisted computed column",
                 "total AS (a + b) PERSISTED", persisted=True),
]


def table_name(case: ComputedCase) -> str:
    return f"comp_{case.name}"


def stored_columns(case: ComputedCase) -> list[str]:
    """Columns a correct parser must surface, in colid order.

    ``total`` is declared between ``b`` and ``label`` (colid 4), so a persisted
    computed column appears before ``label``; a non-persisted one is absent.
    """
    return ["id", "a", "b"] + (["total"] if case.persisted else []) + ["label"]


def expected_rows(case: ComputedCase) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for rid, a, b, label in _ROWS:
        row: dict[str, object] = {"id": rid, "a": a, "b": b, "label": label}
        if case.persisted:
            row["total"] = a + b
        out.append(row)
    return out


def build_sql() -> str:
    parts: list[str] = [
        "USE [master];",
        "GO",
        f"IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN "
        f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
        f"DROP DATABASE [{DB_NAME}]; END;",
        "GO",
        f"CREATE DATABASE [{DB_NAME}];",
        "GO",
        f"USE [{DB_NAME}];",
        "GO",
        # Persisted computed columns require these ANSI settings at create time.
        "SET QUOTED_IDENTIFIER ON;",
        "SET ANSI_NULLS ON;",
        "GO",
    ]
    for case in CASES:
        tbl = table_name(case)
        parts.append(
            f"CREATE TABLE [{tbl}] (id int NOT NULL PRIMARY KEY CLUSTERED, "
            f"a int NOT NULL, b int NOT NULL, {case.computed_sql}, "
            "label nvarchar(20) NULL);"
        )
        parts.append("GO")
        for rid, a, b, label in _ROWS:
            parts.append(
                f"INSERT INTO [{tbl}] (id, a, b, label) "
                f"VALUES ({rid}, {a}, {b}, N'{label}');"
            )
        parts.append("GO")
    return "\n".join(parts) + "\n"


def main() -> int:
    from tools.make_fixture import generate_fixture

    return generate_fixture(DB_NAME, build_sql(), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
