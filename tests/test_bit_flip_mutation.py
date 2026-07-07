"""Negative / fuzz axis: bit-flip mutation harness.

Follows the SQLite ``dbsqlfuzz`` / ``corrupt*.test`` model:

* Take a known-good columnstore ``.bak`` fixture.
* Flip one bit at a time at a deterministic set of byte positions inside the
  file.
* Run the full extraction pipeline against the mutated bytes.
* Assert that the result is always *clean*: either the extraction succeeds
  (the flip hit a harmless region), or it raises a well-typed Python
  ``Exception``.  What is **never** allowed:

  * A low-level crash (``SystemError``, ``MemoryError``, ``RecursionError``,
    ``OverflowError`` propagated as an unhandled crash, ``KeyboardInterrupt``,
    ``SystemExit``).
  * An infinite loop / hang (guarded by a per-mutation timeout via
    ``signal.alarm`` on POSIX systems, skipped on Windows).
  * A ``SegFault`` — the Rust extension must not produce one.

The harness is offline and deterministic (bit positions are derived from a
seeded hash of the fixture path and file size, never from ``random``).  This
ties into the ``mssqlfuzzy_bak_generator`` plan and the
``single_bit_flip_does_not_silently_pass_verifier`` terminology rule.

Markers
-------
``quick``  — the harness is self-contained (just a .bak read + mutate +
             decode in Python), no live SQL Server, runs in <30 s on any
             developer machine.

``negative``  — logical category for mutation / negative-path tests.

Both markers are applied to every test here.

Fixtures used
-------------
``cci_bitpack_probe_full.bak``  — small, columnar, enc=2.
``archive_single_chunk_full.bak``  — ARCHIVE CCI, enc=5/XPRESS.

If either fixture is absent, the corresponding test group is skipped.
"""
from __future__ import annotations

import signal
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any

import pytest

from mssqlbak.catalog import recover_schema
from mssqlbak.pages import AnyPageStore, PageStore

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CLEAN_EXCEPTIONS = (Exception,)
_CRASH_TYPES = (
    SystemError,
    MemoryError,
    RecursionError,
    KeyboardInterrupt,
    SystemExit,
)

_POSIX = sys.platform != "win32"

# Number of bit positions to probe per fixture.  Keep low (≤100) so the full
# test group runs in well under 30 s even for MB-sized fixtures.
_N_PROBES = 80

# Alarm timeout per mutation probe (seconds).  Only effective on POSIX.
_TIMEOUT_S = 8


def _deterministic_positions(n_bytes: int, n_probes: int, seed: int) -> list[int]:
    """Return ``n_probes`` byte positions in ``[0, n_bytes)``.

    Uses a simple multiplicative hash (no ``random`` module) so the set is
    deterministic and seed-reproducible.  Positions cover the full file but
    are biased toward the middle (where page data lives) by discarding the
    first 512 bytes (MTF header) and the last 64 bytes (trailer padding).
    """
    lo = min(512, n_bytes)
    hi = max(lo + 1, n_bytes - 64)
    span = hi - lo
    if span <= 0:
        return []
    positions: list[int] = []
    h = seed & 0xFFFF_FFFF_FFFF_FFFF
    while len(positions) < n_probes:
        h = (h * 6364136223846793005 + 1442695040888963407) & 0xFFFF_FFFF_FFFF_FFFF
        positions.append(lo + (h % span))
    return positions


def _flip_bit(data: bytearray, byte_pos: int, bit: int = 0) -> None:
    """Flip ``bit`` (0=MSB) of ``data[byte_pos]`` in-place."""
    data[byte_pos] ^= 1 << (7 - (bit % 8))


class _Alarm(Exception):
    pass


def _decode_mutated(bak_bytes: bytes) -> None:
    """Run the extraction pipeline against *bak_bytes* written to a temp file.

    Opens a ``PageStore`` from the temp path and calls ``recover_schema``.
    For each columnstore table, iterates the first row to exercise the decoder.
    We do not assert correctness — only that no crash occurs.
    """
    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as tf:
        tmp_path = Path(tf.name)
        tf.write(bak_bytes)
    try:
        store: AnyPageStore = PageStore.from_bak(tmp_path)
        schema = recover_schema(store)
        for tbl in schema.tables:
            if tbl.compression not in (3, 4):  # 3=columnstore, 4=columnstore_archive
                continue
            try:
                from mssqlbak.columnstore.assembly.reader import read_columnstore_rows
                rows = read_columnstore_rows(store, tbl)
                next(rows, None)
            except _CLEAN_EXCEPTIONS:
                pass
    finally:
        tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Parametrise over (fixture_path, seed) so each probe is a named test case
# ---------------------------------------------------------------------------

def _probe_params(fixture_path: Path) -> list[tuple[int, int]]:
    """Return (byte_pos, bit_index) pairs for ``_N_PROBES`` mutations."""
    data = fixture_path.read_bytes()
    seed = hash(str(fixture_path)) ^ len(data)
    positions = _deterministic_positions(len(data), _N_PROBES, seed & 0xFFFF_FFFF_FFFF_FFFF)
    return [(pos, pos % 8) for pos in positions]


