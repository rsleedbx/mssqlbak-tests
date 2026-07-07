"""Quick check: extract every sample .bak and print a status line per file."""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

from mssqlbak import extract_bak_to_delta

SAMPLES = Path(__file__).parent.parent / "tests" / "fixtures_realworld"


def main() -> None:
    baks = sorted(SAMPLES.glob("*.bak"))
    if not baks:
        print("No .bak files found in", SAMPLES)
        return

    ok_total = skip_total = err_total = 0
    for bak in baks:
        t0 = time.time()
        try:
            with tempfile.TemporaryDirectory() as d:
                r = extract_bak_to_delta(bak, d)
            skipped = r.skipped
            elapsed = time.time() - t0
            if skipped:
                status = f"SKIP({len(skipped)})"
                skip_total += 1
            else:
                status = "OK"
                ok_total += 1
            print(
                f"{status:12s} {r.total_rows:>10,}r {len(r.extracted):>3}t"
                f"  {elapsed:5.1f}s  {bak.name}"
            )
            for t in skipped[:5]:
                print(f"             skip: {t.name} — {t.skip_reason}")
            if len(skipped) > 5:
                print(f"             ... and {len(skipped) - 5} more")
        except Exception as exc:  # noqa: BLE001
            print(f"{'ERROR':12s} {'':>10}   {'':>3}         {bak.name}: {exc}")
            err_total += 1

    print()
    print(f"Done: {ok_total} fully OK, {skip_total} with skips, {err_total} errors")


if __name__ == "__main__":
    main()
