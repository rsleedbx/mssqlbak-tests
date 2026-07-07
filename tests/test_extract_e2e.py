from __future__ import annotations

from pathlib import Path

import pytest
from deltalake import DeltaTable

from mssqlbak.extract import extract_bak_to_delta
from tools.typematrix import TYPE_CASES, expected_rows


@pytest.mark.fixture
def test_extract_writes_all_tables(fixture_bak: Path, tmp_path: Path) -> None:
    extract_bak_to_delta(fixture_bak, tmp_path / "delta")
    for case in TYPE_CASES:
        if case.fallback_xtype is not None:
            # SS2025-only types (e.g. native json, type_id 244) have no table in
            # the SS2022 typecoverage fixture; covered by dedicated coverage tests.
            continue
        dt = DeltaTable(str(tmp_path / "delta" / "dbo" / f"t_{case.name}"))
        assert dt.to_pyarrow_table().num_rows == len(case.rows)


@pytest.mark.fixture
def test_extract_int_values_round_trip(fixture_bak: Path, tmp_path: Path) -> None:
    extract_bak_to_delta(fixture_bak, tmp_path / "delta")
    dt = DeltaTable(str(tmp_path / "delta" / "dbo" / "t_int"))
    table = dt.to_pyarrow_table()
    got = set(table.column("v").to_pylist())
    expected = {row.value for row in expected_rows("int")}
    assert got == expected
