"""Boundary-value test matrix for large-row-group columnstore tests.

Each BoundaryCase produces exactly N_LABELED boundary rows plus N_FILLER filler
rows in the fixture.  The labeled rows cover MIN, MAX, second-to-MIN,
second-to-MAX, an in-range value, and NULL.  The filler rows push the row group
past the ~1024-row threshold so SQL Server uses enc=4 compression in the
clustered columnstore index.

Key regression cases:
  bigint / money with MIN value
    enc=4 uses 2^63 as null sentinel (not 0) when mn == INT64_MIN.
    With 4 rows the fixture stays in enc=1; with 1200 rows it uses enc=4 so
    the special-sentinel code path is exercised for the first time.
  second-to-MIN / second-to-MAX for all numeric types
    Catches off-by-one errors in the ``mn + (stored - 1) * magnitude`` formula
    used by enc=1 decoding.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from decimal import Decimal

from tools.typematrix import Row

N_LABELED = 6     # boundary rows per table (validated by tests)
N_FILLER = 1194   # filler rows; total = N_LABELED + N_FILLER = 1200


def _f32(x: float) -> float:
    """Round *x* to the nearest IEEE 754 float32 value."""
    return struct.unpack("<f", struct.pack("<f", x))[0]


# Exact float32 maximum finite value (0x7F7FFFFF).
_REAL_MAX = struct.unpack("<f", bytes([0xFF, 0xFF, 0x7F, 0x7F]))[0]


@dataclass(frozen=True)
class BoundaryCase:
    """One numeric type with its boundary rows and a SQL filler expression."""

    name: str
    sql_type: str
    rows: list[Row]     # N_LABELED rows; label is the key for test lookups
    filler_sql: str     # SQL expression for filler INSERT; references CTE column ``n``

    @property
    def labels(self) -> list[str]:
        return [r.label for r in self.rows]


BOUNDARY_CASES: list[BoundaryCase] = [
    # --------------------------------------------------------------------- bigint
    # The enc=4 null-sentinel collision (mn == INT64_MIN → sentinel = 2^63)
    # only surfaces in a large row group that contains the type minimum value.
    BoundaryCase(
        "bigint", "bigint",
        [
            Row("min",     -9223372036854775808),
            Row("max",     9223372036854775807),
            Row("sec_min", -9223372036854775807),
            Row("sec_max", 9223372036854775806),
            Row("zero",    0),
            Row("null",    None),
        ],
        filler_sql="CAST(n + 1000 AS BIGINT)",
    ),
    # ----------------------------------------------------------------------- int
    BoundaryCase(
        "int", "int",
        [
            Row("min",     -2147483648),
            Row("max",     2147483647),
            Row("sec_min", -2147483647),
            Row("sec_max", 2147483646),
            Row("zero",    0),
            Row("null",    None),
        ],
        filler_sql="CAST(n + 1000 AS INT)",
    ),
    # ------------------------------------------------------------------ smallint
    BoundaryCase(
        "smallint", "smallint",
        [
            Row("min",     -32768),
            Row("max",     32767),
            Row("sec_min", -32767),
            Row("sec_max", 32766),
            Row("zero",    0),
            Row("null",    None),
        ],
        filler_sql="CAST((n % 100) AS SMALLINT)",
    ),
    # ------------------------------------------------------------------ tinyint
    # Tinyint has no negative values; use mid=127 instead of zero.
    BoundaryCase(
        "tinyint", "tinyint",
        [
            Row("min",     0),
            Row("max",     255),
            Row("sec_min", 1),
            Row("sec_max", 254),
            Row("mid",     127),
            Row("null",    None),
        ],
        filler_sql="CAST((n % 200) AS TINYINT)",
    ),
    # ----------------------------------------------------------------------- money
    # money is stored as int64 × 10000; its minimum value maps to INT64_MIN so
    # the same enc=4 null-sentinel fix applies as for bigint.
    BoundaryCase(
        "money", "money",
        [
            Row("min",     Decimal("-922337203685477.5808")),
            Row("max",     Decimal("922337203685477.5807")),
            Row("sec_min", Decimal("-922337203685477.5807")),
            Row("sec_max", Decimal("922337203685477.5806")),
            Row("zero",    Decimal("0.0000")),
            Row("null",    None),
        ],
        filler_sql="CAST(n AS MONEY)",
    ),
    # ---------------------------------------------------------------- smallmoney
    # smallmoney is int32 × 10000; its minimum (INT32_MIN) does NOT trigger the
    # INT64_MIN special case.  Tests normal enc=1/enc=4 decoding of a 4-byte type.
    BoundaryCase(
        "smallmoney", "smallmoney",
        [
            Row("min",     Decimal("-214748.3648")),
            Row("max",     Decimal("214748.3647")),
            Row("sec_min", Decimal("-214748.3647")),
            Row("sec_max", Decimal("214748.3646")),
            Row("zero",    Decimal("0.0000")),
            Row("null",    None),
        ],
        filler_sql="CAST((n % 200000) AS SMALLMONEY)",
    ),
    # ----------------------------------------------------------------------- real
    # SQL Server stores REAL (float32) values as 8-byte float64 in enc=4 segments.
    # Min/max use the exact float32 bit pattern (0xFF7FFFFF / 0x7F7FFFFF).
    BoundaryCase(
        "real", "real",
        [
            Row("min",     -_REAL_MAX),
            Row("max",     _REAL_MAX),
            Row("sec_min", _f32(-3.4e38)),
            Row("sec_max", _f32(3.4e38)),
            Row("zero",    0.0),
            Row("null",    None),
        ],
        filler_sql="CAST(n AS REAL)",
    ),
    # ---------------------------------------------------------------------- float
    BoundaryCase(
        "float", "float",
        [
            Row("min",     -1.7976931348623157e308),
            Row("max",     1.7976931348623157e308),
            Row("sec_min", -1.7e308),
            Row("sec_max", 1.7e308),
            Row("zero",    0.0),
            Row("null",    None),
        ],
        filler_sql="CAST(n AS FLOAT)",
    ),
]

CASE_BY_NAME: dict[str, BoundaryCase] = {c.name: c for c in BOUNDARY_CASES}
