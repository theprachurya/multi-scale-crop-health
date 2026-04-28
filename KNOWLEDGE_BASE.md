# 🌾 Multi-Scale Crop Health Classification — Complete Knowledge Base

> **Project Codename:** MultiScaleCropNet  
> **Domain:** Precision Agriculture · Deep Learning · Multi-Modal Sensor Fusion  
> **Institution:** SRM Institute of Science and Technology, Chennai, India  
> **Authors:** Prachurya Subhasmita, Mohammad Sufyan · **Advisor:** Dr. E. Poongothai  
> **Status:** Research-grade implementation with trained models and IEEE-format paper  

---

## 1. Project Overview

### 1.1 What This Project Is

This is a **research-grade deep learning system** that performs three-class crop health classification (Healthy / Stressed / Diseased) by simultaneously fusing imagery from three distinct spatial scales:

| Scale | Source Dataset | Modality | Resolution |
|-------|---------------|----------|------------|
| **Micro** | PlantVillage (~54,000 images) | Close-up leaf photographs | Sub-millimetre focal |
| **Meso** | MH-SoyaHealthVision (~2,840 images) | UAV/aerial soybean imagery | Centimetre-scale |
| **Macro** | EuroSAT (~27,000 images) | Sentinel-2 satellite tiles | 10–60 m per pixel |

### 1.2 Central Hypothesis

> *A deep learning model that jointly fuses features from leaf, UAV, and satellite imagery significantly outperforms any single-modality baseline for three-class crop health classification.*

This hypothesis is validated through a **complete seven-configuration ablation study**, where every single and dual modality combination is compared against the full three-modality fusion.

### 1.3 Key Results

| Configuration | Accuracy | F1-Macro |
|---------------|----------|----------|
| Satellite Only | 0.8968 | 0.8958 |
| UAV Only | 0.9739 | 0.9738 |
| Leaf Only | 0.9552 | 0.9550 |
| Satellite + UAV | 0.9876 | 0.9876 |
| UAV + Leaf | 0.9876 | 0.9876 |
| Satellite + Leaf | 0.9888 | 0.9888 |
| **Full Fusion** | **0.9925** | **0.9925** |

The latest Colab T4 full-fusion run achieves **99.25% accuracy** and **F1-macro of 0.9925** on a balanced test set of 804 samples (268 per class), outperforming every reduced configuration.

---

## 2. Three-Class Biological Taxonomy

All three heterogeneous datasets are unified under a single biologically grounded taxonomy:

### Class 0 — Healthy
- **Definition:** No visible damage. Normal pigmentation, leaf architecture, and canopy density.
- **PlantVillage mapping:** Any folder containing `___healthy`
- **MH-SoyaHealthVision mapping:** `Healthy_Soyabean`
- **EuroSATallBands mapping (prior):** `AnnualCrop`, `PermanentCrop` — agricultural healthy priors

### Class 1 — Stressed (Reversible)
- **Definition:** Externally caused, surface-level, or mechanical damage. Reversible with intervention. Includes pest feeding, drought scorch, manageable surface fungi.
- **PlantVillage mapping:** Cedar Apple Rust, Powdery Mildew, Common Rust, Isariopsis Leaf Blight, Leaf Mold, Spider Mites, Leaf Scorch
- **MH-SoyaHealthVision mapping:** Soyabean Rust, Semilooper Pest Attack, Caterpillar Pest Attack
- **EuroSATallBands mapping (prior):** `HerbaceousVegetation` (and `HerbaceousVegatation` variant), `Pasture` — stressed priors

### Class 2 — Diseased (Irreversible)
- **Definition:** Systemic pathogen infection (viral, bacterial, or invasive fungal) affecting vascular tissue. Irreversible, requires immediate intervention or crop destruction.
- **PlantVillage mapping:** Bacterial Spot, Early/Late Blight, Black Rot, Apple Scab, Esca, Septoria, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Huanglongbing
- **MH-SoyaHealthVision mapping:** Soyabean Mosaic (Soybean Mosaic Virus — systemic, spreads through phloem)
- **EuroSATallBands final labeling:** NDVI percentile partition on mapped TIFF tiles (lower 33% Diseased, middle 34% Stressed, upper 33% Healthy)

