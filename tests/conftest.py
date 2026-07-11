"""Shared test fixtures and markers."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Transparent decompression of *.bak.zst fixture sidecars
# ---------------------------------------------------------------------------
# Some large fixtures are stored compressed (zstd level 19) to keep them under
# GitHub's 100 MB per-file limit.  When a *.bak.zst exists but the raw *.bak
# does not, decompress it in-place so downstream code sees a normal .bak path.
# This runs at conftest import time — before test modules are collected — so
# dynamically-discovered cases in test_stats._stats_cases() find the raw file.

def _expand_zst_fixtures(*dirs: Path) -> None:
    """Decompress *.bak.zst -> *.bak for any compressed fixture sidecar."""
    try:
        import zstandard as zstd  # optional; only needed when .zst sidecars exist
    except ImportError:
        return
    dctx = zstd.ZstdDecompressor()
    for d in dirs:
        if not d.is_dir():
            continue
        for zst_path in sorted(d.glob("*.bak.zst")):
            bak_path = zst_path.with_suffix("")  # strip .zst -> *.bak
            if not bak_path.exists():
                with zst_path.open("rb") as src, bak_path.open("wb") as dst:
                    dctx.copy_stream(src, dst)


_TESTS_DIR = Path(__file__).parent
_expand_zst_fixtures(*_TESTS_DIR.glob("fixtures_*"))

# ---------------------------------------------------------------------------

# All fixture paths resolve relative to this directory.  Set FIXTURE_DIR to
# point at a different version-specific fixture tree (e.g. tests/fixtures_2019).
_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))

# SS2025-specific fixture directory (VECTOR, native JSON).
_FIXTURE_DIR_2025 = Path(__file__).parent / "fixtures_2025"

FIXTURE_BAK = _FIXTURE_DIR / "typecoverage_full.bak"
FIXTURE_BACPAC = _FIXTURE_DIR / "typecoverage.bacpac"
FIXTURE_BAK_COMPRESSED = (
    _FIXTURE_DIR / "typecoverage_full_compressed.bak"
)
FIXTURE_BAK_CONSTRAINTS = (
    _FIXTURE_DIR / "constraintcoverage_full.bak"
)
# Data-compression matrix (ROW/PAGE/columnstore rowsets) -- distinct from the
# backup-compressed (MS_XPRESS) fixture above.
FIXTURE_BAK_DATACOMPRESSION = (
    _FIXTURE_DIR / "compressioncoverage_full.bak"
)
# Persisted vs non-persisted computed columns.
FIXTURE_BAK_COMPUTED = (
    _FIXTURE_DIR / "computedcoverage_full.bak"
)
# Binary-XML construct coverage (untyped xml documents).
FIXTURE_BAK_XML = (
    _FIXTURE_DIR / "xmlcoverage_full.bak"
)
# Geometry/geography/hierarchyid under ROW and PAGE compression.
FIXTURE_BAK_GEO = (
    _FIXTURE_DIR / "geocoverage_full.bak"
)


FIXTURE_BAK_TABLETYPE = (
    _FIXTURE_DIR / "tabletypecoverage_full.bak"
)
FIXTURE_BAK_TABLETYPE_DIFF = (
    _FIXTURE_DIR / "tabletypecoverage_diff.bak"
)
# Large-row-group boundary-value fixture (1 200 rows per table, forces enc=4).
FIXTURE_BAK_BOUNDARY = (
    _FIXTURE_DIR / "boundarycoverage_full.bak"
)
# Feature-coverage fixture: temporal tables, COMPRESS(), UTF-8 collation, NCCI.
FIXTURE_BAK_FEATURE = (
    _FIXTURE_DIR / "featurecoverage_full.bak"
)
# V13 is_hidden probe fixture: temporal tables with HIDDEN vs non-HIDDEN period columns.
FIXTURE_BAK_TEMPORAL_HIDDEN = (
    _FIXTURE_DIR / "temporal_hidden_full.bak"
)
# PAGE-compression CI anchor/dictionary decode fixture (0x02 anchor-only CI).
FIXTURE_BAK_PAGECOMP_ANCHOR = (
    _FIXTURE_DIR / "pagecomp_anchor_full.bak"
)
FIXTURE_BAK_PAGECOMP_LONG_PREFIX = (
    _FIXTURE_DIR / "pagecomp_long_prefix_full.bak"
)
# Multi-file (primary MDF + secondary NDF) database backup.
FIXTURE_BAK_NDF = (
    _FIXTURE_DIR / "ndfcoverage_full.bak"
)
# ARCHIVE columnstore null-encoding probe (Gap 5).
FIXTURE_BAK_ARCHIVE_NULL = (
    _FIXTURE_DIR / "archivenull_full.bak"
)
# Partitioned columnstore ARCHIVE probe — four tables covering single-partition,
# all-partition, mixed-partition, and round-trip REBUILD scenarios (Gap 5 supplement).
FIXTURE_BAK_ARCHIVE_COLUMNSTORE_PARTITION = (
    _FIXTURE_DIR / "archive_columnstore_partition_full.bak"
)
# Gap I-1: all dictionary-encoded types under COLUMNSTORE_ARCHIVE.
# Seven tables (CHAR/VARCHAR/NCHAR/NVARCHAR/BINARY/VARBINARY/UNIQUEIDENTIFIER),
# each with 35,000 rows so enc_type=5 (multi-sub-block) is triggered for every type.
# First fixture built with the new SqlDialect / EngineAdapter architecture.
FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES = (
    _FIXTURE_DIR / "archive_columnstore_types_full.bak"
)
# Part II: random-order variant — same schema/assertions, INSERT ORDER BY NEWID()
FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES_RANDOM = (
    _FIXTURE_DIR / "archive_columnstore_types_random_full.bak"
)
# PFOR exercise: two tables (plain COLUMNSTORE + COLUMNSTORE_ARCHIVE) of INT
# columns engineered to emit Patched-FOR exceptions (sparse / deep / compulsory /
# dense outliers).  Stresses the bit-pack exception-walk path that monotonic
# fixtures never reach.
FIXTURE_BAK_PFOR_COLUMNSTORE = (
    _FIXTURE_DIR / "pfor_columnstore_full.bak"
)
# Part II: random-order variant of PFOR
FIXTURE_BAK_PFOR_COLUMNSTORE_RANDOM = (
    _FIXTURE_DIR / "pfor_columnstore_random_full.bak"
)
# CCI bit-pack probes: controlled known-value (modK = pk % K) enc=2 dictionary
# columns that crack the per-segment frame-of-reference (FOR) base layout.
FIXTURE_BAK_CCI_BITPACK_PROBE = (
    _FIXTURE_DIR / "cci_bitpack_probe_full.bak"
)
FIXTURE_BAK_CCI_BITPACK_PROBE_BIGINT = (
    _FIXTURE_DIR / "cci_bitpack_probe_bigint_full.bak"
)
FIXTURE_BAK_CCI_BITPACK_PROBE_HIGHBASE = (
    _FIXTURE_DIR / "cci_bitpack_probe_highbase_full.bak"
)
# TODO-F1: small ARCHIVE CHAR(10) table (~5000 rows) whose enc=5 blob fits in a
# single 64KB XPRESS chunk — exercises the chunk-0-only decode path that all the
# ≥35,000-row enc=5 fixtures never reach.
FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK = (
    _FIXTURE_DIR / "archive_single_chunk_full.bak"
)
# Part II: random-order variant of single-chunk
FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK_RANDOM = (
    _FIXTURE_DIR / "archive_single_chunk_random_full.bak"
)
# Heap table with xml/varchar(MAX)/varbinary(MAX) LOBs (Gap 10 regression guard).
FIXTURE_BAK_XML_HEAP = (
    _FIXTURE_DIR / "xmlheap_full.bak"
)
# Gap D-1: sparse columns + column set (sparse vector record layout).
FIXTURE_BAK_SPARSE = (
    _FIXTURE_DIR / "sparse_full.bak"
)
# Gap H-1: forwarded records on heap (forwarding stub + overflow page).
FIXTURE_BAK_FORWARDED_RECORDS = (
    _FIXTURE_DIR / "forwarded_records_full.bak"
)
# Gap H-2: ghost (deleted) records on heap (ghost status bit must be checked).
FIXTURE_BAK_GHOST_RECORDS = (
    _FIXTURE_DIR / "ghost_records_full.bak"
)
# Gap C-3: multiple small CCI compressed rowgroups.
FIXTURE_BAK_MULTI_ROWGROUP = (
    _FIXTURE_DIR / "multi_rowgroup_full.bak"
)
# Regression: bounded VARCHAR CCI string dictionaries from real-world TPC-BB.
FIXTURE_BAK_CCI_STRING_DICT_REGRESSION = (
    _FIXTURE_DIR / "cci_string_dict_regression_full.bak"
)
# Gap H-3: max-row-width — CHAR(8000), one row per page.
FIXTURE_BAK_MAX_ROW_WIDTH = (
    _FIXTURE_DIR / "max_row_width_full.bak"
)
# Gap G-2: surrogate pairs in nvarchar (UTF-16 surrogate-pair code points).
FIXTURE_BAK_SURROGATE_PAIRS = (
    _FIXTURE_DIR / "surrogate_pairs_full.bak"
)
# Gap H-4: high slot density — 100,000 TINYINT rows (many slots per page).
FIXTURE_BAK_HIGH_SLOT_DENSITY = (
    _FIXTURE_DIR / "high_slot_density_full.bak"
)
# Gap C-9: CCI PARTITION SWITCH — rowgroup ownership reassigned via metadata-only switch.
FIXTURE_BAK_CCI_SWITCH = (
    _FIXTURE_DIR / "cci_switch_full.bak"
)
# Gap C-10: CCI REORGANIZE + deleted-row bitmap.
FIXTURE_BAK_CCI_REORGANIZE = (
    _FIXTURE_DIR / "cci_reorganize_full.bak"
)
# Gap E-1: nonclustered covering index with INCLUDE columns.
FIXTURE_BAK_COVERING_INDEX = (
    _FIXTURE_DIR / "covering_index_full.bak"
)
# Gap D-2: sql_variant per-value type extraction.
FIXTURE_BAK_SQL_VARIANT_EXTRACT = (
    _FIXTURE_DIR / "sql_variant_extract_full.bak"
)
# Gap C-4: filtered NCCI (WHERE clause) — base table must return all rows, not just filtered set.
FIXTURE_BAK_FILTERED_NCCI = (
    _FIXTURE_DIR / "filtered_ncci_full.bak"
)
# Gap C-5: NCCI on heap — RID-locator column must not contaminate data extraction.
FIXTURE_BAK_NCCI_HEAP = (
    _FIXTURE_DIR / "ncci_heap_full.bak"
)
# identity-coverage: all 6 SQL Server IDENTITY-capable types decoded correctly.
FIXTURE_BAK_IDENTITY_COVERAGE = (
    _FIXTURE_DIR / "identity_coverage_full.bak"
)
# Gap D-3: rowversion/timestamp — 8-byte big-endian bytes, monotonically increasing.
FIXTURE_BAK_ROWVERSION_EXTRACT = (
    _FIXTURE_DIR / "rowversion_extract_full.bak"
)
# Gap D-4: hierarchyid — raw varbinary bytes of correct length per path.
FIXTURE_BAK_HIERARCHYID_EXTRACT = (
    _FIXTURE_DIR / "hierarchyid_extract_full.bak"
)
# Gap C-11: non-persisted computed columns in CCI — absent from segments, no crash.
FIXTURE_BAK_CCI_COMPUTED = (
    _FIXTURE_DIR / "cci_computed_full.bak"
)
# Gap C-12: CCI + B-tree NC indexes on same table — NC pages must not contaminate CCI read.
FIXTURE_BAK_CCI_BTREE_NCI = (
    _FIXTURE_DIR / "cci_btree_nci_full.bak"
)
# Gap C-7: ordered CCI (SS2022+ ORDER clause) — same segment format, metadata accuracy.
FIXTURE_BAK_ORDERED_CCI = (
    _FIXTURE_DIR / "ordered_cci_full.bak"
)
# Gap A-5: non-default BLOCKSIZE backup — BLOCKSIZE=4096, auto-detected by reader.
FIXTURE_BAK_BACKUP_BLOCKSIZE = (
    _FIXTURE_DIR / "backup_blocksize_full.bak"
)
# Gap C-8: CCI string/binary min-max segment metadata (SS2022+) — NULL-minmax path.
FIXTURE_BAK_CCI_STRING_MINMAX = (
    _FIXTURE_DIR / "cci_string_minmax_full.bak"
)
# Regular-CCI enc=5 CHAR with >64 KiB pool — guards the ARCHIVE-probe false positive
# that misrouted ordinary CCI CHAR segments to the archive decoder (all-NULL).
FIXTURE_BAK_CCI_ENC5_LARGEPOOL = (
    _FIXTURE_DIR / "cci_enc5_largepool_full.bak"
)
# Gap E-3: XML index — internal node table must be skipped by recover_schema.
FIXTURE_BAK_XML_INDEX = (
    _FIXTURE_DIR / "xml_index_full.bak"
)
# Gap E-4: spatial index — internal tessellation table must be skipped by recover_schema.
FIXTURE_BAK_SPATIAL_INDEX = (
    _FIXTURE_DIR / "spatial_index_full.bak"
)
# Cell gap: scalar user-defined alias types such as Flag and NameStyle.
FIXTURE_BAK_ALIAS_TYPES = (
    _FIXTURE_DIR / "alias_types_full.bak"
)
# Cell gap: XML schema collection typed XML values.
FIXTURE_BAK_TYPED_XML = (
    _FIXTURE_DIR / "typed_xml_full.bak"
)
# Cell gap: exact geometry/geography WKT values.
FIXTURE_BAK_SPATIAL_EDGE = (
    _FIXTURE_DIR / "spatial_edge_full.bak"
)
# Cell gap: rowstore float/real extreme values.
FIXTURE_BAK_FLOAT_EXTREME = (
    _FIXTURE_DIR / "float_extreme_full.bak"
)
# Cell gap: rowstore image and max-type LOB payloads.
FIXTURE_BAK_ROWSTORE_LOB_IMAGE = (
    _FIXTURE_DIR / "rowstore_lob_image_full.bak"
)
# Real-world regression: rowstore HTML/JSON/Unicode markup LOB payloads.
FIXTURE_BAK_ROWSTORE_LOB_MARKUP = (
    _FIXTURE_DIR / "rowstore_lob_markup_full.bak"
)
# Real-world regression: binary/hash PII-shaped rowstore cells.
FIXTURE_BAK_ROWSTORE_HASH_PII = (
    _FIXTURE_DIR / "rowstore_hash_pii_full.bak"
)
# Regression: nvarchar(max) values whose first UTF-16LE byte is 0x21.
FIXTURE_BAK_NVARCHAR_MAX_U21 = (
    _FIXTURE_DIR / "nvarchar_max_u21_full.bak"
)
# Regression: ROW-compressed nvarchar SCSU vs UTF-16LE heuristic.
FIXTURE_BAK_COMPRESSED_NVARCHAR = (
    _FIXTURE_DIR / "compressed_nvarchar_full.bak"
)
# Regression: TORN_PAGE_DETECTION sector-bit restoration.
FIXTURE_BAK_TORN_PAGE = (
    _FIXTURE_DIR / "torn_page_full.bak"
)
# Gap D-5: VECTOR column type (SS2025 only) — stored in fixtures_2025.
FIXTURE_BAK_VECTOR = (
    _FIXTURE_DIR_2025 / "vector_full.bak"
)
# Gap D-6: native JSON column type (SS2025 only) — stored in fixtures_2025.
FIXTURE_BAK_NATIVE_JSON = (
    _FIXTURE_DIR_2025 / "native_json_full.bak"
)
# Gap G-1: UTF-8 collation varchar (SS2019+ only).
FIXTURE_BAK_UTF8_COLLATION = (
    _FIXTURE_DIR / "utf8_collation_full.bak"
)
# Gap K-1: CCI with 1,200 rows — exercises real segment encoding paths (all versions).
FIXTURE_BAK_TABLETYPE_CCI_LARGE = (
    _FIXTURE_DIR / "tabletype_cci_large_full.bak"
)
# Gap C-1: CCI delta store — cs_mixed (compressed + open delta) + cs_delta_only (delta only).
FIXTURE_BAK_DELTA_ROWGROUP = (
    _FIXTURE_DIR / "delta_rowgroup_full.bak"
)
# Gap K-3: one-table-per-type CCI (1,200 rows) — char/varbinary/bit/binary/uuid.
# Gap C-6: CCI tables with VARCHAR(MAX), NVARCHAR(MAX), VARBINARY(MAX) columns
# (1,200 rows each; varint-encoded dictionary entries; short/medium/long values).
FIXTURE_BAK_CCI_LOB = (
    _FIXTURE_DIR / "cci_lob_full.bak"
)
FIXTURE_BAK_CCI_TYPES_LARGE = (
    _FIXTURE_DIR / "cci_types_large_full.bak"
)
# Gap K-5: NCCI type coverage — 19 rowstore tables each with a NONCLUSTERED COLUMNSTORE INDEX.
FIXTURE_BAK_NCCI_TYPES = (
    _FIXTURE_DIR / "ncci_types_full.bak"
)
# Real-world regression: taxi/rate/cost numeric digest values across rowstore/NCCI/CCI.
FIXTURE_BAK_REALWORLD_NUMERIC_DIGEST = (
    _FIXTURE_DIR / "realworld_numeric_digest_full.bak"
)
# Real-world regression: richer memory-optimized XTP schemas.
FIXTURE_BAK_XTP_RICH = (
    _FIXTURE_DIR / "xtp_rich_full.bak"
)
# Large compressed XTP fixture that flushes checkpoint DATA chunks and induces
# boundary-straddle rows (drives the checkpoint DATA-file decoder).
FIXTURE_BAK_XTP_CHECKPOINT = (
    _FIXTURE_DIR / "xtp_checkpoint_straddle_full.bak"
)
# Confidence-only corrupt metadata fixture; intentionally has no stats sidecar.
FIXTURE_BAK_CORRUPT_METADATA_CONFIDENCE = (
    _FIXTURE_DIR / "corrupt_metadata_confidence_full.bak"
)
# Gap F-1: TDE-encrypted database — mssqlbak must raise EncryptedBackupError.
FIXTURE_BAK_TDE = (
    _FIXTURE_DIR / "tde_full.bak"
)
# Gap K-2: datetime/bit/decimal boundary values in enc=4 CCI segments.
FIXTURE_BAK_BOUNDARY_DATETIME = (
    _FIXTURE_DIR / "boundarycoverage_datetime_full.bak"
)
# Gap G-3: per-column collation override — Latin1/Greek/Hebrew/UTF-8 varchar columns.
FIXTURE_BAK_MIXED_COLLATION = (
    _FIXTURE_DIR / "mixed_collation_full.bak"
)
# Extended CCI bug-trigger tables — int/varchar50/char10_varied/binary4/nvarchar50_sparse.
FIXTURE_BAK_CCI_EXTENDED = (
    _FIXTURE_DIR / "cci_extended_full.bak"
)
# Row-size and LOB-page boundary coverage:
#   rb_overflow (in-row vs ROW_OVERFLOW at ±2 of 8060 bytes)
#   rb_lob      (single- vs two-LOB-page at ±2 of 8096 bytes)
#   rb_page_fill (3 full data pages of fixed-width CHAR(100) rows)
FIXTURE_BAK_ROWBOUNDARY = (
    _FIXTURE_DIR / "rowboundary_full.bak"
)
# F1: VARBINARY(16) micro — 7 hand-chosen rows to inspect Format C pool/index (M1/M2/M3).
# Three tables: cci_varbinary_micro (7), cci_varbinary_micro_nullonly (21),
# cci_varbinary_micro_1byte (20).
FIXTURE_BAK_CCI_VARBINARY_MICRO = (
    _FIXTURE_DIR / "cci_varbinary_micro_full.bak"
)
# F4: BINARY(8) + VARBINARY(8) side-by-side in the same row group (1,200 rows).
FIXTURE_BAK_CCI_BINARY_VARBINARY_COMPARE = (
    _FIXTURE_DIR / "cci_binary_varbinary_compare_full.bak"
)
# F2+F3+F5: maxwidth/narrowmax/small-rowgroup probes for Format C item_size + boundary.
#   cci_varbinary_maxwidth       — VARBINARY(16) all-16-byte values, 1,200 rows (F2)
#   cci_varbinary_narrowmax      — VARBINARY(4), 1,200 rows (F3)
#   cci_varbinary_small_rowgroup — VARBINARY(16), 128 rows, no NULLs (F5)
FIXTURE_BAK_CCI_VARBINARY_PROBE = (
    _FIXTURE_DIR / "cci_varbinary_probe_full.bak"
)
# Record-layout matrix (PK position, column-count boundaries).
FIXTURE_BAK_LAYOUT = (
    _FIXTURE_DIR / "layoutcoverage_full.bak"
)
FIXTURE_BAK_LAYOUT_COMPRESSED = (
    _FIXTURE_DIR / "layoutcoverage_compressed.bak"
)
# Catalog version-matrix snapshots (G21).
FIXTURE_BAK_CATALOG_SS = {
    year: _FIXTURE_DIR / f"catalog_ss{year}.bak"
    for year in ("2012", "2016", "2019", "2022")
}
FIXTURE_BAK_MSSQLBAK_V1 = (
    _FIXTURE_DIR / "mssqlbak_v1_inspect.bak"
)
# Dirty / fuzzy backup investigation fixtures.
FIXTURE_BAK_DIRTY_CONCURRENT = (
    _FIXTURE_DIR / "dirtycoverage_concurrent.bak"
)
FIXTURE_BAK_DIRTY_UNCOMMITTED = (
    _FIXTURE_DIR / "dirtycoverage_uncommitted.bak"
)
FIXTURE_DIRTY_GROUND_TRUTH = (
    _FIXTURE_DIR / "dirty_ground_truth.json"
)
# DDL-during-backup fixtures (Scenarios C / D / E).
FIXTURE_BAK_DIRTY_TRUNCATE = (
    _FIXTURE_DIR / "dirtycoverage_truncate.bak"
)
FIXTURE_BAK_DIRTY_ADDCOL = (
    _FIXTURE_DIR / "dirtycoverage_addcol.bak"
)
FIXTURE_BAK_DIRTY_DROPTABLE = (
    _FIXTURE_DIR / "dirtycoverage_droptable.bak"
)
# DDL-during-backup fixtures (Scenarios F / G / H / I / J / K).
FIXTURE_BAK_DIRTY_DROPCOL = (
    _FIXTURE_DIR / "dirtycoverage_dropcol.bak"
)
FIXTURE_BAK_DIRTY_ADDNOTNULL = (
    _FIXTURE_DIR / "dirtycoverage_addnotnull.bak"
)
FIXTURE_BAK_DIRTY_ALTERCOL = (
    _FIXTURE_DIR / "dirtycoverage_altercol.bak"
)
FIXTURE_BAK_DIRTY_CREATETABLE = (
    _FIXTURE_DIR / "dirtycoverage_createtable.bak"
)
FIXTURE_BAK_DIRTY_REBUILDIDX = (
    _FIXTURE_DIR / "dirtycoverage_rebuildidx.bak"
)
FIXTURE_BAK_DIRTY_CREATEIDX = (
    _FIXTURE_DIR / "dirtycoverage_createidx.bak"
)
FIXTURE_BAK_DIRTY_DROPIDX = (
    _FIXTURE_DIR / "dirtycoverage_dropidx.bak"
)
# DML-during-backup fixtures (Scenarios L / M).
FIXTURE_BAK_DIRTY_DELETE = (
    _FIXTURE_DIR / "dirtycoverage_delete.bak"
)
FIXTURE_BAK_DIRTY_UPDATE = (
    _FIXTURE_DIR / "dirtycoverage_update.bak"
)
# Remaining untested scenarios (N / O / P / Q / R).
FIXTURE_BAK_DIRTY_ALTERCOL_REWRITE = (
    _FIXTURE_DIR / "dirtycoverage_altercol_rewrite.bak"
)
FIXTURE_BAK_DIRTY_ALTERDB = (
    _FIXTURE_DIR / "dirtycoverage_alterdb.bak"
)
FIXTURE_BAK_DIRTY_SAVEPOINT = (
    _FIXTURE_DIR / "dirtycoverage_savepoint.bak"
)
FIXTURE_BAK_DIRTY_NESTED = (
    _FIXTURE_DIR / "dirtycoverage_nested.bak"
)
FIXTURE_BAK_DIRTY_SWITCH = (
    _FIXTURE_DIR / "dirtycoverage_switch.bak"
)
# Incremental (full + 6 differential) chain.
FIXTURE_BAK_INCREMENTAL_FULL = (
    _FIXTURE_DIR / "incrementalcoverage_full.bak"
)
FIXTURE_BAK_INCREMENTAL_DIFFS = [
    _FIXTURE_DIR / f"incrementalcoverage_diff_{n:02d}.bak"
    for n in range(1, 7)
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--samples",
        action="store_true",
        default=False,
        help="Also run real-world large .bak/.bacpac benchmarks from tests/fixtures_realworld/.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "fixture: requires the generated reference .bak fixture")
    config.addinivalue_line("markers", "engine: requires a live SQL Server (podman + mssql_python)")
    config.addinivalue_line(
        "markers",
        "sample: requires a downloaded Microsoft sample .bak (python -m tools.fetch_sample_baks)",
    )
    config.addinivalue_line(
        "markers",
        "samples: real-world large .bak benchmark (opt-in via --samples flag)",
    )
    # Tiered value-correctness suites (SQLite veryquick/full/all model).
    config.addinivalue_line(
        "markers", "quick: fast offline cell/digest checks on small synthetic fixtures"
    )
    config.addinivalue_line(
        "markers", "full: all fixtures across all versions (value verification)"
    )
    config.addinivalue_line(
        "markers", "matrix: full + distribution permutations (expensive cross-product)"
    )
    config.addinivalue_line(
        "markers",
        "negative: mutation / negative-path tests (bit-flip harness, corrupt input)",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if not config.getoption("--samples", default=False):
        skip = pytest.mark.skip(reason="pass --samples to include real-world sample benchmarks")
        for item in items:
            if "samples" in item.keywords:
                item.add_marker(skip)


@pytest.fixture
def fixture_bak() -> Path:
    if not FIXTURE_BAK.exists():
        pytest.skip(f"reference fixture missing: {FIXTURE_BAK} (run tools/make_fixture.py)")
    return FIXTURE_BAK


@pytest.fixture
def fixture_bak_compressed() -> Path:
    if not FIXTURE_BAK_COMPRESSED.exists():
        pytest.skip(f"compressed reference fixture missing: {FIXTURE_BAK_COMPRESSED}")
    return FIXTURE_BAK_COMPRESSED


@pytest.fixture
def fixture_bak_layout() -> Path:
    if not FIXTURE_BAK_LAYOUT.exists():
        pytest.skip(
            f"layout fixture missing: {FIXTURE_BAK_LAYOUT} "
            "(run python -m tools.make_layout_fixture)"
        )
    return FIXTURE_BAK_LAYOUT


@pytest.fixture
def fixture_bak_constraints() -> Path:
    if not FIXTURE_BAK_CONSTRAINTS.exists():
        pytest.skip(
            f"constraint fixture missing: {FIXTURE_BAK_CONSTRAINTS} "
            "(run python -m tools.constraintmatrix)"
        )
    return FIXTURE_BAK_CONSTRAINTS


@pytest.fixture
def fixture_bak_datacompression() -> Path:
    if not FIXTURE_BAK_DATACOMPRESSION.exists():
        pytest.skip(
            f"data-compression fixture missing: {FIXTURE_BAK_DATACOMPRESSION} "
            "(run python -m tools.compressionmatrix)"
        )
    return FIXTURE_BAK_DATACOMPRESSION


@pytest.fixture
def fixture_bak_computed() -> Path:
    if not FIXTURE_BAK_COMPUTED.exists():
        pytest.skip(
            f"computed-column fixture missing: {FIXTURE_BAK_COMPUTED} "
            "(run python -m tools.computedmatrix)"
        )
    return FIXTURE_BAK_COMPUTED


@pytest.fixture
def fixture_bak_xml() -> Path:
    if not FIXTURE_BAK_XML.exists():
        pytest.skip(
            f"xml-coverage fixture missing: {FIXTURE_BAK_XML} "
            "(run python -m tools.xmlmatrix)"
        )
    return FIXTURE_BAK_XML


@pytest.fixture
def fixture_bak_geo() -> Path:
    if not FIXTURE_BAK_GEO.exists():
        pytest.skip(
            f"geo-coverage fixture missing: {FIXTURE_BAK_GEO} "
            "(run python -m tools.geomatrix)"
        )
    return FIXTURE_BAK_GEO


@pytest.fixture
def fixture_bak_tabletype() -> Path:
    if not FIXTURE_BAK_TABLETYPE.exists():
        pytest.skip(
            f"table-type coverage fixture missing: {FIXTURE_BAK_TABLETYPE} "
            "(run python tools/make_tabletype_fixture.py)"
        )
    return FIXTURE_BAK_TABLETYPE


@pytest.fixture
def fixture_bak_tabletype_diff() -> Path:
    if not FIXTURE_BAK_TABLETYPE_DIFF.exists():
        pytest.skip(
            f"table-type differential fixture missing: {FIXTURE_BAK_TABLETYPE_DIFF} "
            "(run python tools/make_tabletype_fixture.py)"
        )
    return FIXTURE_BAK_TABLETYPE_DIFF


@pytest.fixture
def fixture_bak_boundary() -> Path:
    if not FIXTURE_BAK_BOUNDARY.exists():
        pytest.skip(
            f"boundary fixture missing: {FIXTURE_BAK_BOUNDARY} "
            "(run python tools/make_boundary_fixture.py)"
        )
    return FIXTURE_BAK_BOUNDARY


@pytest.fixture(scope="session")
def fixture_bak_dirty() -> tuple[Path, Path, dict]:
    """Return (concurrent_bak, uncommitted_bak, ground_truth) for dirty-backup tests."""
    import json
    missing = [
        p for p in [
            FIXTURE_BAK_DIRTY_CONCURRENT,
            FIXTURE_BAK_DIRTY_UNCOMMITTED,
            FIXTURE_DIRTY_GROUND_TRUTH,
        ]
        if not p.exists()
    ]
    if missing:
        pytest.skip(
            f"dirty fixtures missing: {[p.name for p in missing]} "
            "(run python tools/make_dirty_fixture.py)"
        )
    gt = json.loads(FIXTURE_DIRTY_GROUND_TRUTH.read_text())
    return FIXTURE_BAK_DIRTY_CONCURRENT, FIXTURE_BAK_DIRTY_UNCOMMITTED, gt


@pytest.fixture(scope="session")
def fixture_bak_dirty_ddl() -> tuple[Path, Path, Path, dict]:
    """Return (truncate_bak, addcol_bak, droptable_bak, ground_truth) for DDL-during-backup tests.

    Scenarios C, D, and E: TRUNCATE TABLE during backup, ADD COLUMN then static
    backup, and DROP TABLE during backup.  All require the DDL fixtures produced
    by ``python tools/make_dirty_fixture.py``.
    """
    import json
    missing = [
        p for p in [
            FIXTURE_BAK_DIRTY_TRUNCATE,
            FIXTURE_BAK_DIRTY_ADDCOL,
            FIXTURE_BAK_DIRTY_DROPTABLE,
            FIXTURE_DIRTY_GROUND_TRUTH,
        ]
        if not p.exists()
    ]
    if missing:
        pytest.skip(
            f"DDL dirty fixtures missing: {[p.name for p in missing]} "
            "(run python tools/make_dirty_fixture.py)"
        )
    gt = json.loads(FIXTURE_DIRTY_GROUND_TRUTH.read_text())
    return (
        FIXTURE_BAK_DIRTY_TRUNCATE,
        FIXTURE_BAK_DIRTY_ADDCOL,
        FIXTURE_BAK_DIRTY_DROPTABLE,
        gt,
    )


@pytest.fixture(scope="session")
def fixture_bak_dirty_ddl2() -> tuple[Path, Path, Path, Path, Path, Path, Path, dict]:
    """Return 7 BAK paths + ground_truth for Scenarios F–K.

    Scenarios:
      F — DROP COLUMN, static backup
      G — ADD COLUMN NOT NULL WITH DEFAULT, static backup
      H — ALTER COLUMN (compatible type), static backup
      I — CREATE TABLE during backup
      J — ALTER INDEX REBUILD during backup
      K_create — CREATE INDEX during backup
      K_drop   — DROP INDEX during backup

    Requires fixtures from ``python tools/make_dirty_fixture.py``.
    """
    import json
    paths = [
        FIXTURE_BAK_DIRTY_DROPCOL,
        FIXTURE_BAK_DIRTY_ADDNOTNULL,
        FIXTURE_BAK_DIRTY_ALTERCOL,
        FIXTURE_BAK_DIRTY_CREATETABLE,
        FIXTURE_BAK_DIRTY_REBUILDIDX,
        FIXTURE_BAK_DIRTY_CREATEIDX,
        FIXTURE_BAK_DIRTY_DROPIDX,
        FIXTURE_DIRTY_GROUND_TRUTH,
    ]
    missing = [p for p in paths if not p.exists()]
    if missing:
        pytest.skip(
            f"DDL-2 dirty fixtures missing: {[p.name for p in missing]} "
            "(run python tools/make_dirty_fixture.py)"
        )
    gt = json.loads(FIXTURE_DIRTY_GROUND_TRUTH.read_text())
    return (
        FIXTURE_BAK_DIRTY_DROPCOL,
        FIXTURE_BAK_DIRTY_ADDNOTNULL,
        FIXTURE_BAK_DIRTY_ALTERCOL,
        FIXTURE_BAK_DIRTY_CREATETABLE,
        FIXTURE_BAK_DIRTY_REBUILDIDX,
        FIXTURE_BAK_DIRTY_CREATEIDX,
        FIXTURE_BAK_DIRTY_DROPIDX,
        gt,
    )


@pytest.fixture(scope="session")
def fixture_bak_dirty_dml() -> tuple[Path, Path, dict]:
    """Return (delete_bak, update_bak, ground_truth) for DML-during-backup tests.

    Scenarios:
      L — Uncommitted DELETE (ghost rows): backup while an open DELETE is held.
      M — Uncommitted UPDATE (in-place): backup while an open UPDATE is held.

    Requires fixtures from ``python tools/make_dirty_fixture.py``.
    """
    import json
    missing = [
        p for p in [
            FIXTURE_BAK_DIRTY_DELETE,
            FIXTURE_BAK_DIRTY_UPDATE,
            FIXTURE_DIRTY_GROUND_TRUTH,
        ]
        if not p.exists()
    ]
    if missing:
        pytest.skip(
            f"DML dirty fixtures missing: {[p.name for p in missing]} "
            "(run python tools/make_dirty_fixture.py)"
        )
    gt = json.loads(FIXTURE_DIRTY_GROUND_TRUTH.read_text())
    return FIXTURE_BAK_DIRTY_DELETE, FIXTURE_BAK_DIRTY_UPDATE, gt


@pytest.fixture(scope="session")
def fixture_bak_dirty_remaining() -> tuple[Path, Path, Path, Path, Path, dict]:
    """Return 5 BAK paths + ground_truth for Scenarios N–R.

    Scenarios:
      N — ALTER COLUMN type rewrite (NVARCHAR→VARCHAR), static backup
      O — ALTER DATABASE SET COMPATIBILITY_LEVEL during backup
      P — Savepoints (ROLLBACK TO SAVEPOINT then outer ROLLBACK)
      Q — Nested transactions (BEGIN inside BEGIN, outer ROLLBACK)
      R — ALTER TABLE SWITCH PARTITION during backup

    Requires fixtures from ``python tools/make_dirty_fixture.py``.
    """
    import json
    paths = [
        FIXTURE_BAK_DIRTY_ALTERCOL_REWRITE,
        FIXTURE_BAK_DIRTY_ALTERDB,
        FIXTURE_BAK_DIRTY_SAVEPOINT,
        FIXTURE_BAK_DIRTY_NESTED,
        FIXTURE_BAK_DIRTY_SWITCH,
        FIXTURE_DIRTY_GROUND_TRUTH,
    ]
    missing = [p for p in paths if not p.exists()]
    if missing:
        pytest.skip(
            f"remaining dirty fixtures missing: {[p.name for p in missing]} "
            "(run python tools/make_dirty_fixture.py)"
        )
    gt = json.loads(FIXTURE_DIRTY_GROUND_TRUTH.read_text())
    return (
        FIXTURE_BAK_DIRTY_ALTERCOL_REWRITE,
        FIXTURE_BAK_DIRTY_ALTERDB,
        FIXTURE_BAK_DIRTY_SAVEPOINT,
        FIXTURE_BAK_DIRTY_NESTED,
        FIXTURE_BAK_DIRTY_SWITCH,
        gt,
    )


@pytest.fixture(scope="session")
def fixture_bak_incremental() -> tuple[Path, list[Path]]:
    """Return (full_path, [diff_01, …, diff_06]) for the incremental chain.

    Skips the entire session if any of the 7 files is missing; regenerate with
    ``python tools/make_incremental_fixture.py``.
    """
    missing = [p for p in [FIXTURE_BAK_INCREMENTAL_FULL, *FIXTURE_BAK_INCREMENTAL_DIFFS]
               if not p.exists()]
    if missing:
        pytest.skip(
            f"incremental fixtures missing: {[p.name for p in missing]} "
            "(run python tools/make_incremental_fixture.py)"
        )
    return FIXTURE_BAK_INCREMENTAL_FULL, FIXTURE_BAK_INCREMENTAL_DIFFS


@pytest.fixture
def fixture_bak_ndf() -> Path:
    if not FIXTURE_BAK_NDF.exists():
        pytest.skip(
            f"NDF fixture missing: {FIXTURE_BAK_NDF} "
            "(run python tools/make_ndf_fixture.py)"
        )
    return FIXTURE_BAK_NDF


@pytest.fixture
def fixture_bak_feature() -> Path:
    if not FIXTURE_BAK_FEATURE.exists():
        pytest.skip(
            f"feature-coverage fixture missing: {FIXTURE_BAK_FEATURE} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> feature)"
        )
    return FIXTURE_BAK_FEATURE


@pytest.fixture
def fixture_bak_temporal_hidden() -> Path:
    if not FIXTURE_BAK_TEMPORAL_HIDDEN.exists():
        pytest.skip(
            f"temporal_hidden fixture missing: {FIXTURE_BAK_TEMPORAL_HIDDEN} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> temporal-hidden)"
        )
    return FIXTURE_BAK_TEMPORAL_HIDDEN


@pytest.fixture
def fixture_bak_pagecomp_anchor() -> Path:
    if not FIXTURE_BAK_PAGECOMP_ANCHOR.exists():
        pytest.skip(
            f"pagecomp_anchor fixture missing: {FIXTURE_BAK_PAGECOMP_ANCHOR} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> pagecomp-anchor)"
        )
    return FIXTURE_BAK_PAGECOMP_ANCHOR


@pytest.fixture
def fixture_bak_pagecomp_long_prefix() -> Path:
    if not FIXTURE_BAK_PAGECOMP_LONG_PREFIX.exists():
        pytest.skip(
            f"pagecomp_long_prefix fixture missing: {FIXTURE_BAK_PAGECOMP_LONG_PREFIX} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> pagecomp-long-prefix)"
        )
    return FIXTURE_BAK_PAGECOMP_LONG_PREFIX


@pytest.fixture
def fixture_bak_archive_null() -> Path:
    if not FIXTURE_BAK_ARCHIVE_NULL.exists():
        pytest.skip(
            f"ARCHIVE null fixture missing: {FIXTURE_BAK_ARCHIVE_NULL} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> archive-null)"
        )
    return FIXTURE_BAK_ARCHIVE_NULL


@pytest.fixture
def fixture_bak_archive_columnstore_partition() -> Path:
    if not FIXTURE_BAK_ARCHIVE_COLUMNSTORE_PARTITION.exists():
        pytest.skip(
            f"ARCHIVE columnstore partition fixture missing: "
            f"{FIXTURE_BAK_ARCHIVE_COLUMNSTORE_PARTITION} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> archive-columnstore-partition)"
        )
    return FIXTURE_BAK_ARCHIVE_COLUMNSTORE_PARTITION


@pytest.fixture
def fixture_bak_archive_columnstore_types() -> Path:
    if not FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES.exists():
        pytest.skip(
            f"ARCHIVE columnstore types fixture missing: "
            f"{FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> archive-columnstore-types)"
        )
    return FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES


@pytest.fixture
def fixture_bak_archive_columnstore_types_random() -> Path:
    if not FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES_RANDOM.exists():
        pytest.skip(
            f"ARCHIVE columnstore types random fixture missing: "
            f"{FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES_RANDOM} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> archive-columnstore-types-random)"
        )
    return FIXTURE_BAK_ARCHIVE_COLUMNSTORE_TYPES_RANDOM


@pytest.fixture
def fixture_bak_pfor_columnstore() -> Path:
    if not FIXTURE_BAK_PFOR_COLUMNSTORE.exists():
        pytest.skip(
            f"PFOR columnstore fixture missing: {FIXTURE_BAK_PFOR_COLUMNSTORE} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> pfor-columnstore)"
        )
    return FIXTURE_BAK_PFOR_COLUMNSTORE


@pytest.fixture
def fixture_bak_pfor_columnstore_random() -> Path:
    if not FIXTURE_BAK_PFOR_COLUMNSTORE_RANDOM.exists():
        pytest.skip(
            f"PFOR columnstore random fixture missing: {FIXTURE_BAK_PFOR_COLUMNSTORE_RANDOM} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> pfor-columnstore-random)"
        )
    return FIXTURE_BAK_PFOR_COLUMNSTORE_RANDOM


@pytest.fixture
def fixture_bak_cci_bitpack_probe() -> Path:
    if not FIXTURE_BAK_CCI_BITPACK_PROBE.exists():
        pytest.skip(
            f"CCI bit-pack probe fixture missing: {FIXTURE_BAK_CCI_BITPACK_PROBE} "
            "(run: python -m tools.fixture_run all-versions --suite cci-bitpack-probe-int)"
        )
    return FIXTURE_BAK_CCI_BITPACK_PROBE


@pytest.fixture
def fixture_bak_cci_bitpack_probe_bigint() -> Path:
    if not FIXTURE_BAK_CCI_BITPACK_PROBE_BIGINT.exists():
        pytest.skip(
            f"CCI bit-pack bigint probe fixture missing: {FIXTURE_BAK_CCI_BITPACK_PROBE_BIGINT} "
            "(run: python -m tools.fixture_run all-versions --suite cci-bitpack-probe-bigint)"
        )
    return FIXTURE_BAK_CCI_BITPACK_PROBE_BIGINT


@pytest.fixture
def fixture_bak_cci_bitpack_probe_highbase() -> Path:
    if not FIXTURE_BAK_CCI_BITPACK_PROBE_HIGHBASE.exists():
        pytest.skip(
            f"CCI bit-pack highbase probe fixture missing: {FIXTURE_BAK_CCI_BITPACK_PROBE_HIGHBASE} "
            "(run: python -m tools.fixture_run all-versions --suite cci-bitpack-probe-highbase)"
        )
    return FIXTURE_BAK_CCI_BITPACK_PROBE_HIGHBASE


@pytest.fixture
def fixture_bak_archive_single_chunk() -> Path:
    if not FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK.exists():
        pytest.skip(
            f"single-chunk ARCHIVE fixture missing: {FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> archive-single-chunk)"
        )
    return FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK


@pytest.fixture
def fixture_bak_archive_single_chunk_random() -> Path:
    if not FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK_RANDOM.exists():
        pytest.skip(
            f"single-chunk ARCHIVE random fixture missing: {FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK_RANDOM} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> archive-single-chunk-random)"
        )
    return FIXTURE_BAK_ARCHIVE_SINGLE_CHUNK_RANDOM


@pytest.fixture
def fixture_bak_xml_heap() -> Path:
    if not FIXTURE_BAK_XML_HEAP.exists():
        pytest.skip(
            f"xml-heap fixture missing: {FIXTURE_BAK_XML_HEAP} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> xml-heap)"
        )
    return FIXTURE_BAK_XML_HEAP


@pytest.fixture
def fixture_bak_sparse() -> Path:
    if not FIXTURE_BAK_SPARSE.exists():
        pytest.skip(
            f"sparse fixture missing: {FIXTURE_BAK_SPARSE} "
            "(run: python -m tools.fixture_run all-versions --suite sparse)"
        )
    return FIXTURE_BAK_SPARSE


@pytest.fixture
def fixture_bak_forwarded_records() -> Path:
    if not FIXTURE_BAK_FORWARDED_RECORDS.exists():
        pytest.skip(
            f"forwarded-records fixture missing: {FIXTURE_BAK_FORWARDED_RECORDS} "
            "(run: python -m tools.fixture_run all-versions --suite forwarded-records)"
        )
    return FIXTURE_BAK_FORWARDED_RECORDS


@pytest.fixture
def fixture_bak_ghost_records() -> Path:
    if not FIXTURE_BAK_GHOST_RECORDS.exists():
        pytest.skip(
            f"ghost-records fixture missing: {FIXTURE_BAK_GHOST_RECORDS} "
            "(run: python -m tools.fixture_run all-versions --suite ghost-records)"
        )
    return FIXTURE_BAK_GHOST_RECORDS


@pytest.fixture
def fixture_bak_multi_rowgroup() -> Path:
    if not FIXTURE_BAK_MULTI_ROWGROUP.exists():
        pytest.skip(
            f"multi-rowgroup fixture missing: {FIXTURE_BAK_MULTI_ROWGROUP} "
            "(run: python -m tools.fixture_run all-versions --suite multi-rowgroup)"
        )
    return FIXTURE_BAK_MULTI_ROWGROUP


@pytest.fixture
def fixture_bak_cci_string_dict_regression() -> Path:
    if not FIXTURE_BAK_CCI_STRING_DICT_REGRESSION.exists():
        pytest.skip(
            "cci-string-dict-regression fixture missing: "
            f"{FIXTURE_BAK_CCI_STRING_DICT_REGRESSION} "
            "(run: python -m tools.fixture_run all-versions "
            "--suite cci-string-dict-regression)"
        )
    return FIXTURE_BAK_CCI_STRING_DICT_REGRESSION


@pytest.fixture
def fixture_bak_max_row_width() -> Path:
    if not FIXTURE_BAK_MAX_ROW_WIDTH.exists():
        pytest.skip(
            f"max-row-width fixture missing: {FIXTURE_BAK_MAX_ROW_WIDTH} "
            "(run: python -m tools.fixture_run all-versions --suite max-row-width)"
        )
    return FIXTURE_BAK_MAX_ROW_WIDTH


@pytest.fixture
def fixture_bak_surrogate_pairs() -> Path:
    if not FIXTURE_BAK_SURROGATE_PAIRS.exists():
        pytest.skip(
            f"surrogate-pairs fixture missing: {FIXTURE_BAK_SURROGATE_PAIRS} "
            "(run: python -m tools.fixture_run all-versions --suite surrogate-pairs)"
        )
    return FIXTURE_BAK_SURROGATE_PAIRS


@pytest.fixture
def fixture_bak_high_slot_density() -> Path:
    if not FIXTURE_BAK_HIGH_SLOT_DENSITY.exists():
        pytest.skip(
            f"high-slot-density fixture missing: {FIXTURE_BAK_HIGH_SLOT_DENSITY} "
            "(run: python -m tools.fixture_run all-versions --suite high-slot-density)"
        )
    return FIXTURE_BAK_HIGH_SLOT_DENSITY


@pytest.fixture
def fixture_bak_cci_switch() -> Path:
    if not FIXTURE_BAK_CCI_SWITCH.exists():
        pytest.skip(
            f"cci-switch fixture missing: {FIXTURE_BAK_CCI_SWITCH} "
            "(run: python -m tools.fixture_run all-versions --suite cci-switch)"
        )
    return FIXTURE_BAK_CCI_SWITCH


@pytest.fixture
def fixture_bak_cci_reorganize() -> Path:
    if not FIXTURE_BAK_CCI_REORGANIZE.exists():
        pytest.skip(
            f"cci-reorganize fixture missing: {FIXTURE_BAK_CCI_REORGANIZE} "
            "(run: python -m tools.fixture_run all-versions --suite cci-reorganize)"
        )
    return FIXTURE_BAK_CCI_REORGANIZE


@pytest.fixture
def fixture_bak_covering_index() -> Path:
    if not FIXTURE_BAK_COVERING_INDEX.exists():
        pytest.skip(
            f"covering-index fixture missing: {FIXTURE_BAK_COVERING_INDEX} "
            "(run: python -m tools.fixture_run all-versions --suite covering-index)"
        )
    return FIXTURE_BAK_COVERING_INDEX


@pytest.fixture
def fixture_bak_sql_variant_extract() -> Path:
    if not FIXTURE_BAK_SQL_VARIANT_EXTRACT.exists():
        pytest.skip(
            f"sql-variant-extract fixture missing: {FIXTURE_BAK_SQL_VARIANT_EXTRACT} "
            "(run: python -m tools.fixture_run all-versions --suite sql-variant-extract)"
        )
    return FIXTURE_BAK_SQL_VARIANT_EXTRACT


@pytest.fixture
def fixture_bak_filtered_ncci() -> Path:
    if not FIXTURE_BAK_FILTERED_NCCI.exists():
        pytest.skip(
            f"filtered-ncci fixture missing: {FIXTURE_BAK_FILTERED_NCCI} "
            "(run: python -m tools.fixture_run all-versions --suite filtered-ncci)"
        )
    return FIXTURE_BAK_FILTERED_NCCI


@pytest.fixture
def fixture_bak_ncci_heap() -> Path:
    if not FIXTURE_BAK_NCCI_HEAP.exists():
        pytest.skip(
            f"ncci-heap fixture missing: {FIXTURE_BAK_NCCI_HEAP} "
            "(run: python -m tools.fixture_run all-versions --suite ncci-heap)"
        )
    return FIXTURE_BAK_NCCI_HEAP


@pytest.fixture
def fixture_bak_identity_coverage() -> Path:
    if not FIXTURE_BAK_IDENTITY_COVERAGE.exists():
        pytest.skip(
            f"identity-coverage fixture missing: {FIXTURE_BAK_IDENTITY_COVERAGE} "
            "(run: python -m tools.fixture_run all-versions --suite identity-coverage)"
        )
    return FIXTURE_BAK_IDENTITY_COVERAGE


@pytest.fixture
def fixture_bak_rowversion_extract() -> Path:
    if not FIXTURE_BAK_ROWVERSION_EXTRACT.exists():
        pytest.skip(
            f"rowversion-extract fixture missing: {FIXTURE_BAK_ROWVERSION_EXTRACT} "
            "(run: python -m tools.fixture_run all-versions --suite rowversion-extract)"
        )
    return FIXTURE_BAK_ROWVERSION_EXTRACT


@pytest.fixture
def fixture_bak_hierarchyid_extract() -> Path:
    if not FIXTURE_BAK_HIERARCHYID_EXTRACT.exists():
        pytest.skip(
            f"hierarchyid-extract fixture missing: {FIXTURE_BAK_HIERARCHYID_EXTRACT} "
            "(run: python -m tools.fixture_run all-versions --suite hierarchyid-extract)"
        )
    return FIXTURE_BAK_HIERARCHYID_EXTRACT


@pytest.fixture
def fixture_bak_cci_computed() -> Path:
    if not FIXTURE_BAK_CCI_COMPUTED.exists():
        pytest.skip(
            f"cci-computed fixture missing: {FIXTURE_BAK_CCI_COMPUTED} "
            "(run: python -m tools.fixture_run all-versions --suite cci-computed)"
        )
    return FIXTURE_BAK_CCI_COMPUTED


@pytest.fixture
def fixture_bak_cci_btree_nci() -> Path:
    if not FIXTURE_BAK_CCI_BTREE_NCI.exists():
        pytest.skip(
            f"cci-btree-nci fixture missing: {FIXTURE_BAK_CCI_BTREE_NCI} "
            "(run: python -m tools.fixture_run all-versions --suite cci-btree-nci)"
        )
    return FIXTURE_BAK_CCI_BTREE_NCI


@pytest.fixture
def fixture_bak_ordered_cci() -> Path:
    if not FIXTURE_BAK_ORDERED_CCI.exists():
        pytest.skip(
            f"ordered-cci fixture missing: {FIXTURE_BAK_ORDERED_CCI} "
            "(run: python -m tools.fixture_run all-versions --suite ordered-cci "
            "--version 2022 --version 2025)"
        )
    return FIXTURE_BAK_ORDERED_CCI


@pytest.fixture
def fixture_bak_utf8_collation() -> Path:
    if not FIXTURE_BAK_UTF8_COLLATION.exists():
        pytest.skip(
            f"utf8-collation fixture missing: {FIXTURE_BAK_UTF8_COLLATION} "
            "(run: python -m tools.fixture_run all-versions --suite utf8-collation "
            "--version 2019 --version 2022 --version 2025)"
        )
    return FIXTURE_BAK_UTF8_COLLATION


@pytest.fixture
def fixture_bak_tabletype_cci_large() -> Path:
    if not FIXTURE_BAK_TABLETYPE_CCI_LARGE.exists():
        pytest.skip(
            f"tabletype-cci-large fixture missing: {FIXTURE_BAK_TABLETYPE_CCI_LARGE} "
            "(run: python -m tools.fixture_run all-versions --suite tabletype-cci-large)"
        )
    return FIXTURE_BAK_TABLETYPE_CCI_LARGE


@pytest.fixture
def fixture_bak_cci_extended() -> Path:
    """Path to the extended CCI bug-trigger fixture.

    Generate with::

        python -m tools.fixture_run cci-extended
        python -m tools.fixture_run all-versions --suite cci-extended
    """
    if not FIXTURE_BAK_CCI_EXTENDED.exists():
        pytest.skip(
            f"cci-extended fixture missing: {FIXTURE_BAK_CCI_EXTENDED} "
            "(run: python -m tools.fixture_run all-versions --suite cci-extended)"
        )
    return FIXTURE_BAK_CCI_EXTENDED


@pytest.fixture
def fixture_bak_rowboundary() -> Path:
    """Path to the row-size and LOB-page boundary fixture.

    Covers the 8060-byte in-row/ROW_OVERFLOW boundary (Bug B-3), the
    8096-byte LOB single-page boundary, and data-page slot-array capacity.

    Generate with::

        python -m tools.fixture_run row-boundary
        python -m tools.fixture_run all-versions --suite row-boundary
    """
    if not FIXTURE_BAK_ROWBOUNDARY.exists():
        pytest.skip(
            f"row-boundary fixture missing: {FIXTURE_BAK_ROWBOUNDARY} "
            "(run: python -m tools.fixture_run all-versions --suite row-boundary)"
        )
    return FIXTURE_BAK_ROWBOUNDARY


@pytest.fixture
def fixture_bak_cci_varbinary_micro() -> Path:
    """Path to the F1 VARBINARY micro diagnostic fixture.

    Three tables: cci_varbinary_micro (7 rows), cci_varbinary_micro_nullonly
    (21 rows), cci_varbinary_micro_1byte (20 rows).

    Generate with::

        python -m tools.fixture_run cci-varbinary-micro
        python -m tools.fixture_run all-versions --suite cci-varbinary-micro
    """
    if not FIXTURE_BAK_CCI_VARBINARY_MICRO.exists():
        pytest.skip(
            f"cci-varbinary-micro fixture missing: {FIXTURE_BAK_CCI_VARBINARY_MICRO} "
            "(run: python -m tools.fixture_run all-versions --suite cci-varbinary-micro)"
        )
    return FIXTURE_BAK_CCI_VARBINARY_MICRO


@pytest.fixture
def fixture_bak_cci_binary_varbinary_compare() -> Path:
    """Path to the F4 BINARY(8)+VARBINARY(8) comparison fixture (1,200 rows).

    Generate with::

        python -m tools.fixture_run cci-binary-varbinary-compare
        python -m tools.fixture_run all-versions --suite cci-binary-varbinary-compare
    """
    if not FIXTURE_BAK_CCI_BINARY_VARBINARY_COMPARE.exists():
        pytest.skip(
            f"cci-binary-varbinary-compare fixture missing: {FIXTURE_BAK_CCI_BINARY_VARBINARY_COMPARE} "
            "(run: python -m tools.fixture_run all-versions --suite cci-binary-varbinary-compare)"
        )
    return FIXTURE_BAK_CCI_BINARY_VARBINARY_COMPARE


@pytest.fixture
def fixture_bak_cci_varbinary_probe() -> Path:
    """Path to the F2+F3+F5 varbinary probe fixture.

    Three tables: cci_varbinary_maxwidth (F2), cci_varbinary_narrowmax (F3),
    cci_varbinary_small_rowgroup (F5).

    Generate with::

        python -m tools.fixture_run cci-varbinary-probe
        python -m tools.fixture_run all-versions --suite cci-varbinary-probe
    """
    if not FIXTURE_BAK_CCI_VARBINARY_PROBE.exists():
        pytest.skip(
            f"cci-varbinary-probe fixture missing: {FIXTURE_BAK_CCI_VARBINARY_PROBE} "
            "(run: python -m tools.fixture_run all-versions --suite cci-varbinary-probe)"
        )
    return FIXTURE_BAK_CCI_VARBINARY_PROBE


@pytest.fixture
def fixture_bak_cci_lob() -> Path:
    """Path to the C-6 CCI LOB-types fixture.

    Generate with::

        python -m tools.fixture_run cci-lob
        python -m tools.fixture_run all-versions --suite cci-lob
    """
    if not FIXTURE_BAK_CCI_LOB.exists():
        pytest.skip(
            f"cci-lob fixture missing: {FIXTURE_BAK_CCI_LOB} "
            "(run: python -m tools.fixture_run all-versions --suite cci-lob)"
        )
    return FIXTURE_BAK_CCI_LOB


@pytest.fixture
def fixture_bak_cci_types_large() -> Path:
    """Path to the K-3 one-table-per-type CCI fixture.

    Generate with::

        python -m tools.fixture_run cci-types-large
        python -m tools.fixture_run all-versions --suite cci-types-large
    """
    if not FIXTURE_BAK_CCI_TYPES_LARGE.exists():
        pytest.skip(
            f"cci-types-large fixture missing: {FIXTURE_BAK_CCI_TYPES_LARGE} "
            "(run: python -m tools.fixture_run all-versions --suite cci-types-large)"
        )
    return FIXTURE_BAK_CCI_TYPES_LARGE


@pytest.fixture
def fixture_bak_ncci_types() -> Path:
    """Path to the K-5 NCCI type-coverage fixture.

    Generate with::

        python -m tools.fixture_run ncci-types
        python -m tools.fixture_run all-versions --suite ncci-types
    """
    if not FIXTURE_BAK_NCCI_TYPES.exists():
        pytest.skip(
            f"ncci-types fixture missing: {FIXTURE_BAK_NCCI_TYPES} "
            "(run: python -m tools.fixture_run all-versions --suite ncci-types)"
        )
    return FIXTURE_BAK_NCCI_TYPES


@pytest.fixture
def fixture_bak_realworld_numeric_digest() -> Path:
    """Path to the real-world numeric digest regression fixture."""
    if not FIXTURE_BAK_REALWORLD_NUMERIC_DIGEST.exists():
        pytest.skip(
            f"realworld-numeric-digest fixture missing: {FIXTURE_BAK_REALWORLD_NUMERIC_DIGEST} "
            "(run: python -m tools.fixture_run all-versions --suite realworld-numeric-digest)"
        )
    return FIXTURE_BAK_REALWORLD_NUMERIC_DIGEST


@pytest.fixture
def fixture_bak_xtp_rich() -> Path:
    """Path to the rich XTP memory-optimized regression fixture."""
    if not FIXTURE_BAK_XTP_RICH.exists():
        pytest.skip(
            f"xtp-rich fixture missing: {FIXTURE_BAK_XTP_RICH} "
            "(run: python -m tools.fixture_run all-versions --suite xtp-rich)"
        )
    return FIXTURE_BAK_XTP_RICH


@pytest.fixture
def fixture_bak_xtp_checkpoint() -> Path:
    """Path to the large XTP checkpoint-straddle fixture."""
    if not FIXTURE_BAK_XTP_CHECKPOINT.exists():
        pytest.skip(
            f"xtp-checkpoint fixture missing: {FIXTURE_BAK_XTP_CHECKPOINT} "
            "(run: python -m tools.fixture_run all-versions --suite xtp-checkpoint)"
        )
    return FIXTURE_BAK_XTP_CHECKPOINT


@pytest.fixture
def fixture_bak_corrupt_metadata_confidence() -> Path:
    """Path to the intentionally corrupt confidence-only metadata fixture."""
    if not FIXTURE_BAK_CORRUPT_METADATA_CONFIDENCE.exists():
        pytest.skip(
            f"corrupt-metadata-confidence fixture missing: {FIXTURE_BAK_CORRUPT_METADATA_CONFIDENCE} "
            "(run: python -m tools.fixture_run --fixture-dir <dir> corrupt-metadata-confidence)"
        )
    return FIXTURE_BAK_CORRUPT_METADATA_CONFIDENCE


@pytest.fixture
def fixture_bak_tde() -> Path:
    """Path to the F-1 TDE-encrypted backup fixture.

    Generate with::

        python -m tools.fixture_run tde
        python -m tools.fixture_run all-versions --suite tde
    """
    if not FIXTURE_BAK_TDE.exists():
        pytest.skip(
            f"TDE fixture missing: {FIXTURE_BAK_TDE} "
            "(run: python -m tools.fixture_run all-versions --suite tde)"
        )
    return FIXTURE_BAK_TDE


@pytest.fixture
def fixture_bak_boundary_datetime() -> Path:
    """Path to the K-2 datetime/bit/decimal boundary fixture.

    Generate with::

        python -m tools.fixture_run boundary-datetime
        python -m tools.fixture_run all-versions --suite boundary-datetime
    """
    if not FIXTURE_BAK_BOUNDARY_DATETIME.exists():
        pytest.skip(
            f"Boundary-datetime fixture missing: {FIXTURE_BAK_BOUNDARY_DATETIME} "
            "(run: python -m tools.fixture_run all-versions --suite boundary-datetime)"
        )
    return FIXTURE_BAK_BOUNDARY_DATETIME


@pytest.fixture
def fixture_bak_mixed_collation() -> Path:
    """Path to the G-3 per-column collation override fixture.

    Generate with::

        python -m tools.fixture_run mixed-collation
        python -m tools.fixture_run all-versions --suite mixed-collation
    """
    if not FIXTURE_BAK_MIXED_COLLATION.exists():
        pytest.skip(
            f"mixed-collation fixture missing: {FIXTURE_BAK_MIXED_COLLATION} "
            "(run: python -m tools.fixture_run all-versions --suite mixed-collation)"
        )
    return FIXTURE_BAK_MIXED_COLLATION


@pytest.fixture
def fixture_bak_delta_rowgroup() -> Path:
    """Path to the CCI delta-store fixture (Gap C-1).

    Generate with::

        python -m tools.fixture_run delta-rowgroup
        python -m tools.fixture_run all-versions --suite delta-rowgroup
    """
    if not FIXTURE_BAK_DELTA_ROWGROUP.exists():
        pytest.skip(
            f"delta-rowgroup fixture missing: {FIXTURE_BAK_DELTA_ROWGROUP} "
            "(run: python -m tools.fixture_run all-versions --suite delta-rowgroup)"
        )
    return FIXTURE_BAK_DELTA_ROWGROUP


@pytest.fixture
def fixture_bacpac() -> Path:
    """Path to the generated type-coverage BACPAC fixture.

    Generate with::

        python -m tools.make_bacpac_fixture
    """
    if not FIXTURE_BACPAC.exists():
        pytest.skip(
            f"BACPAC fixture missing: {FIXTURE_BACPAC} "
            "(run: python -m tools.make_bacpac_fixture)"
        )
    return FIXTURE_BACPAC


@pytest.fixture
def fixture_bak_backup_blocksize() -> Path:
    """Path to the non-default BLOCKSIZE fixture (Gap A-5).

    Generate with::

        python -m tools.fixture_run all-versions --suite backup-blocksize
    """
    if not FIXTURE_BAK_BACKUP_BLOCKSIZE.exists():
        pytest.skip(
            f"backup-blocksize fixture missing: {FIXTURE_BAK_BACKUP_BLOCKSIZE} "
            "(run: python -m tools.fixture_run all-versions --suite backup-blocksize)"
        )
    return FIXTURE_BAK_BACKUP_BLOCKSIZE


@pytest.fixture
def fixture_bak_cci_string_minmax() -> Path:
    """Path to the CCI string min-max metadata fixture (Gap C-8).

    Generate with::

        python -m tools.fixture_run all-versions --suite cci-string-minmax --version 2022
    """
    if not FIXTURE_BAK_CCI_STRING_MINMAX.exists():
        pytest.skip(
            f"cci-string-minmax fixture missing: {FIXTURE_BAK_CCI_STRING_MINMAX} "
            "(run: python -m tools.fixture_run all-versions --suite cci-string-minmax "
            "--version 2022)"
        )
    return FIXTURE_BAK_CCI_STRING_MINMAX


@pytest.fixture
def fixture_bak_cci_enc5_largepool() -> Path:
    """Path to the regular-CCI enc=5 CHAR large-pool fixture.

    Generate with::

        python -m tools.fixture_run all-versions --suite cci-enc5-largepool
    """
    if not FIXTURE_BAK_CCI_ENC5_LARGEPOOL.exists():
        pytest.skip(
            f"cci-enc5-largepool fixture missing: {FIXTURE_BAK_CCI_ENC5_LARGEPOOL} "
            "(run: python -m tools.fixture_run all-versions --suite cci-enc5-largepool)"
        )
    return FIXTURE_BAK_CCI_ENC5_LARGEPOOL


@pytest.fixture
def fixture_bak_xml_index() -> Path:
    """Path to the XML index fixture (Gap E-3).

    Generate with::

        python -m tools.fixture_run all-versions --suite xml-index
    """
    if not FIXTURE_BAK_XML_INDEX.exists():
        pytest.skip(
            f"xml-index fixture missing: {FIXTURE_BAK_XML_INDEX} "
            "(run: python -m tools.fixture_run all-versions --suite xml-index)"
        )
    return FIXTURE_BAK_XML_INDEX


@pytest.fixture
def fixture_bak_spatial_index() -> Path:
    """Path to the spatial index fixture (Gap E-4).

    Generate with::

        python -m tools.fixture_run all-versions --suite spatial-index
    """
    if not FIXTURE_BAK_SPATIAL_INDEX.exists():
        pytest.skip(
            f"spatial-index fixture missing: {FIXTURE_BAK_SPATIAL_INDEX} "
            "(run: python -m tools.fixture_run all-versions --suite spatial-index)"
        )
    return FIXTURE_BAK_SPATIAL_INDEX


@pytest.fixture
def fixture_bak_alias_types() -> Path:
    """Path to the alias scalar type cell fixture."""
    if not FIXTURE_BAK_ALIAS_TYPES.exists():
        pytest.skip(
            f"alias-types fixture missing: {FIXTURE_BAK_ALIAS_TYPES} "
            "(run: python -m tools.fixture_run all-versions --suite alias-types)"
        )
    return FIXTURE_BAK_ALIAS_TYPES


@pytest.fixture
def fixture_bak_typed_xml() -> Path:
    """Path to the typed XML cell fixture."""
    if not FIXTURE_BAK_TYPED_XML.exists():
        pytest.skip(
            f"typed-xml fixture missing: {FIXTURE_BAK_TYPED_XML} "
            "(run: python -m tools.fixture_run all-versions --suite typed-xml)"
        )
    return FIXTURE_BAK_TYPED_XML


@pytest.fixture
def fixture_bak_spatial_edge() -> Path:
    """Path to the spatial edge cell fixture."""
    if not FIXTURE_BAK_SPATIAL_EDGE.exists():
        pytest.skip(
            f"spatial-edge fixture missing: {FIXTURE_BAK_SPATIAL_EDGE} "
            "(run: python -m tools.fixture_run all-versions --suite spatial-edge)"
        )
    return FIXTURE_BAK_SPATIAL_EDGE


@pytest.fixture
def fixture_bak_float_extreme() -> Path:
    """Path to the float/real extreme cell fixture."""
    if not FIXTURE_BAK_FLOAT_EXTREME.exists():
        pytest.skip(
            f"float-extreme fixture missing: {FIXTURE_BAK_FLOAT_EXTREME} "
            "(run: python -m tools.fixture_run all-versions --suite float-extreme)"
        )
    return FIXTURE_BAK_FLOAT_EXTREME


@pytest.fixture
def fixture_bak_rowstore_lob_image() -> Path:
    """Path to the rowstore LOB/image cell fixture."""
    if not FIXTURE_BAK_ROWSTORE_LOB_IMAGE.exists():
        pytest.skip(
            f"rowstore-lob-image fixture missing: {FIXTURE_BAK_ROWSTORE_LOB_IMAGE} "
            "(run: python -m tools.fixture_run all-versions --suite rowstore-lob-image)"
        )
    return FIXTURE_BAK_ROWSTORE_LOB_IMAGE


@pytest.fixture
def fixture_bak_rowstore_lob_markup() -> Path:
    """Path to the rowstore markup LOB regression fixture."""
    if not FIXTURE_BAK_ROWSTORE_LOB_MARKUP.exists():
        pytest.skip(
            f"rowstore-lob-markup fixture missing: {FIXTURE_BAK_ROWSTORE_LOB_MARKUP} "
            "(run: python -m tools.fixture_run all-versions --suite rowstore-lob-markup)"
        )
    return FIXTURE_BAK_ROWSTORE_LOB_MARKUP


@pytest.fixture
def fixture_bak_rowstore_hash_pii() -> Path:
    """Path to the rowstore binary/hash PII regression fixture."""
    if not FIXTURE_BAK_ROWSTORE_HASH_PII.exists():
        pytest.skip(
            f"rowstore-hash-pii fixture missing: {FIXTURE_BAK_ROWSTORE_HASH_PII} "
            "(run: python -m tools.fixture_run all-versions --suite rowstore-hash-pii)"
        )
    return FIXTURE_BAK_ROWSTORE_HASH_PII


@pytest.fixture
def fixture_bak_nvarchar_max_u21() -> Path:
    """Path to the nvarchar(max) 0x21-first-byte regression fixture."""
    if not FIXTURE_BAK_NVARCHAR_MAX_U21.exists():
        pytest.skip(
            f"nvarchar-max-u21 fixture missing: {FIXTURE_BAK_NVARCHAR_MAX_U21} "
            "(run: python -m tools.fixture_run all-versions --suite nvarchar-max-u21)"
        )
    return FIXTURE_BAK_NVARCHAR_MAX_U21


@pytest.fixture
def fixture_bak_compressed_nvarchar() -> Path:
    """Path to the ROW-compressed nvarchar SCSU/UTF-16LE regression fixture."""
    if not FIXTURE_BAK_COMPRESSED_NVARCHAR.exists():
        pytest.skip(
            f"compressed-nvarchar fixture missing: {FIXTURE_BAK_COMPRESSED_NVARCHAR} "
            "(run: python -m tools.fixture_run all-versions --suite compressed-nvarchar)"
        )
    return FIXTURE_BAK_COMPRESSED_NVARCHAR


@pytest.fixture
def fixture_bak_torn_page() -> Path:
    """Path to the TORN_PAGE_DETECTION regression fixture."""
    if not FIXTURE_BAK_TORN_PAGE.exists():
        pytest.skip(
            f"torn-page fixture missing: {FIXTURE_BAK_TORN_PAGE} "
            "(run: python -m tools.fixture_run all-versions --suite torn-page)"
        )
    return FIXTURE_BAK_TORN_PAGE


@pytest.fixture
def fixture_bak_vector() -> Path:
    """Path to the VECTOR column fixture (Gap D-5, SS2025 only).

    Generate with::

        python -m tools.fixture_run all-versions --suite vector --version 2025
    """
    if not FIXTURE_BAK_VECTOR.exists():
        pytest.skip(
            f"vector fixture missing: {FIXTURE_BAK_VECTOR} "
            "(run: python -m tools.fixture_run all-versions --suite vector --version 2025)"
        )
    return FIXTURE_BAK_VECTOR


@pytest.fixture
def fixture_bak_native_json() -> Path:
    """Path to the native JSON column fixture (Gap D-6, SS2025 only).

    Generate with::

        python -m tools.fixture_run all-versions --suite native-json --version 2025
    """
    if not FIXTURE_BAK_NATIVE_JSON.exists():
        pytest.skip(
            f"native-json fixture missing: {FIXTURE_BAK_NATIVE_JSON} "
            "(run: python -m tools.fixture_run all-versions --suite native-json --version 2025)"
        )
    return FIXTURE_BAK_NATIVE_JSON
