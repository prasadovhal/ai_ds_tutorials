"""
Example 3: Multi-Message Prompts
=================================

This example shows how to return multi-turn conversation prompts.

Instead of returning a single string, a prompt can return a LIST
of messages. Each message has:
  - "role": either "user" or "assistant"
  - "content": the text of that message

This is useful when you want to set up a conversation context.
For example, a code review prompt might include:
  1. A system-like message (sent as "user") setting the role
  2. A user message with the actual code to review

Why multi-message?
  - Single string = one instruction
  - Multi-message = a whole conversation setup
  - This gives the LLM better context about how to respond

Key concepts:
- Returning a list of message dictionaries
- Using "role" and "content" keys
- Setting up system-like context with user messages
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("MultiMessagePrompts")


# ---- Prompt 1: Code Review ----
# This prompt returns TWO messages:
#   1. A "user" message that sets the context (act as a code reviewer)
#   2. A "user" message with the actual code to review
# The LLM receives both messages and understands the full context.
@server.prompt()
def code_review(code: str, language: str = "Python") -> list:
    """Review code for bugs, style, and improvements."""
    return [
        # First message: Set the context / role
        # We use "user" role because MCP prompts support "user" and "assistant"
        {
            "role": "user",
            "content": (
                f"You are an expert {language} code reviewer. "
                f"Review the following code carefully. "
                f"Check for:\n"
                f"- Bugs and logical errors\n"
                f"- Code style and readability\n"
                f"- Performance issues\n"
                f"- Security concerns\n"
                f"- Suggestions for improvement\n\n"
                f"Be constructive and explain your reasoning."
            ),
        },
        # Second message: Provide the code to review
        {
            "role": "user",
            "content": f"Here is the {language} code to review:\n\n```{language}\n{code}\n```",
        },
    ]


# ---- Prompt 2: Debug Help ----
# This prompt helps debug an error by providing:
#   1. A context message that sets up the debugging role
#   2. A message with the error details and code
# This gives the LLM everything it needs to help debug.
@server.prompt()
def debug_help(code: str, error_message: str) -> list:
    """Help debug code that produces an error."""
    return [
        # First message: Set the debugging context
        {
            "role": "user",
            "content": (
                "You are an expert debugging assistant. "
                "A developer is stuck with an error in their code. "
                "Help them understand:\n"
                "1. What is causing the error\n"
                "2. How to fix it\n"
                "3. How to prevent similar errors in the future\n\n"
                "Be patient and explain step by step."
            ),
        },
        # Second message: The actual error and code
        {
            "role": "user",
            "content": (
                f"I'm getting this error:\n\n"
                f"```\n{error_message}\n```\n\n"
                f"Here is my code:\n\n"
                f"```python\n{code}\n```\n\n"
                f"Can you help me fix this?"
            ),
        },
    ]


# ---- Run the server ----
if __name__ == "__main__":
    server.run()
