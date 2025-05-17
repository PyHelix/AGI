import unittest
from pathlib import Path

from server.apps.common.train_utils import ppo_loop


class TrainUtilsTests(unittest.TestCase):
    def test_ppo_loop_outputs(self) -> None:
        delta, reward, kl, before, after = ppo_loop(Path('w'), Path('d'), 5, 0.1)
        self.assertGreater(delta, 0)
        self.assertGreater(reward, 0)
        self.assertGreaterEqual(before, after)
        self.assertGreaterEqual(after, 0)
        self.assertAlmostEqual(before, 1.0)


if __name__ == '__main__':
    unittest.main()
