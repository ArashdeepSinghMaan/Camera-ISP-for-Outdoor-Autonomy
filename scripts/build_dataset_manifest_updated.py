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

# IMPORTANT:
# This threshold is used only to characterize the large black border
# observed in the lab_printouts subset. It is NOT a sensor black-level
# calibration value and must not be used as an ISP BLC parameter.
LAB_PRINTOUT_ROI_THRESHOLD = 10


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
            encoding="utf-8",
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

        # Missing optional fields do NOT make META invalid.
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
# Heuristic ROI analysis for lab_printouts
#
# This is descriptive dataset analysis only.
# It is NOT an official camera ROI and NOT a BLC parameter.
# ---------------------------------------------------------------------

def inspect_lab_printout_roi(path):

    result = {
        "threshold": LAB_PRINTOUT_ROI_THRESHOLD,
        "x_min": None,
        "x_max": None,
        "y_min": None,
        "y_max": None,
        "width": None,
        "height": None,
        "active_percent": None,
        "valid": False,
    }

    try:

        raw = np.fromfile(
            path,
            dtype=RAW_DTYPE,
        )

        expected_pixels = RAW_WIDTH * RAW_HEIGHT

        if raw.size != expected_pixels:

            result["error"] = (
                f"Expected {expected_pixels} pixels, "
                f"found {raw.size}"
            )

            return result

        raw = raw.reshape(
            RAW_HEIGHT,
            RAW_WIDTH,
        )

        mask = raw > LAB_PRINTOUT_ROI_THRESHOLD

        ys, xs = np.where(mask)

        if len(xs) == 0:

            result["error"] = (
                "No pixels above ROI threshold"
            )

            return result

        x_min = int(xs.min())
        x_max = int(xs.max())
        y_min = int(ys.min())
        y_max = int(ys.max())

        result["x_min"] = x_min
        result["x_max"] = x_max
        result["y_min"] = y_min
        result["y_max"] = y_max

        result["width"] = x_max - x_min + 1
        result["height"] = y_max - y_min + 1

        result["active_percent"] = float(
            100.0 * mask.mean()
        )

        result["valid"] = True

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

    # The subset is the immediate parent directory of the RAW file.
    subset = None

    if raw_path is not None:
        subset = Path(raw_path).parent.name

    meta = parse_meta(meta_path)
    white_point = parse_white_point(wp_path)
    ccm = parse_ccm(ccm_path)
    raw = inspect_raw(raw_path)

    record = {

        "scene_id": stem,

        "subset": subset,

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

    # -------------------------------------------------------------
    # Dataset-specific descriptive analysis
    # -------------------------------------------------------------

    if subset == "lab_printouts":

        record["analysis"] = {
            "heuristic_roi": inspect_lab_printout_roi(
                raw_path
            )
        }

    # -------------------------------------------------------------
    # Keep parser errors if present
    # -------------------------------------------------------------

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

        "subset_counts": Counter(),

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

        "meta_optional_field_counts": {
            "iso": 0,
            "privacy_masked": 0,
        },

        "privacy_masked_values": Counter(),
    }

    for item in manifest:

        subset = item.get("subset")

        if subset is not None:
            summary["subset_counts"][subset] += 1

        presence = item["presence"]

        for key in summary["missing"]:

            if not presence[key]:
                summary["missing"][key] += 1

        for key in summary["invalid"]:

            mapping = {
                "raw": "raw",
                "meta": "metadata",
                "white_point": "white_point",
                "ccm": "ccm",
            }

            field = mapping[key]

            if not item[field]["valid"]:
                summary["invalid"][key] += 1

        if all(presence.values()):

            summary["complete_frames"] += 1

        optional_fields = item[
            "metadata"
        ]["optional_fields_present"]

        if optional_fields["iso"]:
            summary[
                "meta_optional_field_counts"
            ]["iso"] += 1

        if optional_fields["privacy_masked"]:
            summary[
                "meta_optional_field_counts"
            ]["privacy_masked"] += 1

        privacy = item[
            "metadata"
        ]["privacy_masked"]

        if privacy is not None:
            summary[
                "privacy_masked_values"
            ][str(privacy)] += 1

    summary["subset_counts"] = dict(
        summary["subset_counts"]
    )

    summary["privacy_masked_values"] = dict(
        summary["privacy_masked_values"]
    )

    return summary


