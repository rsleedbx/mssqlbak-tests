"""Download public SQL Server sample `.bak` databases for regression testing.

The Microsoft `sql-server-samples` repository links to a number of sample
backup files (AdventureWorks, WideWorldImporters, and a few standalone Azure
blobs). SQLskills.com also publishes several sample databases as zip archives.
These files are large, so they are kept out of git (see `.gitignore`) and
downloaded on demand into `tests/fixtures_realworld/`.

Usage::

    python -m tools.fetch_sample_baks            # fetch everything missing
    python -m tools.fetch_sample_baks --force     # re-download even if present
    python -m tools.fetch_sample_baks --only AdventureWorks2022.bak
    python -m tools.fetch_sample_baks --only CreditBackup100.bak

Downloads are idempotent: a file is skipped if it already exists with a
non-zero size. Partial downloads go to a `.part` file and are renamed only on
success, so an interrupted run never leaves a truncated `.bak` in place.

When ``zip_member`` is set the download URL points to a zip archive; the named
member is extracted from it and the zip is discarded.
"""
from __future__ import annotations

import argparse
import io
import sys
import os
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEST_DIR = Path(os.environ.get("SAMPLE_DIR", str(_REPO_ROOT / "tests" / "fixtures_realworld")))

_GH = "https://github.com/microsoft/sql-server-samples/releases/download"
_ADW = f"{_GH}/adventureworks"
_ADW_2008R2 = f"{_GH}/adventureworks2008r2"
_WWI = f"{_GH}/wide-world-importers-v1.0"
# Stack Overflow Mini — Brent Ozar's public SQL Server 2022 sample database.
# 2008–2009 data only; ~758 MB compressed.  License: CC BY-SA 4.0.
# Source: https://github.com/BrentOzarULTD/Stack-Overflow-Database/releases
_SO_MINI_URL = (
    "https://github.com/BrentOzarULTD/Stack-Overflow-Database"
    "/releases/download/20230114/StackOverflowMini.bak"
)

# AdventureWorks OLTP / Data Warehouse / LT, one backup per SQL Server version.
_ADVENTUREWORKS = [
    "AdventureWorks2012", "AdventureWorks2014", "AdventureWorks2016",
    "AdventureWorks2016_EXT", "AdventureWorks2017", "AdventureWorks2019",
    "AdventureWorks2022", "AdventureWorks2025",
    "AdventureWorksDW2012", "AdventureWorksDW2014", "AdventureWorksDW2016",
    "AdventureWorksDW2016_EXT", "AdventureWorksDW2017", "AdventureWorksDW2019",
    "AdventureWorksDW2022", "AdventureWorksDW2025",
    "AdventureWorksLT2012", "AdventureWorksLT2014", "AdventureWorksLT2016",
    "AdventureWorksLT2017", "AdventureWorksLT2019", "AdventureWorksLT2022",
    "AdventureWorksLT2025",
]

_WIDE_WORLD_IMPORTERS = [
    "WideWorldImporters-Full", "WideWorldImporters-Full_old",
    "WideWorldImporters-Standard", "WideWorldImporters-Standard_old",
    "WideWorldImportersDW-Full", "WideWorldImportersDW-Standard",
]

_WIDE_WORLD_IMPORTERS_BACPAC = [
    "WideWorldImporters-Full",
    "WideWorldImporters-Full_old",
    "WideWorldImporters-Standard",
    "WideWorldImporters-Standard_old",
    "WideWorldImportersDW-Full",
    "WideWorldImportersDW-Standard",
]


@dataclass(frozen=True)
class Sample:
    filename: str
    url: str
    # When the URL is a zip archive, name the member to extract.
    zip_member: str = field(default="")
    # Human-readable download page for samples that require manual acceptance.
    # When set the script will NOT download; it prints the URL and skips.
    manual_download_page: str = field(default="")


# SourceForge mirror of the ML/Language-Extensions tutorial databases. The
# original Azure blobs (sqlchoice.blob.core.windows.net) have been retired, so
# TutorialDB / tpcxbb_1gb are sourced here instead. NYCTaxi_Sample is mirror-only.
_SF = (
    "https://sourceforge.net/projects/azure-data-sql-samples.mirror/files"
    "/sql-ml-language-extensions-tutorials"
)

