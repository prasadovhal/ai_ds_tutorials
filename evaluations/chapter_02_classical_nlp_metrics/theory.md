# Chapter 2: Classical NLP Metrics

A compact reference for 17 classical NLP evaluation metrics.

---

## Metric 1: Accuracy

Fraction of predictions the model got right -- the simplest evaluation starting point.

**Intuition:** A 10-question quiz where 7 correct = 70%. No partial credit, no nuance.

```
Accuracy = (1/N) * SUM( I(y_i == y_hat_i) )

where:
  N       = total predictions
  y_i     = ground truth label for sample i
  y_hat_i = predicted label for sample i
  I(...)  = indicator function (1 if true, 0 if false)
```

**Pros/Cons:**
- (+) Simplest metric, works for any number of classes, no hyperparameters
- (-) Misleading on imbalanced datasets (95% class A -> always predict A = 95%)
- (-) No distinction between error types; no partial credit

---

## Metric 2: Precision

Measures how often positive predictions are actually correct -- the quality of predictions.

**Intuition:** "Of all the shots fired, how many hit the target?" High precision = few false alarms.

```
                  TP_C
Precision_C = -----------
              TP_C + FP_C

where (for class C):
  TP_C = correctly predicted as C
  FP_C = incorrectly predicted as C (actually another class)
```

**Pros/Cons:**
- (+) Essential when false positives are costly (spam filters, medical diagnosis)
- (+) Works per-class to identify weak spots
- (-) Ignores false negatives; must be paired with recall

---

## Metric 3: Recall

Measures what fraction of actual positives the model found -- completeness of detection.

**Intuition:** "Of all the survivors in the area, how many did the rescue team find?" Missing someone is the worst outcome.

```
              TP_C
Recall_C = -----------
           TP_C + FN_C

where (for class C):
  TP_C = correctly predicted as C
  FN_C = actually C but predicted as something else
```

```
High Precision, Low Recall:         High Recall, Low Precision:
Model is CONSERVATIVE               Model is AGGRESSIVE
"I only speak when I'm sure"        "I flag everything just in case"
```

**Pros/Cons:**
- (+) Critical for safety-sensitive applications (disease screening)
- (+) Complements precision
- (-) A model predicting everything as class C has 100% recall for C

---

## Metric 4: F1 Score

Harmonic mean of precision and recall, penalizing extreme imbalance in either.

**Intuition:** A scalpel with 100% precision but 1% recall is useless. A bulldozer with 100% recall but 10% precision destroys everything. F1 demands both.

```
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
```

**Pros/Cons:**
- (+) Balances precision and recall; harmonic mean penalizes extreme values
- (+) Multiple variants (micro/macro/weighted) for different needs
- (-) Assumes equal importance of P and R (use F-beta otherwise); ignores true negatives

---

## Metric 5: Confusion Matrix

Shows the FULL picture of classification errors -- which classes are confused with which.

**Intuition:** A chart showing "When the answer was A, how many students said A, B, C, D, E?" Diagonal = correct; off-diagonal = errors.

```
                    PREDICTED
               A    B    C    D    E
          +----+----+----+----+----+
ACTUAL A  | TP |    |    |    |    |   <- diagonal = correct
       B  |    | TP |    |    |    |
       C  |    |    | TP |    |    |   off-diagonal = errors
       D  |    |    |    | TP |    |
       E  |    |    |    |    | TP |
          +----+----+----+----+----+
```

**Pros/Cons:**
- (+) Reveals systematic confusions; foundation for all classification metrics
- (-) Hard to compare across models (table, not number); grows as NxN

---

## Metric 6: BLEU (Bilingual Evaluation Understudy)

Measures n-gram precision of generated text against a reference, with a brevity penalty for short outputs.

**Intuition:** Count how many phrases (1-word through 4-word) from the student's essay also appear in the model answer. More shared phrases = higher BLEU.

```
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
```

```
Reference: "The cat sat on the mat"
Hypothesis: "The cat on the mat sat"

Unigrams (BLEU-1): Match 6/6 = 1.000
Bigrams (BLEU-2):  Match 3/5 = 0.600 ("cat on" and "mat sat" not in ref)
```

**Pros/Cons:**
- (+) Fast, deterministic, reproducible; good corpus-level correlation for translation
- (-) Precision-only (no recall); no semantic understanding; sentence-level unreliable

---

## Metric 7: ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

Recall counterpart to BLEU -- measures how much of the reference content is captured in the hypothesis.

