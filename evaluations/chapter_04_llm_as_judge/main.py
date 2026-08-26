"""
Chapter 4: LLM-as-a-Judge

Simple version with no classes and no hidden control flow.
"""

from statistics import mean


QUESTION = "Which answer better explains photosynthesis?"
ANSWER_A = "Photosynthesis lets plants use sunlight, water, and carbon dioxide to make glucose and oxygen."
ANSWER_B = "Plants are green and they grow outside. Photosynthesis is probably food."
REFERENCE = "A good answer should mention sunlight, carbon dioxide, water, glucose, and oxygen."


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def word_overlap(reference, answer):
    reference_words = set(reference.lower().replace(",", "").replace(".", "").split())
    answer_words = set(answer.lower().replace(",", "").replace(".", "").split())
    return len(reference_words & answer_words) / len(reference_words)


def pointwise_score(answer):
    return round(5 * word_overlap(REFERENCE, answer), 2)


def pairwise_winner(answer_a, answer_b):
    score_a = pointwise_score(answer_a)
    score_b = pointwise_score(answer_b)
    if score_a > score_b:
        return "A"
    if score_b > score_a:
        return "B"
    return "tie"


def pass_fail(answer, threshold=2.5):
    return pointwise_score(answer) >= threshold


def likert(answer):
    return max(1, round(pointwise_score(answer)))


def rubric(answer):
    checks = {
        "mentions_inputs": "sunlight" in answer.lower() and "water" in answer.lower(),
        "mentions_outputs": "glucose" in answer.lower() or "oxygen" in answer.lower(),
        "scientifically_clear": len(answer.split()) > 8,
    }
    return checks


def geval(answer):
    scores = [pointwise_score(answer), likert(answer)]
    return round(mean(scores), 2)


def arena_vote(answer_a, answer_b):
    return pairwise_winner(answer_a, answer_b)


def elo_update(rating_a, rating_b, winner):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 - expected_a
    actual_a = 1 if winner == "A" else 0
    actual_b = 1 if winner == "B" else 0
    k = 32
    new_a = rating_a + k * (actual_a - expected_a)
    new_b = rating_b + k * (actual_b - expected_b)
    return round(new_a, 1), round(new_b, 1)


def constitutional_check(answer):
    return "unsafe" not in answer.lower()


def self_evaluation(answer):
    return {"self_score": pointwise_score(answer), "self_comment": "Good coverage" if pointwise_score(answer) > 3 else "Needs detail"}


def reflexion(answer):
    improved = answer + " It also explains that glucose stores energy for the plant."
    return improved


def judge_agreement(scores):
    first = scores[0]
    matches = 0
    for score in scores[1:]:
        if score == first:
            matches += 1
    return matches / (len(scores) - 1)


def bias_check(answer_a_first_score, answer_b_first_score):
    return abs(answer_a_first_score - answer_b_first_score)


def meta_evaluation():
    human_preference = "A"
    judge_preference = pairwise_winner(ANSWER_A, ANSWER_B)
    return judge_preference == human_preference


def human_agreement():
    labels = ["A", "A", "B"]
    return labels.count("A") / len(labels)


def production_best_practices():
    practices = [
        "use clear rubric",
        "test judge bias",
        "keep human spot checks",
        "track judge drift",
        "version judge prompts",
    ]
    for item in practices:
        print(f"- {item}")


def main():
    section("Chapter 4: LLM-as-a-Judge")
    print("1. History: lexical metrics came first, judge models came later.")
    print("2. Why BLEU and ROUGE fail: wording can differ while meaning stays correct.")
    print("3. Judge prompt engineering: tell the judge what to score and why.")

    section("4. Pointwise Evaluation")
    print(f"A: {pointwise_score(ANSWER_A)}/5")
    print(f"B: {pointwise_score(ANSWER_B)}/5")

    section("5. Pairwise Evaluation")
    print(f"Winner: {pairwise_winner(ANSWER_A, ANSWER_B)}")

    section("6. Pass/Fail")
    print(f"A pass: {pass_fail(ANSWER_A)}")
    print(f"B pass: {pass_fail(ANSWER_B)}")

    section("7. Likert Scale")
    print(f"A likert: {likert(ANSWER_A)}")
    print(f"B likert: {likert(ANSWER_B)}")

    section("8. Rubric-Based Evaluation")
    print(f"A rubric: {rubric(ANSWER_A)}")
    print(f"B rubric: {rubric(ANSWER_B)}")

    section("9. G-Eval Style")
    print(f"A G-Eval: {geval(ANSWER_A)}")
    print(f"B G-Eval: {geval(ANSWER_B)}")

    section("10. Arena Style")
    print(f"Arena winner: {arena_vote(ANSWER_A, ANSWER_B)}")

    section("11. Tournament and Elo")
    print(f"Updated ratings: {elo_update(1200, 1200, 'A')}")

    section("12. Constitutional Evaluation")
    print(f"A safe: {constitutional_check(ANSWER_A)}")

    section("13. Self-Evaluation")
    print(self_evaluation(ANSWER_A))

    section("14. Reflexion")
    print(reflexion(ANSWER_B))

    section("15. Multi-Agent Judging")
    judge_scores = [pointwise_score(ANSWER_A), pointwise_score(ANSWER_A), pointwise_score(ANSWER_B)]
    print(f"Judge scores: {judge_scores}")

    section("16. Judge Agreement")
    print(f"Agreement: {judge_agreement(judge_scores):.2f}")

    section("17. Judge Reliability")
    print("Reliable judges give similar scores when rerun on the same answer.")

    section("18. Bias Detection")
    print(f"Position bias gap: {bias_check(4.2, 4.0):.2f}")

    section("19. Meta-Evaluation")
    print(f"Judge agrees with human: {meta_evaluation()}")

    section("20. Human Agreement")
    print(f"Human agreement on winner A: {human_agreement():.2%}")

    section("21. Production Best Practices")
    production_best_practices()


if __name__ == "__main__":
    main()
