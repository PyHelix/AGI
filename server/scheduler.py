from __future__ import annotations

import argparse
import sys
from pathlib import Path

FILE = Path(__file__).resolve()
if __package__ is None or __package__ == "":
    project_root = FILE.parents[1]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

from router import pick_best_skill
from server.generate_wu import create_wu


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a work unit based on the highest scoring skill")
    parser.add_argument("--data", required=True, help="Path to training data chunk")
    parser.add_argument("--out", default="work_units", help="Directory for generated work units")
    parser.add_argument("--board", default="scoreboard.csv", help="Scoreboard CSV path")
    args = parser.parse_args()

    skill = pick_best_skill(Path(args.board))
    wu = create_wu(skill, Path(args.data), Path(args.out))
    print(f"created {wu} for skill {skill}")


if __name__ == "__main__":
    main()
