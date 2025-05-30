"""Utility to generate an Ed25519 keypair for signing results."""
import argparse
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


def generate_keypair(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    (out_dir / "signing_key.pem").write_bytes(
        priv.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    (out_dir / "verify_key.pem").write_bytes(
        pub.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="project_keys")
    args = parser.parse_args()
    generate_keypair(Path(args.out))
    print(f"Keys written to {args.out}")


if __name__ == "__main__":
    main()
