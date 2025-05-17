import json
import os
import sys
from pathlib import Path
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception:  # pragma: no cover - cryptography optional
    AESGCM = None

from aginet.log import get_logger

MOMENTUM = 0.9
STATE_FILE = Path("fedopt_state.json")
KEY_FILE = Path("project_keys/weights.key")
OUT_FILE = Path("global_weights.enc")
log = get_logger(__name__)


def encrypt_weight(value: float) -> None:
    if AESGCM is None:
        OUT_FILE.write_text(str(value))
        return
    key = bytes.fromhex(KEY_FILE.read_text().strip())
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, str(value).encode(), None)
    OUT_FILE.write_bytes(nonce + ct)


def aggregate(delta_paths):
    totals = []
    for p in delta_paths:
        text = p.read_text().strip()
        try:
            data = json.loads(text)
            val = float(data.get("w", 0.0))
        except json.JSONDecodeError:
            val = 0.0
            for line in text.splitlines():
                if line.startswith("delta:"):
                    val = float(line.split(":", 1)[1].strip())
                    break
        totals.append(val)
    if not totals:
        return 0.0
    return sum(totals) / len(totals)


def main():
    deltas = [Path(p) for p in sys.argv[1:]]
    delta_avg = aggregate(deltas)
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    else:
        state = {"v": 0.0, "weight": 0.0}

    v = MOMENTUM * state["v"] + delta_avg
    weight = state["weight"] + v
    state = {"v": v, "weight": weight}
    STATE_FILE.write_text(json.dumps(state))
    encrypt_weight(weight)
    log.info("new_weight=%s", weight)


if __name__ == "__main__":
    main()
