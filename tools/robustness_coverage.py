#!/usr/bin/env python3
"""Generate ``docs/ROBUSTNESS_COVERAGE.md`` — what the parser skips, and why.

The extraction objective is "get every user table out (clustered and heap); for
everything else, inspect and skip it knowing we do not handle it".  This report documents
the *skip contract*: which backup contents are extracted, which are detected and
skipped (with a stable reason), and which are simply not enumerated as data.

It is partly **generated** from the committed fixtures: the per-table outcome
table is produced by running :func:`mssqlbak.inspect.classify_table` over every
fixture present, so ``tests/test_robustness.py`` fails if the classifier
regresses or this file drifts.

Regenerate:  ``python -m tools.robustness_coverage``
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.inspect import classify_table, recover_object_inventory  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "ROBUSTNESS_COVERAGE.md"
FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))

# Fixtures whose per-table outcomes are rendered (those present are used).
_FIXTURES = [
    "typecoverage_full.bak",
    "constraintcoverage_full.bak",
    "compressioncoverage_full.bak",
    "computedcoverage_full.bak",
]


def _outcome_rows() -> list[tuple[str, str, str, str]]:
    """(fixture, table, OK/SKIP, reason) for every table in every fixture."""
    rows: list[tuple[str, str, str, str]] = []
    for name in _FIXTURES:
        path = FIXTURE_DIR / name
        if not path.exists():
            continue
        store = PageStore.from_bak(path)
        for table in sorted(recover_schema(store).tables, key=lambda t: t.name):
            support = classify_table(table)
            if support.supported:
                rows.append((name, table.name, "OK", "—"))
            else:
                rows.append((name, table.name, "SKIP", support.reason or ""))
    return rows


def build_report() -> str:
    rows = _outcome_rows()
    n_ok = sum(1 for r in rows if r[2] == "OK")
    n_skip = len(rows) - n_ok

    # Inventory summary from the constraint fixture (richest object set).
    inv_line = ""
    cc = FIXTURE_DIR / "constraintcoverage_full.bak"
    if cc.exists():
        inv = recover_object_inventory(PageStore.from_bak(cc))
        n_user = sum(1 for o in inv if not o.is_system)
        n_sys = len(inv) - n_user
        inv_line = (
            f"`recover_object_inventory` enumerates **every** `sysschobjs` object; "
            f"the constraint fixture has {n_user} user objects and {n_sys} system "
            "objects, each tagged with its type and schema."
        )

    lines: list[str] = [
        "# Robustness & skip coverage",
        "",
        "What happens when a backup contains something the row reader does not "
        "handle.  The contract is: **extract every supported table; for everything "
        "else, inspect and skip it with a recorded reason — never crash the run and "
        "never emit silently-wrong data.**  **Generated** in part by "
        "`python -m tools.robustness_coverage`; `tests/test_robustness.py` fails if "
        "the classifier regresses or this file drifts.",
        "",
        "Sibling coverage docs: [TYPE_COVERAGE.md](TYPE_COVERAGE.md), "
        "[CONSTRAINT_COVERAGE.md](CONSTRAINT_COVERAGE.md), "
        "[METADATA_COVERAGE.md](METADATA_COVERAGE.md), "
        "[BACKUP_COVERAGE.md](BACKUP_COVERAGE.md), anchored by "
        "[BYTE_MAP.md](BYTE_MAP.md).",
        "",
        "## Three layers of defence",
        "",
        "1. **Inventory** — `mssqlbak.inspect.recover_object_inventory` lists every "
        "object in the backup (tables, views, procedures, triggers, functions, "
        "constraints, queues, internal/system tables) so nothing is invisible.",
        "2. **Pre-flight classification** — `classify_table` decides, from catalog "
        "metadata alone, whether each user table can be read, and if not, why. "
        "Skips are *known* before any page is touched.",
        "3. **Per-table safety net** — `extract_bak_to_delta` isolates each table; an "
        "unanticipated structure raises, is caught, and is recorded as a skip "
        "rather than aborting the whole extraction.",
        "",
        "## What is extracted vs skipped",
        "",
        "| Backup content | Behaviour | How |",
        "|----------------|-----------|-----|",
        "| Clustered user tables + rows (incl. LOB / row-overflow / legacy text) | **extracted** | row reader |",
        "| Persisted computed columns | **extracted** | stored like a regular column (has a `sysrscols` row) |",
        "| Non-persisted computed columns | excluded from output | no `sysrscols` storage row; dropped from the record layout so offsets stay aligned |",
        "| Views, stored procedures, triggers, functions, defaults (programmability) | not enumerated as data | only `type='U'` objects with a data rowset are read |",
        "| Security: users, roles, permissions | not enumerated as data | live in system schemas (`sys`), never emitted |",
        "| Nonclustered / unique / full-text indexes, statistics | not read as rows | index pages classified skippable in the byte map |",
        "| PK / FK / UNIQUE / CHECK / DEFAULT / cascade rules | decoded for inspection, ignored for data | catalog-only metadata |",
        "| Heap table (no clustered index) | **extracted** | row reader walks the IAM extent bitmap, filtered by page `obj_id` |",
        "| Sparse large-database layout (omitted unallocated extents) | **extracted** | each page is placed at `page_id*8192`, so gaps zero-fill (seen in AdventureWorks2022) |",
        "| Empty heap (no allocated pages / no IAM) | **extracted** (0 rows) | recognised as empty rather than a locate failure (ETL staging tables) |",
        "| Multi-file DB (data on secondary `file_id≠1`) | **extracted** | every data file is reconstructed per `file_id`; the catalog's page locators resolve onto the right file (seen in WideWorldImporters) |",
        "| ROW / PAGE data-compressed table | **skip + report** | `classify_table` → `compressed` (sysrowsets `cmprlevel`) |",
        "| Columnstore table | **skip + report** | column-segment storage, not FixedVar row pages |",
        "| Partitioned table (>1 data partition) | **skip + report** | `classify_table` → `partitioned` |",
        "| Data on a `file_id` absent from the backup | **skip + report** | `classify_table` → `multi-file` (referenced file not in the image) |",
        "| Column of an undecodable type | **skip + report** | `classify_table` → `unsupported-type` |",
        "| Any other unanticipated structure | **skip + report** | per-table safety net catches the error |",
        "| TDE-encrypted backup | rejected at file level | container demux refuses to proceed |",
        "",
    ]
    if inv_line:
        lines += [inv_line, ""]
    lines += [
        f"**Coverage across committed fixtures:** {n_ok} table(s) extract, "
        f"{n_skip} skip with an explicit reason; none crash the run.",
        "",
        "## Per-table outcomes (from the fixtures)",
        "",
        "| Fixture | Table | Result | Reason |",
        "|---------|-------|--------|--------|",
    ]
    for fixture, table, status, reason in rows:
        lines.append(f"| `{fixture}` | `{table}` | {status} | {reason} |")
    lines += [
        "",
        "See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.",
        "",
    ]
    return "\n".join(lines)


def write_report() -> Path:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(build_report())
    return DOC_PATH


def main() -> int:
    path = write_report()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
