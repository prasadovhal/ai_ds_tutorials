# Chapter 8: Agent Evaluation

## Overview

Agent evaluation spans multiple dimensions that go far beyond simple accuracy. Unlike standalone LLMs that produce a single response, agents are stateful systems that think, call tools, observe results, and decide what to do next. Evaluating them requires measuring not just whether they got the right answer, but how they got there -- the quality of their planning, the efficiency of their tool use, their ability to self-correct, and their coordination when working alongside other agents.

This chapter covers the complete evaluation framework for LLM-based agents:

- **Task completion and goal achievement** -- did the agent work?
- **Trajectory and planning quality** -- was the path sensible?
- **Tool use correctness and efficiency** -- right tools, right arguments?
- **Memory and reflection** -- does the agent learn from its own trace?
- **Multi-agent coordination** -- do agents collaborate or duplicate effort?
- **Domain-specific evaluation** -- coding quality, browser navigation
- **Comparative ranking** -- Elo tournaments for agent comparison

Standard benchmarks (AgentBench, SWE-Bench, GAIA, WebArena) provide cross-system comparisons on curated, reproducible task suites.

---

## 1. Task Completion Evaluation

### Problem

The most fundamental question about an agent: did it finish the job? A chatbot that gives a wrong answer is bad, but an agent that gets stuck in an infinite loop or abandons a task midway is worse. We need a way to measure both binary completion (done or not done) and partial progress.

### Intuition

Think of task completion like a delivery service. Binary completion asks "did the package arrive?" Partial scoring asks "how far did it get?" An agent that completed the task but missed the goal is like a delivery that arrived at the right building but wrong apartment -- partial credit applies.

### How It Works

Task completion evaluation combines two signals:

1. **Binary completion**: Did the agent declare itself finished (produce a final answer)?
2. **Goal achievement**: Did the final answer match the ground truth?

The partial scoring scheme:

| Task Completed | Goal Achieved | Partial Score |
|:--------------:|:------------:|:-------------:|
| Yes            | Yes          | 1.0           |
| Yes            | No           | 0.5           |
| No             | Yes          | 0.75 (rare)   |
| No             | No           | 0.0           |

### Key Concepts

- **Completion rate**: Fraction of traces where the agent declared a final answer
- **Goal rate**: Fraction of traces where the goal was actually achieved
- **Answer accuracy**: Fraction of traces where the final answer matched the ground truth
- **Average partial score**: Mean of partial scores across all traces, giving a nuanced view of overall performance

### Batch Evaluation

When evaluating a batch of traces, the evaluator produces aggregate metrics: completion rate, goal rate, accuracy, and average partial score. The per-trace breakdown shows each trace's final answer vs. ground truth with a PASS/FAIL label, making it easy to spot systematic failures.

---

## 2. Goal Achievement Evaluation

### Problem

An agent might complete a task (produce output) without actually achieving its stated goal. Goal achievement evaluation digs deeper than binary completion to check whether the agent met its requirements, including sub-goals.

### Intuition

Imagine asking an assistant to "book a flight to Paris for under $500 with a window seat." The assistant might book a flight to Paris (partial success) but forget the window seat or exceed the budget. Goal achievement checks every requirement, not just the top-level request.

### How It Works

The evaluator examines:

1. **Primary goal**: Was the stated goal achieved?
2. **Answer correctness**: Does the final answer match ground truth?
3. **Sub-goal completion**: Were all sub-requirements met? Each missed sub-goal reduces the score by 0.25.
4. **Issues found**: Total number of issues logged during execution.
5. **Missed requirements**: Specific requirements flagged as "partial" or "missed."

### Key Concepts

- **Sub-goal decomposition**: Breaking a complex goal into checkable components
- **Missed requirements detection**: Scanning issues for partial completions
- **Graduated scoring**: A score between 0 and 1 reflecting how many sub-goals were met, not just pass/fail

---

## 3. Planning Quality Evaluation

### Problem

Agents that plan before acting tend to be more efficient. But not all plans are equal -- some are vague, some are infeasible, and some are ignored during execution. We need metrics to evaluate the quality of an agent's plan and how well it was followed.

### Intuition

