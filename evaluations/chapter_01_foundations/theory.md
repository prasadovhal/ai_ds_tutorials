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

### Problem

You deploy an LLM to answer science questions. Users complain it's wrong 40% of the time. But you didn't know because you never measured it.

### Why It Exists

LLMs are non-deterministic. They can sound confident while being completely wrong. Without evaluation, you're flying blind.

### Intuition

Think of evaluation like a speedometer in a car. The car runs fine without one — but you'll get a speeding ticket because you can't tell how fast you're going.

Evaluation is your speedometer for AI quality.

### Key Reasons

1. **Measure quality** — "How good is my model?"
2. **Compare models** — "Is model A better than model B?"
3. **Detect regressions** — "Did my latest change break something?"
4. **Build trust** — "Can I deploy this to production?"
5. **Improve systems** — "Where exactly does my model fail?"

### Takeaway

Evaluation is not optional. It's the difference between "I think it works" and "I know it works, here's the data."

---

## 2. Offline vs Online Evaluation

### Problem

When should you evaluate? Before deployment? After? Both?

### Intuition

- **OFFLINE** = exam before graduation (controlled, complete, pre-deployment)
- **ONLINE** = performance review at work (real-world, continuous, post-deployment)

### ASCII Diagram

```
OFFLINE EVALUATION                 ONLINE EVALUATION
┌──────────────────┐               ┌──────────────────┐
│  Fixed Dataset   │               │  Live Traffic    │
│  (train.csv)     │               │  (user queries)  │
│       │          │               │       │          │
│       ▼          │               │       ▼          │
│  Run Model       │               │  Run Model       │
│       │          │               │       │          │
│       ▼          │               │       ▼          │
│  Compare with    │               │  Log Response    │
│  Ground Truth    │               │  + User Feedback │
│       │          │               │       │          │
│       ▼          │               │       ▼          │
│  Batch Report    │               │  Rolling Metrics │
└──────────────────┘               └──────────────────┘
Before deployment                  After deployment
```

### Comparison Table

| Aspect       | Offline              | Online               |
|-------------|----------------------|----------------------|
| When        | Before deployment    | After deployment     |
| Data        | Fixed dataset        | Live traffic         |
| Speed       | Batch (minutes)      | Real-time (ms)       |
| Ground truth| Usually available    | Often unavailable    |
| Coverage    | Pre-selected cases   | Real distribution    |
| Use case    | Model selection      | Monitoring & alerts  |

### Best Practice

Use BOTH. Offline to validate before deploy, Online to catch issues that only appear with real users.

---

## 3. Intrinsic vs Extrinsic Evaluation

### Problem

Your model gets 90% accuracy on the test set, but users are unhappy. How is that possible?

### Intuition

- **INTRINSIC** = "How well does the model answer questions?" (task quality)
- **EXTRINSIC** = "Are users actually satisfied?" (real-world impact)

A model can be intrinsically good but extrinsically bad:
- 90% accurate but takes 10 seconds per response (too slow)
- 90% accurate but fails on the 10% that matters most to users

### Key Insight

In production, extrinsic metrics often matter MORE than intrinsic ones. Users don't care about your F1 score — they care about their experience.

---

## 4. Human vs Automatic Evaluation

### Problem

Some qualities (helpfulness, creativity, safety) are hard to measure automatically. But human evaluation is slow and expensive.

### Intuition

- **AUTOMATIC** = Calculator (fast, cheap, consistent, limited)
- **HUMAN** = Expert reviewer (slow, expensive, nuanced, subjective)

### When to Use Which

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

### Key Insight

- Automatic evaluation: < 0.001 seconds, $0 cost
- Human evaluation: ~900 seconds, ~$9 cost (for just 30 questions!)

At scale (10,000 questions), human evaluation would cost ~$3,000 and take ~83 hours. That's why automatic metrics are essential for day-to-day evaluation, with human evaluation reserved for high-stakes decisions.

---

## 5. Reference vs Reference-Free Evaluation

### Problem

Sometimes you have the correct answer (ground truth). Sometimes you don't. How do you evaluate in each case?

### Intuition

- **REFERENCE-BASED** = Grading an exam with an answer key
- **REFERENCE-FREE** = Grading an essay without a rubric (just: "is it good?")

### ASCII Diagram

