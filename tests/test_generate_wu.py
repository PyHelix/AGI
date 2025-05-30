import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.generate_wu import create_wu


class GenerateWuTests(unittest.TestCase):
    def test_create_wu_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "sample.dat"
            data.write_text("test")
            out_dir = Path(tmp) / "out"
            wu = create_wu("vision", data, out_dir)
            self.assertTrue(wu.exists())
            text = wu.read_text()
            self.assertIn("train_local.py", text)


if __name__ == "__main__":
    unittest.main()
