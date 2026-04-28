# Train all ablations sequentially (PowerShell)

Write-Host "Starting Ablation Suite..." -ForegroundColor Green
.\venv_cuda\Scripts\python.exe experiments/run_experiment.py --ablation
Write-Host "Ablation Suite Complete. Check outputs/metrics/ablation_results.csv." -ForegroundColor Green
