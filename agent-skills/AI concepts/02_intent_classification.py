"""
File 2: Intent Classification
Concepts: Intent classification, rule-based + LLM-based routing

After recognizing the query, we need to understand its intent: is it a simple factual question,
a complex research task, or off-topic? Two approaches: keyword rules (fast) + LLM judgment (accurate).
This becomes the foundation for routing logic in file 3.
"""

import os
from dotenv import load_dotenv
import ollama

load_dotenv()

client = ollama.Client()

def rule_based_intent(query):
    """
    Fast intent classification using keyword rules.
    No LLM call = instant, cheap, predictable.
    Trade-off: brittle if query phrasing changes.

    Returns: "factual", "research_analysis", "off_topic"
    """

    query_lower = query.lower()

    # Check for off-topic keywords
    off_topic_words = ["joke", "recipe", "movie", "sport", "music", "weather", "dating"]
    if any(word in query_lower for word in off_topic_words):
        return "off_topic"

    # Check for research keywords (complex queries)
    research_words = ["compare", "analyze", "evaluate", "difference between", "pros and cons", "vs", "versus"]
    if any(word in query_lower for word in research_words):
        return "research_analysis"

    # Check for simple factual keywords
    factual_words = ["what is", "define", "explain", "how does", "tell me about"]
    if any(word in query_lower for word in factual_words):
        return "factual"

    # Default: assume factual if unsure
    return "factual"


def llm_based_intent(query):
    """
    Use LLM to classify intent. More accurate for edge cases, but slower and costs tokens.
    Call this when rule-based is ambiguous.

    The LLM is instructed to return ONLY the intent label (no explanation).
    This keeps output predictable and easy to parse.
    """

    system_prompt = """You are an intent classifier for a science assistant.
    Classify the user's query into ONE of these categories:
    - "factual": Simple definition, fact, or explanation (e.g., "What is DNA?")
    - "research_analysis": Complex comparison, analysis, or evaluation (e.g., "Compare two theories")
    - "off_topic": Not related to science (e.g., "Tell me a joke")

    Return ONLY the category name. No explanation."""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    intent = response['message']['content'].strip().lower()

    # Validate response; if garbage, default to factual
    if intent not in ["factual", "research_analysis", "off_topic"]:
        intent = "factual"

    return intent


def hybrid_intent_classifier(query):
    """
    Best of both worlds: try rule-based first (fast).
    If it returns "factual" or "off_topic" with high confidence, use it.
    If ambiguous, fall back to LLM for accuracy.

    This balances speed and accuracy.
    """

    rule_intent = rule_based_intent(query)

    # If rule-based found off_topic or clear research keywords, trust it
    if rule_intent in ["off_topic", "research_analysis"]:
        return rule_intent, "rule-based"

    # Otherwise use LLM for verification (handles edge cases like "distinguish between X and Y")
    llm_intent = llm_based_intent(query)
    return llm_intent, "llm-based"


if __name__ == "__main__":
    print("File 2: Intent Classification")
    print("=" * 60)

    test_queries = [
        "What is photosynthesis?",
        "Compare C3 and C4 photosynthesis pathways",
        "Tell me a funny joke",
        "Explain quantum entanglement",
        "What's better: cats or dogs?",
        "How does CRISPR gene editing work?",
        "Analyze the pros and cons of AI in healthcare",
        "What time is it?",
    ]

    print("\n--- Rule-Based Intent Classification ---")
    for query in test_queries:
        intent = rule_based_intent(query)
        print(f"Query: {query[:50]}")
        print(f"  Intent: {intent}\n")

    print("\n--- Hybrid Intent Classification (Rule + LLM) ---")
    for query in test_queries[:4]:  # Just first 4 to save time
        intent, method = hybrid_intent_classifier(query)
        print(f"Query: {query[:50]}")
        print(f"  Intent: {intent} (via {method})\n")

    print("=" * 60)
    print("Key Takeaways:")
    print("1. Rule-based classification is fast but brittle")
    print("2. LLM-based classification is accurate but slow (needs token count)")
    print("3. Hybrid approach: use rules for obvious cases, LLM for edge cases")
    print("4. Intent classification feeds into routing logic (next file)")
    print("5. Always parse LLM output strictly to avoid surprises")
