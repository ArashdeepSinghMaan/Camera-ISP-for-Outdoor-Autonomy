# Phase 1 --- Dataset & Camera Signal Characterization

## 1. Objective

Phase 1 establishes a reliable understanding of the camera dataset
before implementing any ISP operation.

The objective is to characterize:

-   dataset organization and frame correspondence
-   RAW image format and dimensions
-   Bayer representation
-   frame-level camera metadata
-   white-point information
-   color-correction matrices
-   RAW signal distributions
-   subset-specific RAW behavior
-   non-image regions and their effect on signal statistics

No RAW processing or ISP correction is applied in this phase. The
purpose is to understand the input signal before designing the ISP
stages.

------------------------------------------------------------------------

## 2. Dataset Overview

Dataset root:

``` text
/media/hitech/WD_Access/Camera_ISP/Sony_IMX135
```

The dataset contains three subsets:

  Subset                 Frames
  ------------------- ---------
  `field_3_cameras`         144
  `lab_printouts`           300
  `lab_realscene`            20
  **Total**             **464**

Each RAW frame is associated with a five-file bundle:

``` text
.plain16
.meta
.wp
.ccm
.jpg
```

Dataset-wide validation found:

  Component                 Present
  --------------------- -----------
  RAW (`.plain16`)        464 / 464
  META (`.meta`)          464 / 464
  White point (`.wp`)     464 / 464
  CCM (`.ccm`)            464 / 464
  JPEG (`.jpg`)           464 / 464

No missing frame components were detected.

The manifest builder reports 466 unique file stems because the dataset
tree contains two additional non-frame stems/files. Frame construction
is based on the presence of the `.plain16` RAW file, resulting in 464
frame records.

------------------------------------------------------------------------

## 3. RAW Format

The RAW files use:

``` text
Width          : 3264
Height         : 2448
Data type      : uint16
Bytes/pixel    : 2
Pixels/frame   : 7,990,272
Bytes/frame    : 15,980,544
```

The expected RAW size is:

``` text
3264 × 2448 × 2 = 15,980,544 bytes
```

Dataset-wide validation found no RAW files with an incorrect file size.

The RAW files therefore have a consistent structural representation
across all 464 frames.

------------------------------------------------------------------------

## 4. Bayer Characterization

The RAW data is Bayer-mosaiced rather than directly containing
three-channel RGB pixels.

The Bayer analysis was performed by separating the mosaic into:

``` text
R
G1
G2
B
```

using the identified Bayer arrangement.

For the inspected RAW frame, the four planes had the following
characteristics:

  Plane     Min    Max      Mean
  ------- ----- ------ ---------
  G1         67   1023   252.332
  R          62   1023   174.721
  B          54   1023   162.654
  G2         67   1023   251.947

The two green planes were very similar in the inspected frame.

The original RAW indexing is preserved during analysis. Display-only
rotation was kept separate from RAW data indexing.

------------------------------------------------------------------------

## 5. RAW Visualization

A RAW visualization tool was created to inspect:

1.  the Bayer mosaic
2.  the R plane
3.  the G1 plane
4.  the G2 plane
5.  the B plane

Display normalization is treated as a visualization operation and is not
considered a RAW correction.

This distinction is important because display normalization must not be
confused with black-level correction, gain correction, or tone mapping.

------------------------------------------------------------------------

## 6. META File Characterization

The `.meta` files contain frame-level camera/exposure information.

Four fields are present in every one of the 464 frames:

``` text
exposure_time
analog_gain
aperture
normalized_exposure_s
```

Two additional fields occur conditionally:

``` text
iso
privacy_masked
```

Field presence:

  Field                        Presence
  ------------------------- -----------
  `exposure_time`             464 / 464
  `analog_gain`               464 / 464
  `aperture`                  464 / 464
  `normalized_exposure_s`     464 / 464
  `iso`                       317 / 464
  `privacy_masked`            102 / 464

Four valid META structures were observed:

  -----------------------------------------------------------------------
                                     Count Fields
  ---------------------------------------- ------------------------------
                                       246 exposure + gain + aperture +
                                           normalized exposure + ISO

                                       116 exposure + gain + aperture +
                                           normalized exposure

                                        71 exposure + gain + aperture +
                                           normalized exposure + ISO +
                                           privacy

                                        31 exposure + gain + aperture +
                                           normalized exposure + privacy
  -----------------------------------------------------------------------

The initial manifest implementation incorrectly classified 362 files as
invalid because it treated `privacy_masked` as required. This was
corrected after inspecting the dataset-wide META schemas.

After correction:

``` text
Invalid META files: 0
```

Missing optional fields are therefore treated as absent metadata rather
than malformed files.

