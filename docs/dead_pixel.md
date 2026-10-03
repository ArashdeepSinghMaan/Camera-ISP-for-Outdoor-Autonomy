# Dead Pixel Detection and Correction

## 1. Overview

A camera sensor is composed of millions of individual photosites/pixels.

Ideally, every photosite should produce a response that is related to the amount of light reaching it:

```text
Incident Light
      ↓
   Photodiode
      ↓
 Charge Generation
      ↓
 Analog Readout
      ↓
 ADC
      ↓
 RAW Pixel Value
```

In a real image sensor, some pixels may behave abnormally.

A defective pixel may:

* Always produce a value close to zero
* Always produce a very high value
* Remain at approximately the same value regardless of illumination
* Produce an abnormal response compared with neighboring pixels
* Behave correctly sometimes and incorrectly at other times

These defective pixels can produce visible artifacts and can also affect downstream computer vision.

Therefore, **defective-pixel detection and correction should be considered an early RAW-domain ISP operation.**

---

# 2. What Is a Dead Pixel?

A **dead pixel** is a sensor photosite that has lost most or all of its ability to respond correctly to incoming light.

For example:

```text
Normal pixel:

Dark scene → low value
Bright scene → high value


Dead pixel:

Dark scene → ~constant low value
Bright scene → ~constant low value
```

Conceptually:

```text
             Normal Pixel
Light ───────────────► Response

             Dead Pixel
Light ───────────────► Almost no response
```

If the sensor is producing a Bayer RAW image, a defective pixel exists at a specific sensor location and corresponds to one specific CFA component:

```text
R G R G
G B G B
R G R G
G B G B
```

For example, a defective pixel at:

```text
(row=100, col=200)
```

might be an R photosite.

This is important because correction should generally use information from **the same Bayer color plane** whenever possible.

---

# 3. Dead Pixel vs Other Defective Pixels

"Dead pixel" is often used informally for all bad sensor pixels, but several different defect behaviors exist.

## 3.1 Dead Pixel

A dead pixel has little or no useful response.

Example:

```text
Expected:

Dark   →  80 DN
Medium → 500 DN
Bright → 2500 DN

Defective:

Dark   → 0 DN
Medium → 2 DN
Bright → 3 DN
```

The pixel remains near zero even when illumination increases.

---

# 3.2 Hot Pixel

A hot pixel produces an abnormally high value.

Example:

```text
Expected:

Dark scene → 60 DN

Hot pixel:

Dark scene → 1800 DN
```

It may appear as a bright point in an otherwise dark image.

Hot pixels are particularly visible in:

* Night scenes
* Long exposures
* High ISO
* Dark-frame captures

---

# 3.3 Stuck Pixel

A stuck pixel produces approximately the same output regardless of illumination.

For example:

```text
Scene illumination:

Dark       Medium       Bright
   ↓          ↓            ↓

Pixel:

1000 DN    1002 DN       999 DN
```

The pixel is effectively "stuck" around one output value.

A stuck pixel can therefore appear:

* Bright
* Dark
* Or somewhere in between

depending on the stuck value.

---

# 3.4 Warm Pixel

A warm pixel is not necessarily completely defective, but has significantly higher dark-current response than surrounding pixels.

Example:

```text
Normal dark pixel:

52 DN

Warm pixel:

180 DN
```

Warm pixels become more problematic with:

* Higher sensor temperature
* Longer exposure
* Higher ISO

A warm pixel may therefore not be obvious under normal operating conditions.

---

# 3.5 Intermittent Pixel

An intermittent defective pixel does not fail consistently.

Example:

```text
Frame 1 → normal
Frame 2 → normal
Frame 3 → abnormal
Frame 4 → normal
Frame 5 → abnormal
```

These defects are harder to detect from a single image.

Temporal analysis is useful here.

---

# 3.6 Clustered Defects

Sometimes several neighboring pixels are defective.

Example:

```text
Normal:

x x x x x
x x x x x
x x x x x

Cluster:

x x D D x
x D D D x
x x D x x
```

A cluster is more difficult to correct because a simple neighboring-pixel interpolation may not have enough valid information.

---

# 3.7 Row and Column Defects

Some sensor defects can affect an entire row or column, or produce abnormal readout behavior.

Example:

```text
Normal image:

----------------
----------------
----------------
----------------

Column defect:

-------|--------
-------|--------
-------|--------
-------|--------
```

These should not be confused with individual dead pixels.

They may originate from:

