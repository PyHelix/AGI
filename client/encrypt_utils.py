"""Simple AES helper for encrypting files."""

import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file(path: Path, key: bytes) -> Path:
    """Encrypt ``path`` using AESGCM and return the encrypted file path."""
    data = path.read_bytes()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, data, None)
    out = path.with_suffix(path.suffix + ".enc")
    out.write_bytes(nonce + ct)
    return out
