import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

from client.encrypt_utils import encrypt_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Run training locally and encrypt the result")
    parser.add_argument("--script", required=True, help="Path to train_local.py")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True, help="Path for raw delta")
    parser.add_argument("--key", default="project_keys/weights.key", help="Hex AES key")
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--lr", type=float, default=1e-4)
    args = parser.parse_args()

    # run the provided training script
    subprocess.run([
        sys.executable,
        args.script,
        "--weights",
        args.weights,
        "--data",
        args.data,
        "--output",
        args.output,
        "--steps",
        str(args.steps),
        "--lr",
        str(args.lr),
    ], check=True)

    delta_path = Path(args.output)
    sha = hashlib.sha256(delta_path.read_bytes()).hexdigest()
    delta_path.write_text(delta_path.read_text() + f"sha256: {sha}\n")

    key = bytes.fromhex(Path(args.key).read_text().strip())
    enc = encrypt_file(delta_path, key)
    print(f"encrypted delta written to {enc}")


if __name__ == "__main__":
    main()