---

## 3. System Architecture

### 3.1 High-Level Architecture Diagram

```
Input Triplet: (Leaf Image, UAV Image, Satellite Image)
                 │                │                │
                 ▼                ▼                ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
         │ EfficientNet  │ │   ResNet50   │ │   ResNet50   │
         │     B0        │ │  (instance 1)│ │  (instance 2)│
         │  (frozen)     │ │  (frozen)    │ │  (frozen)    │
         └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                │                │                │
           GAP ─┤           GAP ─┤           GAP ─┤
                │                │                │
         [1280-dim]       [2048-dim]       [2048-dim]
                │                │                │
                └────────┬───────┘────────────────┘
                         │
                 ┌───────▼────────┐
                 │ Concatenation  │
                 │  Fusion Layer  │
                 │  (5376-dim)    │
                 └───────┬────────┘
                         │
                 ┌───────▼────────┐
                 │ Classification │
                 │     Head       │
                 │ 5376→1024→256→3│
                 └───────┬────────┘
                         │
                    [3 Classes]
              Healthy / Stressed / Diseased
```

### 3.2 Backbone Encoders

#### Leaf Branch — EfficientNet-B0
- **File:** `models/backbones.py` → `EfficientNetB0Backbone`
- **Pre-trained on:** ImageNet-1K
- **Output dimension:** 1,280 (after Global Average Pooling)
- **Parameters:** 5.3M total
- **Freezing strategy:** `features.0` through `features.6` frozen; `features.7` and `features.8` trainable
- **Rationale:** Compound scaling achieves strong accuracy suited to high inter-class texture variability of leaf disease imagery

#### UAV Branch — ResNet50 (Instance 1)
- **File:** `models/backbones.py` → `ResNet50Backbone`
- **Pre-trained on:** ImageNet-1K
- **Output dimension:** 2,048 (after Global Average Pooling)
- **Parameters:** 25.6M total
- **Freezing strategy:** All layers frozen except `layer4`
- **Rationale:** Deep residual structure is effective for coarser spatial patterns in aerial crop imagery

#### Satellite Branch — ResNet50 (Instance 2)
- **Same architecture** as UAV branch but **separate weight instance** (no weight sharing)
- **Rationale:** Reflects the similar geometric character of aerial and satellite imagery relative to close-up leaf photography

### 3.3 Fusion Module
- **File:** `models/fusion_module.py`
- **Primary method:** `ConcatFusion` — parameter-free concatenation ensuring no modality's information is discarded
- **Output dimension:** 1280 + 2048 + 2048 = **5,376**
- **Additional implemented options:**
  - `AttentionFusion` — shared-space cross-modal self-attention
  - `LearnedGatingFusion` — sample-wise modality gates
  - `ScalarWeightedFusion` — learnable global scalar modality weights with projection to shared embedding

### 3.4 Classification Head
- **File:** `models/classifier.py` → `ClassificationHead`
- **Architecture:**
  ```
  FC(5376 → 1024) → BatchNorm1d → ReLU → Dropout(0.5)
  FC(1024 → 256)  → BatchNorm1d → ReLU → Dropout(0.3)
  FC(256 → 3)     → [Softmax applied externally via loss function]
  ```
- **Weight initialization:** Kaiming He (fan_in, nonlinearity=relu)
- **BatchNorm parameters:** weight=1, bias=0

### 3.5 Master Model
- **File:** `models/multiscale_net.py` → `MultiScaleCropNet`
- **Constructor parameters:**
  - `active_modalities`: list from `['leaf', 'uav', 'satellite']` — enables ablation by selectively activating branches
  - `freeze_backbones`: bool (default `True`)
  - `dropout_rate`: float (default `0.5`)
  - `num_classes`: int (default `3`)
  - `fusion_method`: `'concat'`, `'attention'`, `'learned_gating'`, or `'scalar_weighted'`
