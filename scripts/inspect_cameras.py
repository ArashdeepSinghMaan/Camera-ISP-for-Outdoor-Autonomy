#!/usr/bin/env python3

from pathlib import Path
import argparse
import json


KNOWN_CAMERA_NAMES = {
    "Canon_5DSR",
    "Nikon_D810",
    "Sony_IMX135",
    "Sony_IMX135_BLCCSC",
}


def inspect_camera(root: Path):

    result = {}

    for camera_dir in sorted(root.iterdir()):

        if not camera_dir.is_dir():
            continue

        camera_name = camera_dir.name

        categories = []

        for child in sorted(camera_dir.iterdir()):

            if child.is_dir():
                categories.append(child.name)

        files = [
            p for p in camera_dir.rglob("*")
            if p.is_file()
        ]

        extension_counts = {}

        for path in files:

            ext = path.suffix.lower()

            if ext:
                extension_counts[ext] = (
                    extension_counts.get(ext, 0) + 1
                )

        result[camera_name] = {
            "path": str(camera_dir.resolve()),
            "categories": categories,
            "file_count": len(files),
            "extensions": extension_counts,
        }

    return result


def print_report(report):

    print("=" * 70)
    print("CAMERA / SCENE INVENTORY")
    print("=" * 70)

    for camera, info in report.items():

        print(f"\nCamera: {camera}")

        print("  Categories:")

        for category in info["categories"]:
            print(f"    - {category}")

        print(
            f"  Files: {info['file_count']}"
        )

        print("  Extensions:")

        for ext, count in sorted(
            info["extensions"].items()
        ):
            print(
                f"    {ext:12s} {count}"
            )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/metadata/intel_tau/cameras.json"
        ),
    )

    args = parser.parse_args()

    report = inspect_camera(args.root)

    print_report(report)

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(args.output, "w") as f:

        json.dump(
            report,
            f,
            indent=2
        )

    print(
        f"\nSaved:\n  {args.output}"
    )


if __name__ == "__main__":
    main()
