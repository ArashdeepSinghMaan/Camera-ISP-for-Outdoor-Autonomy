#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from .metadata_reader import parse_metadata

SUPPORTED_BAYER_PATTERNS = {
    "RGGB",
    "BGGR",
    "GRBG",
    "GBRG",
}


@dataclass
class RawImage:
    """
    Structured representation of a RAW Bayer frame.
    """

    data: np.ndarray
    width: int
    height: int
    bayer_pattern: str
    path: Path
    dtype: np.dtype
    metadata: Optional[dict] = None

    @property
    def shape(self):
        return self.data.shape

    @property
    def min(self):
        return int(self.data.min())

    @property
    def max(self):
        return int(self.data.max())

    @property
    def mean(self):
        return float(self.data.mean())


def validate_bayer_pattern(
    bayer_pattern: str,
) -> str:

    if bayer_pattern is None:
        raise ValueError(
            "Bayer pattern must be explicitly provided. "
            "The RAW reader will never guess the Bayer pattern."
        )

    pattern = bayer_pattern.upper()

    if pattern not in SUPPORTED_BAYER_PATTERNS:

        supported = ", ".join(
            sorted(SUPPORTED_BAYER_PATTERNS)
        )

        raise ValueError(
            f"Unsupported Bayer pattern: "
            f"{bayer_pattern!r}. "
            f"Supported patterns: {supported}"
        )

    return pattern


def validate_dimensions(
    width: int,
    height: int,
) -> None:

    if not isinstance(width, int):
        raise TypeError(
            f"width must be int, got {type(width).__name__}"
        )

    if not isinstance(height, int):
        raise TypeError(
            f"height must be int, got {type(height).__name__}"
        )

    if width <= 0:
        raise ValueError(
            f"width must be > 0, got {width}"
        )

    if height <= 0:
        raise ValueError(
            f"height must be > 0, got {height}"
        )

    if width % 2 != 0 or height % 2 != 0:

        raise ValueError(
            "Bayer RAW dimensions must be even. "
            f"Got width={width}, height={height}"
        )


def read_raw(
    path,
    width: int,
    height: int,
    bayer_pattern: str,
    metadata: Optional[dict] = None,
    load_metadata: bool = True,
) -> RawImage:

    path = Path(path)

    if load_metadata and metadata is None:
        metadata_path = path.with_suffix(".meta")

        if metadata_path.exists():
            metadata = parse_metadata(metadata_path)

    if not path.exists():

        raise FileNotFoundError(
            f"RAW file does not exist:\n{path}"
        )

    if not path.is_file():

        raise ValueError(
            f"RAW path is not a file:\n{path}"
        )

    validate_dimensions(
        width,
        height,
    )

    bayer_pattern = validate_bayer_pattern(
        bayer_pattern
    )

    expected_pixels = width * height

    expected_bytes = expected_pixels * 2

    actual_bytes = path.stat().st_size

    if actual_bytes != expected_bytes:

        raise ValueError(
            "RAW file size mismatch.\n"
            f"File: {path}\n"
            f"Expected: {expected_bytes:,} bytes\n"
            f"Found:    {actual_bytes:,} bytes"
        )

    raw = np.fromfile(
        path,
        dtype=np.uint16,
    )

    if raw.size != expected_pixels:

        raise ValueError(
            "RAW pixel count mismatch.\n"
            f"Expected: {expected_pixels:,}\n"
            f"Found:    {raw.size:,}"
        )

    raw = raw.reshape(
        height,
        width,
    )

    return RawImage(
        data=raw,
        width=width,
        height=height,
        bayer_pattern=bayer_pattern,
        path=path.resolve(),
        dtype=raw.dtype,
        metadata=metadata,
    )
