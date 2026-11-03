# Project 6: Agent Evaluation Framework

Trace evaluation + Elo tournament ranking for multiple agents, with Langfuse tracing.

## Run
```bash
cd projects/06_agent_eval_framework
python main.py
```

## What It Does
- Defines 3 simulated agent traces (Alpha, Beta, Gamma)
- Evaluates: task completion, tool efficiency, tool correctness, answer accuracy
- Computes trajectory score (weighted composite)
- Runs Elo tournament with round-robin matches
- Produces ranked leaderboard with score breakdown
- Sends results to Langfuse

## Dependencies
langfuse (optional)
