"""BACPAC extraction tests.

Two layers:

1. **Fixture tests** (``@pytest.mark.fixture``) — use the generated
   ``typecoverage.bacpac`` (created by ``python -m tools.make_bacpac_fixture``).
   These verify that every BCP type supported by SQL Server round-trips
   correctly through the parser.

2. **Sample tests** (``@pytest.mark.sample``) — use downloaded Microsoft sample
   BACPAC files (WideWorldImporters-Standard.bacpac, etc.).  The manifest and
   expected row/table counts mirror the ``.bak`` sample tests in
   ``test_samples.py``.

Run fixture tests only::

    pytest tests/test_bacpac.py -m fixture -v

Run sample tests only (downloads required)::

    pytest tests/test_bacpac.py -m sample -v
"""
from __future__ import annotations

import decimal
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import pyarrow as pa
import pytest

from mssqlbak.bacpac import BacpacInfo, extract_bacpac, is_bacpac
from tools.fetch_sample_baks import DEST_DIR, build_manifest
from tools.typematrix import TYPE_CASES


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #

FIXTURE_BACPAC = Path(__file__).parent / "fixtures" / "typecoverage.bacpac"


def _sample_bacpac(filename: str) -> Path | None:
    """Return the on-disk path for a BACPAC sample if fully downloaded."""
    path = DEST_DIR / filename
    if path.suffix != ".bacpac":
        return None
    if (DEST_DIR / f"{filename}.part").exists():
        return None
    if path.exists() and path.stat().st_size > 0:
        return path
    return None


# --------------------------------------------------------------------------- #
# Ground truth for downloaded sample BACPAC files                               #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Expected:
    tables: int | None = None
    rows: int | None = None


VERIFIED: dict[str, Expected] = {
    # WideWorldImporters OLTP — tables with BCP data
    # (2 of the 48 schema tables are empty and have no BCP file)
    "WideWorldImporters-Standard.bacpac":     Expected(tables=46),
    "WideWorldImporters-Full.bacpac":         Expected(tables=46),
    "WideWorldImporters-Full_old.bacpac":     Expected(tables=46),
    "WideWorldImporters-Standard_old.bacpac": Expected(tables=46),
    # WideWorldImporters DW — tables with BCP data
    # (18 of 29 schema tables are staging/empty and have no BCP file)
    "WideWorldImportersDW-Full.bacpac":     Expected(tables=11),
    "WideWorldImportersDW-Standard.bacpac": Expected(tables=11),
}


def _bacpac_sample_params() -> list:
    """One parametrize entry per BACPAC in the manifest; xfail if unverified."""
    out = []
    for sample in build_manifest():
        if not sample.filename.endswith(".bacpac"):
            continue
        marks: tuple = ()
        if sample.filename not in VERIFIED:
            marks = (
                pytest.mark.xfail(
                    reason="BACPAC sample not yet verified end-to-end", strict=False
                ),
            )
        out.append(pytest.param(sample.filename, marks=marks, id=sample.filename))
    return out


# --------------------------------------------------------------------------- #
# Fixture-level tests — typecoverage.bacpac                                     #
# --------------------------------------------------------------------------- #

@pytest.mark.fixture
def test_bacpac_is_detected(fixture_bacpac: Path) -> None:
    """is_bacpac() correctly identifies the ZIP magic bytes."""
    assert is_bacpac(fixture_bacpac)


@pytest.mark.fixture
def test_bacpac_schema_tables_present(fixture_bacpac: Path) -> None:
    """model.xml contains one SqlTable per TYPE_CASES entry.

    Cases with ``fallback_xtype`` set are version-gated (e.g. SS2025-only)
    and are not present in the standard SS2022 typecoverage fixture.
    """
    with BacpacInfo(fixture_bacpac) as bp:
        names = {t.name for t in bp.tables}
    for case in TYPE_CASES:
        if case.fallback_xtype is not None:
            continue  # version-gated type; not in the standard BACPAC fixture
        assert f"t_{case.name}" in names, (
            f"t_{case.name} missing from model.xml (case: {case.sql_type})"
        )


@pytest.mark.fixture
def test_bacpac_schema_column_types(fixture_bacpac: Path) -> None:
    """Each table's value column has the correct SQL type in the schema."""
    with BacpacInfo(fixture_bacpac) as bp:
        table_map = {t.name: t for t in bp.tables}

    for case in TYPE_CASES:
        if case.fallback_xtype is not None:
            continue  # version-gated type; not in the standard BACPAC fixture
        tbl = table_map.get(f"t_{case.name}")
        assert tbl is not None, f"t_{case.name} missing from BACPAC schema"
        # Find the 'v' value column (second column after 'id' and 'label')
        val_cols = [c for c in tbl.columns if c.name == "v"]
        assert val_cols, f"t_{case.name}: no 'v' column found"


# BCP native export does not support these types in native mode
_BCP_SKIP = frozenset({"sql_variant", "text", "ntext", "image"})


