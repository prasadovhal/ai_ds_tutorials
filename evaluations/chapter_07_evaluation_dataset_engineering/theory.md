# Chapter 7 -- Evaluation Dataset Engineering

Building and validating evaluation datasets that reliably measure LLM performance.

Your model is only as good as the dataset you evaluate it on. A flawed evaluation dataset leads to wrong conclusions about model quality, which leads to bad deployment decisions. This chapter covers how to design, validate, and maintain evaluation datasets that you can actually trust.

---

## Overview

Evaluation Dataset Engineering is the discipline of constructing evaluation datasets that are **balanced, clean, comprehensive, and trustworthy**. It goes far beyond simply collecting questions and answers. It requires systematic design, rigorous quality control, contamination prevention, noise detection, and continuous meta-evaluation.

### Topics Covered

1. Benchmark Design -- Balanced subset selection with topic/difficulty quotas
2. Dataset Quality Checks -- Completeness, correctness, consistency validation
3. Coverage Metrics -- Topic, difficulty, and answer distribution coverage with entropy
4. Failure-Mode Coverage and Dataset Balancing -- Duplicate detection, answer skew, prompt outliers
5. Contamination Detection and Data Leakage -- Exact match, near-duplicate, and answer leakage checks
6. Label Noise Detection -- Annotator disagreement and model-consensus methods
7. Cohen's Kappa -- Inter-rater agreement for 2 raters, built from scratch
8. Fleiss' Kappa -- Inter-rater agreement for N raters, built from scratch
9. Meta-Evaluation -- Evaluating the evaluation dataset itself, plus evaluator reliability

---

## 1. Benchmark Design

### Problem

You have a large pool of evaluation questions, but using all of them is impractical. How do you select a subset that fairly represents the full evaluation space?

### Intuition

A benchmark is not just a collection of questions -- it is a carefully designed evaluation instrument. Think of it like designing a school exam. You would not put 50 easy questions and 0 hard ones. You would not test only one topic out of ten. A good exam covers the syllabus fairly.

### How It Works

A benchmark has defined:

- **Scope** -- what it measures
- **Structure** -- how questions are organized
- **Balance** -- fair representation across categories
- **Difficulty gradient** -- easy to hard progression

The benchmark designer:

1. Classifies each question by topic and difficulty
2. Filters by requested topics (if any)
3. Groups questions by difficulty level
4. Selects questions to maintain the target difficulty distribution (e.g., 40% easy, 40% medium, 20% hard)
5. Fills remaining slots from leftover questions
6. Trims to target size
7. Computes design statistics (topic counts, difficulty counts, answer distribution)

### Key Concepts

- **Target size**: The desired number of questions in the benchmark
- **Difficulty distribution**: The intended proportion of easy/medium/hard questions
- **Reproducibility**: A seed parameter ensures the same benchmark can be regenerated
- **Validation**: After design, the benchmark is checked for issues such as too few questions (fewer than 10), answer imbalance, duplicate prompts, and empty prompts

### Design Principles

- Balanced across difficulty levels
- Representative of available topics
- Answer distribution checked for bias
- Reproducible via seed parameter

---

## 2. Dataset Quality Checks

### Problem

Raw evaluation data often has missing fields, invalid labels, inconsistent formatting, and other quality problems that silently corrupt evaluation results.

### Intuition

This is like a factory quality inspector checking products on an assembly line. Each product must meet certain standards before it ships. Quality checks verify completeness, correctness, and consistency of every item.

### How It Works

Quality is measured across three dimensions:

#### Completeness

Are all required fields present and non-empty?

- Required fields: `id`, `prompt`, `ground_truth`
- Each question should also have all answer choices (A, B, C, D, E)
- Missing or empty fields are flagged with severity levels (critical, high, low)

**Completeness score**: `1.0 - (issues / max_possible_issues)`

#### Correctness

Are labels valid? Are prompts well-formed?

- Ground truth must be one of the valid answer set (A, B, C, D, E)
- The answer option must have a corresponding choice text
- Prompts should end with expected punctuation (?, ., :, ;)

#### Consistency

Are formats uniform across the dataset?