- **Forward pass:** Supports `return_aux=True` for optional modality-specific auxiliary logits (leaf and UAV) used in consistency regularization

---

## 4. Data Pipeline

### 4.1 Dataset Extraction
- **File:** `scripts/extract_datasets.py`
- **Input:** Three zip files placed in project root:
  - `plantvillage.zip` → extracted to `data/raw/leaf/`
  - `mhsoyahealthvision.zip` → nested zips are detected and extracted; only `Soyabean_UAV-Based_Image_Dataset` folder is used → `data/raw/uav/`
  - `eurosat.zip` → extracted to `data/raw/satellite/`

### 4.2 Sentinel-2 Multispectral Handling
- **Files:** `preprocessing/align_datasets.py`, `data/dataset.py`
- **Process:** EuroSATallBands TIFF files are retained for preprocessing and loaded with `tifffile`.
  - NDVI is computed from B08/B04 during alignment for class partitioning.
  - RGB for model input is generated on-the-fly from B04/B03/B02 in the dataloader.

### 4.3 Biological Alignment & Triplet Generation
- **File:** `preprocessing/align_datasets.py`
- **Key functions:**
  - `get_modality_dict(raw_dir, modality)` — scans raw directories and classifies images into Healthy/Stressed/Diseased using biological keyword rules
  - NDVI partitioning over mapped satellite TIFF tiles:
    - NDVI = (B08 - B04) / (B08 + B04 + eps)
    - Lower 33% NDVI -> Diseased
    - Middle 34% NDVI -> Stressed
    - Upper 33% NDVI -> Healthy
  - `generate_triplets(base_dir)` — main pipeline entry point

### 4.4 Data Splitting Strategy — Zero Leakage
1. For each class `c` and modality `m`, the raw image pool is randomly permuted and split **70/15/15** into disjoint train/val/test pools
2. Triplets are formed by sampling **independently with replacement** from corresponding split pools — guaranteeing no cross-split leakage
3. Class balance is enforced: `max(⌊N_min × ratio⌋, floor)` triplets per class, with floors of 1,000 (train), 200 (val), 200 (test)

### 4.5 Final Dataset Sizes
| Split | Total Triplets | Per Class |
|-------|---------------|-----------|
| Train | 3,759 | 1,253 |
| Validation | 804 | 268 |
| Test | 804 | 268 |

### 4.6 Output Files
- `data/triplets/train_triplets.csv` — columns: `leaf_path`, `uav_path`, `satellite_path`, `label`
- `data/triplets/val_triplets.csv`
- `data/triplets/test_triplets.csv`

---

## 5. Data Loading & Augmentation

### 5.1 Dataset Classes
- **File:** `data/dataset.py`
- **`CropTripletDataset`**: Loads (leaf, uav, satellite, label) triplets from CSV. Supports separate transforms per modality. Handles TIF-to-RGB conversion on-the-fly via `tifffile` if needed. Falls back to dummy green images if paths don't exist.
- **`SingleModalityDataset`**: Used for single-modality ablation baselines. Returns (image, label) pairs.

### 5.2 Augmentation Pipeline
- **File:** `preprocessing/transforms.py`

**Training augmentations (aggressive, anti-overfitting):**
```python
Resize(256×256) → RandomCrop(224) → RandomHorizontalFlip(0.5) → RandomVerticalFlip(0.3)
→ RandomRotation(±15°) → ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1)
→ RandomGrayscale(0.05) → ToTensor → Normalize(ImageNet μ,σ)
```

**Validation/Test (deterministic):**
```python
Resize(224×224) → ToTensor → Normalize(ImageNet μ,σ)
```

**ImageNet normalization:** `mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`

---

## 6. Training Infrastructure

### 6.1 Loss Function
- **File:** `training/loss_functions.py`
- **Cross-Entropy with Label Smoothing** (ε = 0.1):
  ```
  L = -(1 - ε) × log(p_y) - (ε/K) × Σ log(p_k)   where K=3
  ```
