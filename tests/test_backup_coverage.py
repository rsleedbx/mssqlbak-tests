"""Guard: the committed backup-type-coverage doc must match a fresh generation.

Keeps ``docs/BACKUP_COVERAGE.md`` honest -- every row marked SUPPORTED carries a
validator that runs against the committed fixtures, so if the full-restore path
regresses (or a row's status changes), this test fails until the doc is
regenerated with ``python -m tools.backup_coverage``.
"""
from __future__ import annotations

import pytest

from tools.backup_coverage import (
    KINDS,
    SUPPORTED,
    DOC_PATH,
    build_report,
)


@pytest.mark.fixture
def test_backup_coverage_doc_is_current() -> None:
    expected = build_report()
    actual = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    assert actual == expected, (
        "docs/BACKUP_COVERAGE.md is stale; regenerate it with "
        "`python -m tools.backup_coverage`"
    )


def test_every_supported_kind_has_a_validator() -> None:
    """A SUPPORTED backup type with no validator cannot be trusted -- disallow it."""
    unvalidated = [
        k.name for k in KINDS if k.status == SUPPORTED and k.validate is None
    ]
    assert not unvalidated, (
        f"SUPPORTED backup types need a validator: {unvalidated}"
    )


@pytest.mark.fixture
def test_all_supported_claims_hold() -> None:
    """Every SUPPORTED validator must pass against the committed fixtures."""
    broken = [
        k.name
        for k in KINDS
        if k.status == SUPPORTED and k.validate is not None and not k.validate()
    ]
    assert not broken, f"SUPPORTED backup types failing validation: {broken}"


@pytest.mark.fixture
def test_full_database_backup_is_supported() -> None:
    """The first-priority capability -- full restore -- must stay SUPPORTED."""
    full = next(k for k in KINDS if k.name == "Full database backup")
    assert full.status == SUPPORTED
    assert full.validate is not None and full.validate()
