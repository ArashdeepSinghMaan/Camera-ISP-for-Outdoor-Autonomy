#!/usr/bin/env python3

from pathlib import Path
import argparse


def inspect_meta(path: Path):

    print("=" * 70)
    print("INTEL-TAU .META FILE INSPECTION")
    print("=" * 70)

    if not path.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist:\n{path}"
        )

    print(f"\nFile:")
    print(f"  {path}")

    print(
        f"\nFile size:"
        f"\n  {path.stat().st_size} bytes"
    )

    # ------------------------------------------------------------
    # Read raw bytes
    # ------------------------------------------------------------

    data = path.read_bytes()

    print("\nFirst 128 bytes:")

    print(data[:128])

    print("\nHex dump:")

    print(
        data[:128].hex(" ")
    )

    # ------------------------------------------------------------
    # Try text representation
    # ------------------------------------------------------------

    print("\nUTF-8 interpretation:")

    try:

        text = data.decode(
            "utf-8"
        )

        print(text)

    except UnicodeDecodeError as e:

        print(
            "Not valid UTF-8."
        )

        print(
            f"Decode error: {e}"
        )


def main():

    parser = argparse.ArgumentParser(
        description="Inspect INTEL-TAU .meta file"
    )

    parser.add_argument(
        "--file",
        required=True,
        type=Path,
    )

    args = parser.parse_args()

    inspect_meta(
        args.file
    )


if __name__ == "__main__":
    main()
