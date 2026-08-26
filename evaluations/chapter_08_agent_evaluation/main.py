import sys, io; if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
"""
Chapter 8: Agent Evaluation
Demonstrates every evaluator on real and synthetic agent traces.
"""

import json
from dataset import (
    load_sample_data, get_agent_traces, get_multi_agent_traces,
    get_coding_agent_traces, get_browser_agent_traces, get_tools_catalog,
    generate_synthetic_batch,
)
from evaluator import (
    TaskCompletionEvaluator, GoalAchievementEvaluator, TrajectoryEvaluator,
    ToolUseEvaluator, PlanQualityEvaluator, MemoryEvaluator,
    ReflectionEvaluator, MultiAgentEvaluator, CodingAgentEvaluator,
    BrowserAgentEvaluator, EloRating, full_evaluation,
)


def sep(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def pretty(obj, indent=2):
    print(json.dumps(obj, indent=indent, default=str))


# -------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------
data = load_sample_data()
traces = get_agent_traces(data)
multi_traces = get_multi_agent_traces(data)
code_traces = get_coding_agent_traces(data)
browser_traces = get_browser_agent_traces(data)
tools_catalog = get_tools_catalog(data)

print("Chapter 8: Agent Evaluation")
print(f"Loaded {len(traces)} agent traces, {len(multi_traces)} multi-agent, "
      f"{len(code_traces)} coding, {len(browser_traces)} browser traces")

# ===================================================================
# 1. Task Completion Evaluation
# ===================================================================
sep("1. Task Completion Evaluation")
tc_eval = TaskCompletionEvaluator()
batch_result = tc_eval.evaluate_batch(traces)
print(f"Completion rate: {batch_result['completion_rate']:.2%}")
print(f"Goal achievement rate: {batch_result['goal_rate']:.2%}")
print(f"Answer accuracy: {batch_result['accuracy']:.2%}")
print(f"Average partial score: {batch_result['avg_partial_score']:.3f}")

print("\nPer-trace breakdown:")
for i, (t, r) in enumerate(zip(traces, batch_result["individual"])):
    status = "PASS" if r["answer_correct"] else "FAIL"
    print(f"  {t['trace_id']} ({t['trace_type']:<20s}) | "
          f"answer={r['final_answer']} truth={r['ground_truth']} [{status}] | "
          f"partial={r['partial_score']:.2f}")

# ===================================================================
# 2. Goal Achievement Evaluation
# ===================================================================
sep("2. Goal Achievement Evaluation")
ga_eval = GoalAchievementEvaluator()
for t in traces:
    r = ga_eval.evaluate(t)
    print(f"  {t['trace_id']}: achieved={r['achieved']}, "
          f"sub_goal={r['sub_goal_completion']:.2f}, issues={r['issues_found']}")
    if r["missed_requirements"]:
        for m in r["missed_requirements"]:
            print(f"    - missed: {m}")

# ===================================================================
# 3. Planning Quality Evaluation
# ===================================================================
sep("3. Planning Quality Evaluation")
pq_eval = PlanQualityEvaluator()
for t in traces:
    r = pq_eval.evaluate(t)
    print(f"  {t['trace_id']}: quality={r['overall_plan_quality']:.3f} "
          f"(adherence={r['plan_adherence']:.2f}, specificity={r['plan_specificity']:.2f}, "
          f"feasibility={r['feasibility_score']:.1f})")
    print(f"    plan({r['plan_length']} steps): {r['plan_steps']}")

# ===================================================================
# 4. Trace / Trajectory Evaluation
# ===================================================================
sep("4. Trace / Trajectory Evaluation")
traj_eval = TrajectoryEvaluator(optimal_steps=3)
for t in traces:
    r = traj_eval.evaluate(t)
    loop_flag = " [LOOP]" if r["has_loops"] else ""
    print(f"  {t['trace_id']}: steps={r['total_steps']}, "
          f"efficiency={r['efficiency_score']:.3f}, "
          f"waste={r['waste_ratio']:.2f}, "
          f"cost=${r['cost']:.2f}, "
          f"latency={r['latency_ms']}ms{loop_flag}")

# ===================================================================
# 5. Tool Use Evaluation
# ===================================================================
sep("5. Tool Use Evaluation")
tu_eval = ToolUseEvaluator(tools_catalog)
for t in traces:
    r = tu_eval.evaluate(t)
    print(f"  {t['trace_id']}: calls={r['total_tool_calls']}, "
          f"efficiency={r['tool_efficiency']:.2f}, "
          f"diversity={r['tool_diversity']:.2f}, "
          f"errors={r['errors']}, "
          f"wrong_tool={r['wrong_tool_selections']}, "
          f"arg_quality={r['argument_quality']:.2f}, "
          f"cost=${r['estimated_cost']:.2f}")
    print(f"    tools used: {r['tool_frequency']}")

# ===================================================================
# 6. Memory Evaluation
# ===================================================================
sep("6. Memory Evaluation")
mem_eval = MemoryEvaluator()
for t in traces:
    r = mem_eval.evaluate(t)
    print(f"  {t['trace_id']}: utilization={r['memory_utilization']:.3f}, "
          f"redundant_queries={r['redundant_queries']}, "
          f"efficiency={r['memory_efficiency']:.3f}")

# ===================================================================
# 7. Reflection Evaluation
# ===================================================================
sep("7. Reflection Evaluation")
ref_eval = ReflectionEvaluator()
for t in traces:
    r = ref_eval.evaluate(t)
    print(f"  {t['trace_id']}: quality={r['reflection_quality']:<25s} "
          f"score={r['reflection_score']:.1f}, "
          f"reflection_steps={r['reflection_steps']}, "
          f"verification_steps={r['verification_steps']}, "
          f"errors={r['errors_encountered']}")

# ===================================================================
# 8. Multi-Agent Evaluation
# ===================================================================
sep("8. Multi-Agent Evaluation")
ma_eval = MultiAgentEvaluator()
for mt in multi_traces:
    r = ma_eval.evaluate(mt)
    print(f"  {mt['trace_id']} ({mt['scenario']}):")
    print(f"    agents={r['agent_names']}, coord_score={r['coordination_score']:.2f}")
    print(f"    steps={r['total_steps']}, redundant_tools={r['redundant_tool_calls']}, "
          f"efficiency={r['multi_agent_efficiency']:.3f}")
    print(f"    role_sep={r['role_separation']}, no_redundant={r['no_redundant_work']}, "
          f"handoffs={r['effective_handoffs']}, consensus={r['consensus_reached']}")
    for name, stats in r["per_agent_stats"].items():
        print(f"      {name}: {stats['role'][:50]} | steps={stats['steps']}, tools={stats['tool_calls']}")

# ===================================================================
# 9. Coding Agent Evaluation
# ===================================================================
sep("9. Coding Agent Evaluation")
ca_eval = CodingAgentEvaluator()
for ct in code_traces:
    r = ca_eval.evaluate(ct)
    print(f"  {ct['trace_id']} - Task: {ct['task'][:60]}")
    print(f"    tests: {r['tests_passed']}/{r['tests_passed']+r['tests_failed']} passed "
          f"({r['test_pass_rate']:.0%}), LOC={r['lines_of_code']}, "
          f"complexity={r['code_complexity']}")
    checks = r["quality_checks"]
    flags = [k.replace("has_", "").replace("_", " ") for k, v in checks.items() if v]
    missing = [k.replace("has_", "").replace("_", " ") for k, v in checks.items() if not v]
    print(f"    quality={r['quality_score']:.2f}, overall={r['overall_score']:.3f}")
    print(f"    present: {flags}")
    print(f"    missing: {missing}")

# ===================================================================
# 10. Browser Agent Evaluation
# ===================================================================
sep("10. Browser Agent Evaluation")
ba_eval = BrowserAgentEvaluator()
for bt in browser_traces:
    r = ba_eval.evaluate(bt)
    print(f"  {bt['trace_id']} - Task: {bt['task'][:60]}")
    print(f"    steps={r['total_steps']}, nav={r['navigation_actions']}, "
          f"interact={r['interaction_actions']}")
    print(f"    efficiency={r['efficiency_score']:.3f}, "
          f"errors={r['error_count']}, dead_ends={r['dead_ends']}, "
          f"completed={r['task_completed']}")
    if r["errors"]:
        for e in r["errors"]:
            print(f"      error: {e}")

# ===================================================================
# 11. Elo Rating Tournament
# ===================================================================
sep("11. Elo Rating - Agent Comparison Tournament")
elo = EloRating(k=32, initial_rating=1500)

agent_scores = {
    "AgentV1_Efficient": [],
    "AgentV2_Verbose": [],
    "AgentV3_WrongTool": [],
    "AgentV4_Looping": [],
}

for t in traces:
    correct = 1 if t["final_answer"] == t["ground_truth"] else 0
    agent_scores["AgentV1_Efficient"].append(correct)

import random
random.seed(42)
n_tasks = len(traces)
agent_scores["AgentV2_Verbose"] = [1, 1, 1, 1, 0, 0]
agent_scores["AgentV3_WrongTool"] = [0, 1, 1, 0, 0, 0]
agent_scores["AgentV4_Looping"] = [1, 0, 0, 1, 0, 1]

elo.run_tournament(agent_scores)
leaderboard = elo.get_leaderboard()

print("Leaderboard after round-robin tournament:")
for rank, (name, rating) in enumerate(leaderboard, 1):
    wins = sum(agent_scores[name])
    print(f"  #{rank} {name:<25s} Elo={rating:.1f}  wins={wins}/{n_tasks}")

print(f"\nTotal matches played: {len(elo.match_history)}")

# ===================================================================
# 12. Full Evaluation Pipeline
# ===================================================================
sep("12. Full Evaluation Pipeline")
trace_good = traces[0]
trace_bad = traces[4]

for label, trace in [("GOOD", trace_good), ("BAD", trace_bad)]:
    print(f"\n--- {label}: {trace['trace_id']} ({trace['trace_type']}) ---")
    results = full_evaluation(trace, tools_catalog)
    for evaluator_name, result in results.items():
        print(f"\n  [{evaluator_name}]")
        for k, v in result.items():
            if isinstance(v, dict):
                print(f"    {k}:")
                for kk, vv in v.items():
                    print(f"      {kk}: {vv}")
            elif isinstance(v, list) and len(v) > 3:
                print(f"    {k}: [{len(v)} items]")
            else:
                print(f"    {k}: {v}")

# ===================================================================
# 13. Benchmarks Overview
# ===================================================================
sep("13. Agent Benchmarks Overview")
benchmarks = {
    "AgentBench": ("OS/DB/KG/web/lateral-thinking", ["success_rate", "task_completion", "efficiency"]),
    "SWE-Bench": ("Real GitHub issue patches", ["resolve_rate", "patch_correctness", "test_pass_rate"]),
    "GAIA": ("Multi-step real-world + tools", ["exact_match_accuracy", "tool_use_efficiency"]),
    "WebArena": ("Web browsing on self-hosted sites", ["task_success_rate", "step_efficiency"]),
}
for name, (desc, metrics) in benchmarks.items():
    print(f"  {name}: {desc} | Metrics: {', '.join(metrics)}")

# ===================================================================
# 14. Synthetic Batch Evaluation
# ===================================================================
sep("14. Synthetic Batch Evaluation")
synth = generate_synthetic_batch(10, seed=123)
synth_batch = TaskCompletionEvaluator().evaluate_batch(synth)
print(f"Synthetic batch ({len(synth)} traces):")
print(f"  Completion rate: {synth_batch['completion_rate']:.2%}")
print(f"  Goal rate: {synth_batch['goal_rate']:.2%}")
print(f"  Accuracy: {synth_batch['accuracy']:.2%}")
print(f"  Avg partial score: {synth_batch['avg_partial_score']:.3f}")

# ===================================================================
# Summary
# ===================================================================
sep("Summary")
print("Agent evaluation dimensions: task completion, goal achievement, trajectory,")
print("tool use, planning, memory, reflection, multi-agent, coding, browser, Elo.")
print("Benchmarks: AgentBench, SWE-Bench, GAIA, WebArena.")
