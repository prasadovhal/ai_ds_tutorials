# Chapter 8: Agent Evaluation

## Overview

Unlike standalone LLMs, agents are stateful systems that think, call tools, observe results, and decide next steps. Evaluation must cover not just correctness but planning quality, tool efficiency, self-correction, and multi-agent coordination.

This chapter covers: task completion, goal achievement, planning quality, trajectory evaluation, tool use, memory, reflection, multi-agent coordination, coding agents, browser agents, Elo ranking, and standard benchmarks.

---

## 1. Task Completion Evaluation

Checks whether the agent finished and whether the final answer is correct. Combines binary completion with partial scoring.

| Task Completed | Goal Achieved | Partial Score |
|:-:|:-:|:-:|
| Yes | Yes | 1.0 |
| Yes | No | 0.5 |
| No | Yes | 0.75 |
| No | No | 0.0 |

**Metrics**: completion_rate, goal_rate, answer_accuracy, avg_partial_score.

---

## 2. Goal Achievement Evaluation

An agent can complete a task (produce output) without meeting its stated goal. This evaluator checks primary goal, answer correctness, and sub-goal completion. Each missed sub-goal reduces the score by 0.25. Issues flagged as "partial" or "missed" are surfaced.

**Key idea**: graduated scoring between 0-1 based on sub-goal decomposition, not binary pass/fail.

---

## 3. Planning Quality Evaluation

Scores how good the agent's plan was and whether it was followed.

```
overall = 0.3 * adherence + 0.2 * specificity + 0.2 * min(1.0, execution_ratio) + 0.3 * feasibility
```

- **Adherence** (0.3): fraction of plan steps that map to actual actions
- **Specificity** (0.2): average word count per step, normalized against 10 words
- **Execution ratio** (0.2): how closely action count matches plan length
- **Feasibility** (0.3): 1.0 if goal achieved, 0.5 if completed but missed, 0.0 otherwise

---

## 4. Trace / Trajectory Evaluation

Measures efficiency of the agent's step-by-step execution path. Two agents may reach the same answer, but one in 3 steps and another in 15 with detours.

- **Efficiency**: `optimal_steps / actual_steps` (capped at 1.0)
- **Waste ratio**: `unnecessary_steps / total_steps`
- **Loop detection**: repeated identical tool calls indicate the agent is stuck (unique vs. total tool call comparison)
- **Reasoning quality distribution**: counts per label (focused, vague, wrong_tool, etc.)
- **Latency and cost**: total time and monetary cost

---

## 5. Tool Use Evaluation

Checks whether the agent selected the right tools, used correct arguments, and did so efficiently.

- **Tool frequency**: which tools called, how often
- **Errors**: tool calls producing error observations
- **Wrong tool**: steps flagged with "wrong_tool" reasoning quality
- **Argument quality**: fraction of calls with non-empty, valid arguments
- **Diversity**: `unique_tools / total_calls`
- **Efficiency**: `(total_calls - errors) / total_calls`
- **Cost**: sum of per-tool costs from catalog

---

## 6. Memory Evaluation

Measures how well the agent reuses earlier information and avoids redundant queries.

**Memory utilization**: do later thoughts reference earlier observations? Measured by word overlap (3+ meaningful words in common, excluding stop words).

```
utilization = memory_references / max(1, total_thoughts - 1)
```

**Redundant query detection**: Jaccard similarity > 0.6 between tool call arguments flags a redundant query.

```
efficiency = 1.0 - (redundant_queries / max(1, total_tool_queries))
```

**Jaccard similarity**: `|A ∩ B| / |A ∪ B|`

---

## 7. Reflection Evaluation

Measures the agent's capacity for metacognition -- self-correction and verification.

**Positive signals** in thoughts: "verify", "check", "confirm", "reconsider", "correct", "mistake"
**Negative signals**: "gave_up", "jumped_to_conclusion", "ignored"

| Condition | Quality | Score |
|:--|:--|:-:|
| Self-corrected + goal achieved | strong | 1.0 |
| Reflected + goal achieved | adequate | 0.7 |
| Reflected but goal missed | present_but_insufficient | 0.4 |
| No reflection | absent | 0.1 |

**Reflection rate**: `reflection_steps / total_steps`

---

## 8. Multi-Agent Evaluation