* Pixel circuitry
* Column amplifiers
* Readout electronics
* ADC/readout paths
* Sensor manufacturing defects

---

# 4. Why We Must Detect Defective Pixels in RAW

The preferred location is:

```text
RAW
 ↓
Defective Pixel Correction
 ↓
Black-Level / other sensor corrections
 ↓
Bayer processing
 ↓
Demosaicing
 ↓
RGB
```

The exact ordering can depend on the camera architecture, but the important principle is:

> **Correct sensor defects before demosaicing whenever possible.**

Consider a defective R pixel:

```text
R G R G
G B G B
R G R G
G B G B
```

If we demosaic first:

```text
RAW defect
     ↓
Demosaicing
     ↓
RGB artifact spreads
```

A single defective RAW photosite can influence multiple RGB pixels.

Therefore:

```text
RAW defect
    ↓
Correct first
    ↓
Demosaic clean Bayer data
```

is preferable.

---

# 5. How Do We Find Dead Pixels?

There is no single universal test.

A robust defective-pixel detection system should combine several methods.

The main approaches are:

```text
1. Dark-frame analysis
2. Flat-field analysis
3. Spatial neighbor analysis
4. Temporal analysis
5. Multi-exposure analysis
6. Sensor calibration data
```

---

# 6. Method 1 — Dark-Frame Detection

Capture an image with essentially no incoming light.

For example:

```text
Lens covered
       ↓
Dark frame
       ↓
RAW sensor values
```

For a healthy pixel:

```text
Dark frame ≈ black level + dark current
```

A dead pixel may produce:

```text
≈ 0
```

while a hot pixel may produce:

```text
much higher than surrounding pixels
```

Example:

```text
Dark frame:

52  54  53  55  52
51  53   0  54  52
53  52  54  55  51
```

The `0` candidate is suspicious.

However:

> A low value in a single dark image is not automatically proof of a dead pixel.

Sensor noise and black-level variation must be considered.

---

# 7. Method 2 — Flat-Field Detection

A flat-field image contains approximately uniform illumination.

For example:

```text
Uniform light
     ↓
Diffuser / integrating setup
     ↓
Sensor
```

The image should produce relatively smooth responses.

Example:

```text
Healthy region:

1002 1005 1001
1004 1003 1006
1001 1005 1002


Defective pixel:

1002 1005 1001
1004    0 1006
1001 1005 1002
```

The outlier becomes obvious.

Flat-field testing is especially useful for detecting:

* Dead pixels
* Hot pixels
* Low-response pixels
* High-response pixels
* Non-uniform pixels

---

# 8. Method 3 — Spatial Neighbor Analysis

For every pixel, compare it against nearby pixels of the **same Bayer phase**.

For example, for an R pixel:

```text
R G R G R
G B G B G
R G R G R
G B G B G
R G R G R
```

An R pixel should primarily be compared with other R pixels:

```text
R neighbors

R   R   R
  R
R   R   R
```

rather than directly comparing it with G or B pixels.

A simple detector can calculate:

```text
local_median = median(same-color neighbors)

deviation = |pixel - local_median|
```

If:

```text
deviation > threshold
```

the pixel becomes a defective-pixel candidate.

---

# 9. Why Neighbor Detection Alone Is Not Enough

Consider a real image containing a bright red light.

The center pixel may legitimately be much brighter than its neighbors.

Therefore:

```text
Large spatial difference
        ≠
Defective pixel
```

This is why detection should use multiple pieces of evidence.

A better decision system is:

```text
Dark-frame evidence
        +
Flat-field evidence
        +
Spatial evidence
        +
Temporal evidence
        ↓
Defective Pixel Decision
```

---

# 10. Method 4 — Temporal Detection

Capture multiple frames of the same scene.

For each pixel:

```text
Pixel (x,y):

Frame 1 → 503
Frame 2 → 505
Frame 3 → 502
Frame 4 → 504
```

Normal.

A defective pixel may produce:

```text
Frame 1 → 2
Frame 2 → 1
Frame 3 → 3
Frame 4 → 2
```

while surrounding pixels respond normally.

Temporal information helps distinguish:

```text
Real scene structure
        vs
Persistent sensor defect
```

---

# 11. Method 5 — Multi-Exposure Detection

One of the strongest tests is to change exposure or illumination.

For a healthy pixel:

```text
Exposure 1 → 100 DN
Exposure 2 → 300 DN
Exposure 3 → 800 DN
Exposure 4 → 1800 DN
```

