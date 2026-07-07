import pyarrow as pa

from mssqlbak.catalog import Column, Table
from mssqlbak.extract import (
    _build_rs_col_info,
    _build_rs_col_info_compressed,
    _is_rust_bytes_redecode,
    _redecode_mixed_cols,
)
from mssqlbak.types import NVARCHAR, VARBINARY, arrow_schema_for


def _nvarchar_col(*, encrypted: bool) -> Column:
    return Column(
        name="secret",
        colid=1,
        type_id=NVARCHAR,
        max_length=50,
        precision=0,
        scale=0,
        nullable=True,
        leaf_offset=-1,
        is_variable=True,
        user_type_id=NVARCHAR,
        null_bit=1,
        collation_id=2056 if encrypted else 872468488,
        is_encrypted=encrypted,
    )


def test_rust_fast_path_requests_raw_bytes_for_encrypted_nvarchar() -> None:
    col = _nvarchar_col(encrypted=True)
    table = Table("t", object_id=1, columns=[col])

    assert _is_rust_bytes_redecode(col)
    col_info = _build_rs_col_info(table)
    compressed_col_info = _build_rs_col_info_compressed(table)
    assert col_info is not None
    assert compressed_col_info is not None
    assert col_info[0][0] == VARBINARY
    assert compressed_col_info[0][0] == VARBINARY


def test_rust_fast_path_keeps_plain_nvarchar_on_text_path() -> None:
    col = _nvarchar_col(encrypted=False)
    table = Table("t", object_id=1, columns=[col])

    assert not _is_rust_bytes_redecode(col)
    col_info = _build_rs_col_info(table)
    compressed_col_info = _build_rs_col_info_compressed(table)
    assert col_info is not None
    assert compressed_col_info is not None
    assert col_info[0][0] == NVARCHAR
    assert compressed_col_info[0][0] == NVARCHAR


def test_redecode_encrypted_nvarchar_ciphertext_to_repr() -> None:
    col = _nvarchar_col(encrypted=True)
    table = Table("t", object_id=1, columns=[col])
    schema = arrow_schema_for(table)
    raw = b"\x01" + (b"x" * 48)
    batch = pa.record_batch([pa.array([raw], type=pa.binary())], names=["secret"])

    decoded = _redecode_mixed_cols(batch, [(0, col, schema.field(0).type, lambda v: v)], schema)

    assert decoded.column(0).to_pylist() == [repr(raw)]
