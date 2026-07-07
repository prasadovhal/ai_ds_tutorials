# Chapter 6: Golden Dataset Engineering

Golden datasets are small, high-quality, human-verified evaluation sets that serve as the ground truth benchmark for your LLM system. This chapter covers the complete lifecycle of golden dataset engineering: why they matter, how to build them, how to annotate and validate them, how to use them for regression testing, and how to maintain them over time.

---

## 1. Why Golden Datasets & Dataset Types

### Problem

When evaluating LLMs, RAG pipelines, or AI agents, you need a reliable benchmark to measure performance. Public benchmarks may not reflect your domain. Training data is noisy. Test sets can become stale. Without a curated, human-verified reference set, you cannot confidently detect regressions, compare prompts, or validate releases.

### Intuition

Think of a golden dataset as the "exam paper" for your AI system. Just as a well-designed exam tests all the important topics at various difficulty levels, a golden dataset must cover your domain comprehensively, be free of errors, and be small enough to maintain but large enough to be statistically meaningful.

### How It Works

Golden datasets are built through a deliberate pipeline:

```
Raw Data --> Categorize --> Deduplicate --> Sample --> Annotate
    --> Quality Check --> Version --> Deploy as Benchmark
```

### Dataset Types Comparison

```
+------------------+----------+----------+----------+-----------+
| Property         | Training | Test     | Golden   | Synthetic |
+------------------+----------+----------+----------+-----------+
| Size             | Large    | Medium   | Small    | Any       |
| Quality          | Variable | Good     | Highest  | Variable  |
| Human-reviewed   | Rarely   | Sometimes| Always   | Never     |
| Use case         | Learning | Eval     | Benchmark| Augment   |
| Update frequency | Rarely   | Rarely   | Often    | On-demand |
| Cost to create   | Low      | Medium   | High     | Low       |
+------------------+----------+----------+----------+-----------+
```

### Key Concepts

- **Golden dataset**: Small, high-quality, human-verified benchmark. Always human-reviewed. Updated often. Used as the definitive evaluation reference.
- **Training dataset**: Large, variable quality. Used for model learning. Rarely human-reviewed at scale.
- **Test dataset**: Medium-sized, good quality. Used for general evaluation. Sometimes human-reviewed.
- **Synthetic dataset**: Any size, variable quality. Never used directly without human review. Generated on-demand to augment real data.
- **Validation dataset**: Used during model development to tune hyperparameters. Separate from final evaluation.
- **Benchmark dataset**: Standardized public evaluation set (e.g., MMLU, HumanEval). Not customized to your domain.
- **Production dataset**: Real-world data from deployed systems. Source material for building golden datasets.
- **Evaluation dataset**: Broader term for any dataset used to measure system performance.

### Why Benchmarks Alone Are Insufficient

Public benchmarks do not reflect your specific domain, user base, edge cases, or deployment context. A golden dataset captures what matters for your application.

---

## 2. Creating Golden Datasets: Sampling, Deduplication, Balancing

### Problem

Raw data from production logs, training sets, or support tickets is noisy, redundant, and imbalanced. Directly using it as an evaluation set leads to unreliable metrics that overrepresent common cases and miss rare but important ones.

### Intuition

Building a golden dataset is like curating a museum collection. You do not display everything -- you select representative pieces across different periods and styles, remove duplicates, and ensure every important area is covered.

### How It Works

Building a golden dataset involves four key operations:

1. **Categorization**: Classify items by domain, topic, or intent
2. **Deduplication**: Remove redundant items using similarity measures
3. **Stratified Sampling**: Sample proportionally from each category to maintain representation
4. **Category Balancing**: Adjust counts to prevent extreme skew

### Key Concepts

#### Categorization

Questions are categorized by detecting domain keywords in the prompt and answer text. In production, this would use an LLM or human annotation rather than keyword matching.

Categories for a science domain might include: physics, biology, chemistry, mathematics, earth_science, astronomy, and general.

#### Difficulty Estimation

Difficulty is estimated using heuristics:
- Longer prompts tend to indicate harder questions
- Longer answer options suggest more nuance
- High similarity between answer choices makes them harder to distinguish

In production, use human ratings or model performance data for more accurate difficulty estimation.

#### Deduplication

