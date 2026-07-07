# Chapter 7 - Evaluation Dataset Engineering

Building and validating evaluation datasets that reliably measure LLM performance.

## Files

| File | Description |
|------|-------------|
| `dataset.py` | Data loading, topic/difficulty detection, duplicate finding, simulated predictions |
| `evaluator.py` | Quality checks, coverage analysis, contamination detection, label noise, Cohen's/Fleiss' Kappa, meta-evaluation |
| `theory.md` | All theory, formulas, intuition, diagrams, and interview questions |
| `sample_data.json` | 20 MCQ questions with intentional quality issues (duplicates, noise, imbalance) |
| `main.py` | End-to-end demonstration of all topics |

## Topics Covered

1. **Benchmark Design** -- Balanced subset selection with topic/difficulty quotas
2. **Dataset Quality Checks** -- Completeness, correctness, consistency validation
3. **Coverage Metrics** -- Topic, difficulty, and answer distribution coverage with entropy
4. **Failure-Mode Coverage & Balancing** -- Duplicate detection, answer skew, prompt outliers
5. **Contamination Detection** -- Exact match, near-duplicate, and answer leakage checks
6. **Label Noise Detection** -- Annotator disagreement and model-consensus methods
7. **Cohen's Kappa** -- Inter-rater agreement for 2 raters, built from scratch
8. **Fleiss' Kappa** -- Inter-rater agreement for N raters, built from scratch
9. **Meta-Evaluation** -- Evaluating the evaluation dataset itself, plus evaluator reliability

## Run

```bash
cd chapter_07_evaluation_dataset_engineering
python main.py
```

No external dependencies required -- uses only the Python standard library.
