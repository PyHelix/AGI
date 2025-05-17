import csv
from pathlib import Path
import tempfile
import unittest

from router import pick_best_skill


class RouterTests(unittest.TestCase):
    def test_pick_best_skill_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            board = Path(tmpdir) / "score.csv"
            self.assertEqual(pick_best_skill(board), "vision")

    def test_pick_best_skill_highest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            board = Path(tmpdir) / "board.csv"
            with board.open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["worker_id", "skill", "reward", "credit"])
                writer.writerow(["w1", "skill_a", "0.4", "1"])
                writer.writerow(["w2", "skill_b", "0.9", "1"])
                writer.writerow(["w3", "skill_a", "0.6", "1"])
            self.assertEqual(pick_best_skill(board), "skill_b")


if __name__ == "__main__":
    unittest.main()
