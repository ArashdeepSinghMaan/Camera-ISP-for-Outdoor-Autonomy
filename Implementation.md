# Adaptive Camera ISP for Outdoor Robotics

## Research-Oriented Image Signal Processing Pipeline

A modular, hardware-aware and perception-oriented Camera Image Signal Processing (ISP) pipeline designed for robotic vision.

The project is implemented in two stages:

1. **Standalone ISP** — a ROS-independent implementation for algorithm development, dataset processing, experimentation and benchmarking.
2. **ROS 2 Humble ISP** — a real-time robotics deployment layer built on top of the standalone ISP core.

The long-term objective is to investigate whether **adaptive camera image processing can improve the robustness of robotic perception under changing illumination and environmental conditions**.

---

# 1. Project Vision

A conventional camera pipeline can be represented as:

```text
Camera Sensor
      │
      ▼
   RAW Bayer
      │
      ▼
 Black Level Correction
      │
      ▼
 Lens Shading Correction
      │
      ▼
 Demosaicing
      │
      ▼
 White Balance
      │
      ▼
 Color Correction
      │
      ▼
 Tone Mapping
      │
      ▼
 Gamma
      │
      ▼
 Noise Reduction
      │
      ▼
 Sharpening
      │
      ▼
 RGB Image
      │
      ▼
 Perception
```

Most conventional pipelines use fixed or manually tuned parameters.

This project investigates a different approach:

```text
                    Scene
                      │
                      ▼
              Scene Estimation
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Lighting      Weather     Exposure
          │           │           │
          └───────────┼───────────┘
                      ▼
              ISP Parameter Model
                      │
                      ▼
               Adaptive ISP
                      │
                      ▼
               RGB Image
                      │
                      ▼
                 Perception
```

The central question is:

> Can the ISP adapt its processing parameters according to the scene so that the resulting image is more suitable for robotic perception?

The objective is therefore **not simply image enhancement**.

The objective is:

```text
Sensor Data
    ↓
Camera ISP
    ↓
Scene-adaptive Image
    ↓
Robotic Perception
    ↓
Quantitative Evaluation
```

---

# 2. Research Questions

## Primary Research Question

> Does adaptive image signal processing improve the robustness of camera-based perception for robots operating under changing environmental and illumination conditions?

## Secondary Questions

1. Which ISP stages have the greatest influence on perception?
2. Does better visual image quality necessarily result in better machine perception?
3. Can ISP parameters be predicted automatically from an input scene?
4. Can one ISP configuration work across different illumination conditions?
5. Can adaptive processing reduce perception degradation under difficult conditions?
6. What is the computational cost of adaptive ISP?
7. Can a perception-aware ISP outperform an image-quality-only ISP?
8. How much of the ISP should remain classical and how much should be learned?

---

# 3. Dataset Strategy

The project will use multiple datasets for different purposes.

## 3.1 INTEL-TAU

INTEL-TAU will be the primary dataset for the **RAW-domain ISP development stage**.

INTEL-TAU contains 7,022 scenes captured using:

* Canon 5DSR
* Nikon D810
* Sony IMX135

It provides RAW Bayer data as well as processed variants and illumination ground truth. The dataset also provides camera-specific information such as Bayer layout and frame dimensions. The RAW dataset is approximately 290 GB, while the preprocessed dataset is approximately 50 GB.

Dataset resource:

[INTEL-TAU Dataset — Tampere University](https://researchportal.tuni.fi/en/datasets/intel-tau/?utm_source=chatgpt.com)

Associated publication:

Laakom et al., **"INTEL-TAU: A Color Constancy Dataset," IEEE Access, 2021**.

## 3.2 Role of INTEL-TAU

INTEL-TAU will primarily be used for:

```text
RAW Bayer
    ↓
Black-Level Correction
    ↓
Demosaicing
    ↓
White Balance
    ↓
Color Correction
    ↓
Gamma / Tone Mapping
    ↓
RGB
```

and for validating:

* White balance
* Illumination estimation
* Demosaicing
* Color correction
* Camera invariance
* Color shading
* RAW-to-RGB processing

The dataset provides ground-truth white points, and the RAW variant provides `.plain16` RAW images, `.ccm` color correction matrices and `.wp` white-point files.

---

# 4. Important Dataset Limitation

INTEL-TAU should **not** be treated as the complete dataset for the robotics part of this project.

Its primary purpose is illumination estimation and color constancy.

Therefore:

```text
                    Camera ISP Project
                           │
             ┌─────────────┴─────────────┐
             │                           │
        ISP Development            Robotics Evaluation
             │                           │
        INTEL-TAU                  ROS/ROS2 bags
             │                           │
       RAW processing             Real robot images
       AWB / CCM                  Environment changes
       Demosaicing                Perception
       Color science              Navigation
```

This separation will make the research methodology much stronger.

---

# 5. Two-Version Architecture

The final repository will contain two implementations.

## Version A — Standalone

```text
Image / RAW File
      │
      ▼
Dataset Reader
      │
      ▼
ISP Core
      │
      ▼
Processed Image
      │
      ├──────────────► Image Quality Metrics
      │
      ├──────────────► Color Constancy Metrics
      │
      └──────────────► Perception Model
```

This version has:

* No ROS dependency
* Python API
* C++ core where useful
* Dataset readers
* Experiment scripts
* Visualization
* Benchmarking
* Model training
* Configuration files

## Version B — ROS 2 Humble

```text
/camera/image_raw
       │
       ▼
 Camera ISP Node
       │
       ├──────► /camera_isp/image
       │
       ├──────► /camera_isp/debug
       │
       └──────► /camera_isp/parameters
```

The ROS implementation will call the same ISP core.

---

# 6. Design Principle

The most important architectural rule is:

> **ROS must be an interface layer, not part of the ISP algorithm.**

Therefore:

```text
                 ┌─────────────────────┐
                 │      ISP CORE       │
                 │                     │
                 │ RAW processing      │
                 │ AWB                 │
                 │ CCM                 │
                 │ Gamma               │
                 │ Tone mapping        │
                 │ Denoising           │
                 │ Sharpening          │
                 │ Scene estimation     │
                 │ Adaptive control     │
                 └──────────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
             Standalone              ROS2
               API                    Node
```

This allows us to test the ISP independently from ROS.

---

# 7. Standalone Version Architecture

The first implementation will be organized as:

```text
Input
 │
 ▼
Data Loader
 │
 ▼
Input Normalization
 │
 ▼
RAW / RGB Detection
 │
 ├─────────────── RAW
 │                  │
 │                  ▼
 │             Black Level
 │                  │
 │                  ▼
 │             Lens Shading
 │                  │
 │                  ▼
 │             Demosaicing
 │
 └─────────────── RGB
                    │
                    ▼
              Common ISP Path
                    │
                    ▼
             White Balance
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
             Output RGB
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Image Evaluation      Perception
```

---

# 8. Phase 0 — Repository Setup

Initial repository:

```text
camera_isp/
│
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
│
├── configs/
│   ├── camera/
│   ├── isp/
│   ├── experiments/
│   └── datasets/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── metadata/
│
├── camera_isp/
│   ├── io/
│   ├── raw/
│   ├── isp/
│   ├── adaptive/
│   ├── metrics/
│   ├── perception/
│   └── visualization/
│
├── cpp/
│   ├── raw/
│   ├── isp/
│   └── bindings/
│
├── scripts/
│   ├── inspect_dataset.py
│   ├── extract_samples.py
│   ├── run_pipeline.py
│   ├── evaluate.py
│   └── benchmark.py
│
├── experiments/
│   ├── 01_raw_pipeline/
│   ├── 02_white_balance/
│   ├── 03_color_correction/
│   ├── 04_tone_mapping/
│   ├── 05_fixed_isp/
│   ├── 06_adaptive_rules/
│   └── 07_learning_based/
│
├── models/
│
├── results/
│
└── docs/
    ├── architecture.md
    ├── camera_data.md
    ├── raw_format.md
    ├── isp_modules.md
    ├── experiments.md
    └── benchmarks.md
```

---

# 9. Phase 1 — Dataset Inspection

Before implementing any ISP algorithm, the first task is to understand the actual data.

For INTEL-TAU we need to determine:

```text
Camera
Resolution
Bit depth
RAW format
Bayer pattern
Black level
Saturation level
White point format
CCM format
File organization
```

The RAW files are stored in a 2-byte-per-pixel format and can be interpreted as `uint16`; camera-specific information required for reading the RAW data is provided in the dataset metadata.

## First tool

Create:

```text
scripts/inspect_intel_tau.py
```

It should report:

```text
Camera:
Image:
Width:
Height:
Bit depth:
Bayer pattern:
Black level:
Maximum value:
RAW dtype:
White point:
CCM available:
```

Example:

```bash
python scripts/inspect_intel_tau.py \
    --dataset /path/to/INTEL-TAU
```

---

# 10. Phase 2 — RAW Reader

Implement:

```text
camera_isp/io/raw_reader.py
```

Responsibilities:

1. Read `.plain16`
2. Load camera metadata
3. Determine width and height
4. Determine Bayer pattern
5. Convert bytes → uint16
6. Validate dimensions
7. Return a structured RAW object

Conceptual API:

```python
raw = read_raw(
    path,
    width=...,
    height=...,
    bayer_pattern="RGGB"
)
```

The reader should never silently guess the Bayer pattern.

Incorrect Bayer interpretation can corrupt the entire ISP pipeline.

---

# 11. Phase 3 — RAW Normalization

Raw sensor values should first be converted into a normalized representation.

Given:

```text
I_raw
B = black level
S = saturation level
```

black-level correction:

```text
I_blc = I_raw - B
```

and normalization:

```text
I_norm = (I_raw - B) / (S - B)
```

The result should be clipped:

```text
I_norm = clip(I_norm, 0, 1)
```

This stage should support:

```text
uint16 RAW
      ↓
Black Level Correction
      ↓
Normalized Float32 RAW
```

---

# 12. Phase 4 — Bayer Visualization

Before demosaicing, implement a Bayer diagnostic viewer.

It should visualize:

```text
RAW image
R channel samples
G channel samples
B channel samples
Bayer pattern
Histogram
```

Example:

```text
RGGB

R G R G
G B G B
R G R G
G B G B
```

This is an important debugging stage.

---

# 13. Phase 5 — Demosaicing

Convert:

```text
Bayer RAW
    ↓
RGB
```

Implement the following in sequence.

## Version 1

Bilinear demosaicing.

## Version 2

OpenCV demosaicing.

## Version 3

Edge-aware demosaicing.

## Version 4

Potential learned demosaicing.

The first implementation should remain classical.

---

# 14. Demosaicing Evaluation

Evaluate:

```text
Bilinear
vs
OpenCV
vs
Edge-aware
```

Metrics may include:

* PSNR
* SSIM
* Color error
* Edge preservation
* Visual artifacts

Where appropriate, compare against the processed/reference images provided by the dataset.

---

# 15. Phase 6 — Automatic White Balance

Implement several AWB algorithms.

## 15.1 Ground Truth White Point

INTEL-TAU provides illumination/white-point ground truth.

Use this initially for validation.

---

## 15.2 Gray World

Calculate:

```text
mean_R
mean_G
mean_B
```

Then estimate gains:

```text
gain_R = mean_G / mean_R
gain_B = mean_G / mean_B
```

Apply:

```text
R' = gain_R R
G' = G
B' = gain_B B
```

---

## 15.3 White Patch

Find bright pixels and estimate the illuminant from them.

---

## 15.4 Learning-Based AWB

Later:

```text
Image
  ↓
CNN
  ↓
Illumination Estimate
  ↓
RGB Gains
```

This should not be the first implementation.

---

# 16. Phase 7 — Color Correction Matrix

The camera sensor color space must be transformed toward a target color space.

Use:

```text
[R']       [m11 m12 m13] [R]
[G']   =   [m21 m22 m23] [G]
[B']       [m31 m32 m33] [B]
```

INTEL-TAU provides CCM information for the RAW data.

Implement:

```text
camera_isp/isp/color_correction.py
```

API:

```python
rgb_corrected = apply_ccm(
    rgb,
    ccm
)
```

---

# 17. Phase 8 — Gamma

Implement configurable gamma transformation.

For normalized intensity:

```text
I_out = I_in^(1/gamma)
```

The exact convention must be documented and tested.

Do not assume that every dataset or camera uses the same gamma convention.

---

# 18. Phase 9 — Tone Mapping

Implement classical methods:

### Global

```text
Global tone curve
```

### Local

```text
CLAHE
```

### Highlight compression

```text
Highlight roll-off
```

### Shadow enhancement

```text
Shadow lifting
```

These should remain independent modules.

Example:

```python
output = tone_mapper.process(
    image,
    method="clahe",
    strength=0.4
)
```

---

# 19. Phase 10 — Denoising

Implement:

```text
Gaussian
Median
Bilateral
Non-local Means
```

Later investigate:

```text
Learned Denoiser
```

The primary trade-off is:

```text
Noise reduction
       ↕
Detail preservation
```

Evaluation must therefore include edge/detail preservation.

---

# 20. Phase 11 — Sharpening

Implement unsharp masking:

```text
I_sharp = I + α(I - Blur(I))
```

Parameters:

```text
alpha
blur_sigma
```

must be configurable.

Excessive sharpening should be explicitly measured because it can create artificial edges and adversely affect perception.

---

# 21. Phase 12 — Fixed Classical ISP

Once individual modules are validated, combine them.

Initial pipeline:

```text
RAW
 ↓
Black Level
 ↓
Demosaic
 ↓
White Balance
 ↓
CCM
 ↓
Gamma
 ↓
Tone Mapping
 ↓
Denoising
 ↓
Sharpening
 ↓
RGB
```

This becomes:

# Fixed ISP Baseline

The fixed configuration is essential because all adaptive experiments will be compared against it.

---

# 22. Configuration System

Do not hard-code ISP parameters.

Use YAML/JSON configuration.

Example:

```yaml
input:
  format: raw
  bit_depth: 16
  bayer_pattern: RGGB

black_level:
  enabled: true
  value: 512

demosaic:
  enabled: true
  method: bilinear

white_balance:
  enabled: true
  method: gray_world

color_correction:
  enabled: true

gamma:
  enabled: true
  value: 2.2

tone_mapping:
  enabled: true
  method: clahe
  strength: 0.3

denoise:
  enabled: true
  method: bilateral
  strength: 0.2

sharpen:
  enabled: true
  strength: 0.15
```

Then:

```bash
python scripts/run_pipeline.py \
    --config configs/isp/fixed_isp.yaml
```

---

# 23. Phase 13 — ISP Ablation Framework

Before developing adaptive ISP, measure every module independently.

For example:

```text
Baseline
Baseline + AWB
Baseline + CCM
Baseline + Tone Mapping
Baseline + Denoising
Baseline + Sharpening
Full ISP
```

Create an experiment table:

| Experiment | AWB | CCM | Tone | Denoise | Sharp |
| ---------- | --: | --: | ---: | ------: | ----: |
| E0         |  No |  No |   No |      No |    No |
| E1         | Yes |  No |   No |      No |    No |
| E2         | Yes | Yes |   No |      No |    No |
| E3         | Yes | Yes |  Yes |      No |    No |
| E4         | Yes | Yes |  Yes |     Yes |    No |
| E5         | Yes | Yes |  Yes |     Yes |   Yes |

This will tell us which stages actually matter.

---

# 24. Phase 14 — Scene Estimation

After establishing the fixed ISP, introduce adaptation.

The scene estimator should initially calculate classical image statistics.

Features:

```text
Mean brightness
Median brightness
Percentile brightness
Dynamic range
Clipped highlights
Clipped shadows
RGB statistics
Color temperature estimate
Saturation
Local contrast
Noise estimate
Edge density
```

Example:

```python
features = estimate_scene(image)
```

Output:

```python
{
    "brightness": 0.31,
    "dynamic_range": 0.74,
    "highlight_clipping": 0.03,
    "shadow_clipping": 0.12,
    "noise": 0.08,
    "contrast": 0.41
}
```

---

# 25. Phase 15 — Rule-Based Adaptive ISP

This is the first adaptive implementation.

Example:

```text
                Scene
                  │
                  ▼
          Scene Statistics
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     Lighting   Noise     Contrast
        │         │         │
        └─────────┼─────────┘
                  ▼
            Rule Engine
                  │
                  ▼
           ISP Parameters
```

Example rules:

```text
IF brightness is low:

    increase shadow lifting
    increase denoising
    reduce sharpening

IF highlight clipping is high:

    compress highlights
    reduce aggressive tone expansion

IF noise is high:

    increase denoising
    reduce sharpening

IF contrast is low:

    increase local contrast

IF estimated fog condition is high:

    modify tone mapping
    increase local contrast
```

The exact rules will be experimentally determined rather than assumed to be optimal.

---

# 26. Phase 16 — Adaptive Parameter Vector

Represent the ISP configuration as a parameter vector:

```text
θ = [
    gamma,
    contrast,
    tone_strength,
    denoise_strength,
    sharpening_strength,
    wb_gain_R,
    wb_gain_B
]
```

The adaptive system becomes:

```text
Image
  ↓
Scene Encoder
  ↓
Feature Vector
  ↓
Parameter Predictor
  ↓
θ
  ↓
ISP
  ↓
Output Image
```

---

# 27. Phase 17 — Learning-Based Adaptive ISP

After the rule-based system is stable, implement a learned parameter predictor.

Initial architecture:

```text
Input Image
     │
     ▼
MobileNet / EfficientNet
     │
     ▼
Global Average Pooling
     │
     ▼
MLP
     │
     ▼
ISP Parameter Vector
```

Output:

```text
gamma
contrast
denoise
sharpen
tone mapping
WB gains
```

The first learned model should be deliberately small.

The objective is not to build another large vision network.

The objective is to learn:

> **Which ISP configuration should be applied to this scene?**

---

# 28. Phase 18 — Parameter Constraints

The neural network must not directly produce arbitrary ISP parameters.

Use bounded outputs.

For example:

```text
gamma ∈ [0.5, 3.0]

denoise ∈ [0, 1]

sharpen ∈ [0, 1]

contrast ∈ [0.5, 2.0]

WB gain ∈ [0.5, 2.5]
```

Use appropriate activations or parameter transformations.

This prevents unstable ISP outputs.

---

# 29. Phase 19 — Perception Integration

The next stage is to connect the ISP to a perception model.

Initially use a fixed pretrained model.

Example:

```text
Original Image
       │
       ▼
 YOLO
       │
       ▼
Detection Metrics
```

Then:

```text
Original
   │
   ▼
Adaptive ISP
   │
   ▼
 YOLO
   │
   ▼
Detection Metrics
```

The perception model should initially remain frozen.

This isolates the effect of the ISP.

---

# 30. Baseline Experiments

At minimum implement:

## Baseline A

```text
Original
 ↓
Perception
```

## Baseline B

```text
Original
 ↓
Fixed ISP
 ↓
Perception
```

## Baseline C

```text
Original
 ↓
Rule-Based Adaptive ISP
 ↓
Perception
```

## Baseline D

```text
Original
 ↓
Learning-Based Adaptive ISP
 ↓
Perception
```

Comparison:

```text
                Image Quality
                     +
              Perception
                     +
                 Latency
```

---

# 31. Perception Metrics

For object detection:

```text
Precision
Recall
mAP@50
mAP@50-95
```

For segmentation:

```text
mIoU
Dice/F1
Pixel Accuracy
Per-Class IoU
```

The primary comparison should be performed per environmental condition.

Example:

```text
             Original   Fixed ISP   Adaptive ISP

Day             X           X            X
Low Light       X           X            X
Night           X           X            X
Fog             X           X            X
Rain            X           X            X
```

---

# 32. Image Quality Metrics

Where a suitable reference exists:

```text
PSNR
SSIM
LPIPS
ΔE
```

Without a reference image:

```text
Brightness
Contrast
Dynamic range
Clipping
Noise
Saturation
Sharpness
```

Important:

> A no-reference image-quality improvement must not automatically be interpreted as a perception improvement.

Both must be evaluated independently.

---

# 33. Color Constancy Metrics

For INTEL-TAU specifically, evaluate illumination estimation.

Given predicted white point:

```text
p_pred
```

and ground truth:

```text
p_gt
```

calculate angular error:

```text
error =
acos(
    (p_pred · p_gt) /
    (||p_pred|| ||p_gt||)
)
```

Report:

```text
Mean Angular Error
Median Angular Error
Percentile Errors
```

This allows the RAW ISP development to be quantitatively evaluated before introducing robotics perception.

---

# 34. Computational Evaluation

Every implementation must be benchmarked.

Measure:

```text
RAW loading time
Black-level time
Demosaicing time
AWB time
CCM time
Tone mapping time
Denoising time
Sharpening time
Total ISP time
```

Example:

```text
RAW loading       4.1 ms
Black level       0.4 ms
Demosaicing       5.2 ms
AWB               0.7 ms
CCM               0.3 ms
Tone mapping      2.1 ms
Denoising         4.5 ms
Sharpening        0.8 ms
--------------------------------
Total            18.1 ms
```

Later measure:

```text
CPU utilization
GPU utilization
RAM
VRAM
FPS
```

---

# 35. C++ / Python Strategy

The first standalone implementation can be primarily Python for research speed.

Recommended split:

```text
Python
 ├── Dataset handling
 ├── Experiments
 ├── Configuration
 ├── Metrics
 ├── Visualization
 └── ML models

C++
 ├── RAW processing
 ├── Demosaicing
 ├── Pixel operations
 ├── ISP kernels
 └── Performance-critical operations
```

Python can call the C++ implementation through bindings when required.

Do not optimize everything in C++ from day one.

First establish correctness.

Then optimize bottlenecks.

---

# 36. GPU Strategy

GPU acceleration should come after the CPU reference implementation is correct.

Possible progression:

```text
CPU NumPy
    ↓
OpenCV
    ↓
C++
    ↓
CUDA
    ↓
TensorRT / Jetson
```

Each implementation must produce numerically comparable results.

---

# 37. Experiment Reproducibility

Every experiment must save:

```text
Configuration
Dataset version
Input camera
Random seed
Model version
ISP parameters
Runtime
Metrics
Output images
```

Example:

```text
results/
└── experiment_001/
    ├── config.yaml
    ├── metrics.json
    ├── runtime.json
    ├── predictions/
    ├── images/
    └── log.txt
```

---

# 38. Visualization

Create a standard visualization format.

For every experiment:

```text
┌──────────────────────────────────────────┐
│ Original                                 │
├──────────────────────────────────────────┤
│ Fixed ISP                                │
├──────────────────────────────────────────┤
│ Adaptive ISP                             │
├──────────────────────────────────────────┤
│ Difference / Enhancement Visualization   │
└──────────────────────────────────────────┘
```

Also visualize:

```text
RAW Bayer
Demosaiced
White-balanced
Color-corrected
Tone-mapped
Denoised
Final
```

This will be extremely useful for debugging the ISP.

---

# 39. Experiment Tracking

Each experiment should have a unique ID.

Example:

```text
EXP-001
EXP-002
EXP-003
```

Metadata:

```yaml
experiment: EXP-014

dataset:
  name: INTEL-TAU
  camera: Sony_IMX135

pipeline:
  demosaic: bilinear
  awb: gray_world
  ccm: true
  tone_mapping: clahe
  denoise: bilateral
  sharpening: true

metrics:
  angular_error: ...
  psnr: ...
  ssim: ...
```

---

# 40. Recommended Development Order

Do NOT start with the neural adaptive ISP.

Follow this exact order:

```text
1. Dataset inspection
        ↓
2. RAW reader
        ↓
3. RAW visualization
        ↓
4. Black-level correction
        ↓
5. Demosaicing
        ↓
6. White balance
        ↓
7. CCM
        ↓
8. Gamma
        ↓
9. Tone mapping
        ↓
10. Denoising
        ↓
11. Sharpening
        ↓
12. Fixed ISP
        ↓
13. ISP evaluation
        ↓
14. Scene statistics
        ↓
15. Rule-based adaptation
        ↓
16. Perception evaluation
        ↓
17. Learning-based adaptation
        ↓
18. Perception-aware optimization
        ↓
19. C++ optimization
        ↓
20. GPU optimization
        ↓
21. ROS 2 Humble
```

---

# 41. Version 1 Milestone

The first major milestone should be:

```text
INTEL-TAU RAW
      ↓
RAW Reader
      ↓
Black Level Correction
      ↓
Demosaicing
      ↓
White Balance
      ↓
CCM
      ↓
Gamma
      ↓
RGB
```

with:

```text
Ground Truth White Point
        ↓
Color Constancy Evaluation
```

At this point we will have a **real RAW-domain ISP**, rather than simply an RGB enhancement pipeline.

---

# 42. Version 2 Milestone

Then:

```text
RAW
 ↓
Fixed ISP
 ↓
RGB
```

with configurable:

```text
AWB
CCM
Gamma
Tone Mapping
Denoising
Sharpening
```

and complete benchmarking.

---

# 43. Version 3 Milestone

Rule-based adaptation:

```text
Image
 ↓
Scene Statistics
 ↓
Rule Engine
 ↓
ISP Parameters
 ↓
Adaptive ISP
```

---

# 44. Version 4 Milestone

Learning-based adaptation:

```text
Image
 ↓
CNN
 ↓
ISP Parameters
 ↓
Adaptive ISP
```

---

# 45. Version 5 Milestone

Perception-aware ISP:

```text
Image
 ↓
Adaptive ISP
 ↓
Perception
 ↓
Perception Loss
       │
       └─────────────┐
                     ▼
               ISP optimization
```

Potential objective:

```text
L =
λ_image L_image
+
λ_color L_color
+
λ_perception L_perception
+
λ_runtime L_runtime
```

The exact formulation will be determined experimentally.

---

# 46. ROS 2 Humble Version

Only after the standalone implementation is stable will the ROS version be developed.

The architecture will become:

```text
ROS 2 Camera
     │
     ▼
/camera/image_raw
     │
     ▼
ROS 2 ISP Wrapper
     │
     ▼
Standalone ISP Core
     │
     ▼
/camera_isp/image
     │
     ├──────► Perception
     │
     └──────► Visualization
```

The ROS node should not contain ISP algorithms.

---

# 47. ROS 2 Interface

Expected topics:

```text
/camera/image_raw
/camera/camera_info

/camera_isp/image
/camera_isp/debug
/camera_isp/parameters
/camera_isp/scene
```

Potential services:

```text
/set_isp_mode
/set_isp_parameters
/reset_isp
```

Potential modes:

```text
RAW
FIXED
RULE_ADAPTIVE
LEARNED_ADAPTIVE
```

---

# 48. ROS 2 Parameters

Example:

```yaml
camera_isp:
  ros__parameters:

    mode: "adaptive"

    gamma: 2.2

    tone_mapping:
      enabled: true

    denoise:
      enabled: true

    sharpening:
      enabled: true

    adaptive:
      enabled: true
```

The ROS layer should simply translate ROS parameters/messages into the standalone ISP configuration.

---

# 49. Deployment Target

The final deployment target will be robotic hardware.

Potential hardware:

```text
Desktop GPU
      ↓
Laptop GPU
      ↓
NVIDIA Jetson
```

Eventually:

```text
Camera
 ↓
ROS 2
 ↓
Camera ISP
 ↓
TensorRT Perception
 ↓
Nav2 / Robot System
```

---

# 50. Final System

The complete system should eventually look like:

```text
                         CAMERA
                            │
                            ▼
                       RAW / RGB
                            │
                            ▼
                  ┌───────────────────┐
                  │   Scene Analysis  │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Adaptive ISP      │
                  │                   │
                  │ BLC               │
                  │ Demosaic          │
                  │ AWB               │
                  │ CCM               │
                  │ Gamma             │
                  │ Tone Mapping      │
                  │ Denoise           │
                  │ Sharpen            │
                  └─────────┬─────────┘
                            │
                            ▼
                       RGB IMAGE
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
         Image Quality             Perception
           Evaluation              Model
                │                       │
                │                       ▼
                │                Detection /
                │                Segmentation
                │                       │
                └───────────┬───────────┘
                            ▼
                     Final Evaluation
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
         Image Quality  Perception      Runtime
```

---

# 51. Final Experimental Matrix

The final paper-quality experiment should compare:

```text
                         Original
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           Fixed ISP    Rule Adaptive   Learned Adaptive
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                       Perception
```

Across:

```text
Day
Low illumination
Night
High illumination
Backlighting
Fog
Rain
Shadow-heavy scenes
Motion
Sensor noise
```

where these conditions are actually represented in the selected robotic datasets.

---

# 52. Success Criteria

The project will be considered technically successful if it demonstrates:

## 1. Correct ISP

A physically and computationally consistent image-processing pipeline.

## 2. Adaptive Behavior

The ISP changes its parameters according to scene characteristics.

## 3. Quantitative Benefit

The experiments establish whether adaptive processing changes downstream perception performance.

## 4. Real-Time Potential

The computational cost is measured and optimized toward robotic deployment.

A negative result is also scientifically useful if the experiment is properly controlled.

---

# 53. Research Contribution

The contribution should not be framed as:

> "We implemented several image enhancement techniques."

Instead, the project investigates:

> **How should camera image processing adapt to changing environmental conditions when the ultimate objective is reliable robotic perception?**

The project therefore connects:

```text
RAW Sensor Data
       ↓
Camera ISP
       ↓
Color / Illumination
       ↓
Scene Understanding
       ↓
Adaptive Processing
       ↓
Computer Vision
       ↓
Robotic Perception
       ↓
Real-Time Deployment
```

---

# 54. Final Repository Goal

The completed repository should provide:

```text
camera_isp/
│
├── standalone/
│   ├── RAW processing
│   ├── Classical ISP
│   ├── Adaptive ISP
│   ├── Dataset tools
│   ├── Evaluation
│   └── Benchmarking
│
├── ros2/
│   └── ROS 2 Humble interface
│
├── models/
│
├── experiments/
│
├── results/
│
└── docs/
```

The **standalone directory is the actual research core**.

The ROS 2 implementation is the **robotics deployment interface**.

---

# 55. Immediate Next Step

Do not implement the complete ISP yet.

The first implementation task is:

```text
INTEL-TAU
    ↓
Dataset Inspection
    ↓
Understand directory structure
    ↓
Identify one camera
    ↓
Read one RAW frame
    ↓
Verify dimensions
    ↓
Verify Bayer pattern
    ↓
Display RAW Bayer
    ↓
Verify black level
```

Only after this is correct should we implement:

```text
RAW
 ↓
Black Level Correction
 ↓
Demosaicing
```

This will give us a reliable foundation for the rest of the project.

---

# 56. Project Philosophy

The project will follow four principles:

### Correctness before optimization

```text
Correct
  ↓
Validated
  ↓
Benchmarked
  ↓
Optimized
```

### Classical before learning

```text
Classical ISP
      ↓
Rule-based adaptation
      ↓
Learning-based adaptation
```

### Measurement before claims

Every improvement must be supported by:

```text
Metric
+
Controlled experiment
+
Baseline
```

### Robotics relevance

The final objective is not simply:

```text
"Make the image look better."
```

It is:

```text
"Produce camera data that allows a robot to perceive the world more reliably."
```

---

# 57. Current Implementation Target

### We are currently here:

```text
                    CAMERA ISP
                        │
                        ▼
                 INTEL-TAU RAW
                        │
                        ▼
              ┌──────────────────┐
              │ Dataset Inspection│  ← START HERE
              └─────────┬────────┘
                        ▼
                  RAW Reader
                        ▼
               RAW Visualization
                        ▼
              Black-Level Correction
                        ▼
                  Demosaicing
                        ▼
                White Balance
                        ▼
                      CCM
                        ▼
                 Fixed ISP
                        ▼
              Adaptive ISP
                        ▼
                Perception
                        ▼
                 ROS 2 Humble
```

The first objective is therefore **not the adaptive neural ISP**.

The first objective is to build a **correct RAW → RGB camera pipeline and understand every signal transformation occurring between the sensor and the final image**.
