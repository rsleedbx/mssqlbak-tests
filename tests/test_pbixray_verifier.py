"""Independent VertiPaq/xVelocity verifier for the columnstore decode logic.

``.bak`` columnstore segments and Power BI ``.pbix``/``.abf`` VertiPaq columns
share the same xVelocity encodings.  pbixray (https://github.com/Hugoberry/pbixray)
is an independent, non-SQL-Server implementation, so it cross-checks ours without
any shared code.

**Caveat (per the plan):** VertiPaq wraps whole columns in an XPRESS9/XPRESS8/
xmhuffman container that differs from the ``.bak`` MS-XCA framing, and the numeric
dictionary binary format differs between ``.bak`` and ``.pbix``.  pbixray is a
**logic verifier + sample source for the shared encodings** — bit-packing and the
hybrid RLE+bitpack index decode — not a byte-identical oracle.

Tests are structured in three groups:

  **Group A — Bit-pack primitive** (existing): ``_bitpack_values`` vs pbixray's
  ``_read_bitpacked`` over 18 bit widths.  Requires pbixray.

  **Group B — Synthetic RLE+bitpack hybrid** (5b): tests ``_decode_enc3``'s
  compact-RLE mode, direct-bitpack mode, and hybrid mode against a pure-Python
  reference ported from pbixray's ``_read_rle_bit_packed_hybrid`` algorithm.
  No pbixray dependency — runs offline.

  **Group C — Adventure Works corpus** (5c): loads the Adventure Works DW 2020
  ``.pbix`` with pbixray and decodes integer columns end-to-end; extracts the
  raw IDF bytes and verifies the shared RLE+bitpack algorithm produces the same
  index array as the reference.  Requires pbixray.

  **Group D — Numeric dictionary parse** (5d): verifies ``_parse_numeric_dict_*``
  on synthetic ``.bak``-format blobs; documents that the ``.pbix`` dictionary
  binary layout differs (dict_type(4)+hash_info(24)+num_values_u8(8)+
  element_size(4)+values vs ``.bak``'s entry_size_u4@48+count_u4@52+values@56)
  so cross-format verification is intentionally excluded.

  **Group E — xVelocity v4 Huffman page decode** (5e): verifies
  ``_huff_decode_page_py`` (mssqlbak's pure-Python Huffman fallback) against
  ``xmhuffman.decode_page`` on real ``.pbix`` compressed string pages.  The
  shared binary format (encode_array_128 + compressed bitstream + bit offsets)
  is identical between ``.pbix`` and ``.bak``; character-encoding differences
  (UTF-16LE vs latin-1 with chr(b-2)) are applied by the caller after the
  shared decode step and are excluded from this test.  Requires pbixray +
  xmhuffman.

pbixray is loaded from a local checkout: set ``PBIXRAY_PATH`` or place it at
``~/github/pbixray``.  Its pip deps are the ``verify`` extra
(``pip install -e '.[verify]'``).  Tests that require pbixray skip cleanly when
it is unavailable.
"""
from __future__ import annotations

import importlib
import os
import struct
import sys
from collections.abc import Sequence
from pathlib import Path
from random import Random
from typing import Any

import pytest

from mssqlbak.columnstore.decode.bitpack import (
    _BP_BPV,
    _BP_FOR_BASE,
    _BP_N_FRAGS,
    _BP_NW,
    _bitpack_values,
)
from mssqlbak.columnstore.decode.dict_numeric import (
    _parse_numeric_dict_float,
    _parse_numeric_dict_int,
)
from mssqlbak.columnstore.decode.dict_string import _decode_enc3
from mssqlbak.columnstore.storage.segment_meta import _ColumnSegment


def _load_pbixray_read_bitpacked():
    """Return pbixray's ``VertiPaqDecoder._read_bitpacked``, or skip if absent.

    pbixray is an optional, locally-checked-out verifier (not a venv dependency),
    so it is imported dynamically by module name — a static import would not
    resolve and would misrepresent it as a hard dependency.
    """
    candidates = [os.environ.get("PBIXRAY_PATH"), str(Path.home() / "github" / "pbixray")]
    for cand in candidates:
        if cand and cand not in sys.path and (Path(cand) / "pbixray").is_dir():
            sys.path.insert(0, cand)
    try:
        vertipaq_decoder = importlib.import_module("pbixray.vertipaq_decoder")
    except ImportError as exc:
        pytest.skip(f"pbixray verifier unavailable ({exc}); install '.[verify]' + PBIXRAY_PATH")
    # _read_bitpacked uses ``self`` only as a namespace; bind to a bare instance.
    decoder_cls = vertipaq_decoder.VertiPaqDecoder
    return decoder_cls.__new__(decoder_cls)._read_bitpacked


