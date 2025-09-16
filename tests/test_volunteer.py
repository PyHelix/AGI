import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from client.volunteer import WorkUnit, parse_wu, train


class DummyRun:
    def __init__(self):
        self.calls = []

    def __call__(self, cmd, check):
        self.calls.append(cmd)


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

    unit = parse_wu(wu_dir)
    assert unit.skill == "vision"
    assert unit.steps == 64
    assert abs(unit.lr - 0.0002) < 1e-9
    assert unit.shard_id == "vision-nodeA-shard0"
    assert unit.resource_class == "gpu"


def test_train_passes_metadata(tmp_path: Path, monkeypatch) -> None:
    dummy = DummyRun()
    monkeypatch.setattr(subprocess, "run", dummy)

    unit = WorkUnit(
        skill="vision",
        weights=tmp_path / "weights.txt",
        data=tmp_path / "data.txt",
        steps=128,
        lr=0.001,
        shard_id="vision-gpu",
        resource_class="gpu",
    )
    unit.weights.write_text("0.0")
    unit.data.write_text("data")

    train(unit, tmp_path / "delta.txt")

    assert dummy.calls
    cmd = dummy.calls[0]
    assert "--steps" in cmd
    assert "128" in cmd
    assert "--shard-id" in cmd
    assert "vision-gpu" in cmd
    assert "--resource-class" in cmd
    assert "gpu" in cmd
