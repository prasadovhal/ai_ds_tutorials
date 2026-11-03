# Chapter 9: Production Evaluation

Production evaluation maintains quality **AFTER** deployment. While offline evaluation measures performance on test data, production evaluation ensures your LLM system keeps working correctly with real users under real conditions.

Nine key systems:

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

A **regression** is a previously correct behavior that breaks after a change (prompt update, model swap, hyperparameter tuning). Without regression testing, you only discover these failures after users complain.

Compare new model predictions against a golden dataset. If the fraction of previously-correct answers that become wrong (**regression rate**) exceeds a threshold (typically 5%), the test fails.

```
Golden Dataset --> [Run Model] --> Predictions --> [Compare] --> Pass/Fail
```

**Key terms**: Golden dataset (versioned Q&A reference), baseline predictions (current production model), regression rate = `regressions / baseline_correct`, stable correct/wrong (both models agree).

A regression report shows: model/dataset versions, accuracy delta, regression count and rate vs. threshold, and pass/fail decision. Each regression lists the question ID, ground truth, old prediction, and new prediction.

---

## 2. Canary Testing

Deploying to 100% of traffic immediately is risky. Canary testing routes a small percentage to the new model first, like the "canary in a coal mine." If quality holds, traffic increases through stages (5% -> 10% -> 25% -> 50% -> 100%). If quality drops at any stage, all traffic rolls back to the control model.

```
Traffic --> [Load Balancer]
                |
           +---------+---------+
           |                   |
      [Control]           [Canary]
      (1 - pct)%           pct %
           |                   |
           +----> [Compare] <--+
                      |
                 [Promote / Rollback]
```

**Key terms**: Control group (production model), canary group (new model), accuracy threshold (minimum absolute accuracy, e.g. 70%), max regression rate (maximum accuracy gap, e.g. 10%), minimum requests per stage (e.g. 20 to avoid deciding on too little data).

**Outcome**: PROMOTED (all stages passed) or ROLLED_BACK (failed at any stage).

---

## 3. Shadow Deployment

Runs a new model in parallel on live traffic but **never serves its responses** -- zero user-facing risk. Compare outputs offline to decide if the shadow is ready. Think of a new hire shadowing an experienced employee: only the experienced employee's work goes to the client.

```
Request --> [Primary Model] --> Response to user
    |
    +----> [Shadow Model]  --> Logged (not served)
                |
           [Compare] --> Promotion Decision
```

**Key terms**: Agreement rate (fraction where both models match), primary-only correct (would be regressions if shadow deployed), shadow-only correct (improvements the shadow offers).

**Recommendations**: PROMOTE (shadow >2% better), CONSIDER (slightly better, extend test), NEUTRAL (equivalent), CAUTION (slightly worse), REJECT (significantly worse).

---

## 4. Drift Detection

Models are static; the world is not. Over time, user queries change, topic distributions shift, and the relationship between inputs and correct answers evolves. Drift detection catches the gap between what your model expects and what it encounters.

```
[Reference Window] --+
                     |--> [Statistical Test] --> Drift Score --> [Alert if exceeded]
[Current Window]  ---+
```

**Three types of drift:**

| Type | What changes | Detection method | Threshold |
|------|-------------|-----------------|-----------|
| Input drift | Distribution of incoming queries | KL divergence + length shift | KL > 0.10, length shift > 15% |
| Output drift | Distribution of model predictions | KL divergence on predictions | KL > 0.10 |
| Concept drift | Input-output relationship | Accuracy delta between windows | Delta > 8-10% |

**KL Divergence**: `D_KL(P || Q) = sum(P(x) * log(P(x) / Q(x)))`. Zero means identical distributions; higher = more drift. Uses Laplace smoothing for zero probabilities.

**Severity**: None (0 drift types), Low (1), Medium (2), High (all 3).

---

## 5. Production Monitoring

Evaluation runs periodically; monitoring runs continuously via sliding time windows. Like a heart rate monitor for your model's accuracy, latency, and error rates.

```
[Incoming Requests] --> [Log] --> [Window Buffer] --> [Compute Metrics] --> [Dashboard/Alerts]
```

**Metrics tracked:**
- **Accuracy / Error Rate** in each window
- **Latency percentiles**: P50 (median), P95 (SLA target), P99 (worst-case outliers)
- **Prediction distribution** across answer classes
- **Model version distribution** across serving traffic

**Window config**: Window size (e.g. 50 requests), step size (typically half window size) for overlapping sliding windows. Smaller windows = more responsive but noisier.

**Trend analysis**: Linear regression over metric history yields improving / degrading / stable classification.

---

## 6. Alerting

You cannot watch dashboards 24/7. Alerting bridges monitoring (passive) and incident response (active).

