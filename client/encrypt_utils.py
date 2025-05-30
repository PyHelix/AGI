"""Helper for simple AES encryption of result files."""
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file(src: Path, key_file: Path, dest: Path) -> None:
    key = bytes.fromhex(key_file.read_text().strip())
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, src.read_bytes(), None)
    dest.write_bytes(nonce + ct)
