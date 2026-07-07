#!/usr/bin/env python3
"""G44 DBCC CSINDEX probe — columnstore binary dictionary (version-4 hash format).

Restores ``cs_lob_preamble2.bak`` and runs
  DBCC TRACEON(3604);
  DBCC CSINDEX(<db>, <rowset_id>, <col_id>, 0, 2, 0);
to dump the contents of the dictionary (object_type=2) for the ``long_str``
column.  The output maps entry indices → string values, which we can then
correlate against the raw blob bytes in ``tests/fixtures_2022/probe/G44_blob.bin``
to reverse-engineer the version-4 binary-dictionary layout.

Run via:
    python -m tools.make_g44_probe
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fixture_utils import _run_sql, fixture_credentials, sqlcmd_base  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

_SQL_G44 = r"""
SET NOCOUNT ON;
GO

DECLARE @bak NVARCHAR(500);
SET @bak = N'/tmp/cs_lob_preamble2.bak';

IF DB_ID(N'G44Probe') IS NOT NULL BEGIN
    ALTER DATABASE [G44Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [G44Probe];
END;

RESTORE DATABASE [G44Probe] FROM DISK = @bak
WITH MOVE N'LobPreamble2' TO N'/var/opt/mssql/data/G44Probe.mdf',
     MOVE N'LobPreamble2_log' TO N'/var/opt/mssql/data/G44Probe_log.ldf',
     REPLACE, STATS=10;
GO

USE [G44Probe];
GO

-- Dictionary catalog for the long_str CCI column
SELECT
    p.partition_id AS hobt_id,
    c.column_id,
    c.name AS col_name,
    d.dictionary_id,
    d.type,
    d.entry_count
FROM sys.column_store_dictionaries d
JOIN sys.partitions p ON p.partition_id = d.hobt_id
JOIN sys.indexes i ON i.object_id = p.object_id AND i.index_id = p.index_id
JOIN sys.columns c ON c.object_id = p.object_id AND c.column_id = d.column_id
WHERE i.type = 5  -- clustered columnstore
ORDER BY c.column_id, d.dictionary_id;
GO

-- DBCC CSINDEX segment dump for col long_str (object_type=1 = segment)
DBCC TRACEON(3604);
GO

DECLARE @db   INT = DB_ID();
DECLARE @hobt BIGINT;
SELECT TOP 1 @hobt = p.partition_id
FROM sys.partitions p
JOIN sys.indexes i ON i.object_id = p.object_id AND i.index_id = p.index_id
WHERE i.type = 5;

PRINT CONCAT(N'DBCC CSINDEX: db=', @db, N' hobt=', @hobt, N' col=2 dict=0');

-- object_type=1 = column segment (gives encoding, min/max, bitpack info)
DBCC CSINDEX(@db, @hobt, 2, 0, 1, 0) WITH NO_INFOMSGS;
GO

-- ALL 1200 row values ordered by long_str (= sorted rank order)
-- Rank 0 = first alphabetically, rank 1199 = last
SELECT id, long_str FROM cs_lob_preamble ORDER BY long_str;
GO

USE [master];
GO

IF DB_ID(N'G44Probe') IS NOT NULL BEGIN
    ALTER DATABASE [G44Probe] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [G44Probe];
END;
GO
"""


def run(container: str, sa_pass: str, out_dir: Path) -> None:
    import subprocess

    out_dir.mkdir(parents=True, exist_ok=True)
    bak_src  = out_dir / "cs_lob_preamble2.bak"
    probe_out = out_dir / "G44_csindex_output.txt"

    if not bak_src.exists():
        print(f"skip: {bak_src} not found", file=sys.stderr)
        return

    # Copy the .bak into the container
    print("copying cs_lob_preamble2.bak into container …", file=sys.stderr)
    cp = subprocess.run(
        ["podman", "cp", str(bak_src), f"{container}:/tmp/cs_lob_preamble2.bak"],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        raise RuntimeError(f"podman cp failed: {cp.stderr}")

    print("running DBCC CSINDEX probe …", file=sys.stderr)
    sqlcmd = sqlcmd_base("sa", sa_pass, container)
    output = _run_sql(container, sqlcmd, _SQL_G44)

    probe_out.write_text(output, encoding="utf-8")
    print(f"wrote {probe_out}", file=sys.stderr)

    # Also dump the raw dict blob to a binary sidecar
    from mssqlbak.pages import PageStore
    from mssqlbak.mtf import extract_mdf_pages
    from mssqlbak.catalog import _bootstrap
    from mssqlbak.columnstore import _collect_blobs, _read_dict_blob_ids
    from mssqlbak.catalog import recover_schema

    img   = extract_mdf_pages(bak_src)
    store = PageStore(img)
    boot  = _bootstrap(store)
    schema = recover_schema(store)
    blobs = _collect_blobs(store)
    t = schema.tables[0]
    rowset_ids = {rs for _, rs in boot.obj_to_rowsets.get(t.object_id, [])}
    dict_bids  = _read_dict_blob_ids(store, boot, rowset_ids)

    for key, bid in sorted(dict_bids.items()):
        blob = blobs.get(bid)
        if blob:
            blob_path = out_dir / f"G44_dict_blob_{bid}.bin"
            blob_path.write_bytes(blob)
            print(f"wrote raw blob {bid}: {len(blob)} bytes → {blob_path}", file=sys.stderr)

    print("done", file=sys.stderr)


def main() -> int:
    user, password, container = fixture_credentials()
    out_dir_default = REPO_ROOT / "tests" / "fixtures_2022"
    out_dir = Path(os.environ.get("FIXTURE_DIR", out_dir_default))
    run(container, password, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
