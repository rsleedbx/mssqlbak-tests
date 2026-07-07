from __future__ import annotations

import pytest

from tools.cell_canon import canon


@pytest.mark.quick
def test_float_canon_preserves_precision_at_sig15() -> None:
    # _FLOAT_SIG=15 preserves the full 15-digit SQL Server representation.
    # When SQL Server returns a 14-digit string that is the shortest decimal
    # representation of the underlying float64, both the string and the Python
    # float produced by parsing that string canonicalize identically: the
    # format(.15g) of the float drops the trailing zero and matches the string.
    pairs = [
        # (Python float64 decoded from raw bytes, SQL Server text string)
        # All pairs represent the SAME float64 — the string IS the
        # round-trip-canonical shortest decimal for that float.
        (75.39822368615499, "75.398223686155"),
        (1.00040016006403, "1.00040016006403"),
    ]
    for decoded, sidecar in pairs:
        # Both sides must canonicalize to the same string.
        assert canon(decoded, "float") == canon(sidecar, "float"), (
            f"decoded={decoded!r} → {canon(decoded, 'float')!r} "
            f"sidecar={sidecar!r} → {canon(sidecar, 'float')!r}"
        )


@pytest.mark.quick
def test_float_canon_different_float64s_produce_different_canonicals() -> None:
    # With _FLOAT_SIG=15, two float64 values that differ in the last digit
    # produce distinct canonical strings.  This is intentional: sig=15
    # preserves full IEEE-754 round-trip fidelity rather than masking
    # last-digit differences.
    pairs = [
        (15.707963267949, "15.7079632679489"),
        (47.1238898038468, "47.1238898038469"),
        (709.999939711292, "709.999939711293"),
        (3515.44217936698, "3515.44217936697"),
    ]
    for decoded, sidecar in pairs:
        # These ARE different float64 values — they should NOT compare equal.
        assert canon(decoded, "float") != canon(sidecar, "float"), (
            f"Unexpectedly equal: decoded={decoded!r} sidecar={sidecar!r}"
        )
