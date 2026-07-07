# Chapter 9: Production Evaluation

Production evaluation is about maintaining quality **AFTER** deployment. While offline evaluation tells you how a model performs on test data, production evaluation ensures your LLM system continues to work correctly in the real world, with real users, under real conditions.

This chapter covers nine key systems for production evaluation:

1. **Regression Testing** -- Catch accuracy regressions before release
2. **Canary Testing** -- Gradual rollout with automatic rollback
3. **Shadow Deployment** -- Risk-free A/B comparison on live traffic
4. **Drift Detection** -- Detect input/output/concept distribution shifts
5. **Production Monitoring** -- Sliding-window metrics for real-time tracking
6. **Alerting** -- Threshold + anomaly alerts with escalation
7. **CI/CD Quality Gates** -- Automated pass/fail deployment decisions
8. **Versioning** -- Track prompts, datasets, and models over time
9. **Continuous Benchmarking** -- Long-term performance trending and charts

---

## 1. Regression Testing

### Problem

You have a working LLM in production. You make changes -- update the prompt, swap the model, tune hyperparameters -- and suddenly queries that used to work correctly now fail. This is a **regression**: a previously correct behavior that becomes incorrect after a change.

### Why It Exists

LLMs are not deterministic software. A small prompt change can improve accuracy on one category of questions while silently breaking another. Without regression testing, you only discover these failures after users complain.

### Intuition

Think of it like a teacher grading exams. You have a "golden" answer key (the golden dataset). When a student (model version) takes the exam, you compare their answers to the key. If the new student gets answers wrong that the previous student got right, those are regressions.

### How It Works

Regression testing compares a new model's predictions against a golden dataset to detect cases where previously correct answers become wrong.

```
Golden Dataset (versioned)
    |
    v
[Run Model] --> Predictions
    |
    v
[Compare] --> {passed, failed, regressions, improvements}
    |
    v
[Report] --> Pass/Fail decision
```

### Key Concepts

- **Golden Dataset**: A versioned, curated set of questions with known correct answers. Used as the stable reference for all regression tests.
- **Baseline Predictions**: The predictions from the current production model (the model you are comparing against).
- **Regression**: A question that the baseline model answered correctly but the new model answers incorrectly.
- **Improvement**: A question that the baseline model answered incorrectly but the new model answers correctly.
- **Regression Rate**: The fraction of previously correct answers that become wrong. Calculated as: `regressions / baseline_correct`.
- **Threshold**: The maximum allowed regression rate. A common default is 5% (0.05). If the regression rate exceeds this threshold, the test fails.
- **Stable Correct**: Questions both models answer correctly.
- **Stable Wrong**: Questions both models answer incorrectly.

### How the Report Works

A regression test report shows:
- Model version and dataset version
- New model accuracy vs. baseline accuracy
- The accuracy delta (positive means improvement, negative means degradation)
- Number of regressions and the regression rate vs. the threshold
- Number of improvements
- Pass/fail decision based on whether the regression rate exceeds the threshold

For each regression, you can drill down to see:
- The question ID
- The expected ground truth answer
- What the old model predicted (correct)
- What the new model predicted (incorrect)

### Example: Good Model vs. Bad Model

A good model (v1.1-improved) might show:
- Accuracy improved from baseline
- Low regression rate (below 5% threshold)
- Result: **PASSED**

A bad model (v2.0-regression) might show:
- Accuracy dropped significantly from baseline
- High regression rate (well above 5% threshold)
- Result: **FAILED**
- Specific regressions listed with question IDs for debugging

---

## 2. Canary Testing

### Problem

You have a new model version ready to deploy. Deploying it to 100% of traffic immediately is risky -- if it has a problem, all users are affected at once. You need a way to test it gradually on real traffic.

### Why It Exists

Lab testing cannot fully replicate production conditions. Real users send unexpected queries, traffic patterns vary, and edge cases emerge that test datasets never cover. Canary testing lets you validate on real traffic with limited blast radius.

### Intuition

Think of the "canary in a coal mine." Miners would send a canary bird into the mine first. If the canary was fine, the air was safe. If not, the miners stayed out. Similarly, you send a small percentage of traffic to the new model first. If quality holds, you increase traffic. If quality drops, you roll back.

### How It Works

Routes a small percentage of traffic to a new model version and progressively increases if quality holds.

