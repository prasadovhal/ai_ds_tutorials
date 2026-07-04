"""
Chapter 2 - Classical NLP Metrics
Evaluator module: Pure-function implementations of ALL classical NLP metrics.

Every metric is implemented from scratch using only the Python standard library.
No numpy, no sklearn, no nltk. This is intentional -- understanding the math
matters more than calling a library function.

Metrics implemented:
  1.  Accuracy (exact match ratio)
  2.  Precision (per-class positive prediction quality)
  3.  Recall (per-class detection completeness)
  4.  F1 Score (micro, macro, weighted)
  5.  Confusion Matrix (NxN with ASCII visualization)
  6.  BLEU (1-4 gram + corpus BLEU with brevity penalty)
  7.  ROUGE (ROUGE-1, ROUGE-2, ROUGE-L)
  8.  METEOR (alignment-based with synonym/stem matching)
  9.  CIDEr (consensus-based TF-IDF n-gram scoring)
  10. BERTScore (simplified embedding similarity)
  11. BLEURT (architecture explanation + simplified proxy)
  12. MoverScore (simplified Word Mover's Distance)
  13. Exact Match (strict string equality)
  14. Token F1 (token-level overlap)
  15. Perplexity (with simple n-gram language model)
  16. Cross Entropy (information-theoretic loss)
  17. Calibration (predicted probability vs actual correctness)
"""

import math
import re
from collections import Counter
from typing import Optional


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    text = text.lower().strip()
    # Split on whitespace and strip punctuation from edges
    tokens = re.findall(r'\b\w+\b', text)
    return tokens


def _get_ngrams(tokens: list[str], n: int) -> Counter:
    """Extract n-grams from a token list and return their counts."""
    ngrams = Counter()
    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i:i + n])
        ngrams[ngram] += 1
    return ngrams


def _lcs_length(seq1: list, seq2: list) -> int:
    """Compute the length of the Longest Common Subsequence."""
    m, n = len(seq1), len(seq2)
    # Optimize space: only keep two rows
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


# Porter stemmer -- minimal implementation for METEOR
_STEP1_SUFFIXES = [
    ('sses', 'ss'), ('ies', 'i'), ('ss', 'ss'), ('s', ''),
]
_STEP2_SUFFIXES = [
    ('ational', 'ate'), ('tional', 'tion'), ('enci', 'ence'),
    ('anci', 'ance'), ('izer', 'ize'), ('isation', 'ize'),
    ('ization', 'ize'), ('ation', 'ate'), ('ator', 'ate'),
    ('alism', 'al'), ('iveness', 'ive'), ('fulness', 'ful'),
    ('ousness', 'ous'), ('aliti', 'al'), ('iviti', 'ive'),
    ('biliti', 'ble'), ('ness', 'ness'), ('ment', 'ment'),
]


def _simple_stem(word: str) -> str:
    """Very simplified stemmer for demonstration purposes."""
    word = word.lower()
    if len(word) <= 3:
        return word

    for suffix, replacement in _STEP1_SUFFIXES:
        if word.endswith(suffix):
            word = word[:-len(suffix)] + replacement
            break

    for suffix, replacement in _STEP2_SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) + len(replacement) >= 3:
            word = word[:-len(suffix)] + replacement
            break

    # Remove common endings
    for suffix in ['ing', 'ed', 'ly']:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[:-len(suffix)]
            break

    return word


# Simple synonym groups for METEOR demonstration
_SYNONYM_GROUPS = [
    {"big", "large", "huge", "enormous", "massive", "giant"},
    {"small", "tiny", "little", "minute", "miniature"},
    {"fast", "quick", "rapid", "swift", "speedy"},
    {"slow", "sluggish", "unhurried", "gradual"},
    {"good", "great", "excellent", "fine", "wonderful"},
    {"bad", "poor", "terrible", "awful", "horrible"},
    {"correct", "right", "accurate", "precise", "exact"},
    {"wrong", "incorrect", "inaccurate", "false", "erroneous"},
    {"answer", "response", "reply", "solution"},
    {"question", "query", "inquiry", "problem"},
    {"because", "since", "as", "due"},
    {"show", "demonstrate", "illustrate", "display"},
    {"change", "modify", "alter", "transform"},
    {"increase", "grow", "rise", "expand"},
    {"decrease", "reduce", "shrink", "diminish", "drop"},
    {"theory", "hypothesis", "model", "framework"},
    {"force", "power", "energy", "strength"},
    {"distance", "length", "range", "span"},
]


def _are_synonyms(word1: str, word2: str) -> bool:
    """Check if two words are synonyms using our simple synonym table."""
    w1, w2 = word1.lower(), word2.lower()
    if w1 == w2:
        return True
    for group in _SYNONYM_GROUPS:
        if w1 in group and w2 in group:
            return True
    return False


# ============================================================================
# 1. ACCURACY
# ============================================================================

def accuracy(ground_truths: list, predictions: list) -> float:
    """
    Accuracy = (number of correct predictions) / (total predictions)

    The simplest evaluation metric. Counts the fraction of predictions
    that exactly match the ground truth.

    Args:
        ground_truths: List of correct labels
        predictions: List of predicted labels

    Returns:
        Float between 0.0 and 1.0
    """
    if len(ground_truths) != len(predictions):
        raise ValueError("Lists must have the same length")
    if not ground_truths:
        return 0.0
    correct = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == pred)
    return correct / len(ground_truths)


# ============================================================================
# 2. PRECISION
# ============================================================================

