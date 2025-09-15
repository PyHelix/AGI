import argparse
from pathlib import Path


def _read_float(path: Path) -> float:
    """Return the first float value stored in ``path``.

    Training scripts emit metric files containing multiple ``key: value``
    pairs (see ``server/apps/*/train_local.py``).  The previous
    implementation assumed the file only contained a raw floating point
    number, which meant the simulated volunteer could not apply the
    aggregated update it just produced.  To make the pipeline compatible
    with the generated files we look for a ``delta`` key while still
    supporting legacy files that only contain the numeric value.
    """

    text = path.read_text().strip()
    if not text:
        raise ValueError(f"{path} is empty")

    # Fast path for legacy files that only contain a float.
    try:
        return float(text)
    except ValueError:
        pass

    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() == "delta":
            return float(value.strip())

    raise ValueError(f"delta value not found in {path}")


def apply_delta(weight_file: Path, delta_file: Path, out_file: Path) -> None:
    weight = _read_float(weight_file)
    delta = _read_float(delta_file)
    out_file.write_text(str(weight + delta))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weight", required=True)
    parser.add_argument("--delta", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    apply_delta(Path(args.weight), Path(args.delta), Path(args.out))


if __name__ == "__main__":
    main()
