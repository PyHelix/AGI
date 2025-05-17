import argparse
import json
from pathlib import Path

from server.apps.common.train_utils import ppo_loop
from aginet.log import get_logger

log = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Local fine-tuning with PPO and LoRA")
    parser.add_argument("--weights", required=True, help="Initial model weights")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--output", required=True, help="Output file for weight deltas")
    parser.add_argument("--steps", type=int, default=100, help="Training steps")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    delta, reward, kl, loss_before, loss_after = ppo_loop(
        Path(args.weights), Path(args.data), args.steps, args.lr
    )
    output = Path(args.output)
    data = {
        "w": delta,
        "reward": reward,
        "kl": kl,
        "loss_before": loss_before,
        "loss_after": loss_after,
        "version": "0.2",
    }
    output.write_text(json.dumps(data))
    log.info("wrote delta to %s", output)


if __name__ == "__main__":
    main()
