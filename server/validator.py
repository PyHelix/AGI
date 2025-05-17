import hashlib
import json
import sys
from pathlib import Path

from aginet.log import get_logger

log = get_logger(__name__)


def validate(delta_path: Path) -> float:
    if not delta_path.exists():
        return 0.0
    text = delta_path.read_text()
    content_hash = hashlib.sha256(delta_path.read_bytes()).hexdigest()
    try:
        data = json.loads(text)
        reward = float(data.get('reward', 0))
        kl = float(data.get('kl', 0))
        loss_before = float(data.get('loss_before', 0))
        loss_after = float(data.get('loss_after', 0))
        file_hash = data.get('sha256', '')
    except json.JSONDecodeError:
        lines = text.splitlines()
        sha_line = next((l for l in lines if l.startswith('sha256:')), None)
        reward_line = next((l for l in lines if l.startswith('reward:')), None)
        kl_line = next((l for l in lines if l.startswith('kl:')), 'kl:0')
        before_line = next((l for l in lines if l.startswith('loss_before:')), 'loss_before:0')
        after_line = next((l for l in lines if l.startswith('loss_after:')), 'loss_after:0')
        if not reward_line:
            return 0.0
        reward = float(reward_line.split(':', 1)[1].strip())
        kl = float(kl_line.split(':', 1)[1].strip())
        loss_before = float(before_line.split(':', 1)[1].strip())
        loss_after = float(after_line.split(':', 1)[1].strip())
        file_hash = sha_line.split(':', 1)[1].strip() if sha_line else ''

    if reward < 0.6:
        return 0.0

    if file_hash and file_hash != content_hash:
        return 0.0
    return reward - kl - (loss_before - loss_after)


def main():
    delta_file = Path(sys.argv[1])
    score = validate(delta_file)
    if score > 0:
        log.info("ACCEPT %s", score)
        sys.exit(0)
    else:
        log.info("REJECT")
        sys.exit(1)


if __name__ == "__main__":
    main()