```
Traffic --> [Load Balancer]
                |
           +---------+---------+
           |                   |
      [Control]           [Canary]
      (1 - pct)%           pct %
           |                   |
      [Evaluate]          [Evaluate]
           |                   |
           +----> [Compare] <--+
                      |
                 [Promote / Rollback]
```

### Key Concepts

- **Control Group**: Traffic served by the current production model. This is your baseline.
- **Canary Group**: Traffic served by the new model version being tested.
- **Canary Percentage**: The fraction of traffic routed to the canary. Typically starts at 5% and increases through stages.
- **Rollout Stages**: Progressive stages of increasing canary traffic. A typical progression is: 5% (smoke test) -> 10% (initial canary) -> 25% (expanded canary) -> 50% (half traffic) -> 100% (full rollout).
- **Accuracy Threshold**: The minimum absolute accuracy the canary must achieve (e.g., 70%).
- **Max Regression Rate**: The maximum allowed accuracy gap between control and canary (e.g., 10%).
- **Promote**: If the canary passes all stages, deploy it as the new production model.
- **Rollback**: If the canary fails at any stage, revert all traffic to the control model and stop the rollout.
- **Minimum Requests per Stage**: The minimum number of canary requests required before evaluating a stage (e.g., 20). This prevents making decisions on too little data.

### Rollout Report

A rollout report shows each stage with:
- Stage name and traffic percentage
- Control accuracy vs. canary accuracy
- Accuracy delta (canary minus control)
- Pass/fail status

If the canary fails at any stage, the rollout is halted and the final status is "ROLLED_BACK". If all stages pass, the final status is "PROMOTED".

### Example: Failed vs. Successful Canary

A failed canary (low-quality model, e.g., 72% accuracy vs. 80% control) might fail at the initial stage because the accuracy gap exceeds the max regression rate.

A successful canary (high-quality model, e.g., 84% accuracy vs. 80% control) passes through all stages and is promoted to full traffic.

---

## 3. Shadow Deployment

### Problem

You want to compare a new model against your production model on real traffic, but you cannot risk serving bad responses to users. How do you test with real data without affecting users?

### Why It Exists

Canary testing still serves some users the new model's responses. Shadow deployment eliminates all user-facing risk by running the new model in parallel but never serving its responses.

### Intuition

Imagine a new hire shadowing an experienced employee. The new hire handles every task alongside the experienced employee, but only the experienced employee's work goes to the client. Afterward, you compare their outputs offline to decide if the new hire is ready.

### How It Works

Runs a new model in parallel on the same traffic without serving its responses, then compares accuracy offline.

```
Request --> [Primary Model v1.1] --> Response to user
    |
    +----> [Shadow Model v2.0]  --> Logged (not served)
                |
           [Compare Primary vs Shadow]
                |
           [Promotion Decision]
```

### Key Concepts

- **Primary Model**: The current production model whose responses are served to users.
- **Shadow Model**: The new model running in parallel. Its responses are logged but never served.
- **Agreement Rate**: The fraction of questions where both models give the same prediction. High agreement means the models behave similarly.
- **Both Correct**: Questions where both models answer correctly.
- **Both Wrong**: Questions where both models answer incorrectly.
- **Primary Only Correct**: Questions where the primary model is right but the shadow is wrong (these would be regressions if you deployed the shadow).
- **Shadow Only Correct**: Questions where the shadow model is right but the primary is wrong (these are improvements the shadow offers).
- **Disagreements**: Questions where the two models give different predictions, regardless of correctness.

### Promotion Recommendations

Based on the comparison, the system generates a recommendation:
- **PROMOTE**: Shadow outperforms primary significantly (more than 2% better)
- **CONSIDER**: Shadow slightly better, run a longer test
- **NEUTRAL**: Performance equivalent, decide based on other factors (latency, cost)
- **CAUTION**: Shadow slightly worse, investigate regressions
- **REJECT**: Shadow significantly worse than primary

### Example: Better Shadow vs. Worse Shadow

A better shadow model (85% vs. 80% primary accuracy) shows many shadow-only correct answers and earns a PROMOTE recommendation.

A worse shadow model (65% vs. 80% primary accuracy) shows many primary-only correct answers and earns a REJECT recommendation.

---

## 4. Drift Detection

### Problem

