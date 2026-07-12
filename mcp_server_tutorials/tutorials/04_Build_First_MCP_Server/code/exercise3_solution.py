"""
Exercise 3 Solution: Prompt Server
=====================================
An MCP server with three reusable prompt templates.
"""

# ============================================================
# STEP 1: Import FastMCP
# ============================================================
from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 2: Create the server
# ============================================================
server = FastMCP("PromptTemplateServer")

# ============================================================
# STEP 3: Summarize prompt
# ============================================================
@server.prompt()
def summarize(text: str) -> str:
    """Summarize the given text into key points."""

    prompt = f"""Please read the following text carefully and provide a concise summary.

Instructions:
- Identify the main topic
- Extract 3-5 key points
- Write a 2-3 sentence summary
- Use simple, clear language

Text to summarize:
---
{text}
---

Please provide your summary:"""

    return prompt

# ============================================================
# STEP 4: Translate prompt
# ============================================================
@server.prompt()
def translate(text: str, target_language: str) -> str:
    """Translate the given text to the target language."""

    prompt = f"""Translate the following text to {target_language}.

Rules:
- Maintain the original meaning as closely as possible
- Preserve the tone (formal/informal) of the original
- If there are idioms, find equivalent expressions in {target_language}
- Do not add explanations, just provide the translation

Original text:
---
{text}
---

Translation to {target_language}:"""

    return prompt

# ============================================================
# STEP 5: Explain prompt
# ============================================================
@server.prompt()
def explain(topic: str, difficulty_level: str) -> str:
    """Explain a topic at a given difficulty level."""

    # Build instructions based on difficulty level
    # This makes the prompt more useful by adapting to the audience
    if difficulty_level.lower() == "beginner":
        level_instructions = """- Use very simple language, no jargon
- Include a real-world analogy
- Assume no prior knowledge of the topic
- Keep the explanation under 150 words"""
    elif difficulty_level.lower() == "advanced":
        level_instructions = """- Use technical terminology where appropriate
- Include implementation details
- Discuss edge cases and trade-offs
- Reference related concepts and best practices"""
    else:
        # Default to intermediate
        level_instructions = """- Use clear language with some technical terms
- Explain any jargon you use
- Include a practical example
- Keep the explanation focused and structured"""

    prompt = f"""Explain the following topic at a {difficulty_level} level.

Topic: {topic}

Guidelines:
{level_instructions}

Please provide your explanation:"""

    return prompt

# ============================================================
# STEP 6: Run the server
# ============================================================
if __name__ == "__main__":
    server.run()
