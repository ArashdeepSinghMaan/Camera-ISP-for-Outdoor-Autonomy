#!/usr/bin/env python3

from pathlib import Path

import cv2
import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.isp.demosaic import demosaic_bilinear


RAW_PATH = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)


def main():

    print("Demosaicing Difference Analysis")
    print("===============================")

    raw_image = read_raw(
        path=RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    )

    raw = raw_image.data

    ours = demosaic_bilinear(
        raw,
        "GRBG",
    )

    reference = cv2.cvtColor(
        raw,
        cv2.COLOR_BayerGRBG2RGB,
    ).astype(np.float32)

    difference = np.abs(
        ours - reference
    )

    # ---------------------------------------------------------
    # Global statistics
    # ---------------------------------------------------------

    print("\nGlobal difference")
    print("-----------------")

    print(
        f"Mean   : {difference.mean():.6f}"
    )

    print(
        f"Median : {np.median(difference):.6f}"
    )

    print(
        f"Maximum: {difference.max():.6f}"
    )

    for percentile in [90, 95, 99, 99.9, 99.99]:

        print(
            f"P{percentile:<5}: "
            f"{np.percentile(difference, percentile):.6f}"
        )

    # ---------------------------------------------------------
    # Difference thresholds
    # ---------------------------------------------------------

    print("\nPixels above thresholds")
    print("-----------------------")

    total = difference.size

    for threshold in [0, 1, 2, 5, 10, 20, 50, 100]:

        count = np.count_nonzero(
            difference > threshold
        )

        percentage = (
            count / total * 100.0
        )

        print(
            f">{threshold:3d} DN : "
            f"{count:10d} pixels "
            f"({percentage:.6f}%)"
        )

    # ---------------------------------------------------------
    # Per-channel statistics
    # ---------------------------------------------------------

    print("\nPer-channel difference")
    print("----------------------")

    channel_names = ["R", "G", "B"]

    for channel, name in enumerate(channel_names):

        diff = difference[:, :, channel]

        print(
            f"{name}: "
            f"mean={diff.mean():.6f}, "
            f"median={np.median(diff):.6f}, "
            f"max={diff.max():.6f}"
        )

    # ---------------------------------------------------------
    # Border vs interior
    # ---------------------------------------------------------

    border = 2

    interior = difference[
        border:-border,
        border:-border,
        :
    ]

    print("\nInterior difference")
    print("-------------------")

    print(
        f"Mean   : {interior.mean():.6f}"
    )

    print(
        f"Median : {np.median(interior):.6f}"
    )

    print(
        f"Maximum: {interior.max():.6f}"
    )

    # ---------------------------------------------------------
    # Location of maximum difference
    # ---------------------------------------------------------

    index = np.unravel_index(
        np.argmax(difference),
        difference.shape,
    )

    y, x, channel = index

    print("\nMaximum difference location")
    print("---------------------------")

    print(
        f"x       : {x}"
    )

    print(
        f"y       : {y}"
    )

    print(
        f"channel : {channel_names[channel]}"
    )

    print(
        f"ours    : {ours[y, x, channel]:.6f}"
    )

    print(
        f"OpenCV  : {reference[y, x, channel]:.6f}"
    )

    print(
        f"diff    : {difference[y, x, channel]:.6f}"
    )

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
