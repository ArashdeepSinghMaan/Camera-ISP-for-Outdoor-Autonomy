import numpy as np
from camera_isp.io.raw_reader import read_raw
from camera_isp.raw.bayer import extract_bayer_channels


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


channels = extract_bayer_channels(
    raw.data,
    raw.bayer_pattern,
)


print("Bayer extraction test")
print("---------------------")

print("Pattern:", channels.pattern)

print("\nShapes:")
print("R :", channels.R.shape)
print("G1:", channels.G1.shape)
print("G2:", channels.G2.shape)
print("B :", channels.B.shape)

print("\nStatistics:")

for name, image in [
    ("R", channels.R),
    ("G1", channels.G1),
    ("G2", channels.G2),
    ("B", channels.B),
]:

    print(
        f"{name:2s}: "
        f"min={image.min():4d}, "
        f"max={image.max():4d}, "
        f"mean={image.mean():.3f}, "
        f"median={np.median(image):.3f}"
    )
