"""Coverage test for the PAGE-compression long-prefix decode regression.

SQL Server's PAGE-compression prefix encoder emits a two-byte extended form
``[0x80][plen]`` when the shared prefix between a row value and the page anchor
is ≥ 128 bytes.  Before the fix in ``rust/src/page_compress.rs``, the Rust
``expand_prefix`` function mis-read ``0x80`` as a literal prefix length of 128
and then included the actual plen byte as part of the expanded value, corrupting
all rows that triggered the extended form.

The fixture creates a PAGE-compressed ``NVARCHAR(400)`` column whose 100 rows
all share a 70-character ASCII prefix (70 × 2 = 140 UTF-16LE bytes > 128).
Every row therefore exercises the ``0x80 <len>`` path.  A correct decode
returns the exact ``SHARED_PREFIX + suffix`` string; the pre-fix symptom was a
value starting with ``SHARED_PREFIX[:1] + chr(0x82) + …`` (the plen byte
embedded in the output).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows  # type: ignore[attr-defined]
from tools.make_pagecomp_long_prefix_fixture import (
    EXPECTED,
    ROW_COUNT,
    SHARED_PREFIX,
    TABLE,
)

pytestmark = pytest.mark.fixture


def _rows(bak: Path) -> list[dict]:
    store = PageStore.from_bak(str(bak))
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == TABLE)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


def test_row_count(fixture_bak_pagecomp_long_prefix: Path) -> None:
    rows = _rows(fixture_bak_pagecomp_long_prefix)
    assert len(rows) == ROW_COUNT


def test_all_rows_have_correct_prefix(fixture_bak_pagecomp_long_prefix: Path) -> None:
    """Every decoded value must begin with SHARED_PREFIX.

    Before the expand_prefix fix, values with a 140-byte UTF-16LE anchor prefix
    would start with a corrupted first character because the extended 0x80 plen
    byte was spliced into the output instead of being consumed as metadata.
    """
    rows = _rows(fixture_bak_pagecomp_long_prefix)
    bad = [
        (r["id"], r["descr"])
        for r in rows
        if not isinstance(r["descr"], str) or not r["descr"].startswith(SHARED_PREFIX)
    ]
    assert not bad, (
        f"{len(bad)} row(s) do not start with the expected 70-char prefix:\n"
        + "\n".join(f"  id={row_id!r}: {val!r}" for row_id, val in bad[:5])
    )


def test_exact_values_match_expected(fixture_bak_pagecomp_long_prefix: Path) -> None:
    """Each row must decode to the exact expected string."""
    rows = _rows(fixture_bak_pagecomp_long_prefix)
    by_id = {r["id"]: r["descr"] for r in rows}
    mismatches = {
        row_id: (by_id.get(row_id), want)
        for row_id, want in EXPECTED.items()
        if by_id.get(row_id) != want
    }
    assert not mismatches, (
        f"{len(mismatches)} row(s) do not match expected values:\n"
        + "\n".join(
            f"  id={row_id}: got={got!r} want={want!r}"
            for row_id, (got, want) in list(mismatches.items())[:5]
        )
    )


def test_shared_prefix_long_enough_to_trigger_extended_plen() -> None:
    """Sanity-check: the fixture prefix must be ≥ 64 chars (128 UTF-16LE bytes)."""
    assert len(SHARED_PREFIX) >= 64, (
        f"prefix is only {len(SHARED_PREFIX)} chars = {len(SHARED_PREFIX) * 2} bytes; "
        "must be ≥ 64 chars to exceed the 128-byte threshold for extended plen"
    )