- Label smoothing prevents overconfident predictions on proxy-generated satellite diseased images
- Optional cross-scale consistency loss in trainer:
  - `L_total = L_ce + lambda * L_cons`
  - `L_cons` is KL divergence between leaf and UAV auxiliary logits with temperature scaling
  - Defaults: `consistency_lambda=0.2`, `consistency_temperature=2.0`
- Supports optional class weights (not used by default since dataset is balanced)

### 6.2 Optimizer
- **File:** `training/optimizers.py`
- **AdamW** with decoupled weight decay regularization
- **Differential learning rates:**
  - Backbone parameters (unfrozen layers): `lr = 1e-4`
  - Head + Fusion parameters: `lr = 1e-3`
- **Weight decay:** `1e-4` (L2 regularization)
- **Scheduler:** `CosineAnnealingLR` with `T_max = epochs`, `eta_min = 1e-6`

### 6.3 Training Loop
- **File:** `training/trainer.py` → `Trainer`
- **Features:**
  - Per-epoch train/validate cycle with tqdm progress bars
  - Gradient clipping: `clip_grad_norm_(max_norm=1.0)`
  - CSV logging of per-epoch metrics
  - Best-model checkpointing (lowest validation loss)
  - **Early stopping** with patience=10 (monitors validation loss)
  - **Overfitting detection:** Warns if train/val accuracy gap exceeds 15%, critical alert at 20%
  - Modality-aware batch unpacking via `_unpack_batch()`

### 6.4 Anti-Overfitting Measures (Complete List)
1. **Backbone freezing** — protects ImageNet pre-trained weights
2. **Aggressive data augmentation** — random crop, flip, rotation, color jitter, grayscale
3. **Label smoothing** (ε=0.1) — prevents overconfident predictions
4. **Dropout** — p=0.5 (first FC layer), p=0.3 (second FC layer)
5. **BatchNorm** — before each activation
6. **Weight decay** (L2 regularization) — 1e-4 via AdamW
7. **Gradient clipping** — max L2 norm of 1.0
8. **Early stopping** — patience=10 on validation loss
9. **Train/Val gap monitoring** — warns on >15% accuracy divergence
10. **CosineAnnealingLR scheduler** — prevents learning rate plateaus

---

## 7. Evaluation & Ablation Study

### 7.1 Metrics
- **File:** `evaluation/metrics.py`
- Computed metrics:
  - **Accuracy** (overall)
  - **Precision** (macro-averaged + per-class)
  - **Recall** (macro-averaged + per-class)
  - **F1-Score** (macro-averaged + per-class)
  - **Full classification report** (sklearn format)
- Macro averaging weights each class equally, appropriate for assessing robustness

### 7.2 Confusion Matrix
- **File:** `evaluation/confusion_matrix.py`
- Generates normalized confusion matrices with both raw counts and percentages
- Saved as PNG (300 DPI) using seaborn heatmaps

### 7.3 Ablation Runner
- **File:** `evaluation/ablation_runner.py` → `AblationRunner`
- Runs **all 7 experiments** sequentially:
  1. `satellite_only` — Satellite branch only (ResNet50)
  2. `uav_only` — UAV branch only (ResNet50)
  3. `leaf_only` — Leaf branch only (EfficientNet-B0)
  4. `sat_uav` — Satellite + UAV (two ResNet50 branches)
  5. `uav_leaf` — UAV + Leaf
  6. `sat_leaf` — Satellite + Leaf
  7. `full_fusion` — All three branches
- Compiles results into `ablation_results.csv` and generates a bar chart comparison PNG

### 7.4 Per-Class Full Fusion Results

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Healthy | 1.0000 | 1.0000 | 1.0000 | 268 |
| Stressed | 0.9925 | 0.9851 | 0.9888 | 268 |
| Diseased | 0.9852 | 0.9925 | 0.9888 | 268 |
| **Macro Avg** | **0.9926** | **0.9925** | **0.9925** | **804** |

---

