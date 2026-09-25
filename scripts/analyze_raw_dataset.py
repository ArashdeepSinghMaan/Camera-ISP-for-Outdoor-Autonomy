#!/usr/bin/env python3

from pathlib import Path
import argparse
import json

import numpy as np


RAW_WIDTH = 3264
RAW_HEIGHT = 2448
RAW_DTYPE = np.uint16
BLACK_LEVEL = 64
SATURATION_LEVEL = 1023


def analyze_raw(path: Path):

    expected_pixels = RAW_WIDTH * RAW_HEIGHT
    expected_bytes = expected_pixels * 2

    file_size = path.stat().st_size

    if file_size != expected_bytes:
        raise ValueError(
            f"Invalid RAW size: {path}\n"
            f"Expected: {expected_bytes}\n"
            f"Found:    {file_size}"
        )

    raw = np.fromfile(
        path,
        dtype=RAW_DTYPE,
    )

    if raw.size != expected_pixels:
        raise ValueError(
            f"Invalid RAW pixel count: {path}\n"
            f"Expected: {expected_pixels}\n"
            f"Found:    {raw.size}"
        )

    values = raw.astype(np.float64)

    percentiles = np.percentile(
        values,
        [
            0,
            1,
            5,
            25,
            50,
            75,
            95,
            99,
            99.9,
            100,
        ],
    )

    below_black = np.count_nonzero(
        raw < BLACK_LEVEL
    )

    saturated = np.count_nonzero(
        raw >= SATURATION_LEVEL
    )

    return {
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "std": float(values.std()),

        "p0": float(percentiles[0]),
        "p1": float(percentiles[1]),
        "p5": float(percentiles[2]),
        "p25": float(percentiles[3]),
        "p50": float(percentiles[4]),
        "p75": float(percentiles[5]),
        "p95": float(percentiles[6]),
        "p99": float(percentiles[7]),
        "p99_9": float(percentiles[8]),
        "p100": float(percentiles[9]),

        "pixels_below_black_level": int(
            below_black
        ),

        "percent_pixels_below_black_level": float(
            100.0 * below_black / raw.size
        ),

        "pixels_saturated": int(
            saturated
        ),

        "percent_pixels_saturated": float(
            100.0 * saturated / raw.size
        ),
    }


def summarize_frame_statistics(records):

    fields = [
        "min",
        "max",
        "mean",
        "median",
        "std",
        "p0",
        "p1",
        "p5",
        "p25",
        "p50",
        "p75",
        "p95",
        "p99",
        "p99_9",
        "p100",
        "pixels_below_black_level",
        "percent_pixels_below_black_level",
        "pixels_saturated",
        "percent_pixels_saturated",
    ]

    summary = {}

    for field in fields:

        values = np.asarray(
            [
                record[field]
                for record in records
            ],
            dtype=np.float64,
        )

        summary[field] = {
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "median": float(np.median(values)),
            "std": float(values.std()),
        }

    return summary


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Dataset-wide RAW signal "
            "characterization"
        )
    )

    parser.add_argument(
        "--root",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/metadata/intel_tau/"
            "raw_statistics.json"
        ),
    )

    args = parser.parse_args()

    raw_files = sorted(
        args.root.rglob("*.plain16")
    )

    print("=" * 70)
    print("INTEL-TAU RAW DATASET ANALYSIS")
    print("=" * 70)

    print(
        f"\nRAW files found: {len(raw_files)}"
    )

    records = []

    for index, path in enumerate(
        raw_files,
        start=1,
    ):

        print(
            f"\rProcessing "
            f"{index}/{len(raw_files)}: "
            f"{path.name}",
            end="",
            flush=True,
        )

        stats = analyze_raw(path)

        records.append(
            {
                "scene_id": path.stem,
                "path": str(path.resolve()),
                **stats,
            }
        )

    print("\n")

    summary = summarize_frame_statistics(
        records
    )

    output = {
        "dataset": {
            "root": str(
                args.root.resolve()
            ),
            "frame_count": len(records),
            "width": RAW_WIDTH,
            "height": RAW_HEIGHT,
            "dtype": "uint16",
            "black_level_reference": BLACK_LEVEL,
            "saturation_level": SATURATION_LEVEL,
        },
        "summary": summary,
        "frames": records,
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        args.output,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
        )

    print("=" * 70)
    print("DATASET RAW SUMMARY")
    print("=" * 70)

    important_fields = [
        "min",
        "max",
        "mean",
        "median",
        "std",
        "p1",
        "p5",
        "p95",
        "p99",
        "p99_9",
        "percent_pixels_below_black_level",
        "percent_pixels_saturated",
    ]

    for field in important_fields:

        stats = summary[field]

        print(f"\n{field}")

        print(
            f"  min    : {stats['min']:.6f}"
        )

        print(
            f"  max    : {stats['max']:.6f}"
        )

        print(
            f"  mean   : {stats['mean']:.6f}"
        )

        print(
            f"  median : {stats['median']:.6f}"
        )

        print(
            f"  std    : {stats['std']:.6f}"
        )

    print("\n" + "=" * 70)

    print(
        f"Saved:\n"
        f"  {args.output}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
