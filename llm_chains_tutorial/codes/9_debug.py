import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import langchain
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

# Turn on verbose logging
langchain.debug = True
langchain.verbose = True

# Now run any chain
# You will see every step: The raw prompt entering, the raw JSON leaving, etc.
response = llm.invoke("Hi")
print(response.content)

"""

AIMessage(content='Hi there! How can I help you today?', additional_kwargs={}, response_metadata={'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': [], 'model_provider': 'google_genai'}, id='lc_run--019c93ec-fc18-75d0-9702-ac3e98819587-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 2, 'output_tokens': 32, 'total_tokens': 34, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 22}})

"""