# Chapter 2: Classical NLP Metrics

A comprehensive walk-through of 17 classical NLP evaluation metrics.

---

## Metric 1: Accuracy

### What Problem Does It Solve?

Accuracy answers the most basic question in evaluation: "What fraction of the time did the model get it right?" It is the starting point for any classification or MCQ evaluation. However, it can be misleading on imbalanced datasets where always predicting the majority class yields high accuracy.

### Intuition

Imagine a 10-question quiz. If a student gets 7 right, their accuracy is 70%. Simple count of hits divided by total attempts. Like checking your exam score — no partial credit, no nuance.

### Formula

```
              Number of correct predictions
Accuracy = ------------------------------------
              Total number of predictions

Accuracy = (1/N) * SUM( I(y_i == y_hat_i) )

where:
  N       = total predictions
  y_i     = ground truth label for sample i
  y_hat_i = predicted label for sample i
  I(...)  = indicator function (1 if true, 0 if false)
```

### ASCII Diagram

```
Good model (10 questions):
[C][C][C][C][C][C][C][C][C][X]   C=correct, X=wrong
 ^  ^  ^  ^  ^  ^  ^  ^  ^  ^
 D  B  E  D  C  E  A  D  A  C   (predictions match ground truth)
Accuracy = 9/10 = 90%
```

### Advantages

- Simplest metric to understand and communicate
- Works for any number of classes
- No hyperparameters

### Limitations

- Misleading on imbalanced datasets (e.g., 95% class A → always predict A = 95%)
- No distinction between types of errors (false positive vs false negative)
- No partial credit for "almost right" answers

---

## Metric 2: Precision

### What Problem Does It Solve?

Precision answers: "When the model predicts class X, how often is it actually class X?" It measures the quality of positive predictions. High precision means few false alarms. This is critical when false positives are costly — e.g., spam filters (flagging legitimate email as spam is annoying), or medical diagnosis (false cancer diagnosis causes unnecessary anxiety).

### Intuition

A sniper analogy: precision is like asking "Of all the shots fired, how many hit the target?" A precise model does not cry wolf — when it makes a claim, you can trust it.

### Formula

```
                   True Positives (TP)
Precision_C = --------------------------------
              True Positives + False Positives

                  TP_C
Precision_C = -----------
              TP_C + FP_C

where (for class C):
  TP_C = correctly predicted as C
  FP_C = incorrectly predicted as C (actually another class)
```

### Advantages

- Focuses on the quality of positive predictions
- Essential when false positives are costly
- Works per-class (can identify weak spots)

### Limitations

- Ignores false negatives (model could miss everything and have 100% precision)
- Must be paired with recall for a complete picture
- A model that predicts class C only once (and gets it right) has 100% precision

---

## Metric 3: Recall

### What Problem Does It Solve?

Recall answers: "Of all the actual instances of class X, how many did the model find?" It measures completeness of detection. High recall means few missed cases. Critical when false negatives are dangerous — e.g., disease screening (missing a cancer case is worse than a false alarm).

### Intuition

A search-and-rescue analogy: recall is like asking "Of all the survivors in the area, how many did the team actually find?" You want to find everyone — missing someone is the worst outcome.

### Formula

```
                 True Positives (TP)
Recall_C = --------------------------------
           True Positives + False Negatives

                TP_C
Recall_C = -----------
           TP_C + FN_C

where (for class C):
  TP_C = correctly predicted as C
  FN_C = actually C but predicted as something else
```

### Precision vs Recall Trade-off

```
High Precision, Low Recall:         High Recall, Low Precision:
Model is CONSERVATIVE               Model is AGGRESSIVE
"I only speak when I'm sure"        "I flag everything just in case"

+----------+                         +----------+
|    TP    |  <- Few predictions     |  TP | FP |  <- Many predictions
|          |     but accurate        |    |    |     catches everything
+----------+                         +----+----+
| FN | TN  |  <- Misses many         |   TN    |  <- Few misses
+----+-----+                         +---------+
```

