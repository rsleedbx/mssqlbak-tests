# tpcxbb `pr_review_content` — Huffman underfull-tree decoding investigation
_Written 2026-07-02, updated 2026-07-02_

## Current state

| Metric | Before this session | After fb9e0b1 | After escape-advance fix |
|---|---|---|---|
| correct | 83,049 | 83,105 | **83,114** |
| got_only | 76 | 19 | **10** |
| want_only | 90 | 34 | **25** |

The 62,506 empty-row symptom from the original plan was resolved in a prior session. The remaining 10 `got_only` / 25 `want_only` are all Bucket B (non-escape, n_unused=2 pages).

---

## What was tried and why

### Finding 1: all cl=15 substitutions have shift +2

Running `tools/diag/pr_review_full_subs.py` across all got_only strings showed that every incorrect cl=max_len symbol on the two affected encode_arrays (`bde8b0ed`, `b48c5b50`) was exactly 2 positions too high in the canonical code group.

| got_sym | gt_sym | our_pos(got) | our_pos(gt) | shift |
|---|---|---|---|---|
| `=` (63) | `%` (39) | 8 | 6 | +2 |
| `>` (64) | `+` (45) | 9 | 7 | +2 |
| `@` (66) | `=` (63) | 10 | 8 | +2 |
| `\` (94) | `=` (63) | 18 | 16 | +2 |
| `^` (96) | `>` (64) | 19 | 17 | +2 |
| `{` (125) | `_` (97) | 22 | 20 | +2 |
| `|` (126) | `` ` `` (98) | 23 | 21 | +2 |

All cl=15 substitutions had shift = **exactly +2** with no exceptions.

### Root cause identified

`bde8b0ed` has 128 available cl=15 slots and 125 data symbols → 3 unused slots.
`b48c5b50` has 150 available cl=15 slots and 147 data symbols → 3 unused slots.

For pages with ≥3 unused cl=15 slots, SQL Server places **2 escape-prefix codes at positions 0 and 1** of the max-length code group, pushing all data symbols up by 2. The remaining unused slot sits at the end as the conventional end-of-record padding code.

For pages with exactly 2 unused slots, SQL Server uses the end-of-range convention (all-ones / near-all-ones codes), which the existing decoder already handles correctly.

### Fix attempt 1: `n_available - n_max_syms >= 2`

Reserving 2 leading positions for all underfull pages with ≥2 unused slots.

**Result: massively worse** — `correct` dropped from 83,049 to 76,249. Many pages have exactly 2 unused slots and use the end-of-range convention; applying the +2 shift to them broke previously correct strings.

### Fix attempt 2: `n_available - n_max_syms >= 3` (committed)

Reserving 2 leading positions only for pages with 3 or more unused cl=max_len slots.

**Result:** correct=83,105 (+56), got_only=19 (−57), want_only=34 (−56).

This fix is in `_build_huff_table` in `mssqlbak/columnstore/decode/dict_xvelocity.py`.

---

## Remaining 19 got_only / 34 want_only

From `tools/diag/pr_review_escape_pages.py`:

| EA | unused | got_only count | notes |
|---|---|---|---|
| `b48c5b50` | 3 | 5 | All `esc=1` (escape handles) |
| `bde8b0ed` | 3 | 4 | All `esc=1` (escape handles) |
| `145e4997` | 2 | 1 | `esc=0` |
| `1b57548d` | 2 | 1 | `esc=0` |
| `33cddc3d` | 2 | 1 | `esc=0` |
| `35448b34` | 2 | 1 | `esc=0` |
| `4a4ea36f` | 1 | 1 | `esc=0` |
| `a31205ea` | 2 | 1 | `esc=0` |
| `c05d16e1` | 2 | 1 | `esc=0` |
| `cbe5cb20` | 2 | 1 | `esc=0` |
| `f3056577` | 2 | 1 | `esc=0` |
| (no EA) | — | 1 | xmhuffman page |

### Bucket A: escape handles on bde8b0ed / b48c5b50 (9 errors) — RESOLVED ✓

The root cause was an off-by-one in the bit advance past the escape-prefix code.

**Discovery:** A brute-force scan over `advance ∈ {13, 14, 15, 16}` for each of the 9 failing handles uniformly showed that `advance = max_len − 1 = 14` gave the correct `r[1:]` content (✓ for all 6 tested cases). `advance = 15` (the previous value) was wrong for all.

**Root cause:** The two reserved start-escape codes at positions 0 and 1 of the max_len group have codes `B15` and `B15+1`, where `B15 = 32768 − n_available` is always even (canonical Huffman property). These two codes therefore share a common `(max_len−1)`-bit parent node. SQL Server writes that **14-bit parent code** into the bitstream — not the full 15-bit leaf codes. Our max_len=15 wide table lookup reads one extra bit, so advancing 15 bits over-consumed by 1 bit, shifting all subsequent symbol decodes by 1 bit.

**Complication:** Advancing `max_len−1` for ALL escape detections caused regression for handles that start with **end-of-range padding codes** (e.g. all-ones 0x7FFF). These codes are genuine 15-bit codes (no parent sharing) and need `advance = max_len`. Specifically: for `n_unused = 3`, one end-padding code remains at the high end (idx=32767), used for different escape handles. Brute-force confirmed that those handles need `advance = 15`.

**Fix implemented:** `_build_huff_table` now returns `esc_start_code` (the base code `B15` before the +2 shift, or −1 for non-+2-shift pages). `_huff_decode_page_py` uses `max_len − 1` advance only when `idx ∈ {esc_start_code, esc_start_code+1}`, and `max_len` advance otherwise.

**Result:** All 9 Bucket A errors fixed. No regression on the 671 passing tests or on handles that use end-padding codes.

### Bucket B: non-escape errors on n_unused=2 pages (10 errors) — OPEN

These handles have `esc=0` (not escape-prefixed) and are on pages with n_unused=2 (end-of-range escape convention, no +2 shift). The strings are wrong in isolated positions or have embedded non-printable bytes.

Current 10 remaining `got_only` errors:
| EA | esc_adv | Notes |
|---|---|---|
| `33cddc3d` | 15 | "Awesome Preview of Europe..." |
| `35448b34` | 15 | "For 25 min made-for-tv cartoon..." |
| `145e4997` | 15 | "Great first cd from very brisk clip..." |
| `a31205ea` | 15 | "It seems somebody was complaining..." |
| `cbe5cb20` | 15 | "Practically ignored by music criticism..." |
| `1b57548d` | 15 | "Say what you will care about Leon Payne.\\x97\\x06..." |
| `f3056577` | 15 | "The quality and selection of this nonsense..." |
| `c05d16e1` | 15 | "Theodor Seuss Giesel was best known as..." |
| `4a4ea36f` | 15 | "one of Ruth's receipes..." |
| (no-info) | — | "\\x80FUNNY PEOPLESTARRING: Adam Sandler..." |

The `\\x97\\x06` and `\\x80` prefix suggest these may involve the ISO-8859-1 widening issue flagged in the duckdb-pbix-extension analysis: decoded symbols ≥ 0x80 may need to be widened to 2-byte UTF-8 sequences rather than stored as raw single bytes.

**Next diagnostic:** use `pr_review_diverge.py` to categorize each error and check whether any of the 25 `want_only` strings contain non-ASCII (Latin-1) characters. If so, implement ISO-8859-1 → UTF-8 widening in `_decode_payload`.

---

## Confirmed facts (this session)

| Fact | Source |
|---|---|
| All cl=15 substitutions on underfull pages have shift +2. | `pr_review_full_subs.py` |
| SQL Server places 2 escape codes at cl=max_len positions 0, 1 when n_unused ≥ 3. | Inferred from universal +2 shift on bde8b0ed/b48c5b50 (both n_unused=3). |
| Pages with n_unused=2 use end-of-range escape convention (no shift needed). | Confirmed: applying ≥2 condition broke them; ≥3 condition leaves them untouched. |
| The fix `n_available - n_max_syms >= 3: code += 2` resolves 57 of 76 got_only errors. | `pr_review_setdiff.py` before/after comparison. |
| The two start-escape codes (B15, B15+1) are a 14-bit parent pair — SQL Server writes the 14-bit code, not the 15-bit leaf. | Brute-force advance test on all 9 Bucket A handles: advance=14 ✓, advance=15 ✗. |
| End-of-range padding codes (e.g. all-ones 0x7FFF) on the same +2-shift pages remain genuine 15-bit codes and need advance=15. | Confirmed by esc_idx=32767 on the 5 regression handles. |
| `_build_huff_table` now returns `esc_start_code` (B15 for +2-shift pages, −1 otherwise). | Code change; 671 tests pass. |
| `_huff_decode_page_py` now distinguishes start-escape (advance=max_len−1) from end-padding (advance=max_len) by comparing idx against {esc_start_code, esc_start_code+1}. | Code change; all 9 Bucket A errors resolved. |

---

## External reference investigation (2026-07-02)

Three external codebases were examined to find documented escape-code or underfull-tree handling in xVelocity Huffman. **None contain the escape mechanism we need.**

### pbixray (Python)

Delegates entirely to the closed-source `xmhuffman` C extension (`xmhuffman.decode_page`). No escape or underfull logic is visible in the Python layer.

### xmhuffman-cython (C/Cython kernel for pbixray)

Strict textbook canonical Huffman. **Rejects underfull trees with `return -3`** (Kraft sum check). No escape-code handling, no reserved slots at max_len. Underfull trees are a non-case for this implementation.

### duckdb-pbix-extension (C++ / Kaitai Struct)

Naive canonical Huffman — also no escape handling. **Two implementation details are actionable for us:**

1. **ISO-8859-1 → UTF-8 widening.** Every decoded byte is passed through:
   ```cpp
   if (code >= 0x80) {
       utf8.push_back(0xC2 + (code > 0xBF));
       utf8.push_back((code & 0x3F) + 0x80);
   }
   ```
   This means xVelocity Huffman symbols are ISO-8859-1 (Latin-1) code points, not plain ASCII. Our `_V4_CHAR_OFFSET = 2` handles the ASCII-range correctly, but any symbol ≥ 0x80 would need to be widened to a 2-byte UTF-8 sequence instead. Worth checking whether any of the 34 `want_only` strings contain non-ASCII characters.

2. **16-bit word byte-swap in the decode loop.**
   ```cpp
   byte_pos = (byte_pos & ~0x01) + (1 - (byte_pos & 0x01));
   ```
   The compressed buffer is consumed as a stream of 16-bit little-endian words, swapping even/odd bytes within each pair before reading bits MSB-first. Our Python decoder should be verified to do the same.

3. **`ui_decode_bits` is in the format but unused.** The duckdb decoder reads this u4 field but never uses it in decoding. Not relevant to escape handling.

4. **Escape codes are SQL Server-proprietary.** No known open-source implementation handles the underfull-tree escape-reservation convention. The empirical approach (ground-truth byte inspection) remains the only viable path.

### MS-XLDM (Microsoft Open Specification)

The official spec for the VertiPaq/xVelocity Spreadsheet Data Model File Format ([MS-XLDM] v8.3, 2025-08-19, §2.7.4 and §2.3.2.1.2.4.2). Key confirmed facts:

**2.7.4.1.1 "Classical Unbalanced Huffman Tree"** — Microsoft's own term for what we call an underfull tree. Explicitly allowed. Quote: *"this method does not require that the tree be balanced"*. No restriction on Kraft sum.

**No escape code documentation** — Sections 2.7.4 through 2.7.4.2 contain zero mention of escape codes, reserved max-len slots, or unused-slot handling. The escape mechanism we empirically discovered is SQL Server-specific and undocumented in the public spec.

**Codeword length constraints** — minimum 2 bits, maximum 15 bits. `uiDecodeBits` MUST NOT exceed 12. Pages with cl=15 codewords therefore always require tree traversal (not the fast lookup table), which is why they fall back to our Python decoder.

**Character set mode** — The PBIX/MS-XLDM format has two charset modes:
- `XM_HUFFMAN_SINGLECHARSET = 0x000aba91`: upper byte stripped from stream, stored in a `CharacterSetUsed` (1 byte) field; must be added back to each decoded symbol.
- `XM_HUFFMAN_MULTICHARSET = 0x000aba92`: all bytes encoded in stream; no byte to add back.

**SQL Server .bak V4 diverges from this spec**: our `_V4_EA_OFF_IN_HDR = 12` shows the V4 page header layout is:
```
StoreTotalBits      (4 bytes, offset 0)
CharacterSetTypeId  (4 bytes, offset 4)  — not explicitly read
uiDecodeBits        (4 bytes, offset 8)  — not explicitly read
encodeArray         (128 bytes, offset 12)
```
The `AllocationSize` (8 bytes) and `CharacterSetUsed` (1 byte) fields from the PBIX format are **absent** from the SQL Server V4 layout. Instead, the fixed `_V4_CHAR_OFFSET = 2` is applied uniformly to all decoded symbols — this is SQL Server-specific and has no equivalent in the MS-XLDM spec.

### Open-XML-SDK

Not relevant — purely the OOXML markup SDK (Word/Excel/PowerPoint XML). No VertiPaq, ABF, or Huffman content.

---

## Scope

- All remaining errors are still within `tpcxbb_1gb.bak pr_review_content`.
- The fix must not regress any pages decoded by `xmhuffman` (those never enter the Python fallback path).
- The synthetic fixture suites (2017/2019/2022/2025) currently pass and must continue to pass.