A good travel plan specifies flights, hotels, and activities in order. A bad plan says "go somewhere nice." Planning quality evaluation measures whether the agent's plan was specific, feasible, and actually followed during execution.

### How It Works

The evaluator scores four dimensions:

1. **Plan adherence** (weight: 0.3): What fraction of plan steps map to actual actions taken?
2. **Plan specificity** (weight: 0.2): Are plan steps detailed (measured by average word count, normalized against 10 words)?
3. **Plan-to-execution ratio** (weight: 0.2): How closely does the number of actions match the plan length?
4. **Feasibility** (weight: 0.3): Did the plan lead to success? (1.0 if goal achieved, 0.5 if task completed but goal missed, 0.0 otherwise)

**Overall plan quality formula:**

```
overall = 0.3 * adherence + 0.2 * specificity + 0.2 * min(1.0, execution_ratio) + 0.3 * feasibility
```

### Key Concepts

- **Plan adherence**: Measures discipline -- did the agent stick to its plan?
- **Plan specificity**: Vague plans (e.g., "figure it out") score low; detailed plans score high
- **Feasibility**: The ultimate test -- a beautiful plan that fails is still a bad plan
- Plans with more detailed steps (higher word count per step) receive higher specificity scores

---

## 4. Trace / Trajectory Evaluation

### Problem

Two agents might both get the right answer, but one does it in 3 steps while the other takes 15 steps with 8 unnecessary detours. Trajectory evaluation measures the efficiency and quality of the agent's step-by-step execution path.

### Intuition

Think of GPS navigation. Two routes might reach the same destination, but one is a direct highway while the other zigzags through side streets. Trajectory evaluation is the GPS efficiency score for agents -- it penalizes unnecessary steps, loops, and wasted computation.

### How It Works

Key metrics computed:

1. **Efficiency score**: `optimal_steps / actual_steps` (capped at 1.0). A perfect agent hits the optimal step count.
2. **Waste ratio**: `unnecessary_steps / total_steps`. How much of the agent's work was pointless?
3. **Loop detection**: Repeated identical tool calls indicate the agent is stuck. Computed by comparing unique vs. total tool call strings.
4. **Reasoning quality distribution**: Counts of each reasoning quality label (e.g., "focused_and_relevant", "vague_result", "wrong_tool_for_task").
5. **Latency and cost**: Total time and monetary cost of the trace.

### Key Concepts

- **Optimal steps**: The minimum number of steps a perfect agent would need (configurable, default: 2)
- **Waste ratio**: High waste means the agent is doing unnecessary work
- **Loop detection**: Repeated tool calls are a strong signal of agent confusion
- **Self-corrections**: Number of times the agent corrected its own mistakes (can be positive if it leads to success)

---

## 5. Tool Use Evaluation

### Problem

Agents interact with the world through tools. Choosing the wrong tool, passing bad arguments, or calling tools unnecessarily all waste resources and reduce accuracy. Tool use evaluation checks whether the agent selected the right tools, used them correctly, and did so efficiently.

### Intuition

A carpenter who uses a screwdriver to hammer nails is using the wrong tool. One who uses the right hammer but hits the wrong nail has an argument problem. Tool use evaluation checks both tool selection and argument quality.

### How It Works

The evaluator measures:

1. **Total tool calls**: Raw count of tool invocations
2. **Tool frequency**: Which tools were called and how often
3. **Errors**: Tool calls that produced error observations
4. **Wrong tool selections**: Steps flagged with "wrong_tool" reasoning quality
5. **Argument quality**: Fraction of tool calls with non-empty, valid arguments
6. **Tool diversity**: `unique_tools / total_calls` -- high diversity means varied tool use
7. **Tool efficiency**: `(total_calls - errors) / total_calls` -- error-free call rate
8. **Estimated cost**: Sum of per-tool costs from the tools catalog

### Key Concepts

- **Tool diversity score**: Measures whether the agent uses a variety of tools vs. hammering the same one repeatedly
- **Argument quality**: Tools called with empty or missing arguments are likely to fail
- **Cost estimation**: Each tool can have an associated cost in the catalog; total cost tracks resource usage
- **Wrong tool detection**: Uses reasoning quality annotations to flag mismatched tool choices

---

## 6. Memory Evaluation

### Problem

