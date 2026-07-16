"""Offline row-level value correctness tests.

Two layers:

1. ``quick`` — a fully self-contained round-trip that builds a synthetic
   ``.cells/`` sidecar and exercises ``tools.cell_canon`` + ``tools.value_verify``
   end to end (no live SQL, no fixtures). This is what proves the diff engine works.
2. ``full`` — discovery over real fixtures that already have a ``<bak>.cells/``
   sidecar; decodes each ``.bak`` and asserts ``cells_ok == cells_total`` and all
   digests match (xfail mirrors ``tools.known_gaps``). Skips cleanly until the
   ground-truth capture step (``tools/cells_capture.py``, needs a live container)
   has produced any ``.cells/`` directories.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from mssqlbak.sink import sanitize_fqn
from tests.fixture_companions import is_redundant_stripe, resolve_bak_input
from tools.cell_canon import canon, column_digest
from tools.known_gaps import expected_skipped_tables, gap_reason, version_from_fixture_dir
from tools.value_verify import (
    MANIFEST_NAME,
    _arrow_column_digest,
    _canon_col,
    _canon_to_arrow,
    load_manifest,
    verify_bak,
    verify_table,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- #
# canon() unit checks (the SSOT)
# --------------------------------------------------------------------------- #
@pytest.mark.quick
@pytest.mark.parametrize(
    "value,sql_type,expected",
    [
        (None, "int", None),
        (True, "bit", "1"),
        (False, "bit", "0"),
        ("True", "flag", "1"),
        ("False", "flag", "0"),
        ("0", "namestyle", "0"),
        ("ab  ", "char(4)", "ab"),
        ("cd ", "nchar(3)", "cd"),
        (b"\xab\x12", "varbinary(8)", "ab12"),
        (b"\xde\xad\xbe\xef", "sql_variant", "0xdeadbeef"),
        (1.0, "float", "1"),
        (0.1, "real", "0.1"),
        (123, "int", "123"),
    ],
)
def test_canon_rules(value: object, sql_type: str, expected: str | None) -> None:
    assert canon(value, sql_type) == expected


@pytest.mark.quick
def test_canon_float_quantizes_beyond_precision() -> None:
    # Two doubles differing only past 15 significant digits canonicalize equal.
    assert canon(0.1 + 0.2, "float") == canon(0.3, "float")


@pytest.mark.quick
def test_canon_float_text_does_not_overflow_max_finite_value() -> None:
    assert canon("1.79769313486232E+308", "float") == "1.79769313486232e+308"
    assert canon("-1.79769313486232E+308", "float") == "-1.79769313486232e+308"


@pytest.mark.quick
def test_canon_xml_normalizes_sql_server_text_forms() -> None:
    decoded = "<root><empty></empty><lines>\r\nx</lines><n>21000.0</n><d>3.1400</d></root>"
    captured = "<root><empty/><lines>&#x0D;\nx</lines><n>21000</n><d>3.14</d></root>"
    assert canon(decoded, "xml") == canon(captured, "xml")


@pytest.mark.quick
def test_canon_spatial_normalizes_float_text_precision() -> None:
    decoded = "POINT (-122.408489591016 37.7605893030868)"
    captured = "POINT (-122.40848959101599 37.7605893030868)"
    assert canon(decoded, "geography") == canon(captured, "geography")


@pytest.mark.quick
def test_column_digest_is_order_independent() -> None:
    a = column_digest(["x", "y", None, "z"])
    b = column_digest([None, "z", "x", "y"])
    assert a == b and a.startswith("sha256:")


# --------------------------------------------------------------------------- #
# Synthetic .cells/ round-trip — exercises verify_table fully offline
# --------------------------------------------------------------------------- #
def _write_synthetic_cells(cells_dir: Path) -> dict[str, str]:
    """Build a one-table ground-truth sidecar; return {column: sql_type}.

    Mirrors what tools/cells_capture.py writes: the parquet holds the CANONICAL
    string of each cell (not typed values), and the manifest digest is over those
    same canonical strings.
    """
    cells_dir.mkdir(parents=True, exist_ok=True)
    sql_types = {"id": "int", "code": "char(4)", "ratio": "float"}
    raw: dict[str, list[object]] = {
        "id": [1, 2, 3, 4],
        "code": ["ab  ", "cd  ", "ef  ", "gh  "],  # space-padded source
        "ratio": [0.1, 0.2, 0.3, 0.4],
    }
    canon_cols = {c: [canon(v, sql_types[c]) for v in raw[c]] for c in sql_types}
    gt = pa.table({c: pa.array(canon_cols[c], pa.string()) for c in sql_types})
    pq.write_table(gt, cells_dir / "dbo.t.parquet")

    def digest(col: str) -> str:
        return column_digest(canon_cols[col])

    manifest = {
        "bak": "synthetic.bak",
        "tables": [
            {
                "fqn": "dbo.t",
                "row_count": 4,
                "key_columns": ["id"],
                "mode": "full",
                "columns": [
                    {"name": c, "sql_type": t, "digest": digest(c), "null_count": 0}
                    for c, t in sql_types.items()
                ],
            }
        ],
    }
    (cells_dir / "_manifest.json").write_text(json.dumps(manifest))
    return sql_types


def _decoded_ok() -> pa.Table:
    # char(4) decoded without trailing pad (CHAR semantics) — canon makes it equal.
    return pa.table(
        {
            "id": pa.array([1, 2, 3, 4], pa.int64()),
            "code": pa.array(["ab", "cd", "ef", "gh"]),
            "ratio": pa.array([0.1, 0.2, 0.3, 0.4], pa.float64()),
        }
    )


@pytest.mark.quick
def test_verify_table_passes_on_matching_cells(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_synthetic_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    res = verify_table(_decoded_ok(), cells, entry)
    assert res.ok, (res.col_mismatches, res.digest_mismatches, res.samples)
    assert res.cells_total == 8 and res.cells_ok == 8  # 4 rows x (code, ratio)


@pytest.mark.quick
def test_verify_table_catches_wrong_cell(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_synthetic_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    bad = pa.table(
        {
            "id": pa.array([1, 2, 3, 4], pa.int64()),
            "code": pa.array(["ab", "cd", "ef", "gh"]),
            "ratio": pa.array([0.1, 0.2, 9.99, 0.4], pa.float64()),  # row id=3 wrong
        }
    )
    res = verify_table(bad, cells, entry)
    assert not res.ok
    assert res.col_mismatches == {"ratio": 1}
    assert res.cells_ok == 7 and res.cells_total == 8
    assert any(col == "ratio" for _key, col, _got, _want in res.samples)


@pytest.mark.quick
def test_verify_table_full_mode_skips_digest(tmp_path: Path) -> None:
    """Full-mode tables skip the manifest digest check — the keyed compare covers all rows.

    A tampered manifest digest does NOT cause a failure for a full-mode table
    whose cells are all correct.  Digest is the authority only for sample/
    digest-only tables where the per-cell compare doesn't cover the full column.
    """
    cells = tmp_path / "synthetic.bak.cells"
    _write_synthetic_cells(cells)
    manifest = load_manifest(cells)
    manifest["tables"][0]["columns"][1]["digest"] = "sha256:deadbeef"  # tamper "code"
    (cells / "_manifest.json").write_text(json.dumps(manifest))
    res = verify_table(_decoded_ok(), cells, manifest["tables"][0])
    # All cells match; tampered manifest digest is silently ignored in full mode.
    assert res.ok, (res.col_mismatches, res.digest_mismatches, res.samples)


@pytest.mark.quick
def test_verify_table_sample_mode_catches_digest_mismatch(tmp_path: Path) -> None:
    """Sample mode catches a tampered manifest digest because the digest is the
    authority for the full column (sample compare only covers ~200 K rows)."""
    cells = tmp_path / "synthetic.bak.cells"
    _write_sample_cells(cells)
    manifest = load_manifest(cells)
    manifest["tables"][0]["columns"][0]["digest"] = "sha256:deadbeef"  # tamper "id"
    (cells / "_manifest.json").write_text(json.dumps(manifest))
    entry = manifest["tables"][0]
    extracted = pa.table(
        {
            "id": pa.array([1, 2, 3], pa.int64()),
            "val": pa.array([10, 20, 30], pa.int64()),
        }
    )
    res = verify_table(extracted, cells, entry)
    assert "id" in res.digest_mismatches and not res.ok


@pytest.mark.quick
def test_verify_table_catches_missing_row(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_synthetic_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    short = _decoded_ok().slice(0, 3)  # drop row id=4
    res = verify_table(short, cells, entry)
    assert res.missing_keys == 1 and not res.ok


def _write_digest_only_cells(cells_dir: Path) -> None:
    """Build a keyless (digest-only) sidecar with per-column sorted value sets."""
    cells_dir.mkdir(parents=True, exist_ok=True)
    canon_vals = ["2001-01-01T00:00:00+00:00", "2001-01-02T00:00:00+00:00",
                  "2001-01-03T00:00:00+00:00"]
    gt = pa.table({"val": pa.array(sorted(canon_vals), pa.string())})
    pq.write_table(gt, cells_dir / "dbo.k.parquet")
    manifest = {
        "bak": "synthetic.bak",
        "tables": [
            {
                "fqn": "dbo.k",
                "row_count": 3,
                "key_columns": [],
                "mode": "digest-only",
                "values_sorted": True,
                "columns": [
                    {"name": "val", "sql_type": "datetimeoffset",
                     "digest": column_digest(canon_vals), "null_count": 0}
                ],
            }
        ],
    }
    (cells_dir / "_manifest.json").write_text(json.dumps(manifest))


def _write_sample_cells(cells_dir: Path) -> None:
    """Build a sampled sidecar whose manifest digest covers the full column."""
    cells_dir.mkdir(parents=True, exist_ok=True)
    sql_types = {"id": "int", "val": "int"}
    full_vals = [10, 20, 30]
    sample = pa.table(
        {
            "id": pa.array(["1", "2"], pa.string()),
            "val": pa.array(["10", "20"], pa.string()),
        }
    )
    pq.write_table(sample, cells_dir / "dbo.sampled.parquet")
    manifest = {
        "bak": "synthetic.bak",
        "tables": [
            {
                "fqn": "dbo.sampled",
                "row_count": 3,
                "key_columns": ["id"],
                "mode": "sample",
                "sample_n": 2,
                "columns": [
                    {
                        "name": c,
                        "sql_type": t,
                        "digest": column_digest(
                            [canon(v, t) for v in ([1, 2, 3] if c == "id" else full_vals)]
                        ),
                        "null_count": 0,
                    }
                    for c, t in sql_types.items()
                ],
            }
        ],
    }
    (cells_dir / "_manifest.json").write_text(json.dumps(manifest))


def _write_capped_digest_cells(cells_dir: Path) -> None:
    """Build a capped digest-only sidecar whose manifest covers the full column."""
    cells_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.table({"val": pa.array(["1", "2"], pa.string())}),
        cells_dir / "dbo.capped.parquet",
    )
    manifest = {
        "bak": "synthetic.bak",
        "tables": [
            {
                "fqn": "dbo.capped",
                "row_count": 4,
                "key_columns": [],
                "mode": "digest-only",
                "values_sorted": True,
                "values_capped": 2,
                "columns": [
                    {
                        "name": "val",
                        "sql_type": "int",
                        "digest": column_digest(["1", "2", "3", "4"]),
                        "null_count": 0,
                    }
                ],
            }
        ],
    }
    (cells_dir / "_manifest.json").write_text(json.dumps(manifest))


def _write_raw_full_sidecar_cells(cells_dir: Path) -> None:
    """Build an older full sidecar that stores raw bit strings."""
    cells_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.table(
            {
                "id": pa.array(["1", "2"], pa.string()),
                "flag": pa.array(["True", "False"], pa.string()),
            }
        ),
        cells_dir / "dbo.raw_bits.parquet",
    )
    manifest = {
        "bak": "synthetic.bak",
        "tables": [
            {
                "fqn": "dbo.raw_bits",
                "row_count": 2,
                "key_columns": ["id"],
                "mode": "full",
                "columns": [
                    {
                        "name": "id",
                        "sql_type": "int",
                        "digest": column_digest(["1", "2"]),
                        "null_count": 0,
                    },
                    {
                        "name": "flag",
                        "sql_type": "bit",
                        "digest": column_digest(["True", "False"]),
                        "null_count": 0,
                    },
                ],
            }
        ],
    }
    (cells_dir / "_manifest.json").write_text(json.dumps(manifest))


def _write_unknown_alias_base_type_cells(cells_dir: Path) -> None:
    """Build a full sidecar for an unknown alias over bit."""
    cells_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.table(
            {
                "id": pa.array(["1", "2"], pa.string()),
                "random_flag_123": pa.array(["1", "0"], pa.string()),
            }
        ),
        cells_dir / "dbo.alias_base.parquet",
    )
    manifest = {
        "bak": "synthetic.bak",
        "tables": [
            {
                "fqn": "dbo.alias_base",
                "row_count": 2,
                "key_columns": ["id"],
                "mode": "full",
                "columns": [
                    {
                        "name": "id",
                        "sql_type": "int",
                        "digest": column_digest(["1", "2"]),
                        "null_count": 0,
                    },
                    {
                        "name": "random_flag_123",
                        "sql_type": "RandomFlag123",
                        "base_sql_type": "bit",
                        "digest": column_digest(["1", "0"]),
                        "null_count": 0,
                    },
                ],
            }
        ],
    }
    (cells_dir / "_manifest.json").write_text(json.dumps(manifest))


@pytest.mark.quick
def test_digest_only_diagnosis_surfaces_value_setdiff(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_digest_only_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    # Decoder got the third value wrong (a real decode-side divergence).
    bad = pa.table({"val": pa.array([
        "2001-01-01T00:00:00+00:00",
        "2001-01-02T00:00:00+00:00",
        "2001-01-03T06:00:00+00:00",  # wrong instant
    ])})
    res = verify_table(bad, cells, entry)
    assert res.mode == "digest-only"
    assert "val" in res.digest_mismatches and not res.ok
    got_only = [s for s in res.samples if s[1] == "got-only"]
    want_only = [s for s in res.samples if s[1] == "want-only"]
    assert any("06:00:00" in (s[2] or "") for s in got_only)
    assert any("2001-01-03T00:00:00" in (s[3] or "") for s in want_only)


@pytest.mark.quick
def test_digest_only_clean_has_no_samples(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_digest_only_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    good = pa.table({"val": pa.array([
        "2001-01-01T00:00:00+00:00",
        "2001-01-02T00:00:00+00:00",
        "2001-01-03T00:00:00+00:00",
    ])})
    res = verify_table(good, cells, entry)
    assert res.ok and not res.digest_mismatches and not res.samples


@pytest.mark.quick
def test_sample_sidecar_uses_manifest_full_column_digest(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_sample_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    extracted = pa.table(
        {
            "id": pa.array([1, 2, 3], pa.int64()),
            "val": pa.array([10, 20, 30], pa.int64()),
        }
    )
    res = verify_table(extracted, cells, entry)
    assert res.ok, (res.col_mismatches, res.digest_mismatches, res.samples)
    assert res.cells_total == 2 and res.cells_ok == 2


@pytest.mark.quick
def test_capped_digest_only_uses_manifest_full_column_digest(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_capped_digest_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    extracted = pa.table({"val": pa.array([1, 2, 3, 4], pa.int64())})

    res = verify_table(extracted, cells, entry)

    assert res.ok, (res.digest_mismatches, res.samples)


@pytest.mark.quick
def test_raw_full_sidecar_normalizes_before_cell_compare(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_raw_full_sidecar_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    extracted = pa.table(
        {
            "id": pa.array([1, 2], pa.int64()),
            "flag": pa.array([True, False], pa.bool_()),
        }
    )

    res = verify_table(extracted, cells, entry)

    assert res.ok, (res.col_mismatches, res.digest_mismatches, res.samples)
    assert res.cells_total == 2 and res.cells_ok == 2


@pytest.mark.quick
def test_manifest_base_sql_type_canonicalizes_unknown_alias(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_unknown_alias_base_type_cells(cells)
    entry = load_manifest(cells)["tables"][0]
    extracted = pa.table(
        {
            "id": pa.array([1, 2], pa.int64()),
            "random_flag_123": pa.array([True, False], pa.bool_()),
        }
    )

    res = verify_table(extracted, cells, entry)

    assert res.ok, (res.col_mismatches, res.digest_mismatches, res.samples)
    assert res.cells_total == 2 and res.cells_ok == 2


@pytest.mark.quick
def test_verify_bak_handles_absent_table(tmp_path: Path) -> None:
    cells = tmp_path / "synthetic.bak.cells"
    _write_synthetic_cells(cells)
    results = verify_bak({}, cells)  # decode produced no tables
    assert results["dbo.t"].error is not None and not results["dbo.t"].ok


# --------------------------------------------------------------------------- #
# Real-fixture discovery (activates once .cells/ sidecars are captured)
# --------------------------------------------------------------------------- #
def _fixtures_with_cells() -> list[Path]:
    out: list[Path] = []
    for d in sorted(REPO_ROOT.glob("tests/fixtures_*")):
        for cells in sorted(d.glob("*.bak.cells")):
            bak = cells.parent / cells.name.removesuffix(".cells")
            # Striped companions share identical data — only the lowest stripe
            # is exercised (it resolves to the full merged set at extract time).
            if is_redundant_stripe(bak):
                continue
            out.append(cells)
    return out


_CELLS_DIRS = _fixtures_with_cells()


@pytest.mark.full
@pytest.mark.skipif(not _CELLS_DIRS, reason="no .cells/ sidecars yet (run cells capture)")
@pytest.mark.parametrize("cells_dir", _CELLS_DIRS, ids=lambda p: p.name)
@pytest.mark.parametrize(
    "level",
    [
        "digest",
        pytest.param("full", marks=pytest.mark.matrix),
    ],
)
def test_fixture_cells_match_ground_truth(cells_dir: Path, level: str) -> None:
    from mssqlbak.extract import extract_bak_to_delta  # local: heavy import
    import deltalake  # type: ignore[import]
    import tempfile

    bak = cells_dir.parent / cells_dir.name.removesuffix(".cells")
    if not (cells_dir / MANIFEST_NAME).is_file():
        pytest.skip(
            f"{cells_dir.name}: no {MANIFEST_NAME} (pre-manifest capture; recapture "
            "with tools.cells_capture to enable cell verification)"
        )
    manifest = load_manifest(cells_dir)
    version = version_from_fixture_dir(cells_dir.parent)
    reason = gap_reason(bak.stem, version)
    # Striped / differential backups need their companion files merged in.
    bak_input = resolve_bak_input(bak)
    extract_arg = (
        [str(p) for p in bak_input] if isinstance(bak_input, list) else str(bak_input)
    )
    with tempfile.TemporaryDirectory() as tmp:
        try:
            extract_bak_to_delta(extract_arg, tmp)
        except Exception as exc:  # noqa: BLE001
            # A known gap whose extraction raises by design (e.g. TDE) xfails;
            # otherwise the failure is real and must surface.
            if reason is not None:
                pytest.xfail(f"{reason}: extract raised {type(exc).__name__}: {exc}")
            raise
        extracted: dict[str, pa.Table] = {}
        for schema_dir in Path(tmp).iterdir():
            if not schema_dir.is_dir():
                continue
            for tbl_dir in schema_dir.iterdir():
                if tbl_dir.is_dir():
                    extracted[f"{schema_dir.name}.{tbl_dir.name}"] = deltalake.DeltaTable(
                        str(tbl_dir)
                    ).to_pyarrow_table()
        skipped = expected_skipped_tables(bak.stem)
        failures: list[str] = []
        for entry in manifest.get("tables", []):
            ext = extracted.get(entry["fqn"]) or extracted.get(sanitize_fqn(entry["fqn"]))
            if ext is None:
                if entry["fqn"] in skipped:
                    # Intentionally unsupported for this backup (e.g. XTP tables
                    # whose real CFP checkpoint layout is not yet recognised —
                    # see tools/known_gaps.py KNOWN_SKIPPED_TABLES).
                    continue
                failures.append(f"{entry['fqn']}: absent from decode")
                continue
            res = verify_table(ext, cells_dir, entry, level=level)
            if not res.ok:
                detail = (
                    res.col_mismatches
                    or res.digest_mismatches
                    or res.order_mismatches
                    or res.error
                )
                failures.append(f"{entry['fqn']}: {detail}")
    if failures and reason is not None:
        pytest.xfail(f"{reason}: {failures}")
    assert not failures, "; ".join(failures)


# --------------------------------------------------------------------------- #
# _arrow_column_digest unit tests — must match cell_canon.column_digest exactly
# --------------------------------------------------------------------------- #

@pytest.mark.quick
@pytest.mark.parametrize(
    "values,label",
    [
        ([], "empty"),
        ([None, None, None], "all_nulls"),
        (["a", "b", "c"], "simple_ascii"),
        (["z", "a", "m", None], "with_null"),
        (["über", "café", "日本語", "😀"], "unicode"),
        # Adjacent-length values: "aa" vs "a", "aaa" sort next to each other.
        # The length prefix ensures same-content-prefix values hash correctly.
        (["a", "aa", "aaa", "b", "ba"], "adjacent_length"),
        (["1", "10", "2", "9", "100"], "numeric_strings"),
        (["x"] * 1000, "many_duplicates"),
        (["", "a", " "], "empty_string_in_mix"),
    ],
)
def test_arrow_column_digest_matches_column_digest(
    values: list[str | None], label: str
) -> None:
    arr = pa.array(values, pa.string())
    ref = column_digest(values)
    got = _arrow_column_digest(arr)
    assert got == ref, f"{label}: arrow={got!r} ref={ref!r}"


@pytest.mark.quick
def test_arrow_column_digest_large_string_matches_string() -> None:
    """large_string (int64 offsets) must produce the same digest as string."""
    values = ["hello", None, "world", "über", ""]
    arr_str = pa.array(values, pa.string())
    arr_large = pa.array(values, pa.large_string())
    assert _arrow_column_digest(arr_str) == _arrow_column_digest(arr_large)
    assert _arrow_column_digest(arr_large) == column_digest(values)


@pytest.mark.quick
def test_arrow_column_digest_starts_with_sha256() -> None:
    arr = pa.array(["x"])
    assert _arrow_column_digest(arr).startswith("sha256:")


# --------------------------------------------------------------------------- #
# _canon_to_arrow unit tests — must match _canon_col per vectorized type
# --------------------------------------------------------------------------- #

@pytest.mark.quick
@pytest.mark.parametrize(
    "values,arrow_type,sql_type",
    [
        # Integer family — all integer Arrow types map to pc.cast(…, pa.string())
        ([-5, 0, 42, None], pa.int8(), "tinyint"),
        ([-100, 0, 32767, None], pa.int16(), "smallint"),
        ([-2**31, 0, 2**31 - 1, None], pa.int32(), "int"),
        ([-2**63 + 1, 0, 2**63 - 1, None], pa.int64(), "bigint"),
        ([0, 127, 255, None], pa.uint8(), "tinyint"),
        ([0, 65535, None], pa.uint16(), "smallint"),
        # String passthrough family
        (["hello", "world", None], pa.string(), "varchar"),
        (["α", "β", None], pa.string(), "nvarchar"),
        (["x", None], pa.large_string(), "text"),
        (["a", "b"], pa.string(), "hierarchyid"),
        # char/nchar: trailing-space trim
        (["abc   ", "hi", None, "  "], pa.string(), "char"),
        (["xy  ", "z", None], pa.string(), "nchar"),
        # uniqueidentifier: lowercase
        (["A1B2C3D4-E5F6-7890-ABCD-EF0000000000", None], pa.string(), "uniqueidentifier"),
        # bit: bool → "1"/"0"
        ([True, False, None], pa.bool_(), "bit"),
    ],
)
def test_canon_to_arrow_matches_canon_col_vectorized(
    values: list, arrow_type: pa.DataType, sql_type: str
) -> None:
    col = pa.array(values, arrow_type)
    py_list = col.to_pylist()
    expected = _canon_col(py_list, sql_type)
    got = _canon_to_arrow(col, sql_type).to_pylist()
    assert got == expected, f"sql_type={sql_type!r}: got={got} expected={expected}"


@pytest.mark.quick
@pytest.mark.parametrize(
    "sql_type",
    ["float", "real", "datetime", "binary", "varbinary", "xml"],
)
def test_canon_to_arrow_python_fallback_matches_canon_col(sql_type: str) -> None:
    """For types that need Python canon(), _canon_to_arrow falls back and matches."""
    # Use string inputs that are already in canonical form — ensures the fallback
    # path round-trips cleanly regardless of live SQL Server data.
    values = ["1.0", "2.0", None]
    col = pa.array(values, pa.string())
    expected = _canon_col(values, sql_type)
    got = _canon_to_arrow(col, sql_type).to_pylist()
    assert got == expected, f"sql_type={sql_type!r}: got={got} expected={expected}"


@pytest.mark.quick
def test_canon_to_arrow_chunked_array() -> None:
    """ChunkedArray input is handled (combine_chunks internally)."""
    chunks = [pa.array([1, 2], pa.int32()), pa.array([3, None], pa.int32())]
    chunked = pa.chunked_array(chunks)
    got = _canon_to_arrow(chunked, "int").to_pylist()
    assert got == ["1", "2", "3", None]


@pytest.mark.quick
def test_canon_to_arrow_uniqueidentifier_mixed_case() -> None:
    guids = [
        "A1B2C3D4-E5F6-7890-ABCD-EF1234567890",
        "a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # already lower
        None,
    ]
    col = pa.array(guids, pa.string())
    got = _canon_to_arrow(col, "uniqueidentifier").to_pylist()
    assert got == [g.lower() if g else None for g in guids]



# ---------------------------------------------------------------------------
# Vectorized digest parity tests (Change 1 & 2 of vectorize plan)
# ---------------------------------------------------------------------------

@pytest.mark.quick
@pytest.mark.parametrize(
    "values",
    [
        ["alpha", "beta", "gamma"],
        ["alpha", "beta", "gamma", "alpha"],  # duplicate
        [],
        [None, None],
        ["", "x", None, "y"],             # empty string + nulls
        ["\t hello\n", "back\\slash"],    # embedded whitespace / backslash
        ["A", "B", "C", "D", "E", "F"],
    ],
)
def test_multiset_digest_parity(values: list) -> None:
    """_arrow_column_digest (vectorized) must reproduce column_digest bit-for-bit."""
    arr = pa.array(values, type=pa.string())
    assert _arrow_column_digest(arr) == column_digest(values)


@pytest.mark.quick
def test_multiset_digest_parity_large_n() -> None:
    """Exercises the block boundary (>2M rows) in _arrow_column_digest."""
    n = 2_500_000
    values = [str(i) for i in range(n)]
    arr = pa.array(values, type=pa.string())
    assert _arrow_column_digest(arr) == column_digest(values)


@pytest.mark.quick
def test_multiset_digest_parity_block_boundary_nulls() -> None:
    """Nulls sprinkled across a 2M+ array; block splitting must not shift digest."""
    from tools.value_verify import _arrow_column_digest
    from tools.cell_canon import column_digest

    n = 2_200_000
    values = [None if i % 100 == 0 else str(i) for i in range(n)]
    arr = pa.array(values, type=pa.string())
    assert _arrow_column_digest(arr) == column_digest(values)


# ---------------------------------------------------------------------------
# Vectorized ordered-digest parity tests
# ---------------------------------------------------------------------------

@pytest.mark.quick
@pytest.mark.parametrize(
    "values",
    [
        ["alpha", "beta", "gamma"],
        ["alpha", None, "gamma", None, "delta"],
        [None, None, None],
        [],
        ["", "x", None],
        ["\t hello\n", "back\\slash"],
    ],
)
def test_ordered_digest_parity(values: list) -> None:
    """_arrow_ordered_column_digest (vectorized) must reproduce column_ordered_digest bit-for-bit."""
    from tools.value_verify import _arrow_ordered_column_digest
    from tools.cell_canon import column_ordered_digest

    arr = pa.array(values, type=pa.string())
    assert _arrow_ordered_column_digest(arr) == column_ordered_digest(values)


@pytest.mark.quick
def test_ordered_digest_parity_large_n() -> None:
    """Block boundary (>2M rows) with null every 7th row."""
    from tools.value_verify import _arrow_ordered_column_digest
    from tools.cell_canon import column_ordered_digest

    n = 2_200_000
    values = [None if i % 7 == 0 else str(i) for i in range(n)]
    arr = pa.array(values, type=pa.string())
    assert _arrow_ordered_column_digest(arr) == column_ordered_digest(values)


@pytest.mark.quick
def test_ordered_digest_parity_null_at_block_boundary() -> None:
    """Null precisely at the 2M-row block boundary."""
    from tools.value_verify import _arrow_ordered_column_digest, _HASH_BLOCK_ROWS
    from tools.cell_canon import column_ordered_digest

    B = _HASH_BLOCK_ROWS
    values: list = [str(i) for i in range(B - 1)] + [None] + [str(i) for i in range(100)]
    arr = pa.array(values, type=pa.string())
    assert _arrow_ordered_column_digest(arr) == column_ordered_digest(values)


@pytest.mark.quick
def test_ordered_digest_null_at_first_and_last() -> None:
    """Nulls at position 0 and last should produce a different digest from no-null."""
    from tools.value_verify import _arrow_ordered_column_digest
    from tools.cell_canon import column_ordered_digest

    vals_no_null = ["A", "B", "C"]
    vals_first_null: list = [None, "B", "C"]
    vals_last_null: list = ["A", "B", None]
    for vals in [vals_first_null, vals_last_null]:
        arr = pa.array(vals, type=pa.string())
        assert _arrow_ordered_column_digest(arr) == column_ordered_digest(vals)
    # And all three must differ from each other.
    d1 = column_ordered_digest(vals_no_null)
    d2 = column_ordered_digest(vals_first_null)
    d3 = column_ordered_digest(vals_last_null)
    assert d1 != d2 and d1 != d3 and d2 != d3


# ---------------------------------------------------------------------------
# Temporal canon fast-path parity tests (Change 3)
# ---------------------------------------------------------------------------

_D = _dt.date
_DT = _dt.datetime
_T = _dt.time

_TEMPORAL_NULL_CASES = [
    ([None], pa.date32(), "date"),
    ([None, None], pa.date32(), "date"),
]

_TEMPORAL_PARITY_CASES = [
    # date: no sub-day component
    ([None, _D(2024, 1, 15), _D(1, 1, 1), _D(9999, 12, 31)], pa.date32(), "date"),
    # datetime2 at us precision: with and without microseconds
    (
        [None, _DT(2024, 1, 15, 10, 30, 0), _DT(2024, 1, 15, 10, 30, 0, 123456), _DT(2000, 2, 29, 23, 59, 59, 999999)],
        pa.timestamp("us"),
        "datetime2",
    ),
    # datetime at ms precision: cast to us reproduces Python isoformat exactly
    ([None, _DT(2024, 1, 15, 10, 30, 0), _DT(2024, 1, 15, 10, 30, 0, 500000)], pa.timestamp("ms"), "datetime"),
    # smalldatetime at second precision: no decimal part
    ([None, _DT(2024, 1, 15, 10, 30, 0)], pa.timestamp("s"), "smalldatetime"),
    # time at us precision
    ([None, _T(10, 30, 0), _T(10, 30, 0, 123456)], pa.time64("us"), "time"),
]


@pytest.mark.quick
@pytest.mark.parametrize("values,arrow_type,sql_type", _TEMPORAL_NULL_CASES)
def test_temporal_canon_parity_nulls(values: list, arrow_type: pa.DataType, sql_type: str) -> None:
    """All-null temporal arrays must produce all-None canonical strings."""
    arr = pa.array(values, type=arrow_type)
    got = _canon_to_arrow(arr, sql_type).to_pylist()
    assert got == [None] * len(values)


@pytest.mark.quick
@pytest.mark.parametrize("py_values,arrow_type,sql_type", _TEMPORAL_PARITY_CASES)
def test_temporal_canon_parity(
    py_values: list, arrow_type: pa.DataType, sql_type: str
) -> None:
    """_canon_to_arrow temporal fast path must match Python canon() value-for-value."""
    arr = pa.array(py_values, type=arrow_type)
    got = _canon_to_arrow(arr, sql_type).to_pylist()
    expected = [canon(v, sql_type) for v in py_values]
    assert got == expected, f"mismatch for {sql_type}: {list(zip(got, expected))}"


@pytest.mark.quick
def test_float_uses_python_fallback() -> None:
    """float/real columns must still use the Python path (Arrow cast is not canon-compatible)."""
    arr = pa.array([1.5, 0.1, None], type=pa.float64())
    got = _canon_to_arrow(arr, "float").to_pylist()
    expected = [canon(v, "float") for v in [1.5, 0.1, None]]
    assert got == expected
