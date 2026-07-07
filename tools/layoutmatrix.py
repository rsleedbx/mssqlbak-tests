"""Record-layout matrix — PK position and column-count boundary fixtures.

Companion to ``tools/constraintmatrix.py``.  Where that matrix isolates one
*constraint* per table, this one isolates one *layout* dimension per table:
primary-key column position (L01/L02) or total column count (L03).

Every case uses deterministic, seeded row values so parser regressions attribute
to layout rather than random data.
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "LayoutCoverage"
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_PATH = FIXTURE_DIR / "layoutcoverage_full.bak"
OUT_COMPRESSED_PATH = FIXTURE_DIR / "layoutcoverage_compressed.bak"

# Shared filler column definitions (non-PK); reused in every PK-position table.
_FILLER_SPECS: list[tuple[str, str]] = [
    ("f_bit", "bit NOT NULL"),
    ("f_int", "int NOT NULL"),
    ("f_vch", "varchar(20) NOT NULL"),
    ("f_bit2", "bit NOT NULL"),
    ("f_int2", "int NOT NULL"),
]

# Canonical filler values for the three seeded rows.
_FILLER_VALUES: list[tuple[bool, int, str, bool, int]] = [
    (True, 10, "alpha", False, 100),
    (False, 20, "beta", True, 200),
    (True, 30, "gamma", False, 300),
]

PK_POSITIONS = ("first", "second", "penult", "last")


@dataclass(frozen=True)
class PkTypeSpec:
    """One PK-eligible SQL type with canonical test values."""

    name: str
    sql_type: str
    col_def: str  # e.g. "int NOT NULL"
    values: tuple[Any, Any, Any]  # low, mid, high row PK values
    sql_literals: tuple[str, str, str]  # INSERT literals for the three rows


PK_TYPES: list[PkTypeSpec] = [
    PkTypeSpec("int", "int", "int NOT NULL", (1, 2, 3), ("1", "2", "3")),
    PkTypeSpec("bigint", "bigint", "bigint NOT NULL", (1, 2, 3), ("1", "2", "3")),
    PkTypeSpec("smallint", "smallint", "smallint NOT NULL", (1, 2, 3), ("1", "2", "3")),
    PkTypeSpec("tinyint", "tinyint", "tinyint NOT NULL", (1, 2, 3), ("1", "2", "3")),
    PkTypeSpec(
        "uniqueidentifier",
        "uniqueidentifier",
        "uniqueidentifier NOT NULL",
        (
            UUID("11111111-1111-1111-1111-111111111111"),
            UUID("22222222-2222-2222-2222-222222222222"),
            UUID("33333333-3333-3333-3333-333333333333"),
        ),
        (
            "'11111111-1111-1111-1111-111111111111'",
            "'22222222-2222-2222-2222-222222222222'",
            "'33333333-3333-3333-3333-333333333333'",
        ),
    ),
    PkTypeSpec(
        "datetime2",
        "datetime2(7)",
        "datetime2(7) NOT NULL",
        (
            dt.datetime(2020, 1, 1, 0, 0, 0),
            dt.datetime(2020, 6, 15, 12, 30, 45),
            dt.datetime(2021, 12, 31, 23, 59, 59),
        ),
        ("'2020-01-01'", "'2020-06-15 12:30:45'", "'2021-12-31 23:59:59'"),
    ),
    PkTypeSpec(
        "date",
        "date",
        "date NOT NULL",
        (dt.date(2020, 1, 1), dt.date(2020, 6, 15), dt.date(2021, 12, 31)),
        ("'2020-01-01'", "'2020-06-15'", "'2021-12-31'"),
    ),
    PkTypeSpec(
        "char10",
        "char(10)",
        "char(10) NOT NULL",
        ("A         ", "B         ", "C         "),
        ("'A         '", "'B         '", "'C         '"),
    ),
    PkTypeSpec(
        "varchar100",
        "varchar(100)",
        "varchar(100) NOT NULL",
        ("pk_one", "pk_two", "pk_three"),
        ("'pk_one'", "'pk_two'", "'pk_three'"),
    ),
    PkTypeSpec(
        "nchar10",
        "nchar(10)",
        "nchar(10) NOT NULL",
        ("Nα        ", "Nβ        ", "Nγ        "),
        ("N'Nα        '", "N'Nβ        '", "N'Nγ        '"),
    ),
    PkTypeSpec(
        "nvarchar50",
        "nvarchar(50)",
        "nvarchar(50) NOT NULL",
        ("pk_one", "pk_two", "pk_three"),
        ("N'pk_one'", "N'pk_two'", "N'pk_three'"),
    ),
    PkTypeSpec(
        "binary16",
        "binary(16)",
        "binary(16) NOT NULL",
        (b"\x01" * 16, b"\x02" * 16, b"\x03" * 16),
        ("0x01010101010101010101010101010101", "0x02020202020202020202020202020202", "0x03030303030303030303030303030303"),
    ),
    PkTypeSpec(
        "decimal18",
        "decimal(18,0)",
        "decimal(18,0) NOT NULL",
        (Decimal(1), Decimal(2), Decimal(3)),
        ("1", "2", "3"),
    ),
]


@dataclass(frozen=True)
class PkLayoutCase:
    """One table isolating PK type + column position."""

    pk_type: PkTypeSpec
    position: str  # first | second | penult | last
    layout_id: str = "L01"

    @property
    def table_name(self) -> str:
        return f"layout_pk_{self.pk_type.name}_{self.position}"

    @property
    def pk_col_name(self) -> str:
        return "pk_col"


@dataclass(frozen=True)
class ColCountCase:
    """One table isolating total column count."""

    name: str
    n_data_cols: int  # tinyint filler count (PK is separate unless n=1)
    layout_id: str = "L03"

    @property
    def table_name(self) -> str:
        return f"layout_cols_{self.name}"


def all_pk_cases() -> list[PkLayoutCase]:
    return [
        PkLayoutCase(pk, pos)
        for pk in PK_TYPES
        for pos in PK_POSITIONS
    ]


COL_COUNT_CASES: list[ColCountCase] = [
    ColCountCase("1", 0),       # single int PK column only
    ColCountCase("30", 29),     # 29 tinyint + int PK = 30 cols (CD cluster boundary)
    ColCountCase("31", 30),     # 30 tinyint + int PK = 31 cols (second cluster)
    ColCountCase("1023", 1022), # max-1
    ColCountCase("1024", 1023), # max columns (1023 tinyint + int PK)
]


def _column_list_for_pk_case(case: PkLayoutCase) -> list[tuple[str, str, bool]]:
    """Return ordered (name, sql_def, is_pk) column specs."""
    pk = (case.pk_col_name, case.pk_type.col_def, True)
    fillers = [(n, d, False) for n, d in _FILLER_SPECS]
    if case.position == "first":
        return [pk, *fillers]
    if case.position == "second":
        return [fillers[0], pk, *fillers[1:]]
    if case.position == "penult":
        return [*fillers[:-1], pk, fillers[-1]]
    if case.position == "last":
        return [*fillers, pk]
    raise ValueError(f"unknown position {case.position!r}")


def _create_table_sql(case: PkLayoutCase) -> str:
    cols = _column_list_for_pk_case(case)
    parts: list[str] = []
    pk_name: str | None = None
    for name, defn, is_pk in cols:
        if is_pk:
            parts.append(f"[{name}] {defn}")
            pk_name = name
        else:
            parts.append(f"[{name}] {defn}")
    assert pk_name is not None
    body = ", ".join(parts)
    return (
        f"CREATE TABLE [{case.table_name}] ({body}, "
        f"CONSTRAINT [PK_{case.table_name}] PRIMARY KEY CLUSTERED ([{pk_name}]));"
    )


def _insert_sql(case: PkLayoutCase) -> list[str]:
    cols = _column_list_for_pk_case(case)
    col_names = [c[0] for c in cols]
    stmts: list[str] = []
    for row_i, fillers in enumerate(_FILLER_VALUES):
        pk_lit = case.pk_type.sql_literals[row_i]
        fb, fi, fv, fb2, fi2 = fillers
        filler_lits = {
            "f_bit": str(int(fb)),
            "f_int": str(fi),
            "f_vch": f"'{fv}'",
            "f_bit2": str(int(fb2)),
            "f_int2": str(fi2),
        }
        values: list[str] = []
        for name, _, is_pk in cols:
            values.append(pk_lit if is_pk else filler_lits[name])
        names = ", ".join(f"[{n}]" for n in col_names)
        vals = ", ".join(values)
        stmts.append(f"INSERT INTO [{case.table_name}] ({names}) VALUES ({vals});")
    return stmts


def expected_pk_rows(case: PkLayoutCase) -> list[dict[str, Any]]:
    """Canonical rows a correct parser must reproduce."""
    out: list[dict[str, Any]] = []
    for row_i, fillers in enumerate(_FILLER_VALUES):
        row: dict[str, Any] = {case.pk_col_name: case.pk_type.values[row_i]}
        fb, fi, fv, fb2, fi2 = fillers
        row.update({"f_bit": fb, "f_int": fi, "f_vch": fv, "f_bit2": fb2, "f_int2": fi2})
        out.append(row)
    return out


def _col_count_create_sql(case: ColCountCase) -> str:
    if case.n_data_cols == 0:
        return (
            f"CREATE TABLE [{case.table_name}] ("
            f"[id] int NOT NULL CONSTRAINT [PK_{case.table_name}] PRIMARY KEY CLUSTERED);"
        )
    parts = [f"[c{i:04d}] tinyint NOT NULL CONSTRAINT [DF_{case.table_name}_c{i:04d}] DEFAULT 0"
             for i in range(1, case.n_data_cols + 1)]
    parts.append("[id] int NOT NULL")
    body = ", ".join(parts)
    return (
        f"CREATE TABLE [{case.table_name}] ({body}, "
        f"CONSTRAINT [PK_{case.table_name}] PRIMARY KEY CLUSTERED ([id]));"
    )


def _col_count_insert_sql(case: ColCountCase) -> list[str]:
    if case.n_data_cols == 0:
        return [
            f"INSERT INTO [{case.table_name}] ([id]) VALUES (1);",
            f"INSERT INTO [{case.table_name}] ([id]) VALUES (2);",
            f"INSERT INTO [{case.table_name}] ([id]) VALUES (3);",
        ]
    return [
        f"INSERT INTO [{case.table_name}] ([id]) VALUES ({i});"
        for i in (1, 2, 3)
    ]


def expected_col_count_rows(case: ColCountCase) -> list[dict[str, Any]]:
    if case.n_data_cols == 0:
        return [{"id": 1}, {"id": 2}, {"id": 3}]
    row: dict[str, Any] = {"id": 1}
    for i in range(1, case.n_data_cols + 1):
        row[f"c{i:04d}"] = 0
    return [dict(row, id=v) for v in (1, 2, 3)]


def build_sql(*, page_compression: bool = False) -> str:
    """Full create/insert script for ``sqlcmd -i``."""
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
    for case in all_pk_cases():
        create = _create_table_sql(case)
        if page_compression and case.pk_type.name == "int" and case.position == "first":
            create = create.replace(");", ") WITH (DATA_COMPRESSION = PAGE);")
        parts.append(create)
        parts.append("GO")
        parts.extend(_insert_sql(case))
        parts.append("GO")
    for cc in COL_COUNT_CASES:
        parts.append(_col_count_create_sql(cc))
        parts.append("GO")
        parts.extend(_col_count_insert_sql(cc))
        parts.append("GO")
    return "\n".join(parts) + "\n"


def all_table_names() -> set[str]:
    return {c.table_name for c in all_pk_cases()} | {c.table_name for c in COL_COUNT_CASES}
