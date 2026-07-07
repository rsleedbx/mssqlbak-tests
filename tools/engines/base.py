"""Base class for database engine adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class EngineAdapter(ABC):
    """Connects to a running database engine and manages fixture lifecycle.

    Fixture generator scripts call these two methods in order:

    1. ``run_sql(sql, container_sql_path)`` — execute the DDL/DML/BACKUP SQL.
    2. ``extract_backup(container_bak_path, local_path)`` — copy the resulting
       backup file from the engine container to the host filesystem.

    Implementations
    ---------------
    ``SqlServerAdapter``  tools/engines/sqlserver.py — podman + sqlcmd + .bak
    ``PostgresAdapter``   tools/engines/postgres.py  — podman + psql + pg_dump
    ``MySQLAdapter``      tools/engines/mysql.py     — podman + mysql + mysqldump
    ``OracleAdapter``     tools/engines/oracle.py    — podman + sqlplus + RMAN
    """

    @abstractmethod
    def run_sql(self, sql: str, container_sql_path: str) -> None:
        """Write *sql* to *container_sql_path* inside the engine container and
        execute it.  The SQL string should include all DDL, DML, and the
        engine's backup statement (e.g. ``BACKUP DATABASE`` for SQL Server;
        for engines where backup is a shell command the SQL ends after the DML
        and the backup is issued separately by ``extract_backup``).

        Raises ``RuntimeError`` on any non-zero exit from the SQL client.
        """

    @abstractmethod
    def extract_backup(self, container_bak_path: str, local_path: Path) -> int:
        """Copy the backup file at *container_bak_path* inside the engine
        container to *local_path* on the host filesystem.

        Returns the number of bytes written.  Creates parent directories as
        needed.  Raises ``RuntimeError`` on any failure.
        """
