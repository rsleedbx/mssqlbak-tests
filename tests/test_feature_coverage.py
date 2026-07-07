"""Level-1 feature coverage tests — temporal tables, COMPRESS(), UTF-8 collation,
non-clustered columnstore index (NCCI), ledger tables, and graph tables.

All tests use the ``featurecoverage_full.bak`` fixture which was generated from a
local SQL Server 2022 (Podman) via forgedb.  The fixture contains:

* ``temporal_current``  — system-versioned (temporal) table, 50 rows.
* ``temporal_history``  — auto-created history table, 10 rows (updated rows).
* ``compress_col``      — table with a ``VARBINARY(MAX)`` column storing
                         ``COMPRESS(nvarchar_text)`` gzip blobs, 20 rows.
* ``utf8_collation``    — table with three varchar/nvarchar columns: one with
                         standard Latin-1 collation, one with UTF-8 collation
                         (``_SC_UTF8``), and one nvarchar, 6 rows.
* ``ncci_table``        — normal row-store table with a non-clustered columnstore
                         index (NCCI).  1 024 rows.
* ``ledger_account``    — append-only ledger table (``LEDGER = ON, APPEND_ONLY = ON``).
                         3 rows.  The engine auto-adds two hidden bigint columns
                         (``ledger_start_transaction_id``,
                         ``ledger_start_sequence_number``) which mssqlbak exposes.
* ``graph_person``      — ``AS NODE`` graph table.  3 nodes (Alice, Bob, Carol).
                         mssqlbak synthesises ``$node_id_<UUID>`` from the physical
                         ``graph_id_<UUID>`` column.
* ``graph_follows``     — ``AS EDGE`` graph table.  2 directed edges.  mssqlbak
                         synthesises ``$edge_id``, ``$from_id``, and ``$to_id``
                         JSON columns using the ``obj_to_name`` lookup from the schema.

Fixture generation:
    python tools/make_feature_fixture.py   # (or via forgedb + manual sqlcmd)
"""
from __future__ import annotations

import gzip
import json
from decimal import Decimal
from pathlib import Path

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.inspect import classify_table
from mssqlbak.pages import AnyPageStore, PageStore
from mssqlbak.rows import read_table_rows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _store(path: Path) -> AnyPageStore:
    return PageStore.from_bak(path)


def _tables(path: Path) -> dict:
    return {t.name: t for t in recover_schema(_store(path)).tables}


def _rows(path: Path, table: str) -> list[dict]:
    store = _store(path)
    schema = recover_schema(store)
    tbl = next(t for t in schema.tables if t.name == table)
    return list(read_table_rows(store, tbl, schema.obj_to_name))


# ---------------------------------------------------------------------------
# Temporal table (system-versioned)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_temporal_current_row_count(fixture_bak_feature: Path) -> None:
    """The current table holds exactly 50 rows (1–50 inserted; none deleted)."""
    rows = _rows(fixture_bak_feature, "temporal_current")
    assert len(rows) == 50


@pytest.mark.fixture
def test_temporal_current_classify_supported(fixture_bak_feature: Path) -> None:
    """Temporal tables with datetime2 period columns are classified as supported.

    System-versioned tables look like ordinary tables from the catalog's
    perspective: the PERIOD columns are stored as regular DATETIME2 columns
    in the data rowset.  No special handling is required.
    """
    tables = _tables(fixture_bak_feature)
    assert classify_table(tables["temporal_current"]).supported


@pytest.mark.fixture
def test_temporal_current_period_columns_decode(fixture_bak_feature: Path) -> None:
    """``valid_from`` and ``valid_to`` decode to Python datetime objects.

    The open-ended ``valid_to`` sentinel value is 9999-12-31 23:59:59.999999,
    confirming that datetime2 max-value decode is correct for unmodified rows.
    """
    rows = _rows(fixture_bak_feature, "temporal_current")
    assert all("valid_from" in r for r in rows)
    assert all("valid_to" in r for r in rows)
    # All 50 rows in the current table are the live versions — their valid_to
    # is the open-end sentinel (9999-12-31 23:59:59.999999).  The 10 updated
    # rows' old values were pushed to temporal_history, not removed here.
    sentinels = [r for r in rows if r["valid_to"].year == 9999]
    assert len(sentinels) == 50, (
        f"expected all 50 current rows to have sentinel valid_to, got {len(sentinels)}"
    )


