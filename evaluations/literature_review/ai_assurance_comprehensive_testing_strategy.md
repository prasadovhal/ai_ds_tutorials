# AI Assurance: A Comprehensive Testing Strategy for Enterprise AI Systems

**Paper:** arXiv:2605.23459v1 [cs.SE]  
**Authors:** Chitra Badagi, Divye Singh, Animesh Sen, Adinath Shirsath  
**Affiliation:** Thoughtworks Technologies (Pune, Hyderabad, India)  
**Date:** 22 May 2026  
**Pages:** 32 (including appendix with implementation patterns)

---

## Abstract

Enterprise AI systems (LLMs, RAG pipelines, autonomous agents) introduce failure modes that traditional software QA was never designed to detect. These systems are probabilistic, context-sensitive, and emergent — they cannot be verified to be correct, only evaluated with increasing confidence. The paper proposes a comprehensive AI assurance strategy built on three pillars:

1. AI testing should focus on **continuous risk reduction**, not correctness verification
2. Evaluation must be a **core engineering discipline**, not a downstream QA activity
3. AI assurance failures have **fundamentally different organizational impacts** than traditional software defects

The paper introduces an AI-native failure taxonomy, a five-layer AI Assurance Pyramid, and operational guidance on evaluation-driven development, RAG/agent testing, model lifecycle management, and governance.

---

## 1. Understanding Enterprise AI Systems

### The AI Stack Complexity Spectrum

| Level | Key Property | Primary Testing Challenge |
|-------|-------------|--------------------------|
| LLM | Probabilistic generation | No fixed expected output; semantic evaluation required |
| AI Agent | Goal-directed action + tools | Trajectory correctness; false positives via wrong path |
| Agentic AI | Multi-agent coordination + emergence | Coordination failures; context loss; emergent misbehaviour |

Each level adds new properties and demands distinct testing approaches. Strategies sufficient at the LLM level are insufficient at the agentic level.

### The RAG Paradigm

RAG introduces a critical testing constraint: **two independent components must work correctly** and they fail in different ways:
- **Retrieval** must surface the right documents — failure manifests as coherent but factually wrong/incomplete responses
- **Generation** must reason faithfully over retrieved context — failure manifests as hallucination even when retrieval was accurate

Independent evaluation of both pipelines is mandatory. A correct final answer does not confirm correct retrieval.

---

## 2. Why AI Systems Need a New Assurance Model

### The Determinism Problem

Traditional testing relies on: fixed expected outputs, binary pass/fail, coverage as completeness proxy. AI systems break all of these — the same input can produce multiple valid responses and multiple plausible-but-invalid ones.

### Testing as Continuous Risk Reduction

The correct mental model for AI assurance is **risk reduction**, not verification:
- **Reduce uncertainty** — narrow the range of behaviours
- **Bound failure** — establish known limits beyond which the system should not deploy
- **Build confidence over time** — accumulate evidence across distributions

**The equivalent in traditional software is not the test suite, it is the CI/CD pipeline.** Evaluation infrastructure plays the same structural role: continuous verification and maintenance of acceptable system behaviour.

### Business Risk of Getting This Wrong

AI assurance failures are qualitatively different from software bugs:
- **Hallucinated information delivered authoritatively** (e.g., financial assistant fabricating policy terms)
- **Silent behavioural degradation at scale** (thousands of subtly wrong outputs before detection)
- **Adversarial compliance** (model appears to follow safety rules but circumvents under specific conditions)
- **Regulatory and liability exposure** (insufficient evaluation = direct compliance risk)

### Benchmarks Are Not Product Readiness

Model benchmarks (MMLU, HumanEval, leaderboards) measure general capability across broad task distributions. They do not measure how a model will behave on your data, in your domain, under your business constraints. **Domain evaluation determines production readiness.**

### The Four Mindset Shifts

1. **Exact-match validation → Semantic evaluation** — assess meaning, not literal strings
2. **One-time testing → Continuous iteration** — regression-driven, running against maintained datasets
3. **Pass/fail → Observability-driven diagnosis** — instrument all pipeline stages
4. **Component testing → System-level evaluation** — end-to-end across complete user workflows

---

## 3. AI-Native Failure Modes: A Taxonomy

A testing strategy without a failure taxonomy is operationally weak. The paper defines 15 failure modes across 5 categories:

