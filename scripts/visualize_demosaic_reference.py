#!/usr/bin/env python3

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

from camera_isp.io.raw_reader import read_raw


RAW_PATH = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)


def main():

    raw_image = read_raw(
        path=RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    )

    raw = raw_image.data

    rgb = cv2.cvtColor(
        raw,
        cv2.COLOR_BayerGR2RGB,
    )

    # Display normalization only.
    display = rgb.astype(np.float32)

    display -= display.min()

    max_value = display.max()

    if max_value > 0:
        display /= max_value

    plt.figure(figsize=(12, 8))
    plt.imshow(display)
    plt.title("Sony IMX135 — OpenCV GRBG Demosaicing")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