Your model was trained and evaluated on data from a specific time period. Over time, the real-world data changes. Users start asking different types of questions, the distribution of topics shifts, or the relationship between inputs and correct answers evolves. Your model's accuracy degrades silently.

### Why It Exists

Models are static snapshots of patterns learned during training. The world is not static. Drift detection catches the gap between what your model expects and what it actually encounters.

### Intuition

Imagine a weather forecasting model trained on summer data. When fall arrives, the input distribution (temperatures, humidity patterns) shifts. The model's predictions become less accurate -- not because the model broke, but because the world changed. Drift detection is the system that notices "the inputs look different now."

### How It Works

Detects when input distribution, output distribution, or the input-output relationship changes over time.

```
[Reference Window] --+
                     |--> [Statistical Test] --> Drift Score
[Current Window]  ---+                              |
                                              [Threshold]
                                                    |
                                            [Alert if exceeded]
```

### Key Concepts

#### Three Types of Drift

1. **Input Drift**: The distribution of incoming questions changes. Detected by comparing prompt length distributions and answer distributions between reference and current windows using KL divergence and length shift percentage.

2. **Output Drift**: The distribution of model predictions changes. Even if inputs stay the same, the model might start predicting different answer distributions. Detected using KL divergence on prediction distributions.

3. **Concept Drift**: The relationship between inputs and correct answers changes. This manifests as accuracy degradation over time. Detected by comparing accuracy between reference and current windows.

#### Statistical Methods

- **KL Divergence (Kullback-Leibler Divergence)**: Measures how one probability distribution differs from another. A KL divergence of 0 means the distributions are identical. Higher values indicate more drift. Typical threshold: 0.10.

  Formula: `D_KL(P || Q) = sum(P(x) * log(P(x) / Q(x)))` for all x

  Uses Laplace smoothing to handle zero probabilities.

- **Length Shift**: Compares average prompt lengths between windows. Computed as: `|current_avg_length - reference_avg_length| / reference_avg_length`. Typical threshold: 15-20%.

- **Accuracy Delta**: Compares accuracy between windows. Computed as: `reference_accuracy - current_accuracy`. Typical threshold: 8-10%.

#### Severity Levels

The severity of drift is determined by how many types of drift are detected simultaneously:
- **None**: No drift detected in any dimension
- **Low**: One type of drift detected
- **Medium**: Two types of drift detected
- **High**: All three types of drift detected

### Drift Report

A drift detection report shows for each drift type:
- Whether drift was detected (DRIFTED or STABLE)
- The metric values vs. thresholds
- For input drift: length shift percentage and KL divergence
- For output drift: KL divergence on prediction distributions
- For concept drift: accuracy delta between windows
- Overall severity level

### Example: Progressive Drift

In a typical production scenario, drift increases over time:
- Window 0 (reference): Baseline, no drift
- Window 1: Low drift factor, accuracy near baseline, all metrics stable
- Window 2-3: Moderate drift, some metrics start shifting
- Window 4-5: High drift factor, accuracy degraded significantly, input/output/concept all drifted, severity = HIGH

---

## 5. Production Monitoring

### Problem

You need to know how your model is performing right now, not just at evaluation time. Quality can degrade between scheduled evaluations due to traffic spikes, infrastructure issues, or gradual drift.

### Why It Exists

Evaluation runs periodically (daily, weekly). Production monitoring runs continuously. It gives you a real-time view of model health through sliding time windows.

### Intuition

Think of a heart rate monitor. It does not just take your pulse once a day -- it tracks your heartbeat continuously, showing trends and alerting on anomalies. Production monitoring does the same for your model's accuracy, latency, and error rates.

### How It Works

Tracks accuracy, latency, and error rates across sliding time windows.

```
[Incoming Requests] --> [Log Entry]
                            |
                       [Window Buffer]
                            |
                    [Compute Metrics]
                            |
                 [Dashboard / Alert Manager]
```

### Key Concepts

- **Window Size**: The number of recent requests included in each metric computation (e.g., 50 requests). Smaller windows are more responsive but noisier; larger windows are smoother but slower to react.
- **Sliding Window**: The window moves forward by a step size, creating overlapping windows for smoother metric tracking.
- **Step Size**: How far the window advances between computations. Typically half the window size.

#### Metrics Tracked

