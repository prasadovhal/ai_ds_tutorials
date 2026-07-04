"""
Chapter 8: Agent Evaluation - Evaluator Module
Implements all agent evaluation metrics: task completion, goal achievement,
trajectory quality, tool use, planning, memory, reflection, multi-agent
coordination, coding quality, and Elo rating.
"""

import math
import random
from collections import Counter


# ===================================================================
# 1. TaskCompletionEvaluator
# ===================================================================

class TaskCompletionEvaluator:
    """Evaluates whether an agent finished its assigned task (binary + partial)."""

    def evaluate(self, trace):
        completed = trace.get("task_completed", False)
        goal = trace.get("goal_achieved", False)

        # Partial score: 1.0 if both, 0.5 if completed but goal missed, 0.0 otherwise
        if completed and goal:
            partial_score = 1.0
        elif completed and not goal:
            partial_score = 0.5
        elif not completed and goal:
            partial_score = 0.75  # rare: goal met but task not fully done
        else:
            partial_score = 0.0

        return {
            "binary_completion": completed,
            "goal_achieved": goal,
            "partial_score": partial_score,
            "final_answer": trace.get("final_answer"),
            "ground_truth": trace.get("ground_truth"),
            "answer_correct": trace.get("final_answer") == trace.get("ground_truth"),
        }

    def evaluate_batch(self, traces):
        results = [self.evaluate(t) for t in traces]
        n = len(results)
        return {
            "individual": results,
            "completion_rate": sum(r["binary_completion"] for r in results) / n,
            "goal_rate": sum(r["goal_achieved"] for r in results) / n,
            "accuracy": sum(r["answer_correct"] for r in results) / n,
            "avg_partial_score": sum(r["partial_score"] for r in results) / n,
        }


# ===================================================================
# 2. GoalAchievementEvaluator
# ===================================================================

class GoalAchievementEvaluator:
    """Measures whether the agent reached its stated goal and how well."""

    def evaluate(self, trace):
        goal = trace.get("goal", "")
        achieved = trace.get("goal_achieved", False)
        answer_correct = trace.get("final_answer") == trace.get("ground_truth")

        # Breakdown: goal has sub-tasks? Check issues field
        issues = trace.get("issues", [])
        missed_sub = [i for i in issues if "partial" in i.lower() or "missed" in i.lower()]

        sub_goal_completion = 1.0 if not missed_sub else max(0.0, 1.0 - len(missed_sub) * 0.25)

        return {
            "goal": goal,
            "achieved": achieved,
            "answer_correct": answer_correct,
            "sub_goal_completion": round(sub_goal_completion, 2),
            "issues_found": len(issues),
            "missed_requirements": missed_sub,
        }


# ===================================================================
# 3. TrajectoryEvaluator
# ===================================================================

class TrajectoryEvaluator:
    """Evaluates the efficiency and quality of the agent's step-by-step path."""

    def __init__(self, optimal_steps=2, max_acceptable_steps=6):
        self.optimal_steps = optimal_steps
        self.max_acceptable_steps = max_acceptable_steps

    def evaluate(self, trace):
        steps = trace.get("steps", [])
        total = trace.get("total_steps", len(steps))
        unnecessary = trace.get("unnecessary_steps", 0)
        corrections = trace.get("self_corrections", 0)
        latency = trace.get("total_latency_ms", 0)
        cost = trace.get("total_cost", 0.0)

        # Efficiency = optimal / actual (capped at 1.0)
        efficiency = min(1.0, self.optimal_steps / total) if total > 0 else 0.0

        # Waste ratio
        waste_ratio = unnecessary / total if total > 0 else 0.0

        # Reasoning quality distribution
        qualities = [s.get("reasoning_quality", "unknown") for s in steps]
        quality_dist = dict(Counter(qualities))

        # Check for loops (repeated identical tool calls)
        tool_calls = [
            str(s.get("tool_call")) for s in steps if s.get("tool_call")
        ]
        unique_calls = set(tool_calls)
        has_loops = len(tool_calls) - len(unique_calls) > 0
        repeated_calls = len(tool_calls) - len(unique_calls)

        return {
            "total_steps": total,
            "optimal_steps": self.optimal_steps,
            "efficiency_score": round(efficiency, 3),
            "unnecessary_steps": unnecessary,
            "waste_ratio": round(waste_ratio, 3),
            "self_corrections": corrections,
            "has_loops": has_loops,
            "repeated_calls": repeated_calls,
            "latency_ms": latency,
            "cost": cost,
            "reasoning_quality_distribution": quality_dist,
        }


