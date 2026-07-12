"""
Example 3: Server with a Prompt Template
==========================================
This server exposes a PROMPT - a reusable template for
LLM interactions. Prompts help standardize how users
interact with LLMs through MCP.

Think of prompts as pre-written scripts that the client
can fill in with specific values.

What you will learn:
    - How to register a prompt with @server.prompt()
    - How prompts take parameters
    - How prompts return messages (user/assistant format)

How to run:
    poetry run mcp dev example3_server_with_prompt.py

How to test:
    Open MCP Inspector
    Go to the Prompts tab
    Click on "summarize"
    Fill in the "text" parameter with any long text
    You should see the generated prompt messages
"""

# ============================================================
# STEP 1: Import what we need
# ============================================================
from mcp.server.fastmcp import FastMCP

# ============================================================
# STEP 2: Create the server
# ============================================================
server = FastMCP("PromptServer")

# ============================================================
# STEP 3: Register a prompt
# ============================================================
# The @server.prompt() decorator registers this function
# as an MCP prompt template.
#
# When a client calls prompts/get with name="summarize",
# this function is called with the provided arguments.
#
# The function returns a STRING. FastMCP automatically
# wraps it into a proper message format for the client.
#
# WHY use prompts?
# -----------------
# Imagine you have 10 different clients connecting to your
# server. Without prompts, each client would need to write
# its own "summarize this text" prompt. With MCP prompts,
# you define it ONCE on the server, and all clients can
# use the same high-quality prompt.
@server.prompt()
def summarize(text: str) -> str:
    """Summarize the given text concisely."""

    # Build the prompt that will be sent to the LLM
    # We create a clear, structured prompt that tells
    # the LLM exactly what to do
    prompt = f"""Please summarize the following text concisely.
Focus on the key points and main ideas.
Keep the summary to 2-3 sentences.

Text to summarize:
{text}

Summary:"""

    return prompt

# ============================================================
# STEP 4: Add a second prompt with multiple parameters
# ============================================================
# Prompts can take multiple parameters.
# Each parameter becomes part of the prompt template.
@server.prompt()
def explain_concept(concept: str, audience: str) -> str:
    """Explain a concept for a specific audience."""

    prompt = f"""Explain the following concept in simple terms.

Concept: {concept}

Target Audience: {audience}

Instructions:
- Use language appropriate for the target audience
- Include a real-world analogy
- Keep the explanation under 200 words
- Avoid jargon unless the audience is technical

Explanation:"""

    return prompt

# ============================================================
# STEP 5: Add a third prompt to show variety
# ============================================================
@server.prompt()
def review_code(code: str, language: str) -> str:
    """Review code and suggest improvements."""

    prompt = f"""Review the following {language} code.

```{language}
{code}
```

Please provide:
1. A brief description of what the code does
2. Any bugs or issues you find
3. Suggestions for improvement
4. A rating from 1-10 for code quality

Review:"""

    return prompt

# ============================================================
# STEP 6: Run the server
# ============================================================
if __name__ == "__main__":
    server.run()
