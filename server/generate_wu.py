import argparse
import shutil
from pathlib import Path
from typing import Optional

from jinja2 import Template

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = (SCRIPT_DIR / "wu_template.xml").read_text()
ID_FILE = Path("next_wu_id.txt")
BUNDLED_APPS_DIR = SCRIPT_DIR / "apps"
LEGACY_APPS_DIR = Path("apps")


def next_id() -> int:
    if ID_FILE.exists():
        val = int(ID_FILE.read_text()) + 1
    else:
        val = 1
    ID_FILE.write_text(str(val))
    return val


def create_wu(
    skill: str,
    data: Path,
    out: Path,
    *,
    steps: int = 100,
    lr: float = 1e-4,
    shard_id: Optional[str] = None,
    resource_class: Optional[str] = None,
) -> Path:
    """Create a BOINC work unit for the given skill and data.

    Parameters
    ----------
    skill: str
        Name of the skill subfolder. ``init_weights.txt`` is resolved relative to this
        script (``server/apps/<skill>``) with a legacy fallback to ``apps/<skill>`` in the
        current working directory.
    data: Path
        Path to the training data chunk.
    out: Path
        Directory where the work unit files should be written.
    steps: int, optional
        Number of local fine-tuning steps the volunteer should run.
    lr: float, optional
        Learning rate for the local optimizer.
    shard_id: str, optional
        Identifier of the resource shard assigned to the work unit.
    resource_class: str, optional
        Hint describing the hardware tier that should process the work unit.

    Returns
    -------
    Path
        The path to the generated work-unit XML file.
    """

    if steps <= 0:
        raise ValueError("steps must be a positive integer")
    if lr <= 0:
        raise ValueError("lr must be a positive value")

    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_src = Path(data)
    wid = next_id()

    data_dst = out_dir / f"{wid}_{data_src.name}"
    shutil.copy2(data_src, data_dst)

    for weight_dir in (BUNDLED_APPS_DIR, LEGACY_APPS_DIR):
        weights_src = weight_dir / skill / "init_weights.txt"
        if weights_src.exists():
            break
    else:
        raise FileNotFoundError(
            "init_weights.txt not found in bundled server/apps or legacy project apps/ directories"
        )
    weights_dst = out_dir / f"{wid}_{weights_src.name}"
    shutil.copy2(weights_src, weights_dst)

    ctx = {
        "input_filename": data_dst.name,
        "input_filesize": data_dst.stat().st_size,
        "skill_id": skill,
        "input_weights": weights_dst.name,
        "data_chunk": data_dst.name,
        "steps": steps,
        "lr": f"{lr:.8g}",
        "shard_id": shard_id,
        "resource_class": resource_class,
    }
    xml = Template(TEMPLATE).render(**ctx)
    wu_file = out_dir / f"wu_{wid}.xml"
    wu_file.write_text(xml)
    return wu_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--steps", type=int, default=100, help="Training steps for the shard")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate for the shard")
    parser.add_argument("--shard-id", help="Optional identifier for the resource shard")
    parser.add_argument(
        "--resource-class", help="Optional resource class hint (e.g. cpu, gpu)"
    )
    args = parser.parse_args()

    create_wu(
        args.skill,
        Path(args.data),
        Path(args.out),
        steps=args.steps,
        lr=args.lr,
        shard_id=args.shard_id,
        resource_class=args.resource_class,
    )


if __name__ == "__main__":
    main()
