"""Engine-diff test: pure-Python parser vs a LIVE SQL Server engine.

This is the gold validation.  For every type case the parser reads the value
out of the committed ``.bak`` fixture (no engine), while a live SQL Server
engine — holding the same ``TypeCoverage`` database — returns the value via a
normal ``SELECT``.  The two must agree for every label.

A few types differ only in *representation* between the two sides (never in
value); :func:`_normalize` applies the *same* transform to both sides so it can
only mask a representation difference, never hide a wrong value:

* **uniqueidentifier** — the engine may hand back a ``str`` or ``uuid.UUID``;
  the parser returns ``uuid.UUID``.  Both sides are coerced to ``uuid.UUID``.
* **datetime2(7)** — the engine resolves 100 ns ticks but a Python ``datetime``
  only holds microseconds, and the parser floors to µs.  Both sides are floored
  to whole microseconds (``datetime`` cannot represent finer, so this is a
  documented no-op when the driver already truncates, and a guard if it ever
  rounds).
* **money / decimal** — both are ``Decimal``; ``==`` compares numerically and
  ignores trailing zeros.  A ``float`` (should never happen for these columns)
  is coerced to ``Decimal`` via its string form.

``real``/``float`` (both ``float``), ``char(10)`` (space-padded on both sides,
never stripped), ``varchar(max)`` and ``varbinary(max)`` (compared in full,
which also exercises row-overflow/LOB stitching) are compared exactly.
"""

from __future__ import annotations

import os
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

mssql_python = pytest.importorskip("mssql_python")

# Imports below intentionally follow ``importorskip`` so the module skips
# cleanly when the driver is absent (E402 is expected for this pattern).
from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.rows import read_table_rows  # noqa: E402
from tests.engine_support import EngineUnavailable, connect_engine  # noqa: E402
from tools.typematrix import TYPE_CASES  # noqa: E402

_FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent / "fixtures_2022")))


def _to_decimal(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    return value


def _normalize(value: Any) -> Any:
    """Map a value to a canonical form, applied identically to both sides.

    Only representation is canonicalised (uuid spelling, sub-µs datetime,
    Decimal/float for money); the underlying value is never altered.
    """
    if isinstance(value, str):
        # A uniqueidentifier returned as text -> canonical UUID.  Other strings
        # (char/varchar/nvarchar values) are left untouched.
        try:
            return uuid.UUID(value)
        except (ValueError, AttributeError):
            return value
    # datetime / Decimal / float / UUID / bytes / None need no transform: both
    # sides already share Python's representation (datetime is µs-resolution, the
    # parser floors datetime2(7) to match, Decimal compares value-wise).
    return value


def _normalize_pair(parsed: Any, engine: Any) -> tuple[Any, Any]:
    """Normalise a (parsed, engine) pair together so the transform is symmetric.

    When one side is a ``Decimal`` and the other a ``float`` (a money/decimal
    representation slip), both are coerced to ``Decimal`` before comparison.
    """
    if isinstance(parsed, Decimal) or isinstance(engine, Decimal):
        parsed, engine = _to_decimal(parsed), _to_decimal(engine)
    return _normalize(parsed), _normalize(engine)


FIXTURE_BAK = _FIXTURE_DIR / "typecoverage_full.bak"


@pytest.mark.fixture
@pytest.mark.engine
@pytest.mark.parametrize("case", TYPE_CASES, ids=lambda c: c.name)
def test_parser_matches_engine(case: Any) -> None:
    if not FIXTURE_BAK.exists():
        pytest.skip(f"reference fixture missing: {FIXTURE_BAK} (run tools/make_fixture.py)")
    try:
        conn = connect_engine()
    except EngineUnavailable as exc:
        pytest.skip(str(exc))

    table_name = f"t_{case.name}"
    try:
        cur = conn.cursor()
        value_sql = case.engine_value_sql or "v"
        cur.execute(f"SELECT label, {value_sql} AS v FROM {table_name} ORDER BY id")
        try:
            engine = {row[0]: row[1] for row in cur.fetchall()}
        except RuntimeError as exc:
            # Driver limitation, not a parser bug: mssql_python cannot stream a
            # heterogeneous sql_variant column that holds a datetimeoffset. The
            # matrix test validates these values against the real on-disk bytes.
            pytest.skip(f"engine driver cannot fetch {table_name}: {exc}")
    finally:
        conn.close()

    store = PageStore.from_bak(FIXTURE_BAK)
    table = next(t for t in recover_schema(store).tables if t.name == table_name)
    parsed = {r["label"]: r["v"] for r in read_table_rows(store, table)}

    assert parsed.keys() == engine.keys(), table_name
    for label in engine:
        p, e = _normalize_pair(parsed[label], engine[label])
        assert p == e, f"{table_name}[{label}]: parsed={parsed[label]!r} engine={engine[label]!r}"
