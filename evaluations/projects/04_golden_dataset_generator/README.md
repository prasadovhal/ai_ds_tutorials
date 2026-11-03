# Project 4: Golden Dataset Generator

Synthetic dataset creation + validation with deduplication and versioning.

## Run
```bash
cd projects/04_golden_dataset_generator
python main.py
```

## What It Does
- Analyzes source data distribution
- Generates synthetic questions (via Ollama or templates)
- Deduplicates using Jaccard similarity
- Validates answer balance with chi-squared test
- Versions the dataset with metadata tracking

## Dependencies
pandas, scikit-learn, ollama (optional)
