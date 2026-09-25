import sys

import cv2
import numpy as np
import scipy
import yaml
import matplotlib
import PIL


def main():
    print("=" * 50)
    print("Camera ISP Environment Check")
    print("=" * 50)

    print(f"Python      : {sys.version.split()[0]}")
    print(f"NumPy       : {np.__version__}")
    print(f"OpenCV      : {cv2.__version__}")
    print(f"SciPy       : {scipy.__version__}")
    print(f"PyYAML      : {yaml.__version__}")
    print(f"Matplotlib  : {matplotlib.__version__}")
    print(f"Pillow      : {PIL.__version__}")

    print("\nEnvironment OK.")


if __name__ == "__main__":
    main()
