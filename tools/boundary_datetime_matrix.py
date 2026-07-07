"""Boundary-value test matrix for datetime / bit / decimal columnstore tests (Gap K-2).

This is a companion to :mod:`tools.boundary_matrix` (which covers the integer
and float types).  It extends the enc=4 boundary coverage to:

* ``bit`` — 1-bit boolean; exercises the bit-pack segment path at scale
* ``decimal(9,4)`` — 32-bit integer encoded (precision ≤ 9)
* ``decimal(18,4)`` — 64-bit integer encoded (9 < precision ≤ 18)
* ``date`` — 3-byte days since 0001-01-01; tests epoch and maximum date
* ``datetime`` — classic 8-byte format; non-uniform 1/300 s tick precision
* ``datetime2(3)`` — millisecond precision; exact round-trip in Python
* ``time(3)`` — time-of-day with millisecond precision
* ``smalldatetime`` — 4-byte minutes + days; 1900-01-01 epoch
* ``datetimeoffset(3)`` — datetime2 + UTC offset; tests ±14 h offset boundaries

## Why these boundary values matter in CCI enc=4

SQL Server's columnstore enc=4 encodes a segment as:
    stored_value = (actual - min) / magnitude

where ``min`` is the segment minimum and ``magnitude`` is the quantisation
step.  For integer-backed types (date, datetime ticks, decimal) an off-by-one
or overflow at the segment boundaries produces a silently wrong decoded value.

For ``bit``, enc=2 (RLE) or enc=4 bitpack is used at ≥ 1 024 rows.  Null
handling for a boolean type (only two non-null values) has its own path.

## Python precision note

Python ``datetime`` has microsecond precision (6 decimal digits).  SQL Server
``datetime2(n)`` and ``time(n)`` with ``n=7`` have 100-nanosecond precision
(7 digits).  Using ``scale=3`` avoids truncation and gives exact round-trips.

The ``datetime`` type (not ``datetime2``) uses 1/300-second ticks but is
*returned* by SQL Server rounded to whole milliseconds (.000/.003/.007).  Its
maximum sub-second value (299 ticks) is returned as .997 (997_000 µs), not the
raw ``299 * 1_000_000 // 300 == 996_666``.  mssqlbak matches the returned value,
so the expected test values below use the millisecond-rounded representation.
"""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from tools.boundary_matrix import BoundaryCase, N_FILLER
from tools.typematrix import Row

__all__ = ["BOUNDARY_DATETIME_CASES", "N_FILLER"]

# ---------------------------------------------------------------------------
# datetime epoch constants (mirrors mssqlbak.types)
# ---------------------------------------------------------------------------
_DT1900 = dt.datetime(1900, 1, 1)

# SQL Server returns ``datetime`` rounded to whole milliseconds following the
# .000/.003/.007 convention, and mssqlbak now matches that returned value.
# Max sub-second = 299 ticks → .997; one tick → .003; tick 298 → .993.
# (Verified against SQL Server 2017–2025 via boundarycoverage_datetime_full.)
_DATETIME_MAX = dt.datetime(9999, 12, 31, 23, 59, 59, 997_000)
_DATETIME_MIN = dt.datetime(1753, 1, 1, 0, 0, 0, 0)
_DATETIME_SEC_MIN = dt.datetime(1753, 1, 1, 0, 0, 0, 3_000)          # +1 tick → .003
_DATETIME_SEC_MAX = dt.datetime(9999, 12, 31, 23, 59, 59, 993_000)  # −1 tick → .993


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

