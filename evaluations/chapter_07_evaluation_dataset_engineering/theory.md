# Chapter 7 -- Evaluation Dataset Engineering

Your model is only as good as the dataset you evaluate it on. This chapter covers how to design, validate, and maintain evaluation datasets you can trust.

---

## Topics Covered

1. Benchmark Design -- Balanced subset selection with topic/difficulty quotas
2. Dataset Quality Checks -- Completeness, correctness, consistency validation
3. Coverage Metrics -- Topic, difficulty, and answer distribution with entropy
4. Failure-Mode Coverage & Dataset Balancing -- Duplicates, answer skew, prompt outliers
5. Contamination Detection & Data Leakage -- Exact match, near-duplicate, answer leakage
6. Label Noise Detection -- Annotator disagreement and model-consensus methods
7. Cohen's Kappa -- Inter-rater agreement for 2 raters
8. Fleiss' Kappa -- Inter-rater agreement for N raters
9. Meta-Evaluation -- Evaluating the evaluation dataset itself

---

## 1. Benchmark Design

A benchmark is a carefully balanced subset of a question pool, like a well-designed exam that covers the syllabus fairly rather than testing one topic 50 times.

**How it works**: Classify questions by topic/difficulty, then select to match target distributions (e.g., 40% easy, 40% medium, 20% hard). Use a seed for reproducibility. Validate for minimum size (>=10), answer imbalance, duplicate prompts, and empty prompts.

**Key concepts**: target size, difficulty distribution, reproducibility via seed, post-design validation.

---

## 2. Dataset Quality Checks

Raw data often has missing fields, invalid labels, and inconsistent formatting that silently corrupt results.

**Three dimensions**:

- **Completeness**: Are required fields (`id`, `prompt`, `ground_truth`, choices) present and non-empty? Score: `1.0 - (issues / max_possible_issues)`
- **Correctness**: Are labels valid (A-E)? Does the answer option have corresponding text? Do prompts end with expected punctuation?
- **Consistency**: Are prompt lengths within normal range (flag >3 std devs)? Is choice count uniform?

**Overall**: `quality_score = max(0, 1.0 - total_issues / max_possible_issues)`

| Grade | Score Range |
|-------|-------------|
| A     | >= 0.95     |
| B     | >= 0.85     |
| C     | >= 0.70     |
| D     | >= 0.50     |
| F     | < 0.50      |

---

## 3. Coverage Metrics

A dataset might have 1000 questions but all on the same topic. Coverage ensures your test suite exercises all important dimensions.

### Topic Coverage

- **Coverage ratio**: `covered_topics / expected_topics`
- **Entropy**: `H = -SUM(p_i * log2(p_i))` where `p_i` = proportion in topic i
- **Normalized entropy**: `H / H_max` where `H_max = log2(num_topics)`

| Normalized Entropy | Interpretation |
|--------------------|----------------|
| > 0.9              | Excellent      |
| > 0.7              | Good           |
| > 0.5              | Fair           |
| <= 0.5             | Poor           |

### Difficulty Coverage

Ratio of `levels_with_questions / total_expected_levels`, with count and percentage per level.

### Answer Coverage

- **Coverage ratio**: `covered_options / total_options`
- **Balance score**: `1.0 - (max_deviation / total)`

### Overall Coverage

```
overall = topic_ratio * 0.4 + difficulty_ratio * 0.3 + answer_ratio * 0.3
```

Topic gets 40% weight because topic imbalance is the most common and damaging coverage failure.

---

## 4. Failure-Mode Coverage & Dataset Balancing

Even a complete-looking dataset can have hidden failure modes.

### Duplicate Detection

Near-duplicates detected using **Jaccard similarity**: `Jaccard(A, B) = |A INTER B| / |A UNION B|` on word sets. Threshold (e.g., 0.6) determines what counts as a near-duplicate. Duplicates inflate apparent diversity and give unfair weight to certain question types.

### Answer Distribution (Balance Check)

- **Expected**: `100 / num_options` per option
- **Chi-squared**: `SUM((observed_i - expected_i)^2 / expected_i)` -- high value = significant imbalance
- If answer "B" appears 40% instead of expected 20%, models can exploit the pattern.

