"""Simulated volunteer that trains a work unit and uploads an encrypted result."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Tuple

FILE = Path(__file__).resolve()
if __package__ is None or __package__ == "":
    project_root = FILE.parents[1]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

from client.encrypt_utils import encrypt_file


def _flag_value(argv: list[str], flag: str) -> Optional[str]:
    """Return the value that follows ``flag`` in ``argv`` if present."""

    if flag not in argv:
        return None
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise ValueError(f"flag {flag} missing value in work-unit command")
    return argv[index + 1]


def parse_wu(
    wu_dir: Path,
) -> Tuple[str, Path, Path, int, float, Optional[str], Optional[str]]:
    """Extract training configuration from a BOINC work-unit directory."""

    xml_file = next(wu_dir.glob("wu_*.xml"))
    root = ET.parse(xml_file).getroot()
    cmd = root.findtext("command", "")
    argv = shlex.split(cmd)
    if len(argv) < 2:
        raise ValueError("work-unit command is malformed")

    script = Path(argv[1])
    try:
        skill = script.parts[1]
    except IndexError as exc:
        raise ValueError(f"unable to infer skill from command {cmd!r}") from exc

    weights = _flag_value(argv, "--weights")
    data = _flag_value(argv, "--data")
    if weights is None or data is None:
        raise ValueError("work-unit command missing required --weights/--data flags")

    steps_str = _flag_value(argv, "--steps")
    lr_str = _flag_value(argv, "--lr")
    steps = int(steps_str) if steps_str is not None else 100
    lr = float(lr_str) if lr_str is not None else 1e-4
    shard_id = _flag_value(argv, "--shard-id")
    resource_class = _flag_value(argv, "--resource-class")

    return (
        skill,
        wu_dir / weights,
        wu_dir / data,
        steps,
        lr,
        shard_id,
        resource_class,
    )


def train(
    skill: str,
    weights: Path,
    data: Path,
    out: Path,
    *,
    steps: int,
    lr: float,
    shard_id: Optional[str] = None,
    resource_class: Optional[str] = None,
) -> None:
    """Invoke the local training script with metadata from the work unit."""

    script = Path("server/apps") / skill / "train_local.py"
    cmd = [
        sys.executable,
        str(script),
        "--weights",
        str(weights),
        "--data",
        str(data),
        "--output",
        str(out),
        "--steps",
        str(steps),
        "--lr",
        f"{lr:.8g}",
    ]
    if shard_id:
        cmd.extend(["--shard-id", shard_id])
    if resource_class:
        cmd.extend(["--resource-class", resource_class])
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single work unit")
    parser.add_argument("--wu", required=True, help="Directory containing the work unit")
    parser.add_argument("--upload", required=True, help="Directory to upload the encrypted result")
    args = parser.parse_args()

    wu_dir = Path(args.wu)
    (
        skill,
        weights,
        data,
        steps,
        lr,
        shard_id,
        resource_class,
    ) = parse_wu(wu_dir)
    delta = wu_dir / "delta.txt"
    train(
        skill,
        weights,
        data,
        delta,
        steps=steps,
        lr=lr,
        shard_id=shard_id,
        resource_class=resource_class,
    )
    enc = wu_dir / "delta.enc"
    encrypt_file(delta, Path("project_keys/weights.key"), enc)

    upload_dir = Path(args.upload)
    upload_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(enc, upload_dir / enc.name)
    shard_msg = f" shard={shard_id}" if shard_id else ""
    resource_msg = f" resource={resource_class}" if resource_class else ""
    print(f"uploaded {enc.name} from skill {skill}{shard_msg}{resource_msg}")


if __name__ == "__main__":
    main()