# Chinook Database — music-store sample with artists, albums, tracks, invoices.
# Hosted directly in the GitHub repo (not a release asset); raw URL resolves via 302.
# Source: https://github.com/cwoodruff/ChinookDatabase
# License: MIT
_CHINOOK = "https://github.com/cwoodruff/ChinookDatabase/raw/master/restore/MSSQL"

# SQLskills.com public sample databases (zip archives; BAK extracted on download).
# Source: https://www.sqlskills.com/sql-server-resources/sql-server-demos/
# License: publicly redistributable for learning/training purposes.
_SS = "https://www.sqlskills.com/resources/conferences"
_SQLSKILLS: list[tuple[str, str, str]] = [
    # (output_filename, zip_url, member_name_inside_zip)
    ("CreditBackup100.bak",           f"{_SS}/creditbackup100.zip",             "CreditBackup100.bak"),
    ("SalesDBOriginal.bak",           f"{_SS}/salesdb90.zip",                   "SalesDBOriginal.bak"),
    ("SalesDB2014.bak",               f"{_SS}/salesdb2014.zip",                 "SalesDB2014.bak"),
    ("IndexInternals2008.bak",        f"{_SS}/indexinternals2008.zip",           "IndexInternals2008.bak"),
    ("BaseballData.bak",              f"{_SS}/baseball_db.zip",                 "BaseballData.bak"),
    ("EmployeeCaseStudySampleDB2012.bak", f"{_SS}/employeecasestudysampledb2012.zip", "EmployeeCaseStudySampleDB2012.bak"),
]


def build_manifest() -> list[Sample]:
    samples = [Sample(f"{n}.bak", f"{_ADW}/{n}.bak") for n in _ADVENTUREWORKS]
    # SQL Server 2008 R2 variants — different release tag and filename convention.
    # The upstream filenames use dashes; we normalise to AdventureWorks* on disk.
    samples += [
        Sample(
            "AdventureWorks2008R2.bak",
            f"{_ADW_2008R2}/adventure-works-2008r2-oltp.bak",
        ),
        Sample(
            "AdventureWorksDW2008R2.bak",
            f"{_ADW_2008R2}/adventure-works-2008r2-dw.bak",
        ),
    ]
    samples += [Sample(f"{n}.bak", f"{_WWI}/{n}.bak") for n in _WIDE_WORLD_IMPORTERS]
    # WideWorldImporters .bacpac files (Azure SQL Database import/export format).
    # Same GitHub release tag as the .bak files; auto-downloadable.
    samples += [Sample(f"{n}.bacpac", f"{_WWI}/{n}.bacpac") for n in _WIDE_WORLD_IMPORTERS_BACPAC]
    samples += [
        Sample("NYCTaxi_Sample.bak", f"{_SF}/NYCTaxi_Sample.bak/download"),
        Sample("TutorialDB.bak", f"{_SF}/TutorialDB.bak/download"),
        Sample("tpcxbb_1gb.bak", f"{_SF}/tpcxbb_1gb.bak/download"),
        Sample("StackOverflowMini.bak", _SO_MINI_URL),
        Sample("Chinook.bak",       f"{_CHINOOK}/Chinook.bak"),
        Sample("Chinook-id-pk.bak", f"{_CHINOOK}/Chinook-id-pk.bak"),
    ]
    # Standalone Azure blobs referenced from individual feature samples. These
    # assets appear to be retired (no working mirror found); failures are
    # reported, not fatal. Left here to document the original source.
    samples += [
        Sample(
            "telcoedw2.bak",
            "https://sqlchoice.blob.core.windows.net/sqlchoice/samples/telco-customer-churn/teloedw2.bak",
        ),
        Sample(
            "velibDB.bak",
            "https://sq14samples.blob.core.windows.net/data/velibDB.bak",
        ),
    ]
    # SQLskills.com samples — distributed as zip archives containing one BAK each.
    samples += [
        Sample(filename=fname, url=zip_url, zip_member=member)
        for fname, zip_url, member in _SQLSKILLS
    ]
    # Samples that require manual download (login wall, license page, or Cloudflare
    # bot-protection on the download server).  The script will NOT attempt to download
    # these; it prints the URL and skips.  After downloading, place the .bak in
    # tests/fixtures_realworld/.
    samples += [
        Sample(
            filename="ContosoRetailDW.bak",
            url="",
            manual_download_page=(
                "https://www.microsoft.com/en-us/download/details.aspx?id=18279"
                " — download ContosoBIdemoBAK.exe, run it to extract ContosoRetailDW.bak"
            ),
        ),
        Sample(
            filename="GeneralHospital.bak",
            url="",
            manual_download_page=(
                "https://community.qlik.com/t5/Healthcare/General-Hospital-SQL-Server-BAK-file/td-p/1493132"
                " — requires Qlik Community login; download the GeneralHospital.bak attachment"
            ),
        ),
        # Red9.com sample databases — hosted behind Cloudflare bot-protection;
        # visit the page, click each download link, save to tests/fixtures_realworld/.
        # Source: https://red9.com/blog/sample-sql-databases/
        Sample(
            filename="Pubs.bak",
            url="",
            manual_download_page=(
                "https://red9.com/blog/sample-sql-databases/"
                " — click 'Pubs.bak' in the download table (~16 MB, SQL Server 2000+, 11 tables)"
            ),
        ),
        Sample(
            filename="data.gov.bak",
            url="",
            manual_download_page=(
                "https://red9.com/blog/sample-sql-databases/"
                " — click 'data.gov.bak' in the download table"
                " (~208 MB, SQL Server 2019+, 1 table: Electric_Vehicle_Population_Data 150 K rows)"
            ),
        ),
        Sample(
            filename="dba.stackexchange.com.bak",
            url="",
            manual_download_page=(
                "https://red9.com/blog/sample-sql-databases/"
                " — click 'dba.stackexchange.com.bak' in the download table"
                " (~1.3 GB, SQL Server 2019+, 8 tables: Votes 892 K, PostHistory 814 K, Badge 416 K)"
            ),
        ),
    ]
    return samples


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}GiB"


