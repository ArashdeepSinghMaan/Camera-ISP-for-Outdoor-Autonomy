#!/usr/bin/env python3

from pathlib import Path

import cv2
import numpy as np

from camera_isp.io.raw_reader import read_raw


RAW_PATH = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)


def main():

    print("OpenCV Demosaicing Reference")
    print("============================")

    raw_image = read_raw(
        path=RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    )

    raw = raw_image.data

    print("\nRAW")
    print("---")
    print("Shape:", raw.shape)
    print("dtype:", raw.dtype)
    print("min:", raw.min())
    print("max:", raw.max())

    # OpenCV expects the Bayer mosaic directly.
    rgb = cv2.cvtColor(
    raw,
    cv2.COLOR_BayerGRBG2RGB,
    )

    print("\nDemosaiced RGB")
    print("--------------")
    print("Shape:", rgb.shape)
    print("dtype:", rgb.dtype)
    print("min:", rgb.min())
    print("max:", rgb.max())

    print("\nChannel means:")

    print("R:", rgb[:, :, 0].mean())
    print("G:", rgb[:, :, 1].mean())
    print("B:", rgb[:, :, 2].mean())

    print("\nOpenCV reference demosaicing complete.")


if __name__ == "__main__":
    main()
