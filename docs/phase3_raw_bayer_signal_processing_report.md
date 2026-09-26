# Phase 3 Report --- RAW / Bayer Signal Processing

## 1. Phase Overview

**Project:** Adaptive Camera ISP for Outdoor Robotic Perception\
**Dataset:** Sony IMX135 subset of INTEL-TAU\
**Phase:** 3 --- RAW / Bayer Signal Processing

### Objective

Phase 3 establishes the first signal-processing stages of the Camera
ISP. The goal is to move from validated sensor RAW data toward a linear
RGB representation while keeping the processing modular, measurable, and
reproducible.

The phase covers:

1.  Bayer pattern and channel extraction
2.  Black-level characterization
3.  Black-level correction
4.  White-point characterization
5.  White-balance implementation
6.  Demosaicing characterization
7.  Bilinear demosaicing implementation
8.  Integrated Bayer-domain mini-ISP validation

------------------------------------------------------------------------

# 2. Dataset and Sensor Context

The working Sony IMX135 RAW data has:

-   Resolution: **3264 × 2448**
-   RAW dtype: **uint16**
-   Expected pixels: **7,990,272**
-   Expected RAW size: **15,980,544 bytes**
-   Bayer pattern used: **GRBG**

The GRBG Bayer unit cell is:

``` text
G R
B G
```

Therefore the full Bayer structure is:

``` text
G R G R ...
B G B G ...
G R G R ...
B G B G ...
```

The local dataset contains frame bundles consisting of:

``` text
.plain16
.meta
.wp
.ccm
.jpg
```

The field subset used for most Phase 3 experiments contains **144
complete frames**.

------------------------------------------------------------------------

# 3. Subphase 3.1 --- Bayer Pattern and Channel Extraction

## 3.1.1 Bayer Geometry

The canonical GRBG arrangement was established as:

``` text
G R
B G
```

The 8×8 expanded pattern confirmed the expected sampling distribution:

``` text
R = 16 samples
G = 32 samples
B = 16 samples
```

This corresponds to:

-   Red: 25%
-   Green: 50%
-   Blue: 25%

## 3.1.2 Channel Extraction

The Bayer extraction module was implemented in:

``` text
camera_isp/raw/bayer.py
```

It provides separate:

-   `R`
-   `G1`
-   `G2`
-   `B`

planes.

For the 3264 × 2448 RAW image, every extracted plane has:

``` text
1224 × 1632
```

For frame 001, the measured channel statistics were:

  Channel     Min    Max      Mean   Median
  --------- ----- ------ --------- --------
  R            62   1023   174.721      143
  G1           67   1023   252.332      216
  G2           67   1023   251.947      217
  B            54   1023   162.654      152

The two green planes are very close for this frame, but they are
intentionally kept separate because they represent distinct sensor
sampling locations.

**Status: COMPLETE**

------------------------------------------------------------------------

# 4. Subphase 3.2 --- Black-Level Characterization

## 4.1 Motivation

Before applying black-level subtraction, the low-end RAW signal was
characterized across the dataset.

The objective was to determine whether a reliable fixed or
gain-dependent black-level offset could be inferred from the available
scene images.

## 4.2 Low-End Observations

For field and real-scene images, the low-end signal commonly lies around
approximately 60--80 DN.

However, `lab_printouts` contains a large black/non-image border. Its
low-end statistics are therefore dominated by that border and cannot be
interpreted directly as the physical sensor black level.

A threshold around 64 DN was used only as a **characterization
threshold**, not as a calibrated sensor value.

## 4.3 Gain Analysis

A multi-frame analysis was performed against analog gain.

The results showed that low-percentile scene values do not form a simple
monotonic function of analog gain. Even at high gains, substantial
variation exists between frames.

For example, gain-16 frames exhibit materially different low-end
percentile values.

This demonstrates that scene-derived low percentiles are not sufficient
to construct a reliable model:

