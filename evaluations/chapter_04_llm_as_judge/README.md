# Chapter 4 - LLM-as-a-Judge

Comprehensive demonstration of **21 LLM-as-a-Judge techniques** for evaluating language model outputs. All evaluations use simulated judge responses so the code runs without external dependencies.

## Topics Covered

| # | Topic | Description |
|---|-------|-------------|
| 1 | History of LLM-as-a-Judge | Timeline from BLEU (2002) through Chatbot Arena (2023) to modern hybrid pipelines |
| 2 | Why BLEU/ROUGE Are Insufficient | Demonstrates failure cases: paraphrases, hallucinations, shallow word overlap |
| 3 | Judge Prompt Engineering | Design principles for reliable judge prompts: role, rubric, format, CoT |
| 4 | Pointwise Evaluation | Score a single response on a 1-5 scale |
| 5 | Pairwise Evaluation | Compare two responses head-to-head and pick the winner |
| 6 | Pass/Fail Evaluation | Binary quality gate for minimum acceptance criteria |
| 7 | Likert Scale Evaluation | Multi-dimensional rating (accuracy, completeness, clarity, depth, helpfulness) |
| 8 | Rubric-Based Evaluation | Score against specific criteria with defined levels |
| 9 | G-Eval (Chain-of-Thought) | Step-by-step reasoning before scoring, based on the G-Eval paper |
| 10 | Arena-Style Evaluation | Tournament bracket with head-to-head matches across questions |
| 11 | Tournament / Elo Ratings | Elo rating system that accounts for opponent strength |
| 12 | Constitutional Evaluation | Check responses against core principles (accuracy, helpfulness, harmlessness) |
| 13 | Self-Evaluation | A model evaluates its own output |
| 14 | Reflexion | Iterative self-improvement: evaluate, get feedback, revise, repeat |
| 15 | Multi-Agent Judging | Panel of specialist judges reaching consensus |
| 16 | Judge Agreement Metrics | Cohen's Kappa, Pearson correlation, percent agreement |
| 17 | Judge Reliability | Test-retest consistency and calibration checks |
| 18 | Bias Detection | Verbosity bias, position bias, length bias, self-favoritism |
| 19 | Meta-Evaluation | Evaluate the evaluator by comparing judge vs. human scores |
| 20 | Human Agreement Analysis | Measure judge-human agreement on pairwise preferences |
| 21 | Production Best Practices | 28-point checklist for deploying LLM judges in production |

## Project Structure

```
chapter_04_llm_as_judge/
    main.py            - Entry point demonstrating all 21 techniques
    evaluator.py       - All judge implementations, prompt templates, and evaluation logic
    dataset.py         - Data loading and preparation utilities
    theory.md          - All theory, intuition, diagrams, and interview questions
    sample_data.json   - Curated evaluation dataset (10 science questions, 3 models)
    requirements.txt   - Dependencies (standard library only; optional extras listed)
    README.md          - This file
```

## Quick Start

```bash
cd chapter_04_llm_as_judge
python main.py
```

No external dependencies required. The code uses simulated judge responses by default.

## Dataset

The sample dataset (`sample_data.json`) contains:
- **10 science questions** spanning astrophysics, physics, quantum physics, electromagnetics, general relativity, and mathematics
- **3 model responses** per question (Mistral-7B-v0.2, Llama-2-7B-Chat, GPT-4-turbo)
- **5 pairwise comparisons** with human preference labels
- **Bias test pairs** for verbosity, position, and self-favoritism testing

## Key Classes (evaluator.py)

| Class | Technique |
|-------|-----------|
| `PointwiseJudge` | Single-response 1-5 scoring |
| `PairwiseJudge` | Head-to-head comparison |
| `PassFailJudge` | Binary pass/fail gate |
| `LikertJudge` | Multi-dimensional Likert scale |
| `RubricJudge` | Criterion-based rubric scoring |
| `GEvalJudge` | Chain-of-thought evaluation |
| `ArenaEvaluator` | Tournament bracket with win rates |
| `EloRatingSystem` | Elo ratings for model ranking |
| `ConstitutionalJudge` | Principle-based evaluation |
| `SelfEvaluator` | Self-assessment |
| `ReflexionEvaluator` | Iterative improvement loop |
| `MultiJudgePanel` | Multi-agent consensus |
| `JudgeAgreement` | Inter-judge agreement metrics |
| `JudgeReliability` | Test-retest and calibration |
| `BiasDetector` | Bias detection suite |
| `MetaEvaluator` | Judge-vs-human comparison |
| `ClassicalMetricsDemonstrator` | BLEU/ROUGE failure cases |

## Optional: Real LLM Judging

To use a real LLM as the judge instead of simulations, uncomment the Ollama integration in `evaluator.py`:

```bash
# Install Ollama and pull Mistral
ollama serve
ollama pull mistral

# Uncomment the call_ollama function and real judge methods in evaluator.py
```
