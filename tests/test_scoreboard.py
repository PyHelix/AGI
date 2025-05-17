import tempfile
import csv
import unittest
from pathlib import Path

from scoreboard import log_score


class ScoreboardTests(unittest.TestCase):
    def test_log_score_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            board = Path(tmp) / 'scores' / 'board.csv'
            log_score(board, 'worker1', 'vision', 1.0, 2.0)
            self.assertTrue(board.exists())
            with board.open(newline='', encoding='utf-8') as f:
                rows = list(csv.reader(f))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1][0], 'worker1')


if __name__ == '__main__':
    unittest.main()
