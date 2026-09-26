# Camera ISP Project --- Phase 2 Report

## RAW Data Ingestion and Validation

**Project:** Adaptive Image Signal Processing for Robust Outdoor Robotic
Perception\
**Phase:** Phase 2 --- RAW Data Ingestion and Validation\
**Dataset:** Sony IMX135 / INTEL-TAU Camera Dataset\
**Status:** COMPLETE

------------------------------------------------------------------------

## 1. Phase Objective

Phase 2 established a reliable and validated software interface for
reading the camera's RAW sensor data and associated frame metadata.

The objective was deliberately narrow:

> Build a trustworthy RAW ingestion layer before performing any
> Bayer-domain image processing.

This phase therefore focused on:

-   defining the RAW data representation,
-   implementing a reusable RAW reader,
-   validating dimensions and file size,
-   enforcing explicit Bayer-pattern information,
-   loading optional frame metadata,
-   validating metadata structure and required fields,
-   handling malformed input deterministically,
-   and testing the implementation on both valid and invalid inputs.

No ISP operation such as black-level correction, white balance,
demosaicing, color correction, gamma, or tone mapping was performed in
this phase.

The result is the foundation on which the subsequent Bayer-domain ISP
stages can operate.

------------------------------------------------------------------------

# 2. Dataset Context

The project uses the Sony IMX135 portion of the INTEL-TAU dataset.

The local dataset root is:

``` text
/media/hitech/WD_Access/Camera_ISP/Sony_IMX135
```

The dataset contains frame bundles consisting of RAW sensor data,
metadata, white-point information, color-correction information, and a
JPEG reference image.

A representative bundle is:

``` text
S_IMX135_field3cam_001.plain16
S_IMX135_field3cam_001.meta
S_IMX135_field3cam_001.wp
S_IMX135_field3cam_001.ccm
S_IMX135_field3cam_001.jpg
```

For Phase 2, only the `.plain16` RAW file and `.meta` metadata file were
directly relevant.

------------------------------------------------------------------------

# 3. RAW Data Representation

## 3.1 RAW file format

The Sony IMX135 RAW files use the `.plain16` extension.

The RAW sensor samples are stored as 16-bit unsigned integer values.

The validated camera resolution is:

``` text
Width  = 3264 pixels
Height = 2448 pixels
```

Therefore:

``` text
Number of pixels
= 3264 × 2448
= 7,990,272 pixels
```

Because every pixel occupies 2 bytes:

``` text
Expected file size
= 7,990,272 × 2
= 15,980,544 bytes
```

A representative RAW file was confirmed to have exactly this size.

This provides an important integrity check: the reader can reject files
whose byte count does not correspond to the expected image dimensions.

------------------------------------------------------------------------

# 4. RAW Reader Design

The RAW reader was implemented in:

``` text
camera_isp/io/raw_reader.py
```

The design intentionally keeps the RAW representation simple and
explicit.

The reader produces a `RawImage` data structure containing:

-   RAW pixel array,
-   width,
-   height,
-   Bayer pattern,
-   source path,
-   NumPy dtype,
-   optional metadata.

The resulting representation is conceptually:

``` text
RawImage
├── data
├── width
├── height
├── bayer_pattern
├── path
├── dtype
└── metadata
```

The RAW pixel array is represented as:

``` python
numpy.ndarray
```

with:

``` text
dtype = uint16
shape = (2448, 3264)
```

This preserves the original integer sensor representation during
ingestion.

------------------------------------------------------------------------

# 5. Bayer Pattern Handling

The RAW image is not a conventional RGB image.

It contains a Bayer color filter array, meaning each sensor pixel
represents one color component.

The reader therefore requires the Bayer pattern to be explicit.

Supported patterns are:

``` text
RGGB
BGGR
GRBG
GBRG
```

For the Sony IMX135 dataset used in this project, the validated Bayer
arrangement is:

``` text
GRBG
```

The beginning of the Bayer arrangement is:

``` text
G R G R G R ...
B G B G B G ...
G R G R G R ...
B G B G B G ...
```

The reader does not silently guess a Bayer pattern.

This is important because an incorrect Bayer pattern can produce an
apparently valid image while swapping or corrupting color information
downstream.

------------------------------------------------------------------------

# 6. RAW Reader Validation

The RAW reader performs several validation steps before returning a
frame.

## 6.1 Path validation

The supplied path must exist and refer to a file.

Invalid paths are rejected rather than producing confusing NumPy or
downstream errors.

------------------------------------------------------------------------

## 6.2 Dimension validation

The image dimensions must be positive.

Because Bayer processing operates on a two-dimensional pixel lattice,
even dimensions are required.

For the dataset:

``` text
3264 × 2448
```

satisfies this requirement.

------------------------------------------------------------------------

## 6.3 Bayer-pattern validation

The Bayer pattern must belong to:

``` text
RGGB
BGGR
GRBG
GBRG
```

Unsupported or misspelled patterns are rejected.

This makes the color-filter interpretation an explicit part of the data
contract.

------------------------------------------------------------------------

## 6.4 File-size validation

