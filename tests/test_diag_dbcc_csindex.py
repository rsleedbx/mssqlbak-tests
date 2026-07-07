"""Unit checks for the DBCC CSINDEX diagnostic helper."""

from __future__ import annotations


def test_build_dbcc_csindex_sql_supports_bounded_segment_capture() -> None:
    from tools.diag.diag_dbcc_csindex import _build_dbcc_csindex_sql

    sql = _build_dbcc_csindex_sql(
        table="dbo.t",
        column_id=3,
        row_group_id=1,
        object_type=1,
        print_option=0,
        start=4300,
        end=4380,
    )

    assert "DBCC TRACEON(3604)" in sql
    assert "OBJECT_ID(N'dbo.t')" in sql
    assert "DBCC CSINDEX(@db, @hobt, 3, 1, 1, 0, 4300, 4380)" in sql