### Category 1: Grounding and Faithfulness Failures

| Failure Mode | Manifestation |
|-------------|---------------|
| Hallucination | Fabricated facts stated with confidence |
| Grounding failure | Response contradicts retrieved context |
| Retrieval failure | Wrong documents surfaced for the query |

Detection requires semantic evaluation against retrieved context, not just structural output checks.

### Category 2: Reasoning and Planning Failures

| Failure Mode | Manifestation |
|-------------|---------------|
| Reasoning failure | Wrong conclusion from correct premises |
| Instruction drift | Constraints abandoned mid-session |
| Trajectory collapse | Locally valid steps lead to invalid outcome |

The final output may look correct while the reasoning that produced it was flawed.

### Category 3: Safety and Security Failures

| Failure Mode | Manifestation |
|-------------|---------------|
| Prompt injection | Malicious input overrides system instructions |
| Unsafe compliance | Policy-violating request fulfilled |
| Reward hacking | Metric satisfied while intent is violated |

Detection requires adversarial test sets with jailbreak and injection attempts.

### Category 4: System and Coordination Failures

| Failure Mode | Manifestation |
|-------------|---------------|
| Context loss | Earlier conversation state forgotten |
| Tool misuse | Wrong tool or wrong parameters invoked |
| Over-delegation | Sub-agents operate beyond intended scope |
| Infinite loops | Agent retries indefinitely without terminating |

These are the dominant failure mode in agentic architectures. Cannot be detected through individual component evaluation.

### Category 5: Stochastic and Emergent Failures

| Failure Mode | Manifestation |
|-------------|---------------|
| Stochastic inconsistency | Unacceptable pass-rate variance across runs |
| Latent emergence | Unexpected capabilities appear after model update |

Detection requires repeated evaluation runs, consistency analysis, and active monitoring for unexpected capability changes across model versions.

### The Unknown Unknowns Problem

AI systems violate the traditional assumption that failure surfaces can be enumerated. Addressing this requires:
- **Adversarial discovery** — systematic red-teaming to find inputs that break the system
- **Exploratory evaluation** — open-ended runs designed to surface novel failure patterns
- **Emergent capability monitoring** — tracking behaviour across versions for unexpected changes

### Taxonomy as Testing Design Input

Each failure category requires a distinct testing mechanism:
- Grounding failures → semantic evaluation against retrieved context
- Coordination failures → trajectory and handoff testing across agent boundaries
- Safety failures → adversarial test sets with jailbreak and injection attempts
- Stochastic failures → repeated evaluation runs and consistency analysis

---

## 4. Evaluation-Driven Development (EDD)

### Evaluation is Not the Same as Testing

| Dimension | Test | Evaluation |
|-----------|------|-----------|
| Output | Pass / Fail | Score (continuous or categorical) |
| Inputs | Single case | Dataset (many cases) |
| Repeatability | Deterministic | Probabilistic; requires multiple runs |
| Tooling | Assertion frameworks | LLM judges, rubrics, human reviewers |
| Cost | Near zero | Non-trivial (LLM calls, human time) |
| Use case | Infrastructure, schemas, contracts | Semantic quality, reasoning, safety |

Merging these concepts causes two failure types:
- Treating evaluations as tests → false confidence (binary pass/fail on probabilistic behaviour)
- Treating tests as evaluations → wasted effort (using LLM judges for schema validation)

### The EDD Loop

```
Build Eval Dataset → Implement (prompt/config) → Run Evaluations
        ↑                                              ↓
   Define Behaviour ← Refine ← Meets threshold? ──→ Ship
        ↑                                              |
        └──── model/prompt change triggers re-evaluation
```

**Behaviour specification happens through the evaluation dataset**, not through requirements documents. Every model or prompt change re-enters the loop; shipping does not exit it.

### Evaluation Infrastructure Components

1. **Evaluation datasets** — curated collections with expected outputs or scoring criteria, versioned alongside the system
2. **Judges and rubrics** — models and criteria for assessing outputs that cannot be verified deterministically; one rubric per dimension
3. **Scoring and aggregation pipelines** — automated systems that run on schedule/trigger and produce trend data
4. **Regression baselines** — reference scores against which new runs are compared

### Building Evaluation Datasets

