#!/usr/bin/env python3

from pathlib import Path
import argparse
import numpy as np


def inspect_ccm(path: Path):

    print("=" * 70)
    print("INTEL-TAU COLOR CORRECTION MATRIX (.CCM) INSPECTION")
    print("=" * 70)

    if not path.exists():
        raise FileNotFoundError(
            f"CCM file does not exist:\n{path}"
        )

    file_size = path.stat().st_size

    print("\nFile:")
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
    # Try UTF-8 text
    # --------------------------------------------------

    print("\nUTF-8 interpretation:")

    try:
        text = data.decode("utf-8")
        print(text)
    except UnicodeDecodeError:
        print("  Not valid UTF-8 text.")
        text = None

    # --------------------------------------------------
    # Parse as text
    # --------------------------------------------------

    if text is not None:

        try:

            values = np.fromstring(
                text,
                sep=" "
            )

            print("\nParsed numeric values:")

            print(
                f"  Number of values : {len(values)}"
            )

            for i, value in enumerate(values):

                print(
                    f"  [{i}] : {value:.12g}"
                )

            if len(values) == 9:

                ccm = values.reshape(3, 3)

                print("\n3 × 3 CCM:")

                print(ccm)

            else:

                print(
                    "\nWARNING:"
                )

                print(
                    f"Expected 9 values, "
                    f"found {len(values)}."
                )

        except ValueError as e:

            print(
                "\nCould not parse text as numbers."
            )

            print(f"Error: {e}")


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Inspect INTEL-TAU .ccm "
            "color correction matrix"
        )
    )

    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="Path to .ccm file"
    )

    args = parser.parse_args()

    inspect_ccm(
        args.file
    )


if __name__ == "__main__":
    main()
