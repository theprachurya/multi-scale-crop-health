#!/bin/bash
# Train all ablations sequentially

echo "Starting Ablation Suite..."
python experiments/run_experiment.py --ablation
echo "Ablation Suite Complete. Check outputs/metrics/ablation_results.csv."
