"""Base class for SQL dialect adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod


class SqlDialect(ABC):
    """Translates canonical type names into engine-specific SQL syntax.

    Canonical type names are short, engine-neutral strings whose full list
    is defined in the type matrix modules (e.g. ``tools/matrix/type_matrix.py``
    for the pgbak project, or inline in fixture scripts for mssqlbak).

    Parameters
    ----------
    canonical:
        Short base-type name, e.g. ``"int32"``, ``"varchar"``, ``"uuid"``.
    **params:
        Optional integer precision / scale / length parameters.
        Conventional keys: ``n`` (length), ``p`` (precision), ``s`` (scale).

    Returns
    -------
    str
        The SQL type declaration for this engine, e.g. ``"VARCHAR(20)"``.

    Raises
    ------
    ValueError
        If *canonical* is not recognised by this dialect.
    """

    @abstractmethod
    def sql_type(self, canonical: str, **params: int) -> str:
        ...

    @abstractmethod
    def backup_sql(self, db_name: str, container_bak_path: str) -> str:
        """Return the SQL statement that writes a full backup to *container_bak_path*.

        For SQL Server this is a ``BACKUP DATABASE`` statement.
        For PostgreSQL the backup is a shell command (``pg_dump``), so this
        method should return an empty string and the engine adapter handles it.
        """
        ...
