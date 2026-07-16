"""Tests for the fast digest verification level in value_verify.verify_table.

These tests build lightweight in-memory sidecars (manifest JSON + optional
parquet) in a temp directory so no real .bak or live SQL Server is required.

Coverage:
1. digest level catches multiset corruption (wrong values somewhere in a column).
2. digest level PASSES a value-preserving two-row swap; full level catches it.
3. digest level skips GT parquet read for full/sample manifest-mode tables.
4. verify_level="none" path: runner skips verify_table (verified via runner logic).
5. Python/Arrow parity for column_ordered_digest / _arrow_ordered_column_digest.
6. Ordered digest catches value-preserving swap missed by multiset digest.
7. Correct data passes with ordered digest present.
8. String-key table: no false positive for correct data.
9. backfill_ordered_digest: populates ordered_digest, skips digest-only, idempotent.
"""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq

import json

from tools.cell_canon import canon, column_digest, column_ordered_digest
from tools import value_verify
from tools.value_verify import _arrow_ordered_column_digest


# ---------------------------------------------------------------------------
# Helpers for building synthetic sidecars
# ---------------------------------------------------------------------------

def _make_manifest_entry(
    fqn: str,
    columns: list[dict[str, Any]],
    key_columns: list[str],
    mode: str = "full",
) -> dict[str, Any]:
    return {
        "fqn": fqn,
        "mode": mode,
        "key_columns": key_columns,
        "columns": columns,
    }


def _col_entry(name: str, values: Sequence[str | None], sql_type: str = "int") -> dict[str, Any]:
    """Build a manifest column entry with a correct digest for the given values."""
    canon_values = [canon(v, sql_type) if v is not None else None for v in values]
    return {
        "name": name,
        "sql_type": sql_type,
        "digest": column_digest(canon_values),
        "null_count": sum(1 for v in values if v is None),
    }


def _write_gt_parquet(cells_dir: Path, fqn: str, data: dict[str, list[Any]]) -> None:
    """Write a simple ground-truth parquet file (all string columns)."""
    arrays = {col: pa.array(vals, type=pa.string()) for col, vals in data.items()}
    table = pa.table(arrays)
    pq.write_table(table, cells_dir / f"{fqn}.parquet")


def _extracted_table(data: dict[str, list[Any]]) -> pa.Table:
    """Build an Arrow table with int32 id column and large_string value columns."""
    arrays: dict[str, pa.Array] = {}
    for col, vals in data.items():
        if all(v is None or isinstance(v, int) for v in vals):
            arrays[col] = pa.array(vals, type=pa.int32())
        else:
            arrays[col] = pa.array(
                [str(v) if v is not None else None for v in vals],
                type=pa.large_utf8(),
            )
    return pa.table(arrays)


# ---------------------------------------------------------------------------
# 1. digest catches multiset corruption
# ---------------------------------------------------------------------------

class TestDigestCatchesCorruption:
    def test_wrong_value_flagged_as_digest_mismatch(self, tmp_path: Path) -> None:
        fqn = "dbo.t"
        # Ground truth has values [1, 2, 3]; extracted has [1, 2, 99] — multiset differs.
        gt_values = ["1", "2", "3"]
        col = _col_entry("val", gt_values)
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"])
        # No GT parquet written (digest level should not need it for full-mode manifests).

        extracted = _extracted_table({"id": [1, 2, 3], "val": [1, 2, 99]})

        result = value_verify.verify_table(extracted, tmp_path, manifest, level="digest")

        assert "val" in result.digest_mismatches
        assert not result.ok

    def test_correct_values_pass(self, tmp_path: Path) -> None:
        fqn = "dbo.t"
        gt_values = ["10", "20", "30"]
        col = _col_entry("val", gt_values)
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"])

        extracted = _extracted_table({"id": [1, 2, 3], "val": [10, 20, 30]})

        result = value_verify.verify_table(extracted, tmp_path, manifest, level="digest")

        assert not result.digest_mismatches
        assert result.ok

    def test_extra_null_flagged(self, tmp_path: Path) -> None:
        """Adding a NULL where GT has a value changes the digest (NULL excluded from digest)."""
        fqn = "dbo.t"
        gt_values = ["1", "2", "3"]
        col = _col_entry("val", gt_values)
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"])

        # Extracted: one value replaced by NULL → digest covers only non-nulls
        # The digest of [1, 2, None] will differ from [1, 2, 3].
        extracted = _extracted_table({"id": [1, 2, 3], "val": [1, 2, None]})

        result = value_verify.verify_table(extracted, tmp_path, manifest, level="digest")

        assert "val" in result.digest_mismatches
        assert not result.ok

    def test_all_nulls_column_passes_when_digest_absent(self, tmp_path: Path) -> None:
        """Columns without a digest entry are silently skipped (no false positive)."""
        fqn = "dbo.t"
        # Column entry with no digest key.
        col = {"name": "val", "sql_type": "int", "null_count": 3}
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"])

        extracted = _extracted_table({"id": [1, 2, 3], "val": [None, None, None]})

        result = value_verify.verify_table(extracted, tmp_path, manifest, level="digest")

        assert not result.digest_mismatches
        assert result.ok


