#!/usr/bin/env python3
"""
analyze_ivs.py — correlate hook-log IV captures with backup AES keys.

For each probe .bak file:
  1. Extracts the AES content-key from the MSSQLBAK header (RSA unwrap via PVK).
  2. Searches the ivprobe.log for a KEY= entry matching that key.
  3. Records the corresponding IV and call index.
  4. Prints a summary table showing chunk number, call index, and IV.
  5. Attempts full-stream AES-CBC decryption to verify each IV.

Usage:
    python analyze_ivs.py --probe-dir /var/tmp/probe_baks --pvk /var/tmp/probe_baks/probe_cert.pvk
"""

import argparse
import hashlib
import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# PVK loader (SQL Server format, password-protected RC4)
# ---------------------------------------------------------------------------

def load_pvk(pvk_path: Path, password: str):
    """Return an RSA private key object from a SQL Server PVK file."""
    from cryptography.hazmat.decrepit.ciphers.algorithms import ARC4
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers, RSAPublicNumbers

    data = pvk_path.read_bytes()
    # Header: magic(4) key_type(4) encrypted(4) salt_len(4) key_len(4)
    magic = struct.unpack_from("<I", data, 0)[0]
    assert magic == 0xB0B5F11E, f"Bad PVK magic: {magic:#010x}"
    cb_salt = struct.unpack_from("<I", data, 16)[0]
    cb_key  = struct.unpack_from("<I", data, 20)[0]
    salt    = data[24 : 24 + cb_salt]
    key_blob = data[24 + cb_salt : 24 + cb_salt + cb_key]

    rc4_key = hashlib.sha1(salt + password.encode("utf-8")).digest()[:16]
    cipher  = Cipher(ARC4(rc4_key), mode=None, backend=default_backend())
    dec     = cipher.decryptor()
    payload = dec.update(key_blob[8:]) + dec.finalize()

    rsa_magic = struct.unpack_from("<I", payload, 0)[0]
    assert rsa_magic == 0x32415352, f"Bad RSA2 magic: {rsa_magic:#010x}"
    bitlen  = struct.unpack_from("<I", payload, 4)[0]
    pubexp  = struct.unpack_from("<I", payload, 8)[0]
    n_bytes = bitlen // 8
    p_bytes = bitlen // 16
    off     = 12

    def rd(size):
        nonlocal off
        val = int.from_bytes(payload[off : off + size], "little")
        off += size
        return val

    n    = rd(n_bytes)
    p    = rd(p_bytes)
    q    = rd(p_bytes)
    dp   = rd(p_bytes)
    dq   = rd(p_bytes)
    iqmp = rd(p_bytes)
    d    = rd(n_bytes)

    pub  = RSAPublicNumbers(pubexp, n)
    priv = RSAPrivateNumbers(p, q, d, dp, dq, iqmp, pub)
    return priv.private_key(backend=default_backend())


# ---------------------------------------------------------------------------
# MSSQLBAK key extraction
# ---------------------------------------------------------------------------

def extract_content_key(bak_path: Path, rsa_key) -> bytes:
    """
    Read the MSSQLBAK header, unwrap the RSA blob, return the raw AES/3DES key.
    Returns raw key bytes from the PLAINTEXTKEYBLOB (after the 8-byte header).
    """
    from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

    data = bak_path.read_bytes(4096)   # header fits in first 4 KB
    magic = data[:8]
    assert magic == b"MSSQLBAK", f"Not MSSQLBAK: {magic!r}"

    rsa_len = struct.unpack_from("<I", data, 44)[0]
    rsa_blob = data[48 : 48 + rsa_len]
    # byte-reverse before RSA decrypt
    rsa_blob_rev = bytes(reversed(rsa_blob))
    plaintext = rsa_key.decrypt(rsa_blob_rev, asym_padding.PKCS1v15())
    # PLAINTEXTKEYBLOB: btype(1) version(1) reserved(2) algID(4) keylen(4) key(keylen)
    key_len = struct.unpack_from("<I", plaintext, 8)[0]
    content_key = plaintext[12 : 12 + key_len]
    return content_key


# ---------------------------------------------------------------------------
# Hook-log parser
# ---------------------------------------------------------------------------

def parse_log(log_path: Path) -> list[dict]:
    """
    Parse ivprobe.log.  Returns list of dicts with keys:
      idx, func, nid, key_len, key (bytes), iv_len, iv (bytes), backtrace (list[str])
    """
    entries = []
    current = None
    for line in log_path.read_text(errors="replace").splitlines():
        line = line.rstrip()
        if line.startswith("IDX="):
            if current:
                entries.append(current)
            parts = dict(tok.split("=", 1) for tok in line.split() if "=" in tok)
            current = {
                "idx":      int(parts["IDX"]),
                "func":     parts.get("FUNC", ""),
                "nid":      int(parts.get("NID", 0)),
                "key_len":  int(parts.get("KEY_LEN", 0)),
                "key":      bytes.fromhex(parts.get("KEY", "")),
                "iv_len":   int(parts.get("IV_LEN", 0)),
                "iv":       bytes.fromhex(parts.get("IV", "")),
                "backtrace": [],
            }
        elif line.startswith("  BT[") and current is not None:
            current["backtrace"].append(line.strip())
        elif line == "---" and current is not None:
            entries.append(current)
            current = None
    if current:
        entries.append(current)
    return entries


