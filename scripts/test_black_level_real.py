#!/usr/bin/env python3

import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.isp.black_level import apply_black_level


RAW_PATH = (
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)


def print_stats(name, image):
    print(f"\n{name}")
    print("-" * len(name))
    print(f"dtype : {image.dtype}")
    print(f"shape : {image.shape}")
    print(f"min   : {image.min():.3f}")
    print(f"max   : {image.max():.3f}")
    print(f"mean  : {image.mean():.3f}")
    print(f"median: {np.median(image):.3f}")

    for p in [0.1, 1, 5, 50, 95, 99, 99.9]:
        print(
            f"p{p:<4}: "
            f"{np.percentile(image, p):.3f}"
        )


def main():

    print("Real Sony IMX135 Black-Level Test")
    print("==================================")

    raw_image = read_raw(
        path=RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    )

    raw = raw_image.data

    print_stats("Original RAW", raw)

    # ---------------------------------------------------------
    # Experimental offset
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # 64 is NOT being declared as the calibrated
    # sensor black level. It is only an experimental value.
    #

    offset = 64.0

    corrected = apply_black_level(
        raw,
        offset=offset,
    )

    print_stats(
        f"Corrected RAW (experimental offset={offset})",
        corrected,
    )

    # ---------------------------------------------------------
    # Signal change
    # ---------------------------------------------------------

    clipped_fraction = np.mean(corrected == 0.0) * 100.0

    print("\nCorrection summary")
    print("------------------")
    print(f"Offset:              {offset}")
    print(f"Original mean:       {raw.mean():.3f}")
    print(f"Corrected mean:      {corrected.mean():.3f}")
    print(f"Mean reduction:      {raw.mean() - corrected.mean():.3f}")
    print(f"Pixels clipped to 0: {clipped_fraction:.4f}%")

    print("\nReal-data black-level test completed.")


if __name__ == "__main__":
    main()