A well-formed dataset has four components:
1. **Prompt template** — versioned instruction defining model's role and expected behaviour
2. **Golden inputs** — curated set covering: normal requests, edge cases, ambiguous inputs, unsafe requests, adversarial inputs
3. **Expected outputs or scoring criteria** — reference answer or rubric defining correct response
4. **Acceptance thresholds** — target performance level based on domain-specific risk tolerance

### Hybrid Evaluation: Deterministic First, Semantic Where Necessary

- **Deterministic validation** — for structured output (JSON schema, classification labels, field values). Zero token cost, high confidence.
- **Semantic evaluation** — for natural language output. Use LLM judge guided by single-dimension rubrics. One rubric per dimension to avoid inconsistent scoring.
- **Weighted scoring and mandatory gates** — not all dimensions carry equal weight. Mandatory gates enforce non-negotiable dimensions regardless of aggregate score.

### Consistency as an Evaluation Signal

A single evaluation run tells very little about an AI system. **Consistency** = pass rate across repeated runs of same input against same model.

Three verdicts:
- **CONSISTENT_PASS** — system handles input reliably; single-run failures were noise
- **FLAKY** — system passes most of the time but fails occasionally; prompt needs tightening until pass rate ≥ 90%
- **CONSISTENT_FAILURE** — genuine regression; escalate for Layer 1 prompt investigation

---

## 5. The AI Assurance Pyramid

A revised five-layer testing architecture (Layer 0 through Layer 4), organized by three principles:
- Economic cost increases upward
- Diagnostic specificity decreases upward
- Epistemological regime shifts from deterministic (base) to probabilistic (top)

**Key principle: failures should be caught as low in the pyramid as possible.**

```
                    /\
                   /  \
                  / L4 \      Business Outcome Evaluations
                 /------\     (Agent goal completion, compliance,
                / L3     \     hallucination, red-teaming)
               /----------\
              / L2          \   Agent Behavioural Evaluations
             /--------------\   (Trajectory, tool call accuracy,
            / L1              \  reasoning quality, state retention)
           /------------------\
          / L0                  \ Component Evaluations
         /----------------------\ (Prompt eval, retrieval quality,
        / Deterministic Infra    \ tool selection, guardrails)
       /--------------------------\
                                   Deterministic Infrastructure
                                   (APIs, schemas, contracts,
                                    prompt structure, structured outputs)
```

### Layer 0: Deterministic Infrastructure

**What:** APIs, schemas, contracts, prompt structure, structured outputs  
**Scope:** No live LLM calls. Fully offline and deterministic.  
**Three evaluation types:**
- **Tool unit tests** — verify tool logic, schema correctness, error handling
- **Prompt structure validation** — treat prompts as static artifacts; confirm required sections, variables, token bounds, output format
- **API contract tests** — verify external interfaces conform to expected schemas

**KPIs:** Tool reliability rate, schema adherence rate, prompt structure compliance, defect leakage rate

### Layer 1: Component Evaluations

**What:** Prompt evaluations, retrieval quality, tool selection, classifiers, guardrails  
**Scope:** First layer involving live model calls. Each component evaluated in isolation.

**Key evaluation targets:**
- **Prompt evaluation** — each prompt run against its own golden dataset (normal, edge case, adversarial, unsafe inputs)
- **Retrieval quality** — precision (relevance) and recall (coverage) of retrieval pipeline in isolation
- **Tool selection accuracy** — correct tool identification for a given query, independent of agent reasoning
- **Guardrail effectiveness** — safety classifiers tested against adversarial inputs, jailbreak attempts

**KPIs:** Prompt pass rate, prompt regression rate, context precision, context recall, tool routing accuracy, guardrail trigger rate

### Layer 2: Agent Behavioural Evaluations

**What:** Trajectory evaluation, tool call accuracy, reasoning quality, state retention  
**Scope:** Single agent evaluated end-to-end across multi-step tasks. Question shifts from "right output?" to "right path?"

**Key evaluation targets:**
- **Trajectory evaluation** — full sequence of reasoning steps, tool invocations, state transitions compared against reference trajectory or rubric
- **Tool call accuracy** — two independent dimensions: (1) tool selection and (2) parameter construction
- **Reasoning quality** — logical consistency and instruction adherence assessed with rubrics at each decision point
- **State retention** — agent's ability to carry forward context without re-requesting or contradicting