------------------------------------------------------------------------

## 7. Exposure and Camera-Setting Variation

Dataset-wide metadata statistics:

  -----------------------------------------------------------------------------
  Parameter             Min          Max         Mean       Median          Std
  ------------ ------------ ------------ ------------ ------------ ------------
  Exposure         0.000366     0.099883     0.026333     0.024355     0.014355
  time (s)                                                         

  Analog gain           1.0         16.0     2.332936          2.0     2.052157

  Aperture              2.4          2.4          2.4          2.4            0

  Normalized       0.000117     0.511401     0.026810     0.016383     0.057672
  exposure (s)                                                     
  -----------------------------------------------------------------------------

The aperture is constant at 2.4 across all frames.

Exposure time and analog gain vary substantially across the dataset.

This means RAW intensity differences cannot be interpreted solely as
changes in scene illumination. Camera exposure settings also change from
frame to frame.

The exact physical definition or formula of `normalized_exposure_s` has
not been established in this phase. It is therefore retained as a
dataset metadata field without assigning an unverified physical
interpretation.

------------------------------------------------------------------------

## 8. White-Point Metadata

The `.wp` files contain two values interpreted from the dataset
representation as:

``` text
R/G
B/G
```

Dataset-wide statistics:

  Parameter          Min        Max       Mean     Median        Std
  ----------- ---------- ---------- ---------- ---------- ----------
  R/G           0.429504   1.154233   0.708916   0.651125   0.187778
  B/G           0.287049   0.894652   0.520082   0.495794   0.132642

Both values vary substantially across the 464 frames.

Therefore, white-point information should be treated as frame-dependent
metadata rather than as one fixed camera parameter.

No white-point correction is implemented in Phase 1.

------------------------------------------------------------------------

## 9. Color Correction Matrix

Each `.ccm` file contains nine numeric values forming a 3 × 3 matrix.

Example:

``` text
[[ 1.6750269  -0.65038601 -0.02464091]
 [-0.40009271  1.8065471  -0.40645443]
 [-0.11150382 -0.73760016  1.8491040 ]]
```

All 464 frames contain valid CCMs.

Dataset-wide comparison shows:

``` text
Matrices found                         : 464
Maximum absolute difference from first : 0.88576028
Mean absolute difference from first    : 0.15742051
All identical to first                 : False
```

Therefore, the CCM is not constant across the dataset.

The CCM is preserved as frame-level metadata. Its use as a
color-conversion ground truth is not assumed in Phase 1.

------------------------------------------------------------------------

## 10. Dataset-Wide RAW Signal Characterization

All 464 RAW files were scanned to characterize their signal
distributions.

Across individual frames:

  Statistic              Minimum across frames   Maximum across frames
  -------------------- ----------------------- -----------------------
  Frame minimum                              0                      73
  Frame maximum                            530                    1023
  Frame mean                             51.71                  265.37
  Frame median                               0                     242
  P1                                         0                     102
  P5                                         0                     118
  P95                                      166                    1023
  P99                                      197                    1023
  P99.9                                    415                    1023
  \% pixels below 64                        0%                  60.04%
  \% pixels ≥1023                           0%                   8.31%

These statistics demonstrate substantial variation in RAW signal
distributions.

However, the global statistics cannot be interpreted without considering
dataset subset and spatial image content.

------------------------------------------------------------------------

## 11. RAW Signal Statistics by Dataset Subset

### 11.1 `field_3_cameras`

Frames:

``` text
144
```

Characteristics:

``` text
Frame minimum: 12–73
Frame maximum: 689–1023
Frame mean:    107.535–265.367
Frame median:  79–242
P1:            63–102
P5:            65–118
P95:           167–1023
P99:           197–1023
```

Average fraction of pixels below 64:

``` text
0.032%
```

Average fraction of saturated pixels:

``` text
0.346%
```

The subset therefore contains mostly non-zero RAW image content with
varying exposure and highlight saturation.

### 11.2 `lab_realscene`

Frames:

``` text
20
```

Characteristics:

``` text
Frame minimum: 52–67
Frame maximum: 865–1023
Frame mean:    107.864–238.739
Frame median:  84–229
P1:            64–80
P5:            66–115
P95:           232–517
P99:           399–907
```

Average fraction of pixels below 64:

``` text
0.030%
```

Average fraction of saturated pixels:

``` text
0.073%
```

This subset shows RAW signal behavior similar to `field_3_cameras` with
respect to the low-value region.

### 11.3 `lab_printouts`

Frames:

``` text
300
```

This subset is substantially different.

Characteristics:

``` text
Frame minimum: 0
Frame median:  0
P1:            0
P5:            0
```

