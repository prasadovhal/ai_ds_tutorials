import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import os, pandas as pd

print("=" * 70)
print("CHAPTER 11: Evaluation Frameworks — Hands-On Deep Dive")
print("=" * 70)

# ── Load data ──
train_df = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\train.csv").head(5)
corpus_df = pd.read_csv(r"D:\Study\Git_repo\evaluations\data\wiki_stem_corpus.csv", nrows=100)
questions = train_df["prompt"].tolist()
correct_letters = train_df["answer"].tolist()
answer_texts = [row[row["answer"]] for _, row in train_df.iterrows()]
passages = corpus_df["text"].tolist()
print(f"\nLoaded {len(questions)} questions, {len(passages)} corpus passages")
for i in range(min(3, len(questions))):
    print(f"  Q{i+1}: {questions[i][:90]}...")

# ── Generate LLM answers via Ollama ──
print("\n" + "-" * 70)
print("Generating LLM answers with Ollama...")
llm_answers = []
try:
    import ollama
    for q in questions:
        resp = ollama.chat(model="llama3.2", messages=[
            {"role": "user", "content": f"Answer in 1-2 sentences:\n{q[:400]}"}
        ])
        llm_answers.append(resp["message"]["content"])
        print(f"  -> {llm_answers[-1][:80]}...")
except Exception as e:
    print(f"  Ollama unavailable ({e}), falling back to answer texts")
    llm_answers = answer_texts[:]
framework_scores = {}

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("1. DeepEval — Multi-Metric LLM Evaluation")
print("=" * 70)
try:
    from deepeval import evaluate as deepeval_evaluate
    from deepeval.metrics import (AnswerRelevancyMetric, FaithfulnessMetric,
                                  HallucinationMetric, GEval)
    from deepeval.test_case import LLMTestCase

    test_cases = []
    for i in range(3):
        tc = LLMTestCase(
            input=questions[i],
            actual_output=llm_answers[i],
            expected_output=answer_texts[i],
            retrieval_context=[passages[i * 2], passages[i * 2 + 1]],
        )
        test_cases.append(tc)
        print(f"  TestCase {i+1}: {questions[i][:70]}...")

    relevancy = AnswerRelevancyMetric(threshold=0.5)
    relevancy.measure(test_cases[0])
    print(f"\n  [TC1] Answer Relevancy : {relevancy.score:.4f}  (reason: {relevancy.reason[:80]}...)")

    faithful = FaithfulnessMetric(threshold=0.5)
    faithful.measure(test_cases[1])
    print(f"  [TC2] Faithfulness     : {faithful.score:.4f}  (reason: {faithful.reason[:80]}...)")

    halluc = HallucinationMetric(threshold=0.5)
    halluc.measure(test_cases[2])
    print(f"  [TC3] Hallucination    : {halluc.score:.4f}  (reason: {halluc.reason[:80]}...)")

    custom_geval = GEval(
        name="Scientific Accuracy",
        criteria="Determine whether the answer is scientifically accurate and uses correct terminology.",
        evaluation_params=[LLMTestCase.input, LLMTestCase.actual_output, LLMTestCase.expected_output],
        threshold=0.5,
    )
    custom_geval.measure(test_cases[0])
    print(f"  [TC1] GEval Sci-Accuracy: {custom_geval.score:.4f}  (reason: {custom_geval.reason[:80]}...)")

    framework_scores["DeepEval"] = {"relevancy": relevancy.score, "faithfulness": faithful.score,
                                     "hallucination": halluc.score, "geval_sci": custom_geval.score}
except Exception as e:
    print(f"\n  DeepEval not installed: {e}")
    print("  pip install deepeval")
    print("  Sample output -> Answer Relevancy: 0.8234, Faithfulness: 0.7100, Hallucination: 0.1500")
    framework_scores["DeepEval"] = "not installed"

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. RAGAS — RAG Assessment Suite")
print("=" * 70)
try:
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import (faithfulness, answer_relevancy,
                               context_precision, context_recall, answer_correctness)
    from datasets import Dataset

    ragas_data = {
        "question": questions[:3],
        "answer": llm_answers[:3],
        "contexts": [[passages[i * 3], passages[i * 3 + 1], passages[i * 3 + 2]] for i in range(3)],
        "ground_truth": answer_texts[:3],
    }
    ds = Dataset.from_dict(ragas_data)
    print(f"  HuggingFace Dataset: {ds}")

    metrics = [faithfulness, answer_relevancy, context_precision, context_recall, answer_correctness]
    results = ragas_evaluate(ds, metrics=metrics)
    print("\n  RAGAS Per-Metric Results:")
    for name, val in results.items():
        if isinstance(val, (int, float)):
            print(f"    {name:25s}: {val:.4f}")

    framework_scores["RAGAS"] = {k: round(v, 4) for k, v in results.items() if isinstance(v, (int, float))}
