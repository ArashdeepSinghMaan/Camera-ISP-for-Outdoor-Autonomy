from pathlib import Path

import numpy as np

from camera_isp.io.raw_reader import read_raw
from camera_isp.raw.bayer import extract_bayer_channels


DATASET_ROOT = Path(
    "/media/hitech/WD_Access/Camera_ISP/Sony_IMX135"
)

WIDTH = 3264
HEIGHT = 2448
BAYER_PATTERN = "GRBG"


def print_stats(name, image):
    percentiles = [0, 0.01, 0.1, 0.5, 1, 2, 5]

    print(f"\n{name}")

    for p in percentiles:
        value = np.percentile(image, p)

        print(
            f"  p{p:<5}: {value:.3f}"
        )


def analyze_frame(raw_path):

    raw = read_raw(
        raw_path,
        width=WIDTH,
        height=HEIGHT,
        bayer_pattern=BAYER_PATTERN,
        load_metadata=False,
    )

    channels = extract_bayer_channels(
        raw.data,
        raw.bayer_pattern,
    )

    print("=" * 60)
    print(raw_path.name)
    print("=" * 60)

    for name, image in [
        ("R", channels.R),
        ("G1", channels.G1),
        ("G2", channels.G2),
        ("B", channels.B),
    ]:
        print_stats(name, image)


frames = [
    DATASET_ROOT / "field_3_cameras" /
    "S_IMX135_field3cam_001.plain16",

    DATASET_ROOT / "lab_printouts" /
    "S_IMX135_lab_printouts_001.plain16",

    DATASET_ROOT / "lab_realscene" /
    "S_IMX135_lab_realscene_001.plain16",
]


for frame in frames:

    if not frame.exists():
        print(f"WARNING: file not found: {frame}")
        continue

    analyze_frame(frame)
