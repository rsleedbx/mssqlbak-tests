"""Table-organization × data-type regression tests.

Validates that every SQL Server data type decodes correctly across all five
table organizations (plain, heap, cluster, partition, column).  Each test reads
the wide ``tt_{org}`` table from the fixture and compares every decoded column
value against the reference in ``tools/tabletypematrix.py``.

Fixture
-------
The fixture is generated once by ``tools/make_tabletype_fixture.py`` (requires a
running SQL Server container) and committed to tests/fixtures/.  Tests skip when
the fixture file is absent.

Parametrisation
---------------
``test_full_{org}_{type}`` — 5 orgs × 33 types = **165 test cases**.
Each case reads ONE column from the wide table and checks all four rows
(low / high / mid / null) against the reference matrix.

Running
-------
    pytest tests/test_tabletype_coverage.py -q                  # all
    pytest -k "test_full_plain" -q                              # one org
    pytest -k "test_full_column_bit" -q                         # one cell

Incremental (differential) tests
---------------------------------
``test_diff_{org}_{type}`` — same matrix, but against the differential fixture
merged onto the full base via ``PageStore.from_diff_bak``.  Both full and diff
paths are fully implemented and passing (see docs/BACKUP_COVERAGE.md).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.tabletypematrix import (
    COLUMNSTORE_XFAIL,
    LABEL_ID,
    LABELS,
    ORG_CASES,
    OrgCase,
    supported_cases,
    table_name,
)
from tools.typematrix import TypeCase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reference_values(case: TypeCase) -> dict[str, Any]:
    """Return {label: expected_value} for this TypeCase."""
    return {row.label: row.value for row in case.rows}


def _decode_org(
    fixture: Path | PageStore, org: OrgCase
) -> dict[str, dict[str, Any]]:
    """Read ``tt_{org.name}`` and return ``{column_name: {label: decoded_value}}``.

    Labels are inferred from ``id`` using LABEL_ID reversed.  *fixture* may be
    a ``Path`` (opened via ``PageStore.from_bak``) or an already-built
    ``PageStore`` (e.g. a merged differential store).
    """
    id_to_label = {v: k for k, v in LABEL_ID.items()}
    store = PageStore.from_bak(fixture) if isinstance(fixture, Path) else fixture
    schema = recover_schema(store)
    tbl_name = table_name(org)
    table = next((t for t in schema.tables if t.name == tbl_name), None)
    if table is None:
        fixture_label = fixture.name if isinstance(fixture, Path) else repr(fixture)
        pytest.fail(f"Table {tbl_name!r} not found in fixture {fixture_label}")
    result: dict[str, dict[str, Any]] = {}
    for row in read_table_rows(store, table):
        row_id: int = row["id"]
        label = id_to_label.get(row_id, f"id{row_id}")
        for col_name, val in row.items():
            if col_name == "id":
                continue
            result.setdefault(col_name, {})[label] = val
    return result


# ---------------------------------------------------------------------------
# Parametrize IDs
# ---------------------------------------------------------------------------

def _full_params() -> list[tuple[OrgCase, TypeCase]]:
    params = []
    for org in ORG_CASES:
        for case in supported_cases(org):
            params.append((org, case))
    return params


FULL_PARAMS = _full_params()
FULL_IDS = [f"{org.name}_{case.name}" for org, case in FULL_PARAMS]


# ---------------------------------------------------------------------------
# Full-backup tests — 165 cases (5 orgs × 33 types, minus columnstore skips)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("org,case", FULL_PARAMS, ids=FULL_IDS)
def test_full(
    fixture_bak_tabletype: Path, org: OrgCase, case: TypeCase,
    request: pytest.FixtureRequest,
) -> None:
    """Decoded column value matches the reference matrix for every row label."""
    if org.name == "column" and case.name in COLUMNSTORE_XFAIL:
        request.applymarker(pytest.mark.xfail(
            strict=False,
            reason=(
                f"columnstore decoder does not yet handle {case.name!r}: "
                "either enc=5 (raw bytes, not implemented) or a known value "
                "conversion bug for extreme/empty values"
            ),
        ))

    # Read once per org per test run.  Pytest's fixture caching won't help here
    # (fixture_bak_tabletype is function-scoped), but PageStore.from_bak is fast
    # for the small fixture; a session-scoped cache would complicate parametrize.
    decoded = _decode_org(fixture_bak_tabletype, org)
    col_name = f"c_{case.name}"

    if col_name not in decoded:
        if case.fallback_xtype is not None:
            pytest.skip(
                f"{case.name!r} is not present in {table_name(org)!r}; "
                "covered by its version-specific fixture"
            )
        pytest.fail(f"Column {col_name!r} missing from {table_name(org)!r}")

    col_vals = decoded[col_name]
    ref = _reference_values(case)

    for label in LABELS:
        if label not in ref:
            continue  # type case doesn't define this label
        expected = ref[label]
        if label not in col_vals:
            pytest.fail(f"Row label {label!r} not found in {table_name(org)!r}")
        actual = col_vals[label]

        if case.auto:
            # rowversion / engine-populated: just assert non-NULL presence
            assert actual is not None, (org.name, case.name, label)
        elif expected is None:
            assert actual is None, (org.name, case.name, label, actual)
        else:
            assert actual == expected, (org.name, case.name, label)


# ---------------------------------------------------------------------------
# Differential (incremental) tests — base-merge + delta-store reading fully
# implemented; all org types pass.
# ---------------------------------------------------------------------------

@pytest.mark.fixture
@pytest.mark.parametrize("org,case", FULL_PARAMS, ids=FULL_IDS)
def test_diff(
    fixture_bak_tabletype: Path,
    fixture_bak_tabletype_diff: Path,
    org: OrgCase,
    case: TypeCase,
    request: pytest.FixtureRequest,
) -> None:
    """After merging the differential onto the full base, extra rows appear.

    The differential fixture adds two extra rows per table (id=5 and id=6).
    Each row mirrors the 'low' and 'high' reference values respectively.
    """

    store = PageStore.from_diff_bak(fixture_bak_tabletype_diff, fixture_bak_tabletype)
    decoded = _decode_org(store, org)
    col_name = f"c_{case.name}"
    col_vals = decoded.get(col_name, {})
    if not col_vals and case.fallback_xtype is not None:
        pytest.skip(
            f"{case.name!r} is not present in {table_name(org)!r}; "
            "covered by its version-specific fixture"
        )

    # After merge: 4 original + 2 extra = 6 rows per org.
    assert len(col_vals) == 6, (
        f"{table_name(org)}.{col_name}: expected 6 rows after diff merge, "
        f"got {len(col_vals)}"
    )

    # Extra rows mirror low/high values with new ids (5 = low copy, 6 = high copy).
    ref = _reference_values(case)
    for extra_label, src_label in [("id5", "low"), ("id6", "high")]:
        if extra_label not in col_vals:
            pytest.fail(f"Extra row {extra_label!r} not found after diff merge")
        if not case.auto and src_label in ref and ref[src_label] is not None:
            assert col_vals[extra_label] == ref[src_label], (
                org.name, case.name, extra_label
            )


# ---------------------------------------------------------------------------
# Smoke test: fixture schema is complete
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_tabletype_fixture_has_all_org_tables(fixture_bak_tabletype: Path) -> None:
    """Every org table exists in the fixture database."""
    store = PageStore.from_bak(fixture_bak_tabletype)
    schema = recover_schema(store)
    table_names = {t.name for t in schema.tables}
    for org in ORG_CASES:
        assert table_name(org) in table_names, (
            f"Table {table_name(org)!r} missing from fixture"
        )


@pytest.mark.fixture
def test_tabletype_fixture_row_counts(fixture_bak_tabletype: Path) -> None:
    """Each org table contains exactly 4 rows (one per label)."""
    store = PageStore.from_bak(fixture_bak_tabletype)
    schema = recover_schema(store)
    for org in ORG_CASES:
        tbl = next((t for t in schema.tables if t.name == table_name(org)), None)
        if tbl is None:
            pytest.fail(f"Table {table_name(org)!r} not found")
        rows = list(read_table_rows(store, tbl))
        assert len(rows) == len(LABELS), (
            f"{table_name(org)}: expected {len(LABELS)} rows, got {len(rows)}"
        )