def precision_per_class(ground_truths: list, predictions: list) -> dict:
    """
    Precision for class C = TP_C / (TP_C + FP_C)

    "Of all items the model PREDICTED as class C, how many actually ARE class C?"

    High precision = few false positives (model is careful about what it labels).
    """
    classes = sorted(set(ground_truths) | set(predictions))
    result = {}
    for cls in classes:
        tp = sum(1 for gt, p in zip(ground_truths, predictions) if p == cls and gt == cls)
        fp = sum(1 for gt, p in zip(ground_truths, predictions) if p == cls and gt != cls)
        result[cls] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    return result


# ============================================================================
# 3. RECALL
# ============================================================================

def recall_per_class(ground_truths: list, predictions: list) -> dict:
    """
    Recall for class C = TP_C / (TP_C + FN_C)

    "Of all items that ARE class C, how many did the model FIND?"

    High recall = few false negatives (model catches most instances).
    """
    classes = sorted(set(ground_truths) | set(predictions))
    result = {}
    for cls in classes:
        tp = sum(1 for gt, p in zip(ground_truths, predictions) if gt == cls and p == cls)
        fn = sum(1 for gt, p in zip(ground_truths, predictions) if gt == cls and p != cls)
        result[cls] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return result


# ============================================================================
# 4. F1 SCORE
# ============================================================================

def f1_per_class(ground_truths: list, predictions: list) -> dict:
    """
    F1 for class C = 2 * (Precision_C * Recall_C) / (Precision_C + Recall_C)

    The harmonic mean of precision and recall. Balances both concerns.
    """
    prec = precision_per_class(ground_truths, predictions)
    rec = recall_per_class(ground_truths, predictions)
    result = {}
    for cls in prec:
        p, r = prec[cls], rec[cls]
        result[cls] = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return result


def f1_micro(ground_truths: list, predictions: list) -> float:
    """
    Micro F1: Compute TP, FP, FN globally across all classes, then compute F1.
    Gives equal weight to each SAMPLE.
    """
    classes = sorted(set(ground_truths) | set(predictions))
    total_tp = 0
    total_fp = 0
    total_fn = 0
    for cls in classes:
        tp = sum(1 for gt, p in zip(ground_truths, predictions) if p == cls and gt == cls)
        fp = sum(1 for gt, p in zip(ground_truths, predictions) if p == cls and gt != cls)
        fn = sum(1 for gt, p in zip(ground_truths, predictions) if gt == cls and p != cls)
        total_tp += tp
        total_fp += fp
        total_fn += fn
    prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    return 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0


def f1_macro(ground_truths: list, predictions: list) -> float:
    """
    Macro F1: Compute F1 per class, then take unweighted average.
    Gives equal weight to each CLASS (good for imbalanced datasets).
    """
    per_class = f1_per_class(ground_truths, predictions)
    if not per_class:
        return 0.0
    return sum(per_class.values()) / len(per_class)


def f1_weighted(ground_truths: list, predictions: list) -> float:
    """
    Weighted F1: Compute F1 per class, then take weighted average by class support.
    Balances between micro and macro.
    """
    per_class = f1_per_class(ground_truths, predictions)
    support = Counter(ground_truths)
    total = len(ground_truths)
    if total == 0:
        return 0.0
    weighted_sum = sum(per_class.get(cls, 0.0) * count for cls, count in support.items())
    return weighted_sum / total


# ============================================================================
# 5. CONFUSION MATRIX
# ============================================================================

def confusion_matrix(ground_truths: list, predictions: list) -> dict:
    """
    Build an NxN confusion matrix.

    Returns:
        dict with 'labels' (list of class names) and 'matrix' (dict of dicts).
        matrix[actual][predicted] = count
    """
    labels = sorted(set(ground_truths) | set(predictions))
    matrix = {actual: {pred: 0 for pred in labels} for actual in labels}
    for gt, pred in zip(ground_truths, predictions):
        matrix[gt][pred] += 1
    return {"labels": labels, "matrix": matrix}


def render_confusion_matrix(cm: dict, cell_width: int = 6) -> str:
    """Render a confusion matrix as a formatted ASCII string."""
    labels = cm["labels"]
    matrix = cm["matrix"]

    lines = []
    # Header
    header = " " * 12 + "PREDICTED".center(len(labels) * cell_width)
    lines.append(header)
    lines.append(" " * 12 + "".join(f"{l:>{cell_width}}" for l in labels))
    lines.append(" " * 8 + "+" + "-" * (len(labels) * cell_width))

    for i, actual in enumerate(labels):
        row = "".join(f"{matrix[actual][pred]:>{cell_width}}" for pred in labels)
        prefix = "  ACTUAL" if i == 0 else "        "
        lines.append(f"{prefix} {actual:>2s} |{row}")

    return "\n".join(lines)


# ============================================================================
# 6. BLEU (Bilingual Evaluation Understudy)
# ============================================================================

