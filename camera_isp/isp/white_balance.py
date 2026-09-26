#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class WhiteBalanceGains:
    """Per-channel white-balance gains."""

    R: float = 1.0
    G1: float = 1.0
    G2: float = 1.0
    B: float = 1.0


def white_point_to_gains(
    r_over_g: float,
    b_over_g: float,
) -> WhiteBalanceGains:
    """
    Convert white-point coordinates [R/G, B/G]
    into normalized RGB white-balance gains.

    Green is used as the reference channel:

        G_R = 1 / (R/G)
        G_G = 1
        G_B = 1 / (B/G)

    Both Bayer green channels receive the same gain.
    """

    if not np.isfinite(r_over_g):
        raise ValueError(
            f"r_over_g must be finite, got {r_over_g}"
        )

    if not np.isfinite(b_over_g):
        raise ValueError(
            f"b_over_g must be finite, got {b_over_g}"
        )

    if r_over_g <= 0:
        raise ValueError(
            f"r_over_g must be > 0, got {r_over_g}"
        )

    if b_over_g <= 0:
        raise ValueError(
            f"b_over_g must be > 0, got {b_over_g}"
        )

    return WhiteBalanceGains(
        R=1.0 / r_over_g,
        G1=1.0,
        G2=1.0,
        B=1.0 / b_over_g,
    )


def apply_white_balance(
    R: np.ndarray,
    G1: np.ndarray,
    G2: np.ndarray,
    B: np.ndarray,
    gains: WhiteBalanceGains,
):
    """
    Apply white-balance gains to Bayer channels.

    Input channels are converted to float32.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        Corrected R, G1, G2, B channels.
    """

    channels = {
        "R": R,
        "G1": G1,
        "G2": G2,
        "B": B,
    }

    shapes = set()

    for name, channel in channels.items():

        if not isinstance(channel, np.ndarray):
            raise TypeError(
                f"{name} must be a numpy.ndarray"
            )

        if channel.ndim != 2:
            raise ValueError(
                f"{name} must be 2-D, got {channel.shape}"
            )

        shapes.add(channel.shape)

    if len(shapes) != 1:
        raise ValueError(
            f"All Bayer channels must have the same shape. "
            f"Got {shapes}"
        )

    corrected_R = (
        R.astype(np.float32) * np.float32(gains.R)
    )

    corrected_G1 = (
        G1.astype(np.float32) * np.float32(gains.G1)
    )

    corrected_G2 = (
        G2.astype(np.float32) * np.float32(gains.G2)
    )

    corrected_B = (
        B.astype(np.float32) * np.float32(gains.B)
    )

    return (
        corrected_R,
        corrected_G1,
        corrected_G2,
        corrected_B,
    )