# ---------------------------------------------------------------------
# Numerical metadata statistics
# ---------------------------------------------------------------------

def numeric_statistics(manifest):

    fields = [
        "exposure_time",
        "analog_gain",
        "aperture",
        "normalized_exposure_s",
        "iso",
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
# lab_printouts ROI variation analysis
# ---------------------------------------------------------------------

def analyze_lab_printouts_roi(manifest):

    records = []

    for item in manifest:

        if item.get("subset") != "lab_printouts":
            continue

        roi = (
            item
            .get("analysis", {})
            .get("heuristic_roi")
        )

        if roi is None or not roi.get("valid"):
            continue

        records.append(roi)

    if not records:

        return {
            "frames_analyzed": 0,
            "threshold": LAB_PRINTOUT_ROI_THRESHOLD,
        }

    result = {
        "frames_analyzed": len(records),
        "threshold": LAB_PRINTOUT_ROI_THRESHOLD,
    }

    for field in [
        "x_min",
        "x_max",
        "y_min",
        "y_max",
        "width",
        "height",
        "active_percent",
    ]:

        values = np.asarray(
            [
                record[field]
                for record in records
            ],
            dtype=np.float64,
        )

        result[field] = {
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "median": float(
                np.median(values)
            ),
            "unique_count": int(
                np.unique(values).size
            ),
        }

    return result


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

    print("\nDataset root:")
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
    # Validation and analysis
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

    lab_printouts_roi = (
        analyze_lab_printouts_roi(
            manifest
        )
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

    print("\nDataset subsets:")

    for subset, count in sorted(
        summary["subset_counts"].items()
    ):

        print(
            f"  {subset:20s}: {count}"
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
    # Optional META fields
    # -------------------------------------------------------------

    print("\n" + "=" * 70)
    print("META OPTIONAL FIELD PRESENCE")
    print("=" * 70)

    total = summary["total_frames"]

    for field, count in summary[
        "meta_optional_field_counts"
    ].items():

        print(
            f"\n{field:20s}: "
            f"{count} / {total}"
        )

    print("\nPrivacy mask values:")

    for value, count in sorted(
        summary[
            "privacy_masked_values"
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
    # lab_printouts ROI analysis
    # -------------------------------------------------------------

    print("\n" + "=" * 70)
    print("LAB_PRINTOUTS HEURISTIC ROI ANALYSIS")
    print("=" * 70)

    print(
        f"\nFrames analyzed:"
        f" {lab_printouts_roi['frames_analyzed']}"
    )

    print(
        f"Threshold:"
        f" raw > {lab_printouts_roi['threshold']}"
    )

    for field in [
        "x_min",
        "x_max",
        "y_min",
        "y_max",
        "width",
        "height",
        "active_percent",
    ]:

        stats = lab_printouts_roi.get(field)

        if not isinstance(stats, dict):
            continue

        print(f"\n{field}")

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
            f"  unique : {stats['unique_count']}"
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
            "subsets": summary[
                "subset_counts"
            ],
        },

        "summary": summary,

        "statistics": statistics,

        "ccm_analysis": ccm_analysis,

        "lab_printouts_roi_analysis": (
            lab_printouts_roi
        ),

        "notes": {
            "lab_printouts_roi": (
                "Heuristic descriptive analysis only. "
                "The threshold-based ROI is not an "
                "official camera ROI and must not be "
                "used as a black-level correction "
                "parameter without further validation."
            )
        },

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