@pytest.mark.fixture
def test_temporal_current_updated_rows_have_new_value(fixture_bak_feature: Path) -> None:
    """Rows updated (id % 5 == 0) have value = original + 100."""
    rows = _rows(fixture_bak_feature, "temporal_current")
    by_id = {r["id"]: r for r in rows}
    for i in range(1, 51):
        expected = Decimal(str(i * 1.5)) + (100 if i % 5 == 0 else 0)
        assert by_id[i]["value"] == pytest.approx(float(expected), abs=0.01), (
            f"id={i} expected value≈{float(expected):.2f}, got {by_id[i]['value']}"
        )


@pytest.mark.fixture
def test_temporal_current_generated_always_type(fixture_bak_feature: Path) -> None:
    """Period columns on the current table have generated_always_type 1 / 2.

    ``valid_from`` (AS_ROW_START) must have ``generated_always_type=1`` and
    ``valid_to`` (AS_ROW_END) must have ``generated_always_type=2``.
    Non-period columns must have ``generated_always_type=0``.

    Confirmed from featurecoverage_full.bak via raw syscolpars page read:
    syscolpars.status bit 28 (0x10000000) = AS_ROW_START, bit 29 (0x20000000)
    = AS_ROW_END.  V13 — §12.2 of BAK_FORMAT_SPEC.
    """
    tables = _tables(fixture_bak_feature)
    cols = {c.name: c for c in tables["temporal_current"].columns}
    assert cols["valid_from"].generated_always_type == 1, (
        "valid_from should be AS_ROW_START (generated_always_type=1)"
    )
    assert cols["valid_to"].generated_always_type == 2, (
        "valid_to should be AS_ROW_END (generated_always_type=2)"
    )
    assert cols["id"].generated_always_type == 0
    assert cols["value"].generated_always_type == 0


@pytest.mark.fixture
def test_temporal_history_generated_always_type_zero(fixture_bak_feature: Path) -> None:
    """Period columns on the history table have generated_always_type=0.

    The history (archive) table's period columns are plain datetime2 columns;
    the AS_ROW_START / AS_ROW_END flags are only set on the current table's
    syscolpars rows.
    """
    tables = _tables(fixture_bak_feature)
    cols = {c.name: c for c in tables["temporal_history"].columns}
    assert cols["valid_from"].generated_always_type == 0, (
        "history valid_from should be a regular datetime2 (generated_always_type=0)"
    )
    assert cols["valid_to"].generated_always_type == 0, (
        "history valid_to should be a regular datetime2 (generated_always_type=0)"
    )


@pytest.mark.fixture
def test_temporal_hidden_period_columns_is_hidden(fixture_bak_temporal_hidden: Path) -> None:
    """Hidden period columns (HIDDEN keyword) have is_hidden=True.

    ``temporal_hidden.valid_from`` and ``valid_to`` were declared with the
    ``GENERATED ALWAYS AS ROW START HIDDEN`` keyword.  mssqlbak must decode
    ``syscolpars.status`` bit 13 (0x00002000) as ``is_hidden=True``.

    Confirmed from temporal_hidden_full.bak via PageStore XOR analysis:
    status of hidden col = 0x10002001; status of visible col = 0x10000001;
    XOR = 0x00002000 (bit 13).  V13 — §12.2 of BAK_FORMAT_SPEC.
    """
    store = _store(fixture_bak_temporal_hidden)
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}
    hidden_cols  = {c.name: c for c in tables["temporal_hidden"].columns}
    visible_cols = {c.name: c for c in tables["temporal_visible"].columns}

    # HIDDEN period columns — is_hidden must be True.
    assert hidden_cols["valid_from"].is_hidden, "temporal_hidden.valid_from: expected is_hidden=True"
    assert hidden_cols["valid_to"].is_hidden,   "temporal_hidden.valid_to:   expected is_hidden=True"
    # Non-period columns in the same table are NOT hidden.
    assert not hidden_cols["id"].is_hidden
    assert not hidden_cols["value"].is_hidden

    # Visible period columns — is_hidden must be False.
    assert not visible_cols["valid_from"].is_hidden, "temporal_visible.valid_from: expected is_hidden=False"
    assert not visible_cols["valid_to"].is_hidden,   "temporal_visible.valid_to:   expected is_hidden=False"


