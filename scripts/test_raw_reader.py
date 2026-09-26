from camera_isp.io.raw_reader import read_raw


RAW_PATH = (
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.plain16"
)


raw = read_raw(
    RAW_PATH,
    width=3264,
    height=2448,
    bayer_pattern="GRBG",
)


print("RAW reader test")
print("----------------")
print("Path:", raw.path)
print("Shape:", raw.shape)
print("Width:", raw.width)
print("Height:", raw.height)
print("Dtype:", raw.dtype)
print("Bayer:", raw.bayer_pattern)
print("Min:", raw.min)
print("Max:", raw.max)
print("Mean:", raw.mean)
