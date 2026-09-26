#!/usr/bin/env python3

from __future__ import annotations

import cv2
import numpy as np


SUPPORTED_BAYER_PATTERNS = {"GRBG"}


def demosaic_bilinear(
    bayer: np.ndarray,
    bayer_pattern: str,
) -> np.ndarray:
    """
    Bilinear demosaicing of a Bayer image.

    Parameters
    ----------
    bayer:
        2-D Bayer image.

    bayer_pattern:
        Bayer pattern. Currently only GRBG is supported.

    Returns
    -------
    np.ndarray
        RGB image with shape (H, W, 3), dtype float32.

    Notes
    -----
    The implementation uses explicit Bayer masks and linear
    interpolation through OpenCV's separable filtering operation.

    The output channel order is RGB.
    """

    if not isinstance(bayer, np.ndarray):
        raise TypeError(
            f"bayer must be a numpy.ndarray, "
            f"got {type(bayer).__name__}"
        )

    if bayer.ndim != 2:
        raise ValueError(
            f"bayer must be 2-D, got shape {bayer.shape}"
        )

    if bayer_pattern is None:
        raise ValueError(
            "bayer_pattern must be explicitly provided"
        )

    pattern = bayer_pattern.upper()

    if pattern not in SUPPORTED_BAYER_PATTERNS:
        raise ValueError(
            f"Unsupported Bayer pattern: {bayer_pattern!r}. "
            f"Supported: {sorted(SUPPORTED_BAYER_PATTERNS)}"
        )

    height, width = bayer.shape

    if height % 2 != 0 or width % 2 != 0:
        raise ValueError(
            "Bayer image dimensions must be even. "
            f"Got {width} x {height}"
        )

    bayer = bayer.astype(np.float32)

    # ---------------------------------------------------------
    # GRBG geometry
    #
    # G R G R ...
    # B G B G ...
    #
    # ---------------------------------------------------------

    red_mask = np.zeros_like(bayer, dtype=np.float32)
    green_mask = np.zeros_like(bayer, dtype=np.float32)
    blue_mask = np.zeros_like(bayer, dtype=np.float32)

    red_mask[0::2, 1::2] = 1.0

    green_mask[0::2, 0::2] = 1.0
    green_mask[1::2, 1::2] = 1.0

    blue_mask[1::2, 0::2] = 1.0

    red = bayer * red_mask
    green = bayer * green_mask
    blue = bayer * blue_mask

    # ---------------------------------------------------------
    # Bilinear interpolation
    # ---------------------------------------------------------

    # Kernel:
    #
    # 1 2 1
    # 2 4 2
    # 1 2 1
    #
    # normalized by 16.
    #
    # This performs spatial interpolation while preserving
    # the measured samples through reinsertion below.
    #

    kernel = np.array(
        [
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1],
        ],
        dtype=np.float32,
    ) / 16.0

    red_interp = cv2.filter2D(
        red,
        ddepth=-1,
        kernel=kernel,
        borderType=cv2.BORDER_REFLECT,
    )

    green_interp = cv2.filter2D(
        green,
        ddepth=-1,
        kernel=kernel,
        borderType=cv2.BORDER_REFLECT,
    )

    blue_interp = cv2.filter2D(
        blue,
        ddepth=-1,
        kernel=kernel,
        borderType=cv2.BORDER_REFLECT,
    )

    # ---------------------------------------------------------
    # Normalize using interpolated mask weights
    # ---------------------------------------------------------

    red_weight = cv2.filter2D(
        red_mask,
        ddepth=-1,
        kernel=kernel,
        borderType=cv2.BORDER_REFLECT,
    )

    green_weight = cv2.filter2D(
        green_mask,
        ddepth=-1,
        kernel=kernel,
        borderType=cv2.BORDER_REFLECT,
    )

    blue_weight = cv2.filter2D(
        blue_mask,
        ddepth=-1,
        kernel=kernel,
        borderType=cv2.BORDER_REFLECT,
    )

    red_interp /= np.maximum(red_weight, 1e-12)
    green_interp /= np.maximum(green_weight, 1e-12)
    blue_interp /= np.maximum(blue_weight, 1e-12)

    # ---------------------------------------------------------
    # Preserve measured sensor samples exactly
    # ---------------------------------------------------------

    red_interp[red_mask == 1] = bayer[red_mask == 1]
    green_interp[green_mask == 1] = bayer[green_mask == 1]
    blue_interp[blue_mask == 1] = bayer[blue_mask == 1]

    rgb = np.stack(
        [
            red_interp,
            green_interp,
            blue_interp,
        ],
        axis=-1,
    )

    return rgb.astype(np.float32)
