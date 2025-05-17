import unittest
from pathlib import Path
from router import load_rewards, pick_best_skill


class RouterTest(unittest.TestCase):
    def test_pick_best_skill_no_board(self):
        self.assertEqual(pick_best_skill(Path("missing.csv")), "vision")

    def test_load_and_pick(self):
        csv_path = Path("tmp_board.csv")
        csv_path.write_text(
            "worker_id,skill,reward,credit\nw1,skillA,0.2,4\nw2,skillB,0.5,5\n"
        )
        try:
            averages = load_rewards(csv_path)
            self.assertAlmostEqual(averages["skillA"], 0.2)
            self.assertAlmostEqual(averages["skillB"], 0.5)
            self.assertEqual(pick_best_skill(csv_path), "skillB")
        finally:
            csv_path.unlink()


if __name__ == "__main__":
    unittest.main()