The reader verifies that the RAW file contains exactly:

``` text
width × height
```

16-bit values.

Equivalently:

``` text
file_size = width × height × 2 bytes
```

This catches incomplete, truncated, or incorrectly interpreted RAW files
before image processing begins.

------------------------------------------------------------------------

## 6.5 Data-type validation

The RAW data is loaded as:

``` python
np.uint16
```

rather than immediately converting to floating point.

This preserves the original sensor-domain representation.

Floating-point conversion is deferred to ISP stages that actually
require it.

------------------------------------------------------------------------

# 7. `RawImage` Data Model

The Phase 2 implementation introduced a small data model:

``` python
@dataclass
class RawImage:
    data: np.ndarray
    width: int
    height: int
    bayer_pattern: str
    path: Path
    dtype: np.dtype
    metadata: Optional[dict] = None
```

Convenience properties were also provided for:

``` text
shape
min
max
mean
```

This gives downstream modules a consistent object instead of passing
independent arrays and configuration variables throughout the pipeline.

------------------------------------------------------------------------

# 8. Metadata Reader

The second major component of Phase 2 was the metadata parser:

``` text
camera_isp/io/metadata_reader.py
```

The local dataset uses `.meta` files.

A representative metadata file contains:

``` text
exposure_time 0.042203
analog_gain 4.196721
aperture 2.4
normalized_exposure_s 0.056677
privacy_masked 1
```

The parser converts these values into a Python dictionary with
appropriate numeric types.

------------------------------------------------------------------------

# 9. Required Metadata Fields

The parser defines four required fields:

``` text
exposure_time
analog_gain
aperture
normalized_exposure_s
```

These are considered necessary for a valid frame metadata record in the
current project.

The parser does not require every optional field to be present.

------------------------------------------------------------------------

# 10. Optional Metadata Fields

The following fields were observed as optional:

``` text
iso
privacy_masked
```

This distinction was important because the initial dataset inspection
showed that not every metadata record necessarily contains the same
optional information.

The parser was therefore corrected so that the required schema is
limited to the fields that are actually mandatory.

------------------------------------------------------------------------

# 11. Metadata Validation

The metadata parser performs structural validation.

It rejects:

-   missing required fields,
-   duplicate fields,
-   unknown fields,
-   malformed numeric values,
-   malformed metadata lines.

This prevents silently accepting corrupted metadata.

The philosophy is:

``` text
bad metadata
    ↓
fail early
    ↓
fix dataset/input
```

rather than:

``` text
bad metadata
    ↓
silently guess
    ↓
produce scientifically questionable ISP results
```

------------------------------------------------------------------------

# 12. Frame-Level Validation

The combination of the RAW reader and metadata reader establishes a
frame-level contract.

A valid frame should contain:

``` text
RAW
 ├── correct dimensions
 ├── correct byte count
 ├── uint16 samples
 └── explicit Bayer pattern

META
 ├── exposure_time
 ├── analog_gain
 ├── aperture
 └── normalized_exposure_s
```

Optional fields may also be present.

This provides a stable input boundary for the ISP pipeline.

------------------------------------------------------------------------

# 13. Positive Tests

The implementation was tested using valid RAW and metadata inputs.

The tests confirmed that:

-   valid RAW files can be loaded,
-   the output has the expected shape,
-   the dtype is `uint16`,
-   the Bayer pattern is preserved,
-   metadata is loaded correctly,
-   valid optional metadata fields are accepted.

For the representative Sony IMX135 frame:

``` text
RAW shape = (2448, 3264)
dtype     = uint16
```

The dimensions agree with the known sensor image size.

------------------------------------------------------------------------

# 14. Negative Tests

Negative tests were also implemented.

The reader/parser was tested against invalid conditions including:

``` text
invalid path
invalid dimensions
odd dimensions
unsupported Bayer pattern
incorrect RAW file size
missing metadata fields
duplicate metadata fields
unknown metadata fields
malformed metadata values
```

The expected behavior was confirmed: invalid input is rejected rather
than silently interpreted.

This is particularly important for a research pipeline because a silent
input error can propagate into later quantitative experiments and
invalidate comparisons.

------------------------------------------------------------------------

# 15. Why This Phase Matters for ISP Research

It can be tempting to start directly with operations such as:

``` text
RAW → demosaic → RGB
```

However, an ISP experiment is only meaningful when the input
representation is well defined.

For example, if the RAW reader accidentally:

-   interprets the wrong dimensions,
-   uses the wrong dtype,
-   shifts byte alignment,
-   assumes an incorrect Bayer pattern,
-   or silently accepts a truncated file,

then later observations about white balance, color correction, noise, or
perception robustness may be attributed to the ISP even though the
problem originated at the input stage.

Phase 2 therefore establishes the data integrity boundary:

``` text
                Phase 2
                    │
                    ▼
        ┌─────────────────────┐
        │ Validated RAW Input │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Validated Metadata  │
        └──────────┬──────────┘
                   │
                   ▼
             Phase 3 ISP
```

------------------------------------------------------------------------

# 16. Separation of Responsibilities

