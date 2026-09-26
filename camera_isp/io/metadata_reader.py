from pathlib import Path
from typing import Dict


# These fields are present in every valid .meta file.
REQUIRED_FIELDS = {
    "exposure_time",
    "analog_gain",
    "aperture",
    "normalized_exposure_s",
}

# These fields may or may not be present.
OPTIONAL_FIELDS = {
    "iso",
    "privacy_masked",
}


def parse_metadata(path) -> Dict:
    """
    Read and validate a Sony IMX135 .meta file.

    Returns
    -------
    dict
        Parsed camera metadata.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Metadata file does not exist:\n{path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Metadata path is not a file:\n{path}"
        )

    metadata = {}

    with path.open("r") as f:
        for line_number, line in enumerate(f, start=1):

            line = line.strip()

            # Ignore empty lines.
            if not line:
                continue

            parts = line.split()

            if len(parts) != 2:
                raise ValueError(
                    f"Invalid metadata format at line {line_number}: "
                    f"{line!r}"
                )

            key, value = parts

            if key in metadata:
                raise ValueError(
                    f"Duplicate metadata field {key!r} "
                    f"at line {line_number}"
                )

            # All known metadata values in this dataset are numeric.
            try:
                if key == "privacy_masked":
                    metadata[key] = int(value)
                elif key == "iso":
                    metadata[key] = float(value)
                else:
                    metadata[key] = float(value)

            except ValueError as exc:
                raise ValueError(
                    f"Invalid value for metadata field {key!r} "
                    f"at line {line_number}: {value!r}"
                ) from exc

    # ---------------------------------------------------------
    # Validate required fields
    # ---------------------------------------------------------

    missing = REQUIRED_FIELDS - metadata.keys()

    if missing:
        raise ValueError(
            "Metadata is missing required fields: "
            + ", ".join(sorted(missing))
        )

    # ---------------------------------------------------------
    # Validate unknown fields
    # ---------------------------------------------------------

    known_fields = REQUIRED_FIELDS | OPTIONAL_FIELDS

    unknown = set(metadata.keys()) - known_fields

    if unknown:
        raise ValueError(
            "Unknown metadata fields: "
            + ", ".join(sorted(unknown))
        )

    return metadata
