"""
File 13: LangSmith Introduction
Concepts: LangSmith, tracing, prompt management, evaluations

LangSmith is similar to LangFuse but optimized for LangChain/LangGraph workflows.

This file shows:
- What LangSmith is and when to use it
- Basic tracing (requires LANGSMITH_API_KEY from environment)
- Conceptual differences from LangFuse
- When to pick LangSmith vs LangFuse

For this tutorial: LangFuse is primary (you have keys).
LangSmith shown for understanding the ecosystem.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Check if LangSmith API key exists
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# Conditional import (LangSmith is optional for this tutorial)
try:
    from langsmith import Client as LangSmithClient
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("Note: langsmith not installed. Showing conceptual examples only.\n")


def langsmith_vs_langfuse():
    """
    Comparison: LangSmith vs LangFuse
    Both are observability platforms, but optimized for different use cases.
    """

    comparison = {
        "LangSmith": {
            "Best for": "LangChain/LangGraph-native workflows",
            "Key features": [
                "Prompt management (versioning, A/B testing)",
                "Evaluation framework (LangSmith evaluators)",
                "Dataset collection and benchmarking",
                "Integration with LangChain agents"
            ],
            "Strengths": [
                "Excellent prompt version control",
                "Built-in evaluation framework",
                "Agent monitoring",
                "LangChain integrations"
            ],
            "When to use": "Building LangChain agents, managing prompts, running evals"
        },
        "LangFuse": {
            "Best for": "General LLM observability (framework-agnostic)",
            "Key features": [
                "Trace collection (any LLM API)",
                "RAG debugging (retrieval visibility)",
                "Cost tracking",
                "User analytics"
            ],
            "Strengths": [
                "Works with any LLM (Ollama, OpenAI, Anthropic)",
                "Lightweight SDK",
                "Good for RAG debugging",
                "User session analytics"
            ],
            "When to use": "Any LLM app, especially RAG systems"
        }
    }

    print("=== LangSmith vs LangFuse ===\n")
    for platform, details in comparison.items():
        print(f"\n{platform}:")
        print(f"  Best for: {details['Best for']}")
        print(f"  Key features:")
        for f in details['Key features']:
            print(f"    - {f}")
        print(f"  Strengths:")
        for s in details['Strengths']:
            print(f"    - {s}")
        print(f"  When to use: {details['When to use']}")


def conceptual_langsmith_trace():
    """
    Show conceptually how LangSmith tracing works.
    If API key is available, this would create a real trace.
    """

    print("\n=== Conceptual LangSmith Trace ===\n")

    if LANGSMITH_AVAILABLE and LANGSMITH_API_KEY:
        print("✓ LangSmith is installed and API key found")
        print("Note: Real LangSmith integration requires LangChain framework")
        print("For standalone use, see langsmith.Client() documentation")
    else:
        print("✗ LangSmith not fully configured (optional for this tutorial)")
        print("Using conceptual example instead...\n")

    # Conceptual trace structure (as if LangSmith was initialized)
    trace_structure = {
        "trace_id": "trace_abc123",
        "name": "science_qa_with_langsmith",
        "runs": [
            {
                "name": "intent_classification",
                "run_type": "chain",
                "input": {"query": "What is photosynthesis?"},
                "output": {"intent": "factual"}
            },
            {
                "name": "rag_retrieval",
                "run_type": "retriever",
                "input": {"query": "What is photosynthesis?"},
                "output": {
                    "documents": ["Chunk 1: Photosynthesis is...", "Chunk 2: Light reactions..."],
                    "num_docs": 2
                }
            },
            {
                "name": "llm_generation",
                "run_type": "llm",
                "model": "mistral",
                "input": {"prompt": "Answer based on context..."},
                "output": {"text": "Photosynthesis is the process..."},
                "tokens": {"input": 100, "output": 200}
            }
        ]
    }

    import json
    print(json.dumps(trace_structure, indent=2))


def langsmith_prompt_management_concept():
    """
    LangSmith's prompt management feature: version and test prompts.
    This is not available in Ollama setup, but shows the concept.
    """

    print("\n=== LangSmith Prompt Management (Conceptual) ===\n")

    print("LangSmith enables:")
    print("1. Prompt versioning")
    print("   - Save prompt iterations")
    print("   - Roll back to previous versions")
    print("   - Track which version is in production")

    print("\n2. Prompt testing")
    print("   - Test multiple prompt versions against test cases")
    print("   - Measure quality scores")
    print("   - Deploy winning version")

    print("\n3. Example workflow:")
    print("   v1.0: 'Answer the question concisely'")
    print("   v1.1: 'Answer with step-by-step reasoning'")
    print("   v1.2: 'Answer with examples'")
    print("   → Test all 3 → v1.1 wins → Deploy v1.1")

    print("\n4. LangSmith dashboard shows:")
    print("   - Which prompt version is running")
    print("   - Cost per version")
    print("   - Quality metrics per version")


def langsmith_evaluation_framework():
    """
    LangSmith has built-in evaluators for quality assessment.
    These are comparable to file 15 (evaluation metrics).
    """

    print("\n=== LangSmith Evaluation Framework (Conceptual) ===\n")

    print("LangSmith evaluators include:")
    print("- Criteria evaluators: custom criteria (e.g., 'Is answer relevant?')")
    print("- Scoring evaluators: score outputs (1-10)")
    print("- Comparison evaluators: compare two outputs")
    print("- Distance evaluators: semantic similarity to reference")

    print("\nExample LangSmith evaluation:")
    evaluation_example = {
        "dataset_name": "science_questions",
        "runs": [
            {
                "input": {"query": "What is photosynthesis?"},
                "output": "Photosynthesis is the process...",
                "evaluation": {
                    "correctness": {"score": 9, "reasoning": "Accurate, concise"},
                    "completeness": {"score": 7, "reasoning": "Missing some details"},
                    "overall": {"score": 8}
                }
            }
        ]
    }

    import json
    print(json.dumps(evaluation_example, indent=2))


def when_to_use_which():
    """
    Decision matrix: when to use LangSmith vs LangFuse vs custom tracing.
    """

    print("\n=== Decision Matrix ===\n")

    decision_matrix = {
        "Using LangChain/LangGraph agents?": {
            "Yes": "→ LangSmith (native integration)",
            "No": "→ LangFuse or custom"
        },
        "Need prompt versioning/management?": {
            "Yes": "→ LangSmith",
            "No": "→ LangFuse"
        },
        "Building RAG system?": {
            "Yes": "→ LangFuse (better RAG debugging)",
            "No": "→ Either"
        },
        "Need cost tracking per model?": {
            "Yes": "→ LangFuse",
            "No": "→ Either"
        },
        "Want lightweight SDK, minimal setup?": {
            "Yes": "→ LangFuse",
            "No": "→ LangSmith"
        }
    }

    for question, answer in decision_matrix.items():
        print(f"{question}")
        for key, val in answer.items():
            print(f"  {key}: {val}")
        print()


if __name__ == "__main__":
    print("File 13: LangSmith Introduction")
    print("=" * 60)

    langsmith_vs_langfuse()
    conceptual_langsmith_trace()
    langsmith_prompt_management_concept()
    langsmith_evaluation_framework()
    when_to_use_which()

    print("=" * 60)
    print("Key Takeaways:")
    print("1. LangSmith: best for LangChain/LangGraph workflows")
    print("2. LangFuse: best for general LLM apps and RAG systems")
    print("3. Both provide observability; different trade-offs")
    print("4. LangSmith strength: prompt versioning and management")
    print("5. LangFuse strength: RAG debugging and cost tracking")
    print("6. For this tutorial: LangFuse is primary (you have keys)")
    print("7. In production: pick based on your tech stack (LangChain vs other)")
