# Multi-Scale Crop Health Classification

MultiScaleCropNet is a multi-modal crop health classifier that fuses three sensing scales:
- Leaf close-up imagery (PlantVillage)
- UAV canopy imagery (MH-SoyaHealthVision)
- Satellite tiles (EuroSATallBands Sentinel-2)

The target classes are Healthy, Stressed, and Diseased.

## Architecture

```text
Leaf (Micro)  ----[ EfficientNet-B0 ]----[ GAP ]----\\
                                                     \\
UAV (Mid)     ----[    ResNet50     ]----[ GAP ]------[ Fusion (Concat | Attention | Learned Gating) ]--->[ Classifier Head ]---> [3 Classes]
                                                     /                  (1024 -> 256 -> 3)
Satellite (Macro)-[    ResNet50     ]----[ GAP ]----/
```

## Dataset and Labeling Notes

- PlantVillage and MH-SoyaHealthVision are mapped to Healthy/Stressed/Diseased using biological rules.
- Satellite modality uses EuroSATallBands TIFF data.
- In the current pipeline, satellite labels are partitioned by NDVI percentile bands (lower 33% = Diseased, middle 34% = Stressed, upper 33% = Healthy) for mapped agricultural classes.

## Quick Start (Local)

1. Install dependencies.

```bash
pip install -r requirements.txt
```

2. Align data and generate triplets.

```bash
python preprocessing/align_datasets.py
```

3. Train full fusion.

```bash
python experiments/run_experiment.py --config configs/exp_full_fusion.yaml
```

Train weighted full fusion with consistency regularization:

```bash
python experiments/run_experiment.py --config configs/exp_full_fusion_weighted.yaml
```

Run a three-seed summary (mean/std written to `*_seed_summary.json`):

```bash
python experiments/run_experiment.py --config configs/exp_full_fusion_weighted.yaml --seeds 42,123,999
```

4. Run ablations (optional).

```bash
# Windows PowerShell
.\scripts\train_all_ablations.ps1

# Linux/macOS
./scripts/train_all_ablations.sh
```

## Google Colab (T4) Training

Use:
- notebooks/Train_From_Drive_OneClick.ipynb

This notebook mounts Google Drive, extracts a full project zip, aligns datasets, validates triplet paths, trains on T4 GPU, and copies outputs back to Drive.

## Latest Metrics Snapshot

From the latest Colab T4 full-fusion run in output/metrics/full_fusion_metrics.json:
- Accuracy: 0.9925
- Macro Precision: 0.9926
- Macro Recall: 0.9925
- Macro F1: 0.9925

Representative ablation metrics (balanced test set, 804 samples):
- satellite_only: Acc 0.8968, F1 0.8958
- uav_only: Acc 0.9739, F1 0.9738
- leaf_only: Acc 0.9552, F1 0.9550
- sat_uav: Acc 0.9876, F1 0.9876
- uav_leaf: Acc 0.9876, F1 0.9876
- sat_leaf: Acc 0.9888, F1 0.9888
- full_fusion: Acc 0.9925, F1 0.9925

## Output Artifacts

Training writes to:
- output/checkpoints or outputs/checkpoints
- output/metrics or outputs/metrics
- output/confusion_matrices or outputs/confusion_matrices

Use the latest timestamps when selecting final report artifacts.
