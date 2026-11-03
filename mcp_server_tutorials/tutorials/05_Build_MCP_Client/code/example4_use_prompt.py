"""
Example 4: Use a Prompt from the Client
=========================================
This client connects to a server, lists all available prompts,
and then uses session.get_prompt() to get a rendered prompt.

What you will learn:
  - How to list prompts from the server
  - How to get a prompt with arguments using session.get_prompt()
  - How to read the rendered prompt messages

How to run:
  python example4_use_prompt.py

IMPORTANT:
  This client connects to the Chapter 4 AllFeaturesServer.
  That server exposes two prompts:
    - summarize(text)                   -> returns a summarization prompt
    - translate(text, target_language)  -> returns a translation prompt
"""

import asyncio
import os
import sys

# ============================================================
# Step 1: Import the MCP client classes
# ============================================================
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession

# ============================================================
# Step 2: Define the path to the server script
# ============================================================
SERVER_SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "04_Build_First_MCP_Server",
    "code",
    "example4_server_all_features.py"
)
SERVER_SCRIPT_PATH = os.path.abspath(SERVER_SCRIPT_PATH)


# ============================================================
# Step 3: Define the main async function
# ============================================================
async def main():
    """Connect to the server, list prompts, and get rendered prompts."""

    print("=" * 60)
    print("Example 4: Use a Prompt from the Client")
    print("=" * 60)

    # Check that the server script exists
    if not os.path.exists(SERVER_SCRIPT_PATH):
        print(f"\nERROR: Server script not found at:")
        print(f"  {SERVER_SCRIPT_PATH}")
        print(f"\nMake sure you have completed Chapter 4 first.")
        return

    print(f"\nServer: {SERVER_SCRIPT_PATH}")

    # Step 4: Configure and connect
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT_PATH]
    )

    print("Connecting to server...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            # Step 5: Initialize the session
            await session.initialize()
            print("Connected and initialized!\n")

            # ================================================
            # Step 6: List all available prompts
            # ================================================
            # session.list_prompts() sends a prompts/list request.
            # It returns a ListPromptsResult object.
            print("Listing available prompts...")
            print("-" * 50)

            prompts_result = await session.list_prompts()
            prompt_list = prompts_result.prompts

            print(f"Found {len(prompt_list)} prompts:\n")

            # Print each prompt's name, description, and arguments
            for prompt in prompt_list:
                print(f"  Prompt: {prompt.name}")
                if prompt.description:
                    print(f"  Description: {prompt.description}")

                # Print the arguments this prompt expects
                if prompt.arguments:
                    print(f"  Arguments:")
                    for arg in prompt.arguments:
                        required_label = "(required)" if arg.required else "(optional)"
                        print(f"    - {arg.name} {required_label}")
                print()

            # ================================================
            # Step 7: Get the "summarize" prompt
            # ================================================
            # session.get_prompt() sends a prompts/get request.
            # First argument: the name of the prompt.
            # Second argument: a dictionary of argument values.
            print("=" * 50)
            print("Getting prompt: summarize")
            print("=" * 50)

            sample_text = "MCP is a protocol that lets AI applications connect to external tools and data sources. It provides a standard way for clients and servers to communicate."

            print(f"\nInput text: {sample_text}\n")

            prompt_result = await session.get_prompt(
                "summarize",
                {"text": sample_text}
            )

            # The result has a "messages" list.
            # Each message has a "role" (user/assistant) and "content".
            print("Rendered prompt messages:")
            print("-" * 40)

            for message in prompt_result.messages:
                print(f"\n  Role: {message.role}")
                # The content can be a TextContent object or a string
                content = message.content
                if hasattr(content, "text"):
                    print(f"  Content:\n")
                    for line in content.text.split("\n"):
                        print(f"    {line}")
                else:
                    print(f"  Content: {content}")

            # ================================================
            # Step 8: Get the "translate" prompt
            # ================================================
            print("\n" + "=" * 50)
            print("Getting prompt: translate")
            print("=" * 50)

            translate_text = "Hello, how are you today?"
            target_language = "Spanish"

            print(f"\nInput text: {translate_text}")
            print(f"Target language: {target_language}\n")

            prompt_result2 = await session.get_prompt(
                "translate",
                {"text": translate_text, "target_language": target_language}
            )

            print("Rendered prompt messages:")
            print("-" * 40)

            for message in prompt_result2.messages:
                print(f"\n  Role: {message.role}")
                content = message.content
                if hasattr(content, "text"):
                    print(f"  Content:\n")
                    for line in content.text.split("\n"):
                        print(f"    {line}")
                else:
                    print(f"  Content: {content}")

    # Connection is automatically closed
    print("\n" + "=" * 60)
    print("Done! Client disconnected.")
    print("=" * 60)


# ============================================================
# Step 9: Run the async main function
# ============================================================
if __name__ == "__main__":
    asyncio.run(main())