Near-duplicate questions are detected using word-level Jaccard similarity:

```
Jaccard Similarity = |A intersection B| / |A union B|
```

Where A and B are the word sets from two question prompts. Items with similarity above a threshold (e.g., 0.8) are considered duplicates and removed.

In production, use embedding-based cosine similarity for more semantic deduplication.

#### Stratified Sampling

Stratified sampling ensures every category/difficulty level is represented proportionally in the golden dataset. The process:

1. Group items by the stratification variable (category, difficulty, etc.)
2. Calculate each group's proportion of the total
3. Sample from each group proportionally
4. Trim or pad to reach the exact target size

#### Category Balancing

Balancing adjusts category counts to prevent extreme skew. Two approaches:
- **Undersampling**: Reduce majority categories to a target count
- **Keeping all**: For golden data, prefer keeping originals from minority categories and flagging gaps rather than oversampling

#### Edge Case Detection

Edge cases are crucial for golden datasets. They are identified using heuristics:
- Very long prompts (>500 characters) -- complex questions
- Very short prompts (<50 characters) -- potentially ambiguous
- Contains negation words (not, except, without, never, neither) -- tricky questions
- Multiple detailed answer options (similar lengths) -- hard to distinguish

A good golden dataset should contain 10-30% edge cases.

### Creation Sources

Golden datasets can be built from:
- Production logs
- Customer conversations
- Support tickets
- Search queries
- Agent trajectories
- Human-written examples
- LLM-generated examples (with human review)
- Synthetic generation
- Failure-driven sampling
- Active learning
- Hard-negative mining

---

## 3. Annotation Workflow, Rubrics, Inter-Annotator Agreement

### Problem

A golden dataset is only as good as its labels. If one person labels the data and makes mistakes, those errors become your ground truth. Without multiple annotators and agreement measurement, you cannot quantify label quality or catch systematic biases.

### Intuition

Imagine three teachers grading the same exam. If they all agree on every answer, you can be confident in the grades. If they frequently disagree, either the questions are ambiguous or some teachers need calibration. Measuring agreement tells you how trustworthy your labels are.

### How It Works

The annotation workflow follows these steps:

1. Create annotation guidelines and rubrics
2. Have multiple annotators (typically 3+) independently label each item
3. Determine consensus via majority vote
4. Measure inter-annotator agreement using statistical metrics
5. Review items with low agreement
6. Generate quality control reports per annotator

### Key Concepts

#### Annotation Guidelines

A structured annotation guideline document includes:

**Steps for annotators:**
1. Read the question carefully and completely
2. Read ALL five answer options before selecting
3. Select the most accurate and complete answer
4. Rate your confidence (0.0 to 1.0)
5. Estimate the question difficulty (easy/medium/hard)
6. Flag if the question is ambiguous or has errors

**Quality criteria:**
- **Correctness**: The answer must be factually accurate based on established scientific knowledge
- **Completeness**: The chosen answer should fully address the question, not just be partially correct
- **Clarity check**: If the question itself is unclear or ambiguous, flag it for review rather than guessing

**Common pitfalls:**
- Choosing an answer that is only partially correct
- Confusing similar scientific terms (e.g., reddening vs redshifting)
- Selecting the first plausible answer without reading all options
- Letting familiarity bias override careful reading

#### Annotation Rubric

```
5_excellent:    Clearly correct, unambiguous, well-supported
4_good:         Correct with minor stylistic issues
3_acceptable:   Mostly correct but could be more precise
2_poor:         Partially correct or misleading
1_unacceptable: Factually wrong or completely off-topic
```

#### Escalation Criteria

Items should be escalated for expert review when:
- Two annotators disagree on the correct answer
- Average confidence is below 0.6
- Any annotator flags the question as ambiguous

#### Consensus via Majority Vote

For each item, the consensus label is determined by majority vote across all annotators. The annotation record tracks:
- Each annotator's label, confidence, and time spent
- The consensus label and agreement count
- Whether consensus matches the ground truth
- Whether agreement is unanimous

#### Cohen's Kappa (Pairwise Agreement)

Cohen's Kappa measures agreement between two annotators, correcting for chance agreement:

```
Kappa = (P_observed - P_expected) / (1 - P_expected)
```

