"""Table-organization coverage matrix — structural variants × all data types.

Companion to ``tools/typematrix.py``.  Where ``typematrix`` varies the *data
type* with a fixed table structure, this module varies the *table organization*
(heap, clustered index, partition, columnstore, …) with a fixed wide schema that
holds every ``TYPE_CASE`` as a column.

Fixture layout
--------------
One database (``TabletypeCoverage``) contains **one table per org**:

    tt_plain       — clustered PK on id; no compression; baseline
    tt_heap        — heap (no clustered index; IAM scan)
    tt_cluster     — non-unique clustered index on a secondary column
    tt_partition   — range-partitioned on id (2 partitions: ≤5 and >5)
    tt_column      — clustered columnstore (incompatible types omitted)

Each table has ``id int`` (the row key) plus one column ``c_{case.name}`` per
``TypeCase``.  Four rows are inserted: ``id``=1 low, 2 high, 3 mid, 4 null.

The ``rowversion`` type is auto-populated by the engine; we validate non-NULL
rather than comparing to a reference value.

Differential-backup coverage
-----------------------------
After the full backup, a second SQL pass inserts two extra rows (id=5 "extra",
id=6 "extra2") to make the pages dirty, then takes a ``WITH DIFFERENTIAL``
backup.  The differential fixture exercises the base-merge path
(``PageStore.from_diff_bak``; implemented and tested in ``tests/test_tabletype_coverage.py``).

Usage::

    python tools/make_tabletype_fixture.py

Then commit the generated files to tests/fixtures/.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tools.typematrix import TYPE_CASES, TypeCase

# ---------------------------------------------------------------------------
# Types that SQL Server does NOT support inside a columnstore index.
# Deprecated LOBs (text/ntext/image), xml, sql_variant, and CLR UDTs.
# varchar(max)/nvarchar(max)/varbinary(max) ARE supported since SQL Server 2017.
# ---------------------------------------------------------------------------
# Types where the columnstore decoder returns wrong or None values for a small
# (4-row) table in the test fixture.  Tracked here so tests can mark them xfail
# while the passing types remain green regression guards.
#
# Remaining root cause:
#  enc=3, large variable-length MAX types use a compressed dict blob format
#  with a multi-byte (varint-style) length encoding for strings > 255 bytes.
#  The segment blob also has a 12-byte "size prefix" that shifts the bpv/nw
#  offsets.  Both issues require further reverse-engineering of the internal
#  columnstore dictionary format before these can be decoded correctly.
#    varchar_max  — 4 000-char Z string exceeds 1-byte length limit
#    varbinary_max — 1 MiB binary blob stored off-row, not in the dict blob
COLUMNSTORE_XFAIL: frozenset[str] = frozenset()

# Types where the segment decoder was known to return wrong or None values
# only when the row group was large enough to use real compression encoding
# (≥ 1,200 rows).  All five bugs were fixed during Gap K-1/K-3 work:
#
#   decimal_38_10    — FIXED: enc=4 raw bytes now decoded to Decimal
#   datetimeoffset_7 — FIXED: raw bytes now decoded to datetime+tzinfo
#   nvarchar_50      — FIXED: NULL rows now return None (not '')
#   binary_8         — FIXED: enc=1 low value now returns bytes (not None)
#   uniqueidentifier — FIXED: now returns UUID (not '')
#
# Set is intentionally empty; kept for documentation history.
COLUMNSTORE_LARGE_XFAIL: frozenset[str] = frozenset()

COLUMNSTORE_SKIP: frozenset[str] = frozenset(
    # Deprecated LOBs, xml, sql_variant, CLR UDTs, and rowversion are all
    # rejected by SQL Server when creating a columnstore index.
    {"text", "ntext", "image", "xml", "sql_variant",
     "rowversion", "hierarchyid", "geometry", "geography"}
)

# rowversion is always auto; the "null" row insert just omits it (engine fills).
_AUTO_TYPES: frozenset[str] = frozenset({"rowversion"})

# Row labels in insertion order.
LABELS: list[str] = ["low", "high", "mid", "null"]
LABEL_ID: dict[str, int] = {"low": 1, "high": 2, "mid": 3, "null": 4}


@dataclass(frozen=True)
class OrgCase:
    """One table-organization variant.

    ``skip_types`` lists ``TypeCase.name`` values that cannot appear as columns
    for this organization (e.g. columnstore does not support ``xml``).
    ``create_ddl`` is a Python format string; ``{tbl}`` is substituted with the
    table name before emitting SQL.  ``post_create_ddl`` runs after the table is
    created (e.g. to add a columnstore index).
    """

    name: str
    kind: str
    create_ddl: str
    post_create_ddl: str = ""
    skip_types: frozenset[str] = field(default_factory=frozenset)


# ---------------------------------------------------------------------------
# Wide-column DDL shared by all orgs (one NULL column per TypeCase).
# Callers substitute {skip} with a set to suppress certain columns.
# ---------------------------------------------------------------------------
def _cols_ddl(skip: frozenset[str] = frozenset()) -> str:
    """Build the column list for a wide-schema table.

    ``rowversion`` cannot be declared NULL (engine-populated); everything else is
    nullable.  Skipped names are omitted entirely.
    """
    parts: list[str] = ["id int NOT NULL"]
    for case in TYPE_CASES:
        if case.name in skip:
            continue
        if case.auto:
            parts.append(f"c_{case.name} {case.sql_type}")
        else:
            parts.append(f"c_{case.name} {case.sql_type} NULL")
    return ",\n    ".join(parts)


def table_name(org: OrgCase) -> str:
    return f"tt_{org.name}"


def supported_cases(org: OrgCase) -> list[TypeCase]:
    """Type cases that have a column in this org's table."""
    return [c for c in TYPE_CASES if c.name not in org.skip_types]