One design decision from Phase 2 is to keep ingestion separate from ISP
processing.

The architecture is:

``` text
camera_isp/
├── io/
│   ├── raw_reader.py
│   └── metadata_reader.py
│
├── raw/
│   └── ...
│
└── isp/
    └── ...
```

The `io` layer answers:

> What data did the camera provide?

The ISP layer answers:

> How should that sensor data be processed?

This separation makes later experiments easier to reproduce.

For example, the same RAW frame can be passed through:

``` text
fixed ISP
adaptive ISP
learning-based ISP
```

without changing the ingestion layer.

------------------------------------------------------------------------

# 17. Phase 2 Technical Lessons

## 17.1 RAW is not RGB

The `.plain16` file represents sensor measurements, not a
ready-to-display color image.

The pixel values must therefore be interpreted according to the camera's
Bayer pattern.

------------------------------------------------------------------------

## 17.2 Metadata is part of the imaging signal context

Exposure and gain affect how the RAW values should be interpreted.

They become particularly important later when investigating:

-   black level,
-   sensor noise,
-   dynamic range,
-   exposure-dependent behavior,
-   adaptive ISP control.

------------------------------------------------------------------------

## 17.3 Bayer pattern must be explicit

A Bayer pattern is not something the processing pipeline should guess
casually.

The Phase 2 reader therefore requires an explicit supported pattern.

------------------------------------------------------------------------

## 17.4 Input validation is part of the ISP pipeline

For research work, data validation is not merely software hygiene.

It protects the validity of later experiments.

A reproducible ISP pipeline should know exactly:

``` text
what was read
how it was interpreted
which metadata accompanied it
and whether the input passed validation
```

------------------------------------------------------------------------

# 18. Implemented Files

The main Phase 2 implementation files are:

``` text
camera_isp/
└── io/
    ├── raw_reader.py
    └── metadata_reader.py
```

Associated testing scripts were used to validate:

``` text
RAW loading
metadata parsing
positive cases
negative cases
```

------------------------------------------------------------------------

# 19. Phase 2 Final Architecture

At the completion of Phase 2, the project has the following validated
flow:

``` text
                 Dataset
                    │
                    ▼
             ┌─────────────┐
             │ .plain16    │
             │ RAW sensor  │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │ RAW Reader  │
             └──────┬──────┘
                    │
                    │
             ┌──────▼──────┐
             │  RawImage   │
             │ uint16 RAW  │
             │ 3264×2448   │
             │ Bayer=GRBG  │
             └──────┬──────┘
                    │
                    │
             ┌──────▼──────┐
             │ .meta       │
             │ Metadata    │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │  Metadata   │
             │   Reader    │
             └──────┬──────┘
                    │
                    ▼
             Validated Frame
                    │
                    ▼
              Phase 3 ISP
```

------------------------------------------------------------------------

# 20. Phase 2 Completion Criteria

  Criterion                           Status
  ----------------------------------- --------
  RAW reader implemented              PASS
  RAW dtype validated                 PASS
  RAW dimensions validated            PASS
  RAW file-size validation            PASS
  Explicit Bayer-pattern validation   PASS
  `RawImage` data model               PASS
  Metadata reader implemented         PASS
  Required metadata validation        PASS
  Optional metadata handling          PASS
  Duplicate-field rejection           PASS
  Unknown-field rejection             PASS
  Malformed-value rejection           PASS
  Positive tests                      PASS
  Negative tests                      PASS

------------------------------------------------------------------------

# 21. Limitations

Phase 2 intentionally does **not** establish:

-   sensor black-level calibration,
-   white-balance calibration,
-   color correction,
-   demosaicing quality,
-   noise characterization,
-   exposure normalization,
-   tone mapping,
-   or perception performance.

Those questions belong to later phases.

In particular, the RAW reader validates the representation; it does not
claim that the numerical RAW values have already been photometrically
calibrated.

------------------------------------------------------------------------

# 22. Transition to Phase 3

With RAW ingestion and metadata validation complete, the project can
safely move into Bayer-domain signal processing.

The next phase investigates the sensor signal itself:

``` text
Validated RAW
     │
     ├── Bayer channel structure
     │
     ├── low-end / black-level behavior
     │
     ├── white-point information
     │
     └── demosaicing
```

Phase 3 subsequently implemented and characterized:

``` text
Bayer extraction
        ↓
Black-level characterization
        ↓
Black-level correction
        ↓
White-point characterization
        ↓
White balance
        ↓
Demosaicing
        ↓
Integrated Bayer-domain mini-ISP
```

The key principle carried forward is:

> Characterize the sensor data first, implement the processing second,
> and validate the implementation on real RAW frames before moving to
> the next ISP stage.

------------------------------------------------------------------------

# 23. Final Status

**Phase 2 --- RAW Data Ingestion and Validation: COMPLETE**

The project now has a validated RAW/metadata ingestion layer for the
Sony IMX135 dataset.

The output of Phase 2 is a trustworthy sensor-domain representation that
can be consumed by the Bayer-domain ISP modules developed in Phase 3.

**Next major stage:** Phase 4 --- Color Correction / CCM.
