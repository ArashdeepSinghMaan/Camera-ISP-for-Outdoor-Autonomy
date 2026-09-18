# Camera-ISP-for-Outdoor-Autonomy


## Adaptive Image Signal Processing for Robust Outdooor Perception

A research-oriented Camera ISP project that develops and evaluates an **adaptive image signal processing pipeline for robotic cameras** using real-world ROS/ROS 2 bag data.

The objective is to investigate whether camera image processing can be adapted to changing environmental conditions to improve both **image quality** and **downstream robotic perception performance**.

---

# 1. Problem Statement

Robotic perception systems rely heavily on cameras for object detection, semantic segmentation, localization, navigation, and scene understanding.

However, camera images captured by mobile robots can experience significant degradation due to changing environmental and illumination conditions:

* Bright sunlight
* Shadows
* Low illumination
* Night-time operation
* Overexposure
* Underexposure
* High dynamic range scenes
* Fog
* Rain
* Motion
* Sensor noise
* Color shifts
* Loss of local contrast

A perception model trained on relatively well-conditioned images may therefore experience a reduction in detection or segmentation performance when deployed in such conditions.

Traditional camera ISPs apply a fixed or semi-fixed sequence of operations such as:

```text
Sensor
  ↓
Black-Level Correction
  ↓
Lens Shading Correction
  ↓
Demosaicing
  ↓
Auto White Balance
  ↓
Color Correction
  ↓
Noise Reduction
  ↓
Tone Mapping / Gamma
  ↓
Sharpening
  ↓
RGB Image
```

The parameters of these operations are often determined independently of the downstream perception task.

This creates the central research question:

> **Can an adaptive software ISP select image-processing parameters according to the scene and environmental conditions such that the resulting images are more suitable for robotic perception?**

The project will investigate this question using **real robotic camera data recorded in ROS/ROS 2 bag files**.

---

# 2. Project Objective

The project aims to develop a modular Camera ISP pipeline and evaluate its effect on robotic perception.

The system will have three major objectives:

### Objective 1 — Build a Camera ISP Pipeline

Implement classical image-processing stages such as:

* Black-level correction
* Bayer processing, when RAW data is available
* Demosaicing
* White balance
* Color correction
* Gamma correction
* Tone mapping
* Denoising
* Sharpening

For already processed RGB camera streams, the corresponding RAW-dependent stages will be omitted or simulated where appropriate.

---

### Objective 2 — Make the ISP Adaptive

Instead of using one fixed configuration:

```text
Image → Fixed ISP → Output
```

the proposed system will estimate scene conditions and dynamically modify ISP parameters:

```text
                    ┌────────────────────┐
                    │ Scene/Condition    │
                    │ Estimation Module  │
                    └─────────┬──────────┘
                              │
                         ISP Parameters
                              │
                              ▼
Camera Image ───────► Adaptive ISP ───────► Processed Image
```

Possible scene conditions include:

* Day
* Night
* Low light
* High illumination
* Fog
* Rain
* Backlighting
* Shadow-heavy scenes

---

### Objective 3 — Evaluate the Effect on Robot Perception

The final goal is not simply to produce visually pleasing images.

The processed images will be passed to a perception model such as:

* YOLO
* Semantic segmentation
* Object detection
* Robot scene understanding

Performance will be compared before and after ISP processing.

The key comparison will therefore be:

```text
Original Camera Image
        │
        ▼
   Perception Model
        │
        ▼
Baseline Metrics


Original Camera Image
        │
        ▼
   Adaptive ISP
        │
        ▼
   Perception Model
        │
        ▼
Adaptive ISP Metrics
```

---

# 3. Research Question

The primary research question is:

> **Does adaptive image signal processing improve the robustness of camera-based perception for mobile robots under varying environmental and illumination conditions?**

Secondary questions:

1. Which ISP operations have the largest impact on perception performance?
2. Does image enhancement that improves conventional image-quality metrics also improve perception?
3. Can ISP parameters be automatically selected from the scene?
4. Does one ISP configuration work across different environmental conditions?
5. Can an adaptive ISP improve perception without significantly increasing computational latency?

---

# 4. Hypothesis

We hypothesize that:

> **A scene-adaptive ISP can produce images that are more suitable for downstream perception than a fixed image-processing configuration, particularly under challenging illumination and environmental conditions.**

