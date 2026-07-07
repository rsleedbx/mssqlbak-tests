"""Partitioned columnstore ARCHIVE null-encoding tests (Gap 5 — partition supplement).

``archive_columnstore_partition_full.bak`` — four 140,000-row tables on a 4-partition CCI,
each built with a different REBUILD variant to expose how SQL Server writes
ARCHIVE (enc_type=5) segments when partitions carry mixed compression levels.

Partition layout (partition function pf_archive_part, RANGE LEFT):

  Partition | id range           | rows
  ----------|--------------------|-------
  1         | 1 – 35,000         | 35,000
  2         | 35,001 – 70,000    | 35,000
  3         | 70,001 – 105,000   | 35,000
  4         | 105,001 – 140,000  | 35,000

Each partition has 35,000 rows — above the 32,767-row threshold that forces the
multi-sub-block ARCHIVE format (enc_type=5).

Null pattern (identical across all four tables):
  code  CHAR(10)  NULL every 500th row  → 280 NULLs total, 70 per partition
  zip   CHAR(10)  NULL every 1,000th row → 140 NULLs total, 35 per partition

Four scenarios (tables):

  archive_part_single     — Scenario A: partition 1 ARCHIVE, 2-4 COLUMNSTORE
  archive_part_all        — Scenario B: all partitions ARCHIVE
  archive_part_mixed      — Scenario C: partitions 1+3 ARCHIVE, 2+4 COLUMNSTORE
  archive_part_roundtrip  — Scenario D: all ARCHIVE then rebuilt back to COLUMNSTORE

The ``archive_part_mixed`` table is the most diagnostic for Gap 5: partitions
2 and 4 use standard COLUMNSTORE (already decoded correctly) and act as an
internal control.  If those partitions return the correct null counts but
partitions 1 and 3 return 0, the bug is strictly in the enc_type=5 path.

Fixture generation::

    python -m tools.fixture_run --fixture-dir <dir> archive-columnstore-partition
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows


def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _tables(path: Path) -> dict:
    return {t.name: t for t in recover_schema(_store(path)).tables}


def _rows(path: Path, table: str) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# Fixture constants — must match make_archive_columnstore_partition_fixture.py
# ---------------------------------------------------------------------------
_TOTAL_ROWS = 140_000
_PARTITION_ROWS = 35_000
_CODE_NULL_EVERY = 500
_ZIP_NULL_EVERY = 1_000

_EXPECTED_CODE_NULLS = _TOTAL_ROWS // _CODE_NULL_EVERY   # 280
_EXPECTED_ZIP_NULLS = _TOTAL_ROWS // _ZIP_NULL_EVERY     # 140

_CODE_NULLS_PER_PARTITION = _PARTITION_ROWS // _CODE_NULL_EVERY   # 70
_ZIP_NULLS_PER_PARTITION = _PARTITION_ROWS // _ZIP_NULL_EVERY     # 35

# Partition id boundaries (RANGE LEFT on pf_archive_part)
_P1 = range(1, _PARTITION_ROWS + 1)              # 1 – 35,000
_P2 = range(_PARTITION_ROWS + 1, _PARTITION_ROWS * 2 + 1)    # 35,001 – 70,000
_P3 = range(_PARTITION_ROWS * 2 + 1, _PARTITION_ROWS * 3 + 1)  # 70,001 – 105,000
_P4 = range(_PARTITION_ROWS * 3 + 1, _TOTAL_ROWS + 1)         # 105,001 – 140,000

_ALL_TABLES = (
    "archive_part_single",
    "archive_part_all",
    "archive_part_mixed",
    "archive_part_roundtrip",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _null_count(rows: list[dict], col: str, id_range: range | None = None) -> int:
    if id_range is None:
        return sum(1 for r in rows if r[col] is None)
    return sum(1 for r in rows if r["id"] in id_range and r[col] is None)


# ---------------------------------------------------------------------------
# Classify
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("table", _ALL_TABLES)
def test_archive_part_classify_supported(
    fixture_bak_archive_columnstore_partition: Path,
    table: str,
) -> None:
    """All four partitioned tables are CCI — classified as supported."""
    tables = _tables(fixture_bak_archive_columnstore_partition)
    result = classify_table(tables[table])
    assert result.supported, f"{table}: expected supported, got: {result.reason}"


# ---------------------------------------------------------------------------
# Row counts
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("table", _ALL_TABLES)
def test_archive_part_row_count(
    fixture_bak_archive_columnstore_partition: Path,
    table: str,
) -> None:
    """Each table contains exactly 140,000 rows."""
    rows = _rows(fixture_bak_archive_columnstore_partition, table)
    assert len(rows) == _TOTAL_ROWS, (
        f"{table}: expected {_TOTAL_ROWS:,} rows, got {len(rows):,}"
    )


# ---------------------------------------------------------------------------
# Scenario A — archive_part_single
# Partition 1: ARCHIVE (enc_type=5)  |  Partitions 2-4: standard COLUMNSTORE
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_single_total_code_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_single: 280 code NULLs across all partitions."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_single")
    n = _null_count(rows, "code")
    assert n == _EXPECTED_CODE_NULLS, (
        f"code: expected {_EXPECTED_CODE_NULLS} NULLs, got {n} (Gap-5 enc_type=5)"
    )


@pytest.mark.fixture
def test_single_total_zip_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_single: 140 zip NULLs across all partitions."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_single")
    n = _null_count(rows, "zip")
    assert n == _EXPECTED_ZIP_NULLS, (
        f"zip: expected {_EXPECTED_ZIP_NULLS} NULLs, got {n} (Gap-5 enc_type=5)"
    )


@pytest.mark.fixture
def test_single_p1_code_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_single partition 1 (ARCHIVE): 70 code NULLs.

    This is the ARCHIVE partition; Gap 5 causes 0 NULLs here.
    """
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_single")
    n = _null_count(rows, "code", _P1)
    assert n == _CODE_NULLS_PER_PARTITION, (
        f"p1 code: expected {_CODE_NULLS_PER_PARTITION} NULLs, got {n} "
        "(Gap-5 enc_type=5 — ARCHIVE partition)"
    )


