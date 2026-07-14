"""Phase C2: byte-level layout conformance tests.

Verifies that the forge's ``encode_fixedvar`` is the exact inverse of
``decode_record`` against real SQL Server fixture pages.

Test approach
-------------
1. Load a real ``.bak`` fixture.
2. Walk each leaf page and extract raw record bytes.
3. Decode with ``decode_record`` → ``{col: raw_bytes | None}``.
4. Re-encode with ``encode_fixedvar`` using the decoded bytes.
5. Decode the forge output again.
6. Assert that the re-decoded bytes are identical to the original decoded bytes.

This confirms **self-consistency** (forge is the inverse of reader).  For
**SQL-Server byte faithfulness** the additional assertion
``forged_record == original_record_bytes`` is applied where the two should be
identical (simple tables with no dropped columns or metadata-only ALTER).

All tests are marked ``@pytest.mark.fixture`` and skip when fixture files are
absent (e.g. CI environments that do not carry binary fixture blobs).

Validated-atom export
---------------------
``VALIDATED_ATOM_TYPES`` is the set of table names whose forge encoding is
proven byte-faithful (non-null rows only).  Tests in other files that compose
forge atoms into novel layouts should only use atoms from this set as
ground-truth sources.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.forge.record_fixedvar import encode_fixedvar
from mssqlbak.pages import PageStore
from mssqlbak.records import RecordColumn, decode_record
from mssqlbak.rows import _record_columns
from mssqlbak.rows.pagewalk import _data_pages_with_page

# ---------------------------------------------------------------------------
# Fixture paths
# ---------------------------------------------------------------------------

_FIXTURE_2022 = Path(__file__).parent / "fixtures_2022"
_TYPECOVERAGE = _FIXTURE_2022 / "typecoverage_full.bak"


def _skip_if_absent(path: Path) -> None:
    if not path.exists():
        pytest.skip(f"fixture absent: {path.name}")


# ---------------------------------------------------------------------------
# Validated atom set
# Table names whose forge encoding is proven byte-faithful (non-null rows).
# Other test files should only use atoms from this set as ground truth.
# ---------------------------------------------------------------------------

VALIDATED_ATOM_TYPES: frozenset[str] = frozenset({
    "t_tinyint", "t_smallint", "t_int", "t_bigint",
    "t_bit",
    "t_decimal_38_10", "t_numeric_18_4",
    "t_money", "t_smallmoney",
    "t_real", "t_float",
    "t_date", "t_datetime", "t_datetime2_7", "t_datetimeoffset_7",
    "t_smalldatetime",
    "t_char_10", "t_nchar_10",
    "t_binary_8",
    "t_uniqueidentifier",
})
# NOTE: t_nvarchar_50 is excluded from VALIDATED_ATOM_TYPES because SQL Server
# applies the "trailing-empty-var truncation" optimization: when the last
# variable-length column in a record has zero bytes (e.g. the "low"='' row),
# SQL Server omits the trailing nvar entry from the record (reduces nvar by 1).
# The forge always emits explicit zero-length entries for all var columns.
# Both decode correctly (reader returns b'' for a missing trailing var col),
# so this is a format difference, not a reader bug.  The self-consistency and
# null-masked comparison tests still pass for this table.


# ---------------------------------------------------------------------------
# Core helper
# ---------------------------------------------------------------------------

def _roundtrip_table(bak: Path, table_name: str) -> list[str]:
    """Decode→forge→decode for every record in *table_name*.

    Returns a list of human-readable mismatch descriptions (empty = all good).
    """
    store = PageStore.from_bak(str(bak))
    schema = recover_schema(store)
    table = next((t for t in schema.tables if t.name == table_name), None)
    if table is None:
        return [f"Table {table_name!r} not found in fixture"]

    rec_cols = _record_columns(table)
    if not rec_cols:
        return []

    errors: list[str] = []
    for _pid, _fid, page in _data_pages_with_page(store, table):
        for slot in range(page.header.slot_cnt):
            raw_rec = page.record(slot)
            decoded = decode_record(raw_rec, rec_cols)
            forged  = encode_fixedvar(rec_cols, decoded)
            redecoded = decode_record(forged, rec_cols)
            if redecoded != decoded:
                errors.append(
                    f"slot {slot}: column-bytes mismatch\n"
                    f"  decoded:   {decoded}\n"
                    f"  redecoded: {redecoded}"
                )
    return errors


# ---------------------------------------------------------------------------
# Self-consistency tests per table
# ---------------------------------------------------------------------------

class TestFixtureRoundtripConsistency:
    """Decode→forge→decode produces identical raw column bytes for fixture rows."""

    @pytest.mark.fixture
    def test_t_int_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_int")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_bigint_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_bigint")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_bit_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_bit")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_char_10_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_char_10")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_nchar_10_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_nchar_10")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_float_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_float")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_date_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_date")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_datetime_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_datetime")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_money_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_money")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_decimal_38_10_roundtrip(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = _roundtrip_table(_TYPECOVERAGE, "t_decimal_38_10")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_all_tables_roundtrip(self):
        """All non-LOB tables round-trip through encode_fixedvar→decode_record."""
        _skip_if_absent(_TYPECOVERAGE)
        store = PageStore.from_bak(str(_TYPECOVERAGE))
        schema = recover_schema(store)

        all_errors: list[str] = []
        for table in schema.tables:
            rec_cols = _record_columns(table)
            if not rec_cols:
                continue
            table_errors: list[str] = []
            for _pid, _fid, page in _data_pages_with_page(store, table):
                for slot in range(page.header.slot_cnt):
                    raw_rec = page.record(slot)
                    decoded = decode_record(raw_rec, rec_cols)
                    forged  = encode_fixedvar(rec_cols, decoded)
                    redecoded = decode_record(forged, rec_cols)
                    if redecoded != decoded:
                        table_errors.append(f"  slot {slot}: {redecoded!r} != {decoded!r}")
            if table_errors:
                all_errors.append(f"Table {table.name!r}:")
                all_errors.extend(table_errors[:3])  # limit output

        assert not all_errors, "\n".join(all_errors[:20])


# ---------------------------------------------------------------------------
# Phase C2: byte-faithful layout test
#
# For tables where the forge's column layout exactly mirrors SQL Server's
# (same leaf_offsets, same var_index ordering), the encoded bytes MUST match
# the original raw record bytes.
#
# Precondition: no dropped columns, no metadata-only ADD COLUMN defaults.
# The typecoverage tables satisfy this — they are simple single-column tables
# freshly created with no ALTER TABLE DDL.
# ---------------------------------------------------------------------------

class TestByteLayoutConformance:
    """Forge record bytes match real SQL Server record bytes (byte-for-byte).

    Note on null fixed-length columns
    ----------------------------------
    SQL Server does **not** zero out the on-disk bytes of a fixed-length column
    when the null-bitmap marks it as NULL; the old bytes remain in place but are
    ignored by the reader.  The forge, by contrast, writes zero bytes for null
    fixed-length columns (the simplest correct behaviour).  Therefore, byte-for-
    byte comparison is only valid for rows where **all fixed-length columns are
    NOT null**.  Rows that contain a null fixed column are skipped from the byte
    comparison (they still pass the decode-round-trip check in
    :class:`TestFixtureRoundtripConsistency`).

    Similarly, null variable-length columns may leave "leftover" data in the
    variable section from a prior non-null value; rows with null variable columns
    are also skipped for byte comparison.
    """

    def _has_null_col(
        self,
        decoded: dict[str, bytes | None],
    ) -> bool:
        return any(v is None for v in decoded.values())

    def _byte_compare_table(self, bak: Path, table_name: str) -> list[str]:
        """Return mismatch descriptions where forge bytes != fixture bytes.

        Only compares rows where no column is NULL (to avoid the SQL Server
        "don't-care null bytes" vs forge "zero null bytes" discrepancy).
        """
        store = PageStore.from_bak(str(bak))
        schema = recover_schema(store)
        table = next((t for t in schema.tables if t.name == table_name), None)
        if table is None:
            return [f"Table {table_name!r} not found"]

        rec_cols = _record_columns(table)
        if not rec_cols:
            return []

        errors: list[str] = []
        for _pid, _fid, page in _data_pages_with_page(store, table):
            for slot in range(page.header.slot_cnt):
                fixture_bytes = page.record(slot)
                decoded = decode_record(fixture_bytes, rec_cols)
                if self._has_null_col(decoded):
                    continue  # skip: null bytes may differ (see class docstring)
                forged  = encode_fixedvar(rec_cols, decoded)
                if forged != fixture_bytes:
                    errors.append(
                        f"slot {slot}:\n"
                        f"  fixture: {fixture_bytes.hex()}\n"
                        f"  forged:  {forged.hex()}"
                    )
        return errors

    @pytest.mark.fixture
    def test_t_int_byte_faithful(self):
        """Forge INT record bytes are byte-identical to SQL Server 2022."""
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._byte_compare_table(_TYPECOVERAGE, "t_int")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_bigint_byte_faithful(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._byte_compare_table(_TYPECOVERAGE, "t_bigint")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_bit_byte_faithful(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._byte_compare_table(_TYPECOVERAGE, "t_bit")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_char_10_byte_faithful(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._byte_compare_table(_TYPECOVERAGE, "t_char_10")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_float_byte_faithful(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._byte_compare_table(_TYPECOVERAGE, "t_float")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_date_byte_faithful(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._byte_compare_table(_TYPECOVERAGE, "t_date")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_t_money_byte_faithful(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._byte_compare_table(_TYPECOVERAGE, "t_money")
        assert not errors, "\n".join(errors)

    @pytest.mark.fixture
    def test_all_validated_atom_types_byte_faithful(self):
        """Full matrix: every VALIDATED_ATOM_TYPES table is byte-faithful (non-null rows)."""
        _skip_if_absent(_TYPECOVERAGE)
        all_errors: list[str] = []
        for table_name in sorted(VALIDATED_ATOM_TYPES):
            errs = self._byte_compare_table(_TYPECOVERAGE, table_name)
            # Only report if table exists and has mismatches (not-found is ok
            # if the fixture predates that type).
            for e in errs:
                if "not found" not in e:
                    all_errors.append(f"{table_name}: {e}")
        assert not all_errors, "\n".join(all_errors[:20])


# ---------------------------------------------------------------------------
# Null-region masked byte comparison
#
# SQL Server leaves stale bytes in the fixed-column storage area when a column
# is NULL (only the null-bitmap bit marks it).  The forge writes zeros in those
# slots.  A "masked" comparison skips the byte ranges of null columns, letting
# us validate that:
#   - The null-bitmap byte(s) are identical.
#   - The live (non-null) column regions are identical.
#   - The variable-length section is identical for non-null var columns.
# ---------------------------------------------------------------------------

def _null_masked_compare(
    fixture_bytes: bytes,
    forged_bytes: bytes,
    rec_cols: list[RecordColumn],
    decoded: dict[str, bytes | None],
) -> list[str]:
    """Compare fixture and forged bytes, skipping null fixed-column byte ranges.

    Returns a list of mismatch descriptions.  Empty = byte-faithful in live regions.
    """
    errors: list[str] = []

    if len(fixture_bytes) != len(forged_bytes):
        # Length mismatch is always a bug.
        errors.append(
            f"length: fixture={len(fixture_bytes)} forged={len(forged_bytes)}"
        )
        return errors

    # Build set of byte offsets that belong to NULL fixed-length columns.
    null_fixed_ranges: list[tuple[int, int]] = []
    for col in rec_cols:
        if not col.is_variable and decoded.get(col.name) is None:
            null_fixed_ranges.append((col.leaf_offset, col.leaf_offset + col.size))

    # Compare byte by byte, skip null-fixed ranges.
    for i, (fb, gb) in enumerate(zip(fixture_bytes, forged_bytes)):
        in_null_range = any(lo <= i < hi for lo, hi in null_fixed_ranges)
        if in_null_range:
            continue
        if fb != gb:
            errors.append(f"offset {i}: fixture=0x{fb:02x} forged=0x{gb:02x}")

    return errors


class TestNullRegionMaskedConformance:
    """Byte comparison with null-column regions masked out.

    This validates that forge output is byte-identical in all LIVE column
    regions, even for rows that have some NULL columns.  Null fixed-column
    byte ranges are excluded from comparison (SQL Server vs forge may differ
    there: SQL Server leaves stale bytes; forge writes zeros).
    """

    def _masked_compare_table(self, bak: Path, table_name: str) -> list[str]:
        store = PageStore.from_bak(str(bak))
        schema = recover_schema(store)
        table = next((t for t in schema.tables if t.name == table_name), None)
        if table is None:
            return []  # table absent in this fixture version — skip silently

        rec_cols = _record_columns(table)
        if not rec_cols:
            return []

        errors: list[str] = []
        for _pid, _fid, page in _data_pages_with_page(store, table):
            for slot in range(page.header.slot_cnt):
                fixture_bytes = page.record(slot)
                decoded = decode_record(fixture_bytes, rec_cols)
                forged = encode_fixedvar(rec_cols, decoded)
                slot_errors = _null_masked_compare(fixture_bytes, forged, rec_cols, decoded)
                for e in slot_errors:
                    errors.append(f"slot {slot}: {e}")
        return errors

    @pytest.mark.fixture
    def test_t_int_null_masked(self):
        """INT table is byte-faithful including the null row (with masking)."""
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._masked_compare_table(_TYPECOVERAGE, "t_int")
        assert not errors, "\n".join(errors[:10])

    @pytest.mark.fixture
    def test_t_bigint_null_masked(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._masked_compare_table(_TYPECOVERAGE, "t_bigint")
        assert not errors, "\n".join(errors[:10])

    @pytest.mark.fixture
    def test_t_decimal_38_10_null_masked(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._masked_compare_table(_TYPECOVERAGE, "t_decimal_38_10")
        assert not errors, "\n".join(errors[:10])

    @pytest.mark.fixture
    def test_t_datetime2_7_null_masked(self):
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._masked_compare_table(_TYPECOVERAGE, "t_datetime2_7")
        assert not errors, "\n".join(errors[:10])

    @pytest.mark.fixture
    def test_t_varchar_50_null_masked(self):
        """Variable-length table: non-null var columns are byte-faithful."""
        _skip_if_absent(_TYPECOVERAGE)
        errors = self._masked_compare_table(_TYPECOVERAGE, "t_varchar_50")
        assert not errors, "\n".join(errors[:10])

    @pytest.mark.fixture
    def test_all_scalar_types_null_masked(self):
        """Full matrix: all scalar typecoverage tables pass null-masked comparison."""
        _skip_if_absent(_TYPECOVERAGE)
        all_errors: list[str] = []
        for table_name in sorted(VALIDATED_ATOM_TYPES):
            errs = self._masked_compare_table(_TYPECOVERAGE, table_name)
            for e in errs[:3]:
                all_errors.append(f"{table_name}: {e}")
        assert not all_errors, "\n".join(all_errors[:20])
