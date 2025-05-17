import hashlib
import sys
from pathlib import Path


def validate(delta_path: Path) -> float:
    if not delta_path.exists():
        return 0.0
    lines = delta_path.read_text().splitlines()
    content_hash = hashlib.sha256(delta_path.read_bytes()).hexdigest()
    sha_line = next((line for line in lines if line.startswith('sha256:')), None)
    reward_line = next((line for line in lines if line.startswith('reward:')), None)
    kl_line = next((line for line in lines if line.startswith('kl:')), 'kl:0')

    if not reward_line:
        return 0.0
    reward = float(reward_line.split(':', 1)[1].strip())
    if reward < 0.6:
        return 0.0

    file_hash = sha_line.split(':', 1)[1].strip() if sha_line else ''
    if sha_line and file_hash != content_hash:
        return 0.0

    kl = float(kl_line.split(':', 1)[1].strip())
    return reward - kl


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