@pytest.mark.fixture
def test_single_p2_code_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_single partition 2 (COLUMNSTORE): 70 code NULLs — internal control."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_single")
    n = _null_count(rows, "code", _P2)
    assert n == _CODE_NULLS_PER_PARTITION, (
        f"p2 code: expected {_CODE_NULLS_PER_PARTITION} NULLs, got {n} "
        "(standard COLUMNSTORE partition — should not fail)"
    )


# ---------------------------------------------------------------------------
# Scenario B — archive_part_all
# All partitions: ARCHIVE (enc_type=5)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_all_total_code_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_all: 280 code NULLs — all partitions ARCHIVE."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_all")
    n = _null_count(rows, "code")
    assert n == _EXPECTED_CODE_NULLS, (
        f"code: expected {_EXPECTED_CODE_NULLS} NULLs, got {n} (Gap-5 enc_type=5)"
    )


@pytest.mark.fixture
def test_all_total_zip_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_all: 140 zip NULLs — all partitions ARCHIVE."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_all")
    n = _null_count(rows, "zip")
    assert n == _EXPECTED_ZIP_NULLS, (
        f"zip: expected {_EXPECTED_ZIP_NULLS} NULLs, got {n} (Gap-5 enc_type=5)"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("part,id_range", [
    (1, _P1), (2, _P2), (3, _P3), (4, _P4),
])
def test_all_per_partition_code_nulls(
    fixture_bak_archive_columnstore_partition: Path,
    part: int,
    id_range: range,
) -> None:
    """archive_part_all: each partition has exactly 70 code NULLs."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_all")
    n = _null_count(rows, "code", id_range)
    assert n == _CODE_NULLS_PER_PARTITION, (
        f"p{part} code: expected {_CODE_NULLS_PER_PARTITION} NULLs, got {n} "
        "(Gap-5 enc_type=5)"
    )


# ---------------------------------------------------------------------------
# Scenario C — archive_part_mixed
# Partitions 1+3: ARCHIVE (enc_type=5, failing)
# Partitions 2+4: standard COLUMNSTORE (internal control)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_mixed_total_code_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_mixed: 280 code NULLs total."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_mixed")
    n = _null_count(rows, "code")
    assert n == _EXPECTED_CODE_NULLS, (
        f"code: expected {_EXPECTED_CODE_NULLS} NULLs, got {n}"
    )


@pytest.mark.fixture
def test_mixed_total_zip_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_mixed: 140 zip NULLs total."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_mixed")
    n = _null_count(rows, "zip")
    assert n == _EXPECTED_ZIP_NULLS, (
        f"zip: expected {_EXPECTED_ZIP_NULLS} NULLs, got {n}"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("part,id_range", [(2, _P2), (4, _P4)])
def test_mixed_columnstore_partitions_code_nulls(
    fixture_bak_archive_columnstore_partition: Path,
    part: int,
    id_range: range,
) -> None:
    """archive_part_mixed partitions 2+4 (COLUMNSTORE): 70 code NULLs each.

    These are the internal control partitions.  If they pass but partitions 1+3
    return 0 NULLs, Gap 5 is confirmed as strictly an enc_type=5 decode failure.
    """
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_mixed")
    n = _null_count(rows, "code", id_range)
    assert n == _CODE_NULLS_PER_PARTITION, (
        f"p{part} code (COLUMNSTORE control): expected {_CODE_NULLS_PER_PARTITION} "
        f"NULLs, got {n} — should not fail"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("part,id_range", [(2, _P2), (4, _P4)])
def test_mixed_columnstore_partitions_zip_nulls(
    fixture_bak_archive_columnstore_partition: Path,
    part: int,
    id_range: range,
) -> None:
    """archive_part_mixed partitions 2+4 (COLUMNSTORE): 35 zip NULLs each."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_mixed")
    n = _null_count(rows, "zip", id_range)
    assert n == _ZIP_NULLS_PER_PARTITION, (
        f"p{part} zip (COLUMNSTORE control): expected {_ZIP_NULLS_PER_PARTITION} "
        f"NULLs, got {n} — should not fail"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("part,id_range", [(1, _P1), (3, _P3)])
def test_mixed_archive_partitions_code_nulls(
    fixture_bak_archive_columnstore_partition: Path,
    part: int,
    id_range: range,
) -> None:
    """archive_part_mixed partitions 1+3 (ARCHIVE): 70 code NULLs each.

    Gap 5: enc_type=5 null decoding — these return 0 NULLs until the bug is fixed.
    """
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_mixed")
    n = _null_count(rows, "code", id_range)
    assert n == _CODE_NULLS_PER_PARTITION, (
        f"p{part} code (ARCHIVE): expected {_CODE_NULLS_PER_PARTITION} NULLs, got {n} "
        "(Gap-5 enc_type=5 — ARCHIVE partition)"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("part,id_range", [(1, _P1), (3, _P3)])
def test_mixed_archive_partitions_zip_nulls(
    fixture_bak_archive_columnstore_partition: Path,
    part: int,
    id_range: range,
) -> None:
    """archive_part_mixed partitions 1+3 (ARCHIVE): 35 zip NULLs each.

    Gap 5: enc_type=5 null decoding — these return 0 NULLs until the bug is fixed.
    """
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_mixed")
    n = _null_count(rows, "zip", id_range)
    assert n == _ZIP_NULLS_PER_PARTITION, (
        f"p{part} zip (ARCHIVE): expected {_ZIP_NULLS_PER_PARTITION} NULLs, got {n} "
        "(Gap-5 enc_type=5 — ARCHIVE partition)"
    )


# ---------------------------------------------------------------------------
# Non-null value spot-checks (Scenario C — mixed, using control partitions)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_mixed_non_null_values_control_partition(
    fixture_bak_archive_columnstore_partition: Path,
) -> None:
    """Non-null values in partition 2 (COLUMNSTORE) decode correctly.

    SQL Server stores CAST(n AS CHAR(10)) — right-padded to 10 chars.
    After rstrip the value equals the integer string.
    """
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_mixed")
    by_id = {r["id"]: r for r in rows}
    # Sample ids in partition 2 (35,001 – 70,000) that are not multiples of 500.
    for sample_id in (35_001, 40_001, 55_333, 69_999):
        r = by_id[sample_id]
        assert r["code"] is not None, f"id={sample_id}: code unexpectedly NULL"
        assert r["code"].rstrip() == str(sample_id), (
            f"id={sample_id}: code {r['code']!r} != {str(sample_id)!r}"
        )


# ---------------------------------------------------------------------------
# Scenario D — archive_part_roundtrip
# All partitions: ARCHIVE → then rebuilt back to standard COLUMNSTORE
# Final state: all partitions standard COLUMNSTORE
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_roundtrip_total_code_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_roundtrip: 280 code NULLs — all partitions reverted to COLUMNSTORE.

    After the second REBUILD (DATA_COMPRESSION = COLUMNSTORE) the segments should
    be indistinguishable from a table that was never compressed with ARCHIVE.
    """
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_roundtrip")
    n = _null_count(rows, "code")
    assert n == _EXPECTED_CODE_NULLS, (
        f"code: expected {_EXPECTED_CODE_NULLS} NULLs, got {n} "
        "(roundtrip ARCHIVE→COLUMNSTORE)"
    )


@pytest.mark.fixture
def test_roundtrip_total_zip_nulls(fixture_bak_archive_columnstore_partition: Path) -> None:
    """archive_part_roundtrip: 140 zip NULLs — all partitions reverted to COLUMNSTORE."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_roundtrip")
    n = _null_count(rows, "zip")
    assert n == _EXPECTED_ZIP_NULLS, (
        f"zip: expected {_EXPECTED_ZIP_NULLS} NULLs, got {n} "
        "(roundtrip ARCHIVE→COLUMNSTORE)"
    )