Agents that forget information from earlier steps waste time re-querying for facts they already know. Memory evaluation assesses how well the agent reuses information from earlier observations and avoids redundant queries.

### Intuition

Imagine a student who looks up the same formula five times during an exam instead of remembering it from the first lookup. Memory evaluation measures whether the agent "remembers" what it learned in earlier steps and uses that knowledge in later reasoning.

### How It Works

Two complementary checks:

1. **Memory utilization**: Do later thoughts reference information from earlier observations? Measured by word overlap (at least 3 meaningful words in common, excluding stop words like "the", "a", "is").

2. **Redundant query detection**: Does the agent re-search for information it already has? Measured by Jaccard similarity between tool call arguments. If two queries have Jaccard similarity > 0.6, the later one is flagged as redundant.

**Memory utilization formula:**
```
utilization = memory_references / max(1, total_thoughts - 1)
```

**Memory efficiency formula:**
```
efficiency = 1.0 - (redundant_queries / max(1, total_tool_queries))
```

### Key Concepts

- **Memory references in thoughts**: Evidence that the agent is building on prior knowledge
- **Redundant queries**: Tool calls that ask for information already retrieved
- **Jaccard similarity**: `|A intersection B| / |A union B|` -- used to detect near-duplicate queries
- High utilization + low redundancy = good memory usage

---

## 7. Reflection Evaluation

### Problem

The best agents don't just execute -- they reflect on their own reasoning, verify their conclusions, and self-correct when they make mistakes. Reflection evaluation measures the agent's capacity for metacognition.

### Intuition

A chess player who just moves pieces is weaker than one who pauses to ask "wait, does this move actually work?" Reflection evaluation checks whether the agent has these "wait, let me verify" moments and whether they lead to better outcomes.

### How It Works

The evaluator scans agent thoughts for reflection signals:

**Positive signals** (indicate reflection): "verify", "check", "confirm", "reconsider", "correct", "mistake"

**Negative signals** (indicate lack of reflection): "gave_up", "jumped_to_conclusion", "ignored"

Quality scoring:

| Condition | Quality Label | Score |
|:----------|:-------------|:-----:|
| Recovered from errors (self-corrected + goal achieved) | strong | 1.0 |
| Reflected + goal achieved | adequate | 0.7 |
| Reflected but goal not achieved | present_but_insufficient | 0.4 |
| No reflection detected | absent | 0.1 |

### Key Concepts

- **Reflection steps**: Steps where the agent's thought contains positive reflection signals
- **Verification steps**: Steps specifically focused on verifying previous results
- **Error recovery**: The strongest signal -- the agent made a mistake, caught it, and still achieved the goal
- **Reflection rate**: `reflection_steps / total_steps` -- what fraction of the agent's thinking involves self-evaluation

---

## 8. Multi-Agent Evaluation

### Problem

Multi-agent systems introduce new failure modes: agents might duplicate each other's work, fail to communicate, step on each other's toes, or leave gaps in coverage. Evaluating multi-agent systems requires checking coordination quality, not just individual performance.

### Intuition

A well-coordinated team divides work clearly: one person researches, another writes, a third reviews. A poorly coordinated team has everyone researching the same thing while nobody writes. Multi-agent evaluation checks for this coordination.

### How It Works

The evaluator checks four coordination dimensions:

1. **Role separation**: Do agents have clearly distinct roles?
2. **No redundant work**: Are agents avoiding duplicate effort?
3. **Effective handoffs**: Do agents smoothly pass work between each other?
4. **Consensus reached**: Do agents agree on the final output?

**Coordination score:**
```
coordination = (role_separation + no_redundant + effective_handoffs + consensus) / 4.0
```

**Multi-agent efficiency** compares against a single-agent baseline:
```
efficiency = single_agent_baseline_steps / total_multi_agent_steps
```

Additional metrics:
- **Redundant tool calls**: Tool calls made by multiple agents (counted by finding tools called more than once across all agents)
- **Per-agent statistics**: Steps taken and tool calls per agent, with role annotations

### Key Concepts

- **Role separation**: Each agent should have a distinct responsibility
- **Redundant tool calls**: A strong signal of coordination failure -- two agents calling the same tool wastes resources
- **Effective handoffs**: Information flows correctly between agents
- **Efficiency vs. single-agent**: Multi-agent systems should be faster than a single agent, not slower

