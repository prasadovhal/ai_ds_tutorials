# Project 5: Continuous Evaluation System

Drift detection + alerting + trend tracking for model monitoring.

## Run
```bash
cd projects/05_continuous_eval_system
python main.py
```

## What It Does
- Processes data in batches to simulate production traffic
- Tracks accuracy per batch with sliding window
- Detects drift when accuracy drops below threshold
- Fires alerts with severity levels
- Prints trend chart showing accuracy over time

## Dependencies
Python standard library only