# ---------------------------------------------------------------------------
# Chunk-descriptor layout helpers
# ---------------------------------------------------------------------------

CHUNK_TYPE1 = b"\x33\x08\x00\x10"   # 0x10000833
CHUNK_TYPE2 = b"\x33\x10\x00\x20"   # 0x20001033

def iter_chunk_descriptors(bak_data: bytes):
    """
    Yield (offset, descriptor_bytes) for every 32-byte chunk descriptor
    found in the MSSQLBAK container.
    """
    pos = 0
    while pos < len(bak_data) - 32:
        sig = bak_data[pos:pos+4]
        if sig in (CHUNK_TYPE1, CHUNK_TYPE2):
            yield pos, bak_data[pos:pos+32]
            pos += 32
        else:
            pos += 1


# ---------------------------------------------------------------------------
# AES-CBC decryption helper
# ---------------------------------------------------------------------------

def try_decrypt_chunk(ciphertext: bytes, key: bytes, iv: bytes) -> bytes | None:
    """Attempt AES-CBC decryption; return None on padding error."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    try:
        c = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        dec = c.decryptor()
        return dec.update(ciphertext) + dec.finalize()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

NID_NAMES = {
    419: "aes-128-cbc",
    423: "aes-192-cbc",
    427: "aes-256-cbc",
    657: "aes-128-cfb8",
    661: "aes-192-cfb8",
    689: "aes-256-cfb8",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-dir", required=True, type=Path,
                    help="Directory containing probe_*.bak and ivprobe.log")
    ap.add_argument("--pvk", required=True, type=Path,
                    help="Path to probe_cert.pvk")
    ap.add_argument("--pvk-pass", default="PvkPass_1!",
                    help="PVK decryption password (default: PvkPass_1!)")
    ap.add_argument("--log", default=None, type=Path,
                    help="Path to ivprobe.log (default: <probe-dir>/ivprobe.log)")
    args = ap.parse_args()

    probe_dir: Path = args.probe_dir
    log_path = args.log or (probe_dir / "ivprobe.log")

    print(f"Loading PVK from {args.pvk}")
    rsa_key = load_pvk(args.pvk, args.pvk_pass)
    print(f"Parsing hook log from {log_path}")
    log_entries = parse_log(log_path)
    print(f"  {len(log_entries)} hook entries found")

    bak_files = [
        "probe_aes128.bak",
        "probe_aes256.bak",
        "probe_3des.bak",
        "probe_aes128_comp.bak",
    ]

    for bak_name in bak_files:
        bak_path = probe_dir / bak_name
        if not bak_path.exists():
            print(f"\n[SKIP] {bak_name} not found")
            continue

        print(f"\n{'='*60}")
        print(f"  {bak_name}")
        print(f"{'='*60}")

        try:
            content_key = extract_content_key(bak_path, rsa_key)
        except Exception as e:
            print(f"  [ERROR] key extraction failed: {e}")
            continue

        key_hex = content_key.hex()
        print(f"  Content key ({len(content_key)*8}-bit): {key_hex}")

        # Find matching log entries
        matches = [e for e in log_entries if e["key"] == content_key]
        if not matches:
            print(f"  [WARN] No hook log entries matched this key")
            print(f"         (total log entries: {len(log_entries)})")
            continue

        print(f"  Matched {len(matches)} hook call(s):")
        for m in matches:
            nid_name = NID_NAMES.get(m["nid"], f"nid={m['nid']}")
            print(f"    IDX={m['idx']:4d}  {m['func']}  {nid_name}  IV={m['iv'].hex()}")
            if m["backtrace"]:
                for bt in m["backtrace"][:6]:
                    print(f"           {bt}")

        # Attempt decryption with first CBC IV (skip CFB8 which is NID 657/661/689)
        cbc_matches = [m for m in matches if m["nid"] in (419, 423, 427)]
        if not cbc_matches:
            print("  [WARN] No CBC entries — only CFB8 found (likely TDE path)")
            continue

        # Load bak data and find first ciphertext block
        bak_data = bak_path.read_bytes()
        print(f"\n  Chunk descriptors found in {bak_name}:")
        descs = list(iter_chunk_descriptors(bak_data))
        for off, d in descs[:10]:
            nonce = d[24:32]
            ctr   = d[4:8]
            print(f"    @{off:#010x}  type={d[:4].hex()}  ctr={ctr.hex()}  nonce={nonce.hex()}")

        # Try decrypting first encrypted block after the header (offset 512)
        if len(bak_data) > 512 + 4096:
            first_ct = bak_data[512:512+4096]
            for m in cbc_matches[:3]:
                result = try_decrypt_chunk(first_ct[:512], content_key, m["iv"])
                if result and b"TAPE" in result:
                    print(f"\n  [HIT] IDX={m['idx']} IV={m['iv'].hex()} decrypts first block → TAPE marker found!")
                elif result:
                    print(f"\n  IDX={m['idx']} IV={m['iv'].hex()} → starts with {result[:16].hex()}")
                else:
                    print(f"\n  IDX={m['idx']} IV={m['iv'].hex()} → decryption error (padding)")

    print("\nDone.")


if __name__ == "__main__":
    main()
