# 🗑️ TrashBin Fill Monitor

**5% — AI/ML Portfolio Progress**

TrashBin Fill Monitor adalah prototype **Computer Vision** untuk mengklasifikasikan tingkat kepenuhan tempat sampah dari sebuah foto dan menerjemahkan hasil prediksi menjadi **prioritas pengangkutan**.

Project ini dikembangkan sebagai **decision-support system**, bukan sistem otomatis yang menggantikan keputusan petugas.

> **AI membantu menentukan prioritas. Manusia tetap memegang keputusan akhir.**

---

## 📌 Latar Belakang

Pengangkutan sampah sering dilakukan menggunakan jadwal tetap.

Masalahnya, jadwal tetap belum tentu sesuai dengan kondisi aktual:

- tempat sampah yang masih kosong dapat tetap didatangi petugas;
- tempat sampah dapat penuh sebelum jadwal pengangkutan berikutnya;
- petugas belum memiliki prioritas berdasarkan kondisi aktual;
- waktu dan sumber daya operasional dapat digunakan secara kurang efisien.

TrashBin Fill Monitor mengeksplorasi penggunaan Computer Vision untuk mengubah foto tempat sampah menjadi informasi yang lebih mudah ditindaklanjuti.

```text
Foto Tempat Sampah
        ↓
Computer Vision
        ↓
Empty / Half-full / Full
        ↓
Operational Priority
        ↓
Rekomendasi Pengangkutan
```

---

# 🎯 Tujuan Project

Project ini bertujuan untuk:

1. mengklasifikasikan kondisi tempat sampah dari gambar;
2. mengenali tiga level: `empty`, `half-full`, dan `full`;
3. membandingkan performa model pada simulated images dan real images;
4. mempelajari sim-to-real domain shift;
5. menerjemahkan output ML menjadi prioritas operasional;
6. membangun prototype Streamlit yang dapat diuji melalui upload gambar;
7. mendokumentasikan limitation sebelum sistem digunakan pada kondisi nyata.

---

# 🧩 Scope MVP

Input:

```text
1 foto tempat sampah
```

Output:

```text
Predicted class
Confidence
Priority
Recommended action
```

Mapping operasional:

| Fill Level | Priority | Action |
|---|---|---|
| Empty | LOW | Belum perlu diangkut |
| Half-full | MEDIUM | Pantau / jadwalkan |
| Full | HIGH | Prioritaskan pengangkutan |

### Penting

Project ini **tidak menghitung persentase volume fisik sampah**.

Jika output:

```text
Prediction : Half-full
Confidence : 92.9%
```

artinya model 92.9% yakin gambar termasuk class `half-full`, **bukan** tempat sampah terisi 92.9%.

---

# 📦 Dataset

Dataset utama:

**akirsch1/waste-bin-dataset**

Sumber:

```text
https://huggingface.co/datasets/akirsch1/waste-bin-dataset
```

Hasil audit dataset:

```text
Total image files : 1,621
Simulated images  : 1,546
Real images       : 74
Unmapped image    : 1
```

Distribusi simulated data:

| Class | Images |
|---|---:|
| Empty | 371 |
| Half-full | 658 |
| Full | 517 |

Distribusi real data:

| Class | Images |
|---|---:|
| Empty | 22 |
| Half-full | 33 |
| Full | 19 |

Satu image yang tidak dipakai merupakan image dokumentasi/contoh dataset dan tidak memiliki label class yang relevan.

---

# 🔬 Experimental Design

Salah satu keputusan paling penting dalam project ini adalah:

> **Real images tidak digunakan untuk training.**

Pipeline:

```text
Simulated Images
        ↓
Train / Validation

Real Images
        ↓
External Test Only
```

Split yang digunakan:

```text
Train simulated : 1,236
Val simulated   :   310
Real external   :    74
```

Tujuan strategi ini adalah menjawab pertanyaan:

> Apakah model yang belajar dari simulated images masih mampu bekerja ketika diberikan gambar dunia nyata?

Jika real images dicampurkan ke training, pertanyaan tersebut akan lebih sulit dijawab secara jujur.

---

# 🧠 Model

Model utama:

```text
MobileNetV3-Small
```

Pendekatan:

```text
ImageNet Transfer Learning
```

MobileNetV3-Small dipilih karena:

- relatif ringan;
- cocok untuk image classification;
- dapat digunakan pada CPU;
- lebih realistis untuk kemungkinan edge/mobile deployment;
- memiliki pretrained ImageNet weights;
- kompleksitasnya sesuai kebutuhan MVP.

Input:

```text
192 × 192 RGB image
```

---

# 🏋️ Training Strategy

Training dilakukan dalam dua tahap.

## Stage 1 — Classifier Training

Backbone MobileNetV3 dibekukan.

```text
Pretrained MobileNetV3
        ↓
Frozen Backbone
        ↓
Train Classifier Head
```

