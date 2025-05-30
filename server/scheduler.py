import argparse
from pathlib import Path

from router import pick_best_skill
from generate_wu import create_wu


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a work unit for the best skill")
    parser.add_argument("--board", default="scoreboard.csv", help="Scoreboard CSV path")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--out", default="work_units", help="Output directory")
    args = parser.parse_args()

    skill = pick_best_skill(Path(args.board))
    xml_path = create_wu(skill, Path(args.data), Path(args.out))
    print(xml_path)


if __name__ == "__main__":
    main()
