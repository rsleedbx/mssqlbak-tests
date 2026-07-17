#!/usr/bin/env python3
"""Empirical check: does a COMPRESSED (MSSQLBAK) fuzzy backup carry the trailing
re-copied modified pages, and does mssqlbak's compressed path read them like
SQL Server's RESTORE?

Builds the same CCI delete scenario as make_dirty_cci_fixture but takes the
concurrent backup ``WITH COMPRESSION``.  Then compares:

  * SQL Server RESTORE row count (ground truth for this .bak)
  * mssqlbak extract row count (compressed path)
  * whether mssqlbak.compressed._iter_pages yields the same page_id twice with
    different LSNs (the re-copied modified pages)

Run: .venv/bin/python -m tools.diag._diag_compressed_fuzzy
"""
from __future__ import annotations

import struct
import sys
from collections import defaultdict
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from mssqlbak.catalog import recover_schema  # noqa: E402
from mssqlbak.pages import PageStore  # noqa: E402
from mssqlbak.rows import read_table_rows  # noqa: E402
import tools.fixture_utils as _fixture_utils  # noqa: E402
from tools.fixture_utils import (  # noqa: E402
    _copy_out,
    fixture_credentials,
    load_and_backup_stmts,
)
from tools.make_dirty_cci_fixture import (  # noqa: E402
    DELETED_ID_HI,
    DELETED_ID_LO,
    _dml_sql_delete,
    _reset_stmts_delete,
    _setup_stmts,
)
from tools.register_bak import _drop_db, _restore_bak, _run_sql_query  # noqa: E402

_DB = "DirtyCCIDelComp"
_CONTAINER_BAK = "/var/opt/mssql/data/_cci_delete_comp.bak"
_HOST_BAK = Path("/private/tmp/_cci_delete_comp.bak")
_MAGIC = b"MSSQLBAK"


def _restore_count(container: str, password: str, host_bak: Path) -> int:
    """Restore *host_bak* and return dbo.dirty_cci row count (-1 on failure)."""
    db = "DiagCompProbe"
    try:
        _restore_bak(container, password, host_bak, db)
        q = f"USE [{db}];SET NOCOUNT ON;SELECT COUNT(*) FROM dbo.dirty_cci;"
        out = _run_sql_query(container, password, q, sep="|").rstrip().splitlines()[-1]
        return int(out.strip())
    except Exception as exc:  # noqa: BLE001
        print("   restore probe failed:", exc, file=sys.stderr)
        return -1
    finally:
        try:
            _drop_db(container, password, db)
        except Exception:
            pass


def _build() -> None:
    """Loop a concurrent DELETE during a COMPRESSED backup until the restored
    image shows the delete captured (count < 7000), which means the modified
    pages were re-copied into the backup — the case we want to test."""
    import threading
    import time

    user, password, container = fixture_credentials()
    print(f"container={container} user={user}", file=sys.stderr)
    load_and_backup_stmts(container, user, password, _setup_stmts(_DB, "delete"))

    dml  = _fixture_utils.connect(container, user, password, database=_DB,      autocommit=False, timeout=300)
    bak  = _fixture_utils.connect(container, user, password, database="master",  autocommit=True,  timeout=300)
    util = _fixture_utils.connect(container, user, password, database=_DB,       autocommit=True,  timeout=300)
    try:
        for attempt in range(1, 41):
            for stmt in _reset_stmts_delete():
                util.cursor().execute(stmt)
            delay = 0.002 + 0.001 * (attempt % 12)

            def _do(c: object = dml, s: str = _dml_sql_delete(), d: float = delay) -> None:
                time.sleep(d)
                c.cursor().execute(s)  # type: ignore[union-attr]
                c.commit()  # type: ignore[union-attr]

            t = threading.Thread(target=_do, daemon=True)
            t.start()
            bak.cursor().execute(
                f"BACKUP DATABASE [{_DB}] TO DISK=N'{_CONTAINER_BAK}' "
                "WITH FORMAT,INIT,BUFFERCOUNT=1,MAXTRANSFERSIZE=65536,COMPRESSION"
            )
            t.join(timeout=30)
            _copy_out(container, _CONTAINER_BAK, _HOST_BAK)
            cnt = _restore_count(container, password, _HOST_BAK)
            print(f"   attempt {attempt} delay={delay*1000:.0f}ms -> restore count={cnt}",
                  file=sys.stderr)
            if 0 <= cnt < 7000:
                print(f"captured delete in compressed image (count={cnt})", file=sys.stderr)
                return
        print("WARNING: never captured the delete in the compressed image", file=sys.stderr)
    finally:
        dml.close()
        bak.close()
        util.close()


def _restore_truth() -> str:
    user, password, container = fixture_credentials()
    db = "DiagCompFuzzy"
    try:
        _restore_bak(container, password, _HOST_BAK, db)
        q = (f"USE [{db}];SET NOCOUNT ON;"
             f"SELECT COUNT(*) total, "
             f"SUM(CASE WHEN id BETWEEN {DELETED_ID_LO} AND {DELETED_ID_HI} "
             f"THEN 1 ELSE 0 END) band FROM dbo.dirty_cci;")
        return _run_sql_query(container, password, q, sep="|").rstrip().splitlines()[-1]
    finally:
        try:
            _drop_db(container, password, db)
        except Exception:
            pass


def _mssqlbak_count() -> tuple[int, int]:
    store = PageStore.from_bak(_HOST_BAK)
    tabs = {t.name: t for t in recover_schema(store).tables}
    rows = list(read_table_rows(store, tabs["dirty_cci"]))
    ids = [r["id"] for r in rows if isinstance(r.get("id"), int)]
    band = [i for i in ids if DELETED_ID_LO <= i <= DELETED_ID_HI]
    return len(rows), len(band)


def _duplicate_pages() -> None:
    from mssqlbak.compressed import _iter_pages
    data = _HOST_BAK.read_bytes()
    assert data[:8] == _MAGIC, "not an MSSQLBAK container"
    seen: dict[tuple[int, int], list[tuple[int, int, int]]] = defaultdict(list)
    order: dict[tuple[int, int], int] = {}
    n = 0
    for i, (fid, pid, page) in enumerate(_iter_pages(data)):
        lsn = struct.unpack_from("<IIH", page, 40)
        seen[(fid, pid)].append(lsn)
        order[(fid, pid)] = i
        n += 1
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    print(f"_iter_pages yielded {n} pages; {len(dups)} page_ids appear >1 time")
    for k in sorted(dups)[:10]:
        print("  dup", k, "LSNs(order):", dups[k])


def main() -> int:
    from tools.fixture_run import bootstrap_fixture_env
    bootstrap_fixture_env()
    if not _HOST_BAK.exists():
        _build()
    else:
        print(f"reusing existing {_HOST_BAK}", file=sys.stderr)
    print("magic:", _HOST_BAK.read_bytes()[:8])
    print("SQL restore (total|band):", _restore_truth())
    total, band = _mssqlbak_count()
    print(f"mssqlbak extract: total={total} band={band}")
    _duplicate_pages()
    return 0


if __name__ == "__main__":
    sys.exit(main())
