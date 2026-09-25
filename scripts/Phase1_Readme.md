# Phase 1 — INTEL-TAU Dataset & RAW Sensor Characterization

## 1. Objective

The objective of Phase 1 is to understand the INTEL-TAU dataset at the **sensor-data level** before implementing any ISP algorithm.

We do not begin with demosaicing, white balance, tone mapping, denoising, or color correction in this phase.

Instead, we first establish:

* Dataset organization
* Camera-specific data
* Scene categories
* File formats
* RAW file structure
* RAW dimensions
* RAW datatype
* Bayer pattern
* Sensor value range
* Exposure metadata
* Bayer-channel statistics
* White-point information
* Color-correction matrix
* Frame-level correspondence
* Dataset manifest

The goal is to understand exactly what the camera produced before deciding how the ISP should process it.

---

# 2. Dataset

The initial development dataset selected for RAW ISP research is **INTEL-TAU**.

For the current implementation, we are working with the Sony IMX135 camera subset.

Local dataset:

```text
/media/hitech/WD_Access/Camera_ISP/Sony_IMX135
```

Repository:

```text
/media/hitech/WD_Access/Camera_ISP/Repo
```

Python environment:

```text
.venv
```

---

# 3. Dataset Structure Found Locally

The local Sony IMX135 dataset contains three major scene categories:

```text
Sony_IMX135/
├── field_3_cameras/
├── lab_printouts/
└── lab_realscene/
```

The complete local scan identified:

```text
Total files: 2322
```

The file extensions are:

```text
.plain16
.meta
.wp
.ccm
.jpg
.py
.png
```

The primary dataset files are:

```text
.plain16   → RAW sensor data
.meta      → frame exposure metadata
.wp        → white-point information
.ccm       → color correction matrix
.jpg       → reference/processed image
```

There are:

```text
464 .plain16
464 .meta
464 .wp
464 .ccm
464 .jpg
```

plus one `.py` and one `.png` file in the scanned dataset.

---

# 4. Scene Category Distribution

The local scan found:

## field_3_cameras

```text
721 files
```

with approximately:

```text
144 .plain16
144 .meta
144 .wp
144 .ccm
144 .jpg
```

and one additional `.png`.

## lab_printouts

```text
1500 files
```

with:

```text
300 .plain16
300 .meta
300 .wp
300 .ccm
300 .jpg
```

## lab_realscene

```text
100 files
```

with:

```text
20 .plain16
20 .meta
20 .wp
20 .ccm
20 .jpg
```

This confirms that the dataset is organized into **scene/frame bundles**, rather than isolated RAW images.

---

# 5. Frame-Level File Correspondence

A typical frame is:

```text
S_IMX135_field3cam_001.plain16
S_IMX135_field3cam_001.meta
S_IMX135_field3cam_001.wp
S_IMX135_field3cam_001.ccm
S_IMX135_field3cam_001.jpg
```

The common filename stem:

```text
S_IMX135_field3cam_001
```

is therefore the key used to associate the different data products belonging to the same frame.

This is important because the ISP experiment must eventually operate on a synchronized bundle:

```text
                  Frame ID
                     │
        ┌────────────┼────────────┐
        │            │            │
       RAW          META          WP
        │                         │
        │                         │
       CCM                       JPEG
        │                         │
        └────────────┬────────────┘
                     │
              ISP experiment
```

---

# 6. Scripts Created During Phase 1

The following inspection utilities were created:

```text
scripts/
├── inspect_dataset.py
├── inspect_cameras.py
├── inspect_metadata.py
├── inspect_raw.py
├── inspect_bayer.py
├── inspect_white_point.py
├── inspect_ccm.py
├── visualize_raw.py
├── build_dataset_manifest.py
└── generate_dataset_report.py
```

Each script has a specific purpose.

---

# 7. `inspect_dataset.py`

Purpose:

Perform a complete recursive scan of the dataset.

It reports:

* Number of files
* Total dataset size
* File extensions
* Top-level directories
* File counts