- Prompt lengths are analyzed for outliers (more than 3 standard deviations from mean)
- Number of choices should be consistent across all questions
- Prompt length statistics (mean, min, max) are computed

### Overall Quality Score

```
quality_score = max(0, 1.0 - total_issues / max_possible_issues)
```

### Grading Scale

| Grade | Score Range |
|-------|-------------|
| A     | >= 0.95     |
| B     | >= 0.85     |
| C     | >= 0.70     |
| D     | >= 0.50     |
| F     | < 0.50      |

---

## 3. Coverage Metrics

### Problem

A dataset might have 1000 questions but all on the same topic. Coverage measures how well the dataset spans the intended evaluation space.

### Intuition

Imagine you are testing a car. You would not just test it on a highway. You need city roads, hills, rain, night driving, etc. Coverage ensures your test suite exercises all important dimensions.

### How It Works

Coverage is measured along three dimensions:

#### Topic Coverage

Measures how many expected topics are represented.

- **Coverage ratio**: `covered_topics / expected_topics`
- **Entropy-based coverage**: Higher entropy means more uniform distribution across topics

**Entropy formula**:

```
H = -SUM(p_i * log2(p_i))
```

Where `p_i` is the proportion of questions belonging to topic `i`.

**Normalized entropy**: `H / H_max`, where `H_max = log2(number_of_topics)`

| Normalized Entropy | Interpretation |
|--------------------|----------------|
| > 0.9              | Excellent      |
| > 0.7              | Good           |
| > 0.5              | Fair           |
| <= 0.5             | Poor -- topics are heavily imbalanced |

#### Difficulty Coverage

Measures coverage across difficulty levels (easy, medium, hard).

- **Coverage ratio**: `levels_with_questions / total_expected_levels`
- Each level reports its count and percentage

#### Answer Coverage

Checks if correct answers are distributed across all options (A, B, C, D, E).

- **Coverage ratio**: `covered_options / total_options`
- **Balance score**: `1.0 - (max_deviation / total)`, where max_deviation is the largest absolute difference between any option's count and the expected count

### Overall Coverage Score

```
overall = topic_ratio * 0.4 + difficulty_ratio * 0.3 + answer_ratio * 0.3
```

Topic coverage gets the highest weight (40%) because topic imbalance is the most common and damaging coverage failure.

---

## 4. Failure-Mode Coverage and Dataset Balancing

### Problem

Even a dataset that looks complete can have hidden failure modes: duplicates inflating apparent variety, skewed answer distributions creating biased baselines, and prompt length anomalies introducing confounds.

### How It Works

#### Duplicate Detection

Near-duplicate questions are detected using **Jaccard similarity** on word sets:

```
Jaccard(A, B) = |A INTERSECTION B| / |A UNION B|
```

Where A and B are sets of words from two prompts.

- A threshold (e.g., 0.6) determines what counts as a near-duplicate
- Duplicates inflate the apparent size and diversity of the dataset
- They also give unfair weight to certain question types

#### Answer Distribution Analysis (Balance Check)

Checks whether correct answers are evenly distributed across options.

- **Expected percentage**: `100 / number_of_options` (e.g., 20% each for A-E)
- **Max deviation**: Largest percentage point difference from expected
- **Chi-squared statistic**: Measures overall departure from uniform distribution

```
chi_squared = SUM( (observed_i - expected_i)^2 / expected_i )
```

A high chi-squared value indicates significant imbalance. If answer "B" appears 40% of the time instead of the expected 20%, a model could score well just by always guessing "B".

#### Prompt Length Analysis

Analyzes the distribution of prompt lengths (in words and characters):

- min, max, mean, median, standard deviation
- 25th and 75th percentiles
- Extreme outliers may indicate data quality issues

---

## 5. Contamination Detection and Data Leakage

### Problem

Contamination occurs when test data leaks into training data, inflating evaluation scores artificially. The model appears to perform well, but it is simply memorizing answers it has seen before.

### Intuition

Imagine a student who gets the exam paper before the test. Their high score does not reflect true knowledge -- it reflects memorization of leaked answers. Contamination detection is like checking if any students had advance access to the exam.

### Types of Contamination

