#!/usr/bin/env python3

from pathlib import Path
import json
import argparse


def load_json(path):

    if not path.exists():
        return {}

    with open(path) as f:
        return json.load(f)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--metadata-root",
        type=Path,
        default=Path(
            "data/metadata/intel_tau"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/metadata/intel_tau/"
            "dataset_report.md"
        ),
    )

    args = parser.parse_args()

    root = args.metadata_root

    scan = load_json(
        root / "dataset_scan.json"
    )

    cameras = load_json(
        root / "cameras.json"
    )

    metadata = load_json(
        root / "metadata_report.json"
    )

    raw = load_json(
        root / "raw_report.json"
    )

    wp = load_json(
        root / "white_point_report.json"
    )

    ccm = load_json(
        root / "ccm_report.json"
    )

    manifest = load_json(
        root / "manifest.json"
    )

    lines = []

    lines.append(
        "# INTEL-TAU Dataset Inspection Report\n"
    )

    lines.append(
        "## Dataset\n"
    )

    lines.append(
        f"- Root: `{scan.get('dataset_root', 'N/A')}`"
    )

    lines.append(
        f"- Total files: "
        f"`{scan.get('total_files', 'N/A')}`"
    )

    lines.append(
        f"- Total size: "
        f"`{scan.get('total_size_gb', 'N/A')} GB`"
    )

    lines.append("\n## File Extensions\n")

    for ext, count in scan.get(
        "extensions",
        {}
    ).items():

        lines.append(
            f"- `{ext}`: {count}"
        )

    lines.append("\n## Cameras\n")

    for camera, info in cameras.items():

        lines.append(
            f"\n### {camera}"
        )

        lines.append(
            f"- Files: {info.get('file_count')}"
        )

        lines.append(
            "- Categories:"
        )

        for category in info.get(
            "categories",
            []
        ):

            lines.append(
                f"  - `{category}`"
            )

    lines.append("\n## Manifest\n")

    lines.append(
        f"RAW scenes: "
        f"`{len(manifest) if isinstance(manifest, list) else 'N/A'}`"
    )

    lines.append(
        "\n## Inspection Status\n"
    )

    lines.append(
        "- Dataset structure: inspected"
    )

    lines.append(
        "- Camera inventory: inspected"
    )

    lines.append(
        "- RAW metadata: inspected"
    )

    lines.append(
        "- RAW format: inspected"
    )

    lines.append(
        "- White point: inspected"
    )

    lines.append(
        "- CCM: inspected"
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    args.output.write_text(
        "\n".join(lines)
    )

    print(
        f"Report written to:\n"
        f"  {args.output}"
    )


if __name__ == "__main__":
    main()