```
REFERENCE-BASED                    REFERENCE-FREE
┌────────────┐                     ┌────────────┐
│  Question  │                     │  Question  │
│     +      │                     │     +      │
│  Answer    │                     │  Answer    │
│     +      │                     │     │      │
│  Ground    │                     │     ▼      │
│  Truth     │                     │  Quality   │
│     │      │                     │  Checks    │
│     ▼      │                     │  (format,  │
│  Compare   │                     │   length,  │
│  Match?    │                     │   valid?)  │
└────────────┘                     └────────────┘
```

### Comparison Table

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

### Problem

Human evaluation is expensive. Automatic metrics like BLEU don't capture meaning. Is there a middle ground?

### Intuition

Use a STRONGER LLM to evaluate a WEAKER LLM's outputs. Like having a senior engineer review a junior's code.

### How It Works

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│ Question │───▶│ Model Under  │───▶│ Response     │
└──────────┘    │ Test (e.g.   │    └──────┬───────┘
                │ Mistral 7B)  │           │
                └──────────────┘           │
                                           ▼
                ┌──────────────┐    ┌──────────────┐
                │ Judge Model  │◀───│ Judge Prompt │
                │ (e.g. GPT-4 │    │ "Rate this   │
                │  or Mistral  │    │  response    │
                │  Large)      │    │  1-5..."     │
                └──────┬───────┘    └──────────────┘
                       │
                       ▼
                ┌──────────────┐
                │ Score: 4/5   │
                │ Reason: ...  │
                └──────────────┘
```

### Key Types of Model-Based Evaluation

1. **Pointwise** — Score one response at a time (1-5)
2. **Pairwise** — Compare two responses: "Which is better?"
3. **Pass/Fail** — Binary: "Is this acceptable?"
4. **Rubric** — Score against specific criteria

### Advantages

- Cheaper than human evaluation
- More nuanced than exact match
- Scalable to thousands of examples
- Can evaluate open-ended responses

### Limitations

- Judge model can have biases (prefers longer answers, etc.)
- Only as good as the judge model
- Can be gamed (model learns what judge likes, not what's correct)

---

## 7. Regression Testing

### Problem

You update your prompt, fine-tune your model, or change your retrieval pipeline. How do you know you didn't break something?

### Intuition

Like running your test suite after every code change. If the tests pass → safe to deploy. If tests fail → something broke, investigate before deploying.

### How It Works

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│ Golden   │────▶│ Model v1 │────▶│ Predictions  │──┐
│ Dataset  │     └──────────┘     │ (baseline)   │  │
│          │                      └──────────────┘  │  COMPARE
│          │     ┌──────────┐     ┌──────────────┐  │  ───────▶ PASS/FAIL
│          │────▶│ Model v2 │────▶│ Predictions  │──┘
└──────────┘     └──────────┘     │ (candidate)  │
                                  └──────────────┘
```

### Best Practices

1. Maintain a "golden dataset" of critical test cases
2. Set a clear regression threshold (e.g., max 2% drop allowed)
3. Run regression tests automatically in CI/CD
4. Track not just overall accuracy, but PER-QUESTION regressions
5. A question that v1 got right but v2 gets wrong is a RED FLAG — even if v2's overall accuracy is higher

---

## 8. Continuous Evaluation

### Problem

Your model was great when you deployed it. But the world changes. User queries change. Knowledge becomes outdated. How do you know when your model starts degrading?

### Intuition

Like regular health checkups. You don't wait until you're sick to see a doctor. You check regularly to catch problems early.

### Continuous Evaluation Loop

```
┌──────────────────────────────────────────────────┐
│                                                  │
│   Deploy ──▶ Monitor ──▶ Evaluate ──▶ Alert     │
│     ▲                                   │        │
│     │                                   ▼        │
│   Improve ◀── Diagnose ◀── Triage ◀── Issue     │
│                                                  │
└──────────────────────────────────────────────────┘
```

### What to Monitor

1. **Accuracy / quality metrics** — Are we getting better or worse?
2. **Latency trends** — Is the model getting slower?
3. **Error rate distribution** — Are new error types appearing?
4. **Input distribution shift** — Are users asking different things?
5. **Cost per query** — Is inference getting more expensive?

### Alert Triggers

- Accuracy drops more than 2% in a week
- P95 latency exceeds 3 seconds
- New error category appears
- Input distribution shifts significantly

---

## 9. Evaluation Lifecycle

### Problem

Evaluation isn't just "compute accuracy." It's a multi-step process that needs to be tracked and reproduced.

### The 6 Stages