1. **Exact match**: The same question appears verbatim in both train and test sets
2. **Near-duplicate**: A rephrased version of the same question appears in both sets
3. **Answer leakage**: Test answers are visible during training
4. **Indirect leakage**: Training on the source material of test questions

### How It Works

#### Exact Match Detection

Compares normalized (lowercased, stripped) prompts between train and test sets. Any exact match is flagged as **critical severity**.

#### Near-Duplicate Detection

Uses a combined score of two similarity measures:

```
combined_score = 0.5 * jaccard_similarity + 0.5 * ngram_overlap
```

**Jaccard similarity**: Word-level overlap between two prompts.

**N-gram overlap**: Compares sequences of N consecutive words (default N=3):

```
ngram_overlap = |ngrams_A INTERSECTION ngrams_B| / min(|ngrams_A|, |ngrams_B|)
```

Matches above the threshold (e.g., 0.5 or 0.7) are flagged as **high severity**.

#### Answer Leakage Analysis

Compares the distribution of correct answers between train and test sets. If the distributions are suspiciously identical, it may indicate systematic leakage.

### Contamination Rate

```
contamination_rate = total_contaminated / test_set_size
```

### Risk Level Scale

| Rate      | Risk Level |
|-----------|------------|
| > 10%     | CRITICAL   |
| > 5%      | HIGH       |
| > 1%      | MEDIUM     |
| <= 1%     | LOW        |

---

## 6. Label Noise Detection

### Problem

Label noise means incorrect ground-truth labels in the evaluation dataset. Even a small amount of label noise (5-10%) can significantly distort evaluation results. If the answer key says 2+2=5, every model that correctly answers 4 gets marked wrong.

### Intuition

In a classroom test, if the answer key says 2+2=5, every student who correctly answers 4 gets marked wrong. Label noise is the equivalent of errors in the answer key.

### Detection Methods

#### Method 1: Annotator Disagreement

If multiple human annotators label the same question and they disagree significantly, the ground truth label may be wrong.

- For each question, compare the ground truth to the **majority vote** of annotators
- If the ground truth differs from the majority vote, flag the item as suspicious
- The **disagreement threshold** controls sensitivity (e.g., 0.5 means at least 50% of annotators must disagree)

#### Method 2: Model Consensus

If multiple independent models all predict a different answer than the ground truth, the label is likely wrong.

- Run multiple models (e.g., 3 models with different accuracy levels) on the same questions
- For each question, find the most common prediction across models
- If the **consensus rate** exceeds a threshold (e.g., 0.66) and the consensus prediction differs from the ground truth, flag the item

### Noise Rate Estimation

```
noise_rate = mismatches / total_checked
```

Where `mismatches` = number of questions where the ground truth differs from the annotator majority vote.

### Noise Rate Interpretation

| Noise Rate | Interpretation |
|------------|----------------|
| < 2%       | Clean dataset  |
| < 5%       | Acceptable noise |
| < 10%      | Moderate noise -- review recommended |
| >= 10%     | High noise -- significant label issues |

---

## 7. Cohen's Kappa -- Inter-Rater Agreement (2 Raters)

### Problem

When two annotators label the same data, how do you measure whether they genuinely agree or if their agreement is just due to chance?

### Intuition

Imagine two teachers grading the same essays. If they agree 80% of the time, that sounds good. But what if there are only 2 possible grades (pass/fail) and 90% of students pass? Then even random grading would agree about 82% of the time! Cohen's Kappa accounts for this chance agreement, giving you the TRUE agreement beyond random.

### Formula

```
kappa = (P_o - P_e) / (1 - P_e)
```

Where:

- **P_o** = observed agreement (fraction of items where raters agree)
- **P_e** = expected agreement by chance

### How P_e Is Computed

For each category c:

```
P_e = SUM over all categories c of (p_rater1_c * p_rater2_c)
```

Where:
- `p_rater1_c` = proportion of items rater 1 assigned to category c
- `p_rater2_c` = proportion of items rater 2 assigned to category c

### Step-by-Step Computation

