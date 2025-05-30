"""Simulated volunteer that trains a work unit and uploads an encrypted result."""
import argparse
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from client.encrypt_utils import encrypt_file


def parse_wu(wu_dir: Path) -> tuple[str, Path, Path]:
    xml_file = next(wu_dir.glob("wu_*.xml"))
    root = ET.parse(xml_file).getroot()
    cmd = root.findtext("command", "")
    # very basic parsing of command line
    skill = cmd.split("apps/")[1].split("/")[0]
    weights = cmd.split("--weights")[1].split()[0]
    data = cmd.split("--data")[1].split()[0]
    return skill, wu_dir / weights, wu_dir / data


def train(skill: str, weights: Path, data: Path, out: Path) -> None:
    script = Path("server/apps") / skill / "train_local.py"
    subprocess.run([
        "python",
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
    args = parser.parse_args()

    wu_dir = Path(args.wu)
    skill, weights, data = parse_wu(wu_dir)
    delta = wu_dir / "delta.txt"
    train(skill, weights, data, delta)
    enc = wu_dir / "delta.enc"
    encrypt_file(delta, Path("project_keys/weights.key"), enc)

    upload_dir = Path(args.upload)
    upload_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(enc, upload_dir / enc.name)
    print(f"uploaded {enc.name} from skill {skill}")


if __name__ == "__main__":
    main()