@pytest.mark.fixture
def test_temporal_hidden_generated_always_type_unchanged(fixture_bak_temporal_hidden: Path) -> None:
    """HIDDEN keyword does not affect generated_always_type.

    Both the hidden and the visible period columns must have
    generated_always_type=1 (AS_ROW_START) and =2 (AS_ROW_END).
    The HIDDEN keyword only sets bit 13; bits 28-29 are independently set.
    """
    store = _store(fixture_bak_temporal_hidden)
    schema = recover_schema(store)
    tables = {t.name: t for t in schema.tables}
    for tbl_name in ("temporal_hidden", "temporal_visible"):
        cols = {c.name: c for c in tables[tbl_name].columns}
        assert cols["valid_from"].generated_always_type == 1, (
            f"{tbl_name}.valid_from: expected generated_always_type=1 (AS_ROW_START)"
        )
        assert cols["valid_to"].generated_always_type == 2, (
            f"{tbl_name}.valid_to: expected generated_always_type=2 (AS_ROW_END)"
        )


@pytest.mark.fixture
def test_temporal_history_row_count(fixture_bak_feature: Path) -> None:
    """The history table holds the 10 superseded rows (id % 5 == 0)."""
    rows = _rows(fixture_bak_feature, "temporal_history")
    assert len(rows) == 10


@pytest.mark.fixture
def test_temporal_history_classify_supported(fixture_bak_feature: Path) -> None:
    """The auto-created history table is a plain heap and classified as supported."""
    tables = _tables(fixture_bak_feature)
    assert classify_table(tables["temporal_history"]).supported


@pytest.mark.fixture
def test_temporal_history_ids_are_multiples_of_five(fixture_bak_feature: Path) -> None:
    """History rows come only from the 10 rows updated (id 5, 10, …, 50)."""
    rows = _rows(fixture_bak_feature, "temporal_history")
    ids = {r["id"] for r in rows}
    assert ids == {5, 10, 15, 20, 25, 30, 35, 40, 45, 50}


# ---------------------------------------------------------------------------
# COMPRESS() column (gzip varbinary blob)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_compress_col_row_count(fixture_bak_feature: Path) -> None:
    """compress_col contains 20 rows."""
    rows = _rows(fixture_bak_feature, "compress_col")
    assert len(rows) == 20


@pytest.mark.fixture
def test_compress_col_blob_is_gzip(fixture_bak_feature: Path) -> None:
    """The ``compressed`` column is returned as raw bytes starting with the
    gzip magic bytes ``\\x1f\\x8b``.

    The COMPRESS() T-SQL function stores a gzip blob in a VARBINARY(MAX)
    column.  mssqlbak correctly returns this as a Python ``bytes`` object;
    callers that want the decompressed value must call ``gzip.decompress``
    themselves.
    """
    rows = _rows(fixture_bak_feature, "compress_col")
    for r in rows:
        blob = r["compressed"]
        assert isinstance(blob, bytes), f"id={r['id']}: expected bytes, got {type(blob)}"
        assert blob[:2] == b"\x1f\x8b", (
            f"id={r['id']}: expected gzip magic 1f8b, got {blob[:2].hex()}"
        )


@pytest.mark.fixture
def test_compress_col_gzip_roundtrip(fixture_bak_feature: Path) -> None:
    """Decompressing the blob and decoding as UTF-16LE reproduces ``raw_text``.

    SQL Server's COMPRESS() compresses the internal UTF-16LE byte representation
    of NVARCHAR data.  Decompressing with gzip and decoding as UTF-16LE exactly
    reproduces the original string value.
    """
    rows = _rows(fixture_bak_feature, "compress_col")
    for r in rows:
        decompressed = gzip.decompress(r["compressed"]).decode("utf-16-le")
        assert decompressed == r["raw_text"], (
            f"id={r['id']}: roundtrip mismatch"
        )


