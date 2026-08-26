"""
Chapter 1: Foundations of LLM Evaluation

Beginner-friendly version:
- one file
- no classes
- small functions
- top-to-bottom flow
"""

from collections import Counter
from statistics import mean


QUESTIONS = [
    {"id": 1, "prompt": "What planet is called the Red Planet?", "truth": "Mars", "pred": "Mars"},
    {"id": 2, "prompt": "What gas do plants absorb?", "truth": "Carbon dioxide", "pred": "Oxygen"},
    {"id": 3, "prompt": "What force pulls objects down?", "truth": "Gravity", "pred": "Gravity"},
    {"id": 4, "prompt": "What is H2O?", "truth": "Water", "pred": "Water"},
    {"id": 5, "prompt": "What star is at the center of our solar system?", "truth": "Sun", "pred": "Sun"},
]

MODEL_SCORES = {
    "good_model": 0.90,
    "medium_model": 0.70,
    "poor_model": 0.40,
}


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def accuracy(rows):
    correct = 0
    for row in rows:
        if row["truth"] == row["pred"]:
            correct += 1
    return correct / len(rows)


def errors(rows):
    wrong_rows = []
    for row in rows:
        if row["truth"] != row["pred"]:
            wrong_rows.append(row)
    return wrong_rows


def rolling_accuracy(rows, window_size):
    recent_rows = rows[-window_size:]
    return accuracy(recent_rows)


def per_label_accuracy(rows):
    grouped = {}
    for row in rows:
        label = row["truth"]
        grouped.setdefault(label, [])
        grouped[label].append(row)

    results = {}
    for label, label_rows in grouped.items():
        results[label] = accuracy(label_rows)
    return results


def confusion_counts(rows):
    matrix = {}
    for row in rows:
        key = (row["truth"], row["pred"])
        matrix[key] = matrix.get(key, 0) + 1
    return matrix


def reference_free_check(answer, allowed_answers):
    return {
        "is_valid_option": answer in allowed_answers,
        "length": len(answer),
    }


def judge_score(answer, truth):
    if answer == truth:
        return 5
    return 2


def compare_versions(old_score, new_score, allowed_drop=0.02):
    delta = new_score - old_score
    if delta < -allowed_drop:
        status = "regression"
    elif delta > 0:
        status = "improved"
    else:
        status = "stable"
    return {"old": old_score, "new": new_score, "delta": delta, "status": status}


def trend_summary(history):
    best = max(history, key=lambda item: item["accuracy"])
    worst = min(history, key=lambda item: item["accuracy"])
    deltas = []
    for index in range(1, len(history)):
        previous_score = history[index - 1]["accuracy"]
        current_score = history[index]["accuracy"]
        deltas.append(current_score - previous_score)
    return {"best": best, "worst": worst, "avg_delta": mean(deltas)}


def dashboard(rows):
    report = {
        "accuracy": accuracy(rows),
        "total_questions": len(rows),
        "total_errors": len(errors(rows)),
        "per_label_accuracy": per_label_accuracy(rows),
        "confusion_matrix": confusion_counts(rows),
    }
    return report


def print_dashboard(report):
    print(f"Overall accuracy: {report['accuracy']:.2%}")
    print(f"Questions: {report['total_questions']}")
    print(f"Errors: {report['total_errors']}")
    print("Per-label accuracy:")
    for label, score in report["per_label_accuracy"].items():
        print(f"  {label}: {score:.2%}")
    print("Confusion pairs:")
    for pair, count in report["confusion_matrix"].items():
        print(f"  truth={pair[0]} pred={pair[1]} -> {count}")


def topic_1_why_evaluation_matters():
    section("1. Why Evaluation Matters")
    distribution = Counter(row["truth"] for row in QUESTIONS)
    print(f"Dataset size: {len(QUESTIONS)}")
    print(f"Answer distribution: {dict(distribution)}")
    for model_name, score in MODEL_SCORES.items():
        print(f"{model_name}: {score:.0%} accuracy")


def topic_2_offline_vs_online():
    section("2. Offline vs Online Evaluation")
    print(f"Offline batch accuracy: {accuracy(QUESTIONS):.2%}")
    print(f"Online rolling accuracy over last 3 questions: {rolling_accuracy(QUESTIONS, 3):.2%}")


