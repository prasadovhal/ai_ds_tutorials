# Chapter 6: Golden Dataset Engineering

Golden datasets are small, high-quality, human-verified evaluation sets serving as ground truth benchmarks for LLM systems. This chapter covers their full lifecycle: creation, annotation, versioning, regression testing, synthetic augmentation, and quality evaluation.

---

## 1. Why Golden Datasets & Dataset Types

### Problem
Public benchmarks don't reflect your domain, users, or edge cases. Training data is noisy. Without a curated, human-verified reference set, you can't detect regressions, compare prompts, or validate releases.

### Intuition
A golden dataset is the "exam paper" for your AI system -- covers all topics, various difficulty levels, error-free, small enough to maintain but large enough to be meaningful.

### Pipeline
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

### Dataset Type Definitions
- **Golden**: Small, human-verified benchmark. Always reviewed. Updated often.
- **Training**: Large, variable quality. Used for model learning.
- **Test**: Medium-sized, good quality. General evaluation.
- **Synthetic**: Any size, variable quality. Never used without human review.
- **Validation**: Tunes hyperparameters during development. Separate from final eval.
- **Benchmark**: Standardized public set (e.g., MMLU, HumanEval). Not domain-specific.
- **Production**: Real-world data from deployed systems. Source material for golden datasets.
- **Evaluation**: Broader term for any dataset measuring system performance.

---

## 2. Creating Golden Datasets: Sampling, Deduplication, Balancing

### Problem
Raw production data is noisy, redundant, and imbalanced -- overrepresents common cases, misses rare important ones.

### Key Operations

**Categorization**: Classify items by domain/topic/intent. Use keywords (simple) or LLM/human annotation (production).

**Difficulty Estimation**: Heuristics -- longer prompts = harder, high answer-choice similarity = harder. Production: use human ratings or model performance data.

**Deduplication** via Jaccard similarity:
```
Jaccard = |A intersection B| / |A union B|
```
Items above threshold (e.g., 0.8) are duplicates. Production: use embedding-based cosine similarity.

**Stratified Sampling**: Group by category/difficulty, sample proportionally from each group to maintain representation.

**Category Balancing**: Reduce majority categories (undersampling). For golden data, prefer keeping minority originals and flagging gaps over oversampling.

**Edge Case Detection** -- flag items with:
- Very long (>500 chars) or very short (<50 chars) prompts
- Negation words (not, except, without, never, neither)
- Multiple similar-length answer options

Target: 10-30% edge cases in the golden dataset.

### Creation Sources
Production logs, customer conversations, support tickets, search queries, agent trajectories, human-written examples, LLM-generated (with review), synthetic generation, failure-driven sampling, active learning, hard-negative mining.

---

## 3. Annotation Workflow, Rubrics, Inter-Annotator Agreement

### Problem
Labels are only as good as their annotators. Single-annotator labels can't quantify quality or catch bias.

### Workflow
1. Create guidelines and rubrics
2. 3+ annotators independently label each item
3. Determine consensus via majority vote
4. Measure inter-annotator agreement
5. Review low-agreement items
6. Generate per-annotator quality reports

### Annotation Rubric
```
5_excellent:    Clearly correct, unambiguous, well-supported
4_good:         Correct with minor stylistic issues
3_acceptable:   Mostly correct but could be more precise
2_poor:         Partially correct or misleading
1_unacceptable: Factually wrong or completely off-topic
```

### Escalation Criteria
Escalate when: two annotators disagree, average confidence < 0.6, or any annotator flags ambiguity.

### Cohen's Kappa (Pairwise Agreement)

Measures agreement between two annotators, correcting for chance:
```
Kappa = (P_observed - P_expected) / (1 - P_expected)
```
- **P_observed** = proportion where both agree
- **P_expected** = expected agreement by chance

**Interpretation scale:**
```
< 0.00    Poor (worse than chance)
0.00-0.20 Slight
0.21-0.40 Fair
0.41-0.60 Moderate
0.61-0.80 Substantial
0.81-1.00 Almost perfect
```

Why not just percentage agreement? Two annotators could agree 80% by chance if both favor the same labels. Kappa corrects for this.

### Fleiss' Kappa (3+ Annotators)

