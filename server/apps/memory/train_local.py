import argparse
from pathlib import Path


def ppo_train(weights: Path, data: Path, steps: int, lr: float):
    """Placeholder PPO loop with 4-bit LoRA.
    This does not implement real training but simulates updates."""
    delta = 0.0
    reward = 0.0
    for _ in range(steps):
        # Fake optimization step
        delta += 0.01 * lr
        reward += 0.1
    reward /= steps
    return delta, reward


def main():
    parser = argparse.ArgumentParser(description="Local fine-tuning with PPO and LoRA")
    parser.add_argument("--weights", required=True, help="Initial model weights")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--output", required=True, help="Output file for weight deltas")
    parser.add_argument("--steps", type=int, default=100, help="Training steps")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    delta, reward = ppo_train(Path(args.weights), Path(args.data), args.steps, args.lr)
    output = Path(args.output)
    output.write_text(f"delta: {delta}\nreward: {reward}\n")


if __name__ == "__main__":
    main()
