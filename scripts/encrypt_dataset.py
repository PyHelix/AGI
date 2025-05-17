import argparse
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_FILE = Path("project_keys/weights.key")


def main() -> None:
    parser = argparse.ArgumentParser(description="Encrypt dataset file")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    key = bytes.fromhex(KEY_FILE.read_text().strip())
    data = Path(args.input).read_bytes()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, data, None)
    Path(args.output).write_bytes(nonce + ct)


if __name__ == "__main__":
    main()