**KPIs:** Trajectory correctness rate, tool call accuracy, unnecessary call rate, instruction adherence rate, single-agent task success rate

### Layer 3: Multi-Agent and Workflow Evaluations

**What:** Agent handoff accuracy, orchestration correctness, coordination, failure recovery  
**Scope:** Where agentic systems become genuinely complex. Each handoff is a potential failure.

**Key evaluation targets:**
- **Agent handoff accuracy** — fidelity of context transfer between agents (distinct from tool call accuracy)
- **Orchestration correctness** — whether orchestrating agent routes to correct sub-agents with appropriate scoping
- **Failure recovery** — whether system recovers gracefully from sub-agent failures
- **Emergent behaviour detection** — scenarios designed to surface coordination failures invisible in individual agent evaluation

**KPIs:** Agent handoff accuracy, state retention across agents, recovery success rate, trajectory efficiency score, multi-agent task success rate

### Layer 4: Business Outcome Evaluations

**What:** Agent goal completion, compliance, hallucination risk, KPI alignment  
**Scope:** Most visible, most expensive, least diagnostic layer.

**Key evaluation targets:**
- **Agent goal completion** — did agent fulfill user's end-to-end objective?
- **Business rule compliance** — adherence to all applicable policies and regulatory requirements
- **Hallucination detection** — end-to-end output assessment (complements component-level faithfulness)
- **Red-teaming** — adversarial scenarios to surface unknown failure modes

**KPIs:** Agent goal completion rate, factual accuracy score, business rule compliance rate, hallucination rate, end-to-end regression pass rate

### The Pyramid as a Diagnostic Tool

The pyramid is also a diagnostic instrument. When a production issue surfaces, check bottom-up:

| Symptom in Production | Check First | Likely Root Cause |
|----------------------|-------------|-------------------|
| Final responses suddenly less accurate | Layer 4 regression suite | Model drift or prompt degradation |
| Agent calling wrong tools intermittently | Layer 2 trajectory tests | Model update changed tool call behaviour |
| Tool receiving wrong parameters | Layer 2 tool call accuracy | Prompt change affected parameter construction |
| Multi-step tasks losing context midway | Layer 3 coordination tests | State handoff between agents is breaking |
| Output format breaking downstream | Layer 0 prompt validation | Prompt output structure drifted from schema |
| Guardrail missing unsafe queries | Layer 1 guardrail evaluation | Model update reduced guardrail sensitivity |
| Correct answer, wrong reasoning path | Layer 2 trajectory tests | False positive: fragile trajectory that will fail later |

---

## 6. Testing RAG and Agentic Systems

### RAG Assessment Metrics

Four metrics that have gained broad industry adoption:

1. **Context Precision** — Is the retrieved content actually useful? Measures relevance of retrieved documents to the query. Low score = retrieval precision issue.

2. **Context Recall** — Did retrieval capture everything needed? Measures whether all required information was surfaced. Low score = chunking strategy, embedding quality, or search threshold issue.

3. **Faithfulness** — Is the response grounded in the retrieved context? Primary quantitative safeguard against hallucination. Low score = generation grounding issue.

4. **Answer Relevancy** — Did the model actually answer the question? Measures how directly the response addresses the query. Low score = prompt instruction clarity issue.

### RAG Diagnostic Profiles

Score combinations map to specific root causes:

| Precision | Recall | Faithfulness | Relevancy | Diagnosis |
|-----------|--------|-------------|-----------|-----------|
| Low | Low | Any | Any | Retrieval pipeline broken: check chunking and embeddings |
| High | Low | Any | Any | Missing documents: recall issue, check index coverage |
| High | High | Low | Any | Hallucination: generation grounding insufficient |
| High | High | High | Low | Prompt issue: response shaping or instruction clarity |
| High | High | High | High | System performing well across all dimensions |

### RAG Quality Gates

- **Faithfulness and context recall are non-negotiable** (hallucination and incompleteness are highest-risk)
- Precision and answer relevancy admit slightly more flexibility
- A system that fails the faithfulness gate should not be deployed regardless of other scores

### Agentic System Testing: Applying the Pyramid

Key agentic-specific challenges:

**Prompt evaluation — multiplicity and cascade risk:**
- Each agent has its own prompt set requiring its own golden dataset and regression baseline
- Cascade failure: prompt regression in upstream agent degrades downstream agents silently
- Every agent prompt requires independent evaluation on every model update and prompt change

