#!/usr/bin/env python3

from pathlib import Path

import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.isp.black_level import apply_black_level


DATASET = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras"
)

WIDTH = 3264
HEIGHT = 2448
BAYER_PATTERN = "GRBG"

OFFSET = 64.0


def main():

    raw_files = sorted(DATASET.glob("*.plain16"))

    print("Black-Level Offset Sweep")
    print("========================")
    print(f"Dataset : {DATASET}")
    print(f"Frames  : {len(raw_files)}")
    print(f"Offset  : {OFFSET}")
    print()

    clipped = []
    mean_before = []
    mean_after = []
    p01_before = []
    p01_after = []

    for raw_path in raw_files:

        image = read_raw(
            path=raw_path,
            width=WIDTH,
            height=HEIGHT,
            bayer_pattern=BAYER_PATTERN,
        )

        raw = image.data

        corrected = apply_black_level(
            raw,
            offset=OFFSET,
        )

        clip_fraction = (
            np.count_nonzero(corrected == 0.0)
            / corrected.size
            * 100.0
        )

        clipped.append(clip_fraction)

        mean_before.append(raw.mean())
        mean_after.append(corrected.mean())

        p01_before.append(np.percentile(raw, 0.1))
        p01_after.append(np.percentile(corrected, 0.1))

    clipped = np.asarray(clipped)
    mean_before = np.asarray(mean_before)
    mean_after = np.asarray(mean_after)
    p01_before = np.asarray(p01_before)
    p01_after = np.asarray(p01_after)

    print("Clipping statistics")
    print("-------------------")
    print(f"Minimum : {clipped.min():.6f}%")
    print(f"Median  : {np.median(clipped):.6f}%")
    print(f"Mean    : {clipped.mean():.6f}%")
    print(f"Maximum : {clipped.max():.6f}%")

    print("\nMean signal")
    print("-----------")
    print(f"Before median: {np.median(mean_before):.3f}")
    print(f"After median : {np.median(mean_after):.3f}")

    print("\nP0.1 signal")
    print("-----------")
    print(f"Before median: {np.median(p01_before):.3f}")
    print(f"After median : {np.median(p01_after):.3f}")

    print("\nFrames with >1% pixels clipped:")

    count = np.count_nonzero(clipped > 1.0)

    print(count)

    print("\nFrames with >5% pixels clipped:")

    count = np.count_nonzero(clipped > 5.0)

    print(count)

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
