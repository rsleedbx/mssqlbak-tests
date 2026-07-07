#!/usr/bin/env python3
"""Generate ``docs/BYTE_MAP.md`` — a complete, byte-for-byte map of a .bak file.

This is the **master** coverage document.  Where ``METADATA_COVERAGE.md`` tracks
descriptor *fields* and ``TYPE_COVERAGE.md`` tracks column *types*, this report
tiles **every byte** of the backup into exactly one category — metadata, data,
or skippable container framing — and asserts that nothing is left unclassified.

Why it matters: a SQL Server restore reproduces the embedded data-file page
image.  Confidence that we can reconstruct (or fully understand) a backup
requires knowing what *every* byte is, not just the parts we currently decode.
A non-zero "UNKNOWN" total is a direct, quantified confidence gap.

The map is built purely from the file bytes (no engine):

* ``[0, image_start)``  — MTF descriptor blocks (TAPE/SSET = metadata; soft
  filemarks = framing) followed by the MDF data-stream descriptors (MSDA).
* ``[image_start, image_end)`` — the contiguous 8 KB MDF page image of data
  file 1, sub-classified per page by ``m_type`` (data / index / LOB = data;
  GAM/IAM/PFS/boot/etc. = allocation; all-zero = unallocated).
* ``[image_end, EOF)`` — end-of-set trailer: the log-file data stream (often a
  zero-byte payload for a fresh DB), ESET/EOTM descriptors, filemarks, padding.

The image bounds come from ``mssqlbak.mtf`` (the same logic the extractor uses),
so the "data" total here is exactly what the extractor reads.  When a live
engine is available, ``tests/test_byte_map.py`` cross-checks the detected image
size against ``RESTORE FILELISTONLY``'s ``BackupSizeInBytes`` for data file 1.

Regenerate:  ``python -m tools.byte_map``
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mssqlbak import mtf  # noqa: E402
from mssqlbak.reader import (  # noqa: E402
    BLOCK_SSET,
    BLOCK_TAPE,
    _detect_block_size,
    is_compressed_or_encrypted,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "BYTE_MAP.md"
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(REPO_ROOT / "tests" / "fixtures_2022")))
FIXTURE = _FIXTURE_DIR / "typecoverage_full.bak"

# ── Categories and the three top-level buckets ─────────────────────────────────

METADATA   = "METADATA"     # descriptor fields we parse (see METADATA_COVERAGE.md)
DATA       = "DATA"         # MDF data/index/LOB pages (see TYPE_COVERAGE.md)
ALLOCATION = "ALLOCATION"   # GAM/SGAM/IAM/PFS/boot/file-header/… bookkeeping pages
UNUSED     = "UNUSED"       # unallocated, zero-filled pages
FRAMING    = "FRAMING"      # MTF container: descriptors, stream headers, padding
UNKNOWN    = "UNKNOWN"      # unclassified — MUST be zero for full confidence

# Bucket each category rolls up into for the headline summary.
BUCKET = {
    METADATA:   "Metadata",
    DATA:       "Data",
    ALLOCATION: "Skippable",
    UNUSED:     "Skippable",
    FRAMING:    "Skippable",
    UNKNOWN:    "Unknown",
}

# Which coverage doc owns the detail of each category.
ANCHOR = {
    METADATA: "[METADATA_COVERAGE.md](METADATA_COVERAGE.md)",
    DATA:     "[TYPE_COVERAGE.md](TYPE_COVERAGE.md)",
}

# MDF page types (m_type, byte 1 of the 96-byte page header).
_PAGE_TYPES: dict[int, tuple[str, str]] = {
    1:  (DATA,       "data page"),
    2:  (DATA,       "index page"),
    3:  (DATA,       "LOB / text-mix page"),
    4:  (DATA,       "LOB / text-tree page"),
    7:  (ALLOCATION, "sort page"),
    8:  (ALLOCATION, "GAM (global allocation map)"),
    9:  (ALLOCATION, "SGAM (shared global allocation map)"),
    10: (ALLOCATION, "IAM (index allocation map)"),
    11: (ALLOCATION, "PFS (page free space)"),
    13: (ALLOCATION, "boot page"),
    15: (ALLOCATION, "file-header page"),
    16: (ALLOCATION, "differential bitmap"),
    17: (ALLOCATION, "ML (bulk-logged) map"),
    18: (ALLOCATION, "dbcc / file-maintenance page"),
    19: (ALLOCATION, "file-maintenance page"),
}

# MTF descriptor DBLK type codes that carry parsed metadata.
_METADATA_BLOCKS = {BLOCK_TAPE: "TAPE media descriptor",
                    BLOCK_SSET: "SSET backup-set descriptor"}


@dataclass(frozen=True)
class Segment:
    """A contiguous run of bytes assigned to exactly one category."""

    offset: int
    length: int
    category: str
    detail: str

    @property
    def end(self) -> int:
        return self.offset + self.length


@dataclass(frozen=True)
class PageClass:
    """An aggregated page-type bucket within the data-file image."""

    category: str
    detail: str
    pages: int

    @property
    def nbytes(self) -> int:
        return self.pages * mtf.PAGE_SIZE


@dataclass(frozen=True)
class ByteMap:
    """The complete tiling of a .bak file."""

    path: Path
    file_size: int
    block_size: int
    image_start: int
    image_end: int
    segments: list[Segment]      # tiles [0, file_size) exactly
    page_classes: list[PageClass]  # sub-tiling of [image_start, image_end)


def _classify_page(page: bytes) -> tuple[str, str]:
    if page == mtf._ZERO_PAGE:
        return (UNUSED, "unallocated (zero-filled) page")
    m_type = page[mtf._OFF_TYPE]
    if m_type in _PAGE_TYPES:
        return _PAGE_TYPES[m_type]
    return (UNKNOWN, f"unrecognised page m_type={m_type}")


def build_map(path: str | Path) -> ByteMap:
    """Tile *path* into a complete, gap-free byte map."""
    p = Path(path)
    if is_compressed_or_encrypted(p):
        raise ValueError(f"{p.name!r} is a compressed/encrypted backup; no MTF byte map.")
    buf = p.read_bytes()
    n = len(buf)

    with p.open("rb") as f:
        block_size = _detect_block_size(f)

    image_start = mtf._find_image_start(buf)
    # Physical span of the page image in the file: the page bytes are stored
    # contiguously (page-id gaps are sparse omissions, not file gaps), so count
    # consecutive 8 KB slots that are blank or file-1 pages until the next
    # (non-page) MTF descriptor -- the same stop the page walk uses.
    npages = 0
    _off = image_start
    while _off + mtf.PAGE_SIZE <= n:
        _page = buf[_off : _off + mtf.PAGE_SIZE]
        _pid, _fid = mtf._PAGE_LOC.unpack_from(_page, mtf._OFF_PAGE_ID)
        if _page == mtf._ZERO_PAGE or (_pid == 0 and _fid == 0) or _fid == 1:
            npages += 1
            _off += mtf.PAGE_SIZE
            continue
        break
    # Trim trailing unallocated (blank) pages: the reassembled image the
    # extractor returns is sized to the last real page, so the DATA span ends
    # there and any trailing blanks fall into the end-of-set trailer.
    while npages > 0:
        _last = buf[image_start + (npages - 1) * mtf.PAGE_SIZE : image_start + npages * mtf.PAGE_SIZE]
        _pid, _fid = mtf._PAGE_LOC.unpack_from(_last, mtf._OFF_PAGE_ID)
        if _last == mtf._ZERO_PAGE or (_pid == 0 and _fid == 0):
            npages -= 1
        else:
            break
    image_end = image_start + npages * mtf.PAGE_SIZE

    segments: list[Segment] = []

    # ── Pre-image: MTF descriptor blocks, then the data-stream descriptors ─────
    off = 0
    while off < image_start:
        tag = buf[off : off + 4]
        if off + block_size <= image_start and tag in _METADATA_BLOCKS:
            segments.append(Segment(off, block_size, METADATA, _METADATA_BLOCKS[tag]))
            off += block_size
        elif off + block_size <= image_start and tag == b"SFMB":
            segments.append(Segment(off, block_size, FRAMING, "soft filemark (SFMB)"))
            off += block_size
        else:
            # Remaining bytes before the image are the MTF data-stream framing
            # (MSDA stream header + SPAD/APAD alignment pads).
            segments.append(Segment(off, image_start - off, FRAMING,
                                    "MDF data-stream descriptors (MSDA) + padding"))
            off = image_start

    # ── The MDF data-file page image (file 1) ─────────────────────────────────
    segments.append(Segment(image_start, image_end - image_start, DATA,
                            "MDF data-file page image (file 1)"))

    # ── Trailer: end-of-set descriptors + log-file stream ─────────────────────
    if image_end < n:
        segments.append(Segment(image_end, n - image_end, FRAMING,
                                 "end-of-set trailer: log-file stream, "
                                 "ESET/EOTM, filemarks, padding"))

    # ── Sub-tiling of the image by page type ──────────────────────────────────
    counts: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for k in range(npages):
        page = buf[image_start + k * mtf.PAGE_SIZE : image_start + (k + 1) * mtf.PAGE_SIZE]
        key = _classify_page(page)
        if key not in counts:
            counts[key] = 0
            order.append(key)
        counts[key] += 1
    page_classes = [PageClass(cat, detail, counts[(cat, detail)]) for cat, detail in order]

    return ByteMap(
        path=p.resolve(),
        file_size=n,
        block_size=block_size,
        image_start=image_start,
        image_end=image_end,
        segments=segments,
        page_classes=page_classes,
    )


def bucket_totals(bm: ByteMap) -> dict[str, int]:
    """Roll the tiling up into Metadata / Data / Skippable / Unknown byte totals."""
    totals = {"Metadata": 0, "Data": 0, "Skippable": 0, "Unknown": 0}
    for seg in bm.segments:
        if seg.category == DATA:
            continue  # the image is accounted at page granularity below
        totals[BUCKET[seg.category]] += seg.length
    for pc in bm.page_classes:
        totals[BUCKET[pc.category]] += pc.nbytes
    return totals


def _pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.2f}%" if whole else "0%"


def build_report(fixture: Path = FIXTURE) -> str:
    bm = build_map(fixture)
    totals = bucket_totals(bm)
    accounted = totals["Metadata"] + totals["Data"] + totals["Skippable"]
    unknown = totals["Unknown"]

    lines: list[str] = [
        "# Byte map (master coverage)",
        "",
        "Every byte of the backup, classified as **metadata**, **data**, or",
        "**skippable** container framing. **Generated** by `python -m tools.byte_map`",
        "from the file bytes alone; `tests/test_byte_map.py` fails if this file is",
        "stale or if the tiling leaves any byte unclassified.",
        "",
        "This is the master document. It anchors the field- and type-level reports:",
        "",
        "- **Metadata** bytes → detailed in [METADATA_COVERAGE.md](METADATA_COVERAGE.md)",
        "- **Data** bytes (MDF page image) → decoded per the types in [TYPE_COVERAGE.md](TYPE_COVERAGE.md)",
        "- **Skippable** bytes → MTF container framing, allocation/system pages, "
        "unallocated pages, and the end-of-set trailer (not part of restored row data)",
        "",
        "Which backup *types* (full / differential / log / …) can be restored at all "
        "is tracked separately in [BACKUP_COVERAGE.md](BACKUP_COVERAGE.md); how keys, "
        "indexes and constraints are encoded is in "
        "[CONSTRAINT_COVERAGE.md](CONSTRAINT_COVERAGE.md); what is detected and "
        "skipped (heaps, compression, partitioning, …) is in "
        "[ROBUSTNESS_COVERAGE.md](ROBUSTNESS_COVERAGE.md).",
        "",
        f"**Fixture:** `{bm.path.name}` — {bm.file_size:,} bytes, "
        f"MTF block size {bm.block_size}.",
        "",
        f"**Accounted: {_pct(accounted, bm.file_size)} of the file "
        f"({accounted:,} / {bm.file_size:,} bytes). "
        f"UNKNOWN: {unknown:,} bytes.**",
        "",
        "## Byte budget",
        "",
        "| Bucket | Bytes | Share | Meaning |",
        "|--------|------:|------:|---------|",
        f"| Metadata | {totals['Metadata']:,} | {_pct(totals['Metadata'], bm.file_size)} "
        "| Backup descriptors we parse into fields |",
        f"| Data | {totals['Data']:,} | {_pct(totals['Data'], bm.file_size)} "
        "| MDF data-file page image (the restored content) |",
        f"| Skippable | {totals['Skippable']:,} | {_pct(totals['Skippable'], bm.file_size)} "
        "| Container framing, allocation/system pages, unallocated space, trailer |",
        f"| **Unknown** | **{unknown:,}** | **{_pct(unknown, bm.file_size)}** "
        "| **Unclassified — must be 0** |",
        "",
        "## Top-level layout",
        "",
        "Contiguous regions, in file order. These tile the whole file with no gaps.",
        "",
        "| Offset | Length | Category | Region | Anchor |",
        "|-------:|-------:|----------|--------|--------|",
    ]
    for seg in bm.segments:
        anchor = ANCHOR.get(seg.category, "—")
        lines.append(
            f"| {seg.offset:,} | {seg.length:,} | {seg.category} | {seg.detail} | {anchor} |"
        )

    image_bytes = bm.image_end - bm.image_start
    lines += [
        "",
        "## Inside the data-file image (per page type)",
        "",
        f"The {image_bytes:,}-byte image is {image_bytes // mtf.PAGE_SIZE} pages of "
        f"{mtf.PAGE_SIZE} bytes. Each page's `m_type` determines its class:",
        "",
        "| Class | Page type | Pages | Bytes | Share of image |",
        "|-------|-----------|------:|------:|---------------:|",
    ]
    for pc in bm.page_classes:
        lines.append(
            f"| {pc.category} | {pc.detail} | {pc.pages} | {pc.nbytes:,} "
            f"| {_pct(pc.nbytes, image_bytes)} |"
        )

    lines += [
        "",
        "## Restore completeness",
        "",
        "The **data** bucket is exactly the page image the extractor reads, located by",
        "`mssqlbak.mtf`. For a SQL Server restore this is the content written back to",
        "the `.mdf`. When a live engine is available, `tests/test_byte_map.py` confirms",
        "this image equals `RESTORE FILELISTONLY`'s `BackupSizeInBytes` for data file 1,",
        "so the data file is captured byte-for-byte.",
        "",
        "The **log file** is carried in the end-of-set trailer as its own MTF stream.",
        "For a copy-only backup of a freshly created database its backed-up payload is",
        "0 bytes (nothing to extract). A full crash-consistent *restore* of a database",
        "with log activity would also need that stream replayed; the data-hydration use",
        "case this parser targets does not.",
        "",
        "## Legend",
        "",
        "- **METADATA** — backup descriptor fields parsed by `reader.py` (see "
        "[METADATA_COVERAGE.md](METADATA_COVERAGE.md)).",
        "- **DATA** — MDF data / index / LOB pages; row values decoded per "
        "[TYPE_COVERAGE.md](TYPE_COVERAGE.md).",
        "- **ALLOCATION** — GAM/SGAM/IAM/PFS/boot/file-header/diff/ML pages: structural "
        "bookkeeping, not row data.",
        "- **UNUSED** — unallocated, zero-filled pages.",
        "- **FRAMING** — MTF container: descriptor blocks, stream headers, filemarks, "
        "padding, end-of-set trailer.",
        "- **UNKNOWN** — bytes the map could not classify. A non-zero total is a "
        "confidence gap and fails the guard test.",
        "",
        "See [README](../README.md) and [DESIGN](../DESIGN.md) for parser scope.",
        "",
    ]
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