- **Accuracy**: Fraction of correct predictions in the window
- **Error Rate**: `1 - accuracy`
- **Latency Percentiles**: P50 (median), P95, P99 -- measuring response time distribution
  - P50: Half of requests are faster than this
  - P95: 95% of requests are faster than this (used for SLA targets)
  - P99: 99% of requests are faster than this (catches worst-case outliers)
- **Latency Mean/Min/Max**: Additional latency statistics
- **Prediction Distribution**: How predictions are distributed across answer classes
- **Model Version Distribution**: Which model versions are serving traffic

#### Trend Analysis

The monitor computes linear trends over the metrics history:
- **Improving**: Metric is trending upward (positive slope for accuracy)
- **Degrading**: Metric is trending downward (negative slope for accuracy)
- **Stable**: No significant trend (slope near zero)

The slope is computed using simple linear regression over the metric values across windows.

---

## 6. Alerting

### Problem

You cannot stare at dashboards 24/7. You need automated alerts that tell you when something goes wrong, with appropriate severity levels and escalation.

### Why It Exists

Production issues happen at 3am. Alerting is the bridge between monitoring (passive observation) and incident response (active intervention).

### Intuition

Think of a home security system. It has rules: if a door opens after midnight, trigger a warning. If the alarm is triggered three times in a row, escalate to the police. Similarly, the alert manager has rules for model metrics, with escalation when problems persist.

### How It Works

Fires threshold-based and anomaly-based alerts with automatic escalation after repeated violations.

```
[Metrics] --> [Alert Rules Engine]
                   |
            +------+------+
            |             |
      [Threshold]   [Anomaly]
            |             |
            v             v
       [Alert Queue] <---+
            |
      [Escalation]
            |
      [Notification]
```

### Key Concepts

#### Alert Types

1. **Threshold Alerts**: Fire when a metric crosses a fixed boundary.
   - Example: "Alert if accuracy drops below 72%"
   - Example: "Alert if P95 latency exceeds 450ms"
   - Operators supported: `>=`, `<=`, `>`, `<`, `==`

2. **Anomaly Alerts**: Fire when a metric deviates significantly from a healthy baseline.
   - Uses standard deviation (z-score) to detect unusual values
   - z-score = `|current_value - baseline_mean| / baseline_std`
   - Fires when z-score exceeds the sigma threshold (typically 2.0)
   - Example: If healthy accuracy is 0.78-0.81 (mean=0.795, std=0.009), an accuracy of 0.55 has a z-score of ~27, far exceeding the threshold

#### Severity Levels

- **info**: Informational, no action needed
- **warning**: Investigate soon
- **critical**: Immediate action required

#### Escalation

Alerts automatically escalate after repeated violations:
- If a warning-level alert fires 3 or more times consecutively, it is escalated to **critical** severity
- When the metric recovers (alert condition no longer met), the consecutive fire counter resets to zero

#### Alert Summary

The alert manager tracks all fired alerts and provides a summary:
- Total alerts fired
- Breakdown by severity (warning vs. critical)
- Breakdown by rule name

### Example: Degradation and Recovery Scenario

A typical scenario might show:
1. **Healthy**: No alerts fired (accuracy=0.80, latency=400ms)
2. **Degrading**: Warning alert for low accuracy (accuracy=0.73)
3. **Worse**: Multiple alerts -- low accuracy + high latency + anomaly detected
4. **Critical**: Critical accuracy alert fires, accuracy anomaly escalates
5. **Recovering**: Some alerts still fire but trend improves
6. **Recovered**: No alerts fired, metrics back to normal

---

## 7. CI/CD Integration and Evaluation Gates

### Problem

Manual deployment decisions are slow, subjective, and error-prone. Different team members may have different standards for "good enough to deploy." You need automated, objective deployment criteria.

### Why It Exists

CI/CD (Continuous Integration / Continuous Deployment) automates the build-test-deploy cycle for software. Evaluation gates extend this to LLM systems by requiring models to pass quality checks before deployment.

### Intuition

Think of airport security checkpoints. Every passenger (model version) must pass through multiple gates: ID check (accuracy gate), bag scan (regression gate), metal detector (latency gate). If you fail any mandatory gate, you do not board the plane (deploy to production). Some gates are "blocking" (must pass) and some are "warnings" (logged but not blocking).

### How It Works

Each deployment stage must pass evaluation gates; a single blocking failure halts the pipeline.

