import tempfile
import unittest
from pathlib import Path

from router import pick_best_skill, load_rewards


class RouterTests(unittest.TestCase):
    def test_default_skill_when_board_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = Path(tmp) / "nonexistent.csv"
            self.assertEqual(pick_best_skill(board), "vision")

    def test_pick_best_skill_from_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = Path(tmp) / "scoreboard.csv"
            with board.open("w", newline="", encoding="utf-8") as f:
                f.write("worker_id,skill,reward,credit\n")
                f.write("w1,vision,0.5,1\n")
                f.write("w2,language,1.2,1\n")
                f.write("w3,language,0.8,1\n")
            self.assertEqual(pick_best_skill(board), "language")
            averages = load_rewards(board)
            self.assertAlmostEqual(averages["vision"], 0.5)
            self.assertAlmostEqual(averages["language"], 1.0)


if __name__ == "__main__":
    unittest.main()
