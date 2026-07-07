#!/usr/bin/env python3
"""Generate ``docs/CONSTRAINT_COVERAGE.md`` — how constraints/indexes are encoded.

Companion to ``tools/type_coverage.py`` (one data type per table) and
``tools/metadata_coverage.py``.  This report puts one *constraint* per table
(``tools/constraintmatrix.py``) and reads the resulting ``.bak`` back with
:func:`mssqlbak.catalog.recover_catalog_objects` to show, per variant, exactly
which catalog rows each constraint/index produces.

The report is deterministic: it parses the committed constraint fixture and
renders the *recovered* encoding, so ``tests/test_constraint_coverage.py`` fails
if the decode regresses or the doc drifts.

Regenerate:  ``python -m tools.constraint_coverage``
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak.catalog import (  # noqa: E402
    INDEX_CLUSTERED,
    INDEX_HEAP,
    Index,
    recover_catalog_objects,
    recover_schema,
)
from mssqlbak.pages import PageStore  # noqa: E402
from tools.constraintmatrix import CASES, table_name  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "CONSTRAINT_COVERAGE.md"
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
FIXTURE = _FIXTURE_DIR / "constraintcoverage_full.bak"


def _index_label(idx: Index, colname: dict[int, str]) -> str:
    if idx.index_type == INDEX_HEAP:
        return "heap (no clustered index)"
    kind = "clustered" if idx.index_type == INDEX_CLUSTERED else "nonclustered"
    flags = []
    if idx.is_primary_key:
        flags.append("PK")
    if idx.is_unique_constraint:
        flags.append("unique-constraint")
    elif idx.is_unique:
        flags.append("unique")
    cols = ", ".join(colname.get(c, f"col{c}") for c in idx.key_columns) or "—"
    suffix = f" [{', '.join(flags)}]" if flags else ""
    return f"{kind}{suffix} on ({cols})"


def build_report(fixture: Path = FIXTURE) -> str:
    store = PageStore.from_bak(fixture)
    schema = recover_schema(store)
    objs = recover_catalog_objects(store)
    by_name = {t.name: t for t in schema.tables}

    n_extractable = sum(
        1 for t in schema.tables if t.name.startswith("cc_") and t.index_id in (0, 1)
    )
    n_total = sum(1 for c in CASES)

    lines: list[str] = [
        "# Constraint & index coverage",
        "",
        "How SQL Server encodes keys, indexes and constraints in a backup, and what",
        "the parser recovers.  **Generated** by `python -m tools.constraint_coverage`",
        "from the committed constraint fixture (one constraint isolated per table);",
        "`tests/test_constraint_coverage.py` fails if the decode regresses or this",
        "file drifts.",
        "",
        "Sibling coverage docs: [TYPE_COVERAGE.md](TYPE_COVERAGE.md) (column data), "
        "[METADATA_COVERAGE.md](METADATA_COVERAGE.md) (backup metadata), "
        "[BACKUP_COVERAGE.md](BACKUP_COVERAGE.md) (backup types), anchored by "
        "[BYTE_MAP.md](BYTE_MAP.md).",
        "",
        "## Where constraints live in the backup",
        "",
        "A `.bak` is a physical page image, so every constraint and index is present "
        "in the system base-table pages (and, for indexes, as physical B-tree pages):",
        "",
        "- **`sysschobjs` (object id 34)** — one row per *constraint object*: "
        "`type` ∈ {`PK`, `UQ`, `F`, `C`, `D`} with `pid` = the parent table's object "
        "id. A plain index is **not** a constraint and produces no row here.",
        "- **`sysidxstats` (object id 54)** — one row per index/heap: `type` "
        "0=heap, 1=clustered, 2=nonclustered; `status` bits `0x20`=primary key, "
        "`0x08`=unique, `0x40`=unique constraint.",
        "- **`sysiscols` (object id 55)** — one row per index key column: `intprop` "
        "is the table column id, `subid` the key ordinal.",
        "- **Physical index pages** — a clustered index *is* the table's data pages; "
        "nonclustered indexes get their own B-tree pages (separate rowsets), "
        "classified *skippable* in the byte map and never read as table rows.",
        "",
        "For a full database -> Delta restore the parser reads the clustered data "
        "rowset (index_id=1) or heap (index_id=0, traversed via IAM chain); "
        "FK/CHECK/DEFAULT are metadata-only and do not affect row decoding.",
        "",
        f"**Coverage:** {n_extractable}/{n_total} constraint-variant tables extract their "
        "rows (clustered indexes and heaps; both paths supported); "
        f"all {n_total} have their constraints and indexes decoded from the catalog.",
        "",
        "## Per-variant encoding (recovered from the fixture)",
        "",
        "| Variant table | Constraint under test | `sysschobjs` objects | Indexes (`sysidxstats`/`sysiscols`) | Rows |",
        "|---------------|-----------------------|----------------------|-------------------------------------|------|",
    ]

    for case in CASES:
        tn = table_name(case)
        table = by_name.get(tn)
        colname = {c.colid: c.name for c in table.columns} if table else {}
        cons = objs.constraints_for(table.object_id) if table else []
        idxs = objs.indexes_for(table.object_id) if table else []
        con_txt = ", ".join(f"`{c.type_code}`:{c.name}" for c in cons) or "—"
        idx_txt = "; ".join(
            _index_label(i, colname) for i in sorted(idxs, key=lambda i: i.index_id)
        ) or "—"
        rows = "yes" if (table and table.index_id in (0, 1)) else "catalog-only"
        lines.append(f"| `{tn}` | {case.kind} | {con_txt} | {idx_txt} | {rows} |")

    lines += [
        "",
        "## Key findings",
        "",
        "- **Primary key** always yields an auto-named `PK` object in `sysschobjs`; "
        "a *clustered* PK is the data rowset (`indid=1`), a *nonclustered* PK leaves "
        "a heap (`indid=0`) plus a separate nonclustered index.",
        "- **Unique constraint** vs **unique index**: both create a unique "
        "nonclustered index, but only the constraint adds a `UQ` object "
        "(`status` bit `0x40`); a bare `CREATE UNIQUE INDEX` does not.",
        "- **Plain nonclustered index** adds an index with no `sysschobjs` object and "
        "no unique bit.",
        "- **Foreign key / check / default** add `F` / `C` / `D` objects with no new "
        "index or data pages.",
        "",
        "See [README](../README.md) and [DESIGN](../DESIGN.md) for parser limitations.",
        "",
    ]
    return "\n".join(lines)


def write_report(fixture: Path = FIXTURE) -> Path:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(build_report(fixture))
    return DOC_PATH


def main() -> int:
    if not FIXTURE.exists():
        print(f"error: constraint fixture missing: {FIXTURE}", file=sys.stderr)
        return 2
    path = write_report()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