Multi-agent systems have unique failure modes: duplication, poor communication, coverage gaps. Evaluates four coordination dimensions:

1. **Role separation**: distinct roles per agent
2. **No redundant work**: no duplicate effort
3. **Effective handoffs**: smooth information transfer
4. **Consensus reached**: agents agree on output

```
coordination = (role_separation + no_redundant + effective_handoffs + consensus) / 4.0
efficiency = single_agent_baseline_steps / total_multi_agent_steps
```

Also tracks redundant tool calls across agents and per-agent statistics.

---

## 9. Coding Agent Evaluation

Specialized evaluation for code-generating agents.

```
overall = 0.5 * test_pass_rate + 0.4 * quality_score + 0.1 * complexity_bonus
```

- **Test pass rate** (0.5): `tests_passed / total_tests`
- **Quality score** (0.4): average of 5 binary checks -- docstrings, type hints, error handling, naming conventions, no unused imports
- **Complexity bonus** (0.1): 1.0 for "low" complexity, 0.5 otherwise

---

## 10. Browser Agent Evaluation

Evaluates web-navigation agents on efficiency and error handling.

- **Navigation actions**: page loads, link clicks, URL navigations
- **Interaction actions**: form fills, button clicks, element selections
- **Efficiency**: `optimal_steps / actual_steps` (optimal baseline: 3)
- **Dead ends**: pages requiring backtracking -- a critical waste signal
- **Error rate**: `errors / total_steps`

---

## 11. Elo Rating - Agent Comparison Tournament

Ranks agents via pairwise comparisons, like chess ratings.

**Elo formula:**

```
Expected score:  E_A = 1 / (1 + 10^((R_B - R_A) / 400))
Rating update:   R_A_new = R_A + K * (S_A - E_A)
```

- `R_A`, `R_B` = current ratings of agents A and B
- `E_A` = expected score (probability of A winning)
- `S_A` = actual score (1 win, 0.5 draw, 0 loss)
- `K` = update factor (default 32, controls sensitivity)

**Tournament**: all agents start at 1500, round-robin pairwise comparison across shared tasks, ratings updated after each match.

---

## 12. Full Evaluation Pipeline

Runs all seven evaluators on a single trace for a unified report: task completion, goal achievement, trajectory, tool use, plan quality, memory, reflection. Comparing good vs. bad traces reveals exactly where failures occur.

---

## 13. Agent Benchmarks

| Benchmark | Focus | Key Metrics | URL |
|:--|:--|:--|:--|
| AgentBench | OS, DB, KG, web, lateral thinking | success_rate, efficiency | github.com/THUDM/AgentBench |
| SWE-Bench | Real GitHub issue patches | resolve_rate, test_pass_rate | swebench.com |
| GAIA | Multi-step real-world questions | exact_match, tool_efficiency | huggingface.co/gaia-benchmark |
| WebArena | Web browsing on self-hosted sites | task_success_rate, navigation_accuracy | webarena.dev |

---

## 14. Synthetic Batch Evaluation

Synthetic trace generation stress-tests evaluators at scale without running real agents. Configurable parameters: step count (2-7), goal achievement (70% default), tool calls from a catalog, randomized reasoning quality labels.

---

## LangGraph, Langfuse & Tracing

- **LangGraph**: handles the think-act-observe loop natively with state management and tool binding. Without it, you write fragile while-loops.
- **Langfuse**: captures full trajectories as nested spans with per-step cost, scores, and filtering by low-performing runs.
- **Tracing**: per-step latency, token counts, and error attribution -- essential for diagnosing whether failures are in reasoning, tool execution, or synthesis.

---

## Hands-On: LangGraph ReAct Agent

Build a LangGraph ReAct agent (ChatOllama + Mistral) on science questions. Tools: `search_knowledge` (science facts), `calculate` (math), `get_hint` (topic hints). Extract traces from LangGraph messages and evaluate: task completion, tool calls, answer correctness, trajectory length. Optional LangSmith/Langfuse integration for dashboard visualization.

---

## Evaluator Comparison Table