# ---------------------------------------------------------------------------
# 2. digest PASSES value-preserving swap; full CATCHES it
# ---------------------------------------------------------------------------

class TestDigestVsFullSwapDetection:
    def _swapped_case(self, tmp_path: Path) -> tuple[dict[str, Any], pa.Table, pa.Table]:
        """GT has rows (id=1, val='A'), (id=2, val='B').
        Extracted (correct) matches.
        Swapped has values transposed: (id=1, val='B'), (id=2, val='A').
        The column multiset is {'A','B'} in both cases → digest passes.
        """
        fqn = "dbo.swap"
        gt_values = ["A", "B"]  # canonical strings for varchar
        col = _col_entry("val", gt_values, sql_type="varchar(10)")
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"])

        # Write GT parquet for the full-mode keyed compare.
        _write_gt_parquet(
            tmp_path, fqn,
            {"id": ["1", "2"], "val": ["A", "B"]},
        )

        correct = _extracted_table({"id": [1, 2], "val": ["A", "B"]})
        swapped = _extracted_table({"id": [1, 2], "val": ["B", "A"]})
        return manifest, correct, swapped

    def test_digest_passes_swapped(self, tmp_path: Path) -> None:
        manifest, _, swapped = self._swapped_case(tmp_path)
        result = value_verify.verify_table(swapped, tmp_path, manifest, level="digest")
        # Multiset is identical → digest passes.
        assert not result.digest_mismatches
        assert result.ok

    def test_full_catches_swapped(self, tmp_path: Path) -> None:
        manifest, _, swapped = self._swapped_case(tmp_path)
        result = value_verify.verify_table(swapped, tmp_path, manifest, level="full")
        # Keyed compare: id=1 expects 'A' but got 'B' → col_mismatch.
        assert "val" in result.col_mismatches
        assert not result.ok

    def test_full_passes_correct(self, tmp_path: Path) -> None:
        manifest, correct, _ = self._swapped_case(tmp_path)
        result = value_verify.verify_table(correct, tmp_path, manifest, level="full")
        assert not result.col_mismatches
        assert result.ok


# ---------------------------------------------------------------------------
# 3. digest level skips GT parquet read for full/sample manifest tables
# ---------------------------------------------------------------------------

class TestDigestSkipsParquet:
    def test_no_parquet_read_for_full_mode_manifest(self, tmp_path: Path) -> None:
        """For a full-mode manifest table, level=digest must not read the parquet."""
        fqn = "dbo.t"
        gt_values = ["5", "10", "15"]
        col = _col_entry("val", gt_values)
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"], mode="full")
        # Deliberately do NOT write a parquet so any read would raise.

        extracted = _extracted_table({"id": [1, 2, 3], "val": [5, 10, 15]})

        # Spy on pq.read_table; it must not be called.
        with patch("pyarrow.parquet.read_table") as mock_read:
            result = value_verify.verify_table(extracted, tmp_path, manifest, level="digest")
            mock_read.assert_not_called()

        assert result.ok

    def test_full_level_would_attempt_parquet_read(self, tmp_path: Path) -> None:
        """Confirm that level=full DOES attempt to read parquet (file missing → error result)."""
        fqn = "dbo.t"
        gt_values = ["5", "10", "15"]
        col = _col_entry("val", gt_values)
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"], mode="full")
        # No parquet written.

        extracted = _extracted_table({"id": [1, 2, 3], "val": [5, 10, 15]})

        # With level=full and a missing parquet the function should hit the
        # "gt is None" branch and set an error on the result.
        result = value_verify.verify_table(extracted, tmp_path, manifest, level="full")
        assert result.error is not None


