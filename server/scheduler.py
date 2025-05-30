import argparse
from pathlib import Path

from router import pick_best_skill
from server.generate_wu import create_wu


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a work unit based on the highest scoring skill"
    )
    parser.add_argument("--data", required=True, help="Path to training data chunk")
    parser.add_argument("--out", default="work_units", help="Directory for generated work units")
    parser.add_argument("--board", default="scoreboard.csv", help="Scoreboard CSV path")
    args = parser.parse_args()

    skill = pick_best_skill(Path(args.board))
    wu = create_wu(skill, Path(args.data), Path(args.out))
    print(f"created {wu} for skill {skill}")


if __name__ == "__main__":
    main()