# ===================================================================
# 4. ToolUseEvaluator
# ===================================================================

class ToolUseEvaluator:
    """Evaluates tool selection accuracy, argument quality, and efficiency."""

    def __init__(self, tools_catalog=None):
        self.tools_catalog = tools_catalog or {}

    def evaluate(self, trace):
        steps = trace.get("steps", [])
        tool_steps = [s for s in steps if s.get("tool_call") is not None]

        total_calls = len(tool_steps)
        tools_used = [s["tool_call"]["tool"] for s in tool_steps]
        unique_tools = set(tools_used)
        tool_freq = dict(Counter(tools_used))

        # Check for wrong-tool usage (heuristic: observation contains "Error")
        errors = 0
        wrong_tool = 0
        for s in tool_steps:
            obs = s.get("observation", "") or ""
            quality = s.get("reasoning_quality", "")
            if "Error" in obs:
                errors += 1
            if "wrong_tool" in quality:
                wrong_tool += 1

        # Argument quality: check if arguments dict is non-empty
        good_args = sum(
            1 for s in tool_steps
            if s["tool_call"].get("arguments") and len(s["tool_call"]["arguments"]) > 0
        )

        # Cost calculation
        total_cost = 0.0
        for t in tools_used:
            if t in self.tools_catalog:
                total_cost += self.tools_catalog[t].get("cost", 0)

        # Tool diversity score
        diversity = len(unique_tools) / total_calls if total_calls > 0 else 0.0

        # Efficiency: calls without errors / total calls
        efficiency = (total_calls - errors) / total_calls if total_calls > 0 else 1.0

        return {
            "total_tool_calls": total_calls,
            "unique_tools_used": sorted(unique_tools),
            "tool_frequency": tool_freq,
            "errors": errors,
            "wrong_tool_selections": wrong_tool,
            "argument_quality": round(good_args / total_calls, 2) if total_calls > 0 else 1.0,
            "tool_diversity": round(diversity, 3),
            "tool_efficiency": round(efficiency, 3),
            "estimated_cost": round(total_cost, 2),
        }


# ===================================================================
# 5. PlanQualityEvaluator
# ===================================================================

class PlanQualityEvaluator:
    """Evaluates the quality, coherence, and execution of the agent's plan."""

    def evaluate(self, trace):
        plan = trace.get("plan", [])
        steps = trace.get("steps", [])
        goal_achieved = trace.get("goal_achieved", False)

        plan_length = len(plan)

        # Was the plan followed? Compare plan steps to actual actions taken
        actions_taken = [s.get("action") for s in steps if s.get("action") != "final_answer"]

        # Rough adherence: what fraction of plan steps map to actual actions
        plan_adherence = min(1.0, len(actions_taken) / plan_length) if plan_length > 0 else 0.0

        # Plan specificity: longer/more-detailed plan items score higher
        avg_plan_detail = sum(len(p.split()) for p in plan) / plan_length if plan_length else 0
        specificity = min(1.0, avg_plan_detail / 10.0)

        # Plan-to-execution ratio
        plan_execution_ratio = len(actions_taken) / plan_length if plan_length > 0 else 0.0

        # Feasibility: did the plan lead to success?
        feasibility = 1.0 if goal_achieved else 0.5 if trace.get("task_completed") else 0.0

        overall = round(
            0.3 * plan_adherence + 0.2 * specificity + 0.2 * min(1.0, plan_execution_ratio) + 0.3 * feasibility,
            3,
        )

        return {
            "plan_length": plan_length,
            "plan_steps": plan,
            "plan_adherence": round(plan_adherence, 3),
            "plan_specificity": round(specificity, 3),
            "plan_execution_ratio": round(plan_execution_ratio, 3),
            "feasibility_score": feasibility,
            "overall_plan_quality": overall,
        }


