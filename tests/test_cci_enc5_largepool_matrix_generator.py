"""Unit checks for the enc=5 large-pool evidence fixture generator."""

from __future__ import annotations


def test_largepool_matrix_defines_boundary_variants() -> None:
    from tools.make_cci_enc5_largepool_matrix_fixture import (
        DB_NAME,
        OUT_PATH,
        TABLE_CASES,
        build_stmts,
    )

    assert DB_NAME == "CciEnc5LargePoolMatrix"
    assert OUT_PATH.name == "cci_enc5_largepool_matrix_full.bak"

    names = {case.name for case in TABLE_CASES}
    assert {
        "char_32767_distinct_var",
        "char_32768_distinct_var",
        "char_65536_distinct_var",
        "char_80000_distinct_var",
        "varchar_80000_distinct_var",
        "char_80000_lowcard_var",
        "char_80000_fullwidth",
    } <= names

    stmts = "\n".join(build_stmts())
    for case in TABLE_CASES:
        assert f"CREATE TABLE dbo.{case.name}" in stmts
        assert f"ALTER INDEX cci ON dbo.{case.name}" in stmts


def test_largepool_matrix_is_registered_with_fixture_run() -> None:
    from tools.fixture_run import _COMMANDS

    assert "cci-enc5-largepool-matrix" in _COMMANDS
