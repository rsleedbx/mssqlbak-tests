"""Canonical cell serialization — the SSOT shared by cell capture and verify.

Both the ground-truth capture (``tools/cells_capture.py``, future) and the offline
diff engine (``tools/value_verify.py``) serialize every cell through :func:`canon`
so the two sides compare byte-for-byte without per-call-site drift. The SAME
canonical string feeds both the per-cell comparison and the per-column
:func:`column_digest`, so a digest can never disagree with a cell compare.

The rules mirror the existing aggregate comparators
(``tools/register_bak._minmax_col_exprs`` / ``correctness_coverage._minmax_equal``):
char/nchar trailing-space trim, float/real significant-digit quantization,
decimal fixed scale, hex for binary, ISO-8601 (UTC) for temporal.
"""

from __future__ import annotations

import functools
import hashlib
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

# Significant digits used to quantize binary floating point to a stable decimal
# string.  15 is the correct value for two reasons:
#
# 1. Round-trip fidelity: SQL Server emits FLOAT text with up to 15 significant
#    digits (e.g. "1.79769313486232E+308" for the maximum finite value).  At
#    sig=15 both the SQL Server text and Python's repr() of the same float64
#    (which has up to 17 digits) round to the same 15-digit canonical form.
#    sig=13 introduces a one-digit drift for 14-digit SQL Server text (e.g.
#    "75.398223686155" → "75.39822368616" at 13g vs "75.39822368615" for the
#    matching Python repr), which was masked only because GT parquet was
#    changed (commit 35d6d9c) to store Python repr() instead of SQL Server
#    text.
#
# 2. Large float ID coverage: 13 was previously chosen as the minimum to
#    distinguish adjacent large float IDs (≈ 2.85 × 10¹²).  15 also
#    distinguishes them (with more precision), so there is no reason to use
#    the minimum — 15 is the correct value.
_FLOAT_SIG = 15
_REAL_SIG = 6

_ALIASES: dict[str, str] = {
    # AdventureWorks defines these user scalar types over bit.  Cell sidecars
    # preserve the alias name, while decoded rows expose Python bool values.
    "flag": "bit",
    "namestyle": "bit",
}

_GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_DECIMAL_TEXT_RE = re.compile(r"^-?\d+\.\d+$")
_DATETIMEOFFSET_SPACE_RE = re.compile(r"(\.\d+)? ([+-]\d\d:\d\d)$")
_FRACTIONAL_SECONDS_RE = re.compile(r"(\d{2}:\d{2}:\d{2})\.(\d{7})(?=([+-]\d\d:\d\d)?$)")
_XML_EMPTY_ELEMENT_RE = re.compile(r"<([A-Za-z_][\w:.-]*)([^<>]*)></\1>")
_XML_DECIMAL_TEXT_RE = re.compile(r">(-?\d+\.\d+)<")
_WKT_NUMBER_RE = re.compile(r"(?<![A-Za-z_])[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[Ee][-+]?\d+)?")


@functools.lru_cache(maxsize=None)
def _base_type(sql_type: str) -> str:
    """Return the lowercase base type name, stripping any ``(...)`` parameters."""
    t = sql_type.strip().lower()
    paren = t.find("(")
    if paren != -1:
        t = t[:paren]
    t = t.strip()
    return _ALIASES.get(t, t)


# CLR UDT columns whose canonical text form is produced by a method call rather
# than a plain SELECT (the driver otherwise returns the raw UDT serialization).
# geometry/geography use AsTextZM() (includes Z/M ordinates) to match
# mssqlbak.spatial.decode_spatial; hierarchyid uses ToString() to match
# mssqlbak.hierarchyid.decode_hierarchyid ("/1/2/").  Shared by both the
# ground-truth capture (tools/cells_capture) and the stats min/max exprs
# (tools/register_bak) so the two never drift.
_CLR_TO_TEXT: dict[str, str] = {
    "geography": "AsTextZM()",
    "geometry": "AsTextZM()",
    "hierarchyid": "ToString()",
}


def clr_text_method(base_type: str) -> str | None:
    """Return the CLR ``.Method()`` that yields *base_type*'s canonical string.

    Returns ``None`` for non-UDT types (which are captured via a plain SELECT).
    """
    return _CLR_TO_TEXT.get(base_type.lower())


def _scale_of(sql_type: str) -> int | None:
    """Parse the scale from a ``decimal(p,s)`` / ``numeric(p,s)`` type, else None."""
    lo, hi = sql_type.find("("), sql_type.find(")")
    if lo == -1 or hi == -1 or hi < lo:
        return None
    parts = sql_type[lo + 1 : hi].split(",")
    if len(parts) == 2:
        try:
            return int(parts[1])
        except ValueError:
            return None
    return None


