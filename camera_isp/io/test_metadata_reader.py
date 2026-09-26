from camera_isp.io.metadata_reader import parse_metadata


META_PATH = (
    "/media/hitech/WD_Access/Camera_ISP/"
    "Sony_IMX135/field_3_cameras/"
    "S_IMX135_field3cam_001.meta"
)


metadata = parse_metadata(META_PATH)


print("Metadata reader test")
print("--------------------")

for key, value in metadata.items():
    print(f"{key}: {value}")

print("\nFields:")
print(sorted(metadata.keys()))
