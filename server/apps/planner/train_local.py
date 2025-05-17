import argparse
from pathlib import Path

from server.apps.common.train_utils import ppo_loop


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
    output.write_text(
        f"delta: {delta}\nreward: {reward}\nkl: {kl}\nloss_before: {loss_before}\nloss_after: {loss_after}\n"
    )


if __name__ == "__main__":
    main()
