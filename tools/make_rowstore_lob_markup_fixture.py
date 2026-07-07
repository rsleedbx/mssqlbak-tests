#!/usr/bin/env python3
"""Generate ``rowstore_lob_markup_full.bak`` — real-world markup LOB cells."""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
    skip_if_exists,
)

DB_NAME = "RowstoreLobMarkup"
TABLE = "lob_markup_probe"
ROW_COUNT = 5

_HTML_VALUES: dict[int, str] = {
    1: "<article><h1>Question</h1><p>Short body &amp; tags.</p></article>",
    2: "html-long-" + ("<p class='body'>realworld markup payload</p>" * 260),
    3: "<div data-kind='mixed'>ASCII markup with entity &quot;quoted&quot;</div>",
}
_WIDE_VALUES: dict[int, str] = {
    1: "wide-body-" + ("Omega " * 40),
    2: "wide-long-" + (chr(0x03A9) * 2048),
    3: "emoji-free unicode " + (chr(0x263A) * 128),
}
_JSON_VALUES: dict[int, str] = {
    1: '{"CustomFields":{"Tags":["fragile","sale"],"Search":"blue widget"}}',
    2: '{"Description":"' + ("searchable product text " * 420) + '"}',
    3: '{"html":"<p>stored as text</p>","empty":"","n":3}',
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


EXPECTED_HTML_SHA256 = {
    row_id: _sha256(value.encode("utf-8"))
    for row_id, value in _HTML_VALUES.items()
}
EXPECTED_WIDE_SHA256 = {
    row_id: _sha256(value.encode("utf-16-le"))
    for row_id, value in _WIDE_VALUES.items()
}
EXPECTED_JSON_SHA256 = {
    row_id: _sha256(value.encode("utf-8"))
    for row_id, value in _JSON_VALUES.items()
}

FIXTURE_DIR = Path(os.environ.get("FIXTURE_DIR", str(_REPO_ROOT / "tests" / "fixtures_2022")))
OUT_PATH = FIXTURE_DIR / "rowstore_lob_markup_full.bak"
_CONTAINER_BAK = f"/tmp/{DB_NAME}_full.bak"


def build_stmts() -> list[str]:
    return [
        f"""IF DB_ID(N'{DB_NAME}') IS NOT NULL BEGIN
    ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [{DB_NAME}]
END""",
        f"CREATE DATABASE [{DB_NAME}]",
        f"USE [{DB_NAME}]",
        f"""CREATE TABLE dbo.{TABLE} (
    id        INT           NOT NULL PRIMARY KEY CLUSTERED,
    html_body VARCHAR(MAX)  NULL,
    wide_body NVARCHAR(MAX) NULL,
    json_body VARCHAR(MAX)  NULL
)""",
        f"""INSERT INTO dbo.{TABLE} (id, html_body, wide_body, json_body)
VALUES
    (1,
     '<article><h1>Question</h1><p>Short body &amp; tags.</p></article>',
     N'wide-body-' + REPLICATE(CAST(N'Omega ' AS NVARCHAR(MAX)), 40),
     '{{"CustomFields":{{"Tags":["fragile","sale"],"Search":"blue widget"}}}}'),
    (2,
     'html-long-' + REPLICATE(CAST('<p class=''body''>realworld markup payload</p>' AS VARCHAR(MAX)), 260),
     N'wide-long-' + REPLICATE(CAST(NCHAR(0x03A9) AS NVARCHAR(MAX)), 2048),
     '{{"Description":"' + REPLICATE(CAST('searchable product text ' AS VARCHAR(MAX)), 420) + '"}}'),
    (3,
     '<div data-kind=''mixed''>ASCII markup with entity &quot;quoted&quot;</div>',
     N'emoji-free unicode ' + REPLICATE(CAST(NCHAR(0x263A) AS NVARCHAR(MAX)), 128),
     '{{"html":"<p>stored as text</p>","empty":"","n":3}}'),
    (4, '', N'', ''),
    (5, NULL, NULL, NULL)""",
        "USE [master]",
        f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{_CONTAINER_BAK}' WITH FORMAT, INIT, COPY_ONLY",
    ]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--force", action="store_true", help="overwrite existing .bak")
    args = p.parse_args()

    if skip_if_exists(OUT_PATH, force=args.force):
        return 0

    user, password, container = fixture_credentials()
    print(f"using container {container} as {user}")
    print(f"inserting {ROW_COUNT} markup LOB rows")

    load_and_backup_stmts(container, user, password, build_stmts())
    size = _copy_out(container, _CONTAINER_BAK, OUT_PATH)
    print(f"wrote {OUT_PATH} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
