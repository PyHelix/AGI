from pathlib import Path
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file(path: Path, key: bytes) -> Path:
    """Encrypt the given file with AESGCM and return the encrypted path."""
    data = path.read_bytes()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, data, None)
    out = path.with_suffix(path.suffix + ".enc")
    out.write_bytes(nonce + ciphertext)
    return out