**Tool call accuracy — independent failure dimensions:**
- Tool selection and parameter construction fail independently
- Evaluation scenarios must be designed so each dimension can be checked independently

**Trajectory evaluation — reference trajectories vs rubrics:**
- Reference trajectories: precise but brittle (valid alternative paths fail evaluation)
- Rubrics: more flexible but must be designed carefully to avoid passing clearly incorrect paths
- For constrained tasks with known optimal path → reference trajectory
- For tasks with multiple valid approaches → rubric with mandatory steps and prohibited patterns

**Stateful evaluation — making context loss verifiably detectable:**
- Only useful if context loss produces a verifiably wrong output
- A state-retaining agent and a context-dropping agent must produce detectably different outputs on same scenario

**Agent handoff accuracy — constructing explicitly dependent scenarios:**
- Evaluation scenarios must be constructed so downstream agent's output depends explicitly on a specific element the upstream agent transfers
- Include baseline (complete handoff) and variation (element omitted/corrupted)

**Failure injection testing:**
- Deliberately break individual components: API errors, empty retrieval results, malformed tool responses
- Each failure mode and each expected recovery path (retry, fallback, clarification, clean termination) should be a distinct evaluation scenario

**Emergent behaviour testing:**
- Construct inputs that force specific coordination failures
- Ambiguous handoff instructions, state conflicts, tasks requiring correct handling of incomplete upstream output
- Build from real production incidents

**Agent goal completion:**
- Cannot be predicted from sum of lower-layer scores
- Task-level success criteria must be defined at the scenario level
- Requires structured LLM judge with task-level rubric or human evaluation
- Final gate before any agentic system change is approved for deployment

---

## 7. Model Lifecycle, Drift and Regression Management

### Prompts Are Behavioural Specifications

A prompt is not a text string — it is a **behavioural specification**: it defines what the model should do, how it should reason, and what it should produce. Change the model underneath and the specification may be interpreted differently.

In enterprise applications, a single user query passes through multiple independent LLM interactions (safety check, intent classification, query rewriting, RAG generation, response formatting). Each must be re-validated when the model changes. **Model migration must be treated as a first-class release event.**

### The Three Change Scenarios

| Scenario | Risk Level | Evaluation Discipline |
|----------|-----------|----------------------|
| New model, same prompts | Medium | Re-evaluate all prompts |
| Same model, prompt change | Medium | Evaluate changed prompt |
| New model + prompt change | **Highest** | Isolate: validate model first with existing prompts, then introduce prompt changes separately |

**Key insight:** Scenario 3 (simultaneous change) requires variable isolation. Validate the new model against existing prompts first. Once baseline is stable, introduce prompt changes with their own evaluation runs.

### Model Drift: The Silent Degrader

Model drift = changes in model behaviour over time, even when nothing has changed in your system. Providers periodically update hosted models (safety tuning, alignment adjustments, performance improvements) without always issuing changelogs.

The danger is not catastrophic failure — it is **slight wrongness, consistently, across a large volume of interactions**.

*Example: A travel assistant confidently recommends non-stop flights as instructed. After a quiet model update, it begins occasionally ignoring that instruction. No error is thrown. User satisfaction scores start dipping and by the time the pattern is identified, it has been happening for weeks.*

The only reliable defence: **prompt-level regression testing running continuously**, not just at release time. Requires evaluation-based detection — tracking quality scores over time and flagging when trends degrade beyond a threshold.

### Building Prompt Test Datasets for Regression

Three scenario types critical for regression management:
1. **Edge cases** — inputs at boundary of expected behaviour, most sensitive to model-level changes
2. **Unsafe and adversarial inputs** — where model drift is most likely to manifest (safety tuning updates)
3. **Previously failing inputs that were fixed** — prompt engineering fixes may not hold with a different model interpreter

### Continuous Monitoring in Practice

| Trigger | Scope | Action on Degradation |
|---------|-------|-----------------------|
| Scheduled (daily) | Full prompt test suite at Layer 1 | Flag prompts with score trend > 5% decline over 7 days |
| Model version change | All prompts, all layers | Block deployment until Layer 1 baseline is re-established |
| Prompt update | Updated prompt + dependent downstream prompts | Require evaluation run before merge |
| Production incident | Affected prompt + upstream components | Identify pyramid layer of origin; add incident case to dataset |