1. **Build confusion matrix**: Count how many items each rater assigned to each category pair
2. **Compute P_o**: Sum the diagonal of the confusion matrix and divide by total items
3. **Compute P_e**: For each category, multiply the row marginal proportion by the column marginal proportion, then sum
4. **Compute kappa**: Apply the formula

### Interpretation Scale

| Kappa Value | Interpretation |
|-------------|----------------|
| < 0.00      | Less than chance agreement |
| 0.00 - 0.20 | Slight agreement |
| 0.21 - 0.40 | Fair agreement |
| 0.41 - 0.60 | Moderate agreement |
| 0.61 - 0.80 | Substantial agreement |
| 0.81 - 1.00 | Almost perfect agreement |

### Example Scenarios

- **Perfect agreement** (both raters give identical labels): Kappa = 1.0 (Almost perfect agreement)
- **Two annotators with 80% accuracy**: Kappa typically falls in the Moderate to Substantial range
- **Near-random agreement** (one rater assigns random labels): Kappa is near 0 or negative (Slight or Less than chance agreement)

---

## 8. Fleiss' Kappa -- Inter-Rater Agreement (Multiple Raters)

### Problem

Cohen's Kappa works for exactly 2 raters. When you have 3, 5, or more raters labeling the same items, you need a generalization.

### Intuition

You have 5 people taste-testing 10 dishes, each rating them "good", "okay", or "bad". Fleiss' Kappa tells you whether the tasters genuinely agree or if their agreement is just what you would expect from random ratings.

### Formula

```
kappa = (P_bar - P_e_bar) / (1 - P_e_bar)
```

Where:

- **P_bar** = mean of per-item agreement proportions (observed agreement)
- **P_e_bar** = expected agreement by chance

### Step-by-Step Computation

**Step 1: Build the count matrix**

For N items, k categories, and n raters per item, create a matrix where `n_ij` = number of raters who assigned item i to category j.

**Step 2: Compute P_i for each item**

```
P_i = (1 / (n * (n-1))) * (SUM_j(n_ij^2) - n)
```

Where:
- `n` = number of raters
- `n_ij` = number of raters who assigned item i to category j

**Step 3: Compute P_bar (mean observed agreement)**

```
P_bar = (1/N) * SUM_i(P_i)
```

Where N = number of items.

**Step 4: Compute p_j (category proportions)**

```
p_j = (1 / (N * n)) * SUM_i(n_ij)
```

The proportion of all assignments that go to category j.

**Step 5: Compute P_e_bar (expected agreement by chance)**

```
P_e_bar = SUM_j(p_j^2)
```

**Step 6: Compute Fleiss' Kappa**

```
kappa = (P_bar - P_e_bar) / (1 - P_e_bar)
```

### Interpretation Scale

Same as Cohen's Kappa:

| Kappa Value | Interpretation |
|-------------|----------------|
| < 0.00      | Less than chance agreement |
| 0.00 - 0.20 | Slight agreement |
| 0.21 - 0.40 | Fair agreement |
| 0.41 - 0.60 | Moderate agreement |
| 0.61 - 0.80 | Substantial agreement |
| 0.81 - 1.00 | Almost perfect agreement |

### Example Scenarios

- **5 raters on 10 items**: Compute from the annotation matrix in sample data, observe category proportions
- **3 annotators on 20 questions** (85% agreement rate): Typically yields Moderate to Substantial kappa
- **Perfect agreement** (all raters identical): Kappa = 1.0

### Cohen's Kappa vs Fleiss' Kappa

| Feature | Cohen's Kappa | Fleiss' Kappa |
|---------|---------------|---------------|
| Number of raters | Exactly 2 | 2 or more |
| Input format | Two lists of labels | Matrix of category counts per item |
| Chance correction | Yes | Yes |
| Use case | Comparing two annotators | Comparing N annotators |
| Special case | -- | Reduces to Cohen's Kappa when N=2 |

---

## 9. Meta-Evaluation -- Evaluating the Evaluator

### Problem

Before using an evaluation dataset to judge models, you need to know: "Is our evaluation dataset itself good enough to trust?" A bad evaluation dataset leads to wrong conclusions about model quality, which leads to bad deployment decisions.

### Intuition

