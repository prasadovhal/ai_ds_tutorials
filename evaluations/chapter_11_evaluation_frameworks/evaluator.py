"""
Chapter 11 - Evaluation Frameworks
Simplified evaluator implementations mimicking each framework's API pattern.
Uses only Python standard library.
"""

import math
import random
import time
from collections import OrderedDict
from typing import Any


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def _word_overlap(text_a: str, text_b: str) -> float:
    """Jaccard word overlap as a simple similarity proxy."""
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def _sentence_count(text: str) -> int:
    return max(1, text.count(".") + text.count("!") + text.count("?"))


def _contains_extra_info(answer: str, context: str) -> float:
    """Fraction of answer words NOT found in context (hallucination proxy)."""
    ans_words = set(answer.lower().split())
    ctx_words = set(context.lower().split())
    if not ans_words:
        return 0.0
    extra = ans_words - ctx_words
    return len(extra) / len(ans_words)


def _context_as_str(context) -> str:
    if isinstance(context, list):
        return " ".join(context)
    return str(context)


# ===================================================================
# 1. DeepEval-Style Evaluator
# ===================================================================

class DeepEvalMetric:
    """Base metric class mimicking DeepEval's metric interface."""
    def __init__(self, name: str, threshold: float = 0.5):
        self.name = name
        self.threshold = threshold
        self.score = 0.0
        self.reason = ""

    def measure(self, test_case: dict) -> float:
        raise NotImplementedError

    @property
    def is_successful(self) -> bool:
        return self.score >= self.threshold


class FaithfulnessMetric(DeepEvalMetric):
    """Measures whether the answer is grounded in the provided context."""
    def __init__(self, threshold: float = 0.7):
        super().__init__("Faithfulness", threshold)

    def measure(self, test_case: dict) -> float:
        ctx = _context_as_str(test_case.get("contexts", test_case.get("context", "")))
        answer = test_case.get("answer", test_case.get("actual_output", ""))
        extra = _contains_extra_info(answer, ctx)
        self.score = round(1.0 - extra, 2)
        self.reason = f"{int(extra*100)}% of answer words not in context"
        return self.score


class AnswerRelevancyMetric(DeepEvalMetric):
    """Measures how relevant the answer is to the question."""
    def __init__(self, threshold: float = 0.7):
        super().__init__("Answer Relevancy", threshold)

    def measure(self, test_case: dict) -> float:
        question = test_case.get("question", test_case.get("input", ""))
        answer = test_case.get("answer", test_case.get("actual_output", ""))
        self.score = round(_word_overlap(question, answer) + 0.45, 2)
        self.score = min(self.score, 1.0)
        self.reason = f"Word overlap + baseline relevancy"
        return self.score


class HallucinationMetric(DeepEvalMetric):
    """Measures hallucinated content not supported by context."""
    def __init__(self, threshold: float = 0.5):
        super().__init__("Hallucination", threshold)

    def measure(self, test_case: dict) -> float:
        ctx = _context_as_str(test_case.get("contexts", test_case.get("context", "")))
        answer = test_case.get("answer", test_case.get("actual_output", ""))
        self.score = round(_contains_extra_info(answer, ctx), 2)
        self.reason = f"Hallucination score (lower is better)"
        return self.score


class DeepEvalStyleEvaluator:
    """Mimics DeepEval's test-case evaluation pattern."""

    def __init__(self):
        self.metrics = [
            FaithfulnessMetric(),
            AnswerRelevancyMetric(),
            HallucinationMetric(),
        ]

    def evaluate(self, test_cases: list[dict]) -> list[dict]:
        results = []
        for tc in test_cases:
            tc_result = {"id": tc.get("id", "unknown"), "metrics": {}}
            for metric in self.metrics:
                score = metric.measure(tc)
                tc_result["metrics"][metric.name] = {
                    "score": score,
                    "passed": metric.is_successful,
                    "reason": metric.reason,
                }
            results.append(tc_result)
        return results


# ===================================================================
# 2. RAGAS-Style Evaluator
# ===================================================================