```
[Code Push] --> [Build] --> [Unit Tests]
     |
     v
[Eval Gate 1: Accuracy] --> Pass? --> [Eval Gate 2: Regression]
     |                                       |
     | Fail                                  | Pass?
     v                                       v
[REJECT]                     [Eval Gate 3: Latency] --> Pass?
                                      |                    |
                                      | Fail               v
                                      v             [Eval Gate 4: Drift]
                                  [REJECT]                 |
                                                      Pass? --> [DEPLOY]
                                                        |
                                                    [REJECT]
```

### Key Concepts

#### Gate Configuration

Each gate has:
- **Name**: Human-readable identifier (e.g., "accuracy_gate")
- **Metric**: The metric key to check (e.g., "accuracy")
- **Operator**: Comparison operator (`>=`, `<=`, `>`, `<`, `==`)
- **Threshold**: The pass/fail boundary value
- **Description**: Human-readable explanation of the gate's purpose
- **Blocking**: If True, pipeline stops on failure. If False, logs a warning but continues.

#### Typical Production Gates

| Gate | Metric | Condition | Description |
|------|--------|-----------|-------------|
| accuracy_gate | accuracy | >= 0.75 | Min 75% accuracy on golden set |
| regression_gate | regression_rate | <= 0.05 | Max 5% regression rate |
| latency_gate | p95_latency_ms | <= 500 | P95 latency under 500ms |
| drift_gate | kl_divergence | <= 0.10 | Output drift within tolerance |

#### Pipeline Decision

- **DEPLOY**: All blocking gates passed. The model is approved for deployment.
- **REJECT**: At least one blocking gate failed. Deployment is halted. The report identifies the first failing gate.

#### Gate Report

The pipeline report shows:
- Version being evaluated
- Number of gates passed out of total
- Each gate with [PASS], [FAIL], or [ERR] status
- The metric value vs. threshold for each gate
- Whether each gate is blocking or warning-only
- Final decision: DEPLOY or REJECT
- If rejected: which gate blocked deployment

### Example: Passing vs. Failing Pipeline

A good model (v2.1) with metrics like accuracy=0.83, regression_rate=0.03, p95_latency=380ms, kl_divergence=0.05 passes all gates and gets the DEPLOY decision.

A bad model (v2.0) with metrics like accuracy=0.65, regression_rate=0.12 fails the accuracy and regression gates and gets the REJECT decision, with deployment blocked at the first failing gate.

---

## 8. Prompt, Dataset, and Model Versioning

### Problem

Over time, you change prompts, add data to golden datasets, and release new model versions. Without versioning, you cannot answer: "Which prompt was running when accuracy dropped last Tuesday?" or "What changed between the version that worked and the one that broke?"

### Why It Exists

LLM systems have three axes of change: the prompt template, the evaluation dataset, and the model itself. Any of these can cause a quality regression. Versioning lets you track, compare, and roll back each independently.

### Intuition

Think of version control (Git) for code. You would never deploy code without tracking changes. Prompt versioning does the same for prompt templates, dataset versioning tracks evaluation data changes, and model versioning tracks which model is running.

### How It Works

Tracks prompt templates with content-addressable hashing, records performance per version, and supports rollback.

### Prompt Versioning

```
[New Prompt] --> [Hash & Version]
                      |
                 [Store in Registry]
                      |
            +---------+---------+
            |                   |
       [Evaluate]         [Compare]
            |                   |
            v                   v
      [Metrics Log]     [Diff Report]
            |
       [Set Active / Rollback]
```

#### Key Concepts

- **Content-Addressable Hashing**: Each prompt template is hashed using SHA-256. Identical content always produces the same hash, so you can detect duplicate registrations and verify content integrity.
- **Version Table**: Lists all registered prompt versions with their hash, label, active status, average accuracy, and number of performance samples.
- **Performance Logging**: Each prompt version can have multiple performance snapshots logged against it (accuracy, latency, etc.).
- **Version Comparison**: Compare two prompt versions to see:
  - Lines added and removed (simple diff)
  - Accuracy change between versions
  - Template length changes
- **Rollback**: Instantly revert to the previous active prompt version. This is critical for incident response -- if a new prompt causes a regression, you can roll back in seconds.

### Dataset Versioning

Golden datasets evolve over time:
- **v1.0**: Initial dataset (e.g., 50 questions)
- **v1.1**: Expanded dataset (e.g., 75 questions)
- **v2.0**: Major expansion with rebalanced distribution (e.g., 100 questions)
- **v2.1**: Full coverage (e.g., all available questions)

