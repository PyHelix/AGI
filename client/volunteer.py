import argparse
import hashlib
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from encrypt_utils import encrypt_file


def parse_wu(wu_dir: Path) -> tuple[str, Path, Path]:
    xml_file = next(wu_dir.glob("wu_*.xml"))
    root = ET.parse(xml_file).getroot()
    cmd = root.findtext("command", "")
    skill = cmd.split("apps/")[1].split("/")[0]
    weights = cmd.split("--weights")[1].split()[0]
    data = cmd.split("--data")[1].split()[0]
    return skill, wu_dir / weights, wu_dir / data


def train(skill: str, weights: Path, data: Path, out: Path) -> None:
    script = Path("server/apps") / skill / "train_local.py"
    subprocess.run([
        sys.executable,
        str(script),
        "--weights",
        str(weights),
        "--data",
        str(data),
        "--output",
        str(out),
    ], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single work unit")
    parser.add_argument("--wu", required=True, help="Directory containing the work unit")
    parser.add_argument("--upload", required=True, help="Directory to upload the encrypted result")
    parser.add_argument("--key", default="project_keys/weights.key", help="Hex AES key")
    args = parser.parse_args()

    wu_dir = Path(args.wu)
    skill, weights, data = parse_wu(wu_dir)
    delta = wu_dir / "delta.txt"
    train(skill, weights, data, delta)

    sha = hashlib.sha256(delta.read_bytes()).hexdigest()
    delta.write_text(delta.read_text() + f"sha256: {sha}\n")

    key = bytes.fromhex(Path(args.key).read_text().strip())
    enc = wu_dir / "delta.enc"
    encrypt_file(delta, key, enc)

    upload_dir = Path(args.upload)
    upload_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(enc, upload_dir / enc.name)
    print(f"uploaded {enc.name} from skill {skill}")


if __name__ == "__main__":
    main()