# ---------------------------------------------------------------------------
# 4. verify_level="none" leaves verify_results empty
# ---------------------------------------------------------------------------

class TestVerifyLevelNone:
    def test_want_cells_false_when_level_none(self, tmp_path: Path) -> None:
        """When verify_level='none', want_cells is False and verify_table is never called."""
        from tools.correctness_coverage.runner import _StreamingStatsSink

        fqn = "dbo.t"
        col = _col_entry("val", ["1", "2", "3"])
        manifest_entry = _make_manifest_entry(fqn, [col], key_columns=["id"])
        manifest_by_fqn = {fqn: manifest_entry}

        # Build a fake cells_dir so the path exists.
        cells_dir = tmp_path / "cells"
        cells_dir.mkdir()

        # want_cells is driven by: cells_dir.exists() AND verify_level != "none"
        # When verify_level="none", want_cells=False → sink never calls verify_table.
        sink = _StreamingStatsSink(
            cells_dir=None,   # None because want_cells=False
            want_cells=False,
            manifest_by_fqn=manifest_by_fqn,
            verify_level="none",
        )

        schema = pa.schema([("id", pa.int32()), ("val", pa.int32())])
        batch = pa.record_batch(
            [pa.array([1, 2, 3], pa.int32()), pa.array([1, 2, 3], pa.int32())],
            schema=schema,
        )
        sink.open_table(fqn, schema)
        sink.write_batch(batch)
        sink.finish()

        assert sink.verify_results == {}
        assert sink.verify_s == 0.0

    def test_want_cells_true_with_digest(self, tmp_path: Path) -> None:
        """When verify_level='digest' and cells_dir exists, verify_table IS called."""
        from tools.correctness_coverage.runner import _StreamingStatsSink

        fqn = "dbo.t"
        col = _col_entry("val", ["1", "2", "3"])
        manifest_entry = _make_manifest_entry(fqn, [col], key_columns=["id"])
        manifest_by_fqn = {fqn: manifest_entry}

        cells_dir = tmp_path / "cells"
        cells_dir.mkdir()

        sink = _StreamingStatsSink(
            cells_dir=cells_dir,
            want_cells=True,
            manifest_by_fqn=manifest_by_fqn,
            verify_level="digest",
        )

        schema = pa.schema([("id", pa.int32()), ("val", pa.int32())])
        batch = pa.record_batch(
            [pa.array([1, 2, 3], pa.int32()), pa.array([1, 2, 3], pa.int32())],
            schema=schema,
        )
        sink.open_table(fqn, schema)
        sink.write_batch(batch)
        sink.finish()

        # verify_table was called → verify_results is populated and verify_s > 0.
        assert fqn in sink.verify_results
        assert sink.verify_s > 0.0


# ---------------------------------------------------------------------------
# Helper: build a manifest column entry WITH both digest and ordered_digest.
# ---------------------------------------------------------------------------

def _col_entry_ordered(
    name: str,
    gt_values_in_order: Sequence[str | None],
    sql_type: str = "varchar(10)",
) -> dict[str, Any]:
    """Build a manifest column entry with both digest and ordered_digest."""
    canon_values = [canon(v, sql_type) if v is not None else None for v in gt_values_in_order]
    return {
        "name": name,
        "sql_type": sql_type,
        "digest": column_digest(canon_values),
        "ordered_digest": column_ordered_digest(canon_values),
        "null_count": sum(1 for v in canon_values if v is None),
    }


# ---------------------------------------------------------------------------
# 5. Python / Arrow parity for ordered digest
# ---------------------------------------------------------------------------

