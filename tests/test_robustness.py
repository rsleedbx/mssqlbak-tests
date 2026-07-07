"""Robustness / inspect-and-skip tests + coverage-doc guard.

Verifies the skip contract: every supported table extracts, every unsupported
one is detected (heap, ROW/PAGE compression, multi-file, partition, undecodable
type) and skipped with a reason, and no single table can abort the run.
Columnstore (cmprlevel=3) is now supported via the segment decoder.
Also keeps ``docs/ROBUSTNESS_COVERAGE.md`` in sync.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.extract import extract_bak_to_delta
from mssqlbak.inspect import classify_table, recover_object_inventory
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows
from tools.robustness_coverage import DOC_PATH, build_report


@pytest.mark.fixture
def test_robustness_doc_is_current(fixture_bak_constraints: Path) -> None:
    expected = build_report()
    actual = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    assert actual == expected, (
        "docs/ROBUSTNESS_COVERAGE.md is stale; regenerate with "
        "`python -m tools.robustness_coverage`"
    )


# --- object inventory ------------------------------------------------------
@pytest.mark.fixture
def test_inventory_splits_user_and_system(fixture_bak_constraints: Path) -> None:
    inv = recover_object_inventory(PageStore.from_bak(fixture_bak_constraints))
    user = [o for o in inv if not o.is_system]
    # The user objects are our cc_ tables and their constraints; system objects
    # (sys / INFORMATION_SCHEMA schemas) vastly outnumber them.
    assert {o.type_label for o in user} >= {"table", "primary_key", "foreign_key"}
    assert all(o.schema_id not in (3, 4) for o in user)
    assert len(inv) - len(user) > len(user)  # mostly system objects


@pytest.mark.fixture
def test_inventory_finds_programmability_objects(fixture_bak_constraints: Path) -> None:
    """Views/procs/functions are present in the backup and reported (not data)."""
    inv = recover_object_inventory(PageStore.from_bak(fixture_bak_constraints))
    labels = {o.type_label for o in inv}
    assert {"view", "stored_procedure", "scalar_function"} <= labels


# --- table classification --------------------------------------------------
@pytest.mark.fixture
def test_classify_heap_supported(fixture_bak_constraints: Path) -> None:
    store = PageStore.from_bak(fixture_bak_constraints)
    tables = {t.name: t for t in recover_schema(store).tables}
    heap = tables["cc_pk_nonclustered"]
    assert heap.index_id == 0  # nonclustered PK leaves a heap
    # Heaps are now supported (walked via the IAM bitmap) and read their rows.
    assert classify_table(heap).supported
    assert sum(1 for _ in read_table_rows(store, heap)) > 0
    assert classify_table(tables["cc_pk"]).supported


@pytest.mark.fixture
def test_classify_compression(fixture_bak_datacompression: Path) -> None:
    tables = {t.name: t for t in recover_schema(PageStore.from_bak(fixture_bak_datacompression)).tables}
    assert classify_table(tables["cmp_none"]).supported
    # ROW and PAGE compression over int/varchar columns are read via the CD path
    # (PAGE adds a per-page dictionary/anchor); columnstore is read via the
    # segment decoder (enc=1/2/3/4; enc=5 raw-bytes columns return None).
    assert classify_table(tables["cmp_row"]).supported
    assert classify_table(tables["cmp_page"]).supported
    assert classify_table(tables["cmp_columnstore"]).supported


@pytest.mark.fixture
def test_compression_values(fixture_bak_datacompression: Path) -> None:
    """ROW/PAGE-compressed rows decode to exactly the same values as the baseline.

    ``cmp_none``, ``cmp_row`` and ``cmp_page`` hold the identical 1000 rows over a
    wide column set -- ``int``, ``varchar``, Unicode (``nvarchar``/``nchar``,
    SCSU-compressed, incl. a Cyrillic case), ``decimal``/``numeric`` (vardecimal),
    and the temporal family (``datetime``/``datetime2``/``date``/``time``/
    ``datetimeoffset``).  Compression only changes the physical encoding, so every
    decoded value -- across excess-encoded integers, the SCSU expander, vardecimal
    bit-packing, the PAGE dictionary and the column-prefix anchor -- must match the
    uncompressed baseline cell-for-cell.
    """
    from tools.compressionmatrix import ROW_COUNT as _COMPRESSION_ROW_COUNT
    store = PageStore.from_bak(fixture_bak_datacompression)
    tables = {t.name: t for t in recover_schema(store).tables}
    baseline = {r["id"]: r for r in read_table_rows(store, tables["cmp_none"])}
    assert len(baseline) == _COMPRESSION_ROW_COUNT
    # A Cyrillic nvarchar row proves the SCSU dynamic-window path round-trips.
    assert baseline[5]["nm"] == "\u041f\u0440\u0438\u0432\u0435\u0442"
    for name in ("cmp_row", "cmp_page"):
        rows = {r["id"]: r for r in read_table_rows(store, tables[name])}
        assert rows == baseline, name


@pytest.mark.fixture
def test_cmprlevel_layout_sane(fixture_bak_datacompression: Path) -> None:
    """The sysrowsets layout extension reads the right field: none=0,row=1,page=2."""
    tables = {t.name: t for t in recover_schema(PageStore.from_bak(fixture_bak_datacompression)).tables}
    assert tables["cmp_none"].compression == 0
    assert tables["cmp_row"].compression == 1
    assert tables["cmp_page"].compression == 2


@pytest.mark.fixture
def test_columnstore_archive_decodes(fixture_bak_datacompression: Path) -> None:
    """Columnstore ARCHIVE (cmprlevel=4, XPRESS) segments decode correctly.

    ``cmp_columnstore_archive`` is a CCI with ``DATA_COMPRESSION =
    COLUMNSTORE_ARCHIVE`` (``sys.partitions.data_compression=4``).  Archival
    columnstore uses XPRESS compression on column segments instead of no
    compression.  The existing segment reader already calls ``_xpress_decompress``
    whenever ``uncompressed_size != compressed_size``, so both cmprlevel=3 and
    cmprlevel=4 share the same code path.

    1 000 rows are inserted with the same formula as the baseline tables.
    Every 7th row has ``name=NULL``.
    """
    from tools.compressionmatrix import ROW_COUNT as _COMPRESSION_ROW_COUNT
    store = PageStore.from_bak(fixture_bak_datacompression)
    tables = {t.name: t for t in recover_schema(store).tables}
    assert "cmp_columnstore_archive" in tables
    t = tables["cmp_columnstore_archive"]
    assert t.compression == 4
    rows = {r["id"]: r for r in read_table_rows(store, t)}
    assert len(rows) == _COMPRESSION_ROW_COUNT
    assert rows[1]["nm"] == "name1"   # nvarchar column; 'name' (varchar) stores 'val1'
    assert rows[7]["nm"] is None      # every 7th row has NULL nm
    assert rows[1]["amount"] is not None


# --- resilient extraction --------------------------------------------------
@pytest.mark.fixture
def test_extract_does_not_abort_on_unsupported(fixture_bak_datacompression: Path) -> None:
    """Unsupported tables must not stop the others from extracting."""
    report = extract_bak_to_delta(fixture_bak_datacompression, tempfile.mkdtemp())
    extracted = {r.name for r in report.extracted}
    # Columnstore is now supported alongside ROW, PAGE, and uncompressed.
    assert {"cmp_none", "cmp_row", "cmp_page", "cmp_columnstore"} <= extracted
    assert report.total_rows > 0


@pytest.mark.fixture
def test_extract_reads_heap_table(fixture_bak_constraints: Path) -> None:
    """The nonclustered-PK heap is now extracted alongside the clustered tables."""
    report = extract_bak_to_delta(fixture_bak_constraints, tempfile.mkdtemp())
    extracted = {r.name for r in report.extracted}
    assert {"cc_pk", "cc_pk_nonclustered", "cc_fk_child", "cc_unique_index"} <= extracted


@pytest.mark.fixture
def test_extract_reports_compression_skips(fixture_bak_datacompression: Path) -> None:
    from tools.compressionmatrix import ROW_COUNT as _COMPRESSION_ROW_COUNT
    report = extract_bak_to_delta(fixture_bak_datacompression, tempfile.mkdtemp())
    by_name = {r.name: r for r in report.tables}
    assert by_name["cmp_none"].extracted and by_name["cmp_none"].rows == _COMPRESSION_ROW_COUNT
    # ROW and PAGE are read via the CD path; columnstore via the segment decoder.
    assert by_name["cmp_row"].extracted and by_name["cmp_row"].rows == _COMPRESSION_ROW_COUNT
    assert by_name["cmp_page"].extracted and by_name["cmp_page"].rows == _COMPRESSION_ROW_COUNT
    assert by_name["cmp_columnstore"].extracted and by_name["cmp_columnstore"].rows == _COMPRESSION_ROW_COUNT


@pytest.mark.fixture
def test_clr_udt_under_compression(fixture_bak_geo: Path) -> None:
    """geography / geometry / hierarchyid decode correctly under ROW and PAGE compression.

    ``LocationsRow`` (ROW-compressed) and ``LocationsNone`` (uncompressed) share
    the same schema and rows; they must round-trip identically.  ``Locations``
    (PAGE-compressed) is a superset (adds ``geom``, 5 rows); verified separately.
    """
    store = PageStore.from_bak(fixture_bak_geo)
    tables = {t.name: t for t in recover_schema(store).tables}
    # ROW vs uncompressed: identical schema and rows.
    baseline = {r["id"]: r for r in read_table_rows(store, tables["LocationsNone"])}
    row_rows = {r["id"]: r for r in read_table_rows(store, tables["LocationsRow"])}
    assert row_rows == baseline, "LocationsRow"
    # PAGE: 5 rows, extra geom column -- check WKT and NULL values.
    page_rows = {r["id"]: r for r in read_table_rows(store, tables["Locations"])}
    assert len(page_rows) == 5
    assert page_rows[1]["pt"] == "POINT (-74.006 40.7128)"   # New York (geography)
    assert page_rows[1]["geom"] == "POINT (0 0)"             # geometry
    assert page_rows[1]["hid"] == "/"                         # hierarchyid root
    assert page_rows[4]["pt"] is None                         # NULL geography
    assert page_rows[5]["hid"] == "/1/1/"                    # hierarchyid child
    # ROW spot-check.
    assert baseline[1]["pt"] == "POINT (2.3522 48.8566)"    # Paris
    assert baseline[1]["hid"] == "/"
    assert baseline[3]["pt"] is None


@pytest.mark.fixture
def test_spatial_v2_and_zm_roundtrip(fixture_bak_geo: Path) -> None:
    """Version-2 curve types and Z/M coordinates decode correctly end-to-end.

    SpatialCurves: CircularString, CompoundCurve, CurvePolygon, FullGlobe.
    SpatialZM: POINT/LINESTRING/POLYGON with Z and ZM coordinates.
    SpatialLob: large geometry (15 KB) stored off-row as LOB.
    """
    store = PageStore.from_bak(fixture_bak_geo)
    tables = {t.name: t for t in recover_schema(store).tables}

    # --- Version-2 curve types ---
    curves = {r["id"]: r for r in read_table_rows(store, tables["SpatialCurves"])}
    assert curves[1]["geom"] == "CIRCULARSTRING (0 0, 1 1, 2 0)"
    assert curves[2]["geom"] == "COMPOUNDCURVE (CIRCULARSTRING (0 0, 1 1, 2 0), (2 0, 3 0))"
    assert curves[3]["geom"] == "CURVEPOLYGON (CIRCULARSTRING (0 0, 2 2, 4 0, 2 -2, 0 0))"
    assert curves[4]["geog"] == "FULLGLOBE"
    assert curves[5]["geom"] is None

    # --- Z and ZM coordinates ---
    zm = {r["id"]: r for r in read_table_rows(store, tables["SpatialZM"])}
    assert zm[1]["geom"] == "POINT (3 4 5)"
    assert zm[2]["geom"] == "LINESTRING (0 0 1, 1 1 2, 2 4 3)"
    assert zm[3]["geom"] == "POLYGON ((0 0 1, 4 0 2, 4 4 3, 0 4 4, 0 0 1))"
    assert zm[4]["geom"] == "POINT (3 4 5 6)"
    assert zm[5]["geom"] is None

    # --- Large spatial LOB (15 KB, stored off-row) ---
    lob = {r["id"]: r for r in read_table_rows(store, tables["SpatialLob"])}
    large_wkt = lob[1]["geom"]
    assert large_wkt is not None
    assert large_wkt.startswith("MULTIPOINT (")
    assert "(499 499)" in large_wkt  # last point confirms full stitching
    assert lob[2]["geom"] == "POINT (1 2)"


@pytest.mark.fixture
def test_geography_lob_stitches(fixture_bak_geo: Path) -> None:
    """Large geography (15 KB) stored off-row is fully stitched via LOB pages.

    spatial_lob_test id=4 is a 500-point MULTIPOINT geography whose on-disk
    binary is ~15 KB — well above the 8 KB in-row limit.  Confirming the last
    point proves the entire LOB chain was traversed.
    """
    store = PageStore.from_bak(fixture_bak_geo)
    tables = {t.name: t for t in recover_schema(store).tables}

    rows = {r["id"]: r for r in read_table_rows(store, tables["spatial_lob_test"])}
    wkt = rows[4]["geog"]
    assert wkt is not None
    assert wkt.startswith("MULTIPOINT (")
    # 500 points span lon/lat 0.0 … 49.9 in 0.1 steps
    assert wkt.count("(") == 501  # 1 outer + 500 per-point parens
    assert "(49.9 49.9)" in wkt   # last point confirms full LOB stitching


@pytest.mark.fixture
def test_ndf_secondary_file_rows_decoded(fixture_bak_ndf: Path) -> None:
    """Rows from a secondary NDF (file_id=3) are returned alongside primary rows.

    NdfCoverage has two data files:
      - primary MDF   (file_id=1): primary_tbl   — 10 rows
      - secondary NDF (file_id=3): secondary_tbl — 10 rows

    This confirms that PageStore.from_bak ingests both image streams and that
    catalog recovery + row decoding traverse file_id=3 pages correctly.
    """
    store = PageStore.from_bak(fixture_bak_ndf)
    # The store must expose both data file IDs (log file has no data pages).
    assert 1 in store.available_files, "primary MDF (file_id=1) missing"
    secondary_ids = store.available_files - {1}
    assert secondary_ids, f"no secondary NDF found (available_files={store.available_files})"

    tables = {t.name: t for t in recover_schema(store).tables}
    assert "primary_tbl" in tables
    assert "secondary_tbl" in tables

    primary = list(read_table_rows(store, tables["primary_tbl"]))
    secondary = list(read_table_rows(store, tables["secondary_tbl"]))

    assert len(primary) == 10
    assert len(secondary) == 10
    assert primary[0]["val"] == "primary_row_1"
    assert secondary[0]["val"] == "secondary_row_1"