---

## 9. Coding Agent Evaluation

### Problem

Code-generating agents need specialized evaluation beyond generic task completion. The code must not only work (pass tests) but also be well-structured, documented, and maintainable.

### Intuition

A coding interview doesn't just check if your code produces the right output. It also checks naming conventions, error handling, documentation, and code organization. Coding agent evaluation applies the same rigor.

### How It Works

The evaluator scores three dimensions:

1. **Test pass rate** (weight: 0.5): `tests_passed / total_tests`
2. **Quality score** (weight: 0.4): Average of five quality checks (each is binary 0 or 1):
   - Has docstrings
   - Has type hints
   - Has error handling
   - Follows naming conventions
   - No unused imports
3. **Complexity bonus** (weight: 0.1): 1.0 for "low" complexity, 0.5 otherwise

**Overall score formula:**
```
overall = 0.5 * test_pass_rate + 0.4 * quality_score + 0.1 * complexity_bonus
```

### Key Concepts

- **Test pass rate**: The most important signal -- does the code actually work?
- **Quality checks**: Five binary checks covering documentation, typing, error handling, naming, and import hygiene
- **Lines of code (LOC)**: Measured by counting non-empty lines
- **Code complexity**: A qualitative label ("low", "medium", "high") reflecting structural complexity

---

## 10. Browser Agent Evaluation

### Problem

Browser-based agents must navigate websites, fill forms, click buttons, and extract information. They face unique challenges: pages load dynamically, elements may not be where expected, and wrong clicks lead to dead ends.

### Intuition

Think of a user navigating a complex website to book a flight. An efficient user goes directly to the search page, enters criteria, and books. An inefficient user clicks random links, hits dead ends, and reloads pages. Browser agent evaluation measures this navigation efficiency.

### How It Works

Key metrics:

1. **Navigation actions**: Page loads, link clicks, URL navigations
2. **Interaction actions**: Form fills, button clicks, element selections
3. **Efficiency score**: `optimal_steps / actual_steps` (optimal baseline: 3 steps)
4. **Error count**: Number of errors encountered (page not found, element not clickable, etc.)
5. **Dead ends**: Pages or states from which the agent had to backtrack
6. **Error rate**: `errors / total_steps`
7. **Task completed**: Boolean -- did the agent finish the browser task?

### Key Concepts

- **Dead ends**: A critical metric -- each dead end means the agent wasted steps navigating to a useless page and backtracking
- **Navigation vs. interaction split**: Helps diagnose whether failures are in finding the right page or in using page elements
- **Error types**: Element not found, page timeout, wrong page, permission denied -- each suggests different agent weaknesses

---

## 11. Elo Rating - Agent Comparison Tournament

### Problem

When comparing multiple agent variants, raw accuracy numbers can be misleading. Agent A might beat Agent B on easy tasks but lose on hard ones. We need a principled ranking system that accounts for the difficulty of tasks and produces a single, comparable score.

### Intuition

Elo ratings work like chess rankings. A player who beats strong opponents gains more rating points than one who beats weak opponents. Applied to agents, we run pairwise comparisons across shared tasks and update ratings based on who "wins" each task.

### How It Works

**Elo formula:**

```
Expected score:  E_A = 1 / (1 + 10^((R_B - R_A) / 400))
Rating update:   R_A_new = R_A + K * (S_A - E_A)
```

Where:
- `R_A`, `R_B` = current ratings of agents A and B
- `E_A` = expected score for agent A (probability of winning)
- `S_A` = actual score (1 for win, 0.5 for draw, 0 for loss)
- `K` = update factor (default: 32) -- controls how much each match affects ratings

**Tournament process:**
1. All agents start with the same initial rating (default: 1500)
2. Round-robin: every pair of agents is compared across all shared tasks
3. Per-task wins, losses, and draws are aggregated into a single match score
4. Elo ratings are updated after each pairwise comparison
5. Final leaderboard is sorted by rating

### Key Concepts

- **K-factor**: Controls rating sensitivity. Higher K = ratings change faster. Default 32 is standard for new players.
- **Initial rating**: 1500 by convention (same as chess). All agents start equal.
- **Round-robin tournament**: Every agent plays against every other agent, ensuring fair comparison
- **Aggregated match scores**: Per-task comparisons are rolled up: `score_A = (wins_A + 0.5 * draws) / total_tasks`

