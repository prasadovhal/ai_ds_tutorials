"""
Chapter 10 - LLM Application Observability
Evaluator module: Tools for tracing, logging, latency analysis,
token counting, cost calculation, prompt tracking, and dashboards.
"""

import time
import math
import random
import uuid
import json
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict


# ---------------------------------------------------------------------------
# 1. TRACE MANAGER - Distributed traces with spans
# ---------------------------------------------------------------------------

class Span:
    """A single unit of work within a trace."""

    def __init__(self, name: str, trace_id: str, span_id: Optional[str] = None,
                 parent_span_id: Optional[str] = None, attributes: Optional[dict] = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id or f"span-{uuid.uuid4().hex[:8]}"
        self.parent_span_id = parent_span_id
        self.attributes = attributes or {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.status = "UNSET"

    def start(self):
        self.start_time = time.time()
        self.status = "IN_PROGRESS"
        return self

    def end(self, status: str = "OK"):
        self.end_time = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        if self.start_time and self.end_time:
            return round((self.end_time - self.start_time) * 1000, 2)
        return 0.0

    def to_dict(self) -> dict:
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
        }


class TraceManager:
    """Manage distributed traces with parent-child span relationships."""

    def __init__(self):
        self.traces: dict[str, list[Span]] = defaultdict(list)

    def create_trace(self, name: str = "trace") -> str:
        """Create a new trace and return its ID."""
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        return trace_id

    def start_span(self, trace_id: str, name: str,
                   parent_span_id: Optional[str] = None,
                   attributes: Optional[dict] = None) -> Span:
        """Create and start a span within a trace."""
        span = Span(name=name, trace_id=trace_id,
                    parent_span_id=parent_span_id, attributes=attributes)
        span.start()
        self.traces[trace_id].append(span)
        return span

    def end_span(self, span: Span, status: str = "OK"):
        """End a span with a status."""
        span.end(status)

    def get_trace(self, trace_id: str) -> list[dict]:
        """Get all spans for a trace as dicts."""
        return [s.to_dict() for s in self.traces.get(trace_id, [])]

    def get_all_traces(self) -> dict[str, list[dict]]:
        """Get all traces."""
        return {tid: [s.to_dict() for s in spans]
                for tid, spans in self.traces.items()}

    def get_slow_traces(self, threshold_ms: float = 3000) -> list[dict]:
        """Find traces whose root span exceeds the threshold."""
        slow = []
        for trace_id, spans in self.traces.items():
            root_spans = [s for s in spans if s.parent_span_id is None]
            for root in root_spans:
                if root.duration_ms > threshold_ms:
                    slow.append({
                        "trace_id": trace_id,
                        "root_span": root.name,
                        "duration_ms": root.duration_ms,
                    })
        return slow

    def print_trace(self, trace_id: str):
        """Print a trace tree."""
        spans = self.traces.get(trace_id, [])
        if not spans:
            print(f"  No spans found for trace {trace_id}")
            return

        # Build tree
        children = defaultdict(list)
        roots = []
        for s in spans:
            if s.parent_span_id is None:
                roots.append(s)
            else:
                children[s.parent_span_id].append(s)

        def _print(span, indent=0):
            prefix = "  " * indent + ("|-- " if indent > 0 else "")
            status_icon = "[OK]" if span.status == "OK" else f"[{span.status}]"
            print(f"  {prefix}{span.name} {status_icon} {span.duration_ms}ms")
            for child in children.get(span.span_id, []):
                _print(child, indent + 1)

        for root in roots:
            _print(root)

    def load_from_sample(self, sample_traces: list[dict]):
        """Load traces from sample_data.json format."""
        for trace_data in sample_traces:
            trace_id = trace_data["trace_id"]
            for span_data in trace_data["spans"]:
                span = Span(
                    name=span_data["name"],
                    trace_id=trace_id,
                    span_id=span_data["span_id"],
                    parent_span_id=span_data["parent_span_id"],
                    attributes=span_data.get("attributes", {}),
                )
                # Estimate duration from start/end times if present
                if "start_time" in span_data and "end_time" in span_data:
                    start = datetime.fromisoformat(span_data["start_time"].replace("Z", "+00:00"))
                    end = datetime.fromisoformat(span_data["end_time"].replace("Z", "+00:00"))
                    span.start_time = start.timestamp()
                    span.end_time = end.timestamp()
                    span.status = "OK"
                self.traces[trace_id].append(span)


# ---------------------------------------------------------------------------
# 2. LLM LOGGER - Structured logging for LLM calls
# ---------------------------------------------------------------------------

class LLMLogger:
    """Structured logging for LLM pipeline events."""

    LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}

    def __init__(self, min_level: str = "INFO"):
        self.min_level = min_level
        self.logs: list[dict] = []

    def _should_log(self, level: str) -> bool:
        return self.LEVELS.get(level, 0) >= self.LEVELS.get(self.min_level, 0)

    def log(self, level: str, component: str, message: str,
            metadata: Optional[dict] = None):
        """Add a structured log entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "component": component,
            "message": message,
            "metadata": metadata or {},
        }
        self.logs.append(entry)
        return entry

    def info(self, component: str, message: str, **kwargs):
        return self.log("INFO", component, message, kwargs if kwargs else None)

    def warning(self, component: str, message: str, **kwargs):
        return self.log("WARNING", component, message, kwargs if kwargs else None)

    def error(self, component: str, message: str, **kwargs):
        return self.log("ERROR", component, message, kwargs if kwargs else None)

    def debug(self, component: str, message: str, **kwargs):
        return self.log("DEBUG", component, message, kwargs if kwargs else None)

    def get_logs(self, level: Optional[str] = None,
                 component: Optional[str] = None) -> list[dict]:
        """Filter logs by level and/or component."""
        result = self.logs
        if level:
            result = [l for l in result if l["level"] == level]
        if component:
            result = [l for l in result if l["component"] == component]
        return result

    def get_errors(self) -> list[dict]:
        return [l for l in self.logs if l["level"] in ("ERROR", "CRITICAL")]

    def get_warnings(self) -> list[dict]:
        return [l for l in self.logs if l["level"] == "WARNING"]

    def print_logs(self, last_n: Optional[int] = None, level: Optional[str] = None):
        """Print formatted logs."""
        logs = self.get_logs(level=level)
        if last_n:
            logs = logs[-last_n:]

        level_markers = {
            "DEBUG": "[ ]", "INFO": "[*]", "WARNING": "[!]",
            "ERROR": "[X]", "CRITICAL": "[!!!]"
        }
        for entry in logs:
            marker = level_markers.get(entry["level"], "[?]")
            ts = entry["timestamp"][:19]
            meta_str = ""
            if entry["metadata"]:
                meta_items = [f"{k}={v}" for k, v in entry["metadata"].items()]
                meta_str = " | " + ", ".join(meta_items)
            print(f"  {marker} {ts} [{entry['component']}] {entry['message']}{meta_str}")

    def load_from_sample(self, sample_logs: list[dict]):
        """Load logs from sample_data.json format."""
        for log_entry in sample_logs:
            self.logs.append({
                "timestamp": log_entry["timestamp"],
                "level": log_entry["level"],
                "component": log_entry["component"],
                "message": log_entry["message"],
                "metadata": log_entry.get("metadata", {}),
            })

    def summary(self) -> dict:
        """Return a summary of log counts by level."""
        counts = defaultdict(int)
        for entry in self.logs:
            counts[entry["level"]] += 1
        return dict(counts)


# ---------------------------------------------------------------------------
# 3. LATENCY TRACKER - P50, P95, P99 percentile calculations
# ---------------------------------------------------------------------------

class LatencyTracker:
    """Track and analyze latency distributions for LLM calls."""

    def __init__(self, threshold_ms: float = 3000.0):
        self.latencies: list[float] = []
        self.threshold_ms = threshold_ms

    def record(self, latency_ms: float):
        """Record a latency measurement."""
        self.latencies.append(latency_ms)

    def record_batch(self, latencies: list[float]):
        """Record multiple latency measurements."""
        self.latencies.extend(latencies)

    def _percentile(self, p: float) -> float:
        """Calculate the p-th percentile."""
        if not self.latencies:
            return 0.0
        sorted_vals = sorted(self.latencies)
        n = len(sorted_vals)
        idx = (p / 100) * (n - 1)
        lower = int(math.floor(idx))
        upper = int(math.ceil(idx))
        if lower == upper:
            return sorted_vals[lower]
        frac = idx - lower
        return sorted_vals[lower] * (1 - frac) + sorted_vals[upper] * frac

    @property
    def p50(self) -> float:
        return round(self._percentile(50), 1)

    @property
    def p95(self) -> float:
        return round(self._percentile(95), 1)

    @property
    def p99(self) -> float:
        return round(self._percentile(99), 1)

    @property
    def mean(self) -> float:
        if not self.latencies:
            return 0.0
        return round(sum(self.latencies) / len(self.latencies), 1)

    @property
    def count(self) -> int:
        return len(self.latencies)

    def get_slow_calls(self) -> list[dict]:
        """Get calls that exceeded the threshold."""
        return [{"index": i, "latency_ms": lat}
                for i, lat in enumerate(self.latencies)
                if lat > self.threshold_ms]

    def get_stats(self) -> dict:
        """Return full latency statistics."""
        if not self.latencies:
            return {"count": 0}
        return {
            "count": self.count,
            "mean_ms": self.mean,
            "min_ms": round(min(self.latencies), 1),
            "max_ms": round(max(self.latencies), 1),
            "p50_ms": self.p50,
            "p95_ms": self.p95,
            "p99_ms": self.p99,
            "slow_calls": len(self.get_slow_calls()),
            "threshold_ms": self.threshold_ms,
        }

    def print_stats(self):
        """Print latency statistics."""
        stats = self.get_stats()
        print(f"  Requests:  {stats['count']}")
        print(f"  Mean:      {stats['mean_ms']}ms")
        print(f"  P50:       {stats['p50_ms']}ms")
        print(f"  P95:       {stats['p95_ms']}ms")
        print(f"  P99:       {stats['p99_ms']}ms")
        print(f"  Min/Max:   {stats['min_ms']}ms / {stats['max_ms']}ms")
        print(f"  Slow (>{stats['threshold_ms']}ms): {stats['slow_calls']}")

    def print_histogram(self, bins: int = 8):
        """Print a text histogram of latency distribution."""
        if not self.latencies:
            print("  No data")
            return
        sorted_vals = sorted(self.latencies)
        lo, hi = sorted_vals[0], sorted_vals[-1]
        bin_width = (hi - lo) / bins if hi > lo else 1
        counts = [0] * bins
        for v in sorted_vals:
            idx = min(int((v - lo) / bin_width), bins - 1)
            counts[idx] += 1
        max_count = max(counts) if counts else 1
        for i, c in enumerate(counts):
            bin_lo = lo + i * bin_width
            bin_hi = bin_lo + bin_width
            bar = "#" * int(30 * c / max_count) if max_count > 0 else ""
            print(f"  {bin_lo:7.0f}-{bin_hi:7.0f}ms | {bar} ({c})")


# ---------------------------------------------------------------------------
# 4. TOKEN COUNTER - Estimate token counts
# ---------------------------------------------------------------------------

class TokenCounter:
    """Track token usage across LLM calls."""

    def __init__(self):
        self.records: list[dict] = []

    def record(self, input_tokens: int, output_tokens: int,
               model: str = "gpt-4", question_id: Optional[int] = None):
        """Record token usage for a single call."""
        self.records.append({
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "model": model,
            "question_id": question_id,
        })

    @staticmethod
    def estimate(text: str) -> int:
        """Estimate token count using ~4 chars/token heuristic."""
        return max(1, len(text) // 4)

    def total_input(self) -> int:
        return sum(r["input_tokens"] for r in self.records)

    def total_output(self) -> int:
        return sum(r["output_tokens"] for r in self.records)

    def total_tokens(self) -> int:
        return self.total_input() + self.total_output()

    def avg_input(self) -> float:
        if not self.records:
            return 0.0
        return round(self.total_input() / len(self.records), 1)

    def avg_output(self) -> float:
        if not self.records:
            return 0.0
        return round(self.total_output() / len(self.records), 1)

    def get_stats(self) -> dict:
        return {
            "calls": len(self.records),
            "total_input_tokens": self.total_input(),
            "total_output_tokens": self.total_output(),
            "total_tokens": self.total_tokens(),
            "avg_input_per_call": self.avg_input(),
            "avg_output_per_call": self.avg_output(),
        }

    def by_model(self) -> dict:
        """Group token usage by model."""
        groups: dict[str, dict] = {}
        for r in self.records:
            m = r["model"]
            if m not in groups:
                groups[m] = {"calls": 0, "input_tokens": 0, "output_tokens": 0}
            groups[m]["calls"] += 1
            groups[m]["input_tokens"] += r["input_tokens"]
            groups[m]["output_tokens"] += r["output_tokens"]
        return groups

    def print_stats(self):
        stats = self.get_stats()
        print(f"  Total calls:         {stats['calls']}")
        print(f"  Total input tokens:  {stats['total_input_tokens']:,}")
        print(f"  Total output tokens: {stats['total_output_tokens']:,}")
        print(f"  Total tokens:        {stats['total_tokens']:,}")
        print(f"  Avg input/call:      {stats['avg_input_per_call']}")
        print(f"  Avg output/call:     {stats['avg_output_per_call']}")


# ---------------------------------------------------------------------------
# 5. COST CALCULATOR - Per-model pricing
# ---------------------------------------------------------------------------

class CostCalculator:
    """Calculate costs based on token usage and model pricing."""

    DEFAULT_PRICING = {
        "gpt-4": {"input_per_1k": 0.03, "output_per_1k": 0.06},
        "gpt-4-turbo": {"input_per_1k": 0.01, "output_per_1k": 0.03},
        "gpt-3.5-turbo": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
        "claude-3-opus": {"input_per_1k": 0.015, "output_per_1k": 0.075},
        "claude-3-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
        "claude-3-haiku": {"input_per_1k": 0.00025, "output_per_1k": 0.00125},
    }

    def __init__(self, pricing: Optional[dict] = None):
        self.pricing = pricing or self.DEFAULT_PRICING
        self.usage_log: list[dict] = []

    def calculate(self, input_tokens: int, output_tokens: int,
                  model: str = "gpt-4") -> dict:
        """Calculate cost for a single call."""
        if model not in self.pricing:
            return {"error": f"Unknown model: {model}", "total_cost": 0.0}

        rates = self.pricing[model]
        input_cost = (input_tokens / 1000) * rates["input_per_1k"]
        output_cost = (output_tokens / 1000) * rates["output_per_1k"]
        total = round(input_cost + output_cost, 6)

        record = {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": total,
        }
        self.usage_log.append(record)
        return record

    def total_cost(self) -> float:
        return round(sum(r["total_cost"] for r in self.usage_log), 6)

    def cost_by_model(self) -> dict:
        """Breakdown of costs by model."""
        breakdown: dict[str, dict] = {}
        for r in self.usage_log:
            m = r["model"]
            if m not in breakdown:
                breakdown[m] = {"calls": 0, "input_cost": 0.0,
                                "output_cost": 0.0, "total_cost": 0.0}
            breakdown[m]["calls"] += 1
            breakdown[m]["input_cost"] += r["input_cost"]
            breakdown[m]["output_cost"] += r["output_cost"]
            breakdown[m]["total_cost"] += r["total_cost"]
        # Round
        for m in breakdown:
            for k in ("input_cost", "output_cost", "total_cost"):
                breakdown[m][k] = round(breakdown[m][k], 6)
        return breakdown

    def compare_models(self, input_tokens: int, output_tokens: int) -> list[dict]:
        """Compare costs across all models for the same usage."""
        results = []
        for model in sorted(self.pricing.keys()):
            rates = self.pricing[model]
            ic = (input_tokens / 1000) * rates["input_per_1k"]
            oc = (output_tokens / 1000) * rates["output_per_1k"]
            results.append({
                "model": model,
                "input_cost": round(ic, 4),
                "output_cost": round(oc, 4),
                "total_cost": round(ic + oc, 4),
            })
        results.sort(key=lambda x: x["total_cost"])
        return results

    def print_summary(self):
        breakdown = self.cost_by_model()
        print(f"  Total cost: ${self.total_cost():.4f}")
        for model, data in breakdown.items():
            print(f"  {model}: {data['calls']} calls, "
                  f"${data['total_cost']:.4f} "
                  f"(in: ${data['input_cost']:.4f}, out: ${data['output_cost']:.4f})")


# ---------------------------------------------------------------------------
# 6. PROMPT TRACKER - Version prompts, track effectiveness
# ---------------------------------------------------------------------------

class PromptTracker:
    """Track prompt versions and their effectiveness metrics."""

    def __init__(self):
        self.versions: dict[str, dict] = {}
        self.results: dict[str, list[dict]] = defaultdict(list)

    def register_version(self, version: str, template: str,
                         description: str = ""):
        """Register a prompt version."""
        self.versions[version] = {
            "template": template,
            "description": description,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

    def record_result(self, version: str, correct: bool,
                      confidence: float, latency_ms: float,
                      tokens: int = 0):
        """Record a result for a prompt version."""
        self.results[version].append({
            "correct": correct,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "tokens": tokens,
        })

    def get_version_stats(self, version: str) -> dict:
        """Get performance stats for a prompt version."""
        records = self.results.get(version, [])
        if not records:
            return {"version": version, "count": 0}
        n = len(records)
        correct = sum(1 for r in records if r["correct"])
        return {
            "version": version,
            "count": n,
            "accuracy": round(correct / n, 4),
            "avg_confidence": round(sum(r["confidence"] for r in records) / n, 4),
            "avg_latency_ms": round(sum(r["latency_ms"] for r in records) / n, 1),
            "avg_tokens": round(sum(r["tokens"] for r in records) / n, 1),
        }

    def compare_versions(self) -> list[dict]:
        """Compare all registered prompt versions."""
        comparisons = []
        for v in sorted(self.versions.keys()):
            stats = self.get_version_stats(v)
            stats["description"] = self.versions[v].get("description", "")
            comparisons.append(stats)
        return comparisons

    def print_comparison(self):
        """Print a comparison table of prompt versions."""
        comps = self.compare_versions()
        print(f"  {'Version':<10} {'Accuracy':>10} {'Confidence':>12} "
              f"{'Latency':>10} {'Tokens':>8}  Description")
        print(f"  {'-'*10} {'-'*10} {'-'*12} {'-'*10} {'-'*8}  {'-'*20}")
        for c in comps:
            if c["count"] == 0:
                continue
            print(f"  {c['version']:<10} {c['accuracy']:>10.1%} "
                  f"{c['avg_confidence']:>12.3f} "
                  f"{c['avg_latency_ms']:>9.0f}ms "
                  f"{c['avg_tokens']:>8.0f}  {c['description']}")

    def load_from_sample(self, prompt_versions: dict):
        """Load prompt version data from sample_data.json."""
        for version, data in prompt_versions.items():
            self.register_version(
                version=version,
                template=data["template"],
                description=data.get("description", ""),
            )


# ---------------------------------------------------------------------------
# 7. RESPONSE MONITOR - Quality signal tracking
# ---------------------------------------------------------------------------

class ResponseMonitor:
    """Monitor response quality signals like accuracy, confidence, format."""

    def __init__(self, confidence_threshold: float = 0.5):
        self.responses: list[dict] = []
        self.confidence_threshold = confidence_threshold

    def record(self, predicted: str, ground_truth: str,
               confidence: float, format_ok: bool = True,
               model: str = "gpt-4", latency_ms: float = 0.0):
        """Record a response for quality monitoring."""
        self.responses.append({
            "predicted": predicted,
            "ground_truth": ground_truth,
            "correct": predicted == ground_truth,
            "confidence": confidence,
            "format_ok": format_ok,
            "model": model,
            "latency_ms": latency_ms,
        })

    @property
    def accuracy(self) -> float:
        if not self.responses:
            return 0.0
        correct = sum(1 for r in self.responses if r["correct"])
        return round(correct / len(self.responses), 4)

    @property
    def format_error_rate(self) -> float:
        if not self.responses:
            return 0.0
        errors = sum(1 for r in self.responses if not r["format_ok"])
        return round(errors / len(self.responses), 4)

    def low_confidence_responses(self) -> list[dict]:
        """Get responses below the confidence threshold."""
        return [r for r in self.responses
                if r["confidence"] < self.confidence_threshold]

    def misclassified(self) -> list[dict]:
        """Get incorrect responses."""
        return [r for r in self.responses if not r["correct"]]

    def high_confidence_errors(self) -> list[dict]:
        """Responses that were wrong but had high confidence -- most concerning."""
        return [r for r in self.responses
                if not r["correct"] and r["confidence"] >= 0.8]

    def get_quality_report(self) -> dict:
        return {
            "total_responses": len(self.responses),
            "accuracy": self.accuracy,
            "avg_confidence": round(
                sum(r["confidence"] for r in self.responses) / len(self.responses), 4
            ) if self.responses else 0.0,
            "format_error_rate": self.format_error_rate,
            "format_errors": sum(1 for r in self.responses if not r["format_ok"]),
            "low_confidence_count": len(self.low_confidence_responses()),
            "high_confidence_errors": len(self.high_confidence_errors()),
            "misclassified_count": len(self.misclassified()),
        }

    def print_report(self):
        report = self.get_quality_report()
        print(f"  Total responses:         {report['total_responses']}")
        print(f"  Accuracy:                {report['accuracy']:.1%}")
        print(f"  Avg confidence:          {report['avg_confidence']:.3f}")
        print(f"  Format errors:           {report['format_errors']} "
              f"({report['format_error_rate']:.1%})")
        print(f"  Low confidence (<{self.confidence_threshold}):   "
              f"{report['low_confidence_count']}")
        print(f"  High-confidence errors:  {report['high_confidence_errors']}")


# ---------------------------------------------------------------------------
# 8. OBSERVABILITY DASHBOARD - Text-based summary dashboard
# ---------------------------------------------------------------------------

class ObservabilityDashboard:
    """Unified text dashboard aggregating all observability signals."""

    def __init__(self, latency_tracker: LatencyTracker,
                 token_counter: TokenCounter,
                 cost_calculator: CostCalculator,
                 response_monitor: ResponseMonitor,
                 llm_logger: LLMLogger,
                 prompt_tracker: Optional[PromptTracker] = None):
        self.latency = latency_tracker
        self.tokens = token_counter
        self.costs = cost_calculator
        self.quality = response_monitor
        self.logger = llm_logger
        self.prompts = prompt_tracker

    def render(self):
        """Render the full text-based dashboard."""
        width = 70
        self._header("LLM OBSERVABILITY DASHBOARD", width)

        # Latency section
        self._section("LATENCY METRICS", width)
        self.latency.print_stats()
        print()
        self.latency.print_histogram(bins=6)

        # Token section
        self._section("TOKEN USAGE", width)
        self.tokens.print_stats()

        # Cost section
        self._section("COST ANALYSIS", width)
        self.costs.print_summary()

        # Quality section
        self._section("RESPONSE QUALITY", width)
        self.quality.print_report()

        # Prompt versions
        if self.prompts and self.prompts.versions:
            self._section("PROMPT VERSION COMPARISON", width)
            self.prompts.print_comparison()

        # Log summary
        self._section("LOG SUMMARY", width)
        summary = self.logger.summary()
        for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            count = summary.get(level, 0)
            if count > 0:
                print(f"  {level:<10}: {count}")

        errors = self.logger.get_errors()
        if errors:
            print(f"\n  Last {min(3, len(errors))} errors:")
            for e in errors[-3:]:
                print(f"    [{e['timestamp'][:19]}] {e['message']}")

        self._footer(width)

    def _header(self, title: str, width: int):
        print()
        print("=" * width)
        print(f"  {title:^{width - 4}}")
        print("=" * width)

    def _section(self, title: str, width: int):
        print()
        print(f"  --- {title} {'-' * max(0, width - len(title) - 7)}")

    def _footer(self, width: int):
        print()
        print("=" * width)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"  Dashboard generated: {ts}")
        print("=" * width)
