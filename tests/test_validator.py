import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.validator import validate


class ValidatorTests(unittest.TestCase):
    def test_missing_file_returns_zero(self) -> None:
        self.assertEqual(validate(Path('nope')), 0.0)

    def test_low_reward_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'delta.txt'
            p.write_text('reward: 0.1\nkl:0.0\nloss_before:1.0\nloss_after:0.9\n')
            self.assertEqual(validate(p), 0.0)

    def test_valid_file_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'delta.txt'
            p.write_text('reward: 1.0\nkl:0.1\nloss_before:1.0\nloss_after:0.8\n')
            score = validate(p)
            self.assertGreater(score, 0.0)


if __name__ == '__main__':
    unittest.main()