```
┌───────────────────┐
│ 1. Dataset Prep   │  Load, clean, validate data
│         │         │
│         ▼         │
│ 2. Model Inference│  Run model on evaluation set
│         │         │
│         ▼         │
│ 3. Metric Compute │  Calculate accuracy, F1, etc.
│         │         │
│         ▼         │
│ 4. Error Analysis  │  Classify and analyze failures
│         │         │
│         ▼         │
│ 5. Regression Check│  Compare with previous version
│         │         │
│         ▼         │
│ 6. Report Generate │  Create dashboard & artifacts
└───────────────────┘
```

---

## 10. Evaluation Pipelines

### Problem

You run the same evaluation steps repeatedly. How do you automate and standardize this?

### Intuition

Like a CI/CD pipeline but for model evaluation. Define once, run many times, compare results.

### Pipeline Benefits

1. **Reproducibility** — Same steps, same order, every time
2. **Automation** — No manual steps, runs in CI/CD
3. **Comparability** — Same pipeline for all model versions
4. **Extensibility** — Add/remove steps as needed
5. **Auditability** — Track what was run and when

---

## 11. Failure Analysis & Error Taxonomy

### Problem

Knowing your model is 80% accurate tells you 20% of answers are wrong — but WHY are they wrong? Different errors need different fixes.

### Error Taxonomy for MCQ

| Error Type      | Description                             |
|----------------|-----------------------------------------|
| wrong_choice    | Model picked an incorrect option        |
| hallucination   | Model invented an answer not in choices |
| no_response     | Model failed to respond                 |
| format_error    | Response couldn't be parsed             |
| partial_correct | Right reasoning, wrong final pick       |

### Why It Matters

- `wrong_choice` → improve the model/prompt
- `hallucination` → add output constraints
- `no_response` → fix timeout/retry logic
- `format_error` → fix output parsing

Each error type has a DIFFERENT fix.

### Failure Analysis Process

1. **CLASSIFY** — Put each error into a category
2. **QUANTIFY** — How many of each type?
3. **PRIORITIZE** — Which error type hurts the most?
4. **ROOT CAUSE** — Why does this error happen?
5. **FIX** — Apply targeted fix for that error type
6. **VERIFY** — Run regression test to confirm the fix works

### Common Mistake

Trying to fix all errors at once. Instead, fix the most common/impactful error category FIRST, then re-evaluate.

---

## 12. Evaluation Dashboard

### Problem

You've computed 20 metrics. How do you present them so that a stakeholder can understand the model's health at a glance?

### Intuition

Like a car dashboard — the key gauges are front and center. Details available if you look deeper, but the summary is immediate.

---

## 13. Evaluation in CI/CD

### Problem

How do you automatically block bad models from reaching production?

### Intuition

Like unit tests in CI. If tests fail, the PR can't merge. If evaluation fails, the model can't deploy.

### CI/CD Pipeline with Evaluation Gates

```
┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐
│ Code     │──▶ │ Build    │──▶ │ Evaluation   │──▶ │ Deploy   │
│ Change   │    │ & Test   │    │ Gate         │    │          │
└──────────┘    └──────────┘    │              │    └──────────┘
                                │ ✓ accuracy   │
                                │   >= 75%     │
                                │ ✓ regression │
                                │   <= 2%      │
                                │              │
                                │ PASS → deploy│
                                │ FAIL → block │
                                └──────────────┘
```

### CI/CD Evaluation Best Practices

1. Define clear pass/fail thresholds BEFORE deployment
2. Test against a golden dataset (not random samples)
3. Check BOTH absolute quality AND regression
4. Log all evaluation results for audit trail
5. Alert on failures — don't just silently block
6. Include evaluation time in your deployment budget

---

## Chapter 1 Summary

### Key Takeaways

1. Evaluation is mandatory, not optional — it's your AI speedometer
2. Use OFFLINE evaluation before deployment, ONLINE after
3. INTRINSIC measures the task, EXTRINSIC measures the impact
4. AUTOMATIC is fast and cheap; HUMAN captures nuance
5. REFERENCE-BASED needs ground truth; REFERENCE-FREE doesn't
6. LLM-as-a-Judge bridges the gap between automatic and human
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

1. What's the difference between offline and online evaluation?
2. When would you use reference-free evaluation?
3. How do you prevent model regressions in production?
4. What is LLM-as-a-Judge and when would you use it?
5. Design an evaluation pipeline for a RAG-based Q&A system.
6. What metrics would you track for continuous evaluation?
7. How would you set up evaluation gates in a CI/CD pipeline?
