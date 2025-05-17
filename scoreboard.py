#!/usr/bin/env python3
"""Simple scoreboard logger."""
import csv
import argparse
from pathlib import Path


def log_score(board: Path, worker: str, skill: str, reward: float, credit: float) -> None:
    """Append a single result entry to the scoreboard CSV."""
    board.parent.mkdir(parents=True, exist_ok=True)
    exists = board.exists()
    with board.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["worker_id", "skill", "reward", "credit"])
        writer.writerow([worker, skill, reward, credit])


def main() -> None:
    """Parse arguments and record a single scoreboard entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', default='scoreboard.csv')
    parser.add_argument('--worker', required=True)
    parser.add_argument('--skill', required=True)
    parser.add_argument('--reward', type=float, required=True)
    parser.add_argument('--credit', type=float, required=True)
    args = parser.parse_args()

    log_score(Path(args.board), args.worker, args.skill, args.reward, args.credit)


if __name__ == '__main__':
    main()
