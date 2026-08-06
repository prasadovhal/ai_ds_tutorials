"""
File 3: Complexity & Domain Routing
Concepts: Complexity estimation, domain classification, routing decisions

We've classified intent (factual vs research). Now we need to route based on:
1. How complex is the query? (1-10 scale)
2. Which science domain? (biology, physics, chemistry, astronomy)

Complex queries get deeper prompts. Domain routing helps tailor answers.
"""

import os
from dotenv import load_dotenv
import ollama

load_dotenv()

client = ollama.Client()

def estimate_complexity_heuristic(query):
    """
    Fast heuristic-based complexity scoring (1-10).
    No LLM call; uses query length, vocabulary, and keyword patterns.

    Rationale: Complex queries often have more words, jargon, or nested clauses.
    Simple factual queries are usually short and direct.
    """

    complexity_score = 5  # start neutral

    # Length heuristic: longer queries tend to be more complex
    word_count = len(query.split())
    if word_count < 5:
        complexity_score -= 2
    elif word_count > 30:
        complexity_score += 2

    # Vocabulary heuristic: technical jargon signals complexity
    technical_terms = [
        "mechanism", "pathway", "model", "theory", "hypothesis",
        "differential", "spectrum", "coefficient", "kinetics", "topology"
    ]
    jargon_count = sum(1 for term in technical_terms if term in query.lower())
    complexity_score += jargon_count

    # Comparison keywords: "compare", "vs", "analyze" = more complex
    comparison_keywords = ["compare", "versus", "vs", "difference", "analyze", "evaluate"]
    if any(kw in query.lower() for kw in comparison_keywords):
        complexity_score += 3

    # Clamp to 1-10
    complexity_score = max(1, min(10, complexity_score))

    return complexity_score


def estimate_complexity_llm(query):
    """
    Use LLM to score complexity. More accurate than heuristic.
    Returns a score 1-10 from the model.

    LLM can understand semantic nuance: "explain quantum tunneling" is more complex
    than "what is a proton", even though they're similar length.
    """

    system_prompt = """You are a complexity evaluator for science questions.
    Score the query's conceptual difficulty on a scale of 1-10:
    1-3: Simple factual (definitions, basic facts)
    4-6: Moderate (requires some domain knowledge)
    7-10: Complex (requires synthesis, comparison, deep reasoning)

    Return ONLY a number (1-10). No explanation."""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    try:
        score = int(response['message']['content'].strip())
        score = max(1, min(10, score))  # clamp to 1-10
    except:
        score = 5  # default to middle if parsing fails

    return score


def classify_domain(query):
    """
    Classify which science domain the query belongs to.
    Domains: biology, physics, chemistry, astronomy, general

    This helps tailor prompts. E.g., biology answers mention cells;
    physics answers use equations. One system prompt can't do all.
    """

    query_lower = query.lower()

    # Domain keywords (simple keyword matching)
    domains = {
        "biology": ["dna", "protein", "cell", "gene", "mitochondria", "photosynthesis", "crispr", "evolution", "organism", "enzyme"],
        "physics": ["quantum", "relativity", "black hole", "entropy", "wave", "particle", "energy", "force", "motion", "light"],
        "chemistry": ["atom", "bond", "reaction", "element", "periodic", "catalyst", "oxidation", "molecule", "electron"],
        "astronomy": ["star", "planet", "galaxy", "exoplanet", "cosmic", "nebula", "supernova", "dark matter", "cmb"]
    }

    # Count keyword matches per domain
    domain_scores = {}
    for domain, keywords in domains.items():
        matches = sum(1 for kw in keywords if kw in query_lower)
        domain_scores[domain] = matches

    # Return domain with highest match count
    if max(domain_scores.values()) > 0:
        return max(domain_scores, key=domain_scores.get)
    else:
        return "general"


def routing_decision(query):
    """
    Combined routing decision based on complexity + domain.

    High complexity + specific domain → use specialized RAG (file 10)
    Low complexity → use fast simple LLM answer
    General domain → use general-purpose system prompt
    """

    complexity = estimate_complexity_llm(query)
    domain = classify_domain(query)

    routing_path = "unknown"
    if complexity <= 3:
        routing_path = "simple_direct_answer"
    elif complexity <= 6 and domain != "general":
        routing_path = "domain_specific_answer"
    else:
        routing_path = "rag_with_context"

    return {
        "query": query,
        "complexity": complexity,
        "domain": domain,
        "routing_path": routing_path
    }


if __name__ == "__main__":
    print("File 3: Complexity & Domain Routing")
    print("=" * 60)

    test_queries = [
        "What is DNA?",
        "Explain the citric acid cycle step by step",
        "Compare thermodynamic entropy and information entropy",
        "What is a black hole?",
        "How do exoplanet detection methods differ?",
    ]

    print("\n--- Complexity Estimation (Heuristic) ---")
    for query in test_queries:
        score = estimate_complexity_heuristic(query)
        print(f"Query: {query[:50]}")
        print(f"  Complexity (heuristic): {score}\n")

    print("\n--- Routing Decision (Complexity + Domain) ---")
    for query in test_queries:
        decision = routing_decision(query)
        print(f"Query: {decision['query'][:50]}")
        print(f"  Complexity (LLM): {decision['complexity']}")
        print(f"  Domain: {decision['domain']}")
        print(f"  Routing path: {decision['routing_path']}\n")

    print("=" * 60)
    print("Key Takeaways:")
    print("1. Complexity drives resource allocation (simple = fast, complex = thorough)")
    print("2. Domain classification allows specialized prompts/retrieval")
    print("3. Heuristics are fast; LLM judgment is accurate—use hybrid approach")
    print("4. Routing paths: simple_answer → domain_answer → rag_with_context")
    print("5. This routing feeds into file 4 (token/cost decisions)")