``` text
black_level = f(analog_gain)
```

A dedicated dark-frame calibration would be required to establish a
physical sensor black-level model.

**Conclusion:**

> No sensor-specific black-level calibration value was inferred from
> scene images.

**Status: COMPLETE**

------------------------------------------------------------------------

# 5. Subphase 3.3 --- Black-Level Correction

A configurable scalar black-level correction was implemented in:

``` text
camera_isp/isp/black_level.py
```

The operation is:

``` text
uint16 RAW
    ↓
float32
    ↓
subtract configurable offset
    ↓
clip negative values to zero
```

The implementation intentionally does not hardcode a sensor calibration
value.

## 5.1 Unit Tests

The following were validated:

-   zero offset preserves the signal
-   scalar offset subtraction
-   negative-result clipping
-   invalid offset rejection
-   invalid dimensionality rejection

All tests passed.

## 5.2 Real-Data Experiment

An experimental offset of:

``` text
64 DN
```

was evaluated on frame 001.

Original:

``` text
min    = 54
max    = 1023
mean   = 210.413
median = 181
p0.1   = 70
p1     = 75
p5     = 88
```

After subtracting 64 DN:

``` text
min    = 0
max    = 959
mean   = 146.413
median = 117
p0.1   = 6
p1     = 11
p5     = 24
```

Only:

``` text
0.0001%
```

of pixels were clipped in the frame-001 experiment.

## 5.3 Multi-Frame 64-DN Experiment

Across all 144 field frames:

``` text
Offset:             64 DN
Median clipping:    0.000707%
Mean clipping:      0.085822%
Maximum clipping:   3.273931%
Frames >1% clipped: 3 / 144
Frames >5% clipped: 0 / 144
```

The median frame mean changed from:

``` text
172.415 → 108.415
```

and median P0.1 changed from:

``` text
67 → 3
```

This is numerically consistent with subtracting 64 DN.

## 5.4 Interpretation

The experiment supports 64 DN as a useful **experimental configuration**
for this dataset.

It does not establish 64 DN as the physical sensor black-level
calibration.

**Status: COMPLETE**

------------------------------------------------------------------------

# 6. Subphase 3.4 --- White-Point Characterization

The dataset provides `.wp` files containing two values:

``` text
R/G
B/G
```

These values were characterized across the 144 field frames.

## 6.1 R/G Distribution

  Percentile          R/G
  ------------ ----------
  P0             0.429504
  P1             0.444441
  P5             0.498490
  P25            0.546610
  P50            0.625345
  P75            0.786105
  P95            0.873226
  P99            1.049132
  P100           1.154233

Mean:

``` text
0.656734
```

Standard deviation:

``` text
0.142432
```

## 6.2 B/G Distribution

  Percentile          B/G
  ------------ ----------
  P0             0.287049
  P1             0.348551
  P5             0.383946
  P25            0.448959
  P50            0.555564
  P75            0.658381
  P95            0.756794
  P99            0.838285
  P100           0.894652

Mean:

``` text
0.562169
```

Standard deviation:

``` text
0.128116
```

## 6.3 Important Interpretation

For frame 001:

``` text
Dataset WP:
R/G = 0.649375400
B/G = 0.463837690
```

while full-frame RAW means gave approximately:

``` text
Measured scene R/G = 0.692952
Measured scene B/G = 0.645094
```

These are not the same quantities.

The dataset white point represents illumination/white-point information
and should not be expected to equal the average RGB chromaticity of an
arbitrary scene.

The dataset documentation/paper describes the white-point ground truth
as being obtained from ColorChecker grey patches under the scene
illumination. Therefore, the `.wp` values should be treated as
white-point/illuminant information rather than as direct measurements of
the full-frame scene mean.

The local RAW subset does not contain the associated pixel-aligned
ColorChecker RAW needed for direct patch-level validation.

**Status: COMPLETE**

------------------------------------------------------------------------