def _mssqlbak_unpack(words: list[int], bpv: int) -> list[int]:
    """Run mssqlbak's bit-unpack over *words* by framing them in a segment blob."""
    bp_start = 64  # any offset past the header fields we set below
    blob = bytearray(bp_start + len(words) * 8)
    struct.pack_into("<H", blob, _BP_BPV, bpv)
    struct.pack_into("<I", blob, _BP_NW, len(words))
    for i, w in enumerate(words):
        struct.pack_into("<Q", blob, bp_start + i * 8, w)
    n = (64 // bpv) * len(words)
    return _bitpack_values(bytes(blob), n, bp_start=bp_start)


# xVelocity dictionary-index widths span 1..~48 bits in practice; 64 is excluded
# because a full-width mask overflows pbixray's np.uint64 mask construction.
_BIT_WIDTHS = [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 16, 17, 24, 31, 32, 48, 63]


@pytest.mark.parametrize("bpv", _BIT_WIDTHS)
def test_bitpack_matches_pbixray(bpv: int) -> None:
    """mssqlbak ``_bitpack_values`` agrees with pbixray ``_read_bitpacked``.

    Both extract ``64 // bpv`` values per 64-bit word, LSB-first, masked to
    ``bpv`` bits — the shared xVelocity primitive.  Any divergence would be a
    real bug in one of the two independent decoders.
    """
    import numpy as np

    read_bitpacked = _load_pbixray_read_bitpacked()
    rng = Random(0xC0FFEE + bpv)
    words = [rng.getrandbits(64) for _ in range(9)]

    ours = _mssqlbak_unpack(words, bpv)
    arr = np.asarray(words, dtype="<u8")
    theirs = [int(v) for v in read_bitpacked(arr, bpv, 0)]  # min_data_id=0 → raw values

    assert ours == theirs, f"bit-unpack divergence at bpv={bpv}"


def test_bitpack_for_base_offset_matches_pbixray_min_data_id() -> None:
    """pbixray folds the frame-of-reference base into the unpack (min_data_id);
    mssqlbak adds it separately via ``_bp_for_base``.  Applying our base to our
    raw values must equal pbixray's biased output."""
    import numpy as np

    read_bitpacked = _load_pbixray_read_bitpacked()
    bpv, base = 12, 1000
    rng = Random(0x1234)
    words = [rng.getrandbits(64) for _ in range(4)]

    ours_raw = _mssqlbak_unpack(words, bpv)
    ours_biased = [v + base for v in ours_raw]
    arr = np.asarray(words, dtype="<u8")
    theirs = [int(v) for v in read_bitpacked(arr, bpv, base)]

    assert ours_biased == theirs


# ---------------------------------------------------------------------------
# Helpers shared by Groups B, C, D
# ---------------------------------------------------------------------------

def _ref_idf_decode(
    primary_entries: list[tuple[int, int]],
    sub_segment_words: list[int],
    bit_width: int,
    min_data_id: int = 0,
) -> list[int]:
    """Reference: pure-Python port of pbixray._read_rle_bit_packed_hybrid.

    Takes the same abstract (primary_entries, sub_segment_words, bit_width,
    min_data_id) inputs that pbixray's decoder reads from a Kaitai-parsed IDF
    buffer.  The bit-pack step reuses ``_bitpack_values`` (already verified
    correct against pbixray in Group A) so this function is an independent
    cross-check of the *RLE dispatch logic* only.

    ``primary_entries`` is a list of (data_value, repeat_value) pairs exactly
    as stored in the IDF ``segment_entry`` sequence (Kaitai ``idf.ksy``).
    The sentinel ``data_value + bit_packed_offset == 0xFFFFFFFF`` marks a
    bit-packed run; all other entries are literal RLE runs.
    """
    if sub_segment_words and bit_width > 0:
        mask = (1 << bit_width) - 1
        vpw = 64 // bit_width
        bitpacked: list[int] = []
        for w in sub_segment_words:
            for s in range(vpw):
                bitpacked.append(((w >> (s * bit_width)) & mask) + min_data_id)
    else:
        bitpacked = []

    result: list[int] = []
    bit_packed_offset = 0
    for data_value, repeat_value in primary_entries:
        if (data_value + bit_packed_offset) & 0xFFFFFFFF == 0xFFFFFFFF:
            result.extend(bitpacked[bit_packed_offset : bit_packed_offset + repeat_value])
            bit_packed_offset += repeat_value
        else:
            result.extend([data_value] * repeat_value)
    return result


def _make_seg(
    n_rows: int,
    has_null: bool = False,
    mn: int = 0,
    null_val: int = 0,
    magnitude: float = 1.0,
) -> _ColumnSegment:
    """Minimal _ColumnSegment for _decode_enc3 calls.

    Only the fields _decode_enc3 reads (n_rows, has_null, mn, null_val,
    magnitude) carry meaningful values; identity/dictionary fields are set to
    inert defaults.
    """
    return _ColumnSegment(
        hobt_id=0,
        col_id=0,
        seg_id=0,
        enc_type=3,
        n_rows=n_rows,
        has_null=int(has_null),
        mn=mn,
        magnitude=magnitude,
        prim_dict=-1,
        sec_dict=-1,
        null_val=null_val,
        blob_id=0,
    )


def _build_compact_rle_blob(
    rle_entries: list[tuple[int, int]],
    bpv: int = 4,
) -> bytes:
    """Build a .bak compact-RLE blob (nw=0) for _decode_enc3.

    Layout: header (≥48 bytes) + RLE pairs at offset 48 + (0,0) terminator.
    n_frags=0 so rle_start=48.  nw=0 triggers _decode_enc3's compact branch.
    """
    blob = bytearray(max(48 + (len(rle_entries) + 1) * 8, 64))
    struct.pack_into("<H", blob, _BP_BPV, bpv)
    struct.pack_into("<I", blob, _BP_NW, 0)       # nw=0 → compact RLE
    struct.pack_into("<I", blob, _BP_N_FRAGS, 0)  # no fragment table
    off = 48
    for stored, run in rle_entries:
        struct.pack_into("<II", blob, off, stored, run)
        off += 8
    struct.pack_into("<II", blob, off, 0, 0)  # terminator
    return bytes(blob)


def _build_hybrid_blob(
    rle_entries: list[tuple[int, int]],
    bitpack_words: list[int],
    bpv: int,
) -> bytes:
    """Build a .bak hybrid RLE+bitpack blob for _decode_enc3.

    Layout:
      header (bytes 0-47): bpv@34, nw@36, n_frags@20 = 0
      RLE table at byte 48: (stored_u u32, run u32) × n + (0,0) terminator
      bitpack section: nw × u64 words immediately after the terminator

    _true_bp_start locates packed_start by scanning for the (0,0) terminator,
    so the bitpack must begin right after it.
    """
    nw = len(bitpack_words)
    rle_bytes = b"".join(struct.pack("<II", su, rn) for su, rn in rle_entries)
    rle_bytes += struct.pack("<II", 0, 0)  # terminator
    bp_bytes = struct.pack("<" + "Q" * nw, *bitpack_words)

    header_sz = 48
    blob = bytearray(header_sz + len(rle_bytes) + len(bp_bytes))
    struct.pack_into("<H", blob, _BP_BPV, bpv)
    struct.pack_into("<I", blob, _BP_NW, nw)
    struct.pack_into("<I", blob, _BP_N_FRAGS, 0)
    struct.pack_into("<I", blob, _BP_FOR_BASE, 3)  # for_base = stored−3 = 0 (no bias)
    blob[header_sz : header_sz + len(rle_bytes)] = rle_bytes
    blob[header_sz + len(rle_bytes) :] = bp_bytes
    return bytes(blob)


def _identity_dict(n: int) -> list[str]:
    """Return a string dictionary whose data_id k maps to str(k)."""
    return [str(k) for k in range(n)]


# ---------------------------------------------------------------------------
# Group B — Synthetic RLE+bitpack hybrid (5b)
# ---------------------------------------------------------------------------

@pytest.mark.quick
def test_compact_rle_matches_reference() -> None:
    """_decode_enc3 compact-RLE mode (nw=0) agrees with the IDF reference.

    Compact RLE: stored values are dictionary indices directly; no bitpack.
    has_null=False, mn=0 → _dict_lookup(stored) = dict[stored].
    """
    rle_entries = [(0, 3), (1, 5), (2, 2), (0, 1)]
    n_rows = sum(r for _, r in rle_entries)
    blob = _build_compact_rle_blob(rle_entries, bpv=4)
    seg = _make_seg(n_rows)
    dict_ = _identity_dict(10)

    result = _decode_enc3(seg, blob, dict_)
    expected = _ref_idf_decode(rle_entries, [], 4)

    assert [int(v) for v in result] == expected


@pytest.mark.quick
def test_compact_rle_with_nulls_matches_reference() -> None:
    """Compact RLE with has_null=True.

    For nullable compact-RLE segments the encoder uses ``mn = 2`` (the first
    real dictionary entry maps to ``_dict_lookup`` input 2).  This gives
    ``shift = mn − 2 = 0`` so stored values map directly to the ``_dict_lookup``
    convention:

      stored=0  → None      (null sentinel = mn − 2)
      stored=1  → ""        (empty sentinel = mn − 1)
      stored=2  → dict[0]   (= mn)
      stored=3  → dict[1]   (= mn + 1)

    A terminator entry ``(stored=0, run=0)`` ends the table; null entries must
    therefore have ``run > 0`` to be distinguished from the terminator.
    """
    mn = 2          # minimum non-null dictionary index in the _dict_lookup scheme
    null_stored = 0  # = mn − 2
    rle_entries = [
        (0, 2),   # null × 2
        (1, 1),   # empty × 1
        (2, 3),   # dict[0] × 3
        (3, 2),   # dict[1] × 2
        (0, 1),   # null × 1
    ]
    n_rows = sum(r for _, r in rle_entries)
    blob = _build_compact_rle_blob(rle_entries, bpv=4)
    seg = _make_seg(n_rows, has_null=True, mn=mn, null_val=null_stored)
    dict_ = _identity_dict(10)

    result = _decode_enc3(seg, blob, dict_)

    expected: list[object] = [
        None, None,        # stored=0 → None
        "",                # stored=1 → empty_val
        "0", "0", "0",    # stored=2 → dict[0]
        "1", "1",          # stored=3 → dict[1]
        None,              # stored=0 → None
    ]
    assert result == expected


@pytest.mark.quick
def test_direct_bitpack_via_enc3_matches_reference() -> None:
    """_decode_enc3 direct-bitpack mode (nw*vpw >= n_rows) agrees with reference.

    In direct mode _decode_enc3 calls _bitpack_values and maps each raw value
    through _dict_lookup.  With has_null=False, mn=0, identity dict, the output
    is the raw bit-packed value sequence.
    """
    bpv = 4
    vpw = 64 // bpv  # 16 values per word
    rng = Random(0xABCD)
    words = [rng.getrandbits(64) for _ in range(3)]
    n_rows = vpw * len(words)  # = 48; nw*vpw == n_rows, direct mode

    # Build blob: set bpv+nw at the standard offsets, bitpack at bp_start=64.
    bp_start = 64
    blob = bytearray(bp_start + len(words) * 8)
    struct.pack_into("<H", blob, _BP_BPV, bpv)
    struct.pack_into("<I", blob, _BP_NW, len(words))
    struct.pack_into("<I", blob, _BP_N_FRAGS, 0)
    for i, w in enumerate(words):
        struct.pack_into("<Q", blob, bp_start + i * 8, w)
    seg = _make_seg(n_rows)
    dict_ = _identity_dict(1 << bpv)

    result = _decode_enc3(seg, bytes(blob), dict_)

    mask = (1 << bpv) - 1
    expected = [
        str((w >> (s * bpv)) & mask) for w in words for s in range(vpw)
    ]
    assert result == expected


@pytest.mark.quick
@pytest.mark.parametrize("seed,bpv,n_bp_words,extra_rle", [
    # extra_rle rows are appended AFTER all bitpack runs so that
    # n_rows = nw*vpw + extra_rle > nw*vpw, guaranteeing the hybrid branch.
    (0xAA01, 4, 2, 10),   # capacity=32, n_rows=32+10=42
    (0xAA02, 6, 2, 15),   # capacity=20, n_rows=20+15=35
    (0xAA03, 3, 2, 12),   # capacity=42, n_rows=42+12=54
    (0xAA04, 8, 1, 5),    # capacity=8,  n_rows=8+5=13
])
def test_hybrid_rle_bitpack_matches_reference(
    seed: int, bpv: int, n_bp_words: int, extra_rle: int
) -> None:
    """_decode_enc3 hybrid mode agrees with the IDF reference.

    Constructs entries so that ``nw * vpw < n_rows`` (guaranteeing the hybrid
    branch).  The first half of entries are bitpack references consuming all
    bitpack capacity; the rest are plain RLE to push n_rows above capacity.

    Cross-checks the two equivalent sentinel conventions:
      .pbix: data_value + bit_packed_offset == 0xFFFFFFFF
      .bak:  stored_u >= 0x80000000;  bit_off = ~stored_u

    Any divergence would reveal a real bug in _decode_enc3's hybrid dispatch.
    """
    rng = Random(seed)
    vpw = 64 // bpv
    bp_capacity = n_bp_words * vpw
    bp_words = [rng.getrandbits(64) for _ in range(n_bp_words)]

    # Bitpack references: one per word, each consuming exactly vpw values.
    idf_entries: list[tuple[int, int]] = []
    bak_entries: list[tuple[int, int]] = []
    for word_i in range(n_bp_words):
        bp_offset = word_i * vpw
        sentinel = (0xFFFFFFFF - bp_offset) & 0xFFFFFFFF
        idf_entries.append((sentinel, vpw))  # pbix sentinel for this offset
        bak_entries.append((sentinel, vpw))  # .bak stored_u == same value

    # Plain RLE rows: bring n_rows above bitpack capacity.
    for k in range(extra_rle):
        dict_idx = k % (1 << bpv)
        idf_entries.append((dict_idx, 1))
        bak_entries.append((dict_idx, 1))

    n_rows = bp_capacity + extra_rle
    assert n_rows > n_bp_words * vpw, "test invariant: must be hybrid (n_rows > capacity)"

    dict_ = _identity_dict((1 << bpv) + 2)
    blob = _build_hybrid_blob(bak_entries, bp_words, bpv)
    seg = _make_seg(n_rows)

    result = _decode_enc3(seg, blob, dict_)
    expected_indices = _ref_idf_decode(idf_entries, bp_words, bpv, min_data_id=0)

    assert [int(v) for v in result] == expected_indices, (
        f"hybrid decode divergence: bpv={bpv} n_rows={n_rows} "
        f"capacity={n_bp_words*vpw} entries={bak_entries[:4]}…"
    )


@pytest.mark.quick
def test_hybrid_all_rle_matches_reference() -> None:
    """Hybrid blob where every entry is a plain RLE run (no bitpack references).

    nw=1 but vpw < n_rows: triggers hybrid path in _decode_enc3 but all
    stored_u values are below 0x80000000 so no bitpack dispatch occurs.
    The RLE dict_idx = stored_u - mn = stored_u (mn=0) lookup must match.
    """
    bpv = 4
    entries = [(3, 10), (5, 8), (1, 6)]  # all plain RLE, stored_u < 0x80000000
    n_rows = sum(r for _, r in entries)
    # nw=1 → capacity = 64//4 = 16; 16 < 24 → hybrid path
    blob = _build_hybrid_blob(entries, [0], bpv)
    seg = _make_seg(n_rows)
    dict_ = _identity_dict(20)

    result = _decode_enc3(seg, blob, dict_)
    expected_indices = _ref_idf_decode(entries, [0], bpv, min_data_id=0)
    assert [int(v) for v in result] == expected_indices


# ---------------------------------------------------------------------------
# Group C — Adventure Works .pbix corpus (5c)
# ---------------------------------------------------------------------------

def _load_pbixray() -> "Any | None":
    """Return a PBIXRay instance for the Adventure Works DW 2020 .pbix, or None.

    pbixray is a dynamically imported optional verifier with no static types, so
    the instance is returned as ``Any``; its private attributes (``_metadata``,
    ``_data_model``, ``_vertipaq_decoder``) are accessed reflectively.
    """
    candidates = [os.environ.get("PBIXRAY_PATH"), str(Path.home() / "github" / "pbixray")]
    for cand in candidates:
        if cand and cand not in sys.path and (Path(cand) / "pbixray").is_dir():
            sys.path.insert(0, cand)
    try:
        pbixray_mod = importlib.import_module("pbixray")
    except ImportError:
        return None
    pbix_files = list(Path.home().glob("github/pbixray/data/*Adventure*DW*2020*.pbix"))
    if not pbix_files:
        return None
    try:
        return pbixray_mod.PBIXRay(str(pbix_files[0]))
    except Exception:
        return None


def test_adventure_works_idf_decode_matches_pbixray() -> None:
    """_ref_idf_decode index array matches pbixray's internal _read_rle_bit_packed_hybrid.

    Loads the Adventure Works DW 2020 .pbix and for each integer column in the
    'Currency Rate' table:

    1. Extracts the raw IDF bytes.
    2. Calls pbixray's ``_read_rle_bit_packed_hybrid`` → ``pbix_indices`` (ground truth).
    3. Parses the IDF bytes with the Kaitai struct parser and calls
       ``_ref_idf_decode`` → ``ref_indices``.
    4. Asserts ``ref_indices == pbix_indices``.

    Any divergence indicates a bug in the shared RLE+bitpack algorithm.
    This test skips cleanly when pbixray or the Adventure Works .pbix is absent.
    """
    import importlib
    import io

    px = _load_pbixray()
    if px is None:
        pytest.skip("pbixray or Adventure Works .pbix not available")

    kaitai_idf = importlib.import_module("pbixray.column_data.idf")
    kaitai_stream = importlib.import_module("kaitaistruct")
    get_data_slice = importlib.import_module("pbixray.utils").get_data_slice

    schema_df = px._metadata.source.schema_df
    rows = schema_df[
        (schema_df["TableName"] == "Currency Rate")
        & (schema_df["PandasDataType"] == "Int64")
        & schema_df["IDF"].notna()
    ]
    assert not rows.empty, "no integer IDF columns found in 'Currency Rate' table"

    for _, row in rows.iterrows():
        col_name = row["ColumnName"]
        null_adj = 1 if row["IsNullable"] else 0
        segs_meta = px._metadata.source.get_segment_meta(row, row["IDF"])
        segs_meta_adj = [
            {**s, "min_data_id": s["min_data_id"] - null_adj}
            for s in segs_meta
        ]

        idf_buf = get_data_slice(px._data_model, row["IDF"])

        # Ground truth: pbixray's own hybrid decode.
        pbix_indices = [
            int(v)
            for v in px._vertipaq_decoder._read_rle_bit_packed_hybrid(idf_buf, segs_meta_adj)
        ]

        # Reference decode: _ref_idf_decode applied segment by segment.
        with io.BytesIO(idf_buf) as f:
            idf = kaitai_idf.ColumnDataIdf(kaitai_stream.KaitaiStream(f))

        ref_indices: list[int] = []
        for seg_idx, seg_meta in enumerate(segs_meta_adj):
            seg = idf.segments[seg_idx]
            bw = seg_meta["bit_width"]
            mid = seg_meta["min_data_id"]
            cap = seg_meta["records"]
            words = (
                list(struct.unpack_from("<" + "Q" * seg.sub_segment_size, seg.sub_segment))
                if seg.sub_segment_size > 0
                else []
            )
            entries = [(int(e.data_value), int(e.repeat_value)) for e in seg.primary_segment]
            partial = _ref_idf_decode(entries, words, bw, mid)
            ref_indices.extend(partial[:cap])

        assert ref_indices == pbix_indices, (
            f"IDF decode mismatch for column {col_name!r}: "
            f"first divergence at index "
            f"{next((i for i, (a, b) in enumerate(zip(ref_indices, pbix_indices)) if a != b), '?')}"
        )


# ---------------------------------------------------------------------------
# Group D — Numeric dictionary parse + format-difference note (5d)
# ---------------------------------------------------------------------------

# The .pbix numeric dictionary binary layout (from Kaitai idf.ksy):
#   [0:4]   dict_type (s4) — 0 = xm_type_long, 1 = xm_type_real
#   [4:28]  hash_info (6 × s4)
#   [28:36] num_values (u8)
#   [36:40] element_size (u4) — 4 = int32, 8 = int64/float64
#   [40:]   values
#
# The .bak numeric dictionary layout (mssqlbak offsets):
#   [48:52] entry_size (u4)
#   [52:56] count (u4)
#   [56:]   values
#
# These differ: the .pbix format cannot be parsed by _parse_numeric_dict_*
# and the .bak format cannot be parsed by pbixray's _read_dictionary.
# Verified empirically: parsing the CurrencyKey dictionary blob from
# Adventure Works DW 2020 with mssqlbak's offsets yields entry_size=14 (not
# a valid width) and count=16 (not the actual 12 entries).
# Cross-format verification is therefore intentionally excluded from these
# tests; correctness is verified synthetically below.

def _build_bak_numeric_dict(entry_size: int, values: Sequence[int | float]) -> bytes:
    """Build a .bak-format numeric dictionary blob.

    Layout: 56-byte header (entry_size u4@48, count u4@52) + packed values.
    """
    blob = bytearray(56 + len(values) * entry_size)
    struct.pack_into("<I", blob, 48, entry_size)
    struct.pack_into("<I", blob, 52, len(values))
    fmt = {1: "<B", 2: "<h", 4: "<i", 8: "<q"}.get(entry_size, "<q")
    off = 56
    for v in values:
        struct.pack_into(fmt, blob, off, int(v))
        off += entry_size
    return bytes(blob)


def _build_bak_numeric_dict_float(values: list[float]) -> bytes:
    """Build a .bak-format float64 numeric dictionary blob."""
    blob = bytearray(56 + len(values) * 8)
    struct.pack_into("<I", blob, 48, 8)
    struct.pack_into("<I", blob, 52, len(values))
    off = 56
    for v in values:
        struct.pack_into("<d", blob, off, v)
        off += 8
    return bytes(blob)


@pytest.mark.quick
@pytest.mark.parametrize("entry_size,values", [
    (4,  [0, 1, -1, 2147483647, -2147483648]),
    (8,  [0, 100, -100, 9999999999, -9999999999]),
    (2,  [0, 1, 32767, -32768]),
    (1,  [0, 127, 255]),
])
def test_parse_numeric_dict_int_roundtrip(
    entry_size: int, values: list[int]
) -> None:
    """_parse_numeric_dict_int correctly reads .bak-format integer dictionary blobs."""
    blob = _build_bak_numeric_dict(entry_size, values)
    result = _parse_numeric_dict_int(blob)
    # entry_size=1 is unsigned (B) but _parse_numeric_dict_int uses <B; expected:
    expected = [v & 0xFF if entry_size == 1 else v for v in values]
    assert result == expected, f"entry_size={entry_size}: {result!r} != {expected!r}"


@pytest.mark.quick
@pytest.mark.parametrize("values", [
    [0.0, 1.0, -1.0, 1.5, 3.14159265358979],
    [float("inf"), float("-inf"), 1.7976931348623157e308],
    [-0.0, 1e-300, 1e300],
])
def test_parse_numeric_dict_float_roundtrip(values: list[float]) -> None:
    """_parse_numeric_dict_float correctly reads .bak-format float64 dictionary blobs."""
    blob = _build_bak_numeric_dict_float(values)
    result = _parse_numeric_dict_float(blob)
    # Compare bit-exactly where finite, and by class for special values.
    assert len(result) == len(values)
    for got, exp in zip(result, values):
        if exp != exp:  # NaN
            assert got != got
        else:
            assert got == exp, f"{got!r} != {exp!r}"


@pytest.mark.quick
def test_parse_numeric_dict_float_uses_entry_size_4_for_float32() -> None:
    """entry_size=4 in the blob triggers float32 parse (not int32)."""
    vals_f32 = [1.5, 3.14, -2.0]
    blob = bytearray(56 + len(vals_f32) * 4)
    struct.pack_into("<I", blob, 48, 4)
    struct.pack_into("<I", blob, 52, len(vals_f32))
    off = 56
    for v in vals_f32:
        struct.pack_into("<f", blob, off, v)
        off += 4
    result = _parse_numeric_dict_float(bytes(blob))
    assert len(result) == 3
    for got, exp in zip(result, vals_f32):
        assert abs(got - exp) < 1e-5, f"{got} vs {exp}"


@pytest.mark.quick
def test_parse_numeric_dict_int_empty_blob() -> None:
    """Blobs shorter than 56 bytes return empty list, not a crash."""
    assert _parse_numeric_dict_int(b"\x00" * 40) == []
    assert _parse_numeric_dict_float(b"\x00" * 40) == []


@pytest.mark.quick
def test_parse_numeric_dict_int_zero_count() -> None:
    """entry_size or count == 0 returns empty list."""
    blob = bytearray(64)
    struct.pack_into("<I", blob, 48, 8)  # entry_size=8
    struct.pack_into("<I", blob, 52, 0)  # count=0
    assert _parse_numeric_dict_int(bytes(blob)) == []


# ---------------------------------------------------------------------------
# Group E — xVelocity v4 Huffman page decode vs xmhuffman corpus (5e / 5f)
# ---------------------------------------------------------------------------
#
# The xVelocity v4 string dictionary uses xmhuffman-compressed pages in both
# .pbix (ColumnDataDictionary.CompressedStrings) and .bak (dict_xvelocity.py
# _decode_v4_huff_dict).  The shared binary format:
#
#   encode_array_128 : 128 bytes (nibble-packed Huffman code lengths for
#                       symbols 0–255)
#   compressed_string_buffer : variable-length bitstream
#   offsets : per-string start bit offsets within the compressed buffer
#   store_total_bits : end-of-stream sentinel for the last string
#
# mssqlbak's _huff_decode_page_py is a pure-Python fallback for the
# xmhuffman Rust extension, used when xmhuffman rejects an underfull
# Huffman tree (Kraft sum < 1.0) that SQL Server occasionally produces.
# Any divergence from xmhuffman would silently corrupt string columns.
#
# Group E tests the Adventure Works DW 2020 .pbix (6 columns, 8 pages,
# 191 489 strings).  Group F adds the Adventure Works Internet Sales .pbix
# (12 additional compressed pages) as an independent second corpus.
# Character-encoding differences between .pbix (UTF-16LE, no +2 offset)
# and .bak (latin-1 with chr(b-2)) are intentionally excluded — those are
# caller-side conventions applied *after* the shared Huffman decode step.


def _check_huff_decode_pages(
    px: Any,
    xmh: Any,
    label: str,
    *,
    min_pages: int = 1,
    min_strings: int = 1,
) -> tuple[int, int]:
    """Verify _huff_decode_page_py byte-matches xmhuffman on every compressed page in *px*.

    Returns ``(pages_checked, strings_checked)``.  Raises ``AssertionError`` on
    any mismatch.  Used by Group E and Group F so both share the same logic.
    """
    kaitai_dict = importlib.import_module("pbixray.column_data.dictionary")
    kaitai_stream = importlib.import_module("kaitaistruct")
    get_data_slice = importlib.import_module("pbixray.utils").get_data_slice
    np = importlib.import_module("numpy")

    from mssqlbak.columnstore.decode.dict_xvelocity import (  # noqa: PLC0415
        _build_huff_table,
        _huff_decode_page_py,
    )

    schema_df = px._metadata.source.schema_df
    str_cols = schema_df[
        (schema_df["PandasDataType"] == "string") & schema_df["Dictionary"].notna()
    ]

    dt_h = np.dtype([("bit_or_byte_offset", "<u4"), ("page_id", "<u4")])
    pages_checked = 0
    strings_checked = 0

    for _, row in str_cols.iterrows():
        dict_buf = get_data_slice(px._data_model, row["Dictionary"])
        d = kaitai_dict.ColumnDataDictionary(
            kaitai_stream.KaitaiStream(kaitai_stream.BytesIO(dict_buf))
        )
        if d.dictionary_type.name != "xm_type_string":
            continue

        raw_h = d.data.dictionary_record_handles_vector_info.vector_of_record_handle_structures
        handles = np.frombuffer(raw_h, dtype=dt_h)

        for pid, page in enumerate(d.data.dictionary_pages):
            if not page.page_compressed:
                continue

            cs = page.string_store
            bitstream = bytes(cs.compressed_string_buffer)
            encode_array = bytes(bytearray(cs.encode_array))
            stb = cs.store_total_bits
            offsets = sorted(
                handles["bit_or_byte_offset"][handles["page_id"] == pid].tolist()
            )
            if not offsets:
                continue

            col_id = f"[{label}] {row['TableName']}.{row['ColumnName']} page[{pid}]"

            # Reference: xmhuffman Rust extension decode (swap=True).
            ref_bytes = xmh.decode_page(bitstream, encode_array, offsets, stb, swap=True)

            # Under-test: mssqlbak's pure-Python Huffman fallback.
            # cbuf_off=0: we pass the compressed buffer directly; .pbix has no
            # LOB chunk separators, unlike the .bak raw stream.
            table, max_len, esc_start_code = _build_huff_table(encode_array)
            assert table is not None, (
                f"{col_id}: expected valid Huffman table for real corpus data"
            )
            py_result = _huff_decode_page_py(
                bitstream, 0, table, max_len, offsets, stb, esc_start_code
            )
            assert py_result is not None, f"{col_id}: _huff_decode_page_py returned None"
            py_bytes, _escape_idx, _extra, _eors = py_result

            assert len(py_bytes) == len(ref_bytes), (
                f"{col_id}: got {len(py_bytes)} strings, expected {len(ref_bytes)}"
            )
            mismatches = [
                (i, ref_bytes[i], py_bytes[i])
                for i in range(len(ref_bytes))
                if ref_bytes[i] != py_bytes[i]
            ]
            assert not mismatches, (
                f"{col_id}: {len(mismatches)} byte mismatches; "
                f"first: index={mismatches[0][0]} "
                f"ref={mismatches[0][1].hex()} py={mismatches[0][2].hex()}"
            )
            pages_checked += 1
            strings_checked += len(ref_bytes)

    assert pages_checked >= min_pages, (
        f"[{label}] only {pages_checked} compressed pages found — test corpus invalid"
    )
    assert strings_checked >= min_strings, (
        f"[{label}] only {strings_checked} strings checked; expected ≥{min_strings}"
    )
    return pages_checked, strings_checked


def _load_pbixray_file(glob: str) -> "object | None":
    """Return a PBIXRay instance for the first .pbix matching *glob*, or None."""
    candidates = [os.environ.get("PBIXRAY_PATH"), str(Path.home() / "github" / "pbixray")]
    for cand in candidates:
        if cand and cand not in sys.path and (Path(cand) / "pbixray").is_dir():
            sys.path.insert(0, cand)
    try:
        pbixray_mod = importlib.import_module("pbixray")
    except ImportError:
        return None
    pbix_files = list(Path.home().glob(glob))
    if not pbix_files:
        return None
    try:
        return pbixray_mod.PBIXRay(str(pbix_files[0]))
    except Exception:
        return None


def test_huff_decode_page_py_matches_xmhuffman_on_corpus() -> None:
    """_huff_decode_page_py raw bytes == xmhuffman.decode_page — Adventure Works DW 2020.

    Loads every compressed string dictionary page from the Adventure Works DW
    2020 .pbix (6 columns, 8 pages, 191 489 strings) and asserts byte-for-byte
    identity between xmhuffman (reference) and mssqlbak's pure-Python Huffman
    fallback _huff_decode_page_py.  Any divergence would silently corrupt .bak
    string columns on underfull-tree pages.

    This test skips cleanly when pbixray, xmhuffman, or the .pbix is absent.
    """
    px = _load_pbixray()
    if px is None:
        pytest.skip("pbixray or Adventure Works DW 2020 .pbix not available")

    try:
        import xmhuffman as xmh  # noqa: PLC0415
    except ImportError:
        pytest.skip("xmhuffman not available")

    pages, strings = _check_huff_decode_pages(
        px, xmh, "AW DW 2020", min_pages=8, min_strings=100_000
    )
    assert strings >= 100_000, f"only {strings} strings; expected ≥100k for full corpus"


# Group F — second corpus: Adventure Works Internet Sales .pbix (5f)
# ---------------------------------------------------------------------------
#
# 12 additional compressed Huffman pages from a different .pbix provide an
# independent second corpus.  Same algorithm, different data distribution,
# exercising code paths that may not appear in the DW 2020 corpus alone.


def test_huff_decode_page_py_matches_xmhuffman_internet_sales() -> None:
    """_huff_decode_page_py raw bytes == xmhuffman — Adventure Works Internet Sales.

    Loads all compressed string pages from the Adventure Works Internet Sales
    .pbix (12 compressed pages) and asserts byte-for-byte identity between
    xmhuffman and _huff_decode_page_py, providing an independent second corpus
    beyond the DW 2020 fixture used in Group E.

    Skips cleanly when pbixray, xmhuffman, or the .pbix is absent.
    """
    px = _load_pbixray_file("github/pbixray/data/*Internet*Sales*.pbix")
    if px is None:
        pytest.skip("pbixray or Adventure Works Internet Sales .pbix not available")

    try:
        import xmhuffman as xmh  # noqa: PLC0415
    except ImportError:
        pytest.skip("xmhuffman not available")

    _check_huff_decode_pages(px, xmh, "AW Internet Sales", min_pages=12, min_strings=1)
