"""SQL Server engine adapter — thin wrapper over ``tools.fixture_utils``."""
from __future__ import annotations

from pathlib import Path

from tools.engines.base import EngineAdapter
from tools.fixture_utils import (
    _copy_out,
    _load_and_backup,
    fixture_credentials,
    sqlcmd_base,
)


class SqlServerAdapter(EngineAdapter):
    """Executes SQL against a running SQL Server Podman container.

    Credentials and container discovery follow the same convention as all
    other fixture generators: ``FIXTURE_DBA_PASSWORD`` (required),
    ``FIXTURE_DBA_USER`` (default: ``sa``), ``FIXTURE_CONTAINER`` (optional
    override for container auto-discovery).

    Instantiation calls ``fixture_credentials()`` immediately, so the adapter
    will exit with a helpful error message if the password is missing.

    Example
    -------
    ::

        dialect = SqlServerDialect()
        engine  = SqlServerAdapter()

        sql = build_sql(dialect)                          # pure function
        engine.run_sql(sql, "/tmp/load_mydb.sql")         # executes in container
        size = engine.extract_backup("/tmp/MyDb.bak",
                                     Path("tests/fixtures/mydb.bak"))
        print(f"wrote {size:,} bytes")
    """

    def __init__(self) -> None:
        user, password, container = fixture_credentials()
        self._container = container
        self._cmd = sqlcmd_base(user, password, container)
        print(f"using container {container} as {user}")

    def run_sql(self, sql: str, container_sql_path: str) -> None:
        """Write *sql* into the container as *container_sql_path* and execute
        it with ``sqlcmd``.  The SQL string must include the ``BACKUP DATABASE``
        statement — no separate backup step is needed for SQL Server."""
        _load_and_backup(self._container, self._cmd, sql, container_sql_path)

    def extract_backup(self, container_bak_path: str, local_path: Path) -> int:
        """``podman cp`` the .bak file out of the container."""
        return _copy_out(self._container, container_bak_path, local_path)
