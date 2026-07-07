from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import deltalake

from mssqlbak.extract import extract_bak_to_delta
from tools.make_xtp_checkpoint_fixture import ROW_COUNT, expected_payload_len


def _extract_table(bak: Path, name: str) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory() as tmp:
        extract_bak_to_delta(str(bak), tmp)
        table_dir = Path(tmp) / "dbo" / name
        if not table_dir.is_dir():
            return []
        return deltalake.DeltaTable(str(table_dir)).to_pyarrow_table().to_pylist()


def test_xtp_checkpoint_recovers_every_row(fixture_bak_xtp_checkpoint: Path) -> None:
    rows = _extract_table(fixture_bak_xtp_checkpoint, "xtp_ckpt")
    ids = sorted(r["id"] for r in rows)
    # Completeness: the dense IDENTITY(1,1) key must enumerate {1..N} with no gaps.
    assert ids == list(range(1, ROW_COUNT + 1)), (
        f"expected {ROW_COUNT} contiguous ids 1..{ROW_COUNT}, "
        f"got {len(ids)} (first gap reveals dropped straddle rows)"
    )


def test_xtp_checkpoint_payloads_byte_exact(fixture_bak_xtp_checkpoint: Path) -> None:
    rows = {r["id"]: r for r in _extract_table(fixture_bak_xtp_checkpoint, "xtp_ckpt")}
    # Spot-check a spread of ids, including likely boundary-straddle rows.
    for id_ in (1, 2, 400, 401, 12_345, ROW_COUNT // 2, ROW_COUNT - 1, ROW_COUNT):
        row = rows.get(id_)
        assert row is not None, f"row id={id_} missing (dropped straddle row)"
        want_len = expected_payload_len(id_)
        assert row["width"] == want_len
        assert row["payload"] == "x" * want_len
