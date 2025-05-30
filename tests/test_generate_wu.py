import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.generate_wu import create_wu


def test_create_wu(tmp_path: Path) -> None:
    data = tmp_path / "sample.txt"
    data.write_text("hello")
    out_dir = tmp_path / "out"
    wu_path = create_wu("vision", data, out_dir)
    assert wu_path.exists()
    xml = wu_path.read_text()
    assert "sample.txt" in xml