@pytest.mark.fixture
@pytest.mark.parametrize("part,id_range", [
    (1, _P1), (2, _P2), (3, _P3), (4, _P4),
])
def test_roundtrip_per_partition_code_nulls(
    fixture_bak_archive_columnstore_partition: Path,
    part: int,
    id_range: range,
) -> None:
    """archive_part_roundtrip: each partition has exactly 70 code NULLs after revert."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_roundtrip")
    n = _null_count(rows, "code", id_range)
    assert n == _CODE_NULLS_PER_PARTITION, (
        f"p{part} code: expected {_CODE_NULLS_PER_PARTITION} NULLs, got {n} "
        "(roundtrip ARCHIVE→COLUMNSTORE)"
    )


@pytest.mark.fixture
def test_roundtrip_non_null_values(fixture_bak_archive_columnstore_partition: Path) -> None:
    """Non-null values decode correctly after ARCHIVE→COLUMNSTORE round-trip."""
    rows = _rows(fixture_bak_archive_columnstore_partition, "archive_part_roundtrip")
    by_id = {r["id"]: r for r in rows}
    for sample_id in (1, 35_001, 70_001, 105_001, 139_999):
        r = by_id[sample_id]
        assert r["code"] is not None, f"id={sample_id}: code unexpectedly NULL"
        assert r["code"].rstrip() == str(sample_id), (
            f"id={sample_id}: code {r['code']!r} != {str(sample_id)!r}"
        )
