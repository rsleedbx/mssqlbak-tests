"""Per-data-type value matrix — the reference values for the .bak parser.

This module is the single source of truth shared by the fixture generator
(``tools/make_fixture.py``) and the parser tests. For every SQL Server data
type it defines a small set of rows (``low``/``high``/``mid`` plus ``null``)
whose ``value`` field is the *canonical Python value* that a correct parser
must reproduce after reading the corresponding page bytes back out of the
backup.

``mid`` values are produced from a single seeded RNG so the matrix — and the
``.bak`` built from it — is byte-for-byte deterministic across runs.
"""

from __future__ import annotations

import datetime as dt
import random
import string
import struct
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

SEED = 20260602

# datetime2(7) high: SQL Server stores 100 ns ticks, but Python datetime only
# resolves to microseconds, so the canonical value is the microsecond floor.
_MAX_DATETIME = dt.datetime(9999, 12, 31, 23, 59, 59, 999999)
_MIN_DATETIME = dt.datetime(1, 1, 1, 0, 0, 0, 0)

# datetime (xtype 61): 1753-01-01 .. 9999-12-31, 1/300 s resolution.  We only use
# whole-second values so they are exact multiples of 1/300 s and round-trip
# losslessly through the engine.
_DATETIME_MIN = dt.datetime(1753, 1, 1, 0, 0, 0)
_DATETIME_MAX = dt.datetime(9999, 12, 31, 23, 59, 59)
# smalldatetime (xtype 58): 1900-01-01 .. 2079-06-06, 1-minute resolution (the
# seconds component is always 0), so we only use whole-minute values.
_SMALLDATETIME_MIN = dt.datetime(1900, 1, 1, 0, 0, 0)
_SMALLDATETIME_MAX = dt.datetime(2079, 6, 6, 23, 59, 0)
_UTC = dt.timezone.utc

_BLOB_CAP = 1_048_576  # 1 MiB cap for the varbinary(max) ``mid`` blob


@dataclass(frozen=True)
class Row:
    """One inserted row: a ``label`` and the canonical Python ``value``.

    ``sql`` overrides the generated literal for the ``v`` column when the value
    needs an explicit cast (e.g. to pin a ``sql_variant`` base type).
    """

    label: str
    value: Any
    sql: str | None = None


@dataclass(frozen=True)
class TypeCase:
    """All rows that exercise a single SQL Server column type.

    ``auto`` marks an engine-populated column (e.g. ``rowversion``) whose value
    cannot be inserted: the fixture inserts only the ``label`` and the reference
    matrix has no known value to assert, so such cases are validated by the
    engine-diff test alone.

    ``canonical`` is the engine-neutral type name used by the ``SqlDialect``
    layer (e.g. ``"int32"``, ``"timestamptz"``, ``"varchar"``).  It is empty
    for types with no cross-engine equivalent (CLR UDTs, deprecated LOBs).
    Empty string means "SQL Server only — no dialect mapping needed".
    """

    name: str
    sql_type: str
    nullable: bool
    rows: list[Row]
    auto: bool = False
    # SQL projection the engine-diff uses to read the value back. Defaults to the
    # column itself; CLR types need a text accessor (``v.STAsText()`` for spatial,
    # ``v.ToString()`` for hierarchyid) so the engine returns the same canonical
    # string the parser decodes to instead of the raw CLR blob.
    engine_value_sql: str | None = None
    # Engine-neutral type name for SqlDialect mapping.  Set for all portable
    # types; left empty for SQL-Server-specific types (CLR UDTs, deprecated LOBs).
    canonical: str = ""
    # For types that cannot appear in the standard typecoverage fixture (e.g.
    # SS2025-only types), set ``fallback_xtype`` to register the type_id in
    # ``_matrix_results`` even when no corresponding table exists in the fixture.
    fallback_xtype: int | None = None


def _f32(x: float) -> float:
    """Round ``x`` to its float32 representation (what a ``real`` column stores)."""
    return struct.unpack("<f", struct.pack("<f", x))[0]