An important part of the investigation will be testing whether this hypothesis actually holds.

The project will not assume that every enhancement improves perception.

For example:

```text
Higher contrast
     ↓
Visually better image
     ↓
Possibly worse segmentation
```

Therefore, both **image quality** and **perception performance** will be evaluated.

---

# 5. Why Use Robotics ROS Bags?

Instead of relying exclusively on generic photography datasets, this project will use camera data collected from real robotic platforms.

ROS/ROS 2 bags provide valuable information such as:

```text
Camera Images
     +
Camera Calibration
     +
Timestamp
     +
Robot Motion
     +
LiDAR
     +
IMU
     +
Odometry
```

This makes the dataset particularly useful for studying camera processing in robotics.

The project can initially focus on the camera stream and later exploit the additional robot sensors for more advanced experiments.

---

# 6. Input Data

The primary input will be ROS/ROS 2 bag files.

Example:

```text
robot_bag/
├── camera/
├── lidar/
├── imu/
├── odometry/
└── tf/
```

Relevant camera topics may include:

```text
/camera/image_raw
/camera/image_color
/camera/image_rect_color
/camera/camera_info
```

or compressed equivalents.

The exact topic names will depend on the robot and recording configuration.

---

# 7. Important RAW vs RGB Consideration

A true hardware-oriented ISP normally operates on sensor RAW data:

```text
RAW Bayer
    ↓
Black Level
    ↓
Lens Shading
    ↓
Demosaicing
    ↓
AWB
    ↓
CCM
    ↓
Gamma
    ↓
Tone Mapping
    ↓
RGB
```

However, many ROS camera bags contain images that have already passed through the camera manufacturer's ISP:

```text
Camera Sensor
     ↓
Hardware ISP
     ↓
RGB
     ↓
ROS Bag
```

Therefore, the project will first inspect the bag files.

### Case A — RAW Bayer available

We can implement a much more complete ISP.

### Case B — RGB/YCbCr images available

We will implement a **software ISP / post-ISP enhancement pipeline** and study adaptive processing.

This distinction will be explicitly documented in the project.

---

# 8. Proposed Architecture

```text
                    ROS / ROS2 BAG
                          │
                          ▼
                  Camera Data Reader
                          │
                          ▼
                  Frame Extraction
                          │
                          ▼
                 Camera Calibration
                          │
                          ▼
                ┌──────────────────┐
                │ Scene Estimation │
                │                  │
                │ illumination     │
                │ weather          │
                │ exposure         │
                │ image statistics │
                └────────┬─────────┘
                         │
                         ▼
                 ISP Parameter Model
                         │
                         ▼
              ┌──────────────────────┐
              │    Adaptive ISP      │
              │                      │
              │ WB                   │
              │ Denoising            │
              │ Contrast             │
              │ Tone Mapping         │
              │ Gamma                │
              │ Sharpening           │
              └──────────┬───────────┘
                         │
                         ▼
                  Processed Image
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Image Quality            Perception
         Evaluation             Evaluation
              │                     │
              ▼                     ▼
       PSNR / SSIM / ΔE       mAP / Recall
       Contrast / Noise       Segmentation
                              Performance
```

---

# 9. ISP Modules

## 9.1 Black-Level Correction

Remove the sensor's black-level offset:

```text
I_corrected = I_raw - B
```

where:

* `I_raw` = sensor pixel value
* `B` = black-level offset

This stage is applicable when RAW data is available.

---

# 9.2 Demosaicing

Convert the Bayer CFA representation into RGB.

Candidate implementations:

* Bilinear
* Edge-aware
* OpenCV demosaicing
* Custom implementation

The project can later compare classical algorithms.

---

# 9.3 Automatic White Balance

Candidate methods:

### Gray World

Assume the average scene color should be approximately neutral.

### White Patch

Estimate the illuminant from bright image regions.

### Learning-based AWB

Predict RGB gain values using a lightweight neural network.

---

# 9.4 Color Correction Matrix

Apply a 3×3 color correction matrix:

```text
[R']
[G'] = M [R]
[B']     [B]
```

where `M` is learned or calibrated.

---

# 9.5 Gamma Correction

Apply nonlinear intensity transformation:

```text
I_out = I_in^γ
```

The gamma parameter can be adapted according to scene illumination.

---

# 9.6 Tone Mapping

