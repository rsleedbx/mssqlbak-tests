from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import deltalake
import pytest

from mssqlbak.compressed import is_mssqlbak
from mssqlbak.catalog import recover_schema
from mssqlbak.extract import extract_bak_to_delta
from mssqlbak.pages import PageStore
from mssqlbak.xtp import read_xtp_rows
from mssqlbak.xtp import scan_cfp_log_records
from tools.make_xtp_probe_fixture import (
    ID_1COL,
    ID_2COL,
    ID_A,
    ID_B,
    ID_C,
    NV_LABEL,
    SCORE,
)
from tools.make_xtp_simple_fixture import FIXED_EXPECTED, VAR_EXPECTED

_FIXTURES_2025 = Path(__file__).parent / "fixtures_2025"
_FIXTURES_REALWORLD = Path(__file__).parent / "fixtures_realworld"


def _extract_tables(bak: Path) -> dict[str, list[dict[str, Any]]]:
    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(bak), tmp)
        root = Path(tmp)
        tables: dict[str, list[dict[str, Any]]] = {}
        for schema_dir in root.iterdir():
            if not schema_dir.is_dir():
                continue
            for table_dir in schema_dir.iterdir():
                if table_dir.is_dir():
                    table = deltalake.DeltaTable(str(table_dir)).to_pyarrow_table()
                    tables[f"{schema_dir.name}.{table_dir.name}"] = table.to_pylist()
        return tables


@pytest.mark.fixture
def test_xtp_simple_decodes_fixed_and_variable_tables() -> None:
    bak = _FIXTURES_2025 / "xtp_simple_full.bak"
    if not bak.exists():
        pytest.skip(f"fixture missing: {bak}")

    tables = _extract_tables(bak)

    fixed_rows = sorted(tables["dbo.xtp_fixed"], key=lambda r: r["id"])
    assert fixed_rows == [
        {"id": id_, "score": score, "flag": flag}
        for id_, (score, flag) in sorted(FIXED_EXPECTED.items())
    ]

    var_rows = sorted(tables["dbo.xtp_var"], key=lambda r: r["id"])
    assert var_rows == [
        {"id": id_, "label": label}
        for id_, label in sorted(VAR_EXPECTED.items())
    ]


@pytest.mark.fixture
def test_xtp_probe_decodes_all_probe_tables() -> None:
    bak = _FIXTURES_2025 / "xtp_probe_full.bak"
    if not bak.exists():
        pytest.skip(f"fixture missing: {bak}")

    tables = _extract_tables(bak)

    assert tables["dbo.probe_1i1r"] == [{"id": ID_1COL}]
    assert tables["dbo.probe_2i1r"] == [{"id": ID_2COL, "score": SCORE}]
    assert sorted(tables["dbo.probe_1i3r"], key=lambda r: r["id"]) == [
        {"id": ID_B},
        {"id": ID_A},
        {"id": ID_C},
    ]
    assert tables["dbo.probe_nv1r"] == [{"id": ID_1COL, "label": NV_LABEL}]
    assert tables["dbo.probe_nv1r_null"] == [{"id": ID_2COL, "label": None}]


def test_wwi_xtp_log_scan_keeps_records_before_large_checkpoint_header() -> None:
    bak = _FIXTURES_REALWORLD / "WideWorldImporters-Full.bak"
    if not bak.exists():
        pytest.skip(f"fixture missing: {bak}")

    records = scan_cfp_log_records(bak.read_bytes()).get(0x4, [])
    seqs = [seq for seq, _payload in records]

    # A seq may carry more than one distinct payload (a genuine row plus a
    # checkpoint metadata twin), so the scan can emit a few duplicate seqs; the
    # completeness gate resolves each seq to the copy that decodes consistently.
    # What matters here is that every seq 1..65_998 is present and the early
    # records before the large checkpoint header are not dropped.
    distinct = sorted(set(seqs))
    assert distinct == list(range(1, 65_999))
    assert distinct[:10] == list(range(1, 11))


def test_wwi_xtp_log_decode_maps_temperature_tables() -> None:
    bak = _FIXTURES_REALWORLD / "WideWorldImporters-Full.bak"
    if not bak.exists():
        pytest.skip(f"fixture missing: {bak}")

    schema = recover_schema(PageStore.from_bak(str(bak)))
    tables = [
        t
        for t in schema.tables
        if t.is_memory_optimized and t.name.endswith("Temperatures")
    ]

    rows = read_xtp_rows(bak.read_bytes(), tables, is_compressed=is_mssqlbak(str(bak)))

    assert {name: len(got) for name, got in rows.items()} == {
        "ColdRoomTemperatures": 4,
        "VehicleTemperatures": 65_998,
    }