class TestOrderedDigestParity:
    def test_simple_values(self) -> None:
        values = ["alpha", "beta", "gamma"]
        python_result = column_ordered_digest(values)
        arrow_arr = pa.array(values, type=pa.string())
        arrow_result = _arrow_ordered_column_digest(arrow_arr)
        assert python_result == arrow_result

    def test_with_nulls(self) -> None:
        values: list[str | None] = ["alpha", None, "gamma", None, "delta"]
        python_result = column_ordered_digest(values)
        arrow_arr = pa.array(values, type=pa.string())
        arrow_result = _arrow_ordered_column_digest(arrow_arr)
        assert python_result == arrow_result

    def test_all_nulls(self) -> None:
        values: list[str | None] = [None, None, None]
        python_result = column_ordered_digest(values)
        arrow_arr = pa.array(values, type=pa.string())
        arrow_result = _arrow_ordered_column_digest(arrow_arr)
        assert python_result == arrow_result

    def test_empty(self) -> None:
        values: list[str | None] = []
        python_result = column_ordered_digest(values)
        arrow_arr = pa.array(values, type=pa.string())
        arrow_result = _arrow_ordered_column_digest(arrow_arr)
        assert python_result == arrow_result

    def test_large_string_array(self) -> None:
        """large_utf8 (int64 offsets) also produces parity."""
        values = ["x", "y", "z"]
        python_result = column_ordered_digest(values)
        arrow_arr = pa.array(values, type=pa.large_utf8())
        arrow_result = _arrow_ordered_column_digest(arrow_arr)
        assert python_result == arrow_result

    def test_order_sensitivity(self) -> None:
        """Reversed order must produce a different digest."""
        fwd = column_ordered_digest(["A", "B", "C"])
        rev = column_ordered_digest(["C", "B", "A"])
        assert fwd != rev

    def test_null_position_sensitivity(self) -> None:
        """Null in position 0 vs position 1 must produce different digests."""
        d0 = column_ordered_digest([None, "A"])
        d1 = column_ordered_digest(["A", None])
        assert d0 != d1

    def test_parity_with_chunked_array(self) -> None:
        values: list[str | None] = ["one", None, "two"]
        python_result = column_ordered_digest(values)
        chunk1 = pa.array(["one", None], type=pa.string())
        chunk2 = pa.array(["two"], type=pa.string())
        chunked = pa.chunked_array([chunk1, chunk2])
        arrow_result = _arrow_ordered_column_digest(chunked)
        assert python_result == arrow_result


# ---------------------------------------------------------------------------
# 6. Ordered digest catches value-preserving swap missed by multiset digest
# ---------------------------------------------------------------------------

class TestOrderedDigestCatchesSwap:
    def _setup(
        self, tmp_path: Path
    ) -> tuple[dict[str, Any], pa.Table, pa.Table]:
        """GT: id=[1,2], val=['A','B'].  Swapped: id=[1,2], val=['B','A'].
        The multiset {'A','B'} is identical so the regular digest passes;
        the ordered digest (sorted by key id ascending) differs.
        """
        fqn = "dbo.ordered_swap"
        # GT in key order [id=1→'A', id=2→'B'].
        col = _col_entry_ordered("val", ["A", "B"])
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"])

        correct = _extracted_table({"id": [1, 2], "val": ["A", "B"]})
        swapped = _extracted_table({"id": [1, 2], "val": ["B", "A"]})
        return manifest, correct, swapped

    def test_swap_detected_at_digest_level(self, tmp_path: Path) -> None:
        manifest, _, swapped = self._setup(tmp_path)
        result = value_verify.verify_table(swapped, tmp_path, manifest, level="digest")
        assert "val" in result.order_mismatches, result
        assert not result.ok

    def test_multiset_digest_still_passes_swapped(self, tmp_path: Path) -> None:
        """Confirms the multiset digest alone cannot distinguish the swap."""
        manifest, _, swapped = self._setup(tmp_path)
        result = value_verify.verify_table(swapped, tmp_path, manifest, level="digest")
        assert "val" not in result.digest_mismatches

    def test_correct_data_passes_ordered(self, tmp_path: Path) -> None:
        manifest, correct, _ = self._setup(tmp_path)
        result = value_verify.verify_table(correct, tmp_path, manifest, level="digest")
        assert not result.order_mismatches
        assert result.ok

    def test_ordered_digest_absent_graceful_degrade(self, tmp_path: Path) -> None:
        """If ordered_digest is missing from the manifest, skip check (no false positive)."""
        fqn = "dbo.no_ordered"
        col = _col_entry("val", ["A", "B"], sql_type="varchar(10)")
        # col has no 'ordered_digest' key.
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"])
        swapped = _extracted_table({"id": [1, 2], "val": ["B", "A"]})
        result = value_verify.verify_table(swapped, tmp_path, manifest, level="digest")
        assert not result.order_mismatches
        assert result.ok  # multiset is unchanged, no ordered digest to check

    def test_ordered_digest_skipped_for_sample_mode(self, tmp_path: Path) -> None:
        """Sample-mode tables must not run the ordered digest check.

        The GT parquet for sample tables contains fewer rows than the full
        extract, so any pre-computed ordered_digest would be from the sample
        (not the full table) and would always differ.
        """
        fqn = "dbo.sample_table"
        col = _col_entry_ordered("val", ["A", "B"])
        manifest = _make_manifest_entry(fqn, [col], key_columns=["id"], mode="sample")
        # Even with a swap, sample-mode tables must not report order_mismatches.
        swapped = _extracted_table({"id": [1, 2], "val": ["B", "A"]})
        result = value_verify.verify_table(swapped, tmp_path, manifest, level="digest")
        assert not result.order_mismatches  # sample mode skips ordered check