# ===================================================================
# 6. MemoryEvaluator
# ===================================================================

class MemoryEvaluator:
    """Evaluates how well the agent uses memory (information from earlier steps)."""

    def evaluate(self, trace):
        steps = trace.get("steps", [])

        # Heuristic: does a later thought reference information from an earlier observation?
        observations = []
        memory_references = 0
        total_thoughts = 0

        for s in steps:
            obs = s.get("observation") or ""
            thought = s.get("thought", "")
            total_thoughts += 1

            # Check if thought references keywords from earlier observations
            for prev_obs in observations:
                prev_words = set(prev_obs.lower().split()) - {"the", "a", "is", "to", "and", "of", "in", "for"}
                thought_words = set(thought.lower().split())
                overlap = prev_words & thought_words
                if len(overlap) >= 3:
                    memory_references += 1
                    break

            if obs:
                observations.append(obs)

        # Did agent re-search for already-known info?
        tool_queries = []
        redundant_queries = 0
        for s in steps:
            tc = s.get("tool_call")
            if tc and tc.get("arguments"):
                q = str(tc["arguments"])
                for prev_q in tool_queries:
                    # Simple similarity check
                    prev_set = set(prev_q.lower().split())
                    curr_set = set(q.lower().split())
                    if prev_set and curr_set:
                        jaccard = len(prev_set & curr_set) / len(prev_set | curr_set)
                        if jaccard > 0.6:
                            redundant_queries += 1
                            break
                tool_queries.append(q)

        utilization = memory_references / max(1, total_thoughts - 1)

        return {
            "total_observations_stored": len(observations),
            "memory_references_in_thoughts": memory_references,
            "memory_utilization": round(utilization, 3),
            "redundant_queries": redundant_queries,
            "memory_efficiency": round(
                1.0 - (redundant_queries / max(1, len(tool_queries))), 3
            ),
        }


# ===================================================================
# 7. ReflectionEvaluator
# ===================================================================

class ReflectionEvaluator:
    """Evaluates the agent's ability to self-correct and reflect on mistakes."""

    POSITIVE_SIGNALS = ["verify", "check", "confirm", "reconsider", "correct", "mistake"]
    NEGATIVE_SIGNALS = ["gave_up", "jumped_to_conclusion", "ignored"]

    def evaluate(self, trace):
        steps = trace.get("steps", [])
        corrections = trace.get("self_corrections", 0)

        # Scan thoughts for reflection language
        reflection_steps = 0
        verification_steps = 0
        for s in steps:
            thought = (s.get("thought", "") or "").lower()
            quality = (s.get("reasoning_quality", "") or "").lower()

            if any(sig in thought for sig in self.POSITIVE_SIGNALS):
                reflection_steps += 1
            if "verif" in quality or "verification" in thought:
                verification_steps += 1

        # Did agent catch its own errors?
        errors_in_obs = sum(
            1 for s in steps if "Error" in (s.get("observation") or "")
        )
        recovered = corrections > 0 and trace.get("goal_achieved", False)

        total = len(steps)
        reflection_rate = reflection_steps / total if total > 0 else 0.0

        # Quality score
        if recovered:
            quality = "strong"
            score = 1.0
        elif reflection_steps > 0 and trace.get("goal_achieved"):
            quality = "adequate"
            score = 0.7
        elif reflection_steps > 0:
            quality = "present_but_insufficient"
            score = 0.4
        else:
            quality = "absent"
            score = 0.1

        return {
            "self_corrections": corrections,
            "reflection_steps": reflection_steps,
            "verification_steps": verification_steps,
            "reflection_rate": round(reflection_rate, 3),
            "errors_encountered": errors_in_obs,
            "recovered_from_errors": recovered,
            "reflection_quality": quality,
            "reflection_score": score,
        }