Average fraction of pixels below 64:

``` text
58.243%
```

Average fraction of saturated pixels:

``` text
0.059%
```

The large population of low-valued pixels was investigated spatially
rather than being interpreted directly as sensor black level.

------------------------------------------------------------------------

## 12. `lab_printouts` Non-Image Border Investigation

Visualization of the `lab_printouts` data revealed a large black border
surrounding the actual photographed image.

A threshold-based analysis using:

``` text
RAW > 10
```

was used only as a heuristic method for characterizing the non-black
image region.

For one representative frame:

``` text
x_min = 520
x_max = 2738
y_min = 616
y_max = 2054
```

The detected active region occupied approximately:

``` text
39.96% of the full RAW frame
```

The same analysis was then performed over all 300 `lab_printouts`
frames.

### ROI variation across 300 frames

  Quantity                Range
  ------------- ---------------
  `x_min`              416--636
  `x_max`            2678--2880
  `y_min`              540--718
  `y_max`            2020--2184
  Active area     39.96--43.33%

The detected image region is therefore **not fixed** across the subset.

Consequently, the heuristic ROI must not be treated as a fixed camera
calibration ROI.

The analysis establishes that a substantial part of the `lab_printouts`
RAW frame is a variable black/non-image border.

------------------------------------------------------------------------

## 13. Black-Level Interpretation

A value of 64 was initially used as a reference threshold during signal
characterization.

The dataset investigation showed that this value must not yet be treated
as a universal black-level correction constant.

Reasons:

1.  Some RAW frames have minimum values below 64.
2.  `field_3_cameras` and `lab_realscene` have only about 0.03% of
    pixels below 64 on average.
3.  `lab_printouts` has approximately 58.24% of pixels below 64 on
    average.
4.  The `lab_printouts` low-valued pixels are strongly associated with a
    large spatial border outside the photographed image.
5.  The valid-image region itself varies across the `lab_printouts`
    frames.

Therefore:

> The current evidence supports using 64 as a signal-analysis reference
> threshold, but does not establish 64 as the universal sensor black
> level.

The exact black-level model remains a Phase 2 investigation.

------------------------------------------------------------------------

## 14. Dataset Manifest

The dataset manifest is generated by:

``` text
scripts/build_dataset_manifest.py
```

Output:

``` text
data/metadata/intel_tau/manifest.json
```

The manifest records:

-   dataset information
-   frame file paths
-   file presence
-   RAW validation
-   META values
-   optional META field presence
-   white-point values
-   CCM matrices
-   dataset-level metadata statistics
-   CCM variation analysis
-   per-frame records

The manifest is intended to be the central machine-readable description
of the dataset for subsequent ISP experiments.

------------------------------------------------------------------------

## 15. Phase 1 Findings

The dataset characterization establishes the following:

### Confirmed

-   464 complete RAW frame bundles are available.
-   Every frame has RAW, META, WP, CCM, and JPEG files.
-   RAW files consistently use the validated 3264 × 2448, 16-bit,
    2-byte/pixel structure.
-   The RAW data is Bayer-mosaiced.
-   Exposure time varies substantially.
-   Analog gain varies substantially.
-   Aperture remains fixed at 2.4.
-   White-point values vary across frames.
-   CCMs vary across frames.
-   META files contain four universally present core fields.
-   ISO and privacy metadata are conditional fields.
-   RAW signal distributions differ substantially between dataset
    subsets.
-   `lab_printouts` contains a large, spatially varying black/non-image
    border.

### Not yet established

The following are intentionally left unresolved:

-   exact physical meaning/formula of `normalized_exposure_s`
-   exact sensor black-level model
-   whether the heuristic `lab_printouts` ROI corresponds to an official
    dataset/camera ROI
-   exact relationship between ISO and analog gain
-   whether and how the supplied CCM should be used as a calibration
    ground truth
-   optimal BLC strategy for each dataset subset

These questions should be investigated during the ISP implementation
phase rather than assumed from the current observations.

------------------------------------------------------------------------

## 16. Phase 1 Conclusion

Phase 1 successfully establishes a validated dataset and camera-signal
baseline for the Camera ISP project.

The most important result is that the dataset should **not be treated as
a collection of identically captured RGB scenes**. The RAW signal is
influenced by:

``` text
scene/content
     +
exposure settings
     +
white-point variation
     +
CCM variation
     +
dataset-specific spatial structure
```

The `lab_printouts` subset additionally contains a variable non-image
border that strongly affects global RAW statistics.

Therefore, the next ISP stage should begin from the **RAW signal model
and black-level investigation**, using subset-aware analysis and
avoiding assumptions derived from global statistics alone.

Phase 1 is considered complete.
