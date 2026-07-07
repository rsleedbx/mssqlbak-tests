from __future__ import annotations

from mssqlbak.confidence import Severity, analyze_bak


def test_corrupt_metadata_confidence_fails_catalog_recovery(
    fixture_bak_corrupt_metadata_confidence,
) -> None:
    report = analyze_bak(fixture_bak_corrupt_metadata_confidence)

    assert report.status is Severity.FAIL
    assert any(
        check.name == "catalog_consistency" and check.severity is Severity.FAIL
        for check in report.checks
    )
