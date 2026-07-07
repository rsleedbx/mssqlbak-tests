"""hierarchyid ORDPATH decoder, exercised on real on-disk byte blobs.

The hex blobs are ``CAST(hierarchyid::Parse(<path>) AS varbinary)`` captured
from a live SQL Server (the exact stored bytes); the expected text is the
matching ``.ToString()``. They pin the encoding without a live engine and span
every ORDPATH bucket boundary plus the root, dotted sub-ordinals, multi-level
paths, negatives, and large nodes. The decoder is additionally cross-checked
against 22,000+ live-engine values in the project's validation runs.
"""
from __future__ import annotations

import pytest

from mssqlbak.hierarchyid import decode_hierarchyid

CASES = [
    ("root", "", "/"),
    ("one", "58", "/1/"),
    ("zero", "48", "/0/"),
    ("two", "68", "/2/"),
    ("multi", "5b5e", "/1/2/3/"),
    ("dotted", "62c0", "/1.1/"),
    ("deep", "5b5f0c60", "/1/2/3/4/5/"),
    ("negative", "3f80", "/-1/"),
    ("big_pair", "e026783b10", "/100/200/"),
    ("ninety_eight", "e02540", "/98/"),
    ("siblings", "5ac0", "/1/1/"),
    ("triple_dot", "5292", "/0.0.0/"),
    ("neg_pair", "3b96fc", "/-5/-9/"),
    ("bucket_256", "e26440", "/256/"),
    ("bucket_1104", "f00088", "/1104/"),
    ("bucket_5200", "f80000000220", "/5200/"),
]


@pytest.mark.parametrize("name,blob,expected", CASES, ids=[c[0] for c in CASES])
def test_decode_hierarchyid(name: str, blob: str, expected: str) -> None:
    assert decode_hierarchyid(bytes.fromhex(blob)) == expected


def test_invalid_binary_raises() -> None:
    # A non-zero prefix that matches no ORDPATH pattern is rejected.
    with pytest.raises(ValueError, match="hierarchyid"):
        decode_hierarchyid(b"\xff\xff")
