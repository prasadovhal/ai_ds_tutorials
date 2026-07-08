# Chapter 1: Foundations of LLM Evaluation

## Topics Covered

1. Why evaluation matters
2. Offline vs Online evaluation
3. Intrinsic vs Extrinsic evaluation
4. Human vs Automatic evaluation
5. Reference vs Reference-free evaluation
6. Model-based evaluation
7. Regression testing
8. Continuous evaluation
9. Evaluation lifecycle
10. Evaluation pipelines
11. Failure analysis & Error taxonomy
12. Evaluation dashboards
13. Evaluation in CI/CD

---

## 1. Why Evaluation Matters

**Problem:** You deploy an LLM and users complain it's wrong 40% of the time, but you never measured it.

**Intuition:** Evaluation is your speedometer for AI quality -- without it, you're flying blind because LLMs sound confident even when wrong.

**Key Reasons:**

1. **Measure quality** -- "How good is my model?"
2. **Compare models** -- "Is model A better than model B?"
3. **Detect regressions** -- "Did my latest change break something?"
4. **Build trust** -- "Can I deploy this to production?"
5. **Improve systems** -- "Where exactly does my model fail?"

---

## 2. Offline vs Online Evaluation

**Problem:** When should you evaluate -- before deployment, after, or both?

**Intuition:** Offline = exam before graduation (controlled, pre-deployment). Online = performance review at work (real-world, post-deployment). Use both.

```
OFFLINE EVALUATION                 ONLINE EVALUATION
+-----------------+                +-----------------+
| Fixed Dataset   |                | Live Traffic    |
|      |          |                |      |          |
|      v          |                |      v          |
| Run Model       |                | Run Model       |
|      |          |                |      |          |
|      v          |                |      v          |
| Compare with    |                | Log Response    |
| Ground Truth    |                | + User Feedback |
|      |          |                |      |          |
|      v          |                |      v          |
| Batch Report    |                | Rolling Metrics |
+-----------------+                +-----------------+
Before deployment                  After deployment
```

| Aspect       | Offline              | Online               |
|-------------|----------------------|----------------------|
| When        | Before deployment    | After deployment     |
| Data        | Fixed dataset        | Live traffic         |
| Speed       | Batch (minutes)      | Real-time (ms)       |
| Ground truth| Usually available    | Often unavailable    |
| Coverage    | Pre-selected cases   | Real distribution    |
| Use case    | Model selection      | Monitoring & alerts  |

---

## 3. Intrinsic vs Extrinsic Evaluation

**Problem:** Model gets 90% accuracy but users are unhappy -- how?

**Intuition:** Intrinsic = "How well does the model answer?" (task quality). Extrinsic = "Are users satisfied?" (real-world impact). A 90%-accurate model that takes 10s per response or fails on the 10% users care most about is extrinsically bad.

In production, extrinsic metrics often matter MORE. Users don't care about your F1 score.

---

## 4. Human vs Automatic Evaluation

**Problem:** Helpfulness and safety are hard to measure automatically, but human evaluation is slow and expensive.

**Intuition:** Automatic = calculator (fast, cheap, consistent, limited). Human = expert reviewer (slow, expensive, nuanced, subjective).

| What you're evaluating      | Automatic  | Human     |
|-----------------------------|-----------|-----------|
| Exact match / accuracy      | Best      |           |
| Format compliance           | Best      |           |
| Helpfulness                 |           | Best      |
| Creativity                  |           | Best      |
| Safety / toxicity           | Partial   | Best      |
| Factual correctness         | Partial   | Best      |
| Regression testing (CI/CD)  | Best      |           |
| User preference (A vs B)    |           | Best      |

**Scale comparison:** Automatic < 0.001s, $0. Human ~900s, ~$9 for 30 questions. At 10,000 questions: ~$3,000 and ~83 hours.

---

## 5. Reference vs Reference-Free Evaluation

**Problem:** Sometimes you have ground truth, sometimes you don't -- how do you evaluate each case?