except Exception as e:
    print(f"\n  RAGAS not installed: {e}")
    print("  pip install ragas datasets")
    print("  Sample output -> faithfulness: 0.7833, answer_relevancy: 0.8012, context_precision: 0.6500")
    framework_scores["RAGAS"] = "not installed"

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. LangChain — Criteria, Distance & QA Evaluators")
print("=" * 70)
try:
    from langchain.evaluation import load_evaluator
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="llama3.2", temperature=0)
    lc_scores = {}

    # Criteria evaluators — correctness, helpfulness, relevance
    for criterion in ["correctness", "helpfulness", "relevance"]:
        evaluator = load_evaluator("labeled_criteria", llm=llm, criteria=criterion)
        result = evaluator.evaluate_strings(
            input=questions[0][:300], prediction=llm_answers[0], reference=answer_texts[0],
        )
        score = result.get("score", "N/A")
        lc_scores[criterion] = score
        print(f"  Criteria '{criterion}': score={score}  reasoning={str(result.get('reasoning',''))[:80]}...")

    # String distance evaluator (no LLM needed)
    dist_eval = load_evaluator("string_distance", distance="levenshtein")
    dist_result = dist_eval.evaluate_strings(prediction=llm_answers[0], reference=answer_texts[0])
    lc_scores["levenshtein"] = round(dist_result["score"], 4)
    print(f"  String Distance (Levenshtein): {dist_result['score']:.4f}")

    # QA evaluator
    qa_eval = load_evaluator("qa", llm=llm)
    qa_result = qa_eval.evaluate_strings(
        input=questions[1][:300], prediction=llm_answers[1], reference=answer_texts[1],
    )
    lc_scores["qa"] = qa_result.get("score", "N/A")
    print(f"  QA Evaluator: score={qa_result.get('score')}  reasoning={str(qa_result.get('reasoning',''))[:80]}...")

    framework_scores["LangChain"] = lc_scores
