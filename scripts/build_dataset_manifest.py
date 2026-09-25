#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict, Counter
import argparse
import json
import re

import numpy as np


# ---------------------------------------------------------------------
# Dataset constants established during Phase 1 inspection
# ---------------------------------------------------------------------

RAW_WIDTH = 3264
RAW_HEIGHT = 2448
RAW_DTYPE = np.uint16
RAW_BYTES_PER_PIXEL = 2

EXPECTED_RAW_BYTES = (
    RAW_WIDTH
    * RAW_HEIGHT
    * RAW_BYTES_PER_PIXEL
)


# ---------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------

def collect_files(root: Path):

    files_by_stem = defaultdict(dict)

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        stem = path.stem
        extension = path.suffix.lower()

        files_by_stem[stem][extension] = str(
            path.resolve()
        )

    return files_by_stem


# ---------------------------------------------------------------------
# META parser
# ---------------------------------------------------------------------
def parse_meta(path):

    result = {
        "exposure_time": None,
        "analog_gain": None,
        "aperture": None,
        "normalized_exposure_s": None,
        "iso": None,
        "privacy_masked": None,

        "valid": False,
        "required_fields_present": False,
        "optional_fields_present": {
            "iso": False,
            "privacy_masked": False,
        },
    }

    if path is None:
        return result

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) < 2:
                    continue

                key = parts[0]
                value = parts[1]

                if key == "exposure_time":

                    result["exposure_time"] = float(value)

                elif key == "analog_gain":

                    result["analog_gain"] = float(value)

                elif key == "aperture":

                    result["aperture"] = float(value)

                elif key == "normalized_exposure_s":

                    result["normalized_exposure_s"] = float(value)

                elif key == "iso":

                    result["iso"] = float(value)

                    result[
                        "optional_fields_present"
                    ]["iso"] = True

                elif key == "privacy_masked":

                    result["privacy_masked"] = int(value)

                    result[
                        "optional_fields_present"
                    ]["privacy_masked"] = True

        required = [
            "exposure_time",
            "analog_gain",
            "aperture",
            "normalized_exposure_s",
        ]

        result["required_fields_present"] = all(
            result[key] is not None
            for key in required
        )

        result["valid"] = (
            result["required_fields_present"]
        )

    except Exception as exc:

        result["error"] = str(exc)

    return result
# ---------------------------------------------------------------------
# White-point parser
#
# Dataset format:
#     R/G    B/G
# ---------------------------------------------------------------------

def parse_white_point(path):

    result = {
        "rg_ratio": None,
        "bg_ratio": None,
        "valid": False,
    }

    if path is None:
        return result

    try:

        text = Path(path).read_text(
            encoding="utf-8"
        )

        values = [
            float(x)
            for x in re.findall(
                r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
                r"(?:[eE][-+]?\d+)?",
                text,
            )
        ]

        if len(values) != 2:

            result["error"] = (
                f"Expected 2 numeric values, "
                f"found {len(values)}"
            )

            return result

        result["rg_ratio"] = values[0]
        result["bg_ratio"] = values[1]
        result["valid"] = True

    except Exception as exc:

        result["error"] = str(exc)

    return result


# ---------------------------------------------------------------------
# CCM parser
#
# Dataset format:
#     9 values -> 3 x 3 matrix
# ---------------------------------------------------------------------

def parse_ccm(path):

    result = {
        "matrix": None,
        "valid": False,
    }

    if path is None:
        return result

    try:

        text = Path(path).read_text(
            encoding="utf-8"
        )

        values = [
            float(x)
            for x in re.findall(
                r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
                r"(?:[eE][-+]?\d+)?",
                text,
            )
        ]

        if len(values) != 9:

            result["error"] = (
                f"Expected 9 numeric values, "
                f"found {len(values)}"
            )

            return result

        matrix = np.asarray(
            values,
            dtype=np.float64,
        ).reshape(3, 3)

        result["matrix"] = matrix.tolist()
        result["valid"] = True

    except Exception as exc:

        result["error"] = str(exc)

    return result


# ---------------------------------------------------------------------
# RAW validator
# ---------------------------------------------------------------------

def inspect_raw(path):

    result = {
        "width": RAW_WIDTH,
        "height": RAW_HEIGHT,
        "dtype": "uint16",
        "bytes": None,
        "expected_bytes": EXPECTED_RAW_BYTES,
        "size_valid": False,
        "valid": False,
    }

    if path is None:
        return result

    try:

        file_size = Path(path).stat().st_size

        result["bytes"] = file_size

        result["size_valid"] = (
            file_size == EXPECTED_RAW_BYTES
        )

        result["valid"] = result["size_valid"]

    except Exception as exc:

        result["error"] = str(exc)

    return result


# ---------------------------------------------------------------------
# Build one frame record
# ---------------------------------------------------------------------

