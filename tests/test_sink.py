from __future__ import annotations

from pathlib import Path

import pyarrow as pa
from deltalake import DeltaTable

from mssqlbak.sink import DeltaSink


def test_sink_writes_readable_delta(tmp_path: Path) -> None:
    sink = DeltaSink(tmp_path / "out")
    schema = pa.schema([("id", pa.int32()), ("label", pa.string())])
    sink.open_table("dbo.t_int", schema)
    sink.write_batch(pa.record_batch([[1, 2], ["low", "high"]], schema=schema))
    sink.close()
    dt = DeltaTable(str(tmp_path / "out" / "dbo" / "t_int"))
    assert dt.to_pyarrow_table().num_rows == 2


def test_sink_append_accumulates_rows(tmp_path: Path) -> None:
    sink = DeltaSink(tmp_path / "out")
    schema = pa.schema([("id", pa.int32()), ("label", pa.string())])
    sink.open_table("dbo.t_int", schema)
    sink.write_batch(pa.record_batch([[1], ["low"]], schema=schema))
    sink.write_batch(pa.record_batch([[2], ["high"]], schema=schema))
    sink.close()
    dt = DeltaTable(str(tmp_path / "out" / "dbo" / "t_int"))
    assert dt.to_pyarrow_table().num_rows == 2
