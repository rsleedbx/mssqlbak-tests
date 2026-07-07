## 8. XPRESS Compression (MS-XCA LZ77+Huffman)

Reference: [MS-XCA] — *Xpress Compression Algorithm*.

### 8.1 Sub-chunk format `[CONFIRMED against MS-XCA]`

Each XPRESS chunk consists of:
1. A **256-byte Huffman prefix table**: 512 codeword lengths encoded as 4-bit
   nibbles (even symbol = low nibble, odd = high nibble).
2. A **bitstream** of LZ77 tokens.

Maximum output per chunk: 65 536 bytes (`_SUB_CHUNK_OUT`).

### 8.2 Kraft completeness as a synchronization marker `[CORROBORATED]`

A valid Huffman table fills the code space exactly (Kraft sum = 1).  The
probability of a random 256-byte sequence satisfying Kraft equality is
extremely low, making it a strong structural marker for locating chunk
boundaries in the MSSQLBAK container stream.

External corroboration: MS-XCA defines the XPRESS prefix as 512 Huffman codeword
lengths encoded in 256 bytes; Kraft-McMillan gives the prefix-code completeness
condition used as the structural filter. This corroborates the marker, not the
MSSQLBAK record-header semantics.

---