BOUNDARY_DATETIME_CASES: list[BoundaryCase] = [
    # ----------------------------------------------------------------------- bit
    # SQL Server CCI uses a bitpack (enc=2 or enc=4) for BIT at scale.
    # Two non-null values only; we add duplicate labels to hit N_LABELED=6.
    BoundaryCase(
        "bit", "bit",
        [
            Row("one",    True),
            Row("zero",   False),
            Row("one2",   True),
            Row("zero2",  False),
            Row("one3",   True),
            Row("null",   None),
        ],
        filler_sql="CAST(n % 2 AS BIT)",
    ),
    # ----------------------------------------------------------- decimal(9,4)
    # Precision ≤ 9 → CCI stores as int32 (4-byte scaled integer).
    BoundaryCase(
        "decimal_9_4", "decimal(9,4)",
        [
            Row("min",     Decimal("-99999.9999")),
            Row("max",     Decimal("99999.9999")),
            Row("sec_min", Decimal("-99999.9998")),
            Row("sec_max", Decimal("99999.9998")),
            Row("zero",    Decimal("0.0000")),
            Row("null",    None),
        ],
        filler_sql="CAST((n % 10000) * 0.0001 AS DECIMAL(9,4))",
    ),
    # ---------------------------------------------------------- decimal(18,4)
    # 9 < precision ≤ 18 → CCI stores as int64 (8-byte scaled integer).
    BoundaryCase(
        "decimal_18_4", "decimal(18,4)",
        [
            Row("min",     Decimal("-99999999999999.9999")),
            Row("max",     Decimal("99999999999999.9999")),
            Row("sec_min", Decimal("-99999999999999.9998")),
            Row("sec_max", Decimal("99999999999999.9998")),
            Row("zero",    Decimal("0.0000")),
            Row("null",    None),
        ],
        filler_sql="CAST((n % 10000) AS DECIMAL(18,4))",
    ),
    # ----------------------------------------------------------------------- date
    # Stored as a 3-byte integer (days since 0001-01-01).
    # Min = day 0; max = day 3,652,058.
    BoundaryCase(
        "date", "date",
        [
            Row("min",     dt.date(1, 1, 1)),
            Row("max",     dt.date(9999, 12, 31)),
            Row("sec_min", dt.date(1, 1, 2)),
            Row("sec_max", dt.date(9999, 12, 30)),
            Row("mid",     dt.date(2000, 1, 1)),
            Row("null",    None),
        ],
        filler_sql="DATEADD(day, n, '2000-01-01')",
    ),
    # ------------------------------------------------------------------ datetime
    # 8-byte format: uint32 ticks (1/300 s), int32 days since 1900-01-01.
    # Min = 1753-01-01 (SQL Server lower bound for classic datetime).
    # Max tick = 299; SQL Server returns it ms-rounded as .997 (997_000 µs).
    BoundaryCase(
        "datetime", "datetime",
        [
            Row("min",     _DATETIME_MIN),
            Row("max",     _DATETIME_MAX),
            Row("sec_min", _DATETIME_SEC_MIN),
            Row("sec_max", _DATETIME_SEC_MAX),
            Row("mid",     dt.datetime(2000, 1, 1, 12, 0, 0)),
            Row("null",    None),
        ],
        filler_sql="CAST(DATEADD(day, n, '2000-01-01') AS DATETIME)",
    ),
    # --------------------------------------------------------------- datetime2(3)
    # Scale 3 = millisecond precision → Python datetime round-trip is exact.
    # Min = 0001-01-01 00:00:00.000; max = 9999-12-31 23:59:59.999.
    BoundaryCase(
        "datetime2_3", "datetime2(3)",
        [
            Row("min",     dt.datetime(1, 1, 1, 0, 0, 0, 0)),
            Row("max",     dt.datetime(9999, 12, 31, 23, 59, 59, 999_000)),
            Row("sec_min", dt.datetime(1, 1, 1, 0, 0, 0, 1_000)),
            Row("sec_max", dt.datetime(9999, 12, 31, 23, 59, 59, 998_000)),
            Row("mid",     dt.datetime(2000, 1, 1, 12, 0, 0, 500_000)),
            Row("null",    None),
        ],
        filler_sql="CAST(DATEADD(ms, n % 86400000, CAST(N'2000-01-01 00:00:00.000' AS DATETIME2(3))) AS DATETIME2(3))",
    ),
    # ------------------------------------------------------------------ time(3)
    # Scale 3 = millisecond time-of-day; exact Python round-trip.
    BoundaryCase(
        "time_3", "time(3)",
        [
            Row("min",     dt.time(0, 0, 0, 0)),
            Row("max",     dt.time(23, 59, 59, 999_000)),
            Row("sec_min", dt.time(0, 0, 0, 1_000)),
            Row("sec_max", dt.time(23, 59, 59, 998_000)),
            Row("mid",     dt.time(12, 0, 0, 0)),
            Row("null",    None),
        ],
        filler_sql="CAST(DATEADD(ms, n % 86400000, CAST(N'00:00:00.000' AS TIME(3))) AS TIME(3))",
    ),
    # --------------------------------------------------------------- smalldatetime
    # 4-byte: uint16 minutes since midnight, uint16 days since 1900-01-01.
    # Min = 1900-01-01 00:00; max = 2079-06-06 23:59.
    BoundaryCase(
        "smalldatetime", "smalldatetime",
        [
            Row("min",     dt.datetime(1900, 1, 1, 0, 0, 0, 0)),
            Row("max",     dt.datetime(2079, 6, 6, 23, 59, 0, 0)),
            Row("sec_min", dt.datetime(1900, 1, 1, 0, 1, 0, 0)),
            Row("sec_max", dt.datetime(2079, 6, 6, 23, 58, 0, 0)),
            Row("mid",     dt.datetime(2000, 1, 1, 12, 0, 0, 0)),
            Row("null",    None),
        ],
        filler_sql="CAST(DATEADD(day, n % 60000, '1950-01-01') AS SMALLDATETIME)",
    ),
    # --------------------------------------------------------- datetimeoffset(3)
    # datetime2(3) + int16 UTC offset in minutes.
    # Tests:
    #   min/max — datetime extremes at UTC+0
    #   pos_off  — +14:00 (maximum positive offset, East/West boundary)
    #   neg_off  — -14:00 (maximum negative offset)
    # The stored offset is preserved: mssqlbak returns a tz-aware datetime
    # whose tzinfo equals the stored offset.
    BoundaryCase(
        "datetimeoffset_3", "datetimeoffset(3)",
        [
            Row("min",     dt.datetime(1, 1, 1, 0, 0, 0, 0,
                                       tzinfo=dt.timezone.utc)),
            Row("max",     dt.datetime(9999, 12, 31, 23, 59, 59, 999_000,
                                       tzinfo=dt.timezone.utc)),
            Row("sec_min", dt.datetime(1, 1, 1, 0, 0, 0, 1_000,
                                       tzinfo=dt.timezone.utc)),
            Row("pos_off", dt.datetime(2000, 1, 1, 12, 0, 0, 0,
                                       tzinfo=dt.timezone(dt.timedelta(hours=14)))),
            Row("neg_off", dt.datetime(2000, 1, 1, 12, 0, 0, 0,
                                       tzinfo=dt.timezone(dt.timedelta(hours=-14)))),
            Row("null",    None),
        ],
        filler_sql=(
            "CAST(DATEADD(ms, n % 86400000,"
            " CAST(N'2000-01-01 00:00:00.000 +00:00' AS DATETIMEOFFSET(3)))"
            " AS DATETIMEOFFSET(3))"
        ),
    ),
]

DATETIME_CASE_BY_NAME: dict[str, BoundaryCase] = {
    c.name: c for c in BOUNDARY_DATETIME_CASES
}