**Intuition:** BLEU asks "How much of hypothesis is in reference?" (precision). ROUGE asks "How much of reference is in hypothesis?" (recall). ROUGE-L uses longest common subsequence.

```
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
```

**Pros/Cons:**
- (+) Recall-focused; ROUGE-L captures ordering; reports P, R, and F1
- (-) Surface-level overlap only (no semantics); poor at paraphrases

---

## Metric 8: METEOR (Metric for Evaluation of Translation with Explicit ORdering)

Addresses BLEU's inability to credit synonyms or word variations; aligns words via exact match, stemming, and synonyms, then penalizes fragmentation.

**Intuition:** A teacher who gives credit for synonyms ("big"="large") and word forms ("running"="ran"), but penalizes scrambled word order.

```
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
```

**Pros/Cons:**
- (+) Handles synonyms/morphology; fragmentation penalty rewards fluency; better human correlation than BLEU
- (-) Requires synonym tables and stemmer (language-dependent); slower than BLEU

---

## Metric 9: CIDEr (Consensus-based Image Description Evaluation)

Measures how well a generated caption matches the consensus among multiple references using TF-IDF weighted n-grams.

**Intuition:** If 5 people describe a photo and all say "sunset over ocean", CIDEr rewards matching that consensus. Common words ("the") get downweighted; distinctive words ("sunset") get upweighted.

```
TF-IDF weighted n-gram vectors:
  TF(ngram)  = count(ngram) / total_ngrams_in_doc
  IDF(ngram) = log( num_docs / doc_freq(ngram) )
  g_n(s)     = TF-IDF vector for sentence s at n-gram order n

CIDEr_n = (1/M) * SUM_i( cosine_sim(g_n(hyp), g_n(ref_i)) )

CIDEr = (1/N) * SUM_n( CIDEr_n )    (averaged over n-gram orders)

Convention: multiply by 10 for scaling.
```

**Pros/Cons:**
- (+) TF-IDF emphasizes informative content; handles multiple references naturally
- (-) Requires multiple references for best results; can overweight rare n-grams

---

## Metric 10: BERTScore (Simplified)

Uses contextual BERT embeddings for token-level semantic similarity, capturing meaning beyond exact word overlap.

**Intuition:** Instead of matching exact words, asks "Do words in the hypothesis have similar MEANINGS to words in the reference?" using BERT embeddings. Like a bilingual translator judging similarity instead of a word-matching machine.

```
Real BERTScore:
  1. ref_embeddings = BERT(reference)    # contextual vectors for each token
  2. hyp_embeddings = BERT(hypothesis)

  Precision = (1/|hyp|) * SUM_h( max_r( cosine_sim(h, r) ) )
  Recall    = (1/|ref|) * SUM_r( max_h( cosine_sim(r, h) ) )
  F1        = 2 * P * R / (P + R)
```

**Pros/Cons:**
- (+) Captures semantic similarity (synonyms, paraphrases); strong human correlation
- (-) Requires GPU; not interpretable; depends on BERT model used

---

## Metric 11: BLEURT (BERT-based Learned Evaluation Understudy for Text)

Fine-tunes BERT on human quality judgments to directly predict text quality scores, learning nuances no handcrafted formula can capture.

**Intuition:** BERTScore is like a dictionary checking word meanings. BLEURT is like a trained human judge who has read thousands of evaluations and implicitly learned grammar, coherence, and factuality.

```
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
```

**Pros/Cons:**
- (+) Learns from human judgments; single score output; robust via synthetic pre-training
- (-) Large checkpoint required; biased toward WMT data; black-box; expensive at scale

---

## Metric 12: MoverScore (Word Mover's Distance)

Frames text similarity as optimal transport: minimum "effort" to transform hypothesis word distribution into reference word distribution in embedding space.

**Intuition:** Piles of dirt (hypothesis words) and holes to fill (reference words) in meaning-space. MoverScore is the minimum total distance to move dirt into holes. Similar texts require less movement.

```
Word Mover's Distance (WMD):
  min SUM( T_ij * c(w_i, w_j) )

subject to:
  SUM_j(T_ij) = d_i   (supply constraint)
  SUM_i(T_ij) = d_j   (demand constraint)

where:
  T_ij   = amount of word i transported to word j
  c(i,j) = 1 - cosine_sim(embedding_i, embedding_j)
  d_i    = weight of word i (usually 1/|text|)

MoverScore = 1 - normalized_WMD
```