Where:
- **P_observed** = proportion of items where both annotators agree
- **P_expected** = proportion of items where agreement is expected by chance

**Interpretation scale:**
```
< 0.00    Poor (worse than chance)
0.00-0.20 Slight
0.21-0.40 Fair
0.41-0.60 Moderate
0.61-0.80 Substantial
0.81-1.00 Almost perfect
```

**Why percentage agreement is insufficient:** Two annotators could agree 80% of the time purely by chance if they both favor the same labels. Kappa corrects for this by subtracting expected chance agreement, giving a more honest measure of true agreement.

#### Fleiss' Kappa (Multi-Annotator Agreement)

Fleiss' Kappa extends Cohen's Kappa to three or more annotators:

```
Fleiss' Kappa = (P_bar - P_e) / (1 - P_e)
```

Where:
- **P_bar** = mean of per-item agreement proportions (P_i)
- **P_e** = expected agreement by chance, computed from the overall distribution of labels across all annotators
- **P_i** = proportion of agreeing pairs for item i = (sum of squared category counts - n_raters) / (n_raters * (n_raters - 1))

The interpretation scale is the same as Cohen's Kappa. A Fleiss' Kappa above 0.6 indicates substantial agreement and is generally the minimum acceptable threshold for golden dataset labels.

#### Annotator Quality Control

Quality control reports track per-annotator statistics:
- **Accuracy**: How often the annotator matches ground truth
- **Average confidence**: Mean self-reported confidence score
- **Average time**: Mean labeling time per item (very fast may indicate carelessness; very slow may indicate confusion)
- **Items needing review**: Items where consensus was not unanimous, along with review rates

---

## 4. Regression Testing & Prompt Comparison

### Problem

When you change a prompt template, swap a model, or modify a pipeline, how do you know if the new version is better or worse? Without a fixed benchmark, you cannot reliably detect regressions -- cases where the new version fails on items the old version handled correctly.

### Intuition

A golden dataset acts as a fixed exam that you administer to every version of your system. By comparing scores and identifying specific items that changed from correct to incorrect (regressions) or incorrect to correct (improvements), you get a detailed picture of what changed and why.

### How It Works

Regression testing with a golden dataset:

1. Run both model/prompt versions on the same golden dataset
2. Compare overall accuracy
3. Identify per-item changes:
   - **Regressions**: Items that version A got right but version B got wrong
   - **Improvements**: Items that version A got wrong but version B got right
   - **Stable correct**: Both versions got right
   - **Stable wrong**: Both versions got wrong
4. Analyze per-category breakdowns
5. Flag if net accuracy decreased (is_regression = delta < -2%)

### Key Concepts

#### Model Version Comparison

Compare two sets of predictions against golden ground truth. Key metrics:
- Overall accuracy for each version
- Delta (accuracy difference)
- Regression count and specific items
- Improvement count and specific items
- Stable correct/wrong counts
- Per-category accuracy with visual bar charts

#### Prompt Strategy Comparison

Compare multiple prompt strategies on the same golden dataset:
- **Zero-shot**: Direct question without examples
- **Few-shot**: Question with example demonstrations
- **Chain-of-thought**: Step-by-step reasoning prompts
- **Self-consistency**: Multiple reasoning paths with majority vote

Results are ranked by accuracy with spread (difference between best and worst) to quantify the impact of prompt engineering.

#### Per-Category Analysis

Breaking down performance by category reveals where specific versions excel or struggle. A version might improve overall but regress on a specific category, which per-category analysis catches.

---

## 5. Versioning, Drift Detection, Maintenance

### Problem

Golden datasets are not static. Questions become outdated, errors are discovered, new edge cases emerge, and production data shifts. Without versioning and drift detection, your benchmark silently becomes stale, and evaluation results become unreliable.

### Intuition

Think of versioning like version control for code. Every change to the dataset is tracked with a version number, author, date, and description. Drift detection is like monitoring -- it alerts you when the world has changed enough that your benchmark needs updating.

### How It Works

#### Dataset Versioning

Each version records:
- Version number (semantic versioning: major.minor.patch)
- Creation date and author
- Description of changes
- Item count
- Content hash (MD5 of item IDs and ground truth labels for integrity checking)

#### Version Diffing

