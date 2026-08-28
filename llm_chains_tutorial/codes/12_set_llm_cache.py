import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import langchain
from langchain_community.cache import InMemoryCache
# Direct assignment (Old Syntax)
langchain.llm_cache = InMemoryCache()

from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)


# 2. Run the same query twice
llm.invoke("Tell me a joke") # Takes 2 seconds, costs money
llm.invoke("Tell me a joke") # Takes 0.001 seconds, costs nothing!