**Intuition:** Reference-based = grading with an answer key. Reference-free = grading an essay without a rubric (just: "is it good?").

| Aspect          | Reference-based     | Reference-free          |
|-----------------|---------------------|-------------------------|
| Requires        | Ground truth        | Nothing                 |
| Measures        | Correctness         | Quality signals         |
| Precision       | High                | Lower                   |
| Cost            | Needs labeled data  | No labeling needed      |
| Use case        | Exact tasks (MCQ)   | Open-ended generation   |
| Example metrics | Accuracy, F1, BLEU  | Fluency, coherence, LLM-as-a-Judge |

---

## 6. Model-Based Evaluation (LLM-as-a-Judge Preview)

**Problem:** Human evaluation is expensive, BLEU doesn't capture meaning -- is there a middle ground?

**Intuition:** Use a stronger LLM to evaluate a weaker LLM's outputs, like a senior engineer reviewing a junior's code.

```
Question --> Model Under Test --> Response
                                     |
                                     v
              Judge Model <-- Judge Prompt ("Rate 1-5...")
                   |
                   v
              Score: 4/5, Reason: ...
```

**Key types:** (1) Pointwise -- score one response 1-5, (2) Pairwise -- "which is better?", (3) Pass/Fail -- binary acceptable?, (4) Rubric -- score against specific criteria.

| Aspect      | Detail                                              |
|-------------|-----------------------------------------------------|
| Advantages  | Cheaper than human, more nuanced than exact match, scalable, handles open-ended |
| Limitations | Judge biases (prefers longer answers), only as good as judge model, can be gamed |

---

## 7. Regression Testing

**Problem:** You update your prompt or model -- how do you know you didn't break something?

**Intuition:** Like running your test suite after every code change. Tests pass = safe to deploy; tests fail = investigate.

```
Golden Dataset --> Model v1 --> Predictions (baseline) --+
                                                         |--> COMPARE --> PASS/FAIL
Golden Dataset --> Model v2 --> Predictions (candidate) --+
```

**Practices:** Maintain a golden dataset, set a regression threshold (e.g., max 2% drop), run in CI/CD, track per-question regressions (a question v1 got right but v2 gets wrong is a red flag even if overall accuracy improves).

---

## 8. Continuous Evaluation

**Problem:** Your model was great at deploy time, but queries change and knowledge becomes outdated.

**Intuition:** Like regular health checkups -- check regularly to catch degradation early.

```
Deploy --> Monitor --> Evaluate --> Alert
  ^                                  |
  |                                  v
Improve <-- Diagnose <-- Triage <-- Issue
```

**What to monitor:** accuracy trends, latency trends, error rate distribution, input distribution shift, cost per query.

**Alert triggers:** accuracy drops >2%/week, P95 latency >3s, new error category appears, input distribution shifts.

---

## 9. Evaluation Lifecycle

**Problem:** Evaluation is a multi-step process that needs tracking and reproducibility, not just "compute accuracy."

**The 6 stages:** (1) Dataset Prep -- load, clean, validate, (2) Model Inference -- run model on eval set, (3) Metric Compute -- calculate accuracy/F1/etc., (4) Error Analysis -- classify failures, (5) Regression Check -- compare with previous version, (6) Report Generate -- create dashboard & artifacts.

---

## 10. Evaluation Pipelines

**Problem:** You run the same evaluation steps repeatedly -- how do you automate and standardize?

**Intuition:** Like a CI/CD pipeline but for model evaluation. Define once, run many times, compare results.

**Benefits:** Reproducibility, automation, comparability across model versions, extensibility, auditability.

---

## 11. Failure Analysis & Error Taxonomy

**Problem:** 80% accuracy means 20% are wrong -- but WHY? Different errors need different fixes.

| Error Type      | Description                             | Fix                      |
|----------------|-----------------------------------------|--------------------------|
| wrong_choice    | Picked an incorrect option              | Improve model/prompt     |
| hallucination   | Invented an answer not in choices       | Add output constraints   |
| no_response     | Failed to respond                       | Fix timeout/retry logic  |
| format_error    | Response couldn't be parsed             | Fix output parsing       |
| partial_correct | Right reasoning, wrong final pick       | Improve final selection  |

