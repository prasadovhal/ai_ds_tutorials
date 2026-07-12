"""
Exercise 1: Writing Style Prompts
===================================

TASK:
Create an MCP server with 3 prompts for different writing styles:

1. formal_style(text, audience)
   - Rewrites text in a formal, professional tone
   - The "audience" parameter specifies who will read it
     (e.g., "executives", "clients", "board members")

2. casual_style(text, context)
   - Rewrites text in a casual, friendly tone
   - The "context" parameter specifies the situation
     (e.g., "team chat", "social media", "blog post")

3. technical_style(text, domain)
   - Rewrites text in a technical, precise tone
   - The "domain" parameter specifies the technical field
     (e.g., "machine learning", "web development", "data science")

HINTS:
- Use @server.prompt() decorator
- Each function returns a string with instructions for the LLM
- Include the parameters in the returned prompt text
- Think about what makes each writing style unique

Try it yourself before looking at exercise1_solution.py!
"""

from mcp.server.fastmcp import FastMCP

# Step 1: Create the MCP server
server = FastMCP("WritingStyleExercise")

# ---- YOUR CODE HERE ----

# Prompt 1: formal_style
# TODO: Create a prompt that rewrites text in formal style
# Parameters: text (str), audience (str)


# Prompt 2: casual_style
# TODO: Create a prompt that rewrites text in casual style
# Parameters: text (str), context (str)


# Prompt 3: technical_style
# TODO: Create a prompt that rewrites text in technical style
# Parameters: text (str), domain (str)


# ---- END YOUR CODE ----

# Run the server
if __name__ == "__main__":
    server.run()
