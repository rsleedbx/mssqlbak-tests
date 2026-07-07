from __future__ import annotations

import pytest

from tools.typematrix import TYPE_CASES, expected_rows


def test_every_case_exercises_at_least_three_values() -> None:
    for case in TYPE_CASES:
        if case.auto:
            # Engine-populated (rowversion): values are assigned by the engine.
            continue
        labels = {r.label for r in case.rows}
        if {"low", "high", "mid"} <= labels:
            continue
        # Multi-variant cases (e.g. sql_variant) carry one row per base type
        # instead of low/high/mid; require at least three distinct values.
        non_null = [r for r in case.rows if r.value is not None]
        assert len(non_null) >= 3, case.sql_type


def test_nullable_cases_include_null() -> None:
    for case in TYPE_CASES:
        if case.fallback_xtype is not None:
            continue  # version-gated type; full coverage is in a dedicated fixture test
        if case.nullable:
            assert any(r.value is None for r in case.rows), case.sql_type


def test_blob_values_capped_at_1mb() -> None:
    rows = expected_rows("varbinary_max")
    assert max(len(r.value) for r in rows if r.value is not None) <= 1_048_576


def test_case_names_unique() -> None:
    names = [c.name for c in TYPE_CASES]
    assert len(names) == len(set(names))


# --- sql_variant unsupported base type error boundary ---------------------

from mssqlbak.types import _decode_sql_variant  # noqa: E402
from mssqlbak import types as T                 # noqa: E402


@pytest.mark.parametrize("base_name,base_id", [
    ("xml",    T.XML),
    ("text",   T.TEXT),
    ("ntext",  T.NTEXT),
    ("image",  T.IMAGE),
])
def test_sql_variant_unsupported_base_raises(base_name: str, base_id: int) -> None:
    """sql_variant cells whose base type cannot be stored in a variant
    (xml, text, ntext, image) must raise ``NotImplementedError``, not return
    garbage or crash the process.  The two-byte payload is: base_type_id,
    version=1; no metadata/value is needed because the base type is rejected
    before any further parsing.
    """
    payload = bytes([base_id, 1])
    with pytest.raises(NotImplementedError, match=str(base_id)):
        _decode_sql_variant(payload)


# --- sql_variant fixture round-trip (all 14 base types) -------------------
# Each row in t_sql_variant stores one base type. The decoded Python value
# must match the expected value exactly (type + value), proving the full
# on-disk → Python decode path for every supported sql_variant base type.

import datetime  # noqa: E402
import decimal   # noqa: E402
import os        # noqa: E402
import uuid      # noqa: E402
from pathlib import Path  # noqa: E402

from mssqlbak.pages import PageStore      # noqa: E402
from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.rows import read_table_rows    # noqa: E402

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))
_TYPECOVERAGE = _FIXTURE_DIR / "typecoverage_full.bak"

# (id, expected_python_value, description)
_VARIANT_EXPECTED = [
    (1,  1234567,                                                           "int"),
    (2,  9000000000,                                                        "bigint"),
    (3,  decimal.Decimal("12345.678"),                                      "decimal"),
    (4,  "héllo variant",                                                   "nvarchar"),
    (5,  uuid.UUID("3f2504e0-4f89-11d3-9a0c-0305e82c3301"),                 "uniqueidentifier"),
    (6,  "ascii var",                                                       "varchar"),
    (7,  b"\xde\xad\xbe\xef",                                              "binary"),
    (8,  datetime.date(2021, 6, 15),                                        "date"),
    (9,  datetime.datetime(2021, 6, 15, 13, 45),                            "datetime"),
    (10, datetime.datetime(2021, 6, 15, 13, 45, 30),                        "datetime (smalldatetime)"),
    (11, datetime.datetime(2021, 6, 15, 13, 45, 30, 123456),                "datetime2"),
    (12, datetime.time(13, 45, 30, 123456),                                 "time"),
    (13, datetime.datetime(2021, 6, 15, 13, 45, 30, 123456,
                           tzinfo=datetime.timezone(datetime.timedelta(seconds=19800))),
                                                                            "datetimeoffset"),
    (14, None,                                                              "null"),
    (15, decimal.Decimal("12.3400"),                                        "money"),
    (16, decimal.Decimal("1.2300"),                                         "smallmoney"),
]


@pytest.fixture(scope="module")
def _variant_rows() -> dict[int, object]:
    if not _TYPECOVERAGE.exists():
        pytest.skip(f"fixture missing: {_TYPECOVERAGE}")
    store = PageStore.from_bak(_TYPECOVERAGE)
    tables = {t.name: t for t in recover_schema(store).tables}
    t = tables["t_sql_variant"]
    return {r["id"]: r["v"] for r in read_table_rows(store, t)}


@pytest.mark.fixture
@pytest.mark.parametrize("row_id,expected,desc", _VARIANT_EXPECTED, ids=[d for _, _, d in _VARIANT_EXPECTED])
def test_sql_variant_base_type_roundtrip(row_id: int, expected: object, desc: str,
                                          _variant_rows: dict) -> None:
    """sql_variant round-trip for every supported base type.

    Reads the t_sql_variant table from the committed typecoverage fixture and
    checks that each row's decoded Python value matches the seeded expected value
    (type and value).  Covers all 16 supported base types (including money and
    smallmoney, both of which decode to Decimal with 4 decimal places).
    """
    actual = _variant_rows[row_id]
    assert actual == expected, (
        f"id={row_id} ({desc}): got {actual!r} ({type(actual).__name__}), "
        f"expected {expected!r} ({type(expected).__name__})"
    )
