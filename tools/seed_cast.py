#!/usr/bin/env python3
"""Data-distribution axis builder for columnstore matrix fixtures.

Two public functions:

:func:`dist_expr`
    Returns a SQL expression string for ``g(pk)`` — a pure integer in
    ``[0, span)`` — from a named distribution token.  It does NOT know about
    types; it only produces an index.

:func:`cast_int_to`
    Wraps ``g(pk)`` in a type-specific ``CAST`` / ``CONVERT`` expression to
    produce a concrete SQL value for the given ``sql_type``.  Reuses the
    ``low`` / ``high`` domain anchors from :mod:`tools.typematrix`.

Together they compose as::

    cast_int_to(sql_type, dist_expr(dist, span=span))

All SQL is T-SQL and targets SQL Server 2017+.

Distribution catalog (tokens match :data:`tools.fixture_name.DIST`)
--------------------------------------------------------------------
``asc``
    ``pk % span`` — monotonic ascending index.
``desc``
    ``span - 1 - (pk % span)`` — monotonic descending.
``rand``
    ``ABS(CONVERT(BIGINT, BINARY_CHECKSUM(pk) * 2654435761) % span)`` —
    deterministic multiplicative hash; reproducible, no per-query RAND().
``const``
    ``0`` — all values the same (minimum domain value); longest single RLE run.
``runs``
    ``(pk / r) % k`` — *r* identical rows then change; hybrid RLE.
``cycle``
    ``pk % k`` — cycling *k* distinct values; controls bitpack width
    ``bpv = CEILING(LOG(k+1) / LOG(2))``.
``mmbnd``
    ``pk % 2`` — alternates between index 0 (min) and index 1 (max);
    the two-value cross-rowgroup min/max boundary.
``min``
    ``0`` — all minimum domain value (alias for ``const``).
``max``
    ``span - 1`` — all maximum domain value.

The *span* parameter is the distinct-count cardinality of the domain.  For
bounded types the plan recommends capping *span* to a practcal value (e.g.
1 048 576 for int, full domain for tinyint, etc.).  ``cast_int_to`` picks a
sensible default if *span* is 0 or None.

Implementation note on deterministic pseudo-random
---------------------------------------------------
SQL Server evaluates ``RAND()`` once per query (the ``RAND()`` gotcha noted in
``tools/fixture_name.py`` and the seed_cast skill), so all rows get the same
value.  We use a multiplicative hash instead::

    ABS(CONVERT(BIGINT, CONVERT(BINARY(8), CAST(pk AS BIGINT))
                        * 2654435761) % span)

which is the Knuth multiplicative hash (golden-ratio constant) — stable,
reproducible, and produces a visually random-looking sequence.
"""
from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_name import DIST

# ---------------------------------------------------------------------------
# Distribution expression: g(pk) -> index in [0, span)
# ---------------------------------------------------------------------------

_DEFAULT_SPAN = 1_000_000  # used when caller passes span=None


def dist_expr(
    dist: str,
    *,
    span: int | None = None,
    k: int | None = None,
    r: int | None = None,
) -> str:
    """Return a T-SQL expression for the distribution index ``g(pk)``.

    Parameters
    ----------
    dist:
        One of the :data:`tools.fixture_name.DIST` tokens.
    span:
        The cardinality of the domain in ``[0, span)``.  Used by ``asc``,
        ``desc``, ``rand``, ``mmbnd``.  Defaults to ``_DEFAULT_SPAN`` when
        ``None``.
    k:
        Distinct-value count for ``cycle`` and ``runs`` distributions.
        Defaults to ``min(512, span or _DEFAULT_SPAN)``.
    r:
        Run length for the ``runs`` distribution (number of identical rows
        before the value changes).  Defaults to 16.

    Returns a T-SQL expression referencing a column named ``pk``.
    """
    if dist not in DIST:
        raise ValueError(f"unknown dist token {dist!r}; valid: {sorted(DIST)}")

    sp: int = span if span and span > 0 else _DEFAULT_SPAN
    kk: int = k if k and k > 0 else min(512, sp)
    rr: int = r if r and r > 0 else 16

    if dist == "asc":
        return f"pk % {sp}"
    if dist == "desc":
        return f"{sp} - 1 - (pk % {sp})"
    if dist in ("rand",):
        return (
            f"ABS(CONVERT(BIGINT, CONVERT(BINARY(8), CAST(pk AS BIGINT)) "
            f"* CONVERT(BIGINT, 2654435761)) % {sp})"
        )
    if dist == "const":
        return "0"
    if dist == "min":
        return "0"
    if dist == "max":
        return str(sp - 1)
    if dist == "mmbnd":
        return "pk % 2"
    if dist == "cycle":
        return f"pk % {kk}"
    if dist == "runs":
        return f"(pk / {rr}) % {kk}"
    raise ValueError(f"unhandled dist {dist!r}")  # unreachable