class RAGASStyleEvaluator:
    """Mimics RAGAS component-metric pattern for RAG evaluation."""

    @staticmethod
    def faithfulness(question: str, answer: str, contexts: list[str]) -> float:
        ctx = " ".join(contexts)
        extra = _contains_extra_info(answer, ctx)
        return round(1.0 - extra, 2)

    @staticmethod
    def answer_relevancy(question: str, answer: str, contexts: list[str]) -> float:
        return round(min(_word_overlap(question, answer) + 0.45, 1.0), 2)

    @staticmethod
    def context_precision(question: str, contexts: list[str]) -> float:
        if not contexts:
            return 0.0
        scores = []
        for ctx in contexts:
            scores.append(_word_overlap(question, ctx))
        return round(sum(scores) / len(scores) + 0.35, 2)

    @staticmethod
    def context_recall(answer: str, reference: str, contexts: list[str]) -> float:
        ctx = " ".join(contexts)
        ref_overlap = _word_overlap(reference, ctx)
        return round(min(ref_overlap + 0.30, 1.0), 2)

    def evaluate(self, dataset: list[dict]) -> list[dict]:
        results = []
        for item in dataset:
            q = item["question"]
            a = item["answer"]
            ctxs = item["contexts"] if isinstance(item["contexts"], list) else [item["contexts"]]
            ref = item.get("reference", a)
            results.append({
                "id": item.get("id", "unknown"),
                "faithfulness": self.faithfulness(q, a, ctxs),
                "answer_relevancy": self.answer_relevancy(q, a, ctxs),
                "context_precision": self.context_precision(q, ctxs),
                "context_recall": self.context_recall(a, ref, ctxs),
            })
        return results


# ===================================================================
# 3. LangSmith-Style Evaluator
# ===================================================================

class LangSmithRun:
    """Represents a single LLM run with inputs/outputs."""
    def __init__(self, run_id: str, inputs: dict, outputs: dict):
        self.run_id = run_id
        self.inputs = inputs
        self.outputs = outputs
        self.start_time = time.time()
        self.end_time = self.start_time + random.uniform(0.1, 0.5)

    @property
    def latency_ms(self) -> float:
        return round((self.end_time - self.start_time) * 1000, 1)


class LangSmithStyleEvaluator:
    """Mimics LangSmith's run-based evaluation with datasets and custom evaluators."""

    def __init__(self, dataset_name: str = "default"):
        self.dataset_name = dataset_name
        self.runs: list[LangSmithRun] = []
        self.evaluators: list[dict] = []

    def create_run(self, inputs: dict, outputs: dict) -> LangSmithRun:
        run = LangSmithRun(f"run_{len(self.runs)+1:03d}", inputs, outputs)
        self.runs.append(run)
        return run

    def add_evaluator(self, name: str, func):
        self.evaluators.append({"name": name, "func": func})

    def evaluate_runs(self) -> list[dict]:
        results = []
        for run in self.runs:
            run_result = {
                "run_id": run.run_id,
                "latency_ms": run.latency_ms,
                "evaluations": {},
            }
            for ev in self.evaluators:
                score = ev["func"](run)
                run_result["evaluations"][ev["name"]] = round(score, 2)
            results.append(run_result)
        return results


# ===================================================================
# 4. Promptfoo-Style Evaluator
# ===================================================================

