"""
File 4: Token, Cost & Latency Routing
Concepts: Token counting, cost estimation, latency-aware selection

Now we know the complexity and domain. But will this query be expensive or slow?
Token counts tell us: longer contexts = more cost. This file shows how to estimate
and route accordingly. Cost is critical for production systems.
"""

import os
from dotenv import load_dotenv
import time
import ollama

load_dotenv()

client = ollama.Client()

def estimate_token_count(text):
    """
    Estimate token count as a rough heuristic.
    Most English text: ~1 token per 0.75 words (rough rule of thumb).

    Real token counting requires a tokenizer (e.g., tiktoken for GPT, sentencepiece for Ollama).
    For this tutorial, we use simple heuristic.
    """
    # Split on whitespace and common punctuation
    words = len(text.split())
    estimated_tokens = int(words / 0.75)
    return estimated_tokens


def estimate_cost_for_query(query, model="mistral"):
    """
    Estimate inference cost based on token count.

    Cost model for Ollama (local) is $0 (free), but we'll show the calculation
    as if it were an API call (e.g., Claude, GPT-4). This teaches cost reasoning.

    Example pricing:
    - Input: $0.003 per 1K tokens
    - Output: $0.012 per 1K tokens (output usually more expensive)
    """

    prompt_tokens = estimate_token_count(query)

    # Assume average response is ~150 tokens for simple, ~500 for complex
    estimated_output_tokens = 150

    # Pricing (hypothetical, as if calling API)
    input_cost_per_1k = 0.003  # dollars
    output_cost_per_1k = 0.012  # dollars

    total_input_cost = (prompt_tokens / 1000) * input_cost_per_1k
    total_output_cost = (estimated_output_tokens / 1000) * output_cost_per_1k
    total_cost = total_input_cost + total_output_cost

    return {
        "prompt_tokens": prompt_tokens,
        "estimated_output_tokens": estimated_output_tokens,
        "total_tokens": prompt_tokens + estimated_output_tokens,
        "estimated_cost": round(total_cost, 6),
        "input_cost": round(total_input_cost, 6),
        "output_cost": round(total_output_cost, 6)
    }


def cost_aware_routing(query, budget_dollars=0.10):
    """
    Decide whether to proceed based on cost budget.

    High-cost queries: warn user, offer summary/condensed version
    Very high-cost: reject and ask for simpler query
    """

    cost_info = estimate_cost_for_query(query)
    estimated_cost = cost_info["estimated_cost"]

    if estimated_cost > budget_dollars:
        # Over budget: suggest alternatives
        return {
            "proceed": False,
            "reason": "Cost exceeded budget",
            "cost_info": cost_info,
            "suggestion": "Consider asking a simpler question or summarizing your prompt"
        }
    elif estimated_cost > budget_dollars * 0.7:
        # Approaching budget limit: warn but proceed
        return {
            "proceed": True,
            "reason": "Cost near budget limit; proceeding with caution",
            "cost_info": cost_info,
            "suggestion": "This will be relatively expensive. Proceed? (Y/N)"
        }
    else:
        # Safe to proceed
        return {
            "proceed": True,
            "reason": "Cost within budget",
            "cost_info": cost_info,
            "suggestion": None
        }


def latency_aware_routing(query_complexity):
    """
    Route based on expected latency.

    Simple queries (complexity 1-3): use fast model (small/quantized)
    Complex queries (complexity 7+): use slower but powerful model
    Medium: balanced model

    For Ollama, we just have one local model, but this teaches the concept.
    In production, you'd pick different models: mistral-7b (fast), mistral-large (slow, accurate).
    """

    if query_complexity <= 3:
        model_choice = "mistral"  # fast, small model
        latency_budget_ms = 500   # expect answer in <500ms
    elif query_complexity <= 6:
        model_choice = "mistral"  # balanced model
        latency_budget_ms = 1500  # expect answer in <1.5s
    else:
        model_choice = "mistral"  # powerful model (in prod: mistral-large)
        latency_budget_ms = 3000  # complex queries can take up to 3s

    return {
        "model": model_choice,
        "latency_budget_ms": latency_budget_ms
    }


def measure_latency(query):
    """
    Measure actual LLM latency for a query.
    Track: time from request → first token, and total time.

    This data feeds into SLA monitoring and fallback decisions.
    """

    start_time = time.time()

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a science expert. Answer concisely."},
            {"role": "user", "content": query}
        ]
    )

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    return {
        "latency_ms": round(latency_ms, 2),
        "response": response['message']['content'][:100],
    }


if __name__ == "__main__":
    print("File 4: Token, Cost & Latency Routing")
    print("=" * 60)

    test_queries = [
        "What is photosynthesis?",
        "Explain the complete mechanism of photosynthesis including electron transport chains and the Calvin cycle",
    ]

    print("\n--- Cost Estimation ---")
    for query in test_queries:
        cost_info = estimate_cost_for_query(query)
        print(f"Query: {query[:50]}")
        print(f"  Tokens: {cost_info['total_tokens']}")
        print(f"  Estimated cost: ${cost_info['estimated_cost']}")
        print()

    print("\n--- Cost-Aware Routing (budget: $0.10) ---")
    for query in test_queries:
        routing = cost_aware_routing(query, budget_dollars=0.10)
        print(f"Query: {query[:50]}")
        print(f"  Proceed: {routing['proceed']}")
        print(f"  Reason: {routing['reason']}")
        print()

    print("\n--- Latency-Aware Routing ---")
    for complexity in [2, 5, 8]:
        routing = latency_aware_routing(complexity)
        print(f"Complexity {complexity}:")
        print(f"  Model: {routing['model']}")
        print(f"  Latency budget: {routing['latency_budget_ms']}ms")
        print()

    print("\n--- Measuring Actual Latency ---")
    latency_data = measure_latency(test_queries[0])
    print(f"Query: {test_queries[0]}")
    print(f"  Latency: {latency_data['latency_ms']}ms")
    print(f"  Response preview: {latency_data['response']}")

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Token count estimation drives cost prediction")
    print("2. Cost budget prevents runaway expenses in production")
    print("3. Latency budgets route queries to appropriate models")
    print("4. Simple queries: fast model, low latency")
    print("5. Complex queries: powerful model, accept higher latency")
    print("6. Actual latency measurement validates assumptions")