## 8. Experiment Configuration System

### 8.1 Default Configuration
- **File:** `configs/default_config.yaml`
- All experiments inherit these defaults:

| Parameter | Value |
|-----------|-------|
| `epochs` | 12 |
| `batch_size` | 8 |
| `backbone_lr` | 0.0001 |
| `head_lr` | 0.001 |
| `weight_decay` | 0.0001 |
| `early_stopping_patience` | 10 |
| `gradient_clip_norm` | 1.0 |
| `dropout_rate` | 0.5 |
| `label_smoothing` | 0.1 |
| `seed` | 42 |
| `freeze_backbones` | true |
| `fusion_method` | concat |
| `consistency_lambda` | 0.2 |
| `consistency_temperature` | 2.0 |
| `num_workers` | 0 |

### 8.2 Experiment-Specific Configs
Each experiment overrides only `active_modalities` and `experiment_name`:

| Config File | Active Modalities |
|-------------|------------------|
| `configs/exp_satellite_only.yaml` | `[satellite]` |
| `configs/exp_uav_only.yaml` | `[uav]` |
| `configs/exp_leaf_only.yaml` | `[leaf]` |
| `configs/exp_sat_uav.yaml` | `[satellite, uav]` |
| `configs/exp_uav_leaf.yaml` | `[uav, leaf]` |
| `configs/exp_sat_leaf.yaml` | `[satellite, leaf]` |
| `configs/exp_full_fusion.yaml` | `[leaf, uav, satellite]` |
| `configs/exp_full_fusion_weighted.yaml` | `[leaf, uav, satellite]` + `fusion_method=scalar_weighted` |

### 8.3 Experiment Runner
- **File:** `experiments/run_experiment.py`
- Unified entry point: `python experiments/run_experiment.py --config configs/exp_full_fusion.yaml`
- Also supports `--ablation` flag to run all 7 experiments via `AblationRunner`
- Sets random seed (default 42) for full reproducibility
- Supports multi-seed execution via `--seeds` (e.g., `42,123,999`) and writes aggregate mean/std summary JSON
- Loads best checkpoint after training and evaluates on test set
- Exports: JSON metrics, confusion matrix PNG, training curves PNG, CSV epoch logs

---

## 9. Utility Modules

### 9.1 Logger
- **File:** `utils/logger.py`
- `setup_logger()` — creates dual-output logger (console + timestamped log file)
- `CSVLogger` — appends per-epoch metrics to CSV (epoch, train_loss, val_loss, train_acc, val_acc, val_f1)

### 9.2 IO Utilities
- **File:** `utils/io_utils.py`
- `save_checkpoint()` — saves model state dict, optimizer state, epoch, best_val_loss; also saves `best_*.pth` when `is_best=True`
- `load_checkpoint()` — restores model and optional optimizer states
- `save_json()` / `load_json()` — dictionary serialization

### 9.3 Visualizer
- **File:** `utils/visualizer.py`
- `plot_training_curves()` — dual subplot (Loss + Accuracy) with optional early stopping vertical line marker
- `generate_gradcam()` — placeholder for Grad-CAM visualization (future work)

### 9.4 Early Stopping
- **File:** `utils/early_stopping.py`
- Monitors validation loss; triggers stop after `patience` consecutive non-improvements
- Includes `check_overfitting()` passive method for train/val gap monitoring

---

## 10. Web Frontend (Flask Dashboard)

### 10.1 Overview
- **Backend:** `frontend/app.py` — Flask application serving on `http://localhost:5000`
- **Frontend:** `frontend/templates/index.html` + `frontend/static/style.css` + `frontend/static/script.js`
- **Purpose:** Interactive drag-and-drop inference dashboard for live triplet prediction

### 10.2 Architecture
- Loads the trained `best_full_fusion.pth` checkpoint on startup
- Exposes two routes:
  - `GET /` — renders the dashboard UI
  - `POST /predict` — accepts three image uploads (`leaf`, `uav`, `satellite`), returns JSON prediction

