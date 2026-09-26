#!/usr/bin/env python3

from __future__ import annotations

import numpy as np


def apply_black_level(
    raw: np.ndarray,
    offset: float = 0.0,
) -> np.ndarray:
    """
    Apply scalar black-level correction to a RAW Bayer image.

    Parameters
    ----------
    raw:
        2-D RAW Bayer image.

    offset:
        Black-level offset in RAW digital numbers (DN).

    Returns
    -------
    np.ndarray
        Black-level-corrected image in float32.

    Notes
    -----
    The offset is intentionally configurable. No sensor-specific
    black-level value is hardcoded here.
    """

    if not isinstance(raw, np.ndarray):
        raise TypeError(
            f"raw must be a numpy.ndarray, got {type(raw).__name__}"
        )

    if raw.ndim != 2:
        raise ValueError(
            f"RAW image must be 2-D, got shape {raw.shape}"
        )

    if not np.isfinite(offset):
        raise ValueError(
            f"offset must be finite, got {offset}"
        )

    if offset < 0:
        raise ValueError(
            f"offset must be >= 0, got {offset}"
        )

    corrected = raw.astype(np.float32) - np.float32(offset)

    # Black-level subtraction cannot produce negative sensor signal.
    np.maximum(corrected, 0.0, out=corrected)

    return corrected
