#!/usr/bin/env python3
"""Simple scheduler that creates a work unit for the best-performing skill."""
import argparse
from pathlib import Path

from router import pick_best_skill
from server.generate_wu import create_wu


def main() -> None:
    parser = argparse.ArgumentParser(description="Create work unit for best skill")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--out", required=True, help="Output directory for work unit")
    parser.add_argument("--board", default="scoreboard.csv", help="Scoreboard CSV")
    args = parser.parse_args()

    skill = pick_best_skill(Path(args.board))
    wu_path = create_wu(skill, Path(args.data), Path(args.out))
    print(f"Generated {wu_path} for skill {skill}")


if __name__ == "__main__":
    main()
