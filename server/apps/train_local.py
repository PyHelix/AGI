import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Simple local fine-tuning script")
    parser.add_argument("--weights", required=True, help="Initial model weights")
    parser.add_argument("--data", required=True, help="Training data chunk")
    parser.add_argument("--output", required=True, help="Output file for weight deltas")
    args = parser.parse_args()

    # In a real setup you would load the model and perform fine-tuning here.
    # This example only writes a placeholder delta and reward.
    output = Path(args.output)
    output.write_text("delta: 0\nreward: 0.0\n")


if __name__ == "__main__":
    main()