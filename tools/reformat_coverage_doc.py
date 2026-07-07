#!/usr/bin/env python3
"""Reformat an existing correctness-coverage markdown doc in-place.

Three transforms applied:
  1. Re-sort all fixture sections (summary rows + per-fixture sections) by
     .bak filename, case-insensitively, alphabetically.
  2. Inject the SQL Server version *year* (e.g. "2022") into each
     per-fixture section heading.
  3. Add a "Type" column to every per-fixture table row, derived from
     the .bak file's catalog (rowstore / columnstore / memory-optimized).

Usage::

    python -m tools.reformat_coverage_doc
    python -m tools.reformat_coverage_doc --doc docs/correctness_coverage_fixtures_realworld.md
    python -m tools.reformat_coverage_doc --fixture-dir tests/fixtures_realworld --no-write
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Catalog-based table type lookup
# ---------------------------------------------------------------------------

_COMP_COLUMNSTORE = frozenset({3, 4})  # COLUMNSTORE and COLUMNSTORE_ARCHIVE


def _table_type(is_memory_optimized: bool, compression: int) -> str:
    if is_memory_optimized:
        return "memory-optimized"
    if compression in _COMP_COLUMNSTORE:
        return "columnstore"
    return "rowstore"


def _load_table_types(bak_path: Path) -> dict[str, str]:
    """Return {fqn: type_str} for every user table in *bak_path*."""
    from mssqlbak.pages import PageStore
    from mssqlbak.catalog import recover_schema

    try:
        store = PageStore.from_bak(str(bak_path))
        schema = recover_schema(store)
    except Exception:
        return {}

    return {
        f"{t.schema}.{t.name}": _table_type(t.is_memory_optimized, t.compression)
        for t in schema.tables
    }


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

_BAK_RE = re.compile(r"^### `([^`]+\.bak)`")
_SQL_VER_RE = re.compile(r"SQL Server (\d{4})")
_TABLE_HEADER_RE = re.compile(
    r"^\| Table \|(?:\s*Type\s*\|)?\s*Source rows \| Row count \| Null count \| Min/max \| Col count \| Notes \|"
)
# Matches any markdown table separator row (starts with |--- or |:-- etc.)
_TABLE_SEP_RE = re.compile(r"^\|[-:]+\|")
_TABLE_ROW_RE = re.compile(r"^\| `([^`]+)` \|")
_SUMMARY_HEADER_RE = re.compile(
    r"^\| Backup \| Source rows \| Source cols \|"
)
_SUMMARY_ROW_RE = re.compile(r"^\| `([^`]+\.bak)` \|")


def _extract_year(sql_ver_line: str) -> str:
    """Return '2022' (or '') from a _SQL Server ..._ line."""
    m = _SQL_VER_RE.search(sql_ver_line)
    return m.group(1) if m else ""


def _bak_sort_key(name: str) -> str:
    return name.lower()


# ---------------------------------------------------------------------------
# Section splitter
# ---------------------------------------------------------------------------

class Section:
    """One per-fixture ### block."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    @property
    def bak_name(self) -> str:
        m = _BAK_RE.match(self.lines[0])
        return m.group(1) if m else ""

    @property
    def year(self) -> str:
        for line in self.lines[:4]:
            y = _extract_year(line)
            if y:
                return y
        return ""


def _split_sections(body: str) -> tuple[list[str], list[Section], list[str]]:
    """Return (preamble_lines, sections, tail_lines).

    preamble_lines: everything up to (but not including) the first ###
    tail_lines:     everything after the last section line (timings, footer)
    """
    lines = body.splitlines(keepends=True)

    # Find where per-fixture sections start and the timings block begins
    first_section_idx = None
    timings_idx = None
    for i, line in enumerate(lines):
        if first_section_idx is None and _BAK_RE.match(line):
            first_section_idx = i
        if line.startswith("## Extraction timings"):
            timings_idx = i

    if first_section_idx is None:
        return lines, [], []

    preamble = lines[:first_section_idx]
    section_lines = lines[first_section_idx:timings_idx]
    tail = lines[timings_idx:] if timings_idx is not None else []

    # Split section_lines into individual sections
    sections: list[Section] = []
    current: list[str] = []
    for line in section_lines:
        if _BAK_RE.match(line) and current:
            sections.append(Section(current))
            current = []
        current.append(line)
    if current:
        sections.append(Section(current))

    return preamble, sections, tail


