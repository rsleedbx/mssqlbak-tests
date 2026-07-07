"""Decode-path census regression test.

Verifies that each heuristic decision point in the string/LOB decoders takes
the same code path for the sentinel fixtures as recorded in
``tests/census_baseline.json``.

Why this exists
---------------
The string/LOB decoder stack is built from **magic-byte heuristics**, not
grounded discriminators.  Each "fix" can silently flip a branch for a
fixture that wasn't being tested at the time.  The census captures, per
``(fixture, table)``, the *sorted unique set* of branch tags emitted during a
full table extraction.  When a heuristic changes, the census changes — and
this test fails immediately, *before* column digests need to be recomputed.

How to update
-------------
Run::

    MSSQLBAK_DECODE_TRACE=1 python tools/diag/_cli.py census \\
        --version 2022 --output tests/census_baseline.json

after verifying that the heuristic change is intentional and correct for all
affected fixtures.

Heuristic tags documented in ``mssqlbak/decode_trace.py``.

Coverage notes
--------------
The following tags are defined but not currently covered by any fixture in the
baseline (they represent rare or legacy paths):

    align:nrows-nonzero  — constant-encoded enc=1 blob (all values identical)
    align:deinterleave   — legacy pre-2012 CCI with 12-byte LOB preamble
    u21:strip-all        — row-store inline varchar(max)/varbinary(max) with 0x21 prefix
    enc5:multichunk      — large-n multi-chunk XPRESS path (n > 32 767)
    v4split:empty        — empty xVelocity v4 record buffer
    v4split:char-multi   — multi-value CHAR(n) packed into one record handle
    dict:utf16-ok        — small enc=3 string dict decoded as UTF-16LE
    dict:cp1252-ok       — small enc=3 string dict decoded as cp1252
    dict:binary          — small enc=3 binary dict
    dict:empty           — empty small dict
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO = Path(__file__).resolve().parent.parent
_BASELINE_PATH = _REPO / "tests" / "census_baseline.json"

# The 9 baseline fixtures — all live under tests/fixtures_2022/.
_BASELINE_FIXTURES: list[str] = [
    "archive_columnstore_types_full.bak",
    "cci_extended_full.bak",
    "cci_lob_full.bak",
    "cci_string_minmax_full.bak",
    "columnstore_minimal.bak",
    "cs_lob_preamble.bak",
    "cs_lob_preamble2.bak",
    "nvarchar_max_u21_full.bak",
    "tabletypecoverage_full.bak",
]


def _run_census(version: str = "2022") -> dict[str, dict[str, list[str]]]:
    """Extract all baseline fixtures with tracing enabled.

    Returns ``{fixture_key: {table: sorted_unique_tags}}``.
    """
    os.environ["MSSQLBAK_DECODE_TRACE"] = "1"
    # Reload decode_trace so _ACTIVE is True even if the module was already
    # imported before the env flag was set.
    if "mssqlbak.decode_trace" in sys.modules:
        dt_mod = importlib.reload(sys.modules["mssqlbak.decode_trace"])
    else:
        import mssqlbak.decode_trace as dt_mod  # type: ignore[assignment]

    from mssqlbak.catalog import recover_schema  # type: ignore[attr-defined]
    from mssqlbak.pages import PageStore  # type: ignore[attr-defined]
    from mssqlbak.rows import read_table_rows  # type: ignore[attr-defined]

    fixtures_dir = _REPO / "tests" / f"fixtures_{version}"
    result: dict[str, dict[str, list[str]]] = {}

    for fname in _BASELINE_FIXTURES:
        bak = fixtures_dir / fname
        key = f"fixtures_{version}/{fname}"
        if not bak.exists():
            pytest.skip(f"Fixture not found: {bak}")

        store = PageStore.from_bak(bak)
        schema = recover_schema(store)
        tbl_tags: dict[str, list[str]] = {}
        for tbl in schema.tables or []:
            dt_mod.reset()
            try:
                for _ in read_table_rows(store, tbl, schema.obj_to_name or {}):
                    pass
            except Exception:
                pass
            raw = dt_mod.get_and_reset()
            unique = sorted(set(raw))
            if unique:
                tbl_tags[tbl.name] = unique
        result[key] = tbl_tags

    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_census_baseline_exists() -> None:
    """The census baseline JSON file must be present and parseable."""
    assert _BASELINE_PATH.exists(), (
        f"census baseline not found: {_BASELINE_PATH}\n"
        "Run: MSSQLBAK_DECODE_TRACE=1 python tools/diag/_cli.py census "
        "--version 2022 --output tests/census_baseline.json"
    )
    data = json.loads(_BASELINE_PATH.read_text())
    assert isinstance(data, dict)
    assert len(data) >= 1


def test_census_matches_baseline() -> None:
    """All baseline fixtures must produce exactly the same branch tags as recorded.

    A diff means a heuristic decision point changed code path for at least one
    table.  Verify the change is intentional, fix any affected fixtures, then
    update the baseline.
    """
    baseline = json.loads(_BASELINE_PATH.read_text())
    got = _run_census()

    diffs: list[str] = []
    for fixture_key, expected_tables in baseline.items():
        got_tables = got.get(fixture_key, {})
        for table, expected_tags in expected_tables.items():
            got_tags = got_tables.get(table, [])
            if got_tags != expected_tags:
                diffs.append(
                    f"  {fixture_key}/{table}:\n"
                    f"    baseline = {expected_tags}\n"
                    f"    got      = {got_tags}"
                )

    if diffs:
        pytest.fail(
            "Decode-path census CHANGED — a heuristic branch flipped.\n"
            "Verify the change is intentional, then update tests/census_baseline.json.\n\n"
            + "\n".join(diffs)
        )
