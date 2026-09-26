#!/usr/bin/env python3

from pathlib import Path

import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.raw.bayer import extract_bayer_channels
from camera_isp.isp.black_level import apply_black_level
from camera_isp.isp.white_balance import (
    white_point_to_gains,
    apply_white_balance,
)
from camera_isp.isp.demosaic import demosaic_bilinear


RAW_PATH = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)

WIDTH = 3264
HEIGHT = 2448
BAYER_PATTERN = "GRBG"

# Experimental configuration.
BLACK_LEVEL_OFFSET = 64.0

R_OVER_G = 0.649375400
B_OVER_G = 0.463837690


def print_stats(name, image):

    print(f"\n{name}")
    print("-" * len(name))

    print(f"dtype  : {image.dtype}")
    print(f"shape  : {image.shape}")
    print(f"min    : {image.min():.6f}")
    print(f"max    : {image.max():.6f}")
    print(f"mean   : {image.mean():.6f}")
    print(f"median : {np.median(image):.6f}")


def main():

    print("Phase 3 Integrated Bayer-Domain ISP Test")
    print("=========================================")

    # ---------------------------------------------------------
    # 1. Read RAW
    # ---------------------------------------------------------

    raw_image = read_raw(
        path=RAW_PATH,
        width=WIDTH,
        height=HEIGHT,
        bayer_pattern=BAYER_PATTERN,
    )

    raw = raw_image.data

    print_stats(
        "1. Original RAW",
        raw,
    )

    # ---------------------------------------------------------
    # 2. Black-level correction
    # ---------------------------------------------------------

    corrected_raw = apply_black_level(
        raw,
        offset=BLACK_LEVEL_OFFSET,
    )

    print_stats(
        "2. After black-level correction",
        corrected_raw,
    )

    clipped_pixels = np.count_nonzero(
        corrected_raw == 0.0
    )

    clipping_percentage = (
        clipped_pixels / corrected_raw.size * 100.0
    )

    print(
        f"Experimental offset : "
        f"{BLACK_LEVEL_OFFSET:.1f} DN"
    )

    print(
        f"Pixels clipped      : "
        f"{clipping_percentage:.6f}%"
    )

    # ---------------------------------------------------------
    # 3. Bayer extraction
    # ---------------------------------------------------------

    channels = extract_bayer_channels(
        corrected_raw,
        BAYER_PATTERN,
    )

    print("\n3. Bayer channels")
    print("-----------------")

    print(
        f"R  mean: {channels.R.mean():.6f}"
    )

    print(
        f"G1 mean: {channels.G1.mean():.6f}"
    )

    print(
        f"G2 mean: {channels.G2.mean():.6f}"
    )

    print(
        f"B  mean: {channels.B.mean():.6f}"
    )

    # ---------------------------------------------------------
    # 4. White balance
    # ---------------------------------------------------------

    gains = white_point_to_gains(
        r_over_g=R_OVER_G,
        b_over_g=B_OVER_G,
    )

    print("\n4. White balance")
    print("----------------")

    print(
        f"R gain : {gains.R:.6f}"
    )

    print(
        f"G1 gain: {gains.G1:.6f}"
    )

    print(
        f"G2 gain: {gains.G2:.6f}"
    )

    print(
        f"B gain : {gains.B:.6f}"
    )

    R, G1, G2, B = apply_white_balance(
        channels.R,
        channels.G1,
        channels.G2,
        channels.B,
        gains,
    )

    print(
        f"WB R mean : {R.mean():.6f}"
    )

    print(
        f"WB G mean : "
        f"{((G1.mean() + G2.mean()) / 2.0):.6f}"
    )

    print(
        f"WB B mean : {B.mean():.6f}"
    )

    # ---------------------------------------------------------
    # 5. Reconstruct Bayer image
    # ---------------------------------------------------------

    wb_bayer = np.empty_like(
        corrected_raw,
        dtype=np.float32,
    )

    wb_bayer[0::2, 1::2] = R
    wb_bayer[0::2, 0::2] = G1
    wb_bayer[1::2, 1::2] = G2
    wb_bayer[1::2, 0::2] = B

    print_stats(
        "5. White-balanced Bayer",
        wb_bayer,
    )

    # ---------------------------------------------------------
    # 6. Demosaicing
    # ---------------------------------------------------------

    rgb = demosaic_bilinear(
        wb_bayer,
        BAYER_PATTERN,
    )

    print_stats(
        "6. Final RGB",
        rgb,
    )

    # ---------------------------------------------------------
    # 7. RGB channel statistics
    # ---------------------------------------------------------

    print("\n7. Final RGB channels")
    print("---------------------")

    print(
        f"R mean: {rgb[:, :, 0].mean():.6f}"
    )

    print(
        f"G mean: {rgb[:, :, 1].mean():.6f}"
    )

    print(
        f"B mean: {rgb[:, :, 2].mean():.6f}"
    )

    # ---------------------------------------------------------
    # 8. Sanity checks
    # ---------------------------------------------------------

    assert rgb.shape == (
        HEIGHT,
        WIDTH,
        3,
    )

    assert rgb.dtype == np.float32

    assert np.isfinite(rgb).all()

    assert rgb.min() >= 0.0

    print("\n8. Sanity checks")
    print("----------------")
    print("RGB shape        : PASS")
    print("RGB dtype        : PASS")
    print("Finite values    : PASS")
    print("Non-negative RGB  : PASS")

    print("\nPhase 3 integrated pipeline test complete.")


if __name__ == "__main__":
    main()