# ---------------------------------------------------------------------------
# Type-cast: cast_int_to(sql_type, index_expr) -> SQL value expression
# ---------------------------------------------------------------------------

# Numeric span per SQL type (cardinality of [low, high] used by asc/desc/rand).
# For types where the domain is very large we cap at a practical span.
_TYPE_SPAN: dict[str, int] = {
    "tinyint":       256,
    "smallint":      65_536,
    "int":           1_000_000,
    "bigint":        1_000_000_000,
    "bit":           2,
    "real":          1_000_000,
    "float":         1_000_000_000,
    "money":         1_000_000,
    "smallmoney":    1_000_000,
}


def _typematrix_sql_type(sql_type: str) -> str | None:
    """Return the typematrix ``TypeCase.name`` for *sql_type*, or None."""
    from tools.typematrix import TYPE_CASES
    for tc in TYPE_CASES:
        if tc.sql_type.lower() == sql_type.lower():
            return tc.name
    return None


def cast_int_to(sql_type: str, index_expr: str, *, span: int | None = None) -> str:
    """Return a T-SQL expression that casts *index_expr* to *sql_type*.

    *index_expr* is a SQL expression producing an integer in ``[0, span)``.
    The resulting SQL value is a concrete ``sql_type`` datum suitable for
    INSERT … SELECT.

    Rules
    -----
    * Integer types: ``lo + (index % dom_span)`` where ``lo`` is the type minimum
      and ``dom_span = hi - lo + 1`` (clamped to the type domain).
    * Floating-point (``real``, ``float``): linearly scale index into ``[lo, hi]``.
    * Fixed-precision (``decimal``, ``numeric``, ``money``, ``smallmoney``): scale
      index by the ``magnitude`` of the low anchor.
    * Date/time: add *index* days/seconds to the minimum date/time.
    * Character strings: ``CONVERT(CHAR/NCHAR/…, CONVERT(VARBINARY, index_expr))``.
    * Binary types: ``CONVERT(BINARY/VARBINARY, index_expr)``.
    * ``uniqueidentifier``: construct a deterministic UUID by embedding the index.
    * ``bit``: ``CAST((index_expr % 2) AS BIT)``.
    * ``multi``: returns the identity expression (index_expr unchanged).

    For MAX types (``varchar(max)``, ``nvarchar(max)``, ``varbinary(max)``) the
    returned SQL produces a short value whose byte-length scales with the index
    — ``REPLICATE`` for char types, ``CONVERT(VARBINARY, …)`` for binary.
    """
    t = sql_type.lower().strip()

    # ------------------------------------------------------------------ bit
    if t == "bit":
        return f"CAST(({index_expr}) % 2 AS BIT)"

    # ------------------------------------------------------------------ exact integers
    _INT_DOMAINS: dict[str, tuple[int, int]] = {
        "tinyint":  (0, 255),
        "smallint": (-32_768, 32_767),
        "int":      (-2_147_483_648, 2_147_483_647),
        "bigint":   (-9_223_372_036_854_775_808, 9_223_372_036_854_775_807),
    }
    if t in _INT_DOMAINS:
        lo, hi = _INT_DOMAINS[t]
        dom_span = hi - lo + 1
        sp = span if span and span > 0 else min(dom_span, _DEFAULT_SPAN)
        # lo + ((index % sp) % dom_span) → stays within [lo, hi]
        return f"CAST({lo} + (CAST({index_expr} AS BIGINT) % {sp}) AS {t.upper()})"

    # ------------------------------------------------------------------ float / real
    if t in ("real", "float"):
        # Avoid overflow: cap domains at practical finite limits for the step computation.
        # Full float domain [−1.7e308, 1.7e308] gives step = 3.4e308/N which overflows.
        # Use [−1e15, 1e15] instead — plenty of dynamic range for encoding coverage.
        lo, hi = (-3.4e38, 3.4e38) if t == "real" else (-1e15, 1e15)
        sp = span if span and span > 0 else _TYPE_SPAN.get(t, 1_000_000)
        step = (hi - lo) / max(1, sp - 1)
        precision = "REAL" if t == "real" else "FLOAT"
        return (
            f"CAST({lo!r} + CAST({index_expr} AS FLOAT) * {step!r} AS {precision})"
        )

    # ------------------------------------------------------------------ decimal / numeric
    _DEC_RE = __import__("re").match(r"(decimal|numeric)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", t)
    if _DEC_RE:
        kind = _DEC_RE.group(1).upper()
        p, s = int(_DEC_RE.group(2)), int(_DEC_RE.group(3))
        max_int = 10 ** (p - s) - 1
        sp = span if span and span > 0 else min(max_int, _DEFAULT_SPAN)
        # Scatter index over negative and positive halves to exercise both signs.
        return (
            f"CONVERT({kind}({p},{s}), "
            f"CAST(CAST({index_expr} AS BIGINT) - {sp // 2} AS FLOAT) * 1e-{s})"
        )

    # ------------------------------------------------------------------ money / smallmoney
    if t == "money":
        sp = span if span and span > 0 else 10_000_000
        return f"CONVERT(MONEY, CAST(CAST({index_expr} AS BIGINT) - {sp // 2} AS FLOAT) * 0.0001)"
    if t == "smallmoney":
        sp = span if span and span > 0 else 200_000
        return f"CONVERT(SMALLMONEY, CAST(CAST({index_expr} AS BIGINT) - {sp // 2} AS FLOAT) * 0.0001)"

    # ------------------------------------------------------------------ date
    if t == "date":
        return f"DATEADD(DAY, {index_expr}, CAST('0001-01-01' AS DATE))"

    # ------------------------------------------------------------------ time
    _TIME_RE = __import__("re").match(r"time\s*\(\s*(\d+)\s*\)", t)
    if _TIME_RE or t == "time":
        return f"DATEADD(SECOND, {index_expr}, CAST('00:00:00' AS TIME))"

    # ------------------------------------------------------------------ datetime / datetime2 / smalldatetime
    if t == "datetime":
        return f"DATEADD(SECOND, {index_expr}, CAST('1753-01-01' AS DATETIME))"
    if t == "smalldatetime":
        return f"DATEADD(MINUTE, {index_expr}, CAST('1900-01-01' AS SMALLDATETIME))"
    _DT2_RE = __import__("re").match(r"datetime2\s*\(\s*(\d+)\s*\)", t)
    if _DT2_RE or t == "datetime2":
        return f"DATEADD(SECOND, {index_expr}, CAST('0001-01-01' AS DATETIME2))"

    # ------------------------------------------------------------------ datetimeoffset
    _DTO_RE = __import__("re").match(r"datetimeoffset\s*\(\s*(\d+)\s*\)", t)
    if _DTO_RE or t == "datetimeoffset":
        return (
            f"DATEADD(SECOND, {index_expr}, "
            f"CAST('0001-01-01 00:00:00 +00:00' AS DATETIMEOFFSET))"
        )

    # ------------------------------------------------------------------ fixed char / nchar
    _CHAR_RE = __import__("re").match(r"(n?char)\s*\(\s*(\d+)\s*\)", t)
    if _CHAR_RE:
        kind = _CHAR_RE.group(1).upper()
        n = int(_CHAR_RE.group(2))
        # LEFT(CONVERT(VARCHAR(20), index), n) right-padded to fixed width.
        return (
            f"CAST(LEFT(CONVERT(VARCHAR(20), {index_expr}), {n}) AS {kind}({n}))"
        )

    # ------------------------------------------------------------------ varchar / nvarchar (bounded)
    _VC_RE = __import__("re").match(r"(n?varchar)\s*\(\s*(\d+)\s*\)", t)
    if _VC_RE:
        kind = _VC_RE.group(1).upper()
        n = int(_VC_RE.group(2))
        return (
            f"CAST(LEFT(CONVERT(VARCHAR(20), {index_expr}), {n}) AS {kind}({n}))"
        )

    # ------------------------------------------------------------------ MAX types
    if t in ("varchar(max)", "nvarchar(max)"):
        kind = "NVARCHAR" if t.startswith("n") else "VARCHAR"
        return f"CAST(CONVERT(VARCHAR(20), {index_expr}) AS {kind}(MAX))"
    if t == "varbinary(max)":
        return (
            f"CAST(CONVERT(VARBINARY(MAX), CONVERT(BINARY(8), "
            f"CAST({index_expr} AS BIGINT))) AS VARBINARY(MAX))"
        )

    # ------------------------------------------------------------------ binary / varbinary (bounded)
    _BIN_RE = __import__("re").match(r"(var)?binary\s*\(\s*(\d+)\s*\)", t)
    if _BIN_RE:
        is_var = bool(_BIN_RE.group(1))
        n = int(_BIN_RE.group(2))
        kind = f"VARBINARY({n})" if is_var else f"BINARY({n})"
        return (
            f"CAST(CONVERT(BINARY(8), CAST({index_expr} AS BIGINT)) AS {kind})"
        )

    # ------------------------------------------------------------------ uniqueidentifier
    if t == "uniqueidentifier":
        # Embed index as low 8 bytes of a deterministic GUID.
        return (
            f"CAST(CONVERT(BINARY(8), CAST({index_expr} AS BIGINT)) "
            f"+ 0x0000000000000000 AS UNIQUEIDENTIFIER)"
        )

    # ------------------------------------------------------------------ multi / pass-through
    if t == "multi":
        return index_expr

    raise ValueError(
        f"cast_int_to: unsupported sql_type {sql_type!r}; "
        "add it to seed_cast.py or use 'multi' for a pass-through"
    )


