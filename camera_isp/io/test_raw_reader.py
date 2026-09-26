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


print("RAW + Metadata test")
print("-------------------")

print("Shape:", raw.shape)
print("Dtype:", raw.dtype)
print("Bayer:", raw.bayer_pattern)

print("\nRAW statistics:")
print("Min:", raw.min)
print("Max:", raw.max)
print("Mean:", raw.mean)

print("\nCamera metadata:")

if raw.metadata is None:
    print("No metadata loaded.")
else:
    for key, value in raw.metadata.items():
        print(f"{key}: {value}")
