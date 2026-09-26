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


def analyze_frame(raw_path):

    # ---------------------------------------------------------
    # Read RAW + metadata
    # ---------------------------------------------------------

    raw = read_raw(
        raw_path,
        width=WIDTH,
        height=HEIGHT,
        bayer_pattern=BAYER_PATTERN,
        load_metadata=True,
    )

    # ---------------------------------------------------------
    # Extract Bayer channels
    # ---------------------------------------------------------

    channels = extract_bayer_channels(
        raw.data,
        raw.bayer_pattern,
    )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    metadata = raw.metadata

    if metadata is None:
        raise ValueError(
            f"No metadata found for {raw_path}"
        )

    # ---------------------------------------------------------
    # Low-end statistics
    # ---------------------------------------------------------

    return {
        "frame": raw_path.name,

        "exposure_time":
            metadata["exposure_time"],

        "analog_gain":
            metadata["analog_gain"],

        "normalized_exposure_s":
            metadata["normalized_exposure_s"],

        "R_p01":
            float(np.percentile(channels.R, 0.1)),

        "G1_p01":
            float(np.percentile(channels.G1, 0.1)),

        "G2_p01":
            float(np.percentile(channels.G2, 0.1)),

        "B_p01":
            float(np.percentile(channels.B, 0.1)),
    }


def main():

    dataset_dir = (
        DATASET_ROOT / "field_3_cameras"
    )

    raw_files = sorted(
        dataset_dir.glob("*.plain16")
    )

    print("=" * 100)
    print("BLACK-LEVEL / LOW-END vs CAMERA METADATA")
    print("=" * 100)

    print(f"Frames: {len(raw_files)}")

    results = []

    for index, raw_path in enumerate(
        raw_files,
        start=1,
    ):

        result = analyze_frame(raw_path)

        results.append(result)

        if index % 25 == 0 or index == len(raw_files):

            print(
                f"Processed "
                f"{index}/{len(raw_files)}"
            )

    # ---------------------------------------------------------
    # Sort by analog gain
    # ---------------------------------------------------------

    results.sort(
        key=lambda x: (
            x["analog_gain"],
            x["exposure_time"],
        )
    )

    # ---------------------------------------------------------
    # Print results
    # ---------------------------------------------------------

    print("\n")
    print(
        f"{'Frame':<42}"
        f"{'Gain':>8}"
        f"{'Exposure':>12}"
        f"{'NormExp':>12}"
        f"{'R':>8}"
        f"{'G1':>8}"
        f"{'G2':>8}"
        f"{'B':>8}"
    )

    print("-" * 106)

    for r in results:

        print(
            f"{r['frame']:<42}"
            f"{r['analog_gain']:>8.3f}"
            f"{r['exposure_time']:>12.6f}"
            f"{r['normalized_exposure_s']:>12.6f}"
            f"{r['R_p01']:>8.2f}"
            f"{r['G1_p01']:>8.2f}"
            f"{r['G2_p01']:>8.2f}"
            f"{r['B_p01']:>8.2f}"
        )


if __name__ == "__main__":
    main()