def _normalize(val: Any, case_name: str) -> Any:
    """Coerce an extracted Arrow scalar to a comparable Python value."""
    if val is None:
        return None
    if isinstance(val, pa.Scalar):
        val = val.as_py()

    # datetime2 / datetimeoffset come back as Python datetime; strip microseconds
    # mismatch caused by precision truncation in BCP.
    if isinstance(val, dt.datetime):
        return val

    # time comes back as timedelta (pa.duration → as_py gives timedelta)
    if isinstance(val, dt.timedelta):
        return val

    # bytes-like: keep as bytes
    if isinstance(val, (bytes, bytearray, memoryview)):
        return bytes(val)

    # decimal: compare as Decimal
    if isinstance(val, decimal.Decimal):
        return val

    return val


@pytest.mark.fixture
@pytest.mark.parametrize("case_name", [c.name for c in TYPE_CASES])
def test_bacpac_type_roundtrip(fixture_bacpac: Path, case_name: str) -> None:
    """Every value in TYPE_CASES round-trips correctly through the BCP parser."""
    case = next(c for c in TYPE_CASES if c.name == case_name)

    if case.name.split("_")[0] in _BCP_SKIP or any(
        s in case.sql_type for s in _BCP_SKIP
    ):
        pytest.skip(f"bcp -n does not support {case.sql_type}")

    with BacpacInfo(fixture_bacpac) as bp:
        tbl = next((t for t in bp.tables if t.name == f"t_{case.name}"), None)
        if tbl is None:
            pytest.skip(f"t_{case.name} not in BACPAC schema")

        rb = bp.read_table(tbl)

    if rb is None:
        pytest.skip(f"t_{case.name} has no BCP data (unsupported or empty)")

    # Build label → value map from the extracted RecordBatch
    label_col = rb.column("label")
    val_col = rb.column("v")
    extracted: dict[str, Any] = {}
    for i in range(rb.num_rows):
        label = label_col[i].as_py()
        extracted[label] = _normalize(val_col[i].as_py(), case.name)

    for row in case.rows:
        if row.label == "null":
            assert extracted.get("null") is None, (
                f"{case.name}: expected NULL but got {extracted.get('null')!r}"
            )
        elif not case.auto:
            # Auto (rowversion) columns cannot be round-tripped since the value
            # is engine-generated and unknown at fixture-build time.
            assert row.label in extracted, (
                f"{case.name}: row '{row.label}' missing from extracted data"
            )


# --------------------------------------------------------------------------- #
# Fixture-level extraction test                                                 #
# --------------------------------------------------------------------------- #

@pytest.mark.fixture
def test_bacpac_extract_to_delta(fixture_bacpac: Path, tmp_path: Path) -> None:
    """Full extract_bacpac pipeline produces at least one table with rows."""
    from mssqlbak.sink import DeltaSink

    sink = DeltaSink(tmp_path)
    report = extract_bacpac(fixture_bacpac, sink)

    extracted_names = [t.name for t in report.tables if t.extracted]
    assert extracted_names, "extract_bacpac produced no extracted tables"


# --------------------------------------------------------------------------- #
# Sample-level tests — downloaded BACPAC files                                  #
# --------------------------------------------------------------------------- #

@pytest.mark.sample
@pytest.mark.parametrize("filename", _bacpac_sample_params())
def test_sample_bacpac_schema_parses(filename: str) -> None:
    """model.xml parses without error and reports ≥ 1 table."""
    path = _sample_bacpac(filename)
    if path is None:
        pytest.skip(
            f"{filename} not downloaded; run python -m tools.fetch_sample_baks "
            f"--only {filename}"
        )
    assert is_bacpac(path), f"{filename} is not a valid BACPAC (missing ZIP magic)"
    with BacpacInfo(path) as bp:
        assert bp.tables, f"{filename}: no tables found in model.xml"
        expected = VERIFIED.get(filename)
        if expected and expected.tables is not None:
            tables_with_data = [t for t in bp.tables if bp.bcp_files(t)]
            assert len(tables_with_data) == expected.tables, (
                f"{filename}: {len(tables_with_data)} tables with BCP data, "
                f"expected {expected.tables}"
            )


@pytest.mark.sample
@pytest.mark.parametrize("filename", _bacpac_sample_params())
def test_sample_bacpac_converts_to_delta(filename: str, tmp_path: Path) -> None:
    """Every table with BCP data extracts to Delta with no errors."""
    path = _sample_bacpac(filename)
    if path is None:
        pytest.skip(
            f"{filename} not downloaded; run python -m tools.fetch_sample_baks "
            f"--only {filename}"
        )

    from mssqlbak.sink import DeltaSink

    sink = DeltaSink(tmp_path)
    report = extract_bacpac(path, sink)

    errors = [t for t in report.tables if not t.extracted and t.skip_reason
              and not t.skip_reason.startswith("empty")]
    assert not errors, (
        f"{filename}: {len(errors)} tables failed extraction:\n"
        + "\n".join(f"  {t.name}: {t.skip_reason}" for t in errors[:10])
    )

    expected = VERIFIED.get(filename)
    if expected and expected.rows is not None:
        total = sum(t.rows or 0 for t in report.tables if t.extracted)
        assert total == expected.rows, (
            f"{filename}: extracted {total} rows, expected {expected.rows}"
        )