Compare two versions to see exactly what changed:
- **Added items**: New items in the newer version
- **Removed items**: Items dropped from the newer version
- **Modified items**: Items where fields changed (ground truth, category, etc.)
- **Unchanged items**: Items identical across versions

#### Drift Detection

Drift detection compares distributions between a baseline (golden dataset) and current data (production or updated dataset) using Total Variation Distance (TVD):

```
TVD = 0.5 * sum(|p_i - q_i|)
```

Where:
- **p_i** = proportion of category i in the baseline
- **q_i** = proportion of category i in the current data
- Range: [0, 1] where 0 = identical distributions, 1 = completely different

Drift is measured across three dimensions:
- **Category drift**: Shift in topic distribution
- **Difficulty drift**: Shift in difficulty distribution
- **Answer drift**: Shift in answer key distribution

**Severity thresholds:**
```
< 0.10   None
0.10-0.25 Low
0.25-0.50 Moderate (needs update)
> 0.50   High (urgent update needed)
```

#### Maintenance Tracking

Track dataset health over time with quality checkpoints:
- Version, date, quality score, item count, and notes for each checkpoint
- Trend analysis: improving, degrading, or stable
- Automatic maintenance action recommendations:
  - Quality below 70% triggers urgent full review
  - Declining quality for 3+ checkpoints triggers a warning
  - Dataset smaller than 20 items triggers a size warning

#### Quality Score Over Time (ASCII Chart)

```
Quality Score Over Time:
--------------------------------------------------
1.0.0    |############################............| 72.0%
1.1.0    |###############################.........| 78.0%
1.2.0    |################################........| 82.0%
2.0.0    |##################################......| 85.0%
--------------------------------------------------
```

### Key Concepts

- **Semantic versioning**: Use major.minor.patch (e.g., 2.1.0). Major = breaking changes or large overhauls. Minor = additions. Patch = corrections.
- **Content hashing**: Generate a hash of all item IDs and ground truth labels. If the hash changes, the content changed. Enables integrity verification.
- **Rollback**: The ability to revert to any previous version if a new version introduces problems.
- **Changelog**: Every version includes a human-readable description of what changed and why.

---

## 6. Synthetic Data Generation

### Problem

Real-world data for evaluation can be scarce, especially for new domains, edge cases, or low-resource languages. Manually creating golden dataset items is expensive and slow. You need a way to bootstrap or augment your dataset.

### Intuition

Synthetic data is like a practice exam generated by a teacher. It can help test coverage in areas where real questions are sparse, but it is not a substitute for actual exam questions. Every synthetic item must be reviewed by a human before it earns "golden" status.

### How It Works

The synthetic data generation workflow:

1. Define templates or prompt an LLM to generate questions in specific formats
2. Generate candidate questions across target categories
3. Run automated validation checks
4. Submit all generated items for human review
5. Only include approved items in the golden dataset

### Key Concepts

#### Generation Methods

- **Template-based**: Fill in concept placeholders in predefined question patterns (e.g., "What is the relationship between {concept_a} and {concept_b}?")
- **LLM-based**: Prompt a language model to generate questions in a specific format and domain (production approach)
- **Perturbation-based**: Modify existing questions to create variations

#### Validation Checks

Automated validation before human review:
- Prompt is not empty or too short (<10 characters)
- All 5 answer choices exist
- Ground truth label is valid (A-E)
- No duplicate choice text

#### Human Review Workflow

Every synthetic item must go through human review. Reviewers:
1. Check factual correctness
2. Verify answer options are realistic and distinct
3. Confirm the ground truth label
4. Rate quality on a 1-5 scale
5. Flag issues (ambiguous, incorrect, etc.)

Review outcomes:
- **Approved**: Factually correct, well-formed question
- **Needs revision**: Answer options need improvement or question needs clarification
- **Rejected**: Question is ambiguous or incorrect

#### Critical Warnings

```
! All synthetic items MUST be human-reviewed before use
! Ground truth labels are placeholders -- verify each one
! Choice text is template-generated -- replace with real content
```

#### When NOT to Use Synthetic Data

- When you have sufficient real data
- For final production benchmarks without human review
- When the domain requires expert knowledge that templates cannot capture
- When synthetic patterns could leak into training data (contamination risk)

---

## 7. Full Dataset Quality Evaluation

### Problem

