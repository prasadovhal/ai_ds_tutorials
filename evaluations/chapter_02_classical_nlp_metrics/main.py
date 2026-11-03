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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix as sk_confusion_matrix

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
    return accuracy_score(truth, preds)


def precision_for_label(truth, preds, label):
    return precision_score(truth, preds, labels=[label], average=None, zero_division=0.0)[0]


def recall_for_label(truth, preds, label):
    return recall_score(truth, preds, labels=[label], average=None, zero_division=0.0)[0]


def compute_f1_score(precision_value, recall_value):
    if precision_value + recall_value == 0:
        return 0.0
    return 2 * precision_value * recall_value / (precision_value + recall_value)


def confusion_matrix(truth, preds):
    labels = sorted(set(truth + preds))
    cm = sk_confusion_matrix(truth, preds, labels=labels)
    return {labels[i]: {labels[j]: int(cm[i][j]) for j in range(len(labels))} for i in range(len(labels))}


try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from rouge_score import rouge_scorer
    HAS_BLEU = True
    HAS_ROUGE = True
except ImportError:
    HAS_BLEU = False
    HAS_ROUGE = False


def tokenize(text):
    return text.lower().split()


def bleu_1(reference, hypothesis):
    if HAS_BLEU:
        ref_tokens = reference.lower().split()
        hyp_tokens = hypothesis.lower().split()
        smooth = SmoothingFunction().method1
        return sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=smooth)
    return 0.0


def rouge_1(reference, hypothesis):
    if HAS_ROUGE:
        scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
        scores = scorer.score(reference, hypothesis)
        return scores['rouge1'].fmeasure
    return 0.0


def exact_match(reference, hypothesis):
    return reference.strip().lower() == hypothesis.strip().lower()


def token_f1(reference, hypothesis):
    if not HAS_BLEU and not HAS_ROUGE:
        return 0.0
    ref_tokens = set(reference.lower().split())
    hyp_tokens = set(hypothesis.lower().split())
    if not ref_tokens or not hyp_tokens:
        return 0.0
    intersection = len(ref_tokens & hyp_tokens)
    precision = intersection / len(hyp_tokens) if hyp_tokens else 0.0
    recall = intersection / len(ref_tokens) if ref_tokens else 0.0
    return compute_f1_score(precision, recall)


def cross_entropy(probabilities):
    """Compute cross-entropy from probability values."""
    total = 0
    for probability in probabilities:
        if probability <= 0:
            raise ValueError("Probabilities must be positive")
        total += -math.log(probability)
    return total / len(probabilities)


def perplexity(probabilities):
    """Compute perplexity from probability values."""
    ce = cross_entropy(probabilities)
    return math.exp(ce)


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
        f1_value = compute_f1_score(precision_value, recall_value)
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