def _rand_ascii(rng: random.Random, n: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(rng.choice(alphabet) for _ in range(n))


def _rand_date(rng: random.Random) -> dt.date:
    return dt.date.fromordinal(rng.randint(dt.date.min.toordinal(), dt.date.max.toordinal()))


def _rand_datetime(rng: random.Random) -> dt.datetime:
    d = _rand_date(rng)
    micro = rng.randint(0, 86_400_000_000 - 1)
    secs, us = divmod(micro, 1_000_000)
    hh, rem = divmod(secs, 3600)
    mm, ss = divmod(rem, 60)
    return dt.datetime(d.year, d.month, d.day, hh, mm, ss, us)


def _rand_time(rng: random.Random) -> dt.time:
    micro = rng.randint(0, 86_400_000_000 - 1)
    return (dt.datetime.min + dt.timedelta(microseconds=micro)).time()


def _rand_datetime_seconds(rng: random.Random, lo: dt.datetime, hi: dt.datetime) -> dt.datetime:
    span = int((hi - lo).total_seconds())
    return lo + dt.timedelta(seconds=rng.randint(0, span))


def _rand_smalldatetime(rng: random.Random, lo: dt.datetime, hi: dt.datetime) -> dt.datetime:
    span = int((hi - lo).total_seconds()) // 60
    return lo + dt.timedelta(minutes=rng.randint(0, span))


def _rand_datetimeoffset(rng: random.Random) -> dt.datetime:
    base = _rand_datetime(rng)
    off_min = rng.randint(-14 * 60, 14 * 60)
    return base.replace(tzinfo=dt.timezone(dt.timedelta(minutes=off_min)))


def _nullable(rows: list[Row]) -> list[Row]:
    return [*rows, Row("null", None)]


def _build_cases() -> list[TypeCase]:
    rng = random.Random(SEED)

    def case(
        name: str,
        sql_type: str,
        low: Any,
        high: Any,
        mid: Any,
        canonical: str = "",
    ) -> TypeCase:
        rows = _nullable([Row("low", low), Row("high", high), Row("mid", mid)])
        return TypeCase(name=name, sql_type=sql_type, nullable=True, rows=rows,
                        canonical=canonical)

    cases: list[TypeCase] = [
        case("tinyint", "tinyint", 0, 255, rng.randint(0, 255), canonical="int8"),
        case("smallint", "smallint", -32768, 32767, rng.randint(-32768, 32767), canonical="int16"),
        case("int", "int", -2147483648, 2147483647, rng.randint(-2147483648, 2147483647), canonical="int32"),
        case(
            "bigint",
            "bigint",
            -9223372036854775808,
            9223372036854775807,
            rng.randint(-9223372036854775808, 9223372036854775807),
            canonical="int64",
        ),
        case("bit", "bit", False, True, bool(rng.randint(0, 1)), canonical="bool"),
        case(
            "decimal_38_10",
            "decimal(38,10)",
            Decimal("-9999999999999999999999999999.9999999999"),
            Decimal("9999999999999999999999999999.9999999999"),
            Decimal(rng.randint(-(10**38 - 1), 10**38 - 1)).scaleb(-10),
            canonical="decimal",
        ),
        case(
            "numeric_18_4",
            "numeric(18,4)",
            Decimal("-99999999999999.9999"),
            Decimal("99999999999999.9999"),
            Decimal(rng.randint(-(10**18 - 1), 10**18 - 1)).scaleb(-4),
            canonical="numeric",
        ),
        case(
            "money",
            "money",
            Decimal("-922337203685477.5808"),
            Decimal("922337203685477.5807"),
            Decimal(rng.randint(-9223372036854775808, 9223372036854775807)).scaleb(-4),
            canonical="money",
        ),
        case(
            "smallmoney",
            "smallmoney",
            Decimal("-214748.3648"),
            Decimal("214748.3647"),
            Decimal(rng.randint(-2147483648, 2147483647)).scaleb(-4),
            canonical="smallmoney",
        ),
        case("real", "real", _f32(-3.4e38), _f32(3.4e38), _f32(rng.uniform(-1e6, 1e6)), canonical="float32"),
        case("float", "float", -1.7e308, 1.7e308, rng.uniform(-1e9, 1e9), canonical="float64"),
        case("date", "date", dt.date(1, 1, 1), dt.date(9999, 12, 31), _rand_date(rng), canonical="date"),
        case(
            "datetime2_7",
            "datetime2(7)",
            _MIN_DATETIME,
            _MAX_DATETIME,
            _rand_datetime(rng),
            canonical="datetime2",
        ),
        case(
            "time_7",
            "time(7)",
            dt.time(0, 0, 0),
            dt.time(23, 59, 59, 999999),
            _rand_time(rng),
            canonical="time",
        ),
        case(
            "smalldatetime",
            "smalldatetime",
            _SMALLDATETIME_MIN,
            _SMALLDATETIME_MAX,
            _rand_smalldatetime(rng, _SMALLDATETIME_MIN, _SMALLDATETIME_MAX),
            canonical="smalldatetime",
        ),
        case(
            "datetime",
            "datetime",
            _DATETIME_MIN,
            _DATETIME_MAX,
            _rand_datetime_seconds(rng, _DATETIME_MIN, _DATETIME_MAX),
            canonical="datetime",
        ),
        case(
            "datetimeoffset_7",
            "datetimeoffset(7)",
            dt.datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=_UTC),
            dt.datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=_UTC),
            _rand_datetimeoffset(rng),
            canonical="timestamptz",
        ),
        case("char_10", "char(10)", "a".ljust(10), "z".ljust(10), _rand_ascii(rng, 10), canonical="char"),
        case(
            "nchar_10",
            "nchar(10)",
            "a".ljust(10),
            "caf\u00e9\u00fc\u00f1\u20ac".ljust(10),
            _rand_ascii(rng, 10),
            canonical="nchar",
        ),
        case("varchar_max", "varchar(max)", "", "Z" * 4000, _rand_ascii(rng, 64), canonical="varchar"),
        case(
            "nvarchar_50",
            "nvarchar(50)",
            "",
            "N" * 50,
            "caf\u00e9\U0001f600" + _rand_ascii(rng, 20),
            canonical="nvarchar",
        ),
        case(
            "binary_8",
            "binary(8)",
            b"\x00" * 8,
            b"\xff" * 8,
            rng.randbytes(8),
            canonical="binary",
        ),
        case(
            "varbinary_max",
            "varbinary(max)",
            b"",
            b"\x00",
            rng.randbytes(_BLOB_CAP),
            canonical="varbinary",
        ),
        case(
            "uniqueidentifier",
            "uniqueidentifier",
            UUID(int=0),
            UUID(int=(1 << 128) - 1),
            UUID(int=rng.getrandbits(128)),
            canonical="uuid",
        ),
        case("text", "text", "", "Z" * 4000, _rand_ascii(rng, 64)),    # no canonical: deprecated LOB
        case(
            "ntext",
            "ntext",
            "",
            "N" * 4000,
            "caf\u00e9\U0001f600" + _rand_ascii(rng, 20),
        ),                                                               # no canonical: deprecated LOB
        case("image", "image", b"", b"\x00", rng.randbytes(64)),        # no canonical: deprecated LOB
        _xml_case(rng),           # canonical="" — xml is engine-specific
        _sql_variant_case(),      # canonical="" — SQL Server only
        _rowversion_case(),       # canonical="" — SQL Server only
        _geometry_case(),         # canonical="" — CLR UDT
        _geography_case(),        # canonical="" — CLR UDT
        _hierarchyid_case(),      # canonical="" — CLR UDT
        _native_json_case(),      # canonical="" — SS2025 MSJSONB, decoded to compact JSON text
    ]
    return cases