except Exception as e:
    print(f"\n  LangChain eval not installed: {e}")
    print("  pip install langchain langchain-ollama")
    print("  Sample output -> correctness: 1, helpfulness: 1, levenshtein: 0.7821")
    framework_scores["LangChain"] = "not installed"

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. Promptfoo — Config-Driven Prompt Testing")
print("=" * 70)
try:
    import yaml

    promptfoo_config = {
        "description": "STEM QA evaluation from train.csv",
        "providers": ["ollama:chat:llama3.2"],
        "prompts": [
            "Answer the following science question concisely:\n{{question}}",
            "You are a science expert. Provide a brief, accurate answer:\n{{question}}",
        ],
        "tests": [
            {
                "vars": {"question": questions[i][:300]},
                "assert": [
                    {"type": "llm-rubric", "value": f"Answer should convey: {answer_texts[i][:150]}"},
                    {"type": "contains", "value": correct_letters[i]},
                    {"type": "javascript", "value": "output.length > 20"},
                ],
            }
            for i in range(min(3, len(questions)))
        ],
    }

    config_path = os.path.join(os.path.dirname(__file__), "promptfooconfig.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(promptfoo_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"  Wrote: {config_path}")
    print(f"  {len(promptfoo_config['prompts'])} prompt variants, {len(promptfoo_config['tests'])} test cases (3 assertions each)")
    print(f"\n  Run with: npx promptfoo eval -c \"{config_path}\"")
    print(f"  View UI : npx promptfoo view")
    framework_scores["Promptfoo"] = "config generated"
except Exception as e:
    print(f"\n  Promptfoo config generation failed: {e}")
    print("  pip install pyyaml  &&  npm install -g promptfoo")
    framework_scores["Promptfoo"] = "not installed"

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. LangSmith — Tracing & Evaluation Platform")
print("=" * 70)
try:
    from langsmith import Client
    from langsmith.evaluation import evaluate as ls_evaluate

    print("  LangSmith SDK loaded successfully.")
    print("  Setup: export LANGCHAIN_API_KEY=<your-key>")
    print("         export LANGCHAIN_TRACING_V2=true\n")

    client = Client()

    dataset_name = "stem_qa_eval_ch11"
    examples = [
        {"inputs": {"question": questions[i]}, "outputs": {"answer": answer_texts[i]}}
        for i in range(3)
    ]
    print(f"  Would create dataset '{dataset_name}' with {len(examples)} examples")
    print("  Example input : ", examples[0]["inputs"]["question"][:70], "...")
    print("  Example output: ", examples[0]["outputs"]["answer"][:70], "...")

    def correctness_evaluator(run, example):
        pred = run.outputs.get("answer", "")
        ref = example.outputs.get("answer", "")
        return {"key": "exact_match", "score": int(pred.strip() == ref.strip())}

    print("\n  Evaluator: correctness_evaluator (exact match)")
    print("  To run: ls_evaluate(<target_fn>, data=dataset_name, evaluators=[correctness_evaluator])")
    framework_scores["LangSmith"] = "SDK loaded, needs API key"
except Exception as e:
    print(f"\n  LangSmith not installed: {e}")
    print("  pip install langsmith")
    print("  Sample flow: Client() -> create_dataset -> evaluate(target, data, evaluators)")
    framework_scores["LangSmith"] = "not installed"

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. Phoenix (Arize) — Observability & Tracing")
print("=" * 70)
try:
    import phoenix as px
    from phoenix.otel import register

    session = px.launch_app()
    print(f"  Phoenix session active: {session.url}")

    tracer_provider = register(project_name="stem_qa_eval_ch11")
    print(f"  OTEL tracer registered for project 'stem_qa_eval_ch11'")
    print("  Auto-instrumentation: add phoenix.otel instrument calls for LangChain / LlamaIndex")
    print(f"  Dashboard: open {session.url} in browser to view traces and spans")
    print(f"  Corpus loaded: {len(passages)} passages available for retrieval analysis")

    framework_scores["Phoenix"] = f"dashboard at {session.url}"
except Exception as e:
    print(f"\n  Phoenix not installed: {e}")
    print("  pip install arize-phoenix")
    print("  Sample flow: px.launch_app() -> register(project) -> auto-instrument LLM calls")
    print("  Dashboard URL: http://localhost:6006")
    framework_scores["Phoenix"] = "not installed"

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. Langfuse — Tracing, Scoring & Evaluation")
print("=" * 70)
try:
    from langfuse import Langfuse
    import sys as _sys
    _sys.path.insert(0, r"D:\Study\Git_repo\evaluations")
    from constant import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

    langfuse = Langfuse(
        secret_key=LANGFUSE_SECRET_KEY,
        public_key=LANGFUSE_PUBLIC_KEY,
        host=LANGFUSE_BASE_URL,
    )

    trace = langfuse.trace(name="ch11-framework-comparison")

    for i in range(min(3, len(questions))):
        generation = trace.generation(
            name=f"eval-question-{i}",
            model="ollama/llama3.2",
            input=questions[i][:300],
            output=llm_answers[i][:300],
            metadata={"expected": answer_texts[i][:100]},
        )
        exact_match = 1.0 if correct_letters[i].lower() in llm_answers[i].lower() else 0.0
        generation.score(name="exact_match", value=exact_match)
        generation.score(name="answer_length", value=float(len(llm_answers[i].split())))
        print(f"  Q{i+1}: traced + scored (exact_match={exact_match})")

    if isinstance(framework_scores.get("DeepEval"), dict):
        for metric, val in framework_scores["DeepEval"].items():
            trace.score(name=f"deepeval_{metric}", value=float(val))

    langfuse.flush()
    print("\n  Langfuse traces sent. Dashboard: https://cloud.langfuse.com")
    print("  Features: tracing, scoring, prompt management, datasets, evals")
    framework_scores["Langfuse"] = "traces sent"
except Exception as e:
    print(f"\n  Langfuse not installed: {e}")
    print("  pip install langfuse")
    print("  Sample flow: Langfuse() -> trace() -> generation() -> score()")
    framework_scores["Langfuse"] = "not installed"

# ═══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("COMPARISON TABLE: Evaluation Frameworks at a Glance")
print("=" * 70)

table = [
    ["Framework",   "Approach",              "Key Metrics",                            "Pricing",         "Best For"],
    ["DeepEval",    "Code-first, pytest",    "Relevancy, Faithfulness, GEval",         "Free / OSS",     "CI/CD metric pipelines"],
    ["RAGAS",       "Dataset-level RAG",     "Faithfulness, Precision, Recall",        "Free / OSS",     "RAG pipeline benchmarks"],
    ["LangChain",   "Criteria + distance",   "Correctness, Helpfulness, Edit dist",    "Free / OSS",     "Quick ad-hoc eval in chains"],
    ["Promptfoo",   "Config YAML, CLI",      "LLM-rubric, contains, JS asserts",       "Free / OSS",     "Prompt A/B testing"],
    ["LangSmith",   "Platform + tracing",    "Custom evaluators, tracing",             "Free tier + $",  "Production monitoring"],
    ["Phoenix",     "OTEL observability",    "Traces, spans, embeddings",              "Free / OSS",     "LLM observability & debug"],
    ["Langfuse",    "Cloud + OSS tracing",   "Traces, scores, prompt mgmt",            "Free tier + $",  "Production tracing & eval"],
]

col_widths = [max(len(row[c]) for row in table) + 2 for c in range(5)]
for i, row in enumerate(table):
    line = "  " + "".join(row[c].ljust(col_widths[c]) for c in range(5))
    print(line)
    if i == 0:
        print("  " + "-" * sum(col_widths))

print("\n" + "-" * 70)
print("Framework Status:")
for fw, status in framework_scores.items():
    if isinstance(status, dict):
        metrics_str = ", ".join(f"{k}={v}" for k, v in status.items())
        print(f"  {fw:12s}: {metrics_str}")
    else:
        print(f"  {fw:12s}: {status}")

print("\n" + "=" * 70)
print("Chapter 11 hands-on complete.")
print("=" * 70)