# 7. Subphase 3.5 --- White-Balance Implementation

White-balance processing was implemented in:

``` text
camera_isp/isp/white_balance.py
```

Two responsibilities were deliberately separated.

## 7.1 White Point → Gains

For the selected diagonal correction convention:

\[ g_R = `\frac{1}{R/G}`{=tex} \]

\[ g_G = 1 \]

\[ g_B = `\frac{1}{B/G}`{=tex} \]

Both Bayer green planes use unity gain.

## 7.2 Generic WB Application

The generic WB function accepts explicit:

``` text
R
G1
G2
B
```

channels and a `WhiteBalanceGains` structure.

This keeps the ISP core independent from the source of the gains.

Future gain sources can therefore include:

``` text
Dataset white point
        ↓
Classical AWB
        ↓
Learned/adaptive estimator
        ↓
same WB engine
```

## 7.3 Unit Tests

Validated:

-   white-point to gain conversion
-   gain application
-   unity gains
-   invalid white-point values
-   mismatched channel dimensions

All tests passed.

## 7.4 Real-Data Validation

For frame 001:

``` text
WP:
R/G = 0.649375400
B/G = 0.463837690

Gains:
R = 1.539941304
G1 = 1
G2 = 1
B = 2.155926570
```

The scene-average RGB channels do not become neutral after this
operation. This is expected because the white point represents
illumination information and the arbitrary scene contains objects with
their own reflectance/color.

Therefore, the validation criterion is not:

``` text
full-frame R = G = B
```

The result is documented as a white-point-derived correction rather than
reproduction of a proprietary camera AWB algorithm.

**Status: COMPLETE**

------------------------------------------------------------------------

# 8. Subphase 3.6 --- Demosaicing Characterization

## 8.1 Objective

The objective was to understand the conversion from the GRBG Bayer
mosaic to RGB before implementing an independent demosaicer.

An OpenCV conversion was used as a reference only.

## 8.2 Correct Bayer Reference

An initial abbreviated OpenCV Bayer conversion produced an R/B reversal.
This was detected through channel statistics.

The reference was corrected to the explicit GRBG conversion:

``` python
cv2.COLOR_BayerGRBG2RGB
```

After correction, OpenCV produced:

``` text
R = 174.873
G = 252.203
B = 162.812
```

which is consistent with the measured Bayer-channel statistics.

This was an important validation lesson: Bayer phase and RGB ordering
must be explicitly controlled.

## 8.3 Visual Characterization

The OpenCV reference was inspected on:

-   repeated window blinds
-   plant/leaf structures
-   clothing/fine texture
-   high-contrast edges

The reconstructed image was spatially coherent, with no obvious
catastrophic:

-   Bayer-phase error
-   checkerboard artifact
-   severe zippering
-   large-scale false-color artifact

No pixel-aligned RGB ground truth was available, so quantitative
demosaicing image-quality metrics such as PSNR/SSIM were not claimed.

**Status: COMPLETE**

------------------------------------------------------------------------

# 9. Subphase 3.7 --- Bilinear Demosaicing Implementation

A controlled GRBG bilinear demosaicer was implemented in:

``` text
camera_isp/isp/demosaic.py
```

The implementation:

-   accepts a 2-D Bayer image
-   requires an explicit Bayer pattern
-   currently supports GRBG
-   uses float32 processing
-   reconstructs RGB
-   preserves measured Bayer samples
-   handles image boundaries using reflected borders

## 9.1 Validation

For frame 001:

``` text
Output shape:
(2448, 3264, 3)

dtype:
float32

range:
54 → 1023
```

All measured Bayer samples were preserved exactly.

## 9.2 Comparison Against Correct OpenCV Reference

Results:

``` text
Mean absolute difference:    0.169905 DN
Median absolute difference:  0 DN
Maximum absolute difference: 102 DN
Pixels exactly equal:        58.4121%
```

