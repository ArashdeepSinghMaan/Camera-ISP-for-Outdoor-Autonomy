#!/usr/bin/env python3

from pathlib import Path

import cv2
import numpy as np


RAW_PATH = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)

OUTPUT_DIR = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Repo/results/phase3/demosaicing"
)

WIDTH = 3264
HEIGHT = 2448


def normalize_for_display(image):
    """
    Normalize image only for visualization.
    Does not modify ISP data.
    """

    image = image.astype(np.float32)

    min_value = image.min()
    max_value = image.max()

    if max_value <= min_value:
        return np.zeros_like(image, dtype=np.uint8)

    image = (
        (image - min_value)
        / (max_value - min_value)
        * 255.0
    )

    return np.clip(image, 0, 255).astype(np.uint8)


def save_crop(
    image,
    name,
    x1,
    y1,
    x2,
    y2,
    scale=4,
):
    """
    Extract and enlarge a crop.

    Coordinates refer to the demosaiced RGB image.
    """

    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        raise ValueError(
            f"Empty crop: {name}"
        )

    display_crop = normalize_for_display(crop)

    enlarged = cv2.resize(
        display_crop,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_NEAREST,
    )

    output_path = OUTPUT_DIR / f"{name}.png"

    cv2.imwrite(
        str(output_path),
        cv2.cvtColor(
            enlarged,
            cv2.COLOR_RGB2BGR,
        ),
    )

    print(
        f"{name:20s} "
        f"ROI=({x1},{y1})-({x2},{y2}) "
        f"shape={crop.shape} "
        f"-> {output_path}"
    )


def main():

    print("Demosaicing Crop Inspection")
    print("===========================")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Read RAW
    # ---------------------------------------------------------

    raw = np.fromfile(
        RAW_PATH,
        dtype=np.uint16,
    ).reshape(
        HEIGHT,
        WIDTH,
    )

    print("\nRAW:")
    print("Shape:", raw.shape)
    print("dtype:", raw.dtype)

    # ---------------------------------------------------------
    # OpenCV reference demosaicing
    # ---------------------------------------------------------

    rgb = cv2.cvtColor(
        raw,
        cv2.COLOR_BayerGR2RGB,
    )

    print("\nRGB:")
    print("Shape:", rgb.shape)
    print("dtype:", rgb.dtype)

    # ---------------------------------------------------------
    # Full frame
    # ---------------------------------------------------------

    full = normalize_for_display(rgb)

    cv2.imwrite(
        str(OUTPUT_DIR / "full_frame.png"),
        cv2.cvtColor(full, cv2.COLOR_RGB2BGR),
    )

    # ---------------------------------------------------------
    # High-frequency regions
    # ---------------------------------------------------------
    #
    # These ROIs are intentionally approximate.
    # They can be adjusted after visual inspection.
    #

    crops = {

        # Window blinds / repeated horizontal structure
        "crop_blinds": (
            2050,
            1150,
            3200,
            1900,
        ),

        # Plant leaves / thin structures
        "crop_plant": (
            2050,
            450,
            3200,
            1050,
        ),

        # Clothing / high contrast boundaries
        "crop_clothing": (
            1250,
            500,
            2150,
            1500,
        ),

        # Wall / object boundaries
        "crop_edges": (
            400,
            500,
            1450,
            1800,
        ),
    }

    print("\nSaving crops")
    print("------------")

    for name, roi in crops.items():

        save_crop(
            rgb,
            name,
            *roi,
            scale=4,
        )

    print("\nDemosaicing crop inspection complete.")


if __name__ == "__main__":
    main()