def build_record(stem, files):

    raw_path = files.get(".plain16")
    meta_path = files.get(".meta")
    wp_path = files.get(".wp")
    ccm_path = files.get(".ccm")
    jpeg_path = files.get(".jpg")

    meta = parse_meta(meta_path)
    white_point = parse_white_point(wp_path)
    ccm = parse_ccm(ccm_path)
    raw = inspect_raw(raw_path)

    record = {

        "scene_id": stem,

        "files": {
            "raw": raw_path,
            "meta": meta_path,
            "white_point": wp_path,
            "ccm": ccm_path,
            "jpeg": jpeg_path,
        },

        "presence": {
            "raw": raw_path is not None,
            "meta": meta_path is not None,
            "white_point": wp_path is not None,
            "ccm": ccm_path is not None,
            "jpeg": jpeg_path is not None,
        },

        "raw": raw,

        "metadata": {
	    "exposure_time": meta["exposure_time"],
	    "analog_gain": meta["analog_gain"],
	    "aperture": meta["aperture"],
	    "normalized_exposure_s": (
		meta["normalized_exposure_s"]
	    ),
	    "iso": meta["iso"],
	    "privacy_masked": meta["privacy_masked"],

	    "valid": meta["valid"],

	    "required_fields_present": (
		meta["required_fields_present"]
	    ),

	    "optional_fields_present": (
		meta["optional_fields_present"]
	    ),
	},

        "white_point": {
            "rg_ratio": white_point["rg_ratio"],
            "bg_ratio": white_point["bg_ratio"],
            "valid": white_point["valid"],
        },

        "ccm": {
            "matrix": ccm["matrix"],
            "valid": ccm["valid"],
        },
    }

    # Keep parser errors if present.

    if "error" in meta:
        record["metadata"]["error"] = meta["error"]

    if "error" in white_point:
        record["white_point"]["error"] = (
            white_point["error"]
        )

    if "error" in ccm:
        record["ccm"]["error"] = ccm["error"]

    if "error" in raw:
        record["raw"]["error"] = raw["error"]

    return record


# ---------------------------------------------------------------------
# Dataset validation
# ---------------------------------------------------------------------

def validate_manifest(manifest):

    summary = {

        "total_frames": len(manifest),

        "complete_frames": 0,

        "missing": {
            "raw": 0,
            "meta": 0,
            "white_point": 0,
            "ccm": 0,
            "jpeg": 0,
        },

        "invalid": {
            "raw": 0,
            "meta": 0,
            "white_point": 0,
            "ccm": 0,
        },

        "privacy_masked_counts": Counter(),

    }

    for item in manifest:

        presence = item["presence"]

        for key in summary["missing"]:

            if not presence[key]:
                summary["missing"][key] += 1

        for key in summary["invalid"]:

            if not item[
                {
                    "raw": "raw",
                    "meta": "metadata",
                    "white_point": "white_point",
                    "ccm": "ccm",
                }[key]
            ]["valid"]:

                summary["invalid"][key] += 1

        if all(presence.values()):

            summary["complete_frames"] += 1

        privacy = item["metadata"][
            "privacy_masked"
        ]

        if privacy is not None:
            summary["privacy_masked_counts"][
                str(privacy)
            ] += 1

    summary["privacy_masked_counts"] = dict(
        summary["privacy_masked_counts"]
    )

    return summary


# ---------------------------------------------------------------------
# Numerical statistics
# ---------------------------------------------------------------------

def numeric_statistics(manifest):

    fields = [
        "exposure_time",
        "analog_gain",
        "aperture",
        "normalized_exposure_s",
    ]

    statistics = {}

    for field in fields:

        values = []

        for item in manifest:

            value = item["metadata"][field]

            if value is not None:
                values.append(value)

        if not values:
            continue

        values = np.asarray(
            values,
            dtype=np.float64,
        )

        statistics[field] = {

            "count": int(values.size),

            "min": float(values.min()),

            "max": float(values.max()),

            "mean": float(values.mean()),

            "median": float(
                np.median(values)
            ),

            "std": float(values.std()),
        }

    # White point statistics

    for field in [
        "rg_ratio",
        "bg_ratio",
    ]:

        values = []

        for item in manifest:

            value = item["white_point"][field]

            if value is not None:
                values.append(value)

        if not values:
            continue

        values = np.asarray(
            values,
            dtype=np.float64,
        )

        statistics[field] = {

            "count": int(values.size),

            "min": float(values.min()),

            "max": float(values.max()),

            "mean": float(values.mean()),

            "median": float(
                np.median(values)
            ),

            "std": float(values.std()),
        }

    return statistics


# ---------------------------------------------------------------------
# CCM variation analysis
# ---------------------------------------------------------------------

