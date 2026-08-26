"""
Chapter 8: Agent Evaluation

Standalone, small-function version.
"""

from statistics import mean


TRACE = {
    "goal": "Find the capital of France and answer clearly.",
    "steps": ["plan search", "use search tool", "read result", "answer Paris"],
    "used_tools": ["search"],
    "expected_tools": ["search"],
    "final_answer": "Paris",
    "ground_truth": "Paris",
}


def line():
    print("=" * 72)


def section(title):
    print()
    line()
    print(title)
    line()


def task_completion(trace):
    return 1.0 if trace["final_answer"] else 0.0


def goal_achievement(trace):
    return 1.0 if trace["final_answer"] == trace["ground_truth"] else 0.0


def plan_quality(trace):
    return min(len(trace["steps"]) / 4, 1.0)


def trajectory_quality(trace):
    useful_steps = 0
    for step in trace["steps"]:
        if step in ["plan search", "use search tool", "read result", "answer Paris"]:
            useful_steps += 1
    return useful_steps / len(trace["steps"])


def tool_use(trace):
    matched = 0
    for tool in trace["expected_tools"]:
        if tool in trace["used_tools"]:
            matched += 1
    return matched / len(trace["expected_tools"])


def memory_quality(previous_fact, final_answer):
    return 1.0 if previous_fact in final_answer or previous_fact == final_answer else 0.0


def reflection_quality(original_answer, improved_answer):
    return 1.0 if len(improved_answer) > len(original_answer) else 0.5


def multi_agent_score(agent_scores):
    return mean(agent_scores)


def coding_agent_score(passed_tests, total_tests):
    return passed_tests / total_tests


def browser_agent_score(completed_actions, total_actions):
    return completed_actions / total_actions


def elo_update(rating_a, rating_b, winner):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    actual_a = 1 if winner == "A" else 0
    new_a = rating_a + 32 * (actual_a - expected_a)
    return round(new_a, 1)


def main():
    section("Chapter 8: Agent Evaluation")

    section("1. Task Completion")
    print(f"Task completion: {task_completion(TRACE):.2f}")

    section("2. Goal Achievement")
    print(f"Goal achievement: {goal_achievement(TRACE):.2f}")

    section("3. Planning")
    print(f"Plan quality: {plan_quality(TRACE):.2f}")

    section("4. Trajectory")
    print(f"Trajectory quality: {trajectory_quality(TRACE):.2f}")

    section("5. Tool Use")
    print(f"Tool use score: {tool_use(TRACE):.2f}")

    section("6. Memory")
    print(f"Memory score: {memory_quality('Paris', TRACE['final_answer']):.2f}")

    section("7. Reflection")
    print(f"Reflection score: {reflection_quality('Paris', 'Paris is the capital of France.'):.2f}")

    section("8. Multi-Agent")
    print(f"Multi-agent score: {multi_agent_score([0.8, 0.9, 0.7]):.2f}")

    section("9. Coding Agents")
    print(f"Coding agent score: {coding_agent_score(8, 10):.2f}")

    section("10. Browser Agents")
    print(f"Browser agent score: {browser_agent_score(5, 6):.2f}")

    section("11. Elo Ranking")
    print(f"New rating for agent A after win: {elo_update(1200, 1200, 'A')}")


if __name__ == "__main__":
    main()
