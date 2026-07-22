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


def test_sink_empty_table_creates_delta_with_schema(tmp_path: Path) -> None:
    """open_table + close with no write_batch must still create a Delta table.

    A 0-row table should produce a valid Delta table whose schema matches the
    Arrow schema that was passed to open_table, so that round-trip readback can
    verify column count and column names even when no rows were extracted.
    """
    sink = DeltaSink(tmp_path / "out")
    schema = pa.schema([("id", pa.int64()), ("name", pa.string()), ("val", pa.float64())])
    sink.open_table("dbo.empty_tbl", schema)
    sink.close()  # no write_batch call

    dt = DeltaTable(str(tmp_path / "out" / "dbo" / "empty_tbl"))
    result = dt.to_pyarrow_table()
    assert result.num_rows == 0
    assert result.schema.names == ["id", "name", "val"]


def test_sink_empty_table_column_sanitization(tmp_path: Path) -> None:
    """Column names with UC-invalid characters are sanitized in the empty Delta table."""
    sink = DeltaSink(tmp_path / "out")
    schema = pa.schema([("my col", pa.int32()), ("val;2", pa.string())])
    sink.open_table("dbo.sanitized", schema)
    sink.close()

    dt = DeltaTable(str(tmp_path / "out" / "dbo" / "sanitized"))
    result = dt.to_pyarrow_table()
    assert result.num_rows == 0
    # UC-sanitized: spaces and semicolons replaced with underscores
    for col in result.schema.names:
        assert " " not in col and ";" not in col


def test_sink_empty_table_nonnull_int_schema(tmp_path: Path) -> None:
    """open_table + close with no write_batch on a cci_switch_src-style schema.

    cci_switch_src is a 3-column all-INT NOT NULL CCI table that ends up empty
    after an ALTER TABLE ... SWITCH TO.  The columnstore extraction path calls
    open_table but produces no write_batch calls for it; close() must still
    materialise a 0-row Delta table so coverage readback yields a non-None
    actual node and column-count verification passes.
    """
    sink = DeltaSink(tmp_path / "out")
    schema = pa.schema([
        pa.field("id",    pa.int32(), nullable=False),
        pa.field("batch", pa.int32(), nullable=False),
        pa.field("val",   pa.int32(), nullable=False),
    ])
    sink.open_table("dbo.cci_switch_src", schema)
    sink.close()  # no write_batch — table was empty after SWITCH

    dt = DeltaTable(str(tmp_path / "out" / "dbo" / "cci_switch_src"))
    result = dt.to_pyarrow_table()
    assert result.num_rows == 0
    assert result.schema.names == ["id", "batch", "val"]