**Pros/Cons:**
- (+) Captures semantic similarity via optimal transport; handles reordering naturally
- (-) Computationally expensive O(n^3); requires good word embeddings

---

## Metric 13: Exact Match

Strictest text metric: prediction must be EXACTLY the same as reference (after optional normalization). No partial credit.

**Intuition:** Like a password check. "New York" and "new york" match with case normalization. "New York City" vs "New York" = no match.

```
EM(ref, hyp) = 1  if normalize(ref) == normalize(hyp)
               0  otherwise

Normalization (optional): lowercase + strip whitespace

EM_score = (1/N) * SUM( EM(ref_i, hyp_i) )
```

**Pros/Cons:**
- (+) Unambiguous, no tunable parameters, fast, perfect for factoid QA
- (-) No partial credit ("Barack Obama" vs "Obama" = 0); sensitive to formatting

---

## Metric 14: Token F1

Gives partial credit for overlapping tokens, complementing Exact Match in extractive QA.

**Intuition:** Like partial-credit grading. If the answer is 3 words and the student gets 2 right, they deserve some points.

```
common_tokens = tokens shared between reference and hypothesis

               |common_tokens|
Precision = ----------------------
            |hypothesis_tokens|

               |common_tokens|
Recall    = ----------------------
            |reference_tokens|

F1 = 2 * Precision * Recall / (Precision + Recall)
```

| Prediction          | EM    | Token-F1 |
|---------------------|-------|----------|
| "Barack Obama"      | 1.00  | 1.00     |
| "Obama"             | 0.00  | 0.67     |
| "President Obama"   | 0.00  | 0.67     |
| "Donald Trump"      | 0.00  | 0.00     |

**Pros/Cons:**
- (+) Partial credit; simple and fast; standard in SQuAD evaluation
- (-) Bag-of-words (ignores order); no semantic understanding; treats all tokens equally

---

## Metric 15: Perplexity

Measures how "surprised" a language model is by a text. Lower perplexity = model expected what it saw.

**Intuition:** Perplexity of 10 means the model is as confused as choosing randomly among 10 equally likely options at each step. Perplexity of 1 = perfect prediction.

```
PP(W) = exp( -(1/N) * SUM( log P(w_i | context) ) )

Equivalently: PP(W) = P(w_1, w_2, ..., w_N) ^ (-1/N)

where:
  W     = the text (sequence of words)
  N     = number of words
  P(w_i | context) = probability of word i given its context

Relationship to Cross Entropy:
  PP = exp(H)  = 2^(H / ln2)
  where H = cross entropy of the language model
```

```
Perplexity Scale:
|  1.0 -------- Perfect prediction (impossible in practice)
| ~10  -------- Excellent LM (GPT-4 on clean English)
| ~50  -------- Good LM
| ~100 -------- Reasonable LM
| ~500 -------- Weak LM
| |V|  -------- Random guessing (V = vocabulary size)
Lower is better
```

**Pros/Cons:**
- (+) Standard LM metric; mathematically principled (information theory)
- (-) Only measures the model, not generation quality; sensitive to vocabulary/tokenization; low PP does not guarantee good generation

---

## Metric 16: Cross Entropy

Measures the gap between the true label distribution and the model's predicted probabilities. Standard training loss for classifiers and language models.

**Intuition:** Average bits needed when your coding scheme uses the model's predictions (q) but the actual data follows distribution (p). If q matches p, cross entropy equals entropy of p (minimum).

```
General form:
  H(p, q) = -SUM( p(x) * log(q(x)) )

Classification (one-hot labels):
  CE = -(1/N) * SUM( log( q(correct_class_i) ) )

where:
  p(x) = true distribution (usually one-hot for classification)
  q(x) = predicted probability distribution

Relationship to Perplexity:  PP = exp(CE)
```

**Pros/Cons:**
- (+) Standard training loss; penalizes confident wrong predictions heavily; directly related to perplexity
- (-) Requires probability estimates; sensitive to calibration; not bounded; hard to interpret alone

---

## Metric 17: Calibration (Expected Calibration Error)

Measures whether a model's confidence scores match reality -- when it says "80% confident", is it correct 80% of the time?

**Intuition:** A weather forecaster saying "70% chance of rain" should be right 7/10 times. ECE measures overall miscalibration.

```
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
```

```
Perfect Calibration (ECE=0):     Overconfident Model:
Acc                              Acc
1.0|        /                    1.0|        .
   |      /                        |      .
   |    /   <- y=x line            |    .    <- below diagonal
   |  /                            |  .  /
   |/                              |./  /
---+---------> Conf                +---------> Conf
   0       1.0                     0       1.0
```