# ---------------------------------------------------------------------------
# 7. String keys sort deterministically — no false positive for correct data
# ---------------------------------------------------------------------------

class TestStringKeyOrdering:
    def test_string_key_correct_data_passes(self, tmp_path: Path) -> None:
        """String primary keys (e.g. name) must sort stably so correct data never fails."""
        fqn = "dbo.strkey"
        # Key column: name (alphabetically sorted: alice < bob < charlie)
        # val in that order: [10, 20, 30]
        gt_in_key_order = ["10", "20", "30"]  # values for alice, bob, charlie
        col = _col_entry_ordered("score", gt_in_key_order, sql_type="int")
        manifest = _make_manifest_entry(fqn, [col], key_columns=["name"])

        # Extracted in a different order — after key sort should match GT.
        extracted = pa.table({
            "name": pa.array(["charlie", "alice", "bob"], type=pa.large_utf8()),
            "score": pa.array(["30", "10", "20"], type=pa.large_utf8()),
        })
        result = value_verify.verify_table(extracted, tmp_path, manifest, level="digest")
        assert not result.order_mismatches, result.order_mismatches
        assert result.ok

    def test_string_key_wrong_assignment_fails(self, tmp_path: Path) -> None:
        """Wrong score assigned to a name (after key-sort) must trigger order_mismatches."""
        fqn = "dbo.strkey"
        gt_in_key_order = ["10", "20", "30"]
        col = _col_entry_ordered("score", gt_in_key_order, sql_type="int")
        manifest = _make_manifest_entry(fqn, [col], key_columns=["name"])

        # alice→30, bob→20, charlie→10 — wrong assignment
        extracted = pa.table({
            "name": pa.array(["charlie", "alice", "bob"], type=pa.large_utf8()),
            "score": pa.array(["10", "30", "20"], type=pa.large_utf8()),
        })
        result = value_verify.verify_table(extracted, tmp_path, manifest, level="digest")
        # Multiset is unchanged; ordered digest catches wrong assignment.
        assert not result.digest_mismatches
        assert "score" in result.order_mismatches
        assert not result.ok


# ---------------------------------------------------------------------------
# 8. backfill_ordered_digest: populate, skip digest-only, idempotent
# ---------------------------------------------------------------------------