At first, the 102-DN maximum appeared significant, so its location and
distribution were investigated.

## 9.3 Difference Localization

Difference percentiles:

``` text
P90    = 0.5 DN
P95    = 0.5 DN
P99    = 0.5 DN
P99.9  = 0.5 DN
P99.99 = 8.625 DN
```

Pixels differing by more than:

``` text
1 DN   = 0.069889%
2 DN   = 0.053023%
5 DN   = 0.023620%
10 DN  = 0.006796%
20 DN  = 0.000839%
50 DN  = 0.000083%
100 DN = 0.000004%
```

The maximum difference occurred at:

``` text
x = 2042
y = 0
channel = G

Our implementation = 323 DN
OpenCV reference   = 425 DN
Difference         = 102 DN
```

The pixel is on the first image row.

When the image border was excluded:

``` text
Interior mean difference   = 0.166288 DN
Interior median difference = 0 DN
Interior maximum           = 0.5 DN
```

Therefore the large maximum difference is attributed to different
boundary handling between the custom implementation and OpenCV.

## 9.4 Conclusion

The custom bilinear implementation provides extremely close interior
agreement with the OpenCV reference and is suitable as the project's
transparent classical demosaicing baseline.

**Status: COMPLETE**

------------------------------------------------------------------------

# 10. Subphase 3.8 --- Integrated Bayer-Domain Mini-ISP

The first integrated Phase 3 pipeline was tested:

``` text
RAW uint16
    ↓
Black-level correction
    ↓
Bayer extraction
    ↓
White balance
    ↓
Bayer reconstruction
    ↓
GRBG bilinear demosaicing
    ↓
RGB float32
```

## 10.1 Configuration

``` text
Bayer pattern:       GRBG
Black-level offset:  64 DN (experimental)
R/G:                 0.649375400
B/G:                 0.463837690
```

## 10.2 Signal Evolution

### Original RAW

``` text
min    = 54
max    = 1023
mean   = 210.413239
median = 181
```

### After black-level correction

``` text
min    = 0
max    = 959
mean   = 146.413147
median = 117
```

Clipped:

``` text
0.000075%
```

### After Bayer-domain white balance

Channel means:

``` text
R  = 170.503
G1 = 188.332
G2 = 187.947
B  = 212.690
```

Average green:

``` text
G = 188.139
```

### Final RGB

``` text
shape  = (2448, 3264, 3)
dtype  = float32
min    = 0
max    = 2067.533
mean   = 190.444
median = 156.305
```

Final RGB channel means:

``` text
R = 170.498
G = 188.139
B = 212.695
```

## 10.3 Sanity Checks

All passed:

``` text
RGB shape       PASS
RGB dtype       PASS
Finite values   PASS
Non-negative    PASS
```

The increase of the maximum above the original 10-bit value of 1023 is
expected because white-balance gains greater than one are applied in
float32 linear space.

**Status: COMPLETE**

------------------------------------------------------------------------

# 11. Phase 3 Final Architecture

The completed Phase 3 signal path is:

``` text
                    SONY IMX135 RAW
                         │
                         │ uint16
                         ▼
                 ┌─────────────────┐
                 │ RAW Validation  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Black Level     │
                 │ Correction      │
                 └────────┬────────┘
                          │
                          │ float32
                          ▼
                 ┌─────────────────┐
                 │ GRBG Bayer      │
                 │ Representation  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ White Balance   │
                 │ R/G, B/G gains  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ GRBG Bilinear   │
                 │ Demosaicing     │
                 └────────┬────────┘
                          │
                          ▼
                    LINEAR RGB
                     float32
```

This is the first functional RAW-to-RGB portion of the ISP.

------------------------------------------------------------------------

# 12. Files Implemented During Phase 3

## Core modules

``` text
camera_isp/
├── raw/
│   └── bayer.py
└── isp/
    ├── black_level.py
    ├── white_balance.py
    └── demosaic.py
```