It also produces a JSON dataset scan.

Expected output:

```text
data/metadata/intel_tau/dataset_scan.json
```

This was the first tool used to establish what actually exists in the local dataset.

---

# 8. `inspect_cameras.py`

Purpose:

Understand the camera/scene directory organization.

For the current Sony dataset it established:

```text
field_3_cameras
lab_printouts
lab_realscene
```

and counted the different file types within each category.

This confirmed that the local dataset structure differs somewhat from the structure described in some INTEL-TAU documentation.

---

# 9. Important Issue: `.mat` vs `.meta`

Initially, the metadata inspection script was written assuming that the dataset contained MATLAB `.mat` metadata files.

The first implementation used:

```python
scipy.io.loadmat()
```

However, the local Sony IMX135 dataset contains:

```text
.meta
```

files rather than the expected `.mat` files.

An incorrect version of `inspect_raw.py` also attempted to interpret a `.plain16` file as a MATLAB file, resulting in:

```text
ValueError: read length must be non-negative or -1
```

The cause was not corrupted RAW data.

The problem was that the wrong inspection script was being executed.

The scripts were subsequently separated into:

```text
inspect_metadata.py
```

for `.meta` files and:

```text
inspect_raw.py
```

for `.plain16` RAW files.

This distinction is important and should be preserved.

---

# 10. `.meta` File Investigation

The following file was inspected:

```text
S_IMX135_field3cam_001.meta
```

File size:

```text
115 bytes
```

Contents:

```text
exposure_time       0.042203
analog_gain         4.196721
aperture            2.400000
normalized_exposure_s 0.056677
privacy_masked      1
```

The `.meta` file is therefore **frame exposure metadata**, not the RAW geometry/Bayer-format metadata we initially expected.

The current interpretation is:

| Field                 |    Value |
| --------------------- | -------: |
| exposure_time         | 0.042203 |
| analog_gain           | 4.196721 |
| aperture              |      2.4 |
| normalized_exposure_s | 0.056677 |
| privacy_masked        |        1 |

The metadata is potentially valuable later for adaptive ISP experiments because exposure conditions can be related to the RAW signal.

However, Phase 1 does not yet use these values to classify scenes or adapt ISP parameters.

---

# 11. RAW Format

The `.plain16` file was identified as the actual RAW Bayer sensor data.

Example:

```text
S_IMX135_field3cam_001.plain16
```

The RAW was successfully loaded using:

```python
np.fromfile(
    path,
    dtype=np.uint16
)
```

The RAW dimensions used for the Sony IMX135 dataset are:

```text
Width  = 3264
Height = 2448
```

Therefore:

```text
Pixels = 3264 × 2448
       = 7,990,272 pixels
```

The file stores:

```text
2 bytes/pixel
```

so the expected file size is:

```text
3264 × 2448 × 2
= 15,980,544 bytes
```

The actual file size was:

```text
15,980,544 bytes
```

Therefore the RAW file-size consistency check passed.

---

# 12. RAW Loading Verification

The inspected frame produced:

```text
dtype:
uint16

shape:
(2448, 3264)

elements:
7,990,272
```

This confirms that the RAW file can be correctly represented as:

```text
RAW[2448, 3264]
```

with one sensor sample per pixel.

No demosaicing has been performed at this point.

---

# 13. RAW Statistics

For:

```text
S_IMX135_field3cam_001.plain16
```

the measured statistics were:

```text
Minimum : 54
Maximum : 1023
Mean    : 210.413
Median  : 181
Std     : 108.771
```

Percentiles:

```text
0%      : 54
0.1%    : 70
1%      : 75
5%      : 88
25%     : 131
50%     : 181
75%     : 258
95%     : 442
99%     : 546
99.9%   : 598
100%    : 1023
```

These values describe the **sensor-domain signal** before any ISP processing.

---

# 14. Important RAW Observation: Sensor Range

The Sony RAW data uses a 10-bit signal range represented inside a `uint16` container.

The meaningful nominal range being used for this dataset is:

```text
0 ─────────────── 1023
```

The observed maximum is:

```text
1023
```

which confirms that some pixels reach the upper sensor limit.

However:

```text
99.9 percentile = 598
```

while:

```text
maximum = 1023
```

Therefore, only a small fraction of pixels are reaching the maximum in this particular frame.

This is useful for later investigation of:

* clipping
* saturation
* highlight preservation
* exposure
* tone mapping
* HDR scenes

But no conclusions about scene illumination should be drawn from this single frame alone.

---

# 15. Bayer Pattern

The Sony IMX135 RAW was investigated using the Bayer arrangement:

```text
G R
B G
```

This is represented internally in the code as:

```text
GRBG
```

Some dataset/documentation terminology may represent the same arrangement as:

```text
GR_BG
```

These are not different Bayer arrangements in this context.

Our canonical internal representation is:

```text
GRBG
```

with:

```text
G1 R
B  G2
```

The Bayer extraction implementation is:

```python
"GRBG": {
    "G1": (0, 0),
    "R":  (0, 1),
    "B":  (1, 0),
    "G2": (1, 1),
}
```

The code can optionally accept:

```text
GR_BG
```

as an alias for:

```text
GRBG
```

---

# 16. Bayer Channel Statistics

The Bayer planes extracted from the inspected RAW frame have dimensions:

```text
1224 × 1632
```

for each channel.

Measured statistics:

| Channel | Min |  Max |    Mean | Median |     Std |
| ------- | --: | ---: | ------: | -----: | ------: |
| G1      |  67 | 1023 | 252.332 |    216 | 122.845 |
| R       |  62 | 1023 | 174.721 |    143 |  83.091 |
| B       |  54 | 1023 | 162.654 |    152 |  58.375 |
| G2      |  67 | 1023 | 251.947 |    217 | 122.001 |

One useful observation is that:

```text
G1 mean = 252.332
G2 mean = 251.947
```

so the two green planes are very close for this frame.

Their medians are also close:

```text
G1 = 216
G2 = 217
```

This does not by itself establish sensor calibration quality, but it is a useful baseline for later analysis.

---

# 17. Important Observation About Black Level

The nominal black level being investigated for this sensor is approximately:

```text
64
```

However, the observed RAW minimum is:

```text
54
```

Therefore:

```text
minimum RAW < nominal black level
```

This is an important observation.

It means we should **not blindly implement**:

```python
raw_uint16 - 64
```

without understanding how negative corrected values should be represented and handled.

For example:

```text
RAW = 54

54 - 64 = -10
```

Therefore any real BLC implementation must first convert the RAW data to a suitable signed or floating-point representation.

This issue is documented here for investigation in the next ISP stage; BLC itself is **not part of Phase 1 yet**.

---

# 18. RAW Visualization

A dedicated script was created:

```text
scripts/visualize_raw.py
```

The visualization performs:

```text
.plain16
   ↓
uint16 RAW
   ↓
H × W Bayer array
   ↓
display normalization
   ↓
visualization
```

The display normalization is:

```text
display = (RAW - black_level)
          ----------------------
          saturation - black_level
```

with the current display parameters:

```text
black level = 64
saturation  = 1023
```

This normalization is **only for visualization**.

It is not the implementation of Black-Level Correction.

---

# 19. Important Distinction: Visualization vs ISP Processing

The visualization script must not modify the actual RAW data.

The correct conceptual flow is:

```text
Original RAW
    │
    ├───────────────→ ISP processing
    │
    │
    └───────────────→ Visualization
```

The visualization may normalize or rotate the displayed image.

The ISP pipeline must preserve the original RAW indexing unless a specific processing stage requires otherwise.

---

# 20. RAW Orientation

During early investigation, an existing RAW visualization used:

```python
np.rot90(raw, 2)
```

to rotate the image by 180°.

This raised an important distinction.

A display rotation is not necessarily a RAW-coordinate transformation.

Therefore we distinguish:

```text
RAW memory / sensor indexing
```

from:

