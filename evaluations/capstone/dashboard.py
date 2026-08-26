import sys, io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json
from datetime import datetime


def render_dashboard(eval_results, gate_results=None, regression=None):
    """Render an ASCII dashboard from evaluation results."""
    w = 60
    lines = []
    lines.append("=" * w)
    lines.append("  CAPSTONE EVALUATION DASHBOARD".center(w))
    lines.append(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(w))
    lines.append("=" * w)

    # Accuracy section
    acc = eval_results.get("accuracy", {})
    lines.append(f"\n  ACCURACY")
    lines.append(f"  {'Score:':<25} {acc.get('accuracy', 0):.2%}")
    lines.append(f"  {'Correct / Total:':<25} {acc.get('correct', 0)} / {acc.get('total', 0)}")
    bar_len = int(acc.get("accuracy", 0) * 30)
    lines.append(f"  [{'#' * bar_len}{'.' * (30 - bar_len)}]")

    # Retrieval section
    ret = eval_results.get("retrieval", {})
    lines.append(f"\n  RETRIEVAL")
    lines.append(f"  {'Context Precision:':<25} {ret.get('context_precision', 0):.4f}")
    lines.append(f"  {'Context Recall:':<25} {ret.get('context_recall', 0):.4f}")

    # Generation section
    gen = eval_results.get("generation", {})
    lines.append(f"\n  GENERATION")
    lines.append(f"  {'Faithfulness:':<25} {gen.get('faithfulness', 0):.4f}")
    lines.append(f"  {'Relevance:':<25} {gen.get('relevance', 0):.4f}")

    # Latency section
    lat = eval_results.get("latency", {})
    lines.append(f"\n  LATENCY")
    lines.append(f"  {'P50:':<25} {lat.get('p50', 0):.4f}s")
    lines.append(f"  {'P95:':<25} {lat.get('p95', 0):.4f}s")
    lines.append(f"  {'Average:':<25} {lat.get('avg', 0):.4f}s")

    # Judge section
    judge = eval_results.get("judge", {})
    lines.append(f"\n  LLM JUDGE")
    lines.append(f"  {'Avg Score (1-5):':<25} {judge.get('avg_score', 0):.1f}")

    # Quality gates
    if gate_results:
        lines.append(f"\n  QUALITY GATES  [{gate_results.get('verdict', '?')}]")
        for name, g in gate_results.get("gates", {}).items():
            mark = "PASS" if g["status"] == "PASS" else "FAIL"
            lines.append(f"    {name:<20} {g['value']:.4f}  (min {g['threshold']})  [{mark}]")

    # Regression
    if regression:
        lines.append(f"\n  REGRESSION CHECK  [{regression.get('verdict', '?')}]")
        for name, c in regression.get("comparisons", {}).items():
            lines.append(f"    {name:<20} v1={c['v1']:.4f}  v2={c['v2']:.4f}  [{c['status']}]")

    lines.append("\n" + "=" * w)
    return "\n".join(lines)


def save_report(eval_results, path="capstone_report.json"):
    """Save evaluation results to a JSON file."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": eval_results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  Report saved to {path}")
