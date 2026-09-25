from pathlib import Path
from collections import Counter
import json


def scan_dataset(root: Path):
    print("=" * 70)
    print("INTEL-TAU DATASET INSPECTION")
    print("=" * 70)

    if not root.exists():
        raise FileNotFoundError(f"Dataset does not exist: {root}")

    print(f"\nDataset root:")
    print(f"  {root}")

    files = list(root.rglob("*"))

    files = [p for p in files if p.is_file()]

    print(f"\nTotal files found: {len(files)}")

    extensions = Counter(
        p.suffix.lower()
        for p in files
        if p.suffix
    )

    print("\nFile extensions:")
    for ext, count in sorted(extensions.items()):
        print(f"  {ext:12s} {count}")

    directories = sorted(
        p for p in root.iterdir()
        if p.is_dir()
    )

    print("\nTop-level directories:")

    for directory in directories:
        print(f"  {directory.name}")

    return {
        "root": str(root),
        "total_files": len(files),
        "extensions": dict(extensions),
        "top_level_directories": [
            d.name for d in directories
        ],
    }


def main():

    import argparse

    parser = argparse.ArgumentParser(
        description="Inspect INTEL-TAU dataset structure"
    )

    parser.add_argument(
        "--root",
        required=True,
        type=Path,
        help="Path to INTEL-TAU dataset root"
    )

    parser.add_argument(
        "--output",
        default="data/metadata/intel_tau_scan.json",
        type=Path,
        help="Output JSON report"
    )

    args = parser.parse_args()

    report = scan_dataset(args.root)

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

    print(f"\nReport written to:")
    print(f"  {args.output}")


if __name__ == "__main__":
    main()
