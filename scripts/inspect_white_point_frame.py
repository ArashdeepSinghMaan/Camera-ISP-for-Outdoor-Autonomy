#!/usr/bin/env python3

from pathlib import Path

import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.raw.bayer import extract_bayer_channels


RAW_PATH = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)

WP_PATH = RAW_PATH.with_suffix(".wp")


def read_wp(path):

    values = []

    with path.open("r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            values.extend(float(x) for x in line.split())

    if len(values) != 2:
        raise ValueError(
            f"Expected 2 values, got {len(values)}"
        )

    return values[0], values[1]


def main():

    raw_image = read_raw(
        RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    )

    channels = extract_bayer_channels(
        raw_image.data,
        "GRBG",
    )

    r_over_g_wp, b_over_g_wp = read_wp(WP_PATH)

    R = channels.R.astype(np.float64)
    G1 = channels.G1.astype(np.float64)
    G2 = channels.G2.astype(np.float64)
    B = channels.B.astype(np.float64)

    G = (G1 + G2) / 2.0

    print("White-Point Convention Investigation")
    print("=====================================")

    print("\nDataset WP metadata")
    print("-------------------")
    print(f"R/G: {r_over_g_wp:.9f}")
    print(f"B/G: {b_over_g_wp:.9f}")

    print("\nFull-frame channel means")
    print("------------------------")
    print(f"R : {R.mean():.6f}")
    print(f"G1: {G1.mean():.6f}")
    print(f"G2: {G2.mean():.6f}")
    print(f"G : {G.mean():.6f}")
    print(f"B : {B.mean():.6f}")

    measured_rg = R.mean() / G.mean()
    measured_bg = B.mean() / G.mean()

    print("\nMeasured full-frame ratios")
    print("--------------------------")
    print(f"R/G: {measured_rg:.9f}")
    print(f"B/G: {measured_bg:.9f}")

    print("\nCandidate normalized gains")
    print("--------------------------")

    gain_r = 1.0 / r_over_g_wp
    gain_g = 1.0
    gain_b = 1.0 / b_over_g_wp

    print(f"R gain: {gain_r:.9f}")
    print(f"G gain: {gain_g:.9f}")
    print(f"B gain: {gain_b:.9f}")

    print("\nNormalized channel means")
    print("------------------------")

    corrected_r = R.mean() * gain_r
    corrected_g = G.mean() * gain_g
    corrected_b = B.mean() * gain_b

    print(f"R: {corrected_r:.6f}")
    print(f"G: {corrected_g:.6f}")
    print(f"B: {corrected_b:.6f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
