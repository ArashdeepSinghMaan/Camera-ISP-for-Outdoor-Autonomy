#!/usr/bin/env python3

from pathlib import Path

import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.raw.bayer import extract_bayer_channels
from camera_isp.isp.white_balance import (
    apply_white_balance,
    white_point_to_gains,
)


RAW_PATH = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)


def read_white_point(path):

    values = []

    with path.open("r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            values.extend(float(x) for x in line.split())

    if len(values) != 2:
        raise ValueError(
            f"Expected 2 white-point values, got {len(values)}"
        )

    return values[0], values[1]


def print_stats(name, R, G1, G2, B):

    G = (G1 + G2) / 2.0

    print(f"\n{name}")
    print("-" * len(name))

    print(f"R  mean: {R.mean():.6f}")
    print(f"G1 mean: {G1.mean():.6f}")
    print(f"G2 mean: {G2.mean():.6f}")
    print(f"G  mean: {G.mean():.6f}")
    print(f"B  mean: {B.mean():.6f}")

    print("\nChannel ratios:")

    print(
        f"R/G: {R.mean() / G.mean():.6f}"
    )

    print(
        f"B/G: {B.mean() / G.mean():.6f}"
    )


def main():

    print("Real RAW White-Balance Validation")
    print("=================================")

    # ---------------------------------------------------------
    # Read RAW
    # ---------------------------------------------------------

    raw_image = read_raw(
        path=RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    )

    # ---------------------------------------------------------
    # Extract Bayer channels
    # ---------------------------------------------------------

    channels = extract_bayer_channels(
        raw_image.data,
        "GRBG",
    )

    # ---------------------------------------------------------
    # Read WP
    # ---------------------------------------------------------

    wp_path = RAW_PATH.with_suffix(".wp")

    r_over_g, b_over_g = read_white_point(
        wp_path
    )

    print("\nDataset white point")
    print("-------------------")
    print(f"R/G: {r_over_g:.9f}")
    print(f"B/G: {b_over_g:.9f}")

    # ---------------------------------------------------------
    # Convert WP → gains
    # ---------------------------------------------------------

    gains = white_point_to_gains(
        r_over_g=r_over_g,
        b_over_g=b_over_g,
    )

    print("\nWhite-balance gains")
    print("-------------------")
    print(f"R : {gains.R:.9f}")
    print(f"G1: {gains.G1:.9f}")
    print(f"G2: {gains.G2:.9f}")
    print(f"B : {gains.B:.9f}")

    # ---------------------------------------------------------
    # Before WB
    # ---------------------------------------------------------

    print_stats(
        "Before white balance",
        channels.R.astype(np.float32),
        channels.G1.astype(np.float32),
        channels.G2.astype(np.float32),
        channels.B.astype(np.float32),
    )

    # ---------------------------------------------------------
    # Apply WB
    # ---------------------------------------------------------

    R, G1, G2, B = apply_white_balance(
        channels.R,
        channels.G1,
        channels.G2,
        channels.B,
        gains,
    )

    # ---------------------------------------------------------
    # After WB
    # ---------------------------------------------------------

    print_stats(
        "After white balance",
        R,
        G1,
        G2,
        B,
    )

    print("\nWhite-balance real-data validation complete.")


if __name__ == "__main__":
    main()
