import argparse
import json
from pathlib import Path


def load_value(p: Path) -> float:
    text = p.read_text().strip()
    try:
        data = json.loads(text)
        return float(data.get("w", 0.0))
    except json.JSONDecodeError:
        return float(text)


def save_value(p: Path, val: float) -> None:
    p.write_text(json.dumps({"w": val, "version": "0.2"}))


def apply_delta(weight_file: Path, delta_file: Path, out_file: Path) -> None:
    weight = load_value(weight_file)
    delta = load_value(delta_file)
    save_value(out_file, weight + delta)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weight", required=True)
    parser.add_argument("--delta", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    apply_delta(Path(args.weight), Path(args.delta), Path(args.out))


if __name__ == "__main__":
    main()
