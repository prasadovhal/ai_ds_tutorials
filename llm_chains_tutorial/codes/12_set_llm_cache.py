import langchain
from langchain_community.cache import InMemoryCache
# Direct assignment (Old Syntax)
langchain.llm_cache = InMemoryCache()

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from constant import GOOGLE_API_KEY

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")


# 2. Run the same query twice
llm.invoke("Tell me a joke") # Takes 2 seconds, costs money
llm.invoke("Tell me a joke") # Takes 0.001 seconds, costs nothing!