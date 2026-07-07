"""Tests for the columnstore row decoder (mssqlbak/columnstore.py).

Uses the ``columnstore_minimal.bak`` fixture which contains five tables
(cs_1, cs_10, cs_100, cs_1000, cs_10000), each with a clustered columnstore
index and no deltastore (every row group is compressed via
``ALTER INDEX ... REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)``).

Column schema (matches tools/columnstore_minimal.py):
    id int NOT NULL, code int NOT NULL,
    name varchar(20) NULL,       -- enc=5, returns None
    nm nvarchar(40) NULL,        -- enc=3 dictionary; verified
    ncf nchar(10) NULL,          -- enc=5, returns None
    amount decimal(18,4) NULL,   -- enc=1; verified
    qty numeric(9,2) NULL,       -- enc=1; verified
    dt datetime NULL,            -- enc=1; verified
    dt2 datetime2(3) NULL,       -- enc=1 (5-byte frac + 3-byte date); verified
    d date NULL,                 -- enc=1; verified
    t time(3) NULL,              -- enc=1 (100 ns ticks); verified
    dto datetimeoffset(3) NULL   -- enc=5, returns None

Row generation rule (tools/columnstore_minimal.py _row_literal):
    - i % 7 == 0 → all nullable columns NULL.
    - i % 5 == 0 → nm = Cyrillic 'Привет', otherwise f'name{i%10}'.
    - inst = datetime(2001,1,1) + timedelta(minutes=i, milliseconds=i%1000)
    - amount = Decimal(f'{i}.{i%10000:04d}')  (decimal(18,4))
    - qty    = Decimal(f'{i%1000000}.{i%100:02d}')  (numeric(9,2))
"""
from __future__ import annotations

import datetime as dt
import os
from decimal import Decimal
from pathlib import Path

import pytest

import json

from mssqlbak.catalog import Column, recover_schema
from mssqlbak.columnstore import read_columnstore_rows
from mssqlbak.columnstore.decode.enc5_raw import _enc5_item_to_python, _variable_text_pool_map
from mssqlbak.types import NVARCHAR
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))
_FIXTURE = _FIXTURE_DIR / "columnstore_minimal.bak"
_BASE_DT = dt.datetime(2001, 1, 1)


def test_archive_variable_text_pool_coalesces_signed_numeric_suffix_offsets() -> None:
    pool = b"-73.986099-73.991028-74.004707"
    offsets = [0, 10, 11, 20]

    pool_map = _variable_text_pool_map(pool, offsets, len(pool))

    assert pool_map[10] == b"-73.991028"
    assert pool_map[11] == b"-73.991028"


def test_archive_variable_text_pool_coalesces_decimal_suffix_offsets() -> None:
    pool = b"40.76079940.646940.755276"
    offsets = [0, 9, 11, 16]

    pool_map = _variable_text_pool_map(pool, offsets, len(pool))

    assert pool_map[9] == b"40.6469"
    assert pool_map[11] == b"40.6469"


def test_enc5_nvarchar_item_strips_double_wide_nul_padding() -> None:
    col = Column(
        name="Description",
        colid=1,
        type_id=NVARCHAR,
        max_length=200,
        precision=0,
        scale=0,
        nullable=True,
        leaf_offset=-1,
        is_variable=True,
    )
    raw = "Ride".encode("utf-16-le").replace(b"\x00", b"\x00\x00\x00")

    assert _enc5_item_to_python(raw, col) == "Ride"


def _store() -> AnyPageStore:
    if not _FIXTURE.exists():
        pytest.skip(
            f"columnstore fixture missing: {_FIXTURE} "
            "(run python -m tools.columnstore_minimal)"
        )
    return PageStore.from_bak(_FIXTURE)