```text
physical/display orientation
```

The current visualization script supports an optional:

```text
--rotate-display
```

argument.

When enabled, only the displayed image is rotated.

The underlying Bayer indexing remains unchanged.

This is important because changing RAW orientation without updating the Bayer pattern can effectively change the interpretation of the Bayer mosaic.

---

# 21. Current RAW Processing Understanding

At the end of the current investigation, we understand the beginning of the ISP pipeline as:

```text
              Sensor
                │
                ▼
         Bayer RAW signal
                │
                │
          .plain16 file
                │
                ▼
            uint16
                │
                ▼
         H × W RAW array
                │
                ▼
            GRBG Bayer
                │
                ▼
       ┌──────────────────┐
       │ ISP starts here  │
       └──────────────────┘
```

The actual ISP operations have **not yet been implemented**.

---

# 22. White Point `.wp`

The dataset also provides:

```text
.wp
```

files.

The planned inspection tool is:

```text
scripts/inspect_white_point.py
```

The purpose is to determine the exact values stored in the `.wp` file and understand how they relate to the sensor's color channels.

This step has **not yet been completed**.

---

# 23. Color Correction Matrix `.ccm`

The dataset also provides:

```text
.ccm
```

files.

The planned inspection tool is:

```text
scripts/inspect_ccm.py
```

The expected structure is a 3×3 color correction matrix represented by nine values.

This step has **not yet been completed**.

An important methodological point is that the CCM supplied by INTEL-TAU should not automatically be treated as perfect ground-truth color calibration. It needs to be understood in the context of how the dataset generated and selected it.

Therefore we will inspect the actual values first before deciding how they are used in our ISP experiments.

---

# 24. JPEG Reference

Each frame also contains a:

```text
.jpg
```

image.

This image is important because it provides an already processed representation of the same scene/frame.

Conceptually:

```text
RAW
 │
 │ camera ISP
 ▼
JPEG
```

The JPEG will eventually allow us to compare:

```text
Our ISP output
        vs
Dataset JPEG
```

However, the JPEG should not automatically be treated as a perfect ground-truth image.

It is a processed image and therefore includes the effects of the original camera processing pipeline.

---

# 25. Dataset Manifest

The planned script:

```text
scripts/build_dataset_manifest.py
```

will create a frame-level table such as:

```text
frame_id
camera
scene
raw_path
meta_path
wp_path
ccm_path
jpg_path
```

For example:

```text
S_IMX135_field3cam_001
```

should resolve to:

```text
.plain16
.meta
.wp
.ccm
.jpg
```

This manifest will become the foundation for reproducible experiments.

The manifest has not yet been fully validated against all naming patterns in the dataset.

Therefore it should be treated as a **first-pass tool**, not yet the final dataset indexing system.

---

# 26. Dataset Report

The planned script:

```text
scripts/generate_dataset_report.py
```

will consolidate the inspection results into a human-readable dataset report.

The final Phase 1 report should contain:

* Dataset overview
* Camera information
* Scene categories
* File counts
* File formats
* RAW dimensions
* Bayer information
* Metadata fields
* White-point information
* CCM information
* Sample RAW statistics
* Dataset consistency checks

This has not yet been finalized.

---

# 27. Current Phase 1 Status

```text
[x] Download/access INTEL-TAU
[x] Identify actual local dataset root
[x] Scan dataset
[x] Identify file extensions
[x] Identify scene categories
[x] Identify Sony IMX135 subset
[x] Establish frame filename correspondence
[x] Inspect .meta format
[x] Identify exposure metadata
[x] Identify RAW dimensions
[x] Verify RAW file size
[x] Read .plain16 as uint16
[x] Reshape RAW frame
[x] Calculate RAW statistics
[x] Identify Bayer representation
[x] Extract Bayer planes
[x] Calculate Bayer-channel statistics
[x] Create RAW visualization
[x] Separate RAW indexing from display orientation

[ ] Inspect .wp
[ ] Understand .wp semantics
[ ] Inspect .ccm
[ ] Understand .ccm semantics
[ ] Validate RAW/Bayer information against dataset metadata/documentation
[ ] Build complete frame manifest
[ ] Validate manifest across all scene categories
[ ] Generate final Phase 1 dataset report
[ ] Document all remaining dataset ambiguities
```