### Prompt Length Analysis

Computes min, max, mean, median, std, percentiles. Extreme outliers may indicate truncated text or boilerplate.

---

## 5. Contamination Detection & Data Leakage

Contamination = test data leaking into training data, inflating scores. Like a student getting the exam paper before the test.

### Types

1. **Exact match**: Same question verbatim in train and test
2. **Near-duplicate**: Rephrased version in both sets
3. **Answer leakage**: Test answers visible during training
4. **Indirect leakage**: Training on source material of test questions

### Detection Methods

**Exact match**: Compare normalized (lowercased, stripped) prompts. Flagged as critical severity.

**Near-duplicate**: Combined score = `0.5 * jaccard + 0.5 * ngram_overlap` where `ngram_overlap = |ngrams_A INTER ngrams_B| / min(|ngrams_A|, |ngrams_B|)` (default N=3).

**Answer leakage**: Compare answer distributions between train/test -- suspiciously identical distributions suggest systematic leakage.

### Contamination Rate & Risk

```
contamination_rate = total_contaminated / test_set_size
```

| Rate   | Risk Level |
|--------|------------|
| > 10%  | CRITICAL   |
| > 5%   | HIGH       |
| > 1%   | MEDIUM     |
| <= 1%  | LOW        |

---

## 6. Label Noise Detection

Label noise = incorrect ground-truth labels. Even 5-10% noise significantly distorts results. If the answer key says 2+2=5, every correct model gets marked wrong.

### Method 1: Annotator Disagreement

Compare ground truth to majority vote of multiple annotators. If they disagree beyond a threshold (e.g., 0.5), flag as suspicious.

### Method 2: Model Consensus

Run multiple independent models on the same questions. If consensus rate exceeds threshold (e.g., 0.66) and differs from ground truth, flag the item.

### Noise Rate

```
noise_rate = mismatches / total_checked
```

| Noise Rate | Interpretation |
|------------|----------------|
| < 2%       | Clean          |
| < 5%       | Acceptable     |
| < 10%      | Moderate -- review recommended |
| >= 10%     | High -- significant issues |

---

## 7. Cohen's Kappa -- Inter-Rater Agreement (2 Raters)

Measures whether two annotators genuinely agree beyond chance. If 90% of students pass, even random grading agrees ~82% of the time -- raw agreement is misleading.

### Formula

```
kappa = (P_o - P_e) / (1 - P_e)
```

- **P_o** = observed agreement (fraction where raters agree)
- **P_e** = expected chance agreement = `SUM(p_rater1_c * p_rater2_c)` for each category c

### Computation Steps

1. Build confusion matrix of category assignments
2. P_o = diagonal sum / total
3. P_e = sum of (row marginal proportion * column marginal proportion) per category
4. Apply formula

### Interpretation Scale

| Kappa Value | Interpretation |
|-------------|----------------|
| < 0.00      | Less than chance |
| 0.00 - 0.20 | Slight         |
| 0.21 - 0.40 | Fair           |
| 0.41 - 0.60 | Moderate       |
| 0.61 - 0.80 | Substantial    |
| 0.81 - 1.00 | Almost perfect |

---

## 8. Fleiss' Kappa -- Inter-Rater Agreement (N Raters)

Generalizes Cohen's Kappa to 3+ raters labeling the same items.

### Formula

```
kappa = (P_bar - P_e_bar) / (1 - P_e_bar)
```

### Computation Steps

For N items, k categories, n raters per item, with `n_ij` = raters assigning item i to category j:

1. **P_i per item**: `P_i = (1/(n*(n-1))) * (SUM_j(n_ij^2) - n)`
2. **P_bar** (mean observed): `(1/N) * SUM_i(P_i)`
3. **p_j** (category proportions): `(1/(N*n)) * SUM_i(n_ij)`
4. **P_e_bar** (expected chance): `SUM_j(p_j^2)`
5. **Kappa**: `(P_bar - P_e_bar) / (1 - P_e_bar)`

### Interpretation Scale

Same as Cohen's Kappa (see table above).

### Cohen's vs Fleiss' Kappa

