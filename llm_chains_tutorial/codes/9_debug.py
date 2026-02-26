import langchain
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from constant import GOOGLE_API_KEY

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 1. Initialize Model
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")

# Turn on verbose logging
langchain.debug = True
langchain.verbose = True

# Now run any chain
# You will see every step: The raw prompt entering, the raw JSON leaving, etc.
response = llm.invoke("Hi")
print(response)

"""

AIMessage(content='Hi there! How can I help you today?', additional_kwargs={}, response_metadata={'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': [], 'model_provider': 'google_genai'}, id='lc_run--019c93ec-fc18-75d0-9702-ac3e98819587-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 2, 'output_tokens': 32, 'total_tokens': 34, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 22}})

"""