```
[Metrics] --> [Alert Rules Engine]
                   |
            +------+------+
            |             |
      [Threshold]   [Anomaly]
            |             |
       [Alert Queue] --> [Escalation] --> [Notification]
```

**Threshold alerts**: Fire when a metric crosses a fixed boundary (e.g. accuracy <= 0.72, P95 latency >= 450ms).

**Anomaly alerts**: Fire when a metric deviates from a healthy baseline using z-score = `|value - mean| / std`. Typical sigma threshold: 2.0.

**Severity levels**: info (no action), warning (investigate soon), critical (immediate action).

**Escalation**: After 3+ consecutive warning fires, auto-escalate to critical. Counter resets when the metric recovers.

---

## 7. CI/CD Integration and Evaluation Gates

CI/CD automates build-test-deploy. Evaluation gates extend this to LLMs by requiring models to pass quality checks before deployment. Like airport security: every model must pass through mandatory checkpoints.

```
[Code Push] --> [Build] --> [Unit Tests] --> [Gate 1: Accuracy] --> [Gate 2: Regression]
                                                --> [Gate 3: Latency] --> [Gate 4: Drift] --> [DEPLOY]
                                           Any blocking failure --> [REJECT]
```

Each gate has: name, metric, operator, threshold, blocking flag (True = must pass, False = warning only).

| Gate | Metric | Condition | Description |
|------|--------|-----------|-------------|
| accuracy_gate | accuracy | >= 0.75 | Min 75% accuracy on golden set |
| regression_gate | regression_rate | <= 0.05 | Max 5% regression rate |
| latency_gate | p95_latency_ms | <= 500 | P95 latency under 500ms |
| drift_gate | kl_divergence | <= 0.10 | Output drift within tolerance |

**Decision**: DEPLOY (all blocking gates passed) or REJECT (any blocking gate failed, report identifies which).

---

## 8. Prompt, Dataset, and Model Versioning

LLM systems have three axes of change: prompt template, evaluation dataset, and model. Any can cause a regression. Versioning lets you track, compare, and roll back each independently -- just like Git for code.

**Prompt versioning**: Each template is hashed (SHA-256) for content-addressable storage. Log performance per version, diff two versions (lines added/removed, accuracy change), and rollback instantly for incident response.

**Dataset versioning**: Golden datasets evolve (v1.0: 50 questions -> v1.1: 75 -> v2.0: 100 rebalanced). Each version tracks question count and answer distribution.

**Model versioning**: Each version records release date, description, expected accuracy, prompt version, and status (deprecated / canary / production).

---

## 9. Continuous Benchmarking

Individual evaluations are snapshots. Continuous benchmarking provides the longitudinal view -- like a stock chart for your model's accuracy and latency across versions.

```
[Model Version N] --> [Run Benchmark] --> [Record] --> [Append to History] --> [Trend & Charts]
```

**Key concepts**: Benchmark history (ordered results per version), named baselines (e.g. "initial_release" = v1.0 for long-term comparison), ASCII charts (visual metric trends), trend analysis (linear regression: improving / degrading / stable).

Example: v1.0 (78% acc, 250ms) -> v1.1 (80%, 240ms) -> v2.0 (65%, 180ms -- regression) -> v2.1 (83%, 200ms -- best). Trend: accuracy improving, latency improving.

---

## Why Use Langfuse and Tracing in Production?

Langfuse provides a production dashboard where every model version, CI/CD gate decision, and drift result is logged as a trace. When a regression happens at 3am, filter by model version and time window to find exactly which queries degraded. Tracing turns "accuracy dropped 5%" into "accuracy dropped for physics questions because the new prompt truncates context after 2000 tokens."

---

## Summary

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

1. Never deploy without regression testing. A 5% overall improvement can hide a 20% regression on a critical category.
2. Use canary deployments (start at 5% traffic), not big-bang deployments.
3. Shadow deployments carry zero user-facing risk -- use them for safe comparison.
4. Drift is inevitable. Monitor all three types: input, output, and concept drift.
5. Automate deployment decisions with CI/CD gates. Humans design gates; pipelines enforce them.
6. Version everything. If you cannot answer "what changed?", you cannot fix regressions.
7. Continuous benchmarking reveals trends a single evaluation cannot show.
8. Alerting with escalation prevents alert fatigue.
9. Tracing turns aggregate metrics into actionable, query-level insights.

---

## Common Mistakes

