"""Live-engine connection helper for the engine-diff test.

Returns a ``mssql_python`` connection to the SQL Server engine that holds the
same ``TypeCoverage`` database the committed ``.bak`` fixture was built from.
The engine's query results are the gold standard the pure-Python parser is
validated against (``tests/test_engine_diff.py``).

Connection parameters are read from the environment so nothing secret is
committed; only ``ENGINE_DB_PASSWORD`` has no default.  When the password is
unset or the connection cannot be established, :func:`connect_engine` raises
:class:`EngineUnavailable`, which the test converts into a skip so ordinary
``pytest`` runs (without a live engine) are unaffected.
"""

from __future__ import annotations

import os
from typing import Any

# mssql_python is an optional/dev dependency; import lazily so this module can
# be imported (and the test can skip) even when the driver is absent.


class EngineUnavailable(RuntimeError):
    """Raised when the live SQL Server engine cannot be reached."""


def _conn_string(password: str) -> str:
    host = os.environ.get("ENGINE_DB_HOST", "127.0.0.1")
    port = os.environ.get("ENGINE_DB_PORT", "30004")
    user = os.environ.get("ENGINE_DB_USER", "sa")
    database = os.environ.get("ENGINE_DB_NAME", "TypeCoverage")
    return (
        f"Server={host},{port};Database={database};Uid={user};Pwd={password};"
        "Encrypt=yes;TrustServerCertificate=yes;"
    )


def connect_engine() -> Any:
    """Return a live ``mssql_python`` connection to the type-coverage engine.

    Raises :class:`EngineUnavailable` if ``ENGINE_DB_PASSWORD`` is unset,
    the ``mssql_python`` driver is missing, or the connection attempt fails.
    """
    password = os.environ.get("ENGINE_DB_PASSWORD")
    if not password:
        raise EngineUnavailable(
            "ENGINE_DB_PASSWORD is unset; export it to run the engine-diff test"
        )
    try:
        import mssql_python
    except ImportError as exc:  # pragma: no cover - driver is a dev extra
        raise EngineUnavailable(f"mssql_python is not installed: {exc}") from exc
    try:
        return mssql_python.connect(_conn_string(password))
    except Exception as exc:  # noqa: BLE001 - surface any driver/connect failure as a skip
        raise EngineUnavailable(f"could not connect to SQL Server engine: {exc}") from exc
