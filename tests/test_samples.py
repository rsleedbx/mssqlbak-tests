"""End-to-end conversion of the real Microsoft ``sql-server-samples`` databases.

This page is the running checklist of every public sample ``.bak`` we target.
The catalogue is the *same* manifest the downloader uses
(:func:`tools.fetch_sample_baks.build_manifest`), so the list here can never
drift from what ``python -m tools.fetch_sample_baks`` fetches.

The backups are large and are **not** committed; they live under
``tests/fixtures_realworld/`` (git-ignored).  For each sample:

* **missing**  -> the test is *skipped* (so a clean checkout stays green);
* **present, verified** (:data:`VERIFIED`) -> strict: the whole database must
  convert to Delta with **zero** skipped tables, matching the recorded table
  and row counts;
* **present, not yet verified** -> marked ``xfail`` (non-strict): we know it is
  downloadable but have not yet driven it to a clean full extraction.  When a
  sample is fixed, move it into :data:`VERIFIED` and drop the xfail.

Run only this page with::

    pytest tests/test_samples.py -v
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from mssqlbak import extract_bak_to_delta
from mssqlbak.catalog import recover_schema
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.fetch_sample_baks import DEST_DIR, build_manifest


@dataclass(frozen=True)
class Expected:
    """Recorded ground truth for a sample proven to convert fully.

    ``None`` fields are not asserted (used when only some counts are pinned).
    ``skipped`` is the number of tables that are expected to be skipped for a
    known structural reason (e.g. In-Memory OLTP, multi-file).  When non-zero
    the "no unexpected skips" assertion is relaxed to allow exactly that count.
    """

    tables: int | None = None
    rows: int | None = None
    skipped: int = 0


# Samples proven to extract *every* user table to Delta, with engine-validated
# counts.  Keep this in sync as more samples are driven to a clean conversion.
VERIFIED: dict[str, Expected] = {
    # 71 user tables, 760,837 rows (row counts matched the live engine; all XML
    # columns byte-identical) -- see the AdventureWorks2022 work.
    "AdventureWorks2012.bak": Expected(tables=71, rows=760_837),
    "AdventureWorks2014.bak": Expected(tables=71, rows=760_838),
    "AdventureWorks2016.bak": Expected(tables=71, rows=760_838),
    "AdventureWorks2017.bak": Expected(tables=71, rows=760_837),
    "AdventureWorks2022.bak": Expected(tables=71, rows=760_837),
    "AdventureWorks2025.bak": Expected(tables=71, rows=760_167),
    # Single rental_data table; compressed (MSSQLBAK/XPRESS) container.
    "TutorialDB.bak": Expected(tables=1, rows=453),
    # AdventureWorks LT (lightweight) family -- uncompressed TAPE backups.
    "AdventureWorksLT2012.bak": Expected(tables=12, rows=4_277),
    "AdventureWorksLT2014.bak": Expected(tables=12, rows=4_277),
    "AdventureWorksLT2016.bak": Expected(tables=12, rows=4_277),
    "AdventureWorksLT2017.bak": Expected(tables=12, rows=4_277),
    "AdventureWorksLT2019.bak": Expected(tables=12, rows=4_277),
    "AdventureWorksLT2022.bak": Expected(tables=12, rows=4_277),
    "AdventureWorksLT2025.bak": Expected(tables=12, rows=4_277),
    # AdventureWorks DW (data-warehouse) family -- compressed MSSQLBAK containers.
    # 2012 is the v1 (8-byte header) container variant; 2014+ are v2 (32-byte).
    "AdventureWorksDW2012.bak": Expected(tables=31, rows=1_060_820),
    "AdventureWorksDW2014.bak": Expected(tables=31, rows=1_060_820),
    "AdventureWorksDW2016.bak": Expected(tables=31, rows=1_060_820),
    "AdventureWorksDW2017.bak": Expected(tables=31, rows=1_060_820),
    "AdventureWorksDW2025.bak": Expected(tables=31, rows=1_047_563),
    # WideWorldImporters DW (Standard) -- compressed MSSQLBAK, all rowstore.
    "WideWorldImportersDW-Standard.bak": Expected(tables=29, rows=923_643),
    # DW2019/DW2022 are larger (97MB) MSSQLBAK containers of the same schema.
    "AdventureWorksDW2019.bak": Expected(tables=31, rows=1_060_820),
    "AdventureWorksDW2022.bak": Expected(tables=31, rows=1_060_820),
    # WideWorldImporters OLTP (compressed MSSQLBAK); exercises geography columns
    # and temporal *_Archive history tables whose dropped column shifts the
    # variable-column layout (see _record_columns var_index from leaf_offset).
    "WideWorldImporters-Standard.bak": Expected(tables=48, rows=4_713_833),
    # WideWorldImporters OLTP — Full (larger dataset) and an older file variant.
    # Countries_Archive / StateProvinces_Archive now decode (unsupported spatial
    # formats return null rather than crashing); _walk_leaf stops at unavailable
    # pages instead of raising.
    "WideWorldImporters-Full.bak": Expected(tables=48, rows=4_713_833, skipped=0),
    "WideWorldImporters-Full_old.bak": Expected(tables=48, rows=4_713_832, skipped=0),
    # WideWorldImportersDW-Standard_old: an older file variant of the DW.
    "WideWorldImporters-Standard_old.bak": Expected(tables=48, rows=4_713_832),
    # AdventureWorks2019: same schema as 2017/2022; promoted after verified pass.
    "AdventureWorks2019.bak": Expected(tables=71, rows=760_837),
    # NYCTaxi demo database: populated sample, 2-table extract (row count updated
    # when the fixture was refreshed with actual data).
    "NYCTaxi_Sample.bak": Expected(tables=2, rows=1_703_957),
    # AdventureWorks2016_EXT: extended AW2016 with In-Memory OLTP (Hekaton/XTP)
    # tables. report.extracted counts 92 table attempts. All seven XTP tables now
    # land byte-exact from the log tail + checkpoint container:
    # SpecialOffer_inmem 16, DemoSalesOrderDetailSeed 538,
    # DemoSalesOrderHeaderSeed 31,465, SpecialOfferProduct_inmem 538,
    # Product_inmem 504, SalesOrderHeader_inmem 31,465, and
    # SalesOrderDetail_inmem 121,317.
    # Total rows = 1,192,874 base + 185,843 XTP.
    "AdventureWorks2016_EXT.bak": Expected(tables=92, rows=1_378_717, skipped=0),
    # tpcxbb_1gb: TPC-BB benchmark with ARCHIVE columnstore tables.  Row count
    # updated now that ARCHIVE CCI decoding is complete (was 94,044 when only
    # rowstore tables were decoded; full dataset confirmed by stats.json).
    "tpcxbb_1gb.bak": Expected(tables=30, rows=34_001_580),
    # AdventureWorksDW2016_EXT: extended DW with ARCHIVE columnstore (CCI) and
    # PAGE-compressed fact tables.  FactResellerSalesXL_CCI and
    # FactResellerSalesXL_PageCompressed each hold 11,669,638 rows (confirmed by
    # stats.json); row count was updated once ARCHIVE CCI decoding was fixed.
    "AdventureWorksDW2016_EXT.bak": Expected(tables=33, rows=24_400_096),
    # WideWorldImportersDW-Full: DW Full variant.  12 In-Memory OLTP staging
    # tables (Hekaton/XTP); all 29 tables extract (staging tables land as empty).
    "WideWorldImportersDW-Full.bak": Expected(tables=29, rows=923_643, skipped=0),
    # --- Newly verified databases (promoted from xfail after clean extraction) ---
    # AdventureWorksDW2008R2: early DW schema (v1 container), 28 tables.
    "AdventureWorksDW2008R2.bak": Expected(tables=28, rows=282_030),
    # StackOverflowMini: public SO data dump, row-compressed tables.
    "StackOverflowMini.bak": Expected(tables=9, rows=8_097_337),
    # Chinook: cross-platform sample, two variants (identity PK and natural key).
    "Chinook.bak": Expected(tables=11, rows=16_075),
    "Chinook-id-pk.bak": Expected(tables=11, rows=16_075),
    # CreditBackup100: financial sample.  Matches the live-engine count
    # (1,656,574).  This database uses PAGE_VERIFY TORN_PAGE_DETECTION; the
    # earlier 1,647,271 count was 9,303 rows short because the reader did not
    # reverse the per-sector torn-page bit substitution, so slot-0 of every
    # clustered-index leaf decoded to garbage and was dropped.  See
    # mssqlbak.pages.restore_torn_page.
    "CreditBackup100.bak": Expected(tables=10, rows=1_656_574),
    # SalesDB variants: lightweight sales samples.
    "SalesDBOriginal.bak": Expected(tables=5, rows=6_735_508),
    "SalesDB2014.bak": Expected(tables=4, rows=6_735_507),
    # IndexInternals2008 / EmployeeCaseStudySampleDB2012: internals teaching DBs.
    "IndexInternals2008.bak": Expected(tables=2, rows=160_000),
    "EmployeeCaseStudySampleDB2012.bak": Expected(tables=2, rows=160_000),
    # BaseballData: public Lahman baseball statistics dataset.
    "BaseballData.bak": Expected(tables=25, rows=493_104),
    # ContosoRetailDW: large Microsoft Contoso retail data warehouse (~34M rows).
    "ContosoRetailDW.bak": Expected(tables=26, rows=34_326_475),
    # GeneralHospital: hospital operations sample.
    "GeneralHospital.bak": Expected(tables=13, rows=2_175_940),
    # Pubs: classic "pubs" sample database.
    "Pubs.bak": Expected(tables=11, rows=255),
    # data.gov: open government dataset.
    "data.gov.bak": Expected(tables=1, rows=150_482),
    # dba.stackexchange.com: DBA community Q&A data dump.
    "dba.stackexchange.com.bak": Expected(tables=8, rows=2_968_576),
}


def _sample_path(filename: str) -> Path | None:
    """Return the on-disk path for *filename* if it is fully downloaded.

    Only the exact ``.bak`` is considered.  A download in progress writes to a
    sibling ``<name>.bak.part`` and is renamed to ``.bak`` only on success, so a
    ``.bak`` whose ``.part`` still exists is treated as incomplete and skipped
    (this guards against a ``--force`` re-download racing the test run).
    """
    path = DEST_DIR / filename
    if path.suffix != ".bak":
        return None
    if (DEST_DIR / f"{filename}.part").exists():
        return None
    if path.exists() and path.stat().st_size > 0:
        return path
    return None


def _params() -> list:
    """One parametrize entry per manifest sample; xfail the unverified ones."""
    out = []
    for sample in build_manifest():
        marks = ()
        if sample.filename not in VERIFIED:
            marks = (
                pytest.mark.xfail(
                    reason="sample not yet verified end-to-end", strict=False
                ),
            )
        out.append(pytest.param(sample.filename, marks=marks, id=sample.filename))
    return out


@pytest.mark.sample
@pytest.mark.parametrize("filename", _params())
def test_sample_bak_converts_to_delta(filename: str, tmp_path: Path) -> None:
    """Every supported user table of the sample converts to Delta with no skips."""
    path = _sample_path(filename)
    if path is None:
        pytest.skip(
            f"{filename} not downloaded; run python -m tools.fetch_sample_baks "
            f"--only {filename}"
        )

    report = extract_bak_to_delta(path, tmp_path)

    assert report.extracted, f"{filename}: no tables were extracted"
    skipped = {t.name: t.skip_reason for t in report.skipped}
    expected = VERIFIED.get(filename)
    allowed_skips = expected.skipped if expected is not None else 0
    if len(skipped) > allowed_skips:
        unexpected = dict(list(skipped.items())[allowed_skips:])
        assert False, (
            f"{filename}: {len(skipped)} tables skipped "
            f"(allowed {allowed_skips}); unexpected: {unexpected}"
        )

    if expected is not None and expected.tables is not None:
        assert len(report.extracted) == expected.tables, (
            f"{filename}: extracted {len(report.extracted)} tables, "
            f"expected {expected.tables}"
        )
    if expected is not None and expected.rows is not None:
        assert report.total_rows == expected.rows, (
            f"{filename}: extracted {report.total_rows} rows, "
            f"expected {expected.rows}"
        )


@pytest.mark.sample
@pytest.mark.parametrize("filename", ["AdventureWorksLT2012.bak", "BaseballData.bak"])
def test_realworld_catalog_recovers_expected_user_tables(filename: str) -> None:
    """Catalog traversal must recover all user tables from older real-world backups."""
    path = _sample_path(filename)
    if path is None:
        pytest.skip(
            f"{filename} not downloaded; run python -m tools.fetch_sample_baks "
            f"--only {filename}"
        )
    expected = VERIFIED[filename]

    schema = recover_schema(PageStore.from_bak(path))

    assert expected.tables is not None
    assert len(schema.tables) == expected.tables


@pytest.mark.sample
def test_chinook_id_pk_uses_first_backup_set() -> None:
    """Chinook-id-pk.bak contains two backup sets; default restore uses FILE=1."""
    path = _sample_path("Chinook-id-pk.bak")
    if path is None:
        pytest.skip(
            "Chinook-id-pk.bak not downloaded; run python -m tools.fetch_sample_baks "
            "--only Chinook-id-pk.bak"
        )

    store = PageStore.from_bak(path)
    table = next(t for t in recover_schema(store).tables if t.name == "Employee")
    employee_1 = next(r for r in read_table_rows(store, table) if r["Id"] == 1)

    assert employee_1["ReportsTo"] is None