def _geometry_case() -> TypeCase:
    """A geometry column; values are the OGC WKT the parser must reproduce.

    ``sql`` builds each value from the same WKT (SRID 0); the engine-diff reads
    it back via ``v.STAsText()``, which returns the identical canonical WKT.
    """
    wkts = [
        ("point", "POINT (3 4)"),
        ("empty", "POINT EMPTY"),
        ("line", "LINESTRING (0 0, 1 1, 2 4)"),
        ("poly", "POLYGON ((0 0, 4 0, 4 4, 0 4, 0 0))"),
        ("polyhole", "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0), (2 2, 2 4, 4 4, 4 2, 2 2))"),
        ("mpoint", "MULTIPOINT ((1 2), (3 4))"),
        ("mline", "MULTILINESTRING ((0 0, 1 1), (2 2, 3 3))"),
        ("mpoly", "MULTIPOLYGON (((0 0, 1 0, 1 1, 0 0)), ((10 10, 12 10, 12 12, 10 10)))"),
        ("gc", "GEOMETRYCOLLECTION (POINT (1 1), LINESTRING (2 2, 3 3))"),
    ]
    rows = [Row(label, wkt, sql=f"geometry::STGeomFromText('{wkt}', 0)") for label, wkt in wkts]
    return TypeCase(
        name="geometry", sql_type="geometry", nullable=True,
        rows=_nullable(rows), engine_value_sql="v.STAsText()",
    )