Each version tracks the number of questions and the answer distribution, so you can see how the dataset composition changed.

### Model Versioning

Each model version records:
- **Release date**
- **Description** of changes
- **Expected accuracy**
- **Prompt version** it uses
- **Status**: deprecated, canary, production

Example version history:
- v1.0: Baseline model (78% accuracy, deprecated)
- v1.1: Minor prompt optimization (80% accuracy, deprecated)
- v2.0: Major model update with new architecture (82% expected, but regression found -- status: canary)
- v2.1: Hotfix for v2.0 regressions (83% accuracy, status: production)

---

## 9. Continuous Benchmarking

### Problem

Individual evaluations give you a snapshot. You need a longitudinal view: is your system getting better or worse over time? Where are the trends headed?

### Why It Exists

Without continuous benchmarking, you might celebrate a 2% accuracy gain without noticing that latency doubled, or you might deploy a "faster" model without realizing accuracy has been declining for three versions.

### Intuition

Think of a stock chart. You do not just look at today's price -- you look at the trend over weeks and months. Continuous benchmarking creates the equivalent chart for your model's accuracy and latency across versions.

### How It Works

Records accuracy and latency per model version, computes trends, and generates ASCII charts.

```
[Model Version N] --> [Run Benchmark Suite]
                            |
                      [Record Results]
                            |
                    [Append to History]
                            |
                  [Trend Analysis & Charts]
                            |
                [Compare Against Baselines]
```

### Key Concepts

- **Benchmark History**: Ordered list of benchmark results across model versions, each recording accuracy, P50 latency, P95 latency, and metadata (date, etc.).
- **Named Baselines**: You can designate any version as a named baseline (e.g., "initial_release" = v1.0) for comparison. This lets you answer: "How does the current model compare to where we started?"
- **Comparison Table**: Shows all versions side-by-side with accuracy, latency, and delta from the best version.
- **ASCII Chart**: Visual representation of metric trends across versions. Each version gets a horizontal bar proportional to its metric value.
- **Trend Analysis**: Uses linear regression to determine if a metric is improving, degrading, or stable. Reports slope, best, worst, and current values.
- **Baseline Comparison**: Compare any version against a named baseline to see accuracy and latency deltas.

### Example: Version History Analysis

A typical benchmark history might show:
- v0.9: 72% accuracy, 300ms P50 latency (pre-release)
- v1.0: 78% accuracy, 250ms P50 latency (initial release -- set as baseline)
- v1.1: 80% accuracy, 240ms P50 latency (improvement)
- v2.0: 65% accuracy, 180ms P50 latency (regression -- faster but less accurate)
- v2.1: 83% accuracy, 200ms P50 latency (hotfix -- best accuracy yet)

The trend analysis shows:
- Accuracy trend: improving (positive slope, best=83%, worst=65%)
- Latency P50 trend: improving (negative slope = lower latency, best=180ms, worst=300ms)

Comparing v2.1 to the baseline (v1.0):
- Accuracy: 78% -> 83% (+5%)
- Latency P50: 250ms -> 200ms (-50ms)

---

## Why Use Langfuse and Tracing in Production?

Langfuse gives you a production-grade dashboard where every model version, every CI/CD gate decision, and every drift detection result is logged as a trace. When a regression happens at 3am, you can filter by model version and time window to see exactly which queries degraded -- without grepping through log files.

Tracing is what turns "accuracy dropped 5%" into "accuracy dropped for physics questions because the new prompt truncates context after 2000 tokens."

---

## Summary

Production evaluation is about maintaining quality AFTER deployment. The nine key systems work together as a comprehensive production evaluation framework:

| System | Purpose | When to Use |
|--------|---------|-------------|
| Regression Testing | Catch accuracy regressions before release | Before every deployment |
| Canary Testing | Gradual rollout with automatic rollback | During deployment |
| Shadow Deployment | Risk-free A/B comparison on live traffic | Before committing to a new model |
| Drift Detection | Detect input/output/concept distribution shifts | Continuously in production |
| Monitoring | Sliding-window metrics for real-time tracking | Always on in production |
| Alerting | Threshold + anomaly alerts with escalation | Always on in production |
| CI/CD Gates | Automated pass/fail deployment decisions | In deployment pipeline |
| Versioning | Track prompts, datasets, and models over time | Every change |
| Continuous Benchmark | Long-term performance trending and charts | After every version release |