### Advantages

- Measures completeness of detection
- Critical for safety-sensitive applications
- Complements precision

### Limitations

- A model that predicts everything as class C has 100% recall for C
- Must be paired with precision
- Does not account for false positives

---

## Metric 4: F1 Score

### What Problem Does It Solve?

F1 balances precision and recall into a single number using their harmonic mean. It solves the problem of trading off precision vs recall. The harmonic mean punishes extreme imbalance: if either precision or recall is low, F1 will be low.

### Intuition

If precision is the "sharpness" of a tool and recall is its "coverage", F1 is like asking "overall, how good is this tool?" A surgeon's scalpel with 100% precision but 1% recall is useless. A bulldozer with 100% recall but 10% precision destroys everything. F1 demands both.

### Formula

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

### Advantages

- Balances precision and recall in one number
- Harmonic mean penalizes extreme values
- Multiple variants for different needs (micro/macro/weighted)

### Limitations

- Assumes precision and recall are equally important (use F-beta for other weights)
- Macro F1 can be unstable with few samples per class
- Does not account for true negatives

---

## Metric 5: Confusion Matrix

### What Problem Does It Solve?

A confusion matrix shows the FULL picture of classification errors. While accuracy, precision, and recall are single numbers, the confusion matrix reveals exactly which classes are being confused with which. It answers: "When the model gets it wrong, what does it predict instead?"

### Intuition

Think of a teacher grading student responses. The confusion matrix is like a chart showing: "When the answer was A, how many students said A, B, C, D, or E?" The diagonal shows correct answers; off-diagonal cells show specific confusions.

### Structure

```
                    PREDICTED
               A    B    C    D    E
          +----+----+----+----+----+
ACTUAL A  | TP |    |    |    |    |   <- diagonal = correct
       B  |    | TP |    |    |    |
       C  |    |    | TP |    |    |   off-diagonal = errors
       D  |    |    |    | TP |    |   (which class it was confused with)
       E  |    |    |    |    | TP |
          +----+----+----+----+----+
```

### Advantages

- Shows COMPLETE error patterns (not just a single number)
- Reveals systematic confusions between specific classes
- Foundation for computing all classification metrics

### Limitations

