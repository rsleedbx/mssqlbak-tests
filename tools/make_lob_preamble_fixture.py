"""
G41 fixture: cs_lob_preamble.bak

Creates a CCI table with nvarchar(4000) dictionary blobs large enough to
trigger the LOB preamble + deinterleave path in columnstore.py.

The LOB preamble path fires when the dictionary blob exceeds 65 536 bytes
(_COLUMN_LOB_CHUNK = 65536).  We need:
- A string CCI column with many long, distinct values
- Enough rows to push the dictionary past the 65 KB threshold

Strategy: 1400 rows × ~50-char distinct strings = ~70 KB raw, which should
produce a dictionary blob > 65 536 bytes.  Use nvarchar(4000) to get wide
strings.

Run via tools/fixture_run.py or directly:
  python -m tools.make_lob_preamble_fixture
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

def _sql(container: str, sa_pass: str, query: str, *, database: str = "master") -> None:
    from tools.make_fixture import discover_sqlcmd_path
    result = subprocess.run(
        [
            "podman", "exec", container,
            discover_sqlcmd_path(container),
            "-S", "localhost", "-U", "sa", "-P", sa_pass,
            "-C", "-b",
            "-d", database,
            "-Q", query,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout, result.stderr, file=sys.stderr)
        raise RuntimeError(f"sqlcmd failed (rc={result.returncode})")


def build_sql() -> str:
    # Generate 1400 rows of distinct nvarchar(4000) values.
    # Each value is a unique 60-char string that starts with a different prefix
    # so the dictionary compression cannot collapse them much.
    # 1400 rows × ~120 bytes UTF-16LE per value ≈ 168 KB raw dictionary.
    rows: list[str] = []
    for i in range(1400):
        # Each value is unique and long enough that many are distinct entries
        val = f"row_{i:06d}_" + ("X" * 52)  # ~62 chars → 124 bytes UTF-16LE
        rows.append(f"({i}, N'{val}')")

    insert_chunks: list[str] = []
    chunk_size = 100
    for start in range(0, len(rows), chunk_size):
        chunk = rows[start : start + chunk_size]
        insert_chunks.append(
            "INSERT INTO cs_lob_preamble(id, long_str) VALUES\n"
            + ",\n".join(chunk) + ";"
        )

    inserts = "\n".join(insert_chunks)
    return f"""
IF DB_ID('LobPreamble') IS NOT NULL BEGIN
  ALTER DATABASE LobPreamble SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
  DROP DATABASE LobPreamble;
END;
CREATE DATABASE LobPreamble;
GO
USE LobPreamble;
GO
CREATE TABLE cs_lob_preamble (
    id          int              NOT NULL,
    long_str    nvarchar(4000)   NOT NULL,
    CONSTRAINT  pk_cslp PRIMARY KEY NONCLUSTERED (id)
);
GO
{inserts}
GO
-- Force a columnstore index to compress all rows into one row group
CREATE CLUSTERED COLUMNSTORE INDEX cci_lob_preamble ON cs_lob_preamble
    WITH (MAXDOP=1);
GO
"""


def run(container: str, sa_pass: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    host_bak = out_dir / "cs_lob_preamble.bak"
    if host_bak.exists():
        print(f"skip (already exists): {host_bak.name}", file=sys.stderr)
        return
    container_bak = "/tmp/cs_lob_preamble.bak"

    print("[1/3] Creating LobPreamble database …")
    sql = build_sql()
    _sql(container, sa_pass, sql)

    print("[2/3] Checking dictionary blob size …")
    check_simple = """
USE LobPreamble;
SELECT d.column_id, d.dictionary_id, d.type,
       d.entry_count,
       DATALENGTH(d.columnstore_value) AS blob_bytes
FROM sys.column_store_dictionaries d
JOIN sys.partitions p ON p.partition_id = d.hobt_id
JOIN sys.objects o ON o.object_id = p.object_id
WHERE o.name = 'cs_lob_preamble'
ORDER BY d.column_id, d.dictionary_id;
"""
    from tools.make_fixture import discover_sqlcmd_path
    result = subprocess.run(
        [
            "podman", "exec", container,
            discover_sqlcmd_path(container),
            "-S", "localhost", "-U", "sa", "-P", sa_pass,
            "-C", "-d", "LobPreamble",
            "-Q", check_simple,
        ],
        capture_output=True, text=True,
    )
    print(result.stdout.strip() or "(no dict rows - checking via column_store_segments)")

    count_sql = """
USE LobPreamble;
SELECT COUNT(*) AS segment_count,
       SUM(row_count) AS total_rows
FROM sys.column_store_row_groups
WHERE object_id = OBJECT_ID('cs_lob_preamble');
"""
    result2 = subprocess.run(
        [
            "podman", "exec", container,
            discover_sqlcmd_path(container),
            "-S", "localhost", "-U", "sa", "-P", sa_pass,
            "-C", "-d", "LobPreamble",
            "-Q", count_sql,
        ],
        capture_output=True, text=True,
    )
    print(result2.stdout.strip())

    print("[3/3] Backing up …")
    backup_sql = f"""
USE LobPreamble;
BACKUP DATABASE LobPreamble
  TO DISK = N'{container_bak}'
  WITH COMPRESSION, FORMAT, INIT, STATS=20;
"""
    _sql(container, sa_pass, backup_sql)
    subprocess.run(
        ["podman", "cp", f"{container}:{container_bak}", str(host_bak)],
        check=True,
    )
    print(f"Written: {host_bak} ({host_bak.stat().st_size:,} bytes)")


def main() -> int:
    from tools.fixture_run import bootstrap_fixture_env

    _server, container = bootstrap_fixture_env()
    password = os.environ["FIXTURE_DBA_PASSWORD"]
    fixtures_dir = Path(os.environ.get("FIXTURE_DIR", str(Path(__file__).parent.parent / "tests" / "fixtures")))
    run(container, password, fixtures_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