def bleu_n(reference: str, hypothesis: str, n: int = 1) -> float:
    """
    Sentence-level BLEU-N score.

    BLEU-N = clipped_n_gram_matches / total_hypothesis_n_grams

    Measures n-gram precision: what fraction of the hypothesis n-grams
    appear in the reference?
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if len(hyp_tokens) < n:
        return 0.0

    ref_ngrams = _get_ngrams(ref_tokens, n)
    hyp_ngrams = _get_ngrams(hyp_tokens, n)

    # Clipped counts: min of hypothesis count and reference count for each n-gram
    clipped = 0
    for ngram, count in hyp_ngrams.items():
        clipped += min(count, ref_ngrams.get(ngram, 0))

    total = sum(hyp_ngrams.values())
    return clipped / total if total > 0 else 0.0


def brevity_penalty(reference: str, hypothesis: str) -> float:
    """
    Brevity Penalty (BP) for BLEU.
    Penalizes hypotheses that are shorter than the reference.

    BP = exp(1 - ref_len / hyp_len)  if hyp_len < ref_len
    BP = 1.0                          if hyp_len >= ref_len
    """
    ref_len = len(_tokenize(reference))
    hyp_len = len(_tokenize(hypothesis))
    if hyp_len == 0:
        return 0.0
    if hyp_len >= ref_len:
        return 1.0
    return math.exp(1 - ref_len / hyp_len)


def bleu_score(reference: str, hypothesis: str, max_n: int = 4,
               weights: Optional[list[float]] = None) -> dict:
    """
    Combined BLEU score with brevity penalty.

    BLEU = BP * exp( sum( w_n * log(p_n) ) )

    where p_n is the n-gram precision and w_n is the weight for that n-gram order.
    Default weights: uniform (1/max_n each).

    Returns dict with individual BLEU-1..N, combined BLEU, and brevity penalty.
    """
    if weights is None:
        weights = [1.0 / max_n] * max_n

    bp = brevity_penalty(reference, hypothesis)
    precisions = {}
    log_avg = 0.0
    all_positive = True

    for n in range(1, max_n + 1):
        p_n = bleu_n(reference, hypothesis, n)
        precisions[f"BLEU-{n}"] = round(p_n, 4)
        if p_n > 0:
            log_avg += weights[n - 1] * math.log(p_n)
        else:
            all_positive = False

    if all_positive:
        combined = bp * math.exp(log_avg)
    else:
        combined = 0.0

    return {
        **precisions,
        "brevity_penalty": round(bp, 4),
        "BLEU": round(combined, 4),
    }


def corpus_bleu(references: list[str], hypotheses: list[str],
                max_n: int = 4, weights: Optional[list[float]] = None) -> dict:
    """
    Corpus-level BLEU: aggregates n-gram counts across all sentence pairs
    before computing precision.
    """
    if weights is None:
        weights = [1.0 / max_n] * max_n

    total_ref_len = 0
    total_hyp_len = 0
    total_clipped = {n: 0 for n in range(1, max_n + 1)}
    total_count = {n: 0 for n in range(1, max_n + 1)}

    for ref, hyp in zip(references, hypotheses):
        ref_tokens = _tokenize(ref)
        hyp_tokens = _tokenize(hyp)
        total_ref_len += len(ref_tokens)
        total_hyp_len += len(hyp_tokens)

        for n in range(1, max_n + 1):
            ref_ngrams = _get_ngrams(ref_tokens, n)
            hyp_ngrams = _get_ngrams(hyp_tokens, n)
            for ngram, count in hyp_ngrams.items():
                total_clipped[n] += min(count, ref_ngrams.get(ngram, 0))
            total_count[n] += sum(hyp_ngrams.values())

    # Brevity penalty at corpus level
    if total_hyp_len == 0:
        bp = 0.0
    elif total_hyp_len >= total_ref_len:
        bp = 1.0
    else:
        bp = math.exp(1 - total_ref_len / total_hyp_len)

    precisions = {}
    log_avg = 0.0
    all_positive = True
    for n in range(1, max_n + 1):
        p_n = total_clipped[n] / total_count[n] if total_count[n] > 0 else 0.0
        precisions[f"BLEU-{n}"] = round(p_n, 4)
        if p_n > 0:
            log_avg += weights[n - 1] * math.log(p_n)
        else:
            all_positive = False

    combined = bp * math.exp(log_avg) if all_positive else 0.0

    return {
        **precisions,
        "brevity_penalty": round(bp, 4),
        "corpus_BLEU": round(combined, 4),
        "corpus_size": len(references),
    }


# ============================================================================
# 7. ROUGE (Recall-Oriented Understudy for Gisting Evaluation)
# ============================================================================

def rouge_n(reference: str, hypothesis: str, n: int = 1) -> dict:
    """
    ROUGE-N: n-gram recall between reference and hypothesis.

    ROUGE-N Recall    = matching_n_grams / reference_n_grams
    ROUGE-N Precision = matching_n_grams / hypothesis_n_grams
    ROUGE-N F1        = harmonic mean of the two

    Unlike BLEU (precision-focused), ROUGE is recall-focused:
    "How much of the reference is captured in the hypothesis?"
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    ref_ngrams = _get_ngrams(ref_tokens, n)
    hyp_ngrams = _get_ngrams(hyp_tokens, n)

    matching = 0
    for ngram, count in ref_ngrams.items():
        matching += min(count, hyp_ngrams.get(ngram, 0))

    ref_total = sum(ref_ngrams.values())
    hyp_total = sum(hyp_ngrams.values())

    recall = matching / ref_total if ref_total > 0 else 0.0
    precision = matching / hyp_total if hyp_total > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def rouge_l(reference: str, hypothesis: str) -> dict:
    """
    ROUGE-L: Longest Common Subsequence based metric.

    Uses LCS instead of n-grams, capturing sentence-level structure.
    LCS does not require consecutive matches (unlike n-grams), so it
    is more flexible in measuring ordering.

    Recall    = LCS_length / reference_length
    Precision = LCS_length / hypothesis_length
    F1        = harmonic mean
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    lcs_len = _lcs_length(ref_tokens, hyp_tokens)

    recall = lcs_len / len(ref_tokens) if len(ref_tokens) > 0 else 0.0
    precision = lcs_len / len(hyp_tokens) if len(hyp_tokens) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "lcs_length": lcs_len,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def rouge_scores(reference: str, hypothesis: str) -> dict:
    """Compute ROUGE-1, ROUGE-2, and ROUGE-L together."""
    return {
        "ROUGE-1": rouge_n(reference, hypothesis, n=1),
        "ROUGE-2": rouge_n(reference, hypothesis, n=2),
        "ROUGE-L": rouge_l(reference, hypothesis),
    }


# ============================================================================
# 8. METEOR (Metric for Evaluation of Translation with Explicit ORdering)
# ============================================================================

def meteor_score(reference: str, hypothesis: str,
                 alpha: float = 0.9, beta: float = 3.0, gamma: float = 0.5) -> dict:
    """
    METEOR: Alignment-based metric using exact match, stemming, and synonyms.

    Steps:
    1. Align hypothesis words to reference words (exact -> stem -> synonym)
    2. Compute unigram precision and recall
    3. Compute F-mean (weighted harmonic mean, favoring recall)
    4. Apply fragmentation penalty (rewards contiguous matches)

    METEOR = F_mean * (1 - gamma * frag^beta)

    Parameters:
        alpha: weight of recall vs precision (higher = more recall weight)
        beta: fragmentation penalty strength
        gamma: fragmentation penalty weight
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if not ref_tokens or not hyp_tokens:
        return {"score": 0.0, "precision": 0.0, "recall": 0.0,
                "f_mean": 0.0, "penalty": 1.0, "matches": 0,
                "chunks": 0, "match_details": []}

    # Stage 1: Alignment -- find matches (exact, stem, synonym)
    ref_matched = [False] * len(ref_tokens)
    hyp_matched = [False] * len(hyp_tokens)
    match_details = []

    # Pass 1: Exact matches
    for i, h_tok in enumerate(hyp_tokens):
        for j, r_tok in enumerate(ref_tokens):
            if not ref_matched[j] and not hyp_matched[i] and h_tok == r_tok:
                ref_matched[j] = True
                hyp_matched[i] = True
                match_details.append((i, j, "exact"))
                break

    # Pass 2: Stem matches
    for i, h_tok in enumerate(hyp_tokens):
        if hyp_matched[i]:
            continue
        h_stem = _simple_stem(h_tok)
        for j, r_tok in enumerate(ref_tokens):
            if not ref_matched[j] and h_stem == _simple_stem(r_tok):
                ref_matched[j] = True
                hyp_matched[i] = True
                match_details.append((i, j, "stem"))
                break

    # Pass 3: Synonym matches
    for i, h_tok in enumerate(hyp_tokens):
        if hyp_matched[i]:
            continue
        for j, r_tok in enumerate(ref_tokens):
            if not ref_matched[j] and _are_synonyms(h_tok, r_tok):
                ref_matched[j] = True
                hyp_matched[i] = True
                match_details.append((i, j, "synonym"))
                break

    matches = len(match_details)

    # Stage 2: Precision and Recall
    precision = matches / len(hyp_tokens) if hyp_tokens else 0.0
    recall = matches / len(ref_tokens) if ref_tokens else 0.0

    # F-mean with alpha weighting (higher alpha = more recall focus)
    if precision == 0 and recall == 0:
        f_mean = 0.0
    else:
        f_mean = (precision * recall) / (alpha * precision + (1 - alpha) * recall)

    # Stage 3: Fragmentation penalty
    # Count chunks: groups of contiguous aligned words
    if matches == 0:
        chunks = 0
        penalty = 1.0
    else:
        # Sort matches by hypothesis index
        sorted_matches = sorted(match_details, key=lambda x: x[0])
        chunks = 1
        for k in range(1, len(sorted_matches)):
            prev_ref_idx = sorted_matches[k - 1][1]
            curr_ref_idx = sorted_matches[k][1]
            if curr_ref_idx != prev_ref_idx + 1:
                chunks += 1

        frag = chunks / matches
        penalty = gamma * (frag ** beta)

    score = f_mean * (1 - penalty) if f_mean > 0 else 0.0
    score = max(0.0, score)

    return {
        "score": round(score, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f_mean": round(f_mean, 4),
        "penalty": round(penalty, 4),
        "matches": matches,
        "chunks": chunks,
        "match_details": [(hyp_tokens[h], ref_tokens[r], t) for h, r, t in match_details],
    }


# ============================================================================
# 9. CIDEr (Consensus-based Image Description Evaluation)
# ============================================================================

def cider_score(references: list[str], hypothesis: str, max_n: int = 4) -> dict:
    """
    CIDEr: Measures how well a hypothesis captures consensus among references.

    Uses TF-IDF weighted n-gram matching. Designed for image captioning but
    applicable to any text generation task with multiple references.

    CIDEr_n = (1/M) * sum_i( (g_n(hyp) . g_n(ref_i)) / (|g_n(hyp)| * |g_n(ref_i)|) )
    CIDEr   = (1/N) * sum_n( CIDEr_n )

    where g_n(s) is the TF-IDF vector of n-grams in sentence s.
    """
    num_refs = len(references)
    if num_refs == 0:
        return {"score": 0.0, "per_n": {}}

    hyp_tokens = _tokenize(hypothesis)
    ref_tokens_list = [_tokenize(r) for r in references]

    # All documents = references + hypothesis (for IDF computation)
    all_docs = ref_tokens_list + [hyp_tokens]
    num_docs = len(all_docs)

    per_n_scores = {}

    for n in range(1, max_n + 1):
        # Compute n-gram counts for all documents
        all_ngram_counts = [_get_ngrams(doc, n) for doc in all_docs]

        # Compute document frequency for each n-gram
        df = Counter()
        for ngram_counts in all_ngram_counts:
            for ngram in ngram_counts:
                df[ngram] += 1

        # Compute TF-IDF vectors
        def tfidf_vector(ngram_counts, doc_len):
            vec = {}
            for ngram, count in ngram_counts.items():
                tf = count / doc_len if doc_len > 0 else 0.0
                idf = math.log(max(1.0, num_docs / df[ngram])) if df[ngram] > 0 else 0.0
                vec[ngram] = tf * idf
            return vec

        hyp_ngrams = all_ngram_counts[-1]
        hyp_vec = tfidf_vector(hyp_ngrams, max(1, len(hyp_tokens) - n + 1))

        # Cosine similarity between hypothesis and each reference
        similarities = []
        for i in range(num_refs):
            ref_ngrams = all_ngram_counts[i]
            ref_len = max(1, len(ref_tokens_list[i]) - n + 1)
            ref_vec = tfidf_vector(ref_ngrams, ref_len)

            # Dot product
            all_keys = set(hyp_vec.keys()) | set(ref_vec.keys())
            dot = sum(hyp_vec.get(k, 0.0) * ref_vec.get(k, 0.0) for k in all_keys)

            # Magnitudes
            hyp_mag = math.sqrt(sum(v ** 2 for v in hyp_vec.values())) if hyp_vec else 0.0
            ref_mag = math.sqrt(sum(v ** 2 for v in ref_vec.values())) if ref_vec else 0.0

            if hyp_mag > 0 and ref_mag > 0:
                similarities.append(dot / (hyp_mag * ref_mag))
            else:
                similarities.append(0.0)

        # Average across references
        avg_sim = sum(similarities) / num_refs if similarities else 0.0
        # CIDEr convention: multiply by 10
        per_n_scores[f"CIDEr-{n}"] = round(avg_sim * 10, 4)

    # Final CIDEr: average across n-gram orders
    final_score = sum(per_n_scores.values()) / max_n
    return {
        "score": round(final_score, 4),
        "per_n": per_n_scores,
    }


# ============================================================================
# 10. BERTScore (Simplified -- embedding similarity without actual model)
# ============================================================================

def bertscore_simplified(reference: str, hypothesis: str) -> dict:
    """
    BERTScore (Simplified Simulation):

    REAL BERTScore:
      1. Pass reference and hypothesis through BERT to get contextual embeddings
      2. For each token in hypothesis, find most similar token in reference (cosine sim)
      3. Precision = average of max similarities (hypothesis -> reference)
      4. Recall = average of max similarities (reference -> hypothesis)
      5. F1 = harmonic mean

    THIS SIMPLIFIED VERSION:
      - Uses character n-gram overlap as a proxy for semantic similarity
      - Demonstrates the greedy matching concept without requiring a model
      - Shows the precision/recall/F1 structure

    For real BERTScore, use the `bert_score` Python package with a BERT model.
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if not ref_tokens or not hyp_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0,
                "note": "Empty input"}

    def char_ngram_similarity(word1: str, word2: str, n: int = 3) -> float:
        """Compute character n-gram overlap as a proxy for embedding similarity."""
        if word1 == word2:
            return 1.0
        set1 = set()
        set2 = set()
        for i in range(max(0, len(word1) - n + 1)):
            set1.add(word1[i:i + n])
        for i in range(max(0, len(word2) - n + 1)):
            set2.add(word2[i:i + n])
        if not set1 or not set2:
            # Fallback for very short words
            return 1.0 if word1 == word2 else 0.0
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union) if union else 0.0

    # Precision: for each hypothesis token, find best match in reference
    precision_scores = []
    for h_tok in hyp_tokens:
        best_sim = max(char_ngram_similarity(h_tok, r_tok) for r_tok in ref_tokens)
        precision_scores.append(best_sim)

    # Recall: for each reference token, find best match in hypothesis
    recall_scores = []
    for r_tok in ref_tokens:
        best_sim = max(char_ngram_similarity(r_tok, h_tok) for h_tok in hyp_tokens)
        recall_scores.append(best_sim)

    precision = sum(precision_scores) / len(precision_scores)
    recall = sum(recall_scores) / len(recall_scores)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "note": "Simplified (char n-gram proxy). Real BERTScore uses BERT embeddings.",
    }


# ============================================================================
# 11. BLEURT (Simplified -- learned metric concept)
# ============================================================================

def bleurt_simplified(reference: str, hypothesis: str) -> dict:
    """
    BLEURT (Simplified Simulation):

    REAL BLEURT (Bilingual Evaluation Understudy with Representations from Transformers):
      1. Pre-train BERT on synthetic data (backtranslation, word drops, etc.)
      2. Fine-tune on human quality judgments (WMT, etc.)
      3. Input: (reference, hypothesis) pair
      4. Output: single scalar quality score

    THIS SIMPLIFIED VERSION:
      - Combines multiple surface-level features as a proxy
      - Demonstrates the concept of a LEARNED metric
      - Shows how multiple signals get combined into one score

    Architecture of real BLEURT:
      Reference ──┐
                   ├──▶ [BERT encoder] ──▶ [Regression head] ──▶ Score
      Hypothesis ──┘

    For real BLEURT, use Google's `bleurt` package with a checkpoint.
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if not ref_tokens or not hyp_tokens:
        return {"score": 0.0, "features": {}, "note": "Empty input"}

    # Feature 1: Token overlap (like F1)
    ref_set = set(ref_tokens)
    hyp_set = set(hyp_tokens)
    overlap = ref_set & hyp_set
    token_precision = len(overlap) / len(hyp_set) if hyp_set else 0.0
    token_recall = len(overlap) / len(ref_set) if ref_set else 0.0
    token_f1 = (2 * token_precision * token_recall / (token_precision + token_recall)
                if (token_precision + token_recall) > 0 else 0.0)

    # Feature 2: Length ratio
    len_ratio = len(hyp_tokens) / len(ref_tokens) if ref_tokens else 0.0
    len_penalty = 1.0 - abs(1.0 - len_ratio) * 0.5  # Penalty for length mismatch
    len_penalty = max(0.0, len_penalty)

    # Feature 3: Bigram overlap
    ref_bigrams = _get_ngrams(ref_tokens, 2)
    hyp_bigrams = _get_ngrams(hyp_tokens, 2)
    bigram_match = 0
    for bg, count in hyp_bigrams.items():
        bigram_match += min(count, ref_bigrams.get(bg, 0))
    bigram_total = sum(hyp_bigrams.values())
    bigram_precision = bigram_match / bigram_total if bigram_total > 0 else 0.0

    # Feature 4: Order preservation (using LCS)
    lcs_len = _lcs_length(ref_tokens, hyp_tokens)
    order_score = lcs_len / max(len(ref_tokens), len(hyp_tokens))

    # Combine features with learned-like weights
    features = {
        "token_f1": round(token_f1, 4),
        "length_penalty": round(len_penalty, 4),
        "bigram_precision": round(bigram_precision, 4),
        "order_preservation": round(order_score, 4),
    }

    # Weighted combination (simulating what a trained model would learn)
    score = (0.35 * token_f1 +
             0.15 * len_penalty +
             0.25 * bigram_precision +
             0.25 * order_score)

    return {
        "score": round(score, 4),
        "features": features,
        "note": "Simplified proxy. Real BLEURT uses fine-tuned BERT regression.",
    }


# ============================================================================
# 12. MoverScore (Simplified Word Mover's Distance)
# ============================================================================

def moverscore_simplified(reference: str, hypothesis: str) -> dict:
    """
    MoverScore (Simplified):

    REAL MoverScore:
      1. Get contextual embeddings from BERT for both texts
      2. Compute Word Mover's Distance (WMD): minimum cost to "transport"
         hypothesis word distribution to reference word distribution
      3. Cost = 1 - cosine_similarity between embeddings

    THIS SIMPLIFIED VERSION:
      - Uses character-level edit distance as proxy for word distance
      - Implements a greedy bipartite matching (approximation of WMD)
      - Demonstrates the transportation concept

    Intuition: How much "work" does it take to transform the hypothesis
    into the reference by moving words around?
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if not ref_tokens or not hyp_tokens:
        return {"score": 0.0, "avg_distance": 1.0, "note": "Empty input"}

    def edit_distance(s1: str, s2: str) -> int:
        """Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return edit_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                cost = 0 if c1 == c2 else 1
                curr_row.append(min(
                    curr_row[j] + 1,        # insert
                    prev_row[j + 1] + 1,    # delete
                    prev_row[j] + cost,     # replace
                ))
            prev_row = curr_row
        return prev_row[-1]

    def word_distance(w1: str, w2: str) -> float:
        """Normalized word distance as proxy for embedding distance."""
        if w1 == w2:
            return 0.0
        max_len = max(len(w1), len(w2))
        if max_len == 0:
            return 0.0
        return edit_distance(w1, w2) / max_len

    # Greedy matching: for each hypothesis word, find closest reference word
    total_distance = 0.0
    ref_used = [False] * len(ref_tokens)
    matches = []

    for h_tok in hyp_tokens:
        best_dist = float('inf')
        best_idx = -1
        for j, r_tok in enumerate(ref_tokens):
            if not ref_used[j]:
                d = word_distance(h_tok, r_tok)
                if d < best_dist:
                    best_dist = d
                    best_idx = j
        if best_idx >= 0:
            ref_used[best_idx] = True
            total_distance += best_dist
            matches.append((h_tok, ref_tokens[best_idx], round(best_dist, 3)))
        else:
            total_distance += 1.0
            matches.append((h_tok, "<unmatched>", 1.0))

    # Add penalty for unmatched reference words
    unmatched_ref = sum(1 for used in ref_used if not used)
    total_distance += unmatched_ref * 0.5

    max_possible = max(len(ref_tokens), len(hyp_tokens))
    avg_distance = total_distance / max_possible if max_possible > 0 else 0.0

    # Convert distance to similarity score (0 = different, 1 = identical)
    score = max(0.0, 1.0 - avg_distance)

    return {
        "score": round(score, 4),
        "avg_distance": round(avg_distance, 4),
        "total_distance": round(total_distance, 4),
        "top_matches": matches[:8],
        "note": "Simplified (edit distance proxy). Real MoverScore uses BERT + WMD.",
    }


# ============================================================================
# 13. EXACT MATCH
# ============================================================================

def exact_match(reference: str, hypothesis: str, normalize: bool = True) -> dict:
    """
    Exact Match: Strict string equality check.

    If normalize=True, strips whitespace and lowercases before comparing.
    Used in extractive QA (SQuAD), classification, and factoid questions.
    """
    if normalize:
        ref_clean = reference.strip().lower()
        hyp_clean = hypothesis.strip().lower()
    else:
        ref_clean = reference
        hyp_clean = hypothesis

    match = ref_clean == hyp_clean

    return {
        "match": match,
        "score": 1.0 if match else 0.0,
        "reference_normalized": ref_clean,
        "hypothesis_normalized": hyp_clean,
    }


def exact_match_score(references: list[str], hypotheses: list[str],
                      normalize: bool = True) -> float:
    """Compute Exact Match accuracy across a dataset."""
    if not references:
        return 0.0
    matches = sum(
        1 for r, h in zip(references, hypotheses)
        if exact_match(r, h, normalize)["match"]
    )
    return matches / len(references)


# ============================================================================
# 14. TOKEN F1
# ============================================================================

def token_f1(reference: str, hypothesis: str) -> dict:
    """
    Token-level F1: Measures overlap at the token level.

    Used in extractive QA (SQuAD) alongside Exact Match.
    Unlike Exact Match, gives partial credit for partial overlap.

    Precision = |common_tokens| / |hypothesis_tokens|
    Recall    = |common_tokens| / |reference_tokens|
    F1        = harmonic mean
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if not ref_tokens and not hyp_tokens:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not ref_tokens or not hyp_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    ref_counter = Counter(ref_tokens)
    hyp_counter = Counter(hyp_tokens)

    # Common tokens: min of counts for each token
    common = 0
    for token in hyp_counter:
        common += min(hyp_counter[token], ref_counter.get(token, 0))

    precision = common / len(hyp_tokens) if hyp_tokens else 0.0
    recall = common / len(ref_tokens) if ref_tokens else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "common_tokens": common,
        "reference_length": len(ref_tokens),
        "hypothesis_length": len(hyp_tokens),
    }


# ============================================================================
# 15. PERPLEXITY
# ============================================================================

def build_ngram_lm(corpus: list[str], n: int = 2) -> dict:
    """
    Build a simple n-gram language model from a corpus.

    Returns a dict mapping (n-1)-gram context to probability distribution
    over next words. Uses add-one (Laplace) smoothing.
    """
    # Collect all n-gram counts
    ngram_counts = Counter()
    context_counts = Counter()
    vocabulary = set()

    for text in corpus:
        tokens = ["<s>"] * (n - 1) + _tokenize(text) + ["</s>"]
        vocabulary.update(tokens)
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i + n])
            context = ngram[:-1]
            ngram_counts[ngram] += 1
            context_counts[context] += 1

    vocab_size = len(vocabulary)

    return {
        "ngram_counts": dict(ngram_counts),
        "context_counts": dict(context_counts),
        "vocab_size": vocab_size,
        "n": n,
    }


def compute_perplexity(text: str, lm: dict) -> dict:
    """
    Perplexity: How surprised the language model is by the text.

    PP(W) = exp( -(1/N) * sum( log P(w_i | context) ) )

    Lower perplexity = model is less surprised = text is more likely.
    Perplexity of 1.0 means the model perfectly predicts every next word.
    Perplexity of V (vocab size) means uniform random guessing.

    Uses add-one smoothing to avoid zero probabilities.
    """
    n = lm["n"]
    ngram_counts = lm["ngram_counts"]
    context_counts = lm["context_counts"]
    vocab_size = lm["vocab_size"]

    tokens = ["<s>"] * (n - 1) + _tokenize(text) + ["</s>"]
    num_tokens = len(tokens) - (n - 1)  # Exclude start padding

    if num_tokens <= 0:
        return {"perplexity": float('inf'), "log_probability": float('-inf'),
                "num_tokens": 0}

    log_prob_sum = 0.0
    token_probs = []

    for i in range(n - 1, len(tokens)):
        ngram = tuple(tokens[i - n + 1:i + 1])
        context = ngram[:-1]

        # Add-one (Laplace) smoothed probability
        ngram_count = ngram_counts.get(ngram, 0)
        context_count = context_counts.get(context, 0)
        prob = (ngram_count + 1) / (context_count + vocab_size)

        log_prob = math.log(prob)
        log_prob_sum += log_prob
        token_probs.append({
            "token": tokens[i],
            "context": " ".join(context),
            "probability": round(prob, 6),
            "log_probability": round(log_prob, 4),
        })

    avg_log_prob = log_prob_sum / num_tokens
    perplexity = math.exp(-avg_log_prob)

    return {
        "perplexity": round(perplexity, 4),
        "log_probability": round(log_prob_sum, 4),
        "avg_log_probability": round(avg_log_prob, 4),
        "num_tokens": num_tokens,
        "token_details": token_probs[:10],  # First 10 for display
    }


# ============================================================================
# 16. CROSS ENTROPY
# ============================================================================

def cross_entropy(true_distribution: list[float],
                  predicted_distribution: list[float]) -> float:
    """
    Cross Entropy: H(p, q) = -sum( p(x) * log(q(x)) )

    Measures the average number of bits needed to encode data from
    distribution p using code optimized for distribution q.

    Lower = predicted distribution is closer to the true distribution.

    Used as a loss function in language modeling and classification.
    """
    if len(true_distribution) != len(predicted_distribution):
        raise ValueError("Distributions must have the same length")

    ce = 0.0
    for p, q in zip(true_distribution, predicted_distribution):
        if p > 0:
            # Clip q to avoid log(0)
            q_clipped = max(q, 1e-10)
            ce -= p * math.log(q_clipped)
    return ce


def cross_entropy_from_labels(ground_truths: list[str], predictions: list[str],
                              confidences: list[float]) -> dict:
    """
    Cross Entropy for classification: uses predicted confidence on the correct class.

    CE = -(1/N) * sum( log(confidence_on_correct_class) )

    This is what most ML frameworks report as "cross entropy loss."
    """
    if not ground_truths:
        return {"cross_entropy": 0.0, "num_samples": 0}

    total_ce = 0.0
    for gt, pred, conf in zip(ground_truths, predictions, confidences):
        if gt == pred:
            # Model predicted correctly with this confidence
            prob_correct = conf
        else:
            # Model predicted wrong; assume remaining probability is split
            prob_correct = (1 - conf) / 4  # 4 other choices for MCQ
        prob_correct = max(prob_correct, 1e-10)
        total_ce -= math.log(prob_correct)

    avg_ce = total_ce / len(ground_truths)

    return {
        "cross_entropy": round(avg_ce, 4),
        "total_log_loss": round(total_ce, 4),
        "num_samples": len(ground_truths),
    }


# ============================================================================
# 17. CALIBRATION
# ============================================================================

def calibration_analysis(ground_truths: list[str], predictions: list[str],
                         confidences: list[float],
                         n_bins: int = 10) -> dict:
    """
    Calibration: Are predicted probabilities aligned with actual correctness?

    A well-calibrated model that says "I'm 80% confident" should be
    correct 80% of the time.

    Expected Calibration Error (ECE):
      ECE = sum( |bin_size/total| * |accuracy_in_bin - avg_confidence_in_bin| )

    Returns bin-level analysis and overall ECE.
    """
    if not ground_truths:
        return {"ece": 0.0, "bins": [], "num_samples": 0}

    # Create bins
    bin_boundaries = [i / n_bins for i in range(n_bins + 1)]
    bins = [{
        "lower": bin_boundaries[i],
        "upper": bin_boundaries[i + 1],
        "count": 0,
        "correct": 0,
        "confidence_sum": 0.0,
    } for i in range(n_bins)]

    for gt, pred, conf in zip(ground_truths, predictions, confidences):
        # Find the right bin
        bin_idx = min(int(conf * n_bins), n_bins - 1)
        bins[bin_idx]["count"] += 1
        bins[bin_idx]["confidence_sum"] += conf
        if gt == pred:
            bins[bin_idx]["correct"] += 1

    # Compute ECE
    total = len(ground_truths)
    ece = 0.0
    bin_details = []

    for b in bins:
        if b["count"] > 0:
            bin_accuracy = b["correct"] / b["count"]
            bin_confidence = b["confidence_sum"] / b["count"]
            bin_weight = b["count"] / total
            ece += bin_weight * abs(bin_accuracy - bin_confidence)
            bin_details.append({
                "range": f"{b['lower']:.1f}-{b['upper']:.1f}",
                "count": b["count"],
                "accuracy": round(bin_accuracy, 4),
                "avg_confidence": round(bin_confidence, 4),
                "gap": round(abs(bin_accuracy - bin_confidence), 4),
            })
        else:
            bin_details.append({
                "range": f"{b['lower']:.1f}-{b['upper']:.1f}",
                "count": 0,
                "accuracy": None,
                "avg_confidence": None,
                "gap": 0.0,
            })

    # Overall stats
    total_correct = sum(1 for gt, p in zip(ground_truths, predictions) if gt == p)
    avg_confidence = sum(confidences) / len(confidences)

    return {
        "ece": round(ece, 4),
        "overall_accuracy": round(total_correct / total, 4) if total > 0 else 0.0,
        "avg_confidence": round(avg_confidence, 4),
        "overconfident": avg_confidence > (total_correct / total if total > 0 else 0),
        "bins": bin_details,
        "num_samples": total,
    }


def render_calibration_diagram(cal: dict) -> str:
    """Render an ASCII calibration diagram."""
    lines = []
    lines.append("    Confidence vs Accuracy (Calibration Plot)")
    lines.append("    " + "-" * 52)
    lines.append("    Conf Range  | Count | Accuracy | Confidence | Gap")
    lines.append("    " + "-" * 52)

    for b in cal["bins"]:
        if b["count"] > 0:
            acc_bar = "#" * int(b["accuracy"] * 20)
            conf_bar = "." * int(b["avg_confidence"] * 20)
            lines.append(
                f"    {b['range']:>9s}  | {b['count']:>5d} | "
                f"{b['accuracy']:.2f}  {acc_bar:<20s} | "
                f"{b['avg_confidence']:.2f} | {b['gap']:.3f}"
            )
        else:
            lines.append(f"    {b['range']:>9s}  |     0 |   --   |   --   |  --")

    lines.append("    " + "-" * 52)
    lines.append(f"    ECE = {cal['ece']:.4f}")
    if cal['overconfident']:
        lines.append("    Model is OVERCONFIDENT (avg confidence > accuracy)")
    else:
        lines.append("    Model is UNDERCONFIDENT (avg confidence < accuracy)")
    return "\n".join(lines)
