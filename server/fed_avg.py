import sys
from pathlib import Path


def aggregate(delta_paths):
    # Placeholder aggregator: just average numbers from delta files
    totals = []
    for p in delta_paths:
        with open(p) as f:
            for line in f:
                if line.startswith("delta:"):
                    val = float(line.split(":",1)[1].strip())
                    totals.append(val)
    if not totals:
        return 0.0
    return sum(totals) / len(totals)


def main():
    deltas = [Path(p) for p in sys.argv[1:]]
    new_weight = aggregate(deltas)
    print(f"new_weight={new_weight}")


if __name__ == "__main__":
    main()