---

# 28. What We Have Learned So Far

The most important result of Phase 1 is that we are no longer treating the dataset as simply:

```text
RAW image → RGB image
```

We now understand it as a collection of synchronized sensor and calibration information:

```text
                         INTEL-TAU
                            │
             ┌──────────────┼──────────────┐
             │              │              │
           RAW            META             Calibration
             │              │              │
         .plain16       .meta         ┌────┴────┐
             │                        │         │
             │                       .wp       .ccm
             │
             ▼
        Bayer sensor
          samples
             │
       ┌─────┼─────┐
       │     │     │
       R    G1/G2   B
       │     │     │
       └─────┼─────┘
             │
             ▼
       ISP processing
```

This is the foundation required for an adaptive Camera ISP.

---

# 29. Important Lessons From Phase 1

### Lesson 1 — Never assume the dataset structure

The official dataset description and the local dataset organization were not identical.

We therefore inspected the actual local files before building the pipeline.

### Lesson 2 — File extensions matter

`.plain16`, `.meta`, `.wp`, `.ccm`, and `.jpg` are different data products and must not be interpreted using the same reader.

### Lesson 3 — RAW is not RGB

The `.plain16` data contains Bayer sensor measurements.

A single RAW pixel represents one color sample, not a complete RGB pixel.

### Lesson 4 — Bayer interpretation must remain consistent

The Bayer pattern determines which RAW positions correspond to:

```text
R
G1
G2
B
```

A wrong Bayer interpretation can produce a completely incorrect color reconstruction.

### Lesson 5 — Visualization is not ISP processing

Display normalization and orientation must not be confused with actual sensor processing.

### Lesson 6 — Sensor statistics are more informative than immediately looking at JPEGs

RAW statistics reveal:

* sensor range
* clipping
* distribution
* channel differences
* possible black-level behavior

before any camera processing hides these effects.

---

# 30. Phase 1 Completion Criteria

Phase 1 will be considered complete when we can take any selected Sony IMX135 frame and answer:

```text
What camera produced it?
        ↓
What scene/category is it from?
        ↓
What RAW file belongs to it?
        ↓
What are its dimensions?
        ↓
What is its Bayer pattern?
        ↓
What is its sensor value range?
        ↓
What exposure settings were used?
        ↓
What white-point information is provided?
        ↓
What CCM is provided?
        ↓
What JPEG corresponds to it?
        ↓
Can all of these files be linked automatically?
```

Only after these questions are answered should we freeze the Phase 1 dataset representation.

---

# 31. Final Phase 1 Data Model

The target representation for each frame is:

```text
Frame
│
├── frame_id
│
├── camera
│   └── Sony_IMX135
│
├── scene
│   ├── field_3_cameras
│   ├── lab_printouts
│   └── lab_realscene
│
├── raw
│   ├── path
│   ├── width
│   ├── height
│   ├── dtype
│   ├── bit_depth
│   └── bayer_pattern
│
├── exposure
│   ├── exposure_time
│   ├── analog_gain
│   ├── aperture
│   └── normalized_exposure_s
│
├── calibration
│   ├── white_point
│   └── ccm
│
└── reference
    └── jpg
```

This structure will provide the clean interface between **dataset characterization** and the later ISP implementation.

---

# 32. Current Position

We are **not yet moving to the ISP implementation phase**.

The immediate remaining work is:

```text
Inspect .wp
      ↓
Understand white-point values
      ↓
Inspect .ccm
      ↓
Understand CCM
      ↓
Build and validate manifest
      ↓
Generate Phase 1 report
      ↓
Freeze dataset representation
      ↓
PHASE 1 COMPLETE
```

Only after this checklist is complete will we proceed to the first actual ISP processing stage.