def _geography_case() -> TypeCase:
    """A geography column (SRID 4326); values are OGC WKT in long/lat order.

    geography stores points as (lat, long); the parser swaps to OGC (long, lat)
    so its output equals ``v.STAsText()``.
    """
    wkts = [
        ("point", "POINT (-122.3 47.6)"),
        ("line", "LINESTRING (-122 47, -121 46)"),
        ("poly", "POLYGON ((-122 47, -121 47, -121 48, -122 48, -122 47))"),
        ("mpoint", "MULTIPOINT ((-122 47), (-121 46))"),
    ]
    rows = [Row(label, wkt, sql=f"geography::STGeomFromText('{wkt}', 4326)") for label, wkt in wkts]
    return TypeCase(
        name="geography", sql_type="geography", nullable=True,
        rows=_nullable(rows), engine_value_sql="v.STAsText()",
    )


def _hierarchyid_case() -> TypeCase:
    """A hierarchyid column; values are the canonical path strings.

    ``sql`` parses each path; the engine-diff reads it back via ``v.ToString()``.
    Covers the root, single/multi level, a dotted (sub-ordinal) node, and a
    large node that exercises a wider ORDPATH bucket.
    """
    paths = [
        ("root", "/"),
        ("l1", "/1/"),
        ("l123", "/1/2/3/"),
        ("dot", "/1.1/"),
        ("big", "/100/200/"),
        ("deep", "/1/2/3/4/5/"),
    ]
    rows = [Row(label, p, sql=f"hierarchyid::Parse('{p}')") for label, p in paths]
    return TypeCase(
        name="hierarchyid", sql_type="hierarchyid", nullable=True,
        rows=_nullable(rows), engine_value_sql="v.ToString()",
    )


def _xml_case(rng: random.Random) -> TypeCase:
    """XML documents covering elements, attributes, nesting, escaping, etc.

    ``value`` is the canonical text SQL Server serialises back (matched by the
    engine-diff); ``sql`` is the literal inserted.  CDATA is normalised by the
    engine to escaped text.
    """
    rows = [
        Row("simple", "<a>1</a>"),
        Row("text", "<n>" + _rand_ascii(rng, 20) + "</n>"),
        Row("attrs", '<root id="7"><x>hi</x><y>two</y></root>'),
        Row("empty", "<e/>"),
        Row("repeat", "<r><x>1</x><x>2</x></r>"),
        Row("escape", "<t>a &lt; b &amp; c</t>"),
        Row("attresc", '<a p="x&quot;y"/>'),
        Row("cdata", "<doc>a&lt;b</doc>", sql="N'<doc><![CDATA[a<b]]></doc>'"),
        Row("long", "<b>" + "x" * 300 + "</b>"),
    ]
    return TypeCase(name="xml", sql_type="xml", nullable=True, rows=_nullable(rows))


