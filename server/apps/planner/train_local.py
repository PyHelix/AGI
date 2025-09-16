import argparse
import sys
from pathlib import Path

FILE = Path(__file__).resolve()
if __package__ is None or __package__ == "":
    for parent in FILE.parents[1: min(4, len(FILE.parents))]:
        parent_str = str(parent)
        if parent_str not in sys.path:
            sys.path.insert(0, parent_str)

try:
    from server.apps.common.train_utils import ppo_loop
except ModuleNotFoundError:  # pragma: no cover - fallback for BOINC project layout
    from common.train_utils import ppo_loop


def main():
    parser = argparse.ArgumentParser(description="Local fine-tuning with PPO and LoRA")
    parser.add_argument("--weights", required=True, help="Initial model weights")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--output", required=True, help="Output file for weight deltas")
    parser.add_argument("--steps", type=int, default=100, help="Training steps")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--shard-id", help="Optional identifier for this shard")
    parser.add_argument(
        "--resource-class",
        help="Optional resource class hint (for logging only)",
    )
    args = parser.parse_args()

    delta, reward, kl, loss_before, loss_after = ppo_loop(
        Path(args.weights), Path(args.data), args.steps, args.lr
    )
    output = Path(args.output)
    lines = [
        f"delta: {delta}",
        f"reward: {reward}",
        f"kl: {kl}",
        f"loss_before: {loss_before}",
        f"loss_after: {loss_after}",
    ]
    if args.shard_id:
        lines.append(f"shard_id: {args.shard_id}")
    if args.resource_class:
        lines.append(f"resource_class: {args.resource_class}")
    lines.append("")
    output.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