### 10.3 Prediction Response Format
```json
{
  "prediction": "Healthy",
  "confidence": 98.5,
  "probabilities": {
    "Healthy": 0.985,
    "Stressed": 0.010,
    "Diseased": 0.005
  }
}
```

### 10.4 UI Features
- Three drag-and-drop upload zones (Leaf 🌿, UAV 🚁, Satellite 🛰)
- Image preview on upload
- Animated probability bars (green for Healthy, amber for Stressed, red for Diseased)
- Loading spinner during inference
- Particle animation background
- Typography: DM Serif Display + DM Mono (Google Fonts)

---

## 11. Complete Project Structure

```
multi-scale-crop-health/
│
├── configs/                              # YAML experiment configurations
│   ├── default_config.yaml               # Base hyperparameters (all exps inherit)
│   ├── exp_full_fusion.yaml              # [leaf, uav, satellite]
│   ├── exp_leaf_only.yaml                # [leaf]
│   ├── exp_uav_only.yaml                 # [uav]
│   ├── exp_satellite_only.yaml           # [satellite]
│   ├── exp_sat_uav.yaml                  # [satellite, uav]
│   ├── exp_uav_leaf.yaml                 # [uav, leaf]
│   └── exp_sat_leaf.yaml                 # [satellite, leaf]
│
├── data/
│   ├── dataset.py                        # CropTripletDataset, SingleModalityDataset
│   ├── raw/                              # Raw extracted images (leaf/, uav/, satellite/)
│   ├── processed/                        # Processed/mapped images
│   └── triplets/                         # Generated CSV triplet files
│       ├── train_triplets.csv
│       ├── val_triplets.csv
│       └── test_triplets.csv
│
├── models/
│   ├── __init__.py
│   ├── backbones.py                      # ResNet50Backbone, EfficientNetB0Backbone
│   ├── fusion_module.py                  # ConcatFusion, AttentionFusion
│   ├── classifier.py                     # ClassificationHead (5376→1024→256→3)
│   └── multiscale_net.py                 # MultiScaleCropNet (master model)
│
├── preprocessing/
│   ├── __init__.py
│   ├── align_datasets.py                 # Class mapping, proxy generation, triplet creation
│   ├── eurosat_processor.py              # EuroSAT class mapping utility
│   └── transforms.py                     # Train/Val augmentation pipelines
│
├── training/
│   ├── __init__.py
│   ├── loss_functions.py                 # CrossEntropy + label smoothing
│   ├── optimizers.py                     # AdamW + CosineAnnealingLR
│   └── trainer.py                        # Training loop with early stopping
│
├── evaluation/
│   ├── __init__.py
│   ├── metrics.py                        # Accuracy, Precision, Recall, F1 computation
│   ├── confusion_matrix.py               # Normalized confusion matrix with seaborn
│   └── ablation_runner.py                # Sequential 7-experiment runner
│
├── experiments/
│   └── run_experiment.py                 # Unified experiment entry point
│
├── utils/
│   ├── __init__.py
│   ├── early_stopping.py                 # EarlyStopping callback
│   ├── io_utils.py                       # Checkpoint save/load, JSON I/O
│   ├── logger.py                         # File+console logger, CSVLogger
│   └── visualizer.py                     # Training curves, Grad-CAM placeholder
│
├── scripts/
│   ├── convert_tif_to_jpg.py             # Optional utility (current pipeline uses on-the-fly TIFF loading)
│   ├── extract_datasets.py               # ZIP extraction pipeline
│   ├── train_all_ablations.ps1           # Windows PowerShell ablation runner
│   └── train_all_ablations.sh            # Linux/macOS ablation runner
│
├── frontend/
│   ├── app.py                            # Flask inference server
│   ├── templates/
│   │   └── index.html                    # Dashboard UI
│   └── static/
│       ├── style.css                     # Dashboard styling
│       └── script.js                     # Drag-and-drop + AJAX prediction
│
├── notebooks/
│   └── CropHealth_Colab.ipynb            # Self-contained Google Colab notebook
│
├── outputs/
│   ├── checkpoints/                      # best_*.pth and per-epoch checkpoints
│   ├── metrics/                          # CSV logs, JSON reports, training curves, ablation chart
│   ├── confusion_matrices/               # Per-experiment confusion matrix PNGs
│   └── gradcam/                          # Reserved for Grad-CAM outputs
│
├── Supporting Documents/
│   ├── Architecture Document (1).docx
│   ├── Functional Document (1).docx
│   ├── Functional Test case Template (1).xlsx
│   └── Sprint Retrospective (1).xlsx
│
├── ieee.tex                              # IEEE-format research paper (LaTeX)
├── pipeline.md                           # Detailed processing pipeline documentation
├── architecture_diagram.png              # Generated architecture diagram
├── requirements.txt                      # Python dependencies
├── README.md                             # Project README
└── .gitignore                            # Git ignore rules
```

