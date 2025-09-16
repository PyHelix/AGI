"""Resource-aware work-unit sharding for the BOINC training pipeline."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from itertools import cycle
from pathlib import Path
from typing import Iterable, List, Sequence

try:
    from server.generate_wu import create_wu
except ModuleNotFoundError:  # pragma: no cover - allows running as a script from repo root
    sys.path.append(str(Path(__file__).resolve().parent))
    from generate_wu import create_wu


@dataclass(slots=True)
class ResourceSpec:
    """Description of a volunteer's available compute resources."""

    identifier: str
    weight: float = 1.0
    max_tasks: int = 1
    resource_class: str = "general"

    @classmethod
    def from_mapping(cls, mapping: dict) -> "ResourceSpec":
        if "id" not in mapping:
            raise ValueError("resource entry is missing the 'id' field")
        identifier = str(mapping["id"])
        weight = float(mapping.get("weight", 1.0))
        max_tasks = int(mapping.get("max_tasks", mapping.get("max_batch", 1)))
        resource_class = str(
            mapping.get("resource_class")
            or mapping.get("kind")
            or mapping.get("type")
            or "general"
        )
        if weight <= 0:
            raise ValueError("resource weight must be positive")
        if max_tasks <= 0:
            raise ValueError("max_tasks must be positive")
        return cls(
            identifier=identifier,
            weight=weight,
            max_tasks=max_tasks,
            resource_class=resource_class,
        )

    def scaled_steps(self, base_steps: int) -> int:
        steps = int(round(base_steps * self.weight))
        return max(1, steps)

    def scaled_lr(self, base_lr: float) -> float:
        lr = base_lr * max(0.5, self.weight)
        return max(1e-12, lr)


@dataclass(slots=True)
class ShardAssignment:
    """Computed shard tied to a specific resource."""

    shard_id: str
    resource: ResourceSpec
    data_path: Path
    steps: int
    lr: float
    wu_path: Path | None = None


def load_resource_specs(path: Path) -> List[ResourceSpec]:
    """Load resource descriptions from a JSON file."""

    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError("resource specification must be a JSON array")
    return [ResourceSpec.from_mapping(entry) for entry in data]


def split_data_chunks(data: Path, shard_count: int, work_dir: Path) -> List[Path]:
    """Return a list of data chunks that should be used for sharding."""

    if shard_count <= 0:
        raise ValueError("shard_count must be positive")

    data = data.expanduser().resolve()
    if data.is_dir():
        chunks = sorted(p for p in data.iterdir() if p.is_file())
        if not chunks:
            raise ValueError(f"no data files found in {data}")
        return chunks

    text = data.read_text().splitlines()
    if not text:
        text = [""]

    shard_dir = (work_dir / "data_shards").resolve()
    shard_dir.mkdir(parents=True, exist_ok=True)

    chunk_size = max(1, math.ceil(len(text) / shard_count))
    chunks: List[Path] = []
    for index in range(shard_count):
        start = index * chunk_size
        chunk_lines = text[start : start + chunk_size]
        if not chunk_lines and chunks:
            # Reuse previous data when there are more shards than unique chunks
            chunk_lines = text[-chunk_size:]
        dest = shard_dir / f"{data.stem}_shard{index}{data.suffix or '.txt'}"
        dest.write_text("\n".join(chunk_lines) + ("\n" if chunk_lines else ""))
        chunks.append(dest)

    return chunks


def plan_shards(
    skill: str,
    data_chunks: Sequence[Path],
    resources: Sequence[ResourceSpec],
    base_steps: int,
    base_lr: float,
) -> List[ShardAssignment]:
    """Create shard assignments for each resource specification."""

    if not resources:
        raise ValueError("at least one resource specification is required")
    if not data_chunks:
        raise ValueError("no data chunks provided")
    if base_steps <= 0:
        raise ValueError("base_steps must be positive")
    if base_lr <= 0:
        raise ValueError("base_lr must be positive")

    chunk_cycle = cycle(data_chunks)
    assignments: List[ShardAssignment] = []
    for resource in resources:
        steps = resource.scaled_steps(base_steps)
        lr = resource.scaled_lr(base_lr)
        for replica in range(resource.max_tasks):
            data_path = next(chunk_cycle)
            shard_id = f"{skill}-{resource.identifier}-shard{replica}"
            assignments.append(
                ShardAssignment(
                    shard_id=shard_id,
                    resource=resource,
                    data_path=data_path,
                    steps=steps,
                    lr=lr,
                )
            )
    return assignments


def create_sharded_work_units(
    skill: str,
    data: Path,
    resources: Sequence[ResourceSpec],
    out_dir: Path,
    *,
    base_steps: int = 100,
    base_lr: float = 1e-4,
) -> List[ShardAssignment]:
    """Generate BOINC work units for each resource shard."""

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    shard_count = sum(resource.max_tasks for resource in resources)
    data_chunks = split_data_chunks(Path(data), shard_count, out_dir)

    assignments = plan_shards(skill, data_chunks, resources, base_steps, base_lr)
    for assignment in assignments:
        assignment.wu_path = create_wu(
            skill,
            assignment.data_path,
            out_dir,
            steps=assignment.steps,
            lr=assignment.lr,
            shard_id=assignment.shard_id,
            resource_class=assignment.resource.resource_class,
        )
    return assignments


def _resource_summary(assignments: Iterable[ShardAssignment]) -> str:
    parts = []
    for assignment in assignments:
        steps = assignment.steps
        lr = assignment.lr
        resource = assignment.resource
        parts.append(
            f"{resource.identifier}({resource.resource_class}) -> {assignment.shard_id}"
            f" steps={steps} lr={lr:.6g}"
        )
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan sharded work units for volunteers")
    parser.add_argument("--skill", required=True, help="Skill name to train")
    parser.add_argument("--data", required=True, help="Path to the dataset file or directory")
    parser.add_argument("--resources", required=True, help="JSON file describing volunteers")
    parser.add_argument("--out", required=True, help="Directory where work units will be written")
    parser.add_argument("--base-steps", type=int, default=100, help="Baseline number of training steps")
    parser.add_argument("--base-lr", type=float, default=1e-4, help="Baseline learning rate")
    args = parser.parse_args()

    specs = load_resource_specs(Path(args.resources))
    assignments = create_sharded_work_units(
        args.skill,
        Path(args.data),
        specs,
        Path(args.out),
        base_steps=args.base_steps,
        base_lr=args.base_lr,
    )
    print(_resource_summary(assignments))


if __name__ == "__main__":
    main()
