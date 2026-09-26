#!/usr/bin/env python3

from pathlib import Path

import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.raw.bayer import extract_bayer_channels


DATASET_ROOT = Path(
    "/media/hitech/WD_Access/Camera_ISP/Sony_IMX135"
)

WIDTH = 3264
HEIGHT = 2448
BAYER_PATTERN = "GRBG"

PERCENTILES = [0, 0.01, 0.1, 0.5, 1, 2, 5]


def analyze_frame(raw_path):

    raw = read_raw(
        raw_path,
        width=WIDTH,
        height=HEIGHT,
        bayer_pattern=BAYER_PATTERN,
        load_metadata=False,
    )

    channels = extract_bayer_channels(
        raw.data,
        raw.bayer_pattern,
    )

    result = {}

    for name, image in [
        ("R", channels.R),
        ("G1", channels.G1),
        ("G2", channels.G2),
        ("B", channels.B),
    ]:

        result[name] = [
            float(np.percentile(image, p))
            for p in PERCENTILES
        ]

    return result


def analyze_subset(subset_name, subset_dir):

    raw_files = sorted(subset_dir.glob("*.plain16"))

    print("\n" + "=" * 70)
    print(f"SUBSET: {subset_name}")
    print("=" * 70)

    print(f"Frames found: {len(raw_files)}")

    if not raw_files:
        print("No RAW files found.")
        return

    all_results = {
        "R": [],
        "G1": [],
        "G2": [],
        "B": [],
    }

    for index, raw_path in enumerate(raw_files, start=1):

        result = analyze_frame(raw_path)

        for channel in all_results:
            all_results[channel].append(
                result[channel]
            )

        if index % 25 == 0 or index == len(raw_files):
            print(
                f"Processed {index}/{len(raw_files)}"
            )

    print("\nAggregate statistics")
    print("--------------------")

    for channel in ["R", "G1", "G2", "B"]:

        values = np.asarray(
            all_results[channel],
            dtype=np.float64,
        )

        print(f"\n{channel}")

        for i, percentile in enumerate(PERCENTILES):

            frame_values = values[:, i]

            print(
                f"  p{percentile:<5}: "
                f"min={frame_values.min():8.3f}, "
                f"median={np.median(frame_values):8.3f}, "
                f"max={frame_values.max():8.3f}"
            )


def main():

    subsets = {
        "field_3_cameras":
            DATASET_ROOT / "field_3_cameras",

        "lab_printouts":
            DATASET_ROOT / "lab_printouts",

        "lab_realscene":
            DATASET_ROOT / "lab_realscene",
    }

    for name, directory in subsets.items():

        analyze_subset(
            name,
            directory,
        )


if __name__ == "__main__":
    main()