# ===================================================================
# 8. MultiAgentEvaluator
# ===================================================================

class MultiAgentEvaluator:
    """Evaluates coordination, role clarity, and efficiency in multi-agent traces."""

    def evaluate(self, multi_trace):
        agents = multi_trace.get("agents", {})
        coord = multi_trace.get("coordination_quality", {})
        goal = multi_trace.get("goal_achieved", False)

        agent_names = list(agents.keys())
        total_steps = multi_trace.get("total_steps", 0)
        total_tools = multi_trace.get("total_tool_calls", 0)

        # Role separation
        role_separation = coord.get("clear_role_separation", False)
        no_redundant = coord.get("no_redundant_work", False)
        effective_handoffs = coord.get("effective_handoffs", False)
        consensus = coord.get("consensus_reached", False)

        # Check for duplicated tool calls across agents
        all_tools = []
        per_agent_stats = {}
        for name, info in agents.items():
            calls = info.get("tool_calls", [])
            all_tools.extend(calls)
            per_agent_stats[name] = {
                "role": info.get("role", ""),
                "steps": info.get("steps_taken", 0),
                "tool_calls": len(calls),
            }

        tool_counts = Counter(all_tools)
        redundant_tools = sum(v - 1 for v in tool_counts.values() if v > 1)

        # Coordination score: 0-1
        coord_score = sum([role_separation, no_redundant, effective_handoffs, consensus]) / 4.0

        # Efficiency: compare to single-agent baseline (assume optimal single = 3 steps)
        single_agent_baseline = 3
        multi_efficiency = single_agent_baseline / total_steps if total_steps > 0 else 0.0

        return {
            "num_agents": len(agent_names),
            "agent_names": agent_names,
            "per_agent_stats": per_agent_stats,
            "total_steps": total_steps,
            "total_tool_calls": total_tools,
            "redundant_tool_calls": redundant_tools,
            "coordination_score": coord_score,
            "role_separation": role_separation,
            "no_redundant_work": no_redundant,
            "effective_handoffs": effective_handoffs,
            "consensus_reached": consensus,
            "goal_achieved": goal,
            "multi_agent_efficiency": round(multi_efficiency, 3),
        }


# ===================================================================
# 9. CodingAgentEvaluator
# ===================================================================

class CodingAgentEvaluator:
    """Evaluates code quality metrics for code-generating agents."""

    def evaluate(self, code_trace):
        quality = code_trace.get("code_quality", {})
        tests = code_trace.get("test_results", {})

        passed = tests.get("passed", 0)
        total = tests.get("total", 1)
        pass_rate = passed / total if total > 0 else 0.0

        # Quality checklist
        checks = {
            "has_docstring": quality.get("has_docstring", False),
            "has_type_hints": quality.get("has_type_hints", False),
            "has_error_handling": quality.get("has_error_handling", False),
            "follows_naming_conventions": quality.get("follows_naming_conventions", False),
            "no_unused_imports": quality.get("no_unused_imports", False),
        }
        quality_score = sum(checks.values()) / len(checks)

        complexity = quality.get("code_complexity", "unknown")

        # Code length heuristic
        code = code_trace.get("generated_code", "")
        loc = len([line for line in code.split("\n") if line.strip()])

        overall = round(0.5 * pass_rate + 0.4 * quality_score + 0.1 * (1.0 if complexity == "low" else 0.5), 3)

        return {
            "test_pass_rate": round(pass_rate, 3),
            "tests_passed": passed,
            "tests_failed": tests.get("failed", 0),
            "quality_checks": checks,
            "quality_score": round(quality_score, 3),
            "code_complexity": complexity,
            "lines_of_code": loc,
            "overall_score": overall,
        }


# ===================================================================
# 10. BrowserAgentEvaluator
# ===================================================================