def _expected_row(i: int) -> dict:
    """Reconstruct the expected column values for row i (1-indexed).

    Columns returned by the decoder only (enc=5 columns omitted since they
    produce None and are tested separately).
    """
    code = i % 50
    inst = _BASE_DT + dt.timedelta(minutes=i, milliseconds=(i % 1000))
    if i % 7 == 0:
        return {
            "id": i, "code": code,
            "nm": None, "amount": None, "qty": None,
            "dt": None, "dt2": None, "d": None, "t": None,
        }
    nm = "Привет" if i % 5 == 0 else f"name{i % 10}"
    # datetime has 1/300 s resolution; the inserted ms value rounds to the
    # nearest tick, and SQL Server returns that tick rounded back to whole
    # milliseconds (.000/.003/.007) — which is what mssqlbak now decodes to.
    dt_micro = inst.microsecond // 1000 * 1000  # ms precision
    ticks = round(dt_micro * 300 / 1_000_000)   # nearest 1/300 s tick
    micro_exact = ticks * 1_000_000 // 300
    dt_actual = _BASE_DT + dt.timedelta(
        minutes=i, microseconds=((micro_exact + 500) // 1000) * 1000
    )
    return {
        "id":     i,
        "code":   code,
        "nm":     nm,
        "amount": Decimal(f"{i}.{i % 10000:04d}"),
        "qty":    Decimal(f"{i % 1_000_000}.{i % 100:02d}"),
        "dt":     dt_actual,
        "dt2":    inst.replace(microsecond=(inst.microsecond // 1000) * 1000),
        "d":      inst.date(),
        "t":      inst.time().replace(microsecond=(inst.microsecond // 1000) * 1000),
    }


# ---------------------------------------------------------------------------
# classify_table: columnstore tables must be marked supported
# ---------------------------------------------------------------------------

def test_classify_columnstore_supported() -> None:
    store = _store()
    schema = recover_schema(store)
    cs_tables = [t for t in schema.tables if t.name.startswith("cs_")]
    assert cs_tables, "No cs_* tables found in fixture"
    for table in cs_tables:
        result = classify_table(table, store.available_files)
        assert result.supported, (
            f"{table.name} was classified as unsupported: {result.reason}"
        )


# ---------------------------------------------------------------------------
# cs_1: single-row table — simplest smoke test for every supported column
# ---------------------------------------------------------------------------

def test_cs_1_row_count() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    rows = list(read_table_rows(store, table))
    assert len(rows) == 1


def test_cs_1_integer_columns() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    assert row["id"]   == 1
    assert row["code"] == 1


def test_cs_1_nvarchar_dictionary() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    assert row["nm"] == "name1"


def test_cs_1_decimal_columns() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    assert row["amount"] == Decimal("1.0001")
    assert row["qty"]    == Decimal("1.01")


def test_cs_1_date_column() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    assert row["d"] == dt.date(2001, 1, 1)


def test_cs_1_time_column() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    # inst = datetime(2001,1,1) + timedelta(minutes=1, ms=1) → 00:01:00.001
    assert row["t"] == dt.time(0, 1, 0, 1000)


def test_cs_1_datetime_column() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    # 1 ms → nearest 1/300-s tick → 0 ticks (rounds down from 0.3)
    assert row["dt"] == dt.datetime(2001, 1, 1, 0, 1, 0, 0)


def test_cs_1_datetime2_column() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    # datetime2(3) preserves milliseconds exactly
    assert row["dt2"] == dt.datetime(2001, 1, 1, 0, 1, 0, 1000)


def test_cs_1_enc5_columns_decoded() -> None:
    """enc=5 columns (varchar, nchar, datetimeoffset) are now decoded."""
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1")
    row = list(read_table_rows(store, table))[0]
    # Row i=1: name='val1', ncf='ncf1      ' (nchar(10)), dto=2001-01-01 00:01:00.001+05:30
    assert row["name"] == "val1"
    assert row["ncf"] == "ncf1      "
    expected_dto = dt.datetime(
        2001, 1, 1, 0, 1, 0, 1000,
        tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30)),
    )
    assert row["dto"] == expected_dto


# ---------------------------------------------------------------------------
# cs_10: ten rows – null handling and dictionary multi-row encoding
# ---------------------------------------------------------------------------

def test_cs_10_row_count() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_10")
    rows = list(read_table_rows(store, table))
    assert len(rows) == 10


def test_cs_10_nullable_row_is_null(
    tmp_path: Path,  # noqa: ARG001  (inject fixture to trigger skip check)
) -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_10")
    rows = {r["id"]: r for r in read_table_rows(store, table)}
    null_row = rows[7]  # i=7, 7%7==0 → all nullable columns NULL
    assert null_row["nm"]     is None
    assert null_row["amount"] is None
    assert null_row["qty"]    is None
    assert null_row["dt"]     is None
    assert null_row["dt2"]    is None
    assert null_row["d"]      is None
    assert null_row["t"]      is None


def test_cs_10_non_null_rows_correct() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_10")
    rows = {r["id"]: r for r in read_table_rows(store, table)}
    for i in range(1, 11):
        expected = _expected_row(i)
        row = rows[i]
        for key, exp_val in expected.items():
            actual = row[key]
            assert actual == exp_val, (
                f"cs_10 row i={i} column '{key}': expected {exp_val!r}, got {actual!r}"
            )


def test_cs_10_cyrillic_nm() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_10")
    rows = {r["id"]: r for r in read_table_rows(store, table)}
    assert rows[5]["nm"] == "Привет"   # i=5, 5%5==0


# ---------------------------------------------------------------------------
# cs_100: hundred rows – enc=2 (constant-value) columns and larger blobs
# ---------------------------------------------------------------------------

def test_cs_100_row_count() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_100")
    rows = list(read_table_rows(store, table))
    assert len(rows) == 100


def test_cs_100_null_rows_present() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_100")
    rows = {r["id"]: r for r in read_table_rows(store, table)}
    # Every 7th row is null: 7, 14, 21, ..., 98
    null_ids = [i for i in range(1, 101) if i % 7 == 0]
    assert null_ids
    for nid in null_ids:
        assert rows[nid]["nm"]     is None, f"id={nid} nm should be None"
        assert rows[nid]["amount"] is None, f"id={nid} amount should be None"


def test_cs_100_sample_rows_correct() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_100")
    rows = {r["id"]: r for r in read_table_rows(store, table)}
    for i in (1, 2, 5, 10, 50, 99, 100):
        expected = _expected_row(i)
        row = rows[i]
        for key, exp_val in expected.items():
            actual = row[key]
            assert actual == exp_val, (
                f"cs_100 row i={i} column '{key}': expected {exp_val!r}, got {actual!r}"
            )


@pytest.mark.parametrize("row_id", [4231, 4281, 4331])
def test_cs_10000_datetimeoffset_values_are_not_year1(row_id: int) -> None:
    """Large enc=5 datetimeoffset segments must not decode non-null rows as year 1."""
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_10000")
    rows = {r["id"]: r for r in read_table_rows(store, table)}
    inst = _BASE_DT + dt.timedelta(minutes=row_id, milliseconds=(row_id % 1000))
    expected = inst.replace(
        microsecond=(inst.microsecond // 1000) * 1000,
        tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30)),
    )
    assert rows[row_id]["dto"] == expected


# ---------------------------------------------------------------------------
# cs_1000: thousand rows
# ---------------------------------------------------------------------------

def test_cs_1000_row_count() -> None:
    store = _store()
    schema = recover_schema(store)
    table = next(t for t in schema.tables if t.name == "cs_1000")
    rows = list(read_table_rows(store, table))
    assert len(rows) == 1000


# ---------------------------------------------------------------------------
# G44 — xVelocity v4 large string dictionary (enc=3, blob > 65 536 bytes)
#
# cs_lob_preamble2.bak contains a 1200-row columnstore table with a varchar
# column stored as an xVelocity v4 hash-dict (blob 2001) plus a sibling v7
# sorted pool (blob 23844).
#
# The G44.json sidecar carries all 1200 strings in data_id order (alphabetical
# rank) as the verifier reference.
#
# Decoder coverage:
#   • With xmhuffman (Python ≤ 3.11 wheel): all 1200 positions decode via the
#     raw-CBUF Huffman path (_decode_v4_huff_dict); sorted output → data_id.
#   • Without xmhuffman: 194 / 1200 bookmark positions decode via the v7
#     sorted-pool fallback; the remaining 1006 return None.
# ---------------------------------------------------------------------------

_G44_FIXTURE = _FIXTURE_DIR / "cs_lob_preamble2.bak"
_G44_SIDECAR = _FIXTURE_DIR / "G44.json"
_G44_FULL_COUNT = 1200
_G44_BOOKMARK_COUNT = 194


def _g44_store() -> AnyPageStore:
    if not _G44_FIXTURE.exists():
        pytest.skip(f"G44 fixture missing: {_G44_FIXTURE}")
    return PageStore.from_bak(_G44_FIXTURE)


def test_g44_large_dict_row_count() -> None:
    """cs_lob_preamble2 must contain exactly 1200 rows."""
    store = _g44_store()
    table = recover_schema(store).tables[0]
    rows = list(read_columnstore_rows(store, table))
    assert len(rows) == _G44_FULL_COUNT


def test_g44_large_dict_bookmark_coverage() -> None:
    """At least 194 bookmark positions must decode to non-None long_str.

    When xmhuffman is installed the full 1200-string Huffman path runs and all
    1200 positions are non-None.  Without xmhuffman the v7 sorted-pool
    fallback provides exactly 194 non-None positions.  This test therefore
    checks a minimum coverage floor rather than an exact count.
    """
    store = _g44_store()
    table = recover_schema(store).tables[0]
    rows = list(read_columnstore_rows(store, table))
    non_null = [r for r in rows if r.get("long_str") is not None]
    assert len(non_null) >= _G44_BOOKMARK_COUNT, (
        f"Expected ≥ {_G44_BOOKMARK_COUNT} decoded rows, got {len(non_null)}"
    )


def test_g44_large_dict_matches_verifier() -> None:
    """All decoded strings must be valid entries in the G44 verifier sidecar."""
    if not _G44_SIDECAR.exists():
        pytest.skip(f"G44 verifier sidecar missing: {_G44_SIDECAR}")
    g44_entries: set[str] = set(json.loads(_G44_SIDECAR.read_text())["entries"])
    store = _g44_store()
    table = recover_schema(store).tables[0]
    rows = list(read_columnstore_rows(store, table))
    bad = [
        (r.get("id"), r["long_str"])
        for r in rows
        if r.get("long_str") is not None and r["long_str"] not in g44_entries
    ]
    assert not bad, f"Decoded strings not in G44.json: {bad[:5]}"


def test_g44_large_dict_full_coverage() -> None:
    """With xmhuffman all 1200 long_str values must decode and match verifier.

    Skipped when xmhuffman is not installed (Python > 3.11 or wheel absent).
    """
    pytest.importorskip("xmhuffman")
    if not _G44_SIDECAR.exists():
        pytest.skip(f"G44 verifier sidecar missing: {_G44_SIDECAR}")
    g44_entries: list[str] = json.loads(_G44_SIDECAR.read_text())["entries"]
    store = _g44_store()
    table = recover_schema(store).tables[0]
    rows = list(read_columnstore_rows(store, table))
    non_null = [r["long_str"] for r in rows if r.get("long_str") is not None]
    assert len(non_null) == _G44_FULL_COUNT, (
        f"Expected all {_G44_FULL_COUNT} rows decoded, got {len(non_null)}"
    )
    bad = [s for s in non_null if s not in set(g44_entries)]
    assert not bad, f"Decoded strings not in G44.json: {bad[:5]}"