Maksimal 5 epoch.

Best validation Macro-F1:

```text
≈ 79.65%
```

## Stage 2 — Partial Fine-Tuning

Tiga blok terakhir backbone dibuka.

```text
Last Backbone Blocks
        +
Classifier
        ↓
Fine-Tuning
```

Maksimal 5 epoch.

Final validation Macro-F1:

```text
83.08%
```

---

# 🖼️ Image Preprocessing

Training pipeline:

```text
Resize 192 × 192
Random Horizontal Flip
Random Rotation
Color Jitter
Tensor Conversion
ImageNet Normalization
```

Validation dan real external test:

```text
Resize 192 × 192
Tensor Conversion
ImageNet Normalization
```

Augmentasi tidak digunakan pada evaluation data.

---

# ⚖️ Class Imbalance Handling

Distribusi simulated dataset tidak sepenuhnya seimbang.

Training menggunakan:

```text
WeightedRandomSampler
```

Tujuannya agar class dengan jumlah image lebih sedikit tetap mendapatkan representasi yang memadai selama training.

Validation dan external test **tidak di-resample**.

---

# 📊 Hasil Evaluasi

## Simulated Validation

Jumlah: **310 images**

| Metric | Score |
|---|---:|
| Accuracy | **83.55%** |
| Macro Precision | **83.16%** |
| Macro Recall | **83.01%** |
| Macro F1 | **83.08%** |

Per-class:

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| Empty | 76.71% | 75.68% | 76.19% |
| Half-full | 80.45% | 81.06% | 80.75% |
| Full | 92.31% | 92.31% | 92.31% |

## Real External Test

Jumlah: **74 images**

| Metric | Score |
|---|---:|
| Accuracy | **77.03%** |
| Macro Precision | **78.04%** |
| Macro Recall | **75.86%** |
| Macro F1 | **76.33%** |

Per-class:

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| Empty | 83.33% | 90.91% | 86.96% |
| Half-full | 72.22% | 78.79% | 75.36% |
| Full | 78.57% | 57.89% | 66.67% |

---

# 🌍 Sim-to-Real Domain Gap

```text
Simulated Validation Macro-F1 : 83.08%
Real External Test Macro-F1   : 76.33%
Gap                           : ≈ 6.76 percentage points
```

Penurunan performa ini menunjukkan bahwa simulated data belum sepenuhnya mewakili distribusi gambar dunia nyata.

---

# 🔎 Error Analysis

Confusion matrix real external test:

```text
                 Predicted
True          Empty  Half-full  Full
Empty           20       2       0
Half-full        4      26       3
Full             0       8      11
```

Failure mode paling penting:

```text
FULL → HALF-FULL
```

Recall class `full` hanya **57.89%**. Secara operasional, error ini penting karena dapat menyebabkan bin penuh tidak mendapatkan prioritas tertinggi.

---

# 🖥️ Streamlit Prototype

Aplikasi utama: `app.py`

```text
Upload Image
        ↓
Preprocessing
        ↓
MobileNetV3
        ↓
Class Probabilities
        ↓
Predicted Fill Level
        ↓
Priority Mapping
        ↓
Recommended Action
```

Aplikasi menampilkan uploaded image, predicted class, confidence, probability distribution, operational priority, rekomendasi tindakan, benchmark context, dan limitation.

---

# 👤 Human-in-the-Loop

```text
AI Predicts
        ↓
System Prioritizes
        ↓
Human Verifies
        ↓
Operational Decision
```

Project adalah **decision-support system**, bukan sistem keputusan otomatis.

---

# 📁 Struktur Repository

```text
trashbin-fill-monitor/
├── app.py
├── README.md
├── AGENTS.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── assets/
│   ├── cm_real_external_test.png
│   ├── cm_simulated_validation.png
│   └── real_prediction_examples.png
├── data/
├── models/
│   └── checkpoint tidak dipublikasikan
├── notebooks/
├── reports/
│   ├── classification_report_real_external_test.csv
│   ├── classification_report_simulated_validation.csv
│   ├── domain_gap_summary.csv
│   ├── final_summary.json
│   ├── real_external_test.csv
│   ├── real_predictions.csv
│   ├── train_split.csv
│   ├── training_history.csv
│   └── val_split.csv
└── src/
    ├── __init__.py
    ├── config.py
    ├── dataset.py
    ├── model.py
    ├── predict.py
    └── utils.py
```

---

# 🔐 Model Checkpoint Policy

Model checkpoint **tidak dipublikasikan di GitHub**.

File lokal:

```text
models/trashbin_fill_monitor_mobilenetv3.pth
```

Repository publik berfokus pada training pipeline, evaluation, inference code, reports, documentation, dan reproducibility.

`.gitignore` tetap harus mengabaikan:

```gitignore
*.pth
*.pt
*.onnx
```

---

# ▶️ Menjalankan Aplikasi

