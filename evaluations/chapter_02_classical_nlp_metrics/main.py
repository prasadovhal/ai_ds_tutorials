"""
Chapter 2 - Classical NLP Metrics
=================================
Main demonstration script that runs ALL 17 classical NLP evaluation
metrics with live examples on sample data.

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
    print(f"    Dataset: {len(questions)} science MCQ questions")
    print(f"    Text examples: {len(text_examples)} reference/hypothesis pairs")
    print(f"    Models compared: good (90%), mediocre (60%), poor (30%), overconfident (50%)")

    # ======================================================================
    # METRIC 1: ACCURACY
    # ======================================================================
    print_header(1, "ACCURACY")

    acc_good = accuracy(ground_truths, good_preds)
    acc_med = accuracy(ground_truths, med_preds)
    acc_poor = accuracy(ground_truths, poor_preds)
    acc_over = accuracy(ground_truths, overconf_preds)

    print(f"    Good model accuracy:          {acc_good:.2%}  ({acc_good:.4f})")
    print(f"    Mediocre model accuracy:      {acc_med:.2%}  ({acc_med:.4f})")
    print(f"    Poor model accuracy:          {acc_poor:.2%}  ({acc_poor:.4f})")
    print(f"    Overconfident model accuracy:  {acc_over:.2%}  ({acc_over:.4f})")

    # Per-question breakdown for good model
    print("\n    Per-question breakdown (good model):")
    for i, (gt, pred) in enumerate(zip(ground_truths, good_preds)):
        status = "CORRECT" if gt == pred else "WRONG  "
        print(f"      Q{i}: truth={gt}  pred={pred}  -> {status}")

    # ======================================================================
    # METRIC 2: PRECISION
    # ======================================================================
    print_header(2, "PRECISION")

    for model_name, preds in [("Good", good_preds), ("Mediocre", med_preds), ("Poor", poor_preds)]:
        prec = precision_per_class(ground_truths, preds)
        print(f"\n    {model_name} model precision per class:")
        for cls, val in sorted(prec.items()):
            bar = "#" * int(val * 20)
            print(f"      Class {cls}: {val:.4f}  {bar}")

    # ======================================================================
    # METRIC 3: RECALL
    # ======================================================================
    print_header(3, "RECALL")

    for model_name, preds in [("Good", good_preds), ("Mediocre", med_preds), ("Poor", poor_preds)]:
        rec = recall_per_class(ground_truths, preds)
        print(f"\n    {model_name} model recall per class:")
        for cls, val in sorted(rec.items()):
            bar = "#" * int(val * 20)
            print(f"      Class {cls}: {val:.4f}  {bar}")

    # ======================================================================
    # METRIC 4: F1 SCORE
    # ======================================================================
    print_header(4, "F1 SCORE")

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

    # ======================================================================
    # METRIC 5: CONFUSION MATRIX
    # ======================================================================
    print_header(5, "CONFUSION MATRIX")

    for model_name, preds in [("Good", good_preds), ("Mediocre", med_preds), ("Poor", poor_preds)]:
        cm = confusion_matrix(ground_truths, preds)
        print(f"\n    {model_name} model:")
        print(render_confusion_matrix(cm))
        print()

    # ======================================================================
    # METRIC 6: BLEU
    # ======================================================================
    print_header(6, "BLEU (Bilingual Evaluation Understudy)")

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

    # ======================================================================
    # METRIC 7: ROUGE
    # ======================================================================
    print_header(7, "ROUGE (Recall-Oriented Understudy for Gisting Evaluation)")

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

    # ======================================================================
    # METRIC 8: METEOR
    # ======================================================================
    print_header(8, "METEOR (Metric for Evaluation of Translation with Explicit ORdering)")

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

    # ======================================================================
    # METRIC 9: CIDEr
    # ======================================================================
    print_header(9, "CIDEr (Consensus-based Image Description Evaluation)")

    cider_refs = [ex["reference"] for ex in text_examples[:3]]

    for i, ex in enumerate(text_examples[:3]):
        ref_list = [ex["reference"]]
        print(f"\n    Example {i+1}:")

        for quality, hyp_key in [("Good", "good_hypothesis"),
                                  ("Mediocre", "mediocre_hypothesis"),
                                  ("Poor", "poor_hypothesis")]:
            hyp = ex[hyp_key]
            result = cider_score(ref_list, hyp)
            per_n_str = "  ".join(f"{k}={v:.3f}" for k, v in result["per_n"].items())
            print(f"      {quality:10s}: CIDEr={result['score']:.4f}  ({per_n_str})")

    # ======================================================================
    # METRIC 10: BERTScore
    # ======================================================================
    print_header(10, "BERTScore (Simplified)")

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

    # ======================================================================
    # METRIC 11: BLEURT
    # ======================================================================
    print_header(11, "BLEURT (BERT-based Learned Evaluation Understudy for Text)")

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

    # ======================================================================
    # METRIC 12: MoverScore
    # ======================================================================
    print_header(12, "MoverScore (Word Mover's Distance)")

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

    # ======================================================================
    # METRIC 13: EXACT MATCH
    # ======================================================================
    print_header(13, "EXACT MATCH")

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

    # ======================================================================
    # METRIC 14: TOKEN F1
    # ======================================================================
    print_header(14, "TOKEN F1")

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

    # ======================================================================
    # METRIC 15: PERPLEXITY
    # ======================================================================
    print_header(15, "PERPLEXITY")

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

    # ======================================================================
    # METRIC 16: CROSS ENTROPY
    # ======================================================================
    print_header(16, "CROSS ENTROPY")

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

    # ======================================================================
    # METRIC 17: CALIBRATION
    # ======================================================================
    print_header(17, "CALIBRATION (Expected Calibration Error)")

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
        print(f"    {q}")
        print(f"    {a}")

    # ======================================================================
    # CLOSING
    # ======================================================================
    print("\n" + "=" * 78)
    print("  END OF CHAPTER 2: CLASSICAL NLP EVALUATION METRICS")
    print("=" * 78)
    print()
    print("    Key takeaway: No single metric tells the whole story.")
    print("    Next: Chapter 3 - Modern LLM Evaluation Frameworks")
    print()


if __name__ == "__main__":
    main()