| Feature | Cohen's | Fleiss' |
|---------|---------|---------|
| Raters | Exactly 2 | 2 or more |
| Input | Two label lists | Matrix of category counts |
| Chance correction | Yes | Yes |
| Use case | Pairwise comparison | N-annotator assessment |

---

## 9. Meta-Evaluation -- Evaluating the Evaluator

Before using a dataset to judge models, verify the dataset itself is trustworthy. Check the ruler before measuring.

### Dimensions Scored

1. **Quality** -- from DatasetQualityChecker
2. **Coverage** -- from CoverageAnalyzer
3. **Label Quality** -- `max(0, 1.0 - noise_rate * 5)` (20% noise = 0.0 score)

**Overall**: `mean(dimension_scores)`

| Grade | Score Range |
|-------|-------------|
| A     | >= 0.90     |
| B     | >= 0.80     |
| C     | >= 0.65     |
| D     | >= 0.50     |
| F     | < 0.50      |

### Recommendations Engine

Auto-generated based on scores: fix quality issues if <0.9, improve coverage if <0.7, review labels if noise >5%.

### Evaluator Reliability (Coefficient of Variation)

Run the evaluator multiple times with different seeds, then: `CV = std_dev / mean`

| CV Value | Interpretation |
|----------|----------------|
| < 0.05   | Highly reliable |
| < 0.10   | Reliable |
| < 0.20   | Moderately reliable |
| >= 0.20  | Unreliable |

---

## Summary Table

```
Metric                          Value
------------------------------  ----------
Dataset quality score/grade     (from quality checker)
Coverage score                  (weighted average)
Topic/Difficulty/Answer coverage (ratios)
Contamination rate              (contaminated/test_size)
Label noise rate                (mismatches/total)
Cohen's Kappa (2 raters)        (kappa value)
Fleiss' Kappa (N raters)        (kappa value)
Meta-eval overall               (mean of dimensions)
Evaluator reliability (CV)      (coefficient of variation)
```

---

## Comparison of All Techniques

| Technique | Measures | Input | Output | When to Use |
|-----------|----------|-------|--------|-------------|
| Benchmark Design | Balanced subset selection | Question pool | Structured benchmark | Before evaluation |
| Quality Checks | Completeness/correctness | Dataset items | Issue report + score | Every dataset |
| Coverage Analysis | Topic/difficulty/answer spread | Dataset + dimensions | Ratios + entropy | Building/auditing datasets |
| Duplicate Detection | Redundant questions | Prompt pairs | Similarity scores | Before finalizing |
| Contamination Detection | Train-test leakage | Train + test sets | Contamination rate | Before model comparison |
| Label Noise Detection | Incorrect ground truths | Annotations/predictions | Suspicious items | When annotation quality uncertain |
| Cohen's Kappa | 2-rater agreement | Two label lists | Kappa score | Pairwise annotator comparison |
| Fleiss' Kappa | N-rater agreement | Rating matrix | Kappa score | Multi-annotator assessment |
| Meta-Evaluation | Dataset trustworthiness | All above results | Scorecard + recommendations | Final validation |

---

## Common Mistakes

1. **Using raw accuracy for annotator agreement** -- ignores chance. Always use Kappa.
2. **Ignoring contamination** -- even near-duplicates leak information. Check exact + near-duplicate.
3. **Assuming answer key is correct** -- use label noise detection to find mislabeled items.
4. **No coverage checks** -- 100 physics + 2 biology questions is not a "science" benchmark.
5. **Not checking balance** -- if 50% of answers are "B", models exploit the pattern.
6. **One-time evaluation** -- datasets need versioning, drift detection, periodic re-validation.
7. **Confusing Cohen's/Fleiss' Kappa** -- Cohen's = 2 raters only, Fleiss' = N raters.
8. **Ignoring prompt length outliers** -- may indicate truncated text or boilerplate.
9. **No seed for reproducibility** -- always set a seed for benchmark design and simulation.
10. **Evaluating evaluator only once** -- run multiple times; high CV = unstable results.

---

## Best Practices

