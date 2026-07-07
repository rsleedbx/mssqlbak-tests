"""Constraint-encoding matrix — tables that isolate one constraint each.

Companion to ``tools/typematrix.py``.  Where that matrix puts one *data type*
per table, this one puts one *constraint* per table so we can positively
identify how each constraint/index is encoded in the ``.bak`` (i.e. which
``sysschobjs`` object rows, ``sysidxstats``/``sysiscols`` index rows, and
physical index pages it adds).

Isolation rule
--------------
Every table shares the **same** three columns ``(id, code, name)`` and the
**same** seeded rows, and every table has a clustered ``PRIMARY KEY`` on ``id``
so it stays row-readable by the parser.  Each table then adds *exactly one* extra
constraint on top of that baseline, so a diff of the recovered catalog between
the baseline (``cc_pk``) and any variant attributes the difference to that one
constraint.  The single exception is ``cc_pk_nonclustered`` (a heap whose PK is a
nonclustered index): it exists to observe the heap + nonclustered-PK encoding and
is excluded from row-level extraction assertions.

The rows are fixed (no RNG needed — the values are incidental; the *constraints*
are the subject), so the resulting ``.bak`` is deterministic.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "ConstraintCoverage"

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_PATH = FIXTURE_DIR / "constraintcoverage_full.bak"

# Sentinel: insert the row WITHOUT the ``name`` column so a DEFAULT fires.
USE_DEFAULT = object()

# Shared rows for every variant table: (id, code, name).  ``name`` may be the
# USE_DEFAULT sentinel (only used by the default-constraint table).
_BASE_ROWS: list[tuple[int, int, object]] = [
    (1, 10, "alpha"),
    (2, 20, "beta"),
    (3, 30, None),
]

# The FK target table holds the ids that the child's ``code`` references.
_PARENT_ROWS: list[tuple[int, int, object]] = [
    (10, 100, "p10"),
    (20, 200, "p20"),
    (30, 300, "p30"),
]

_DEFAULT_NAME = "dflt"


@dataclass(frozen=True)
class ConstraintCase:
    """One table that isolates a single constraint/index on the shared layout."""

    name: str                 # table is ``cc_<name>``
    kind: str                 # human label for the constraint under test
    # Column + inline-constraint text inside ``CREATE TABLE (...)``.
    columns_sql: str
    rows: list[tuple[int, int, object]]
    clustered: bool = True     # False => heap (nonclustered PK); catalog-only
    post_sql: list[str] = field(default_factory=list)  # CREATE INDEX, etc.
    references: str | None = None  # parent table name for a FK case
    # Hypothesis for the doc — refined after reverse-engineering the fixture.
    expected_encoding: str = ""


def _pk_cols(extra: str = "") -> str:
    base = "id int NOT NULL PRIMARY KEY CLUSTERED, code int NOT NULL, name varchar(20) NULL"
    return f"{base}{extra}"


CASES: list[ConstraintCase] = [
    ConstraintCase(
        "pk", "primary key (clustered) — baseline",
        _pk_cols(), _BASE_ROWS,
        expected_encoding="sysidxstats indid=1 (clustered); sysiscols key col=id; "
        "a 'PK' object in sysschobjs. No extra pages beyond the data rowset.",
    ),
    ConstraintCase(
        "fk_parent", "FK target (clustered PK)",
        _pk_cols(), _PARENT_ROWS,
        expected_encoding="same as cc_pk; exists to be referenced by cc_fk_child.",
    ),
    ConstraintCase(
        "pk_nonclustered", "primary key (nonclustered) → heap",
        "id int NOT NULL PRIMARY KEY NONCLUSTERED, code int NOT NULL, name varchar(20) NULL",
        _BASE_ROWS, clustered=False,
        expected_encoding="data rowset is a heap (indid=0); the PK is a separate "
        "nonclustered index (indid>1) in sysidxstats with its own B-tree pages.",
    ),
    ConstraintCase(
        "unique_constraint", "unique constraint",
        _pk_cols(", CONSTRAINT uq_code UNIQUE (code)"), _BASE_ROWS,
        expected_encoding="adds a 'UQ' object in sysschobjs plus a nonclustered "
        "unique index (sysidxstats indid>1, status unique) over code.",
    ),
    ConstraintCase(
        "unique_index", "unique index (no constraint object)",
        _pk_cols(), _BASE_ROWS,
        post_sql=["CREATE UNIQUE INDEX ix_unique_index_code ON [cc_unique_index](code);"],
        expected_encoding="a nonclustered unique index in sysidxstats/sysiscols, "
        "but NO constraint object in sysschobjs (an index is not a constraint).",
    ),
    ConstraintCase(
        "index_nonclustered", "nonclustered index (no constraint object)",
        _pk_cols(), _BASE_ROWS,
        post_sql=["CREATE INDEX ix_index_code ON [cc_index_nonclustered](code);"],
        expected_encoding="a non-unique nonclustered index in sysidxstats/sysiscols; "
        "no sysschobjs object.",
    ),
    ConstraintCase(
        "fk_child", "foreign key",
        _pk_cols(", CONSTRAINT fk_code FOREIGN KEY (code) REFERENCES [cc_fk_parent](id)"),
        _BASE_ROWS, references="cc_fk_parent",
        expected_encoding="adds an 'F' object in sysschobjs and FK column rows in the "
        "FK base table(s); no new index/pages (FK is metadata only).",
    ),
    ConstraintCase(
        "check_constraint", "check constraint",
        _pk_cols(", CONSTRAINT ck_code CHECK (code > 0)"), _BASE_ROWS,
        expected_encoding="adds a 'C' object in sysschobjs; the predicate text is "
        "stored in sysobjvalues. No index/pages.",
    ),
    ConstraintCase(
        "default_constraint", "default constraint",
        "id int NOT NULL PRIMARY KEY CLUSTERED, code int NOT NULL, "
        "name varchar(20) NULL CONSTRAINT df_name DEFAULT 'dflt'",
        [(1, 10, "alpha"), (2, 20, "beta"), (3, 30, USE_DEFAULT)],
        expected_encoding="adds a 'D' object in sysschobjs linked from syscolpars.dflt; "
        "the default expression is stored in sysobjvalues.",
    ),
]


def expected_rows(case: ConstraintCase) -> list[dict[str, object]]:
    """Canonical (id, code, name) rows a correct parser must reproduce."""
    out: list[dict[str, object]] = []
    for rid, code, name in case.rows:
        resolved = _DEFAULT_NAME if name is USE_DEFAULT else name
        out.append({"id": rid, "code": code, "name": resolved})
    return out


def table_name(case: ConstraintCase) -> str:
    return f"cc_{case.name}"


def _insert(case: ConstraintCase) -> list[str]:
    tbl = table_name(case)
    stmts: list[str] = []
    for rid, code, name in case.rows:
        if name is USE_DEFAULT:
            stmts.append(f"INSERT INTO [{tbl}] (id, code) VALUES ({rid}, {code});")
        elif name is None:
            stmts.append(f"INSERT INTO [{tbl}] (id, code, name) VALUES ({rid}, {code}, NULL);")
        else:
            esc = str(name).replace("'", "''")
            stmts.append(
                f"INSERT INTO [{tbl}] (id, code, name) VALUES ({rid}, {code}, N'{esc}');"
            )
    return stmts


def build_sql() -> str:
    """Full create/insert/backup script for ``sqlcmd -i`` (deterministic).

    Tables are created parent-before-child so the FK reference resolves; the
    backup target is filled in by the fixture runner.
    """
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
    ]
    # Parent tables (FK targets) must exist before children reference them.
    ordered = sorted(CASES, key=lambda c: c.references is not None)
    for case in ordered:
        tbl = table_name(case)
        parts.append(f"CREATE TABLE [{tbl}] ({case.columns_sql});")
        parts.append("GO")
        parts.extend(_insert(case))
        for stmt in case.post_sql:
            parts.append(stmt)
        parts.append("GO")
    return "\n".join(parts) + "\n"


def main() -> int:
    from tools.make_fixture import generate_fixture

    return generate_fixture(DB_NAME, build_sql(), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