def _canon_sql_variant_text(value: Any) -> str:
    """Normalize stable text forms used for heterogeneous sql_variant columns."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "0x" + bytes(value).hex()
    s = str(value)
    if _GUID_RE.match(s):
        return s.lower()
    if s.lower().startswith("0x"):
        return s.lower()
    if _DECIMAL_TEXT_RE.match(s):
        # SQL Server's CAST(sql_variant AS NVARCHAR) trims decimal scale, while
        # mssqlbak preserves it.  The base type/scale are not available in the
        # manifest, so compare the numeric value for sql_variant cells.
        return s.rstrip("0").rstrip(".")
    if "T" in s and re.match(r"^\d{4}-\d{2}-\d{2}T", s):
        s = s.replace("T", " ")
    s = _FRACTIONAL_SECONDS_RE.sub(lambda m: f"{m.group(1)}.{m.group(2)[:6]}", s)
    return _DATETIMEOFFSET_SPACE_RE.sub(lambda m: (m.group(1) or "") + m.group(2), s)


def _canon_bit(value: Any) -> str:
    """Normalize bools plus SQL/driver text forms to the digest's 0/1 domain."""
    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("0", "false"):
            return "0"
        if s in ("1", "true"):
            return "1"
    return "1" if value else "0"


def _format_sig_decimal(value: Decimal, sig: int) -> str:
    text = format(value, f".{sig}g")
    if "e" not in text and "E" not in text:
        if "." in text:
            text = text.rstrip("0").rstrip(".")
    else:
        # Strip trailing zeros from the coefficient in scientific notation so
        # that e.g. "1.00000000000000e+15" (from Decimal("1000000000000000.0"))
        # renders as "1e+15", matching Python's float g format.
        e_idx = text.lower().find("e")
        coeff = text[:e_idx]
        exp_part = text[e_idx:]  # e.g. "e+15"
        if "." in coeff:
            coeff = coeff.rstrip("0").rstrip(".")
        text = coeff + exp_part
    return text


def _canon_float(value: Any, sig: int) -> str:
    """Quantize floats while keeping already-textual finite sidecars finite.

    SQL Server displays ``FLOAT`` values with at most 15 significant digits.
    That 15-digit text is not always a lossless round-trip: Python's ``float()``
    may return a neighbour float64 that, at sig < 15, rounds in the opposite
    direction.  Using ``sig = 15`` (``_FLOAT_SIG``) avoids this: both the GT
    string ``'75.398223686155'`` and the extracted ``75.39822368615496`` format
    identically at 15 g — the ``format(extracted, '.15g')`` result strips its
    trailing zero and matches the SQL Server text exactly.

    The string branch goes through ``Decimal`` directly (not ``float()``) so
    that out-of-range literals like ``'-1.79769313486232e+308'`` are preserved
    rather than overflowing to ``-inf``.  The non-string branch goes through
    ``repr()`` → ``Decimal`` to get the shortest exact decimal before rounding.
    """
    if isinstance(value, str):
        s = value.strip()
        lo = s.lower()
        if lo in ("inf", "+inf", "infinity", "+infinity"):
            return "inf"
        if lo in ("-inf", "-infinity"):
            return "-inf"
        if lo in ("nan", "+nan", "-nan"):
            return "nan"
        try:
            return _format_sig_decimal(Decimal(s), sig)
        except (InvalidOperation, ValueError):
            return s
    # Route non-string values through repr() → Decimal for a canonical
    # shortest-exact decimal.  Python's float `g` format switches to scientific
    # notation at exp < -4 (e.g. 2.3e-05 → "2.3e-05"), whereas
    # Decimal('2.3e-05') normalises to Decimal('0.000023') and formats as
    # "0.000023" — matching the GT string captured from SQL Server.
    _fv = float(value)
    _fv_repr = repr(_fv)
    _fv_lower = _fv_repr.lower()
    if _fv_lower in ("inf", "+inf", "infinity", "+infinity"):
        return "inf"
    if _fv_lower in ("-inf", "-infinity"):
        return "-inf"
    if "nan" in _fv_lower:
        return "nan"
    try:
        return _format_sig_decimal(Decimal(_fv_repr), sig)
    except (InvalidOperation, ValueError, OverflowError):
        return format(_fv, f".{sig}g")


