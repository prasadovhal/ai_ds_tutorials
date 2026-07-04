"""
Chapter 2 - Classical NLP Metrics
=================================
Main demonstration script that walks through ALL 17 classical NLP evaluation
metrics with explanations, formulas, intuition, and live examples.

Metrics covered:
  1.  Accuracy
  2.  Precision
  3.  Recall
  4.  F1 Score
  5.  Confusion Matrix
  6.  BLEU
  7.  ROUGE
  8.  METEOR
  9.  CIDEr
  10. BERTScore (simplified)
  11. BLEURT (simplified)
  12. MoverScore (simplified)
  13. Exact Match
  14. Token F1
  15. Perplexity
  16. Cross Entropy
  17. Calibration
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from dataset import (
    load_sample_data,
)

from evaluator import (
    # Classification metrics
    accuracy,
    precision_per_class,
    recall_per_class,
    f1_per_class,
    f1_micro,
    f1_macro,
    f1_weighted,
    confusion_matrix,
    render_confusion_matrix,
    # Text generation metrics
    bleu_n,
    brevity_penalty,
    bleu_score,
    corpus_bleu,
    rouge_n,
    rouge_l,
    rouge_scores,
    meteor_score,
    cider_score,
    bertscore_simplified,
    bleurt_simplified,
    moverscore_simplified,
    exact_match,
    exact_match_score,
    token_f1,
    # Language model metrics
    build_ngram_lm,
    compute_perplexity,
    cross_entropy,
    cross_entropy_from_labels,
    # Calibration
    calibration_analysis,
    render_calibration_diagram,
)


# ============================================================================
# UTILITY: Section formatting
# ============================================================================

def print_header(number, title, width=78):
    """Print a prominent section header."""
    print("\n" + "=" * width)
    print(f"  METRIC {number}: {title}")
    print("=" * width)


def print_subheader(text, width=78):
    """Print a sub-section header."""
    print(f"\n  --- {text} {'─' * max(1, width - len(text) - 8)}")


def print_wrapped(text, indent=4):
    """Print text with indentation, wrapping at word boundaries."""
    prefix = " " * indent
    words = text.split()
    line = prefix
    for word in words:
        if len(line) + len(word) + 1 > 78:
            print(line)
            line = prefix + word
        else:
            line = line + " " + word if line.strip() else prefix + word
    if line.strip():
        print(line)


# ============================================================================
# MAIN
# ============================================================================

def main():
    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    data = load_sample_data()
    questions = data["questions"]
    llm = data["simulated_llm_responses"]
    text_examples = data["text_generation_examples"]

    # Build ground truth and prediction lists
    ground_truths = [q["ground_truth"] for q in questions]

    good_preds = llm["good_model"]["predictions"]
    good_confs = llm["good_model"]["confidences"]

    med_preds = llm["mediocre_model"]["predictions"]
    med_confs = llm["mediocre_model"]["confidences"]

    poor_preds = llm["poor_model"]["predictions"]
    poor_confs = llm["poor_model"]["confidences"]

    overconf_preds = llm["overconfident_model"]["predictions"]
    overconf_confs = llm["overconfident_model"]["confidences"]

    # Reference / hypothesis pairs for text generation metrics
    references = [ex["reference"] for ex in text_examples]
    good_hyps = [ex["good_hypothesis"] for ex in text_examples]
    med_hyps = [ex["mediocre_hypothesis"] for ex in text_examples]
    poor_hyps = [ex["poor_hypothesis"] for ex in text_examples]

    # ------------------------------------------------------------------
    # Title
    # ------------------------------------------------------------------
    print("=" * 78)
    print("  CHAPTER 2: CLASSICAL NLP EVALUATION METRICS")
    print("  A Comprehensive Walk-Through of 17 Metrics")
    print("=" * 78)
    print()
    print_wrapped(
        "This chapter covers the foundational metrics used to evaluate NLP "
        "and LLM systems. We start with classification metrics (Accuracy, "
        "Precision, Recall, F1, Confusion Matrix), move to text generation "
        "metrics (BLEU, ROUGE, METEOR, CIDEr, BERTScore, BLEURT, MoverScore, "
        "Exact Match, Token F1), and finish with information-theoretic and "
        "probabilistic metrics (Perplexity, Cross Entropy, Calibration)."
    )
    print()
    print(f"    Dataset: {len(questions)} science MCQ questions")
    print(f"    Text examples: {len(text_examples)} reference/hypothesis pairs")
    print(f"    Models compared: good (90%), mediocre (60%), poor (30%), overconfident (50%)")

    # ======================================================================
    # METRIC 1: ACCURACY
    # ======================================================================
    print_header(1, "ACCURACY")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Accuracy answers the most basic question in evaluation: 'What "
        "fraction of the time did the model get it right?' It is the starting "
        "point for any classification or MCQ evaluation. However, it can be "
        "misleading on imbalanced datasets where always predicting the majority "
        "class yields high accuracy."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Imagine a 10-question quiz. If a student gets 7 right, their accuracy "
        "is 70%. Simple count of hits divided by total attempts. Like checking "
        "your exam score -- no partial credit, no nuance."
    )

    print_subheader("Formula")
    print("""
                  Number of correct predictions
    Accuracy = ------------------------------------
                  Total number of predictions

    Accuracy = (1/N) * SUM( I(y_i == y_hat_i) )

    where:
      N       = total predictions
      y_i     = ground truth label for sample i
      y_hat_i = predicted label for sample i
      I(...)  = indicator function (1 if true, 0 if false)
    """)

    print_subheader("Results on sample data")
    acc_good = accuracy(ground_truths, good_preds)
    acc_med = accuracy(ground_truths, med_preds)
    acc_poor = accuracy(ground_truths, poor_preds)
    acc_over = accuracy(ground_truths, overconf_preds)

    print(f"    Good model accuracy:          {acc_good:.2%}  ({acc_good:.4f})")
    print(f"    Mediocre model accuracy:      {acc_med:.2%}  ({acc_med:.4f})")
    print(f"    Poor model accuracy:          {acc_poor:.2%}  ({acc_poor:.4f})")
    print(f"    Overconfident model accuracy:  {acc_over:.2%}  ({acc_over:.4f})")

    print_subheader("ASCII Diagram")
    print("""
    Good model (10 questions):
    [C][C][C][C][C][C][C][C][C][X]   C=correct, X=wrong
     ^  ^  ^  ^  ^  ^  ^  ^  ^  ^
     D  B  E  D  C  E  A  D  A  C   (predictions match ground truth)
    Accuracy = 9/10 = 90% (by design, may vary with sample data)
    """)

    # Show per-question breakdown for good model
    print("    Per-question breakdown (good model):")
    for i, (gt, pred) in enumerate(zip(ground_truths, good_preds)):
        status = "CORRECT" if gt == pred else "WRONG  "
        print(f"      Q{i}: truth={gt}  pred={pred}  -> {status}")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Simplest metric to understand and communicate
      + Works for any number of classes
      + No hyperparameters

    Limitations:
      - Misleading on imbalanced datasets (e.g., 95% class A -> always predict A = 95%)
      - No distinction between types of errors (false positive vs false negative)
      - No partial credit for 'almost right' answers
    """)

    # ======================================================================
    # METRIC 2: PRECISION
    # ======================================================================
    print_header(2, "PRECISION")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Precision answers: 'When the model predicts class X, how often is "
        "it actually class X?' It measures the quality of positive predictions. "
        "High precision means few false alarms. This is critical when false "
        "positives are costly -- e.g., spam filters (flagging legitimate email "
        "as spam is annoying), or medical diagnosis (false cancer diagnosis "
        "causes unnecessary anxiety)."
    )

    print_subheader("Intuition")
    print_wrapped(
        "A sniper analogy: precision is like asking 'Of all the shots fired, "
        "how many hit the target?' A precise model does not cry wolf -- when "
        "it makes a claim, you can trust it."
    )

    print_subheader("Formula")
    print("""
                       True Positives (TP)
    Precision_C = --------------------------------
                  True Positives + False Positives

                      TP_C
    Precision_C = -----------
                  TP_C + FP_C

    where (for class C):
      TP_C = correctly predicted as C
      FP_C = incorrectly predicted as C (actually another class)
    """)

    print_subheader("Results on sample data")
    for model_name, preds in [("Good", good_preds), ("Mediocre", med_preds), ("Poor", poor_preds)]:
        prec = precision_per_class(ground_truths, preds)
        print(f"\n    {model_name} model precision per class:")
        for cls, val in sorted(prec.items()):
            bar = "#" * int(val * 20)
            print(f"      Class {cls}: {val:.4f}  {bar}")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Focuses on the quality of positive predictions
      + Essential when false positives are costly
      + Works per-class (can identify weak spots)

    Limitations:
      - Ignores false negatives (model could miss everything and have 100% precision)
      - Must be paired with recall for a complete picture
      - A model that predicts class C only once (and gets it right) has 100% precision
    """)

    # ======================================================================
    # METRIC 3: RECALL
    # ======================================================================
    print_header(3, "RECALL")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Recall answers: 'Of all the actual instances of class X, how many "
        "did the model find?' It measures completeness of detection. High "
        "recall means few missed cases. Critical when false negatives are "
        "dangerous -- e.g., disease screening (missing a cancer case is worse "
        "than a false alarm)."
    )

    print_subheader("Intuition")
    print_wrapped(
        "A search-and-rescue analogy: recall is like asking 'Of all the "
        "survivors in the area, how many did the team actually find?' You want "
        "to find everyone -- missing someone is the worst outcome."
    )

    print_subheader("Formula")
    print("""
                     True Positives (TP)
    Recall_C = --------------------------------
               True Positives + False Negatives

                    TP_C
    Recall_C = -----------
               TP_C + FN_C

    where (for class C):
      TP_C = correctly predicted as C
      FN_C = actually C but predicted as something else
    """)

    print_subheader("Results on sample data")
    for model_name, preds in [("Good", good_preds), ("Mediocre", med_preds), ("Poor", poor_preds)]:
        rec = recall_per_class(ground_truths, preds)
        print(f"\n    {model_name} model recall per class:")
        for cls, val in sorted(rec.items()):
            bar = "#" * int(val * 20)
            print(f"      Class {cls}: {val:.4f}  {bar}")

    print_subheader("Precision vs Recall Trade-off")
    print("""
    High Precision, Low Recall:         High Recall, Low Precision:
    Model is CONSERVATIVE               Model is AGGRESSIVE
    "I only speak when I'm sure"        "I flag everything just in case"

    +----------+                         +----------+
    |    TP    |  <- Few predictions     |  TP | FP |  <- Many predictions
    |          |     but accurate        |    |    |     catches everything
    +----------+                         +----+----+
    | FN | TN  |  <- Misses many         |   TN    |  <- Few misses
    +----+-----+                         +---------+
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Measures completeness of detection
      + Critical for safety-sensitive applications
      + Complements precision

    Limitations:
      - A model that predicts everything as class C has 100% recall for C
      - Must be paired with precision
      - Does not account for false positives
    """)

    # ======================================================================
    # METRIC 4: F1 SCORE
    # ======================================================================
    print_header(4, "F1 SCORE")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "F1 balances precision and recall into a single number using their "
        "harmonic mean. It solves the problem of trading off precision vs "
        "recall. The harmonic mean punishes extreme imbalance: if either "
        "precision or recall is low, F1 will be low."
    )

    print_subheader("Intuition")
    print_wrapped(
        "If precision is the 'sharpness' of a tool and recall is its "
        "'coverage', F1 is like asking 'overall, how good is this tool?' A "
        "surgeon's scalpel with 100% precision but 1% recall is useless. "
        "A bulldozer with 100% recall but 10% precision destroys everything. "
        "F1 demands both."
    )

    print_subheader("Formula")
    print("""
              2 * Precision * Recall
    F1 = ------------------------------
              Precision + Recall

    Variants:
      Micro F1:    Pool all TP, FP, FN globally -> one F1
                   (weights each SAMPLE equally)

      Macro F1:    F1 per class, then average
                   (weights each CLASS equally -- good for imbalanced data)

      Weighted F1: F1 per class, weighted by class support
                   (compromise between micro and macro)
    """)

    print_subheader("Results on sample data")
    for model_name, preds in [("Good", good_preds), ("Mediocre", med_preds), ("Poor", poor_preds)]:
        f1pc = f1_per_class(ground_truths, preds)
        f1mi = f1_micro(ground_truths, preds)
        f1ma = f1_macro(ground_truths, preds)
        f1w = f1_weighted(ground_truths, preds)

        print(f"\n    {model_name} model:")
        print(f"      Per-class F1:")
        for cls, val in sorted(f1pc.items()):
            bar = "#" * int(val * 20)
            print(f"        Class {cls}: {val:.4f}  {bar}")
        print(f"      Micro F1:    {f1mi:.4f}")
        print(f"      Macro F1:    {f1ma:.4f}")
        print(f"      Weighted F1: {f1w:.4f}")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Balances precision and recall in one number
      + Harmonic mean penalizes extreme values
      + Multiple variants for different needs (micro/macro/weighted)

    Limitations:
      - Assumes precision and recall are equally important (use F-beta for other weights)
      - Macro F1 can be unstable with few samples per class
      - Does not account for true negatives
    """)

    # ======================================================================
    # METRIC 5: CONFUSION MATRIX
    # ======================================================================
    print_header(5, "CONFUSION MATRIX")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "A confusion matrix shows the FULL picture of classification errors. "
        "While accuracy, precision, and recall are single numbers, the confusion "
        "matrix reveals exactly which classes are being confused with which. "
        "It answers: 'When the model gets it wrong, what does it predict instead?'"
    )

    print_subheader("Intuition")
    print_wrapped(
        "Think of a teacher grading student responses. The confusion matrix "
        "is like a chart showing: 'When the answer was A, how many students "
        "said A, B, C, D, or E?' The diagonal shows correct answers; "
        "off-diagonal cells show specific confusions."
    )

    print_subheader("Structure")
    print("""
                        PREDICTED
                   A    B    C    D    E
              +----+----+----+----+----+
    ACTUAL A  | TP |    |    |    |    |   <- diagonal = correct
           B  |    | TP |    |    |    |
           C  |    |    | TP |    |    |   off-diagonal = errors
           D  |    |    |    | TP |    |   (which class it was confused with)
           E  |    |    |    |    | TP |
              +----+----+----+----+----+
    """)

    print_subheader("Results on sample data")
    for model_name, preds in [("Good", good_preds), ("Mediocre", med_preds), ("Poor", poor_preds)]:
        cm = confusion_matrix(ground_truths, preds)
        print(f"\n    {model_name} model:")
        print(render_confusion_matrix(cm))
        print()

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Shows COMPLETE error patterns (not just a single number)
      + Reveals systematic confusions between specific classes
      + Foundation for computing all classification metrics

    Limitations:
      - Harder to compare across models (it's a table, not a number)
      - Grows as NxN with N classes (impractical for 1000+ classes)
      - Doesn't directly suggest what to fix
    """)

    # ======================================================================
    # METRIC 6: BLEU
    # ======================================================================
    print_header(6, "BLEU (Bilingual Evaluation Understudy)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "BLEU measures how much a generated text overlaps with a reference "
        "text at the n-gram level. Originally designed for machine translation, "
        "it became the first widely-used automatic metric for text generation. "
        "It is precision-oriented: it checks what fraction of the generated "
        "n-grams appear in the reference."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Imagine comparing a student's essay to a model answer. BLEU counts "
        "how many phrases (1-word, 2-word, 3-word, 4-word) from the student's "
        "essay also appear in the model answer. More shared phrases = higher "
        "BLEU. A short but accurate summary gets a brevity penalty."
    )

    print_subheader("Formula")
    print("""
    BLEU-N: precision for n-grams of size N

                   SUM( min(count_hyp(ngram), count_ref(ngram)) )
    BLEU-N = -------------------------------------------------------
                        SUM( count_hyp(ngram) )

    Combined BLEU = BP * exp( SUM( w_n * log(BLEU-n) ) )

    Brevity Penalty:
      BP = 1                        if |hyp| >= |ref|
      BP = exp(1 - |ref| / |hyp|)   if |hyp| < |ref|

    where:
      w_n   = weight for n-gram order (typically 1/4 each)
      |hyp| = hypothesis length in tokens
      |ref| = reference length in tokens
    """)

    print_subheader("Results on sample data")
    for i, ex in enumerate(text_examples[:3]):
        ref = ex["reference"]
        print(f"\n    Example {i+1}: {ref[:60]}...")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = bleu_score(ref, hyp)
            print(f"      {quality:10s}: BLEU={result['BLEU']:.4f}  "
                  f"(B1={result['BLEU-1']:.3f} B2={result['BLEU-2']:.3f} "
                  f"B3={result['BLEU-3']:.3f} B4={result['BLEU-4']:.3f} "
                  f"BP={result['brevity_penalty']:.3f})")

    # Corpus BLEU
    print("\n    Corpus-level BLEU (across all examples):")
    for quality, hyps in [("Good", good_hyps), ("Mediocre", med_hyps), ("Poor", poor_hyps)]:
        result = corpus_bleu(references, hyps)
        print(f"      {quality:10s}: corpus_BLEU={result['corpus_BLEU']:.4f}")

    print_subheader("ASCII Diagram")
    print("""
    Reference: "The cat sat on the mat"
    Hypothesis: "The cat on the mat sat"

    Unigrams (BLEU-1):
      Hyp: [the] [cat] [on] [the] [mat] [sat]
      Ref: [the] [cat] [sat] [on] [the] [mat]
      Match: 6/6 = 1.000

    Bigrams (BLEU-2):
      Hyp: [the cat] [cat on] [on the] [the mat] [mat sat]
      Ref: [the cat] [cat sat] [sat on] [on the] [the mat]
      Match: 3/5 = 0.600  ("cat on" and "mat sat" not in reference)
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Fast, deterministic, and reproducible
      + Correlates reasonably well with human judgment for translation
      + N-gram matching captures phrase-level quality

    Limitations:
      - Precision-only (ignores how much of reference is covered -> see ROUGE)
      - No semantic understanding (synonyms get zero credit)
      - Sentence-level BLEU is unreliable (designed for corpus-level)
      - Brevity penalty is crude
    """)

    # ======================================================================
    # METRIC 7: ROUGE
    # ======================================================================
    print_header(7, "ROUGE (Recall-Oriented Understudy for Gisting Evaluation)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "ROUGE is the recall counterpart to BLEU. While BLEU asks 'How much "
        "of the hypothesis is in the reference?' (precision), ROUGE asks "
        "'How much of the reference is captured in the hypothesis?' (recall). "
        "Designed for summarization evaluation where coverage of key content matters."
    )

    print_subheader("Intuition")
    print_wrapped(
        "If a teacher writes 10 key points, ROUGE checks how many the student "
        "mentioned. BLEU checks how many of the student's points are valid. "
        "ROUGE-L uses the longest common subsequence -- the longest chain of "
        "words that appear in the same order in both texts."
    )

    print_subheader("Formula")
    print("""
    ROUGE-N:
                     |overlapping n-grams|
      Recall    = ----------------------------
                     |reference n-grams|

                     |overlapping n-grams|
      Precision = ----------------------------
                     |hypothesis n-grams|

      F1 = 2 * Precision * Recall / (Precision + Recall)

    ROUGE-L:
      Based on Longest Common Subsequence (LCS):
      Recall    = LCS_length / |reference|
      Precision = LCS_length / |hypothesis|
      F1 = harmonic mean
    """)

    print_subheader("Results on sample data")
    for i, ex in enumerate(text_examples[:3]):
        ref = ex["reference"]
        print(f"\n    Example {i+1}: {ref[:60]}...")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = rouge_scores(ref, hyp)
            r1 = result["ROUGE-1"]
            r2 = result["ROUGE-2"]
            rl = result["ROUGE-L"]
            print(f"      {quality:10s}: "
                  f"R1-F1={r1['f1']:.3f}  R2-F1={r2['f1']:.3f}  RL-F1={rl['f1']:.3f}")

    print_subheader("BLEU vs ROUGE Comparison")
    print("""
    BLEU (Precision-focused)         ROUGE (Recall-focused)
    "How much of hypothesis          "How much of reference
     is in the reference?"            is in the hypothesis?"

    Best for: Translation            Best for: Summarization

    Hypothesis too SHORT:            Hypothesis too SHORT:
      BLEU might still be high         ROUGE will be low
      (what it says is correct)        (reference content is missing)

    Hypothesis too LONG:             Hypothesis too LONG:
      BLEU will drop                   ROUGE might still be high
      (added wrong n-grams)            (reference content is covered)
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Recall-focused: measures content coverage
      + ROUGE-L captures ordering without fixed n-gram size
      + Reports precision, recall, AND F1 (more complete than BLEU)

    Limitations:
      - Still based on surface-level overlap (no semantics)
      - Does not handle paraphrasing well
      - Multiple reference handling varies by implementation
    """)

    # ======================================================================
    # METRIC 8: METEOR
    # ======================================================================
    print_header(8, "METEOR (Metric for Evaluation of Translation with Explicit ORdering)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "METEOR addresses BLEU's key weakness: no credit for synonyms or "
        "word variations. It aligns words between reference and hypothesis "
        "using exact match, stemming, and synonym lookup. It also penalizes "
        "fragmented matches, rewarding fluent translations."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Imagine a teacher who gives credit not just for exact words but also "
        "for synonyms ('big' = 'large') and word forms ('running' = 'ran'). "
        "METEOR also checks if matching words appear in the same order -- "
        "a scrambled but word-perfect answer gets a penalty."
    )

    print_subheader("Formula")
    print("""
    Step 1: Align words (exact -> stem -> synonym matching)
    Step 2: Compute precision and recall from aligned word count
    Step 3: Compute F-mean (weighted harmonic mean, favoring recall):

                      Precision * Recall
      F_mean = -----------------------------------
               alpha * Precision + (1-alpha) * Recall

    Step 4: Apply fragmentation penalty:
      frag = chunks / matches
      penalty = gamma * frag^beta

      METEOR = F_mean * (1 - penalty)

    Default: alpha=0.9 (recall-heavy), beta=3.0, gamma=0.5
    """)

    print_subheader("Results on sample data")
    for i, ex in enumerate(text_examples[:3]):
        ref = ex["reference"]
        print(f"\n    Example {i+1}: {ref[:60]}...")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = meteor_score(ref, hyp)
            print(f"      {quality:10s}: METEOR={result['score']:.4f}  "
                  f"(P={result['precision']:.3f} R={result['recall']:.3f} "
                  f"F={result['f_mean']:.3f} chunks={result['chunks']} "
                  f"matches={result['matches']})")

    # Show match details for one example
    print("\n    Match details (Example 1, good hypothesis):")
    result = meteor_score(text_examples[0]["reference"], text_examples[0]["good_hypothesis"])
    for hyp_word, ref_word, match_type in result["match_details"][:12]:
        print(f"      '{hyp_word}' <-> '{ref_word}'  ({match_type})")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Handles synonyms and morphological variations
      + Fragmentation penalty rewards fluency
      + Better correlation with human judgments than BLEU (at sentence level)

    Limitations:
      - Requires synonym tables and stemmer (language-dependent)
      - Slower than BLEU due to alignment
      - Parameters (alpha, beta, gamma) need tuning per language
    """)

    # ======================================================================
    # METRIC 9: CIDEr
    # ======================================================================
    print_header(9, "CIDEr (Consensus-based Image Description Evaluation)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "CIDEr measures how well a generated caption matches the consensus "
        "among multiple reference captions. It uses TF-IDF weighting to "
        "emphasize informative n-grams (rare, distinctive words) over common "
        "ones. Designed for image captioning where multiple valid descriptions exist."
    )

    print_subheader("Intuition")
    print_wrapped(
        "If 5 people describe a photo and all say 'sunset over ocean', those "
        "words are the consensus. CIDEr rewards a hypothesis that captures "
        "this consensus. Common words like 'the' and 'is' get downweighted "
        "(low IDF), while distinctive words like 'sunset' get upweighted."
    )

    print_subheader("Formula")
    print("""
    TF-IDF weighted n-gram vectors:
      TF(ngram)  = count(ngram) / total_ngrams_in_doc
      IDF(ngram) = log( num_docs / doc_freq(ngram) )
      g_n(s)     = TF-IDF vector for sentence s at n-gram order n

    CIDEr_n = (1/M) * SUM_i( cosine_sim(g_n(hyp), g_n(ref_i)) )

    CIDEr = (1/N) * SUM_n( CIDEr_n )    (averaged over n-gram orders)

    Convention: multiply by 10 for scaling.
    """)

    print_subheader("Results on sample data")
    # Use all text examples as references for CIDEr (it needs multiple refs)
    cider_refs = [ex["reference"] for ex in text_examples[:3]]

    for i, ex in enumerate(text_examples[:3]):
        ref_list = [ex["reference"]]  # CIDEr typically uses multiple refs per image
        print(f"\n    Example {i+1}:")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = cider_score(ref_list, hyp)
            per_n_str = "  ".join(f"{k}={v:.3f}" for k, v in result["per_n"].items())
            print(f"      {quality:10s}: CIDEr={result['score']:.4f}  ({per_n_str})")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + TF-IDF weighting emphasizes important content words
      + Handles multiple references naturally (consensus-based)
      + Good correlation with human judgments for captioning

    Limitations:
      - Requires multiple references per example for best results
      - TF-IDF is computed on the test set (no external corpus)
      - Can overweight rare n-grams that happen to match
    """)

    # ======================================================================
    # METRIC 10: BERTScore
    # ======================================================================
    print_header(10, "BERTScore (Simplified)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "BERTScore addresses the fundamental limitation of all surface-level "
        "metrics: they cannot detect semantic similarity. 'The cat sat on the "
        "mat' and 'A feline rested on the rug' share meaning but few n-grams. "
        "BERTScore uses contextual embeddings from BERT to compute token-level "
        "similarity, capturing meaning beyond exact word overlap."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Instead of matching exact words, BERTScore asks: 'Do the words in "
        "the hypothesis have similar MEANINGS to words in the reference?' It "
        "uses BERT to understand each word in context, then finds the best "
        "semantic match for each word. Like having a bilingual translator "
        "judge similarity instead of a word-matching machine."
    )

    print_subheader("Formula")
    print("""
    Real BERTScore:
      1. ref_embeddings = BERT(reference)    # contextual vectors for each token
      2. hyp_embeddings = BERT(hypothesis)

      Precision = (1/|hyp|) * SUM_h( max_r( cosine_sim(h, r) ) )
      Recall    = (1/|ref|) * SUM_r( max_h( cosine_sim(r, h) ) )
      F1        = 2 * P * R / (P + R)

    This demo uses character n-gram overlap as a proxy for BERT embeddings.
    """)

    print_subheader("Results on sample data")
    for i, ex in enumerate(text_examples[:3]):
        ref = ex["reference"]
        print(f"\n    Example {i+1}: {ref[:60]}...")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = bertscore_simplified(ref, hyp)
            print(f"      {quality:10s}: F1={result['f1']:.4f}  "
                  f"(P={result['precision']:.3f} R={result['recall']:.3f})")

    print(f"\n    Note: {result['note']}")

    print_subheader("Architecture Diagram")
    print("""
                    Reference text
                         |
                    [Tokenizer]
                         |
                   [BERT Encoder]
                         |
              [ref_embed_1, ref_embed_2, ..., ref_embed_m]
                         |
                    Greedy matching ---+
                    (max cosine sim)   |
                         |             |
              [hyp_embed_1, hyp_embed_2, ..., hyp_embed_n]
                         |
                   [BERT Encoder]
                         |
                    [Tokenizer]
                         |
                    Hypothesis text

              Precision = avg(max match for each hyp token)
              Recall    = avg(max match for each ref token)
              F1        = harmonic mean
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Captures semantic similarity (synonyms, paraphrases)
      + Contextual (same word in different contexts gets different embeddings)
      + Strong correlation with human judgments across tasks

    Limitations:
      - Requires GPU for fast inference (BERT is large)
      - Not interpretable (why did two tokens get high similarity?)
      - Depends on the BERT model used (different models -> different scores)
      - Our simplified version uses character n-grams, not actual BERT
    """)

    # ======================================================================
    # METRIC 11: BLEURT
    # ======================================================================
    print_header(11, "BLEURT (BERT-based Learned Evaluation Understudy for Text)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "BLEURT goes beyond BERTScore by LEARNING what makes text quality "
        "good. Instead of using a fixed similarity formula, BLEURT fine-tunes "
        "BERT on human quality judgments. The model learns to predict human "
        "scores directly, capturing nuances that no handcrafted formula can."
    )

    print_subheader("Intuition")
    print_wrapped(
        "BERTScore is like a dictionary that checks if words mean the same "
        "thing. BLEURT is like a trained human judge who has read thousands "
        "of evaluations and learned what constitutes good text. The judge "
        "considers grammar, coherence, factuality, and more -- all implicitly."
    )

    print_subheader("Formula (Architecture)")
    print("""
    Training pipeline:
      1. Pre-train BERT (language modeling)
      2. Pre-train on synthetic tasks:
         - Random word drops / insertions
         - Back-translation pairs
         - Predict BLEU/ROUGE from pairs (warm-up)
      3. Fine-tune on human quality judgments (WMT ratings)

    Inference:
      Reference ──> [Tokenizer] ──>
                                     [BERT Encoder] ──> [Regression Head] ──> Score
      Hypothesis -> [Tokenizer] ──>

    Our simplified version combines: token F1, length penalty,
    bigram precision, and order preservation (LCS-based).
    """)

    print_subheader("Results on sample data")
    for i, ex in enumerate(text_examples[:3]):
        ref = ex["reference"]
        print(f"\n    Example {i+1}: {ref[:60]}...")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = bleurt_simplified(ref, hyp)
            feats = result["features"]
            print(f"      {quality:10s}: BLEURT={result['score']:.4f}  "
                  f"(tok_f1={feats['token_f1']:.3f} "
                  f"len_pen={feats['length_penalty']:.3f} "
                  f"bigram={feats['bigram_precision']:.3f} "
                  f"order={feats['order_preservation']:.3f})")

    print(f"\n    Note: {result['note']}")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Learns from human judgments (captures subtle quality aspects)
      + Single score output (easy to use)
      + Pre-training on synthetic data makes it robust

    Limitations:
      - Requires downloading a large checkpoint
      - Quality depends on the training data (biased toward WMT)
      - Not interpretable (black-box regression)
      - Expensive to compute at scale
    """)

    # ======================================================================
    # METRIC 12: MoverScore
    # ======================================================================
    print_header(12, "MoverScore (Word Mover's Distance)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "MoverScore frames text similarity as an optimal transport problem: "
        "What is the minimum 'effort' needed to transform the hypothesis "
        "word distribution into the reference word distribution? It uses "
        "BERT embeddings as the space and Earth Mover's Distance (Wasserstein "
        "distance) as the transport cost."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Imagine you have piles of dirt (hypothesis words) and holes to fill "
        "(reference words). Each word has a position in meaning-space. "
        "MoverScore is the minimum total distance you need to 'move' the dirt "
        "to fill all the holes. Similar texts require less movement."
    )

    print_subheader("Formula")
    print("""
    Word Mover's Distance (WMD):
      min SUM( T_ij * c(w_i, w_j) )

    subject to:
      SUM_j(T_ij) = d_i   (supply constraint: each hypothesis word is fully moved)
      SUM_i(T_ij) = d_j   (demand constraint: each reference word is fully filled)

    where:
      T_ij   = amount of word i transported to word j
      c(i,j) = 1 - cosine_sim(embedding_i, embedding_j)
      d_i    = weight of word i (usually 1/|text|)

    MoverScore = 1 - normalized_WMD

    Our simplified version uses edit distance instead of embedding distance.
    """)

    print_subheader("Results on sample data")
    for i, ex in enumerate(text_examples[:3]):
        ref = ex["reference"]
        print(f"\n    Example {i+1}: {ref[:60]}...")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = moverscore_simplified(ref, hyp)
            print(f"      {quality:10s}: MoverScore={result['score']:.4f}  "
                  f"(avg_dist={result['avg_distance']:.3f})")

    # Show transportation plan for one example
    result = moverscore_simplified(text_examples[0]["reference"],
                                   text_examples[0]["good_hypothesis"])
    print("\n    Transportation plan (Example 1, good hypothesis):")
    print("      Hypothesis word  ->  Reference word  (distance)")
    for hw, rw, dist in result["top_matches"]:
        arrow = "====" if dist == 0.0 else "--->" if dist < 0.3 else "..>>"
        print(f"      {hw:15s}  {arrow}  {rw:15s}  ({dist:.3f})")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Captures semantic similarity through optimal transport
      + Handles reordering naturally (no n-gram constraint)
      + Elegant mathematical framework

    Limitations:
      - Computationally expensive (optimal transport is O(n^3))
      - Requires good word embeddings (BERT or similar)
      - Our simplified version uses edit distance, not real embeddings
    """)

    # ======================================================================
    # METRIC 13: EXACT MATCH
    # ======================================================================
    print_header(13, "EXACT MATCH")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Exact Match (EM) is the strictest text evaluation metric: the "
        "prediction must be EXACTLY the same as the reference. Used in "
        "extractive QA (SQuAD) where the model must extract the exact span "
        "from the passage. No partial credit -- either perfect or zero."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Like a password check: either it matches exactly, or it is wrong. "
        "'New York' and 'new york' match if we normalize case. "
        "'New York City' and 'New York' do NOT match. Simple but strict."
    )

    print_subheader("Formula")
    print("""
    EM(ref, hyp) = 1  if normalize(ref) == normalize(hyp)
                   0  otherwise

    Normalization (optional): lowercase + strip whitespace

    EM_score = (1/N) * SUM( EM(ref_i, hyp_i) )
    """)

    print_subheader("Results on sample data")
    em_pairs = [
        ("The Roche limit", "The Roche limit", "Exact match"),
        ("The Roche limit", "the roche limit", "Case difference"),
        ("The Roche limit", "Roche limit", "Missing word"),
        ("42", "42", "Number match"),
        ("New York City", "New York", "Partial match"),
        ("Paris", "paris, france", "Extra content"),
    ]

    print("    Pair comparisons:")
    for ref, hyp, description in em_pairs:
        result = exact_match(ref, hyp)
        status = "MATCH" if result["match"] else "NO MATCH"
        print(f"      '{ref}' vs '{hyp}'")
        print(f"        -> {status}  (score={result['score']:.0f})  [{description}]")

    # Corpus-level EM
    em_refs = [ex["reference"] for ex in text_examples[:3]]
    em_good = [ex["good_hypothesis"] for ex in text_examples[:3]]
    em_score = exact_match_score(em_refs, em_good)
    print(f"\n    Corpus EM (good hyps vs refs): {em_score:.2%}")
    print("    (Expected 0% -- paraphrased text will not match exactly)")

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Unambiguous: no tunable parameters
      + Fast to compute
      + Perfect for factoid QA with single correct answer

    Limitations:
      - No partial credit ("Barack Obama" vs "Obama" = 0)
      - Sensitive to formatting, punctuation, articles
      - Cannot handle valid paraphrases or alternative phrasings
    """)

    # ======================================================================
    # METRIC 14: TOKEN F1
    # ======================================================================
    print_header(14, "TOKEN F1")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Token F1 gives partial credit for overlapping tokens, complementing "
        "Exact Match. In extractive QA (SQuAD), if the reference is 'Barack "
        "Obama' and the prediction is 'President Barack Obama', Exact Match "
        "gives 0 but Token F1 gives credit for the two shared tokens."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Like a teacher grading a fill-in-the-blank with partial credit. "
        "If the answer is 3 words and the student gets 2 right, they deserve "
        "some points. Token F1 counts shared words, then computes the harmonic "
        "mean of precision and recall at the token level."
    )

    print_subheader("Formula")
    print("""
    common_tokens = tokens shared between reference and hypothesis
                    (using minimum count for repeated tokens)

                   |common_tokens|
    Precision = ----------------------
                |hypothesis_tokens|

                   |common_tokens|
    Recall    = ----------------------
                |reference_tokens|

    F1 = 2 * Precision * Recall / (Precision + Recall)
    """)

    print_subheader("Results on sample data")
    tf1_pairs = [
        ("The Roche limit is the distance", "The Roche limit is the distance"),
        ("The Roche limit is the distance", "the Roche limit distance"),
        ("The Roche limit is the distance", "Something completely different"),
        ("Barack Obama was the president", "President Barack Obama"),
        ("machine learning is a subset of artificial intelligence",
         "machine learning is part of AI"),
    ]

    print("    Pair comparisons:")
    for ref, hyp in tf1_pairs:
        result = token_f1(ref, hyp)
        print(f"\n      Reference:  '{ref}'")
        print(f"      Hypothesis: '{hyp}'")
        print(f"      -> F1={result['f1']:.4f}  P={result['precision']:.4f}  "
              f"R={result['recall']:.4f}  "
              f"(common={result['common_tokens']}/{result['reference_length']})")

    # Compare with text generation examples
    print("\n    Text generation examples:")
    for i, ex in enumerate(text_examples[:3]):
        ref = ex["reference"]
        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = token_f1(ref, hyp)
            print(f"      Ex{i+1} {quality:8s}: Token-F1={result['f1']:.4f}")

    print_subheader("Exact Match vs Token F1")
    print("""
    Example: Reference = "Barack Obama"

    Prediction          EM    Token-F1
    ------------------- ----  --------
    "Barack Obama"      1.00    1.00
    "Obama"             0.00    0.67
    "President Obama"   0.00    0.67
    "Barack"            0.00    0.67
    "Donald Trump"      0.00    0.00

    Token F1 provides a smoother, more informative signal than EM.
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Gives partial credit (unlike Exact Match)
      + Simple and fast
      + Standard in extractive QA evaluation (SQuAD)

    Limitations:
      - Bag-of-words: ignores word order
      - No semantic understanding (synonyms get zero credit)
      - Treats all tokens equally (function words = content words)
    """)

    # ======================================================================
    # METRIC 15: PERPLEXITY
    # ======================================================================
    print_header(15, "PERPLEXITY")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Perplexity measures how 'surprised' a language model is by a text. "
        "It is the standard evaluation metric for language models themselves "
        "(not for text generation quality). Lower perplexity means the model "
        "assigns higher probability to the text -- it expected what it saw."
    )

    print_subheader("Intuition")
    print_wrapped(
        "If perplexity is 10, the model is as confused as if it had to choose "
        "randomly among 10 equally likely options at each step. A perplexity "
        "of 1 means perfect prediction (zero surprise). A perplexity of "
        "|vocabulary| means uniform random guessing."
    )

    print_subheader("Formula")
    print("""
    PP(W) = exp( -(1/N) * SUM( log P(w_i | context) ) )

    Equivalently: PP(W) = P(w_1, w_2, ..., w_N) ^ (-1/N)

    where:
      W     = the text (sequence of words)
      N     = number of words
      P(w_i | context) = probability of word i given its context

    Relationship to Cross Entropy:
      PP = exp(H)  = 2^(H / ln2)
      where H = cross entropy of the language model
    """)

    print_subheader("Results on sample data")
    # Build a simple language model from references
    corpus = [ex["reference"] for ex in text_examples]
    lm = build_ngram_lm(corpus, n=2)

    print(f"    Language model: bigram (n=2), trained on {len(corpus)} reference texts")
    print(f"    Vocabulary size: {lm['vocab_size']}")

    print("\n    Perplexity on different texts:")
    test_texts = [
        ("Reference text (in-domain)", text_examples[0]["reference"]),
        ("Good hypothesis", text_examples[0]["good_hypothesis"]),
        ("Mediocre hypothesis", text_examples[0]["mediocre_hypothesis"]),
        ("Poor hypothesis", text_examples[0]["poor_hypothesis"]),
        ("Random sentence", "The quick brown fox jumps over the lazy dog"),
    ]

    for label, text in test_texts:
        result = compute_perplexity(text, lm)
        print(f"      {label:30s}: PP={result['perplexity']:10.2f}  "
              f"(tokens={result['num_tokens']})")

    print_subheader("ASCII Diagram")
    print("""
    Perplexity Scale:
    |
    |  1.0 -------- Perfect prediction (impossible in practice)
    |
    |  ~10 -------- Excellent LM (GPT-4 on clean English)
    |
    |  ~50 -------- Good LM
    |
    | ~100 -------- Reasonable LM
    |
    | ~500 -------- Weak LM
    |
    |  |V| -------- Random guessing (V = vocabulary size)
    |
    Lower is better
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Standard metric for language model evaluation
      + Mathematically principled (information theory)
      + Comparable across different texts with same model

    Limitations:
      - Only measures the model, not generation quality
      - Sensitive to vocabulary size and tokenization
      - A model can have low perplexity but generate boring, repetitive text
      - Not comparable across models with different vocabularies
    """)

    # ======================================================================
    # METRIC 16: CROSS ENTROPY
    # ======================================================================
    print_header(16, "CROSS ENTROPY")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Cross entropy measures the gap between two probability distributions: "
        "the true labels and the model's predicted probabilities. It is the "
        "standard loss function for training classifiers and language models. "
        "Lower cross entropy means the model's probability estimates are "
        "closer to the truth."
    )

    print_subheader("Intuition")
    print_wrapped(
        "Imagine you need to design a code to transmit messages. Cross entropy "
        "is the average number of bits you need if you design your code based "
        "on the model's predictions (q) but the actual data follows a different "
        "distribution (p). If q matches p perfectly, cross entropy equals the "
        "entropy of p (minimum possible)."
    )

    print_subheader("Formula")
    print("""
    General form:
      H(p, q) = -SUM( p(x) * log(q(x)) )

    Classification (one-hot labels):
      CE = -(1/N) * SUM( log( q(correct_class_i) ) )

    where:
      p(x) = true distribution (usually one-hot for classification)
      q(x) = predicted probability distribution
      q(correct_class_i) = model's confidence on the correct answer

    Relationship to Perplexity:  PP = exp(CE)
    """)

    print_subheader("Results on sample data")

    # Distribution-level cross entropy
    print("    Distribution-level cross entropy examples:")
    distributions = [
        ("Perfect match", [0.2, 0.3, 0.5], [0.2, 0.3, 0.5]),
        ("Close match", [0.2, 0.3, 0.5], [0.25, 0.25, 0.5]),
        ("Bad match", [0.2, 0.3, 0.5], [0.5, 0.4, 0.1]),
        ("One-hot true, confident pred", [0, 0, 1.0], [0.05, 0.05, 0.9]),
        ("One-hot true, uncertain pred", [0, 0, 1.0], [0.3, 0.3, 0.4]),
    ]

    for label, p, q in distributions:
        ce = cross_entropy(p, q)
        print(f"      {label:35s}: CE = {ce:.4f}")
        print(f"        p={p}  q={q}")

    # Classification cross entropy from labels
    print("\n    Classification cross entropy (from model predictions):")
    for model_name, preds, confs in [
        ("Good", good_preds, good_confs),
        ("Mediocre", med_preds, med_confs),
        ("Poor", poor_preds, poor_confs),
        ("Overconfident", overconf_preds, overconf_confs),
    ]:
        result = cross_entropy_from_labels(ground_truths, preds, confs)
        print(f"      {model_name:15s}: CE = {result['cross_entropy']:.4f}  "
              f"(N={result['num_samples']})")

    print_subheader("Cross Entropy vs KL Divergence")
    print("""
    H(p, q) = H(p) + D_KL(p || q)

    Cross Entropy = Entropy of true distribution
                    + KL Divergence (extra bits due to using q instead of p)

    When p is fixed (which it usually is in training):
      Minimizing Cross Entropy == Minimizing KL Divergence
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Standard training loss (gradient-friendly)
      + Penalizes confident wrong predictions heavily (log scale)
      + Mathematically principled (information theory)
      + Directly related to perplexity (PP = exp(CE))

    Limitations:
      - Requires probability estimates (not just predictions)
      - Sensitive to calibration (overconfident model gets punished)
      - Not bounded (unlike accuracy which is 0-1)
      - Hard to interpret in isolation (what is "good" CE?)
    """)

    # ======================================================================
    # METRIC 17: CALIBRATION
    # ======================================================================
    print_header(17, "CALIBRATION (Expected Calibration Error)")

    print_subheader("What problem does it solve?")
    print_wrapped(
        "Calibration measures whether a model's confidence scores match "
        "reality. When a model says '80% confident', is it actually correct "
        "80% of the time? A well-calibrated model's confidence is trustworthy. "
        "This is essential for decision-making systems where confidence "
        "thresholds determine actions."
    )

    print_subheader("Intuition")
    print_wrapped(
        "A weather forecaster who says '70% chance of rain' should be right "
        "about 7 out of 10 times they make that prediction. If it rains "
        "only 3/10 times, they are overconfident. If it rains 9/10 times, "
        "they are underconfident. ECE measures this overall miscalibration."
    )

    print_subheader("Formula")
    print("""
    Expected Calibration Error (ECE):
      1. Bin predictions by confidence level (e.g., 10 bins: 0-0.1, 0.1-0.2, ...)
      2. For each bin:
           accuracy_b   = fraction of correct predictions in that bin
           confidence_b = average confidence in that bin
      3. ECE = SUM( (|bin_b| / N) * |accuracy_b - confidence_b| )

    Perfect calibration: ECE = 0  (accuracy == confidence in every bin)

    Reliability Diagram:
      Plot accuracy vs confidence for each bin.
      Perfect calibration = diagonal line.
    """)

    print_subheader("Results on sample data")
    for model_name, preds, confs in [
        ("Good model", good_preds, good_confs),
        ("Mediocre model", med_preds, med_confs),
        ("Poor model", poor_preds, poor_confs),
        ("Overconfident model", overconf_preds, overconf_confs),
    ]:
        cal = calibration_analysis(ground_truths, preds, confs, n_bins=5)
        print(f"\n    {model_name}:")
        print(f"      ECE = {cal['ece']:.4f}")
        print(f"      Overall accuracy:    {cal['overall_accuracy']:.4f}")
        print(f"      Average confidence:  {cal['avg_confidence']:.4f}")
        print(f"      Overconfident? {'YES' if cal['overconfident'] else 'NO'}")

    # Detailed calibration for overconfident model
    print("\n    Detailed calibration analysis (Overconfident model):")
    cal_over = calibration_analysis(ground_truths, overconf_preds, overconf_confs, n_bins=5)
    print(render_calibration_diagram(cal_over))

    print("\n    Detailed calibration analysis (Good model):")
    cal_good = calibration_analysis(ground_truths, good_preds, good_confs, n_bins=5)
    print(render_calibration_diagram(cal_good))

    print_subheader("Calibration Diagram Explanation")
    print("""
    Perfect Calibration (ECE=0):     Overconfident Model:
    Acc                              Acc
    1.0|        /                    1.0|        .
       |      /                        |      .
       |    /   <- y=x line            |    .    <- below diagonal
       |  /                            |  .  /
       |/                              |./  /
    ---+---------> Conf                +---------> Conf
       0       1.0                     0       1.0

    Points below the diagonal = overconfident (confidence > accuracy)
    Points above the diagonal = underconfident (accuracy > confidence)
    """)

    print_subheader("Advantages & Limitations")
    print("""
    Advantages:
      + Measures trustworthiness of probability estimates
      + Essential for decision-making systems
      + ECE is a single interpretable number
      + Bin-level analysis reveals where miscalibration occurs

    Limitations:
      - Sensitive to the number of bins
      - Requires large samples for reliable bin statistics
      - ECE can be gamed (post-hoc temperature scaling fixes ECE but not the model)
      - Does not measure discrimination (a constant predictor can be well-calibrated)
    """)

    # ======================================================================
    # SUMMARY COMPARISON TABLE
    # ======================================================================
    print("\n" + "=" * 78)
    print("  SUMMARY: ALL 17 METRICS AT A GLANCE")
    print("=" * 78)

    print("""
    +-----+-------------------+------------+-----------+------------------------+
    | #   | Metric            | Type       | Range     | Best For               |
    +-----+-------------------+------------+-----------+------------------------+
    |  1  | Accuracy          | Classif.   | [0, 1]    | Balanced datasets      |
    |  2  | Precision         | Classif.   | [0, 1]    | Low false positive cost |
    |  3  | Recall            | Classif.   | [0, 1]    | Low false negative cost |
    |  4  | F1 Score          | Classif.   | [0, 1]    | Balancing P & R        |
    |  5  | Confusion Matrix  | Classif.   | counts    | Error analysis         |
    +-----+-------------------+------------+-----------+------------------------+
    |  6  | BLEU              | Generation | [0, 1]    | Machine translation    |
    |  7  | ROUGE             | Generation | [0, 1]    | Summarization          |
    |  8  | METEOR            | Generation | [0, 1]    | Translation (semantic) |
    |  9  | CIDEr             | Generation | [0, 10]   | Image captioning       |
    | 10  | BERTScore         | Generation | [0, 1]    | Semantic similarity    |
    | 11  | BLEURT            | Generation | [-1, 1]*  | Learned quality        |
    | 12  | MoverScore        | Generation | [0, 1]    | Optimal transport sim  |
    | 13  | Exact Match       | Extractive | {0, 1}    | Factoid QA (SQuAD)    |
    | 14  | Token F1          | Extractive | [0, 1]    | Extractive QA (SQuAD) |
    +-----+-------------------+------------+-----------+------------------------+
    | 15  | Perplexity        | LM Eval    | [1, inf)  | Language model quality |
    | 16  | Cross Entropy     | LM / Loss  | [0, inf)  | Training loss          |
    | 17  | Calibration (ECE) | Probabilit.| [0, 1]    | Confidence reliability |
    +-----+-------------------+------------+-----------+------------------------+

    * BLEURT range depends on implementation; simplified version is [0, 1].
    """)

    # Metric results comparison table
    print("    Model performance comparison (selected metrics):")
    print("    " + "-" * 70)
    print(f"    {'Metric':<20s} {'Good':>10s} {'Mediocre':>10s} {'Poor':>10s} {'Overconf':>10s}")
    print("    " + "-" * 70)

    # Accuracy
    print(f"    {'Accuracy':<20s} "
          f"{accuracy(ground_truths, good_preds):>10.4f} "
          f"{accuracy(ground_truths, med_preds):>10.4f} "
          f"{accuracy(ground_truths, poor_preds):>10.4f} "
          f"{accuracy(ground_truths, overconf_preds):>10.4f}")

    # F1 Macro
    print(f"    {'F1 (macro)':<20s} "
          f"{f1_macro(ground_truths, good_preds):>10.4f} "
          f"{f1_macro(ground_truths, med_preds):>10.4f} "
          f"{f1_macro(ground_truths, poor_preds):>10.4f} "
          f"{f1_macro(ground_truths, overconf_preds):>10.4f}")

    # Cross Entropy
    ce_good = cross_entropy_from_labels(ground_truths, good_preds, good_confs)
    ce_med = cross_entropy_from_labels(ground_truths, med_preds, med_confs)
    ce_poor = cross_entropy_from_labels(ground_truths, poor_preds, poor_confs)
    ce_over = cross_entropy_from_labels(ground_truths, overconf_preds, overconf_confs)
    print(f"    {'Cross Entropy':<20s} "
          f"{ce_good['cross_entropy']:>10.4f} "
          f"{ce_med['cross_entropy']:>10.4f} "
          f"{ce_poor['cross_entropy']:>10.4f} "
          f"{ce_over['cross_entropy']:>10.4f}")

    # ECE
    cal_g = calibration_analysis(ground_truths, good_preds, good_confs)
    cal_m = calibration_analysis(ground_truths, med_preds, med_confs)
    cal_p = calibration_analysis(ground_truths, poor_preds, poor_confs)
    cal_o = calibration_analysis(ground_truths, overconf_preds, overconf_confs)
    print(f"    {'ECE (calibration)':<20s} "
          f"{cal_g['ece']:>10.4f} "
          f"{cal_m['ece']:>10.4f} "
          f"{cal_p['ece']:>10.4f} "
          f"{cal_o['ece']:>10.4f}")

    print("    " + "-" * 70)

    # Text generation metrics comparison (first example)
    ref = text_examples[0]["reference"]
    print(f"\n    Text generation metrics (Example 1):")
    print("    " + "-" * 55)
    print(f"    {'Metric':<20s} {'Good':>10s} {'Mediocre':>10s} {'Poor':>10s}")
    print("    " + "-" * 55)

    for metric_name, metric_fn in [
        ("BLEU", lambda r, h: bleu_score(r, h)["BLEU"]),
        ("ROUGE-1 F1", lambda r, h: rouge_n(r, h, 1)["f1"]),
        ("ROUGE-L F1", lambda r, h: rouge_l(r, h)["f1"]),
        ("METEOR", lambda r, h: meteor_score(r, h)["score"]),
        ("BERTScore F1", lambda r, h: bertscore_simplified(r, h)["f1"]),
        ("BLEURT", lambda r, h: bleurt_simplified(r, h)["score"]),
        ("MoverScore", lambda r, h: moverscore_simplified(r, h)["score"]),
        ("Token F1", lambda r, h: token_f1(r, h)["f1"]),
    ]:
        g = metric_fn(ref, text_examples[0]["good_hypothesis"])
        m = metric_fn(ref, text_examples[0]["mediocre_hypothesis"])
        p = metric_fn(ref, text_examples[0]["poor_hypothesis"])
        print(f"    {metric_name:<20s} {g:>10.4f} {m:>10.4f} {p:>10.4f}")

    print("    " + "-" * 55)

    # ======================================================================
    # INTERVIEW QUESTIONS
    # ======================================================================
    print("\n" + "=" * 78)
    print("  INTERVIEW QUESTIONS & ANSWERS")
    print("=" * 78)

    questions_and_answers = [
        (
            "Q1: Why is accuracy alone insufficient for evaluating an LLM on an "
            "imbalanced dataset?",
            "A1: On an imbalanced dataset (e.g., 95% class A, 5% class B), a "
            "model that always predicts class A achieves 95% accuracy without "
            "learning anything useful. Precision, recall, and F1 (especially "
            "macro-averaged) reveal performance on minority classes that "
            "accuracy hides."
        ),
        (
            "Q2: What is the key difference between BLEU and ROUGE?",
            "A2: BLEU is precision-oriented (what fraction of hypothesis "
            "n-grams appear in the reference), while ROUGE is recall-oriented "
            "(what fraction of reference n-grams appear in the hypothesis). "
            "BLEU penalizes short outputs (brevity penalty); ROUGE penalizes "
            "missing content. BLEU is standard for translation; ROUGE for "
            "summarization."
        ),
        (
            "Q3: Why does METEOR often correlate better with human judgment "
            "than BLEU?",
            "A3: METEOR handles synonyms (large=big), stemming (running=ran), "
            "and word order (fragmentation penalty). BLEU only does exact "
            "n-gram matching. METEOR also computes both precision and recall "
            "with a recall-weighted F-mean, giving a more balanced assessment."
        ),
        (
            "Q4: What is the relationship between cross entropy and perplexity?",
            "A4: Perplexity = exp(Cross Entropy). If a language model has "
            "cross entropy H on a text, its perplexity is e^H. Minimizing "
            "cross entropy during training directly minimizes perplexity. "
            "A cross entropy of 0 gives perplexity 1 (perfect prediction)."
        ),
        (
            "Q5: Why is calibration important for LLM deployment?",
            "A5: Calibration ensures that confidence scores are meaningful. "
            "In production, systems often use confidence thresholds to decide "
            "when to trust the model vs. escalate to a human. If a model is "
            "overconfident (says 95% confident but is only right 60% of the "
            "time), these thresholds become unreliable, leading to silent "
            "failures."
        ),
        (
            "Q6: How does BERTScore improve over surface-level metrics like "
            "BLEU and ROUGE?",
            "A6: BERTScore uses contextual embeddings from BERT to compute "
            "token-level cosine similarity instead of exact n-gram matching. "
            "This means semantically similar words (synonyms, paraphrases) "
            "receive high similarity scores even without exact string overlap. "
            "It captures meaning, not just surface form."
        ),
        (
            "Q7: In SQuAD evaluation, why are both Exact Match and Token F1 "
            "reported?",
            "A7: Exact Match is strict (all or nothing) and measures how "
            "often the model gets the answer perfectly right. Token F1 gives "
            "partial credit for overlapping tokens. Together, they show both "
            "the model's precision in extracting exact spans AND its ability "
            "to identify relevant content even when the boundaries are slightly off."
        ),
        (
            "Q8: What is the F-beta score and when would you use F2 vs F0.5?",
            "A8: F-beta = (1+beta^2) * (P*R) / (beta^2*P + R). F2 (beta=2) "
            "weights recall 4x more than precision -- use when missing positives "
            "is costly (disease screening). F0.5 (beta=0.5) weights precision "
            "4x more than recall -- use when false positives are costly "
            "(spam detection). F1 (beta=1) weights them equally."
        ),
        (
            "Q9: What is the difference between micro and macro F1?",
            "A9: Micro F1 pools all true positives, false positives, and "
            "false negatives globally before computing F1. It weights each "
            "SAMPLE equally, so majority classes dominate. Macro F1 computes "
            "F1 per class and averages them, weighting each CLASS equally. "
            "Use macro F1 when minority class performance matters."
        ),
        (
            "Q10: Can a model have low perplexity but still generate poor text?",
            "A10: Yes. Perplexity measures how well the model PREDICTS text, "
            "not how well it GENERATES text. A model can memorize training data "
            "(low perplexity) but produce repetitive, generic, or factually "
            "incorrect text when sampling. Perplexity also does not capture "
            "diversity, coherence, or factual correctness of generated text."
        ),
    ]

    for q, a in questions_and_answers:
        print()
        print_wrapped(q)
        print_wrapped(a)

    # ======================================================================
    # CLOSING
    # ======================================================================
    print("\n" + "=" * 78)
    print("  END OF CHAPTER 2: CLASSICAL NLP EVALUATION METRICS")
    print("=" * 78)
    print()
    print_wrapped(
        "Key takeaway: No single metric tells the whole story. Classification "
        "tasks need precision, recall, and F1 alongside accuracy. Text "
        "generation tasks benefit from combining surface-level metrics (BLEU, "
        "ROUGE) with semantic metrics (BERTScore, BLEURT). And probabilistic "
        "metrics (perplexity, cross entropy, calibration) are essential for "
        "understanding model confidence and language modeling quality."
    )
    print()
    print("    Next: Chapter 3 - Modern LLM Evaluation Frameworks")
    print()


if __name__ == "__main__":
    main()
