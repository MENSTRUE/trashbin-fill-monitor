# AGENTS.md — TrashBin Fill Monitor

Dokumen ini adalah source of truth untuk AI coding agent yang bekerja pada repository **TrashBin Fill Monitor**.

Agent harus membaca file ini sebelum melakukan perubahan signifikan.

---

## Project Identity

```text
Project  : TrashBin Fill Monitor
Progress : 5%
Domain   : Computer Vision / Smart Waste
Task     : Waste-bin fill-level image classification
```

Public branding:

```text
5% — TrashBin Fill Monitor
```

Jangan gunakan:

```text
Day 5/100
100 Days Challenge
```

Persentase menunjukkan progress belajar, bukan nomor hari.

---

## Problem

Project membantu memprioritaskan pengangkutan tempat sampah berdasarkan kondisi visual.

Current input:

```text
single image
```

Current classes:

```text
empty
half-full
full
```

Operational mapping:

```text
empty → LOW → Belum perlu diangkut
half-full → MEDIUM → Pantau / jadwalkan
full → HIGH → Prioritaskan pengangkutan
```

Project adalah:

```text
decision-support prototype
```

Bukan:

```text
automatic waste collection system
```

---

## Dataset

Dataset:

```text
akirsch1/waste-bin-dataset
```

Source:

```text
Hugging Face
```

Observed data:

```text
Total images : 1621
Simulated    : 1546
Real         : 74
Unmapped     : 1
```

Simulated distribution:

```text
empty       371
half-full   658
full        517
```

Real distribution:

```text
empty        22
half-full    33
full         19
```

---

## CRITICAL: Evaluation Protocol

Real images MUST NOT silently enter training.

Current protocol:

```text
SIMULATED
→ train + validation

REAL
→ external test only
```

Exact split:

```text
train simulated : 1236
val simulated   : 310
real external   : 74
```

Purpose:

```text
evaluate sim-to-real generalization
```

Agent MUST NOT silently:

```text
mix real images into training
random split all domains together
train on external test
tune model using real-test labels
```

If a future experiment changes this protocol, create a **new experiment** and document it separately.

---

## Model

Current model:

```text
MobileNetV3-Small
```

Method:

```text
ImageNet Transfer Learning
```

Input:

```text
192 × 192 RGB
```

Stage 1:

```text
freeze backbone
train classifier
max 5 epochs
```

Stage 2:

```text
unfreeze last 3 backbone blocks
fine-tune
max 5 epochs
```

Class balancing:

```text
WeightedRandomSampler
```

---

## Current Benchmark — Source of Truth

### Simulated Validation

```text
samples           : 310
accuracy          : 83.55%
macro precision   : 83.16%
macro recall      : 83.01%
macro F1          : 83.08%
```

### Real External Test

```text
samples           : 74
accuracy          : 77.03%
macro precision   : 78.04%
macro recall      : 75.86%
macro F1          : 76.33%
```

Domain gap:

```text
≈ 6.76 percentage points Macro-F1
```

Reports in `reports/` are the source of truth.

---

## Real-Test Per-Class Metrics

```text
EMPTY
Precision : 83.33%
Recall    : 90.91%
F1        : 86.96%

HALF-FULL
Precision : 72.22%
Recall    : 78.79%
F1        : 75.36%

FULL
Precision : 78.57%
Recall    : 57.89%
F1        : 66.67%
```

Primary failure mode:

```text
FULL → HALF-FULL
```

Do not hide this limitation.

---

## Confidence Interpretation

NEVER claim:

```text
92% confidence = trash bin is 92% full
```

Correct interpretation:

```text
92% confidence = model assigns 92% probability to the predicted class
```

Current model performs:

```text
classification
```

Not:

```text
physical volume estimation
```

---

## Model Checkpoint Policy

Model binaries are intentionally not published.

Ignore:

```text
*.pth
*.pt
*.onnx
```

Local inference model:

```text
models/trashbin_fill_monitor_mobilenetv3.pth
```

Agent MUST NOT:

```text
force-add checkpoint
remove checkpoint ignore rule
commit model binaries
upload model to GitHub
```

unless user explicitly requests it.

---

## Repository Structure

```text
trashbin-fill-monitor/
├── app.py
├── README.md
├── AGENTS.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── assets/
├── data/
├── models/
├── notebooks/
├── reports/
└── src/
```

---

## Streamlit App

Expected flow:

```text
Upload Image
↓
Preprocess
↓
MobileNetV3
↓
Probabilities
↓
Prediction
↓
Priority
↓
Recommended Action
```

Do NOT claim:

```text
real-time municipal deployment
physical fill percentage
IoT connectivity
automatic dispatch
production readiness
```

---

## Human Verification Rule

Always preserve:

```text
Model predicts
System prioritizes
Human verifies
Human decides
```

Preferred wording:

> AI membantu menentukan prioritas. Manusia tetap memegang keputusan akhir.

---

## Reports

Important files:

```text
reports/
├── classification_report_real_external_test.csv
├── classification_report_simulated_validation.csv
├── domain_gap_summary.csv
├── final_summary.json
├── real_external_test.csv
├── real_predictions.csv
├── train_split.csv
├── training_history.csv
└── val_split.csv
```

When metrics are needed, read reports instead of guessing from README or memory.

---

## Assets

```text
assets/
├── cm_real_external_test.png
├── cm_simulated_validation.png
└── real_prediction_examples.png
```

---

## Python Style

Target:

```text
Python 3.11
```

Rules:

```text
prefer pathlib.Path
keep functions small
use clear naming
type hints encouraged
CPU inference must work
GPU optional
avoid unnecessary dependencies
never hard-code user-specific absolute Windows paths in public code
```

---

## Dependencies

Keep dependencies minimal.

Core:

```text
streamlit
torch
torchvision
pillow
pandas
numpy
```

Do not introduce new frameworks unless they add clear value.

---

## Development Priorities

Order:

```text
1. correctness
2. evaluation integrity
3. real-domain robustness
4. operational usefulness
5. simplicity
6. UI polish
```

Do not add complex models merely because they are more advanced.

---

## Public Result Reporting

Never report only:

```text
83.08% F1
```

without context.

Preferred:

```text
Simulated Validation Macro-F1 : 83.08%
Real External Test Macro-F1   : 76.33%
```

The domain gap is part of the project story.

---

## Do Not Overclaim

Forbidden unless future evidence exists:

```text
production-ready
works for all bins
accurate physical fill percentage
real smart-city deployment
proven cost savings
real IoT monitoring
municipal system
```

Allowed:

```text
prototype
MVP
benchmark
decision-support
sim-to-real experiment
external real-image test
```

---

## Roadmap

Preferred future order:

```text
more real data
↓
clearer labels
↓
bin detection
↓
segmentation / fill estimation
↓
confidence calibration
↓
cost-sensitive evaluation
↓
temporal monitoring
↓
multi-bin dashboard
↓
IoT integration
↓
route optimization
↓
field validation
```

---

## Re-Training Rules

Before retraining:

```text
define experiment objective
preserve baseline
use reproducible seed
keep real test isolated
compare with current benchmark
save reports
document changes
```

Never overwrite baseline metrics silently.

---

## Definition of Done — Current MVP

```text
[x] dataset audited
[x] model trained
[x] simulated validation
[x] real external evaluation
[x] error analysis
[x] local inference
[x] Streamlit app
[x] reports
[x] documentation
```

Publishing model binaries is **not required**.

---

## Core Principle

> **AI membantu menentukan prioritas. Manusia tetap memegang keputusan akhir.**