## Characterization / validation scripts

``` text
scripts/
├── analyze_bayer_low_end.py
├── analyze_bayer_low_end_all.py
├── analyze_black_level_vs_metadata.py
├── analyze_black_level_offset_64.py
├── analyze_white_point.py
├── inspect_white_point_frame.py
├── inspect_bayer_pattern.py
├── test_opencv_demosaic.py
├── inspect_demosaic_crops.py
├── test_black_level.py
├── test_black_level_real.py
├── test_white_balance.py
├── test_white_balance_real.py
├── test_demosaic.py
├── analyze_demosaic_difference.py
└── test_phase3_pipeline.py
```

------------------------------------------------------------------------

# 13. Major Technical Lessons

## 13.1 RAW values are sensor measurements, not display RGB

The RAW Bayer signal cannot be treated as an RGB image directly.

The sensor samples only one color component at each pixel.

## 13.2 Black-level calibration cannot be inferred reliably from ordinary scene images

Low-end scene statistics are affected by scene content, borders,
exposure, gain, and illumination.

A true sensor calibration should use dark frames.

## 13.3 Bayer phase must be treated as a first-class parameter

Using the wrong Bayer conversion can produce a plausible image while
swapping color channels.

The OpenCV R/B discrepancy demonstrated this directly.

## 13.4 White point and scene-average chromaticity are different concepts

The `.wp` metadata represents illumination/white-point information. It
should not be validated by expecting the arbitrary scene average to
become neutral.

## 13.5 Demosaicing should be validated numerically

Visual inspection alone did not reveal the initial R/B ordering issue.
Channel statistics immediately exposed it.

## 13.6 Floating-point representation becomes important after black-level correction

Once offsets and gains are applied, the signal is no longer naturally
bounded to the original uint16 sensor range.

The ISP should therefore operate in float32 after RAW correction.

------------------------------------------------------------------------

# 14. Current Limitations

The following limitations should be explicitly carried into future
phases:

### Black level

No dedicated dark-frame calibration is available in the current local
subset.

Therefore:

``` text
64 DN = experimental parameter
```

and not:

``` text
64 DN = calibrated IMX135 black level
```

### White balance

The `.wp` metadata provides ground-truth illumination information, but
the local subset does not contain the corresponding pixel-aligned
ColorChecker data required for direct patch-level validation.

### Demosaicing

No native pixel-aligned RGB ground truth is available for the RAW
frames.

Therefore, the OpenCV implementation is used as a **reference
baseline**, not as ground truth.

### Demosaicing algorithm

The current implementation is deliberately simple bilinear
interpolation. It is a transparent baseline rather than a
state-of-the-art production demosaicer.

### Color correction

CCM processing has not yet been integrated.

### Display rendering

Gamma/tone mapping has not yet been applied. The current RGB is still a
linear sensor-space representation.

------------------------------------------------------------------------

# 15. Phase 3 Final Result

Phase 3 successfully established a reproducible RAW-to-linear-RGB
processing path:

\[ `\boxed{
RAW
\rightarrow
Black\ Level
\rightarrow
White\ Balance
\rightarrow
Demosaicing
\rightarrow
Linear\ RGB
}`{=tex} \]

The implementation is modular and parameterized, which is important for
the later adaptive ISP stages.

The output of Phase 3 is **not yet a final display-quality image**. It
is the linear RGB foundation on which subsequent color correction, tone
mapping, denoising, sharpening, and adaptive processing can operate.

# Phase 3 Status: COMPLETE

------------------------------------------------------------------------

# 16. Transition to the Next Phase

The next ISP stages should build on this validated linear RGB
representation.

The natural next stage is:

``` text
Phase 4
Color Correction / CCM
```

where we will characterize the `.ccm` files, understand their numerical
behavior, determine how they should be applied to the linear RGB output,
and validate the transformation before moving to tone mapping.