---

## 12. Full Evaluation Pipeline

### Problem

Running evaluators one at a time gives fragmented results. A full evaluation pipeline runs every applicable evaluator on a single trace and produces a unified report, making it easy to compare good vs. bad traces across all dimensions.

### How It Works

The full evaluation function runs seven evaluators on each trace:

1. **Task completion** -- binary and partial scores
2. **Goal achievement** -- goal, sub-goals, missed requirements
3. **Trajectory** -- step count, efficiency, waste, loops, cost
4. **Tool use** -- selection accuracy, arguments, diversity, errors
5. **Plan quality** -- adherence, specificity, feasibility
6. **Memory** -- utilization, redundant queries
7. **Reflection** -- self-correction, verification, quality

Running this on both a "good" trace and a "bad" trace reveals exactly where the bad agent falls short and guides targeted improvements.

---

## 13. Agent Benchmarks Overview

### AgentBench

Multi-dimensional benchmark testing agents across OS, DB, KG, web, and lateral-thinking tasks.

- **Metrics**: success_rate, task_completion, efficiency
- **URL**: https://github.com/THUDM/AgentBench

### SWE-Bench

Real GitHub issues from popular repos; agents must generate patches that pass existing test suites.

- **Metrics**: resolve_rate, patch_correctness, test_pass_rate
- **URL**: https://www.swebench.com/

### GAIA

General AI Assistants benchmark with multi-step real-world questions requiring tool use and reasoning.

- **Metrics**: exact_match_accuracy, tool_use_efficiency
- **URL**: https://huggingface.co/gaia-benchmark

### WebArena

Realistic web-browsing tasks on self-hosted sites (shopping, forums, maps, GitLab, Wikipedia).

- **Metrics**: task_success_rate, step_efficiency, navigation_accuracy
- **URL**: https://webarena.dev/

---

## 14. Synthetic Batch Evaluation

### Problem

Real agent traces are expensive to collect. Synthetic trace generation lets you stress-test evaluators at scale, verify they handle edge cases, and build regression test suites without running actual agents.

### How It Works

The synthetic generator creates traces with configurable parameters:
- **Number of steps**: Random between 2 and 7
- **Goal achieved**: Randomized (70% chance of success by default)
- **Task completed**: Linked to goal achievement with additional randomness
- **Tool calls**: Drawn from a catalog of tool names (search_knowledge_base, calculate, lookup_formula, verify_answer, ask_human)
- **Reasoning quality**: Randomly assigned from labels like "focused_and_relevant", "thorough_verification", "vague_result", "wrong_tool_for_task", "jumped_to_conclusion", "decisive"

Synthetic traces include plans, steps with tool calls, observations, answers, cost, and latency -- everything a real trace would have.

---

## Why Use LangGraph, Langfuse, and Tracing for Agents

### LangGraph

Agents are inherently stateful -- they think, call tools, observe results, and decide what to do next. LangGraph's `create_react_agent` handles this loop natively with built-in state management, tool binding, and message history. Without it, you write fragile while-loops that break when the agent takes unexpected paths.

### Langfuse

Agent traces are complex (5-20 steps). Langfuse captures the full trajectory as nested spans, so you can see exactly which tool call failed, which reasoning step was wrong, and how much each step cost. Attach scores (accuracy, efficiency, trajectory) to each trace and filter by low-performing runs in the dashboard.

### Tracing

Agents make multiple LLM calls per task. Without tracing, you can't tell if a slow response was caused by the reasoning step, a tool timeout, or the final synthesis. Tracing gives you per-step latency, token counts, and error attribution -- essential for debugging agent failures in production.

---

## Hands-On: LangGraph ReAct Agent Evaluation

### Setup

The hands-on exercise builds a real LangGraph ReAct agent using ChatOllama (Mistral), runs it on science questions, captures full traces, and evaluates agent trajectories.

### Tools Available to the Agent

1. **search_knowledge**: Searches a knowledge bank for science facts (physics, chemistry, biology, astrophysics, math, optics, electromagnetism)
2. **calculate**: Evaluates simple math expressions safely
3. **get_hint**: Returns hints for specific science topics (dynamics, scaling, diffraction, thermodynamics, quantum)

