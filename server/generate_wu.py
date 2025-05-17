import argparse
import shutil
from pathlib import Path

from aginet.log import get_logger

TEMPLATE = Path(__file__).with_name("wu_template.xml").read_text()
ID_FILE = Path("next_wu_id.txt")
log = get_logger(__name__)


def next_id() -> int:
    if ID_FILE.exists():
        try:
            val = int(ID_FILE.read_text()) + 1
        except ValueError:
            val = 1
    else:
        val = 1
    ID_FILE.write_text(str(val))
    return val


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_src = Path(args.data)
    data_dst = out_dir / data_src.name
    shutil.copy2(data_src, data_dst)

    weights_src = Path(f"server/apps/{args.skill}/init_weights.txt")
    weights_dst = out_dir / weights_src.name
    shutil.copy2(weights_src, weights_dst)

    wid = next_id()
    ctx = {
        "input_filename": data_dst.name,
        "input_filesize": data_dst.stat().st_size,
        "skill_id": args.skill,
        "input_weights": weights_dst.name,
        "data_chunk": data_dst.name,
        "steps": 100,
        "lr": 1e-4,
    }
    xml = TEMPLATE.format(**ctx)
    (out_dir / f"wu_{wid}.xml").write_text(xml)
    log.info("Generated work unit %s", wid)


if __name__ == "__main__":
    main()
