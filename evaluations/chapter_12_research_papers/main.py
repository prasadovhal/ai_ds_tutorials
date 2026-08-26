"""
Chapter 12: Research Papers on LLM Evaluation

One-file educational demo of landmark paper ideas.
"""

from statistics import mean


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def mt_bench():
    scores_a = [8.5, 8.0]
    scores_b = [7.0, 7.5]
    return {"model_a_avg": mean(scores_a), "model_b_avg": mean(scores_b), "winner": "A"}


def g_eval():
    rubric_scores = [4, 5, 4]
    return mean(rubric_scores)


def ragas():
    return {"faithfulness": 0.84, "answer_relevance": 0.80, "context_precision": 0.77}


def ares():
    return {"synthetic_labels_used": True, "judge_accuracy": 0.79}


def agent_bench():
    return {"task_success": 0.68, "tool_use": 0.75}


def swe_bench():
    return {"issues_solved": 3, "total_issues": 10, "score": 0.30}


def reflexion():
    return {"before": 0.55, "after": 0.72}


def calibration():
    return {"ece": 0.09}


def bias():
    return {"position_bias_gap": 0.07}


def meta_evaluation():
    return {"judge_human_agreement": 0.83}


def main():
    section("Chapter 12: Research Papers")

    section("1. MT-Bench")
    print(mt_bench())

    section("2. G-Eval")
    print(f"G-Eval average rubric score: {g_eval():.2f}")

    section("3. RAGAS")
    print(ragas())

    section("4. ARES")
    print(ares())

    section("5. AgentBench")
    print(agent_bench())

    section("6. SWE-Bench")
    print(swe_bench())

    section("7. Reflexion")
    print(reflexion())

    section("8. Calibration Papers")
    print(calibration())

    section("9. Bias Papers")
    print(bias())

    section("10. Meta-Evaluation")
    print(meta_evaluation())


if __name__ == "__main__":
    main()