### Trace Extraction

LangGraph message objects are converted into simple step dictionaries with:
- **role**: human, ai, or tool
- **content**: The message text
- **tool_calls**: List of tool invocations (for AI messages)
- **tool**: Tool name (for tool response messages)

### Evaluation Metrics (Hands-On)

Each trace is scored on:
- **Task complete**: Did the agent produce a final answer?
- **Tool calls**: Number of tool invocations
- **Tools used**: Which tools were called
- **Tool correct**: Were any tools used at all?
- **Answer correct**: Does the predicted answer match ground truth?
- **Trajectory length**: Total number of steps in the trace

### LangSmith Integration

When enabled (`LANGSMITH_TRACING=true`), all agent traces are automatically sent to the LangSmith dashboard for visualization and analysis at https://smith.langchain.com.

### Langfuse Integration

Langfuse captures each question as a span within a trace, with scores for answer correctness, tool call count, and trajectory length. View results at https://cloud.langfuse.com.

---

## Summary

Agent evaluation spans multiple dimensions:

- **Task completion and goal achievement** -- did it work?
- **Trajectory and planning quality** -- was the path sensible?
- **Tool use correctness and efficiency** -- right tools, right arguments?
- **Memory and reflection** -- does it learn from its own trace?
- **Multi-agent coordination** -- do agents collaborate or duplicate?
- **Domain-specific**: coding quality, browser navigation
- **Comparative ranking** via Elo tournaments

Standard benchmarks (AgentBench, SWE-Bench, GAIA, WebArena) provide cross-system comparisons on curated, reproducible task suites.

---

## Evaluator Comparison Table

| Evaluator | What It Measures | Key Metric | When to Use |
|:----------|:----------------|:-----------|:------------|
| TaskCompletion | Did the agent finish? | completion_rate, accuracy | Every agent evaluation |
| GoalAchievement | Did it meet requirements? | sub_goal_completion | Complex multi-requirement tasks |
| PlanQuality | Was the plan good and followed? | overall_plan_quality | Agents with explicit planning |
| Trajectory | Was the execution path efficient? | efficiency_score, waste_ratio | Optimizing agent cost/latency |
| ToolUse | Right tools, right arguments? | tool_efficiency, argument_quality | Tool-using agents |
| Memory | Does it remember earlier info? | memory_utilization, redundant_queries | Multi-step reasoning agents |
| Reflection | Does it self-correct? | reflection_score, reflection_quality | Agents with error recovery |
| MultiAgent | Do agents coordinate well? | coordination_score | Multi-agent systems |
| CodingAgent | Is generated code good? | test_pass_rate, quality_score | Code generation agents |
| BrowserAgent | Is navigation efficient? | efficiency_score, dead_ends | Web browsing agents |
| EloRating | How do agents compare? | Elo rating | Comparing agent variants |

---

## Common Mistakes

1. **Evaluating only accuracy**: An agent with 90% accuracy but 20 steps per task is worse than one with 85% accuracy and 3 steps. Always evaluate efficiency alongside correctness.
2. **Ignoring tool argument quality**: An agent might select the right tool but pass wrong arguments. Track argument quality separately.
3. **Not checking for loops**: Agents stuck in infinite loops burn tokens and cost money. Always run loop detection.
4. **Skipping memory evaluation**: Redundant queries are a silent cost multiplier. An agent that re-searches for known information wastes resources.
5. **Evaluating multi-agent systems as single agents**: Multi-agent coordination failures (redundant work, poor handoffs) are invisible to single-agent evaluators.
6. **Using raw scores without baselines**: An efficiency score of 0.5 means nothing without knowing the optimal step count. Always calibrate against baselines.
7. **Not running full evaluation pipeline**: Individual evaluators catch individual problems. Only the full pipeline reveals how dimensions interact.

---

## Best Practices

