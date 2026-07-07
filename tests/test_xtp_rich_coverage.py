from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import deltalake

from mssqlbak.extract import extract_bak_to_delta
from tools.make_xtp_rich_fixture import FIXED_EXPECTED, MIXED_EXPECTED


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


def test_xtp_rich_decodes_fixed_table(fixture_bak_xtp_rich: Path) -> None:
    rows = sorted(_extract_tables(fixture_bak_xtp_rich)["dbo.xtp_rich_fixed"], key=lambda r: r["id"])

    for row, (id_, (score, flag, amount)) in zip(rows, sorted(FIXED_EXPECTED.items())):
        assert row["id"] == id_
        assert row["score"] == score
        assert row["flag"] == flag
        assert str(row["amount"]) == str(amount)


def test_xtp_rich_decodes_mixed_table(fixture_bak_xtp_rich: Path) -> None:
    rows = sorted(_extract_tables(fixture_bak_xtp_rich)["dbo.xtp_rich_mixed"], key=lambda r: r["id"])

    for row, (id_, (label, note)) in zip(rows, sorted(MIXED_EXPECTED.items())):
        assert row["id"] == id_
        assert row["label"] == label
        assert row["note"] == note