---

## 12. Dependencies & Requirements

```
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.23.0
opencv-python>=4.7.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.2.0
pandas>=1.5.0
pyyaml>=6.0
tqdm>=4.65.0
flask>=2.3.0
pillow>=9.5.0
grad-cam>=1.4.8
tifffile  (for EuroSAT multispectral processing)
```

**Training hardware:** Google Colab Tesla T4 (CUDA runtime), PyTorch 2.5.1, batch size 8

---

## 13. End-to-End Execution Pipeline

### Step 1: Environment Setup
```bash
pip install -r requirements.txt
```

### Step 2: Dataset Extraction
```bash
# Place plantvillage.zip, mhsoyahealthvision.zip, eurosat.zip in project root
python scripts/extract_datasets.py
```

### Step 3: TIF-to-JPG Conversion (EuroSAT)
```bash
# Optional only (not required in current NDVI/TIFF pipeline)
python scripts/convert_tif_to_jpg.py
```

### Step 4: Biological Alignment & Triplet Generation
```bash
python preprocessing/align_datasets.py
```
This will:
- Scan all three `data/raw/` modality directories
- Apply biological class mapping rules
- Compute NDVI-based satellite class partitioning for EuroSATallBands
- Split data 70/15/15 with zero leakage
- Create balanced triplet CSVs in `data/triplets/`

### Step 5: Training (Single Experiment)
```bash
python experiments/run_experiment.py --config configs/exp_full_fusion.yaml
```

### Step 6: Training (Full Ablation — All 7 Experiments)
```bash
# Windows PowerShell
.\scripts\train_all_ablations.ps1

# Linux/macOS
./scripts/train_all_ablations.sh

# Or via Python
python experiments/run_experiment.py --ablation
```

### Step 7: Launch Inference Dashboard
```bash
cd frontend
python app.py
# Open http://localhost:5000
```

---

## 14. Training Dynamics — Why Training Accuracy < Validation Accuracy

An important characteristic of this system: **training accuracy is consistently lower than validation accuracy** (e.g., 85.5% vs 99.5% in Epoch 1). This is **expected** and is **not a bug**:

1. **Training augmentation is aggressive** — random crops, flips, rotations, color jitter make training images systematically harder to classify
2. **Frozen backbone design** — generalization is provided by ImageNet pre-training; the small trainable head generalizes readily from epoch one
3. **The validation gap does not signal overfitting** — it signals that the model has strong pre-trained features and the augmented training data is intentionally harder

---

## 15. Key Design Decisions & Rationale

### Why Three Scales?
- **Leaf (Micro):** Captures fine-grained morphological textures (lesion boundaries, color signatures)
- **UAV (Meso):** Provides spatial distribution context (canopy structure, lesion spread patterns)
- **Satellite (Macro):** Adds land management context (managed vs. unmanaged vegetation, field-level health)
- No single scale captures the full diagnostic picture

### Why Frozen Backbones?
- Preserves rich ImageNet pre-trained features
- Reduces GPU memory to fit within 4 GB VRAM budget
- Shortens convergence time (5 epochs sufficient)
- Prevents catastrophic forgetting on small datasets