1. **Run all evaluators**: Use the full evaluation pipeline to get a complete picture.
2. **Set realistic optimal step counts**: The trajectory evaluator's optimal_steps parameter should reflect the actual minimum for your task domain.
3. **Maintain a tools catalog**: Track per-tool costs so the tool use evaluator can estimate total cost accurately.
4. **Generate synthetic traces for testing**: Before deploying evaluators on real traces, validate them on synthetic data.
5. **Compare good vs. bad traces**: Run full evaluation on known-good and known-bad traces to calibrate your expectations.
6. **Use Elo for variant comparison**: When testing multiple agent architectures or prompt strategies, Elo gives a principled ranking.
7. **Integrate tracing (LangSmith/Langfuse)**: Production agents need observability. Attach evaluation scores to traced runs for monitoring.
8. **Track trends over time**: A single evaluation is a snapshot. Continuous evaluation catches regressions.
9. **Weight evaluation dimensions by use case**: For a customer support agent, accuracy matters most. For a research agent, tool diversity and memory might matter more.
10. **Include domain-specific evaluators**: Generic evaluators miss domain-specific quality signals (code quality for coding agents, navigation efficiency for browser agents).

---

## Interview Questions

1. **What is the difference between task completion and goal achievement?**
   Task completion checks if the agent produced a final output. Goal achievement checks if that output actually satisfied the stated requirements. An agent can complete a task (produce an answer) without achieving the goal (the answer is wrong).

2. **How do you detect loops in agent traces?**
   Compare the set of unique tool calls to the total list of tool calls. If there are more total calls than unique calls, the agent repeated identical tool calls, indicating a loop.

3. **What is the waste ratio and why does it matter?**
   Waste ratio = unnecessary_steps / total_steps. It measures what fraction of the agent's work was pointless. High waste means the agent is burning tokens and time on steps that don't contribute to the goal.

4. **How does Elo rating work for agent comparison?**
   Agents are compared pairwise across shared tasks. The expected score is calculated using the Elo formula, and ratings are updated based on actual vs. expected performance. Agents that beat strong opponents gain more rating points.

5. **What are the four dimensions of multi-agent coordination quality?**
   Role separation (distinct responsibilities), no redundant work (no duplication), effective handoffs (smooth information transfer), and consensus reached (agents agree on output).

6. **How do you evaluate memory in an agent?**
   Check if later thoughts reference keywords from earlier observations (memory utilization), and check if tool queries are near-duplicates of earlier queries using Jaccard similarity (redundant query detection).

7. **What quality checks matter for coding agents?**
   Test pass rate (does it work?), docstrings, type hints, error handling, naming conventions, and import hygiene. The overall score weights test pass rate at 50%, quality at 40%, and complexity at 10%.

8. **Why is reflection evaluation important?**
   Agents that self-correct and verify their reasoning are more reliable. Reflection evaluation distinguishes agents that blindly execute from those that pause to check their work.

9. **Name four major agent benchmarks and what they test.**
   AgentBench (multi-dimensional: OS, DB, web), SWE-Bench (real GitHub issue resolution), GAIA (multi-step real-world questions with tool use), WebArena (realistic web browsing tasks).

10. **Why do you need tracing for agent evaluation in production?**
    Agents make multiple LLM calls per task. Tracing provides per-step latency, token counts, and error attribution, making it possible to diagnose whether a failure was caused by reasoning, tool execution, or synthesis.

---

## Project Structure

```text
chapter_08_agent_evaluation/
    sample_data.json    -- Agent traces: single-agent, multi-agent, coding, and browser
    dataset.py          -- Data loading + synthetic trace generation
    evaluator.py        -- All evaluation metrics (10 evaluator classes + Elo)
    main.py             -- Demonstrations with output for every evaluator
    hands_on.py         -- LangGraph ReAct agent with real evaluation
```

Run with:

```bash
cd chapter_08_agent_evaluation
python main.py
```

Requirements: Python 3.7+ (standard library only for main evaluation). For hands-on: LangGraph, LangChain, ChatOllama, pandas, and optionally Langfuse.

---

## Further Reading

- **AgentBench**: https://github.com/THUDM/AgentBench
- **SWE-Bench**: https://www.swebench.com/
- **GAIA Benchmark**: https://huggingface.co/gaia-benchmark
- **WebArena**: https://webarena.dev/
- **LangSmith Tracing**: https://smith.langchain.com
- **Langfuse**: https://cloud.langfuse.com
- **LangGraph ReAct Agent**: LangGraph documentation for `create_react_agent`