# ---------------------------------------------------------------------------
# Per-section transforms
# ---------------------------------------------------------------------------

def _inject_year_in_heading(line: str, year: str) -> str:
    r"""Turn `### \`Foo.bak\` — ✓ pass` into `### \`Foo.bak\` — 2022 — ✓ pass`.

    Idempotent: skips if the year is already present.
    """
    if not year:
        return line
    # Avoid double-insertion
    if year in line:
        return line
    # Insert year after the bak name and first " — "
    return re.sub(r"(### `[^`]+` — )", rf"\g<1>{year} — ", line, count=1)


def _inject_type_column(
    section_lines: list[str],
    type_map: dict[str, str],
) -> list[str]:
    """Insert a 'Type' column into the per-table markdown table (idempotent)."""
    out: list[str] = []
    in_table = False
    header_has_type = False

    for line in section_lines:
        stripped = line.rstrip("\n")
        if _TABLE_HEADER_RE.match(stripped):
            header_has_type = "| Type |" in stripped
            if not header_has_type:
                stripped = stripped.replace(
                    "| Table | Source rows |",
                    "| Table | Type | Source rows |",
                    1,
                )
            out.append(stripped + "\n")
            in_table = True
            continue
        if in_table and _TABLE_SEP_RE.match(stripped):
            # Ensure separator has the same number of columns as the 8-col header.
            # Count pipe separators: 8-col table needs 9 pipes.
            if stripped.count("|") < 9:
                stripped = re.sub(r"^(\|[-:]+\|)", r"\1------|", stripped, count=1)
            out.append(stripped + "\n")
            continue
        if in_table and stripped.startswith("| `"):
            m = _TABLE_ROW_RE.match(stripped)
            if m:
                fqn = m.group(1)
                ttype = type_map.get(fqn, "rowstore")
                already_has = bool(re.match(
                    rf"^\| `{re.escape(fqn)}` \| (?:rowstore|columnstore|memory-optimized) \|",
                    stripped,
                ))
                if not already_has:
                    stripped = stripped.replace(f"| `{fqn}` |", f"| `{fqn}` | {ttype} |", 1)
                else:
                    stripped = re.sub(
                        rf"^\| `{re.escape(fqn)}` \| (?:rowstore|columnstore|memory-optimized) \|",
                        f"| `{fqn}` | {ttype} |",
                        stripped,
                        count=1,
                    )
                out.append(stripped + "\n")
                continue
        if in_table and not stripped.startswith("|"):
            in_table = False
        out.append(line)

    return out


# ---------------------------------------------------------------------------
# Summary table transform
# ---------------------------------------------------------------------------

def _summary_row_key(row: str) -> str:
    """Sort key for a summary-table row line: bak filename, lower-cased."""
    m = _SUMMARY_ROW_RE.match(row.rstrip("\n"))
    return _bak_sort_key(m.group(1)) if m else row.lower()


def _sort_summary_table(preamble: list[str]) -> list[str]:
    r"""Re-sort the summary table rows in *preamble* alphabetically by bak name.

    The summary table sits between `## Summary` and `## Per-fixture detail`.
    Data rows (starting with `| \``) are sorted; header and separator rows
    are left in place.
    """
    out: list[str] = []
    in_summary = False
    row_buffer: list[str] = []
    after_header = False  # True once we've passed the separator row

    for line in preamble:
        stripped = line.rstrip("\n")
        if stripped.startswith("## Summary"):
            in_summary = True
            out.append(line)
            continue
        if in_summary and stripped.startswith("## "):
            # Flush sorted rows then exit summary region
            row_buffer.sort(key=_summary_row_key)
            out.extend(row_buffer)
            row_buffer = []
            in_summary = False
            after_header = False
            out.append(line)
            continue
        if in_summary:
            if _SUMMARY_HEADER_RE.match(stripped):
                out.append(line)
                continue
            if stripped.startswith("|---"):
                out.append(line)
                after_header = True
                continue
            if after_header and _SUMMARY_ROW_RE.match(stripped):
                row_buffer.append(line)
                continue
            # Skip blank lines inside the sorted table region
            if after_header and stripped == "":
                continue
        out.append(line)

    # If summary was last (no trailing ##)
    if row_buffer:
        row_buffer.sort(key=_summary_row_key)
        out.extend(row_buffer)

    return out


