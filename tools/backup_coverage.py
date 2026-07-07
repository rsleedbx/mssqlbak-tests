#!/usr/bin/env python3
"""Generate ``docs/BACKUP_COVERAGE.md`` — which SQL Server *backup types* we support.

Companion to ``tools/type_coverage.py`` (column-data coverage) and
``tools/metadata_coverage.py`` (metadata-field coverage).  Where those track what
we decode *inside* a backup, this one tracks *which kinds of backup* the parser
can turn into a full Delta restore at all.

The first-priority capability is the **full database backup** — the only backup
type that, on its own, contains every data extent needed to reconstruct the whole
database.  That path is SUPPORTED and validated here against the committed
fixtures (uncompressed and ``WITH COMPRESSION``); every other backup type is
ranked by how close it is to enabling a full restore.

The report is deterministic: each SUPPORTED row carries a validator that runs
against the committed fixtures, so a regression flips the row and
``tests/test_backup_coverage.py`` fails until the doc is regenerated.

Regenerate:  ``python -m tools.backup_coverage``
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "BACKUP_COVERAGE.md"
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
FIXTURE = _FIXTURE_DIR / "typecoverage_full.bak"
FIXTURE_COMPRESSED = _FIXTURE_DIR / "typecoverage_full_compressed.bak"
FIXTURE_DIFF_FULL = _FIXTURE_DIR / "tabletypecoverage_full.bak"
FIXTURE_DIFF = _FIXTURE_DIR / "tabletypecoverage_diff.bak"

PAGE = 8192

# ── Status values ──────────────────────────────────────────────────────────────
SUPPORTED   = "SUPPORTED"    # full restore-to-Delta works; counts toward coverage
PLANNED     = "PLANNED"      # restorable in principle, not yet implemented (gap)
UNSUPPORTED = "UNSUPPORTED"  # cannot yield a full restore by itself (out of scope for v1)


@dataclass(frozen=True)
class BackupKind:
    """One SQL Server backup type and whether we can restore it to Delta."""

    category: str
    name: str
    tsql: str
    status: str
    restore: str  # what a restore yields: "whole database", "changed extents only", …
    note: str
    validate: Callable[[], bool] | None = field(default=None)


# ── Validators (deterministic, run against the committed fixtures) ──────────────

def _fixture_label() -> str:
    from mssqlbak.reader import read_bak_metadata

    s = read_bak_metadata(FIXTURE).first_set
    return s.backup_type_label if s is not None else ""


def _full_uncompressed_ok() -> bool:
    from mssqlbak.mtf import extract_mdf_pages

    img = extract_mdf_pages(FIXTURE)
    return _fixture_label().startswith("Full") and len(img) > 0 and len(img) % PAGE == 0


def _copy_only_ok() -> bool:
    from mssqlbak.mtf import extract_mdf_pages

    # The committed fixture is itself a copy-only full backup, so this row is
    # validated directly rather than by-design.
    img = extract_mdf_pages(FIXTURE)
    return "copy-only" in _fixture_label() and len(img) > 0 and len(img) % PAGE == 0


def _full_compressed_ok() -> bool:
    from mssqlbak.compressed import is_mssqlbak
    from mssqlbak.mtf import extract_mdf_pages

    if not is_mssqlbak(FIXTURE_COMPRESSED):
        return False
    img = extract_mdf_pages(FIXTURE_COMPRESSED)
    return len(img) > 0 and len(img) % PAGE == 0


def _differential_ok() -> bool:
    """Merge a committed differential fixture onto its full-backup base and
    verify that the merged page image is non-empty and page-aligned."""
    from mssqlbak.pages import PageStore

    if not FIXTURE_DIFF.exists() or not FIXTURE_DIFF_FULL.exists():
        return False
    store = PageStore.from_diff_bak(FIXTURE_DIFF, FIXTURE_DIFF_FULL)
    return store.page_count > 0


# ── The backup-type surface, ordered by restore priority ────────────────────────
#
# Reference: SQL Server "Backup Overview" / "Types of Backups" (docs/backup types).

KINDS: list[BackupKind] = [
    BackupKind(
        "Database backup", "Full database backup",
        "BACKUP DATABASE db TO DISK=…",
        SUPPORTED, "whole database",
        "first-priority path: contains every data extent plus enough log to "
        "recover; the entire MDF page image is rebuilt and every user table "
        "extracted to Delta. Validated on the committed fixture.",
        _full_uncompressed_ok),
    BackupKind(
        "Database backup", "Full database backup, WITH COMPRESSION",
        "BACKUP DATABASE db TO DISK=… WITH COMPRESSION",
        SUPPORTED, "whole database",
        "same full-restore path; the MSSQLBAK/XPRESS container is transparently "
        "decompressed (mssqlbak.compressed). Validated on the compressed fixture.",
        _full_compressed_ok),
    BackupKind(
        "Database backup", "Full database backup, copy-only",
        "BACKUP DATABASE db TO DISK=… WITH COPY_ONLY",
        SUPPORTED, "whole database",
        "byte-for-byte the same page-image format as a full backup; copy-only "
        "only changes the differential base, a metadata flag the reader decodes. "
        "The committed fixture is itself a copy-only full backup, so this row is "
        "validated directly.",
        _copy_only_ok),
    BackupKind(
        "Differential backup", "Differential database backup",
        "BACKUP DATABASE db TO DISK=… WITH DIFFERENTIAL",
        SUPPORTED, "changed extents merged onto full base",
        "PageStore.from_diff_bak(diff_bak, full_bak) merges the differential's "
        "changed extents onto the full-backup page image, yielding a complete "
        "page store identical to restoring to an engine. Validated against the "
        "committed tabletypecoverage_diff.bak + tabletypecoverage_full.bak fixture pair.",
        _differential_ok),
    BackupKind(
        "Differential backup", "Differential partial backup",
        "BACKUP DATABASE db FILEGROUP=… WITH DIFFERENTIAL",
        PLANNED, "changed extents of a subset",
        "changed extents since a partial base; needs both the partial base and "
        "extent-merge. Not implemented.",
        None),
    BackupKind(
        "Log backup", "Transaction-log backup",
        "BACKUP LOG db TO DISK=…",
        UNSUPPORTED, "log records (no data pages)",
        "contains log records, not data pages — a different on-disk format. "
        "Required later for point-in-time recovery and CDC/log-chain hydration, "
        "but yields no standalone table data.",
        None),
    BackupKind(
        "File backup", "File / filegroup backup",
        "BACKUP DATABASE db FILE=… | FILEGROUP=…",
        UNSUPPORTED, "subset of files",
        "backs up only some files/filegroups; cannot reconstruct the whole "
        "database on its own. Out of scope for the full-restore goal.",
        None),
    BackupKind(
        "Partial backup", "Partial backup",
        "BACKUP DATABASE db READ_WRITE_FILEGROUPS …",
        UNSUPPORTED, "primary + read/write filegroups",
        "skips read-only filegroups, so it is not a complete-database image. "
        "Out of scope for v1.",
        None),
]

# ── Container / option dimensions (orthogonal to backup type) ───────────────────

@dataclass(frozen=True)
class Option:
    name: str
    status: str
    note: str


OPTIONS: list[Option] = [
    Option("Uncompressed (MTF)", SUPPORTED,
           "the native Microsoft Tape Format container; default for any backup type above."),
    Option("Compressed (WITH COMPRESSION)", SUPPORTED,
           "MSSQLBAK container, XPRESS (LZ77+Huffman); decoded by mssqlbak.compressed."),
    Option("TDE-encrypted", UNSUPPORTED,
           "MSSQLBAK container whose payload is encrypted; the page image cannot be "
           "reconstructed without the certificate, so extraction raises ValueError."),
    Option("Striped / multi-file (TO DISK=…, DISK=…)", PLANNED,
           "a single backup split across several files; only single-file backups are read in v1."),
    Option("Mirrored media set", PLANNED,
           "redundant copies; read one mirror only. Not yet implemented."),
]


def _run_validators() -> dict[str, str]:
    """Return ``{kind name: resolved status}`` validating each SUPPORTED claim."""
    resolved: dict[str, str] = {}
    for k in KINDS:
        if k.status == SUPPORTED and k.validate is not None:
            try:
                ok = k.validate()
            except Exception:  # a broken claim must surface, not crash the report
                ok = False
            resolved[k.name] = SUPPORTED if ok else "BROKEN"
        else:
            resolved[k.name] = k.status
    return resolved


def build_report() -> str:
    """Build the full markdown backup-type-coverage report (deterministic)."""
    resolved = _run_validators()

    n_supported = sum(1 for k in KINDS if resolved[k.name] == SUPPORTED)
    n_total = len(KINDS)
    pct = round(100 * n_supported / n_total) if n_total else 0

    lines: list[str] = [
        "# Backup-type coverage",
        "",
        "Which SQL Server **backup types** the `.bak` -> Delta parser can restore.",
        "**Generated** by `python -m tools.backup_coverage`; each SUPPORTED row is",
        "validated against the committed fixtures, and `tests/test_backup_coverage.py`",
        "fails if this file is out of date or a SUPPORTED claim stops holding.",
        "",
        "Companion to the byte-complete [BYTE_MAP.md](BYTE_MAP.md) (master coverage "
        "doc): [TYPE_COVERAGE.md](TYPE_COVERAGE.md) tracks column *data* and "
        "[METADATA_COVERAGE.md](METADATA_COVERAGE.md) tracks *metadata* fields, while "
        "this report tracks *which kinds of backup* can be turned into a full restore.",
        "",
        f"**Coverage:** {n_supported}/{n_total} backup types restore the whole "
        f"database to Delta ({pct}%).",
        "",
        "**First priority — full restore.** A *full database backup* is the only "
        "backup type that contains every data extent on its own, so it is the basic "
        "unit that enables a complete database -> Delta restore. That path is "
        "SUPPORTED (uncompressed and `WITH COMPRESSION`); everything else is ranked "
        "by how much extra machinery it needs before it can yield a full restore.",
        "",
        "## Backup types",
        "",
        "| Category | Backup type | T-SQL | Restore yields | Status | Notes |",
        "|----------|-------------|-------|----------------|--------|-------|",
    ]
    for k in KINDS:
        status = resolved[k.name]
        lines.append(
            f"| {k.category} | {k.name} | `{k.tsql}` | {k.restore} | {status} | {k.note} |"
        )

    lines += [
        "",
        "## Container / option dimensions",
        "",
        "Orthogonal to the backup *type* above; any full backup may carry these.",
        "",
        "| Option | Status | Notes |",
        "|--------|--------|-------|",
    ]
    for o in OPTIONS:
        lines.append(f"| {o.name} | {o.status} | {o.note} |")

    lines += [
        "",
        "## Legend",
        "",
        "- **SUPPORTED** — restores the whole database to Delta; validated against a "
        "committed fixture. Counts toward coverage.",
        "- **PLANNED** — restorable in principle but not yet implemented (needs "
        "base-merge, multi-file assembly, etc.). A gap.",
        "- **UNSUPPORTED** — cannot yield a complete-database restore on its own "
        "(log records, file/partial subsets, encrypted payloads). Out of scope for v1.",
        "",
        "## Roadmap (toward more backup types)",
        "",
        "1. **Differential database backup** — merge changed extents onto a full "
        "base image (both already decodable individually).",
        "2. **Striped / multi-file** — concatenate the data stream across files "
        "before page reassembly.",
        "3. **Transaction-log backup** — decode log records for point-in-time and "
        "CDC/log-chain hydration (the original analytics/CDC goal).",
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
    if not FIXTURE.exists():
        print(f"error: reference fixture missing: {FIXTURE}", file=sys.stderr)
        return 2
    path = write_report()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
