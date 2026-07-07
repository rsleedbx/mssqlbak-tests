"""Locate the source of NUL corruption in dirty-fixture string values.

Instruments the char/nchar decoders: whenever a decoded value contains a NUL,
record the raw input bytes.  If the raw bytes already contain the NUL, the bug
is upstream (log-tail row reconstruction); if not, it is in the decoder.
"""
from __future__ import annotations

import sys
from pathlib import Path

import mssqlbak.rows as R
from mssqlbak import logtail as L
from mssqlbak import types as T
from mssqlbak.catalog import recover_schema
from mssqlbak.logtail import logtail_from_bak
from mssqlbak.pages import PageStore
from mssqlbak.rows import read_table_rows

_hits: list[tuple[str, bytes, str]] = []
_splice: list[str] = []
_subs: list[str] = []

_orig_payload = L._read_log_payload


def _wrap_payload(data, block_start, payload_start, length):  # type: ignore[no-untyped-def]
    out = _orig_payload(data, block_start, payload_start, length)
    # Re-walk the same boundary logic to record, for each substituted byte, the
    # actual on-disk byte value so we can tell sector-framing (0x40) from a
    # boundary-math error (a genuine data byte being zeroed).
    BS = L._BLOCK_SIZE
    in_block = payload_start
    cur_block = block_start
    o = 0
    while o < length:
        if in_block >= BS:
            cur_block += BS
            in_block -= BS
        if in_block % 512 == 0:
            absp = cur_block + in_block
            actual = data[absp] if absp < len(data) else None
            if length <= 64:
                _subs.append(f"sub@abs={absp} (abs%512={absp%512}) actual_byte={actual:#04x} payload_start={payload_start} len={length}")
            o += 1
            in_block += 1
        else:
            nxt = (in_block // 512 + 1) * 512
            chunk = min(nxt - in_block, length - o)
            o += chunk
            in_block += chunk
    return out


L._read_log_payload = _wrap_payload  # type: ignore

_orig_char = T._decode_char
_orig_nchar = T._decode_nchar

_NEEDLE = b"update\x00"


def _wrap_splice(name: str, fn):  # type: ignore[no-untyped-def]
    def inner(arg0, patch):  # type: ignore[no-untyped-def]
        out = fn(arg0, patch)
        if _NEEDLE in bytes(out):
            rs = getattr(patch, "row_start", None)
            rd = getattr(patch, "redo_data", None)
            ud = getattr(patch, "undo_data", None)
            ure = getattr(patch, "undo_row_end", None)
            rre = getattr(patch, "redo_row_end", None)
            _splice.append(
                f"{name}: row_start={rs} undo_row_end={ure} redo_row_end={rre}\n"
                f"    redo_data={rd.hex(' ') if rd else rd}\n"
                f"    undo_data={ud.hex(' ') if ud else ud}\n"
                f"    in ={bytes(arg0).hex(' ')}\n"
                f"    out={bytes(out).hex(' ')}"
            )
        return out
    return inner


R._apply_redo_patch = _wrap_splice("redo", R._apply_redo_patch)  # type: ignore
R._apply_redo_patch_cd = _wrap_splice("redo_cd", R._apply_redo_patch_cd)  # type: ignore
R._apply_before_image = _wrap_splice("before", R._apply_before_image)  # type: ignore
R._apply_before_image_cd = _wrap_splice("before_cd", R._apply_before_image_cd)  # type: ignore


def _wrap_char(raw: bytes, *a, **k):  # type: ignore[no-untyped-def]
    out = _orig_char(raw, *a, **k)
    if isinstance(out, str) and "\x00" in out:
        _hits.append(("char", bytes(raw), out))
    return out


def _wrap_nchar(raw: bytes, *a, **k):  # type: ignore[no-untyped-def]
    out = _orig_nchar(raw, *a, **k)
    if isinstance(out, str) and "\x00" in out:
        _hits.append(("nchar", bytes(raw), out))
    return out


def main() -> int:
    bak = Path(sys.argv[1])
    table_filter = sys.argv[2] if len(sys.argv) > 2 else None
    T._decode_char = _wrap_char  # type: ignore[assignment]
    T._decode_nchar = _wrap_nchar  # type: ignore[assignment]
    ps = PageStore.from_bak(str(bak))
    sch = recover_schema(ps)
    lt = logtail_from_bak(str(bak))
    for t in sch.tables:
        if table_filter and table_filter not in t.name:
            continue
        rows = list(read_table_rows(
            ps, t,
            dirty_slots=lt.dirty_slots,
            restore_slots=lt.restore_slots,
            before_images=lt.before_images,
            redo_rows=lt.redo_rows,
            committed_delete_slots=lt.committed_delete_slots,
            redo_patches=lt.redo_patches,
            restore_rows=lt.restore_rows,
        ))
        print(f"table {t.name}: {len(rows)} rows")
    print(f"\n{len(_hits)} decoded values contain NUL")
    print(f"\n{len(_subs)} sector-boundary substitutions on small payloads:")
    for s in _subs[:12]:
        print("  " + s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
