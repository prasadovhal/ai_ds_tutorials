# Project 1: Simple Evaluator

Builds an accuracy + BLEU + ROUGE evaluator on science MCQ data.

## Run
```bash
cd projects/01_simple_evaluator
python main.py
```

## What It Does
- Loads questions from `data/train.csv`
- Simulates model predictions at different accuracy levels
- Computes accuracy, precision, recall, F1, BLEU, ROUGE
- Prints comparison table across models

## Dependencies
pandas, scikit-learn (via root pyproject.toml)