**Converting incidents into evaluation coverage:** Every production incident is an opportunity to close an evaluation gap. Standard response: identify which pyramid layer should have caught the failure, determine why it didn't, add incident case to the relevant dataset, confirm the updated dataset catches the failure before the fix deploys.

---

## 8. Governance, Human Oversight and Operational Economics

### Human-in-the-Loop Oversight

In high-stakes domains (healthcare, legal, finance), human review is an essential layer of the assurance model. An effective HITL strategy defines **when human judgment is required**:

- **Uncertainty thresholds** — scores below defined confidence boundary are routed to human review
- **Sampling strategies** — statistically representative sample reviewed periodically, regardless of automated scores
- **Escalation workflows** — clear routing from automated failure detection to appropriate human reviewer

Human review is not a replacement for evaluation infrastructure — it is the mechanism through which unknown unknowns are surfaced and converted into evaluation coverage.

### Cost vs. Reliability Tradeoffs

Evaluation infrastructure carries costs (LLM judge calls, human review time, dataset maintenance, compute overhead). Primary levers for managing economics:

- **Deterministic validation before semantic evaluation** — validate structured outputs with assertions before reaching an LLM judge. Eliminates evaluation token cost for majority of outputs.
- **Tiered evaluation frequency** — Layer 0 and Layer 1 run on every change; Layer 3 and Layer 4 run on less frequent cadence unless triggered by incident or migration.
- **Risk-proportionate coverage** — evaluation dataset size and judge invocation frequency proportionate to risk profile. A guardrail prompt warrants more thorough evaluation than a formatting prompt.

### Auditability and Traceability

In regulated industries, AI systems must be demonstrably auditable. For any AI-generated output, the following must be retrievable:
- The model version and configuration that produced it
- The prompt version used, including dynamic variables injected at runtime
- The retrieved context provided (for RAG systems), with source attribution
- The evaluation scores and verdicts from the most recent evaluation run

Requires prompt versioning systems, evaluation lineage tracking, and retrieval provenance infrastructure designed into the system from the outset.

### From QA Teams to Evaluation Engineering

Evaluation engineering in AI systems requires a different skill set from traditional QA:
- Building and curating evaluation datasets
- Designing rubrics
- Maintaining judge pipelines
- Interpreting score trends
- Translating production incidents into evaluation coverage

**Evaluation infrastructure should be a shared platform capability** — centralised, maintained by a dedicated function, consumed by multiple AI product teams. The shift from project-level test suites to platform-level evaluation infrastructure is the organisational equivalent of moving from per-project CI scripts to a shared CI/CD platform.

---

## 9. Conclusion: From Software QA to AI Assurance Engineering

### The Five Core Arguments

1. **AI testing requires a new philosophy.** Testing as risk reduction, not verification. The CI/CD pipeline, not the test suite, is the right analogy.

2. **Failure taxonomy precedes testing strategy.** The 15 failure modes define what the pyramid is built to catch. Adding layers without mapping to failure modes is structural decoration.

3. **Evaluations define behaviour; they do not just verify it.** In AI systems, the evaluation dataset is the primary mechanism through which acceptable behaviour is specified. EDD is the natural consequence of working with systems that cannot be fully programmed.

4. **The pyramid must reflect economics.** Failures caught at Layer 0 are cheap and precisely locatable. Failures caught at Layer 4 are expensive and ambiguous. Push coverage as low as possible.

5. **Evaluation infrastructure is a platform, not a project.** The evaluation stack (datasets, judges, rubrics, scoring pipelines, regression baselines) must become shared platform infrastructure.

### What Changes for Engineering Teams

- Prompts must be **version-controlled and regression-tested** like code
- Every model migration must trigger a **full evaluation run across every prompt**
- Evaluation datasets must be maintained as **living artefacts**, expanded with every production incident
- Quality gates must be **defined before deployment**, not calibrated after the fact

### What Changes for Engineering Leaders

- Investment case is **risk management**, not quality engineering
- Cost of insufficient evaluation = hallucination incidents + model drift detected weeks late + adversarial failures reaching production
- Build evaluation as a **shared platform** that appreciates across AI products, not ad-hoc tooling rebuilt per deployment

### Closing Statement