---

## Key Takeaways

1. **Never deploy without regression testing.** A 5% overall accuracy improvement can hide a 20% regression on a critical category.
2. **Use canary deployments, not big-bang deployments.** Start at 5% traffic and increase gradually.
3. **Shadow deployments are free from user-facing risk.** Use them when you want to compare models without any chance of degrading user experience.
4. **Drift is inevitable.** The question is not "will my model drift?" but "how fast will I detect it?" Monitor all three types: input, output, and concept drift.
5. **Automate deployment decisions with CI/CD gates.** Humans should design the gates; the pipeline should enforce them.
6. **Version everything.** If you cannot answer "what changed?", you cannot fix regressions.
7. **Continuous benchmarking reveals trends.** A single evaluation is a point; continuous benchmarking draws the line.
8. **Alerting with escalation prevents alert fatigue.** Start with warnings; escalate to critical only after repeated violations.
9. **Tracing turns aggregate metrics into actionable insights.** Knowing accuracy dropped is useful; knowing which queries on which topics degraded is actionable.

---

## Common Mistakes

1. **Only testing overall accuracy.** A model can improve overall while regressing on important subsets. Always check per-category and per-question regressions.
2. **Deploying to 100% traffic immediately.** Even with good offline metrics, always use canary or shadow deployments first.
3. **Setting thresholds too tight.** If your accuracy gate is 85% but your model naturally fluctuates between 79-83%, you will never deploy. Set thresholds based on real performance data.
4. **Setting thresholds too loose.** If your regression gate allows 20% regression, it will never catch anything. A 5% threshold is a good starting point.
5. **Ignoring latency in evaluation.** A model that is 5% more accurate but 3x slower may not be a net improvement for users.
6. **Not versioning prompts.** Prompts are code. Treat them with the same version control discipline.
7. **Using the same dataset for training and evaluation.** Data leakage makes your metrics meaningless. Keep golden datasets separate.
8. **Alerting on every metric fluctuation.** Use anomaly detection with appropriate sigma thresholds (2.0-3.0) to avoid alert fatigue.
9. **Not having a rollback plan.** If your canary fails, you need to be able to roll back instantly. Test your rollback process.
10. **Treating evaluation as a one-time event.** Evaluation is a continuous process, not a pre-launch checkbox.

---

## Best Practices

1. **Golden dataset management**: Maintain a versioned golden dataset with at least 50-100 representative questions. Update it quarterly. Include edge cases and failure modes.
2. **Regression threshold**: Start with 5% max regression rate. Tighten to 2-3% as your system matures.
3. **Canary rollout stages**: Use at least 4 stages: 5% -> 10% -> 25% -> 50% -> 100%. Require minimum 20 requests per stage.
4. **Monitoring window size**: Use 50-100 requests per window for accuracy monitoring. Smaller windows for latency.
5. **Alert rules**: Set both threshold alerts (hard boundaries) and anomaly alerts (statistical deviation). Use escalation to prevent alert fatigue.
6. **CI/CD gates**: Make accuracy and regression gates blocking. Make drift gates warning-only (informational but not deployment-blocking).
7. **Prompt versioning**: Hash every prompt template. Log performance per version. Maintain rollback capability.
8. **Continuous benchmarking**: Run benchmarks after every model or prompt change. Set named baselines for long-term comparison.
9. **Drift detection**: Run drift detection on every monitoring window. Use KL divergence threshold of 0.10 and accuracy drift threshold of 0.08-0.10.
10. **Tracing**: Use a production observability tool (Langfuse, LangSmith, Phoenix) to trace individual requests. This is essential for debugging regressions.

---

## Interview Questions

1. **What is the difference between regression testing and A/B testing for LLMs?**
   Regression testing compares a new model against a golden dataset to find previously-correct answers that became wrong. A/B testing compares two models on live traffic to measure which performs better overall. Regression testing is pre-deployment; A/B testing is during deployment.

2. **How do you decide the canary traffic percentage and rollout stages?**
   Start with a small percentage (5%) for a smoke test, then increase gradually (10%, 25%, 50%, 100%). The minimum requests per stage should be enough for statistically meaningful comparison (at least 20-50 requests). The speed of rollout depends on your traffic volume and risk tolerance.

