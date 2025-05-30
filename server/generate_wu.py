import argparse
import shutil
from pathlib import Path

TEMPLATE = Path(__file__).with_name("wu_template.xml").read_text()
ID_FILE = Path("next_wu_id.txt")


def next_id() -> int:
    """Return a monotonically increasing work-unit id."""
    if ID_FILE.exists():
        val = int(ID_FILE.read_text()) + 1
    else:
        val = 1
    ID_FILE.write_text(str(val))
    return val


def create_wu(skill: str, data: Path, out_dir: Path, *, steps: int = 100, lr: float = 1e-4) -> Path:
    """Generate a work unit XML and copy required files.

    Parameters
    ----------
    skill : str
        Skill id, e.g. "vision" or "language".
    data : Path
        Path to the training data chunk.
    out_dir : Path
        Directory where the work-unit XML and input files will be written.
    steps : int, optional
        Training steps to pass to the worker script.
    lr : float, optional
        Learning rate for training.

    Returns
    -------
    Path
        Path to the generated work-unit XML file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    data_dst = out_dir / data.name
    shutil.copy2(data, data_dst)

    weights_src = Path(__file__).with_name("apps") / skill / "init_weights.txt"
    weights_dst = out_dir / weights_src.name
    shutil.copy2(weights_src, weights_dst)

    wid = next_id()
    ctx = {
        "input_filename": data_dst.name,
        "input_filesize": data_dst.stat().st_size,
        "skill_id": skill,
        "input_weights": weights_dst.name,
        "data_chunk": data_dst.name,
        "steps": steps,
        "lr": lr,
    }
    xml = TEMPLATE.format(**ctx)
    xml_path = out_dir / f"wu_{wid}.xml"
    xml_path.write_text(xml)
    return xml_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    create_wu(args.skill, Path(args.data), Path(args.out))


if __name__ == "__main__":
    main()