- Harder to compare across models (it's a table, not a number)
- Grows as NxN with N classes (impractical for 1000+ classes)
- Doesn't directly suggest what to fix

---

## Metric 6: BLEU (Bilingual Evaluation Understudy)

### What Problem Does It Solve?

BLEU measures how much a generated text overlaps with a reference text at the n-gram level. Originally designed for machine translation, it became the first widely-used automatic metric for text generation. It is precision-oriented: it checks what fraction of the generated n-grams appear in the reference.

### Intuition

Imagine comparing a student's essay to a model answer. BLEU counts how many phrases (1-word, 2-word, 3-word, 4-word) from the student's essay also appear in the model answer. More shared phrases = higher BLEU. A short but accurate summary gets a brevity penalty.

### Formula

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

### ASCII Diagram

```
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
```

### Advantages

- Fast, deterministic, and reproducible
- Correlates reasonably well with human judgment for translation
- N-gram matching captures phrase-level quality

### Limitations

- Precision-only (ignores how much of reference is covered → see ROUGE)
- No semantic understanding (synonyms get zero credit)
- Sentence-level BLEU is unreliable (designed for corpus-level)
- Brevity penalty is crude

---

## Metric 7: ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

### What Problem Does It Solve?

ROUGE is the recall counterpart to BLEU. While BLEU asks "How much of the hypothesis is in the reference?" (precision), ROUGE asks "How much of the reference is captured in the hypothesis?" (recall). Designed for summarization evaluation where coverage of key content matters.

### Intuition

If a teacher writes 10 key points, ROUGE checks how many the student mentioned. BLEU checks how many of the student's points are valid. ROUGE-L uses the longest common subsequence — the longest chain of words that appear in the same order in both texts.

### Formula

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

### BLEU vs ROUGE Comparison

```
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
```

### Advantages

- Recall-focused: measures content coverage
- ROUGE-L captures ordering without fixed n-gram size
- Reports precision, recall, AND F1 (more complete than BLEU)

### Limitations

- Still based on surface-level overlap (no semantics)
- Does not handle paraphrasing well
- Multiple reference handling varies by implementation

---

## Metric 8: METEOR (Metric for Evaluation of Translation with Explicit ORdering)

### What Problem Does It Solve?

METEOR addresses BLEU's key weakness: no credit for synonyms or word variations. It aligns words between reference and hypothesis using exact match, stemming, and synonym lookup. It also penalizes fragmented matches, rewarding fluent translations.

### Intuition

Imagine a teacher who gives credit not just for exact words but also for synonyms ("big" = "large") and word forms ("running" = "ran"). METEOR also checks if matching words appear in the same order — a scrambled but word-perfect answer gets a penalty.

### Formula

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

### Advantages

- Handles synonyms and morphological variations
- Fragmentation penalty rewards fluency
- Better correlation with human judgments than BLEU (at sentence level)

### Limitations

- Requires synonym tables and stemmer (language-dependent)
- Slower than BLEU due to alignment
- Parameters (alpha, beta, gamma) need tuning per language

---

## Metric 9: CIDEr (Consensus-based Image Description Evaluation)

### What Problem Does It Solve?

CIDEr measures how well a generated caption matches the consensus among multiple reference captions. It uses TF-IDF weighting to emphasize informative n-grams (rare, distinctive words) over common ones. Designed for image captioning where multiple valid descriptions exist.

### Intuition

If 5 people describe a photo and all say "sunset over ocean", those words are the consensus. CIDEr rewards a hypothesis that captures this consensus. Common words like "the" and "is" get downweighted (low IDF), while distinctive words like "sunset" get upweighted.

### Formula

```
TF-IDF weighted n-gram vectors:
  TF(ngram)  = count(ngram) / total_ngrams_in_doc
  IDF(ngram) = log( num_docs / doc_freq(ngram) )
  g_n(s)     = TF-IDF vector for sentence s at n-gram order n

CIDEr_n = (1/M) * SUM_i( cosine_sim(g_n(hyp), g_n(ref_i)) )

CIDEr = (1/N) * SUM_n( CIDEr_n )    (averaged over n-gram orders)

Convention: multiply by 10 for scaling.
```

### Advantages

- TF-IDF weighting emphasizes important content words
- Handles multiple references naturally (consensus-based)
- Good correlation with human judgments for captioning

### Limitations

- Requires multiple references per example for best results
- TF-IDF is computed on the test set (no external corpus)
- Can overweight rare n-grams that happen to match

---

## Metric 10: BERTScore (Simplified)

### What Problem Does It Solve?

BERTScore addresses the fundamental limitation of all surface-level metrics: they cannot detect semantic similarity. "The cat sat on the mat" and "A feline rested on the rug" share meaning but few n-grams. BERTScore uses contextual embeddings from BERT to compute token-level similarity, capturing meaning beyond exact word overlap.

### Intuition

Instead of matching exact words, BERTScore asks: "Do the words in the hypothesis have similar MEANINGS to words in the reference?" It uses BERT to understand each word in context, then finds the best semantic match for each word. Like having a bilingual translator judge similarity instead of a word-matching machine.

### Formula

```
Real BERTScore:
  1. ref_embeddings = BERT(reference)    # contextual vectors for each token
  2. hyp_embeddings = BERT(hypothesis)

  Precision = (1/|hyp|) * SUM_h( max_r( cosine_sim(h, r) ) )
  Recall    = (1/|ref|) * SUM_r( max_h( cosine_sim(r, h) ) )
  F1        = 2 * P * R / (P + R)
```

### Architecture Diagram

```
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
```

### Advantages

- Captures semantic similarity (synonyms, paraphrases)
- Contextual (same word in different contexts gets different embeddings)
- Strong correlation with human judgments across tasks

### Limitations

- Requires GPU for fast inference (BERT is large)
- Not interpretable (why did two tokens get high similarity?)
- Depends on the BERT model used (different models → different scores)

---

## Metric 11: BLEURT (BERT-based Learned Evaluation Understudy for Text)

### What Problem Does It Solve?

BLEURT goes beyond BERTScore by LEARNING what makes text quality good. Instead of using a fixed similarity formula, BLEURT fine-tunes BERT on human quality judgments. The model learns to predict human scores directly, capturing nuances that no handcrafted formula can.

### Intuition

BERTScore is like a dictionary that checks if words mean the same thing. BLEURT is like a trained human judge who has read thousands of evaluations and learned what constitutes good text. The judge considers grammar, coherence, factuality, and more — all implicitly.

### Formula (Architecture)

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

### Advantages

- Learns from human judgments (captures subtle quality aspects)
- Single score output (easy to use)
- Pre-training on synthetic data makes it robust

### Limitations

- Requires downloading a large checkpoint
- Quality depends on the training data (biased toward WMT)
- Not interpretable (black-box regression)
- Expensive to compute at scale

---

## Metric 12: MoverScore (Word Mover's Distance)

### What Problem Does It Solve?

MoverScore frames text similarity as an optimal transport problem: What is the minimum "effort" needed to transform the hypothesis word distribution into the reference word distribution? It uses BERT embeddings as the space and Earth Mover's Distance (Wasserstein distance) as the transport cost.

### Intuition

Imagine you have piles of dirt (hypothesis words) and holes to fill (reference words). Each word has a position in meaning-space. MoverScore is the minimum total distance you need to "move" the dirt to fill all the holes. Similar texts require less movement.

### Formula

```
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
```

### Advantages

- Captures semantic similarity through optimal transport
- Handles reordering naturally (no n-gram constraint)
- Elegant mathematical framework

### Limitations

- Computationally expensive (optimal transport is O(n^3))
- Requires good word embeddings (BERT or similar)

---

## Metric 13: Exact Match

### What Problem Does It Solve?

Exact Match (EM) is the strictest text evaluation metric: the prediction must be EXACTLY the same as the reference. Used in extractive QA (SQuAD) where the model must extract the exact span from the passage. No partial credit — either perfect or zero.

### Intuition

Like a password check: either it matches exactly, or it is wrong. "New York" and "new york" match if we normalize case. "New York City" and "New York" do NOT match. Simple but strict.

### Formula

```
EM(ref, hyp) = 1  if normalize(ref) == normalize(hyp)
               0  otherwise

Normalization (optional): lowercase + strip whitespace

EM_score = (1/N) * SUM( EM(ref_i, hyp_i) )
```

### Advantages

- Unambiguous: no tunable parameters
- Fast to compute
- Perfect for factoid QA with single correct answer

### Limitations

- No partial credit ("Barack Obama" vs "Obama" = 0)
- Sensitive to formatting, punctuation, articles
- Cannot handle valid paraphrases or alternative phrasings

---

## Metric 14: Token F1

### What Problem Does It Solve?

Token F1 gives partial credit for overlapping tokens, complementing Exact Match. In extractive QA (SQuAD), if the reference is "Barack Obama" and the prediction is "President Barack Obama", Exact Match gives 0 but Token F1 gives credit for the two shared tokens.

### Intuition

Like a teacher grading a fill-in-the-blank with partial credit. If the answer is 3 words and the student gets 2 right, they deserve some points. Token F1 counts shared words, then computes the harmonic mean of precision and recall at the token level.

### Formula

```
common_tokens = tokens shared between reference and hypothesis
                (using minimum count for repeated tokens)

               |common_tokens|
Precision = ----------------------
            |hypothesis_tokens|

               |common_tokens|
Recall    = ----------------------
            |reference_tokens|

F1 = 2 * Precision * Recall / (Precision + Recall)
```

### Exact Match vs Token F1

| Prediction          | EM    | Token-F1 |
|---------------------|-------|----------|
| "Barack Obama"      | 1.00  | 1.00     |
| "Obama"             | 0.00  | 0.67     |
| "President Obama"   | 0.00  | 0.67     |
| "Barack"            | 0.00  | 0.67     |
| "Donald Trump"      | 0.00  | 0.00     |

Token F1 provides a smoother, more informative signal than EM.

### Advantages

- Gives partial credit (unlike Exact Match)
- Simple and fast
- Standard in extractive QA evaluation (SQuAD)

### Limitations

- Bag-of-words: ignores word order
- No semantic understanding (synonyms get zero credit)
- Treats all tokens equally (function words = content words)

---

## Metric 15: Perplexity

### What Problem Does It Solve?

Perplexity measures how "surprised" a language model is by a text. It is the standard evaluation metric for language models themselves (not for text generation quality). Lower perplexity means the model assigns higher probability to the text — it expected what it saw.

### Intuition

If perplexity is 10, the model is as confused as if it had to choose randomly among 10 equally likely options at each step. A perplexity of 1 means perfect prediction (zero surprise). A perplexity of |vocabulary| means uniform random guessing.

### Formula

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

### Perplexity Scale

```
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
```

### Advantages

- Standard metric for language model evaluation
- Mathematically principled (information theory)
- Comparable across different texts with same model

### Limitations

- Only measures the model, not generation quality
- Sensitive to vocabulary size and tokenization
- A model can have low perplexity but generate boring, repetitive text
- Not comparable across models with different vocabularies

---

## Metric 16: Cross Entropy

### What Problem Does It Solve?

Cross entropy measures the gap between two probability distributions: the true labels and the model's predicted probabilities. It is the standard loss function for training classifiers and language models. Lower cross entropy means the model's probability estimates are closer to the truth.

### Intuition

Imagine you need to design a code to transmit messages. Cross entropy is the average number of bits you need if you design your code based on the model's predictions (q) but the actual data follows a different distribution (p). If q matches p perfectly, cross entropy equals the entropy of p (minimum possible).

### Formula

```
General form:
  H(p, q) = -SUM( p(x) * log(q(x)) )

Classification (one-hot labels):
  CE = -(1/N) * SUM( log( q(correct_class_i) ) )

where:
  p(x) = true distribution (usually one-hot for classification)
  q(x) = predicted probability distribution
  q(correct_class_i) = model's confidence on the correct answer

Relationship to Perplexity:  PP = exp(CE)
```

### Cross Entropy vs KL Divergence

```
H(p, q) = H(p) + D_KL(p || q)

Cross Entropy = Entropy of true distribution
                + KL Divergence (extra bits due to using q instead of p)

When p is fixed (which it usually is in training):
  Minimizing Cross Entropy == Minimizing KL Divergence
```

### Advantages

- Standard training loss (gradient-friendly)
- Penalizes confident wrong predictions heavily (log scale)
- Mathematically principled (information theory)
- Directly related to perplexity (PP = exp(CE))

### Limitations

- Requires probability estimates (not just predictions)
- Sensitive to calibration (overconfident model gets punished)
- Not bounded (unlike accuracy which is 0-1)
- Hard to interpret in isolation (what is "good" CE?)

---

## Metric 17: Calibration (Expected Calibration Error)

### What Problem Does It Solve?

Calibration measures whether a model's confidence scores match reality. When a model says "80% confident", is it actually correct 80% of the time? A well-calibrated model's confidence is trustworthy. This is essential for decision-making systems where confidence thresholds determine actions.

### Intuition

A weather forecaster who says "70% chance of rain" should be right about 7 out of 10 times they make that prediction. If it rains only 3/10 times, they are overconfident. If it rains 9/10 times, they are underconfident. ECE measures this overall miscalibration.

### Formula

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

### Calibration Diagram Explanation

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

Points below the diagonal = overconfident (confidence > accuracy)
Points above the diagonal = underconfident (accuracy > confidence)
```

### Advantages

- Measures trustworthiness of probability estimates
- Essential for decision-making systems
- ECE is a single interpretable number
- Bin-level analysis reveals where miscalibration occurs

### Limitations

- Sensitive to the number of bins
- Requires large samples for reliable bin statistics
- ECE can be gamed (post-hoc temperature scaling fixes ECE but not the model)
- Does not measure discrimination (a constant predictor can be well-calibrated)

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

On an imbalanced dataset (e.g., 95% class A, 5% class B), a model that always predicts class A achieves 95% accuracy without learning anything useful. Precision, recall, and F1 (especially macro-averaged) reveal performance on minority classes that accuracy hides.

**Q2: What is the key difference between BLEU and ROUGE?**

BLEU is precision-oriented (what fraction of hypothesis n-grams appear in the reference), while ROUGE is recall-oriented (what fraction of reference n-grams appear in the hypothesis). BLEU penalizes short outputs (brevity penalty); ROUGE penalizes missing content. BLEU is standard for translation; ROUGE for summarization.

**Q3: Why does METEOR often correlate better with human judgment than BLEU?**

METEOR handles synonyms (large=big), stemming (running=ran), and word order (fragmentation penalty). BLEU only does exact n-gram matching. METEOR also computes both precision and recall with a recall-weighted F-mean, giving a more balanced assessment.

**Q4: What is the relationship between cross entropy and perplexity?**

Perplexity = exp(Cross Entropy). If a language model has cross entropy H on a text, its perplexity is e^H. Minimizing cross entropy during training directly minimizes perplexity. A cross entropy of 0 gives perplexity 1 (perfect prediction).

**Q5: Why is calibration important for LLM deployment?**

Calibration ensures that confidence scores are meaningful. In production, systems often use confidence thresholds to decide when to trust the model vs. escalate to a human. If a model is overconfident (says 95% confident but is only right 60% of the time), these thresholds become unreliable, leading to silent failures.

**Q6: How does BERTScore improve over surface-level metrics like BLEU and ROUGE?**

BERTScore uses contextual embeddings from BERT to compute token-level cosine similarity instead of exact n-gram matching. This means semantically similar words (synonyms, paraphrases) receive high similarity scores even without exact string overlap. It captures meaning, not just surface form.

**Q7: In SQuAD evaluation, why are both Exact Match and Token F1 reported?**

Exact Match is strict (all or nothing) and measures how often the model gets the answer perfectly right. Token F1 gives partial credit for overlapping tokens. Together, they show both the model's precision in extracting exact spans AND its ability to identify relevant content even when the boundaries are slightly off.

**Q8: What is the F-beta score and when would you use F2 vs F0.5?**

F-beta = (1+beta^2) * (P*R) / (beta^2*P + R). F2 (beta=2) weights recall 4x more than precision — use when missing positives is costly (disease screening). F0.5 (beta=0.5) weights precision 4x more than recall — use when false positives are costly (spam detection). F1 (beta=1) weights them equally.

**Q9: What is the difference between micro and macro F1?**

Micro F1 pools all true positives, false positives, and false negatives globally before computing F1. It weights each SAMPLE equally, so majority classes dominate. Macro F1 computes F1 per class and averages them, weighting each CLASS equally. Use macro F1 when minority class performance matters.

**Q10: Can a model have low perplexity but still generate poor text?**

Yes. Perplexity measures how well the model PREDICTS text, not how well it GENERATES text. A model can memorize training data (low perplexity) but produce repetitive, generic, or factually incorrect text when sampling. Perplexity also does not capture diversity, coherence, or factual correctness of generated text.

---

## Key Takeaway

No single metric tells the whole story. Classification tasks need precision, recall, and F1 alongside accuracy. Text generation tasks benefit from combining surface-level metrics (BLEU, ROUGE) with semantic metrics (BERTScore, BLEURT). And probabilistic metrics (perplexity, cross entropy, calibration) are essential for understanding model confidence and language modeling quality.
