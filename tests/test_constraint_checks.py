"""Unit tests for internal constraint validation checks.

These tests cover the value-level checks in ``mssqlbak.confidence`` and
``mssqlbak.constraint_check`` that validate decoded output against metadata
stored inside the ``.bak`` itself — no external ground truth required.
"""
from __future__ import annotations

import datetime as dt

import pyarrow as pa

from mssqlbak.confidence import (
    Severity,
    _btree_key_order_check,
    _collation_codepage_check,
    _null_contract_check,
    _type_range_check,
)
from mssqlbak.constraint_check import check_cci_segment


class TestCollationCodepage:
    def test_known_sortid_is_pass(self) -> None:
        # 0x08 = Latin1_General (cp1252) is in the SORTID table.
        check = _collation_codepage_check("dbo.t", "c", 0x08)
        assert check.severity is Severity.PASS

    def test_db_default_collation_low_byte_is_pass(self) -> None:
        # DB-default collations carry the SORTID in the low byte (e.g. 0x3400D008
        # → 0x08 = cp1252), so they resolve to a known code page.
        check = _collation_codepage_check("dbo.t", "c", 0x3400D008)
        assert check.severity is Severity.PASS

    def test_utf8_collation_is_pass(self) -> None:
        check = _collation_codepage_check("dbo.t", "c", 0x100)
        assert check.severity is Severity.PASS

    def test_unknown_sortid_is_warn(self) -> None:
        # 0xFE is not a mapped SORTID → cp1252 fallback → low confidence.
        check = _collation_codepage_check("dbo.t", "c", 0xFE)
        assert check.severity is Severity.WARN
        assert check.evidence["sortid"] == 0xFE


# ---------------------------------------------------------------------------
# Phase 1: type_range checks
# ---------------------------------------------------------------------------


class TestTypeRange:
    def test_tinyint_in_range_is_pass(self) -> None:
        col = pa.array([0, 100, 255], type=pa.int16())
        check = _type_range_check("dbo.t", "val", 48, col)
        assert check.severity is Severity.PASS

    def test_tinyint_out_of_range_is_fail(self) -> None:
        col = pa.array([0, 100, 300], type=pa.int32())
        check = _type_range_check("dbo.t", "val", 48, col)
        assert check.severity is Severity.FAIL
        assert check.evidence["observed_max"] == 300
        assert check.evidence["allowed_max"] == 255

    def test_tinyint_negative_is_fail(self) -> None:
        col = pa.array([-1, 0, 100], type=pa.int16())
        check = _type_range_check("dbo.t", "val", 48, col)
        assert check.severity is Severity.FAIL

    def test_smallint_in_range_is_pass(self) -> None:
        col = pa.array([-32768, 0, 32767], type=pa.int16())
        check = _type_range_check("dbo.t", "val", 52, col)
        assert check.severity is Severity.PASS

    def test_smallint_out_of_range_is_fail(self) -> None:
        col = pa.array([-32769], type=pa.int32())
        check = _type_range_check("dbo.t", "val", 52, col)
        assert check.severity is Severity.FAIL

    def test_int_in_range_is_pass(self) -> None:
        col = pa.array([-2_147_483_648, 0, 2_147_483_647], type=pa.int32())
        check = _type_range_check("dbo.t", "val", 56, col)
        assert check.severity is Severity.PASS

    def test_bigint_in_range_is_pass(self) -> None:
        col = pa.array([-(2**63), 0, 2**63 - 1], type=pa.int64())
        check = _type_range_check("dbo.t", "val", 127, col)
        assert check.severity is Severity.PASS

    def test_unknown_type_id_is_skipped(self) -> None:
        col = pa.array([1, 2, 3])
        check = _type_range_check("dbo.t", "val", 999, col)
        assert check.severity is Severity.PASS

    def test_all_null_column_is_pass(self) -> None:
        col = pa.array([None, None], type=pa.int32())
        check = _type_range_check("dbo.t", "val", 48, col)
        assert check.severity is Severity.PASS

    def test_nvarchar_within_max_length_is_pass(self) -> None:
        # NVARCHAR(10) → max_length_bytes=20
        col = pa.array(["hello", "world"])
        check = _type_range_check("dbo.t", "val", 231, col, max_length=20)
        assert check.severity is Severity.PASS

    def test_nvarchar_exceeds_max_length_is_fail(self) -> None:
        # NVARCHAR(3) → max_length_bytes=6; "hello" has 5 chars > 3
        col = pa.array(["hi", "hello"])
        check = _type_range_check("dbo.t", "val", 231, col, max_length=6)
        assert check.severity is Severity.FAIL

    def test_varchar_within_max_length_is_pass(self) -> None:
        col = pa.array(["abc", "de"])
        check = _type_range_check("dbo.t", "val", 167, col, max_length=5)
        assert check.severity is Severity.PASS

    def test_varchar_exceeds_max_length_is_fail(self) -> None:
        col = pa.array(["abcdef"])
        check = _type_range_check("dbo.t", "val", 167, col, max_length=5)
        assert check.severity is Severity.FAIL


