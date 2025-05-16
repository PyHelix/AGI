import hashlib
import sys
from pathlib import Path


def validate(delta_path: Path) -> float:
    # TODO: add real evaluation. For now accept everything with reward 1.0
    if not delta_path.exists():
        return 0.0
    return 1.0


def main():
    delta_file = Path(sys.argv[1])
    score = validate(delta_file)
    if score > 0:
        print(f"ACCEPT {score}")
        sys.exit(0)
    else:
        print("REJECT")
        sys.exit(1)


if __name__ == "__main__":
    main()