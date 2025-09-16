import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from client import volunteer


def test_parse_wu_extracts_metadata(tmp_path: Path) -> None:
    wu_dir = tmp_path / "wu"
    wu_dir.mkdir()
    xml = wu_dir / "wu_1.xml"
    xml.write_text(
        """
        <workunit>
            <command>python apps/vision/train_local.py --weights weights.txt --data data.txt --steps 64 --lr 0.0002 --output output.txt --shard-id vision-nodeA-shard0 --resource-class gpu</command>
        </workunit>
        """
    )
    (wu_dir / "weights.txt").write_text("0.0")
    (wu_dir / "data.txt").write_text("prompt")

    skill, weights, data, steps, lr, shard_id, resource_class = volunteer.parse_wu(wu_dir)
    assert skill == "vision"
    assert steps == 64
    assert abs(lr - 0.0002) < 1e-9
    assert shard_id == "vision-nodeA-shard0"
    assert resource_class == "gpu"
    assert weights.name == "weights.txt"
    assert data.name == "data.txt"


def test_train_passes_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool) -> None:  # pragma: no cover - executed in test
        calls.append(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)

    weights = tmp_path / "weights.txt"
    data = tmp_path / "data.txt"
    weights.write_text("0.0")
    data.write_text("prompt")

    volunteer.train(
        "vision",
        weights,
        data,
        tmp_path / "delta.txt",
        steps=128,
        lr=0.001,
        shard_id="vision-gpu",
        resource_class="gpu",
    )

    assert calls
    cmd = calls[0]
    assert "--steps" in cmd
    assert "128" in cmd
    assert "--lr" in cmd
    assert any(part.startswith("0.001") for part in cmd)
    assert "--shard-id" in cmd
    assert "vision-gpu" in cmd
    assert "--resource-class" in cmd
    assert "gpu" in cmd


def test_volunteer_help_invocation() -> None:
    script = Path(__file__).resolve().parents[1] / "client" / "volunteer.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Run a single work unit" in result.stdout
