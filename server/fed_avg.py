import sys
from pathlib import Path


def aggregate(delta_paths):
    # Aggregate weight deltas from worker results. Each delta may include a
    # reward score which is used as a weight when averaging. This allows nodes
    # that produced better updates to influence the new weight more strongly.
    weighted = []
    for p in delta_paths:
        delta = None
        reward = 1.0
        with open(p) as f:
            for line in f:
                if line.startswith("delta:"):
                    delta = float(line.split(":", 1)[1].strip())
                elif line.startswith("reward:"):
                    reward = float(line.split(":", 1)[1].strip())
        if delta is not None:
            weighted.append((delta, reward))

    if not weighted:
        return 0.0

    total_reward = sum(r for _, r in weighted)
    if total_reward == 0:
        # Avoid divide-by-zero; fall back to simple average
        return sum(d for d, _ in weighted) / len(weighted)

    return sum(d * r for d, r in weighted) / total_reward


def main():
    deltas = [Path(p) for p in sys.argv[1:]]
    new_weight = aggregate(deltas)
    print(f"new_weight={new_weight}")


if __name__ == "__main__":
    main()