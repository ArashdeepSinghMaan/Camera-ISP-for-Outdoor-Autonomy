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

    print("Bilinear Demosaicing Test")
    print("=========================")

    raw_image = read_raw(
        path=RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    )

    raw = raw_image.data

    # ---------------------------------------------------------
    # Our implementation
    # ---------------------------------------------------------

    rgb = demosaic_bilinear(
        raw,
        "GRBG",
    )

    print("\nOur demosaicer")
    print("--------------")
    print("Shape:", rgb.shape)
    print("dtype:", rgb.dtype)
    print("min:", rgb.min())
    print("max:", rgb.max())

    # ---------------------------------------------------------
    # Basic output checks
    # ---------------------------------------------------------

    assert rgb.shape == (
        raw.shape[0],
        raw.shape[1],
        3,
    )

    assert rgb.dtype == np.float32

    assert np.isfinite(rgb).all()

    # ---------------------------------------------------------
    # Measured sample preservation
    # ---------------------------------------------------------

    # GRBG:
    #
    # R = [0::2, 1::2]
    # G1 = [0::2, 0::2]
    # G2 = [1::2, 1::2]
    # B = [1::2, 0::2]

    assert np.array_equal(
        rgb[0::2, 1::2, 0],
        raw[0::2, 1::2].astype(np.float32),
    )

    assert np.array_equal(
        rgb[0::2, 0::2, 1],
        raw[0::2, 0::2].astype(np.float32),
    )

    assert np.array_equal(
        rgb[1::2, 1::2, 1],
        raw[1::2, 1::2].astype(np.float32),
    )

    assert np.array_equal(
        rgb[1::2, 0::2, 2],
        raw[1::2, 0::2].astype(np.float32),
    )

    print("\nMeasured Bayer samples")
    print("----------------------")
    print("All measured samples preserved exactly.")

    # ---------------------------------------------------------
    # OpenCV reference
    # ---------------------------------------------------------

    reference = cv2.cvtColor(
        raw,
        cv2.COLOR_BayerGRBG2RGB,
    ).astype(np.float32)

    difference = np.abs(
        rgb - reference
    )

    print("\nComparison with OpenCV")
    print("----------------------")
    print(
        "Mean absolute difference:",
        difference.mean(),
    )

    print(
        "Maximum absolute difference:",
        difference.max(),
    )

    print(
        "Median absolute difference:",
        np.median(difference),
    )

    print(
        "Pixels exactly equal:",
        np.mean(difference == 0.0) * 100.0,
        "%",
    )

    # ---------------------------------------------------------
    # Channel statistics
    # ---------------------------------------------------------

    print("\nOur channel means")
    print("-----------------")
    print("R:", rgb[:, :, 0].mean())
    print("G:", rgb[:, :, 1].mean())
    print("B:", rgb[:, :, 2].mean())

    print("\nOpenCV channel means")
    print("--------------------")
    print("R:", reference[:, :, 0].mean())
    print("G:", reference[:, :, 1].mean())
    print("B:", reference[:, :, 2].mean())

    print("\nDemosaicing validation complete.")


if __name__ == "__main__":
    main()
