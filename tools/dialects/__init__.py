"""SQL dialect abstraction layer.

Provides ``SqlDialect`` — an ABC whose implementations translate canonical
type names into engine-specific SQL syntax.

Canonical type names are short, engine-neutral strings (e.g. ``"int32"``,
``"timestamptz"``, ``"varchar"``) that live in the type matrix modules.
Each ``SqlDialect`` subclass maps those names to the SQL syntax its engine
understands.

Usage::

    from tools.dialects.sqlserver import SqlServerDialect

    dialect = SqlServerDialect()
    col_type = dialect.sql_type("varchar", n=20)   # → "varchar(20)"
    col_type = dialect.sql_type("timestamptz")     # → "datetimeoffset(7)"
"""
from tools.dialects.base import SqlDialect

__all__ = ["SqlDialect"]