1. Only testing overall accuracy -- a model can improve overall while regressing on important subsets.
2. Deploying to 100% traffic immediately -- always use canary or shadow deployments first.
3. Thresholds too tight -- if your model fluctuates 79-83%, an 85% gate will never pass. Base thresholds on real data.
4. Thresholds too loose -- a 20% regression gate catches nothing. Start at 5%.
5. Ignoring latency -- 5% more accurate but 3x slower may not be a net improvement.
6. Not versioning prompts -- prompts are code, treat them accordingly.
7. Same dataset for training and evaluation -- data leakage makes metrics meaningless.
8. Alerting on every fluctuation -- use anomaly detection with sigma 2.0-3.0 to avoid fatigue.
9. No rollback plan -- test your rollback process before you need it.
10. Treating evaluation as a one-time event -- it is a continuous process.

---

## Best Practices

1. Maintain a versioned golden dataset (50-100+ questions), updated quarterly, including edge cases.
2. Start with 5% max regression rate; tighten to 2-3% as the system matures.
3. Canary rollout: at least 4 stages (5% -> 10% -> 25% -> 50% -> 100%), minimum 20 requests per stage.
4. Monitoring windows: 50-100 requests for accuracy, smaller for latency.
5. Set both threshold and anomaly alerts; use escalation to prevent fatigue.
6. Make accuracy/regression gates blocking; make drift gates warning-only.
7. Hash every prompt template, log performance per version, maintain rollback capability.
8. Run benchmarks after every model or prompt change; set named baselines.
9. Run drift detection on every monitoring window (KL threshold 0.10, accuracy drift 0.08-0.10).
10. Use a production observability tool (Langfuse, LangSmith, Phoenix) for request-level tracing.

---

## Interview Questions

1. **Difference between regression testing and A/B testing for LLMs?**
   Regression testing compares a new model against a golden dataset pre-deployment to find previously-correct answers that broke. A/B testing compares two models on live traffic during deployment.

2. **How do you decide canary traffic percentage and rollout stages?**
   Start at 5%, increase gradually (10%, 25%, 50%, 100%). Require minimum 20-50 requests per stage for statistical significance. Speed depends on traffic volume and risk tolerance.

3. **What are the three types of production drift?**
   Input drift (query distribution changes), output drift (prediction distribution changes), concept drift (input-output relationship changes, manifesting as accuracy degradation).

4. **Why shadow deployment instead of canary?**
   Shadow carries zero user-facing risk since responses are never served. Use it when you cannot afford any user-experience degradation or need a longer evaluation period.

5. **What makes a good CI/CD evaluation gate?**
   Clear metric, objective threshold based on historical data, blocking or warning-only flag. Good gates cover accuracy, regression rate, latency, and drift.

6. **How do you handle alert fatigue?**
   Use anomaly-based alerts (z-score, sigma 2.0-3.0) alongside thresholds. Implement escalation: warnings first, critical only after 3+ consecutive violations. Reset counter on recovery.

7. **Why is prompt versioning important?**
   A small prompt change can cause large accuracy swings. Content-addressable hashing lets you identify which prompt was active during a problem, compare versions, and roll back instantly.

8. **Monitoring vs. continuous benchmarking?**
   Monitoring tracks real-time metrics on production traffic. Continuous benchmarking runs a fixed suite on each version and tracks trends over time. "How is it doing now?" vs. "How has it evolved?"

9. **How to set regression rate threshold?**
   Start at 5%. Tighten to 2-3% for critical applications. Weight categories by business impact.

10. **What to do when drift is detected?**
    Determine type first. Input drift may need retraining/prompt adaptation. Output drift without input drift suggests infrastructure issues. Concept drift means ground truth shifted -- update the golden dataset. Investigate before acting.

---

## Hands-on Exercises

1. **Regression test suite**: Create a 100-question golden dataset, simulate two model versions, generate a report with regressions, improvements, and pass/fail.
2. **Canary rollout**: Simulate traffic split with progressive stages, handle both promotion and rollback.
3. **Drift detector**: Reference window + 6 simulated windows with progressive drift. Detect all three types, generate severity reports.
4. **CI/CD gates**: Configure 4 gates, test with good and bad model metrics, generate pipeline reports.
5. **Alert manager**: Configure threshold and anomaly rules, simulate degradation-and-recovery, verify escalation.

---

## Mini Project

Build a complete production evaluation pipeline integrating all nine systems: golden dataset with versions, multiple simulated model versions, regression tests, canary rollout, shadow deployment, drift detection across time windows, sliding-window monitoring, alerts with degradation scenario, CI/CD gates, prompt versioning with comparison, continuous benchmarks with trend charts, and a final summary report.

---

## Further Reading

- **Monitoring Machine Learning Models in Production** -- Best practices for deployed ML monitoring
- **Continuous Delivery for Machine Learning** -- CI/CD principles for ML pipelines
- **Detecting and Mitigating Data Drift** -- Statistical drift detection methods
- **Canary Deployments for ML** -- Progressive rollout strategies
- **LLM Observability with Langfuse** -- Production tracing for LLM applications
- **Evaluation-Driven Development** -- Using evaluation gates to drive LLM development
