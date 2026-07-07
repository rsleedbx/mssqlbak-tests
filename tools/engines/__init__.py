"""Database engine adapters.

Provides ``EngineAdapter`` — an ABC whose implementations connect to a
specific database engine, execute SQL, and extract the resulting backup file.

Each adapter wraps the engine's native tooling (sqlcmd + podman for SQL
Server; psql + pg_dump for PostgreSQL; etc.) behind a uniform interface so
fixture generator scripts can be written once and work against any engine.

Usage::

    from tools.engines.sqlserver import SqlServerAdapter

    engine = SqlServerAdapter()
    engine.run_sql(sql_string, container_sql_path="/tmp/load.sql")
    size = engine.extract_backup("/tmp/MyDb.bak", local_path=Path("tests/fixtures/mydb.bak"))
"""
from tools.engines.base import EngineAdapter

__all__ = ["EngineAdapter"]
