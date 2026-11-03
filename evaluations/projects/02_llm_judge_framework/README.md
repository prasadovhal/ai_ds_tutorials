# Project 2: LLM-as-a-Judge Framework

Pointwise + pairwise judging with Ollama, including bias detection.

## Run
```bash
cd projects/02_llm_judge_framework
python main.py
```

## What It Does
- Generates good and bad answers per question
- Pointwise scoring (1-5 scale)
- Pairwise comparison (which is better?)
- Position bias test (swap answer order)
- Works with Ollama or falls back to simulated responses

## Dependencies
requests, ollama (optional)
