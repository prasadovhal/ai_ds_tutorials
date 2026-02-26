"""
Problem: In a web app (like Streamlit or Django), if you use llm.invoke(), the entire server freezes until the answer comes back.
Solution: Use llm.ainvoke() (Async Invoke). This lets your server handle other users while waiting for the LLM.

"""

import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from constant import GOOGLE_API_KEY

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")

async def main():
    # Notice the 'await' keyword
    response = await llm.ainvoke("Hello, how are you?")
    print(response.content)

# Run it
asyncio.run(main())



# Just await the function directly!
# You don't even need to wrap it in a 'main' function if you don't want to.

response = await llm.ainvoke("Hello, are you async?")
print(response.content)