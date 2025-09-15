import tempfile
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from client.apply_delta import apply_delta, _read_float


def test_read_float_accepts_plain_number() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "value.txt"
        p.write_text("1.23")
        assert _read_float(p) == 1.23


def test_read_float_parses_metric_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "metrics.txt"
        p.write_text("reward:1.0\ndelta: 0.5\n")
        assert _read_float(p) == 0.5


def test_apply_delta_writes_sum(tmp_path: Path) -> None:
    weight = tmp_path / "weight.txt"
    delta = tmp_path / "delta.txt"
    out = tmp_path / "out.txt"
    weight.write_text("1.0")
    delta.write_text("delta: 0.25\nreward: 0.8\n")

    apply_delta(weight, delta, out)

    assert out.read_text() == "1.25"
