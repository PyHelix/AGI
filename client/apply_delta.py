import argparse
from pathlib import Path


def apply_delta(weight_file: Path, delta_file: Path, out_file: Path) -> None:
    weight = float(weight_file.read_text().strip())
    delta = float(delta_file.read_text().strip())
    out_file.write_text(str(weight + delta))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weight", required=True)
    parser.add_argument("--delta", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    apply_delta(Path(args.weight), Path(args.delta), Path(args.out))


if __name__ == "__main__":
    main()
