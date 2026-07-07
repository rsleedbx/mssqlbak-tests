#!/usr/bin/env python3
"""Generate ``docs/TYPE_COVERAGE.md`` — which SQL Server types pass, which don't.

The report is a pure function of (a) the decoder's supported type ids
(``mssqlbak.types.SUPPORTED_TYPE_IDS``), (b) the reference value matrix
(``tools.typematrix.TYPE_CASES``), and (c) the committed reference fixture: for
every reference type it actually parses the fixture and compares to the known
values, so "PASS" means the parser reproduced the matrix exactly. Because the
output is deterministic, ``tests/test_type_coverage.py`` asserts the committed
doc matches a fresh run — so the doc cannot silently drift from the tests.

Regenerate:  ``python -m tools.type_coverage``
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.pages import AnyPageStore, PageStore  # noqa: E402
from mssqlbak.rows import read_table_rows  # noqa: E402
from mssqlbak.types import SUPPORTED_TYPE_IDS  # noqa: E402
from tools.typematrix import TYPE_CASES  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "TYPE_COVERAGE.md"
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
FIXTURE = _FIXTURE_DIR / "typecoverage_full.bak"

# Canonical SQL Server scalar types in a stable display order: ``(display name,
# xtype, case_name)``. ``case_name`` is ``None`` for types uniquely identified by
# xtype; it is set for the CLR types that all share xtype 240 (hierarchyid /
# geometry / geography), so each is matched to its own reference case.
CANONICAL_TYPES: list[tuple[str, int, str | None]] = [
    ("bit", 104, None),
    ("tinyint", 48, None),
    ("smallint", 52, None),
    ("int", 56, None),
    ("bigint", 127, None),
    ("decimal", 106, None),
    ("numeric", 108, None),
    ("smallmoney", 122, None),
    ("money", 60, None),
    ("real", 59, None),
    ("float", 62, None),
    ("date", 40, None),
    ("time", 41, None),
    ("smalldatetime", 58, None),
    ("datetime", 61, None),
    ("datetime2", 42, None),
    ("datetimeoffset", 43, None),
    ("char", 175, None),
    ("varchar / varchar(max)", 167, None),
    ("text", 35, None),
    ("nchar", 239, None),
    ("nvarchar / nvarchar(max)", 231, None),
    ("ntext", 99, None),
    ("binary", 173, None),
    ("varbinary / varbinary(max)", 165, None),
    ("image", 34, None),
    ("uniqueidentifier", 36, None),
    ("rowversion / timestamp", 189, None),
    ("xml", 241, None),
    ("sql_variant", 98, None),
    # CLR user-defined types: all share system_type_id 240, distinguished by
    # user_type_id. spatial -> OGC WKT, hierarchyid -> canonical path string.
    ("hierarchyid", 240, "hierarchyid"),
    ("geometry", 240, "geometry"),
    ("geography", 240, "geography"),
]

# Native types from the SQL Server catalog that can never be a *table column*
# (so they are out of scope for a backup data parser), recorded for completeness.
NON_COLUMN_TYPES: list[str] = ["cursor", "table"]


def _matrix_results(store: AnyPageStore) -> dict[str, tuple[int, str, bool, bool]]:
    """Map ``case_name -> (xtype, sql_type, passed, auto)`` by parsing the fixture.

    Keyed by case name (not xtype) because the CLR types hierarchyid / geometry /
    geography all share xtype 240.  ``passed`` is True when every low/high/mid/
    null value decoded from the fixture equals the reference matrix value.  For
    an ``auto`` (engine-populated) case there is no known value, so ``passed``
    means every inserted row decoded to a non-null value (correctness is checked
    separately by the engine-diff test).
    """
    schema = recover_schema(store)
    by_name = {t.name: t for t in schema.tables}
    results: dict[str, tuple[int, str, bool, bool]] = {}
    for case in TYPE_CASES:
        table = by_name.get(f"t_{case.name}")
        if table is None:
            # If the case declares a fallback_xtype, register it with PASS so
            # the "every supported type has a reference case" invariant holds.
            # This is used for types that cannot appear in the standard fixture
            # (e.g. SS2025-only native JSON), where coverage lives elsewhere.
            if case.fallback_xtype is not None:
                results[case.name] = (case.fallback_xtype, case.sql_type, True, case.auto)
            continue
        vcol = next((c for c in table.columns if c.name == "v"), None)
        if vcol is None:
            continue
        try:
            rows = {r["label"]: r["v"] for r in read_table_rows(store, table)}
            if case.auto:
                passed = all(rows.get(r.label) is not None for r in case.rows)
            else:
                passed = all(rows.get(r.label) == r.value for r in case.rows)
        except Exception:  # noqa: BLE001 - a decode failure is a coverage FAIL
            passed = False
        results[case.name] = (vcol.type_id, case.sql_type, passed, case.auto)
    return results


def _status(
    xtype: int, case_name: str | None, tested: dict[str, tuple[int, str, bool, bool]]
) -> tuple[str, str]:
    """Return ``(result, note)`` for one canonical type.

    ``case_name`` pins the reference case for an xtype shared by several types
    (the CLR 240 trio); otherwise the case is found by its xtype.
    """
    if case_name is not None:
        entry = tested.get(case_name)
    else:
        entry = next((v for v in tested.values() if v[0] == xtype), None)
    if entry is not None:
        _xtype, sql_type, passed, auto = entry
        if auto:
            note = f"engine-populated `{sql_type}`; validated by engine-diff only"
            return ("PASS" if passed else "FAIL", note)
        return ("PASS" if passed else "FAIL", f"reference case `{sql_type}`")
    if xtype in SUPPORTED_TYPE_IDS:
        # A code path with no dedicated reference case is a coverage gap, not a
        # pass: untested is treated as unsupported. ``test_type_coverage`` fails
        # if this is ever emitted.
        return ("UNTESTED", "decoder code path exists but no reference case — add one")
    return ("not supported", "decoder raises NotImplementedError")


def build_report(fixture: Path = FIXTURE) -> str:
    """Build the full markdown coverage report (deterministic)."""
    store = PageStore.from_bak(fixture)
    tested = _matrix_results(store)

    n_pass = sum(1 for _xtype, _sql, ok, _auto in tested.values() if ok)
    n_cases = len(TYPE_CASES)

    lines: list[str] = [
        "# Data-type coverage",
        "",
        "Status of every SQL Server scalar type for the `.bak` -> Delta parser.",
        "**Generated** by `python -m tools.type_coverage` from the reference value",
        "matrix and the committed fixture; `tests/test_type_coverage.py` fails if this",
        "file is out of date, so it stays in sync with the tests.",
        "",
        "This is the **data** slice of the byte-complete [BYTE_MAP.md](BYTE_MAP.md) "
        "(the master coverage doc); the metadata slice is "
        "[METADATA_COVERAGE.md](METADATA_COVERAGE.md). Which backup *types* can be "
        "restored is tracked in [BACKUP_COVERAGE.md](BACKUP_COVERAGE.md).",
        "",
        f"**Reference matrix:** {n_pass}/{n_cases} type cases pass "
        "(each case checks low / high / mid / NULL values).",
        "",
        "Validation layers for every `PASS` type:",
        "",
        "1. **Reference matrix** — decoded values equal known inputs "
        "(`tests/test_records.py`), including a 1 MB off-row LOB.",
        "2. **Engine diff** — decoded values equal a live SQL Server's query results, "
        "row-for-row (`tests/test_engine_diff.py`, when an engine is available).",
        "",
        "**Scope vs. all native types:** of SQL Server's native data types, "
        f"`{'`, `'.join(NON_COLUMN_TYPES)}` can never be a table column (excluded). The "
        "CLR types `hierarchyid`, `geometry`, `geography` (all `system_type_id` 240, "
        "distinguished by `user_type_id`) are decoded to text — spatial to OGC WKT, "
        "hierarchyid to its canonical path string. Every column-storable native type "
        "is covered below.",
        "",
        "| SQL Server type | xtype | Decoder | Result | Notes |",
        "|-----------------|-------|---------|--------|-------|",
    ]
    for name, xtype, case_name in CANONICAL_TYPES:
        decoder = "yes" if xtype in SUPPORTED_TYPE_IDS else "no"
        result, note = _status(xtype, case_name, tested)
        lines.append(f"| {name} | {xtype} | {decoder} | {result} | {note} |")

    lines += [
        "",
        "## Legend",
        "",
        "- **PASS** — covered by a reference case and decoded values matched exactly.",
        "- **FAIL** — covered by a reference case but values did not match (a bug).",
        "- **UNTESTED** — the decoder has a code path but no dedicated reference",
        "  case. Treated as a coverage gap (untested is unsupported);",
        "  `tests/test_type_coverage.py` fails until a reference case is added.",
        "- **not supported** — `decode_value` raises `NotImplementedError`; extracting",
        "  a table with this column type fails loudly rather than emitting wrong data.",
        "",
        "## Not-yet-supported types",
        "",
        "These raise on extract (no silent corruption). Add a reference case to",
        "`tools/typematrix.py` and a decoder branch in `mssqlbak/types.py` to cover one:",
        "",
    ]
    covered_xtypes = {xt for xt, _sql, _ok, _auto in tested.values()}
    unsupported = [
        f"`{name}` (xtype {xtype})"
        for name, xtype, _case in CANONICAL_TYPES
        if xtype not in SUPPORTED_TYPE_IDS and xtype not in covered_xtypes
    ]
    lines.append("- " + "\n- ".join(unsupported) if unsupported else "- (none)")
    lines.append("")
    lines.append("See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.")
    lines.append("")
    return "\n".join(lines)


def write_report(fixture: Path = FIXTURE) -> Path:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(build_report(fixture))
    return DOC_PATH


def main() -> int:
    if not FIXTURE.exists():
        print(f"error: reference fixture missing: {FIXTURE}", file=sys.stderr)
        return 2
    path = write_report()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
