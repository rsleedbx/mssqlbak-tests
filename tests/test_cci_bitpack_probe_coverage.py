"""Controlled known-value coverage for the CCI bit-pack dictionary decoder.

These fixtures crack and regression-guard the enc=2 (VALUE_HASH_BASED) integer
columnstore bit-pack layout — specifically the per-segment frame-of-reference
(FOR) base stored at blob offset 40 (``raw + (u32@40 - 3)`` is the absolute
dictionary index; see ``mssqlbak.columnstore._BP_FOR_BASE``).

Every table carries a monotonic ``pk`` anchor and one or more ``modK = pk % K``
columns, so each decoded row is checked against an exact arithmetic identity —
independent of the (unspecified) physical row order within a row group.

The real-world bug this protects against (``tpcxbb_1gb``
``web_clickstreams.wcs_click_date_sk`` decoding min 36898 instead of 36890) is a
multi-row-group table sharing one global dictionary where SQL Server emits
non-zero FOR bases.  These synthetic fixtures emit FOR base 0; the non-zero-base
path is corroborated by the real ``tpcxbb`` fixture in the realworld suite.

Fixture generation::

    python -m tools.fixture_run all-versions --suite cci-bitpack-probe-int
    python -m tools.fixture_run all-versions --suite cci-bitpack-probe-bigint
    python -m tools.fixture_run all-versions --suite cci-bitpack-probe-highbase
"""
from __future__ import annotations

import functools
from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows
from tools.make_cci_bitpack_probe_bigint_fixture import DT_BASE as BIGINT_BASE
from tools.make_cci_bitpack_probe_bigint_fixture import DT_MOD as BIGINT_MOD
from tools.make_cci_bitpack_probe_fixture import MODULI
from tools.make_cci_bitpack_probe_highbase_fixture import DT_BASE as HIGHBASE_BASE
from tools.make_cci_bitpack_probe_highbase_fixture import DT_MOD as HIGHBASE_MOD


@functools.lru_cache(maxsize=None)
def _rows_by_pk(path: Path, table: str) -> dict[int, dict]:
    store: AnyPageStore = PageStore.from_bak(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return {r["pk"]: r for r in read_table_rows(store, tbl, schema.obj_to_name)}


def _assert_modk(by_pk: dict[int, dict], col: str, base: int, mod: int) -> None:
    """Every row must satisfy ``col == base + (pk % mod)``."""
    mism: list[tuple[int, object, int]] = []
    for pk, row in by_pk.items():
        exp = base + (pk % mod)
        got = row[col]
        if got != exp:
            mism.append((pk, got, exp))
            if len(mism) >= 10:
                break
    assert not mism, f"{col}: {len(mism)}+ mismatches (pk, got, expected): {mism}"


# ---------------------------------------------------------------------------
# INT probe — single row group, enc=2 bit-pack, FOR base 0
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("col", list(MODULI))
def test_int_probe_modk(fixture_bak_cci_bitpack_probe: Path, col: str) -> None:
    by_pk = _rows_by_pk(fixture_bak_cci_bitpack_probe, "cci_bitpack_probe")
    assert len(by_pk) == 200_000
    _assert_modk(by_pk, col, 0, MODULI[col])


# ---------------------------------------------------------------------------
# BIGINT probe — multi row group, shared global dictionary (RLE + bit-pack)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_bigint_probe_dt(fixture_bak_cci_bitpack_probe_bigint: Path) -> None:
    store: AnyPageStore = PageStore.from_bak(fixture_bak_cci_bitpack_probe_bigint)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == "cci_bitpack_probe_bigint")
    rows = list(read_table_rows(store, tbl, schema.obj_to_name))
    assert len(rows) == 2_200_000

    by_pk = {r["pk"]: r for r in rows}
    assert len(by_pk) == 2_200_000
    _assert_modk(by_pk, "dt", BIGINT_BASE, BIGINT_MOD)


# ---------------------------------------------------------------------------
# High-base probe — enc=2 simple bit-pack with a high segment min value
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_highbase_probe_dt(fixture_bak_cci_bitpack_probe_highbase: Path) -> None:
    by_pk = _rows_by_pk(fixture_bak_cci_bitpack_probe_highbase, "cci_bitpack_probe_highbase")
    assert len(by_pk) == 200_000
    _assert_modk(by_pk, "dt", HIGHBASE_BASE, HIGHBASE_MOD)