class PromptfooAssertion:
    """Single test assertion mimicking Promptfoo's YAML-driven testing."""
    def __init__(self, assert_type: str, value: Any = None, threshold: float = None):
        self.assert_type = assert_type
        self.value = value
        self.threshold = threshold

    def check(self, output: str, context: str = "") -> dict:
        passed = False
        reason = ""

        if self.assert_type == "contains":
            passed = self.value.lower() in output.lower()
            reason = f"Output {'contains' if passed else 'missing'} '{self.value}'"

        elif self.assert_type == "not-contains":
            passed = self.value.lower() not in output.lower()
            reason = f"Output {'does not contain' if passed else 'contains'} '{self.value}'"

        elif self.assert_type == "is-json":
            try:
                import json
                json.loads(output)
                passed = True
                reason = "Output is valid JSON"
            except (json.JSONDecodeError, TypeError):
                passed = False
                reason = "Output is not valid JSON"

        elif self.assert_type == "similar":
            score = _word_overlap(output, self.value)
            threshold = self.threshold or 0.5
            passed = score >= threshold
            reason = f"Similarity {score:.2f} vs threshold {threshold}"

        elif self.assert_type == "max-length":
            passed = len(output) <= (self.value or 500)
            reason = f"Length {len(output)} vs max {self.value}"

        elif self.assert_type == "min-score":
            score = _word_overlap(output, context) if context else 0.5
            passed = score >= (self.threshold or 0.5)
            reason = f"Score {score:.2f} vs minimum {self.threshold}"

        elif self.assert_type == "llm-rubric":
            score = _word_overlap(output, context) + 0.3 if context else 0.6
            passed = score >= 0.5
            reason = f"LLM rubric score: {min(score, 1.0):.2f}"

        return {"type": self.assert_type, "passed": passed, "reason": reason}


class PromptfooStyleEvaluator:
    """Config-driven test assertion engine mimicking Promptfoo."""

    def __init__(self):
        self.test_cases = []

    def add_test(self, prompt: str, expected_output: str,
                 assertions: list[dict], context: str = ""):
        self.test_cases.append({
            "prompt": prompt,
            "expected": expected_output,
            "assertions": assertions,
            "context": context,
        })

    def run_tests(self, model_outputs: list[str]) -> list[dict]:
        results = []
        for i, (tc, output) in enumerate(zip(self.test_cases, model_outputs)):
            tc_result = {
                "test_index": i,
                "prompt": tc["prompt"][:60],
                "assertions": [],
                "all_passed": True,
            }
            for a_conf in tc["assertions"]:
                assertion = PromptfooAssertion(
                    a_conf["type"],
                    a_conf.get("value"),
                    a_conf.get("threshold"),
                )
                check = assertion.check(output, tc.get("context", ""))
                tc_result["assertions"].append(check)
                if not check["passed"]:
                    tc_result["all_passed"] = False
            results.append(tc_result)
        return results


# ===================================================================
# 5. TruLens-Style Evaluator
# ===================================================================

class TruLensFeedbackFunction:
    """A feedback function mimicking TruLens' pattern."""
    def __init__(self, name: str, func, higher_is_better: bool = True):
        self.name = name
        self.func = func
        self.higher_is_better = higher_is_better

    def __call__(self, *args, **kwargs) -> float:
        return round(self.func(*args, **kwargs), 2)


class TruLensStyleEvaluator:
    """Mimics TruLens' feedback function + app wrapping pattern."""

    def __init__(self, app_name: str = "RAG App"):
        self.app_name = app_name
        self.feedback_functions: list[TruLensFeedbackFunction] = []
        self.records: list[dict] = []

    def add_feedback(self, name: str, func, higher_is_better: bool = True):
        self.feedback_functions.append(
            TruLensFeedbackFunction(name, func, higher_is_better)
        )

    def record(self, input_text: str, output_text: str,
               contexts: list[str] = None) -> dict:
        rec = {
            "record_id": f"rec_{len(self.records)+1:03d}",
            "app": self.app_name,
            "input": input_text,
            "output": output_text,
            "contexts": contexts or [],
            "feedback": {},
            "timestamp": time.time(),
        }
        ctx_str = " ".join(rec["contexts"])
        for ff in self.feedback_functions:
            rec["feedback"][ff.name] = ff(output_text, ctx_str)
        self.records.append(rec)
        return rec

    def get_leaderboard(self) -> dict:
        if not self.records:
            return {}
        agg = {}
        for ff in self.feedback_functions:
            scores = [r["feedback"][ff.name] for r in self.records]
            agg[ff.name] = {
                "mean": round(sum(scores) / len(scores), 3),
                "min": min(scores),
                "max": max(scores),
            }
        return {"app": self.app_name, "num_records": len(self.records), "metrics": agg}


# ===================================================================
# 6. Inspect AI-Style Evaluator
# ===================================================================

