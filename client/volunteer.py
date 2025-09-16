"""Simulated volunteer that trains a work unit and uploads an encrypted result."""

import argparse
import shlex
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from client.encrypt_utils import encrypt_file


@dataclass(slots=True)
class WorkUnit:
    """Configuration extracted from a BOINC work-unit description."""

    skill: str
    weights: Path
    data: Path
    steps: int
    lr: float
    shard_id: Optional[str] = None
    resource_class: Optional[str] = None


def _arg_value(argv: list[str], flag: str, default: Optional[str] = None) -> Optional[str]:
    """Return the value that follows ``flag`` in ``argv`` if present."""

    if flag not in argv:
        return default
    index = argv.index(flag)
    if index + 1 >= len(argv):
        raise ValueError(f"flag {flag} missing value in work-unit command")
    return argv[index + 1]


def parse_wu(wu_dir: Path) -> WorkUnit:
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

    weights = _arg_value(argv, "--weights")
    data = _arg_value(argv, "--data")
    steps = _arg_value(argv, "--steps", "100")
    lr = _arg_value(argv, "--lr", "1e-4")

    if weights is None or data is None:
        raise ValueError("work-unit command missing required --weights/--data flags")

    shard_id = _arg_value(argv, "--shard-id")
    resource_class = _arg_value(argv, "--resource-class")

    return WorkUnit(
        skill=skill,
        weights=wu_dir / weights,
        data=wu_dir / data,
        steps=int(steps),
        lr=float(lr),
        shard_id=shard_id,
        resource_class=resource_class,
    )


def train(unit: WorkUnit, out: Path) -> None:
    script = Path("server/apps") / unit.skill / "train_local.py"
    cmd = [
        "python",
        str(script),
        "--weights",
        str(unit.weights),
        "--data",
        str(unit.data),
        "--output",
        str(out),
        "--steps",
        str(unit.steps),
        "--lr",
        str(unit.lr),
    ]
    if unit.shard_id:
        cmd.extend(["--shard-id", unit.shard_id])
    if unit.resource_class:
        cmd.extend(["--resource-class", unit.resource_class])
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single work unit")
    parser.add_argument("--wu", required=True, help="Directory containing the work unit")
    parser.add_argument("--upload", required=True, help="Directory to upload the encrypted result")
    args = parser.parse_args()

    wu_dir = Path(args.wu)
    unit = parse_wu(wu_dir)
    delta = wu_dir / "delta.txt"
    train(unit, delta)
    enc = wu_dir / "delta.enc"
    encrypt_file(delta, Path("project_keys/weights.key"), enc)

    upload_dir = Path(args.upload)
    upload_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(enc, upload_dir / enc.name)
    shard_msg = f" shard={unit.shard_id}" if unit.shard_id else ""
    resource_msg = (
        f" resource={unit.resource_class}" if unit.resource_class else ""
    )
    print(f"uploaded {enc.name} from skill {unit.skill}{shard_msg}{resource_msg}")


if __name__ == "__main__":
    main()
