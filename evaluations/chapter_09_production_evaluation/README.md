# Chapter 9 - Production Evaluation

Demonstrates how to maintain LLM quality **after** deployment: regression testing, canary rollouts, shadow deployments, drift detection, monitoring, alerting, CI/CD evaluation gates, versioning, and continuous benchmarking.

## Files

| File | Description |
|------|-------------|
| `main.py` | Imports and demonstrates all production evaluation systems |
| `evaluator.py` | Core classes: RegressionTestSuite, CanaryDeployer, ShadowEvaluator, DriftDetector, ProductionMonitor, AlertManager, PromptVersionManager, DeploymentPipeline, ContinuousBenchmark |
| `dataset.py` | Data loading and simulation: production traffic, drift scenarios, canary splits, golden datasets |
| `theory.md` | All theory, intuition, diagrams, and interview questions |
| `sample_data.json` | Simulated production logs, model/prompt versions, alert history, deployment gates |

## Run

```bash
cd chapter_09_production_evaluation
python main.py
```

## Topics Covered

1. **Regression Testing** - Compare new model against golden dataset to catch accuracy regressions
2. **Canary Testing** - Progressive traffic shifting with automatic rollback on quality drop
3. **Shadow Deployment** - Run new model in parallel without serving, compare offline
4. **Drift Detection** - Detect input/output/concept distribution shifts via KL divergence
5. **Production Monitoring** - Sliding-window accuracy, latency percentiles, error rates
6. **Alerting** - Threshold and anomaly-based alerts with severity escalation
7. **CI/CD Evaluation Gates** - Automated pass/fail deployment decisions
8. **Versioning** - Content-addressable prompt versioning, dataset versions, model tracking
9. **Continuous Benchmarking** - Cross-version performance trends with ASCII charts

## Requirements

Python 3.10+ (standard library only). Requires `../data/train.csv` from the Kaggle LLM Science Exam dataset.