# ---------------------------------------------------------------------------
# UTF-8 collation varchar
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_utf8_collation_classify_supported(fixture_bak_feature: Path) -> None:
    """UTF-8 collation tables are currently classified as supported (no catalog
    flag triggers a skip).  The limitation surfaces at decode time for non-ASCII
    characters.
    """
    tables = _tables(fixture_bak_feature)
    assert classify_table(tables["utf8_collation"]).supported


@pytest.mark.fixture
def test_utf8_collation_ascii_chars_correct(fixture_bak_feature: Path) -> None:
    """Pure-ASCII values decode correctly even for UTF-8-collated columns.

    When all characters are below 0x80, UTF-8 and Latin-1 byte sequences are
    identical, so the current Latin-1 decoder produces the right result.
    """
    rows = _rows(fixture_bak_feature, "utf8_collation")
    by_id = {r["id"]: r for r in rows}
    # All three ASCII rows (ids 1, 2, 3) should match across all columns
    for i in (1, 2, 3):
        assert by_id[i]["utf8"] == by_id[i]["wide"], (
            f"id={i}: utf8={by_id[i]['utf8']!r} wide={by_id[i]['wide']!r}"
        )


@pytest.mark.fixture
def test_utf8_collation_non_ascii_chars_correct(fixture_bak_feature: Path) -> None:
    """Non-ASCII UTF-8 characters (é, ï, …) decode to the same string as the
    nvarchar ``wide`` column.

    SQL Server stores UTF-8 collated (``_SC_UTF8``) varchar bytes as UTF-8 on
    disk.  The decoder detects this via ``syscolpars.collationid`` bit 0x100 and
    decodes those columns as UTF-8 instead of Latin-1 / cp1252.
    """
    rows = _rows(fixture_bak_feature, "utf8_collation")
    by_id = {r["id"]: r for r in rows}
    for i in (4, 5, 6):
        assert by_id[i]["utf8"] == by_id[i]["wide"], (
            f"id={i}: utf8={by_id[i]['utf8']!r} != wide={by_id[i]['wide']!r}"
        )


# ---------------------------------------------------------------------------
# Non-clustered columnstore index (NCCI)
# ---------------------------------------------------------------------------

@pytest.mark.fixture
def test_ncci_table_classify_supported(fixture_bak_feature: Path) -> None:
    """A row-store table with an NCCI is classified as supported.

    The NCCI is a secondary index.  The primary data rowset (clustered on ``id``)
    is a normal row-store B-tree that mssqlbak reads without difficulty.
    """
    tables = _tables(fixture_bak_feature)
    assert classify_table(tables["ncci_table"]).supported


@pytest.mark.fixture
def test_ncci_table_row_count(fixture_bak_feature: Path) -> None:
    """ncci_table contains 1 024 rows, readable via the clustered primary key."""
    rows = _rows(fixture_bak_feature, "ncci_table")
    assert len(rows) == 1024


@pytest.mark.fixture
def test_ncci_table_values(fixture_bak_feature: Path) -> None:
    """Row values decode correctly: code = id % 100, amount = id * 0.75."""
    rows = _rows(fixture_bak_feature, "ncci_table")
    by_id = {r["id"]: r for r in rows}
    for i in (1, 100, 512, 1024):
        r = by_id[i]
        assert r["code"] == i % 100, f"id={i}: code"
        assert r["name"] == f"row{i}", f"id={i}: name"
        assert float(r["amount"]) == pytest.approx(i * 0.75, abs=0.01), f"id={i}: amount"


# ---------------------------------------------------------------------------
# Ledger table (append-only)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_ledger_user_columns_decode(fixture_bak_feature: Path) -> None:
    """Ledger table: user-defined columns decode normally.

    ``ledger_account`` is an append-only ledger table.  The three user columns
    (``id`` int, ``name`` nvarchar, ``balance`` decimal) must round-trip
    correctly alongside the engine-generated hidden columns.
    """
    rows = {r["id"]: r for r in _rows(fixture_bak_feature, "ledger_account")}
    assert set(rows) == {1, 2, 3}
    assert rows[1]["name"] == "Alice"
    assert rows[1]["balance"] == Decimal("1000.00")
    assert rows[2]["name"] == "Bob"
    assert rows[3]["balance"] == Decimal("750.50")


