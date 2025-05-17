import csv
from pathlib import Path
from typing import Dict


def load_rewards(board: Path) -> Dict[str, float]:
    """Return average reward per skill from scoreboard."""
    if not board.exists():
        return {}
    totals: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    with board.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            skill = row["skill"]
            reward = float(row["reward"])
            totals[skill] = totals.get(skill, 0.0) + reward
            counts[skill] = counts.get(skill, 0) + 1
    return {s: totals[s] / counts[s] for s in totals}


def pick_best_skill(board: Path = Path("scoreboard.csv")) -> str:
    """Return skill id with highest average reward."""
    averages = load_rewards(board)
    if not averages:
        return "vision"  # default skill
    return max(averages.items(), key=lambda x: x[1])[0]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Select skill based on reward history")
    parser.add_argument("--board", default="scoreboard.csv", help="Path to scoreboard CSV")
    args = parser.parse_args()

    best = pick_best_skill(Path(args.board))
    print(best)