1. Design benchmarks with explicit difficulty quotas (e.g., 40/40/20).
2. Automate quality checks -- run them on every dataset, every time.
3. Measure coverage with entropy, not just counts. 6 topics with 90% in one = low entropy.
4. Remove duplicates before evaluation (Jaccard similarity with appropriate threshold).
5. Check contamination between every pair of splits (train/test, train/val, fine-tune/eval).
6. Use 3+ annotators and report Fleiss' Kappa. Aim for Kappa > 0.6.
7. Combine annotator disagreement AND model consensus for noise detection.
8. Version your datasets -- new version on every fix/addition/removal.
9. Report meta-evaluation scores alongside model scores.
10. Automate all checks in CI/CD.

---

## Interview Questions

1. **Benchmark dataset vs evaluation dataset?**
   Benchmark = carefully balanced subset with defined scope, coverage targets, difficulty distribution. Evaluation dataset = any dataset used for evaluation, may lack these properties.

2. **Why is raw percentage agreement insufficient?**
   It ignores chance agreement. With 90% of items in one class, random annotators agree ~82%. Kappa corrects for this.

3. **What is data contamination?**
   Test data leaking into training data, inflating scores. The model memorizes leaked answers rather than genuinely generalizing.

4. **How to detect label noise?**
   (a) Annotator disagreement -- majority vote differs from ground truth. (b) Model consensus -- multiple models consistently predict a different answer.

5. **Explain Cohen's Kappa formula.**
   `kappa = (P_o - P_e) / (1 - P_e)`. P_o = observed agreement rate. P_e = expected chance agreement from marginal distributions. Measures excess agreement beyond chance.

6. **When Fleiss' Kappa instead of Cohen's?**
   When you have more than 2 raters. Cohen's is for exactly 2; Fleiss' generalizes to N >= 2.

7. **What is meta-evaluation?**
   Evaluating the evaluation dataset itself -- combining quality, coverage, and noise checks into a single trustworthiness score.

8. **How to measure evaluator reliability?**
   Run multiple times with different seeds, compute CV = std_dev / mean. CV < 0.10 = reliable.

9. **Exact-match vs near-duplicate contamination?**
   Exact = identical question in both sets. Near-duplicate = rephrased version, detected via Jaccard + n-gram overlap.

10. **How does entropy measure coverage?**
    Entropy measures distribution uniformity. Normalized entropy (H/H_max) gives 0-1 score. High topic count but concentrated distribution = low entropy.

---

## Hands-On Exercises

1. **Build a Balanced Benchmark**: From 200 questions, design 50 with 30/50/20 difficulty split, 3+ per topic, no duplicates, balanced answers.
2. **Contamination Audit**: Run exact match, near-duplicate (Jaccard + n-gram), and answer leakage analysis. Report rate and risk level.
3. **Inter-Annotator Agreement**: Simulate 3 annotators at 70/80/90% agreement. Compute Fleiss' Kappa. Find minimum rate for Substantial agreement (>0.6).
4. **Label Noise Hunt**: Use both annotator disagreement and model consensus to flag suspicious labels. Determine which is more likely correct.
5. **Full Meta-Evaluation Pipeline**: Run all checks, produce scorecard, write actionable recommendations.

---

## Mini Project: Production Evaluation Dataset Validator

Build a CLI tool that accepts an evaluation dataset (CSV/JSON) and produces:

1. Quality score and grade
2. Coverage analysis with entropy
3. Duplicate detection with similarity scores
4. Contamination check against a training set
5. Label noise estimation
6. Inter-annotator agreement (Cohen's + Fleiss' Kappa)
7. Meta-evaluation scorecard with recommendations
8. Evaluator reliability check (N runs, report CV)

Output: human-readable summary table + machine-readable JSON report.

---

## Further Reading

- Cohen (1960). "A coefficient of agreement for nominal scales."
- Fleiss (1971). "Measuring nominal scale agreement among many raters."
- Dodge et al. (2021). "Documenting Large Webtext Corpora."
- Jacobs & Wallach (2021). "Measurement and Fairness."
- Northcutt, Jiang, & Chuang (2021). "Confident Learning: Estimating Uncertainty in Dataset Labels."
