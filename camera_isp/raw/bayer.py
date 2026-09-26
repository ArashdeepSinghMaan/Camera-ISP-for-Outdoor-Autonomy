from dataclasses import dataclass

import numpy as np


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


@dataclass
class BayerChannels:
    """
    Four physical sensor planes extracted from a Bayer RAW image.
    """

    R: np.ndarray
    G1: np.ndarray
    G2: np.ndarray
    B: np.ndarray

    pattern: str

    @property
    def green(self):
        """
        Return both green planes.
        """
        return self.G1, self.G2


def extract_bayer_channels(
    raw: np.ndarray,
    bayer_pattern: str,
) -> BayerChannels:
    """
    Extract R, G1, G2 and B sensor planes from a Bayer RAW image.

    Parameters
    ----------
    raw:
        2D Bayer RAW image.

    bayer_pattern:
        One of:
        RGGB, BGGR, GRBG, GBRG.

    Returns
    -------
    BayerChannels
    """

    if not isinstance(raw, np.ndarray):
        raise TypeError("raw must be a numpy.ndarray")

    if raw.ndim != 2:
        raise ValueError(
            f"RAW image must be 2D. Got ndim={raw.ndim}"
        )

    pattern = bayer_pattern.upper()

    if pattern not in BAYER_PATTERNS:
        raise ValueError(
            f"Unsupported Bayer pattern: {bayer_pattern!r}. "
            f"Supported patterns: {', '.join(BAYER_PATTERNS)}"
        )

    height, width = raw.shape

    if height % 2 != 0 or width % 2 != 0:
        raise ValueError(
            "RAW dimensions must be even for Bayer extraction. "
            f"Got shape={raw.shape}"
        )

    positions = BAYER_PATTERNS[pattern]

    R_row, R_col = positions["R"]
    G1_row, G1_col = positions["G1"]
    G2_row, G2_col = positions["G2"]
    B_row, B_col = positions["B"]

    R = raw[R_row::2, R_col::2]
    G1 = raw[G1_row::2, G1_col::2]
    G2 = raw[G2_row::2, G2_col::2]
    B = raw[B_row::2, B_col::2]

    return BayerChannels(
        R=R,
        G1=G1,
        G2=G2,
        B=B,
        pattern=pattern,
    )
