"""
Chapter 11: Evaluation Frameworks

One-file comparison of common framework styles.
"""

from statistics import mean


TEST_CASES = [
    {"id": 1, "question": "What is gravity?", "score": 0.90},
    {"id": 2, "question": "Explain photosynthesis.", "score": 0.82},
    {"id": 3, "question": "What is the Roche limit?", "score": 0.74},
]


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def average_score(rows):
    return mean(row["score"] for row in rows)


def pass_rate(rows, threshold):
    passed = 0
    for row in rows:
        if row["score"] >= threshold:
            passed += 1
    return passed / len(rows)


def deepeval_style(rows):
    return {"average": average_score(rows), "pass_rate": pass_rate(rows, 0.75)}


def ragas_style(rows):
    return {"faithfulness": 0.81, "answer_relevance": 0.79, "context_precision": 0.76}


def langsmith_style(rows):
    return {"trace_count": len(rows), "feedback_average": average_score(rows)}


def promptfoo_style(rows):
    return {"yaml_tests": len(rows), "pass_rate": pass_rate(rows, 0.80)}


def trulens_style(rows):
    return {"feedback_functions": 3, "feedback_average": 0.78}


def inspect_style(rows):
    return {"tasks": len(rows), "scorer_average": average_score(rows)}


def phoenix_style(rows):
    return {"spans": 12, "quality_score": average_score(rows), "latency_ms": 920}


def evidently_style(rows):
    return {"drift_score": 0.12, "quality_trend": "stable"}


def openai_evals_style(rows):
    return {"eval_cases": len(rows), "accuracy": pass_rate(rows, 0.75)}


def maxim_style(rows):
    return {"observations": len(rows), "overall": average_score(rows)}


def main():
    section("Chapter 11: Evaluation Frameworks")

    section("1. DeepEval Style")
    print(deepeval_style(TEST_CASES))

    section("2. RAGAS Style")
    print(ragas_style(TEST_CASES))

    section("3. LangSmith Style")
    print(langsmith_style(TEST_CASES))

    section("4. Promptfoo Style")
    print(promptfoo_style(TEST_CASES))

    section("5. TruLens Style")
    print(trulens_style(TEST_CASES))

    section("6. Inspect Style")
    print(inspect_style(TEST_CASES))

    section("7. Phoenix Style")
    print(phoenix_style(TEST_CASES))

    section("8. Evidently Style")
    print(evidently_style(TEST_CASES))

    section("9. OpenAI Evals Style")
    print(openai_evals_style(TEST_CASES))

    section("10. Maxim AI Style")
    print(maxim_style(TEST_CASES))


if __name__ == "__main__":
    main()