3. **What are the three types of drift in production LLM systems?**
   Input drift (the distribution of incoming queries changes), output drift (the distribution of model predictions changes), and concept drift (the relationship between inputs and correct answers changes, manifesting as accuracy degradation).

4. **Why would you use shadow deployment instead of canary deployment?**
   Shadow deployment carries zero user-facing risk because the shadow model's responses are never served. Use it when you cannot afford any degradation in user experience, or when you need a longer evaluation period. Use canary when you need to test under real serving conditions (latency, load).

5. **What makes a good CI/CD evaluation gate?**
   It should have a clear metric, an objective threshold based on historical data, and be either blocking (must pass to deploy) or warning-only. Good gates cover accuracy, regression rate, latency, and drift. Gates should be automated, not manual.

6. **How do you handle alert fatigue in production LLM monitoring?**
   Use anomaly-based alerts (z-score) instead of only threshold alerts. Set appropriate sigma thresholds (2.0-3.0). Implement escalation: start with warnings and only escalate to critical after repeated consecutive violations. Reset the counter when the metric recovers.

7. **Why is prompt versioning important?**
   Prompts are a critical part of the LLM system. A small prompt change can cause large accuracy swings. Content-addressable hashing ensures you can always identify which prompt was active when a problem occurred, compare performance across versions, and roll back instantly.

8. **What is the difference between monitoring and continuous benchmarking?**
   Monitoring tracks real-time metrics on production traffic (sliding windows, alerts). Continuous benchmarking runs a fixed benchmark suite on each model version and tracks performance trends over time. Monitoring tells you "how is the system doing right now?" Continuous benchmarking tells you "how has the system evolved over versions?"

9. **How do you set the regression rate threshold?**
   Start with 5% as a baseline. This means no more than 5% of previously correct answers should become wrong. Tighten to 2-3% for critical applications. The threshold should be based on business impact: if regressions in certain categories are more costly, weight those more heavily.

10. **What should you do when drift is detected?**
    First, determine the type of drift. Input drift may require retraining or prompt adaptation. Output drift without input drift suggests model behavior changed (check for infrastructure issues). Concept drift means the ground truth has shifted and you may need to update your golden dataset. Always investigate before taking action -- not all drift requires intervention.

---

## Hands-on Exercises

1. **Build a regression test suite**: Create a golden dataset of 100 questions. Simulate two model versions. Run regression tests and generate a report showing regressions, improvements, and pass/fail decisions.

2. **Implement a canary rollout**: Simulate traffic split between control and canary models. Implement progressive rollout stages. Handle both successful promotion and rollback scenarios.

3. **Build a drift detector**: Create a reference window and simulate progressive drift over 6 windows. Detect input, output, and concept drift. Generate severity reports.

4. **Design CI/CD evaluation gates**: Configure 4 gates (accuracy, regression, latency, drift). Test with metrics from a good model version and a bad model version. Generate pipeline reports.

5. **Implement an alert manager**: Configure threshold and anomaly rules. Simulate a degradation-and-recovery scenario. Verify escalation logic and alert summaries.

---

## Mini Project

Build a complete production evaluation pipeline that integrates all nine systems:

1. Load a golden dataset and create versioned copies
2. Simulate multiple model versions with different accuracy levels
3. Run regression tests to compare versions
4. Simulate a canary rollout for the best new version
5. Run shadow deployment comparison
6. Detect drift across time windows
7. Monitor production traffic with sliding windows
8. Configure alerts and simulate a degradation scenario
9. Set up CI/CD gates and run the deployment pipeline
10. Version prompts and compare versions
11. Run continuous benchmarks and generate trend charts
12. Generate a final summary report

The project should produce a comprehensive report showing all test results, gate decisions, alerts fired, drift detected, and performance trends.

---

## Further Reading

- **Monitoring Machine Learning Models in Production** -- Best practices for monitoring deployed ML systems
- **Continuous Delivery for Machine Learning** -- Applying CI/CD principles to ML pipelines
- **Detecting and Mitigating Data Drift** -- Statistical methods for drift detection in production
- **Canary Deployments for ML** -- Progressive rollout strategies for model deployment
- **LLM Observability with Langfuse** -- Production tracing and observability for LLM applications
- **Evaluation-Driven Development** -- Using evaluation gates to drive LLM development decisions
