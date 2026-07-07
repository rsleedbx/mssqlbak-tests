"""Boot-page database-default collation (DBINFO.dbi_collation) — G57.

The database-default collation id lives at a confirmed fixed byte offset in
boot-page 9 record 0.  ``mssqlbak.catalog.read_dbi_collation`` reads it, and
string columns whose own ``syscolpars.collationid`` is 0 inherit it instead of
falling back blindly to cp1252.

Offset 392 was grounded with a live-engine verifier (see the ``@pytest.mark.engine``
test below and ``_DBI_COLLATION_OFF`` in ``mssqlbak/catalog.py``):

* All four container defaults (SS2017/2019/2022/2025 →
  ``SQL_Latin1_General_CP1_CI_AS``) store ``0x3400D008`` there — the exact value
  ``COLLATIONPROPERTY(..., 'CollationID')`` reports.
* A database created ``COLLATE Greek_CI_AS`` stores ``0x0000D007`` there, i.e.
  the field tracks the actual database collation rather than a fixed constant.
"""
from __future__ import annotations

import pytest

from mssqlbak.catalog import (
    _DBI_COLLATION_OFF,
    _dbi_collation_from_boot_record,
    read_dbi_collation,
    recover_schema,
)
from mssqlbak.pages import PageStore
from mssqlbak.types import _codec_for_collation, is_known_collation_sortid

from tests.conftest import FIXTURE_BAK

# The default collation of every fixture-building container
# (SQL_Latin1_General_CP1_CI_AS) — verified against the live engine.
_DEFAULT_DB_COLLATION_ID = 0x3400D008
_STRING_XTYPES = frozenset({167, 175, 231, 239, 99})  # varchar/char/nvarchar/nchar/(n)text


@pytest.mark.fixture
def test_read_dbi_collation_matches_container_default() -> None:
    """The DB-default collation reads back as the container default (cp1252)."""
    if not FIXTURE_BAK.exists():
        pytest.skip(f"reference fixture missing: {FIXTURE_BAK}")
    store = PageStore.from_bak(FIXTURE_BAK)
    coll = read_dbi_collation(store)
    assert coll == _DEFAULT_DB_COLLATION_ID
    assert is_known_collation_sortid(coll)
    assert _codec_for_collation(coll) == "cp1252"


@pytest.mark.fixture
def test_schema_exposes_db_collation_id() -> None:
    """recover_schema populates Schema.db_collation_id from the boot page."""
    if not FIXTURE_BAK.exists():
        pytest.skip(f"reference fixture missing: {FIXTURE_BAK}")
    store = PageStore.from_bak(FIXTURE_BAK)
    schema = recover_schema(store)
    assert schema.db_collation_id == _DEFAULT_DB_COLLATION_ID


@pytest.mark.fixture
def test_string_columns_have_a_resolvable_collation() -> None:
    """Every string column resolves to a collation id (own or inherited)."""
    if not FIXTURE_BAK.exists():
        pytest.skip(f"reference fixture missing: {FIXTURE_BAK}")
    store = PageStore.from_bak(FIXTURE_BAK)
    schema = recover_schema(store)
    assert schema.db_collation_id is not None
    for table in schema.tables:
        for col in table.columns:
            if col.type_id in _STRING_XTYPES:
                # Either the column carried its own collation, or it inherited
                # the DB default — never left at the blind-cp1252 zero value.
                assert col.collation_id != 0, f"{table.name}.{col.name}"


def test_dbi_collation_from_boot_record_parses_offset_392() -> None:
    """The parser takes the uint32 LE at the confirmed fixed offset."""
    assert _DBI_COLLATION_OFF == 392
    record = bytearray(_DBI_COLLATION_OFF + 4)
    record[_DBI_COLLATION_OFF : _DBI_COLLATION_OFF + 4] = (0x0000D007).to_bytes(4, "little")
    coll = _dbi_collation_from_boot_record(bytes(record))
    assert coll == 0x0000D007  # Greek_CI_AS, low byte 0x07 → cp1253
    assert _codec_for_collation(coll) == "cp1253"


def test_dbi_collation_from_boot_record_none_on_short_record() -> None:
    """A boot record too short to hold the field degrades to None, not a crash."""
    assert _dbi_collation_from_boot_record(b"\x00" * 100) is None


@pytest.mark.fixture
@pytest.mark.engine
def test_dbi_collation_matches_live_engine() -> None:
    """Verifier: the boot-page value equals the engine's COLLATIONPROPERTY id.

    Grounds offset 392 against an independent source (the running SQL Server)
    rather than trusting the empirical scan alone.  Skips when no engine is
    reachable so ordinary offline runs are unaffected.
    """
    if not FIXTURE_BAK.exists():
        pytest.skip(f"reference fixture missing: {FIXTURE_BAK}")
    from tests.engine_support import EngineUnavailable, connect_engine

    try:
        conn = connect_engine()
    except EngineUnavailable as exc:
        pytest.skip(str(exc))
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT CONVERT(int, COLLATIONPROPERTY("
            "CONVERT(sysname, SERVERPROPERTY('Collation')), 'CollationID'))"
        )
        engine_collid = cur.fetchone()[0] & 0xFFFFFFFF
    finally:
        conn.close()

    store = PageStore.from_bak(FIXTURE_BAK)
    assert read_dbi_collation(store) == engine_collid