Extends Cohen's Kappa:
```
Fleiss' Kappa = (P_bar - P_e) / (1 - P_e)
```
- **P_bar** = mean per-item agreement proportion
- **P_e** = expected chance agreement from overall label distribution
- **P_i** = (sum of squared category counts - n_raters) / (n_raters * (n_raters - 1))

Same interpretation scale. Kappa > 0.6 is the minimum acceptable threshold for golden labels.

### Annotator Quality Control
Track per annotator: accuracy vs ground truth, average confidence, average labeling time (too fast = careless, too slow = confused), and items needing review.

---

## 4. Regression Testing & Prompt Comparison

### Problem
When you change a prompt, model, or pipeline, you need to detect regressions -- items the old version handled but the new one fails on.

### How It Works
1. Run both versions on the same golden dataset
2. Compare overall accuracy and per-item changes:
   - **Regressions**: v1 correct, v2 wrong
   - **Improvements**: v1 wrong, v2 correct
   - **Stable correct/wrong**: both same
3. Per-category breakdown catches hidden regressions
4. Flag if net accuracy delta < -2%

### Prompt Strategy Comparison
Compare zero-shot, few-shot, chain-of-thought, self-consistency on the same golden dataset. Rank by accuracy; measure spread (best - worst) to quantify prompt engineering impact.

---

## 5. Versioning, Drift Detection, Maintenance

### Problem
Golden datasets become stale as domains evolve, errors are found, and production data shifts. Without versioning and drift detection, evaluations become unreliable.

### Dataset Versioning
Use semantic versioning (major.minor.patch). Each version records: version number, date, author, description, item count, content hash (MD5 of IDs + labels for integrity).

### Version Diffing
Compare versions: added items, removed items, modified items (changed fields), unchanged items.

### Drift Detection via Total Variation Distance
```
TVD = 0.5 * sum(|p_i - q_i|)
```
- **p_i** = baseline proportion, **q_i** = current proportion
- Range: [0,1] where 0 = identical, 1 = completely different

Measure across: category drift, difficulty drift, answer drift.

**Severity thresholds:**
```
< 0.10    None
0.10-0.25 Low
0.25-0.50 Moderate (needs update)
> 0.50    High (urgent update needed)
```

### Maintenance Tracking
Track quality checkpoints (version, date, score, count, notes). Detect trends (improving/degrading/stable). Auto-recommend actions: quality < 70% triggers urgent review, 3+ declining checkpoints triggers warning, < 20 items triggers size warning.

```
Quality Score Over Time:
--------------------------------------------------
1.0.0    |############################............| 72.0%
1.1.0    |###############################.........| 78.0%
1.2.0    |################################........| 82.0%
2.0.0    |##################################......| 85.0%
--------------------------------------------------
```

---

## 6. Synthetic Data Generation

### Problem
Real evaluation data can be scarce for new domains, edge cases, or low-resource languages. Manual creation is expensive and slow.

### Workflow
1. Define templates or prompt LLM to generate questions
2. Generate candidates across target categories
3. Run automated validation (format, duplicates, valid labels)
4. Human review every item before golden inclusion

### Generation Methods
- **Template-based**: Fill placeholders in predefined patterns
- **LLM-based**: Prompt a model for domain-specific questions (production approach)
- **Perturbation-based**: Modify existing questions for variations

### Human Review Outcomes
- **Approved**: Factually correct, well-formed
- **Needs revision**: Options or question need improvement
- **Rejected**: Ambiguous or incorrect

### Critical Warnings
- All synthetic items MUST be human-reviewed before use
- Ground truth labels are placeholders -- verify each one
- Never use unreviewed synthetic data in production benchmarks

### When NOT to Use
When sufficient real data exists, for final benchmarks without review, when domain requires expert knowledge templates can't capture, or when synthetic patterns could contaminate training data.

---

## 7. Full Dataset Quality Evaluation

### Problem
You need a holistic quality score combining all dimensions -- not just individual checks.

### Component Scores and Weights

