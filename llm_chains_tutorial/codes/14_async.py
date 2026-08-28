import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Problem: In a web app (like Streamlit or Django), if you use llm.invoke(), the entire server freezes until the answer comes back.
Solution: Use llm.ainvoke() (Async Invoke). This lets your server handle other users while waiting for the LLM.

"""

import asyncio
from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

async def main():
    # Notice the 'await' keyword
    response = await llm.ainvoke("Hello, how are you?")
    print(response.content)

# Run it
asyncio.run(main())



# Just await the function directly!
# You don't even need to wrap it in a 'main' function if you don't want to.
# NOTE: The below only works in Jupyter notebooks / async REPLs.
# In a regular Python script, use asyncio.run() as shown above.

# response = await llm.ainvoke("Hello, are you async?")
# print(response.content)