def analyze_ccm(manifest):

    matrices = []

    for item in manifest:

        matrix = item["ccm"]["matrix"]

        if matrix is not None:

            matrices.append(matrix)

    if not matrices:

        return {
            "count": 0
        }

    matrices = np.asarray(
        matrices,
        dtype=np.float64,
    )

    reference = matrices[0]

    differences = np.abs(
        matrices - reference
    )

    return {

        "count": int(len(matrices)),

        "reference_matrix": (
            reference.tolist()
        ),

        "max_absolute_difference_from_first": float(
            differences.max()
        ),

        "mean_absolute_difference_from_first": float(
            differences.mean()
        ),

        "all_identical_to_first": bool(
            np.array_equal(
                matrices,
                reference,
            )
        ),
    }


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Build and validate an "
            "INTEL-TAU RAW dataset manifest"
        )
    )

    parser.add_argument(
        "--root",
        required=True,
        type=Path,
        help="Dataset root directory",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/metadata/intel_tau/"
            "manifest.json"
        ),
        help="Output manifest JSON",
    )

    args = parser.parse_args()

    root = args.root

    if not root.exists():

        raise FileNotFoundError(
            f"Dataset root does not exist:\n{root}"
        )

    print("=" * 70)
    print("INTEL-TAU DATASET MANIFEST BUILDER")
    print("=" * 70)

    print(f"\nDataset root:")
    print(f"  {root}")

    # -------------------------------------------------------------
    # Discover files
    # -------------------------------------------------------------

    files_by_stem = collect_files(root)

    print(
        f"\nUnique file stems found:"
        f" {len(files_by_stem)}"
    )

    # -------------------------------------------------------------
    # Build records
    # -------------------------------------------------------------

    manifest = []

    for stem, files in sorted(
        files_by_stem.items()
    ):

        # A frame is identified by its RAW file.

        if ".plain16" not in files:
            continue

        record = build_record(
            stem,
            files,
        )

        manifest.append(record)

    # -------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------

    summary = validate_manifest(
        manifest
    )

    statistics = numeric_statistics(
        manifest
    )

    ccm_analysis = analyze_ccm(
        manifest
    )

    # -------------------------------------------------------------
    # Print summary
    # -------------------------------------------------------------

    print("\n" + "=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)

    print(
        f"\nRAW frames found       : "
        f"{summary['total_frames']}"
    )

    print(
        f"Complete frames        : "
        f"{summary['complete_frames']}"
    )

    print("\nMissing files:")

    for key, count in summary[
        "missing"
    ].items():

        print(
            f"  {key:15s}: {count}"
        )

    print("\nInvalid files:")

    for key, count in summary[
        "invalid"
    ].items():

        print(
            f"  {key:15s}: {count}"
        )

    # -------------------------------------------------------------
    # Numerical statistics
    # -------------------------------------------------------------

    print("\n" + "=" * 70)
    print("FRAME METADATA STATISTICS")
    print("=" * 70)

    for field, stats in statistics.items():

        print(f"\n{field}")

        print(
            f"  count  : {stats['count']}"
        )

        print(
            f"  min    : {stats['min']:.6f}"
        )

        print(
            f"  max    : {stats['max']:.6f}"
        )

        print(
            f"  mean   : {stats['mean']:.6f}"
        )

        print(
            f"  median : {stats['median']:.6f}"
        )

        print(
            f"  std    : {stats['std']:.6f}"
        )

    # -------------------------------------------------------------
    # Privacy mask
    # -------------------------------------------------------------

    print("\nPrivacy mask values:")

    for value, count in sorted(
        summary[
            "privacy_masked_counts"
        ].items()
    ):

        print(
            f"  {value}: {count}"
        )

    # -------------------------------------------------------------
    # CCM analysis
    # -------------------------------------------------------------

    print("\n" + "=" * 70)
    print("CCM VARIATION")
    print("=" * 70)

    print(
        f"\nMatrices found:"
        f" {ccm_analysis['count']}"
    )

    if ccm_analysis["count"]:

        print(
            "Maximum absolute difference "
            "from first CCM:"
        )

        print(
            f"  "
            f"{ccm_analysis['max_absolute_difference_from_first']:.12f}"
        )

        print(
            "Mean absolute difference "
            "from first CCM:"
        )

        print(
            f"  "
            f"{ccm_analysis['mean_absolute_difference_from_first']:.12f}"
        )

        print(
            "All CCMs identical to first:"
        )

        print(
            f"  "
            f"{ccm_analysis['all_identical_to_first']}"
        )

    # -------------------------------------------------------------
    # Final JSON
    # -------------------------------------------------------------

    output = {

        "dataset": {
            "root": str(root.resolve()),
            "raw_width": RAW_WIDTH,
            "raw_height": RAW_HEIGHT,
            "raw_dtype": "uint16",
            "raw_bytes_per_pixel": (
                RAW_BYTES_PER_PIXEL
            ),
        },

        "summary": summary,

        "statistics": statistics,

        "ccm_analysis": ccm_analysis,

        "frames": manifest,
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        args.output,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
        )

    print("\n" + "=" * 70)

    print(
        f"Manifest saved to:\n"
        f"  {args.output}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
