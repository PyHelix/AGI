#!/usr/bin/env python3
"""Download model weights using a pre-signed S3 URL."""
import argparse
import requests
from pathlib import Path


def fetch(url: str, out: Path) -> None:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    out.write_bytes(resp.content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch weights from S3")
    parser.add_argument("--url", required=True, help="Signed S3 URL")
    parser.add_argument("--output", required=True, help="Destination file")
    args = parser.parse_args()

    out_path = Path(args.output)
    fetch(args.url, out_path)
    print(f"Downloaded weights to {out_path}")


if __name__ == "__main__":
    main()
