import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.generate_wu import create_wu


def test_create_wu(tmp_path):
    data = tmp_path / "chunk.txt"
    data.write_text("sample")
    out = tmp_path / "wu"
    xml = create_wu("vision", data, out)
    assert xml.exists()
    assert (out / data.name).exists()
    assert (out / "init_weights.txt").exists()