The response changes with illumination.

For a dead pixel:

```text
Exposure 1 → 2 DN
Exposure 2 → 2 DN
Exposure 3 → 3 DN
Exposure 4 → 2 DN
```

For a stuck pixel:

```text
Exposure 1 → 900 DN
Exposure 2 → 901 DN
Exposure 3 → 899 DN
Exposure 4 → 900 DN
```

This gives us a very powerful distinction:

```text
Healthy:
output changes with illumination

Dead:
output remains near zero

Hot:
output is abnormally high in darkness

Stuck:
output remains approximately constant
```

---

# 12. A Practical Detection Pipeline

A robust calibration procedure can be:

```text
                 Sensor
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    Dark Frame  Flat Field  Multiple
                            Exposures
        │          │          │
        └──────────┼──────────┘
                   ▼
            Statistical Analysis
                   │
                   ▼
             Pixel Classification
                   │
                   ▼
             Defect Pixel Map
```

The output should be a defect map:

```text
D(x,y) = 0 → healthy
D(x,y) = 1 → defective
```

But we can make it more informative:

```text
D(x,y) = 0 → healthy
D(x,y) = 1 → dead
D(x,y) = 2 → hot
D(x,y) = 3 → stuck
D(x,y) = 4 → warm
D(x,y) = 5 → intermittent
```

This becomes a **Defective Pixel Map (DPM)**.

---

# 13. Defective Pixel Map

The DPM should be stored separately from the image.

Example:

```text
defective_pixels.json
```

or:

```text
defective_pixel_map.npy
```

Example:

```text
{
    "pixel": [row, column],
    "type": "dead",
    "confidence": 0.98
}
```

For a real camera, a compact representation could be:

```text
(row, column, type)
```

Example:

```text
(102, 204, DEAD)
(551, 823, HOT)
(991, 442, STUCK)
```

---

# 14. How Do We Correct a Dead Pixel?

Once a defective pixel is identified:

```text
RAW
 ↓
Defective Pixel Map
 ↓
Replacement / interpolation
 ↓
Corrected RAW
```

The simplest approach is neighboring-pixel interpolation.

---

# 15. Same-Color Neighbor Interpolation

For a Bayer sensor, do not blindly average the four physically closest pixels.

Instead, use pixels belonging to the same CFA component.

For example:

```text
R G R G R
G B G B G
R G X G R
G B G B G
R G R G R
```

If `X` is a defective R pixel, use surrounding R pixels:

```text
R       R
    X
R       R
```

A simple estimate:

```text
X_corrected =
    median(R_neighbors)
```

Median filtering is often preferable to a simple mean because it is more robust to edges and outliers.

---

# 16. Directional Interpolation

A better method considers horizontal and vertical structure.

For example:

```text
horizontal estimate:

(R_left + R_right) / 2


vertical estimate:

(R_up + R_down) / 2
```

Compare local gradients:

```text
horizontal gradient
        vs
vertical gradient
```

Then choose the direction with lower variation.

Conceptually:

```text
        R
        │
R ───── X ───── R
        │
        R

If horizontal structure is smoother:

X ≈ horizontal interpolation

Otherwise:

X ≈ vertical interpolation
```

This reduces artifacts around edges.

---

# 17. Correction of Hot Pixels

Hot pixels can be corrected in the same way.

Example:

```text
52  54  53
51 900  55
53  52  54
```

If `900` is classified as a hot pixel:

```text
corrected ≈ median(neighboring same-color pixels)
```

The important distinction is that the pixel should be corrected because it is present in the DPM, rather than simply applying a generic median filter to the entire RAW image.

---

# 18. Why a Generic Median Filter Is Not the Ideal Solution

We should not simply do:

```text
RAW
 ↓
Median Filter
 ↓
Demosaic
```

because this can remove legitimate image information.

For example:

```text
Fine edge
Texture
Thin structure
High-frequency detail
```

may be modified.

The preferred strategy is:

```text
Detect defective pixels
        ↓
Create defect map
        ↓
Modify only defective pixels
        ↓
Leave healthy pixels untouched
```

This is much more appropriate for an ISP.

---

# 19. Clustered Defective Pixels

Consider:

```text
D D D
D D D
D D D
```

There may not be enough valid same-color neighbors inside the immediate neighborhood.

In this situation we may need:

```text
Larger neighborhood
        ↓
Directional interpolation
        ↓
Polynomial interpolation
        ↓
Edge-aware reconstruction
```