**Pros/Cons:**
- (+) Measures trustworthiness of probabilities; essential for decision-making systems
- (-) Sensitive to bin count; requires large samples; can be gamed via temperature scaling

---

## Summary: All 17 Metrics at a Glance

| #  | Metric            | Type        | Range     | Best For               |
|----|-------------------|-------------|-----------|------------------------|
| 1  | Accuracy          | Classif.    | [0, 1]    | Balanced datasets      |
| 2  | Precision         | Classif.    | [0, 1]    | Low false positive cost|
| 3  | Recall            | Classif.    | [0, 1]    | Low false negative cost|
| 4  | F1 Score          | Classif.    | [0, 1]    | Balancing P & R        |
| 5  | Confusion Matrix  | Classif.    | counts    | Error analysis         |
| 6  | BLEU              | Generation  | [0, 1]    | Machine translation    |
| 7  | ROUGE             | Generation  | [0, 1]    | Summarization          |
| 8  | METEOR            | Generation  | [0, 1]    | Translation (semantic) |
| 9  | CIDEr             | Generation  | [0, 10]   | Image captioning       |
| 10 | BERTScore         | Generation  | [0, 1]    | Semantic similarity    |
| 11 | BLEURT            | Generation  | [-1, 1]*  | Learned quality        |
| 12 | MoverScore        | Generation  | [0, 1]    | Optimal transport sim  |
| 13 | Exact Match       | Extractive  | {0, 1}    | Factoid QA (SQuAD)     |
| 14 | Token F1          | Extractive  | [0, 1]    | Extractive QA (SQuAD)  |
| 15 | Perplexity        | LM Eval     | [1, inf)  | Language model quality |
| 16 | Cross Entropy     | LM / Loss   | [0, inf)  | Training loss          |
| 17 | Calibration (ECE) | Probabilit. | [0, 1]    | Confidence reliability |

*BLEURT range depends on implementation; simplified version is [0, 1].

---

## Interview Questions

**Q1: Why is accuracy alone insufficient for evaluating an LLM on an imbalanced dataset?**
A model always predicting the majority class achieves high accuracy without learning anything. Macro F1 reveals minority-class performance that accuracy hides.

**Q2: What is the key difference between BLEU and ROUGE?**
BLEU is precision-oriented (hypothesis n-grams in reference); ROUGE is recall-oriented (reference n-grams in hypothesis). BLEU for translation, ROUGE for summarization.

**Q3: Why does METEOR often correlate better with human judgment than BLEU?**
METEOR handles synonyms, stemming, and word order (fragmentation penalty), while BLEU only does exact n-gram matching.

**Q4: What is the relationship between cross entropy and perplexity?**
Perplexity = exp(Cross Entropy). Minimizing CE during training directly minimizes perplexity.

**Q5: Why is calibration important for LLM deployment?**
Production systems use confidence thresholds to decide when to trust the model vs. escalate to a human. Overconfident models make these thresholds unreliable.

**Q6: How does BERTScore improve over surface-level metrics like BLEU and ROUGE?**
BERTScore uses contextual embeddings for token-level cosine similarity, giving credit to synonyms and paraphrases that share no surface overlap.

**Q7: In SQuAD evaluation, why are both Exact Match and Token F1 reported?**
EM measures perfect span extraction; Token F1 gives partial credit. Together they show precision and robustness of span boundaries.

**Q8: What is the F-beta score and when would you use F2 vs F0.5?**
F-beta = (1+beta^2)*(P*R)/(beta^2*P+R). F2 weights recall more (disease screening); F0.5 weights precision more (spam detection).

**Q9: What is the difference between micro and macro F1?**
Micro pools all TP/FP/FN globally (sample-weighted, majority-class dominated). Macro averages per-class F1 (class-weighted, better for minority classes).

**Q10: Can a model have low perplexity but still generate poor text?**
Yes. Perplexity measures prediction, not generation quality. A model can memorize training data (low PP) yet produce repetitive or factually incorrect outputs.

---

## Key Takeaway

No single metric tells the whole story. Classification needs P, R, F1 alongside accuracy. Text generation benefits from combining surface metrics (BLEU, ROUGE) with semantic metrics (BERTScore, BLEURT). Probabilistic metrics (perplexity, CE, calibration) are essential for understanding model confidence.
