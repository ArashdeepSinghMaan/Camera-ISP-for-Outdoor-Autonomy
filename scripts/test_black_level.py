#!/usr/bin/env python3

import numpy as np

from camera_isp.isp.black_level import apply_black_level


def main():

    print("Black-level correction test")
    print("----------------------------")

    raw = np.array(
        [
            [50, 100, 200, 500],
            [60, 120, 250, 600],
        ],
        dtype=np.uint16,
    )

    print("Input:")
    print(raw)
    print("dtype:", raw.dtype)

    # ---------------------------------------------------------
    # Test 1: zero offset
    # ---------------------------------------------------------

    corrected_zero = apply_black_level(raw, offset=0)

    assert corrected_zero.dtype == np.float32
    assert np.array_equal(corrected_zero, raw.astype(np.float32))

    print("\nTest 1: offset = 0")
    print(corrected_zero)

    # ---------------------------------------------------------
    # Test 2: scalar offset
    # ---------------------------------------------------------

    corrected = apply_black_level(raw, offset=50)

    expected = np.array(
        [
            [0, 50, 150, 450],
            [10, 70, 200, 550],
        ],
        dtype=np.float32,
    )

    assert np.array_equal(corrected, expected)

    print("\nTest 2: offset = 50")
    print(corrected)

    # ---------------------------------------------------------
    # Test 3: clipping
    # ---------------------------------------------------------

    raw_low = np.array(
        [
            [10, 20],
            [30, 40],
        ],
        dtype=np.uint16,
    )

    corrected_low = apply_black_level(
        raw_low,
        offset=25,
    )

    expected_low = np.array(
        [
            [0, 0],
            [5, 15],
        ],
        dtype=np.float32,
    )

    assert np.array_equal(corrected_low, expected_low)

    print("\nTest 3: clipping")
    print(corrected_low)

    # ---------------------------------------------------------
    # Test 4: invalid input
    # ---------------------------------------------------------

    try:
        apply_black_level(raw, offset=-1)
        raise AssertionError("Negative offset should fail")
    except ValueError:
        pass

    try:
        apply_black_level(raw[0], offset=10)
        raise AssertionError("1-D RAW should fail")
    except ValueError:
        pass

    print("\nTest 4: invalid inputs")
    print("Passed")

    print("\nAll black-level tests passed.")


if __name__ == "__main__":
    main()
