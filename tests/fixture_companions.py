"""Companion-file resolution for striped / differential ``.bak`` fixtures.

A handful of fixtures cannot be extracted from a single ``.bak`` file:

* **Striped backups** (``prefix_N.bak``, single-digit ``N``) split one database
  across several files; ``extract_bak_to_delta`` needs the whole set.
* **Differential backups** (``*_diff*.bak``) only contain changed pages; they
  need their base ``*_full.bak`` so the diff pages shadow the full-backup pages.

Both ``tests/test_stats.py`` and ``tests/test_value_correctness.py`` resolve
companions through this single module so the two never drift.
"""

from __future__ import annotations

import re
from pathlib import Path


def resolve_bak_input(bak_path: Path) -> Path | list[Path]:
    """Return a single path, or an ordered list of the files needed to extract.

    * Striped backups (``prefix_N.bak``, single-digit N): return all siblings
      sorted by their numeric suffix.  The caller passes the full list to
      ``extract_bak_to_delta`` so ``PageStore.from_stripe`` merges them.
    * Differential backups (``*_diff*.bak``): return ``[full_bak, diff_bak]``
      so diff pages shadow full-backup pages (last-seen-wins in from_stripe).
    * Anything else: return the single path unchanged.
    """
    stem = bak_path.stem

    # Striped: ends with single digit (e.g. striped_full_1, striped_full_2)
    m = re.match(r"^(.+)_(\d)$", stem)
    if m:
        prefix = m.group(1)
        siblings = sorted(
            bak_path.parent.glob(f"{prefix}_?.bak"),
            key=lambda p: int(re.search(r"_(\d)$", p.stem).group(1)),  # type: ignore[union-attr]
        )
        if len(siblings) > 1:
            return siblings

    # Differential: stem contains _diff (e.g. tabletypecoverage_diff,
    # incrementalcoverage_diff_01)
    full_stem = re.sub(r"_diff(_.+)?$", "_full", stem)
    if full_stem != stem:
        full_path = bak_path.parent / f"{full_stem}.bak"
        if full_path.exists():
            return [full_path, bak_path]

    return bak_path


def is_redundant_stripe(bak_path: Path) -> bool:
    """True if ``bak_path`` is a striped companion other than the lowest stripe.

    Stripe companions share identical data, so only the first (lowest-numbered)
    stripe should be exercised; the rest are redundant and resolve to the same
    merged extraction via :func:`resolve_bak_input`.
    """
    m = re.match(r"^(.+)_(\d)$", bak_path.stem)
    if not m:
        return False
    prefix, digit = m.group(1), int(m.group(2))
    return any(
        (bak_path.parent / f"{prefix}_{d}.bak").exists()
        for d in range(1, digit)
    )