```bash
git clone https://github.com/MENSTRUE/trashbin-fill-monitor.git
cd trashbin-fill-monitor
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Checkpoint hasil training harus tersedia di:

```text
models/trashbin_fill_monitor_mobilenetv3.pth
```

Run:

```bash
streamlit run app.py
```

---

# ♻️ Reproduksi Dataset

```bash
hf download akirsch1/waste-bin-dataset \
  --repo-type dataset \
  --local-dir ./dataset/waste-bin-dataset
```

Pipeline:

```text
Dataset Audit
↓
Domain Separation
↓
Simulated Train / Validation Split
↓
Augmentation
↓
Weighted Sampling
↓
MobileNetV3 Transfer Learning
↓
Partial Fine-Tuning
↓
Simulated Validation
↓
Real External Test
↓
Error Analysis
↓
Model Export
```

---

# ⚠️ Limitations

1. Mayoritas training data merupakan simulated images.
2. Real external test hanya terdiri dari 74 images.
3. Model merupakan image classifier dan belum mendeteksi lokasi bin.
4. Out-of-distribution image tetap akan dipaksa masuk salah satu class.
5. Softmax confidence belum dikalibrasi.
6. Model tidak mengukur volume fisik.
7. Belum terdapat temporal monitoring.
8. Belum terhubung ke kamera atau IoT.
9. Belum dilakukan field validation.
10. Project belum production-ready.

---

# 🛣️ Roadmap

## Phase 1 — Larger Real Dataset
Kumpulkan lebih banyak real images dengan variasi bin, angle, lighting, indoor/outdoor, occlusion, dan kualitas kamera.

## Phase 2 — Better Label Definition
Definisikan threshold `empty / half-full / full` berdasarkan kebutuhan operasional.

## Phase 3 — Trash Bin Detection

```text
Image → Bin Detector → Crop → Fill Classifier
```

## Phase 4 — Segmentation

```text
Bin Segmentation + Trash Segmentation → Occupied Area Ratio
```

## Phase 5 — Probability Calibration
Uji calibration curve, ECE, dan temperature scaling.

## Phase 6 — Cost-Sensitive Evaluation
Berikan cost lebih besar pada `FULL → HALF-FULL`.

## Phase 7 — Temporal Monitoring

```text
Timestamped Images → Fill History → Growth Rate → Estimated Urgency
```

## Phase 8 — Multi-Bin Dashboard
Ranking banyak bin berdasarkan priority dan history.

## Phase 9 — IoT / Camera Integration

```text
Camera / Edge Device
↓
Inference Service
↓
Database
↓
Priority Engine
↓
Operations Dashboard
↓
Human Verification
```

## Phase 10 — Route Optimization
Gabungkan priority, lokasi, kapasitas kendaraan, dan jaringan jalan.

## Phase 11 — Field Pilot

```text
Offline Benchmark
↓
Shadow Deployment
↓
Operator Feedback
↓
Threshold Adjustment
↓
Limited Pilot
↓
Operational Evaluation
```

---

# 📚 Pembelajaran Utama

- dataset split adalah bagian dari desain eksperimen;
- validation score tidak sama dengan real-world performance;
- domain shift harus dilaporkan, bukan disembunyikan;
- error memiliki dampak operasional yang berbeda;
- model ringan dapat cukup untuk MVP;
- output ML harus diterjemahkan menjadi informasi yang dapat ditindaklanjuti.

---

# ✅ Status Project

| Komponen | Status |
|---|---|
| Dataset audit | ✅ |
| Simulated / real separation | ✅ |
| MobileNetV3 training | ✅ |
| Fine-tuning | ✅ |
| Simulated validation | ✅ |
| Real external test | ✅ |
| Error analysis | ✅ |
| Local inference | ✅ |
| Streamlit prototype | ✅ |
| Priority mapping | ✅ |
| Documentation | ✅ |
| Larger real dataset | ⏳ |
| Calibration | ⏳ |
| Detection / segmentation | ⏳ |
| IoT integration | ⏳ |
| Field validation | ⏳ |

---

# 🧾 Kesimpulan

TrashBin Fill Monitor adalah **Computer Vision MVP untuk fill-level classification dan collection prioritization**.

Tiga aspek utama yang sudah berhasil dibangun:

```text
1. Training & evaluation pipeline
2. Sim-to-real benchmark
3. Operational Streamlit prototype
```

Hasil utama:

```text
Simulated Validation Macro-F1 : 83.08%
Real External Test Macro-F1   : 76.33%
```

Project belum production-ready. Fokus pengembangan berikutnya adalah larger real dataset, better labels, detection, segmentation, calibration, temporal monitoring, dan field validation.

---

## Author

**Wafa Bila Syaefurokhman**  
GitHub: **MENSTRUE**

---

> **AI membantu menentukan prioritas. Manusia tetap memegang keputusan akhir.**