class InspectTask:
    """Mimics Inspect AI's Task definition (dataset + solver + scorer)."""
    def __init__(self, name: str, dataset: list[dict]):
        self.name = name
        self.dataset = dataset
        self.solver = None
        self.scorers = []

    def set_solver(self, solver_func):
        self.solver = solver_func

    def add_scorer(self, name: str, scorer_func):
        self.scorers.append({"name": name, "func": scorer_func})


class InspectStyleEvaluator:
    """Mimics Inspect AI's task/solver/scorer evaluation pattern."""

    def __init__(self):
        self.tasks: list[InspectTask] = []

    def add_task(self, task: InspectTask):
        self.tasks.append(task)

    def run(self) -> list[dict]:
        all_results = []
        for task in self.tasks:
            task_result = {"task": task.name, "samples": []}
            for item in task.dataset:
                output = task.solver(item) if task.solver else item.get("answer", "")
                scores = {}
                for scorer in task.scorers:
                    scores[scorer["name"]] = scorer["func"](item, output)
                task_result["samples"].append({
                    "id": item.get("id", "unknown"),
                    "output": output[:80] if isinstance(output, str) else str(output)[:80],
                    "scores": scores,
                })
            # Aggregate
            if task_result["samples"]:
                agg = {}
                for s_name in task_result["samples"][0]["scores"]:
                    vals = [s["scores"][s_name] for s in task_result["samples"]]
                    agg[s_name] = round(sum(vals) / len(vals), 3)
                task_result["aggregate"] = agg
            all_results.append(task_result)
        return all_results


# ===================================================================
# 7. Phoenix-Style Evaluator (Arize Phoenix)
# ===================================================================

class PhoenixSpan:
    """Represents a traced span in Phoenix."""
    def __init__(self, name: str, span_type: str = "LLM"):
        self.name = name
        self.span_type = span_type
        self.start_time = time.time()
        self.end_time = None
        self.attributes = {}
        self.evaluations = {}

    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def add_evaluation(self, name: str, score: float, label: str = ""):
        self.evaluations[name] = {"score": round(score, 2), "label": label}

    def end(self):
        self.end_time = time.time()


class PhoenixStyleEvaluator:
    """Mimics Phoenix's tracing + inline evaluation pattern."""

    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.spans: list[PhoenixSpan] = []

    def start_span(self, name: str, span_type: str = "LLM") -> PhoenixSpan:
        span = PhoenixSpan(name, span_type)
        self.spans.append(span)
        return span

    def evaluate_rag(self, dataset: list[dict]) -> list[dict]:
        results = []
        for item in dataset:
            span = self.start_span(f"rag_eval_{item.get('id', 'x')}", "EVALUATOR")
            span.set_attribute("input.value", item.get("question", ""))
            span.set_attribute("output.value", item.get("answer", ""))

            ctx = " ".join(item.get("contexts", []))
            faith = 1.0 - _contains_extra_info(item.get("answer", ""), ctx)
            rel = min(_word_overlap(item.get("question", ""), item.get("answer", "")) + 0.45, 1.0)

            span.add_evaluation("faithfulness", faith, "PASS" if faith > 0.7 else "FAIL")
            span.add_evaluation("relevance", rel, "PASS" if rel > 0.7 else "FAIL")
            span.end()

            results.append({
                "id": item.get("id"),
                "span": span.name,
                "evaluations": span.evaluations,
            })
        return results

    def get_trace_summary(self) -> dict:
        return {
            "project": self.project_name,
            "total_spans": len(self.spans),
            "span_types": dict(
                sorted(
                    {s.span_type: sum(1 for x in self.spans if x.span_type == s.span_type)
                     for s in self.spans}.items()
                )
            ),
        }


# ===================================================================
# 8. Evidently AI-Style Evaluator
# ===================================================================