| Component          | Weight | What It Measures                              |
|--------------------|--------|-----------------------------------------------|
| Coverage           | 25%    | Category, difficulty, answer distribution     |
| Balance            | 20%    | Even distribution across dimensions           |
| Uniqueness         | 20%    | Absence of duplicates                         |
| Annotation Quality | 20%    | Inter-annotator agreement (Fleiss' Kappa)     |
| Edge Cases         | 15%    | 10-30% edge case inclusion                   |

### Coverage Analysis
Weighted combination: category coverage (40%), difficulty coverage (30%), answer balance via Shannon entropy (30%).
```
H = -sum(p_i * log2(p_i))
```
Maximum entropy = most balanced distribution.

### Balance Checking
- **Gini coefficient**: 0 = perfect equality, 1 = max inequality. Balanced if < 0.3.
- **Imbalance ratio**: max/min count. Balanced if < 3.

### Duplicate Detection
- **Exact**: MD5 hash of normalized text
- **Near**: Jaccard similarity above threshold (default 0.75)
- Uniqueness score = unique / total

### Grading Scale
```
A: 90-100  Excellent    B: 80-89  Good    C: 70-79  Acceptable
D: 60-69   Needs improvement              F: <60    Failing
```

---

## Chapter 6 Summary

### Key Takeaways
1. Golden datasets are small, high-quality, human-verified benchmarks
2. Build via: categorize -> deduplicate -> sample -> annotate -> version
3. Measure agreement with Cohen's/Fleiss' Kappa (target > 0.6)
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

### Pros/Cons
**Pros**: Reliable regression detection, domain-specific evaluation, quantifiable label quality, versioned and auditable, catches edge cases.
**Cons**: Expensive to create and maintain, requires multiple annotators, can become stale without drift monitoring, small size limits statistical power, annotation guidelines need expertise.

### Common Mistakes
- Using raw production data without dedup/balancing
- Single annotator (no way to measure label quality)
- Percentage agreement instead of Kappa
- Never updating as domain evolves
- Including unreviewed synthetic data
- Ignoring edge cases
- No versioning or drift detection

### Best Practices
- Start small (50-200 items), grow deliberately
- 3+ annotators, target Kappa > 0.6
- Include 10-30% edge cases
- Semantic versioning + content hashing
- Drift detection monthly or per release
- Synthetic data only to fill gaps, always with human review
- Separate golden dataset from training data (avoid contamination)

### Interview Questions

**Q1: How do you build a golden dataset from scratch?**
Categorize raw data -> deduplicate (Jaccard/embedding similarity) -> stratified sample -> 3+ annotators label independently -> measure Kappa -> remove/re-annotate low-agreement items -> include 10-30% edge cases -> version with semantic versioning.

**Q2: What is Cohen's Kappa and why not just percentage agreement?**
Kappa = (P_observed - P_expected)/(1 - P_expected). Corrects for chance agreement. Two annotators can agree frequently by chance with imbalanced labels. Kappa > 0.6 = substantial, > 0.8 = almost perfect.

**Q3: How do you detect dataset drift?**
Compare baseline vs current distributions using TVD = 0.5 * sum|p_i - q_i|. Monitor category, difficulty, and answer drift. TVD > 0.25 means update needed. Check monthly or per release.

**Q4: When should you use synthetic data?**
To fill coverage gaps when real data is scarce. Always validate via automated checks + human review. Never use unreviewed synthetic data in production benchmarks.

**Q5: How do you version and maintain a golden dataset?**
Semantic versioning, content hashing for integrity, version diffs, changelogs with author/date/description, regular drift detection, quality checkpoints over time, rollback capability.

### Comparison Tables

| Metric               | Annotators | Chance Correction | Use Case                      |
|----------------------|------------|-------------------|-------------------------------|
| Percentage Agreement | 2          | No                | Quick sanity check only       |
| Cohen's Kappa        | 2          | Yes               | Pairwise comparison           |
| Fleiss' Kappa        | 3+         | Yes               | Multi-annotator agreement     |

| Component          | Weight | Ideal       | Method                                 |
|--------------------|--------|-------------|----------------------------------------|
| Coverage           | 25%    | >80%        | Category + difficulty + answer entropy |
| Balance            | 20%    | Gini <0.3   | Gini coefficient, imbalance ratio      |
| Uniqueness         | 20%    | 100%        | Hash + Jaccard similarity              |
| Annotation Quality | 20%    | Kappa >0.6  | Fleiss' Kappa                          |
| Edge Cases         | 15%    | 10-30%      | Heuristic detection                    |

### Further Reading
- Cohen (1960): "A Coefficient of Agreement for Nominal Scales"
- Fleiss (1971): "Measuring Nominal Scale Agreement Among Many Raters"
- RAGAS documentation on golden dataset creation
- DeepEval golden dataset generation guides