**Process:** Classify --> Quantify --> Prioritize --> Root cause --> Fix --> Verify with regression test. Fix the most common/impactful error category FIRST, then re-evaluate.

---

## 12. Evaluation Dashboard

**Problem:** You've computed 20 metrics -- how do you present them so stakeholders understand model health at a glance?

**Intuition:** Like a car dashboard -- key gauges front and center, details available on drill-down.

---

## 13. Evaluation in CI/CD

**Problem:** How do you automatically block bad models from reaching production?

**Intuition:** Like unit tests in CI -- if evaluation fails, the model can't deploy.

```
Code Change --> Build & Test --> Evaluation Gate --> Deploy
                                 accuracy >= 75%
                                 regression <= 2%
                                 PASS -> deploy
                                 FAIL -> block
```

**Practices:** Define pass/fail thresholds before deployment, test against a golden dataset, check both absolute quality and regression, log results for audit, alert on failures.

---

## Chapter 1 Summary

### Key Takeaways

1. Evaluation is mandatory -- it's your AI speedometer
2. Use OFFLINE before deployment, ONLINE after
3. INTRINSIC measures the task, EXTRINSIC measures the impact
4. AUTOMATIC is fast and cheap; HUMAN captures nuance
5. REFERENCE-BASED needs ground truth; REFERENCE-FREE doesn't
6. LLM-as-a-Judge bridges automatic and human evaluation
7. REGRESSION TESTING catches broken models before deployment
8. CONTINUOUS EVALUATION catches degradation after deployment
9. PIPELINES standardize and automate evaluation
10. ERROR TAXONOMY guides targeted improvements
11. DASHBOARDS communicate results to stakeholders
12. CI/CD GATES prevent bad models from reaching production

### Comparison Table

| Method          | Cost         | Speed        | Nuance       |
|-----------------|-------------|-------------|-------------|
| Automatic       | Near zero    | Milliseconds | Low          |
| Human           | $$$          | Hours/days   | High         |
| LLM-as-a-Judge  | $            | Seconds      | Medium-High  |
| Reference-based | Labeling $$  | Fast         | Medium       |
| Reference-free  | Zero         | Fast         | Low-Medium   |

### Common Mistakes

- Only evaluating once (before deployment)
- Only using one metric (accuracy is not enough)
- No regression testing (changes break things silently)
- No error analysis (you can't fix what you don't classify)
- Manual evaluation only (doesn't scale)
- Ignoring latency and cost (users care about these too)

### Interview Questions

1. **What's the difference between offline and online evaluation?**
   Offline uses a fixed dataset before deployment for batch assessment; online uses live traffic after deployment for continuous monitoring.

2. **When would you use reference-free evaluation?**
   When ground truth is unavailable, e.g., open-ended generation tasks where you check quality signals like fluency, coherence, or use LLM-as-a-Judge.

3. **How do you prevent model regressions in production?**
   Maintain a golden dataset, run automated regression tests in CI/CD with a threshold (e.g., max 2% drop), and track per-question regressions.

4. **What is LLM-as-a-Judge and when would you use it?**
   Using a stronger LLM to score a weaker LLM's outputs; use it when human eval is too expensive but automatic metrics like BLEU are too shallow.

5. **Design an evaluation pipeline for a RAG-based Q&A system.**
   Stages: dataset prep, retrieval evaluation (context precision/recall), generation evaluation (faithfulness/relevance), end-to-end accuracy, error analysis, regression check, report.

6. **What metrics would you track for continuous evaluation?**
   Accuracy/quality trends, latency (P50/P95), error rate distribution, input distribution shift, and cost per query.

7. **How would you set up evaluation gates in a CI/CD pipeline?**
   Define minimum accuracy and maximum regression thresholds, run against a golden dataset on every build, block deployment on failure, and log all results for audit.