class EvidentlyStyleEvaluator:
    """Mimics Evidently's data drift + LLM monitoring report pattern."""

    def __init__(self):
        self.reference_data: list[dict] = []
        self.current_data: list[dict] = []

    def set_reference(self, data: list[dict]):
        self.reference_data = data

    def set_current(self, data: list[dict]):
        self.current_data = data

    @staticmethod
    def _compute_stats(values: list[float]) -> dict:
        if not values:
            return {"mean": 0, "std": 0, "min": 0, "max": 0}
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return {
            "mean": round(mean, 3),
            "std": round(math.sqrt(variance), 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
        }

    def text_length_drift(self) -> dict:
        ref_lengths = [len(d.get("answer", "")) for d in self.reference_data]
        cur_lengths = [len(d.get("answer", "")) for d in self.current_data]
        ref_stats = self._compute_stats(ref_lengths)
        cur_stats = self._compute_stats(cur_lengths)
        drift_score = abs(ref_stats["mean"] - cur_stats["mean"]) / max(ref_stats["mean"], 1)
        return {
            "metric": "text_length",
            "reference": ref_stats,
            "current": cur_stats,
            "drift_score": round(drift_score, 3),
            "is_drifted": drift_score > 0.2,
        }

    def quality_drift(self) -> dict:
        ref_scores = [_word_overlap(d.get("question", ""), d.get("answer", ""))
                      for d in self.reference_data]
        cur_scores = [_word_overlap(d.get("question", ""), d.get("answer", ""))
                      for d in self.current_data]
        ref_stats = self._compute_stats(ref_scores)
        cur_stats = self._compute_stats(cur_scores)
        drift_score = abs(ref_stats["mean"] - cur_stats["mean"]) / max(ref_stats["mean"], 0.01)
        return {
            "metric": "answer_quality",
            "reference": ref_stats,
            "current": cur_stats,
            "drift_score": round(drift_score, 3),
            "is_drifted": drift_score > 0.2,
        }

    def generate_report(self) -> dict:
        return {
            "report_type": "LLM Monitoring",
            "reference_size": len(self.reference_data),
            "current_size": len(self.current_data),
            "text_length_drift": self.text_length_drift(),
            "quality_drift": self.quality_drift(),
        }


# ===================================================================
# 9. OpenAI Evals-Style (bonus, for main.py completeness)
# ===================================================================

class OpenAIEvalsStyleEvaluator:
    """Mimics OpenAI Evals' registry + eval spec pattern."""

    def __init__(self):
        self.registry = {}

    def register_eval(self, name: str, eval_func, match_type: str = "exact"):
        self.registry[name] = {"func": eval_func, "match_type": match_type}

    def run_eval(self, eval_name: str, samples: list[dict]) -> dict:
        ev = self.registry.get(eval_name)
        if not ev:
            return {"error": f"Eval '{eval_name}' not found"}
        correct = 0
        details = []
        for s in samples:
            result = ev["func"](s)
            if result:
                correct += 1
            details.append({"id": s.get("id", "?"), "passed": result})
        return {
            "eval": eval_name,
            "accuracy": round(correct / max(len(samples), 1), 3),
            "total": len(samples),
            "passed": correct,
            "details": details,
        }


# ===================================================================
# 10. Maxim AI-Style (bonus, for main.py completeness)
# ===================================================================

class MaximAIStyleEvaluator:
    """Mimics Maxim AI's quality scoring and monitoring pattern."""

    def __init__(self, pipeline_name: str = "default"):
        self.pipeline_name = pipeline_name
        self.quality_checks = []

    def add_quality_check(self, name: str, func):
        self.quality_checks.append({"name": name, "func": func})

    def evaluate(self, entries: list[dict]) -> dict:
        results = []
        for entry in entries:
            entry_result = {"id": entry.get("id", "?"), "checks": {}}
            for qc in self.quality_checks:
                entry_result["checks"][qc["name"]] = round(qc["func"](entry), 2)
            results.append(entry_result)

        # Aggregate
        agg = {}
        if results:
            for name in results[0]["checks"]:
                vals = [r["checks"][name] for r in results]
                agg[name] = round(sum(vals) / len(vals), 3)

        return {
            "pipeline": self.pipeline_name,
            "entries_evaluated": len(entries),
            "results": results,
            "aggregate": agg,
        }