Improve the representation of scenes with large dynamic range.

Candidate methods:

* Global tone mapping
* CLAHE
* Local contrast enhancement
* Highlight compression
* Shadow lifting

---

# 9.7 Denoising

Candidate methods:

* Gaussian
* Median
* Bilateral
* Non-local means
* Fast learned denoising

The project should investigate the trade-off between:

```text
Noise reduction
       ↕
Fine-detail preservation
```

---

# 9.8 Sharpening

A controlled sharpening stage can recover perceived edge detail after denoising.

Example:

```text
I_sharp = I + α(I - Blur(I))
```

The sharpening parameter `α` should be evaluated carefully because excessive sharpening can introduce artifacts.

---

# 10. Adaptive ISP

The main contribution of the project is the adaptive layer.

Instead of:

```text
gamma = 2.2
denoise_strength = fixed
contrast = fixed
```

the system predicts parameters based on the input scene.

Example:

```text
                 Input Image
                      │
                      ▼
              Scene Encoder
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Lighting     Weather     Exposure
       estimate     estimate     estimate
          │           │           │
          └───────────┼───────────┘
                      ▼
                Parameter Head
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
     Gamma        Denoising       Tone Map
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                  Adaptive ISP
```

---

# 11. Two Possible Adaptive Strategies

## Strategy A — Rule-Based Adaptive ISP

Start with interpretable rules.

Example:

```text
IF illumination is low:
    increase shadow exposure
    reduce aggressive sharpening
    increase denoising

IF illumination is high:
    reduce exposure
    compress highlights

IF fog is detected:
    increase local contrast
    adjust tone mapping

IF noise is high:
    increase denoising
```

This provides a strong baseline.

---

## Strategy B — Learning-Based Adaptive ISP

A neural network predicts ISP parameters.

Input:

```text
Camera Image
```

Output:

```text
[
  gamma,
  contrast,
  denoise_strength,
  sharpening_strength,
  tone_mapping_parameter,
  white_balance_gain_R,
  white_balance_gain_B
]
```

The network can initially be small.

For example:

```text
MobileNet / EfficientNet
          ↓
Global Feature Pooling
          ↓
Parameter Regression Head
```

---

# 12. Perception-Aware Optimization

The strongest version of the project will make perception part of the optimization loop.

Instead of optimizing only image quality:

```text
ISP → PSNR / SSIM
```

we investigate:

```text
ISP → Perception
```

For example:

```text
                    RAW / Camera Image
                            │
                            ▼
                       Adaptive ISP
                            │
                            ▼
                       RGB Image
                            │
                            ▼
                      YOLO / Segmentation
                            │
                            ▼
                     Perception Loss
```

A combined objective can be explored:

```text
L = λ1 L_image + λ2 L_perception
```

where:

* `L_image` represents image-quality objectives
* `L_perception` represents downstream perception objectives
* `λ1`, `λ2` control their relative importance

This allows us to investigate whether optimizing an image for human appearance is different from optimizing it for a robot.

---

# 13. Experimental Conditions

The ROS bag dataset will be divided into environmental conditions.

For example:

```text
             Dataset
                │
     ┌──────────┼───────────┐
     ▼          ▼           ▼
    Day       Night       Weather
                            │
                       ┌────┼────┐
                       ▼    ▼    ▼
                     Fog  Rain  Other
```

Additional categories can be introduced depending on what is present in the bags.

---

# 14. Baselines

The project should compare at least four configurations.

### Baseline 1 — Original Camera Output

```text
ROS Bag Image
      ↓
Perception
```

### Baseline 2 — Fixed Classical ISP

```text
ROS Bag Image
      ↓
Fixed ISP
      ↓
Perception
```

### Baseline 3 — Rule-Based Adaptive ISP

```text
ROS Bag Image
      ↓
Scene Estimation
      ↓
Rule-Based ISP
      ↓
Perception
```

### Baseline 4 — Learning-Based Adaptive ISP

```text
ROS Bag Image
      ↓
Scene Network
      ↓
Learned ISP Parameters
      ↓
Adaptive ISP
      ↓
Perception
```

This experimental structure is important because it allows us to determine whether the adaptive component actually provides measurable benefit.

---

# 15. Evaluation Metrics

## Image Quality

Depending on available reference images:

* PSNR
* SSIM
* LPIPS
* Color error ΔE
* Brightness statistics
* Contrast
* Noise level
* Saturation percentage
* Clipped pixel percentage

When no ground-truth image exists, no-reference metrics and carefully defined statistics will be used instead.

---

# 16. Perception Metrics

For object detection:

* Precision
* Recall
* mAP@50
* mAP@50–95

For segmentation:

* mIoU
* Dice/F1
* Pixel accuracy
* Per-class IoU

Robustness can also be measured as:

```text
Performance degradation under condition
=
Performance(condition)
-
Performance(reference condition)
```

The goal is to investigate whether adaptive ISP reduces this degradation.

---

# 17. Computational Metrics

Because the target application is robotics, computational efficiency is important.

Measure:

* Processing latency
* FPS
* CPU utilization
* GPU utilization
* Memory consumption
* End-to-end latency

Example:

```text
ISP latency = 18 ms
Perception latency = 25 ms
Total = 43 ms
```

The system should eventually be tested on hardware relevant to robotic deployment, such as an NVIDIA Jetson platform, if available.

---

# 18. ROS Integration

The final system should operate as a ROS 2 pipeline.

Example:

```text
/camera/image_raw
        │
        ▼
 /camera_isp/input
        │
        ▼
   Camera ISP Node
        │
        ├────────► /camera_isp/image
        │
        ├────────► /camera_isp/debug
        │
        └────────► /camera_isp/parameters
```

The node should support:

```text
ros2 launch camera_isp camera_isp.launch.py
```

Parameters can be configured through YAML.

Example:

```yaml
isp:
  gamma: 2.2
  denoise_strength: 0.4
  contrast: 1.1
  sharpening: 0.2

adaptive:
  enabled: true
```

---

# 19. Project Structure

```text
camera_isp/
│
├── README.md
├── LICENSE
├── requirements.txt
├── CMakeLists.txt
├── package.xml
│
├── config/
│   ├── isp.yaml
│   └── camera.yaml
│
├── launch/
│   └── camera_isp.launch.py
│
├── camera_isp/
│   ├── rosbag_reader.py
│   ├── dataset_builder.py
│   ├── scene_classifier.py
│   ├── metrics.py
│   └── visualization.py
│
├── src/
│   ├── isp_pipeline.cpp
│   ├── demosaic.cpp
│   ├── white_balance.cpp
│   ├── color_correction.cpp
│   ├── tone_mapping.cpp
│   ├── denoising.cpp
│   └── sharpening.cpp
│
├── models/
│   └── scene_classifier/
│
├── scripts/
│   ├── extract_bag.py
│   ├── generate_dataset.py
│   ├── evaluate.py
│   └── benchmark.py
│
├── experiments/
│   ├── baseline/
│   ├── fixed_isp/
│   ├── adaptive_rule/
│   └── adaptive_learning/
│
├── results/
│   ├── image_quality/
│   ├── perception/
│   └── latency/
│
└── docs/
    ├── architecture.md
    └── experiments.md
```

---

# 20. Development Roadmap

## Phase 1 — Understand the Camera Data

Inspect the ROS bags.

Determine:

* Camera model
* Resolution
* Encoding
* FPS
* Available camera_info
* RAW availability
* Exposure information
* Number of environments
* Image compression

Deliverable:

```text
Camera Dataset Report
```

---

## Phase 2 — Build Dataset

Extract frames from ROS bags.

Organize:

```text
dataset/
├── day/
├── low_light/
├── night/
├── fog/
├── rain/
└── challenging/
```

Avoid extracting every frame initially.

Sample frames based on time and scene diversity.

---

## Phase 3 — Classical ISP

Implement:

```text
Input
 ↓
White Balance
 ↓
Color Correction
 ↓
Gamma
 ↓
Tone Mapping
 ↓
Denoising
 ↓
Sharpening
 ↓
Output
```

If RAW is available, add:

```text
Black Level
 ↓
Lens Shading
 ↓
Demosaicing
```

---

## Phase 4 — Establish Baseline

Run the perception model on:

```text
Original
vs
Fixed ISP
```

Record:

```text
mAP
Recall
Precision
Latency
```

---

## Phase 5 — Adaptive Rule-Based ISP

Develop scene-dependent parameter selection.

Example:

```text
Night → denoise + shadow enhancement

Day → highlight preservation

Fog → contrast/tone adjustment
```

