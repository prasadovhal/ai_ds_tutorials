# Project 8: CI/CD Evaluation Pipeline

Quality gates + regression checking for automated model deployment.

## Run
```bash
cd projects/08_cicd_eval_pipeline
python main.py
```

## What It Does
- Simulates baseline (v1) and candidate (v2) model predictions
- Runs quality gates: accuracy threshold, F1 minimum, latency cap
- Performs regression check against baseline
- Produces PASS/FAIL deployment decision
- Prints full pipeline report with gate details

## Dependencies
scikit-learn (optional, falls back to manual metrics)
