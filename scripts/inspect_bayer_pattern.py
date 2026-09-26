#!/usr/bin/env python3

import numpy as np


def main():

    print("Bayer Pattern Inspection")
    print("========================")

    pattern = np.array(
        [
            ["G", "R"],
            ["B", "G"],
        ]
    )

    print("\nGRBG Bayer unit cell:")
    print(pattern)

    print("\nExpanded 8x8 pattern:")

    expanded = np.tile(pattern, (4, 4))

    for row in expanded:
        print(" ".join(row))

    print("\nChannel locations:")

    for name, char in [
        ("R", "R"),
        ("G", "G"),
        ("B", "B"),
    ]:

        locations = np.argwhere(expanded == char)

        print(
            f"{name}: "
            f"{len(locations)} samples"
        )

        print(
            locations[:8]
        )


if __name__ == "__main__":
    main()
