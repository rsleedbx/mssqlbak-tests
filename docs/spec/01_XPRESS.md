## 8. XPRESS Compression (MS-XCA LZ77+Huffman)

Reference: [MS-XCA] — *Xpress Compression Algorithm* (LZ77+Huffman variant).

The XPRESS codec is used in two contexts:
1. **MSSQLBAK container** (`compressed.py`): every backup chunk (extent) is
   compressed with one XPRESS sub-chunk.
2. **Columnstore ARCHIVE blobs** (`columnstore/storage/lob.py`): segment/dict
   blobs may be XPRESS-compressed inside a 12-byte frame.

The production decoder is the `xpress_lz77` **Rust/PyO3 extension** (`rust/`).
The pure-Python reference implementations in `xpress.py`
(`_decompress_python`, `_decompress_until_input_python`) are byte-identical
specification of MS-XCA §2.2 and are used only in tests.

---

### 8.1 Input layout — the compressed chunk `[CONFIRMED against MS-XCA]`

A compressed chunk begins at a byte position `start` and has two parts:

```
[start +   0 : start + 256]  Huffman length table  (256 bytes)
[start + 256 : comp_end   ]  bitstream  (LZ77+Huffman tokens)
```

**Huffman length table**: 512 four-bit codeword lengths packed as nibbles —
symbol `2*i` is the **low nibble** of byte `i`; symbol `2*i+1` is the **high
nibble**.  Source: `xpress.py: _read_lengths`.

```python
for i in range(256):
    lens[2*i]   = data[start + i] & 0xF   # even symbol = low nibble
    lens[2*i+1] = data[start + i] >> 4    # odd  symbol = high nibble
```

**Symbols** 0–255 are literal bytes; 256–511 encode LZ77 back-references.

**Maximum output per sub-chunk**: `_SUB_CHUNK_OUT = 65536` bytes.
Outputs larger than 65 536 span multiple sub-chunks (§8.4).

---

### 8.2 Canonical-Huffman decode table `[CONFIRMED against MS-XCA]`

Build a flat `2^15 = 32768`-entry table from the 512 codeword lengths.
Each entry packs `(symbol << 4) | codeword_length`; unused entries are `0`.
A codeword of length `n` is stored left-justified, filling `2^(15-n)`
contiguous entries.  Source: `xpress.py: _build_decode_table`.

```python
TABLE_BITS = 15
table = [0] * (1 << TABLE_BITS)
by_len = [[] for _ in range(16)]
for sym, n in enumerate(lens):
    if n:
        by_len[n].append(sym)
code = 0
for n in range(1, 16):
    span = 1 << (TABLE_BITS - n)
    for sym in by_len[n]:
        start_idx = code << (TABLE_BITS - n)
        table[start_idx : start_idx + span] = [(sym << 4) | n] * span
        code += 1
    code <<= 1
```

A single `peek(15)` into the bit buffer gives the table index; the entry's
low nibble is the codeword length to consume.

---

### 8.3 Bitstream mechanics `[CONFIRMED against MS-XCA]`

The bitstream uses **16-bit little-endian coding units** consumed **MSB
first** via a left-justified 32-bit accumulator.  Over-reading past the end
yields zero bits.  Source: `xpress.py: _BitStream`.

| Operation | Description |
|-----------|-------------|
| `ensure(n)` | Refill the accumulator if fewer than `n` bits are available; reads one `uint16 LE`, shifts it into the MSB region of `bitbuf`, adds 16 to `bitsleft`. Over-read sets `bitsleft = 32`. |
| `peek(n)` | Read top `n` bits without advancing: `(bitbuf >> 1) >> (31 - n)` |
| `remove(n)` | Advance: `bitbuf = (bitbuf << n) & 0xFFFFFFFF; bitsleft -= n` |
| `pop(n)` | `peek(n)` then `remove(n)` — returns the `n`-bit value |
| `read_byte()` | Read one byte directly from the byte stream (not the bit buffer) |
| `read_u16()` | Read two bytes LE directly from the byte stream |

---

### 8.4 Token decode loop `[CONFIRMED against MS-XCA]`

Source: `xpress.py: _decompress_python` (lines 339–384).

```
pos = start                          # points at the current sub-chunk's 256-byte table
out = bytearray()
while len(out) < out_size:
    build decode table from lens at pos
    bs = bitstream starting at pos + 256
    sub_end = min(len(out) + 65536, out_size)
    while len(out) < sub_end:
        bs.ensure(15)
        entry = table[bs.peek(15)]
        sym = entry >> 4
        bs.remove(entry & 0xF)        # consume the codeword bits
        if sym < 256:                 # literal byte
            out.append(sym)
            continue
        # LZ77 back-reference
        match_len = sym & 0xF         # low nibble of symbol
        log2_off  = (sym >> 4) & 0xF  # next 4 bits of symbol
        bs.ensure(16)
        offset = (1 << log2_off) | bs.pop(log2_off)   # read extra offset bits
        if match_len == 0xF:          # length overrun: read extra byte(s)
            match_len += bs.read_byte()
            if match_len == 0xF + 0xFF:
                match_len = bs.read_u16()   # full 16-bit length
        match_len += MIN_MATCH        # minimum match length is 3
        src = len(out) - offset       # back-reference into already-emitted output
        if src < 0:
            raise ValueError("offset precedes output start")
        # Overlapping copy: must iterate byte-by-byte when offset < match_len
        for _ in range(min(match_len, sub_end - len(out))):
            out.append(out[src]);  src += 1
    pos = bs.next                     # advance to next sub-chunk's table
                                      # (leftover bits in bitbuf are discarded)
return bytes(out)
```

Key constants:
- `MIN_MATCH = 3`
- `NUM_SYMBOLS = 512`, `NUM_CHARS = 256`
- `_SUB_CHUNK_OUT = 65536`

---

### 8.5 Multi-sub-chunk streams `[CONFIRMED against MS-XCA]`

When the decompressed size exceeds 65 536 bytes, the stream is split into
multiple **sub-chunks**.  After each 65 536 bytes of output:

1. The bitstream pointer (`bs.next`) advances to the next sub-chunk.
2. Any leftover bits in the 32-bit accumulator are **discarded**.
3. The next 256 bytes at `bs.next` form the new Huffman length table.
4. A new decode table is built and the loop continues.

The Rust extension and the pure-Python reference handle this identically.

---

### 8.6 Input-bounded variant (unknown output size)

When the compressed extent is known but the exact output size is not,
`decompress_until_input` / `_decompress_until_input_python` decodes until
`pos >= comp_end`.  The caller rounds the resulting length up to the next
8 192-byte page boundary and re-runs `decompress` with that exact size.

The maximum output cap is `_MAX_DECODE_OUTPUT = 1 MiB`; exceeding it raises
`ValueError` to reject false-positive chunk headers during resync.

---

### 8.7 Kraft completeness as a synchronization marker `[CORROBORATED]`

A valid Huffman table fills the code space exactly (Kraft sum = 1).  The
probability of a random 256-byte sequence satisfying Kraft equality is
extremely low, making it a strong structural marker for locating chunk
boundaries in the MSSQLBAK container stream.

External corroboration: MS-XCA defines the XPRESS prefix as 512 Huffman
codeword lengths encoded in 256 bytes; Kraft-McMillan gives the prefix-code
completeness condition used as the structural filter. This corroborates the
marker, not the MSSQLBAK record-header semantics.

Source: `compressed.py: _kraft_complete`.

---
