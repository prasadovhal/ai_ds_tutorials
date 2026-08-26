"""
Chapter 2: Classical NLP Metrics

Covers classic NLP and ML evaluation metrics:
- Classification metrics: accuracy, precision, recall, F1, confusion matrix
- Text generation metrics: BLEU, ROUGE, exact match, token F1
- Language model metrics: perplexity, cross entropy
- Calibration: measuring confidence vs correctness

Demonstrates each metric on both classification and text generation tasks.
Beginner-friendly implementation: one file, no classes, small metric functions.
"""

import math
from collections import Counter


GROUND_TRUTH = ["A", "B", "A", "C", "B", "A"]
GOOD_PREDICTIONS = ["A", "B", "A", "C", "A", "A"]
POOR_PREDICTIONS = ["B", "C", "A", "A", "C", "B"]

REFERENCE = "the cat sat on the mat"
GOOD_TEXT = "the cat sat on the mat"
MEDIUM_TEXT = "the cat sat on mat"
POOR_TEXT = "dogs run in the park"


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def accuracy(truth, preds):
    correct = 0
    for expected, predicted in zip(truth, preds):
        if expected == predicted:
            correct += 1
    return correct / len(truth)


def precision_for_label(truth, preds, label):
    true_positive = 0
    false_positive = 0
    for expected, predicted in zip(truth, preds):
        if predicted == label and expected == label:
            true_positive += 1
        if predicted == label and expected != label:
            false_positive += 1
    if true_positive + false_positive == 0:
        return 0.0
    return true_positive / (true_positive + false_positive)


def recall_for_label(truth, preds, label):
    true_positive = 0
    false_negative = 0
    for expected, predicted in zip(truth, preds):
        if expected == label and predicted == label:
            true_positive += 1
        if expected == label and predicted != label:
            false_negative += 1
    if true_positive + false_negative == 0:
        return 0.0
    return true_positive / (true_positive + false_negative)


def f1_score(precision_value, recall_value):
    if precision_value + recall_value == 0:
        return 0.0
    return 2 * precision_value * recall_value / (precision_value + recall_value)


def confusion_matrix(truth, preds):
    matrix = {}
    labels = sorted(set(truth + preds))
    for expected in labels:
        matrix[expected] = {}
        for predicted in labels:
            matrix[expected][predicted] = 0
    for expected, predicted in zip(truth, preds):
        matrix[expected][predicted] += 1
    return matrix


def tokenize(text):
    return text.lower().split()


def unigram_precision(reference, hypothesis):
    ref_counts = Counter(tokenize(reference))
    hyp_counts = Counter(tokenize(hypothesis))
    overlap = 0
    for token, count in hyp_counts.items():
        overlap += min(count, ref_counts[token])
    if len(tokenize(hypothesis)) == 0:
        return 0.0
    return overlap / len(tokenize(hypothesis))


def unigram_recall(reference, hypothesis):
    ref_tokens = tokenize(reference)
    ref_counts = Counter(ref_tokens)
    hyp_counts = Counter(tokenize(hypothesis))
    overlap = 0
    for token, count in ref_counts.items():
        overlap += min(count, hyp_counts[token])
    return overlap / len(ref_tokens)


def bleu_1(reference, hypothesis):
    precision = unigram_precision(reference, hypothesis)
    ref_len = len(tokenize(reference))
    hyp_len = len(tokenize(hypothesis))
    if hyp_len == 0:
        return 0.0
    brevity_penalty = 1.0
    if hyp_len < ref_len:
        brevity_penalty = math.exp(1 - ref_len / hyp_len)
    return brevity_penalty * precision


def rouge_1(reference, hypothesis):
    return unigram_recall(reference, hypothesis)


def exact_match(reference, hypothesis):
    return reference.strip().lower() == hypothesis.strip().lower()


def token_f1(reference, hypothesis):
    precision_value = unigram_precision(reference, hypothesis)
    recall_value = unigram_recall(reference, hypothesis)
    return f1_score(precision_value, recall_value)


def perplexity(probabilities):
    log_sum = 0
    for probability in probabilities:
        log_sum += math.log(probability)
    average_negative_log = -log_sum / len(probabilities)
    return math.exp(average_negative_log)


def cross_entropy(probabilities):
    total = 0
    for probability in probabilities:
        total += -math.log(probability)
    return total / len(probabilities)


def calibration_gap(correct_flags, confidences):
    accuracy_value = sum(correct_flags) / len(correct_flags)
    confidence_value = sum(confidences) / len(confidences)
    return abs(accuracy_value - confidence_value)


def show_classification_metrics(name, preds):
    section(name)
    print(f"Accuracy: {accuracy(GROUND_TRUTH, preds):.2%}")
    for label in sorted(set(GROUND_TRUTH)):
        precision_value = precision_for_label(GROUND_TRUTH, preds, label)
        recall_value = recall_for_label(GROUND_TRUTH, preds, label)
        f1_value = f1_score(precision_value, recall_value)
        print(f"Label {label}: precision={precision_value:.2f} recall={recall_value:.2f} f1={f1_value:.2f}")
    print("Confusion matrix:")
    for expected, row in confusion_matrix(GROUND_TRUTH, preds).items():
        print(expected, row)


def show_text_metrics():
    section("Text Generation Metrics")
    texts = [("good", GOOD_TEXT), ("medium", MEDIUM_TEXT), ("poor", POOR_TEXT)]
    for name, text in texts:
        print(f"{name}:")
        print(f"  BLEU-1: {bleu_1(REFERENCE, text):.3f}")
        print(f"  ROUGE-1: {rouge_1(REFERENCE, text):.3f}")
        print(f"  Exact Match: {exact_match(REFERENCE, text)}")
        print(f"  Token F1: {token_f1(REFERENCE, text):.3f}")


def show_language_model_metrics():
    section("Language Model Metrics")
    good_probabilities = [0.9, 0.8, 0.7, 0.95]
    poor_probabilities = [0.4, 0.3, 0.2, 0.5]
    print(f"Good text cross entropy: {cross_entropy(good_probabilities):.3f}")
    print(f"Good text perplexity: {perplexity(good_probabilities):.3f}")
    print(f"Poor text cross entropy: {cross_entropy(poor_probabilities):.3f}")
    print(f"Poor text perplexity: {perplexity(poor_probabilities):.3f}")


def show_calibration():
    section("Calibration")
    good_correct = [1, 1, 1, 1, 0, 1]
    good_confidences = [0.85, 0.80, 0.90, 0.88, 0.65, 0.82]
    overconfident_correct = [1, 0, 1, 0, 0, 1]
    overconfident_confidences = [0.95, 0.93, 0.94, 0.92, 0.91, 0.96]
    print(f"Good model calibration gap: {calibration_gap(good_correct, good_confidences):.3f}")
    print(f"Overconfident model calibration gap: {calibration_gap(overconfident_correct, overconfident_confidences):.3f}")


def main():
    section("Chapter 2: Classical NLP Metrics")
    show_classification_metrics("Classification Metrics: Good Predictions", GOOD_PREDICTIONS)
    show_classification_metrics("Classification Metrics: Poor Predictions", POOR_PREDICTIONS)
    show_text_metrics()
    show_language_model_metrics()
    show_calibration()


if __name__ == "__main__":
    main()