# ---------------------------------------------------------------------------
# Quick smoke test (run directly: python -m tools.seed_cast)
# ---------------------------------------------------------------------------

def _smoke() -> None:
    import sys

    ok = True
    checks: list[tuple[str, str, str]] = [
        ("int",          "cycle",  "cycle"),
        ("bigint",       "asc",    "asc"),
        ("tinyint",      "const",  "const"),
        ("bit",          "cycle",  "cycle"),
        ("real",         "rand",   "rand"),
        ("float",        "rand",   "rand"),
        ("decimal(18,4)","asc",    "asc"),
        ("money",        "asc",    "asc"),
        ("date",         "asc",    "asc"),
        ("datetime2(7)", "asc",    "asc"),
        ("char(10)",     "cycle",  "cycle"),
        ("nvarchar(50)", "cycle",  "cycle"),
        ("binary(8)",    "rand",   "rand"),
        ("varbinary(max)","rand",  "rand"),
        ("uniqueidentifier","rand","rand"),
    ]
    for sql_type, dist, _tag in checks:
        try:
            g = dist_expr(dist, span=1000, k=64, r=8)
            expr = cast_int_to(sql_type, g)
            print(f"  {sql_type:22s}  {dist:8s}  →  {expr[:80]}")
        except Exception as exc:
            print(f"  FAIL {sql_type} {dist}: {exc}", file=sys.stderr)
            ok = False

    if ok:
        print("seed_cast smoke OK")
    else:
        sys.exit(1)


if __name__ == "__main__":
    _smoke()