@pytest.mark.fixture
def test_ledger_hidden_columns_exposed(fixture_bak_feature: Path) -> None:
    """Ledger table: mssqlbak exposes the engine-generated hidden columns.

    The engine auto-adds ``ledger_start_transaction_id`` (bigint) and
    ``ledger_start_sequence_number`` (bigint) with ``is_hidden=1`` in
    sys.columns.  These have physical storage and are decoded by mssqlbak
    as regular bigint columns, giving visibility into when each row was
    committed (which SELECT * normally suppresses).
    """
    tables = _tables(fixture_bak_feature)
    col_names = [c.name for c in tables["ledger_account"].columns]
    assert "ledger_start_transaction_id" in col_names
    assert "ledger_start_sequence_number" in col_names
    rows = list(_rows(fixture_bak_feature, "ledger_account"))
    for r in rows:
        # transaction IDs are positive bigints
        assert isinstance(r["ledger_start_transaction_id"], int)
        assert r["ledger_start_transaction_id"] > 0
        assert isinstance(r["ledger_start_sequence_number"], int)


# ---------------------------------------------------------------------------
# Graph tables (NODE / EDGE)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_graph_node_schema(fixture_bak_feature: Path) -> None:
    """graph_person is detected as a NODE table; physical + computed columns present."""
    tables = _tables(fixture_bak_feature)
    assert "graph_person" in tables
    t = tables["graph_person"]
    assert t.is_node
    assert not t.is_edge
    col_names = [c.name for c in t.columns]
    # At least one $node_id_<UUID> computed column
    assert any(n.startswith("$node_id_") for n in col_names)
    # At least one graph_id_<UUID> physical column
    assert any(n.startswith("graph_id_") for n in col_names)
    # User column present
    assert "name" in col_names


@pytest.mark.fixture
def test_graph_node_rows_and_node_id(fixture_bak_feature: Path) -> None:
    """graph_person rows decode; $node_id JSON is synthesised correctly.

    Expected: 3 nodes — Alice (id=0), Bob (id=1), Carol (id=2).
    $node_id format: {"type":"node","schema":"dbo","table":"graph_person","id":N}
    """
    rows = _rows(fixture_bak_feature, "graph_person")
    by_name = {r["name"]: r for r in rows}
    assert set(by_name) == {"Alice", "Bob", "Carol"}
    # Find the $node_id column (name is $node_id_<UUID>)
    node_id_key = next(k for k in by_name["Alice"] if k.startswith("$node_id_"))
    for name, expected_id in [("Alice", 0), ("Bob", 1), ("Carol", 2)]:
        nid = json.loads(by_name[name][node_id_key])
        assert nid["type"] == "node"
        assert nid["table"] == "graph_person"
        assert nid["id"] == expected_id


@pytest.mark.fixture
def test_graph_edge_schema(fixture_bak_feature: Path) -> None:
    """graph_follows is detected as an EDGE table; endpoint columns are present."""
    tables = _tables(fixture_bak_feature)
    assert "graph_follows" in tables
    t = tables["graph_follows"]
    assert t.is_edge
    assert not t.is_node
    col_names = [c.name for c in t.columns]
    assert any(n.startswith("$edge_id_") for n in col_names)
    assert any(n.startswith("$from_id_") for n in col_names)
    assert any(n.startswith("$to_id_") for n in col_names)
    assert "since" in col_names