How do you know if your golden dataset is actually good? Individual checks (coverage, balance, duplicates) tell part of the story, but you need a holistic quality score that combines all dimensions.

### Intuition

A dataset quality score is like a health checkup for your evaluation benchmark. Just as a doctor checks multiple vital signs and combines them into an overall assessment, the quality scorer examines coverage, balance, uniqueness, annotation agreement, and edge case inclusion to produce a composite grade.

### How It Works

The quality scorer combines five components into a single composite score (0-100):

#### Component Scores and Weights

| Component            | Weight | What It Measures                                      |
|----------------------|--------|------------------------------------------------------|
| Coverage             | 25%    | How well the dataset covers categories, difficulties  |
| Balance              | 20%    | Whether categories/difficulties are evenly distributed|
| Uniqueness           | 20%    | Absence of duplicate or near-duplicate items          |
| Annotation Quality   | 20%    | Inter-annotator agreement (Fleiss' Kappa)             |
| Edge Cases           | 15%    | Whether 10-30% of items are edge cases                |

#### Coverage Analysis

Coverage is measured as a weighted combination:
- **Category coverage (40%)**: Percentage of expected categories present in the dataset
- **Difficulty coverage (30%)**: Whether all three difficulty levels (easy, medium, hard) are represented
- **Answer balance (30%)**: Shannon entropy of the answer distribution (higher entropy = more balanced)

Shannon entropy:
```
H = -sum(p_i * log2(p_i))
```
Where p_i is the proportion of items with answer i. Maximum entropy (most balanced) occurs when all answers are equally likely.

Recommendations are generated automatically for gaps:
- Missing categories that should be added
- Missing difficulty levels
- Skewed answer distributions
- Insufficient edge case ratio (below 10%)

#### Balance Checking

Balance is measured using the Gini coefficient and imbalance ratio:

**Gini coefficient:**
- 0 = perfect equality (all categories have same count)
- 1 = maximum inequality (one category has all items)
- Threshold: balanced if Gini < 0.3

**Imbalance ratio:**
- max(count) / min(count)
- Threshold: balanced if ratio < 3

Balance is checked across multiple dimensions: category, difficulty, and ground_truth answer distribution.

#### Duplicate Detection

Two types of duplicates are detected:
- **Exact duplicates**: Items with identical prompts (detected via MD5 hash of normalized text)
- **Near duplicates**: Items with similar prompts (detected via Jaccard similarity above a threshold, default 0.75)

Uniqueness score = unique items / total items

#### Grading Scale

```
A: 90-100  Excellent
B: 80-89   Good
C: 70-79   Acceptable
D: 60-69   Needs improvement
F: <60     Failing
```

---

## Chapter 6 Summary

### Key Takeaways

1. Golden datasets are small, high-quality, human-verified benchmarks
2. Build them via: categorize -> deduplicate -> sample -> annotate -> version
3. Measure inter-annotator agreement with Cohen's and Fleiss' Kappa
4. Use for regression testing when changing prompts/models
5. Version everything -- track diffs, detect drift, maintain quality
6. Synthetic data augments but never replaces human-verified data

### Quality Checklist

```
+---+----------------------------------+
|   | Check                            |
+---+----------------------------------+
| 1 | Coverage: all categories present |
| 2 | Balance: no extreme skew         |
| 3 | No duplicates                    |
| 4 | Annotator agreement > 0.6 kappa  |
| 5 | Edge cases included (10-30%)     |
| 6 | Versioned with changelog         |
| 7 | Regular drift checks             |
+---+----------------------------------+
```

### Common Mistakes

- Using raw production data as-is without deduplication or balancing
- Having a single annotator label all data (no way to measure label quality)
- Relying on percentage agreement instead of Kappa (ignores chance agreement)
- Never updating the golden dataset as the domain evolves
- Including synthetic data without human review
- Ignoring edge cases (dataset too "clean" and easy)
- Not versioning -- making changes without tracking what changed and why
- Skipping drift detection -- benchmark becomes silently stale

### Best Practices

- Start small (50-200 items) and grow deliberately
- Always use multiple annotators (3+) for label quality
- Target Cohen's/Fleiss' Kappa > 0.6 (substantial agreement)
- Include 10-30% edge cases
- Version with semantic versioning and content hashing
- Run drift detection at regular intervals (monthly or per release)
- Use synthetic data only to fill gaps, always with human review
- Maintain a changelog with every version
- Track quality over time with maintenance checkpoints
- Separate the golden dataset from training data to avoid contamination

### Interview Questions

**Q1: How do you build a golden evaluation dataset from scratch?**

Start with raw data from production logs or existing datasets. Categorize items by domain/topic. Deduplicate using embedding or Jaccard similarity. Perform stratified sampling to maintain proportional representation. Have 3+ annotators independently label each item. Measure inter-annotator agreement with Cohen's/Fleiss' Kappa. Remove or re-annotate items with low agreement. Include 10-30% edge cases. Version the dataset with semantic versioning and content hashing. Deploy as the evaluation benchmark.

**Q2: What is Cohen's Kappa and why is percentage agreement insufficient?**

Cohen's Kappa measures agreement between two raters corrected for chance. The formula is Kappa = (P_observed - P_expected) / (1 - P_expected). Percentage agreement is insufficient because two annotators could agree frequently by chance, especially with imbalanced label distributions. Kappa subtracts expected chance agreement to give a more honest measure. Values above 0.6 indicate substantial agreement; above 0.8 is almost perfect.

**Q3: How do you detect and handle dataset drift?**

Compare the distribution of categories, difficulties, and answer keys between the baseline golden dataset and current production data using Total Variation Distance (TVD = 0.5 * sum|p_i - q_i|). If overall drift exceeds 0.25, the dataset needs updating. Monitor drift on a regular schedule (monthly or per release). When drift is detected, add new representative items, retire outdated ones, and create a new version.

**Q4: When should you use synthetic data for evaluation?**

Use synthetic data to fill coverage gaps (missing categories, difficulty levels, or edge cases) when real data is scarce. Always validate synthetic items through automated checks (valid format, no duplicates) and human review (factual correctness, realistic options). Never use unreviewed synthetic data in production benchmarks. Synthetic data augments but never replaces human-verified golden data.

**Q5: How do you version and maintain a golden dataset over time?**

Use semantic versioning (major.minor.patch). Generate content hashes for integrity verification. Track version diffs (added, removed, modified items). Maintain a changelog with author, date, and description. Run regular drift detection against production data. Track quality scores over time with maintenance checkpoints. Set up alerts for quality degradation. Enable rollback to previous versions when needed.

### Comparison Table: Agreement Metrics

| Metric                 | Annotators | Chance Correction | Use Case                         |
|------------------------|------------|-------------------|----------------------------------|
| Percentage Agreement   | 2          | No                | Quick sanity check only          |
| Cohen's Kappa          | 2          | Yes               | Pairwise annotator comparison    |
| Fleiss' Kappa          | 3+         | Yes               | Multi-annotator agreement        |

### Comparison Table: Drift Detection Severity

| TVD Range   | Severity | Action                              |
|-------------|----------|--------------------------------------|
| < 0.10      | None     | Routine review recommended           |
| 0.10 - 0.25 | Low      | Monitor more frequently              |
| 0.25 - 0.50 | Moderate | Update golden dataset                |
| > 0.50      | High     | Urgent: full dataset revision needed |

### Comparison Table: Dataset Quality Components

| Component            | Weight | Ideal Score | Measurement Method          |
|----------------------|--------|-------------|-----------------------------|
| Coverage             | 25%    | >80%        | Category + difficulty + answer entropy |
| Balance              | 20%    | Gini <0.3   | Gini coefficient, imbalance ratio      |
| Uniqueness           | 20%    | 100%        | Hash-based + Jaccard similarity        |
| Annotation Quality   | 20%    | Kappa >0.6  | Fleiss' Kappa                          |
| Edge Cases           | 15%    | 10-30%      | Heuristic edge case detection          |

### Further Reading

- Cohen, J. (1960). "A Coefficient of Agreement for Nominal Scales." -- Original Cohen's Kappa paper
- Fleiss, J.L. (1971). "Measuring Nominal Scale Agreement Among Many Raters." -- Fleiss' Kappa paper
- RAGAS documentation on golden dataset creation for RAG evaluation
- DeepEval golden dataset generation guides
- Anthropic's research on human evaluation and annotation best practices
