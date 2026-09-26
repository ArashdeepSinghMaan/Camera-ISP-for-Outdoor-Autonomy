from camera_isp.io.raw_reader import read_raw


RAW_PATH = (
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)


def run_test(name, func):
    try:
        func()
        print(f"[FAIL] {name}")
    except Exception as e:
        print(f"[PASS] {name}")
        print(f"       {type(e).__name__}: {e}")


# ---------------------------------------------------------
# 1. Wrong width
# ---------------------------------------------------------

run_test(
    "Wrong dimensions",
    lambda: read_raw(
        RAW_PATH,
        width=3200,
        height=2448,
        bayer_pattern="GRBG",
    ),
)


# ---------------------------------------------------------
# 2. Wrong height
# ---------------------------------------------------------

run_test(
    "Wrong height",
    lambda: read_raw(
        RAW_PATH,
        width=3264,
        height=2400,
        bayer_pattern="GRBG",
    ),
)


# ---------------------------------------------------------
# 3. Missing Bayer pattern
# ---------------------------------------------------------

run_test(
    "Missing Bayer pattern",
    lambda: read_raw(
        RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern=None,
    ),
)


# ---------------------------------------------------------
# 4. Invalid Bayer pattern
# ---------------------------------------------------------

run_test(
    "Invalid Bayer pattern",
    lambda: read_raw(
        RAW_PATH,
        width=3264,
        height=2448,
        bayer_pattern="RGGBX",
    ),
)


# ---------------------------------------------------------
# 5. Odd width
# ---------------------------------------------------------

run_test(
    "Odd width",
    lambda: read_raw(
        RAW_PATH,
        width=3265,
        height=2448,
        bayer_pattern="GRBG",
    ),
)


# ---------------------------------------------------------
# 6. Odd height
# ---------------------------------------------------------

run_test(
    "Odd height",
    lambda: read_raw(
        RAW_PATH,
        width=3264,
        height=2449,
        bayer_pattern="GRBG",
    ),
)


# ---------------------------------------------------------
# 7. Non-existent file
# ---------------------------------------------------------

run_test(
    "Missing RAW file",
    lambda: read_raw(
        "/tmp/does_not_exist.plain16",
        width=3264,
        height=2448,
        bayer_pattern="GRBG",
    ),
)
