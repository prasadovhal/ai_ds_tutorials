"""
File 5: User Tier Policies
Concepts: User segmentation, tier-based routing, policy enforcement

Not all users are equal. A professor doing research has different needs than a student
studying for an exam. This file shows how to apply different policies based on user tier.

Tiers: student, researcher, professor
Each tier has: token budget, response depth, allowed domains
"""

import os
from dotenv import load_dotenv
import ollama

load_dotenv()

client = ollama.Client()

# User tier policies: define budget, depth, and constraints for each tier
USER_TIER_POLICIES = {
    "student": {
        "token_budget": 500,  # limit response size (learning context)
        "response_depth": "simplified",  # use simple language
        "allowed_domains": ["biology", "physics", "chemistry", "astronomy", "general"],  # all domains OK
        "include_citations": False,
        "allow_rag": True,
        "description": "For learning: simplified explanations, smaller responses"
    },
    "researcher": {
        "token_budget": 2000,
        "response_depth": "detailed",
        "allowed_domains": ["biology", "physics", "chemistry", "astronomy", "general"],
        "include_citations": True,
        "allow_rag": True,
        "description": "For research: detailed analysis, citations to sources"
    },
    "professor": {
        "token_budget": 5000,
        "response_depth": "comprehensive",
        "allowed_domains": ["biology", "physics", "chemistry", "astronomy", "general"],
        "include_citations": True,
        "allow_rag": True,
        "allow_multi_step_analysis": True,
        "description": "For teaching/research: full depth, citations, multi-step reasoning"
    }
}


def get_tier_policy(user_tier):
    """
    Retrieve policy for a given user tier.
    If tier doesn't exist, default to "student" (most restrictive).
    """
    return USER_TIER_POLICIES.get(user_tier, USER_TIER_POLICIES["student"])


def apply_tier_constraints(query, user_tier, response_draft):
    """
    Enforce tier constraints on the response.

    Input: query, user_tier, response_draft (from LLM)
    Output: constrained response + policy info
    """
    policy = get_tier_policy(user_tier)

    # Constraint 1: Token budget (truncate if needed)
    max_tokens = policy["token_budget"]
    words = response_draft.split()
    if len(words) > max_tokens / 0.75:  # convert tokens to words
        response_draft = " ".join(words[:int(max_tokens / 0.75)])
        response_draft += "\n[Response truncated due to student token budget]"

    # Constraint 2: Add citations disclaimer if tier requires it
    if not policy["include_citations"]:
        response_draft += "\n\n[Note: Sources not included for student tier]"

    return response_draft, policy


def generate_tiered_response(query, user_tier):
    """
    Generate a response tailored to user tier.

    The system prompt changes based on tier:
    - Student: use simple language, focus on key concepts
    - Researcher: include relevant studies/facts
    - Professor: comprehensive with depth
    """
    policy = get_tier_policy(user_tier)

    # Customize system prompt based on tier
    if policy["response_depth"] == "simplified":
        system_prompt = """You are a science tutor for high school students.
        Explain science concepts using simple language and helpful analogies.
        Keep explanations brief and engaging."""
    elif policy["response_depth"] == "detailed":
        system_prompt = """You are a science expert assisting researchers.
        Provide detailed explanations with relevant facts and examples.
        If applicable, mention related research areas or methodologies."""
    else:  # comprehensive
        system_prompt = """You are a senior science professor and researcher.
        Provide comprehensive, nuanced explanations considering multiple perspectives.
        Discuss methodological details and potential limitations of current understanding."""

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    draft = response['message']['content']
    constrained, policy_used = apply_tier_constraints(query, user_tier, draft)

    return {
        "user_tier": user_tier,
        "policy_depth": policy_used["response_depth"],
        "response": constrained,
        "token_budget": policy_used["token_budget"],
        "include_citations": policy_used["include_citations"]
    }


def domain_policy_check(query_domain, user_tier):
    """
    Check if user tier allows queries in this domain.

    In practice, all tiers currently allow all domains. But this shows
    how you'd implement domain restrictions (e.g., restrict classified research).
    """
    policy = get_tier_policy(user_tier)
    allowed = query_domain in policy["allowed_domains"]

    return {
        "allowed": allowed,
        "domain": query_domain,
        "user_tier": user_tier,
        "reason": f"Domain {query_domain} allowed for {user_tier}" if allowed else f"Domain {query_domain} restricted for {user_tier}"
    }


if __name__ == "__main__":
    print("File 5: User Tier Policies")

    print("\n--- Tier Policies Overview ---")
    for tier, policy in USER_TIER_POLICIES.items():
        print(f"\n{tier.upper()}")
        print(f"  Description: {policy['description']}")
        print(f"  Token budget: {policy['token_budget']}")
        print(f"  Response depth: {policy['response_depth']}")
        print(f"  Include citations: {policy['include_citations']}")

    print("\n\n--- Domain Policy Check ---")
    for tier in ["student", "researcher", "professor"]:
        check = domain_policy_check("physics", tier)
        print(f"{tier}: {check['reason']}")

    print("\n\n--- Tiered Response Generation ---")
    test_query = "What is quantum entanglement?"

    for tier in ["student", "researcher", "professor"]:
        result = generate_tiered_response(test_query, tier)
        print(f"\n{tier.upper()} RESPONSE:")
        print(f"  Depth level: {result['policy_depth']}")
        print(f"  Token budget: {result['token_budget']}")
        print(f"  Response preview (first 200 chars):")
        print(f"  {result['response'][:200]}...")
        print()