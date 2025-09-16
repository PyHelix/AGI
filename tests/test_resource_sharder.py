import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import server.generate_wu as generate_wu
from server.resource_sharder import (
    ResourceSpec,
    create_sharded_work_units,
    load_resource_specs,
    plan_shards,
    split_data_chunks,
)


def test_load_resource_specs(tmp_path: Path) -> None:
    specs_file = tmp_path / "resources.json"
    specs_file.write_text(
        json.dumps(
            [
                {"id": "node-a", "weight": 2.5, "max_tasks": 2, "resource_class": "gpu"},
                {"id": "node-b"},
            ]
        )
    )
    specs = load_resource_specs(specs_file)
    assert len(specs) == 2
    assert specs[0].resource_class == "gpu"
    assert specs[0].max_tasks == 2
    assert specs[1].weight == 1.0


def test_split_data_chunks_creates_expected_parts(tmp_path: Path) -> None:
    data_file = tmp_path / "data.txt"
    data_file.write_text("\n".join(str(i) for i in range(9)))
    chunks = split_data_chunks(data_file, shard_count=3, work_dir=tmp_path)
    assert len(chunks) == 3
    assert all(chunk.exists() for chunk in chunks)
    assert "shard0" in chunks[0].name
    assert "shard2" in chunks[2].name

def test_plan_shards_cycles_data(tmp_path: Path) -> None:
    data_chunks = [tmp_path / f"chunk_{i}.txt" for i in range(2)]
    for chunk in data_chunks:
        chunk.write_text("sample")
    specs = [
        ResourceSpec(identifier="fast", weight=2.0, max_tasks=2, resource_class="gpu"),
        ResourceSpec(identifier="slow", weight=0.5, max_tasks=1, resource_class="cpu"),
    ]
    assignments = plan_shards("vision", data_chunks, specs, base_steps=100, base_lr=1e-4)
    assert len(assignments) == 3
    assert assignments[0].steps >= assignments[1].steps
    assert assignments[1].resource.identifier == "fast"
    assert assignments[2].resource.identifier == "slow"
    assert assignments[0].data_path in data_chunks
    assert assignments[1].data_path in data_chunks


def test_create_sharded_work_units_generates_xml(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    data_file = project / "prompts.txt"
    data_file.write_text("prompt-1\nprompt-2\nprompt-3\nprompt-4\n")

    specs = [
        ResourceSpec(identifier="gpu-1", weight=2.0, max_tasks=1, resource_class="gpu"),
        ResourceSpec(identifier="cpu-1", weight=1.0, max_tasks=1, resource_class="cpu"),
    ]

    cwd = os.getcwd()
    os.chdir(project)
    try:
        assignments = create_sharded_work_units(
            "vision",
            data_file,
            specs,
            project / "wu",
            base_steps=50,
            base_lr=2e-4,
        )
    finally:
        os.chdir(cwd)

    assert len(assignments) == 2
    xml_files = list((project / "wu").glob("wu_*.xml"))
    assert len(xml_files) == 2
    xml_text = xml_files[0].read_text()
    assert "--shard-id" in xml_text
    assert "--resource-class" in xml_text
    assert any(assignment.wu_path is not None for assignment in assignments)


def test_create_wu_falls_back_to_legacy_weights(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "legacy"
    project.mkdir()

    data_file = project / "dataset.txt"
    data_file.write_text("sample\n")

    legacy_weights_dir = project / "apps" / "vision"
    legacy_weights_dir.mkdir(parents=True)
    legacy_weights = legacy_weights_dir / "init_weights.txt"
    legacy_weights.write_text("legacy-weight")

    def fake_candidates(skill: str):
        yield Path("/nonexistent") / skill / "init_weights.txt"
        yield legacy_weights

    monkeypatch.setattr(generate_wu, "_weight_candidates", fake_candidates)

    cwd = os.getcwd()
    os.chdir(project)
    try:
        wu_file = generate_wu.create_wu(
            "vision",
            data_file,
            project / "out",
            steps=10,
            lr=1e-3,
        )
    finally:
        os.chdir(cwd)

    assert wu_file.exists()
    copied_weights = next((project / "out").glob("*_init_weights.txt"))
    assert copied_weights.read_text() == "legacy-weight"


def test_resource_sharder_help_invocation() -> None:
    script = Path(__file__).resolve().parents[1] / "server" / "resource_sharder.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Plan sharded work units" in result.stdout