# ---------------------------------------------------------------------------
# Phase 1: null_contract checks
# ---------------------------------------------------------------------------


class TestNullContract:
    def test_nullable_col_with_nulls_is_pass(self) -> None:
        col = pa.array([1, None, 3])
        check = _null_contract_check("dbo.t", "val", is_nullable=True, col=col)
        assert check.severity is Severity.PASS

    def test_not_null_col_without_nulls_is_pass(self) -> None:
        col = pa.array([1, 2, 3])
        check = _null_contract_check("dbo.t", "val", is_nullable=False, col=col)
        assert check.severity is Severity.PASS

    def test_not_null_col_with_nulls_is_fail(self) -> None:
        col = pa.array([1, None, 3])
        check = _null_contract_check("dbo.t", "val", is_nullable=False, col=col)
        assert check.severity is Severity.FAIL
        assert check.evidence["null_count"] == 1

    def test_not_null_col_all_nulls_is_fail(self) -> None:
        col = pa.array([None, None], type=pa.int32())
        check = _null_contract_check("dbo.t", "val", is_nullable=False, col=col)
        assert check.severity is Severity.FAIL

    def test_nullable_col_all_nulls_is_pass(self) -> None:
        col = pa.array([None, None], type=pa.int32())
        check = _null_contract_check("dbo.t", "val", is_nullable=True, col=col)
        assert check.severity is Severity.PASS


# ---------------------------------------------------------------------------
# Phase 2: btree_key_order checks
# ---------------------------------------------------------------------------


class TestBtreeKeyOrder:
    def test_strictly_ascending_is_pass(self) -> None:
        tbl = pa.table({"id": [1, 2, 3], "val": ["a", "b", "c"]})
        check = _btree_key_order_check("dbo.t", "id", tbl)
        assert check.severity is Severity.PASS

    def test_non_decreasing_is_pass(self) -> None:
        # Duplicate keys are valid for non-unique indexes
        tbl = pa.table({"id": [1, 1, 2, 3], "val": ["a", "b", "c", "d"]})
        check = _btree_key_order_check("dbo.t", "id", tbl)
        assert check.severity is Severity.PASS

    def test_disordered_is_fail(self) -> None:
        tbl = pa.table({"id": [1, 3, 2], "val": ["a", "b", "c"]})
        check = _btree_key_order_check("dbo.t", "id", tbl)
        assert check.severity is Severity.FAIL
        assert "violation_at_row" in check.evidence

    def test_single_row_is_pass(self) -> None:
        tbl = pa.table({"id": [42], "val": ["x"]})
        check = _btree_key_order_check("dbo.t", "id", tbl)
        assert check.severity is Severity.PASS

    def test_empty_table_is_pass(self) -> None:
        tbl = pa.table({"id": pa.array([], type=pa.int32()), "val": pa.array([], type=pa.string())})
        check = _btree_key_order_check("dbo.t", "id", tbl)
        assert check.severity is Severity.PASS

    def test_missing_key_col_is_warn(self) -> None:
        tbl = pa.table({"other": [1, 2, 3]})
        check = _btree_key_order_check("dbo.t", "id", tbl)
        assert check.severity is Severity.WARN

    def test_descending_is_fail(self) -> None:
        tbl = pa.table({"id": [3, 2, 1]})
        check = _btree_key_order_check("dbo.t", "id", tbl)
        assert check.severity is Severity.FAIL

    def test_date_key_ascending_is_pass(self) -> None:
        dates = [dt.date(2020, 1, 1), dt.date(2020, 6, 1), dt.date(2021, 1, 1)]
        tbl = pa.table({"dt": pa.array(dates)})
        check = _btree_key_order_check("dbo.t", "dt", tbl)
        assert check.severity is Severity.PASS


