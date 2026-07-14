#!/usr/bin/env python3
"""Generate ``docs/METADATA_COVERAGE.md`` — which backup-metadata fields we extract.

Companion to ``tools/type_coverage.py``.  Where that report tracks column-*data*
coverage, this one enumerates every field in the SQL Server backup container's
metadata (the MTF descriptor blocks plus SQL Server's proprietary config stream)
and records whether ``mssqlbak.reader`` surfaces it.

The report is deterministic: it parses the committed fixture with
``read_bak_metadata`` and confirms each EXPOSED field is actually present, so a
regression flips a row to ``MISSING`` and ``tests/test_metadata_coverage.py``
fails until the doc is regenerated.

Regenerate:  ``python -m tools.metadata_coverage``
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak.reader import (  # noqa: E402
    BakMetadata,
    is_compressed_or_encrypted,
    read_bak_metadata,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "METADATA_COVERAGE.md"
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
FIXTURE = _FIXTURE_DIR / "typecoverage_full.bak"

# Status values.
EXPOSED  = "EXPOSED"   # parsed and surfaced via the public API (counts toward coverage)
INTERNAL = "INTERNAL"  # parsed, used to drive decoding/iteration, not surfaced
SKIPPED  = "SKIPPED"   # present in the format but intentionally not extracted
GAP      = "GAP"       # meaningful metadata we do not yet extract (counts against coverage)


@dataclass(frozen=True)
class Meta:
    """One metadata field in the backup container and its coverage status."""

    source: str
    name: str
    status: str
    api: str = "—"
    note: str = ""
    getter: Callable[[BakMetadata], object] | None = field(default=None)
    optional: bool = False  # EXPOSED capability that the source may legitimately omit


def _fs(meta: BakMetadata, attr: str) -> object:
    s = meta.first_set
    return getattr(s, attr) if s is not None else None


# ── The full metadata surface, grouped by source block ─────────────────────────
#
# References: Microsoft Tape Format Specification v1.00a (MTF_DB_HDR, MTF_TAPE_BLK,
# MTF_SSET_BLK) and SQL Server's undocumented post-descriptor config stream.

FIELDS: list[Meta] = [
    # ── MTF common block header (MTF_DB_HDR) ──────────────────────────────────
    Meta("common header", "DBLK type",               INTERNAL, "—", "dispatches TAPE vs SSET parsing"),
    Meta("common header", "block attributes",        SKIPPED,  "—", "continuation/compression flags"),
    Meta("common header", "offset to first event",   SKIPPED,  "—", "tape stream positioning"),
    Meta("common header", "OS id / OS version",      SKIPPED,  "—", "always Windows NT for SQL Server"),
    Meta("common header", "displayable size",        SKIPPED,  "—", "user-display hint, not authoritative"),
    Meta("common header", "format logical address",  SKIPPED,  "—", "tape positioning"),
    Meta("common header", "control block id",        SKIPPED,  "—", "recovery aid"),
    Meta("common header", "OS-specific data ptr",    INTERNAL, "—", "address of OS extension"),
    Meta("common header", "string type",             INTERNAL, "—", "selects ANSI vs UTF-16LE decode"),
    Meta("common header", "header checksum",         SKIPPED,  "—", "integrity field"),
    Meta("common header", "physical block size",     INTERNAL, "BakMetadata.block_size",
         "detected by probing, exposed", lambda m: m.block_size),

    # ── MTF TAPE descriptor (MTF_TAPE_BLK) ────────────────────────────────────
    Meta("TAPE", "media family id",        SKIPPED,  "—", "media-set grouping"),
    Meta("TAPE", "tape attributes",        SKIPPED,  "—", "soft-filemark/label flags"),
    Meta("TAPE", "media sequence number",  SKIPPED,  "—", "multi-volume ordering"),
    Meta("TAPE", "password encryption",    SKIPPED,  "—", "media password algorithm"),
    Meta("TAPE", "media catalogue type",   SKIPPED,  "—", "MBC type"),
    Meta("TAPE", "media name",             EXPOSED, "MediaInfo.media_name",
         "optional; shares the validated `_resolve_addr` path with software name",
         lambda m: m.media.media_name, optional=True),
    Meta("TAPE", "media description/label", SKIPPED, "—", "pipe-delimited vendor label"),
    Meta("TAPE", "media password",         SKIPPED,  "—", "encrypted password digest"),
    Meta("TAPE", "software name",          EXPOSED, "MediaInfo.software_name",
         "", lambda m: m.media.software_name),
    Meta("TAPE", "software vendor id",     SKIPPED,  "—", "numeric vendor id"),
    Meta("TAPE", "media date",             EXPOSED, "MediaInfo.media_date",
         "", lambda m: m.media.media_date),
    Meta("TAPE", "MTF major version",      EXPOSED, "MediaInfo.mtf_version",
         "", lambda m: m.media.mtf_version),

    # ── MTF SSET descriptor (MTF_SSET_BLK) ────────────────────────────────────
    Meta("SSET", "block attributes (backup kind)", EXPOSED,
         "BackupSetInfo.backup_attributes / backup_type_label",
         "Full / Differential / copy-only", lambda m: _fs(m, "backup_type_label")),
    Meta("SSET", "password encryption",   SKIPPED, "—", "set password algorithm"),
    Meta("SSET", "software compression",  SKIPPED, "—", "compression algorithm id"),
    Meta("SSET", "software vendor id",    SKIPPED, "—", "numeric vendor id"),
    Meta("SSET", "data set number",       EXPOSED, "BackupSetInfo.dataset_number",
         "", lambda m: _fs(m, "dataset_number")),
    Meta("SSET", "data set name",         EXPOSED, "BackupSetInfo.database_name",
         "used as database name when present", lambda m: _fs(m, "database_name")),
    Meta("SSET", "data set description",  SKIPPED, "—", "free-text, usually empty"),
    Meta("SSET", "data set password",     SKIPPED, "—", "encrypted password digest"),
    Meta("SSET", "user name",             EXPOSED, "BackupSetInfo.user_name",
         "", lambda m: _fs(m, "user_name")),
    Meta("SSET", "physical block address", SKIPPED, "—", "tape positioning"),
    Meta("SSET", "media write date",      EXPOSED, "BackupSetInfo.write_date",
         "backup timestamp", lambda m: _fs(m, "write_date")),
    Meta("SSET", "software major version", EXPOSED, "BackupSetInfo.software_version",
         "", lambda m: _fs(m, "software_version")),
    Meta("SSET", "software minor version", SKIPPED, "—", "only major version retained"),
    Meta("SSET", "time zone",             SKIPPED, "—", "UTC offset of write date"),
    Meta("SSET", "MTF minor version",     SKIPPED, "—", "format revision"),
    Meta("SSET", "media catalog version", SKIPPED, "—", "MBC version"),

    # ── SQL Server proprietary config stream (post-descriptor) ────────────────
    Meta("SQL config", "database name",   EXPOSED, "BackupSetInfo.database_name",
         "data-set name or primary .mdf stem", lambda m: _fs(m, "database_name")),
    Meta("SQL config", "data/log file paths", EXPOSED, "BackupSetInfo.data_files",
         ".mdf/.ndf/.ldf paths in the SSET block", lambda m: _fs(m, "data_files")),
    Meta("SQL config", "server instance",  EXPOSED, "BackupSetInfo.server_instance",
         "MACHINE or MACHINE\\INSTANCE extracted from the MQCI sub-block (same "
         "as RESTORE HEADERONLY ServerName); empty when not parseable",
         lambda m: _fs(m, "server_instance")),
    Meta("SQL config", "machine name",    EXPOSED, "BackupSetInfo.machine_name",
         "machine component of server_instance (before the first backslash); "
         "empty when server_instance is absent",
         lambda m: _fs(m, "machine_name"),
         optional=True),
    Meta("SQL config", "backup LSNs (first/last/checkpoint)", GAP, "—",
         "header LSNs are not stored verbatim in the SSET descriptor; the "
         "LSN-shaped triples there are internal fork/differential markers, not "
         "RESTORE HEADERONLY's First/Last/Checkpoint. Available via the engine "
         "for future reverse-engineering"),
    Meta("SQL config", "compression / TDE detection", EXPOSED,
         "reader.is_compressed_or_encrypted()",
         "compressed/encrypted backups use an MSSQLBAK container; compressed "
         "ones are decoded by mssqlbak.compressed (XPRESS) for extraction, "
         "TDE-encrypted ones are unsupported; the MTF info reader needs the "
         "uncompressed form",
         lambda m: not is_compressed_or_encrypted(m.file_path)),
]


def _present(value: object) -> bool:
    """A field is 'present' when the parser returned a real value."""
    if value is None:
        return False
    if isinstance(value, (str, list, bytes)):
        return len(value) > 0
    return True


def _row_status(m: Meta, meta: BakMetadata) -> tuple[str, str]:
    """Return ``(status, note)`` for a field, validating EXPOSED ones."""
    if m.status == EXPOSED and m.getter is not None and not _present(m.getter(meta)):
        if m.optional:
            return (EXPOSED, m.note or "optional; not set in this backup")
        return ("MISSING", f"{m.note} — expected in fixture but absent" if m.note else
                "expected in fixture but absent")
    return (m.status, m.note)


def build_report(fixture: Path = FIXTURE) -> str:
    """Build the full markdown metadata-coverage report (deterministic)."""
    meta = read_bak_metadata(fixture)

    n_exposed = sum(1 for m in FIELDS if m.status == EXPOSED)
    n_gap     = sum(1 for m in FIELDS if m.status == GAP)
    meaningful = n_exposed + n_gap
    pct = round(100 * n_exposed / meaningful) if meaningful else 0

    lines: list[str] = [
        "# Metadata coverage",
        "",
        "Every field in the SQL Server backup container's metadata and whether",
        "`mssqlbak.reader` extracts it. **Generated** by `python -m tools.metadata_coverage`",
        "from the MTF specification field list and the committed fixture;",
        "`tests/test_metadata_coverage.py` fails if this file is out of date or if an",
        "EXPOSED field stops resolving on the fixture.",
        "",
        "This is the **metadata** slice of the byte-complete [BYTE_MAP.md](BYTE_MAP.md) "
        "(the master coverage doc); the data slice is [TYPE_COVERAGE.md](TYPE_COVERAGE.md). "
        "Which backup *types* can be restored is tracked in "
        "[BACKUP_COVERAGE.md](BACKUP_COVERAGE.md).",
        "",
        f"**Coverage:** {n_exposed}/{meaningful} meaningful fields exposed ({pct}%); "
        f"{n_gap} gap(s). Format-internal fields (reserved/checksum/positioning) are "
        "SKIPPED and excluded from the denominator.",
        "",
        "The metadata path (`read_bak_metadata`, used by the CLI `info` command and",
        "`restore`) is independent of the data-decode path (`extract_mdf_pages`, used by",
        "`extract`); they share no block-walking logic. See [DESIGN](../DESIGN.md).",
        "",
        "| Source | Field | Status | Exposed as | Notes |",
        "|--------|-------|--------|------------|-------|",
    ]
    for m in FIELDS:
        status, note = _row_status(m, meta)
        lines.append(f"| {m.source} | {m.name} | {status} | {m.api} | {note} |")

    lines += [
        "",
        "## Legend",
        "",
        "- **EXPOSED** — parsed and surfaced via the public API; validated present on the fixture. Counts toward coverage.",
        "- **INTERNAL** — parsed and used to drive decoding/iteration, but not surfaced as metadata.",
        "- **SKIPPED** — present in the format but intentionally not extracted (reserved, checksum, encryption/compression ids, tape positioning). Not relevant to backup identity.",
        "- **GAP** — meaningful metadata we do not yet extract. Counts against coverage.",
        "- **MISSING** — an EXPOSED field that failed to resolve on the fixture (a regression).",
        "",
        "## Gaps",
        "",
        "To reach 100% coverage, decode these from SQL Server's proprietary config stream:",
        "",
    ]
    gaps = [f"`{m.name}` — {m.note}" for m in FIELDS if m.status == GAP]
    lines.append("- " + "\n- ".join(gaps) if gaps else "- (none)")
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