# ---------------------------------------------------------------------------
# Organization cases
# ---------------------------------------------------------------------------
ORG_CASES: list[OrgCase] = [
    OrgCase(
        name="plain",
        kind="clustered primary key (B-tree, id asc) — no compression; baseline",
        create_ddl=(
            "CREATE TABLE [{tbl}] (\n    {cols},\n"
            "    CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id)\n);"
        ),
    ),
    OrgCase(
        name="heap",
        kind="heap (no clustered index; IAM + forwarded-record scan)",
        create_ddl="CREATE TABLE [{tbl}] (\n    {cols}\n);",
    ),
    OrgCase(
        name="cluster",
        kind="non-unique clustered index on a secondary column (tests non-PK B-tree walk)",
        create_ddl=(
            "CREATE TABLE [{tbl}] (\n    {cols},\n"
            "    id2 AS (id * 2)\n);\n"
            "CREATE CLUSTERED INDEX cix_{tbl} ON [{tbl}](id);"
        ),
    ),
    OrgCase(
        name="partition",
        kind="range-partitioned on id (2 partitions: id ≤ 5 and id > 5)",
        create_ddl=(
            # Partition function / scheme created in make_tabletype_fixture.py
            # before the table; substituted here with {tbl}.
            "CREATE TABLE [{tbl}] (\n    {cols}\n)"
            " ON ps_tt_id(id);"
        ),
    ),
    OrgCase(
        name="column",
        kind="clustered columnstore index (xml/text/sql_variant/CLR types omitted)",
        create_ddl=(
            # No explicit clustered key; the CCI is added post-create.
            "CREATE TABLE [{tbl}] (\n    {cols}\n);"
        ),
        post_create_ddl="CREATE CLUSTERED COLUMNSTORE INDEX cci_{tbl} ON [{tbl}];",
        skip_types=COLUMNSTORE_SKIP,
    ),
]

ORG_BY_NAME: dict[str, OrgCase] = {o.name: o for o in ORG_CASES}
