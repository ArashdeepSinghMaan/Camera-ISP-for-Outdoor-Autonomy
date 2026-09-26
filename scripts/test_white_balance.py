#!/usr/bin/env python3

import numpy as np

from camera_isp.isp.white_balance import (
    WhiteBalanceGains,
    apply_white_balance,
    white_point_to_gains,
)


def main():

    print("White-Balance Test")
    print("==================")

    # ---------------------------------------------------------
    # Test 1: white-point -> gains
    # ---------------------------------------------------------

    gains = white_point_to_gains(
        r_over_g=0.5,
        b_over_g=0.25,
    )

    assert np.isclose(gains.R, 2.0)
    assert np.isclose(gains.G1, 1.0)
    assert np.isclose(gains.G2, 1.0)
    assert np.isclose(gains.B, 4.0)

    print("\nTest 1: white-point conversion")
    print(gains)

    # ---------------------------------------------------------
    # Test 2: apply gains
    # ---------------------------------------------------------

    R = np.array(
        [[100, 200]],
        dtype=np.uint16,
    )

    G1 = np.array(
        [[100, 200]],
        dtype=np.uint16,
    )

    G2 = np.array(
        [[100, 200]],
        dtype=np.uint16,
    )

    B = np.array(
        [[100, 200]],
        dtype=np.uint16,
    )

    corrected = apply_white_balance(
        R,
        G1,
        G2,
        B,
        gains,
    )

    corrected_R, corrected_G1, corrected_G2, corrected_B = corrected

    assert corrected_R.dtype == np.float32
    assert corrected_B.dtype == np.float32

    assert np.array_equal(
        corrected_R,
        np.array([[200, 400]], dtype=np.float32),
    )

    assert np.array_equal(
        corrected_G1,
        np.array([[100, 200]], dtype=np.float32),
    )

    assert np.array_equal(
        corrected_G2,
        np.array([[100, 200]], dtype=np.float32),
    )

    assert np.array_equal(
        corrected_B,
        np.array([[400, 800]], dtype=np.float32),
    )

    print("\nTest 2: gain application")
    print("R :", corrected_R)
    print("G1:", corrected_G1)
    print("G2:", corrected_G2)
    print("B :", corrected_B)

    # ---------------------------------------------------------
    # Test 3: unity gains
    # ---------------------------------------------------------

    unity = WhiteBalanceGains()

    result = apply_white_balance(
        R,
        G1,
        G2,
        B,
        unity,
    )

    assert np.array_equal(
        result[0],
        R.astype(np.float32),
    )

    assert np.array_equal(
        result[1],
        G1.astype(np.float32),
    )

    assert np.array_equal(
        result[2],
        G2.astype(np.float32),
    )

    assert np.array_equal(
        result[3],
        B.astype(np.float32),
    )

    print("\nTest 3: unity gains")
    print("Passed")

    # ---------------------------------------------------------
    # Test 4: invalid white point
    # ---------------------------------------------------------

    for r, b in [
        (0.0, 0.5),
        (-1.0, 0.5),
        (0.5, 0.0),
        (0.5, -1.0),
    ]:
        try:
            white_point_to_gains(r, b)
            raise AssertionError(
                f"Invalid WP accepted: {r}, {b}"
            )
        except ValueError:
            pass

    print("\nTest 4: invalid white-point values")
    print("Passed")

    # ---------------------------------------------------------
    # Test 5: mismatched channel shapes
    # ---------------------------------------------------------

    try:
        apply_white_balance(
            np.zeros((2, 2)),
            np.zeros((2, 3)),
            np.zeros((2, 2)),
            np.zeros((2, 2)),
            unity,
        )
        raise AssertionError(
            "Mismatched channel shapes should fail"
        )
    except ValueError:
        pass

    print("\nTest 5: mismatched shapes")
    print("Passed")

    print("\nAll white-balance tests passed.")


if __name__ == "__main__":
    main()