class BrowserAgentEvaluator:
    """Evaluates browser-based agent traces for navigation efficiency."""

    def evaluate(self, browser_trace):
        steps = browser_trace.get("steps", [])
        total = browser_trace.get("total_steps", len(steps))
        nav_actions = browser_trace.get("total_navigation_actions", 0)
        interaction_actions = browser_trace.get("total_interaction_actions", 0)
        completed = browser_trace.get("task_completed", False)
        errors = browser_trace.get("errors", [])
        dead_ends = browser_trace.get("dead_ends", 0)

        # Efficiency: fewer steps = better; baseline optimal = 3
        optimal = 3
        efficiency = min(1.0, optimal / total) if total > 0 else 0.0

        # Error rate
        error_rate = len(errors) / total if total > 0 else 0.0

        return {
            "total_steps": total,
            "navigation_actions": nav_actions,
            "interaction_actions": interaction_actions,
            "task_completed": completed,
            "errors": errors,
            "error_count": len(errors),
            "dead_ends": dead_ends,
            "efficiency_score": round(efficiency, 3),
            "error_rate": round(error_rate, 3),
        }


# ===================================================================
# 11. EloRating
# ===================================================================

class EloRating:
    """Tournament-style Elo rating system for comparing agents head-to-head."""

    def __init__(self, k=32, initial_rating=1500):
        self.k = k
        self.initial_rating = initial_rating
        self.ratings = {}
        self.match_history = []

    def _expected(self, rating_a, rating_b):
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))

    def _ensure_player(self, name):
        if name not in self.ratings:
            self.ratings[name] = float(self.initial_rating)

    def record_match(self, agent_a, agent_b, score_a, score_b):
        """Record a match. score_a and score_b should each be in {0, 0.5, 1}."""
        self._ensure_player(agent_a)
        self._ensure_player(agent_b)

        ea = self._expected(self.ratings[agent_a], self.ratings[agent_b])
        eb = self._expected(self.ratings[agent_b], self.ratings[agent_a])

        self.ratings[agent_a] += self.k * (score_a - ea)
        self.ratings[agent_b] += self.k * (score_b - eb)

        self.match_history.append({
            "agent_a": agent_a,
            "agent_b": agent_b,
            "score_a": score_a,
            "score_b": score_b,
        })

    def run_tournament(self, agents_scores):
        """Run a round-robin tournament.

        agents_scores: dict mapping agent_name -> list of per-task scores (0 or 1).
        All lists must have the same length (number of tasks).
        """
        names = list(agents_scores.keys())
        n_tasks = len(next(iter(agents_scores.values())))

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                wins_a = sum(
                    1 for t in range(n_tasks)
                    if agents_scores[a][t] > agents_scores[b][t]
                )
                wins_b = sum(
                    1 for t in range(n_tasks)
                    if agents_scores[b][t] > agents_scores[a][t]
                )
                draws = n_tasks - wins_a - wins_b

                # Record aggregated match
                total = wins_a + wins_b + draws
                if total > 0:
                    sa = (wins_a + 0.5 * draws) / total
                    sb = (wins_b + 0.5 * draws) / total
                    self.record_match(a, b, sa, sb)

    def get_leaderboard(self):
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)

    def get_ratings(self):
        return dict(self.ratings)


# ===================================================================
# Convenience: run all evaluators on a trace
# ===================================================================

def full_evaluation(trace, tools_catalog=None):
    """Run every applicable single-trace evaluator and return combined results."""
    return {
        "task_completion": TaskCompletionEvaluator().evaluate(trace),
        "goal_achievement": GoalAchievementEvaluator().evaluate(trace),
        "trajectory": TrajectoryEvaluator().evaluate(trace),
        "tool_use": ToolUseEvaluator(tools_catalog).evaluate(trace),
        "plan_quality": PlanQualityEvaluator().evaluate(trace),
        "memory": MemoryEvaluator().evaluate(trace),
        "reflection": ReflectionEvaluator().evaluate(trace),
    }