def topic_3_intrinsic_vs_extrinsic():
    section("3. Intrinsic vs Extrinsic Evaluation")
    intrinsic = accuracy(QUESTIONS)
    extrinsic_task_completion = 0.80
    extrinsic_user_satisfaction = 4.1
    print(f"Intrinsic metric: accuracy = {intrinsic:.2%}")
    print(f"Extrinsic metric: task completion = {extrinsic_task_completion:.2%}")
    print(f"Extrinsic metric: user satisfaction = {extrinsic_user_satisfaction}/5")


def topic_4_human_vs_automatic():
    section("4. Human vs Automatic Evaluation")
    automatic_score = accuracy(QUESTIONS)
    human_score = 0.82
    print(f"Automatic evaluation: fast and scalable -> {automatic_score:.2%}")
    print(f"Human evaluation: slower but nuanced -> {human_score:.2%}")


def topic_5_reference_vs_reference_free():
    section("5. Reference vs Reference-Free Evaluation")
    row = QUESTIONS[0]
    print(f"Reference-based: truth={row['truth']} pred={row['pred']} match={row['truth'] == row['pred']}")
    free_result = reference_free_check("Mars", ["Mars", "Jupiter", "Venus"])
    print(f"Reference-free: {free_result}")


def topic_6_model_based_evaluation():
    section("6. Model-Based Evaluation")
    for row in QUESTIONS[:3]:
        score = judge_score(row["pred"], row["truth"])
        print(f"Q{row['id']} judge score: {score}/5")


def topic_7_regression_testing():
    section("7. Regression Testing")
    result = compare_versions(0.78, 0.74)
    print(result)


def topic_8_continuous_evaluation():
    section("8. Continuous Evaluation")
    history = [
        {"version": "v1.0", "accuracy": 0.72},
        {"version": "v1.1", "accuracy": 0.75},
        {"version": "v1.2", "accuracy": 0.79},
        {"version": "v1.3", "accuracy": 0.77},
    ]
    summary = trend_summary(history)
    print(f"Best version: {summary['best']}")
    print(f"Worst version: {summary['worst']}")
    print(f"Average delta: {summary['avg_delta']:+.2%}")


def topic_9_lifecycle():
    section("9. Evaluation Lifecycle")
    stages = [
        "prepare dataset",
        "run model",
        "compute metrics",
        "analyze errors",
        "compare with baseline",
        "publish report",
    ]
    for step_number, stage in enumerate(stages, start=1):
        print(f"{step_number}. {stage}")


def topic_10_pipeline():
    section("10. Evaluation Pipeline")
    print("Step 1: load rows")
    print("Step 2: compute accuracy")
    print("Step 3: compute confusion matrix")
    print("Step 4: save report")
    print(f"Pipeline accuracy result: {accuracy(QUESTIONS):.2%}")


def topic_11_error_taxonomy():
    section("11. Failure Analysis and Error Taxonomy")
    wrong_rows = errors(QUESTIONS)
    error_types = {"knowledge_error": 1, "format_error": 0, "reasoning_error": 0}
    print(f"Total errors: {len(wrong_rows)}")
    print(f"Error buckets: {error_types}")
    for row in wrong_rows:
        print(f"Q{row['id']} expected={row['truth']} predicted={row['pred']}")


def topic_12_dashboard():
    section("12. Evaluation Dashboard")
    print_dashboard(dashboard(QUESTIONS))


def topic_13_cicd():
    section("13. Evaluation in CI/CD")
    current_accuracy = accuracy(QUESTIONS)
    minimum_required = 0.75
    deploy_allowed = current_accuracy >= minimum_required
    print(f"Current accuracy: {current_accuracy:.2%}")
    print(f"Minimum required: {minimum_required:.2%}")
    print(f"Deploy allowed: {deploy_allowed}")


def main():
    section("Chapter 1: Foundations of LLM Evaluation")
    topic_1_why_evaluation_matters()
    topic_2_offline_vs_online()
    topic_3_intrinsic_vs_extrinsic()
    topic_4_human_vs_automatic()
    topic_5_reference_vs_reference_free()
    topic_6_model_based_evaluation()
    topic_7_regression_testing()
    topic_8_continuous_evaluation()
    topic_9_lifecycle()
    topic_10_pipeline()
    topic_11_error_taxonomy()
    topic_12_dashboard()
    topic_13_cicd()


if __name__ == "__main__":
    main()