### Why EfficientNet-B0 for Leaf but ResNet50 for UAV/Satellite?
- EfficientNet-B0 excels at fine texture discrimination (5.3M params, compound scaling)
- ResNet50 is better suited for broader spatial patterns (25.6M params, residual connections)
- UAV and Satellite share geometric characteristics, justifying the same architecture family (but separate weight instances)

### Why Synthetic Diseased Satellite Images?
- EuroSAT has no native "Diseased" land-use class
- Satellite labels are NDVI-derived health-state partitions and remain proxy labels (not pathology-ground-truth)
- This is explicitly acknowledged as a limitation in interpretation and deployment claims
- Future work should incorporate real ground-truth diseased field satellite datasets

### Why Concatenation Fusion Instead of Attention?
- Concatenation is parameter-free, ensuring no modality information is lost
- Simpler to reproduce and debug
- Attention fusion is implemented but not reported in the ablation study (reserved for future work)

---

## 16. Limitations & Future Work

### Current Limitations
1. **Satellite Diseased class is synthetic** — photometric proxy, not true spectral disease signatures
2. **Limited training epochs** (5) on 4 GB GPU with frozen backbones
3. **No temporal analysis** — single-snapshot classification only
4. **Cross-dataset alignment is semantic, not pixel-level** — triplets are pseudo-aligned, not physically co-registered
5. **Species bias** — leaf data spans 14 crop species, UAV data is soybean-only

### Future Directions
1. Replace proxy satellite diseased tiles with real field-acquired satellite data
2. Extend taxonomy to individual disease subtypes (fine-grained classification)
3. Explore transformer-based cross-modal attention fusion
4. Integrate temporal satellite sequences to capture disease progression dynamics
5. Unfreeze upper backbone layers with extended training on larger GPUs
6. Complete Grad-CAM visualization for interpretability

---

## 17. Key File Quick Reference

| Purpose | File Path |
|---------|-----------|
| Master model definition | `models/multiscale_net.py` |
| Backbone networks | `models/backbones.py` |
| Fusion strategies | `models/fusion_module.py` |
| Classifier head | `models/classifier.py` |
| Dataset alignment & triplet generation | `preprocessing/align_datasets.py` |
| Data augmentation transforms | `preprocessing/transforms.py` |
| PyTorch dataset classes | `data/dataset.py` |
| Training loop | `training/trainer.py` |
| Loss function | `training/loss_functions.py` |
| Optimizer & scheduler | `training/optimizers.py` |
| Evaluation metrics | `evaluation/metrics.py` |
| Confusion matrix generator | `evaluation/confusion_matrix.py` |
| Ablation study runner | `evaluation/ablation_runner.py` |
| Unified experiment runner | `experiments/run_experiment.py` |
| Web inference dashboard | `frontend/app.py` |
| Experiment configs | `configs/*.yaml` |
| IEEE research paper | `ieee.tex` |

---

## 18. Glossary

| Term | Meaning |
|------|---------|
| **Triplet** | A tuple of (leaf_image, uav_image, satellite_image) with a shared class label |
| **Modality** | One of three imaging scales: leaf, UAV, or satellite |
| **Ablation** | Systematic removal/addition of model components to measure marginal contribution |
| **GAP** | Global Average Pooling — reduces spatial feature maps to a 1D vector |
| **Proxy** | EuroSAT land-use classes repurposed as crop health proxies |
| **Backbone** | Pre-trained CNN feature extractor (EfficientNet-B0 or ResNet50) |
| **Fusion** | Combination of multi-modality feature vectors into a unified representation |
| **Label Smoothing** | Soft targets that prevent overconfident predictions (ε=0.1) |
| **Early Stopping** | Training halts when validation loss stops improving for `patience` epochs |
| **VRAM** | Video RAM (GPU memory); this project targets 4 GB VRAM constraint |

---

*This knowledge base was generated on 2026-03-28 from the complete source code, documentation, and research paper of the Multi-Scale Crop Health Classification project.*
