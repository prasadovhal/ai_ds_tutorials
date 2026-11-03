"""
File 7: Configuration-Driven Routing & A/B Testing
Concepts: Config files, A/B testing prompts, statistical comparison

Instead of hardcoding all logic, load it from a config dict.
This enables A/B testing: compare two prompt styles and pick the winner.

Configuration-driven systems are more maintainable and testable.
"""

import os
from dotenv import load_dotenv
import json
import ollama

load_dotenv()

client = ollama.Client()

# Configuration: routing rules and prompt templates
GATEWAY_CONFIG = {
    "routing_rules": {
        "factual": {
            "model": "mistral",
            "temperature": 0.3,
            "max_tokens": 200,
            "prompt_style": "concise"
        },
        "research_analysis": {
            "model": "mistral",
            "temperature": 0.7,
            "max_tokens": 800,
            "prompt_style": "detailed"
        },
        "off_topic": {
            "model": "mistral",
            "temperature": 0.2,
            "max_tokens": 50,
            "prompt_style": "redirect"
        }
    },
    "prompt_templates": {
        "concise": "Answer this science question in 1-2 sentences: {query}",
        "detailed": "Provide a comprehensive explanation of this science topic: {query}",
        "redirect": "Politely redirect the user to science topics: {query}"
    },
    "ab_tests": [
        {
            "name": "prompt_style_test",
            "variant_a": "concise",
            "variant_b": "detailed",
            "hypothesis": "Detailed explanations score higher for research queries"
        }
    ]
}


def load_config(config_dict=None):
    """
    Load routing configuration from dict or file.
    In production, this might read from YAML, JSON, or environment.
    """
    if config_dict:
        return config_dict
    else:
        return GATEWAY_CONFIG


def get_routing_config(intent_type):
    """
    Retrieve routing config for a given intent.
    Config includes: model, temperature, max_tokens, prompt_style
    """
    config = load_config()
    return config["routing_rules"].get(intent_type, config["routing_rules"]["factual"])


def get_prompt_template(style):
    """
    Get prompt template by style (concise, detailed, redirect).
    """
    config = load_config()
    return config["prompt_templates"].get(style, "{query}")


def generate_response_with_config(query, intent_type):
    """
    Generate response using config-driven routing.
    This replaces hardcoded logic.
    """
    routing_config = get_routing_config(intent_type)
    prompt_style = routing_config["prompt_style"]
    template = get_prompt_template(prompt_style)

    # Format prompt with query
    prompt = template.format(query=query)

    response = client.chat(
        model=routing_config["model"],
        messages=[
            {"role": "system", "content": "You are a helpful science expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "response": response['message']['content'],
        "config_used": routing_config,
        "prompt_style": prompt_style
    }


def rate_response_quality(query, answer):
    """
    Use LLM to rate response quality (1-10).
    This is used in A/B testing to compare variants.
    """

    rating_prompt = f"""Rate the quality of this science answer:

    Question: {query}
    Answer: {answer}

    Quality score (1-10): Only return a number."""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a critical evaluator of science explanations."},
            {"role": "user", "content": rating_prompt}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(1, min(10, score))
    except:
        score = 5

    return score


def ab_test_prompt_styles(query, variant_a="concise", variant_b="detailed", num_runs=1):
    """
    A/B test: generate responses with two different prompt styles.
    Compare quality scores.

    In real A/B testing, you'd run this many times and do statistical analysis.
    Here, we show the concept with a single run.
    """

    template_a = get_prompt_template(variant_a)
    template_b = get_prompt_template(variant_b)

    prompt_a = template_a.format(query=query)
    prompt_b = template_b.format(query=query)

    # Variant A
    response_a = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful science expert."},
            {"role": "user", "content": prompt_a}
        ]
    )
    answer_a = response_a['message']['content']
    score_a = rate_response_quality(query, answer_a)

    # Variant B
    response_b = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful science expert."},
            {"role": "user", "content": prompt_b}
        ]
    )
    answer_b = response_b['message']['content']
    score_b = rate_response_quality(query, answer_b)

    winner = "A" if score_a > score_b else ("B" if score_b > score_a else "TIE")

    return {
        "query": query,
        "variant_a": variant_a,
        "variant_b": variant_b,
        "answer_a": answer_a[:100],
        "answer_b": answer_b[:100],
        "score_a": score_a,
        "score_b": score_b,
        "winner": winner,
        "score_diff": abs(score_a - score_b)
    }


if __name__ == "__main__":
    print("File 7: Configuration-Driven Routing & A/B Testing")

    print("\n--- Load and Display Config ---")
    config = load_config()
    print(json.dumps(config, indent=2)[:500] + "...")

    print("\n\n--- Config-Driven Response Generation ---")
    test_query = "What is photosynthesis?"

    for intent in ["factual", "research_analysis"]:
        result = generate_response_with_config(test_query, intent)
        print(f"\nIntent: {intent}")
        print(f"  Prompt style: {result['prompt_style']}")
        print(f"  Response: {result['response'][:150]}...")

    print("\n\n--- A/B Test: Concise vs Detailed ---")
    ab_result = ab_test_prompt_styles(
        test_query,
        variant_a="concise",
        variant_b="detailed"
    )

    print(f"Query: {ab_result['query']}")
    print(f"\nVariant A ({ab_result['variant_a']}):")
    print(f"  Score: {ab_result['score_a']}/10")
    print(f"  Preview: {ab_result['answer_a']}")
    print(f"\nVariant B ({ab_result['variant_b']}):")
    print(f"  Score: {ab_result['score_b']}/10")
    print(f"  Preview: {ab_result['answer_b']}")
    print(f"\nWinner: Variant {ab_result['winner']} (score diff: {ab_result['score_diff']})")