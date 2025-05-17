import argparse
import os
import subprocess
import threading
from pathlib import Path
from typing import List
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "mscoco_captions_sample.txt"


def save_plot(vals: List[float], path: Path) -> None:
    width = 200
    height = 200
    img = [[255, 255, 255] * width for _ in range(height)]
    if not vals:
        return
    vmin, vmax = min(vals), max(vals)
    denom = vmax - vmin if vmax != vmin else 1
    for i, v in enumerate(vals):
        x = int(i / (len(vals) - 1 or 1) * (width - 1))
        y = int((1 - (v - vmin) / denom) * (height - 1))
        if 0 <= y < height:
            img[y][x * 3 : x * 3 + 3] = [255, 0, 0]
    raw = b"".join(b"\x00" + bytes(row) for row in img)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(raw, 9)),
            chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(png)


def worker(node: int, rnd: int, deltas: List[Path], tmp: Path) -> None:
    skill = "language"
    env = os.environ.copy()
    env["WU_ID"] = f"{rnd}-{node}"
    env["SKILL"] = skill
    node_dir = tmp / f"n{node}_r{rnd}"
    node_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "python", "-m", "server.generate_wu",
        "--skill", skill,
        "--data", str(DATA),
        "--out", str(node_dir),
    ], check=True, env=env)
    weights = node_dir / "init_weights.txt"
    delta_file = node_dir / "delta.json"
    subprocess.run([
        "python", "-m", f"server.apps.{skill}.train_local",
        "--weights", str(weights),
        "--data", str(DATA),
        "--output", str(delta_file),
        "--steps", "1",
    ], check=True, env=env)
    deltas.append(delta_file)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=int, default=5)
    parser.add_argument("--rounds", type=int, default=3)
    args = parser.parse_args()

    tmp = Path("sim_tmp")
    tmp.mkdir(exist_ok=True)
    weights_over_time = []

    for rnd in range(args.rounds):
        deltas: List[Path] = []
        threads = [
            threading.Thread(target=worker, args=(n, rnd, deltas, tmp))
            for n in range(args.nodes)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        result = subprocess.run(
            ["python", "-m", "server.fed_avg", *[str(d) for d in deltas]],
            capture_output=True,
            text=True,
            check=True,
        )
        out = result.stdout + result.stderr
        line = out.strip().split("=")[-1]
        weights_over_time.append(float(line))

    save_plot(weights_over_time, Path("sim.png"))


if __name__ == "__main__":
    main()
