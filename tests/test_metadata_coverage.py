"""Guard: the committed metadata-coverage doc must match a fresh generation.

Keeps ``docs/METADATA_COVERAGE.md`` in sync with the actual parser results on
every run -- if an EXPOSED field stops resolving on the fixture, or the field
registry changes, this test fails until the doc is regenerated with
``python -m tools.metadata_coverage``.
"""
from __future__ import annotations

import pytest

from mssqlbak.reader import read_bak_metadata
from tools.metadata_coverage import EXPOSED, FIELDS, DOC_PATH, _present, build_report


@pytest.mark.fixture
def test_metadata_coverage_doc_is_current(fixture_bak) -> None:
    expected = build_report(fixture_bak)
    actual = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    assert actual == expected, (
        "docs/METADATA_COVERAGE.md is stale; regenerate it with "
        "`python -m tools.metadata_coverage`"
    )


@pytest.mark.fixture
def test_all_exposed_metadata_fields_present(fixture_bak) -> None:
    """Every field marked EXPOSED must actually resolve on the fixture."""
    meta = read_bak_metadata(fixture_bak)
    missing = [
        m.name
        for m in FIELDS
        if m.status == EXPOSED
        and not m.optional
        and m.getter is not None
        and not _present(m.getter(meta))
    ]
    assert not missing, f"EXPOSED metadata fields absent on fixture: {missing}"


def test_every_exposed_field_has_a_getter() -> None:
    """An EXPOSED field without a getter cannot be validated -- disallow it."""
    ungettable = [m.name for m in FIELDS if m.status == EXPOSED and m.getter is None]
    assert not ungettable, f"EXPOSED fields need a getter for validation: {ungettable}"
