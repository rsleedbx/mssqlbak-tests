"""Data-compression matrix — tables that isolate one storage format each.

Companion to ``tools/constraintmatrix.py``.  Every table shares the same
``(id, code, name)`` layout, a clustered ``PRIMARY KEY`` on ``id``, and the same
rows; each table differs only in how its data rowset is *physically stored*:

* ``cmp_none``  — uncompressed (FixedVar records); the baseline the v1 reader handles.
* ``cmp_row``   — ROW compression (CD-format records).
* ``cmp_page``  — PAGE compression (CD records + a per-page compression-info anchor).
* ``cmp_columnstore`` — clustered columnstore (column segments in LOB units, no row pages).

The v1 row reader only understands uncompressed FixedVar records, so ROW/PAGE/
columnstore rowsets must be *detected and skipped*, never decoded blindly (that
would yield silent garbage).  This fixture lets us reverse-engineer the detection
signal and guard it.

Rows are deterministic and intentionally repetitive (``code = id % 50``) so PAGE
compression has dictionary entries to build, exercising the anchor record.

The shared column set also carries the **types whose compressed form differs
from their on-disk form**: ``decimal``/``numeric`` (vardecimal bit packing); the
temporal family (``datetime``, ``datetime2``, ``date``, ``time``,
``datetimeoffset``); and ``nvarchar``/``nchar`` (Unicode-compressed with SCSU,
not UTF-16LE -- one in five ``nvarchar`` rows is Cyrillic so the SCSU dynamic-
window path is exercised end-to-end, not just ASCII passthrough).  After a regen
the ``cmp_row``/``cmp_page`` tables validate every compressed decoder row-for-row
against ``cmp_none``.  ``smalldatetime`` is included (Guess G19) and decoded via
the leading-zero-width path in :mod:`mssqlbak.rowcompress`.

Beyond compression, a single provisioning pass also builds the **record-layer**
fixtures that need a live engine to produce: a **uniquifier** (non-unique
clustered index), **sparse columns** (values stored in a sparse vector), and a
heap exercising **forwarded** records and **ghost** (deleted-not-cleaned) rows.
These let ``mssqlbak.recordtype`` (record-type dispatch) and the sparse-vector
path be validated against real on-disk shapes.
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_NAME = "CompressionCoverage"

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures")))
OUT_PATH = FIXTURE_DIR / "compressioncoverage_full.bak"

ROW_COUNT = 200  # reduced from 1000: wider rows (K-4) + limited host RAM exhaust memory on SS2025


@dataclass(frozen=True)
class CompressionCase:
    """One table that isolates a single physical storage format."""

    name: str          # table is ``cmp_<name>``
    kind: str          # human label for the storage format under test
    # How the clustered index/table is created (filled with the table name).
    create_sql: str
    columnstore: bool = False  # post-create CLUSTERED COLUMNSTORE INDEX
    expected_encoding: str = ""


# Shared column set for the storage-format matrix.  ``id``/``code``/``name``
# keep the original int/varchar coverage; the rest add the fixed types whose
# *compressed* encoding differs from their on-disk form, so cmp_row/cmp_page
# validate those decoders against cmp_none.
#
# K-4 columns (bigint..uid) were added to close the gap where leading-zero
# stripping (bigint/smallint/money), trailing-space stripping (char), trailing-
# zero stripping (binary), and the bit/varbinary/uniqueidentifier round-trip
# paths were absent from the cross-compression comparison.
_COLS = (
    "id int NOT NULL, "
    "code int NOT NULL, "
    "name varchar(20) NULL, "      # single-byte string (not Unicode-compressed)
    "nm nvarchar(40) NULL, "       # Unicode string -> SCSU under compression
    "ncf nchar(10) NULL, "         # fixed Unicode string -> SCSU, re-padded
    "amount decimal(18,4) NULL, "
    "qty numeric(9,2) NULL, "
    "dt datetime NULL, "
    "dt2 datetime2(3) NULL, "
    "d date NULL, "
    "t time(3) NULL, "
    "dto datetimeoffset(3) NULL, "
    "sdt smalldatetime NULL, "
    # K-4: types absent from the matrix before this fix
    "big bigint NULL, "            # 8-byte; leading-zero stripping under ROW
    "si smallint NULL, "           # 2-byte; leading-zero stripping
    "ti tinyint NULL, "            # 1-byte unsigned; covered only by unit tests before
    "bf bit NULL, "                # boolean; TrueBit/ZeroByte CD encoding
    "mon money NULL, "             # 8-byte fixed-scale; leading-zero stripping
    "smon smallmoney NULL, "       # 4-byte fixed-scale
    "ch char(10) NULL, "           # fixed string; trailing-space stripping under ROW/PAGE
    "bn binary(10) NULL, "         # fixed binary; trailing-zero stripping under ROW/PAGE
    "vbn varbinary(20) NULL, "     # variable binary in CD record
    "uid uniqueidentifier NULL"    # 16-byte GUID; round-trip validation
)

_COL_NAMES = (
    "id, code, name, nm, ncf, amount, qty, dt, dt2, d, t, dto, sdt, "
    "big, si, ti, bf, mon, smon, ch, bn, vbn, uid"
)

# Unicode strings built from NCHAR() code points (ASCII-safe in the SQL script).
# Each exercises a different SCSU encoding path under ROW/PAGE compression.
#
# Cyrillic "Привет": SCSU dynamic-window path (SD command selects Cyrillic block,
# subsequent bytes reference that window).  Every 5th row.
_CYRILLIC_NM = "+".join(
    f"NCHAR({cp})" for cp in (0x041F, 0x0440, 0x0438, 0x0432, 0x0435, 0x0442)
)
# CJK "山田" (U+5C71 U+7530): SCSU Unicode mode (SCU 0x0F followed by big-endian
# UTF-16 pairs).  SQL Server appends a trailing 0x10 (SC0) after the Unicode-mode
# bytes; the decoder must not misinterpret that as the high byte of U+10xx.
# Every 3rd row (not every 5th, so it interleaves with Cyrillic rows).
_CJK_NM = "+".join(f"NCHAR({cp})" for cp in (0x5C71, 0x7530))  # 山田
# Arabic "مرحبا" (U+0645 U+0631 U+062D U+0628 U+0627): may use SCSU dynamic-window
# OR Unicode mode depending on the encoder; exercises the Arabic block.
# Every 11th row.
_ARABIC_NM = "+".join(
    f"NCHAR({cp})" for cp in (0x0645, 0x0631, 0x062D, 0x0628, 0x0627)
)
# Mixed ASCII + CJK "Hi山": mode switch from single-byte to Unicode mode mid-value.
# Every 13th row.
_MIXED_NM = "NCHAR(72)+NCHAR(105)+" + "+".join(
    f"NCHAR({cp})" for cp in (0x5C71,)
)

# Deterministic base instant; each row offsets from it so values are stable and
# span sub-second precision (for datetime/datetime2/time) and a tz offset.
_BASE_DT = dt.datetime(2001, 1, 1, 0, 0, 0)


CASES: list[CompressionCase] = [
    CompressionCase(
        "none", "uncompressed (baseline)",
        f"CREATE TABLE [{{tbl}}] ({_COLS}, "
        "CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id));",
        expected_encoding="FixedVar records; sysrowsets compression level 0. Readable.",
    ),
    CompressionCase(
        "row", "ROW compression",
        f"CREATE TABLE [{{tbl}}] ({_COLS}, "
        "CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id) "
        "WITH (DATA_COMPRESSION = ROW));",
        expected_encoding="CD-format records; sysrowsets compression level 1. Not readable.",
    ),
    CompressionCase(
        "page", "PAGE compression",
        f"CREATE TABLE [{{tbl}}] ({_COLS}, "
        "CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id) "
        "WITH (DATA_COMPRESSION = PAGE));",
        expected_encoding="CD records + per-page CI anchor; sysrowsets level 2. Not readable.",
    ),
    CompressionCase(
        "columnstore", "clustered columnstore",
        f"CREATE TABLE [{{tbl}}] ({_COLS});",
        columnstore=True,
        expected_encoding="data in column segments (LOB units), not row pages. Not readable.",
    ),
    CompressionCase(
        "columnstore_archive", "clustered columnstore archive (XPRESS)",
        f"CREATE TABLE [{{tbl}}] ({_COLS});",
        columnstore=True,
        expected_encoding="CCI with COLUMNSTORE_ARCHIVE (cmprlevel=4); segments are XPRESS compressed.",
    ),
]

_ARCHIVE_COMPRESSION_SQL = (
    "ALTER INDEX cci_{tbl} ON [{tbl}] REBUILD WITH (DATA_COMPRESSION = COLUMNSTORE_ARCHIVE);"
)


def table_name(case: CompressionCase) -> str:
    return f"cmp_{case.name}"


def _row_literal(i: int) -> str:
    """One ``(...)`` VALUES tuple for row *i*, deterministic across every table.

    Every 7th row NULLs the nullable trailing columns so the null bitmap is
    exercised under each storage format; the rest carry distinct temporal /
    decimal values spanning sub-second precision and a timezone offset.
    """
    code = i % 50
    name = f"val{i % 10}"
    if i % 7 == 0:
        # 13 original columns + 10 K-4 columns = 23 total values
        return (
            f"({i}, {code}, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, "
            "NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)"
        )
    inst = _BASE_DT + dt.timedelta(minutes=i, milliseconds=(i % 1000))
    # nvarchar: rotate through SCSU encoding paths across rows.
    #   every 5th  → Cyrillic (dynamic-window SCSU)
    #   every 3rd  → CJK (Unicode-mode SCSU; exercises 0x10 trailer bug)
    #   every 11th → Arabic (dynamic-window or Unicode-mode)
    #   every 13th → Mixed ASCII+CJK (mode-switch mid-value)
    #   else       → ASCII passthrough
    if i % 5 == 0:
        nm = _CYRILLIC_NM
    elif i % 3 == 0:
        nm = _CJK_NM
    elif i % 11 == 0:
        nm = _ARABIC_NM
    elif i % 13 == 0:
        nm = _MIXED_NM
    else:
        nm = f"N'name{i % 10}'"
    ncf = f"N'ncf{i % 10}'"                   # nchar(10), space-padded on disk
    amount = f"{i}.{i % 10000:04d}"          # decimal(18,4)
    qty = f"{i % 1000000}.{i % 100:02d}"     # numeric(9,2)
    dtv = inst.strftime("%Y-%m-%d %H:%M:%S.") + f"{inst.microsecond // 1000:03d}"
    datev = inst.strftime("%Y-%m-%d")
    timev = inst.strftime("%H:%M:%S.") + f"{inst.microsecond // 1000:03d}"
    dtov = f"{dtv} +05:30"
    # smalldatetime: whole-minute values (seconds always 0 on disk).
    sdtv = (_BASE_DT + dt.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
    # K-4 extra columns — deterministic values chosen to exercise the specific
    # compression edge-case for each type.
    big = i * 10_000_000          # 4–8 byte excess-encoded bigint (leading-zero strip)
    si = i % 30_000               # 2-byte smallint (leading-zero strip for small i)
    ti = (i % 254) + 1            # 1-byte tinyint (1..254; unsigned passthrough)
    bf = i % 2                    # bit: TrueBit(1) / ZeroByte(0) CD encoding
    mon = f"{i * 12}.3456"        # money — 4 fixed decimal places
    smon = f"{i % 100}.1234"      # smallmoney — 4 decimal places, small range
    ch = f"'ch{i % 100:02d}'"     # 4-char value; char(10) pads with 6 spaces → stripped
    # binary(10): value has trailing zero bytes so trailing-zero stripping fires.
    # High 2 bytes carry i, low 8 bytes are 0x00; last byte is always 0x00.
    bn_hex = f"{i:04X}{'00' * 8}"  # 2 bytes of i + 8 zero bytes = 10 bytes
    bn = f"0x{bn_hex}"
    vbn = f"CONVERT(varbinary(20), {i})"   # variable binary
    # Deterministic GUID: 00000000-0000-0000-0000-<i as 12 hex digits>
    uid_raw = f"{i:032X}"
    uid = (
        f"'{uid_raw[0:8]}-{uid_raw[8:12]}-{uid_raw[12:16]}-{uid_raw[16:20]}-{uid_raw[20:32]}'"
    )
    return (
        f"({i}, {code}, N'{name}', {nm}, {ncf}, {amount}, {qty}, "
        f"'{dtv}', '{dtv}', '{datev}', '{timev}', '{dtov}', '{sdtv}', "
        f"{big}, {si}, {ti}, {bf}, {mon}, {smon}, {ch}, {bn}, {vbn}, {uid})"
    )


def _insert(case: CompressionCase) -> list[str]:
    tbl = table_name(case)
    stmts: list[str] = []
    # 50-row batches: wider rows (K-4 adds 10 cols) can exhaust SQL Server memory
    # pool on constrained instances (SS2025 container) with 200-row batches.
    for start in range(1, ROW_COUNT + 1, 50):
        chunk = range(start, min(start + 50, ROW_COUNT + 1))
        values = ", ".join(_row_literal(i) for i in chunk)
        stmts.append(f"INSERT INTO [{tbl}] ({_COL_NAMES}) VALUES {values};")
    return stmts


def _floats_sql() -> list[str]:
    """Tables for G19: real/float/smalldatetime under ROW and PAGE compression.

    7 rows chosen to exercise:
    * zero-value bytes (row 1) — leading-zero stripping
    * positive fractional (row 3) — pi-ish
    * negative/boundary (row 4) — max smalldatetime 2079-06-06 23:59
    * all-NULL row (row 7)
    """
    rows = [
        "(1, 0.0, 0.0, '1900-01-01 00:00')",
        "(2, 1.0, 1.0, '2000-01-01 00:00')",
        "(3, 3.14, 3.141592653589793, '2024-06-15 13:45')",
        "(4, -1.5, -1.5, '2079-06-06 23:59')",
        "(5, 1e10, 1e100, '2030-12-31 12:00')",
        "(6, -0.0, -0.0, '1901-01-01 00:01')",
        "(7, NULL, NULL, NULL)",
    ]
    vals = ", ".join(rows)
    parts: list[str] = []
    for suffix, compression in (("row", "ROW"), ("page", "PAGE")):
        tbl = f"cmp_{suffix}_floats"
        parts.append(
            f"CREATE TABLE [{tbl}] "
            "(id int NOT NULL, r real NULL, f float NULL, sdt smalldatetime NULL, "
            f"CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id) "
            f"WITH (DATA_COMPRESSION = {compression}));"
        )
        parts.append("GO")
        parts.append(f"INSERT INTO [{tbl}] (id, r, f, sdt) VALUES {vals};")
        parts.append("GO")
    return parts


def _lob_sql() -> list[str]:
    """Tables for legacy LOB types (text/ntext/image/xml/rowversion) under ROW/PAGE.

    3 rows: short values (id=1), large off-row values (id=2), all-NULL (id=3).
    NOTE: text/ntext/image store data off-row; compression only affects the
    in-row pointer and the id/rv fixed columns.
    """
    parts: list[str] = []
    for suffix, compression in (("row", "ROW"), ("page", "PAGE")):
        tbl = f"cmp_{suffix}_lob"
        parts.append(
            f"CREATE TABLE [{tbl}] "
            "(id int NOT NULL, tx text NULL, img image NULL, "
            " ntx ntext NULL, x xml NULL, rv rowversion NOT NULL, "
            f"CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id) "
            f"WITH (DATA_COMPRESSION = {compression}));"
        )
        parts.append("GO")
        parts.append(
            f"INSERT INTO [{tbl}] (id, tx, img, ntx, x) VALUES "
            "(1, 'hello text', 0x48656C6C6F, N'hello ntext', '<a>one</a>');"
        )
        parts.append("GO")
        parts.append(
            f"INSERT INTO [{tbl}] (id, tx, img, ntx, x) VALUES "
            f"(2, REPLICATE('x', 5000), CAST(REPLICATE('y', 5000) AS varbinary(max)), "
            " N'unicode text here', '<b>' + REPLICATE('z', 100) + '</b>');"
        )
        parts.append("GO")
        parts.append(
            f"INSERT INTO [{tbl}] (id, tx, img, ntx, x) VALUES "
            "(3, NULL, NULL, NULL, NULL);"
        )
        parts.append("GO")
    return parts


def _variant_sql() -> list[str]:
    """Tables for sql_variant under ROW and PAGE compression.

    9 rows exercising diverse base types: tinyint, int, bigint, float,
    varchar, nvarchar, date, bit, NULL.  Each row is a separate INSERT so
    SQL Server preserves the declared base type in the sql_variant header
    (multi-row VALUES coerces to a common type).
    """
    # (id, value_expr) — individual INSERT per row to preserve sql_variant base type.
    rows = [
        (1, "CAST(0 AS tinyint)"),
        (2, "CAST(42 AS int)"),
        (3, "CAST(100000 AS bigint)"),
        (4, "CAST(3.14 AS float)"),
        (5, "CAST('hello' AS varchar(20))"),
        (6, "CAST(N'hi' AS nvarchar(20))"),
        (7, "CAST('2024-01-15' AS date)"),
        (8, "CAST(1 AS bit)"),
        (9, "NULL"),
    ]
    parts: list[str] = []
    for suffix, compression in (("row", "ROW"), ("page", "PAGE")):
        tbl = f"cmp_{suffix}_variant"
        parts.append(
            f"CREATE TABLE [{tbl}] "
            "(id int NOT NULL, v sql_variant NULL, "
            f"CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id) "
            f"WITH (DATA_COMPRESSION = {compression}));"
        )
        parts.append("GO")
        for row_id, val_expr in rows:
            parts.append(f"INSERT INTO [{tbl}] (id, v) VALUES ({row_id}, {val_expr});")
        parts.append("GO")
    return parts


def _record_layer_sql() -> list[str]:
    """Record-layer feature tables that need a live engine to materialise.

    * ``uniquifier_*`` -- a **non-unique** clustered index (key ``code`` has only
      50 distinct values over 1000 rows), so SQL Server appends the 4-byte
      uniquifier to duplicate keys.  Built uncompressed and ROW-compressed so the
      uniquifier is exercised in both record formats.
    * ``sparse_cols`` -- SPARSE columns whose values live in the trailing sparse
      vector rather than the normal fixed/variable regions; most rows leave them
      NULL (the case SPARSE optimises for).
    * ``fwd_heap`` -- a heap whose row is grown by UPDATE past the page free
      space, leaving a **forwarding stub** at the original slot and a
      **forwarded** record elsewhere (mirrors OrcaMDF's forwarded-record test).
    * ``ghost_heap`` -- a heap with deleted rows; the deleted slots become
      **ghost** records until background cleanup runs.  Best-effort: a backup
      taken promptly after the DELETE still contains the ghosts.
    """
    parts: list[str] = []

    # Uniquifier: non-unique clustered index over a low-cardinality key.
    for suffix, compression in (("none", ""), ("row", " WITH (DATA_COMPRESSION = ROW)")):
        tbl = f"uniquifier_{suffix}"
        parts.append(
            f"CREATE TABLE [{tbl}] (id int NOT NULL, code int NOT NULL, name varchar(20) NULL);"
        )
        parts.append(
            f"CREATE CLUSTERED INDEX cix_{tbl} ON [{tbl}](code){compression};"
        )
        parts.append("GO")
        for start in range(1, ROW_COUNT + 1, 200):
            chunk = range(start, min(start + 200, ROW_COUNT + 1))
            values = ", ".join(f"({i}, {i % 50}, N'val{i % 10}')" for i in chunk)
            parts.append(f"INSERT INTO [{tbl}] (id, code, name) VALUES {values};")
        parts.append("GO")

    # Sparse columns: mostly NULL, a few populated (stored in the sparse vector).
    parts.append(
        "CREATE TABLE [sparse_cols] (id int NOT NULL PRIMARY KEY, "
        "a int SPARSE NULL, b varchar(40) SPARSE NULL, c decimal(18,4) SPARSE NULL);"
    )
    parts.append("GO")
    svals = []
    for i in range(1, 201):
        if i % 10 == 0:
            svals.append(f"({i}, {i}, N'sparse{i}', {i}.{i % 10000:04d})")
        else:
            svals.append(f"({i}, NULL, NULL, NULL)")
    parts.append(
        "INSERT INTO [sparse_cols] (id, a, b, c) VALUES " + ", ".join(svals) + ";"
    )
    parts.append("GO")

    # Forwarded records: heap row grown past the page so it forwards.
    parts.append("CREATE TABLE [fwd_heap] (a int, b varchar(5000));")
    parts.append(
        "INSERT INTO [fwd_heap] VALUES (25, REPLICATE('A', 4000)), (28, REPLICATE('B', 4000));"
    )
    parts.append("UPDATE [fwd_heap] SET b = REPLICATE('A', 5000) WHERE a = 25;")
    parts.append("GO")

    # Ghost records: delete leaves ghosts until async cleanup (best-effort).
    parts.append("CREATE TABLE [ghost_heap] (id int NOT NULL, v varchar(20) NULL);")
    for start in range(1, 501, 200):
        chunk = range(start, min(start + 200, 501))
        values = ", ".join(f"({i}, N'g{i % 10}')" for i in chunk)
        parts.append(f"INSERT INTO [ghost_heap] (id, v) VALUES {values};")
    parts.append("DELETE FROM [ghost_heap] WHERE id % 2 = 0;")
    parts.append("GO")

    # COLUMN_SET probe: sparse columns + xml COLUMN_SET aggregate.
    # Exercises the column_set synthesis path in read_table_rows.
    parts.append(
        "CREATE TABLE [cs_probe] ("
        "  id    int          NOT NULL PRIMARY KEY, "
        "  a     int          SPARSE NULL, "
        "  b     varchar(50)  SPARSE NULL, "
        "  cs    xml          COLUMN_SET FOR ALL_SPARSE_COLUMNS"
        ");"
    )
    parts.append("GO")
    parts.append("INSERT INTO [cs_probe] (id, a, b) VALUES (1, 42, 'hello');")
    parts.append("INSERT INTO [cs_probe] (id, a, b) VALUES (2, 99, NULL);")
    parts.append("INSERT INTO [cs_probe] (id, a, b) VALUES (3, NULL, 'world');")
    parts.append("INSERT INTO [cs_probe] (id, a, b) VALUES (4, NULL, NULL);")
    parts.append("GO")
    return parts


def _wide_table_sql() -> list[str]:
    """Wide tables for G17/G18: ROW/PAGE compressed tables with >=31 columns.

    The CD long-data region is only present when a record has more than 30
    columns (the CD column-count field uses 5 bits, so the 31st column triggers
    the extended-count encoding in SQL Server 2012+).  These tables have 40 int
    columns plus an identity PK so the parser must navigate the long-data region
    to recover all values.

    Two tables cover ROW and PAGE compression independently:
    * ``cmp_row_wide``  — 40 int cols, ROW compression
    * ``cmp_page_wide`` — 40 int cols, PAGE compression
    """
    # Build column list: c01 .. c40, all int NULL.
    col_defs = ", ".join(f"c{n:02d} int NULL" for n in range(1, 41))
    col_names = ", ".join(f"c{n:02d}" for n in range(1, 41))

    # 50 rows; id = row counter; col value = (row_id * col_index) % 1000.
    # Every 7th row nulls all data columns to exercise the null bitmap.
    def _row_values(i: int) -> str:
        if i % 7 == 0:
            return "(" + str(i) + ", " + ", ".join(["NULL"] * 40) + ")"
        return "(" + str(i) + ", " + ", ".join(str((i * n) % 1000) for n in range(1, 41)) + ")"

    values = ",\n  ".join(_row_values(i) for i in range(1, 51))

    parts: list[str] = []
    for suffix, compression in (("row", "ROW"), ("page", "PAGE")):
        tbl = f"cmp_{suffix}_wide"
        parts.append(
            f"CREATE TABLE [{tbl}] "
            f"(id int NOT NULL, {col_defs}, "
            f"CONSTRAINT pk_{tbl} PRIMARY KEY CLUSTERED (id) "
            f"WITH (DATA_COMPRESSION = {compression}));"
        )
        parts.append("GO")
        parts.append(
            f"INSERT INTO [{tbl}] (id, {col_names}) VALUES\n  {values};"
        )
        parts.append("GO")
    return parts


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
    ]
    for case in CASES:
        tbl = table_name(case)
        parts.append(case.create_sql.replace("{tbl}", tbl))
        parts.append("GO")
        parts.extend(_insert(case))
        parts.append("GO")
        if case.columnstore:
            parts.append(
                f"CREATE CLUSTERED COLUMNSTORE INDEX cci_{tbl} ON [{tbl}] WITH (MAXDOP = 1);"
            )
            parts.append("GO")
            # columnstore_archive: rebuild with XPRESS (COLUMNSTORE_ARCHIVE).
            if case.name == "columnstore_archive":
                parts.append(
                    _ARCHIVE_COMPRESSION_SQL.replace("{tbl}", tbl)
                )
                parts.append("GO")
    parts.extend(_floats_sql())
    parts.extend(_lob_sql())
    parts.extend(_variant_sql())
    parts.extend(_record_layer_sql())
    parts.extend(_wide_table_sql())
    return "\n".join(parts) + "\n"


def main() -> int:
    from tools.make_fixture import generate_fixture

    return generate_fixture(DB_NAME, build_sql(), OUT_PATH)


if __name__ == "__main__":
    sys.exit(main())