Before you use a ruler to measure a table, you should check if the ruler itself is accurate. Meta-evaluation is checking the ruler before measuring.

### How It Works

The MetaEvaluator aggregates results from all other checkers into a single quality scorecard.

#### Dimensions Scored

1. **Quality** -- from DatasetQualityChecker (completeness, correctness, consistency)
2. **Coverage** -- from CoverageAnalyzer (topic, difficulty, answer coverage)
3. **Label Quality** -- from LabelNoiseDetector (noise rate converted to a score)

**Label quality score**: `max(0, 1.0 - noise_rate * 5)`

This means a 20% noise rate gives a label quality score of 0.0 (very bad), and a 0% noise rate gives 1.0 (perfect).

#### Overall Score

```
overall_score = mean(dimension_scores)
```

#### Grading Scale

| Grade | Score Range |
|-------|-------------|
| A     | >= 0.90     |
| B     | >= 0.80     |
| C     | >= 0.65     |
| D     | >= 0.50     |
| F     | < 0.50      |

### Recommendations Engine

Based on the scores, automatic recommendations are generated:

- If quality score < 0.9: "Fix data quality issues (missing fields, invalid labels)"
- If coverage score < 0.7: "Improve coverage -- add questions from underrepresented topics/difficulties"
- If noise rate > 5%: "Review and correct potentially mislabeled examples"
- If everything passes: "Dataset meets quality standards for reliable evaluation"

### Evaluator Reliability Check

The "evaluating the evaluator" problem: if your evaluation method gives different results each time, it is unreliable.

This check runs the evaluator multiple times (e.g., 10 runs) with different seeds and measures the consistency of results.

#### Key Metric: Coefficient of Variation (CV)

```
CV = std_dev / mean
```

Where:
- `std_dev` = standard deviation of scores across runs
- `mean` = mean of scores across runs

Lower CV means more reliable.

#### Reliability Interpretation

| CV Value | Interpretation |
|----------|----------------|
| < 0.05   | Highly reliable |
| < 0.10   | Reliable |
| < 0.20   | Moderately reliable |
| >= 0.20  | Unreliable -- high variance across runs |

A reliable evaluator (CV < 0.10) will give consistent results regardless of random seed or sampling variation.

---

## Summary Table

```
Metric                          Value
------------------------------  ----------
Dataset quality score           (from quality checker)
Dataset quality grade           A/B/C/D/F
Coverage score                  (weighted average)
Topic coverage                  (ratio of covered/expected)
Difficulty coverage             (ratio of covered levels)
Answer balance                  (1 - max_deviation/total)
Contamination rate              (contaminated/test_size)
Label noise rate                (mismatches/total)
Cohen's Kappa (2 raters)        (kappa value)
Fleiss' Kappa (5 raters)        (kappa value)
Meta-eval overall               (mean of dimension scores)
Evaluator reliability (CV)      (coefficient of variation)
```

---

## Comparison of All Techniques

| Technique | What It Measures | Input | Output | When to Use |
|-----------|-----------------|-------|--------|-------------|
| Benchmark Design | Balanced subset selection | Raw question pool | Structured benchmark | Before evaluation begins |
| Quality Checks | Data completeness/correctness | Dataset items | Issue report with score | Every dataset, always |
| Coverage Analysis | Topic/difficulty/answer spread | Dataset + expected dimensions | Coverage ratios + entropy | When building or auditing datasets |
| Duplicate Detection | Redundant questions | Pairs of prompts | Similarity scores | Before finalizing any dataset |
| Contamination Detection | Train-test leakage | Train + test sets | Contamination rate | Critical before any model comparison |
| Label Noise Detection | Incorrect ground truths | Annotations or model predictions | Suspicious items list | When annotation quality is uncertain |
| Cohen's Kappa | 2-rater agreement | Two label lists | Kappa score | Pairwise annotator comparison |
| Fleiss' Kappa | N-rater agreement | Rating matrix | Kappa score | Multi-annotator quality assessment |
| Meta-Evaluation | Overall dataset trustworthiness | All above results | Scorecard + recommendations | Final validation before using dataset |

---

## Common Mistakes