def _sql_variant_case() -> TypeCase:
    """A sql_variant column whose rows pin several base types via explicit casts.

    The on-disk variant header carries the base type and its metadata, so each
    row decodes to the canonical Python value of whatever type it stores.
    """
    uid = UUID("3f2504e0-4f89-11d3-9a0c-0305e82c3301")
    rows = [
        Row("vint", 1234567, sql="CAST(CAST(1234567 AS int) AS sql_variant)"),
        Row("vbig", 9_000_000_000, sql="CAST(CAST(9000000000 AS bigint) AS sql_variant)"),
        Row(
            "vdec",
            Decimal("12345.678"),
            sql="CAST(CAST('12345.678' AS decimal(18,3)) AS sql_variant)",
        ),
        Row(
            "vnvc",
            "h\u00e9llo variant",
            sql="CAST(CAST(N'h\u00e9llo variant' AS nvarchar(50)) AS sql_variant)",
        ),
        Row(
            "vuid",
            uid,
            sql=f"CAST(CAST('{uid}' AS uniqueidentifier) AS sql_variant)",
        ),
        Row("vvc", "ascii var", sql="CAST(CAST('ascii var' AS varchar(50)) AS sql_variant)"),
        Row(
            "vbin",
            b"\xde\xad\xbe\xef",
            sql="CAST(CAST(0xDEADBEEF AS varbinary(50)) AS sql_variant)",
        ),
        Row(
            "vdate",
            dt.date(2021, 6, 15),
            sql="CAST(CAST('2021-06-15' AS date) AS sql_variant)",
        ),
        Row(
            "vsdt",
            dt.datetime(2021, 6, 15, 13, 45, 0),
            sql="CAST(CAST('2021-06-15 13:45:00' AS smalldatetime) AS sql_variant)",
        ),
        Row(
            "vdttm",
            dt.datetime(2021, 6, 15, 13, 45, 30),
            sql="CAST(CAST('2021-06-15 13:45:30' AS datetime) AS sql_variant)",
        ),
        Row(
            "vdt2",
            dt.datetime(2021, 6, 15, 13, 45, 30, 123456),
            sql="CAST(CAST('2021-06-15 13:45:30.1234567' AS datetime2(7)) AS sql_variant)",
        ),
        Row(
            "vtime",
            dt.time(13, 45, 30, 123456),
            sql="CAST(CAST('13:45:30.1234567' AS time(7)) AS sql_variant)",
        ),
        Row(
            "vdto",
            dt.datetime(2021, 6, 15, 13, 45, 30, 123456, tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30))),
            sql="CAST(CAST('2021-06-15 13:45:30.1234567 +05:30' AS datetimeoffset(7)) AS sql_variant)",
        ),
        Row("null", None),
        Row(
            "vmoney",
            Decimal("12.3400"),
            sql="CAST(CAST(12.34 AS money) AS sql_variant)",
        ),
        Row(
            "vsmmoney",
            Decimal("1.2300"),
            sql="CAST(CAST(1.23 AS smallmoney) AS sql_variant)",
        ),
    ]
    return TypeCase(name="sql_variant", sql_type="sql_variant", nullable=True, rows=rows)


def _rowversion_case() -> TypeCase:
    """An engine-populated rowversion column (no insertable value).

    Each inserted row gets a fresh 8-byte value from the database, so the matrix
    has no known value; the engine-diff test validates the decode instead.
    """
    rows = [Row(f"r{i}", None) for i in range(1, 4)]
    return TypeCase(name="rowversion", sql_type="rowversion", nullable=False, rows=rows, auto=True)


def _native_json_case() -> TypeCase:
    """SS2025 native JSON type (type_id 244).

    Stored on-disk as a proprietary binary JSON encoding (MSJSONB).  mssqlbak
    decodes it to compact UTF-8 JSON text.  Fixture coverage is in
    ``tests/test_native_json_coverage.py``.

    This entry exists solely to satisfy the ``test_every_supported_type_has_a_reference_case``
    invariant; the actual round-trip test is in the dedicated coverage file.

    ``fallback_xtype=244`` registers this type_id even when the standard
    typecoverage fixture (SS2022) has no ``t_native_json`` table.
    """
    rows: list[Row] = []
    return TypeCase(
        name="native_json",
        sql_type="json",
        nullable=True,
        rows=rows,
        auto=True,
        fallback_xtype=244,
    )


TYPE_CASES: list[TypeCase] = _build_cases()

_BY_NAME: dict[str, TypeCase] = {c.name: c for c in TYPE_CASES}


def expected_rows(name: str) -> list[Row]:
    """Return the rows for the case named ``name`` (raises ``ValueError`` if unknown)."""
    try:
        return _BY_NAME[name].rows
    except KeyError as exc:
        valid = ", ".join(sorted(_BY_NAME))
        raise ValueError(f"unknown type case '{name}'; valid: {valid}") from exc
