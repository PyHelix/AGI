import argparse
from pathlib import Path

from router import pick_best_skill
from server.generate_wu import create_wu


def schedule_wu(board: Path, data: Path, out_dir: Path) -> Path:
    """Create a work unit for the highest-scoring skill."""
    skill = pick_best_skill(board)
    return create_wu(skill, data, out_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a work unit for the best skill")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--out", default="wu_out", help="Output directory")
    parser.add_argument("--board", default="scoreboard.csv", help="Scoreboard CSV")
    args = parser.parse_args()

    path = schedule_wu(Path(args.board), Path(args.data), Path(args.out))
    print(path)


if __name__ == "__main__":
    main()
