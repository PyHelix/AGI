import argparse
import shutil
from pathlib import Path

from jinja2 import Template

TEMPLATE = Path(__file__).with_name("wu_template.xml").read_text()
ID_FILE = Path("next_wu_id.txt")


def next_id() -> int:
    if ID_FILE.exists():
        val = int(ID_FILE.read_text()) + 1
    else:
        val = 1
    ID_FILE.write_text(str(val))
    return val


def create_wu(skill: str, data: Path, out: Path) -> Path:
    """Create a BOINC work unit for the given skill and data.

    Parameters
    ----------
    skill: str
        Name of the skill subfolder under ``apps/``.
    data: Path
        Path to the training data chunk.
    out: Path
        Directory where the work unit files should be written.

    Returns
    -------
    Path
        The path to the generated work-unit XML file.
    """

    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_src = Path(data)
    data_dst = out_dir / data_src.name
    shutil.copy2(data_src, data_dst)

    weights_src = Path(f"apps/{skill}/init_weights.txt")
    weights_dst = out_dir / weights_src.name
    shutil.copy2(weights_src, weights_dst)

    wid = next_id()
    ctx = {
        "input_filename": data_dst.name,
        "input_filesize": data_dst.stat().st_size,
        "skill_id": skill,
        "input_weights": weights_dst.name,
        "data_chunk": data_dst.name,
        "steps": 100,
        "lr": 1e-4,
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
    args = parser.parse_args()

    create_wu(args.skill, Path(args.data), Path(args.out))


if __name__ == "__main__":
    main()
