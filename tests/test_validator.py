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
            p.write_text('{"w":0.1,"reward":0.1,"kl":0.0,"loss_before":1.0,"loss_after":0.9,"version":"0.2"}')
            self.assertEqual(validate(p), 0.0)

    def test_valid_file_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'delta.txt'
            p.write_text('{"w":0.2,"reward":1.0,"kl":0.1,"loss_before":1.0,"loss_after":0.8,"version":"0.2"}')
            score = validate(p)
            self.assertGreater(score, 0.0)


if __name__ == '__main__':
    unittest.main()
