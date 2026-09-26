#!/usr/bin/env python3

from pathlib import Path

import numpy as np


DATASET = Path(
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras"
)


def read_wp(path):

    values = []

    with path.open("r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            values.extend(float(x) for x in line.split())

    if len(values) != 2:
        raise ValueError(
            f"Expected 2 values in {path}, found {len(values)}"
        )

    return values[0], values[1]


def main():

    wp_files = sorted(DATASET.glob("*.wp"))

    rg = []
    bg = []

    print("White-Point Characterization")
    print("============================")
    print(f"Dataset : {DATASET}")
    print(f"Frames  : {len(wp_files)}")

    for path in wp_files:

        r_over_g, b_over_g = read_wp(path)

        rg.append(r_over_g)
        bg.append(b_over_g)

    rg = np.asarray(rg)
    bg = np.asarray(bg)

    print("\nR/G statistics")
    print("--------------")

    for p in [0, 1, 5, 25, 50, 75, 95, 99, 100]:
        print(
            f"p{p:<3}: {np.percentile(rg, p):.6f}"
        )

    print("\nB/G statistics")
    print("--------------")

    for p in [0, 1, 5, 25, 50, 75, 95, 99, 100]:
        print(
            f"p{p:<3}: {np.percentile(bg, p):.6f}"
        )

    print("\nMean / std")
    print("----------")
    print(f"R/G mean: {rg.mean():.6f}")
    print(f"R/G std : {rg.std():.6f}")
    print(f"B/G mean: {bg.mean():.6f}")
    print(f"B/G std : {bg.std():.6f}")

    print("\nRange")
    print("-----")
    print(f"R/G range: {rg.min():.6f} → {rg.max():.6f}")
    print(f"B/G range: {bg.min():.6f} → {bg.max():.6f}")

    print("\nExtreme frames")
    print("--------------")

    rg_min = np.argmin(rg)
    rg_max = np.argmax(rg)

    bg_min = np.argmin(bg)
    bg_max = np.argmax(bg)

    print(
        f"Minimum R/G: "
        f"{rg[rg_min]:.6f} "
        f"({wp_files[rg_min].name})"
    )

    print(
        f"Maximum R/G: "
        f"{rg[rg_max]:.6f} "
        f"({wp_files[rg_max].name})"
    )

    print(
        f"Minimum B/G: "
        f"{bg[bg_min]:.6f} "
        f"({wp_files[bg_min].name})"
    )

    print(
        f"Maximum B/G: "
        f"{bg[bg_max]:.6f} "
        f"({wp_files[bg_max].name})"
    )


if __name__ == "__main__":
    main()