# ---------------------------------------------------------------------------
# Timings table transform
# ---------------------------------------------------------------------------

def _sort_timings_table(tail: list[str]) -> list[str]:
    """Re-sort the timings table rows in *tail* alphabetically by bak name."""
    _TIMING_ROW_RE = re.compile(r"^\| `([^`]+\.bak)` \|")

    def _timing_key(row: str) -> str:
        m = _TIMING_ROW_RE.match(row.rstrip("\n"))
        return _bak_sort_key(m.group(1)) if m else row.lower()

    out: list[str] = []
    row_buffer: list[str] = []
    after_header = False

    for line in tail:
        stripped = line.rstrip("\n")
        if stripped.startswith("| Backup |"):
            out.append(line)
            continue
        if stripped.startswith("|---"):
            out.append(line)
            after_header = True
            continue
        if after_header and _TIMING_ROW_RE.match(stripped):
            row_buffer.append(line)
            continue
        # Any non-table line flushes buffer
        if row_buffer:
            row_buffer.sort(key=_timing_key)
            out.extend(row_buffer)
            row_buffer = []
            after_header = False
        out.append(line)

    if row_buffer:
        row_buffer.sort(key=_timing_key)
        out.extend(row_buffer)

    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _reformat(doc_path: Path, fixture_dir: Path) -> str:
    text = doc_path.read_text()
    preamble, sections, tail = _split_sections(text)

    # Sort preamble summary table in-place
    preamble = _sort_summary_table(preamble)

    # Sort sections alphabetically
    sections.sort(key=lambda s: _bak_sort_key(s.bak_name))

    # Sort timings table
    tail = _sort_timings_table(tail)

    # Load all table types
    bak_types: dict[str, dict[str, str]] = {}
    bak_files = sorted(fixture_dir.glob("*.bak"))
    print(f"Loading catalogs from {len(bak_files)} .bak files...", file=sys.stderr)
    for bak in bak_files:
        print(f"  {bak.name}", end="", flush=True, file=sys.stderr)
        bak_types[bak.name] = _load_table_types(bak)
        print(" ✓", file=sys.stderr)

    # Transform each section
    new_sections: list[str] = []
    for sec in sections:
        lines = sec.lines[:]
        # Inject year into first line
        year = sec.year
        lines[0] = _inject_year_in_heading(lines[0], year)
        # Inject type column
        type_map = bak_types.get(sec.bak_name, {})
        lines = _inject_type_column(lines, type_map)
        new_sections.append("".join(lines))

    return "".join(preamble) + "".join(new_sections) + "".join(tail)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--doc",
        type=Path,
        default=REPO_ROOT / "docs" / "correctness_coverage_fixtures_realworld.md",
        help="markdown doc to reformat (default: docs/correctness_coverage_fixtures_realworld.md)",
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=REPO_ROOT / "tests" / "fixtures_realworld",
        help="directory containing the .bak files (default: tests/fixtures_realworld)",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="print to stdout instead of overwriting the doc",
    )
    args = parser.parse_args(argv)

    doc_path: Path = args.doc.resolve()
    fixture_dir: Path = args.fixture_dir.resolve()

    if not doc_path.is_file():
        parser.error(f"doc not found: {doc_path}")
    if not fixture_dir.is_dir():
        parser.error(f"fixture-dir not found: {fixture_dir}")

    result = _reformat(doc_path, fixture_dir)

    if args.no_write:
        sys.stdout.write(result)
    else:
        doc_path.write_text(result)
        print(f"==> wrote {doc_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
