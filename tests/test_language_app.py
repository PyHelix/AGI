import subprocess
import sys
from pathlib import Path
import tempfile
import os
import unittest

class LanguageAppTests(unittest.TestCase):
    def test_train_local_outputs_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)/"data.txt"
            data.write_text("hello world")
            weights = Path(tmp)/"weights.txt"
            weights.write_text("0.0")
            out = Path(tmp)/"delta.txt"
            env = os.environ.copy()
            env["WU_ID"] = "t"
            env["SKILL"] = "language"
            subprocess.run([
                sys.executable,
                "-m",
                "server.apps.language.train_local",
                "--weights", str(weights),
                "--data", str(data),
                "--output", str(out),
                "--steps", "1",
            ], check=True, env=env)
            self.assertTrue(out.exists())

if __name__ == "__main__":
    unittest.main()