@pytest.mark.fixture
def test_graph_edge_rows_and_endpoint_synthesis(fixture_bak_feature: Path) -> None:
    """graph_follows $from_id/$to_id correctly reference graph_person rows.

    Edge 0: Alice (id=0) → Bob (id=1)   since 2020-01-01
    Edge 1: Alice (id=0) → Carol (id=2) since 2021-06-01
    """
    rows = _rows(fixture_bak_feature, "graph_follows")
    assert len(rows) == 2
    from_key = next(k for k in rows[0] if k.startswith("$from_id_"))
    to_key = next(k for k in rows[0] if k.startswith("$to_id_"))
    by_edge_id = {json.loads(r[next(k for k in r if k.startswith("$edge_id_"))])["id"]: r
                  for r in rows}
    e0 = by_edge_id[0]
    e1 = by_edge_id[1]
    from0 = json.loads(e0[from_key])
    to0 = json.loads(e0[to_key])
    to1 = json.loads(e1[to_key])
    assert from0["table"] == "graph_person"
    assert from0["id"] == 0   # Alice
    assert to0["table"] == "graph_person"
    assert to0["id"] == 1     # Bob
    assert to1["id"] == 2     # Carol


# ---------------------------------------------------------------------------
# long_text (Gap 2: varchar/nvarchar/char columns longer than 200 chars)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_long_text_row_count(fixture_bak_feature: Path) -> None:
    """long_text contains 3 rows: lex-min, lex-max, and a NULL row."""
    rows = _rows(fixture_bak_feature, "long_text")
    assert len(rows) == 3


@pytest.mark.fixture
def test_long_text_long_varchar_length(fixture_bak_feature: Path) -> None:
    """long_varchar values are exactly 500 characters — well above the old 200-char
    ground-truth truncation limit — confirming that register_bak.py captures the
    full string via the NVARCHAR(4000) cast.
    """
    rows = _rows(fixture_bak_feature, "long_text")
    by_id = {r["id"]: r for r in rows}
    assert by_id[1]["long_varchar"] == "A" * 500, "min row: long_varchar wrong"
    assert by_id[2]["long_varchar"] == "Z" * 500, "max row: long_varchar wrong"
    assert by_id[3]["long_varchar"] is None, "null row: long_varchar should be None"


@pytest.mark.fixture
def test_long_text_long_nvarchar_length(fixture_bak_feature: Path) -> None:
    """long_nvarchar values are exactly 500 characters."""
    rows = _rows(fixture_bak_feature, "long_text")
    by_id = {r["id"]: r for r in rows}
    assert by_id[1]["long_nvarchar"] == "A" * 500, "min row: long_nvarchar wrong"
    assert by_id[2]["long_nvarchar"] == "Z" * 500, "max row: long_nvarchar wrong"
    assert by_id[3]["long_nvarchar"] is None, "null row: long_nvarchar should be None"


@pytest.mark.fixture
def test_long_text_long_char_length(fixture_bak_feature: Path) -> None:
    """long_char is CHAR(500); after RTRIM the value is 500 non-space characters
    for non-NULL rows.  This exercises the NVARCHAR(4000) ground-truth cast for
    fixed-width char columns wider than 200 bytes.
    """
    rows = _rows(fixture_bak_feature, "long_text")
    by_id = {r["id"]: r for r in rows}
    # mssqlbak returns the raw padded value; strip trailing spaces for comparison.
    min_val = by_id[1]["long_char"]
    assert min_val is not None
    assert min_val.rstrip() == "A" * 500, f"min row: long_char wrong ({len(min_val)=})"
    max_val = by_id[2]["long_char"]
    assert max_val is not None
    assert max_val.rstrip() == "Z" * 500, "max row: long_char wrong"
    assert by_id[3]["long_char"] is None, "null row: long_char should be None"


# ---------------------------------------------------------------------------
# memory_oltp (In-Memory OLTP — now supported via XTP decoder)
# ---------------------------------------------------------------------------


@pytest.mark.fixture
def test_memory_oltp_classified_as_supported(fixture_bak_feature: Path) -> None:
    """memory_oltp is an In-Memory OLTP table that is now supported via the
    XTP compact/WAL block decoder.  classify_table should return supported=True
    and the table should extract the expected 3 rows from the fixture.
    """
    tables = _tables(fixture_bak_feature)
    assert "memory_oltp" in tables, (
        "memory_oltp table missing from catalog — was the fixture generated on SS2014+?"
    )
    result = classify_table(tables["memory_oltp"])
    assert result.supported, (
        f"memory_oltp should be classified as supported; skip_code={result.skip_code!r}"
    )