Evaluate against the fixed ISP.

---

## Phase 6 — Learning-Based Adaptation

Train a lightweight model to predict ISP parameters.

```text
Image
 ↓
CNN
 ↓
ISP parameter vector
```

Evaluate whether learned adaptation improves over rule-based adaptation.

---

## Phase 7 — Perception-Aware Optimization

Introduce downstream perception into the optimization process.

Investigate:

```text
Image Quality
       vs
Perception Accuracy
```

This is potentially the most research-oriented part of the project.

---

## Phase 8 — Robotics Deployment

Convert the pipeline into a ROS 2 node.

Benchmark:

```text
CPU
GPU
Jetson
```

Measure end-to-end latency.

---

# 21. Expected Final Demonstration

The final demonstration should show the same robot scene processed using different pipelines:

```text
Original
│
├── Fixed ISP
│
├── Rule-Based Adaptive ISP
│
└── Learning-Based Adaptive ISP
```

Then show:

```text
              Image Quality     Detection
Original           X                X

Fixed ISP           X                X

Rule Adaptive       X                X

Learned Adaptive    X                X
```

along with processing latency.

---

# 22. Final Deliverables

The completed project should contain:

### Software

* ROS 2 Camera ISP package
* Python dataset tools
* C++ ISP implementation
* Adaptive parameter module
* Visualization tools
* Evaluation scripts

### Dataset

* Extracted ROS bag frames
* Environmental condition labels
* Train/validation/test splits

### Models

* Scene-condition classifier
* ISP parameter prediction network

### Experiments

* Original vs ISP
* Fixed vs adaptive ISP
* Rule-based vs learning-based ISP
* Image-quality evaluation
* Perception evaluation
* Runtime benchmarking

### Documentation

* Architecture
* Mathematical formulation
* ISP algorithms
* Dataset methodology
* Experimental results
* Limitations
* Deployment considerations

---

# 23. Success Criteria

The project will be considered successful if it demonstrates all three:

### 1. A technically correct ISP pipeline

The individual ISP stages should be implemented and validated.

### 2. Adaptive behavior

The system should modify processing according to environmental conditions rather than applying one fixed configuration.

### 3. Measurable robotics benefit

The experiments should establish, with quantitative evidence, whether adaptive processing changes downstream perception performance.

Importantly, a result showing **no improvement** is still valuable if the experiment is carefully controlled and explains why.

---

# 24. Potential Research Contribution

The central contribution is not:

> "I implemented an image enhancement pipeline."

Instead, the project investigates:

> **"How should camera image processing adapt to environmental conditions when the ultimate objective is reliable robotic perception?"**

This creates a bridge between:

```text
Camera ISP
      ↓
Computer Vision
      ↓
Deep Learning
      ↓
Robotic Perception
      ↓
Real-Time Deployment
```

This also provides opportunities to study the trade-off between:

```text
Human-perceived image quality
              vs
Machine-perceived image quality
              vs
Computational cost
```

---

# 25. Future Extensions

Potential future extensions include:

* RAW-domain neural ISP
* HDR reconstruction
* Learned demosaicing
* Neural denoising
* Exposure control
* End-to-end perception-aware ISP
* Camera-LiDAR-assisted ISP adaptation
* Temporal ISP using consecutive frames
* GPU/CUDA implementation
* TensorRT deployment
* Jetson optimization
* Multi-camera ISP
* ISP adaptation based on robot motion
* Closed-loop ISP optimization using perception confidence

---

# 26. Project Summary

**Project Name:** Adaptive Camera ISP for Robotics

**Input:** ROS/ROS 2 robotic camera bags

**Core Technology:**

```text
Classical ISP
+
Scene Understanding
+
Adaptive Processing
+
Deep Learning
+
Robotic Perception
```

**Primary Research Question:**

> Can adaptive camera image processing improve the robustness of visual perception for robots operating under changing environmental and illumination conditions?

**Primary Output:**

```text
ROS Bag
   ↓
Camera Dataset
   ↓
Adaptive ISP
   ↓
Processed Camera Image
   ↓
Perception
   ↓
Quantitative Evaluation
```

The project ultimately aims to create a **real-time, measurable, robotics-oriented Camera ISP pipeline rather than a collection of independent image-enhancement algorithms.**
