#!/usr/bin/env python3

from pathlib import Path
import argparse
import numpy as np


def inspect_white_point(path: Path):

    print("=" * 70)
    print("INTEL-TAU WHITE POINT (.WP) INSPECTION")
    print("=" * 70)

    if not path.exists():
        raise FileNotFoundError(
            f"White-point file does not exist:\n{path}"
        )

    file_size = path.stat().st_size

    print(f"\nFile:")
    print(f"  {path}")

    print("\nFile size:")
    print(f"  {file_size} bytes")

    # --------------------------------------------------
    # Read raw bytes
    # --------------------------------------------------

    data = path.read_bytes()

    print("\nRaw bytes:")
    print(data)

    print("\nHex:")
    print(data.hex(" "))

    # --------------------------------------------------
    # Try text interpretation
    # --------------------------------------------------

    print("\nUTF-8 interpretation:")

    try:
        text = data.decode("utf-8")
        print(text)
    except UnicodeDecodeError:
        print("  Not valid UTF-8 text.")

    # --------------------------------------------------
    # Interpret as float64
    # --------------------------------------------------

    if file_size % 8 == 0:

        values = np.fromfile(
            path,
            dtype=np.float64
        )

        print("\nfloat64 interpretation:")

        print(f"  Number of values : {len(values)}")

        for i, value in enumerate(values):
            print(
                f"  [{i}] : {value:.12g}"
            )

    else:

        print(
            "\nFile size is not divisible by 8; "
            "cannot interpret entire file as float64."
        )


def main():

    parser = argparse.ArgumentParser(
        description="Inspect INTEL-TAU .wp white-point file"
    )

    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="Path to .wp file"
    )

    args = parser.parse_args()

    inspect_white_point(
        args.file
    )


if __name__ == "__main__":
    main()
