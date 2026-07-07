"""SQL Server (T-SQL) dialect implementation."""
from __future__ import annotations

from tools.dialects.base import SqlDialect


class SqlServerDialect(SqlDialect):
    """Maps canonical type names to T-SQL syntax.

    Supported canonical names and their default SQL Server equivalents:

    Integers / boolean
        int8 → tinyint, int16 → smallint, int32 → int, int64 → bigint,
        bool → bit

    Fixed-point / monetary
        decimal → decimal({p},{s})  default p=18, s=4
        numeric → numeric({p},{s})  default p=18, s=4
        money → money, smallmoney → smallmoney

    Floating-point
        float32 → real, float64 → float

    Date / time
        date → date
        time → time({n})            default n=7
        datetime → datetime
        datetime2 → datetime2({n})  default n=7
        smalldatetime → smalldatetime
        datetimeoffset / timestamptz → datetimeoffset({n})  default n=7

    Character strings
        char → char({n})            default n=10
        nchar → nchar({n})          default n=10
        varchar → varchar({n})      default n=20
        nvarchar → nvarchar({n})    default n=20
        text → text, ntext → ntext

    Binary strings
        binary → binary({n})        default n=10
        varbinary → varbinary({n})  default n=20
        image → image

    Other
        uuid / uniqueid → uniqueidentifier
        xml → xml
        sql_variant → sql_variant
        rowversion / timestamp → rowversion
        hierarchyid → hierarchyid
        geometry → geometry
        geography → geography
    """

    # Defaults for parameterised types
    _DEFAULTS: dict[str, dict[str, int]] = {
        "decimal":        {"p": 18, "s": 4},
        "numeric":        {"p": 18, "s": 4},
        "time":           {"n": 7},
        "datetime2":      {"n": 7},
        "datetimeoffset": {"n": 7},
        "timestamptz":    {"n": 7},
        "char":           {"n": 10},
        "nchar":          {"n": 10},
        "varchar":        {"n": 20},
        "nvarchar":       {"n": 20},
        "binary":         {"n": 10},
        "varbinary":      {"n": 20},
    }

    def sql_type(self, canonical: str, **params: int) -> str:
        """Return the T-SQL type string for *canonical* with optional *params*."""
        # Merge caller params over dialect defaults
        merged = {**self._DEFAULTS.get(canonical, {}), **params}
        n = merged.get("n", 10)
        p = merged.get("p", 18)
        s = merged.get("s", 4)

        match canonical:
            # Integers / boolean
            case "int8":
                return "tinyint"
            case "int16":
                return "smallint"
            case "int32":
                return "int"
            case "int64":
                return "bigint"
            case "bool":
                return "bit"
            # Fixed-point
            case "decimal":
                return f"decimal({p},{s})"
            case "numeric":
                return f"numeric({p},{s})"
            case "money":
                return "money"
            case "smallmoney":
                return "smallmoney"
            # Floating-point
            case "float32":
                return "real"
            case "float64":
                return "float"
            # Date / time
            case "date":
                return "date"
            case "time":
                return f"time({n})"
            case "datetime":
                return "datetime"
            case "datetime2":
                return f"datetime2({n})"
            case "smalldatetime":
                return "smalldatetime"
            case "datetimeoffset" | "timestamptz":
                return f"datetimeoffset({n})"
            # Character strings
            case "char":
                return f"char({n})"
            case "nchar":
                return f"nchar({n})"
            case "varchar":
                return f"varchar({n})"
            case "nvarchar":
                return f"nvarchar({n})"
            case "text":
                return "text"
            case "ntext":
                return "ntext"
            # Binary strings
            case "binary":
                return f"binary({n})"
            case "varbinary":
                return f"varbinary({n})"
            case "image":
                return "image"
            # Other
            case "uuid" | "uniqueid":
                return "uniqueidentifier"
            case "xml":
                return "xml"
            case "sql_variant":
                return "sql_variant"
            case "rowversion" | "timestamp":
                return "rowversion"
            case "hierarchyid":
                return "hierarchyid"
            case "geometry":
                return "geometry"
            case "geography":
                return "geography"
            case _:
                raise ValueError(
                    f"SqlServerDialect: unknown canonical type {canonical!r}"
                )

    def backup_sql(self, db_name: str, container_bak_path: str) -> str:
        """Return a T-SQL BACKUP DATABASE statement."""
        return (
            f"BACKUP DATABASE [{db_name}] TO DISK = N'{container_bak_path}'"
            " WITH FORMAT, INIT, COPY_ONLY;"
        )