def _download(sample: Sample, dest: Path) -> int:
    part = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(sample.url, headers={"User-Agent": "mssqlbak-fetch/1.0"})
    if sample.zip_member:
        # Download zip into memory, extract the named member to disk.
        with urllib.request.urlopen(req) as resp:  # noqa: S310
            raw = resp.read()
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            data = zf.read(sample.zip_member)
        part.write_bytes(data)
        part.replace(dest)
        return len(data)
    with urllib.request.urlopen(req) as resp, part.open("wb") as out:  # noqa: S310
        total = 0
        while chunk := resp.read(1 << 20):
            out.write(chunk)
            total += len(chunk)
    part.replace(dest)
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-download even if present")
    parser.add_argument("--only", action="append", default=[], metavar="FILENAME",
                        help="only fetch the named .bak (repeatable)")
    parser.add_argument("--list", action="store_true", help="list the manifest and exit")
    args = parser.parse_args(argv)

    manifest = build_manifest()
    if args.only:
        wanted = set(args.only)
        manifest = [s for s in manifest if s.filename in wanted]
        missing = wanted - {s.filename for s in manifest}
        if missing:
            print(f"unknown --only names: {', '.join(sorted(missing))}", file=sys.stderr)
            return 2

    if args.list:
        for s in manifest:
            url = s.manual_download_page if s.manual_download_page else s.url
            print(f"{s.filename}\t{url}")
        return 0

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"destination: {DEST_DIR}")

    failures: list[tuple[str, str]] = []
    fetched = skipped = manual = 0
    for s in manifest:
        dest = DEST_DIR / s.filename
        if dest.exists() and dest.stat().st_size > 0 and not args.force:
            print(f"  skip   {s.filename} ({_human(dest.stat().st_size)} already present)")
            skipped += 1
            continue
        if s.manual_download_page:
            print(f"  manual {s.filename}  (license-gated — download manually)")
            print(f"         {s.manual_download_page}")
            print(f"         then copy {s.filename} to {DEST_DIR}")
            manual += 1
            continue
        print(f"  fetch  {s.filename} <- {s.url}")
        try:
            size = _download(s, dest)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            print(f"  FAIL   {s.filename}: {exc}", file=sys.stderr)
            failures.append((s.filename, str(exc)))
            continue
        print(f"  done   {s.filename} ({_human(size)})")
        fetched += 1

    print(f"\nfetched {fetched}, skipped {skipped}, manual {manual}, failed {len(failures)}")
    if failures:
        print("failures:", file=sys.stderr)
        for name, err in failures:
            print(f"  {name}: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
