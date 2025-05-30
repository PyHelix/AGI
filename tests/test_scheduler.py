import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.scheduler import schedule_wu


class SchedulerTests(unittest.TestCase):
    def test_schedule_wu_selects_best(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            board = Path(tmp) / "board.csv"
            board.write_text("worker_id,skill,reward,credit\nw1,vision,0.5,1\nw2,language,1.0,1\n")
            data = Path(tmp) / "chunk.dat"
            data.write_text("x")
            out_dir = Path(tmp) / "out"
            wu = schedule_wu(board, data, out_dir)
            contents = wu.read_text()
            self.assertIn("language", contents)


if __name__ == "__main__":
    unittest.main()