# ---------------------------------------------------------------------------
# Phase 3: CCI segment constraint checks
# ---------------------------------------------------------------------------


class _FakeSeg:
    """Minimal _ColumnSegment-like object for testing."""

    def __init__(
        self,
        seg_id: int = 0,
        col_id: int = 1,
        enc_type: int = 1,
        n_rows: int = 5,
        has_null: int = 0,
        mn: int = 0,
        magnitude: float = 1.0,
        cdi_max: int = 10,
    ) -> None:
        self.seg_id = seg_id
        self.col_id = col_id
        self.enc_type = enc_type
        self.n_rows = n_rows
        self.has_null = has_null
        self.mn = mn
        self.magnitude = magnitude
        self.cdi_max = cdi_max


class TestCciSegmentConstraint:
    def test_row_count_match_is_pass(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=1, enc_type=2)
        col = pa.array([1, 2, 3])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        rc = next(r for r in results if r.check == "row_count")
        assert rc.passed

    def test_row_count_mismatch_is_fail(self) -> None:
        seg = _FakeSeg(n_rows=5, has_null=1, enc_type=2)
        col = pa.array([1, 2, 3])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        rc = next(r for r in results if r.check == "row_count")
        assert not rc.passed
        assert rc.evidence["decoded"] == 3
        assert rc.evidence["expected"] == 5

    def test_null_contract_no_nulls_when_has_null_0_is_pass(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=0, enc_type=2)
        col = pa.array([1, 2, 3])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        nc = next((r for r in results if r.check == "null_contract"), None)
        assert nc is not None
        assert nc.passed

    def test_null_contract_nulls_when_has_null_0_is_fail(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=0, enc_type=2)
        col = pa.array([1, None, 3])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        nc = next((r for r in results if r.check == "null_contract"), None)
        assert nc is not None
        assert not nc.passed

    def test_null_contract_skipped_when_has_null_1(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=1, enc_type=2)
        col = pa.array([1, None, 3])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        nc = next((r for r in results if r.check == "null_contract"), None)
        assert nc is None  # not checked when segment declares nulls

    def test_value_range_within_bounds_is_pass(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=1, enc_type=1, mn=0, magnitude=1.0, cdi_max=10)
        col = pa.array([0, 5, 10])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        vr = next((r for r in results if r.check == "value_range"), None)
        assert vr is not None
        assert vr.passed

    def test_value_range_exceeds_max_is_fail(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=1, enc_type=1, mn=0, magnitude=1.0, cdi_max=5)
        col = pa.array([0, 5, 999])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        vr = next((r for r in results if r.check == "value_range"), None)
        assert vr is not None
        assert not vr.passed
        assert vr.evidence["obs_max"] == 999

    def test_value_range_skipped_for_enc5(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=1, enc_type=5, mn=0, magnitude=1.0, cdi_max=10)
        col = pa.array([b"a", b"b", b"c"])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        vr = next((r for r in results if r.check == "value_range"), None)
        assert vr is None  # enc=5 skipped

    def test_value_range_skipped_when_cdi_max_zero(self) -> None:
        seg = _FakeSeg(n_rows=3, has_null=1, enc_type=1, mn=0, magnitude=1.0, cdi_max=0)
        col = pa.array([1, 2, 3])
        results = check_cci_segment(seg, col)  # type: ignore[arg-type]
        vr = next((r for r in results if r.check == "value_range"), None)
        assert vr is None  # unknown max
