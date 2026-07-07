"""Single source of truth for known fixture extraction gaps.

Both ``tools/correctness_coverage.py`` (coverage doc ``~`` marker) and
``tests/test_stats.py`` (``pytest.xfail``) resolve gaps through this module so
the two never drift.

Version-conditional gaps
------------------------
Some gaps manifest on only a subset of SQL Server versions (e.g. a
timing-dependent fuzzy-backup case that happens to extract cleanly on SS2017 /
SS2022).  Each :class:`Gap` therefore carries ``passes_on`` - the set of SQL
Server version years on which the fixture actually passes and so must NOT be
xfailed.  Resolve a gap for a given run with :func:`gap_reason`, deriving the
running version from the fixture directory via :func:`version_from_fixture_dir`.
An empty ``passes_on`` means the gap applies on every version where the fixture
exists.

Adding a new gap
----------------
Add an entry to ``KNOWN_GAPS`` with a concise, sourced reason.  The key is the
fixture stem (``Path.stem`` of the ``.bak``).  If the gap is version-conditional,
list the passing version years in ``passes_on``.

Partial-column gaps (min/max only)
-----------------------------------
Column-level min/max gaps live in ``tests/test_stats.py`` ``_KNOWN_MINMAX_COL_GAPS``;
that is purely a test-layer concern (the coverage doc does not do column-level
min/max diffing at this level of granularity) so it remains there.

Expected skipped tables
-----------------------
Some real-world backups contain table schemas whose data is intentionally absent
from extraction because the backing storage is not recoverable from the backup
shape mssqlbak currently understands.  These are tracked at table granularity so
coverage and tests can still score the rest of the fixture normally.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Whole-fixture gaps (fixture_stem -> Gap)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Gap:
    """A known extraction gap between mssqlbak output and SQL Server truth.

    ``reason`` is shown both in the coverage doc and as the pytest xfail reason.
    ``passes_on`` lists SQL Server version years on which the fixture actually
    passes (so it must NOT be xfailed there); empty = the gap applies on every
    version where the fixture exists.
    """

    reason: str
    passes_on: frozenset[int] = field(default_factory=frozenset)


KNOWN_GAPS: dict[str, Gap] = {
    # ── Resolved dirty-row suppression cases ─────────────────────────────────
    # NOTE: dirtycoverage_large_dirty is now FULLY CLEAN on every version (no gap).
    # SQL Server fn_dump_dblog reports all 5,000 LOP_INSERT_ROWS in the backup log
    # tail.  mssqlbak's current scanner also finds all 5,000 dirty INSERT records,
    # suppressing 4,999 by physical slot and the remaining page-split row by the
    # dirty_row_bytes fingerprint path.
    # NOTE: dirtycoverage_cci_delete is now FULLY CLEAN on every version (no gap).
    # Three independent issues it once exposed are all fixed:
    #   1. fuzzy over-read (6,834 vs 6,000) — mtf.py ingests the trailing
    #      modified-page run an online backup appends (highest-LSN-wins);
    #   2. the constant 'phase' = 'compressed' string column decoded to '' —
    #      enc=3 compact-RLE used the nullable shift (mn-2) for a non-nullable
    #      segment; fixed in dict_string.py (shift = mn when not has_null);
    #   3. the 'score' FLOAT column decoded to NaN/denormals on the Rust fast
    #      path (2017/2025, where no log-tail correction runs) — enc=4 float
    #      used null_val as the base for a non-nullable segment instead of the
    #      segment minimum `mn`; fixed in value_for.py AND rust/columnstore.rs.
    # See docs/fuzzy-recovery-redo/chronology-9.md.
    # ── Log records pre-date MinLSN (log-tail window gaps) ───────────────────
    # NOTE: dirtycoverage_rich_update is now FULLY CLEAN on every version.
    # The 2017 nc_val mismatch was not an inherent lost-byte case: the page
    # after-image preserved the correct UTF-16 high zero byte, but the neighbor
    # inference heuristic rewrote X 00 X to X 58 X and produced U+5858.  The fix
    # recovers clobbered bytes from the page after-image before trying neighbor
    # inference, and only uses neighbor inference for offsets not present in the
    # after-image.
    #
    # NOTE: dirtycoverage_committed_delete_v4 is now FULLY CLEAN on every version
    # (no gap).  The 3 phantom rows it once showed on SS2017 (id=328/656/984) were
    # NOT missing log records — all 1000 committed DELETEs are present in the .bak
    # as well-formed LOP_DELETE_ROWS.  The bug was in the scanner: those 3 records
    # begin at block offset 0x30 in OPEN log blocks (the first record of a
    # log-flush segment), below the hardcoded _BLOCK_HDR=0x48 where the OPEN-block
    # scan starts, so the scan landed mid-record and dropped them.  Fixed by also
    # scanning the [0, 0x48) prefix of OPEN blocks in _iter_cont_records
    # (mssqlbak/logtail.py).  Verified: tools/diag/_diag_cdv4_phantom.py.
    # ── Encrypted backups (TDE) ───────────────────────────────────────────────
    "tde_full": Gap(
        "Transparent Data Encryption (TDE): SQL Server writes the MSSQLBAK "
        "container but AES-encrypts every data page.  mssqlbak cannot decrypt "
        "TDE-encrypted backups without the Database Encryption Key (DEK) and "
        "the server certificate stored in master.  Extraction raises "
        "EncryptedBackupError by design."
    ),
    # ── enc=5 ARCHIVE sub-block: exact overflow-row pre_meta layout ───────────
    # [EMPIRICAL] — needs DBCC CSINDEX capture from a COLUMNSTORE_ARCHIVE fixture
    # (use tools/make_matrix_fixtures.py --suite arch2 + tools/diag/diag_dbcc_csindex.py)
    # to confirm the pre_meta format for overflow rows in compressed sub-blocks.
    # Track as absent until the compressed-subblock path is exercised by a fixture.
    # ── enc=5 Format D multichunk / >32767-row overflow rows ─────────────────
    # [EMPIRICAL] — the pre_meta overflow-row layout for Format D multichunk segments
    # (n_rows > 32767, u32@38 == n_rows) is partially observed.  The exact pre_meta
    # stride and last-chunk "contaminated" overflow layout are not yet confirmed by
    # DBCC CSINDEX.  Capture with tools/make_matrix_fixtures.py --suite enc5fa
    # --rows 65537 + tools/diag/diag_dbcc_csindex.py.
    # ── v4 Huffman dict large page count (entry_count > 128) ─────────────────
    # [EMPIRICAL] — the xVelocity v4 dictionary page tree for > 128 entries is not
    # yet confirmed with DBCC CSINDEX.  The current decoder handles single-page
    # dicts only; multi-page decoding is speculative.  Capture with a fixture that
    # has > 128 distinct string values per column.
}


# ---------------------------------------------------------------------------
# Table-level expected skips (fixture_stem -> frozenset of "schema.table" FQNs)
# ---------------------------------------------------------------------------


KNOWN_SKIPPED_TABLES: dict[str, frozenset[str]] = {}


# ---------------------------------------------------------------------------
# Resolution helpers
# ---------------------------------------------------------------------------


def version_from_fixture_dir(fixture_dir: Path | str | None) -> int | None:
    """Derive the SQL Server version year from a fixture directory name.

    ``tests/fixtures_2022`` -> ``2022``.  The shared ``tests/fixtures`` set and
    non-versioned dirs (e.g. ``tests/fixtures_realworld``) -> ``None`` (unknown
    version), in which case version-scoped ``passes_on`` cannot suppress a gap.
    """
    if fixture_dir is None:
        return None
    m = re.search(r"(20\d{2})$", Path(fixture_dir).name)
    return int(m.group(1)) if m else None


def gap_reason(stem: str, version: int | None) -> str | None:
    """Return the known-gap reason for fixture ``stem`` on ``version``.

    Returns ``None`` when the fixture has no known gap on that version (it should
    run and pass) - either because no gap is registered, or because ``version``
    is listed in the gap's ``passes_on``.
    """
    gap = KNOWN_GAPS.get(stem)
    if gap is None:
        return None
    if version is not None and version in gap.passes_on:
        return None
    return gap.reason


def expected_skipped_tables(stem: str) -> frozenset[str]:
    """Return table FQNs intentionally absent from extraction for ``stem``."""
    return KNOWN_SKIPPED_TABLES.get(stem, frozenset())
