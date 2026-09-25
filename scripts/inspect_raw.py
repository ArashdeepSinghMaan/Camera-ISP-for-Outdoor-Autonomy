#!/usr/bin/env python3

from pathlib import Path
import argparse
import numpy as np


def print_percentiles(raw):

    percentiles = [
        0,
        0.1,
        1,
        5,
        25,
        50,
        75,
        95,
        99,
        99.9,
        100,
    ]

    values = np.percentile(
        raw,
        percentiles
    )

    print("\nPercentiles:")

    for p, value in zip(
        percentiles,
        values
    ):
        print(
            f"  {p:>5}% : {value:.3f}"
        )


def inspect_raw(
    path: Path,
    width: int,
    height: int,
):

    print("=" * 70)
    print("RAW IMAGE INSPECTION")
    print("=" * 70)

    if not path.exists():
        raise FileNotFoundError(
            f"RAW file does not exist:\n{path}"
        )

    file_size = path.stat().st_size

    print(f"\nFile:")
    print(f"  {path}")

    print(f"\nFile size:")
    print(f"  {file_size:,} bytes")

    expected_pixels = width * height
    expected_bytes = expected_pixels * 2

    print("\nExpected format:")
    print(f"  Width          : {width}")
    print(f"  Height         : {height}")
    print(f"  Pixels         : {expected_pixels:,}")
    print(f"  Bytes/pixel    : 2")
    print(f"  Expected bytes : {expected_bytes:,}")

    print("\nFile-size check:")

    if file_size == expected_bytes:
        print("  PASS")
    else:
        print("  FAIL")
        print(
            f"  Difference: "
            f"{file_size - expected_bytes:+,} bytes"
        )

    # ------------------------------------------------------------
    # Read RAW
    # ------------------------------------------------------------

    raw = np.fromfile(
        path,
        dtype=np.uint16
    )

    print("\nLoaded RAW:")
    print(f"  dtype       : {raw.dtype}")
    print(f"  elements    : {raw.size:,}")
    print(
        f"  expected    : {expected_pixels:,}"
    )

    if raw.size != expected_pixels:
        raise ValueError(
            "\nRAW dimensions do not match "
            "the supplied width/height."
        )

    raw = raw.reshape(
        height,
        width
    )

    print("\nReshaped RAW:")
    print(f"  shape       : {raw.shape}")
    print(f"  dtype       : {raw.dtype}")

    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    print("\nBasic statistics:")

    print(
        f"  min         : {raw.min()}"
    )

    print(
        f"  max         : {raw.max()}"
    )

    print(
        f"  mean        : {raw.mean():.3f}"
    )

    print(
        f"  median      : {np.median(raw):.3f}"
    )

    print(
        f"  std         : {raw.std():.3f}"
    )

    print_percentiles(raw)

    return raw


def main():

    parser = argparse.ArgumentParser(
        description="Inspect INTEL-TAU .plain16 RAW data"
    )

    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="Path to .plain16 file"
    )

    parser.add_argument(
        "--width",
        required=True,
        type=int,
        help="RAW width"
    )

    parser.add_argument(
        "--height",
        required=True,
        type=int,
        help="RAW height"
    )

    args = parser.parse_args()

    inspect_raw(
        args.file,
        args.width,
        args.height
    )


if __name__ == "__main__":
    main()
