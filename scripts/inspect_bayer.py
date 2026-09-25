#!/usr/bin/env python3

from pathlib import Path
import argparse
import numpy as np


BAYER_PATTERNS = {
    "RGGB": {
        "R":  (0, 0),
        "G1": (0, 1),
        "G2": (1, 0),
        "B":  (1, 1),
    },

    "BGGR": {
        "B":  (0, 0),
        "G1": (0, 1),
        "G2": (1, 0),
        "R":  (1, 1),
    },

    "GRBG": {
        "G1": (0, 0),
        "R":  (0, 1),
        "B":  (1, 0),
        "G2": (1, 1),
    },

    "GBRG": {
        "G1": (0, 0),
        "B":  (0, 1),
        "R":  (1, 0),
        "G2": (1, 1),
    },
}


def inspect_channels(
    raw,
    pattern
):

    pattern = pattern.upper()

    if pattern not in BAYER_PATTERNS:
        raise ValueError(
            f"Unsupported Bayer pattern: {pattern}"
        )

    positions = BAYER_PATTERNS[pattern]

    print("=" * 70)
    print("BAYER CHANNEL INSPECTION")
    print("=" * 70)

    print(f"\nPattern: {pattern}")

    for channel, (
        row,
        col
    ) in positions.items():

        values = raw[
            row::2,
            col::2
        ]

        print(
            f"\n{channel}"
        )

        print(
            f"  shape  : {values.shape}"
        )

        print(
            f"  min    : {values.min()}"
        )

        print(
            f"  max    : {values.max()}"
        )

        print(
            f"  mean   : {values.mean():.3f}"
        )

        print(
            f"  median : {np.median(values):.3f}"
        )

        print(
            f"  std    : {values.std():.3f}"
        )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--width",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--height",
        required=True,
        type=int,
    )

    parser.add_argument(
        "--pattern",
        required=True,
        choices=[
            "RGGB",
            "BGGR",
            "GRBG",
            "GBRG",
        ],
    )

    args = parser.parse_args()

    raw = np.fromfile(
        args.file,
        dtype=np.uint16
    )

    raw = raw.reshape(
        args.height,
        args.width
    )

    inspect_channels(
        raw,
        args.pattern
    )


if __name__ == "__main__":
    main()
