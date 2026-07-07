# XPRESS Implementation History

> **This document is a historical record, not a description of the current implementation.**
> It captures the library evaluation and fork-fix process that led to the in-house
> `xpress_lz77` Rust crate.  For the current state see `docs/PERFORMANCE_PLAN.md`
> (P1 section) and `rust/src/xpress_lz77_huffman.rs`.

---

## Problem

`mssqlbak/xpress.py` is a pure-Python LZ77+Huffman loop implementing MS-XCA §2.2.
Every byte of every compressed backup passes through it, making it the primary CPU
bottleneck for compressed backups.

## Libraries evaluated

Three external options were tested before forking `xpress_lz77`:

| Library | Result | Reason |
|---|---|---|
| `xpress_lz77` (upstream, forensicxlab) | Rust panic at every invocation | Off-by-one in `xpress_lz77_huffman.rs:250`; missing output bounds check |
| `dissect.util.lzxpress_huffman` | 0.8× vs current Python | Pure Python; no speed gain |
| `wimlib` ctypes | 98% error rate | Format mismatch — expects wimlib's own container framing |

Python version does not affect any of these outcomes.  The `xpress_lz77` panic is in
compiled Rust, not the Python runtime.  The `dissect` slowness is interpreter-bound
regardless of Python version.  The wimlib format mismatch is a data framing issue.

## Fork: `rsleedbx/xpress_lz77`

The upstream `forensicxlab/xpress_lz77` crate was forked as `rsleedbx/xpress_lz77`.
Three bugs were fixed to make it compatible with SQL Server's XPRESS streams:

| Fix | Location | What |
|---|---|---|
| 1 | `xpress_lz77_huffman.rs:~250` | LZ77 non-overlapping copy writes past output end |
| 2 | `xpress_lz77_huffman.rs:~234` | LZ77 overlapping copy writes past output end |
| 3 | bit-refill function | Bitstream EOF must yield zero bits (MS-XCA §2.2), not raise |

**Fix 3 detail:** SQL Server XPRESS streams intentionally exhaust the compressed
bitstream before all output bytes are produced.  The pure-Python `_BitStream.ensure`
handles this by treating overread as zero bits:

```python
if self.end - self.next < 2:
    self.bitsleft = 32  # overread → zero bits (MS-XCA §2.2)
    return
```

The Rust `ensure_bits` / bit-refill function required the same rule:

```rust
// When in_buf is exhausted, yield zero bits indefinitely (MS-XCA §2.2)
if self.in_pos + 2 > self.in_buf.len() {
    self.bits_avail = 32;
    return;
}
```

After fixes 1 and 2 but before fix 3, the library raised `ValueError: EOF Error` on
every SQL Server chunk (0/114 succeed even with the exact pre-computed output size).

## Outcome

After the three fixes, `lz77_huffman_decompress_py` and
`lz77_huffman_decompress_until_input_py` handle all SQL Server XPRESS chunks correctly.
The fork was subsequently absorbed into the mssqlbak-local `rust/` crate so the
implementation lives alongside the page decoder and is not a separate wheel dependency.

## Python-side wiring

`mssqlbak/xpress.py` imports the extension at module load via `getattr` (no named
import, so pyright does not flag a missing-attribute error against the untyped extension):

```python
try:
    import xpress_lz77 as _xpress_lz77
    _native_decompress: Callable[[bytes, int], bytes] | None = getattr(
        _xpress_lz77, "lz77_huffman_decompress_py", None
    )
    _native_decompress_until_input: Callable[[bytes, int], bytes] | None = getattr(
        _xpress_lz77, "lz77_huffman_decompress_until_input_py", None
    )
except BaseException:
    _native_decompress = None
    _native_decompress_until_input = None
```

`decompress()` tries the native path first; `decompress_chunk()` (used by
`compressed.py:_decode_chunk`) does a single-pass decode at max-extent size instead of
the old two-pass approach, saving one full decode per chunk.

`pyo3_runtime.PanicException` inherits from `BaseException` (not `Exception`), so
`except BaseException` catches both panics and `ValueError` from the native extension,
enabling transparent fallback to the pure-Python path.
