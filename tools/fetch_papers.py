"""Download freely-accessible reference PDFs used in CORROBORATION_SOURCES.md.

Papers are kept out of git (see ``docs/papers/.gitignore``) and fetched on
demand into ``docs/papers/``.  Only papers with a publicly-accessible URL are
included here; DOI-only papers (H13, D19, Harizopoulos VLDB 2006, …) require
institutional access and must be obtained separately.

Usage::

    python -m tools.fetch_papers              # fetch everything missing
    python -m tools.fetch_papers --force      # re-download even if present
    python -m tools.fetch_papers --only L11   # fetch one token by name

Downloads are idempotent: a file is skipped if it already exists with a
non-zero size.  Partial downloads go to a ``.part`` file and are renamed only
on success, so an interrupted run never leaves a truncated PDF in place.
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEST_DIR = _REPO_ROOT / "docs" / "papers"

_CMU16 = "https://15721.courses.cs.cmu.edu/spring2016/papers"


@dataclass
class Paper:
    token: str
    filename: str
    url: str
    description: str
    note: str = ""


PAPERS: list[Paper] = [
    # ── Larson / SQL Server columnstore ──────────────────────────────────────
    Paper(
        token="L11",
        filename="p1177-larson-sigmod2011.pdf",
        url=f"{_CMU16}/p1177-larson.pdf",
        description='Larson et al., "SQL Server Column Store Indexes", SIGMOD 2011',
        note="§2.2.1 canonical value-encoding formula for C1b (base_id + magnitude)",
    ),
    Paper(
        token="L13",
        filename="larson-sigmod2013.pdf",
        url=f"{_CMU16}/larson-sigmod2013.pdf",
        description='Larson et al., "Enhancements to SQL Server Column Stores", SIGMOD 2013',
        note="Clustered CCI, ARCHIVE layer, delete bitmap as B-tree of (rg_id, row_no)",
    ),
    Paper(
        token="L15",
        filename="larson-vldb2015.pdf",
        url="https://www.vldb.org/pvldb/vol8/p1740-Larson.pdf",
        description='Larson et al., "Real-Time Analytical Processing with SQL Server", VLDB 2015',
        note="Updateable CCI, delta-store tuple mover, archival compression",
    ),
    # ── Hekaton / XTP ────────────────────────────────────────────────────────
    Paper(
        token="FREED14",
        filename="freedman-hekaton-compilation-2014.pdf",
        url=f"{_CMU16}/freedman-ieee2014.pdf",
        description=(
            'Freedman, Ismert, Larson, "Compilation in the Microsoft SQL Server '
            'Hekaton Engine", IEEE Data Engineering Bulletin 2014'
        ),
        note=(
            "§12.2 V04: latch-free hash+range indexes, no buffer pool, "
            "log+checkpoint durability, rebuild from checkpoint at recovery"
        ),
    ),
    Paper(
        token="HKCC12",
        filename="larson-hekaton-mvcc-vldb2012.pdf",
        url=f"{_CMU16}/p298-larson.pdf",
        description=(
            'Larson, Blanas, Diaconu, Freedman, Patel, Zwilling, '
            '"High-Performance Concurrency Control Mechanisms for '
            'Main-Memory Databases", VLDB 2012'
        ),
        note="Hekaton MVCC: begin/end version timestamps, latch-free hash index chain",
    ),
    # ── Compression background ────────────────────────────────────────────────
    Paper(
        token="Z09",
        filename="zukowski-phd-thesis-2009.pdf",
        url="https://ir.cwi.nl/pub/14075/14075B.pdf",
        description="Zukowski PhD thesis, CWI 2009 — Balancing Vectorized Query Execution",
        note="Vectorized bitpacking, PFOR-delta, SIMDized integer compression",
    ),
    Paper(
        token="BTR23",
        filename="btrblocks-sigmod2023.pdf",
        url="https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/papers/btrblocks.pdf",
        description='Kuschewski et al., "BtrBlocks: Efficient Columnar Compression for Data Lakes", SIGMOD 2023',
        note="Survey of modern columnar compression schemes; bit-packing, FOR, RLE taxonomy",
    ),
    Paper(
        token="KRAFT",
        filename="kraft-mcmillan-mit-ocw.pdf",
        url=(
            "https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/"
            "67d8e68cd8fda55366e3f9f0a9465c17_MIT6_441S16_chapter_6.pdf"
        ),
        description="MIT OCW 6.441 chapter 6 — Kraft-McMillan theorem",
        note="§8.2 Kraft sync marker: Huffman code-length completeness invariant",
    ),
    # ── Bw-Tree (Hekaton range indexes) ──────────────────────────────────────
    Paper(
        token="BWTREE13",
        filename="levandoski-bwtree-icde2013.pdf",
        url=f"{_CMU16}/levandoski-icde2013.pdf",
        description='Levandoski, Lomet, Sengupta, "The Bw-Tree: A B-tree for New Hardware", ICDE 2013',
        note="Lock-free B-tree used by Hekaton range indexes (cited by FREED14)",
    ),
    # ── Column-store foundations (4-degree sweep D1/D2) ──────────────────────
    Paper(
        token="ABADI06",
        filename="abadi-compression-execution-sigmod2006.pdf",
        url=f"{_CMU16}/abadi-sigmod2006.pdf",
        description=(
            'Abadi, Madden, Ferreira, "Integrating Compression and Execution '
            'in Column-Oriented Database Systems", SIGMOD 2006'
        ),
        note="RLE, bit-packing, null-suppression operating directly on compressed data",
    ),
    Paper(
        token="ABADI08",
        filename="abadi-column-vs-row-sigmod2008.pdf",
        url=f"{_CMU16}/p967-abadi.pdf",
        description=(
            'Abadi, Madden, Hachem, "Column-Stores vs. Row-Stores: '
            'How Different Are They Really?", SIGMOD 2008'
        ),
        note="Late vs. early materialization; distinct from the 2013 survey in source map",
    ),
    Paper(
        token="HEMAN10",
        filename="heman-positional-updates-sigmod2010.pdf",
        url="https://event.cwi.nl/SIGMOD-RWE/2010/22-7f15a1/paper.pdf",
        description=(
            'Héman, Zukowski, Nes, Sidirourgos, Boncz, '
            '"Positional Update Handling in Column Stores", SIGMOD 2010'
        ),
        note=(
            "Positional Delta Trees (PDT) — SQL Server delta store is the "
            "analogous structure; confirms separate delta B-tree design choice"
        ),
    ),
]


def _fetch(paper: Paper, force: bool) -> bool:
    """Download *paper* to DEST_DIR. Returns True if a download occurred."""
    dest = DEST_DIR / paper.filename
    if dest.exists() and dest.stat().st_size > 0 and not force:
        print(f"  skip  {paper.token:10s} {paper.filename} (already present)")
        return False

    part = dest.with_suffix(".pdf.part")
    print(f"  fetch {paper.token:10s} {paper.url}")
    try:
        req = urllib.request.Request(
            paper.url,
            headers={"User-Agent": "mssqlbak-fetch-papers/1.0"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        part.write_bytes(data)
        part.rename(dest)
        print(f"        → {dest.name} ({len(data) // 1024} KB)")
        return True
    except urllib.error.URLError as exc:
        print(f"  ERROR {paper.token}: {exc}", file=sys.stderr)
        if part.exists():
            part.unlink()
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--force", action="store_true", help="Re-download even if already present")
    ap.add_argument(
        "--only",
        metavar="TOKEN",
        help="Download only the paper with this token (e.g. L11)",
    )
    args = ap.parse_args(argv)

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    targets = PAPERS
    if args.only:
        targets = [p for p in PAPERS if p.token == args.only]
        if not targets:
            known = ", ".join(p.token for p in PAPERS)
            print(f"Unknown token {args.only!r}. Known tokens: {known}", file=sys.stderr)
            return 1

    fetched = skipped = errors = 0
    for paper in targets:
        try:
            downloaded = _fetch(paper, force=args.force)
        except Exception as exc:
            print(f"  ERROR {paper.token}: {exc}", file=sys.stderr)
            errors += 1
            continue
        if downloaded:
            fetched += 1
        else:
            # Could be skip or error logged inside _fetch
            if (DEST_DIR / paper.filename).exists():
                skipped += 1
            else:
                errors += 1

    print(f"\nDone: {fetched} fetched, {skipped} skipped, {errors} errors")
    print(f"Papers saved to: {DEST_DIR}")
    if errors:
        print(
            "\nNOTE: Papers requiring institutional access (H13, D19, LB15, ABADI07) "
            "are not listed here — obtain them via ACM DL or arXiv manually.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