> "The organisations that deploy AI reliably at scale will not be those with the most capable models. They will be those with the most rigorous evaluation infrastructure teams who have internalised that in probabilistic systems, confidence is not a property of the implementation. It is a property of the evidence accumulated through continuous evaluation."

> "Software QA was built for a world where software does what it is told to do. AI assurance must be built for a world where systems do what they have learned to do and where the assurer's job is to continuously measure, bound and improve the gap between the two."

---

## Appendix A: Implementation Patterns

### A.1 Deterministic Validation

Validate structured output (JSON, classification labels, field values) with assertions before invoking any LLM judge. Zero token cost, high confidence.

```python
def validate_structured_output(actual_raw: str, expected_raw: str) -> bool:
    actual = json.loads(actual_raw)
    expected = json.loads(expected_raw)
    assert actual["type"] == expected["type"]
    assert sorted(actual["items"]) == sorted(expected["items"])
    return True
```

### A.2 LLM-as-Judge with Single-Dimension Rubrics

One rubric per dimension — never combine multiple criteria in one rubric. Dimensions: INTENT_ALIGNMENT, FACTUAL_CORRECTNESS, SAFETY_COMPLIANCE.

### A.3 Weighted Scoring and Mandatory Gates

```python
WEIGHTS = {"INTENT_ALIGNMENT": 0.4, "FACTUAL_CORRECTNESS": 0.4, "SAFETY_COMPLIANCE": 0.2}
MANDATORY = {"SAFETY_COMPLIANCE", "FACTUAL_CORRECTNESS"}

def evaluate_pass(scores: dict) -> dict:
    weighted = sum(scores[d] * WEIGHTS[d] for d in WEIGHTS)
    mandatory_pass = all(scores[d] == 1 for d in MANDATORY)
    return {
        "weighted_score": weighted,
        "mandatory_pass": mandatory_pass,
        "final_pass": mandatory_pass and weighted >= 0.8,
        "failed_gates": [d for d in MANDATORY if scores[d] != 1]
    }
```

### A.4 Consistency Testing

Run same evaluation N times (default 10). Classify as CONSISTENT_PASS (≥ 90% pass rate), FLAKY (50-90%), or CONSISTENT_FAILURE (< 50%).

### A.5 RAG Evaluation with RAGAS

Full RAGAS pipeline with quality gates:

```python
QUALITY_GATES = {
    "faithfulness": 0.90,       # Non-negotiable: hallucination risk
    "context_recall": 0.85,     # Non-negotiable: completeness risk
    "context_precision": 0.80,
    "answer_relevancy": 0.80,
}
deploy_approved = all(result[metric] >= threshold for metric, threshold in QUALITY_GATES.items())
```

---

## Key Takeaways

1. **Testing AI is not harder testing — it is a different kind of testing** requiring a philosophical shift from verification to continuous risk reduction
2. **The 15-failure-mode taxonomy** provides a systematic basis for test coverage rather than ad-hoc testing
3. **The 5-layer AI Assurance Pyramid** (L0: Deterministic → L4: Business Outcome) maps each failure class to its detection layer
4. **Evaluation-Driven Development (EDD)** makes evaluation datasets the primary behaviour specification
5. **Test ≠ Evaluation**: tests are binary/deterministic; evaluations are scored/probabilistic — conflating them causes both to fail
6. **Consistency testing** (N repeated runs) distinguishes reliable behaviour from lucky outputs
7. **RAG diagnostic profiles** map score combinations to specific root causes for targeted fixes
8. **Model drift** is the silent degrader — only continuous prompt-level regression testing detects it
9. **Prompts are behavioural specifications** that must be version-controlled, regression-tested, and re-evaluated on every model change
10. **Evaluation infrastructure is a platform capability**, not a per-project QA activity

---

## References

1. Xia et al. "Evaluation-driven development and operations of LLM agents: A process model and reference architecture." arXiv:2411.13768, 2025.
2. Papineni et al. "BLEU: a method for automatic evaluation of machine translation." ACL 2002.
3. Lin. "ROUGE: A package for automatic evaluation of summaries." Text Summarization Branches Out, 2004.
4. VibrantLabs. RAGAS. https://github.com/vibrantlabsai/ragas, 2024.
5. Ip and Vongthongsri. DeepEval. https://github.com/confident-ai/deepeval, May 2026.
