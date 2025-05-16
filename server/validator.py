import sys
from pathlib import Path


def validate(delta_path: Path) -> float:
    # Very small placeholder validation. We read the reward value from the file
    # and accept updates that score above the threshold.
    if not delta_path.exists():
        return 0.0

    reward = 0.0
    with open(delta_path) as f:
        for line in f:
            if line.startswith("reward:"):
                reward = float(line.split(":", 1)[1].strip())
                break

    return reward


def main():
    delta_file = Path(sys.argv[1])
    score = validate(delta_file)
    if score >= 0.5:
        print(f"ACCEPT {score}")
        sys.exit(0)
    else:
        print("REJECT")
        sys.exit(1)


if __name__ == "__main__":
    main()