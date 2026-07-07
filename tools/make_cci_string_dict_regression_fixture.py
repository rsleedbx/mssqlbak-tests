#!/usr/bin/env python3
"""Generate ``cci_string_dict_regression_full.bak``.

This fixture is a fast synthetic guard for real-world TPC-BB string dictionary
failures observed in ``dbo.item.i_item_desc`` and
``dbo.product_reviews.pr_review_content``.  It uses bounded VARCHAR columns in a
clustered columnstore table with two compressed rowgroups, high-cardinality
deterministic strings, explicit empty strings, and NULL sentinels.

Usage:
    python -m tools.fixture_run cci-string-dict-regression
    python -m tools.fixture_run all-versions --suite cci-string-dict-regression
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    seed_sql,
    skip_if_exists,
)

DB_NAME = "CciStringDictRegression"
TABLE = "cci_string_dict_regression"

BATCH1_ROWS = 8_192
BATCH2_ROWS = 8_192
TOTAL_ROWS = BATCH1_ROWS + BATCH2_ROWS

EMPTY_ID = 1
NULL_ID = 2
SAMPLE_IDS = [1, 2, 3, 1_024, BATCH1_ROWS, BATCH1_ROWS + 1, TOTAL_ROWS]

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "cci_string_dict_regression_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def _padded_id(idv: int) -> str:
    return f"{idv:06d}"


def expected_item_desc(idv: int) -> str | None:
    """Return the expected i_item_desc-like value for *idv*."""
    if idv == NULL_ID:
        return None
    if idv == EMPTY_ID:
        return ""
    ch = chr(65 + (idv % 26))
    width = 12 + (idv % 29)
    return (
        f"ITEM-DESC-{_padded_id(idv)}|CLASS={idv % 97:02d}|"
        f"FORM={idv % 17:02d}|{ch * width}"
    )


def expected_review_content(idv: int) -> str | None:
    """Return the expected pr_review_content-like value for *idv*."""
    if idv == NULL_ID:
        return None
    if idv == EMPTY_ID:
        return ""
    ch = chr(97 + (idv % 26))
    width = 40 + (idv % 73)
    return (
        f"review-{_padded_id(idv)}: customer noted quality={idv % 11}; "
        f"shipping={idv % 7}; value={idv % 13}. "
        f"payload[{ch * width}] end."
    )


def _item_sql_expr(id_expr: str) -> str:
    return f"""CASE
        WHEN {id_expr} = {NULL_ID} THEN NULL
        WHEN {id_expr} = {EMPTY_ID} THEN ''
        ELSE
            'ITEM-DESC-' + RIGHT('000000' + CAST({id_expr} AS VARCHAR(6)), 6) +
            '|CLASS=' + RIGHT('00' + CAST({id_expr} % 97 AS VARCHAR(2)), 2) +
            '|FORM=' + RIGHT('00' + CAST({id_expr} % 17 AS VARCHAR(2)), 2) +
            '|' + REPLICATE(CHAR(65 + ({id_expr} % 26)), 12 + ({id_expr} % 29))
    END"""


def _review_sql_expr(id_expr: str) -> str:
    return f"""CASE
        WHEN {id_expr} = {NULL_ID} THEN NULL
        WHEN {id_expr} = {EMPTY_ID} THEN ''
        ELSE
            'review-' + RIGHT('000000' + CAST({id_expr} AS VARCHAR(6)), 6) +
            ': customer noted quality=' + CAST({id_expr} % 11 AS VARCHAR(2)) +
            '; shipping=' + CAST({id_expr} % 7 AS VARCHAR(2)) +
            '; value=' + CAST({id_expr} % 13 AS VARCHAR(2)) +
            '. payload[' + REPLICATE(CHAR(97 + ({id_expr} % 26)), 40 + ({id_expr} % 73)) +
            '] end.'
    END"""


def _insert_batch_stmt(start_id: int, rows: int) -> str:
    id_expr = f"(pk + {start_id})"
    return f"""INSERT INTO dbo.{TABLE} (id, batch, i_item_desc, pr_review_content)
SELECT
    {id_expr} AS id,
    CASE WHEN {id_expr} <= {BATCH1_ROWS} THEN 1 ELSE 2 END AS batch,
    {_item_sql_expr(id_expr)} AS i_item_desc,
    {_review_sql_expr(id_expr)} AS pr_review_content
FROM fkr__seed
WHERE pk < {rows}"""


def build_stmts() -> list[str]:
    stmts: list[str] = [
        f"""IF DB_ID('{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
    ]
    stmts += seed_sql(max(BATCH1_ROWS, BATCH2_ROWS))
    stmts += [
        f"""CREATE TABLE dbo.{TABLE} (
    id INT NOT NULL,
    batch INT NOT NULL,
    i_item_desc VARCHAR(120) NULL,
    pr_review_content VARCHAR(320) NULL
)""",
        f"CREATE CLUSTERED COLUMNSTORE INDEX cci_{TABLE} ON dbo.{TABLE}",
        _insert_batch_stmt(1, BATCH1_ROWS),
        f"ALTER INDEX cci_{TABLE} ON dbo.{TABLE} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        _insert_batch_stmt(BATCH1_ROWS + 1, BATCH2_ROWS),
        f"ALTER INDEX cci_{TABLE} ON dbo.{TABLE} REORGANIZE WITH (COMPRESS_ALL_ROW_GROUPS = ON)",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]
    return stmts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = parser.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {TOTAL_ROWS:,} bounded VARCHAR CCI rows in two batches")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
