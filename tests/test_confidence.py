from __future__ import annotations

import json
from pathlib import Path

import pytest

from mssqlbak.confidence import (
    ConfidenceCheck,
    ConfidenceReport,
    Severity,
    analyze_bak,
)
from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore


def test_confidence_report_rollup_prefers_failed_checks() -> None:
    report = ConfidenceReport(
        bak_name="sample.bak",
        checks=[
            ConfidenceCheck("file_identity", Severity.PASS, "sha256 recorded"),
            ConfidenceCheck("row_count", Severity.FAIL, "decoded 7 rows, expected 8"),
        ],
    )

    assert report.status is Severity.FAIL


def test_confidence_report_rollup_allows_warnings() -> None:
    report = ConfidenceReport(
        bak_name="sample.bak",
        checks=[
            ConfidenceCheck("file_identity", Severity.PASS, "sha256 recorded"),
            ConfidenceCheck("btree_order", Severity.WARN, "no clustered key available"),
        ],
    )

    assert report.status is Severity.WARN


def test_chinook_id_pk_reports_multiple_backup_sets() -> None:
    bak = Path("tests/fixtures_realworld/Chinook-id-pk.bak")
    if not bak.exists():
        pytest.skip("Chinook-id-pk.bak not downloaded")

    report = analyze_bak(bak)

    check = next(c for c in report.checks if c.name == "backup_set_selection")
    assert check.severity is Severity.WARN
    assert check.evidence["backup_sets"] == 2

    file_identity = next(c for c in report.checks if c.name == "file_identity")
    assert file_identity.severity is Severity.PASS
    assert len(str(file_identity.evidence["sha256"])) == 64


def test_chinook_employee_row_count_matches_catalog() -> None:
    bak = Path("tests/fixtures_realworld/Chinook-id-pk.bak")
    if not bak.exists():
        pytest.skip("Chinook-id-pk.bak not downloaded")

    report = analyze_bak(bak)

    employee = [
        c
        for c in report.checks
        if c.name == "row_count_consistency" and c.table == "dbo.Employee"
    ][0]
    assert employee.severity is Severity.PASS
    assert employee.evidence["decoded_rows"] == 8
    assert employee.evidence["catalog_rows"] == 8


@pytest.mark.parametrize("filename", ["AdventureWorksLT2012.bak", "BaseballData.bak"])
def test_realworld_page_structure_checks_pass(filename: str) -> None:
    bak = Path("tests/fixtures_realworld") / filename
    if not bak.exists():
        pytest.skip(f"{filename} not downloaded")

    report = analyze_bak(bak)

    page_checks = [c for c in report.checks if c.name == "page_structure"]
    assert page_checks
    assert {c.severity for c in page_checks} == {Severity.PASS}


def test_confidence_report_cli_json(capsys: pytest.CaptureFixture[str]) -> None:
    bak = Path("tests/fixtures_realworld/Chinook-id-pk.bak")
    if not bak.exists():
        pytest.skip("Chinook-id-pk.bak not downloaded")

    from tools.confidence_report import main

    assert main(["--json", str(bak)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out[0]["bak_name"] == "Chinook-id-pk.bak"
    assert out[0]["status"] == "warn"
    assert any(c["name"] == "backup_set_selection" for c in out[0]["checks"])


def test_columnstore_tables_emit_metadata_confidence() -> None:
    bak = Path("tests/fixtures_2022/columnstore_minimal.bak")
    if not bak.exists():
        pytest.skip("columnstore_minimal.bak not generated")

    report = analyze_bak(bak)

    checks = [c for c in report.checks if c.name == "columnstore_metadata_consistency"]
    assert checks
    assert {c.severity for c in checks} == {Severity.PASS}


@pytest.mark.parametrize(
    "filename,fqn,expected_rows",
    [
        ("WideWorldImporters-Full.bak", "Sales.CustomerTransactions", 97_147),
        ("WideWorldImporters-Full.bak", "Purchasing.SupplierTransactions", 2_438),
        ("WideWorldImportersDW-Full.bak", "Fact.Movement", 236_667),
        ("WideWorldImportersDW-Full.bak", "Fact.Order", 231_412),
        ("WideWorldImportersDW-Full.bak", "Fact.Purchase", 8_367),
        ("WideWorldImportersDW-Full.bak", "Fact.Sale", 228_265),
        ("WideWorldImportersDW-Full.bak", "Fact.Transaction", 99_585),
    ],
)
def test_partitioned_catalog_rows_sum_data_partitions(
    filename: str, fqn: str, expected_rows: int
) -> None:
    bak = Path("tests/fixtures_realworld") / filename
    if not bak.exists():
        pytest.skip(f"{filename} not downloaded")

    schema = recover_schema(PageStore.from_bak(bak))
    table = next(t for t in schema.tables if f"{t.schema}.{t.name}" == fqn)

    assert table.catalog_rows == expected_rows
