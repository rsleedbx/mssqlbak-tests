"""Per-worker resource instrumentation — peak RSS, Arrow pool bytes, wall time.

Snapshots are staged at key points in _run_one and returned in the result
dict so cli.py can write a consolidated ``<out>.resources.json`` for analysis.
"""

from __future__ import annotations

import os
import resource as _resource
import time
from typing import Any

import pyarrow as pa

try:
    import psutil as _psutil

    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


def _rss_mb() -> float:
    """Return the current Resident Set Size of this process in MB."""
    if _HAS_PSUTIL:
        try:
            return _psutil.Process().memory_info().rss / (1024 * 1024)
        except Exception:
            pass
    ru = _resource.getrusage(_resource.RUSAGE_SELF)
    # macOS: ru_maxrss is in bytes; Linux: kilobytes
    if os.uname().sysname == "Linux":
        return ru.ru_maxrss / 1024  # KB → MB
    return ru.ru_maxrss / (1024 * 1024)  # bytes → MB


def _peak_rss_mb() -> float:
    """Return the *maximum* Resident Set Size since process start in MB.

    Uses ``ru_maxrss`` (which is a high-water mark, not current RSS) so the
    returned value only ever increases.  Use this alongside current-RSS
    snapshots to verify no memory was released.
    """
    ru = _resource.getrusage(_resource.RUSAGE_SELF)
    if os.uname().sysname == "Linux":
        return ru.ru_maxrss / 1024  # KB → MB
    return ru.ru_maxrss / (1024 * 1024)  # bytes → MB


def _arrow_pool_mb() -> float:
    """Return bytes currently allocated by the Arrow memory pool in MB.

    Returns 0.0 when PyArrow is built without jemalloc (e.g. this macOS
    build) or uses the system allocator — all Rust-side extraction
    allocations bypass Python's pool and will not appear here.
    """
    try:
        return pa.default_memory_pool().bytes_allocated() / (1024 * 1024)
    except Exception:
        return 0.0


class ResourceMonitor:
    """Collects RSS + Arrow pool snapshots during one worker run.

    Instantiate once at the start of ``_run_case``; call ``snapshot()`` at
    each key checkpoint; include ``to_dict()`` in the returned result dict so
    the parent process can aggregate and write ``<out>.resources.json``.
    """

    def __init__(self) -> None:
        self._pid = os.getpid()
        self._t0 = time.perf_counter()
        self._snapshots: list[dict[str, Any]] = []
        self._peak_rss_mb: float = _rss_mb()

    def snapshot(self, label: str) -> None:
        """Record current RSS, process peak RSS (ru_maxrss), and Arrow pool."""
        rss = _rss_mb()
        peak = _peak_rss_mb()
        if rss > self._peak_rss_mb:
            self._peak_rss_mb = rss
        self._snapshots.append(
            {
                "label": label,
                "elapsed_s": round(time.perf_counter() - self._t0, 3),
                "rss_mb": round(rss, 1),
                "peak_rss_mb": round(peak, 1),
                "arrow_mb": round(_arrow_pool_mb(), 1),
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable summary of this monitor's observations."""
        return {
            "pid": self._pid,
            # Our tracked peak (max of sampled current-RSS values)
            "peak_rss_mb": round(self._peak_rss_mb, 1),
            # OS-level high-water mark since process start (ru_maxrss)
            "hwm_rss_mb": round(_peak_rss_mb(), 1),
            "snapshots": self._snapshots,
        }