1. **Using raw accuracy to measure annotator agreement** -- Raw agreement ignores chance. Two raters might agree 80% of the time purely by chance if the class distribution is skewed. Always use Cohen's or Fleiss' Kappa.

2. **Ignoring contamination between train and test sets** -- Even near-duplicate questions (rephrased versions) can leak information. Always check for both exact and near-duplicate contamination.

3. **Assuming the answer key is always correct** -- Ground truth labels can be wrong. Use label noise detection (annotator disagreement + model consensus) to find and fix mislabeled items.

4. **Building benchmarks without checking coverage** -- A dataset with 100 physics questions and 2 biology questions is not a "science" benchmark. Always measure and report coverage across all intended dimensions.

5. **Not checking dataset balance** -- If 50% of correct answers are "B", models can exploit this pattern. Always verify answer distribution balance.

6. **Treating evaluation as a one-time activity** -- Datasets need versioning, drift detection, and periodic re-validation. Build meta-evaluation into your workflow.

7. **Confusing Cohen's Kappa with Fleiss' Kappa** -- Cohen's is strictly for 2 raters. Fleiss' generalizes to N raters. Using the wrong one gives meaningless results.

8. **Ignoring prompt length outliers** -- Extremely short or long prompts may indicate data quality issues (truncated text, copied boilerplate, etc.).

9. **Not setting a seed for reproducibility** -- Benchmark design and simulation should always use a seed so results can be replicated.

10. **Evaluating the evaluator only once** -- Run multiple times to check reliability. A high coefficient of variation means your results are unstable.

---

## Best Practices

1. **Design benchmarks with explicit difficulty quotas** -- Define the target distribution (e.g., 40% easy, 40% medium, 20% hard) before selecting questions.

2. **Run all quality checks before using any evaluation dataset** -- Completeness, correctness, and consistency checks should be automated and mandatory.

3. **Measure coverage with entropy, not just counts** -- Entropy captures both the presence and the balance of topics. A dataset covering 6 topics but with 90% in one topic has low entropy despite high count-based coverage.

4. **Remove duplicates before evaluation** -- Near-duplicates inflate scores and reduce effective dataset size. Use Jaccard similarity with an appropriate threshold.

5. **Check for contamination between every pair of splits** -- Train/test, train/validation, and even between fine-tuning data and evaluation data.

6. **Use multiple annotators and measure agreement** -- At least 3 annotators, with Fleiss' Kappa reported. Aim for Kappa > 0.6 (Substantial agreement).

7. **Use both annotator disagreement AND model consensus for noise detection** -- These are complementary methods. Annotators catch semantic errors; models catch pattern-level errors.

8. **Version your datasets** -- Track changes over time. When you fix labels, add questions, or remove contamination, create a new version.

9. **Report meta-evaluation scores alongside model scores** -- If your dataset has a quality score of 0.7, your model evaluation results have a corresponding uncertainty.

10. **Automate all checks in CI/CD** -- Dataset quality, coverage, contamination, and noise detection should run automatically whenever the dataset changes.

---

## Interview Questions

1. **What is the difference between a benchmark dataset and an evaluation dataset?**
   A benchmark is a carefully designed, structured, balanced subset with defined scope, coverage targets, and difficulty distribution. An evaluation dataset is any dataset used for evaluation, which may or may not have these properties.

2. **Why is raw percentage agreement insufficient for measuring annotator quality?**
   Because it does not account for chance agreement. If 90% of items belong to one class, two random annotators will agree about 82% of the time. Cohen's/Fleiss' Kappa corrects for this by subtracting expected chance agreement.

3. **What is data contamination and why does it matter?**
   Contamination occurs when test data leaks into training data. It inflates evaluation scores, giving a false sense of model quality. A model that memorized leaked test answers appears to generalize well but actually does not.

4. **How do you detect label noise in an evaluation dataset?**
   Two main methods: (a) Annotator disagreement -- if multiple annotators disagree with the ground truth label, it may be wrong. (b) Model consensus -- if multiple independent models consistently predict a different answer, the label is likely incorrect.

