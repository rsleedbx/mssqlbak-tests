"""LOB inline-root link-count matrix (Guess G30).

One table with three ``varchar(max)`` rows sized to exercise 1, 2, and 3+
twelve-byte LOB links in the in-row inline root.
"""

from __future__ import annotations

LOB_LINKS_TABLE = "lob_links"

# T-SQL REPLICATE() is capped at 8000; build larger payloads with concatenation.
_REPLICATE_MAX = 8000


def _insert_lob_sql(row_id: int, char: str, n: int) -> str:
    """Build a batch that fills ``varchar(max)`` via a ``@v varchar(max)`` loop.

    ``REPLICATE`` is capped at 8000 and chained ``varchar`` ``+`` / ``CONCAT`` on
    literals can still yield 8000-byte rows in ``INSERT VALUES`` contexts.
    Growing a ``varchar(max)`` variable is reliable for LOB link-count fixtures.
    """
    first = min(n, _REPLICATE_MAX)
    return (
        f"DECLARE @v varchar(max);\n"
        f"SET @v = REPLICATE('{char}', {first});\n"
        f"WHILE LEN(@v) < {n}\n"
        f"  SET @v = @v + REPLICATE('{char}', "
        f"CASE WHEN {n} - LEN(@v) > {_REPLICATE_MAX} THEN {_REPLICATE_MAX} "
        f"ELSE {n} - LEN(@v) END);\n"
        f"INSERT INTO [{LOB_LINKS_TABLE}] VALUES ({row_id}, @v);\n"
    )


LOB_LINKS_SQL: list[str] = [
    f"CREATE TABLE [{LOB_LINKS_TABLE}] (id int NOT NULL PRIMARY KEY, v varchar(max) NOT NULL);",
    "GO",
    _insert_lob_sql(1, "A", 7000),
    "GO",
    _insert_lob_sql(2, "B", 50000),
    "GO",
    _insert_lob_sql(3, "C", 120000),
    "GO",
]

# Expected stitched lengths (exact bytes verified by parser tests).
LOB_LINKS_EXPECTED_LEN = {1: 7000, 2: 50000, 3: 120000}
