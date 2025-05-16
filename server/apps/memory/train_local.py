import argparse
import random
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Simple local fine-tuning script")
    parser.add_argument("--weights", required=True, help="Initial model weights")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--output", required=True, help="Output file for weight deltas")
    args = parser.parse_args()

    # In a real setup you would load the model and perform fine-tuning here.
    # This example simulates training by generating a random weight delta in
    # the range [-1, 1] and a reward between 0 and 1. Larger absolute deltas
    # receive lower reward so the aggregator can weight them accordingly.
    delta = random.uniform(-1.0, 1.0)
    reward = max(0.0, 1.0 - abs(delta))

    output = Path(args.output)
    output.write_text(f"delta: {delta}\nreward: {reward}\n")


if __name__ == "__main__":
    main()