5. **Explain Cohen's Kappa formula and what each variable means.**
   `kappa = (P_o - P_e) / (1 - P_e)`. P_o is the observed agreement rate (fraction of items where both raters chose the same label). P_e is the expected agreement rate by chance (computed from the marginal distributions of each rater's labels). The formula measures how much agreement exceeds chance, normalized by the maximum possible excess.

6. **When would you use Fleiss' Kappa instead of Cohen's Kappa?**
   When you have more than 2 raters. Cohen's Kappa is defined for exactly 2 raters. Fleiss' Kappa generalizes to any number N >= 2 of raters labeling the same set of items.

7. **What is meta-evaluation and why is it important?**
   Meta-evaluation is evaluating the evaluation dataset itself. It asks: "Is our dataset good enough to reliably evaluate models?" It combines quality checks, coverage analysis, and label noise detection into a single trustworthiness score.

8. **How do you measure if an evaluator is reliable?**
   Run the evaluator multiple times with different random seeds and measure the coefficient of variation (CV = std_dev / mean). If CV < 0.10, the evaluator is reliable. High CV indicates that results are unstable and cannot be trusted.

9. **What is the difference between exact-match contamination and near-duplicate contamination?**
   Exact-match contamination is when the identical question appears in both sets. Near-duplicate contamination is when a rephrased or slightly modified version appears. Near-duplicates are detected using Jaccard similarity and n-gram overlap with a combined score threshold.

10. **How does entropy measure topic coverage quality?**
    Entropy measures the uniformity of the distribution. Maximum entropy occurs when all topics have equal representation. Normalized entropy (H / H_max) gives a 0-to-1 score where higher values indicate more balanced topic coverage. A dataset with high topic count but concentrated distribution will have low entropy.

---

## Hands-On Exercises

### Exercise 1: Build a Balanced Benchmark

Given a pool of 200 science questions, design a benchmark of 50 questions with:
- 30% easy, 50% medium, 20% hard
- At least 3 questions from each of the 6 science topics
- No duplicate prompts
- Balanced answer distribution

### Exercise 2: Contamination Audit

Take a train set and test set. Run exact match detection, near-duplicate detection (Jaccard + n-gram), and answer leakage analysis. Report the contamination rate and risk level.

### Exercise 3: Inter-Annotator Agreement

Simulate 3 annotators labeling 50 questions with varying agreement rates (70%, 80%, 90%). Compute Fleiss' Kappa for each scenario and compare. Determine the minimum agreement rate needed for Substantial agreement (Kappa > 0.6).

### Exercise 4: Label Noise Hunt

Using both annotator disagreement and model consensus methods, identify suspicious labels in a dataset. For each flagged item, determine whether the ground truth or the majority vote is more likely correct.

### Exercise 5: Full Meta-Evaluation Pipeline

Run the complete meta-evaluation pipeline: quality checks, coverage analysis, contamination detection, label noise detection, and evaluator reliability check. Produce a scorecard and write actionable recommendations for improving the dataset.

---

## Mini Project

### Production Evaluation Dataset Validator

Build a command-line tool that accepts an evaluation dataset (CSV or JSON) and produces a comprehensive quality report including:

1. Quality score and grade (completeness, correctness, consistency)
2. Coverage analysis (topic, difficulty, answer distribution with entropy)
3. Duplicate detection with similarity scores
4. Contamination check against a provided training set
5. Label noise estimation (if annotator labels are available)
6. Inter-annotator agreement (Cohen's Kappa for pairs, Fleiss' Kappa for all)
7. Meta-evaluation scorecard with overall grade and recommendations
8. Evaluator reliability check (run evaluation N times, report CV)

Output should include both a human-readable summary table and a machine-readable JSON report.

---

## Further Reading

- Cohen, J. (1960). "A coefficient of agreement for nominal scales." Educational and Psychological Measurement.
- Fleiss, J. L. (1971). "Measuring nominal scale agreement among many raters." Psychological Bulletin.
- Dodge et al. (2021). "Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus."
- Jacobs & Wallach (2021). "Measurement and Fairness" -- on evaluation dataset design principles.
- Northcutt, Jiang, & Chuang (2021). "Confident Learning: Estimating Uncertainty in Dataset Labels" -- on label noise detection at scale.