def _canon_xml_text(value: Any) -> str:
    """Normalize harmless XML serialization choices between SQL Server and Python."""
    s = str(value)
    s = re.sub(r"&#x0[dD];", "\r", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    previous = None
    while previous != s:
        previous = s
        s = _XML_EMPTY_ELEMENT_RE.sub(r"<\1\2/>", s)
    return _XML_DECIMAL_TEXT_RE.sub(lambda m: f">{m.group(1).rstrip('0').rstrip('.')}<", s)


def _canon_wkt_text(value: Any) -> str:
    """Normalize WKT floating-point spellings without changing the shape text."""

    def repl(match: re.Match[str]) -> str:
        text = match.group(0)
        try:
            number = float(text)
        except ValueError:
            return text
        if number == int(number) and abs(number) < 1e15:
            return str(int(number))
        return format(number, ".15g")

    return _WKT_NUMBER_RE.sub(repl, str(value))


def canon(value: Any, sql_type: str) -> str | None:
    """Serialize one decoded cell to a canonical string (or ``None`` for SQL NULL).

    ``None`` in means a genuine SQL NULL and maps to ``None`` out (kept distinct
    from any decoded string). Every non-null value maps to a deterministic string
    that is stable across the capture and decode sides.
    """
    if value is None:
        return None

    t = _base_type(sql_type)

    if t == "sql_variant":
        return _canon_sql_variant_text(value)

    if t in ("decimal", "numeric", "money", "smallmoney"):
        try:
            d = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return str(value)
        scale = _scale_of(sql_type)
        if scale is not None:
            try:
                d = d.quantize(Decimal(1).scaleb(-scale))
            except InvalidOperation:
                pass
        return format(d, "f")

    if t == "float":
        return _canon_float(value, _FLOAT_SIG)
    if t == "real":
        return _canon_float(value, _REAL_SIG)

    if t in ("binary", "varbinary", "timestamp", "rowversion", "image"):
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value).hex()
        if isinstance(value, int):
            # rowversion/timestamp sometimes decoded as int — normalize to 8-byte hex.
            return value.to_bytes(8, "big").hex()
        return str(value).lower()

    if t == "uniqueidentifier":
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value).hex()
        return str(value).lower()

    if t in ("char", "nchar"):
        # SQL CHAR semantics: trailing space padding is not significant.
        return str(value).rstrip(" ")

    if t == "bit":
        return _canon_bit(value)

    if t == "xml":
        return _canon_xml_text(value)

    if t in ("geometry", "geography"):
        return _canon_wkt_text(value)

    if t in ("datetimeoffset",):
        if isinstance(value, datetime):
            dt = value.astimezone(timezone.utc) if value.tzinfo else value
            return dt.isoformat()
        return str(value)

    if t in ("date", "datetime", "datetime2", "smalldatetime", "time"):
        iso = getattr(value, "isoformat", None)
        if callable(iso):
            return str(iso())
        return str(value)

    return str(value)


def column_digest(canon_values: Iterable[str | None]) -> str:
    """Length-prefixed sha256 over the binary-sorted, non-null canonical values.

    Covers the WHOLE column (even when only a row sample is stored), so set-level
    corruption is caught regardless of row sampling. Length-prefixing each value
    makes the digest unambiguous for adjacent values.
    """
    encoded = sorted(v.encode("utf-8") for v in canon_values if v is not None)
    h = hashlib.sha256()
    for b in encoded:
        h.update(len(b).to_bytes(4, "little") + b)
    return "sha256:" + h.hexdigest()


# Null sentinel for ordered digest: length prefix 0xFFFFFFFF with no payload.
# Distinguishable from any real string (which would need ~4 GB of payload) and
# from the empty string (which has length 0x00000000 with no payload).
_ORDERED_NULL_SENTINEL = b"\xff\xff\xff\xff"


def column_ordered_digest(canon_values_in_order: Iterable[str | None]) -> str:
    """Length-prefixed SHA-256 over canonical values in their given row order.

    Unlike :func:`column_digest` this does **not** sort the values, so the
    hash is sensitive to the position of each value in the column.  Nulls are
    represented by a 4-byte sentinel (``0xFFFFFFFF``) rather than being dropped,
    so a null shifting rows also changes the digest.

    Use together with :func:`column_digest` for order-aware verification: the
    multiset digest catches wrong values; the ordered digest catches values on
    the wrong row.
    """
    h = hashlib.sha256()
    for v in canon_values_in_order:
        if v is None:
            h.update(_ORDERED_NULL_SENTINEL)
        else:
            b = v.encode("utf-8")
            h.update(len(b).to_bytes(4, "little") + b)
    return "sha256:" + h.hexdigest()
