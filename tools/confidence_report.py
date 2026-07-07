#!/usr/bin/env python3
"""Offline confidence report for SQL Server .bak extraction.

Usage examples
--------------
# Basic text report (existing behaviour)
python -m tools.confidence_report path/to.bak

# JSON output
python -m tools.confidence_report --json path/to.bak

# Constraint report — markdown written next to the .bak (or to stdout)
python -m tools.confidence_report --report constraints path/to.bak
python -m tools.confidence_report --report constraints --output-dir /tmp path/to.bak

# Constraint report for CCI segments (requires env var)
MSSQLBAK_CONSTRAINT_CHECKS=1 python -m tools.confidence_report --report constraints path/to.bak
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from mssqlbak.confidence import ConfidenceCheck, ConfidenceReport, Severity, analyze_bak


def _check_to_dict(check: ConfidenceCheck) -> dict[str, Any]:
    return {
        "name": check.name,
        "severity": check.severity.value,
        "message": check.message,
        "table": check.table,
        "evidence": check.evidence,
    }


def _report_to_dict(report: ConfidenceReport) -> dict[str, Any]:
    return {
        "bak_name": report.bak_name,
        "status": report.status.value,
        "checks": [_check_to_dict(check) for check in report.checks],
    }


def _print_text(reports: list[ConfidenceReport]) -> None:
    for report in reports:
        print(f"{report.bak_name}: {report.status.value}")
        for check in report.checks:
            scope = f" [{check.table}]" if check.table else ""
            print(f"  {check.severity.value} {check.name}{scope}: {check.message}")


def _constraint_summary(report: ConfidenceReport) -> str:
    """One-line summary of constraint check results, grouped by check type."""
    n_fail = sum(1 for c in report.checks if c.severity is Severity.FAIL)
    n_warn = sum(1 for c in report.checks if c.severity is Severity.WARN)
    n_pass = sum(1 for c in report.checks if c.severity is Severity.PASS)
    n_total = n_fail + n_warn + n_pass

    # Failure counts per category
    fail_by_type: dict[str, int] = {}
    for c in report.checks:
        if c.severity is Severity.FAIL:
            fail_by_type[c.name] = fail_by_type.get(c.name, 0) + 1

    detail = ", ".join(f"{name}: {cnt}F" for name, cnt in sorted(fail_by_type.items()))
    detail_str = f"  [{detail}]" if detail else ""
    return (
        f"  (constraints) {n_total} total · {n_pass} pass · {n_fail} fail"
        + detail_str
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate offline confidence checks for SQL Server .bak files"
    )
    parser.add_argument("--json", action="store_true", help="write JSON output")
    parser.add_argument(
        "--report",
        choices=["constraints"],
        help="report type; 'constraints' writes a markdown constraint report",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "directory for --report output files; "
            "if omitted the report is written to stdout"
        ),
    )
    parser.add_argument("baks", nargs="+", type=Path, help="backup files to analyze")
    args = parser.parse_args(argv)

    reports = [analyze_bak(path) for path in args.baks]

    if args.report == "constraints":
        for report, path in zip(reports, args.baks):
            md = report.to_markdown()
            if args.output_dir is not None:
                args.output_dir.mkdir(parents=True, exist_ok=True)
                out_path = args.output_dir / f"{path.stem}.constraints.md"
                out_path.write_text(md, encoding="utf-8")
                print(f"Written: {out_path}")
                print(_constraint_summary(report))
            else:
                print(md)
        return 0

    if args.json:
        print(json.dumps([_report_to_dict(report) for report in reports], indent=2))
    else:
        _print_text(reports)
    return 0


if __name__ == "__main__":
    sys.exit(main())