| Evaluator | Measures | Key Metric | When to Use |
|:--|:--|:--|:--|
| TaskCompletion | Did it finish? | completion_rate | Every evaluation |
| GoalAchievement | Met requirements? | sub_goal_completion | Multi-requirement tasks |
| PlanQuality | Plan followed? | overall_plan_quality | Agents with planning |
| Trajectory | Path efficient? | efficiency, waste_ratio | Cost/latency optimization |
| ToolUse | Right tools/args? | tool_efficiency | Tool-using agents |
| Memory | Remembers info? | utilization, redundancy | Multi-step reasoning |
| Reflection | Self-corrects? | reflection_score | Error recovery agents |
| MultiAgent | Coordination? | coordination_score | Multi-agent systems |
| CodingAgent | Code quality? | test_pass_rate | Code generation |
| BrowserAgent | Navigation? | efficiency, dead_ends | Web browsing agents |
| EloRating | Comparison? | Elo rating | Comparing variants |

---

## Common Mistakes

1. **Evaluating only accuracy** -- always measure efficiency alongside correctness
2. **Ignoring argument quality** -- right tool with wrong args still fails
3. **Not checking for loops** -- burns tokens silently
4. **Skipping memory evaluation** -- redundant queries are a hidden cost multiplier
5. **Treating multi-agent as single-agent** -- coordination failures are invisible to single-agent evaluators
6. **No baselines** -- efficiency 0.5 is meaningless without knowing optimal steps
7. **Not running full pipeline** -- individual evaluators miss dimension interactions

---

## Best Practices

1. Run all evaluators via the full pipeline for a complete picture
2. Set realistic optimal step counts for your task domain
3. Maintain a tools catalog with per-tool costs
4. Validate evaluators on synthetic traces before deploying on real data
5. Compare known-good vs. known-bad traces to calibrate expectations
6. Use Elo for variant comparison across architectures/prompts
7. Integrate tracing (LangSmith/Langfuse) and attach scores to traced runs
8. Track evaluation trends over time to catch regressions
9. Weight dimensions by use case (support agent: accuracy; research agent: tool diversity)
10. Add domain-specific evaluators (code quality, navigation efficiency)

---

## Interview Questions

**1. Task completion vs. goal achievement?**
Task completion = agent produced output. Goal achievement = output satisfied requirements. You can complete without achieving.

**2. How detect loops in traces?**
Compare unique vs. total tool calls. More total than unique = repeated calls = loop.

**3. What is waste ratio?**
`unnecessary_steps / total_steps`. High waste = agent burning tokens on non-contributing steps.

**4. How does Elo work for agents?**
Pairwise comparison across shared tasks. Expected score via Elo formula, ratings updated based on actual vs. expected. Beating strong opponents yields more points.

**5. Four dimensions of multi-agent coordination?**
Role separation, no redundant work, effective handoffs, consensus reached.

**6. How evaluate agent memory?**
Memory utilization: later thoughts reference earlier observations (word overlap). Redundancy: Jaccard similarity > 0.6 flags duplicate queries.

**7. Quality checks for coding agents?**
Test pass rate (50%), quality checks -- docstrings, type hints, error handling, naming, imports (40%), complexity bonus (10%).

**8. Why is reflection evaluation important?**
Agents that self-correct are more reliable. Reflection distinguishes blind execution from verified reasoning.

**9. Four major agent benchmarks?**
AgentBench (multi-dimensional), SWE-Bench (GitHub issues), GAIA (multi-step + tools), WebArena (web browsing).

**10. Why tracing for production agents?**
Per-step latency, token counts, error attribution. Diagnoses whether failures are in reasoning, tools, or synthesis.

---

## Project Structure

```text
chapter_08_agent_evaluation/
    sample_data.json    -- Agent traces: single, multi-agent, coding, browser
    dataset.py          -- Data loading + synthetic trace generation
    evaluator.py        -- All evaluators (10 classes + Elo)
    main.py             -- Demonstrations for every evaluator
    hands_on.py         -- LangGraph ReAct agent with real evaluation
```

Run: `cd chapter_08_agent_evaluation && python main.py`

Requirements: Python 3.7+ (stdlib only for main). Hands-on: LangGraph, LangChain, ChatOllama, pandas, optionally Langfuse.

---

## Further Reading

- AgentBench: https://github.com/THUDM/AgentBench
- SWE-Bench: https://www.swebench.com/
- GAIA: https://huggingface.co/gaia-benchmark
- WebArena: https://webarena.dev/
- LangSmith: https://smith.langchain.com
- Langfuse: https://cloud.langfuse.com
- LangGraph ReAct Agent: LangGraph documentation for `create_react_agent`
