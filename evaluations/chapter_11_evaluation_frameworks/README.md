# Chapter 11 - Evaluation Frameworks

Simplified implementations of 10 LLM evaluation frameworks using only the Python standard library.

## Files

| File | Description |
|------|-------------|
| `dataset.py` | Data loading: RAG examples, MCQs, agent traces |
| `sample_data.json` | Sample evaluation data (RAG, MCQ, agent, test cases) |
| `evaluator.py` | Framework-style evaluators (DeepEval, RAGAS, LangSmith, etc.) |
| `theory.md` | All theory, framework comparisons, diagrams, and interview questions |
| `main.py` | Runs all 10 framework demos with output |

## Frameworks Covered

1. **DeepEval** - Unit-test style metrics with `measure()` method
2. **RAGAS** - Component RAG metrics (faithfulness, relevancy, precision, recall)
3. **LangSmith** - Run-based evaluation with custom evaluators
4. **Phoenix (Arize)** - Tracing with inline evaluation spans
5. **OpenAI Evals** - Registry-based eval specs
6. **Promptfoo** - Config-driven assertions with pass/fail
7. **TruLens** - Feedback function pattern
8. **Inspect AI** - Task/solver/scorer pattern
9. **Evidently AI** - Data drift + LLM monitoring
10. **Maxim AI** - End-to-end quality scoring

## Run

```bash
cd chapter_11_evaluation_frameworks
python main.py
```

No external dependencies required.