class TestBackfillOrderedDigest:
    def _write_manifest(self, cells_dir: Path, tables: list[dict[str, Any]]) -> None:
        manifest = {"bak": "test.bak", "captured_at": "2024-01-01T00:00:00", "tables": tables}
        (cells_dir / "_manifest.json").write_text(json.dumps(manifest, indent=2))

    def _read_manifest(self, cells_dir: Path) -> dict[str, Any]:
        return json.loads((cells_dir / "_manifest.json").read_text())

    def test_populates_ordered_digest(self, tmp_path: Path) -> None:
        from tools.backfill_ordered_digest import _backfill_manifest

        fqn = "dbo.t"
        cells_dir = tmp_path / "test.bak.cells"
        cells_dir.mkdir()

        # Write GT parquet (canonical strings).
        _write_gt_parquet(cells_dir, fqn, {"id": ["1", "2", "3"], "val": ["A", "B", "C"]})

        tables = [
            {
                "fqn": fqn,
                "mode": "full",
                "key_columns": ["id"],
                "columns": [
                    {"name": "id", "sql_type": "int", "null_count": 0},
                    {"name": "val", "sql_type": "varchar(10)", "null_count": 0},
                ],
            }
        ]
        self._write_manifest(cells_dir, tables)

        updated, skipped = _backfill_manifest(cells_dir / "_manifest.json")
        assert updated == 1
        assert skipped == 0

        manifest = self._read_manifest(cells_dir)
        tbl = manifest["tables"][0]
        val_col = next(c for c in tbl["columns"] if c["name"] == "val")
        assert "ordered_digest" in val_col
        assert val_col["ordered_digest"].startswith("sha256:")
        # id is a key column — backfill should not write ordered_digest for key cols.
        id_col = next(c for c in tbl["columns"] if c["name"] == "id")
        assert "ordered_digest" not in id_col

    def test_skips_digest_only_mode(self, tmp_path: Path) -> None:
        from tools.backfill_ordered_digest import _backfill_manifest

        fqn = "dbo.digest_only"
        cells_dir = tmp_path / "test.bak.cells"
        cells_dir.mkdir()

        tables = [
            {
                "fqn": fqn,
                "mode": "digest-only",
                "key_columns": [],
                "columns": [{"name": "val", "sql_type": "int", "null_count": 0}],
            }
        ]
        self._write_manifest(cells_dir, tables)

        updated, skipped = _backfill_manifest(cells_dir / "_manifest.json")
        assert updated == 0
        assert skipped == 1

        manifest = self._read_manifest(cells_dir)
        val_col = manifest["tables"][0]["columns"][0]
        assert "ordered_digest" not in val_col

    def test_skips_keyless_table(self, tmp_path: Path) -> None:
        from tools.backfill_ordered_digest import _backfill_manifest

        fqn = "dbo.keyless"
        cells_dir = tmp_path / "test.bak.cells"
        cells_dir.mkdir()
        _write_gt_parquet(cells_dir, fqn, {"val": ["X", "Y"]})

        tables = [
            {
                "fqn": fqn,
                "mode": "full",
                "key_columns": [],
                "columns": [{"name": "val", "sql_type": "int", "null_count": 0}],
            }
        ]
        self._write_manifest(cells_dir, tables)

        updated, skipped = _backfill_manifest(cells_dir / "_manifest.json")
        assert updated == 0
        assert skipped == 1

    def test_idempotent(self, tmp_path: Path) -> None:
        from tools.backfill_ordered_digest import _backfill_manifest

        fqn = "dbo.t"
        cells_dir = tmp_path / "test.bak.cells"
        cells_dir.mkdir()
        _write_gt_parquet(cells_dir, fqn, {"id": ["1", "2"], "val": ["P", "Q"]})

        tables = [
            {
                "fqn": fqn,
                "mode": "full",
                "key_columns": ["id"],
                "columns": [
                    {"name": "id", "sql_type": "int", "null_count": 0},
                    {"name": "val", "sql_type": "varchar(10)", "null_count": 0},
                ],
            }
        ]
        self._write_manifest(cells_dir, tables)

        _backfill_manifest(cells_dir / "_manifest.json")
        manifest_after_first = self._read_manifest(cells_dir)
        digest_after_first = manifest_after_first["tables"][0]["columns"][1]["ordered_digest"]

        _backfill_manifest(cells_dir / "_manifest.json")
        manifest_after_second = self._read_manifest(cells_dir)
        digest_after_second = manifest_after_second["tables"][0]["columns"][1]["ordered_digest"]

        assert digest_after_first == digest_after_second
