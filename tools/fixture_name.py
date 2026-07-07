#!/usr/bin/env python3
"""Single source of truth for columnstore matrix fixture names.

The SQL-version axis is the directory (``tests/fixtures_{2017,2019,2022,2025}``),
so the filename carries the other four axes::

    cs__<org>__<enc>__<type>__<dist>[__<null>][__r<rows>].bak

- ``cs__`` marks a columnstore matrix fixture (vs heap/rowstore/ad-hoc names).
- Fields are separated by **double underscore** ``__`` because type tokens already
  contain single underscores (``datetime2_7``, ``decimal_38_10``, ``char_10``).
- Field order is fixed; trailing optional fields are omitted at their default
  (``null=none``, default row count).

``fixture_name()`` builds a name; ``parse_fixture_name()`` is its inverse and is
what ``tools/columnstore_matrix.py`` uses to pre-place each fixture into its
``{type x technique x organization x distribution x version}`` cell (filename =
declared intent), then reconciles against ``segments.json`` (ground truth).

Both generators and ``tools/seed_cast.py`` import this module, so the token
vocabulary lives here once and never drifts.
"""

from __future__ import annotations

import re

PREFIX = "cs__"

# Controlled token vocabularies (the matrix axes; version is the directory).
ORG: frozenset[str] = frozenset(
    {
        "cci",      # clustered columnstore
        "cciord",   # ordered CCI
        "ccipart",  # partitioned CCI
        "multirg",  # multiple compressed rowgroups
        "delta",    # open delta store (uncompressed rows)
        "delbmp",   # delete bitmap present
        "updbmp",   # update (delete + reinsert) bitmap
        "switch",   # partition switch
        "ccinci",   # CCI + nonclustered btree index
        "nccirs",   # NCCI on rowstore
        "nccihp",   # NCCI on heap
        "ncciflt",  # filtered NCCI
        "computed", # computed column in CCI
    }
)

ENC: frozenset[str] = frozenset(
    {
        "enc1for",  # value / frame-of-reference
        "enc2int",  # bit-packed integer
        "enc2flt",  # bit-packed float
        "enc3v2",   # dictionary v2
        "enc3v4",   # dictionary v4 (Huffman)
        "enc3v7",   # dictionary v7
        "enc3max",  # dictionary, MAX type off-row
        "enc4raw",  # raw 64-bit
        "enc5fa", "enc5fb", "enc5fc", "enc5fd",  # enc=5 XPRESS formats A-D
        "arch",     # ARCHIVE (single XPRESS)
        "arch2",    # ARCHIVE double-compressed sub-block
    }
)

DIST: frozenset[str] = frozenset(
    {
        "asc",    # ascending
        "desc",   # descending
        "rand",   # deterministic pseudo-random
        "const",  # single repeated value
        "runs",   # run-length clusters
        "cycle",  # cycling distinct values (dictionary pressure)
        "mmbnd",  # min/max domain extremes crossing a rowgroup boundary
        "min",    # all minimum domain value
        "max",    # all maximum domain value
    }
)

NULL: frozenset[str] = frozenset(
    {
        "spnull",   # sparse / scattered nulls
        "nullrun",  # clustered null runs
    }
)

# Type token: a typematrix canonical token (may contain single underscores, e.g.
# ``decimal_38_10``) or ``multi`` for a one-column-per-type sweep. Never ``__``.
_TYPE_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
_ROWS_RE = re.compile(r"^r(\d+)$")

# Sidecar / archive suffixes stripped down to the base ``.bak`` stem on parse.
_STRIP_SUFFIXES = (
    ".bak.stats.json",
    ".bak.segments.json",
    ".bak.cells",
    ".cells",
    ".bak.zst",
    ".bak",
)


def fixture_name(
    org: str,
    enc: str,
    type: str,  # noqa: A002 - matches the axis name in the plan/docs
    dist: str,
    null: str | None = None,
    rows: int | None = None,
) -> str:
    """Return the ``cs__…​.bak`` filename for one matrix cell.

    Raises ``ValueError`` on any token outside the controlled vocabulary so a
    generator typo fails loudly instead of producing an unplaceable fixture.
    """
    if org not in ORG:
        raise ValueError(f"unknown org token {org!r}; valid: {sorted(ORG)}")
    if enc not in ENC:
        raise ValueError(f"unknown enc token {enc!r}; valid: {sorted(ENC)}")
    if dist not in DIST:
        raise ValueError(f"unknown dist token {dist!r}; valid: {sorted(DIST)}")
    if type != "multi" and not _TYPE_RE.match(type):
        raise ValueError(f"invalid type token {type!r} (lowercase, single-underscore only)")
    if null is not None and null != "none" and null not in NULL:
        raise ValueError(f"unknown null token {null!r}; valid: {sorted(NULL)} or none")
    if rows is not None and rows < 0:
        raise ValueError(f"rows must be non-negative, got {rows}")

    parts = [PREFIX.rstrip("_"), org, enc, type, dist]
    name = "__".join(parts)
    if null is not None and null != "none":
        name += f"__{null}"
    if rows is not None:
        name += f"__r{rows}"
    return f"{name}.bak"


def _base_stem(name: str) -> str:
    """Strip directory and any known sidecar/archive suffix to the bare stem."""
    base = name.rsplit("/", 1)[-1]
    for suf in _STRIP_SUFFIXES:
        if base.endswith(suf):
            return base[: -len(suf)]
    return base


def parse_fixture_name(name: str) -> dict[str, object]:
    """Inverse of :func:`fixture_name`.

    Accepts a path, filename, stem, or any sidecar name (``.bak.stats.json``,
    ``.segments.json``, ``.cells``, ``.bak.zst``). Returns a dict with
    ``is_matrix``: ``False`` for legacy/ad-hoc names (no ``cs__`` prefix — these
    are placed from ``segments.json`` instead), otherwise ``True`` plus
    ``org, enc, type, dist, null, rows`` (``null``/``rows`` are ``None`` when
    omitted).

    Raises ``ValueError`` for a ``cs__`` name that is structurally malformed —
    that is a generator bug, not a legacy fixture.
    """
    stem = _base_stem(name)
    if not stem.startswith(PREFIX):
        return {"is_matrix": False, "name": stem}

    fields = stem[len(PREFIX):].split("__")
    if len(fields) < 4:
        raise ValueError(f"matrix name {stem!r} has too few fields: {fields}")

    org, enc, type_, dist, *rest = fields
    if org not in ORG:
        raise ValueError(f"matrix name {stem!r}: unknown org {org!r}")
    if enc not in ENC:
        raise ValueError(f"matrix name {stem!r}: unknown enc {enc!r}")
    if dist not in DIST:
        raise ValueError(f"matrix name {stem!r}: unknown dist {dist!r}")
    if type_ != "multi" and not _TYPE_RE.match(type_):
        raise ValueError(f"matrix name {stem!r}: invalid type {type_!r}")

    null: str | None = None
    rows: int | None = None
    for tok in rest:
        m = _ROWS_RE.match(tok)
        if m is not None:
            if rows is not None:
                raise ValueError(f"matrix name {stem!r}: duplicate rows token {tok!r}")
            rows = int(m.group(1))
        elif tok in NULL:
            if null is not None:
                raise ValueError(f"matrix name {stem!r}: duplicate null token {tok!r}")
            null = tok
        else:
            raise ValueError(f"matrix name {stem!r}: unexpected trailing token {tok!r}")

    return {
        "is_matrix": True,
        "org": org,
        "enc": enc,
        "type": type_,
        "dist": dist,
        "null": null,
        "rows": rows,
    }