If the defective region is large, the sensor may require factory calibration or more sophisticated reconstruction.

---

# 20. Detection Thresholds

Detection thresholds should not be arbitrary.

For example:

```text
pixel < threshold
```

is not sufficient.

A better model uses sensor statistics.

For example:

```text
μ = local mean
σ = local standard deviation

z = |pixel - μ| / σ
```

A pixel may be classified as suspicious when:

```text
z > threshold
```

The threshold should be determined experimentally.

For example:

```text
3σ
5σ
6σ
```

can be evaluated during calibration.

---

# 21. Defective Pixel Classification

A useful classification strategy is:

### Dead

```text
Low response
+
Low temporal variation
+
Fails to respond to illumination
```

### Hot

```text
Abnormally high dark-frame response
+
Persistent across frames
```

### Stuck

```text
Very low response to exposure changes
+
Output remains approximately constant
```

### Warm

```text
Elevated dark response
+
Temperature dependent
```

### Intermittent

```text
Abnormal only in a subset of frames
```

### Cluster

```text
Multiple neighboring defective pixels
```

---

# 22. Temperature Matters

Sensor temperature can significantly affect defective-pixel behavior.

Therefore, a production-quality calibration system may construct DPMs for different temperatures:

```text
Temperature
    │
    ├── 20°C → DPM_20
    ├── 40°C → DPM_40
    └── 60°C → DPM_60
```

The ISP can then select the appropriate map.

This is particularly relevant for:

* Automotive cameras
* Robotics
* Long-duration operation
* High-resolution sensors
* High-ISO operation

---

# 23. Where Should This Stage Exist in Our ISP?

For our project, I recommend:

```text
                 RAW
                  │
                  ▼
        RAW Validation
                  │
                  ▼
       Defective Pixel Detection
              / Correction
                  │
                  ▼
       Black-Level Correction
                  │
                  ▼
          Lens Shading Correction
                  │
                  ▼
          Bayer Processing
                  │
                  ▼
            White Balance
                  │
                  ▼
             Demosaicing
                  │
                  ▼
                 CCM
                  │
                  ▼
           Tone Mapping
                  │
                  ▼
                Gamma
                  │
                  ▼
              Denoising
                  │
                  ▼
             Sharpening
                  │
                  ▼
                 RGB
```

For the actual implementation, we should verify the exact ordering of DPC relative to black-level correction based on the sensor's calibration model.

---

# 24. Important Distinction: Detection vs Correction

These are two different problems.

### Detection

```text
Which pixels are defective?
```

Output:

```text
Defective Pixel Map
```

### Correction

```text
What value should replace the defective pixel?
```

Output:

```text
Corrected RAW
```

They should therefore be implemented as separate modules.

For example:

```text
camera_isp/
│
├── isp/
│   ├── defective_pixel_detection.py
│   └── defective_pixel_correction.py
│
└── calibration/
    └── defective_pixel_map.py
```

---

# 25. Our Current Implementation

Our current implementation was inspected specifically for this question.

The current pipeline contains:

```python
raw = read_raw(...)

corrected = apply_black_level(
    raw.data,
    offset=BLACK_LEVEL,
)

channels = extract_bayer_channels(
    corrected,
    BAYER_PATTERN,
)

R, G1, G2, B = apply_white_balance(...)

wb_bayer[0::2, 0::2] = G1
wb_bayer[0::2, 1::2] = R
wb_bayer[1::2, 0::2] = B
wb_bayer[1::2, 1::2] = G2

rgb_before_ccm = demosaic_bilinear(
    wb_bayer,
    BAYER_PATTERN,
)

rgb = apply_ccm(
    rgb_before_ccm,
    ccm,
)
```

This confirms that the current pipeline performs:

```text
RAW
 ↓
Black-Level Correction
 ↓
Bayer Extraction
 ↓
White Balance
 ↓
Bayer Reconstruction
 ↓
Bilinear Demosaicing
 ↓
CCM
```

but **does not currently perform explicit defective-pixel detection or correction**.

The same pipeline structure appears in the other current implementation copy as well.

---

# 26. What About the Negative Pixel Values We Observed?

This is important.

Our previous dataset analysis showed negative values after black-level correction, for example:

```text
R minimum ≈ -1080
G minimum ≈ -1024
B minimum ≈ -683
```

and non-zero percentages of negative values.

These values should **not automatically be interpreted as dead pixels**.

A negative value after:

```text
I_corrected = I_raw - black_level
```

can occur because the chosen black-level estimate is not necessarily the exact per-pixel/per-channel sensor offset.

For example:

```text
RAW = 20 DN
Black level = 64 DN

20 - 64 = -44 DN
```

That tells us something about the black-level model, but does not by itself prove that the physical pixel is dead.

Therefore:

> **Black-level correction and defective-pixel correction must not be conflated.**

---

# 27. What We Should Do Next in Our Project

I recommend adding a dedicated **Phase: Defective Pixel Characterization** before we proceed too deeply into Bayer reconstruction.

Our pipeline becomes:

```text
                  INTEL-TAU RAW
                       │
                       ▼
                 RAW Inspection
                       │
                       ▼
            Defective Pixel Analysis
                       │
              ┌────────┴────────┐
              ▼                 ▼
         Detection          Classification
              │                 │
              └────────┬────────┘
                       ▼
              Defective Pixel Map
                       │
                       ▼
             Defective Pixel Correction
                       │
                       ▼
              Black-Level Correction
                       │
                       ▼
              Bayer Reconstruction
                       │
                       ▼
                  Demosaicing
```

However, there is an important limitation:

**We should not declare pixels dead from the existing 464 RAW frames alone without first understanding whether the dataset provides calibration/dark/flat-field information.**

Our current dataset report confirms that we processed 464 Sony IMX135 frames, using an experimentally chosen 64 DN black level and GRBG Bayer pattern.

So the next investigation should be:

```text
INTEL-TAU / Sony IMX135
        ↓
Find calibration information
        ↓
Check dark frames
        ↓
Check flat-field / reference data
        ↓
Analyze persistent pixel outliers
        ↓
Generate DPM
        ↓
Validate correction
```

---

# 28. Validation

A defective-pixel implementation should not be considered complete merely because the image looks cleaner.

We should measure:

### Detection

```text
True defective pixels detected
False positives
False negatives
Precision
Recall
```

### Correction

```text
RAW residual error
Local smoothness
Edge preservation
Color error
PSNR
SSIM
```

### Downstream perception

```text
Detection mAP
Segmentation mIoU
Recall
Confidence stability
```

Most importantly:

```text
Original RAW
      ↓
ISP
      ↓
Perception


Corrected RAW
      ↓
ISP
      ↓
Perception
```

should be compared under controlled conditions.

---

# 29. Final Design for Our Camera ISP

The long-term architecture should therefore include:

```text
                         RAW SENSOR
                             │
                             ▼
                    RAW Validation
                             │
                             ▼
                 Defective Pixel Correction
                             │
                             ▼
                    Black-Level Correction
                             │
                             ▼
                  Lens Shading Correction
                             │
                             ▼
                       Bayer Processing
                             │
                             ▼
                    White Balance / AWB
                             │
                             ▼
                       Demosaicing
                             │
                             ▼
                  Color Correction Matrix
                             │
                             ▼
                       Tone Mapping
                             │
                             ▼
                          Gamma
                             │
                             ▼
                        Denoising
                             │
                             ▼
                        Sharpening
                             │
                             ▼
                            RGB
                             │
                             ▼
                        Perception
```

The defective-pixel module is therefore not just an optional image-enhancement feature.

It belongs to the **sensor-correction portion of the ISP**.

---

# 30. Key Takeaways

### A dead pixel

A photosite that has little or no useful response to light.

### A hot pixel

A photosite producing abnormally high values, especially in darkness.

### A stuck pixel

A photosite whose output remains approximately constant regardless of illumination.

### Detection

Should ideally use:

```text
Dark frames
+
Flat fields
+
Spatial analysis
+
Temporal analysis
+
Exposure variation
```

### Correction

Prefer:

```text
Defective Pixel Map
        ↓
Same-Bayer-color neighbors
        ↓
Median / directional / edge-aware interpolation
```

rather than applying a generic filter to the whole image.

### Our current implementation

Currently:

```text
❌ No explicit dead-pixel detection
❌ No defective-pixel map
❌ No hot-pixel classification
❌ No stuck-pixel classification
❌ No RAW defective-pixel correction

✓ RAW reading
✓ Black-level correction
✓ Bayer extraction
✓ White balance
✓ Bayer reconstruction
✓ Bilinear demosaicing
✓ CCM
```

Therefore, **dead/defective pixel processing is currently a genuine gap in our implementation**, and I would add it before treating our RAW-to-RGB pipeline as a complete classical ISP.
