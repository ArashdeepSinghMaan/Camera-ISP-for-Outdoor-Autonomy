#!/usr/bin/env python3

from pathlib import Path
import argparse

import numpy as np
import matplotlib.pyplot as plt


BAYER_PATTERNS = {
    "RGGB": {
        "R":  (0, 0),
        "G1": (0, 1),
        "G2": (1, 0),
        "B":  (1, 1),
    },

    "BGGR": {
        "B":  (0, 0),
        "G1": (0, 1),
        "G2": (1, 0),
        "R":  (1, 1),
    },

    "GRBG": {
        "G1": (0, 0),
        "R":  (0, 1),
        "B":  (1, 0),
        "G2": (1, 1),
    },

    "GBRG": {
        "G1": (0, 0),
        "B":  (0, 1),
        "R":  (1, 0),
        "G2": (1, 1),
    },
}


BAYER_ALIASES = {
    "GR_BG": "GRBG",
    "RG_GB": "RGGB",
    "BG_GR": "BGGR",
    "GB_RG": "GBRG",
}


def load_raw(path, width, height):

    if not path.exists():
        raise FileNotFoundError(
            f"RAW file does not exist:\n{path}"
        )

    expected_pixels = width * height
    expected_bytes = expected_pixels * 2
    actual_bytes = path.stat().st_size

    print("=" * 70)
    print("RAW VISUALIZATION")
    print("=" * 70)

    print(f"\nFile:")
    print(f"  {path}")

    print("\nFile size:")
    print(f"  Actual   : {actual_bytes:,} bytes")
    print(f"  Expected : {expected_bytes:,} bytes")

    if actual_bytes != expected_bytes:
        raise ValueError(
            "RAW file size does not match supplied dimensions."
        )

    raw = np.fromfile(
        path,
        dtype=np.uint16
    )

    raw = raw.reshape(
        height,
        width
    )

    print("\nRAW:")
    print(f"  dtype : {raw.dtype}")
    print(f"  shape : {raw.shape}")
    print(f"  min   : {raw.min()}")
    print(f"  max   : {raw.max()}")
    print(f"  mean  : {raw.mean():.3f}")

    return raw


def extract_bayer_planes(raw, pattern):

    pattern = pattern.upper()

    pattern = BAYER_ALIASES.get(
        pattern,
        pattern
    )

    if pattern not in BAYER_PATTERNS:
        raise ValueError(
            f"Unsupported Bayer pattern: {pattern}"
        )

    positions = BAYER_PATTERNS[pattern]

    planes = {}

    for channel, (row, col) in positions.items():

        planes[channel] = raw[
            row::2,
            col::2
        ]

    return pattern, planes


def normalize_for_display(
    image,
    black_level=64,
    saturation=1023
):

    image = image.astype(np.float32)

    image = (
        image - black_level
    ) / (
        saturation - black_level
    )

    image = np.clip(
        image,
        0.0,
        1.0
    )

    return image


def visualize_raw(
    raw,
    pattern,
    black_level,
    saturation,
    rotate_display
):

    pattern, planes = extract_bayer_planes(
        raw,
        pattern
    )

    display_raw = normalize_for_display(
        raw,
        black_level,
        saturation
    )

    if rotate_display:
        display_raw = np.rot90(
            display_raw,
            2
        )

    fig, axes = plt.subplots(
        2,
        3,
        figsize=(18, 11)
    )

    # --------------------------------------------------
    # 1. RAW Bayer mosaic
    # --------------------------------------------------

    axes[0, 0].imshow(
        display_raw,
        cmap="gray",
        vmin=0,
        vmax=1
    )

    axes[0, 0].set_title(
        "RAW Bayer Mosaic"
    )

    axes[0, 0].axis("off")

    # --------------------------------------------------
    # 2. R plane
    # --------------------------------------------------

    axes[0, 1].imshow(
        normalize_for_display(
            planes["R"],
            black_level,
            saturation
        ),
        cmap="gray",
        vmin=0,
        vmax=1
    )

    axes[0, 1].set_title(
        "R Plane"
    )

    axes[0, 1].axis("off")

    # --------------------------------------------------
    # 3. B plane
    # --------------------------------------------------

    axes[0, 2].imshow(
        normalize_for_display(
            planes["B"],
            black_level,
            saturation
        ),
        cmap="gray",
        vmin=0,
        vmax=1
    )

    axes[0, 2].set_title(
        "B Plane"
    )

    axes[0, 2].axis("off")

    # --------------------------------------------------
    # 4. G1
    # --------------------------------------------------

    axes[1, 0].imshow(
        normalize_for_display(
            planes["G1"],
            black_level,
            saturation
        ),
        cmap="gray",
        vmin=0,
        vmax=1
    )

    axes[1, 0].set_title(
        "G1 Plane"
    )

    axes[1, 0].axis("off")

    # --------------------------------------------------
    # 5. G2
    # --------------------------------------------------

    axes[1, 1].imshow(
        normalize_for_display(
            planes["G2"],
            black_level,
            saturation
        ),
        cmap="gray",
        vmin=0,
        vmax=1
    )

    axes[1, 1].set_title(
        "G2 Plane"
    )

    axes[1, 1].axis("off")

    # --------------------------------------------------
    # 6. Information
    # --------------------------------------------------

    axes[1, 2].axis("off")

    information = (
        f"Camera: Sony IMX135\n\n"
        f"RAW size: {raw.shape[1]} × {raw.shape[0]}\n"
        f"Datatype: {raw.dtype}\n"
        f"Bayer: {pattern}\n\n"
        f"RAW min: {raw.min()}\n"
        f"RAW max: {raw.max()}\n"
        f"RAW mean: {raw.mean():.3f}\n\n"
        f"Display black level: {black_level}\n"
        f"Display saturation: {saturation}\n\n"
        f"Display rotation: "
        f"{'180°' if rotate_display else 'None'}"
    )

    axes[1, 2].text(
        0.05,
        0.95,
        information,
        verticalalignment="top",
        fontsize=12
    )

    fig.suptitle(
        "Sony IMX135 — RAW Sensor Visualization",
        fontsize=16
    )

    plt.tight_layout()

    plt.show()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Visualize Sony IMX135 RAW Bayer data "
            "without applying ISP processing."
        )
    )

    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="Path to .plain16 RAW file"
    )

    parser.add_argument(
        "--width",
        required=True,
        type=int,
        help="RAW width"
    )

    parser.add_argument(
        "--height",
        required=True,
        type=int,
        help="RAW height"
    )

    parser.add_argument(
        "--pattern",
        required=True,
        choices=[
            "RGGB",
            "BGGR",
            "GRBG",
            "GBRG",
            "GR_BG",
            "RG_GB",
            "BG_GR",
            "GB_RG",
        ],
        help="Bayer pattern"
    )

    parser.add_argument(
        "--black-level",
        type=float,
        default=64,
        help="Display black level"
    )

    parser.add_argument(
        "--saturation",
        type=float,
        default=1023,
        help="Display saturation point"
    )

    parser.add_argument(
        "--rotate-display",
        action="store_true",
        help="Rotate visualization by 180 degrees only"
    )

    args = parser.parse_args()

    raw = load_raw(
        args.file,
        args.width,
        args.height
    )

    visualize_raw(
        raw,
        args.pattern,
        args.black_level,
        args.saturation,
        args.rotate_display
    )


if __name__ == "__main__":
    main()