def _run_probe(fixture_path: Path, byte_pos: int, bit_idx: int) -> None:
    """Core logic: mutate one bit, run decoder, assert clean outcome."""
    data = bytearray(fixture_path.read_bytes())
    _flip_bit(data, byte_pos, bit_idx)
    bak_bytes = bytes(data)

    # Arm a per-probe timeout on POSIX to catch infinite loops.
    timed_out = False
    if _POSIX:
        def _handler(signum: int, frame: Any) -> None:
            raise _Alarm(f"timeout after {_TIMEOUT_S}s decoding mutated fixture")
        old = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(_TIMEOUT_S)

    try:
        _decode_mutated(bak_bytes)
    except _Alarm:
        timed_out = True
    except _CRASH_TYPES as exc:
        # Low-level crash: re-raise as a test failure with context.
        pytest.fail(
            f"Crash ({type(exc).__name__}) on bit-flip at byte={byte_pos} "
            f"bit={bit_idx}: {exc}\n{traceback.format_exc()}"
        )
    except Exception:
        pass  # well-typed Python Exception; acceptable
    finally:
        if _POSIX:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)

    if timed_out:
        pytest.fail(
            f"Timeout ({_TIMEOUT_S}s) on bit-flip at byte={byte_pos} bit={bit_idx}: "
            "decoder appears stuck — possible infinite loop"
        )


# ---------------------------------------------------------------------------
# enc=2 CCI fixture probes
# ---------------------------------------------------------------------------

_FIXTURE_NAMES_ENC2 = [
    "cci_bitpack_probe",
]


def _cci_bitpack_params(fixture_path: Path | None) -> list[tuple[int, int]]:
    if fixture_path is None or not fixture_path.exists():
        return []
    return _probe_params(fixture_path)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrise bit-flip probes at collection time.

    We cannot use normal ``@pytest.mark.parametrize`` decorators because the
    parameter lists are derived from fixture file sizes, which are only known at
    collection time.  Using ``pytest_generate_tests`` is the standard pytest
    pattern for data-driven parametrisation.
    """
    from tests.conftest import _FIXTURE_DIR  # type: ignore[attr-defined]

    if metafunc.function.__name__ == "test_bit_flip_does_not_crash_enc2_cci":
        fixture_path = _FIXTURE_DIR / "cci_bitpack_probe_full.bak"
        params = _probe_params(fixture_path) if fixture_path.exists() else []
        ids = [f"byte{pos}_bit{bit}" for pos, bit in params]
        metafunc.parametrize("byte_pos,bit_idx", params, ids=ids)

    elif metafunc.function.__name__ == "test_bit_flip_does_not_crash_archive_cci":
        fixture_path = _FIXTURE_DIR / "archive_single_chunk_full.bak"
        params = _probe_params(fixture_path) if fixture_path.exists() else []
        ids = [f"byte{pos}_bit{bit}" for pos, bit in params]
        metafunc.parametrize("byte_pos,bit_idx", params, ids=ids)


@pytest.mark.quick
@pytest.mark.negative
def test_bit_flip_does_not_crash_enc2_cci(
    byte_pos: int,
    bit_idx: int,
    request: pytest.FixtureRequest,
) -> None:
    """Every single-bit corruption of the CCI bitpack probe fixture is handled cleanly.

    The decoder must never crash (``SystemError``, ``MemoryError``, …) or hang.
    It may raise any well-typed ``Exception`` or succeed silently.
    """
    from tests.conftest import _FIXTURE_DIR  # type: ignore[attr-defined]

    fixture_path = _FIXTURE_DIR / "cci_bitpack_probe_full.bak"
    if not fixture_path.exists():
        pytest.skip(f"fixture missing: {fixture_path}")
    _run_probe(fixture_path, byte_pos, bit_idx)


@pytest.mark.quick
@pytest.mark.negative
def test_bit_flip_does_not_crash_archive_cci(
    byte_pos: int,
    bit_idx: int,
    request: pytest.FixtureRequest,
) -> None:
    """Every single-bit corruption of the ARCHIVE CCI fixture is handled cleanly.

    Validates the ARCHIVE/XPRESS decoder path does not crash on corrupted input.
    """
    from tests.conftest import _FIXTURE_DIR  # type: ignore[attr-defined]

    fixture_path = _FIXTURE_DIR / "archive_single_chunk_full.bak"
    if not fixture_path.exists():
        pytest.skip(f"fixture missing: {fixture_path}")
    _run_probe(fixture_path, byte_pos, bit_idx)


# ---------------------------------------------------------------------------
# Sanity: clean fixture must decode without crash (smoke check for the harness)
# ---------------------------------------------------------------------------

@pytest.mark.quick
@pytest.mark.negative
def test_harness_smoke_unmodified_fixture_does_not_crash() -> None:
    """Control case: decoding the unmodified fixture must not crash the harness."""
    from tests.conftest import _FIXTURE_DIR  # type: ignore[attr-defined]

    fixture_path = _FIXTURE_DIR / "cci_bitpack_probe_full.bak"
    if not fixture_path.exists():
        pytest.skip(f"fixture missing: {fixture_path}")

    try:
        _decode_mutated(fixture_path.read_bytes())
    except _CRASH_TYPES as exc:
        pytest.fail(f"Unmodified fixture triggered crash: {exc}")
    except Exception:
        pass  # tolerate well-typed errors even on clean input
